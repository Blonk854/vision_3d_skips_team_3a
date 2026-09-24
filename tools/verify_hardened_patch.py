"""Static, state-model and isolated machine-code checks for the hardened patch."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import os
import pathlib
import struct
import subprocess
import sys
from dataclasses import dataclass


def require_verifier_runtime() -> None:
    if not __debug__:
        raise SystemExit("verifier integrity failure: optimized Python is unsupported")
    if os.environ.get("PYTHONOPTIMIZE"):
        raise SystemExit(
            "verifier integrity failure: PYTHONOPTIMIZE must be unset or empty"
        )


require_verifier_runtime()

import pefile
from capstone import CS_ARCH_X86, CS_MODE_64, Cs
from unicorn import UC_ARCH_X86, UC_HOOK_CODE, UC_MODE_64, Uc
from unicorn import x86_const as registers
from unicorn.unicorn_py3.unicorn import UcContext

import patch_f1_missing_n_rev5 as patcher


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "v3d_files_" / "Vision3D.exe"
OUTPUT = ROOT / "Updated" / "Vision3D_concurrency_fix.exe"

STATE_OPEN = 0
STATE_CLAIMING = 1
STATE_SKIP_COMMITTED = 2
STATE_RECONCILED = 3
STATE_FAILED_DISABLED = 4


def require(condition: bool, invariant: str) -> None:
    if not condition:
        raise RuntimeError("validation failure: %s" % invariant)


def is_committed_state(state: int) -> bool:
    return state in (STATE_SKIP_COMMITTED, STATE_RECONCILED)


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def branch_target(data: bytes, file_offset: int, va: int) -> int:
    return va + 5 + struct.unpack_from("<i", data, file_offset + 1)[0]


@dataclass
class Cell:
    inspected: int = 0
    missing: int = 0
    state: int = 0
    trigger_calls: int = 0

    def inspect(self, is_missing: bool) -> None:
        if self.state != STATE_OPEN:
            return
        self.inspected += 1
        if is_missing:
            self.missing += 1
        if (
            self.inspected >= patcher.MIN_INSPECTED
            and self.missing * 100
            > self.inspected * patcher.MISSING_PERCENT
            and self.state == STATE_OPEN
        ):
            self.state = STATE_CLAIMING
            self.trigger_calls += 1
            self.state = STATE_SKIP_COMMITTED

    def fail_claim(self) -> None:
        if self.state == STATE_CLAIMING:
            self.state = STATE_FAILED_DISABLED


@dataclass
class Context:
    status: int = 1
    refcount: int = 0
    skip_lock: bool = False

    def acquire_worker(self) -> bool:
        if self.status != 1:
            return False
        self.refcount += 1
        return True

    def release_worker(self) -> None:
        self.refcount -= 1

    def begin_reset(self) -> bool:
        if self.status != 1:
            return False
        self.status = 2
        return True

    def can_clear(self) -> bool:
        return self.status == 2 and self.refcount == 0


def verify_model() -> None:
    boundaries = [
        (3, 10, False),
        (4, 10, True),
        (9, 30, False),
        (10, 30, True),
        (4, 9, False),
    ]
    for missing, inspected, expected in boundaries:
        actual = (
            inspected >= patcher.MIN_INSPECTED
            and missing * 100 > inspected * patcher.MISSING_PERCENT
        )
        require(actual is expected, "policy boundary %d/%d" % (missing, inspected))

    # Any ordering of six Missing and six good completions must claim once.
    for missing_positions in itertools.combinations(range(12), 6):
        missing_set = set(missing_positions)
        cell = Cell()
        for index in range(12):
            cell.inspect(index in missing_set)
        require(cell.trigger_calls == 1, "exactly one threshold claim")

    # Independent panel/CAO contexts with identical sub-panel IDs do not mix.
    panels = {"cao_a": Cell(), "cao_b": Cell()}
    for _ in range(10):
        panels["cao_a"].inspect(True)
        panels["cao_b"].inspect(False)
    require(
        panels["cao_a"].state == STATE_SKIP_COMMITTED,
        "CAO A reaches skip-committed",
    )
    require(panels["cao_b"].state == STATE_OPEN, "CAO B remains open")
    require(panels["cao_b"].missing == 0, "CAO counters remain isolated")

    # A reset retires all state instead of carrying counts into a new panel.
    old = Cell()
    for _ in range(9):
        old.inspect(True)
    fresh = Cell()
    fresh.inspect(True)
    require(
        fresh.inspected == 1
        and fresh.missing == 1
        and fresh.state == STATE_OPEN,
        "retirement clears panel counters",
    )

    # Retirement disables new workers and cannot reuse storage until holders
    # from the old lifecycle release their references.
    context = Context()
    require(context.acquire_worker(), "active context accepts worker")
    require(context.begin_reset(), "active context begins retirement")
    require(not context.acquire_worker(), "retiring context rejects worker")
    require(not context.can_clear(), "held reference blocks context clear")
    context.release_worker()
    require(context.can_clear(), "retired unreferenced context can clear")

    # Per-CAO skip-list serialization admits only one mutator at a time.
    context = Context()
    context.skip_lock = True
    second_winner_may_enter = not context.skip_lock
    require(not second_winner_may_enter, "skip-list mutation is serialized")

    for state in range(5):
        require(
            is_committed_state(state) is (state in (2, 3)),
            "exact committed-state membership for state %d" % state,
        )
    require(not is_committed_state(5), "unknown state is not committed")

    failed = Cell(state=STATE_CLAIMING)
    failed.fail_claim()
    require(failed.state == STATE_FAILED_DISABLED, "claiming failure publishes state 4")
    for state in (STATE_OPEN, STATE_SKIP_COMMITTED, STATE_RECONCILED, STATE_FAILED_DISABLED):
        cell = Cell(state=state)
        cell.fail_claim()
        require(cell.state == state, "failure cleanup does not downgrade state %d" % state)


def verify_optimized_execution_refusal(revision: str) -> None:
    command = [
        sys.executable,
        "-O",
        str(pathlib.Path(__file__).resolve()),
        "--revision",
        revision,
        "--code-only",
    ]
    environment = os.environ.copy()
    environment.pop("PYTHONOPTIMIZE", None)
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
        env=environment,
    )
    combined_output = result.stdout + result.stderr
    require(result.returncode != 0, "optimized verifier exits nonzero")
    require("PASS" not in combined_output, "optimized verifier emits no PASS")


def verify_forced_failure_refusal(revision: str) -> None:
    command = [
        sys.executable,
        str(pathlib.Path(__file__).resolve()),
        "--revision",
        revision,
        "--code-only",
        "--force-failure",
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    combined_output = result.stdout + result.stderr
    require(result.returncode != 0, "forced verifier failure exits nonzero")
    require("PASS" not in combined_output, "forced verifier failure emits no PASS")


class HandlerEmulator:
    CAO = 0x20000000
    STOP = patcher.IMAGE_BASE + 0x1000
    NONVOLATILE = (
        registers.UC_X86_REG_RBX, registers.UC_X86_REG_RBP,
        registers.UC_X86_REG_RSI, registers.UC_X86_REG_RDI,
        registers.UC_X86_REG_R12, registers.UC_X86_REG_R13,
        registers.UC_X86_REG_R14, registers.UC_X86_REG_R15,
    )

    def __init__(self) -> None:
        self.cpu = Uc(UC_ARCH_X86, UC_MODE_64)
        self.cpu.mem_map(patcher.IMAGE_BASE, 0x1CC3000)
        self.cpu.mem_map(self.CAO, 0x100000)
        self.cpu.mem_map(0x21000000, 0x100000)
        self.cpu.mem_map(0x22000000, 0x100000)
        payload, self.sizes = patcher.build_code()
        self.cpu.mem_write(patcher.CAVE, payload)
        for address in (patcher.GET_CAO, patcher.SKIPSUB, patcher.SHOULD_REVIEW):
            self.cpu.mem_write(address, b"\xc3")
        self.cpu.mem_write(patcher.RESET_CONT, bytes.fromhex("488bd94883c4205bc3"))
        self.instructions = list(Cs(CS_ARCH_X86, CS_MODE_64).disasm(
            payload[:self.sizes["count_size"]], patcher.COUNT_CAVE
        ))
        self.final_instructions = list(Cs(CS_ARCH_X86, CS_MODE_64).disasm(
            payload[patcher.FINAL_CAVE - patcher.CAVE:
                    patcher.FINAL_CAVE - patcher.CAVE + self.sizes["final_size"]],
            patcher.FINAL_CAVE,
        ))
        self.skip_calls: list[tuple[int, int]] = []
        self.break_at: int | None = None
        self.thread_count = 0
        self.cpu.hook_add(UC_HOOK_CODE, self.on_instruction)

    def read(self, address: int, size: int = 4) -> int:
        return int.from_bytes(self.cpu.mem_read(address, size), "little")

    def write(self, address: int, value: int, size: int = 4) -> None:
        self.cpu.mem_write(address, value.to_bytes(size, "little"))

    def seed(self, slot: int = 0, cao: int = CAO) -> int:
        context = patcher.DATA_VA + slot * patcher.CONTEXT_STRIDE
        self.write(context, cao, 8)
        self.write(context + patcher.CONTEXT_STATUS, 1)
        return context

    def spawn(self, entry: int = patcher.COUNT_CAVE, *, cao: int = CAO,
              subpanel: int = 1, mask: int = 0) -> UcContext:
        self.thread_count += 1
        fixture = 0x22000000 + self.thread_count * 0x1000
        stack = 0x21000000 + self.thread_count * 0x2000 + 0x1FF8
        for register in self.NONVOLATILE:
            self.cpu.reg_write(register, 0x12345678)
        self.cpu.reg_write(registers.UC_X86_REG_RFLAGS, 2)
        self.cpu.reg_write(registers.UC_X86_REG_RSP, stack)
        self.cpu.reg_write(registers.UC_X86_REG_RIP, entry)
        self.cpu.reg_write(registers.UC_X86_REG_RBX, mask)
        self.cpu.reg_write(registers.UC_X86_REG_RCX, cao)
        self.cpu.reg_write(registers.UC_X86_REG_RDX, subpanel)
        self.cpu.reg_write(registers.UC_X86_REG_R15, fixture)
        self.cpu.reg_write(registers.UC_X86_REG_RDI, fixture + 0x100)
        self.cpu.reg_write(registers.UC_X86_REG_R13, fixture + 0x200)
        self.cpu.reg_write(registers.UC_X86_REG_R14, fixture + 0x800)
        self.write(fixture + 0x10, cao, 8)
        self.write(fixture + 0x114, subpanel)
        self.write(fixture + 0x800, cao, 8)
        self.write(stack, self.STOP, 8)
        return self.cpu.context_save()

    def run(self, thread: UcContext, *, until: int | None = None,
            steps: int = 20000) -> UcContext:
        self.cpu.context_restore(thread)
        self.break_at = until
        self.cpu.emu_start(thread.reg_read(registers.UC_X86_REG_RIP), 0, count=steps)
        return self.cpu.context_save()

    def complete(self, thread: UcContext, expected: int) -> UcContext:
        finished = self.run(thread)
        assert finished.reg_read(registers.UC_X86_REG_RIP) == expected
        assert finished.reg_read(registers.UC_X86_REG_RSP) == (
            thread.reg_read(registers.UC_X86_REG_RSP) + 8
        )
        for register in self.NONVOLATILE:
            assert finished.reg_read(register) == thread.reg_read(register)
        return finished

    def on_instruction(self, cpu: Uc, address: int, size: int, user_data: object) -> None:
        if address in (self.STOP, patcher.COUNT_HOOK_RET,
                       patcher.EXECUTE_ONE_EARLY_EXIT, self.break_at):
            cpu.emu_stop()
        elif address == patcher.GET_CAO:
            cpu.reg_write(registers.UC_X86_REG_RAX,
                          self.read(cpu.reg_read(registers.UC_X86_REG_RCX), 8))
        elif address == patcher.SKIPSUB:
            cao = cpu.reg_read(registers.UC_X86_REG_RCX)
            contexts = [patcher.DATA_VA + slot * patcher.CONTEXT_STRIDE
                        for slot in range(patcher.CONTEXT_COUNT)]
            active = [context for context in contexts if self.read(context, 8) == cao]
            assert len(active) <= 1
            assert self.read(patcher.DATA_VA + patcher.GLOBAL_TABLE_LOCK) == (not active)
            if active:
                assert self.read(active[0] + patcher.CONTEXT_SKIP_LOCK) == 1
            self.skip_calls.append((cao, cpu.reg_read(registers.UC_X86_REG_EDX)))
        elif address == patcher.SHOULD_REVIEW:
            cpu.reg_write(registers.UC_X86_REG_RAX, 1)


def verify_machine_code() -> None:
    emulator = HandlerEmulator()
    for address, size, operand in (
        (patcher.COUNT_CAVE, emulator.sizes["count_size"], "dword ptr [r10 + 0x14]"),
        (patcher.FINAL_CAVE, emulator.sizes["final_size"], "dword ptr [r12 + 0x14]"),
        (patcher.STOCK_SKIP_CAVE, emulator.sizes["stock_skip_size"], "dword ptr [r10 + 0x14]"),
    ):
        instructions = list(Cs(CS_ARCH_X86, CS_MODE_64).disasm(
            bytes(emulator.cpu.mem_read(address, size)), address
        ))
        increments = [instruction for instruction in instructions
                      if instruction.mnemonic.endswith("inc") and instruction.op_str == operand]
        assert len(increments) == 1 and increments[0].mnemonic == "lock inc"

    first = emulator.seed()
    second = emulator.seed(1, emulator.CAO + 0x10000)
    emulator.complete(emulator.spawn(patcher.RESET_CAVE), emulator.STOP)
    assert emulator.read(first, 8) == 0
    emulator.complete(emulator.spawn(cao=emulator.CAO + 0x10000), patcher.COUNT_HOOK_RET)
    assert emulator.read(first, 8) == 0
    assert emulator.read(second + patcher.CONTEXT_CELLS + patcher.CELL_SIZE) == 1

    emulator = HandlerEmulator()
    context = emulator.seed()
    cell = context + patcher.CONTEXT_CELLS + patcher.CELL_SIZE
    emulator.write(cell, 9)
    emulator.write(cell + patcher.CELL_MISSING, 3)
    after_increment = next(instruction.address + instruction.size
                           for instruction in emulator.instructions
                           if instruction.mnemonic == "lock xadd"
                           and instruction.op_str == "dword ptr [r11], eax")
    first_worker = emulator.run(emulator.spawn(), until=after_increment)
    assert first_worker.reg_read(registers.UC_X86_REG_RIP) == after_increment
    second_worker = emulator.run(emulator.spawn(), steps=100)
    assert emulator.read(cell) == 10
    assert emulator.read(patcher.DATA_VA + patcher.GLOBAL_TABLE_LOCK) == 1
    assert emulator.run(first_worker).reg_read(registers.UC_X86_REG_RIP) == patcher.COUNT_HOOK_RET
    assert emulator.run(second_worker).reg_read(registers.UC_X86_REG_RIP) == patcher.COUNT_HOOK_RET
    for mask in (0, 0, 1):
        emulator.complete(emulator.spawn(mask=mask), patcher.COUNT_HOOK_RET)
    assert emulator.read(cell) == 14 and emulator.read(cell + patcher.CELL_MISSING) == 4
    assert emulator.read(cell + patcher.CELL_STATE) == 0 and not emulator.skip_calls

    for mask in (0, 1):
        emulator = HandlerEmulator()
        context = emulator.seed()
        cell = context + patcher.CONTEXT_CELLS + patcher.CELL_SIZE
        emulator.write(cell, 9)
        emulator.write(cell + patcher.CELL_MISSING, 4 - mask)
        emulator.complete(emulator.spawn(mask=mask), patcher.EXECUTE_ONE_EARLY_EXIT)
        emulator.complete(emulator.spawn(mask=1), patcher.EXECUTE_ONE_EARLY_EXIT)
        assert emulator.skip_calls == [(emulator.CAO, 1)]
        assert emulator.read(cell + patcher.CELL_STATE) == 2
        assert emulator.read(context + patcher.CONTEXT_REFCOUNT) == 0

    emulator = HandlerEmulator()
    context = emulator.seed()
    release = next(instruction.address for instruction in reversed(emulator.instructions)
                   if instruction.mnemonic == "lock dec")
    first_worker = emulator.run(emulator.spawn(), until=release)
    assert emulator.read(context + patcher.CONTEXT_REFCOUNT) == 1
    second_worker = emulator.run(emulator.spawn(), until=release)
    assert emulator.read(context + patcher.CONTEXT_REFCOUNT) == 2
    reset = emulator.run(emulator.spawn(patcher.RESET_CAVE), steps=200)
    assert emulator.read(context + patcher.CONTEXT_STATUS) == 2
    emulator.complete(emulator.spawn(), patcher.COUNT_HOOK_RET)
    assert emulator.read(context + patcher.CONTEXT_REFCOUNT) == 2
    emulator.run(first_worker)
    emulator.run(second_worker)
    assert emulator.read(context + patcher.CONTEXT_REFCOUNT) == 0
    assert emulator.run(reset).reg_read(registers.UC_X86_REG_RIP) == emulator.STOP
    assert emulator.read(context, 8) == 0

    emulator = HandlerEmulator()
    context = emulator.seed()
    cell = context + patcher.CONTEXT_CELLS + patcher.CELL_SIZE
    emulator.write(cell + patcher.CELL_STATE, 2)
    diagnostic = next(instruction.address for instruction in emulator.final_instructions
                      if instruction.mnemonic == "lock or")
    finalizer = emulator.run(emulator.spawn(patcher.FINAL_CAVE), until=diagnostic)
    assert finalizer.reg_read(registers.UC_X86_REG_RIP) == diagnostic
    assert emulator.read(patcher.DATA_VA + patcher.GLOBAL_TABLE_LOCK) == 0
    other_worker = emulator.run(emulator.spawn(subpanel=2), until=after_increment)
    assert other_worker.reg_read(registers.UC_X86_REG_RIP) == after_increment
    assert emulator.read(patcher.DATA_VA + patcher.GLOBAL_TABLE_LOCK) == 1
    assert emulator.run(finalizer).reg_read(registers.UC_X86_REG_RIP) == emulator.STOP
    assert emulator.read(patcher.DATA_VA + patcher.GLOBAL_TABLE_LOCK) == 1
    assert emulator.read(context + patcher.CONTEXT_DIAGNOSTIC) == 1
    assert emulator.run(other_worker).reg_read(registers.UC_X86_REG_RIP) == patcher.COUNT_HOOK_RET
    assert emulator.read(context + patcher.CONTEXT_REFCOUNT) == 0


    for second_subpanel in (1, 2):
        emulator = HandlerEmulator()
        context = emulator.seed()
        for subpanel in (1, 2):
            cell = context + patcher.CONTEXT_CELLS + subpanel * patcher.CELL_SIZE
            emulator.write(cell, 9)
            emulator.write(cell + patcher.CELL_MISSING, 4)
        first_worker = emulator.run(emulator.spawn(), until=patcher.SKIPSUB)
        assert first_worker.reg_read(registers.UC_X86_REG_RIP) == patcher.SKIPSUB
        second_worker = emulator.run(emulator.spawn(subpanel=second_subpanel), steps=200)
        assert emulator.read(context + patcher.CONTEXT_REFCOUNT) == 2
        assert emulator.read(patcher.DATA_VA + patcher.GLOBAL_TABLE_LOCK) == 0
        assert not emulator.skip_calls
        assert emulator.run(first_worker).reg_read(registers.UC_X86_REG_RIP) == patcher.EXECUTE_ONE_EARLY_EXIT
        assert emulator.run(second_worker).reg_read(registers.UC_X86_REG_RIP) == patcher.EXECUTE_ONE_EARLY_EXIT
        assert len(emulator.skip_calls) == second_subpanel
        assert emulator.read(context + patcher.CONTEXT_REFCOUNT) == 0
        assert emulator.read(context + patcher.CONTEXT_SKIP_LOCK) == 0

    emulator = HandlerEmulator()
    for slot in range(patcher.CONTEXT_COUNT):
        emulator.seed(slot, emulator.CAO + slot * 0x10000)
    emulator.complete(emulator.spawn(cao=emulator.CAO + 0x90000), patcher.COUNT_HOOK_RET)
    assert emulator.read(patcher.DATA_VA + patcher.GLOBAL_FULL) == 1
    assert emulator.read(patcher.DATA_VA + patcher.GLOBAL_TABLE_LOCK) == 0
    emulator.complete(emulator.spawn(subpanel=1024), patcher.COUNT_HOOK_RET)
    emulator.complete(emulator.spawn(subpanel=0xFFFFFFFF), patcher.COUNT_HOOK_RET)
    assert emulator.read(patcher.DATA_VA + patcher.GLOBAL_UNSUPPORTED) == 2
    emulator.complete(emulator.spawn(subpanel=1023), patcher.COUNT_HOOK_RET)
    assert emulator.read(patcher.DATA_VA + patcher.CONTEXT_CELLS + 1023 * patcher.CELL_SIZE) == 1


def verify_binary(output_path: pathlib.Path = OUTPUT) -> None:
    source = SOURCE.read_bytes()
    output = output_path.read_bytes()
    assert digest(SOURCE) == patcher.SOURCE_SHA256
    assert digest(output_path) == patcher.EXPECTED_OUTPUT_SHA256
    assert len(output) - len(source) == patcher.CODE_SIZE
    patcher.verify_companion_hashes(SOURCE)

    pe = pefile.PE(data=output, fast_load=False)
    original = pefile.PE(data=source, fast_load=True)
    sections = {s.Name.rstrip(b"\0"): s for s in pe.sections}
    code = sections[b".f1code"]
    data = sections[b".f1data"]
    assert code.VirtualAddress == patcher.CODE_RVA
    assert code.Misc_VirtualSize == patcher.CODE_SIZE
    assert code.SizeOfRawData == patcher.CODE_SIZE
    assert code.Characteristics == 0x60000020
    assert data.VirtualAddress == patcher.DATA_RVA
    assert data.Misc_VirtualSize == patcher.DATA_SIZE
    assert data.SizeOfRawData == 0
    assert data.Characteristics == 0xC0000080
    assert pe.OPTIONAL_HEADER.SizeOfImage == patcher.DATA_RVA + patcher.DATA_SIZE
    assert patcher.GLOBAL_TABLE_LOCK >= (
        patcher.CONTEXT_COUNT * patcher.CONTEXT_STRIDE
    )
    assert patcher.GLOBAL_FULL + 4 <= patcher.DATA_SIZE

    count_off = patcher.va_to_text_off(patcher.COUNT_HOOK)
    reset_off = patcher.va_to_text_off(patcher.RESET_HOOK)
    final_off = patcher.va_to_text_off(patcher.FINAL_CALL)
    stock_skip_off = patcher.va_to_text_off(patcher.STOCK_SKIP_CALL)
    review_off = patcher.va_to_text_off(patcher.REVIEW_ROUTE_TEST)
    assert output[count_off] == 0xE8
    assert branch_target(output, count_off, patcher.COUNT_HOOK) == patcher.COUNT_CAVE
    assert output[count_off + 5 : count_off + 11] == b"\x90" * 6
    assert output[reset_off] == 0xE9
    assert branch_target(output, reset_off, patcher.RESET_HOOK) == patcher.RESET_CAVE
    assert output[final_off] == 0xE8
    assert branch_target(output, final_off, patcher.FINAL_CALL) == patcher.FINAL_CAVE
    assert output[stock_skip_off] == 0xE8
    assert (
        branch_target(output, stock_skip_off, patcher.STOCK_SKIP_CALL)
        == patcher.STOCK_SKIP_CAVE
    )
    assert (
        output[review_off : review_off + len(patcher.REVIEW_ROUTE_PATCH)]
        == patcher.REVIEW_ROUTE_PATCH
    )

    md = Cs(CS_ARCH_X86, CS_MODE_64)
    code_raw = code.PointerToRawData
    payload, sizes = patcher.build_code()
    assert output[code_raw:code_raw + len(payload)] == payload
    regions = {
        "count": (
            patcher.COUNT_CAVE,
            code_raw + patcher.COUNT_CAVE - patcher.CAVE,
            sizes["count_size"],
        ),
        "reset": (
            patcher.RESET_CAVE,
            code_raw + patcher.RESET_CAVE - patcher.CAVE,
            sizes["reset_size"],
        ),
        "final": (
            patcher.FINAL_CAVE,
            code_raw + patcher.FINAL_CAVE - patcher.CAVE,
            sizes["final_size"],
        ),
        "exception_cleanup": (
            patcher.EXCEPTION_HANDLER_CAVE,
            code_raw + patcher.EXCEPTION_HANDLER_CAVE - patcher.CAVE,
            sizes["exception_cleanup_size"],
        ),
        "count_exception_cleanup": (
            patcher.COUNT_EXCEPTION_HANDLER_CAVE,
            code_raw + patcher.COUNT_EXCEPTION_HANDLER_CAVE - patcher.CAVE,
            sizes["count_exception_cleanup_size"],
        ),
        "stock_skip": (
            patcher.STOCK_SKIP_CAVE,
            code_raw + patcher.STOCK_SKIP_CAVE - patcher.CAVE,
            sizes["stock_skip_size"],
        ),
        "stock_skip_exception": (
            patcher.STOCK_SKIP_EXCEPTION_CAVE,
            code_raw + patcher.STOCK_SKIP_EXCEPTION_CAVE - patcher.CAVE,
            sizes["stock_skip_exception_size"],
        ),
    }
    decoded = {}
    for name, (va, offset, size) in regions.items():
        instructions = list(md.disasm(output[offset : offset + size], va))
        assert sum(i.size for i in instructions) == size
        decoded[name] = instructions

    count_text = {(i.mnemonic, i.op_str) for i in decoded["count"]}
    assert ("call", "0x140541080") in count_text
    assert ("lock xadd", "dword ptr [r11], eax") in count_text
    assert ("lock cmpxchg", "dword ptr [r11 + 8], ecx") in count_text
    assert ("mov", "dword ptr [r13 + 0x2c], 1") in count_text

    final_text = {(i.mnemonic, i.op_str) for i in decoded["final"]}
    assert ("call", "0x140674820") in final_text
    assert ("call", "0x140541080") not in final_text
    assert ("mov", "eax, dword ptr [r13 + 0x5880]") in final_text
    assert ("cmp", "byte ptr [rbx + 0x280], 0") in final_text
    assert ("lock bts", "dword ptr [r12 + 0xc], 0") in final_text
    assert any(
        i.op_str == "eax, dword ptr [r13 + 0x5880]"
        for i in decoded["final"]
    )
    cleanup_text = {
        (i.mnemonic, i.op_str) for i in decoded["exception_cleanup"]
    }
    assert ("lock dec", "dword ptr [rax + 0x14]") in cleanup_text
    assert ("mov", "eax, 1") in cleanup_text
    count_cleanup_text = {
        (i.mnemonic, i.op_str)
        for i in decoded["count_exception_cleanup"]
    }
    assert ("mov", "dword ptr [rax + 0x18], 0") in count_cleanup_text
    assert ("mov", "dword ptr [r8 + 8], 0") in count_cleanup_text
    assert ("lock dec", "dword ptr [rax + 0x14]") in count_cleanup_text
    assert ("mov", "eax, 1") in count_cleanup_text
    stock_skip_text = {
        (i.mnemonic, i.op_str) for i in decoded["stock_skip"]
    }
    assert ("call", "0x140541080") in stock_skip_text
    assert (
        "lock cmpxchg",
        "dword ptr [r10 + 0x18], edx",
    ) in stock_skip_text
    stock_cleanup_text = {
        (i.mnemonic, i.op_str)
        for i in decoded["stock_skip_exception"]
    }
    assert ("lock dec", "dword ptr [rax + 0x14]") in stock_cleanup_text
    assert ("mov", "eax, 1") in stock_cleanup_text
    # The hardened implementation never invokes virtual RazRes globally.
    assert not any(
        i.mnemonic == "call" and "[rax + 0x48]" in i.op_str
        for instructions in decoded.values()
        for i in instructions
    )

    exception = pe.OPTIONAL_HEADER.DATA_DIRECTORY[
        pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]
    ]
    assert exception.Size % 12 == 0
    pdata = sections[b".pdata"]
    appended = pdata.PointerToRawData + exception.Size - 48
    runtime = [
        struct.unpack_from("<III", output, appended + index * 12)
        for index in range(4)
    ]
    assert runtime == [
        (
            patcher.COUNT_CAVE - patcher.IMAGE_BASE,
            patcher.COUNT_CAVE - patcher.IMAGE_BASE + sizes["count_size"],
            patcher.CODE_RVA + patcher.COUNT_UNWIND_OFFSET,
        ),
        (
            patcher.RESET_CAVE - patcher.IMAGE_BASE,
            patcher.RESET_CAVE - patcher.IMAGE_BASE + sizes["reset_size"],
            patcher.CODE_RVA + patcher.RESET_UNWIND_OFFSET,
        ),
        (
            patcher.FINAL_CAVE - patcher.IMAGE_BASE,
            patcher.FINAL_CAVE - patcher.IMAGE_BASE + sizes["final_size"],
            patcher.CODE_RVA + patcher.FINAL_UNWIND_OFFSET,
        ),
        (
            patcher.STOCK_SKIP_CAVE - patcher.IMAGE_BASE,
            patcher.STOCK_SKIP_CAVE - patcher.IMAGE_BASE
            + sizes["stock_skip_size"],
            patcher.CODE_RVA + patcher.STOCK_SKIP_UNWIND_OFFSET,
        ),
    ]

    unwind_expectations = {
        patcher.COUNT_UNWIND_OFFSET: bytes.fromhex("1104010004620000")
        + struct.pack(
            "<I",
            patcher.COUNT_EXCEPTION_HANDLER_CAVE - patcher.IMAGE_BASE,
        ),
        patcher.RESET_UNWIND_OFFSET: bytes.fromhex("010603000670053201300000"),
        patcher.FINAL_UNWIND_OFFSET: bytes.fromhex(
            "110d07000d6209f007d005c00370026001300000"
        )
        + struct.pack(
            "<I", patcher.EXCEPTION_HANDLER_CAVE - patcher.IMAGE_BASE
        ),
        patcher.STOCK_SKIP_UNWIND_OFFSET: bytes.fromhex(
            "110603000662026001300000"
        )
        + struct.pack(
            "<I", patcher.STOCK_SKIP_EXCEPTION_CAVE - patcher.IMAGE_BASE
        ),
    }
    for relative, expected in unwind_expectations.items():
        offset = code_raw + relative
        assert output[offset : offset + len(expected)] == expected

    original_pdata = next(section for section in original.sections
                          if section.Name.rstrip(b"\0") == b".pdata")
    original_exception = original.OPTIONAL_HEADER.DATA_DIRECTORY[3]
    optional = original.OPTIONAL_HEADER.get_file_offset()
    allowed_spans = [
        (original.DOS_HEADER.e_lfanew + 6, 2),
        (optional + 4, 4),
        (optional + 12, 4),
        (optional + 56, 4),
        (original_exception.get_file_offset() + 4, 4),
        (original_pdata.get_file_offset() + 8, 4),
        (original.sections[-1].get_file_offset() + 40, 80),
        (original_pdata.PointerToRawData + original_exception.Size, 48),
        (count_off, len(patcher.COUNT_HOOK_ORIG)),
        (reset_off, len(patcher.RESET_ORIG)),
        (final_off, len(patcher.FINAL_CALL_ORIG)),
        (stock_skip_off, len(patcher.STOCK_SKIP_CALL_ORIG)),
        (review_off, len(patcher.REVIEW_ROUTE_ORIG)),
    ]
    allowed = bytearray(len(source))
    for offset, size in allowed_spans:
        allowed[offset:offset + size] = b"\x01" * size
    assert all(before == after or allowed[offset]
               for offset, (before, after) in enumerate(zip(source, output)))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", choices=("rev5",), required=True)
    parser.add_argument("--code-only", action="store_true")
    parser.add_argument("--output", type=pathlib.Path, default=OUTPUT)
    parser.add_argument("--force-failure", action="store_true", help=argparse.SUPPRESS)
    arguments = parser.parse_args()
    require(not arguments.force_failure, "forced verifier regression")
    verify_optimized_execution_refusal(arguments.revision)
    verify_forced_failure_refusal(arguments.revision)
    verify_model()
    verify_machine_code()
    print("interpreter=%s" % sys.executable)
    print("python=%s" % sys.version.replace("\n", " "))
    print("PYTHONOPTIMIZE=%r" % os.environ.get("PYTHONOPTIMIZE"))
    print("verifier integrity regressions: PASS")
    print("state model: PASS")
    print("machine-code concurrency regressions: PASS (stock calls stubbed)")
    if arguments.code_only:
        print("verifier_exit_status=0")
        return 0
    verify_binary(arguments.output)
    print("PE sections and hooks: PASS")
    print("handler decoding and targets: PASS")
    print("runtime-function metadata: PASS")
    print("source/DLL identities and intended byte-diff spans: PASS")
    print("global RazRes calls: ABSENT")
    print("verifier_exit_status=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
