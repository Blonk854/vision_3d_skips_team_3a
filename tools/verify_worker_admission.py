"""Offline admission/drain experiments; not a Rev6 builder or lifecycle proof.

Execute source-verified stock instructions and an in-memory guard in Unicorn.
Win32/MFC helpers and inspection descendants are stubs. The synchronous body is
executed only by SynchronousBodyEmulator. No target code executes natively, no PE
is emitted. A Windows-only test checks virtual unwind of the replacement entry
using non-executable copied bytes. Selected C++ cleanup funclets are emulated;
native exception dispatch and runtime handlers remain untested.
"""
from __future__ import annotations

import bisect
import ctypes
import hashlib
import json
import os
import pathlib
import platform
import struct
import unittest

if not __debug__ or os.environ.get("PYTHONOPTIMIZE"):
    raise SystemExit("verifier integrity failure: optimized Python is unsupported")

import pefile
from capstone import CS_AC_WRITE, CS_ARCH_X86, CS_MODE_64, Cs
from capstone.x86 import X86_OP_MEM, X86_REG_EAX, X86_REG_RAX
from keystone import KS_ARCH_X86, KS_MODE_64, Ks
from unicorn import (
    UC_ARCH_X86, UC_ERR_READ_UNMAPPED, UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_MODE_64, Uc, UcError,
)
from unicorn import x86_const as registers


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE_HASH = "ccca11b2f05084b484fa5556c67f8874065dbc0b6265177d2517f81265af00f4"
IMAGE_BASE = 0x140000000
AVVTRAIT_HASH = "0f9f68b118112cea87e1735995776934d8d009e3d6d39a8a58562e3fa3e3e5f7"
AVVTRAIT_BASE = 0x180000000
GET_THREAD = 0x1406A1660
DISPATCH = 0x14069FB80
SYNCHRONOUS = 0x14069FCD0
RECEIVER = 0x1406A88E0
DRAIN = 0x1406A9A80
GUARD_SITE = 0x1406A1707
GUARD_CONTINUE = 0x1406A170D
EMPTY_RETURN = 0x1406A180D
SCRATCH_CODE = 0x142000000
RETURN_SENTINEL = SCRATCH_CODE + 0x800
FIXTURE = 0x20000000
PRODUCTION = FIXTURE
POOL = PRODUCTION + 0xEC8
WORKER = FIXTURE + 0x4000
WORKER_ARRAY = FIXTURE + 0x5000
AVAILABILITY = FIXTURE + 0x6000
COPIED_AVAILABILITY = FIXTURE + 0x7000
COMPLETION_ARRAY = FIXTURE + 0x8000
DOCUMENT = FIXTURE + 0x10000
STACK_BASE = 0x21000000
STACK_TOP = STACK_BASE + 0xEFF8
EVENT_HANDLE = 0x1234
AVAILABILITY_HANDLE = 0x2345
WORK_HANDLE = 0x3456
NONVOLATILE = (
    registers.UC_X86_REG_RBX, registers.UC_X86_REG_RBP,
    registers.UC_X86_REG_RSI, registers.UC_X86_REG_RDI,
    registers.UC_X86_REG_R12, registers.UC_X86_REG_R13,
    registers.UC_X86_REG_R14, registers.UC_X86_REG_R15,
)
VOLATILE = (
    registers.UC_X86_REG_RAX, registers.UC_X86_REG_RCX,
    registers.UC_X86_REG_RDX, registers.UC_X86_REG_R8,
    registers.UC_X86_REG_R9, registers.UC_X86_REG_R10,
    registers.UC_X86_REG_R11,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError("validation failure: " + message)


def verified_functions() -> dict[int, bytes]:
    source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
    require(hashlib.sha256(source).hexdigest() == SOURCE_HASH, "stock source identity")
    selection = (
        ("rev2a_entry_gate_pool.json", GET_THREAD),
        ("rev2a_entry_gate_pool.json", DRAIN),
        ("rev2a_entry_gate_second_pass.json", DISPATCH),
        ("rev2a_entry_gate_second_pass.json", RECEIVER),
        ("rev2a_entry_gate_workers.json", SYNCHRONOUS),
    )
    functions = {}
    with pefile.PE(data=source, fast_load=True) as image:
        require(image.OPTIONAL_HEADER.ImageBase == IMAGE_BASE, "stock image base")
        for filename, entry in selection:
            report = json.loads((ROOT / "maps" / filename).read_text(encoding="utf-8"))
            matches = [item for item in report["functions"] if int(item["entry"], 16) == entry]
            require(len(matches) == 1, "unique retained function")
            cursor = entry
            for instruction in matches[0]["instructions"]:
                retained = bytes.fromhex(instruction["bytes"])
                address = int(instruction["address"], 16)
                require(address >= cursor, "ordered nonoverlapping stock instructions")
                cursor = address
                require(image.get_data(cursor - IMAGE_BASE, len(retained)) == retained,
                        "retained bytes agree with source")
                cursor += len(retained)
            functions[entry] = image.get_data(entry - IMAGE_BASE, cursor - entry)
    return functions


def assemble_guard() -> tuple[bytes, bytes]:
    assembler = Ks(KS_ARCH_X86, KS_MODE_64)
    detour, _ = assembler.asm("jmp 0x%x" % SCRATCH_CODE, GUARD_SITE)
    body, _ = assembler.asm(
        "mov r12, rax; xorps xmm0, xmm0; test r12, r12; "
        "jnz 0x%x; xor ebx, ebx; jmp 0x%x" % (GUARD_CONTINUE, EMPTY_RETURN),
        SCRATCH_CODE,
    )
    require(detour is not None and body is not None, "guard assembly")
    require(len(detour) == 5, "near detour length")
    return bytes(detour) + b"\x90", bytes(body)


def assemble_drain_guard() -> tuple[bytes, bytes]:
    assembler = Ks(KS_ARCH_X86, KS_MODE_64)
    detour, _ = assembler.asm("jmp 0x%x" % SCRATCH_CODE, 0x1406A9B6E)
    body, _ = assembler.asm(
        "mov r15d, eax; test eax, eax; jnz 0x1406a9be0; jmp 0x1406a9b73",
        SCRATCH_CODE,
    )
    require(detour is not None and body is not None, "drain guard assembly")
    require(len(detour) == 5, "drain near detour length")
    return bytes(detour), bytes(body)


def assemble_synchronous_entry() -> bytes:
    assembler = Ks(KS_ARCH_X86, KS_MODE_64)
    body, _ = assembler.asm("xor eax, eax; ret", GET_THREAD)
    require(body is not None and bytes(body) == bytes.fromhex("31c0c3"),
            "three-byte synchronous entry replacement")
    return bytes(body)


class AdmissionEmulator:
    def __init__(self, functions: dict[int, bytes], *, guarded: bool,
                 event: int, wait_result: int = 0, synchronous_result: int = 1,
                 synchronous_only: bool = False) -> None:
        require(not (guarded and synchronous_only), "select one admission candidate")
        self.synchronous_only = synchronous_only
        self.cpu = Uc(UC_ARCH_X86, UC_MODE_64)
        self.cpu.mem_map(IMAGE_BASE, 0x1000000)
        self.cpu.mem_map(SCRATCH_CODE, 0x1000)
        self.cpu.mem_map(FIXTURE, 0x20000)
        self.cpu.mem_map(STACK_BASE, 0x10000)
        for entry, code in functions.items():
            self.cpu.mem_write(entry, code)
        if synchronous_only:
            require(bytes(self.cpu.mem_read(GET_THREAD, 3)) == bytes.fromhex("488bc4"),
                    "whole GetThread entry instruction")
            self.cpu.mem_write(GET_THREAD, assemble_synchronous_entry())
        if guarded:
            require(bytes(self.cpu.mem_read(GUARD_SITE, 6)) == bytes.fromhex("4c8be00f57c0"),
                    "whole displaced instructions")
            detour, guard = assemble_guard()
            self.cpu.mem_write(GUARD_SITE, detour)
            self.cpu.mem_write(SCRATCH_CODE, guard)
        self.event = event
        self.wait_result = wait_result
        self.synchronous_result = synchronous_result
        self.calls: list[str] = []
        self.tracked: list[int] = []
        self.lock_depth = 0
        self.log_destructors = 0
        self.write(POOL + 8, WORKER_ARRAY)
        self.write(POOL + 0x20, AVAILABILITY)
        self.write(POOL + 0x38, 1, 4)
        self.write(POOL + 0x3C, 100, 4)
        self.write(WORKER_ARRAY, WORKER)
        self.write(AVAILABILITY, AVAILABILITY_HANDLE)
        self.write(WORKER + 0xA0, WORK_HANDLE)
        self.write(WORKER + 0xB8, 0xBAD0)
        self.write(DOCUMENT + 0x3924, 1, 4)
        self.write(DOCUMENT + 0x607C, 2, 4)
        self.write(DOCUMENT + 0x6080, 3, 1)
        self.before = bytes(self.cpu.mem_read(FIXTURE, 0x20000))
        self.cpu.hook_add(UC_HOOK_CODE, self.on_instruction)

    def write(self, address: int, value: int, size: int = 8) -> None:
        self.cpu.mem_write(address, value.to_bytes(size, "little"))

    def read(self, address: int, size: int = 8) -> int:
        return int.from_bytes(self.cpu.mem_read(address, size), "little")

    def on_instruction(self, cpu: Uc, address: int, size: int, user_data: object) -> None:
        if address == RETURN_SENTINEL:
            cpu.emu_stop()
            return
        opcode = bytes(cpu.mem_read(address, size))
        if opcode[0] == 0xE8:
            target = address + size + struct.unpack("<i", opcode[1:5])[0]
            if target == GET_THREAD:
                return
        elif opcode[:2] == b"\xff\x15":
            target = address + size + struct.unpack("<i", opcode[2:6])[0]
        else:
            return
        require(cpu.reg_read(registers.UC_X86_REG_RSP) % 16 == 0, "call stack alignment")
        argument = cpu.reg_read(registers.UC_X86_REG_RCX)
        result = 0
        if target in (0x140D5F100, 0x140D5F0F8, 0x140D532B8, 0x140D536B8,
                      0x140D53258, 0x140D532F8, 0x140D53300):
            pass
        elif target == 0x140D53250:
            self.log_destructors += 1
        elif target == 0x140D55020:
            self.calls.append("create_event")
            result = self.event
        elif target == 0x140D54FB0:
            self.calls.append("enter_lock")
            self.lock_depth += 1
        elif target == 0x140D54FA8:
            self.calls.append("leave_lock")
            self.lock_depth -= 1
            require(self.lock_depth >= 0, "no unmatched lock release")
        elif target == 0x140653BB0:
            self.calls.append("copy_availability")
            self.write(argument, COPIED_AVAILABILITY)
            self.write(argument + 8, COPIED_AVAILABILITY + 8)
            self.write(argument + 16, COPIED_AVAILABILITY + 8)
            self.write(COPIED_AVAILABILITY, AVAILABILITY_HANDLE)
        elif target == 0x140D55090:
            self.calls.append("wait_available")
            result = self.wait_result
        elif target == 0x140620730:
            self.calls.append("register_event")
            self.tracked.append(cpu.reg_read(registers.UC_X86_REG_R8))
        elif target == 0x140D54F18:
            self.calls.append("reset_available")
            require(argument == AVAILABILITY_HANDLE, "correct worker reservation")
            result = 1
        elif target == 0x140579780:
            self.calls.append("free_availability_copy")
        elif target == 0x1406A15D0:
            result = DOCUMENT
        elif target == 0x140D55028:
            self.calls.append("dispatch_event")
            require(argument == WORK_HANDLE, "correct dispatch event")
            result = 1
        elif target == 0x14069FCD0:
            self.calls.append("synchronous_treatment")
            require(argument == PRODUCTION, "synchronous production argument")
            require(cpu.reg_read(registers.UC_X86_REG_RDX) == 0x1111, "synchronous zone argument")
            require(cpu.reg_read(registers.UC_X86_REG_R8) == 0x2222, "synchronous result argument")
            result = self.synchronous_result
        else:
            raise RuntimeError("unmodeled call at 0x%x to 0x%x" % (address, target))
        self.finish_call(address, size, result)

    def finish_call(self, address: int, size: int, result: int) -> None:
        cpu = self.cpu
        for register in VOLATILE:
            cpu.reg_write(register, 0xABCD)
        for index in range(6):
            cpu.reg_write(getattr(registers, "UC_X86_REG_XMM%d" % index), 0xABCD)
        cpu.reg_write(registers.UC_X86_REG_RFLAGS, 0x202)
        cpu.reg_write(registers.UC_X86_REG_RAX, result)
        cpu.reg_write(registers.UC_X86_REG_RIP, address + size)

    def run(self, entry: int = DISPATCH) -> int:
        for register in NONVOLATILE:
            self.cpu.reg_write(register, 0x5678 + register)
        self.cpu.reg_write(registers.UC_X86_REG_RSP, STACK_TOP)
        self.cpu.reg_write(registers.UC_X86_REG_RCX, POOL if entry in (GET_THREAD, DRAIN) else PRODUCTION)
        argument = DOCUMENT if entry == DRAIN else (1 if entry == GET_THREAD else 0x1111)
        self.cpu.reg_write(registers.UC_X86_REG_RDX, argument)
        self.cpu.reg_write(registers.UC_X86_REG_R8, 0x2222)
        self.write(STACK_TOP, RETURN_SENTINEL)
        self.cpu.emu_start(entry, 0, count=2000)
        require(self.cpu.reg_read(registers.UC_X86_REG_RIP) == RETURN_SENTINEL,
                "bounded normal return")
        require(self.cpu.reg_read(registers.UC_X86_REG_RSP) == STACK_TOP + 8,
                "balanced stack")
        for register in NONVOLATILE:
            require(self.cpu.reg_read(register) == 0x5678 + register, "nonvolatile register preservation")
        require(self.lock_depth == 0, "balanced lock ownership")
        expected_destructors = 0 if self.synchronous_only else 1
        require(self.log_destructors == expected_destructors, "function logger lifetime")
        return self.cpu.reg_read(registers.UC_X86_REG_RAX)


class SynchronousBodyEmulator(AdmissionEmulator):
    def __init__(self, functions: dict[int, bytes], *, zone_result: int,
                 release_result: int, fail_at: str = "") -> None:
        super().__init__(functions, guarded=False, event=EVENT_HANDLE,
                         synchronous_only=True)
        self.zone_result = zone_result
        self.release_result = release_result
        self.fail_at = fail_at
        self.body_calls: list[str] = []
        self.cpu.mem_map(0x2000, 0x2000)
        self.transport = FIXTURE + 0xA000
        self.manager = FIXTURE + 0xC000
        self.write(PRODUCTION + 0xEB8, self.transport)
        self.write(self.transport, FIXTURE + 0xB000)
        self.write(0x2222 + 0x9F8, 7, 4)

    def on_instruction(self, cpu: Uc, address: int, size: int, user_data: object) -> None:
        if address == 0x14069FC94:
            require(cpu.reg_read(registers.UC_X86_REG_RCX) == PRODUCTION,
                    "real synchronous production argument")
            require(cpu.reg_read(registers.UC_X86_REG_RDX) == 0x1111,
                    "real synchronous zone argument")
            require(cpu.reg_read(registers.UC_X86_REG_R8) == 0x2222,
                    "real synchronous storage argument")
            require(cpu.reg_read(registers.UC_X86_REG_RSP) % 16 == 0,
                    "real synchronous call alignment")
            self.body_calls.append("synchronous_enter")
            return
        boundaries = {
            0x14069FD5E: ("acquisition_context", 0x3456),
            0x14069FD95: ("analysis_constructor", 0),
            0x14069FDAA: ("execute_zone", self.zone_result),
            0x14069FDD7: ("storage_manager", self.manager),
            0x14069FE0D: ("release_slot", self.release_result),
            0x14069FE2A: ("analysis_cleanup", 0),
        }
        if address in boundaries:
            name, result = boundaries[address]
            require(cpu.reg_read(registers.UC_X86_REG_RSP) % 16 == 0,
                    "synchronous helper call alignment")
            if name == "execute_zone":
                require(cpu.reg_read(registers.UC_X86_REG_RDX) == 0x1111,
                        "zone executor identity")
                require(cpu.reg_read(registers.UC_X86_REG_R8) == 0x222A,
                        "zone executor result offset")
            elif name == "storage_manager":
                require(cpu.reg_read(registers.UC_X86_REG_RCX) == self.transport,
                        "storage manager receiver")
            elif name == "release_slot":
                require(cpu.reg_read(registers.UC_X86_REG_RCX) == self.manager,
                        "release manager identity")
                require(cpu.reg_read(registers.UC_X86_REG_RDX) == 0x2222,
                        "released storage identity")
                require(cpu.reg_read(registers.UC_X86_REG_R9) == 7,
                        "released zone identifier")
            self.body_calls.append(name)
            if name == self.fail_at:
                raise RuntimeError("injected helper failure: " + name)
            self.finish_call(address, size, result)
            return
        markers = {
            0x14069FDAF: "execute_zone_returned",
            0x14069FDC7: "zone_failure_logged",
            0x14069FE12: "release_slot_returned",
            0x14069FE35: "synchronous_logger_destroyed",
            0x14069FE54: "synchronous_return",
        }
        if address in markers:
            self.body_calls.append(markers[address])
        super().on_instruction(cpu, address, size, user_data)


class DrainEmulator(AdmissionEmulator):
    def __init__(self, functions: dict[int, bytes], *, guarded: bool,
                 count: int, wait_results: list[int]) -> None:
        super().__init__(functions, guarded=False, event=EVENT_HANDLE)
        self.wait_results = list(wait_results)
        self.batches: list[list[int]] = []
        self.closed: list[int] = []
        self.clear_count = 0
        self.handles = [0x1000 + index for index in range(count)]
        self.write(POOL + 0x70, COMPLETION_ARRAY)
        self.write(POOL + 0x78, count)
        for index, handle in enumerate(self.handles):
            self.write(COMPLETION_ARRAY + index * 8, handle)
        self.cpu.mem_write(DOCUMENT + 0x18, struct.pack("<d", 100.0))
        self.before = bytes(self.cpu.mem_read(FIXTURE, 0x20000))
        if guarded:
            require(bytes(self.cpu.mem_read(0x1406A9B6E, 5)) == bytes.fromhex("448bf885c0"),
                    "whole drain displaced instructions")
            detour, guard = assemble_drain_guard()
            self.cpu.mem_write(0x1406A9B6E, detour)
            self.cpu.mem_write(SCRATCH_CODE, guard)

    def on_instruction(self, cpu: Uc, address: int, size: int, user_data: object) -> None:
        if address == 0x1406A9B68:
            require(self.lock_depth == 1, "pool lock held during drain")
            count = cpu.reg_read(registers.UC_X86_REG_RCX)
            pointer = cpu.reg_read(registers.UC_X86_REG_RDX)
            require(0 < count <= 64, "bounded Win32 batch")
            require(cpu.reg_read(registers.UC_X86_REG_R8) == 1, "wait-all semantics")
            require(cpu.reg_read(registers.UC_X86_REG_R9) == count * 100, "stock batch timeout")
            require(bool(self.wait_results), "no unexpected additional wait")
            self.batches.append([self.read(pointer + index * 8) for index in range(count)])
            self.finish_call(address, size, self.wait_results.pop(0))
        elif address == 0x1406A9B9A:
            self.closed.append(cpu.reg_read(registers.UC_X86_REG_RCX))
            self.finish_call(address, size, 1)
        elif address == 0x1406A9BBB:
            require(cpu.reg_read(registers.UC_X86_REG_RCX) == POOL + 0x68, "correct tracking array")
            self.clear_count += 1
            self.write(POOL + 0x78, 0)
            self.finish_call(address, size, 0)
        else:
            super().on_instruction(cpu, address, size, user_data)


class AdmissionGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.functions = verified_functions()

    def test_stock_null_event_reproduces_untracked_dispatch(self) -> None:
        emulator = AdmissionEmulator(self.functions, guarded=False, event=0)
        self.assertEqual(emulator.run(), 1)
        self.assertEqual(emulator.tracked, [0])
        self.assertIn("dispatch_event", emulator.calls)
        self.assertNotIn("synchronous_treatment", emulator.calls)
        self.assertEqual(emulator.read(WORKER + 0xB8), 0)

    def test_guard_null_event_returns_no_worker_before_pool_mutation(self) -> None:
        emulator = AdmissionEmulator(self.functions, guarded=True, event=0)
        self.assertEqual(emulator.run(GET_THREAD), 0)
        self.assertEqual(emulator.calls, ["create_event"])
        self.assertEqual(emulator.tracked, [])
        self.assertEqual(bytes(emulator.cpu.mem_read(FIXTURE, 0x20000)), emulator.before)

    def test_guard_null_event_preserves_synchronous_result(self) -> None:
        for result in (0, 1):
            with self.subTest(result=result):
                emulator = AdmissionEmulator(self.functions, guarded=True, event=0,
                                            synchronous_result=result)
                self.assertEqual(emulator.run(), result)
                self.assertEqual(emulator.calls, ["create_event", "synchronous_treatment"])
                self.assertEqual(emulator.tracked, [])
                self.assertEqual(bytes(emulator.cpu.mem_read(FIXTURE, 0x20000)), emulator.before)

    def test_guard_valid_event_preserves_stock_success_and_no_worker_paths(self) -> None:
        for wait_result in (0, 0x102, 0xFFFFFFFF, 1):
            with self.subTest(wait_result=wait_result):
                stock = AdmissionEmulator(self.functions, guarded=False, event=EVENT_HANDLE,
                                          wait_result=wait_result)
                guarded = AdmissionEmulator(self.functions, guarded=True, event=EVENT_HANDLE,
                                            wait_result=wait_result)
                self.assertEqual(guarded.run(), stock.run())
                self.assertEqual(guarded.calls, stock.calls)
                self.assertEqual(guarded.tracked, stock.tracked)
                self.assertEqual(bytes(guarded.cpu.mem_read(FIXTURE, 0x20000)),
                                 bytes(stock.cpu.mem_read(FIXTURE, 0x20000)))


class SynchronousContainmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.functions = verified_functions()

    def test_entry_returns_without_accessing_pool_or_calling_helpers(self) -> None:
        emulator = AdmissionEmulator(self.functions, guarded=False, event=EVENT_HANDLE,
                                     synchronous_only=True)
        emulator.cpu.mem_unmap(FIXTURE, 0x20000)
        self.assertEqual(emulator.run(GET_THREAD), 0)
        self.assertEqual(emulator.calls, [])
        self.assertEqual(emulator.tracked, [])

    def test_single_lane_receiver_routes_every_execution_path_to_synchronous_work(self) -> None:
        reports = {
            GET_THREAD: "rev2a_entry_gate_pool.json",
            DISPATCH: "rev2a_entry_gate_second_pass.json",
            SYNCHRONOUS: "rev2a_entry_gate_workers.json",
        }
        expected_calls = {
            GET_THREAD: {(DISPATCH, 0x14069FBFD)},
            DISPATCH: {(RECEIVER, 0x1406A8F32), (RECEIVER, 0x1406A9104)},
            SYNCHRONOUS: {
                (DISPATCH, 0x14069FC94),
                (RECEIVER, 0x1406A8EDA),
                (RECEIVER, 0x1406A90E1),
            },
        }
        for entry, filename in reports.items():
            report = json.loads((ROOT / "maps" / filename).read_text(encoding="utf-8"))
            match = [item for item in report["functions"] if int(item["entry"], 16) == entry]
            require(len(match) == 1, "unique caller-coverage function")
            calls = {
                (int(reference["caller"], 16), int(reference["from"], 16))
                for reference in match[0]["incoming"]
                if reference["type"] == "UNCONDITIONAL_CALL"
            }
            self.assertEqual(calls, expected_calls[entry])
            data = [reference for reference in match[0]["incoming"]
                    if reference["type"] == "DATA"]
            self.assertEqual(len(data), 2)
            self.assertTrue(all(reference["caller"] is None for reference in data))

        receiver = self.functions[RECEIVER]

        def stock(address: int, retained: str) -> None:
            expected = bytes.fromhex(retained)
            offset = address - RECEIVER
            self.assertEqual(receiver[offset:offset + len(expected)], expected)

        for address, retained in (
            (0x1406A8E98, "80be580f000000"),
            (0x1406A8E9F, "754f"),
            (0x1406A8EDA, "e8f16dffff"),
            (0x1406A8EF0, "83bee817000000"),
            (0x1406A8EF7, "7563"),
            (0x1406A8F32, "e8496cffff"),
            (0x1406A90C9, "448b8ee8170000"),
            (0x1406A90D0, "4183f902"),
            (0x1406A90D4, "751d"),
            (0x1406A90E1, "e8ea6bffff"),
            (0x1406A90F3, "4183f901"),
            (0x1406A90F7, "7536"),
            (0x1406A9104, "e8776affff"),
        ):
            stock(address, retained)

    def test_dispatch_uses_only_synchronous_fallback_for_all_modeled_outcomes(self) -> None:
        for event in (0, EVENT_HANDLE):
            for wait_result in (0, 0x102, 0xFFFFFFFF, 1):
                for result in (0, 1):
                    with self.subTest(event=event, wait_result=wait_result, result=result):
                        emulator = AdmissionEmulator(
                            self.functions, guarded=False, event=event,
                            wait_result=wait_result, synchronous_result=result,
                            synchronous_only=True)
                        self.assertEqual(emulator.run(), result)
                        self.assertEqual(emulator.calls, ["synchronous_treatment"])
                        self.assertEqual(emulator.tracked, [])
                        self.assertEqual(bytes(emulator.cpu.mem_read(FIXTURE, 0x20000)),
                                         emulator.before)

    def test_repeated_dispatch_does_not_erase_preexisting_work(self) -> None:
        emulator = AdmissionEmulator(self.functions, guarded=False, event=EVENT_HANDLE,
                                     synchronous_only=True)
        emulator.write(POOL + 0x70, COMPLETION_ARRAY)
        emulator.write(POOL + 0x78, 1)
        emulator.write(COMPLETION_ARRAY, EVENT_HANDLE)
        before = bytes(emulator.cpu.mem_read(FIXTURE, 0x20000))
        for result in (1, 0, 1):
            emulator.synchronous_result = result
            self.assertEqual(emulator.run(), result)
            self.assertEqual(bytes(emulator.cpu.mem_read(FIXTURE, 0x20000)), before)
        self.assertEqual(emulator.calls, ["synchronous_treatment"] * 3)
        self.assertEqual(emulator.tracked, [])

    def test_entry_byte_mismatch_is_rejected(self) -> None:
        functions = dict(self.functions)
        functions[GET_THREAD] = b"\x90" + functions[GET_THREAD][1:]
        with self.assertRaisesRegex(RuntimeError, "whole GetThread entry instruction"):
            AdmissionEmulator(functions, guarded=False, event=EVENT_HANDLE,
                              synchronous_only=True)


@unittest.skipUnless(os.name == "nt" and platform.machine().upper() == "AMD64",
                     "requires native Windows AMD64 virtual unwind")
class SynchronousEntryUnwindTests(unittest.TestCase):
    def test_stock_metadata_unwinds_reachable_entry_boundaries(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        require(hashlib.sha256(source).hexdigest() == SOURCE_HASH, "unwind source identity")
        with pefile.PE(data=source) as image:
            entries = [item.struct for item in image.DIRECTORY_ENTRY_EXCEPTION
                       if item.struct.BeginAddress == GET_THREAD - IMAGE_BASE]
            require(len(entries) == 1, "unique GetThread runtime function")
            entry = entries[0]
            require((entry.BeginAddress, entry.EndAddress, entry.UnwindData)
                    == (0x6A1660, 0x6A1837, 0xFD7BB8), "stock runtime function bounds")
            require(image.get_data(entry.UnwindData, 24).hex()
                    == "11220a00225419001e34170012f20bf009e007c005700460",
                    "stock version-one prologue unwind codes")
            mapped = image.get_memory_mapped_image()
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.VirtualAlloc.argtypes = [ctypes.c_void_p, ctypes.c_size_t,
                                        ctypes.c_uint32, ctypes.c_uint32]
        kernel.VirtualAlloc.restype = ctypes.c_void_p
        kernel.VirtualFree.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint32]
        kernel.VirtualFree.restype = ctypes.c_int
        native = ctypes.WinDLL("ntdll")
        native.RtlVirtualUnwind.argtypes = [
            ctypes.c_uint32, ctypes.c_uint64, ctypes.c_uint64, ctypes.c_void_p,
            ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p),
            ctypes.POINTER(ctypes.c_uint64), ctypes.c_void_p,
        ]
        native.RtlVirtualUnwind.restype = ctypes.c_void_p
        allocation = kernel.VirtualAlloc(None, len(mapped), 0x3000, 0x04)
        require(bool(allocation), "non-executable image allocation")
        try:
            ctypes.memmove(allocation, mapped, len(mapped))
            runtime = (ctypes.c_uint32 * 3)(entry.BeginAddress, entry.EndAddress, entry.UnwindData)
            stack = ctypes.create_string_buffer(0x1000)
            stack_pointer = ((ctypes.addressof(stack) + 0x800) & ~15) + 8
            caller = 0x123456789ABC
            ctypes.c_uint64.from_address(stack_pointer).value = caller
            nonvolatile_offsets = (144, 160, 168, 176, 216, 224, 232, 240)
            for candidate, offsets in ((False, (0, 3)), (True, (0, 2))):
                if candidate:
                    ctypes.memmove(allocation + entry.BeginAddress,
                                   assemble_synchronous_entry(), 3)
                for offset in offsets:
                    with self.subTest(candidate=candidate, offset=offset):
                        storage = ctypes.create_string_buffer(1232 + 15)
                        context_address = (ctypes.addressof(storage) + 15) & ~15
                        context = (ctypes.c_ubyte * 1232).from_address(context_address)
                        control_pc = allocation + entry.BeginAddress + offset
                        struct.pack_into("<I", context, 48, 0x10000B)
                        struct.pack_into("<Q", context, 120, 0 if candidate else stack_pointer)
                        struct.pack_into("<Q", context, 152, stack_pointer)
                        struct.pack_into("<Q", context, 248, control_pc)
                        for register_offset in nonvolatile_offsets:
                            struct.pack_into("<Q", context, register_offset, 0x5000 + register_offset)
                        for index in range(6, 16):
                            struct.pack_into("<QQ", context, 416 + 16 * index, index, index + 100)
                        vectors_before = bytes(context[512:672])
                        handler_data = ctypes.c_void_p()
                        frame = ctypes.c_uint64()
                        handler = native.RtlVirtualUnwind(
                            0, allocation, control_pc, ctypes.byref(runtime), context_address,
                            ctypes.byref(handler_data), ctypes.byref(frame), None)
                        self.assertIsNone(handler)
                        self.assertEqual(struct.unpack_from("<Q", context, 248)[0], caller)
                        self.assertEqual(struct.unpack_from("<Q", context, 152)[0], stack_pointer + 8)
                        for register_offset in nonvolatile_offsets:
                            self.assertEqual(struct.unpack_from("<Q", context, register_offset)[0],
                                             0x5000 + register_offset)
                        self.assertEqual(bytes(context[512:672]), vectors_before)
        finally:
            require(bool(kernel.VirtualFree(allocation, 0, 0x8000)), "release non-executable image")


class SynchronousBodyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.functions = verified_functions()

    def test_callers_and_release_unwind_without_local_catch(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        with pefile.PE(data=source) as image:
            for begin, end, unwind_rva, info_rva, expected_info, call_sites in (
                (0x578DD0, 0x578EAD, 0xF767B8, 0xE5E9A8,
                 (0x19930522, 3, 0xF81B70, 0, 0, 4, 0xF767D8, 0x20, 0, 1),
                 ((0x578E4F, 0x578C80, [0x7B9D4E]),)),
                (0x66D9E0, 0x66DADC, 0xFC79D0, 0xE9E0E8,
                 (0x19930522, 3, 0xFC79EC, 0, 0, 4, 0xFC7A08, 0x38, 0, 1),
                 ((0x66DA82, 0x578DD0, [0x7F66AE]),)),
                (0x69FB80, 0x69FCC2, 0xFD4D28, 0xEA8088,
                 (0x19930522, 3, 0xFD4D48, 0, 0, 4, 0xFD4D60, 0x30, 0, 1),
                 ((0x69FC94, 0x69FCD0, [0x7FCFFE]),)),
                (0x6A88E0, 0x6A95AE, 0xFD7490, 0xEA85B0,
                 (0x19930522, 32, 0xFD74C8, 0, 0, 55, 0xFD75D0, 0x150, 0, 1),
                 ((0x6A8F32, 0x69FB80, [0x7FDF98, 0x7FDF54, 0x7FDF38, 0x7FDF0E]),
                  (0x6A9104, 0x69FB80, [0x7FDF54, 0x7FDF38, 0x7FDF0E]))),
            ):
                with self.subTest(function=hex(begin)):
                    entries = [item.struct for item in image.DIRECTORY_ENTRY_EXCEPTION
                               if item.struct.BeginAddress == begin]
                    self.assertEqual(len(entries), 1)
                    self.assertEqual((entries[0].EndAddress, entries[0].UnwindData), (end, unwind_rva))
                    header = image.get_data(unwind_rva, 4)
                    self.assertEqual(header[0], 0x11)
                    tail = unwind_rva + 4 + ((header[2] + 1) & ~1) * 2
                    self.assertEqual(struct.unpack("<II", image.get_data(tail, 8)), (0x7A6232, info_rva))
                    info = struct.unpack("<10I", image.get_data(info_rva, 40))
                    self.assertEqual(info, expected_info)
                    self.assertEqual(info[3:5], (0, 0))
                    unwind = [struct.unpack("<iI", image.get_data(info[2] + index * 8, 8))
                              for index in range(info[1])]
                    ip_states = [struct.unpack("<Ii", image.get_data(info[6] + index * 8, 8))
                                 for index in range(info[5])]
                    for call, target, expected_actions in call_sites:
                        self.assertEqual(image.get_data(call, 5), b"\xe8" + struct.pack("<i", target - call - 5))
                        state = next(state for ip, state in reversed(ip_states) if ip <= call + 4)
                        actions = []
                        while state != -1:
                            self.assertLess(len(actions), len(unwind))
                            self.assertGreaterEqual(state, 0)
                            self.assertLess(state, len(unwind))
                            state, action = unwind[state]
                            actions.append(action)
                        self.assertEqual(actions, expected_actions)

    def test_slot_release_mutates_before_delete_and_retry_decrements_again(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        report = json.loads((ROOT / "maps" / "rev2a_synchronous_slot_release.json")
                            .read_text(encoding="utf-8"))
        self.assertEqual(report["source_sha256"], SOURCE_HASH)
        self.assertEqual([function["entry"] for function in report["functions"]], ["140578dd0"])
        code = {}
        with pefile.PE(data=source, fast_load=True) as image:
            for instruction in report["functions"][0]["instructions"]:
                address = int(instruction["address"], 16)
                retained = bytes.fromhex(instruction["bytes"])
                self.assertEqual(image.get_data(address - IMAGE_BASE, len(retained)), retained)
                code[address] = retained
        slot = FIXTURE + 0x2000
        boundaries = {0x140578E04: "string_construct", 0x140578E1C: "logger_construct",
                      0x140578E28: "string_destroy", 0x140578E4F: "slot_delete",
                      0x140578E6F: "delete_failure_log", 0x140578E83: "delete_success_log",
                      0x140578E8F: "logger_destroy"}
        for initial, force, delete_result, failure, repeat in (
            (2, 0, 1, "", False), (1, 0, 1, "", False),
            (1, 0, 0, "", False), (0, 0, 0, "", False),
            (2, 1, 1, "", False), (1, 0, 1, "logger_construct", False),
            (1, 0, 1, "slot_delete", False), (1, 0, 0, "delete_failure_log", False),
            (1, 0, 1, "delete_success_log", False), (1, 0, 1, "logger_destroy", False),
            (1, 0, 1, "delete_success_log", True),
        ):
            with self.subTest(initial=initial, force=force, result=delete_result,
                              failure=failure, repeat=repeat):
                cpu = Uc(UC_ARCH_X86, UC_MODE_64)
                cpu.mem_map(0x140578000, 0x1000)
                cpu.mem_map(FIXTURE, 0x10000)
                cpu.mem_map(STACK_BASE, 0x10000)
                cpu.mem_map(SCRATCH_CODE, 0x1000)
                for address, retained in code.items():
                    cpu.mem_write(address, retained)
                cpu.mem_write(slot + 0xC80, struct.pack("<i", initial))
                observed = []
                active_failure = failure
                preserved = {register: 0x51000000 + index * 0x100
                             for index, register in enumerate(NONVOLATILE)}

                def on_instruction(machine: Uc, address: int, size: int,
                                   user_data: object) -> None:
                    if address == RETURN_SENTINEL:
                        machine.emu_stop()
                        return
                    require(address in code, "only retained slot-release instructions execute")
                    if address not in boundaries:
                        return
                    self.assertEqual(machine.reg_read(registers.UC_X86_REG_RSP) % 16, 0)
                    name = boundaries[address]
                    observed.append(name)
                    if name == "slot_delete":
                        self.assertEqual(machine.reg_read(registers.UC_X86_REG_RCX), FIXTURE)
                        self.assertEqual(machine.reg_read(registers.UC_X86_REG_RDX), slot)
                        self.assertEqual(machine.reg_read(registers.UC_X86_REG_R8), force)
                    if name == active_failure:
                        raise RuntimeError("injected helper failure: " + name)
                    for register in VOLATILE:
                        machine.reg_write(register, 0xDEAD0000)
                    machine.reg_write(registers.UC_X86_REG_RAX,
                                      delete_result if name == "slot_delete" else 0)
                    machine.reg_write(registers.UC_X86_REG_RIP, address + size)

                cpu.hook_add(UC_HOOK_CODE, on_instruction)
                for attempt in range(2 if repeat else 1):
                    for register, value in preserved.items():
                        cpu.reg_write(register, value)
                    cpu.reg_write(registers.UC_X86_REG_RSP, STACK_TOP)
                    cpu.mem_write(STACK_TOP, struct.pack("<Q", RETURN_SENTINEL))
                    cpu.reg_write(registers.UC_X86_REG_RCX, FIXTURE)
                    cpu.reg_write(registers.UC_X86_REG_RDX, slot)
                    cpu.reg_write(registers.UC_X86_REG_R8, force)
                    if active_failure:
                        with self.assertRaisesRegex(RuntimeError, "injected helper failure: " + active_failure):
                            cpu.emu_start(0x140578DD0, RETURN_SENTINEL + 1, count=100)
                        self.assertNotEqual(cpu.reg_read(registers.UC_X86_REG_RIP), RETURN_SENTINEL)
                    else:
                        cpu.emu_start(0x140578DD0, RETURN_SENTINEL + 1, count=100)
                        self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RIP), RETURN_SENTINEL)
                        self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RSP), STACK_TOP + 8)
                        self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RAX) & 0xFF,
                                         delete_result if initial <= 1 or force else 1)
                        for register, value in preserved.items():
                            self.assertEqual(cpu.reg_read(register), value)
                    expected_count = initial if active_failure == "logger_construct" else initial - attempt - 1
                    self.assertEqual(struct.unpack("<i", cpu.mem_read(slot + 0xC80, 4))[0], expected_count)
                    active_failure = ""
                self.assertEqual(observed.count("slot_delete"),
                                 2 if repeat else int(failure != "logger_construct" and (initial <= 1 or force)))

    def test_slot_delete_exception_boundaries_and_ignored_signal_failure(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        report = json.loads((ROOT / "maps" / "rev2a_synchronous_slot_retirement.json")
                            .read_text(encoding="utf-8"))
        self.assertEqual(report["source_sha256"], SOURCE_HASH)
        self.assertEqual({function["entry"] for function in report["functions"]},
                         {"140578c80", "14051f150"})
        code = {}
        with pefile.PE(data=source) as image:
            for function in report["functions"]:
                for instruction in function["instructions"]:
                    address = int(instruction["address"], 16)
                    retained = bytes.fromhex(instruction["bytes"])
                    self.assertEqual(image.get_data(address - IMAGE_BASE, len(retained)), retained)
                    code[address] = retained
            entries = [item.struct for item in image.DIRECTORY_ENTRY_EXCEPTION
                       if item.struct.BeginAddress == 0x578C80]
            self.assertEqual(len(entries), 1)
            self.assertEqual((entries[0].EndAddress, entries[0].UnwindData), (0x578DCD, 0xF76748))
            self.assertEqual(image.get_data(0xF76748, 4), bytes.fromhex("111f0900"))
            self.assertEqual(struct.unpack("<II", image.get_data(0xF76760, 8)), (0x7A6232, 0xE5E980))
            self.assertEqual(struct.unpack("<10I", image.get_data(0xE5E980, 40)),
                             (0x19930522, 4, 0xF76768, 0, 0, 6, 0xF76788, 0x20, 0, 1))
            self.assertEqual([struct.unpack("<iI", image.get_data(0xF76768 + index * 8, 8))
                              for index in range(4)],
                             [(-1, 0x7D05A0), (0, 0x7D05AE), (-1, 0x7D05AE), (2, 0x7D05BC)])
            self.assertEqual([struct.unpack("<Ii", image.get_data(0xF76788 + index * 8, 8))
                              for index in range(6)],
                             [(0x578C80, -1), (0x578CBB, 0), (0x578CD6, 2),
                              (0x578D45, 3), (0x578D57, 2), (0x578DA6, -1)])
            for address, retained in (
                (0x7D05A0, "488d8a080d000048ff254aeb5800"),
                (0x7D05AE, "488d8a2800000048ff25942c5800"),
                (0x7D05BC, "488d8a5000000048ff251e1e5800"),
            ):
                self.assertEqual(image.get_data(address, 14), bytes.fromhex(retained))
        slot, head, node, record = FIXTURE + 0x2000, FIXTURE + 0x4000, FIXTURE + 0x4100, FIXTURE + 0x4200
        boundaries = {0x140578CB4: "string_construct", 0x140578CCF: "logger_construct",
                      0x140578CDE: "string_destroy", 0x140578D02: "reference_log",
                      0x140578D14: "enter", 0x140578D3E: "storage_construct",
                      0x140578D50: "storage_assign", 0x140578D5C: "storage_destroy",
                      0x140578D77: "leave", 0x140578D9F: "signal", 0x140578DAB: "logger_destroy"}
        for initial, found, force, failure, signal_result in (
            (0, True, 0, "", 1), (0, True, 0, "", 0), (0, False, 0, "", 1),
            (1, True, 0, "", 1), (1, True, 1, "", 1),
            (0, True, 0, "storage_construct", 1), (0, True, 0, "storage_assign", 1),
            (0, True, 0, "storage_destroy", 1), (0, True, 0, "logger_destroy", 1),
        ):
            with self.subTest(initial=initial, found=found, force=force, failure=failure, signal=signal_result):
                cpu = Uc(UC_ARCH_X86, UC_MODE_64)
                for page in {address & ~0xFFF for address in code}:
                    cpu.mem_map(page, 0x1000)
                cpu.mem_map(FIXTURE, 0x10000)
                cpu.mem_map(STACK_BASE, 0x10000)
                cpu.mem_map(SCRATCH_CODE, 0x1000)
                for address, retained in code.items():
                    cpu.mem_write(address, retained)
                for address, value in ((FIXTURE + 0x80, head), (head, node if found else head),
                                       (node, head), (node + 0x10, record), (record + 0x10, slot),
                                       (FIXTURE + 0x78, 0x1234), (STACK_TOP, RETURN_SENTINEL)):
                    cpu.mem_write(address, struct.pack("<Q", value))
                cpu.mem_write(slot + 0xC80, struct.pack("<i", initial))
                cpu.reg_write(registers.UC_X86_REG_RSP, STACK_TOP)
                cpu.reg_write(registers.UC_X86_REG_RCX, FIXTURE)
                cpu.reg_write(registers.UC_X86_REG_RDX, slot)
                cpu.reg_write(registers.UC_X86_REG_R8, force)
                preserved = {register: 0x52000000 + index * 0x100
                             for index, register in enumerate(NONVOLATILE)}
                for register, value in preserved.items():
                    cpu.reg_write(register, value)
                observed = []
                lock_depth = 0
                temporary = STACK_TOP - 0xCE8 + 0x50

                def on_instruction(machine: Uc, address: int, size: int, user_data: object) -> None:
                    nonlocal lock_depth
                    if address == RETURN_SENTINEL:
                        machine.emu_stop()
                        return
                    require(address in code, "only retained slot-delete instructions execute")
                    if address not in boundaries:
                        return
                    self.assertEqual(machine.reg_read(registers.UC_X86_REG_RSP) % 16, 0)
                    name = boundaries[address]
                    observed.append(name)
                    if name in ("enter", "leave"):
                        self.assertEqual(machine.reg_read(registers.UC_X86_REG_RCX), FIXTURE + 0x48)
                        self.assertEqual(lock_depth, int(name == "leave"))
                        lock_depth += 1 if name == "enter" else -1
                    if name.startswith("storage_"):
                        self.assertEqual(lock_depth, 1)
                        self.assertEqual(machine.reg_read(registers.UC_X86_REG_RCX),
                                         slot + 8 if name == "storage_assign" else temporary)
                        if name == "storage_assign":
                            self.assertEqual(machine.reg_read(registers.UC_X86_REG_RDX), temporary)
                    if name == "signal":
                        self.assertEqual(lock_depth, 0)
                        self.assertEqual(machine.reg_read(registers.UC_X86_REG_RCX), 0x1234)
                        self.assertEqual(machine.reg_read(registers.UC_X86_REG_RDX), 1)
                        self.assertEqual(bytes(machine.mem_read(record + 8, 1)), b"\x01")
                        self.assertEqual(bytes(machine.mem_read(slot + 0xC80, 4)), bytes(4))
                    if name == failure:
                        raise RuntimeError("injected helper failure: " + name)
                    for register in VOLATILE:
                        machine.reg_write(register, 0xDEAD0000)
                    machine.reg_write(registers.UC_X86_REG_RAX,
                                      temporary if name == "storage_construct" else signal_result if name == "signal" else 0)
                    machine.reg_write(registers.UC_X86_REG_RIP, address + size)

                cpu.hook_add(UC_HOOK_CODE, on_instruction)
                if failure:
                    with self.assertRaisesRegex(RuntimeError, "injected helper failure: " + failure):
                        cpu.emu_start(0x140578C80, RETURN_SENTINEL + 1, count=150)
                    self.assertNotEqual(cpu.reg_read(registers.UC_X86_REG_RIP), RETURN_SENTINEL)
                else:
                    cpu.emu_start(0x140578C80, RETURN_SENTINEL + 1, count=150)
                    self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RIP), RETURN_SENTINEL)
                    self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RSP), STACK_TOP + 8)
                    self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RAX) & 0xFF, int(found and (initial <= 0 or force)))
                    for register, value in preserved.items():
                        self.assertEqual(cpu.reg_read(register), value)
                storage_failure = failure.startswith("storage_")
                committed = found and (initial <= 0 or force) and not storage_failure
                self.assertEqual(lock_depth, int(storage_failure))
                self.assertEqual(bytes(cpu.mem_read(record + 8, 1)), bytes([int(committed)]))
                self.assertEqual(struct.unpack("<i", cpu.mem_read(slot + 0xC80, 4))[0], 0 if committed else initial)
                self.assertEqual(observed.count("signal"), int(committed))

    def test_zone_storage_constructor_throws_bad_alloc_before_slot_unlock(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        library_bytes = (ROOT / "v3d_files_" / "AvImgBuffer.dll").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        self.assertEqual(hashlib.sha256(library_bytes).hexdigest(),
                         "6a73a7f28ff8911fd1b7693fe97e70fdbff925a57805879bbadb43b10bc90d7f")
        report = json.loads((ROOT / "maps" / "rev2a_synchronous_slot_retirement.json")
                            .read_text(encoding="utf-8"))
        instructions = {item["address"]: item["text"]
                        for function in report["functions"] for item in function["instructions"]}
        self.assertEqual(instructions["140578d14"], "CALL qword ptr [0x140d54fb0]")
        self.assertEqual(instructions["140578d3e"], "CALL qword ptr [0x140d523f0]")
        self.assertEqual(instructions["140578d50"], "CALL qword ptr [0x140d52100]")
        self.assertEqual(instructions["140578d5c"], "CALL qword ptr [0x140d523e8]")
        self.assertEqual(instructions["140578d77"], "CALL qword ptr [0x140d54fa8]")
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image, pefile.PE(
                    data=library_bytes, fast_load=True) as library:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                library.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
                self.assertEqual(library.FILE_HEADER.Machine, 0x8664)
                self.assertEqual(library.OPTIONAL_HEADER.ImageBase, 0x180000000)
                exports = {symbol.name.decode(): symbol.address
                           for symbol in library.DIRECTORY_ENTRY_EXPORT.symbols if symbol.name}
                self.assertEqual(exports["??0CZoneStorage@@QEAA@XZ"], 0x5AE00)
                self.assertEqual(exports["??4CZoneStorage@@QEAAAEAV0@AEBV0@@Z"], 0x5B740)
                self.assertEqual(exports["??1CZoneStorage@@UEAA@XZ"], 0x5B0D0)
                exe_imports = {item.address: item.name.decode()
                               for entry in image.DIRECTORY_ENTRY_IMPORT
                               for item in entry.imports if item.name}
                self.assertEqual(exe_imports[0x140D523F0], b"??0CZoneStorage@@QEAA@XZ".decode())
                self.assertEqual(exe_imports[0x140D52100], "??4CZoneStorage@@QEAAAEAV0@AEBV0@@Z")
                self.assertEqual(exe_imports[0x140D523E8], "??1CZoneStorage@@UEAA@XZ")
                self.assertEqual(exe_imports[0x140D54FB0], "EnterCriticalSection")
                self.assertEqual(exe_imports[0x140D54FA8], "LeaveCriticalSection")
                library_imports = {item.address: item.name.decode() if item.name else str(item.ordinal)
                                   for entry in library.DIRECTORY_ENTRY_IMPORT for item in entry.imports}

                def personality(function_rva):
                    entry = next(item.struct for item in library.DIRECTORY_ENTRY_EXCEPTION
                                 if item.struct.BeginAddress == function_rva)
                    header = library.get_data(entry.UnwindData, 4)
                    data_rva = entry.UnwindData + 4 + ((header[2] + 1) & ~1) * 2
                    handler, language = struct.unpack("<II", library.get_data(data_rva, 8))
                    slot_bytes = library.get_data(handler, 6)
                    self.assertEqual(slot_bytes[:2], b"\xff\x25")
                    displacement = struct.unpack_from("<i", slot_bytes, 2)[0]
                    return header[0] >> 3, library_imports[0x180000000 + handler + 6 + displacement], language

                constructor_flags, constructor_handler, constructor_info = personality(0x5AE00)
                self.assertEqual((constructor_flags, constructor_handler), (2, "__CxxFrameHandler3"))
                info = struct.unpack("<IiIIIIIiII", library.get_data(constructor_info, 40))
                self.assertEqual(info[0], 0x19930522)
                self.assertEqual((info[1], info[3], info[9]), (15, 0, 1))
                ip_states = [struct.unpack("<Ii", library.get_data(info[6] + index * 8, 8))
                             for index in range(info[5])]
                allocation_call = 0x5AEDD
                self.assertEqual(library.get_data(allocation_call, 1), b"\xe8")
                relative = struct.unpack_from("<i", library.get_data(allocation_call, 5), 1)[0]
                self.assertEqual(allocation_call + 5 + relative, 0x398B0)
                state_during_allocation = next(state for ip, state in reversed(ip_states)
                                               if ip <= allocation_call)
                self.assertGreaterEqual(state_during_allocation, 0)
                node_call = struct.unpack_from("<i", library.get_data(0x398C7, 5), 1)[0]
                self.assertEqual(library.get_data(0x398C7, 1), b"\xe8")
                self.assertEqual(0x398C7 + 5 + node_call, 0x5D360)
                self.assertEqual(library_imports[0x180000000 + 0x5D369 + 6 + struct.unpack_from(
                    "<i", library.get_data(0x5D369, 6), 2)[0]], "malloc")
                self.assertEqual(library_imports[0x180000000 + 0x5D377 + 6 + struct.unpack_from(
                    "<i", library.get_data(0x5D377, 6), 2)[0]], "_callnewh")
                throw_relative = struct.unpack_from("<i", library.get_data(0x5D447, 5), 1)[0]
                self.assertEqual(library.get_data(0x5D447, 1), b"\xe8")
                throw = 0x5D447 + 5 + throw_relative
                throw_bytes = library.get_data(throw, 6)
                self.assertEqual(throw_bytes[:2], b"\xff\x25")
                throw_slot = throw + 6 + struct.unpack_from("<i", throw_bytes, 2)[0]
                self.assertEqual(library_imports[0x180000000 + throw_slot], "_CxxThrowException")
                type_displacement = struct.unpack_from("<i", library.get_data(0x5D39E, 7), 3)[0]
                type_site = 0x5D39E + 7 + type_displacement
                self.assertIn(b"bad allocation\x00", library.get_data(type_site, 48))
                destructor_flags, destructor_handler, destructor_info = personality(0x5B0D0)
                self.assertEqual((destructor_flags, destructor_handler), (3, "__CxxFrameHandler3"))
                destructor = struct.unpack("<IiIIIIIiII", library.get_data(destructor_info, 40))
                self.assertEqual((destructor[0], destructor[3], destructor[9]), (0x19930522, 0, 5))
                assign = next(item.struct for item in library.DIRECTORY_ENTRY_EXCEPTION
                              if item.struct.BeginAddress == 0x5B740)
                self.assertEqual(library.get_data(assign.UnwindData, 1)[0] >> 3, 0)
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_receiver_unwind_releases_noexcept_zone_data(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        library_bytes = (ROOT / "v3d_files_" / "HwCommonTools.dll").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        self.assertEqual(hashlib.sha256(library_bytes).hexdigest(),
                         "92f6b2b9f51616162de5184cee9fdccceb1f3c798ee0b65e0886c95fdfb20f15")
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image, pefile.PE(
                    data=library_bytes, fast_load=True) as library:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
                library.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
                self.assertEqual(library.FILE_HEADER.Machine, 0x8664)
                self.assertEqual(library.OPTIONAL_HEADER.ImageBase, 0x180000000)
                exports = {symbol.name.decode(): symbol.address
                           for symbol in library.DIRECTORY_ENTRY_EXPORT.symbols if symbol.name}
                self.assertEqual(exports["??1CZoneData@@QEAA@XZ"], 0x24C40)
                self.assertEqual(exports["??0CZoneData@@QEAA@_KAEBVCViUnitSize@@@Z"], 0x25D20)
                library_imports = {item.address: item.name.decode() if item.name else str(item.ordinal)
                                   for entry in library.DIRECTORY_ENTRY_IMPORT for item in entry.imports}

                def personality(program, function_rva, image_base, imports):
                    entry = next(item.struct for item in program.DIRECTORY_ENTRY_EXCEPTION
                                 if item.struct.BeginAddress == function_rva)
                    header = program.get_data(entry.UnwindData, 4)
                    data_rva = entry.UnwindData + 4 + ((header[2] + 1) & ~1) * 2
                    handler, language = struct.unpack("<II", program.get_data(data_rva, 8))
                    slot_bytes = program.get_data(handler, 6)
                    self.assertEqual(slot_bytes[:2], b"\xff\x25")
                    displacement = struct.unpack_from("<i", slot_bytes, 2)[0]
                    return (header[0] >> 3,
                            imports[image_base + handler + 6 + displacement],
                            language)

                flags, handler, info_rva = personality(
                    library, 0x24C40, 0x180000000, library_imports)
                self.assertEqual((flags, handler), (3, "__CxxFrameHandler3"))
                info = struct.unpack("<IiIIIIIiII", library.get_data(info_rva, 40))
                self.assertEqual((info[0], info[1], info[3], info[9]), (0x19930522, 1, 0, 5))
                constructor_flags, constructor_handler, constructor_info = personality(
                    library, 0x25D20, 0x180000000, library_imports)
                self.assertEqual((constructor_flags, constructor_handler), (2, "__CxxFrameHandler3"))
                constructed = struct.unpack("<IiIIIIIiII", library.get_data(constructor_info, 40))
                self.assertEqual((constructed[0], constructed[1], constructed[3], constructed[9]),
                                 (0x19930522, 16, 0, 1))

                exe_imports = {item.address: item.name.decode()
                               for entry in image.DIRECTORY_ENTRY_IMPORT
                               for item in entry.imports if item.name}
                receiver = next(item.struct for item in image.DIRECTORY_ENTRY_EXCEPTION
                                if item.struct.BeginAddress == 0x6A88E0)
                self.assertEqual(receiver.EndAddress, 0x6A95AE)
                header = image.get_data(receiver.UnwindData, 4)
                self.assertEqual(header[3] & 0xF, 0)
                self.assertEqual(image.get_data(0x6A88E7, 12), bytes.fromhex("555356574154415541564157"))
                self.assertEqual(image.get_data(0x6A88F3, 7), bytes.fromhex("488da808f5ffff"))
                self.assertEqual(image.get_data(0x6A88FA, 7), bytes.fromhex("4881ecb80b0000"))
                self.assertEqual(image.get_data(0x6A8DA1, 7), bytes.fromhex("488d8d40020000"))
                self.assertEqual(image.get_data(0x6A8FAD, 7), bytes.fromhex("488d8d40020000"))
                self.assertEqual((-0xAF8 + 0x240), (-(0x40 + 0xBB8) + 0x340))
                data_rva = receiver.UnwindData + 4 + ((header[2] + 1) & ~1) * 2
                _handler, language = struct.unpack("<II", image.get_data(data_rva, 8))
                function_info = struct.unpack("<IiIIIIIiII", image.get_data(language, 40))
                self.assertEqual((function_info[0], function_info[3], function_info[9]),
                                 (0x19930522, 0, 1))
                ip_states = [struct.unpack("<Ii", image.get_data(function_info[6] + index * 8, 8))
                             for index in range(function_info[5])]
                unwind = [struct.unpack("<iI", image.get_data(function_info[2] + index * 8, 8))
                          for index in range(function_info[1])]

                def state_at(rva):
                    return next(state for ip, state in reversed(ip_states) if ip <= rva)

                self.assertEqual(state_at(0x6A8DA8), 14)
                self.assertEqual(state_at(0x6A8EDA), 16)
                self.assertEqual(state_at(0x6A8F32), 16)
                self.assertEqual(state_at(0x6A9104), 9)

                def action_target(action):
                    raw = image.get_data(action, 16)
                    if b"\xff\x25" in raw:
                        index = raw.index(b"\xff\x25")
                        displacement = struct.unpack_from("<i", raw, index + 2)[0]
                        slot = 0x140000000 + action + index + 6 + displacement
                        return exe_imports[slot]
                    relative = struct.unpack_from("<i", raw, raw.index(b"\xe9") + 1)[0]
                    index = raw.index(b"\xe9")
                    return 0x140000000 + action + index + 5 + relative

                def chain(state):
                    targets = []
                    seen = set()
                    while state != -1 and state not in seen:
                        seen.add(state)
                        state, action = unwind[state]
                        if action:
                            targets.append(action_target(action))
                    return targets

                live = chain(16)
                self.assertEqual(live[0], "??1CZoneData@@QEAA@XZ")
                self.assertIn(0x14051F150, live)
                self.assertIn("??1CBenchManagerFunction@@UEAA@XZ", live)
                self.assertIn("??1CLogManagerFunctionML@@UEAA@XZ", live)
                self.assertNotIn("??1CZoneData@@QEAA@XZ", chain(9))
                self.assertEqual(action_target(unwind[14][1]), "??_DCViUnitSize@@QEAAXXZ")
                ctor_bytes = image.get_data(0x6A8DA8, 6)
                self.assertEqual(ctor_bytes[:2], b"\xff\x15")
                ctor_slot = 0x1406A8DA8 + 6 + struct.unpack_from("<i", ctor_bytes, 2)[0]
                self.assertEqual(exe_imports[ctor_slot], "??0CZoneData@@QEAA@_KAEBVCViUnitSize@@@Z")
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_stock_cpp_unwind_states_select_cleanup_actions(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        with pefile.PE(data=source) as image:
            entries = [item.struct for item in image.DIRECTORY_ENTRY_EXCEPTION
                       if item.struct.BeginAddress == SYNCHRONOUS - IMAGE_BASE]
            self.assertEqual(len(entries), 1)
            entry = entries[0]
            self.assertEqual((entry.EndAddress, entry.UnwindData), (0x69FE55, 0xFD4D80))
            header = image.get_data(entry.UnwindData, 4)
            self.assertEqual(header, bytes.fromhex("111f0900"))
            tail = entry.UnwindData + 4 + ((header[2] + 1) & ~1) * 2
            self.assertEqual(struct.unpack("<II", image.get_data(tail, 8)),
                             (0x7A6232, 0xEA80B0))
            self.assertEqual(struct.unpack("<10I", image.get_data(0xEA80B0, 40)),
                             (0x19930522, 6, 0xFD4DA0, 0, 0, 10, 0xFD4DD0, 0x30, 0, 1))
            unwind = [struct.unpack("<iI", image.get_data(0xFD4DA0 + index * 8, 8))
                      for index in range(6)]
            self.assertEqual(unwind, [(-1, 0x7FD010), (0, 0x7FD01E),
                                      (-1, 0x7FD01E), (2, 0x7FD02C),
                                      (2, 0x7FD038), (4, 0x7FD044)])
            ip_states = [struct.unpack("<Ii", image.get_data(0xFD4DD0 + index * 8, 8))
                         for index in range(10)]
            self.assertEqual(ip_states, [(0x69FCD0, -1), (0x69FD0A, 0),
                                         (0x69FD37, 2), (0x69FD66, 3),
                                         (0x69FD78, 2), (0x69FD9B, 4),
                                         (0x69FDF3, 5), (0x69FE13, 4),
                                         (0x69FE22, 2), (0x69FE30, -1)])
            for return_ip, expected in (
                (0x69FDAF, [0x7FD038, 0x7FD01E]),
                (0x69FE12, [0x7FD044, 0x7FD038, 0x7FD01E]),
                (0x69FE2F, [0x7FD01E]),
            ):
                with self.subTest(return_ip=hex(return_ip)):
                    state = next(state for ip, state in reversed(ip_states)
                                 if ip <= return_ip - 1)
                    actions = []
                    while state != -1:
                        self.assertLess(len(actions), len(unwind))
                        state, action = unwind[state]
                        actions.append(action)
                    self.assertEqual(actions, expected)

    def test_stock_cleanup_funclets_destroy_local_vector(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        report = json.loads((ROOT / "maps" / "rev2a_synchronous_exception_cleanup.json")
                            .read_text(encoding="utf-8"))
        self.assertEqual(report["source_sha256"], SOURCE_HASH)
        code = {}
        with pefile.PE(data=source, fast_load=True) as image:
            for function in report["functions"]:
                for instruction in function["instructions"]:
                    address = int(instruction["address"], 16)
                    retained = bytes.fromhex(instruction["bytes"])
                    self.assertEqual(image.get_data(address - IMAGE_BASE, len(retained)),
                                     retained)
                    code[address] = retained
            for address, encoded in (
                (0x1407FD010, "488d8ae000000048ff25da205600"),
                (0x1407FD01E, "488d8a5000000048ff25d4625500"),
                (0x1407FD02C, "488b8af0000000e9d82ae8ff"),
                (0x1407FD038, "488d8a80000000e98c09e7ff"),
                (0x1407FD044, "488d8ae000000048ff25a6205600"),
            ):
                retained = bytes.fromhex(encoded)
                self.assertEqual(image.get_data(address - IMAGE_BASE, len(retained)), retained)
                code[address] = retained[:7]
                code[address + 7] = retained[7:]

        frame = FIXTURE + 0x1000
        elements = FIXTURE + 0x2000
        vtable = FIXTURE + 0x3000
        string_stub = SCRATCH_CODE + 0x100
        logger_stub = SCRATCH_CODE + 0x200
        element_stub = SCRATCH_CODE + 0x300
        for actions, vector_offset, prefix in (
            ((0x1407FD038, 0x1407FD01E), 0x98, []),
            ((0x1407FD044, 0x1407FD038, 0x1407FD01E), 0x98, ["string"]),
            ((0x1407FD01E,), 0x98, []),
            ((0x1407FD02C, 0x1407FD01E), 0x38, []),
            ((0x1407FD010,), 0x98, ["string"]),
        ):
            for count in (0, 1, 2):
                with self.subTest(actions=actions, count=count):
                    cpu = Uc(UC_ARCH_X86, UC_MODE_64)
                    pages = {address & ~0xFFF for address in code}
                    pages.update((0x140D53000, 0x140D5F000))
                    for page in sorted(pages):
                        cpu.mem_map(page, 0x1000)
                    for address, retained in code.items():
                        cpu.mem_write(address, retained)
                    cpu.mem_map(FIXTURE, 0x10000)
                    cpu.mem_map(STACK_BASE, 0x10000)
                    cpu.mem_map(SCRATCH_CODE, 0x1000)
                    cpu.mem_write(0x140D5F0F8, struct.pack("<Q", string_stub))
                    cpu.mem_write(0x140D53300, struct.pack("<Q", logger_stub))
                    cpu.mem_write(vtable, struct.pack("<Q", element_stub))
                    vector = frame + vector_offset
                    vector_data = struct.pack("<QQQ", elements, elements + count * 0x58,
                                              elements + count * 0x58) if count else bytes(24)
                    cpu.mem_write(vector, vector_data)
                    cpu.mem_write(frame + 0xF0, struct.pack("<Q", frame + 0x38))
                    for index in range(count):
                        cpu.mem_write(elements + index * 0x58, struct.pack("<Q", vtable))
                    observed = []
                    visited = []
                    preserved = {register: 0x51000000 + index * 0x100
                                 for index, register in enumerate(NONVOLATILE)}

                    def on_instruction(machine: Uc, address: int, size: int,
                                       user_data: object) -> None:
                        visited.append(address)
                        if address == RETURN_SENTINEL:
                            machine.emu_stop()
                            return
                        if address not in (string_stub, logger_stub, element_stub, 0x14055870E):
                            require(address in code, "only retained cleanup instructions execute")
                            return
                        receiver = machine.reg_read(registers.UC_X86_REG_RCX)
                        stack = machine.reg_read(registers.UC_X86_REG_RSP)
                        if address == 0x14055870E:
                            self.assertEqual(stack % 16, 0)
                            self.assertEqual(receiver, vector)
                            self.assertEqual(machine.reg_read(registers.UC_X86_REG_RDX), elements)
                            self.assertEqual(machine.reg_read(registers.UC_X86_REG_R8), count)
                            observed.append("free")
                            continuation = address + size
                        else:
                            self.assertEqual(stack % 16, 8)
                            if address == string_stub:
                                self.assertEqual(receiver, frame + 0xE0)
                                observed.append("string")
                            elif address == logger_stub:
                                self.assertEqual(receiver, frame + 0x50)
                                observed.append("logger")
                            else:
                                self.assertEqual(receiver, elements + observed.count("element") * 0x58)
                                self.assertEqual(machine.reg_read(registers.UC_X86_REG_RDX), 0)
                                observed.append("element")
                            continuation = struct.unpack("<Q", machine.mem_read(stack, 8))[0]
                            machine.reg_write(registers.UC_X86_REG_RSP, stack + 8)
                        for register in VOLATILE:
                            machine.reg_write(register, 0xDEAD0000)
                        machine.reg_write(registers.UC_X86_REG_RIP, continuation)

                    cpu.hook_add(UC_HOOK_CODE, on_instruction)
                    for action in actions:
                        for register, value in preserved.items():
                            cpu.reg_write(register, value)
                        cpu.reg_write(registers.UC_X86_REG_RSP, STACK_TOP)
                        cpu.reg_write(registers.UC_X86_REG_RDX, frame)
                        cpu.mem_write(STACK_TOP, struct.pack("<Q", RETURN_SENTINEL))
                        cpu.emu_start(action, RETURN_SENTINEL + 1, count=150)
                        self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RIP), RETURN_SENTINEL)
                        self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RSP), STACK_TOP + 8)
                        for register, value in preserved.items():
                            self.assertEqual(cpu.reg_read(register), value)
                    cleans_vector = any(action in (0x1407FD038, 0x1407FD02C) for action in actions)
                    expected = prefix + (["element"] * count + ["free"]
                                         if cleans_vector and count else [])
                    if 0x1407FD01E in actions:
                        expected.append("logger")
                    self.assertEqual(observed, expected)
                    self.assertEqual(bytes(cpu.mem_read(vector, 24)),
                                     bytes(24) if cleans_vector else vector_data)
                    self.assertNotIn(0x14066D9E0, visited)

    def test_normal_body_releases_after_zone_call_and_masks_failure_results(self) -> None:
        for zone_result in (0, 1):
            for release_result in (0, 1):
                with self.subTest(zone_result=zone_result, release_result=release_result):
                    emulator = SynchronousBodyEmulator(
                        self.functions, zone_result=zone_result, release_result=release_result)
                    self.assertEqual(emulator.run() & 0xFF, 1)
                    expected = ["synchronous_enter", "acquisition_context", "analysis_constructor",
                                "execute_zone", "execute_zone_returned"]
                    if not zone_result:
                        expected.append("zone_failure_logged")
                    expected.extend(["storage_manager", "release_slot", "release_slot_returned",
                                     "analysis_cleanup", "synchronous_logger_destroyed",
                                     "synchronous_return"])
                    self.assertEqual(emulator.body_calls, expected)
                    self.assertEqual(emulator.calls, [])
                    self.assertEqual(emulator.tracked, [])

    def test_injected_helper_failure_is_not_a_normal_completion(self) -> None:
        for boundary in ("execute_zone", "release_slot", "analysis_cleanup"):
            with self.subTest(boundary=boundary):
                emulator = SynchronousBodyEmulator(
                    self.functions, zone_result=1, release_result=1, fail_at=boundary)
                with self.assertRaisesRegex(RuntimeError, "injected helper failure: " + boundary):
                    emulator.run()
                self.assertEqual(emulator.body_calls[-1], boundary)
                self.assertNotIn("synchronous_return", emulator.body_calls)
                if boundary == "execute_zone":
                    self.assertNotIn("release_slot", emulator.body_calls)


class ExportQueueOwnershipTests(unittest.TestCase):
    def test_export_queue_owns_value_records_before_push_returns(self) -> None:
        source = (ROOT / "v3d_files_" / "AvVTraitLib.dll").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), AVVTRAIT_HASH)
        reports = [
            json.loads((ROOT / "maps" / filename).read_text(encoding="utf-8"))
            for filename in (
                "rev2a_export_thread_string_xrefs.json",
                "rev2a_export_thread_records.json",
            )
        ]
        functions = {
            int(function["entry"], 16): function
            for report in reports
            for function in report["functions"]
        }
        expected = {
            0x1805740A0: "CLibraryHelperExportThread::Handler",
            0x1805742B0: "CLibraryHelperExportThread::PushResult",
            0x180574DB0: "CLibraryHelperExportThread::Start",
            0x180574F30: "CLibraryHelperExportThread::Stop",
            0x180573540: "FUN_180573540",
            0x180573670: "FUN_180573670",
            0x1805739D0: "FUN_1805739d0",
            0x180576080: "FUN_180576080",
        }
        self.assertEqual({entry: functions[entry]["name"] for entry in expected}, expected)
        with pefile.PE(data=source, fast_load=True) as image:
            self.assertEqual(image.OPTIONAL_HEADER.ImageBase, AVVTRAIT_BASE)
            for function in functions.values():
                for instruction in function["instructions"]:
                    address = int(instruction["address"], 16)
                    retained = bytes.fromhex(instruction["bytes"])
                    self.assertEqual(
                        image.get_data(address - AVVTRAIT_BASE, len(retained)), retained
                    )

        push = functions[0x1805742B0]["decompilation"]
        copy = functions[0x180573540]["decompilation"]
        destroy = functions[0x1805739D0]["decompilation"]
        append = functions[0x180576080]["decompilation"]
        handler = functions[0x1805740A0]["decompilation"]
        stop = functions[0x180574F30]["decompilation"]
        self.assertIn("CModelResult::GetPtrResultChangeValue(param_2)", push)
        self.assertIn("FUN_180573670(local_248", push)
        self.assertIn("FUN_180576080(this + 0x68", push)
        for offset in range(0, 0x80, 8):
            suffix = "" if offset == 0 else " + 8" if offset == 8 else f" + 0x{offset:x}"
            self.assertIn(f"param_1{suffix},param_2{suffix}", copy)
            self.assertIn(f"param_1{suffix})", destroy)
        self.assertIn("*(undefined4 *)(param_1 + 0x80) = *(undefined4 *)(param_2 + 0x80)", copy)
        self.assertIn("*(undefined8 *)(param_1 + 0x88) = *(undefined8 *)(param_2 + 0x88)", copy)
        self.assertIn("FUN_180573540(param_1[1]", append)
        self.assertIn("param_1[1] = param_1[1] + 0x90", append)
        self.assertIn("FUN_1805739d0(lVar6)", handler)
        self.assertIn("*(undefined8 *)(this + 0x70) = *(undefined8 *)(this + 0x68)", handler)
        self.assertIn("FUN_1805759d0(pCVar1,&local_res8)", stop)
        self.assertIn('"m_oThread.try_join_for(%u ms) failed.",60000', stop)


class SkipUiCallbackEvidenceTests(unittest.TestCase):
    def test_production_view_construction_binding(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        with pefile.PE(data=source, fast_load=True) as image:
            class_name, class_size, schema, factory = struct.unpack(
                "<QIIQ", image.get_data(0x140EAC618 - IMAGE_BASE, 24)
            )
            self.assertEqual((class_size, schema, factory), (0x7018, 0xFFFF, 0x1406AC010))
            self.assertEqual(image.get_string_at_rva(class_name - IMAGE_BASE),
                             b"CProductionView")
            constructor_lea = image.get_data(0x1406AB5A2 - IMAGE_BASE, 7)
            self.assertEqual(constructor_lea[:3], b"\x48\x8d\x05")
            self.assertEqual(
                0x1406AB5A9 + struct.unpack("<i", constructor_lea[3:])[0],
                0x140EAC650,
            )
            self.assertEqual(image.get_data(0x1406AB5A9 - IMAGE_BASE, 3), b"\x48\x89\x07")
            self.assertEqual(
                struct.unpack("<Q", image.get_data(0x140EAC6B0 - IMAGE_BASE, 8))[0],
                0x1406AC2D0,
            )
            self.assertEqual(
                struct.unpack("<QQ", image.get_data(0x140EACE80 - IMAGE_BASE, 16)),
                (0x1407805A6, 0x140EACA40),
            )
            entries = [
                struct.unpack("<IIIIQQ", image.get_data(0x140EACA40 - IMAGE_BASE + index * 32, 32))
                for index in range(34)
            ]
            self.assertEqual(entries[-1], (0, 0, 0, 0, 0, 0))
            self.assertEqual([entry for entry in entries[:-1] if entry[0] in (2, 0x82)],
                             [(2, 0, 0, 0, 0x13, 0x1406AF270)])
            for filename in ("rev2a_skip_view_factory.json",
                             "rev2a_skip_view_construction.json",
                             "rev2a_skip_view_teardown_bindings.json",
                             "rev2a_skip_view_destructor.json",
                             "rev2a_skip_view_destroy_handler.json"):
                report = json.loads((ROOT / "maps" / filename).read_text(encoding="utf-8"))
                self.assertEqual(report["source_sha256"], SOURCE_HASH)
                for function in report["functions"]:
                    self.assertTrue(function["instructions"])
                    for instruction in function["instructions"]:
                        expected = bytes.fromhex(instruction["bytes"])
                        self.assertEqual(
                            image.get_data(int(instruction["address"], 16) - IMAGE_BASE,
                                           len(expected)),
                            expected,
                        )

    def test_registered_callback_reads_live_cao_skip_list(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        reports = [
            json.loads((ROOT / "maps" / filename).read_text(encoding="utf-8"))
            for filename in (
                "rev2a_skip_ui_guid_initializers.json",
                "rev2a_skip_ui_handler.json",
                "rev2a_skip_ui_refresh.json",
                "rev2a_skip_ui_document_lifecycle.json",
                "rev2a_skip_ui_list_storage.json",
                "rev2a_skip_reset_boundary.json",
                "rev2a_skip_list_add.json",
                "rev2a_skip_reset_callers.json",
                "rev2a_skip_com_wrapper.json",
                "rev2a_skip_com_dispatch.json",
                "rev2a_skip_capm_table_binding.json",
                "rev2a_skip_capm_app_binding.json",
                "rev2a_skip_capm_document_accessor.json",
                "rev2a_skip_capm_document_neighbor.json",
                "rev2a_skip_capm_document_publication.json",
                "rev2a_skip_document_lifecycle_wrappers.json",
                "rev2a_skip_document_close_overrides.json",
                "rev2a_skip_document_close_helpers.json",
                "rev2a_skip_document_close_nested.json",
                "rev2a_skip_document_posted_command.json",
                "rev2a_skip_close_command_descendants.json",
                "rev2a_skip_posted_ui_helper.json",
                "rev2a_skip_embedded_window_destructor.json",
                "rev2a_skip_embedded_window_binding.json",
                "rev2a_skip_embedded_window_virtual.json",
                "rev2a_skip_document_sheet_construction.json",
                "rev2a_skip_prepare_reapply.json",
                "rev2a_skip_policy_writers.json",
                "rev2a_skip_policy_single_lane.json",
                "rev2a_skip_policy_dialog_stores.json",
                "rev2a_skip_policy_dialog_handler.json",
            )
        ]
        functions = {
            int(function["entry"], 16): function
            for report in reports
            for function in report["functions"]
        }
        with pefile.PE(data=source, fast_load=True) as image:
            self.assertEqual(image.OPTIONAL_HEADER.ImageBase, IMAGE_BASE)
            entry = image.get_data(0x140EACD20 - IMAGE_BASE, 32)
            self.assertEqual(
                struct.unpack("<IIIIQQ", entry),
                (0xC000, 0, 0, 0, 0x1411982C8, 0x1406B0700),
            )
            self.assertEqual(
                struct.unpack("<IIIIQQ", image.get_data(0x140EACAE0 - IMAGE_BASE, 32)),
                (0x111, 0, 0xB24C, 0xB24C, 0x3A, 0x1406B1840),
            )
            for slot, target in ((0x80, 0x14075AD60), (0xE0, 0x14075D010),
                                 (0xE8, 0x14075D040)):
                self.assertEqual(
                    struct.unpack("<Q", image.get_data(0x140EDDBD0 + slot - IMAGE_BASE, 8))[0],
                    target,
                )
            locator = struct.unpack(
                "<Q", image.get_data(0x140EDDBC8 - IMAGE_BASE, 8)
            )[0]
            self.assertEqual(locator, 0x140F1AB78)
            signature, offset, constructor_offset, descriptor, _, self_rva = struct.unpack(
                "<6I", image.get_data(locator - IMAGE_BASE, 24)
            )
            self.assertEqual((signature, offset, constructor_offset, self_rva),
                             (1, 8, 0, locator - IMAGE_BASE))
            self.assertEqual(image.get_string_at_rva(descriptor + 16), b".?AVCCAPM@@")
            self.assertEqual(
                struct.unpack("<Q", image.get_data(0x140EB0640 - IMAGE_BASE, 8))[0],
                0x14077F754,
            )
            sheet_locator = struct.unpack(
                "<Q", image.get_data(0x140EB0358 - IMAGE_BASE, 8)
            )[0]
            self.assertEqual(sheet_locator, 0x140F14428)
            sheet_rtti = struct.unpack(
                "<6I", image.get_data(sheet_locator - IMAGE_BASE, 24)
            )
            self.assertEqual(sheet_rtti[:3], (1, 0, 0))
            self.assertEqual(sheet_rtti[5], sheet_locator - IMAGE_BASE)
            self.assertEqual(image.get_string_at_rva(sheet_rtti[3] + 16),
                             b".?AVSkipProductionElmt_Sheet@@")
            modal_thunk = image.get_data(0x14077F754 - IMAGE_BASE, 6)
            self.assertEqual(modal_thunk[:2], b"\xff\x25")
            self.assertEqual(0x14077F754 + 6 + struct.unpack("<i", modal_thunk[2:])[0],
                             0x140D5EC88)
            import_limit = pefile.MAX_IMPORT_SYMBOLS
            try:
                pefile.MAX_IMPORT_SYMBOLS = 65536
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]
                ])
                imports = {
                    symbol.address: (entry.dll.lower(), symbol.ordinal, symbol.name)
                    for entry in image.DIRECTORY_ENTRY_IMPORT
                    for symbol in entry.imports
                }
                self.assertEqual(imports[0x140D5EC88], (b"mfc140.dll", 3959, None))
                self.assertEqual(imports[0x140D5BC90],
                                 (b"user32.dll", None, b"InvalidateRect"))
            finally:
                pefile.MAX_IMPORT_SYMBOLS = import_limit
            constructor_vtable = image.get_data(0x14067DECC - IMAGE_BASE, 7)
            self.assertEqual(constructor_vtable[:3], b"\x48\x8d\x05")
            self.assertEqual(0x14067DECC + 7 + struct.unpack("<i", constructor_vtable[3:])[0],
                             0x140EA3868)
            self.assertEqual(image.get_data(0x14067DED3 - IMAGE_BASE, 3), b"\x48\x89\x06")
            for slot, target in ((0, 0x1406892A0), (8, 0x1406807E0),
                                 (0xF8, 0x14077FE0E), (0x100, 0x14068DAB0),
                                 (0x108, 0x14068DC20), (0x110, 0x14068EE00),
                                 (0x118, 0x14068D9D0), (0x1B0, 0x14077FE74),
                                 (0x1C8, 0x14077FE86)):
                self.assertEqual(
                    struct.unpack("<Q", image.get_data(0x140EA3868 + slot - IMAGE_BASE, 8))[0],
                    target,
                )
            for report in reports:
                self.assertEqual(report["source_sha256"], SOURCE_HASH)
            for function in functions.values():
                for instruction in function["instructions"]:
                    retained = bytes.fromhex(instruction["bytes"])
                    self.assertEqual(
                        image.get_data(int(instruction["address"], 16) - IMAGE_BASE,
                                       len(retained)),
                        retained,
                    )

        reapply_calls = {
            int(instruction["address"], 16): instruction["text"]
            for instruction in functions[0x14052E910]["instructions"]
            if instruction["text"].startswith("CALL")
        }
        self.assertEqual(reapply_calls[0x14052E9D3], "CALL 0x14052e010")
        self.assertEqual(reapply_calls[0x14052EAFC], "CALL 0x14052e010")
        self.assertEqual(reapply_calls[0x14052E9E2], "CALL qword ptr [RBX + 0xd8]")
        self.assertEqual(reapply_calls[0x14052EB0B], "CALL qword ptr [RDI + 0xd8]")
        reload_instructions = {
            int(instruction["address"], 16): instruction["text"]
            for instruction in functions[0x140692AF0]["instructions"]
        }
        self.assertEqual(reload_instructions[0x1406937D7], "CALL 0x140541050")
        self.assertEqual(reload_instructions[0x140693802], "LEA RCX,[RSI + 0x23e0]")
        self.assertEqual(reload_instructions[0x140693809], "MOV R8D,dword ptr [RAX + RBX*0x4]")
        self.assertEqual(reload_instructions[0x14069380D], "MOV RDX,qword ptr [RCX + 0x10]")
        password_check = functions[0x1404E0B60]["decompilation"]
        document_constructor = functions[0x14067DEA0]["instructions"]
        self.assertIn("MOV RSI,RCX",
                      [instruction["text"] for instruction in document_constructor])
        self.assertEqual(
            [instruction["text"] for instruction in document_constructor
             if 0x14067DFDD <= int(instruction["address"], 16) <= 0x14067DFEF],
            ["LEA RCX,[RSI + 0x3990]", "XOR R9D,R9D", "XOR R8D,R8D",
             "MOV EDX,0xdc0", "CALL 0x1406c3a30"],
        )
        sheet_constructor = functions[0x1406C3A30]["instructions"]
        self.assertIn("MOV RDI,RCX",
                      [instruction["text"] for instruction in sheet_constructor])
        self.assertEqual(
            [instruction["text"] for instruction in sheet_constructor
             if 0x1406C3A56 <= int(instruction["address"], 16) <= 0x1406C3A5D],
            ["LEA RAX,[0x140eb0360]", "MOV qword ptr [RDI],RAX"],
        )
        self.assertEqual(
            [instruction["text"] for instruction in functions[0x14077F754]["instructions"]],
            ["JMP qword ptr [0x140d5ec88]"],
        )
        invalidation = functions[0x140675F90]["instructions"]
        self.assertEqual(
            [instruction["text"] for instruction in invalidation],
            ["MOV RCX,qword ptr [RCX + 0x40]", "XOR EDX,EDX",
             "LEA R8D,[RDX + 0x1]", "JMP qword ptr [0x140d5bc90]"],
        )
        self.assertIn(
            "USER32.DLL::InvalidateRect",
            [reference["symbol"] for reference in invalidation[-1]["references"]],
        )
        self.assertIn("Ask Password to start production", password_check)
        self.assertIn("CPassword_Edit::DoModal", password_check)
        self.assertEqual(
            [instruction["text"] for instruction in functions[0x140697AB0]["instructions"]],
            ["PUSH RBX", "SUB RSP,0x20", "MOV RBX,RCX", "CALL 0x1406892c0",
             "TEST RAX,RAX", "JNZ 0x140697ac7", "XOR EDX,EDX", "JMP 0x140697acb",
             "MOV RDX,qword ptr [RAX + 0x40]", "MOV RCX,qword ptr [RBX + 0x39d0]",
             "CALL qword ptr [0x140d5bcd8]", "MOV RCX,RAX", "CALL 0x14077f6b2",
             "LEA RCX,[RBX + 0x3990]", "MOV RAX,qword ptr [RCX]", "ADD RSP,0x20",
             "POP RBX", "JMP qword ptr [RAX + 0x2e0]"],
        )
        self.assertEqual(
            [instruction["text"] for instruction in functions[0x1406ABFE0]["instructions"]],
            ["PUSH RBX", "SUB RSP,0x20", "MOV RBX,RCX", "ADD RCX,0x870",
             "CALL 0x140675f90", "MOV RCX,qword ptr [RBX + 0x40]", "MOV R9D,0x105",
             "XOR R8D,R8D", "XOR EDX,EDX", "ADD RSP,0x20", "POP RBX",
             "JMP qword ptr [0x140d5bd48]"],
        )
        guid = "{FEA8416F-2D59-478F-BEFF-5D96AFD6A551}"
        for initializer in (0x140398420, 0x14029B660):
            self.assertIn(f'RegisterWindowMessageA("{guid}")',
                          functions[initializer]["decompilation"])
        self.assertIn("DAT_1411982c8 =", functions[0x14029B660]["decompilation"])
        self.assertIn("FUN_1406adaf0();", functions[0x1406B0700]["decompilation"])
        initial_update = functions[0x1406AF770]["decompilation"]
        self.assertIn("lVar20 = *(longlong *)(param_1 + 0xe8)", initial_update)
        self.assertIn("*(CFormView **)(lVar20 + 0x5838) = param_1", initial_update)
        refresh = functions[0x1406ADAF0]["decompilation"]
        self.assertIn("SkipList_Get(*(CDataCaoTraitement **)(param_1 + 0xe8))", refresh)
        self.assertIn("*(longlong *)(pCVar2 + 0x10)", refresh)
        self.assertIn("*(uint *)(*(longlong *)(pCVar2 + 8) + uVar4 * 4)", refresh)
        self.assertIn("AfxThrowInvalidArgException()", refresh)
        self.assertIn("return (CUIntArray *)(this + 0x23e0)",
                      functions[0x140541040]["decompilation"])
        self.assertIn("CUIntArray::SetSize((CUIntArray *)(this + 0x23e0),0,-1)",
                      functions[0x140541050]["decompilation"])
        self.assertEqual(
            [instruction["text"] for instruction in functions[0x140541020]["instructions"]],
            ["ADD RCX,0x23e0", "MOV R8D,EDX",
             "MOV RDX,qword ptr [RCX + 0x10]", "JMP 0x14077fdd2"],
        )
        self.assertEqual(
            functions[0x140541020]["instructions"][-1]["references"][0]["symbol"],
            "MFC140.DLL::CUIntArray::SetAtGrow",
        )
        com_reset = functions[0x1404AE9D0]["decompilation"]
        self.assertIn("CCOMObjectMgr::CCOMObject::AskListOfSubPanelsToSkip", com_reset)
        self.assertLess(com_reset.index("SkipList_Reset(param_2)"),
                        com_reset.index("SkipList_Add(param_2,"))
        mutation_calls = [
            (int(instruction["address"], 16), int(reference["to"], 16))
            for instruction in functions[0x1404AE9D0]["instructions"]
            for reference in instruction["references"]
            if reference["to"] in ("140541050", "140541020")
        ]
        self.assertEqual(mutation_calls,
                         [(0x1404AEBE9, 0x140541050), (0x1404AEC17, 0x140541020)])
        self.assertIn("ClearTestVectorForSkip(this)",
                      functions[0x140541050]["decompilation"])
        reset_callers = {
            (0x1404AE9D0, 0x1404AEBE9),
            (0x14068F0F0, 0x14068F7D7),
            (0x140692AF0, 0x1406937D7),
            (0x1406A06B0, 0x1406A085E),
            (0x1406A20D0, 0x1406A2D87),
        }
        self.assertEqual(
            {(int(reference["caller"], 16), int(reference["from"], 16))
             for reference in functions[0x140541050]["incoming"]
             if reference["caller"] is not None},
            reset_callers,
        )
        self.assertEqual(
            {(entry, int(instruction["address"], 16))
             for entry, function in functions.items()
             for instruction in function["instructions"]
             for reference in instruction["references"]
             if reference["to"] == "140541050"},
            reset_callers,
        )
        for entry, name in (
            (0x14068F0F0, "CProductionDoc::PrepareExecData"),
            (0x140692AF0, "CProductionDoc::ReloadDoc"),
            (0x1406A20D0, "CProductionThread::HandlerProduction"),
        ):
            self.assertIn(name, functions[entry]["decompilation"])
        com_wrapper = functions[0x1404AECD0]
        self.assertIn("CCOMObjectMgr::AskListOfSubPanelsToSkip",
                      com_wrapper["decompilation"])
        wrapper_instructions = {
            int(instruction["address"], 16): instruction["text"]
            for instruction in com_wrapper["instructions"]
        }
        for address, text in (
            (0x1404AECE4, "MOV RDI,RDX"),
            (0x1404AED59, "MOV RDX,RDI"),
            (0x1404AED5C, "MOV RCX,qword ptr [RBX + 0x8]"),
            (0x1404AED60, "CALL 0x1404ae9d0"),
        ):
            self.assertEqual(wrapper_instructions[address], text)
        self.assertEqual(
            [instruction["text"] for instruction in functions[0x14075AD60]["instructions"]],
            ["ADD RCX,0x10", "JMP 0x1404aecd0"],
        )
        for entry, expected in (
            (0x1404CDFF0, {
                0x1404CE030: "LEA RCX,[RDI + 0x1a8]",
                0x1404CE037: "CALL 0x14075aa80",
            }),
            (0x14075AA80, {
                0x14075AAB6: "LEA RAX,[0x140eddbd0]",
                0x14075AABD: "MOV qword ptr [RCX + 0x8],RAX",
            }),
            (0x1406A15D0, {
                0x1406A160B: "LEA RCX,[RAX + 0x1b0]",
                0x1406A1612: "MOV EDX,dword ptr [RBX + 0xec0]",
                0x1406A161C: "MOV RAX,qword ptr [RCX]",
                0x1406A1629: "JMP qword ptr [RAX + 0xe0]",
            }),
            (0x1406A06B0, {
                0x1406A0826: "LEA RDI,[RAX + 0x1b0]",
                0x1406A0834: "MOV RBX,qword ptr [RDI]",
                0x1406A083A: "CALL 0x1406a15d0",
                0x1406A083F: "MOV RDX,RAX",
                0x1406A0842: "MOV RCX,RDI",
                0x1406A0845: "CALL qword ptr [RBX + 0x80]",
                0x1406A084B: "CMP AL,0x1",
                0x1406A084D: "JZ 0x1406a1056",
                0x1406A085E: "CALL 0x140541050",
            }),
            (0x14067FC20, {
                0x14067FD2D: "MOV RCX,RBX",
                0x14067FD30: "CALL 0x140527b50",
                0x14067FD36: "LEA RCX,[RBX + 0x180]",
                0x14067FD3D: "CALL qword ptr [0x140d5c9c8]",
                0x14067FD44: "LEA RCX,[RBX + 0x6128]",
                0x14067FD4B: "CALL qword ptr [0x140d537c0]",
                0x14067FDA6: "LEA RCX,[RAX + 0x1b0]",
                0x14067FDB4: "MOV RAX,qword ptr [RCX]",
                0x14067FDB7: "XOR R8D,R8D",
                0x14067FDBA: "MOV EDX,dword ptr [RBX + 0x3924]",
                0x14067FDC0: "CALL qword ptr [RAX + 0xe8]",
            }),
            (0x140697200, {
                0x1406972A0: "LEA R14,[RAX + 0x1b0]",
                0x1406972CB: "TEST ESI,ESI",
                0x1406972CD: "JZ 0x140697426",
                0x140697426: "MOV qword ptr [RDI + 0x3924],RBX",
                0x14069743C: "CALL 0x140540e40",
                0x140697441: "MOV RAX,qword ptr [R14]",
                0x140697444: "MOV R8,RDI",
                0x140697447: "XOR EDX,EDX",
                0x140697449: "MOV RCX,R14",
                0x14069744C: "CALL qword ptr [RAX + 0xe8]",
                0x140697455: "XOR R8D,R8D",
                0x140697458: "LEA EDX,[R8 + 0x1]",
                0x14069745C: "MOV RCX,R14",
                0x14069745F: "CALL qword ptr [RAX + 0xe8]",
            }),
            (0x14068DAB0, {
                0x14068DACC: "MOV RBX,RCX",
                0x14068DACF: "XOR EDX,EDX",
                0x14068DAD1: "CALL 0x140697200",
                0x14068DAD6: "TEST AL,AL",
                0x14068DAD8: "JNZ 0x14068dae1",
                0x14068DBEF: "MOV RCX,RBX",
                0x14068DBF2: "CALL 0x14077fe14",
            }),
        ):
            actual = {int(instruction["address"], 16): instruction["text"]
                      for instruction in functions[entry]["instructions"]}
            for address, text in expected.items():
                self.assertEqual(actual[address], text)
            retirement = functions[0x14067FC20]["decompilation"]
            self.assertIn("CProductionDoc::~CProductionDoc", retirement)
            self.assertLess(retirement.index("CDataCaoTraitement::DeleteVector(param_1)"),
                    retirement.index("CDataCao::DeleteCadTab"))
            self.assertLess(retirement.index("CDataCao::DeleteCadTab"),
                    retirement.index("CAsynchCommandExecution::Kill"))
            self.assertLess(retirement.index("CAsynchCommandExecution::Kill"),
                    retirement.index("(*plVar6 + 0xe8)"))
            self.assertIn("CProductionDoc::SetProductionVMC",
                      functions[0x140697200]["decompilation"])
            self.assertEqual(
                [instruction["text"] for instruction in functions[0x1406807E0]["instructions"]],
                ["MOV qword ptr [RSP + 0x8],RBX", "PUSH RDI", "SUB RSP,0x20",
                 "MOV EDI,EDX", "MOV RBX,RCX", "CALL 0x14067fc20", "TEST DIL,0x1",
                 "JZ 0x140680820", "MOV RCX,RBX", "TEST DIL,0x4", "JNZ 0x140680816",
                 "CALL 0x14077f4ae", "MOV RAX,RBX", "MOV RBX,qword ptr [RSP + 0x30]",
                 "ADD RSP,0x20", "POP RDI", "RET", "MOV EDX,0x61f8", "CALL 0x140544110",
                 "MOV RAX,RBX", "MOV RBX,qword ptr [RSP + 0x30]", "ADD RSP,0x20",
                 "POP RDI", "RET"],
            )
        self.assertEqual(
            [instruction["text"] for instruction in functions[0x14068D9D0]["instructions"]],
            ["MOV qword ptr [RSP + 0x8],RBX", "PUSH RDI", "SUB RSP,0x30",
             "MOV RDI,RCX", "CALL 0x1406928d0", "MOV RCX,qword ptr [RDI + 0x3850]",
             "CALL 0x14063b430", "MOV EBX,dword ptr [RDI + 0x3924]", "CALL 0x14077f7f6",
             "LEA R9,[0x1410d50f0]", "MOV dword ptr [RSP + 0x20],0x0",
             "LEA R8,[0x1410d50d0]", "XOR EDX,EDX", "MOV RCX,qword ptr [RAX + 0x8]",
             "CALL 0x1407a6238", "MOV RCX,RAX", "MOV EDX,EBX", "CALL 0x1404e03f0",
             "MOV RCX,RDI", "MOV RBX,qword ptr [RSP + 0x40]", "ADD RSP,0x30",
             "POP RDI", "JMP 0x14077fe26"],
        )
        self.assertIn("CDocument::OnCloseDocument(param_1)",
                      functions[0x14068D9D0]["decompilation"])
        registry_save = functions[0x1406928D0]["decompilation"]
        self.assertIn("CProductionDoc::RegistrySave", registry_save)
        self.assertIn("*(longlong *)(param_1 + 0x23f0)", registry_save)
        self.assertIn("*(ulong *)(*(longlong *)(param_1 + 0x23e8) + uVar4 * 4)", registry_save)
        semaphore_instructions = functions[0x14063B430]["instructions"]
        wait_index = next(index for index, instruction in enumerate(semaphore_instructions)
                          if instruction["address"] == "14063b479")
        self.assertEqual(
            [instruction["text"] for instruction in semaphore_instructions[wait_index:wait_index + 2]],
            ["CALL qword ptr [0x140d54fe0]", "INC dword ptr [RDI + 0x5868]"],
        )
        self.assertIn("WaitForSingleObject", functions[0x14063B430]["decompilation"])
        self.assertIn("ReleaseSemaphore", functions[0x14063B430]["decompilation"])
        notification_posts = [
            int(instruction["address"], 16)
            for instruction in functions[0x1404E03F0]["instructions"]
            if instruction["text"] == "CALL qword ptr [0x140d5bc00]"
        ]
        self.assertEqual(notification_posts, [0x1404E0480, 0x1404E04F3])
        self.assertIn("PostMessageA", functions[0x1404E03F0]["decompilation"])
        self.assertEqual(
            [instruction["text"] for instruction in functions[0x14075D010]["instructions"]],
            ["MOV RAX,qword ptr [RCX + 0x2f0]",
             "SUB RAX,qword ptr [RCX + 0x2e8]", "SAR RAX,0x3", "CMP EDX,EAX",
             "JGE 0x14075d035", "MOV RAX,qword ptr [RCX + 0x2e8]",
             "MOVSXD RDX,EDX", "MOV RAX,qword ptr [RAX + RDX*0x8]", "RET",
             "XOR EAX,EAX", "RET"],
        )
        self.assertEqual(
            [instruction["text"] for instruction in functions[0x14075D040]["instructions"]],
            ["MOV RAX,qword ptr [RCX + 0x2f0]",
             "SUB RAX,qword ptr [RCX + 0x2e8]", "SAR RAX,0x3", "CMP EDX,EAX",
             "JGE 0x14075d067", "MOV RAX,qword ptr [RCX + 0x2e8]",
             "MOVSXD RDX,EDX", "MOV qword ptr [RAX + RDX*0x8],R8",
             "MOV AL,0x1", "RET", "XOR AL,AL", "RET"],
        )

    def test_prepare_exec_reset_is_conditional_on_vector_and_skip_policy(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        report = json.loads((ROOT / "maps" / "rev2a_skip_reset_callers.json")
                            .read_text(encoding="utf-8"))
        self.assertEqual(report["source_sha256"], SOURCE_HASH)
        function = next(function for function in report["functions"]
                        if function["entry"] == "14068f0f0")
        instructions = {int(instruction["address"], 16): bytes.fromhex(instruction["bytes"])
                        for instruction in function["instructions"]
                        if 0x14068F74E <= int(instruction["address"], 16) < 0x14068F7DC}
        with pefile.PE(data=source, fast_load=True) as image:
            for address, retained in instructions.items():
                self.assertEqual(image.get_data(address - IMAGE_BASE, len(retained)), retained)
        for vector_count in (0, 1):
            for policy in (0, 1, 2):
                for skip_count in (0, 2):
                    with self.subTest(vector_count=vector_count, policy=policy,
                                      skip_count=skip_count):
                        cpu = Uc(UC_ARCH_X86, UC_MODE_64)
                        cpu.mem_map(IMAGE_BASE, 0x1000000)
                        cpu.mem_map(FIXTURE, 0x10000)
                        cpu.mem_map(STACK_BASE, 0x10000)
                        for address, retained in instructions.items():
                            cpu.mem_write(address, retained)
                        document = FIXTURE
                        application = FIXTURE + 0x8000
                        module = FIXTURE + 0x9000
                        vector = FIXTURE + 0xA000
                        cpu.mem_write(document + 0x2448,
                                      struct.pack("<QQ", vector, vector + vector_count * 0x28))
                        cpu.mem_write(document + 0x23F0, struct.pack("<Q", skip_count))
                        cpu.mem_write(document + 0x3924, struct.pack("<I", 0))
                        cpu.mem_write(application + 0x18D, bytes([policy]))
                        cpu.mem_write(module + 8, struct.pack("<Q", application))
                        cpu.reg_write(registers.UC_X86_REG_RBX, document)
                        cpu.reg_write(registers.UC_X86_REG_R14, 0)
                        cpu.reg_write(registers.UC_X86_REG_R13, 7)
                        stack = STACK_TOP - 8
                        cpu.reg_write(registers.UC_X86_REG_RSP, stack)
                        calls = []

                        def on_instruction(emulator: Uc, address: int, size: int,
                                           _: object) -> None:
                            if address not in (0x14068F782, 0x14068F7A0,
                                               0x14068F7CA, 0x14068F7D7):
                                return
                            self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RSP), stack)
                            receiver = emulator.reg_read(registers.UC_X86_REG_RCX)
                            if address == 0x14068F782:
                                calls.append("module")
                                result = module
                            elif address == 0x14068F7A0:
                                self.assertEqual(receiver, application)
                                calls.append("cast")
                                result = application
                            else:
                                self.assertEqual(receiver, document)
                                calls.append("reapply" if address == 0x14068F7CA else "reset")
                                result = 3
                            for register in VOLATILE:
                                emulator.reg_write(register, 0xBAD0BAD0)
                            emulator.reg_write(registers.UC_X86_REG_RAX, result)
                            emulator.reg_write(registers.UC_X86_REG_RIP, address + size)

                        cpu.hook_add(UC_HOOK_CODE, on_instruction)
                        cpu.emu_start(0x14068F74E, 0x14068F7DC, count=100)
                        reapply = vector_count > 0 and policy == 1 and skip_count > 0
                        expected = [] if vector_count == 0 else [
                            "module", "cast", "reapply" if reapply else "reset"
                        ]
                        self.assertEqual(calls, expected)
                        self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RIP), 0x14068F7DC)
                        self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RSP), stack)
                        self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RBX), document)
                        self.assertEqual(cpu.reg_read(registers.UC_X86_REG_R13), 3 if reapply else 7)

    def test_production_cycle_reset_is_conditional_on_skip_policy(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        report = json.loads((ROOT / "maps" / "rev2a_skip_reset_callers.json")
                            .read_text(encoding="utf-8"))
        self.assertEqual(report["source_sha256"], SOURCE_HASH)
        function = next(function for function in report["functions"]
                        if function["entry"] == "1406a20d0")
        instructions = {int(instruction["address"], 16): bytes.fromhex(instruction["bytes"])
                        for instruction in function["instructions"]
                        if 0x1406A2D64 <= int(instruction["address"], 16) < 0x1406A2D8C}
        with pefile.PE(data=source, fast_load=True) as image:
            for address, retained in instructions.items():
                self.assertEqual(image.get_data(address - IMAGE_BASE, len(retained)), retained)
        for policy in (0, 1, 2, 255):
            with self.subTest(policy=policy):
                cpu = Uc(UC_ARCH_X86, UC_MODE_64)
                cpu.mem_map(IMAGE_BASE, 0x1000000)
                cpu.mem_map(FIXTURE, 0x10000)
                cpu.mem_map(STACK_BASE, 0x10000)
                for address, retained in instructions.items():
                    cpu.mem_write(address, retained)
                application = FIXTURE
                thread = FIXTURE + 0x1000
                document = FIXTURE + 0x2000
                cpu.mem_write(application + 0x18D, bytes([policy]))
                cpu.reg_write(registers.UC_X86_REG_RAX, application)
                cpu.reg_write(registers.UC_X86_REG_RBX, 0)
                cpu.reg_write(registers.UC_X86_REG_R14, thread)
                stack = STACK_TOP - 8
                cpu.reg_write(registers.UC_X86_REG_RSP, stack)
                calls = []

                def on_instruction(emulator: Uc, address: int, size: int, _: object) -> None:
                    if address not in (0x1406A2D7F, 0x1406A2D87):
                        return
                    self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RSP), stack)
                    self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RCX),
                                     thread if address == 0x1406A2D7F else document)
                    calls.append("document" if address == 0x1406A2D7F else "reset")
                    for register in VOLATILE:
                        emulator.reg_write(register, 0xBAD0BAD0)
                    emulator.reg_write(registers.UC_X86_REG_RAX, document)
                    emulator.reg_write(registers.UC_X86_REG_RIP, address + size)

                cpu.hook_add(UC_HOOK_CODE, on_instruction)
                cpu.emu_start(0x1406A2D64, 0x1406A2D8C, count=100)
                self.assertEqual(calls, ["document", "reset"] if policy == 0 else [])
                self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RIP), 0x1406A2D8C)
                self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RSP), stack)
                self.assertEqual(cpu.reg_read(registers.UC_X86_REG_R14), thread)

    def test_station_mfc140_matches_exe_architecture_and_import_ordinals(self) -> None:
        report = json.loads((ROOT / "maps" / "rev2a_mfc140_station_intake.json")
                            .read_text(encoding="utf-8"))
        source = (ROOT / report["path"]).read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), report["source_sha256"])
        self.assertEqual(len(source), report["source_size"])
        executable = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(executable).hexdigest(), SOURCE_HASH)
        with pefile.PE(data=source, fast_load=True) as library:
            self.assertEqual(library.FILE_HEADER.Machine, report["machine"])
            self.assertEqual(library.OPTIONAL_HEADER.Magic, report["optional_magic"])
            self.assertEqual(library.OPTIONAL_HEADER.ImageBase, report["image_base"])
            library.parse_data_directories(
                directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_RESOURCE"]])
            fixed = library.VS_FIXEDFILEINFO[0]
            version = ".".join(str(value) for value in (
                fixed.FileVersionMS >> 16, fixed.FileVersionMS & 0xFFFF,
                fixed.FileVersionLS >> 16, fixed.FileVersionLS & 0xFFFF))
            self.assertEqual(version, report["file_version"])
            directory = library.OPTIONAL_HEADER.DATA_DIRECTORY[0]
            exports = struct.unpack("<IIHHIIIIIII", library.get_data(directory.VirtualAddress, 40))
            ordinal_base, count, names, table = exports[5:9]
            self.assertEqual((ordinal_base, count, names),
                             (report["export_base"], report["export_functions"], report["export_names"]))
            for expected in report["traced_exports"]:
                index = expected["ordinal"] - ordinal_base
                self.assertTrue(0 <= index < count)
                rva = struct.unpack("<I", library.get_data(table + index * 4, 4))[0]
                self.assertEqual(rva, int(expected["rva"], 16))
                self.assertEqual(directory.VirtualAddress <= rva < directory.VirtualAddress + directory.Size,
                                 expected["forwarded"])
                prefix = bytes.fromhex(expected["prefix"])
                self.assertEqual(library.get_data(rva, len(prefix)), prefix)
            import_limit = pefile.MAX_IMPORT_SYMBOLS
            try:
                pefile.MAX_IMPORT_SYMBOLS = 65536
                with pefile.PE(data=executable, fast_load=True) as image:
                    self.assertEqual(image.FILE_HEADER.Machine, library.FILE_HEADER.Machine)
                    self.assertEqual(image.OPTIONAL_HEADER.Magic, library.OPTIONAL_HEADER.Magic)
                    image.parse_data_directories(
                        directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                    imports = [symbol for entry in image.DIRECTORY_ENTRY_IMPORT
                               if entry.dll.lower() == b"mfc140.dll" for symbol in entry.imports]
                    self.assertTrue(imports)
                    self.assertTrue({3959, 8850, 11881}.issubset({symbol.ordinal for symbol in imports}))
                    for symbol in imports:
                        self.assertIsNone(symbol.name)
                        index = symbol.ordinal - ordinal_base
                        self.assertTrue(0 <= index < count)
                        self.assertNotEqual(struct.unpack("<I", library.get_data(table + index * 4, 4))[0], 0)
            finally:
                pefile.MAX_IMPORT_SYMBOLS = import_limit

    def _verified_station_mfc_functions(self) -> dict[int, dict]:
        expected_hash = "0cf26008fae0cb61dfe49e1c3fc17e0dd860be011d9a6a64b452f56335bafbfe"
        source = (ROOT / "v3d_files_" / "mfc140.dll").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), expected_hash)
        functions = {}
        with pefile.PE(data=source, fast_load=True) as image:
            self.assertEqual(image.OPTIONAL_HEADER.ImageBase, 0x180000000)
            for filename in ("rev2a_mfc140_entrypoints.json", "rev2a_mfc140_control_paths.json",
                             "rev2a_mfc140_modal_pump.json", "rev2a_mfc140_bound_virtuals.json",
                             "rev2a_mfc140_close_receiver.json", "rev2a_mfc140_close_receiver_ctor.json",
                             "rev2a_mfc140_close_receiver_methods.json", "rev2a_mfc140_frame_destroy.json",
                             "rev2a_mfc140_view_base.json", "rev2a_mfc140_view_teardown.json",
                             "rev2a_mfc140_view_detach.json", "rev2a_mfc140_view_ncdestroy.json",
                             "rev2a_mfc140_remove_view.json", "rev2a_mfc140_remove_view_helpers.json",
                             "rev2a_mfc140_view_postdestroy.json", "rev2a_mfc140_view_list_release.json",
                             "rev2a_mfc140_view_frame_counts.json", "rev2a_mfc140_empty_view_pool.json",
                             "rev2a_mfc140_view_block_release.json", "rev2a_mfc140_view_iterators.json",
                             "rev2a_mfc140_window_detach.json", "rev2a_mfc140_window_map_helpers.json",
                             "rev2a_mfc140_empty_window_map.json", "rev2a_mfc140_window_thread_state.json",
                             "rev2a_mfc140_thread_state_helpers.json",
                             "rev2a_mfc140_thread_state_initialization.json",
                             "rev2a_mfc140_thread_state_constructor.json",
                             "rev2a_mfc140_thread_state_allocator.json",
                             "rev2a_mfc140_top_frame_getter.json",
                             "rev2a_mfc140_update_frame_title.json",
                             "rev2a_mfc140_frame_title_writer.json",
                             "rev2a_mfc140_set_window_text.json",
                             "rev2a_mfc140_active_document.json",
                             "rev2a_mfc140_mdi_client.json",
                             "rev2a_mfc140_mdi_parent.json"):
                report = json.loads((ROOT / "maps" / filename).read_text(encoding="utf-8"))
                self.assertEqual(report["source_sha256"], expected_hash)
                self.assertEqual(report["compiler"], "windows")
                for function in report["functions"]:
                    self.assertTrue(function["instructions"])
                    functions[int(function["entry"], 16)] = function
                    for instruction in function["instructions"]:
                        retained = bytes.fromhex(instruction["bytes"])
                        self.assertEqual(image.get_data(int(instruction["address"], 16) -
                                                        0x180000000, len(retained)), retained)
        return functions

    def test_station_mfc140_close_and_modal_bindings(self) -> None:
        functions = self._verified_station_mfc_functions()
        instructions = {int(instruction["address"], 16): instruction["text"]
                        for function in functions.values() for instruction in function["instructions"]}
        for address, expected in (
            (0x180290247, "CALL 0x18028f560"),
            (0x180290252, "MOV RAX,qword ptr [RAX + 0x250]"),
            (0x18021256C, "MOV EDX,0x1"),
            (0x180212571, "MOV RAX,qword ptr [RAX + 0x8]"),
            (0x18027F023, "CALL 0x18028c620"),
            (0x18027BF84, "CALL 0x18021fae0"),
            (0x18021FB08, "CALL 0x180235d10"),
            (0x18021FB0D, "AND qword ptr [RDI + 0xe8],0x0"),
            (0x18021FB1B, "MOV RAX,qword ptr [RAX + 0xf0]"),
            (0x1802ABB8F, "MOV EDX,0x221"),
            (0x1802ABB98, "CALL qword ptr [0x1802ce3d8]"),
            (0x1802ABBC4, "MOV RAX,qword ptr [RCX + 0x358]"),
            (0x180039619, "CALL qword ptr [0x1802cd690]"),
            (0x18003962D, "CALL 0x180236230"),
            (0x180038387, "LEA RAX,[0x1802ea518]"),
            (0x18003838E, "MOV qword ptr [RCX],RAX"),
            (0x180038300, "MOV EAX,dword ptr [RCX + 0x174]"),
            (0x1800394AD, "TEST byte ptr [RCX + 0x168],0x10"),
            (0x18003955B, "MOV RAX,qword ptr [RAX + 0xb8]"),
            (0x1800395AE, "CALL 0x18003b26c"),
            (0x1800395BD, "CALL 0x18003b26c"),
            (0x1801D023C, "MOV RAX,qword ptr [RAX + 0x1c0]"),
            (0x1801D0253, "MOV RAX,qword ptr [RAX + 0x1c8]"),
            (0x1801D0262, "JZ 0x1801d02e9"),
            (0x1801D02E9, "MOV RAX,qword ptr [RBX + 0x120]"),
            (0x1801D02F0, "MOV dword ptr [0x1803f3148],0x1"),
            (0x180279280, "JMP 0x180278320"),
            (0x18027851D, "MOV RAX,qword ptr [RAX + 0xc0]"),
            (0x180278FE3, "JMP 0x180278440"),
            (0x1802783A5, "MOV RAX,qword ptr [RAX + 0xc8]"),
            (0x1802783BB, "JMP 0x180278320"),
            (0x18021F8D0, "AND dword ptr [RCX + 0x120],0x0"),
            (0x18021F8FD, "MOV RAX,qword ptr [RCX + 0x1c8]"),
            (0x18021F910, "MOV RAX,qword ptr [RCX + 0xd0]"),
            (0x18021F932, "MOV dword ptr [RBX + 0x120],ESI"),
            (0x18021F938, "MOV RAX,qword ptr [RAX + 0x1b0]"),
            (0x18021F94B, "MOV RAX,qword ptr [RAX + 0xf8]"),
            (0x18021F958, "CMP dword ptr [RBX + 0x120],0x0"),
            (0x18021F96C, "MOV RAX,qword ptr [RAX + 0x8]"),
            (0x180002850, "RET 0x0"),
            (0x18021AC21, "CALL 0x18021be8c"),
            (0x18021AC80, "CALL 0x180296180"),
            (0x18029626A, "CALL 0x180278390"),
            (0x1802962AA, "MOV RAX,qword ptr [RAX + 0x120]"),
            (0x1802961E9, "XOR R9D,R9D"),
            (0x1802961EC, "XOR R8D,R8D"),
            (0x1802961EF, "XOR EDX,EDX"),
            (0x1802962D2, "XOR R9D,R9D"),
            (0x1802962D5, "XOR R8D,R8D"),
            (0x1802962D8, "XOR EDX,EDX"),
            (0x18021AAD4, "TEST byte ptr [RCX + 0xa8],0x10"),
            (0x18021AAEB, "MOV EDX,0x476"),
        ):
            self.assertEqual(instructions[address], expected)
        executable = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(executable).hexdigest(), SOURCE_HASH)
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=executable, fast_load=True) as image, pefile.PE(
                    str(ROOT / "v3d_files_" / "mfc140.dll"), fast_load=True) as library:
                for parsed in (image, library):
                    parsed.parse_data_directories(directories=[
                        pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                imports = {symbol.address: (entry.dll.lower(), symbol.name, symbol.ordinal)
                           for entry in image.DIRECTORY_ENTRY_IMPORT for symbol in entry.imports}
                library_imports = {symbol.address: (entry.dll.lower(), symbol.name)
                                   for entry in library.DIRECTORY_ENTRY_IMPORT for symbol in entry.imports}
                for slot, name in ((0x1802CDE60, b"GetMessageA"),
                                   (0x1802CE218, b"TranslateMessage"),
                                   (0x1802CE210, b"DispatchMessageA"),
                                   (0x1802CE220, b"PeekMessageA"),
                                   (0x1802CE3D8, b"SendMessageA")):
                    self.assertEqual(library_imports[slot], (b"user32.dll", name))
                exports = struct.unpack("<IIHHIIIIIII", library.get_data(
                    library.OPTIONAL_HEADER.DATA_DIRECTORY[0].VirtualAddress, 40))
                for table, offset, thunk, slot, ordinal, target in (
                    (0x140EACE80, 0, 0x1407805A6, 0x140D5E7A0, 7215, 0x18027EE70),
                    (0x140EA3868, 0xE0, 0x14077FDFC, 0x140D5F630, 5392, 0x18021FB40),
                    (0x140EA3868, 0xE8, 0x14077FE02, 0x140D5F628, 5961, 0x18021FB50),
                    (0x140EA3868, 0xF0, 0x14077FE08, 0x140D5F620, 8734, 0x18021E240),
                    (0x140EA3868, 0x1E0, 0x14077FE9E, 0x140D5F558, 14051, 0x18021E270),
                    (0x140EAC650, 0x250, 0x14077FB6E, 0x140D5FA88, 11718, 0x180212560),
                    (0x140EA3868, 0xF8, 0x14077FE0E, 0x140D5F618, 3727, 0x180002850),
                    (0x140EA3868, 0x1B0, 0x14077FE74, 0x140D5F590, 9134, 0x18021F990),
                    (0x140EA3868, 0x1C8, 0x14077FE86, 0x140D5F578, 11723, 0x180002850),
                    (0x140E39770, 0xC0, 0x14077F97C, 0x140D5FD28, 11849, 0x180278FE0),
                    (0x140E39770, 0xC8, 0x14077F982, 0x140D5FD20, 11881, 0x180279280),
                    (0x140E39770, 0x208, 0x14077FA66, 0x140D5FBF0, 5167, 0x1801D0230),
                    (0x140EA1720, 0xD0, 0x14077FD30, 0x140D5F768, 3803, 0x1802ABB20),
                    (0x140EB0360, 0x120, 0x14077F766, 0x140D5EC70, 2961, 0x18021AAD0),
                    (0x140EB0360, 0x2E0, 0x14077F754, 0x140D5EC88, 3959, 0x18021AB10),
                ):
                    self.assertEqual(struct.unpack("<Q", image.get_data(table + offset - IMAGE_BASE, 8))[0],
                                     thunk)
                    encoded = image.get_data(thunk - IMAGE_BASE, 6)
                    self.assertEqual(encoded[:2], b"\xff\x25")
                    self.assertEqual(thunk + 6 + struct.unpack("<i", encoded[2:])[0], slot)
                    self.assertEqual(imports[slot], (b"mfc140.dll", None, ordinal))
                    self.assertTrue(0 <= ordinal - exports[5] < exports[6])
                    rva = struct.unpack("<I", library.get_data(exports[8] + 4 * (ordinal - exports[5]), 4))[0]
                    self.assertEqual(0x180000000 + rva, target)
                for map_address, getter, base_map in (
                    (0x180339C50, 0x18028BE90, 0x18033D1E0),
                    (0x18033D1E0, 0x18027BEC0, 0x1803390D0),
                    (0x1803390D0, 0x180291A00, 0x18033D900),
                    (0x18033D900, 0x1801E15C0, 0x18034DAA0),
                ):
                    actual_getter, entries = struct.unpack("<QQ", library.get_data(
                        map_address - 0x180000000, 16))
                    self.assertEqual(actual_getter, getter)
                    encoded = library.get_data(getter - 0x180000000, 8)
                    self.assertEqual(encoded[:3], b"\x48\x8d\x05")
                    self.assertEqual(encoded[7:], b"\xc3")
                    self.assertEqual(getter + 7 + struct.unpack("<i", encoded[3:7])[0], base_map)
                    destroy_entries = []
                    for index in range(200):
                        entry = struct.unpack("<IIIIQQ", library.get_data(
                            entries - 0x180000000 + index * 32, 32))
                        if not any(entry):
                            break
                        if entry[0] == 0x82:
                            destroy_entries.append(entry)
                    else:
                        self.fail("Unterminated inherited view message map")
                    self.assertEqual(destroy_entries, [(0x82, 0, 0, 0, 0x13, 0x1802900D0)]
                                     if map_address == 0x18033D900 else [])
                self.assertEqual(library.get_string_at_rva(0x34E970), b"PropertySheetA")
                self.assertEqual(library_imports[0x1802CD690], (b"kernel32.dll", b"DeleteFileA"))
                for slot, name in ((0x1802CD5E8, b"EnterCriticalSection"),
                                   (0x1802CD5E0, b"LeaveCriticalSection"),
                                   (0x1802CD9F0, b"TlsGetValue"),
                                   (0x1802CD768, b"LocalAlloc"),
                                   (0x1802CD9F8, b"LocalReAlloc"),
                                   (0x1802CDA00, b"TlsSetValue")):
                    self.assertEqual(library_imports[slot], (b"kernel32.dll", name))
                self.assertEqual(library_imports[0x1802CE4B0], (b"vcruntime140.dll", b"memset"))
                self.assertEqual(library_imports[0x1802CE558],
                                 (b"api-ms-win-crt-heap-l1-1-0.dll", b"free"))
                self.assertEqual(library_imports[0x1802CE920],
                                 (b"api-ms-win-crt-utility-l1-1-0.dll", b"ldiv"))
                for offset, target in ((0x70, 0x180038300), (0xB0, 0x180039490),
                                       (0xB8, 0x180039600)):
                    self.assertEqual(struct.unpack("<Q", library.get_data(0x2EA518 + offset, 8))[0],
                                     target)
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_station_mfc140_view_list_changed_decision(self) -> None:
        function = self._verified_station_mfc_functions()[0x18021E240]
        for count in (0, 1):
            for auto_delete in (0, 1, 0xFFFFFFFF):
                with self.subTest(count=count, auto_delete=auto_delete):
                    cpu = Uc(UC_ARCH_X86, UC_MODE_64)
                    for base, size in ((0x18021E000, 0x1000), (FIXTURE, 0x1000),
                                       (STACK_BASE, 0x10000), (SCRATCH_CODE, 0x1000)):
                        cpu.mem_map(base, size)
                    for instruction in function["instructions"]:
                        cpu.mem_write(int(instruction["address"], 16), bytes.fromhex(instruction["bytes"]))
                    vtable = FIXTURE + 0x400
                    close_target = SCRATCH_CODE + 0x100
                    update_target = SCRATCH_CODE + 0x200
                    cpu.mem_write(FIXTURE, struct.pack("<Q", vtable))
                    cpu.mem_write(FIXTURE + 0x70, struct.pack("<Q", count))
                    cpu.mem_write(FIXTURE + 0x120, struct.pack("<I", auto_delete))
                    cpu.mem_write(vtable + 0x118, struct.pack("<Q", close_target))
                    cpu.mem_write(vtable + 0x1E0, struct.pack("<Q", update_target))
                    cpu.mem_write(STACK_TOP, struct.pack("<Q", RETURN_SENTINEL))
                    cpu.reg_write(registers.UC_X86_REG_RSP, STACK_TOP)
                    cpu.reg_write(registers.UC_X86_REG_RCX, FIXTURE)
                    for register in NONVOLATILE:
                        cpu.reg_write(register, 0x12345678)
                    cpu.emu_start(0x18021E240, 0x18021E266, count=20)
                    self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RIP), 0x18021E266)
                    self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RAX),
                                     close_target if count == 0 and auto_delete else update_target)
                    self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RCX), FIXTURE)
                    self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RSP), STACK_TOP)
                    for register in NONVOLATILE:
                        self.assertEqual(cpu.reg_read(register), 0x12345678)

    def test_station_mfc140_remove_view_callback_order(self) -> None:
        functions = self._verified_station_mfc_functions()
        for node_count, match_index, block_count in ((1, 0, 0), (1, 0, 1), (1, 0, 2),
                                                    (3, 0, 2), (3, 1, 2), (3, 2, 2)):
            with self.subTest(node_count=node_count, match_index=match_index, block_count=block_count):
                cpu = Uc(UC_ARCH_X86, UC_MODE_64)
                for base, size in ((0x18021E000, 0x2000), (0x180235000, 0x1000),
                                   (0x180030000, 0x1000), (0x180275000, 0x1000), (FIXTURE, 0x1000),
                                   (0x1802CE000, 0x1000),
                                   (STACK_BASE, 0x10000), (SCRATCH_CODE, 0x1000)):
                    cpu.mem_map(base, size)
                for entry in (0x18021FAE0, 0x180235D10, 0x180235A50, 0x1800302C0, 0x180275F10,
                              0x18021E240, 0x18021E270, 0x18021FB40, 0x18021FB50):
                    for instruction in functions[entry]["instructions"]:
                        cpu.mem_write(int(instruction["address"], 16), bytes.fromhex(instruction["bytes"]))
                view = FIXTURE + 0x200
                vtable = FIXTURE + 0x400
                nodes = [FIXTURE + 0x600 + index * 0x20 for index in range(node_count)]
                blocks = [FIXTURE + 0x800 + index * 0x40 for index in range(block_count)]
                callback = 0x18021E240
                cpu.mem_write(SCRATCH_CODE + 0x100, b"\xff\xe0")
                cpu.mem_write(0x1802CEBF0, struct.pack("<Q", SCRATCH_CODE + 0x100))
                cpu.mem_write(FIXTURE, struct.pack("<Q", vtable))
                cpu.mem_write(FIXTURE + 0x60, struct.pack("<QQQ", nodes[0], nodes[-1], node_count))
                cpu.mem_write(FIXTURE + 0x80, struct.pack("<Q", blocks[0] if blocks else 0))
                for index, block in enumerate(blocks):
                    cpu.mem_write(block, struct.pack("<Q", blocks[index + 1]
                                                    if index + 1 < block_count else 0))
                cpu.mem_write(view + 0xE8, struct.pack("<Q", FIXTURE))
                cpu.mem_write(FIXTURE + 0x120, bytes(4))
                cpu.mem_write(vtable + 0xE0, struct.pack("<QQ", 0x18021FB40, 0x18021FB50))
                cpu.mem_write(vtable + 0xF0, struct.pack("<Q", callback))
                cpu.mem_write(vtable + 0x1E0, struct.pack("<Q", 0x18021E270))
                for index, node in enumerate(nodes):
                    cpu.mem_write(node, struct.pack(
                        "<QQQ", nodes[index + 1] if index + 1 < node_count else 0,
                        nodes[index - 1] if index else 0,
                        view if index == match_index else FIXTURE + 0xA00 + index * 0x100))
                    cpu.mem_write(FIXTURE + 0xA40 + index * 0x100, struct.pack("<Q", 0x1000 + index))
                cpu.mem_write(STACK_TOP, struct.pack("<Q", RETURN_SENTINEL))
                cpu.reg_write(registers.UC_X86_REG_RSP, STACK_TOP)
                cpu.reg_write(registers.UC_X86_REG_RCX, FIXTURE)
                cpu.reg_write(registers.UC_X86_REG_RDX, view)
                for register in NONVOLATILE:
                    cpu.reg_write(register, 0x12345678)
                calls = []
                freed_blocks = []

                def dispatch(emulator: Uc, address: int, size: int, _: object) -> None:
                    if address == 0x18021FB08:
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RSP) % 16, 0)
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RCX), FIXTURE + 0x58)
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RDX),
                                         nodes[match_index])
                        self.assertEqual(emulator.mem_read(view + 0xE8, 8), struct.pack("<Q", FIXTURE))
                        calls.append("remove_list_node")
                    elif address == 0x180235A6B:
                        self.assertEqual(node_count, 1)
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RSP) % 16, 0)
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RCX), FIXTURE + 0x58)
                        self.assertEqual(emulator.mem_read(FIXTURE + 0x70, 8), bytes(8))
                        self.assertEqual(emulator.mem_read(view + 0xE8, 8), struct.pack("<Q", FIXTURE))
                        calls.append("pool_cleanup")
                    elif address == 0x1800302E1:
                        self.assertEqual(node_count, 1)
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RSP) % 16, 0)
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RCX),
                                         blocks[0] if blocks else 0)
                        self.assertEqual(emulator.mem_read(FIXTURE + 0x60, 32), bytes(32))
                        self.assertEqual(emulator.mem_read(view + 0xE8, 8), struct.pack("<Q", FIXTURE))
                        calls.append("block_release")
                    elif address == 0x180275F1D:
                        self.assertEqual(node_count, 1)
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RSP) % 16, 0)
                        block = emulator.reg_read(registers.UC_X86_REG_RCX)
                        self.assertEqual(block, blocks[len(freed_blocks)])
                        self.assertEqual(emulator.mem_read(view + 0xE8, 8), struct.pack("<Q", FIXTURE))
                        freed_blocks.append(block)
                        emulator.mem_write(block, b"\xcc" * 0x40)
                        calls.append("free_stub")
                        for register in VOLATILE:
                            emulator.reg_write(register, 0xBAD0BAD0)
                        emulator.reg_write(registers.UC_X86_REG_RIP, address + size)
                    elif address == 0x18021FB2C:
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RSP), STACK_TOP)
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RCX), FIXTURE)
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RAX), callback)
                        self.assertEqual(emulator.mem_read(view + 0xE8, 8), bytes(8))
                        self.assertEqual(emulator.mem_read(FIXTURE + 0x70, 8),
                                         struct.pack("<Q", node_count - 1))
                        calls.append("document_callback")
                    elif address == 0x18021FB40:
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RCX), FIXTURE)
                        self.assertEqual(emulator.mem_read(view + 0xE8, 8), bytes(8))
                        calls.append("view_head")
                    elif address == 0x18021FB50:
                        position = emulator.reg_read(registers.UC_X86_REG_RDX)
                        node = struct.unpack("<Q", emulator.mem_read(position, 8))[0]
                        self.assertIn(node, nodes[:match_index] + nodes[match_index + 1:])
                        calls.append("view_next")
                    elif address in (0x18021E2C0, 0x18021E324, 0x18021E395):
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RSP) % 16, 0)
                        self.assertIn(emulator.reg_read(registers.UC_X86_REG_RCX),
                                      [0x1000 + index for index in range(node_count) if index != match_index])
                        calls.append("visibility_stub")
                        for register in VOLATILE:
                            emulator.reg_write(register, 0xBAD0BAD0)
                        emulator.reg_write(registers.UC_X86_REG_RAX, 0)
                        emulator.reg_write(registers.UC_X86_REG_RIP, address + size)

                cpu.hook_add(UC_HOOK_CODE, dispatch)
                cpu.emu_start(0x18021FAE0, RETURN_SENTINEL, count=1000)
                self.assertEqual(calls, ["remove_list_node"] +
                                 (["pool_cleanup", "block_release"] + ["free_stub"] * block_count
                                  if node_count == 1 else []) +
                                 ["document_callback"] +
                                 (["view_head"] + ["view_next", "visibility_stub"] * (node_count - 1)) * 3)
                self.assertEqual(freed_blocks, blocks if node_count == 1 else [])
                remaining = nodes[:match_index] + nodes[match_index + 1:]
                self.assertEqual(cpu.mem_read(FIXTURE + 0x60, 16), struct.pack(
                    "<QQ", remaining[0] if remaining else 0, remaining[-1] if remaining else 0))
                self.assertEqual(cpu.mem_read(FIXTURE + 0x78, 8), struct.pack(
                    "<Q", 0 if node_count == 1 else nodes[match_index]))
                self.assertEqual(cpu.mem_read(FIXTURE + 0x80, 8), struct.pack(
                    "<Q", 0 if node_count == 1 else FIXTURE + 0x800))
                for index, node in enumerate(remaining):
                    self.assertEqual(cpu.mem_read(node, 16), struct.pack(
                        "<QQ", remaining[index + 1] if index + 1 < len(remaining) else 0,
                        remaining[index - 1] if index else 0))
                self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RIP), RETURN_SENTINEL)
                self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RSP), STACK_TOP + 8)
                for register in NONVOLATILE:
                    self.assertEqual(cpu.reg_read(register), 0x12345678)

    def test_station_mfc140_thread_state_constructor_preserves_map(self) -> None:
        function = self._verified_station_mfc_functions()[0x180137D00]
        for initial_map in (0, FIXTURE + 0x400):
            with self.subTest(initial_map=initial_map):
                cpu = Uc(UC_ARCH_X86, UC_MODE_64)
                for base, size in ((0x180137000, 0x1000), (FIXTURE, 0x1000),
                                   (STACK_BASE, 0x10000), (SCRATCH_CODE, 0x1000)):
                    cpu.mem_map(base, size)
                for instruction in function["instructions"]:
                    cpu.mem_write(int(instruction["address"], 16), bytes.fromhex(instruction["bytes"]))
                cpu.mem_write(FIXTURE, b"\xCC" * 0x138)
                cpu.mem_write(FIXTURE + 0x28, struct.pack("<Q", initial_map))
                cpu.mem_write(STACK_TOP, struct.pack("<Q", RETURN_SENTINEL))
                cpu.reg_write(registers.UC_X86_REG_RSP, STACK_TOP)
                cpu.reg_write(registers.UC_X86_REG_RCX, FIXTURE)
                for register in NONVOLATILE:
                    cpu.reg_write(register, 0x12345678)
                cpu.emu_start(0x180137D00, RETURN_SENTINEL, count=100)
                self.assertEqual(cpu.mem_read(FIXTURE + 0x28, 8), struct.pack("<Q", initial_map))
                self.assertEqual(cpu.mem_read(FIXTURE + 0x18, 8), struct.pack("<Q", 0x108))
                self.assertEqual(cpu.mem_read(FIXTURE + 0x50, 8), struct.pack("<Q", 0x18008C790))
                self.assertEqual(cpu.mem_read(FIXTURE + 0x68, 8), bytes(8))
                self.assertEqual(cpu.mem_read(FIXTURE + 0x70, 4), struct.pack("<I", 0x11))
                self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RAX), FIXTURE)
                self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RIP), RETURN_SENTINEL)
                self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RSP), STACK_TOP + 8)
                for register in NONVOLATILE:
                    self.assertEqual(cpu.reg_read(register), 0x12345678)

    def test_station_mfc140_thread_slot_decisions(self) -> None:
        function = self._verified_station_mfc_functions()[0x18014F850]
        for label, slot, tls_mode, cached, factory, stop in (
            ("cached", 1, "normal", True, True, RETURN_SENTINEL),
            ("negative_slot", -1, "normal", True, True, 0x18014F92A),
            ("slot_at_limit", 4, "normal", True, True, 0x18014F92A),
            ("missing_tls", 1, "missing", True, True, 0x18014F92A),
            ("missing_array", 1, "no_array", True, True, 0x18014F92A),
            ("thread_slot_at_limit", 1, "short", True, True, 0x18014F92A),
            ("empty_slot", 1, "normal", False, True, 0x18014F92A),
            ("missing_factory", 1, "normal", True, False, 0x18014F95B),
            ("unallocated_slot", 0, "normal", True, True, 0x18014F8B0),
        ):
            with self.subTest(case=label):
                cpu = Uc(UC_ARCH_X86, UC_MODE_64)
                for base, size in ((0x18014F000, 0x1000), (0x1803ED000, 0x1000),
                                   (FIXTURE, 0x1000), (STACK_BASE, 0x10000), (SCRATCH_CODE, 0x1000)):
                    cpu.mem_map(base, size)
                for instruction in function["instructions"]:
                    cpu.mem_write(int(instruction["address"], 16), bytes.fromhex(instruction["bytes"]))
                manager, tls_value, slots, value = (FIXTURE + offset for offset in (0x100, 0x200, 0x300, 0x400))
                cpu.mem_write(FIXTURE, struct.pack("<i", slot))
                cpu.mem_write(0x1803ED4F8, struct.pack("<Q", manager))
                cpu.mem_write(manager, struct.pack("<I", 7))
                cpu.mem_write(manager + 0xC, struct.pack("<I", 4))
                cpu.mem_write(tls_value + 0x10, struct.pack("<I", 1 if tls_mode == "short" else 4))
                cpu.mem_write(tls_value + 0x18, struct.pack("<Q", 0 if tls_mode == "no_array" else slots))
                cpu.mem_write(slots + 8, struct.pack("<Q", value if cached else 0))
                cpu.mem_write(STACK_TOP, struct.pack("<Q", RETURN_SENTINEL))
                cpu.reg_write(registers.UC_X86_REG_RSP, STACK_TOP)
                cpu.reg_write(registers.UC_X86_REG_RCX, FIXTURE)
                cpu.reg_write(registers.UC_X86_REG_RDX, 0x180138340 if factory else 0)
                for register in NONVOLATILE:
                    cpu.reg_write(register, 0x12345678)
                calls = []
                lock_depth = 0

                def dispatch(emulator: Uc, address: int, size: int, _: object) -> None:
                    nonlocal lock_depth
                    if address == stop:
                        self.assertEqual(lock_depth, 0)
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RSP) % 16, 0)
                        if address == 0x18014F92A:
                            self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RAX), 0x180138340)
                        elif address == 0x18014F8B0:
                            self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RCX), manager)
                        emulator.emu_stop()
                        return
                    if address not in (0x18014F8D0, 0x18014F8E1, 0x18014F904, 0x18014F90F, 0x18014F91A):
                        return
                    self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RSP) % 16, 0)
                    if address == 0x18014F8E1:
                        self.assertEqual(lock_depth, 1)
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_ECX), 7)
                        calls.append("tls")
                        result = 0 if tls_mode == "missing" else tls_value
                    else:
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RCX), manager + 0x28)
                        entering = address == 0x18014F8D0
                        self.assertEqual(lock_depth, 0 if entering else 1)
                        lock_depth = int(entering)
                        calls.append("enter" if entering else "leave")
                        result = 0
                    for register in VOLATILE:
                        emulator.reg_write(register, 0xBAD0BAD0)
                    emulator.reg_write(registers.UC_X86_REG_RAX, result)
                    emulator.reg_write(registers.UC_X86_REG_RIP, address + size)

                cpu.hook_add(UC_HOOK_CODE, dispatch)
                cpu.emu_start(0x18014F850, RETURN_SENTINEL, count=150)
                self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RIP), stop)
                self.assertEqual(lock_depth, 0)
                self.assertEqual(calls, (["enter"] + (["tls"] if 0 < slot < 4 else []) + ["leave"])
                                 if factory and slot != 0 else [])
                self.assertEqual(cpu.mem_read(FIXTURE, 4), struct.pack("<i", slot))
                self.assertEqual(cpu.mem_read(slots + 8, 8), struct.pack("<Q", value if cached else 0))
                if stop == RETURN_SENTINEL:
                    self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RAX), value)
                    self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RSP), STACK_TOP + 8)
                    for register in NONVOLATILE:
                        self.assertEqual(cpu.reg_read(register), 0x12345678)

    def test_station_mfc140_window_detach_order(self) -> None:
        functions = self._verified_station_mfc_functions()
        cases = [("cached", *case) for case in (
            (0, False, False, (), 0), (0x1234, False, False, (), 0),
            (0x1234, True, False, (), 0), (0x1234, True, True, (), 0),
            (0x1234, True, True, (0x5678,), 0), (0x1234, True, True, (0x1234,), 0),
            (0x1234, True, True, (0x1234,), 1), (0x1234, True, True, (0x1234,), 2),
            (0x1234, True, True, (0x1234, 0x5678), 2),
            (0x1234, True, True, (0x5678, 0x1234), 2),
            (0x1234, True, True, (0x5678, 0x1234, 0x9ABC), 2),
        )] + [(mode, 0x1234, True, True, (0x1234,), 2) for mode in ("fresh", "other_cached")]
        for state_mode, window, has_map, has_buckets, keys, block_count in cases:
            with self.subTest(state_mode=state_mode, window=window, has_map=has_map, has_buckets=has_buckets,
                              keys=keys, block_count=block_count):
                cpu = Uc(UC_ARCH_X86, UC_MODE_64)
                for base, size in ((0x18028F000, 0x1000), (0x180236000, 0x1000), (FIXTURE, 0x2000),
                                   (0x180275000, 0x1000), (0x180138000, 0x1000),
                                   (0x180137000, 0x1000), (0x1802CE000, 0x1000),
                                   (0x18014F000, 0x1000), (0x1803ED000, 0x1000), (0x1803F3000, 0x1000),
                                   (STACK_BASE, 0x10000), (SCRATCH_CODE, 0x1000)):
                    cpu.mem_map(base, size)
                for entry in (0x18028F560, 0x18028F3C8, 0x180236B90, 0x1802368F0, 0x180275F10,
                              0x1801381E0, 0x1801380F0, 0x18014F850, 0x180138340,
                              0x180137D00, 0x18014F120, 0x18014F4A0):
                    for instruction in functions[entry]["instructions"]:
                        cpu.mem_write(int(instruction["address"], 16), bytes.fromhex(instruction["bytes"]))
                cpu.mem_write(0x1802CEBF0, struct.pack("<Q", SCRATCH_CODE + 0x100))
                cpu.mem_write(SCRATCH_CODE + 0x100, b"\xFF\xE0")
                thread_state = FIXTURE + 0x200
                handle_map = FIXTURE + 0x400 if has_map else 0
                buckets = FIXTURE + 0x600
                nodes = [FIXTURE + 0x700 + index * 0x20 for index in range(len(keys))]
                blocks = [FIXTURE + 0x900 + index * 0x40 for index in range(block_count)]
                tls_manager = FIXTURE + 0xA00
                tls_value = FIXTURE + 0xB00
                tls_slots = FIXTURE + 0xC00
                module_wrapper = FIXTURE + 0xD00
                module_state = FIXTURE + 0xE00
                decoy_state = FIXTURE + 0xF00
                selected_map = has_map and state_mode == "cached"
                removed = window in keys and selected_map
                emptied = removed and len(keys) == 1
                remaining = [node for node, key in zip(nodes, keys) if not removed or key != window]
                cpu.mem_write(0x1803ED4F8, struct.pack("<Q", tls_manager))
                cpu.mem_write(0x1803F32E0, struct.pack("<I", 1))
                cpu.mem_write(tls_manager, struct.pack("<I", 7))
                cpu.mem_write(tls_manager + 0xC, struct.pack("<I", 4))
                cpu.mem_write(tls_value + 0x10, struct.pack("<I", 4))
                cpu.mem_write(tls_value + 0x18, struct.pack("<Q", tls_slots))
                cpu.mem_write(tls_slots + 8, struct.pack("<QQQ", module_wrapper, decoy_state,
                                                       0 if state_mode == "fresh" else thread_state))
                cpu.mem_write(module_wrapper + 8, struct.pack("<Q", module_state))
                cpu.mem_write(module_state + 0xF8, struct.pack("<I", 3))
                owner_map = 0xDEADBEEF if state_mode == "cached" else handle_map
                cpu.mem_write(decoy_state + 0x28, struct.pack("<Q", owner_map))
                cpu.mem_write(thread_state + 0x28, struct.pack("<Q", handle_map if selected_map else 0))
                if state_mode == "fresh":
                    cpu.mem_write(thread_state, b"\xCC" * 0x138)
                if has_map:
                    cpu.mem_write(handle_map + 0x30, struct.pack("<Q", buckets if has_buckets else 0))
                    cpu.mem_write(handle_map + 0x38, struct.pack("<I", 1))
                    cpu.mem_write(handle_map + 0x40, struct.pack("<Q", len(keys)))
                    cpu.mem_write(handle_map + 0x50, struct.pack("<Q", blocks[0] if blocks else 0))
                for index, block in enumerate(blocks):
                    cpu.mem_write(block, struct.pack("<Q", blocks[index + 1]
                                                    if index + 1 < len(blocks) else 0))
                cpu.mem_write(buckets, struct.pack("<Q", nodes[0] if nodes else 0))
                for index, (node, key) in enumerate(zip(nodes, keys)):
                    cpu.mem_write(node, struct.pack("<QQQ", nodes[index + 1]
                                                   if index + 1 < len(nodes) else 0, key, FIXTURE))
                cpu.mem_write(FIXTURE + 0x40, struct.pack("<Q", window))
                cpu.mem_write(FIXTURE + 0xD0, struct.pack("<Q", 0x5678))
                cpu.mem_write(FIXTURE + 0xE8, struct.pack("<Q", FIXTURE + 0x800))
                cpu.mem_write(STACK_TOP, struct.pack("<Q", RETURN_SENTINEL))
                cpu.reg_write(registers.UC_X86_REG_RSP, STACK_TOP)
                cpu.reg_write(registers.UC_X86_REG_RCX, FIXTURE)
                for register in NONVOLATILE:
                    cpu.reg_write(register, 0x12345678)
                calls = []
                freed_blocks = []
                lock_depth = 0

                def dispatch(emulator: Uc, address: int, size: int, _: object) -> None:
                    nonlocal lock_depth
                    if address not in (0x18028F578, 0x18028F3E3, 0x18028F58A,
                                       0x180236BAE, 0x180236C22, 0x18028F58F,
                                       0x180236902, 0x180275F1D, 0x18014F8D0,
                                       0x18014F8E1, 0x18014F904, 0x18014F92A,
                                       0x18014F12C, 0x18014F940, 0x18014F4D0,
                                       0x18014F4E9, 0x18014F5E1):
                        return
                    self.assertEqual(emulator.mem_read(FIXTURE + 0x40, 8), struct.pack("<Q", window))
                    self.assertEqual(emulator.mem_read(FIXTURE + 0xD0, 8), struct.pack("<Q", 0x5678))
                    self.assertEqual(emulator.mem_read(FIXTURE + 0xE8, 8),
                                     struct.pack("<Q", FIXTURE + 0x800))
                    if address == 0x18028F578:
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RCX), 0)
                        calls.append("map_lookup")
                        return
                    if address == 0x18028F3E3:
                        calls.append("thread_state")
                        return
                    if address == 0x18014F92A:
                        self.assertEqual(state_mode, "fresh")
                        self.assertEqual(lock_depth, 0)
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RAX), 0x180138340)
                        calls.append("factory")
                        return
                    if address == 0x18014F940:
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RCX), tls_manager)
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_EDX), 3)
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_R8), thread_state)
                        self.assertEqual(emulator.mem_read(thread_state + 0x28, 8), bytes(8))
                        self.assertEqual(emulator.mem_read(tls_slots + 0x18, 8), bytes(8))
                        calls.append("publish")
                        return
                    if address == 0x18028F58A:
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RCX), handle_map + 0x28)
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RDX), window)
                        calls.append("map_remove")
                        return
                    if address == 0x18028F58F:
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RAX), int(removed))
                        calls.append("clear_window")
                        return
                    if address == 0x180236C22:
                        self.assertTrue(emptied)
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RCX), handle_map + 0x28)
                        self.assertEqual(emulator.mem_read(buckets, 8), bytes(8))
                        self.assertEqual(emulator.mem_read(handle_map + 0x40, 8), bytes(8))
                        calls.append("empty_map_cleanup")
                        return
                    tail_return = address == 0x18014F5E1
                    self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RSP) % 16, 8 if tail_return else 0)
                    if address in (0x18014F8D0, 0x18014F4D0):
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RCX), tls_manager + 0x28)
                        self.assertEqual(lock_depth, 0)
                        lock_depth = 1
                        calls.append("enter_lock_stub")
                        result = 0
                    elif address in (0x18014F8E1, 0x18014F4E9):
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_ECX), 7)
                        self.assertEqual(lock_depth, 1)
                        calls.append("tls_get_stub")
                        result = tls_value
                    elif address in (0x18014F904, 0x18014F5E1):
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RCX), tls_manager + 0x28)
                        self.assertEqual(lock_depth, 1)
                        lock_depth = 0
                        calls.append("leave_lock_stub")
                        result = 0
                        if tail_return:
                            self.assertEqual(emulator.mem_read(tls_slots + 0x18, 8), struct.pack("<Q", thread_state))
                    elif address == 0x18014F12C:
                        self.assertEqual(lock_depth, 0)
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_ECX), 0x40)
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RDX), 0x138)
                        emulator.mem_write(thread_state, bytes(0x138))
                        calls.append("zero_alloc_stub")
                        result = thread_state
                    elif address == 0x180236BAE:
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_ECX), window)
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_EDX), 0x1F31D)
                        quotient, remainder = divmod(window, 0x1F31D)
                        result = quotient | (remainder << 32)
                        calls.append("ldiv_stub")
                    elif address == 0x180236902:
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RCX), buckets)
                        self.assertEqual(emulator.mem_read(handle_map + 0x30, 8), struct.pack("<Q", buckets))
                        self.assertEqual(emulator.mem_read(handle_map + 0x48, 8), struct.pack("<Q", nodes[0]))
                        emulator.mem_write(buckets, b"\xCC" * 8)
                        calls.append("bucket_free_stub")
                        result = 0
                    else:
                        block = emulator.reg_read(registers.UC_X86_REG_RCX)
                        self.assertLess(len(freed_blocks), len(blocks))
                        self.assertEqual(block, blocks[len(freed_blocks)])
                        self.assertEqual(emulator.mem_read(handle_map + 0x30, 8), bytes(8))
                        self.assertEqual(emulator.mem_read(handle_map + 0x40, 8), bytes(8))
                        self.assertEqual(emulator.mem_read(handle_map + 0x48, 8), bytes(8))
                        self.assertEqual(emulator.mem_read(handle_map + 0x50, 8), struct.pack("<Q", blocks[0]))
                        emulator.mem_write(block, b"\xCC" * 0x40)
                        freed_blocks.append(block)
                        calls.append("block_free_stub")
                        result = 0
                    for register in VOLATILE:
                        emulator.reg_write(register, 0xBAD0BAD0)
                    emulator.reg_write(registers.UC_X86_REG_RAX, result)
                    if tail_return:
                        stack = emulator.reg_read(registers.UC_X86_REG_RSP)
                        emulator.reg_write(registers.UC_X86_REG_RIP, struct.unpack("<Q", emulator.mem_read(stack, 8))[0])
                        emulator.reg_write(registers.UC_X86_REG_RSP, stack + 8)
                    else:
                        emulator.reg_write(registers.UC_X86_REG_RIP, address + size)

                cpu.hook_add(UC_HOOK_CODE, dispatch)
                cpu.emu_start(0x18028F560, RETURN_SENTINEL, count=700)
                self.assertEqual(calls, (["map_lookup", "thread_state"] +
                                        ["enter_lock_stub", "tls_get_stub", "leave_lock_stub"] * 2
                                        if window else []) +
                                                                 (["factory", "zero_alloc_stub", "publish", "enter_lock_stub",
                                                                     "tls_get_stub", "leave_lock_stub"] if state_mode == "fresh" else []) +
                                                                 (["map_remove"] if window and selected_map else []) +
                                                                 (["ldiv_stub"] if window and selected_map and has_buckets else []) +
                                 (["empty_map_cleanup", "bucket_free_stub"] +
                                  ["block_free_stub"] * block_count if emptied else []) +
                                 (["clear_window"] if window else []))
                self.assertEqual(freed_blocks, blocks if emptied else [])
                self.assertEqual(lock_depth, 0)
                self.assertEqual(cpu.mem_read(tls_slots + 8, 24),
                                 struct.pack("<QQQ", module_wrapper, decoy_state, thread_state))
                self.assertEqual(cpu.mem_read(decoy_state + 0x28, 8), struct.pack("<Q", owner_map))
                self.assertEqual(cpu.mem_read(thread_state + 0x28, 8),
                                 struct.pack("<Q", handle_map if selected_map else 0))
                if has_map:
                    self.assertEqual(cpu.mem_read(handle_map + 0x30, 8), struct.pack(
                        "<Q", buckets if has_buckets and not emptied else 0))
                    self.assertEqual(cpu.mem_read(handle_map + 0x40, 8),
                                     struct.pack("<Q", len(keys) - int(removed)))
                    self.assertEqual(cpu.mem_read(handle_map + 0x48, 8),
                                     struct.pack("<Q", nodes[keys.index(window)] if removed and not emptied else 0))
                    self.assertEqual(cpu.mem_read(handle_map + 0x50, 8),
                                     struct.pack("<Q", blocks[0] if blocks and not emptied else 0))
                    self.assertEqual(cpu.mem_read(buckets, 8),
                                     b"\xCC" * 8 if emptied else struct.pack("<Q", remaining[0] if remaining else 0))
                    for index, node in enumerate(remaining):
                        self.assertEqual(cpu.mem_read(node, 8), struct.pack("<Q", remaining[index + 1]
                                         if index + 1 < len(remaining) else 0))
                for index, block in enumerate(blocks):
                    self.assertEqual(cpu.mem_read(block, 0x40), b"\xCC" * 0x40 if emptied else
                                     struct.pack("<Q", blocks[index + 1] if index + 1 < len(blocks) else 0) + bytes(0x38))
                self.assertEqual(cpu.mem_read(FIXTURE + 0x40, 8), bytes(8))
                self.assertEqual(cpu.mem_read(FIXTURE + 0xD0, 8), bytes(8))
                self.assertEqual(cpu.mem_read(FIXTURE + 0xE8, 8), struct.pack("<Q", FIXTURE + 0x800))
                self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RAX), window)
                self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RIP), RETURN_SENTINEL)
                self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RSP), STACK_TOP + 8)
                for register in NONVOLATILE:
                    self.assertEqual(cpu.reg_read(register), 0x12345678)

    def test_station_mfc140_frame_destroy_dispatch(self) -> None:
        function = self._verified_station_mfc_functions()[0x1802ABB20]
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        report = json.loads((ROOT / "maps" / "rev2a_skip_frame_factory.json").read_text(encoding="utf-8"))
        self.assertEqual(report["source_sha256"], SOURCE_HASH)
        with pefile.PE(data=source, fast_load=True) as image:
            for retained_function in report["functions"]:
                for instruction in retained_function["instructions"]:
                    retained = bytes.fromhex(instruction["bytes"])
                    self.assertEqual(image.get_data(int(instruction["address"], 16) -
                                                    IMAGE_BASE, len(retained)), retained)
            anchor = image.get_data(0x67C2AE, 7)
            self.assertEqual(anchor[:3], b"\x48\x8d\x05")
            self.assertEqual(0x14067C2B5 + struct.unpack("<i", anchor[3:])[0], 0x140EA1720)
            self.assertEqual(image.get_data(0x67C2B5, 3), b"\x48\x89\x03")
            self.assertEqual(struct.unpack("<Q", image.get_data(0xEA16F8, 8))[0], 0x14067C280)
            self.assertEqual(image.get_string_at_rva(0xEA1AF8), b"CProductionChild")
        for child_window, top_survives in ((0, 0), (0x1234, 0), (0x1234, 1)):
            with self.subTest(child_window=child_window, top_survives=top_survives):
                cpu = Uc(UC_ARCH_X86, UC_MODE_64)
                for base, size in ((0x1802AB000, 0x1000), (FIXTURE, 0x1000),
                                   (STACK_BASE, 0x10000), (SCRATCH_CODE, 0x1000)):
                    cpu.mem_map(base, size)
                for instruction in function["instructions"]:
                    cpu.mem_write(int(instruction["address"], 16), bytes.fromhex(instruction["bytes"]))
                cpu.mem_write(FIXTURE + 0x40, struct.pack("<Q", child_window))
                cpu.mem_write(FIXTURE + 0x100, struct.pack("<Q", FIXTURE + 0x400))
                cpu.mem_write(FIXTURE + 0x140, struct.pack("<Q", 0x5678))
                cpu.mem_write(FIXTURE + 0x240, struct.pack("<Q", 0x9ABC))
                cpu.mem_write(STACK_TOP, struct.pack("<Q", RETURN_SENTINEL))
                cpu.reg_write(registers.UC_X86_REG_RSP, STACK_TOP)
                cpu.reg_write(registers.UC_X86_REG_RCX, FIXTURE)
                for register in NONVOLATILE:
                    cpu.reg_write(register, 0x12345678)
                calls = []
                helpers = {0x1802ABB45: ("top", FIXTURE + 0x100),
                           0x1802ABB59: ("get_style", 0x8000),
                           0x1802ABB6E: ("set_style", 0x8000),
                           0x1802ABB7A: ("parent", 0x9ABC),
                           0x1802ABB83: ("wrapper", FIXTURE + 0x200),
                           0x1802ABB98: ("send_destroy", 0),
                           0x1802ABBA1: ("is_window", top_survives),
                           0x1802ABBB9: ("restore_style", 0),
                           0x1802ABBCE: ("recalculate", 0)}

                def dispatch(emulator: Uc, address: int, size: int, _: object) -> None:
                    if address not in helpers:
                        return
                    helper, result = helpers[address]
                    self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RSP) % 16, 0)
                    calls.append(helper)
                    if helper == "send_destroy":
                        for register, expected in ((registers.UC_X86_REG_RCX, 0x9ABC),
                                                   (registers.UC_X86_REG_RDX, 0x221),
                                                   (registers.UC_X86_REG_R8, child_window),
                                                   (registers.UC_X86_REG_R9, 0)):
                            self.assertEqual(emulator.reg_read(register), expected)
                    elif helper == "recalculate":
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RCX), FIXTURE + 0x100)
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RDX), 1)
                    for register in VOLATILE:
                        emulator.reg_write(register, 0xBAD0BAD0)
                    emulator.reg_write(registers.UC_X86_REG_RAX, result)
                    emulator.reg_write(registers.UC_X86_REG_RIP, address + size)

                cpu.hook_add(UC_HOOK_CODE, dispatch)
                cpu.emu_start(0x1802ABB20, RETURN_SENTINEL, count=100)
                expected_calls = ["top", "get_style", "set_style", "parent", "wrapper",
                                  "send_destroy", "is_window"] if child_window else []
                if top_survives:
                    expected_calls += ["restore_style", "recalculate"]
                self.assertEqual(calls, expected_calls)
                self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RIP), RETURN_SENTINEL)
                self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RAX), int(bool(child_window)))
                self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RSP), STACK_TOP + 8)
                for register in NONVOLATILE:
                    self.assertEqual(cpu.reg_read(register), 0x12345678)

    def test_main_frame_title_slot_does_not_clear_document_binding(self) -> None:
        functions = self._verified_station_mfc_functions()
        getter = functions[0x1802AC6A0]
        title = functions[0x1802ACB00]
        writer = functions[0x1802A4700]
        setter = functions[0x1802B3620]
        self.assertEqual(getter["instructions"][1]["text"], "MOV RCX,qword ptr [RCX + 0x40]")
        self.assertEqual(getter["instructions"][-1]["text"], "JMP 0x18028f480")
        self.assertEqual(title["instructions"][0]["address"], "1802acb00")
        self.assertIn("CALL 0x1802a4700", [item["text"] for item in title["instructions"]])
        self.assertIn("CALL 0x1802b3620", [item["text"] for item in writer["instructions"]])
        setter_calls = [item["text"] for item in setter["instructions"]]
        self.assertEqual(setter_calls.count("CALL qword ptr [0x1802cdea8]"), 1)
        self.assertEqual(setter_calls.count("CALL qword ptr [0x1802cd700]"), 1)
        self.assertEqual(setter_calls.count("CALL qword ptr [0x1802cde20]"), 1)
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        report = json.loads((ROOT / "maps" / "rev2a_skip_top_frame_slot.json").read_text(encoding="utf-8"))
        self.assertEqual(report["source_sha256"], SOURCE_HASH)
        wrapper = next(item for item in report["functions"] if int(item["entry"], 16) == 0x140639C80)
        with pefile.PE(data=source, fast_load=True) as image:
            for function in report["functions"]:
                for instruction in function["instructions"]:
                    retained = bytes.fromhex(instruction["bytes"])
                    self.assertEqual(image.get_data(int(instruction["address"], 16) - IMAGE_BASE,
                                                    len(retained)), retained)
            for table, col, name in (
                (0xE8DC48, 0xF0FBB8, b".?AVCMainFrame@@"),
                (0xE8CE88, 0xF0F7E8, b".?AV?$CExtNCW@VCMDIFrameWnd@@@@"),
            ):
                locator = struct.unpack("<6I", image.get_data(col, 24))
                self.assertEqual(locator[0], 1)
                self.assertEqual(locator[1], 0)
                self.assertEqual(locator[5], col)
                self.assertEqual(image.get_data(locator[3] + 16, len(name)), name)
                self.assertEqual(struct.unpack("<Q", image.get_data(table - 8, 8))[0],
                                 IMAGE_BASE + col)
                self.assertEqual(struct.unpack("<Q", image.get_data(table + 0x358, 8))[0],
                                 0x140639C80)
            encoded = image.get_data(0x780336, 6)
            self.assertEqual(encoded[:2], b"\xff\x25")
            slot = 0x140780336 + 6 + struct.unpack("<i", encoded[2:])[0]
            self.assertEqual(slot, 0x140D5E440)
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image, pefile.PE(
                    str(ROOT / "v3d_files_" / "mfc140.dll"), fast_load=True) as library:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                library.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]])
                imports = {symbol.address: (entry.dll.lower(), symbol.ordinal)
                           for entry in image.DIRECTORY_ENTRY_IMPORT for symbol in entry.imports}
                self.assertEqual(imports[0x140D5E440], (b"mfc140.dll", 11444))
                exports = struct.unpack("<IIHHIIIIIII", library.get_data(
                    library.OPTIONAL_HEADER.DATA_DIRECTORY[0].VirtualAddress, 40))
                ordinal_index = 11444 - exports[5]
                self.assertTrue(0 <= ordinal_index < exports[6])
                self.assertEqual(struct.unpack("<I", library.get_data(
                    exports[8] + ordinal_index * 4, 4))[0], 0x2ACB00)
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit
        reads = []

        def reject_document_read(emulator: Uc, _access: int, address: int, size: int,
                                 _value: int, _user: object) -> None:
            if FIXTURE + 0xE8 <= address < FIXTURE + 0xF0:
                reads.append(address)

        for hwnd, window_exists, expect_paint in ((0, 0, False), (0x1111, 0, False), (0x1111, 1, True)):
            with self.subTest(hwnd=hwnd, window_exists=window_exists):
                cpu = Uc(UC_ARCH_X86, UC_MODE_64)
                for base, size in ((0x140639000, 0x1000), (FIXTURE, 0x1000),
                                   (STACK_BASE, 0x10000)):
                    cpu.mem_map(base, size)
                for instruction in wrapper["instructions"]:
                    cpu.mem_write(int(instruction["address"], 16), bytes.fromhex(instruction["bytes"]))
                cpu.mem_write(FIXTURE + 0x40, struct.pack("<Q", hwnd))
                cpu.mem_write(FIXTURE + 0xE8, struct.pack("<Q", 0xDEC0DE))
                cpu.mem_write(STACK_TOP, struct.pack("<Q", RETURN_SENTINEL))
                cpu.reg_write(registers.UC_X86_REG_RSP, STACK_TOP)
                cpu.reg_write(registers.UC_X86_REG_RCX, 0 if hwnd == 0 else FIXTURE)
                cpu.reg_write(registers.UC_X86_REG_RDX, 1)
                for register in NONVOLATILE:
                    cpu.reg_write(register, 0x12345678)
                calls = []

                def dispatch(emulator: Uc, address: int, size: int, _: object) -> None:
                    if address == 0x140639C93:
                        calls.append("title")
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RCX),
                                         0 if hwnd == 0 else FIXTURE)
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RDX), 1)
                        emulator.reg_write(registers.UC_X86_REG_RIP, address + size)
                    elif address == 0x140639CA0:
                        calls.append("is_window")
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RCX), hwnd)
                        emulator.reg_write(registers.UC_X86_REG_RAX, window_exists)
                        emulator.reg_write(registers.UC_X86_REG_RIP, address + size)
                    elif address == 0x140639CBD:
                        calls.append("paint")
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RCX), hwnd)
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RDX), 0x85)
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_R8), 0)
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_R9), 0)
                        return_address = struct.unpack("<Q", emulator.mem_read(
                            emulator.reg_read(registers.UC_X86_REG_RSP), 8))[0]
                        emulator.reg_write(registers.UC_X86_REG_RSP,
                                           emulator.reg_read(registers.UC_X86_REG_RSP) + 8)
                        emulator.reg_write(registers.UC_X86_REG_RIP, return_address)

                cpu.hook_add(UC_HOOK_CODE, dispatch)
                cpu.hook_add(UC_HOOK_MEM_READ, reject_document_read)
                cpu.emu_start(0x140639C80, RETURN_SENTINEL, count=40)
                expected = ["title"]
                if hwnd:
                    expected.append("is_window")
                if expect_paint:
                    expected.append("paint")
                self.assertEqual(calls, expected)
                self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RIP), RETURN_SENTINEL)
                self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RSP), STACK_TOP + 8)
                self.assertEqual(struct.unpack("<Q", cpu.mem_read(FIXTURE + 0xE8, 8))[0], 0xDEC0DE)
                for register in NONVOLATILE:
                    self.assertEqual(cpu.reg_read(register), 0x12345678)
        self.assertEqual(reads, [])

    def test_title_update_reads_active_document_only_while_view_remains(self) -> None:
        functions = self._verified_station_mfc_functions()
        assign = functions[0x1802A3790]
        read = functions[0x1802A3860]
        destroy = functions[0x18027C060]
        activate = functions[0x18027F240]
        focus = functions[0x18027F2A0]
        self.assertIn("AND qword ptr [RCX + 0x170],0x0",
                      [item["text"] for item in assign["instructions"]])
        self.assertLess(
            next(int(item["address"], 16) for item in assign["instructions"]
                 if item["text"] == "AND qword ptr [RCX + 0x170],0x0"),
            next(int(item["address"], 16) for item in assign["instructions"]
                 if item["text"].startswith("CALL ")),
        )
        self.assertEqual(
            [item["text"] for item in read["instructions"] if "0x170" in item["text"]
             or "0xe8" in item["text"]],
            ["MOV RAX,qword ptr [RCX + 0x170]", "MOV RAX,qword ptr [RAX + 0xe8]"],
        )
        self.assertIn("CMP qword ptr [RAX + 0x170],RBX",
                      [item["text"] for item in destroy["instructions"]])
        self.assertEqual(destroy["instructions"][-1]["text"], "JMP 0x180290020")
        self.assertIn("TEST EDI,EDI", [item["text"] for item in activate["instructions"]])
        self.assertNotIn("CALL 0x1802a3790", [item["text"] for item in focus["instructions"]])
        self.assertNotIn("CALL 0x1802a3790", [item["text"] for item in activate["instructions"]])
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        handler = json.loads((ROOT / "maps" / "rev2a_skip_view_destroy_handler.json")
                             .read_text(encoding="utf-8"))
        self.assertEqual(handler["source_sha256"], SOURCE_HASH)
        self.assertIn("CALL 0x14077fbb0",
                      [item["text"] for function in handler["functions"]
                       for item in function["instructions"]])
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image, pefile.PE(
                    str(ROOT / "v3d_files_" / "mfc140.dll"), fast_load=True) as library:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                library.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]])
                imports = {symbol.address: symbol.ordinal
                           for entry in image.DIRECTORY_ENTRY_IMPORT for symbol in entry.imports}
                exports = struct.unpack("<IIHHIIIIIII", library.get_data(
                    library.OPTIONAL_HEADER.DATA_DIRECTORY[0].VirtualAddress, 40))
                for table, offset, thunk, ordinal, target in (
                    (0xE8DC48, 0x2E8, 0x14077FC46, 4861, 0x1802A3860),
                    (0xE8CE88, 0x2E8, 0x14077FC46, 4861, 0x1802A3860),
                    (0xEA1720, 0x2E8, 0x14077FC46, 4861, 0x1802A3860),
                    (0xEAC650, 0x330, 0x14078058E, 8573, 0x18027F240),
                    (0xEAC650, 0x2B0, 0x14077F67C, 7881, 0x180007360),
                    (0xEA1720, 0x2B0, 0x14077FCBE, 7880, 0x180003AE0),
                    (0xE8DC48, 0x2B0, 0x14077FCBE, 7880, 0x180003AE0),
                ):
                    self.assertEqual(struct.unpack("<Q", image.get_data(table + offset, 8))[0], thunk)
                    encoded = image.get_data(thunk - IMAGE_BASE, 6)
                    self.assertEqual(encoded[:2], b"\xff\x25")
                    slot = thunk + 6 + struct.unpack("<i", encoded[2:])[0]
                    self.assertEqual(imports[slot], ordinal)
                    index = ordinal - exports[5]
                    self.assertEqual(struct.unpack("<I", library.get_data(
                        exports[8] + index * 4, 4))[0], target - 0x180000000)
                destroy_thunk = image.get_data(0x77FBB0, 6)
                self.assertEqual(destroy_thunk[:2], b"\xff\x25")
                destroy_slot = 0x14077FBB0 + 6 + struct.unpack("<i", destroy_thunk[2:])[0]
                self.assertEqual(imports[destroy_slot], 9117)
                self.assertEqual(struct.unpack("<I", library.get_data(
                    exports[8] + (9117 - exports[5]) * 4, 4))[0], 0x27C060)
                self.assertEqual(library.get_data(0x7360, 3), b"\x33\xc0\xc3")
                self.assertEqual(library.get_data(0x3AE0, 6), b"\xb8\x01\x00\x00\x00\xc3")
                parent = library.get_data(0x292A70, 84)
                self.assertEqual(hashlib.sha256(parent).hexdigest(),
                                 "4ede6dd24c022f123d3528ef3badc8be5e019c972f7609d76c789c6ecd48d95c")
                self.assertIn(b"\x48\x8b\x81\xb0\x02\x00\x00", parent)
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit
        frame = FIXTURE
        view = FIXTURE + 0x1000
        virtual = next(int(item["address"], 16) for item in assign["instructions"]
                       if item["text"].startswith("CALL "))
        cpu = Uc(UC_ARCH_X86, UC_MODE_64)
        for base, size in ((0x1802A3000, 0x1000), (FIXTURE, 0x3000), (STACK_BASE, 0x10000)):
            cpu.mem_map(base, size)
        for instruction in assign["instructions"]:
            cpu.mem_write(int(instruction["address"], 16), bytes.fromhex(instruction["bytes"]))
        cpu.mem_write(frame + 0x170, struct.pack("<Q", view))
        cpu.mem_write(view, struct.pack("<Q", view + 0x200))
        cpu.mem_write(view + 0x200 + 0x330, struct.pack("<Q", 0x1802A3F00))
        cpu.mem_write(STACK_TOP, struct.pack("<Q", RETURN_SENTINEL))
        cpu.reg_write(registers.UC_X86_REG_RSP, STACK_TOP)
        cpu.reg_write(registers.UC_X86_REG_RCX, frame)
        cpu.reg_write(registers.UC_X86_REG_RDX, 0)
        cpu.reg_write(registers.UC_X86_REG_R8, 1)
        for register in NONVOLATILE:
            cpu.reg_write(register, 0x12345678)
        seen = []

        def on_virtual(emulator: Uc, address: int, _size: int, _: object) -> None:
            if address != virtual:
                return
            seen.append(struct.unpack("<Q", emulator.mem_read(frame + 0x170, 8))[0])
            self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RDX), 0)
            self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RCX), view)
            emulator.reg_write(registers.UC_X86_REG_RIP, address + _size)

        cpu.hook_add(UC_HOOK_CODE, on_virtual)
        cpu.emu_start(0x1802A3790, RETURN_SENTINEL, count=80)
        self.assertEqual(seen, [0])
        self.assertEqual(struct.unpack("<Q", cpu.mem_read(frame + 0x170, 8))[0], 0)
        self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RIP), RETURN_SENTINEL)
        for base, size in ((0x1802A3000, 0x1000),):
            pass
        reader = Uc(UC_ARCH_X86, UC_MODE_64)
        reader.mem_map(0x1802A3000, 0x1000)
        reader.mem_map(frame, 0x1000)
        reader.mem_map(STACK_BASE, 0x10000)
        for instruction in read["instructions"]:
            reader.mem_write(int(instruction["address"], 16), bytes.fromhex(instruction["bytes"]))
        reader.mem_write(frame + 0x170, struct.pack("<Q", 0))
        reader.mem_write(STACK_TOP, struct.pack("<Q", RETURN_SENTINEL))
        reader.reg_write(registers.UC_X86_REG_RSP, STACK_TOP)
        reader.reg_write(registers.UC_X86_REG_RCX, frame)
        reader.emu_start(0x1802A3860, RETURN_SENTINEL, count=20)
        self.assertEqual(reader.reg_read(registers.UC_X86_REG_RAX), 0)
        reader.mem_map(view, 0x1000)
        reader.mem_write(frame + 0x170, struct.pack("<Q", view))
        reader.mem_write(view + 0xE8, struct.pack("<Q", 0xCAFE))
        reader.reg_write(registers.UC_X86_REG_RSP, STACK_TOP)
        reader.reg_write(registers.UC_X86_REG_RCX, frame)
        reader.emu_start(0x1802A3860, RETURN_SENTINEL, count=20)
        self.assertEqual(reader.reg_read(registers.UC_X86_REG_RAX), 0xCAFE)

    def test_station_mfc140_close_receiver_cached_paths(self) -> None:
        getter = self._verified_station_mfc_functions()[0x1801D0230]
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        report = json.loads((ROOT / "maps" / "rev2a_skip_close_receiver_flags.json")
                            .read_text(encoding="utf-8"))
        self.assertEqual(report["source_sha256"], SOURCE_HASH)
        with pefile.PE(data=source, fast_load=True) as image:
            for function in report["functions"]:
                for instruction in function["instructions"]:
                    retained = bytes.fromhex(instruction["bytes"])
                    self.assertEqual(image.get_data(int(instruction["address"], 16) -
                                                    IMAGE_BASE, len(retained)), retained)
            for offset, target in ((0x1C0, 0x1404E0540), (0x1C8, 0x1404E0510)):
                self.assertEqual(struct.unpack("<Q", image.get_data(
                    0x140E39770 + offset - IMAGE_BASE, 8))[0], target)
        for flags in (0, 1, 2, 3):
            for cached in (0, 1):
                for receiver in (0, FIXTURE + 0x800):
                    if flags and not cached and not receiver:
                        continue
                    with self.subTest(flags=flags, cached=cached, receiver=receiver):
                        cpu = Uc(UC_ARCH_X86, UC_MODE_64)
                        for base, size in ((0x1801D0000, 0x1000), (0x1803F3000, 0x1000),
                                           (0x1404E0000, 0x1000), (FIXTURE, 0x1000),
                                           (STACK_BASE, 0x10000), (SCRATCH_CODE, 0x1000)):
                            cpu.mem_map(base, size)
                        for function in (getter, *report["functions"][:2]):
                            for instruction in function["instructions"]:
                                cpu.mem_write(int(instruction["address"], 16),
                                              bytes.fromhex(instruction["bytes"]))
                        cpu.mem_write(FIXTURE, struct.pack("<Q", FIXTURE + 0x400))
                        cpu.mem_write(FIXTURE + 0x5C0, struct.pack("<QQ", 0x1404E0540, 0x1404E0510))
                        cpu.mem_write(FIXTURE + 0x120, struct.pack("<Q", receiver))
                        cpu.mem_write(FIXTURE + 0x14C, struct.pack("<I", flags))
                        cpu.mem_write(0x1803F3148, struct.pack("<I", cached))
                        cpu.mem_write(STACK_TOP, struct.pack("<Q", RETURN_SENTINEL))
                        cpu.reg_write(registers.UC_X86_REG_RSP, STACK_TOP)
                        cpu.reg_write(registers.UC_X86_REG_RCX, FIXTURE)
                        for register in NONVOLATILE:
                            cpu.reg_write(register, 0x12345678)
                        calls = []

                        def dispatch(emulator: Uc, address: int, size: int, _: object) -> None:
                            if address not in (0x1801D0243, 0x1801D025A):
                                return
                            stack = emulator.reg_read(registers.UC_X86_REG_RSP)
                            target = emulator.reg_read(registers.UC_X86_REG_RAX)
                            self.assertEqual(stack % 16, 0)
                            self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RCX), FIXTURE)
                            self.assertIn(target, (0x1404E0540, 0x1404E0510))
                            calls.append(target)
                            emulator.mem_write(stack - 8, struct.pack("<Q", address + size))
                            emulator.reg_write(registers.UC_X86_REG_RSP, stack - 8)
                            emulator.reg_write(registers.UC_X86_REG_RIP, target)

                        cpu.hook_add(UC_HOOK_CODE, dispatch)
                        cpu.emu_start(0x1801D0230, RETURN_SENTINEL, count=100)
                        self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RIP), RETURN_SENTINEL)
                        self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RAX), receiver)
                        self.assertEqual(cpu.mem_read(FIXTURE + 0x120, 8), struct.pack("<Q", receiver))
                        self.assertEqual(cpu.mem_read(0x1803F3148, 4), struct.pack("<I", 1))
                        self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RSP), STACK_TOP + 8)
                        self.assertEqual(calls, [0x1404E0540] if flags & 1 else
                                         [0x1404E0540, 0x1404E0510])
                        for register in NONVOLATILE:
                            self.assertEqual(cpu.reg_read(register), 0x12345678)

    def test_station_mfc140_pump_dispatch_decisions(self) -> None:
        function = self._verified_station_mfc_functions()[0x180278320]
        for scenario, get_result, message, translated, expected in (
            ("quit", 0, 0x12, 0, []),
            ("registered", 1, 0xC321, 0, ["pretranslate", "translate", "dispatch"]),
            ("command", 1, 0x111, 0, ["pretranslate", "translate", "dispatch"]),
            ("consumed", 1, 0xC321, 1, ["pretranslate"]),
            ("idle", 1, 0x36A, 0, []),
            ("error_with_existing_message", 0xFFFFFFFF, 0xC321, 0,
             ["pretranslate", "translate", "dispatch"]),
        ):
            with self.subTest(scenario=scenario):
                cpu = Uc(UC_ARCH_X86, UC_MODE_64)
                cpu.mem_map(0x180278000, 0x1000)
                cpu.mem_map(FIXTURE, 0x1000)
                cpu.mem_map(STACK_BASE, 0x10000)
                cpu.mem_map(SCRATCH_CODE, 0x1000)
                for instruction in function["instructions"]:
                    cpu.mem_write(int(instruction["address"], 16), bytes.fromhex(instruction["bytes"]))
                cpu.mem_write(FIXTURE + 0x60, struct.pack("<I", message))
                cpu.mem_write(STACK_TOP, struct.pack("<Q", RETURN_SENTINEL))
                cpu.reg_write(registers.UC_X86_REG_RSP, STACK_TOP)
                for register in NONVOLATILE:
                    cpu.reg_write(register, 0x12345678)
                calls = []
                helpers = {0x18027832A: "state", 0x180278341: "get",
                           0x180278357: "pretranslate", 0x180278363: "translate",
                           0x18027836C: "dispatch"}

                def on_instruction(emulator: Uc, address: int, size: int, _: object) -> None:
                    if address not in helpers:
                        return
                    helper = helpers[address]
                    self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RSP) % 16, 0)
                    result = 0
                    if helper == "state":
                        result = FIXTURE
                    else:
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RCX), FIXTURE + 0x58)
                        if helper == "get":
                            for register in (registers.UC_X86_REG_RDX, registers.UC_X86_REG_R8,
                                             registers.UC_X86_REG_R9):
                                self.assertEqual(emulator.reg_read(register), 0)
                            result = get_result
                        else:
                            calls.append(helper)
                            result = translated if helper == "pretranslate" else 1
                    for register in VOLATILE:
                        emulator.reg_write(register, 0xBAD0BAD0)
                    emulator.reg_write(registers.UC_X86_REG_RAX, result)
                    emulator.reg_write(registers.UC_X86_REG_RIP, address + size)

                cpu.hook_add(UC_HOOK_CODE, on_instruction)
                cpu.emu_start(0x180278320, RETURN_SENTINEL, count=100)
                self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RIP), RETURN_SENTINEL)
                self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RAX), int(get_result != 0))
                self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RSP), STACK_TOP + 8)
                for register in NONVOLATILE:
                    self.assertEqual(cpu.reg_read(register), 0x12345678)
                self.assertEqual(calls, expected)

    def test_manual_skip_registry_value_can_set_lane_one_policy(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        report = json.loads((ROOT / "maps" / "rev2a_skip_policy_writers.json")
                            .read_text(encoding="utf-8"))
        self.assertEqual(report["source_sha256"], SOURCE_HASH)
        function = next(function for function in report["functions"]
                        if function["entry"] == "1404ddcd0")
        self.assertIn('"Production.ManualSkipLane1"', function["decompilation"])
        self.assertIn("*(bool *)(param_1 + 0x18d) = local_res18[0] != 0;",
                      function["decompilation"])
        single_lane = json.loads((ROOT / "maps" / "rev2a_skip_policy_single_lane.json")
                     .read_text(encoding="utf-8"))
        bodies = {function["entry"]: function["decompilation"]
              for function in single_lane["functions"]}
        self.assertIn("CAVisionApp::OnProductionStartStandard", bodies["1404dba70"])
        self.assertIn("*(undefined1 *)(param_1 + 0x18d) = local_15b8;", bodies["1404dba70"])
        self.assertIn("CAVisionApp::LaunchSingleProdRemoteOrder", bodies["1404d4510"])
        self.assertIn("*(undefined1 *)(param_1 + 0x18d) = 0;", bodies["1404d4510"])
        dialog = json.loads((ROOT / "maps" / "rev2a_skip_policy_dialog_handler.json")
                    .read_text(encoding="utf-8"))["functions"][0]
        self.assertIn("FUN_1404e0b60(uVar3,2)", dialog["decompilation"])
        self.assertIn("param_1[0xa40] = (CExtResizableDialog)0x1;", dialog["decompilation"])
        self.assertIn("CExtResizableDialog::OnOK(param_1)", dialog["decompilation"])
        instructions = {int(instruction["address"], 16): bytes.fromhex(instruction["bytes"])
                        for instruction in function["instructions"]
                        if 0x1404DE090 <= int(instruction["address"], 16) < 0x1404DE09D}
        self.assertEqual(len(instructions), 3)
        with pefile.PE(data=source, fast_load=True) as image:
            self.assertEqual(struct.unpack("<IIIIQQ", image.get_data(0x140E72630 - IMAGE_BASE, 32)),
                             (0x111, 0, 0x820, 0x820, 0x3A, 0x1405C4AE0))
            for address, retained in instructions.items():
                self.assertEqual(image.get_data(address - IMAGE_BASE, len(retained)), retained)
        for configured in (0, 1, 2, 0xFFFFFFFF):
            with self.subTest(configured=configured):
                cpu = Uc(UC_ARCH_X86, UC_MODE_64)
                cpu.mem_map(IMAGE_BASE, 0x1000000)
                cpu.mem_map(FIXTURE, 0x10000)
                for address, retained in instructions.items():
                    cpu.mem_write(address, retained)
                application = FIXTURE
                frame = FIXTURE + 0x1000
                cpu.mem_write(frame + 0x30, struct.pack("<I", configured))
                cpu.mem_write(application + 0x18D, b"\xff")
                cpu.reg_write(registers.UC_X86_REG_RDI, application)
                cpu.reg_write(registers.UC_X86_REG_RBP, frame)
                end = max(address + len(retained) for address, retained in instructions.items())
                cpu.emu_start(0x1404DE090, end, count=3)
                self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RIP), end)
                self.assertEqual(bytes(cpu.mem_read(application + 0x18D, 1)),
                                 bytes([int(configured != 0)]))

    def test_doevents_uses_unfiltered_thread_pump(self) -> None:
        dll_hash = "f5421b5509236d6a5ba7b20c6e764f0af5e0be131bf2b08e2bbe774ac805767e"
        dll_base = 0x180000000
        source = (ROOT / "v3d_files_" / "DyTools0.dll").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), dll_hash)
        report = json.loads((ROOT / "maps" / "rev2a_skip_doevents.json").read_text(encoding="utf-8"))
        self.assertEqual(report["source_sha256"], dll_hash)
        self.assertEqual(len(report["functions"]), 1)
        function = report["functions"][0]
        self.assertEqual(function["entry"], "1800772b0")
        with pefile.PE(data=source, fast_load=True) as image:
            self.assertEqual(image.OPTIONAL_HEADER.ImageBase, dll_base)
            image.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]])
            exports = [symbol for symbol in image.DIRECTORY_ENTRY_EXPORT.symbols
                       if symbol.name == b"?DoEvents@@YAXXZ"]
            self.assertEqual(len(exports), 1)
            self.assertEqual((exports[0].ordinal, exports[0].address, exports[0].forwarder),
                             (1468, 0x772B0, None))
            for instruction in function["instructions"]:
                retained = bytes.fromhex(instruction["bytes"])
                self.assertEqual(image.get_data(int(instruction["address"], 16) - dll_base,
                                                len(retained)), retained)
        executable = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(executable).hexdigest(), SOURCE_HASH)
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=executable, fast_load=True) as image:
                image.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                imports = [(entry.dll, symbol.name, symbol.ordinal)
                           for entry in image.DIRECTORY_ENTRY_IMPORT for symbol in entry.imports
                           if symbol.address == 0x140D53FC0]
                self.assertEqual(imports, [(b"DyTools0.dll", b"?DoEvents@@YAXXZ", None)])
                self.assertEqual(
                    struct.unpack("<Q", image.get_data(0x140E39770 + 0xC8 - IMAGE_BASE, 8))[0],
                    0x14077F982,
                )
                for thunk, slot, ordinal in (
                    (0x14077F982, 0x140D5FD20, 11881),
                    (0x14077FE26, 0x140D5F5F8, 8850),
                ):
                    encoded = image.get_data(thunk - IMAGE_BASE, 6)
                    self.assertEqual(encoded[:2], b"\xff\x25")
                    self.assertEqual(thunk + 6 + struct.unpack("<i", encoded[2:])[0], slot)
                    bindings = [(entry.dll, symbol.name, symbol.ordinal)
                                for entry in image.DIRECTORY_ENTRY_IMPORT for symbol in entry.imports
                                if symbol.address == slot]
                    self.assertEqual(bindings, [(b"mfc140.dll", None, ordinal)])
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

        for scenario, messages, has_thread, pump_result, expected_pumps in (
            ("empty", [], True, 1, []),
            ("no_thread", [0xC321], False, 1, []),
            ("pump_false", [0xC321], True, 0, [0xC321]),
            ("one_message", [0xC321], True, 1, [0xC321]),
            ("two_messages", [0xC321, 0x111], True, 1, [0xC321, 0x111]),
        ):
            with self.subTest(scenario=scenario):
                cpu = Uc(UC_ARCH_X86, UC_MODE_64)
                cpu.mem_map(dll_base, 0x100000)
                cpu.mem_map(FIXTURE, 0x1000)
                cpu.mem_map(STACK_BASE, 0x10000)
                cpu.mem_map(SCRATCH_CODE, 0x1000)
                for instruction in function["instructions"]:
                    cpu.mem_write(int(instruction["address"], 16), bytes.fromhex(instruction["bytes"]))
                cpu.mem_write(FIXTURE, struct.pack("<Q", FIXTURE + 0x100))
                cpu.mem_write(FIXTURE + 0x1C8, struct.pack("<Q", SCRATCH_CODE))
                cpu.mem_write(STACK_TOP, struct.pack("<Q", RETURN_SENTINEL))
                cpu.reg_write(registers.UC_X86_REG_RSP, STACK_TOP)
                for register in NONVOLATILE:
                    cpu.reg_write(register, 0x12345678)
                pending = list(messages)
                pumped = []
                peeks = []
                thread_calls = []

                def on_instruction(emulator: Uc, address: int, size: int, _: object) -> None:
                    if address not in (0x1800772C9, 0x1800772FE, 0x1800772D3, 0x1800772E3):
                        return
                    stack = emulator.reg_read(registers.UC_X86_REG_RSP)
                    self.assertEqual(stack % 16, 0)
                    if address in (0x1800772C9, 0x1800772FE):
                        self.assertEqual([emulator.reg_read(register) for register in (
                            registers.UC_X86_REG_RDX, registers.UC_X86_REG_R8,
                            registers.UC_X86_REG_R9)], [0, 0, 0])
                        self.assertEqual(bytes(emulator.mem_read(stack + 0x20, 4)), bytes(4))
                        message_buffer = emulator.reg_read(registers.UC_X86_REG_RCX)
                        self.assertEqual(message_buffer, stack + 0x30)
                        emulator.mem_write(message_buffer, bytes(48))
                        if pending:
                            emulator.mem_write(message_buffer, struct.pack("<QI", FIXTURE + 0x300, pending[0]))
                        peeks.append(pending[0] if pending else None)
                        result = int(bool(pending))
                    elif address == 0x1800772D3:
                        thread_calls.append(address)
                        result = FIXTURE if has_thread else 0
                    else:
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RCX), FIXTURE)
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RDX), FIXTURE + 0x100)
                        self.assertTrue(pending)
                        pumped.append(pending.pop(0))
                        result = pump_result
                    for register in VOLATILE:
                        emulator.reg_write(register, 0xBAD0BAD0)
                    emulator.reg_write(registers.UC_X86_REG_RAX, result)
                    emulator.reg_write(registers.UC_X86_REG_RIP, address + size)

                cpu.hook_add(UC_HOOK_CODE, on_instruction)
                cpu.emu_start(0x1800772B0, RETURN_SENTINEL, count=1000)
                self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RIP), RETURN_SENTINEL)
                self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RSP), STACK_TOP + 8)
                self.assertEqual(pumped, expected_pumps)
                expected_peeks = messages if scenario in ("no_thread", "pump_false") else messages + [None]
                self.assertEqual(peeks, expected_peeks)
                self.assertEqual(len(thread_calls), len(messages))
                for register in NONVOLATILE:
                    self.assertEqual(cpu.reg_read(register), 0x12345678)

    def test_supervisor_disconnect_pumps_after_failed_wait(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        report = json.loads((ROOT / "maps" / "rev2a_skip_document_close_nested.json")
                            .read_text(encoding="utf-8"))
        self.assertEqual(report["source_sha256"], SOURCE_HASH)
        matches = [function for function in report["functions"]
                   if function["entry"] == "14064b880"]
        self.assertEqual(len(matches), 1)
        instructions = {int(instruction["address"], 16): bytes.fromhex(instruction["bytes"])
                        for instruction in matches[0]["instructions"]}
        with pefile.PE(data=source, fast_load=True) as image:
            for address, retained in instructions.items():
                self.assertEqual(image.get_data(address - IMAGE_BASE, len(retained)), retained)
        helpers = {
            0x14064B8A7: "wait", 0x14064B8B4: "construct",
            0x14064B8CE: "text", 0x14064B8E1: "create",
            0x14064B8F5: "sleep", 0x14064B8FB: "pump",
            0x14064B90A: "disconnect", 0x14064B921: "beep",
            0x14064B931: "beep", 0x14064B945: "release",
            0x14064B951: "destroy",
        }
        for wait_result in (0, 0xFFFFFFFF):
            for busy in (False, True):
                for show_wait_box in (False, True):
                    with self.subTest(wait_result=wait_result, busy=busy,
                                      show_wait_box=show_wait_box):
                        cpu = Uc(UC_ARCH_X86, UC_MODE_64)
                        cpu.mem_map(IMAGE_BASE, 0x1000000)
                        cpu.mem_map(FIXTURE, 0x1000)
                        cpu.mem_map(STACK_BASE, 0x10000)
                        cpu.mem_map(SCRATCH_CODE, 0x1000)
                        for address, retained in instructions.items():
                            cpu.mem_write(address, retained)
                        cpu.mem_write(FIXTURE + 0x118, struct.pack("<Q", EVENT_HANDLE))
                        cpu.mem_write(FIXTURE + 0x14, bytes([0xC if busy else 0]))
                        cpu.mem_write(FIXTURE + 0x88, bytes([show_wait_box]))
                        cpu.mem_write(STACK_TOP, struct.pack("<Q", RETURN_SENTINEL))
                        cpu.reg_write(registers.UC_X86_REG_RSP, STACK_TOP)
                        for register in NONVOLATILE:
                            cpu.reg_write(register, 0x12345678)
                        cpu.reg_write(registers.UC_X86_REG_RCX, FIXTURE)
                        calls = []

                        def on_instruction(emulator, address, size, _):
                            if address == RETURN_SENTINEL:
                                emulator.emu_stop()
                                return
                            if address not in helpers:
                                return
                            name = helpers[address]
                            calls.append(name)
                            self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RSP) & 15, 0)
                            if name in ("wait", "release"):
                                self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RCX), EVENT_HANDLE)
                                self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RDX),
                                                 0xFFFFFFFF if name == "wait" else 1)
                            if name == "disconnect":
                                self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RCX), FIXTURE)
                            if name == "pump":
                                emulator.mem_write(FIXTURE + 0x14, b"\x00")
                            for register in VOLATILE:
                                emulator.reg_write(register, 0xBAD0BAD0)
                            emulator.reg_write(registers.UC_X86_REG_RAX,
                                               wait_result if name == "wait" else 1)
                            emulator.reg_write(registers.UC_X86_REG_RIP, address + size)

                        cpu.hook_add(UC_HOOK_CODE, on_instruction)
                        cpu.emu_start(0x14064B880, RETURN_SENTINEL + 1, count=500)
                        expected = ["wait", "construct"]
                        if show_wait_box:
                            expected += ["text", "create"]
                        if busy:
                            expected += ["sleep", "pump"]
                        expected += ["disconnect", "beep", "beep", "release", "destroy"]
                        self.assertEqual(calls, expected)
                        self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RIP), RETURN_SENTINEL)
                        self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RSP), STACK_TOP + 8)
                        self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RAX), 1)
                        for register in NONVOLATILE:
                            self.assertEqual(cpu.reg_read(register), 0x12345678)

    def test_delayed_callback_reads_dispatch_time_storage(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        instructions = {}
        with pefile.PE(data=source, fast_load=True) as image:
            for filename, entry in (
                ("rev2a_skip_ui_handler.json", 0x1406B0700),
                ("rev2a_skip_ui_refresh.json", 0x1406ADAF0),
                ("rev2a_skip_ui_list_storage.json", 0x140541040),
                ("rev2a_skip_ui_list_storage.json", 0x140541050),
                ("rev2a_skip_capm_document_accessor.json", 0x14075D010),
                ("rev2a_skip_capm_document_neighbor.json", 0x14075D040),
            ):
                report = json.loads((ROOT / "maps" / filename).read_text(encoding="utf-8"))
                self.assertEqual(report["source_sha256"], SOURCE_HASH)
                matches = [function for function in report["functions"]
                           if int(function["entry"], 16) == entry]
                self.assertEqual(len(matches), 1)
                for instruction in matches[0]["instructions"]:
                    address = int(instruction["address"], 16)
                    retained = bytes.fromhex(instruction["bytes"])
                    self.assertEqual(image.get_data(address - IMAGE_BASE, len(retained)), retained)
                    instructions[address] = retained

        reset_points = {
            "reset_before_size": 0x1406ADB44,
            "reset_after_size": 0x1406ADB50,
            "reset_after_bounds": 0x1406ADB67,
        }
        for scenario in ("unchanged", "reused", "rebound", "retired", "capm_cleared",
                 *reset_points):
            with self.subTest(scenario=scenario):
                cpu = Uc(UC_ARCH_X86, UC_MODE_64)
                cpu.mem_map(IMAGE_BASE, 0x1000000)
                cpu.mem_map(FIXTURE, 0x40000)
                cpu.mem_map(STACK_BASE, 0x10000)
                for address, retained in instructions.items():
                    cpu.mem_write(address, retained)
                old_document = FIXTURE + 0x10000
                new_document = FIXTURE + 0x20000
                for document, data, value in (
                    (old_document, FIXTURE + 0x30000, 17),
                    (new_document, FIXTURE + 0x31000, 42),
                ):
                    cpu.mem_write(document + 0x23E8, struct.pack("<QQ", data, 1))
                    cpu.mem_write(data, struct.pack("<I", value))
                cpu.mem_write(FIXTURE + 0xE8, struct.pack("<Q", old_document))
                if scenario == "reused":
                    cpu.mem_write(FIXTURE + 0x30000, struct.pack("<I", 42))
                elif scenario == "rebound":
                    cpu.mem_write(FIXTURE + 0xE8, struct.pack("<Q", new_document))
                elif scenario == "retired":
                    cpu.mem_unmap(old_document + 0x2000, 0x1000)
                elif scenario == "capm_cleared":
                    capm_interface = FIXTURE + 0x4000
                    document_slots = FIXTURE + 0x5000
                    cpu.mem_write(capm_interface + 0x2E8,
                                  struct.pack("<QQ", document_slots, document_slots + 16))
                    cpu.mem_write(document_slots, struct.pack("<QQ", old_document, 0))
                    for entry in (0x14075D040, 0x14075D010):
                        cpu.reg_write(registers.UC_X86_REG_RCX, capm_interface)
                        cpu.reg_write(registers.UC_X86_REG_RDX, 0)
                        cpu.reg_write(registers.UC_X86_REG_R8, 0)
                        cpu.reg_write(registers.UC_X86_REG_RSP, STACK_TOP)
                        cpu.mem_write(STACK_TOP, struct.pack("<Q", RETURN_SENTINEL))
                        cpu.emu_start(entry, RETURN_SENTINEL, count=100)
                        self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RIP), RETURN_SENTINEL)
                        if entry == 0x14075D040:
                            self.assertEqual(cpu.reg_read(registers.UC_X86_REG_AL), 1)
                        else:
                            self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RAX), 0)
                    self.assertEqual(bytes(cpu.mem_read(document_slots, 8)), bytes(8))
                    self.assertEqual(bytes(cpu.mem_read(FIXTURE + 0xE8, 8)),
                                     struct.pack("<Q", old_document))
                cpu.reg_write(registers.UC_X86_REG_RCX, FIXTURE)
                cpu.reg_write(registers.UC_X86_REG_RDX, 0)
                cpu.reg_write(registers.UC_X86_REG_R8, 0)
                cpu.reg_write(registers.UC_X86_REG_RSP, STACK_TOP)
                cpu.mem_write(STACK_TOP, struct.pack("<Q", RETURN_SENTINEL))
                observed = []
                stubbed = []
                paused = []
                callback_exit = []
                reset_calls = []
                phase = "callback"

                def on_instruction(emulator: Uc, address: int, size: int,
                                   user_data: object) -> None:
                    if phase == "reset":
                        if address == 0x140541066:
                            self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RSP) % 16, 0)
                            self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RCX),
                                             old_document + 0x23E0)
                            self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RDX), 0)
                            self.assertEqual(emulator.reg_read(registers.UC_X86_REG_R8),
                                             0xFFFFFFFFFFFFFFFF)
                            emulator.mem_write(old_document + 0x23E8, struct.pack("<QQ", 0, 0))
                            reset_calls.append("modeled SetSize(0)")
                            for register in VOLATILE:
                                emulator.reg_write(register, 0xBAD0)
                            emulator.reg_write(registers.UC_X86_REG_RIP, address + size)
                        elif address == 0x140541073:
                            self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RCX),
                                             old_document)
                            reset_calls.append("stubbed ClearTestVectorForSkip")
                            stack_pointer = emulator.reg_read(registers.UC_X86_REG_RSP)
                            return_address = struct.unpack("<Q", emulator.mem_read(stack_pointer, 8))[0]
                            emulator.reg_write(registers.UC_X86_REG_RSP, stack_pointer + 8)
                            emulator.reg_write(registers.UC_X86_REG_RIP, return_address)
                        return
                    if address == reset_points.get(scenario) and not paused:
                        paused.append(address)
                        emulator.emu_stop()
                    elif address in (0x1406ADBB8, 0x1406ADBBE):
                        callback_exit.append(address)
                        emulator.emu_stop()
                    elif address == 0x1406ADB7B:
                        observed.append(emulator.reg_read(registers.UC_X86_REG_R8D))
                        emulator.emu_stop()
                    elif address in (0x1406ADB17, 0x1406ADB2E, 0x1406ADB55):
                        self.assertEqual(emulator.reg_read(registers.UC_X86_REG_RSP) % 16, 0)
                        stubbed.append(address)
                        for register in VOLATILE:
                            emulator.reg_write(register, 0xBAD0)
                        emulator.reg_write(registers.UC_X86_REG_RIP, address + size)

                cpu.hook_add(UC_HOOK_CODE, on_instruction)
                start_address = 0x1406B0700
                if scenario in reset_points:
                    cpu.emu_start(start_address, RETURN_SENTINEL, count=1000)
                    self.assertEqual(paused, [reset_points[scenario]])
                    callback_context = cpu.context_save()
                    phase = "reset"
                    reset_stack = STACK_TOP - 0x2000
                    cpu.reg_write(registers.UC_X86_REG_RCX, old_document)
                    cpu.reg_write(registers.UC_X86_REG_RSP, reset_stack)
                    cpu.mem_write(reset_stack, struct.pack("<Q", RETURN_SENTINEL))
                    cpu.emu_start(0x140541050, RETURN_SENTINEL, count=1000)
                    self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RIP), RETURN_SENTINEL)
                    self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RSP), reset_stack + 8)
                    self.assertEqual(reset_calls,
                                     ["modeled SetSize(0)", "stubbed ClearTestVectorForSkip"])
                    self.assertEqual(bytes(cpu.mem_read(old_document + 0x23E8, 16)), bytes(16))
                    cpu.context_restore(callback_context)
                    phase = "callback"
                    start_address = reset_points[scenario]
                if scenario in ("retired", "reset_after_bounds"):
                    with self.assertRaises(UcError) as raised:
                        cpu.emu_start(start_address, RETURN_SENTINEL, count=1000)
                    self.assertEqual(raised.exception.errno, UC_ERR_READ_UNMAPPED)
                    self.assertEqual(cpu.reg_read(registers.UC_X86_REG_RIP),
                                     0x1406ADB44 if scenario == "retired" else 0x1406ADB6B)
                    self.assertEqual(observed, [])
                    self.assertEqual(callback_exit, [])
                else:
                    cpu.emu_start(start_address, RETURN_SENTINEL, count=1000)
                    if scenario in reset_points:
                        self.assertEqual(observed, [])
                        self.assertEqual(callback_exit,
                                         [0x1406ADBBE if scenario == "reset_before_size"
                                          else 0x1406ADBB8])
                    else:
                        self.assertEqual(observed,
                                         [17 if scenario in ("unchanged", "capm_cleared") else 42])
                        self.assertEqual(callback_exit, [])
                self.assertEqual(stubbed, [0x1406ADB17, 0x1406ADB2E] +
                                 ([] if scenario in ("retired", "reset_before_size")
                                  else [0x1406ADB55]))

    def test_system_mdiclient_destroy_reaches_a_direct_child_before_return(self) -> None:
        functions = self._verified_station_mfc_functions()
        created = functions[0x1802AB4A0]["instructions"]
        child = functions[0x1802ABCB0]["instructions"]
        wrapper = [item["text"] for item in functions[0x180298070]["instructions"]]
        self.assertEqual(
            [item["text"] for item in functions[0x1802782E0]["instructions"]],
            ["SUB RSP,0x28", "CALL 0x1801381e0", "MOV RAX,qword ptr [RAX + 0x8]",
             "ADD RSP,0x28", "RET"],
        )
        self.assertEqual(
            [item["text"] for item in functions[0x180279250]["instructions"]
             if "0x48" in item["text"] or "0x40" in item["text"]],
            ["MOV RAX,qword ptr [RCX + 0x48]", "MOV RAX,qword ptr [RCX + 0x40]"],
        )

        def position(items, text):
            return next(index for index, item in enumerate(items) if item["text"] == text)

        self.assertLess(position(created, "LEA RDX,[0x180351270]"),
                        position(created, "CALL 0x180298070"))
        self.assertLess(position(created, "MOV RAX,qword ptr [RDI + 0x40]"),
                        position(created, "MOV qword ptr [RSP + 0x40],RAX"))
        self.assertLess(position(created, "MOV qword ptr [RSP + 0x40],RAX"),
                        position(created, "CALL 0x180298070"))
        self.assertLess(position(created, "CALL 0x180298070"),
                        position(created, "MOV qword ptr [RDI + 0x1d8],RAX"))
        self.assertLess(wrapper.index("MOV RSI,RDX"), wrapper.index("MOV RDX,RSI"))
        self.assertLess(wrapper.index("MOV RDX,RSI"),
                        wrapper.index("CALL qword ptr [0x1802ce0b8]"))
        self.assertEqual(
            next(item["text"] for item in child if item["address"] == "1802abce2"),
            "JNZ 0x1802abd03",
        )
        self.assertLess(
            next(int(item["address"], 16) for item in child if item["address"] == "1802abcf6"),
            0x1802ABD03,
        )
        self.assertLess(
            0x1802ABD03,
            next(int(item["address"], 16) for item in child if item["address"] == "1802abdec"),
        )
        child_text = [item["text"] for item in child]
        self.assertIn("MOV RCX,qword ptr [RDI + 0x1d8]", child_text)
        self.assertIn("MOV RDI,qword ptr [RBP + 0x77]", child_text)
        self.assertIn("MOV RDI,qword ptr [RAX + 0x8]", child_text)
        self.assertIn("MOV RDI,qword ptr [RDI + 0x40]", child_text)
        self.assertIn("MOV EDX,0x220", child_text)
        self.assertIn("CALL qword ptr [0x1802ce3d8]", child_text)

        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image, pefile.PE(
                    str(ROOT / "v3d_files_" / "mfc140.dll"), fast_load=True) as library:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                library.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]])
                exe_imports = {item.address: item.ordinal
                               for entry in image.DIRECTORY_ENTRY_IMPORT
                               for item in entry.imports}
                library_imports = {item.address: item.name.decode() if item.name else str(item.ordinal)
                                   for entry in library.DIRECTORY_ENTRY_IMPORT
                                   for item in entry.imports}
                export = library.DIRECTORY_ENTRY_EXPORT.struct

                def ordinal_rva(ordinal):
                    return struct.unpack(
                        "<I", library.get_data(export.AddressOfFunctions +
                                               (ordinal - export.Base) * 4, 4))[0]

                def thunk_ordinal(address):
                    raw = image.get_data(address - IMAGE_BASE, 6)
                    self.assertEqual(raw[:2], b"\xff\x25")
                    displacement = struct.unpack_from("<i", raw, 2)[0]
                    slot = address + 6 + displacement
                    return exe_imports[slot], ordinal_rva(exe_imports[slot])

                for vtable in (0x140E8DC48, 0x140E8CE88):
                    slot = struct.unpack("<Q", image.get_data(vtable + 0x390 - IMAGE_BASE, 8))[0]
                    self.assertEqual(slot, 0x140780312)
                self.assertEqual(thunk_ordinal(0x140780312), (3178, 0x2AB4A0))
                child_slot = struct.unpack("<Q", image.get_data(0xEA1720 + 0x390, 8))[0]
                self.assertEqual(child_slot, 0x14077FD18)
                self.assertEqual(thunk_ordinal(0x14077FD18), (3093, 0x2ABCB0))
                self.assertEqual(library.get_data(0x351270, 10), b"mdiclient\x00")
                self.assertEqual(library_imports[0x1802CE0B8], "CreateWindowExA")
                self.assertEqual(library_imports[0x1802CE3D8], "SendMessageA")
                self.assertEqual(library_imports[0x1802CDFC8], "GetActiveWindow")

                column = struct.unpack("<Q", library.get_data(0x338170 - 8, 8))[0]
                signature, offset, _cd, type_rva, _hierarchy, self_rva = struct.unpack(
                    "<IIIIII", library.get_data(column - 0x180000000, 24))
                self.assertEqual((signature, offset, self_rva), (1, 0, column - 0x180000000))
                self.assertEqual(library.get_data(type_rva + 16, 17), b".?AVCWinThread@@\x00")
                self.assertEqual(
                    struct.unpack("<Q", library.get_data(0x338170 + 0xF8, 8))[0], 0x180279250)

                client_column = struct.unpack("<Q", image.get_data(0xE8D938 - 8, 8))[0]
                signature, offset, _cd, type_rva, _hierarchy, self_rva = struct.unpack(
                    "<IIIIII", image.get_data(client_column - IMAGE_BASE, 24))
                self.assertEqual((signature, offset, self_rva), (1, 0, client_column - IMAGE_BASE))
                self.assertEqual(image.get_data(type_rva + 16, 20), b".?AVCMDIClientWnd@@\x00")
                getter = struct.unpack("<Q", image.get_data(0xE8D938 + 0x60, 8))[0]
                self.assertEqual(getter, 0x140632180)
                relative = struct.unpack_from("<i", image.get_data(0x632180, 5), 1)[0]
                self.assertEqual(image.get_data(0x632180, 1), b"\xe9")
                self.assertEqual(0x140632185 + relative, 0x140632210)
                leaf = image.get_data(0x632210, 8)
                self.assertEqual(leaf[:3], b"\x48\x8d\x05")
                self.assertEqual(leaf[7], 0xC3)
                derived = 0x140632217 + struct.unpack_from("<i", leaf, 3)[0]
                base_getter, entries = struct.unpack("<QQ", image.get_data(derived - IMAGE_BASE, 16))
                first, _code, _id0, _id1, _sig, function = struct.unpack(
                    "<IIIIQQ", image.get_data(entries - IMAGE_BASE, 32))
                terminator = struct.unpack("<IIIIQQ", image.get_data(entries - IMAGE_BASE + 32, 32))
                self.assertEqual((first, function, terminator[0], terminator[5]),
                                 (0x14, 0x140636A50, 0, 0))
                self.assertEqual(thunk_ordinal(base_getter), (7364, 0x291A00))
                image_messages = []
                raw = library.get_data(0x291A00, 8)
                self.assertEqual(raw[:3], b"\x48\x8d\x05")
                self.assertEqual(raw[7], 0xC3)
                map_va = 0x180291A07 + struct.unpack_from("<i", raw, 3)[0]
                seen = set()
                while map_va not in seen and len(seen) < 4:
                    seen.add(map_va)
                    getter, entries = struct.unpack("<QQ", library.get_data(map_va - 0x180000000, 16))
                    for index in range(80):
                        message, _code, _id0, _id1, _sig, function = struct.unpack(
                            "<IIIIQQ", library.get_data(entries - 0x180000000 + index * 32, 32))
                        if message == 0 and function == 0:
                            break
                        image_messages.append(message)
                    raw = library.get_data(getter - 0x180000000, 8)
                    if raw[:3] != b"\x48\x8d\x05" or raw[7] != 0xC3:
                        break
                    map_va = getter + 7 + struct.unpack_from("<i", raw, 3)[0]
                self.assertIn(2, image_messages)
                self.assertIn(0x82, image_messages)
                self.assertNotIn(0x221, image_messages)

                area_column = struct.unpack("<Q", library.get_data(0x2F3EE8 - 8, 8))[0]
                signature, offset, _cd, type_rva, _hierarchy, self_rva = struct.unpack(
                    "<IIIIII", library.get_data(area_column - 0x180000000, 24))
                self.assertEqual((signature, offset, self_rva), (1, 0, area_column - 0x180000000))
                self.assertEqual(library.get_data(type_rva + 16, 24), b".?AVCMDIClientAreaWnd@@\x00")
                area_message, _code, _id0, _id1, _sig, area_handler = struct.unpack(
                    "<IIIIQQ", library.get_data(0x2F3DA0, 32))
                self.assertEqual((area_message, area_handler), (0x221, 0x18007F310))

                for program, base in ((image, IMAGE_BASE), (library, 0x180000000)):
                    section = next(item for item in program.sections if item.Name.startswith(b".text"))
                    blob = section.get_data()
                    hits = []
                    start = 0
                    pattern = b"\xba\x21\x02\x00\x00"
                    while True:
                        found = blob.find(pattern, start)
                        if found < 0:
                            break
                        hits.append(base + section.VirtualAddress + found)
                        start = found + 1
                    self.assertEqual(hits, [0x1802ABB8F] if base == 0x180000000 else [])
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

        if platform.system() != "Windows":
            self.skipTest("user32 WM_MDIDESTROY probe requires Windows")
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        result_type = ctypes.c_ssize_t
        window_proc = ctypes.WINFUNCTYPE(
            result_type, ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_ssize_t)

        class WindowClass(ctypes.Structure):
            _fields_ = [
                ("style", ctypes.c_uint), ("lpfnWndProc", window_proc),
                ("cbClsExtra", ctypes.c_int), ("cbWndExtra", ctypes.c_int),
                ("hInstance", ctypes.c_void_p), ("hIcon", ctypes.c_void_p),
                ("hCursor", ctypes.c_void_p), ("hbrBackground", ctypes.c_void_p),
                ("lpszMenuName", ctypes.c_char_p), ("lpszClassName", ctypes.c_char_p),
            ]

        class ClientCreate(ctypes.Structure):
            _fields_ = [("hWindowMenu", ctypes.c_void_p), ("idFirstChild", ctypes.c_uint)]

        class MdiCreate(ctypes.Structure):
            _fields_ = [
                ("szClass", ctypes.c_char_p), ("szTitle", ctypes.c_char_p),
                ("hOwner", ctypes.c_void_p), ("x", ctypes.c_int), ("y", ctypes.c_int),
                ("cx", ctypes.c_int), ("cy", ctypes.c_int), ("style", ctypes.c_uint),
                ("lParam", ctypes.c_ssize_t),
            ]

        user32.DefWindowProcA.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_ssize_t]
        user32.DefWindowProcA.restype = result_type
        user32.CallWindowProcA.argtypes = [
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_ssize_t]
        user32.CallWindowProcA.restype = result_type
        user32.RegisterClassA.argtypes = [ctypes.c_void_p]
        user32.RegisterClassA.restype = ctypes.c_ushort
        user32.CreateWindowExA.argtypes = [
            ctypes.c_uint, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint,
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
        user32.CreateWindowExA.restype = ctypes.c_void_p
        user32.SendMessageA.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_ssize_t]
        user32.SendMessageA.restype = result_type
        user32.GetParent.argtypes = [ctypes.c_void_p]
        user32.GetParent.restype = ctypes.c_void_p
        user32.DestroyWindow.argtypes = [ctypes.c_void_p]
        user32.IsWindow.argtypes = [ctypes.c_void_p]
        user32.IsWindow.restype = ctypes.c_int
        user32.UnregisterClassA.argtypes = [ctypes.c_char_p, ctypes.c_void_p]
        observed = {"inside": False, "destroyed": False, "previous": None}

        @window_proc
        def default_proc(hwnd, message, wparam, lparam):
            return user32.DefWindowProcA(hwnd, message, wparam, lparam)

        @window_proc
        def child_proc(hwnd, message, wparam, lparam):
            if message == 2 and observed["inside"]:
                observed["destroyed"] = True
            previous = observed["previous"]
            if previous:
                return user32.CallWindowProcA(previous, hwnd, message, wparam, lparam)
            return user32.DefWindowProcA(hwnd, message, wparam, lparam)

        instance = kernel32.GetModuleHandleA(None)
        frame_name = b"V3DSkipMdiFrame"
        child_name = b"V3DSkipMdiChild"
        classes = ((frame_name, default_proc), (child_name, child_proc))
        frame = None
        try:
            for name, proc in classes:
                descriptor = WindowClass()
                descriptor.lpfnWndProc = proc
                descriptor.hInstance = instance
                descriptor.lpszClassName = name
                if not user32.RegisterClassA(ctypes.byref(descriptor)):
                    raise ctypes.WinError(ctypes.get_last_error())
            frame = user32.CreateWindowExA(
                0, frame_name, b"", 0x02000000, 0, 0, 0, 0, None, None, instance, None)
            self.assertTrue(frame)
            client_state = ClientCreate(None, 100)
            client = user32.CreateWindowExA(
                0x200, b"mdiclient", None, 0x46000000, 0, 0, 0, 0, frame, 0xE900,
                instance, ctypes.byref(client_state))
            self.assertTrue(client)
            created_state = MdiCreate(child_name, b"", instance, 0, 0, 10, 10, 0x40000000, 0)
            mdi_child = user32.SendMessageA(
                client, 0x220, 0, ctypes.addressof(created_state))
            self.assertTrue(mdi_child)
            self.assertEqual(user32.GetParent(mdi_child), client)
            nested = user32.CreateWindowExA(
                0, child_name, None, 0x40000000, 0, 0, 1, 1, mdi_child, 1, instance, None)
            self.assertTrue(nested)
            self.assertEqual(user32.GetParent(nested), mdi_child)
            observed["inside"] = True
            user32.SendMessageA(client, 0x221, mdi_child, 0)
            observed["inside"] = False
            self.assertTrue(observed["destroyed"])
            self.assertFalse(user32.IsWindow(mdi_child))
            self.assertFalse(user32.IsWindow(nested))
        finally:
            if frame:
                user32.DestroyWindow(frame)
            for name, _proc in classes:
                user32.UnregisterClassA(name, instance)

    def test_destroyed_hwnd_retires_the_queued_skip_message_on_this_host(self) -> None:
        if platform.system() != "Windows":
            self.skipTest("user32 queued-message probe requires Windows")
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        result_type = ctypes.c_ssize_t
        window_proc = ctypes.WINFUNCTYPE(
            result_type, ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_ssize_t)

        class WindowClass(ctypes.Structure):
            _fields_ = [
                ("style", ctypes.c_uint), ("lpfnWndProc", window_proc),
                ("cbClsExtra", ctypes.c_int), ("cbWndExtra", ctypes.c_int),
                ("hInstance", ctypes.c_void_p), ("hIcon", ctypes.c_void_p),
                ("hCursor", ctypes.c_void_p), ("hbrBackground", ctypes.c_void_p),
                ("lpszMenuName", ctypes.c_char_p), ("lpszClassName", ctypes.c_char_p),
            ]

        class Point(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

        class Message(ctypes.Structure):
            _fields_ = [
                ("hwnd", ctypes.c_void_p), ("message", ctypes.c_uint),
                ("wParam", ctypes.c_size_t), ("lParam", ctypes.c_ssize_t),
                ("time", ctypes.c_uint), ("pt", Point), ("lPrivate", ctypes.c_uint),
            ]

        user32.DefWindowProcA.argtypes = [
            ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_ssize_t]
        user32.DefWindowProcA.restype = result_type
        user32.RegisterClassA.argtypes = [ctypes.c_void_p]
        user32.RegisterClassA.restype = ctypes.c_ushort
        user32.RegisterWindowMessageA.argtypes = [ctypes.c_char_p]
        user32.RegisterWindowMessageA.restype = ctypes.c_uint
        user32.CreateWindowExA.argtypes = [
            ctypes.c_uint, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint,
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
        user32.CreateWindowExA.restype = ctypes.c_void_p
        user32.PostMessageA.argtypes = [
            ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_ssize_t]
        user32.PostMessageA.restype = ctypes.c_int
        user32.PeekMessageA.argtypes = [
            ctypes.POINTER(Message), ctypes.c_void_p, ctypes.c_uint,
            ctypes.c_uint, ctypes.c_uint]
        user32.PeekMessageA.restype = ctypes.c_int
        user32.DestroyWindow.argtypes = [ctypes.c_void_p]
        user32.DestroyWindow.restype = ctypes.c_int
        user32.IsWindow.argtypes = [ctypes.c_void_p]
        user32.IsWindow.restype = ctypes.c_int
        user32.UnregisterClassA.argtypes = [ctypes.c_char_p, ctypes.c_void_p]

        delivered = []

        @window_proc
        def receiver(hwnd, message, wparam, lparam):
            if message == registered:
                delivered.append((hwnd, message))
            return user32.DefWindowProcA(hwnd, message, wparam, lparam)

        instance = kernel32.GetModuleHandleA(None)
        class_name = b"V3DSkipQueuedMessage"
        descriptor = WindowClass()
        descriptor.lpfnWndProc = receiver
        descriptor.hInstance = instance
        descriptor.lpszClassName = class_name
        window = None
        registered = user32.RegisterWindowMessageA(
            b"{FEA8416F-2D59-478F-BEFF-5D96AFD6A551}")
        self.assertGreaterEqual(registered, 0xC000)
        try:
            if not user32.RegisterClassA(ctypes.byref(descriptor)):
                raise ctypes.WinError(ctypes.get_last_error())
            window = user32.CreateWindowExA(
                0, class_name, b"", 0, 0, 0, 0, 0, None, None, instance, None)
            self.assertTrue(window)
            self.assertTrue(user32.PostMessageA(window, registered, 0, 0))
            queued = Message()
            self.assertTrue(
                user32.PeekMessageA(
                    ctypes.byref(queued), None, registered, registered, 0))
            self.assertEqual(queued.hwnd, window)
            self.assertTrue(user32.DestroyWindow(window))
            self.assertFalse(user32.IsWindow(window))
            retired = Message()
            self.assertFalse(
                user32.PeekMessageA(
                    ctypes.byref(retired), None, registered, registered, 1))
            self.assertFalse(user32.PostMessageA(window, registered, 0, 0))
            self.assertEqual(delivered, [])
            window = None
        finally:
            if window:
                user32.DestroyWindow(window)
            user32.UnregisterClassA(class_name, instance)

    def test_production_view_dialog_parent_is_the_child_frame(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        library_bytes = (ROOT / "v3d_files_" / "mfc140.dll").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        self.assertEqual(hashlib.sha256(library_bytes).hexdigest(),
                         "0cf26008fae0cb61dfe49e1c3fc17e0dd860be011d9a6a64b452f56335bafbfe")
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image, pefile.PE(
                    data=library_bytes, fast_load=True) as library:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                library.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]])
                exe_imports = {item.address: item.ordinal
                               for entry in image.DIRECTORY_ENTRY_IMPORT
                               for item in entry.imports}
                library_imports = {item.address: item.name.decode() if item.name else str(item.ordinal)
                                   for entry in library.DIRECTORY_ENTRY_IMPORT
                                   for item in entry.imports}
                export = library.DIRECTORY_ENTRY_EXPORT.struct

                def ordinal_rva(ordinal):
                    return struct.unpack(
                        "<I", library.get_data(export.AddressOfFunctions +
                                               (ordinal - export.Base) * 4, 4))[0]

                def thunk_ordinal(address):
                    raw = image.get_data(address - IMAGE_BASE, 6)
                    self.assertEqual(raw[:2], b"\xff\x25")
                    displacement = struct.unpack_from("<i", raw, 2)[0]
                    return exe_imports[address + 6 + displacement]

                def relative_target(program, rva, opcode):
                    raw = program.get_data(rva, 5)
                    self.assertEqual(raw[0], opcode)
                    return rva + 5 + struct.unpack_from("<i", raw, 1)[0]

                def lea_target(program, rva, image_base):
                    raw = program.get_data(rva, 8)
                    self.assertEqual(raw[:3], b"\x48\x8d\x05")
                    self.assertEqual(raw[7], 0xC3)
                    return image_base + rva + 7 + struct.unpack_from("<i", raw, 3)[0]

                for site in (0x4D3605, 0x4D3662):
                    self.assertEqual(IMAGE_BASE + relative_target(image, site, 0xE8), 0x1406AC4B0)
                    self.assertEqual(IMAGE_BASE + relative_target(image, site + 8, 0xE8), 0x14067C2E0)
                    self.assertEqual(IMAGE_BASE + relative_target(image, site + 16, 0xE8), 0x1406892A0)
                    self.assertEqual(image.get_data(site + 24, 5), bytes.fromhex("48897c2420"))
                    self.assertEqual(image.get_data(site + 32, 5), bytes.fromhex("bad10b0000"))
                self.assertEqual(thunk_ordinal(0x14077FAAE), 804)
                self.assertEqual(ordinal_rva(804), 0x228C90)
                self.assertEqual(library.get_data(0x2296C7, 5), bytes.fromhex("574883ec30"))
                self.assertEqual(library.get_data(0x22974A, 7), bytes.fromhex("4889bdb0000000"))
                self.assertEqual(library.get_data(0x229751, 7), bytes.fromhex("4889b5b8000000"))
                self.assertEqual(library.get_data(0x229758, 12), bytes.fromhex("488b442460488985c0000000"))
                self.assertEqual(0x60 - (8 + 0x30), 0x28)

                getter = struct.unpack("<Q", image.get_data(0xEA1720 + 0x60, 8))[0]
                self.assertEqual(getter, 0x14067C2D0)
                self.assertEqual(IMAGE_BASE + relative_target(image, 0x67C2D0, 0xE9), 0x14067C2F0)
                child_map = lea_target(image, 0x67C2F0, IMAGE_BASE)
                self.assertEqual(child_map, 0x140EA1AE8)
                base_getter, entries = struct.unpack("<QQ", image.get_data(child_map - IMAGE_BASE, 16))
                first = struct.unpack("<IIIIQQ", image.get_data(entries - IMAGE_BASE, 32))
                self.assertEqual((first[0], first[5]), (0, 0))
                self.assertEqual(thunk_ordinal(base_getter), 7222)
                self.assertEqual(ordinal_rva(7222), 0x2ABA80)
                mdi_child_map = lea_target(library, 0x2ABA80, 0x180000000)
                self.assertEqual(mdi_child_map, 0x180342050)
                base_fn, entries = struct.unpack("<QQ", library.get_data(mdi_child_map - 0x180000000, 16))
                create = None
                for index in range(16):
                    message, _code, _id0, _id1, _sig, function = struct.unpack(
                        "<IIIIQQ", library.get_data(entries - 0x180000000 + index * 32, 32))
                    if message == 0 and function == 0:
                        break
                    if message == 1:
                        create = function
                self.assertEqual(create, 0x1802ACAF0)
                self.assertEqual(library.get_data(0x2ACAF0, 12), bytes.fromhex("488b024c8b4030e9845affff"))
                self.assertEqual(0x1802ACAF0 + 12 + struct.unpack_from("<i", bytes.fromhex("845affff"), 0)[0],
                                 0x1802A2580)
                self.assertEqual(library.get_data(0x2A25AE, 7), bytes.fromhex("488b8050030000"))
                child_create = struct.unpack("<Q", image.get_data(0xEA1720 + 0x350, 8))[0]
                self.assertEqual(child_create, 0x14077FCA6)
                self.assertEqual((thunk_ordinal(child_create), ordinal_rva(thunk_ordinal(child_create))),
                                 (9003, 0x2A2530))
                self.assertEqual(library.get_data(0x2A2530, 0x2F), bytes.fromhex(
                    "4883ec28498bc04d85c0741949833800741341b800e90000488bd0e800ffffff"
                    "4885c07405b8010000004883c428c3"))
                self.assertEqual(0x1802A254B + 5 + struct.unpack_from(
                    "<i", library.get_data(0x2A254B, 5), 1)[0], 0x1802A2450)
                self.assertEqual(library.get_data(0x2A2471, 3), bytes.fromhex("488bf1"))
                self.assertEqual(library.get_data(0x2A24B2, 14), bytes.fromhex("488974242833d2488b81b8000000"))
                self.assertEqual(library.get_data(0x2A24A5, 6), bytes.fromhex("41b900008050"))

                view_create = struct.unpack("<Q", image.get_data(0xEAC650 + 0xB8, 8))[0]
                self.assertEqual(view_create, 0x140780582)
                self.assertEqual((thunk_ordinal(view_create), ordinal_rva(thunk_ordinal(view_create))),
                                 (3075, 0x27F050))
                self.assertEqual(image.get_data(0x6AB597, 10), bytes.fromhex("ba2b080000e8c94f0d00"))
                self.assertEqual(IMAGE_BASE + relative_target(image, 0x6AB59C, 0xE8), 0x14078056A)
                self.assertEqual(thunk_ordinal(0x14078056A), 499)
                self.assertEqual(ordinal_rva(499), 0x27EF30)
                self.assertEqual(library.get_data(0x27EF3A, 2), bytes.fromhex("8bda"))
                self.assertEqual(library.get_data(0x27EF52, 3), bytes.fromhex("0fb7c3"))
                self.assertEqual(library.get_data(0x27EF5A, 7), bytes.fromhex("48898730010000"))
                self.assertNotEqual(0x82B, 0)

                self.assertEqual(-(0x28 + 0x17) + 0x6F, 0x30)
                self.assertEqual(library.get_data(0x27F084, 4), bytes.fromhex("4c8b7d6f"))
                self.assertEqual(library.get_data(0x27F0E9, 6), bytes.fromhex("4d8bc7488bcf"))
                self.assertEqual(0x180000000 + relative_target(library, 0x27F0EF, 0xE8), 0x18020B530)
                self.assertEqual(library.get_data(0x20B554, 3), bytes.fromhex("498be8"))
                self.assertEqual(library.get_data(0x20B592, 3), bytes.fromhex("4c8bc5"))
                self.assertEqual(0x180000000 + relative_target(library, 0x20B5B5, 0xE9), 0x18020B5C0)
                self.assertEqual(library.get_data(0x20B5EA, 3), bytes.fromhex("4d8be8"))
                self.assertEqual(library.get_data(0x20B67A, 12), bytes.fromhex("4d85f6750733c0e982010000"))
                self.assertEqual(0x180000000 + relative_target(library, 0x20B681, 0xE9), 0x18020B808)
                self.assertLess(0x18020B726, 0x18020B808)
                self.assertEqual(library.get_data(0x20B71E, 12), bytes.fromhex("4d85ed4c8bc374044d8b4540"))
                call = library.get_data(0x20B730, 5)
                self.assertEqual(call[0], 0xE8)
                dialog = 0x18020B730 + 5 + struct.unpack_from("<i", call, 1)[0]
                self.assertEqual(dialog, 0x18020C190)
                self.assertEqual(library.get_data(0x20C1A4, 3), bytes.fromhex("498bd8"))
                self.assertEqual(library.get_data(0x20C1F5, 9), bytes.fromhex("4c8bc3488bd7488bce"))
                import_call = library.get_data(0x20C1FE, 6)
                self.assertEqual(import_call[:2], b"\xff\x15")
                displacement = struct.unpack_from("<i", import_call, 2)[0]
                self.assertEqual(library_imports[0x18020C1FE + 6 + displacement],
                                 "CreateDialogIndirectParamA")
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_template_view_class_reaches_the_create_context(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        library_bytes = (ROOT / "v3d_files_" / "mfc140.dll").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        self.assertEqual(hashlib.sha256(library_bytes).hexdigest(),
                         "0cf26008fae0cb61dfe49e1c3fc17e0dd860be011d9a6a64b452f56335bafbfe")
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image, pefile.PE(
                    data=library_bytes, fast_load=True) as library:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                library.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]])
                exe_imports = {item.address: item.ordinal
                               for entry in image.DIRECTORY_ENTRY_IMPORT
                               for item in entry.imports}
                export = library.DIRECTORY_ENTRY_EXPORT.struct

                def ordinal_rva(ordinal):
                    return struct.unpack(
                        "<I", library.get_data(export.AddressOfFunctions +
                                               (ordinal - export.Base) * 4, 4))[0]

                def thunk_ordinal(address):
                    raw = image.get_data(address - IMAGE_BASE, 6)
                    self.assertEqual(raw[:2], b"\xff\x25")
                    displacement = struct.unpack_from("<i", raw, 2)[0]
                    return exe_imports[address + 6 + displacement]

                self.assertEqual(library.get_data(0x228CB6, 10), bytes.fromhex("488d052b701000488903"))
                vtable = 0x180228CBD + 0x10702B
                self.assertEqual(vtable, 0x18032FCE8)
                self.assertEqual(struct.unpack("<Q", library.get_data(0x32FCE8 + 0xF0, 8))[0], 0x180229CE0)
                self.assertEqual(struct.unpack("<Q", library.get_data(0x32FCE8 + 0x110, 8))[0], 0x180228ED0)
                self.assertEqual(library.get_data(0x228EFE, 3), bytes.fromhex("488bf1"))
                self.assertEqual(library.get_data(0x228F3D, 20),
                                 bytes.fromhex("488b064533c0488bd7488bce488b80f0000000ff"))
                self.assertEqual(library.get_data(0x229D09, 24),
                                 bytes.fromhex("488b8eb8000000488b86c000000048895c245048897c2438"))
                self.assertEqual(library.get_data(0x229D21, 10), bytes.fromhex("48894424304889742440"))
                self.assertEqual(library.get_data(0x229D43, 29),
                                 bytes.fromhex("8b969800000041b80080cf00488b81e0020000488d4c243048894c2420"))
                child_load = struct.unpack("<Q", image.get_data(0xEA1720 + 0x2E0, 8))[0]
                self.assertEqual(child_load, 0x14077FD2A)
                self.assertEqual(thunk_ordinal(child_load), 8062)
                self.assertEqual(ordinal_rva(8062), 0x2ABEC0)
                self.assertEqual(library.get_data(0x2ABEC3, 12), bytes.fromhex("56574154415641574883ec50"))
                self.assertEqual(0xA0 - (5 * 8 + 0x50), 0x28)
                self.assertEqual(library.get_data(0x2ABEF5, 8), bytes.fromhex("4c8bbc24a0000000"))
                self.assertEqual(library.get_data(0x2ABFC9, 5), bytes.fromhex("4c897c2430"))
                self.assertEqual(library.get_data(0x2ABFE8, 7), bytes.fromhex("488b8790030000"))
                self.assertEqual(0x7F - 0x47, 0x38)
                self.assertEqual(-0x11 + 0x30, 0x1F)
                self.assertEqual(library.get_data(0x2ABD67, 8), bytes.fromhex("488b457f4889459f"))
                self.assertEqual(library.get_data(0x2ABDDF, 8), bytes.fromhex("488b459f4889451f"))
                self.assertEqual(library.get_data(0x2ABDF3, 4), bytes.fromhex("4c8d4def"))
                self.assertEqual(library.get_data(0x2ABDFA, 5), bytes.fromhex("ba20020000"))
                self.assertEqual(library.get_data(0x2ACAF0, 12), bytes.fromhex("488b024c8b4030e9845affff"))
                self.assertEqual(0x1802ACAFC + struct.unpack("<i", bytes.fromhex("845affff"))[0], 0x1802A2580)
                self.assertEqual(library.get_data(0x2A253C, 4), bytes.fromhex("49833800"))
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_title_reads_the_child_document_only_when_the_frame_field_is_null(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        library_bytes = (ROOT / "v3d_files_" / "mfc140.dll").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        self.assertEqual(hashlib.sha256(library_bytes).hexdigest(),
                         "0cf26008fae0cb61dfe49e1c3fc17e0dd860be011d9a6a64b452f56335bafbfe")
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image, pefile.PE(
                    data=library_bytes, fast_load=True) as library:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                library.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]])
                ordinals = {item.ordinal for entry in image.DIRECTORY_ENTRY_IMPORT
                            for item in entry.imports}
                self.assertNotIn(12856, ordinals)
                export = library.DIRECTORY_ENTRY_EXPORT.struct
                setter = struct.unpack(
                    "<I", library.get_data(export.AddressOfFunctions + (12856 - export.Base) * 4, 4))[0]
                self.assertEqual(setter, 0x2A3790)
                self.assertEqual(library.get_data(0x2A3860, 10), bytes.fromhex("488b81700100004885c0"))

                title = library.get_data(0x2ACB00, 0x182)
                branch = title.index(bytes.fromhex("4885db75"))
                self.assertLess(title.index(bytes.fromhex("488b80e8020000")), branch)
                call = title.index(bytes.fromhex("e8ccecffff"))
                self.assertLess(call, branch)
                self.assertEqual(0x1802ACB00 + call + 5 + struct.unpack_from("<i", title, call + 1)[0],
                                 0x1802AB840)
                displacement = title[branch + 4]
                child_read = 0x2ACB00 + branch + 5
                self.assertEqual(0x180000000 + child_read + displacement, 0x1802ACBAA)
                self.assertEqual(library.get_data(child_read, 7), bytes.fromhex("488b0e488b81e8"))
                self.assertEqual(library.get_data(0x2AB84A, 7), bytes.fromhex("488b89d8010000"))
                self.assertEqual(library.get_data(0x2AB86A, 5), bytes.fromhex("ba29020000"))

                def relative_call(rva):
                    raw = library.get_data(rva, 5)
                    self.assertEqual(raw[0], 0xE8)
                    return rva + 5 + struct.unpack_from("<i", raw, 1)[0]

                self.assertEqual(relative_call(0x27C069), 0x292A70)
                self.assertEqual(library.get_data(0x27C073, 18),
                                 bytes.fromhex("48399870010000750e33d2488bc8448d4201"))
                self.assertEqual(relative_call(0x27C085), 0x2A3790)
                self.assertEqual(sorted(relative_call(site) for site in (0x27F24F, 0x27F25F, 0x27F26B)),
                                 [0x27F2A0, 0x292C40, 0x2AEA70])
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_production_document_overrides_the_ole_active_view_slot(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        library_bytes = (ROOT / "v3d_files_" / "mfc140.dll").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        self.assertEqual(hashlib.sha256(library_bytes).hexdigest(),
                         "0cf26008fae0cb61dfe49e1c3fc17e0dd860be011d9a6a64b452f56335bafbfe")
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image, pefile.PE(
                    data=library_bytes, fast_load=True) as library:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                library.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]])
                export = library.DIRECTORY_ENTRY_EXPORT.struct

                def ordinal_rva(ordinal):
                    return struct.unpack(
                        "<I", library.get_data(
                            export.AddressOfFunctions + (ordinal - export.Base) * 4, 4))[0]

                def rip_target(rva):
                    raw = image.get_data(rva, 7)
                    self.assertEqual(raw[:3], bytes.fromhex("488d05"))
                    return rva + 7 + struct.unpack_from("<i", raw, 3)[0]

                self.assertEqual(rip_target(0x6892A0), 0xEA3830)
                runtime = image.get_data(0xEA3830, 0x18)
                name = struct.unpack_from("<Q", runtime, 0)[0]
                self.assertEqual(image.get_data(name - 0x140000000, 15), b"CProductionDoc\x00")
                self.assertEqual(struct.unpack_from("<I", runtime, 8)[0], 0x61F8)
                self.assertEqual(struct.unpack_from("<H", runtime, 12)[0], 0xFFFF)
                self.assertEqual(struct.unpack_from("<Q", runtime, 0x10)[0], 0x140684F40)
                self.assertEqual(image.get_data(0x684F4D, 5), bytes.fromhex("b9f8610000"))
                self.assertEqual(rip_target(0x60B5B0), 0xE7DD60)
                self.assertEqual(image.get_data(0x4D349E, 5), bytes.fromhex("e80d811300"))
                self.assertEqual(0x1404D34A3 + struct.unpack("<i", bytes.fromhex("0d811300"))[0],
                                 0x14060B5B0)
                self.assertEqual(image.get_data(0x4D34AE, 5), bytes.fromhex("bac8070000"))
                self.assertEqual(image.get_data(0x4D356B, 5), bytes.fromhex("baca070000"))
                self.assertEqual(image.get_data(0x4D35C8, 5), bytes.fromhex("bacb070000"))
                self.assertEqual(image.get_data(0x4D3615, 5), bytes.fromhex("e8865c1b00"))
                self.assertEqual(0x1404D361A + struct.unpack("<i", bytes.fromhex("865c1b00"))[0],
                                 0x1406892A0)
                self.assertEqual(image.get_data(0x4D3625, 5), bytes.fromhex("bad10b0000"))

                vtable = 0xEA3868
                self.assertEqual(struct.unpack("<Q", image.get_data(vtable - 8, 8))[0], 0x140F12E78)
                slot = struct.unpack("<Q", image.get_data(vtable + 0x320, 8))[0]
                self.assertEqual(slot, 0x1406970B0)
                self.assertEqual(image.get_data(0x6970C6, 7), bytes.fromhex("4881c1983c0000"))
                imports = {item.address: item.ordinal for entry in image.DIRECTORY_ENTRY_IMPORT
                           for item in entry.imports}
                self.assertEqual(image.get_data(0x6970CD, 6), bytes.fromhex("ff151d806c00"))
                self.assertEqual(imports[0x1406970D3 + 0x6C801D], 1504)
                self.assertEqual(ordinal_rva(1504), 0xDFC0)
                self.assertEqual(image.get_data(0x6970DC, 7), bytes.fromhex("48ff2515806c00"))
                self.assertEqual(imports[0x1406970E3 + 0x6C8015], 1032)
                self.assertEqual(ordinal_rva(1032), 0x2FB0)
                ole = struct.unpack("<Q", image.get_data(0xE7DD98 + 0x320, 8))[0]
                self.assertEqual(ole, 0x140780156)
                thunk = image.get_data(0x780156, 6)
                self.assertEqual(thunk[:2], bytes.fromhex("ff25"))
                displacement = struct.unpack_from("<i", thunk, 2)[0]
                self.assertEqual(imports[0x14078015C + displacement], 3793)
                self.assertEqual(ordinal_rva(3793), 0x26BDC0)
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_production_print_preview_keeps_active_view_on_the_child_frame(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        library_bytes = (ROOT / "v3d_files_" / "mfc140.dll").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        self.assertEqual(hashlib.sha256(library_bytes).hexdigest(),
                         "0cf26008fae0cb61dfe49e1c3fc17e0dd860be011d9a6a64b452f56335bafbfe")
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image, pefile.PE(
                    data=library_bytes, fast_load=True) as library:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                library.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]])
                imports = {item.address: item.ordinal for entry in image.DIRECTORY_ENTRY_IMPORT
                           for item in entry.imports}
                export = library.DIRECTORY_ENTRY_EXPORT.struct

                def ordinal_rva(ordinal):
                    return struct.unpack(
                        "<I", library.get_data(
                            export.AddressOfFunctions + (ordinal - export.Base) * 4, 4))[0]

                view_slot = struct.unpack("<Q", image.get_data(0xEAC650 + 0x370, 8))[0]
                self.assertEqual(view_slot, 0x14077FB50)
                thunk = image.get_data(view_slot - 0x140000000, 6)
                self.assertEqual(thunk[:2], bytes.fromhex("ff25"))
                displacement = struct.unpack_from("<i", thunk, 2)[0]
                self.assertEqual(imports[view_slot + 6 + displacement], 9697)
                self.assertEqual(ordinal_rva(9697), 0x27C720)

                child_base = struct.unpack("<Q", image.get_data(0xEA16E8 + 0x18, 8))[0]
                self.assertEqual(child_base, 0x1407551C0)
                jump = image.get_data(child_base - 0x140000000, 5)
                self.assertEqual(jump[0], 0xE9)
                child_base_thunk = child_base + 5 + struct.unpack_from("<i", jump, 1)[0]
                self.assertEqual(child_base_thunk, 0x14077FD06)
                thunk = image.get_data(child_base_thunk - 0x140000000, 6)
                displacement = struct.unpack_from("<i", thunk, 2)[0]
                self.assertEqual(imports[child_base_thunk + 6 + displacement], 6890)
                self.assertEqual(ordinal_rva(6890), 0x85620)
                self.assertEqual(library.get_data(0x85620, 7),
                                 bytes.fromhex("488d05b9c42b00"))
                mdi_child_class = 0x85627 + struct.unpack(
                    "<i", bytes.fromhex("b9c42b00"))[0]
                mdi_child_name = struct.unpack(
                    "<Q", library.get_data(mdi_child_class, 8))[0]
                self.assertEqual(
                    library.get_data(mdi_child_name - 0x180000000, 13),
                    b"CMDIChildWnd\x00")
                mdi_base = struct.unpack(
                    "<Q", library.get_data(mdi_child_class + 0x18, 8))[0]
                self.assertEqual(mdi_base, 0x1800685F0)
                self.assertEqual(library.get_data(0x685F0, 7),
                                 bytes.fromhex("488d0559832d00"))
                frame_class = 0x685F7 + struct.unpack(
                    "<i", bytes.fromhex("59832d00"))[0]
                frame_name = struct.unpack("<Q", library.get_data(frame_class, 8))[0]
                self.assertEqual(
                    library.get_data(frame_name - 0x180000000, 10),
                    b"CFrameWnd\x00")

                self.assertEqual(library.get_data(0x27C753, 0x24), bytes.fromhex(
                    "488bcfe815630100488bd0488d0deb410c00488bd8"
                    "e843c4fbff4885c07525e869baebff"))
                self.assertEqual(0x18027C75B + struct.unpack(
                    "<i", bytes.fromhex("15630100"))[0], 0x180292A70)
                tested_class = 0x18027C765 + struct.unpack(
                    "<i", bytes.fromhex("eb410c00"))[0]
                self.assertEqual(tested_class, 0x180340950)
                self.assertEqual(tested_class - 0x180000000, frame_class)
                self.assertEqual(library.get_data(0x27C797, 0x35), bytes.fromhex(
                    "488b0333d24c8b8670010000488bcb488b8038030000"
                    "ff153d240500488b967001000041b801000000488bcb"
                    "488b5218e8c46f0200"))
                self.assertEqual(0x18027C7CC + struct.unpack(
                    "<i", bytes.fromhex("c46f0200"))[0], 0x1802A3790)
                self.assertEqual(library.get_data(0x27C7CC, 0x10),
                                 bytes.fromhex("488bcfe89c620100483bd8741e488b07"))
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_document_close_destroys_listed_views_before_skip_release(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        library_bytes = (ROOT / "v3d_files_" / "mfc140.dll").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        self.assertEqual(hashlib.sha256(library_bytes).hexdigest(),
                         "0cf26008fae0cb61dfe49e1c3fc17e0dd860be011d9a6a64b452f56335bafbfe")
        decoder = Cs(CS_ARCH_X86, CS_MODE_64)
        decoder.detail = True
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image, pefile.PE(
                    data=library_bytes, fast_load=True) as library:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
                library.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]])
                imports = {
                    item.address: (entry.dll, item.name.decode() if item.name else None, item.ordinal)
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                self.assertEqual(imports[0x140D5BC00], (b"USER32.dll", "PostMessageA", None))
                export = library.DIRECTORY_ENTRY_EXPORT.struct

                def ordinal_rva(ordinal):
                    return struct.unpack("<I", library.get_data(
                        export.AddressOfFunctions + (ordinal - export.Base) * 4, 4))[0]

                def exe_thunk(address):
                    raw = image.get_data(address - IMAGE_BASE, 6)
                    self.assertEqual(raw[:2], b"\xff\x25")
                    return imports[address + 6 + struct.unpack_from("<i", raw, 2)[0]]

                def instructions(binary, start, size):
                    return list(decoder.disasm(binary.get_data(start - IMAGE_BASE, size), start))

                def r14_or_r15_destination(instruction):
                    return instruction.op_str.split(",")[0].strip()

                text = next(section for section in image.sections if section.Name.startswith(b".text"))
                text_data = text.get_data()
                text_base = IMAGE_BASE + text.VirtualAddress
                writes = []
                cursor = 0
                while True:
                    found = text_data.find(b"\x38\x58\x00\x00", cursor)
                    if found < 0:
                        break
                    cursor = found + 1
                    site = text_base + found
                    matches = []
                    for back in range(15):
                        start = site - back
                        decoded = list(decoder.disasm(image.get_data(start - IMAGE_BASE, back + 8), start))
                        if not decoded or decoded[0].address != start:
                            continue
                        instruction = decoded[0]
                        if not instruction.address <= site < instruction.address + instruction.size:
                            continue
                        for operand in instruction.operands:
                            if (operand.type == X86_OP_MEM and operand.mem.disp == 0x5838
                                    and operand.access & CS_AC_WRITE):
                                matches.append(instruction.address)
                    if matches:
                        writes.append(min(matches))
                self.assertEqual(sorted(set(writes)), [0x14067F60E, 0x1406AF86F])

                constructor = next(item.struct for item in image.DIRECTORY_ENTRY_EXCEPTION
                                   if item.struct.BeginAddress == 0x67DEA0)
                body = instructions(image, IMAGE_BASE + constructor.BeginAddress,
                                    constructor.EndAddress - constructor.BeginAddress)
                clear, store = 0x14067DF59, 0x14067F60E
                destinations = []
                for instruction in body:
                    if instruction.mnemonic.startswith("j"):
                        target = int(instruction.op_str, 16)
                        if clear < target <= store:
                            self.assertTrue(clear < instruction.address <= store)
                        if clear <= instruction.address < store:
                            self.assertLessEqual(target, store)
                    if clear <= instruction.address < store and r14_or_r15_destination(
                            instruction) in {"r14", "r14d", "r14w", "r14b"}:
                        destinations.append(instruction.address)
                self.assertEqual(destinations, [clear])
                self.assertEqual(image.get_data(clear - IMAGE_BASE, 3), bytes.fromhex("4533f6"))
                self.assertEqual(image.get_data(store - IMAGE_BASE, 7), bytes.fromhex("4c89b638580000"))

                initial = next(item.struct for item in image.DIRECTORY_ENTRY_EXCEPTION
                               if item.struct.BeginAddress == 0x6AF770)
                published = instructions(image, IMAGE_BASE + initial.BeginAddress,
                                         initial.EndAddress - initial.BeginAddress)
                view_copy, view_store = 0x1406AF794, 0x1406AF86F
                view_destinations = []
                for instruction in published:
                    if instruction.mnemonic.startswith("j"):
                        target = int(instruction.op_str, 16)
                        if view_copy < target <= view_store:
                            self.assertTrue(view_copy < instruction.address <= view_store)
                        if view_copy <= instruction.address < view_store:
                            self.assertLessEqual(target, view_store)
                    if view_copy <= instruction.address < view_store and r14_or_r15_destination(
                            instruction) in {"r15", "r15d"}:
                        view_destinations.append((instruction.address, instruction.op_str))
                self.assertEqual(view_destinations, [(view_copy, "r15, rcx")])
                self.assertEqual(struct.unpack("<Q", image.get_data(0xEAC978, 8))[0], 0x1406AF770)
                self.assertEqual(image.get_data(0x6AF868, 14), bytes.fromhex(
                    "4d8bafe80000004d89bd38580000"))

                posts = {
                    0x1406A1024: ("488b88385800004533c94533c08b15094caf00488b4940ff15bfab6b00",
                                  0x141195C40, b"\x41\xbd\x03\x00\x00\x00"),
                    0x1406A105E: ("488b88385800004533c94533c08b15cf4baf00488b4940ff1585ab6b00",
                                  0x141195C40, b"\x90"),
                    0x140736FD4: ("488b88385800004533c94533c08b15495baa00488b4940ff150f4c6200",
                                  0x1411DCB30, b"\xe9\x37\x04\x00\x00"),
                }
                for address, (encoded, message, following) in posts.items():
                    raw = bytes.fromhex(encoded)
                    self.assertEqual(image.get_data(address - IMAGE_BASE, len(raw)), raw)
                    self.assertEqual(image.get_data(address + len(raw) - IMAGE_BASE, len(following)), following)
                    self.assertEqual(address + 19 + struct.unpack_from("<i", raw, 15)[0], message)
                    self.assertEqual(address + len(raw) + struct.unpack_from("<i", raw, len(raw) - 4)[0],
                                     0x140D5BC00)

                callers = {0x1406ADAF0: [], 0x1406B0700: []}
                for index in range(len(text_data) - 5):
                    if text_data[index] != 0xE8:
                        continue
                    destination = text_base + index + 5 + struct.unpack_from("<i", text_data, index + 1)[0]
                    if destination in callers:
                        callers[destination].append(text_base + index)
                self.assertEqual(callers[0x1406ADAF0], [0x1406B0704, 0x1406B3B3F])
                self.assertEqual(callers[0x1406B0700], [])
                self.assertEqual(image.get_data(0x6B0700, 9), bytes.fromhex("4883ec28e8e7d3ffff"))
                self.assertEqual(0x1406B0709 + struct.unpack("<i", bytes.fromhex("e7d3ffff"))[0], 0x1406ADAF0)
                self.assertEqual(image.get_data(0x6B3B3C, 8), bytes.fromhex("488bcee8ac9fffff"))
                self.assertEqual(0x1406B3B44 + struct.unpack("<i", bytes.fromhex("ac9fffff"))[0], 0x1406ADAF0)

                self.assertEqual(struct.unpack("<Q", image.get_data(0xEA3868 + 0x118, 8))[0], 0x14068D9D0)
                self.assertEqual(struct.unpack("<Q", image.get_data(0xEA3868 + 8, 8))[0], 0x1406807E0)
                self.assertEqual(image.get_data(0x68DA31, 5), bytes.fromhex("e9f0230f00"))
                self.assertEqual(0x14068DA36 + struct.unpack("<i", bytes.fromhex("f0230f00"))[0], 0x14077FE26)
                self.assertEqual(exe_thunk(0x14077FE26)[2], 8850)
                self.assertEqual(ordinal_rva(8850), 0x21F890)
                self.assertEqual(struct.unpack("<Q", image.get_data(0xEA1720 + 0xD0, 8))[0], 0x14077FD30)
                self.assertEqual(exe_thunk(0x14077FD30), (b"mfc140.dll", None, 3803))
                self.assertEqual(image.get_data(0x6807EF, 5), bytes.fromhex("e82cf4ffff"))
                self.assertEqual(0x1406807F4 + struct.unpack("<i", bytes.fromhex("2cf4ffff"))[0], 0x14067FC20)
                self.assertEqual(image.get_data(0x680028, 5), bytes.fromhex("e9c3fbe9ff"))
                self.assertEqual(0x14068002D + struct.unpack("<i", bytes.fromhex("c3fbe9ff"))[0], 0x14051FBF0)
                self.assertEqual(image.get_data(0x51FCC8, 12), bytes.fromhex("488d8f48240000e8bc020000"))
                self.assertEqual(0x14051FCD4 + struct.unpack("<i", bytes.fromhex("bc020000"))[0], 0x14051FF90)
                self.assertEqual(image.get_data(0x51FD33, 12), bytes.fromhex("488d8fe0230000e899002600"))
                self.assertEqual(0x14051FD3F + struct.unpack("<i", bytes.fromhex("99002600"))[0], 0x14077FDD8)
                self.assertEqual(exe_thunk(0x14077FDD8), (b"mfc140.dll", None, 1439))

                self.assertEqual(library.get_data(0x21F890, 6), bytes.fromhex("48895c240848"))
                loop = bytes.fromhex(
                    "48837970007449488b4360488b4810e885310700488bf84885c00f848f000000"
                    "488b0b488bd7488b81c8010000488bcbff15e3f20a00488b0f488b81d0000000"
                    "488bcfff15d0f20a00")
                self.assertEqual(library.get_data(0x21F8D7, len(loop)), loop)
                self.assertEqual(0x18021F8DE + loop[6], 0x18021F927)
                self.assertLess(0x18021F927, 0x18021F958)
                self.assertEqual(0x18021F8EB + struct.unpack("<i", bytes.fromhex("85310700"))[0], 0x180292A70)
                self.assertEqual(0x18021F920 + struct.unpack("<i", bytes.fromhex("d0f20a00"))[0], 0x1802CEBF0)
                delete = bytes.fromhex("83bb20010000007415488b03ba01000000488bcb488b4008ff157af20a00")
                self.assertEqual(library.get_data(0x21F958, len(delete)), delete)
                self.assertEqual(0x18021F976 + struct.unpack("<i", bytes.fromhex("7af20a00"))[0], 0x1802CEBF0)
                self.assertEqual(struct.unpack("<Q", library.get_data(0x2CEBF0, 8))[0], 0x1802BF060)
                self.assertEqual(library.get_data(0x2BF060, 2), b"\xff\xe0")
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_null_hwnd_skip_post_misses_the_view_message_map(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        library_bytes = (ROOT / "v3d_files_" / "mfc140.dll").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        self.assertEqual(hashlib.sha256(library_bytes).hexdigest(),
                         "0cf26008fae0cb61dfe49e1c3fc17e0dd860be011d9a6a64b452f56335bafbfe")
        handler = struct.pack("<Q", 0x1406B0700)
        identifier = struct.pack("<Q", 0x1411982C8)
        self.assertEqual(source.count(handler), 1)
        self.assertEqual(source.count(identifier), 1)
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image, pefile.PE(
                    data=library_bytes, fast_load=True) as library:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                library.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]])
                imports = {
                    item.address: (entry.dll, item.name.decode() if item.name else None, item.ordinal)
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                library_imports = {
                    item.address: item.name.decode() if item.name else None
                    for entry in library.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                self.assertEqual(
                    struct.unpack("<IIIIQQ", image.get_data(0xEACD20, 32)),
                    (0xC000, 0, 0, 0, 0x1411982C8, 0x1406B0700))
                self.assertEqual(struct.unpack("<Q", image.get_data(0xE39770 + 0x60, 8))[0],
                                 0x1404D25D0)
                self.assertEqual(image.get_data(0x4D25D0, 5), bytes.fromhex("e93b020000"))
                self.assertEqual(0x1404D25D5 + struct.unpack("<i", bytes.fromhex("3b020000"))[0],
                                 0x1404D2810)
                self.assertEqual(image.get_data(0x4D2810, 8), bytes.fromhex("488d0519799600c3"))
                message_map = 0x1404D2817 + struct.unpack("<i", bytes.fromhex("19799600"))[0]
                self.assertEqual(message_map, 0x140E3A130)
                base_getter, entries = struct.unpack("<QQ", image.get_data(message_map - IMAGE_BASE, 16))
                self.assertEqual(base_getter, 0x14077FAA2)
                raw = image.get_data(base_getter - IMAGE_BASE, 6)
                self.assertEqual(raw[:2], b"\xff\x25")
                self.assertEqual(
                    imports[base_getter + 6 + struct.unpack_from("<i", raw, 2)[0]],
                    (b"mfc140.dll", None, 7363))
                seen = []
                cursor = entries
                while True:
                    record = struct.unpack("<IIIIQQ", image.get_data(cursor - IMAGE_BASE, 32))
                    if record == (0, 0, 0, 0, 0, 0):
                        break
                    seen.append(record[0])
                    cursor += 32
                    self.assertLess(len(seen), 80)
                self.assertEqual(len(seen), 55)
                self.assertNotIn(0xC000, seen)

                export = library.DIRECTORY_ENTRY_EXPORT.struct
                pretranslate = struct.unpack("<I", library.get_data(
                    export.AddressOfFunctions + (11849 - export.Base) * 4, 4))[0]
                self.assertEqual(pretranslate, 0x278FE0)
                self.assertEqual(library.get_data(0x278FE0, 8), bytes.fromhex("488bcae958f4ffff"))
                self.assertEqual(0x180278FE8 + struct.unpack("<i", bytes.fromhex("58f4ffff"))[0],
                                 0x180278440)
                self.assertEqual(library.get_data(0x27845B, 14), bytes.fromhex(
                    "48833f00750c488bd7e8970a0000"))
                self.assertEqual(0x180278469 + struct.unpack("<i", bytes.fromhex("970a0000"))[0],
                                 0x180278F00)
                self.assertEqual(library.get_data(0x278F0A, 13), bytes.fromhex(
                    "488b01488bda488bf9488b4060"))
                self.assertEqual(library.get_data(0x278F30, 6), bytes.fromhex("81f900c00000"))
                self.assertEqual(library.get_data(0x278FA7, 6), bytes.fromhex("498b41103908"))
                self.assertEqual(library.get_data(0x29387F, 14), bytes.fromhex(
                    "488b1a488bfa4885db488bf17444"))
                self.assertEqual(0x18029388D + 0x44, 0x1802938D1)
                self.assertEqual(library.get_data(0x2938D1, 2), b"\x33\xc0")
                self.assertEqual(library.get_data(0x290413, 2), b"\x33\xc0")
                self.assertEqual(library.get_data(0x2ABC3A, 13), bytes.fromhex(
                    "8b47082d0001000083f8097740"))
                self.assertEqual(0x1802ABC47 + 0x40, 0x1802ABC87)
                self.assertEqual(library.get_data(0x2ABC87, 2), b"\x33\xc0")
                self.assertEqual(library.get_data(0x278354, 17), bytes.fromhex(
                    "488bcbe8a401000085c07512488bcbff15"))
                self.assertEqual(0x18027835C + struct.unpack("<i", bytes.fromhex("a4010000"))[0],
                                 0x180278500)

                def library_import(address):
                    raw_call = library.get_data(address - 0x180000000, 6)
                    self.assertEqual(raw_call[:2], b"\xff\x15")
                    return library_imports[address + 6 + struct.unpack_from("<i", raw_call, 2)[0]]

                self.assertEqual(library_import(0x180278341), "GetMessageA")
                self.assertEqual(library_import(0x180278363), "TranslateMessage")
                self.assertEqual(library_import(0x18027836C), "DispatchMessageA")
                self.assertEqual(library.get_data(0x2A14D7, 3), bytes.fromhex("4533f6"))
                self.assertEqual(library.get_data(0x2A157A, 7), bytes.fromhex("4c89b720010000"))
                self.assertEqual(image.get_data(0x630093, 7), bytes.fromhex("488d8fd00c0000"))
                menu_call = image.get_data(0x63009A, 6)
                self.assertEqual(menu_call[:2], b"\xff\x15")
                self.assertEqual(
                    imports[0x1406300A0 + struct.unpack_from("<i", menu_call, 2)[0]][:2],
                    (b"ProfUISm.dll", "??0CExtMenuControlBar@@QEAA@XZ"))
                self.assertEqual(image.get_data(0x63A4E6, 24), bytes.fromhex(
                    "84c0752e488d8fd00c0000488bd34c8b0141ff90900a0000"))
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

        if platform.system() != "Windows":
            return
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        result_type = ctypes.c_ssize_t
        window_proc = ctypes.WINFUNCTYPE(
            result_type, ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_ssize_t)

        class WindowClass(ctypes.Structure):
            _fields_ = [
                ("style", ctypes.c_uint), ("lpfnWndProc", window_proc),
                ("cbClsExtra", ctypes.c_int), ("cbWndExtra", ctypes.c_int),
                ("hInstance", ctypes.c_void_p), ("hIcon", ctypes.c_void_p),
                ("hCursor", ctypes.c_void_p), ("hbrBackground", ctypes.c_void_p),
                ("lpszMenuName", ctypes.c_char_p), ("lpszClassName", ctypes.c_char_p),
            ]

        class Point(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

        class Message(ctypes.Structure):
            _fields_ = [
                ("hwnd", ctypes.c_void_p), ("message", ctypes.c_uint),
                ("wParam", ctypes.c_size_t), ("lParam", ctypes.c_ssize_t),
                ("time", ctypes.c_uint), ("pt", Point), ("lPrivate", ctypes.c_uint),
            ]

        delivered = []

        def receive(hwnd, message, wparam, lparam):
            if message == registered:
                delivered.append(hwnd)
            return user32.DefWindowProcA(hwnd, message, wparam, lparam)

        user32.DefWindowProcA.argtypes = [
            ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_ssize_t]
        user32.DefWindowProcA.restype = result_type
        user32.RegisterClassA.argtypes = [ctypes.c_void_p]
        user32.RegisterClassA.restype = ctypes.c_ushort
        user32.RegisterWindowMessageA.argtypes = [ctypes.c_char_p]
        user32.RegisterWindowMessageA.restype = ctypes.c_uint
        user32.CreateWindowExA.argtypes = [
            ctypes.c_uint, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint,
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
        user32.CreateWindowExA.restype = ctypes.c_void_p
        user32.PostMessageA.argtypes = [
            ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_ssize_t]
        user32.PostMessageA.restype = ctypes.c_int
        user32.PeekMessageA.argtypes = [
            ctypes.POINTER(Message), ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint]
        user32.PeekMessageA.restype = ctypes.c_int
        user32.DispatchMessageA.argtypes = [ctypes.POINTER(Message)]
        user32.DispatchMessageA.restype = result_type
        user32.DestroyWindow.argtypes = [ctypes.c_void_p]
        user32.DestroyWindow.restype = ctypes.c_int
        user32.UnregisterClassA.argtypes = [ctypes.c_char_p, ctypes.c_void_p]
        user32.UnregisterClassA.restype = ctypes.c_int
        receiver = window_proc(receive)
        class_name = b"V3DSkipNullHwnd"
        instance = kernel32.GetModuleHandleA(None)
        registered = user32.RegisterWindowMessageA(
            b"{FEA8416F-2D59-478F-BEFF-5D96AFD6A551}")
        self.assertGreaterEqual(registered, 0xC000)
        descriptor = WindowClass(
            0, receiver, 0, 0, instance, None, None, None, None, class_name)
        window = None
        try:
            if not user32.RegisterClassA(ctypes.byref(descriptor)):
                raise ctypes.WinError(ctypes.get_last_error())
            window = user32.CreateWindowExA(
                0, class_name, b"", 0, 0, 0, 0, 0, None, None, instance, None)
            self.assertTrue(window)
            self.assertTrue(user32.PostMessageA(window, registered, 0, 0))
            posted = Message()
            self.assertTrue(user32.PeekMessageA(
                ctypes.byref(posted), window, registered, registered, 1))
            user32.DispatchMessageA(ctypes.byref(posted))
            self.assertEqual(delivered, [window])
            delivered.clear()
            self.assertTrue(user32.PostMessageA(None, registered, 0, 0))
            self.assertFalse(user32.PeekMessageA(
                ctypes.byref(posted), window, registered, registered, 1))
            self.assertTrue(user32.PeekMessageA(
                ctypes.byref(posted), None, registered, registered, 1))
            self.assertFalse(posted.hwnd)
            self.assertEqual(posted.message, registered)
            user32.DispatchMessageA(ctypes.byref(posted))
            self.assertEqual(delivered, [])
        finally:
            pending = Message()
            while user32.PeekMessageA(ctypes.byref(pending), None, registered, registered, 1):
                pass
            if window:
                user32.DestroyWindow(window)
            user32.UnregisterClassA(class_name, instance)

    def test_registered_skip_message_is_not_consumed_by_menu_bar_pretranslate(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        library_bytes = (ROOT / "v3d_files_" / "mfc140.dll").read_bytes()
        menu_bytes = (ROOT / "v3d_files_" / "ProfUISm.dll").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        self.assertEqual(hashlib.sha256(library_bytes).hexdigest(),
                         "0cf26008fae0cb61dfe49e1c3fc17e0dd860be011d9a6a64b452f56335bafbfe")
        self.assertEqual(hashlib.sha256(menu_bytes).hexdigest(),
                         "7292f99502237dcf88092112ba5ad692e5fe9afa64e4f6ea9a22ced5c0d5036a")
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image, pefile.PE(
                    data=library_bytes, fast_load=True) as library, pefile.PE(
                    data=menu_bytes, fast_load=True) as menu:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
                library.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
                menu.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
                self.assertEqual(menu.FILE_HEADER.Machine, 0x8664)
                self.assertEqual(menu.OPTIONAL_HEADER.ImageBase, 0x180000000)
                imports = {
                    item.address: (entry.dll, item.name.decode() if item.name else None, item.ordinal)
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                menu_imports = {
                    item.address: item.name.decode() if item.name else None
                    for entry in menu.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                constructor = next(symbol for symbol in menu.DIRECTORY_ENTRY_EXPORT.symbols
                                   if symbol.ordinal == 708)
                self.assertEqual(constructor.name, b"??0CExtMenuControlBar@@QEAA@XZ")
                self.assertEqual(constructor.address, 0x26C600)
                self.assertEqual(menu.get_data(0x26C630, 10), bytes.fromhex("488d0571512d00488907"))
                vtable = 0x18026C637 + struct.unpack("<i", bytes.fromhex("71512d00"))[0]
                self.assertEqual(vtable, 0x1805417A8)
                self.assertEqual(struct.unpack("<Q", menu.get_data(0x542238, 8))[0], 0x180270AE0)
                handler = next(item.struct for item in menu.DIRECTORY_ENTRY_EXCEPTION
                               if item.struct.BeginAddress == 0x270AE0)
                self.assertEqual(handler.EndAddress, 0x271EE3)

                def menu_bytes_at(rva, text):
                    raw = bytes.fromhex(text)
                    self.assertEqual(menu.get_data(rva, len(raw)), raw)

                menu_bytes_at(0x270B2C, "4885db0f84ef120000")
                menu_bytes_at(0x270B35, "48837b40000f84e4120000")
                menu_bytes_at(0x270B40, "817e0813010000752e")
                menu_bytes_at(0x270B6C, "41be01000000e9b3120000")
                menu_bytes_at(0x270B77, "837e0813751e")
                menu_bytes_at(0x270B93, "4533ffe992120000")
                menu_bytes_at(0x270BD1, "8d41fa83f8020f8634120000")
                menu_bytes_at(0x270C04, "8b46082d0001000083f8097721")
                menu_bytes_at(0x270C27, "41be01000000e9fe110000")
                menu_bytes_at(0x270C56, "8b560881fa11010000751f")
                menu_bytes_at(0x270C80, "8d82defdffff83f8067711")
                menu_bytes_at(0x270DA4, "4533ff")
                menu_bytes_at(0x270DD5, "8d8700ffffffa9faffffff751c")
                menu_bytes_at(0x270DFE, "81ff010100000f85b90f0000")
                menu_bytes_at(0x271DC3, "83ff7b7517")
                menu_bytes_at(0x271DED, "8d8700feffff83f8097735")
                menu_bytes_at(0x271E1F, "4533ffeb09")
                menu_bytes_at(0x271E24, "4533ff458bf7458bfe458bf7")
                menu_bytes_at(0x271E39, "418bc6")
                decoder = Cs(CS_ARCH_X86, CS_MODE_64)
                instructions = list(decoder.disasm(
                    menu.get_data(0x270AE0, handler.EndAddress - 0x270AE0), 0x180270AE0))
                by_address = {insn.address: insn for insn in instructions}

                def target(address):
                    self.assertTrue(by_address[address].op_str.startswith("0x"))
                    return int(by_address[address].op_str, 16)

                self.assertEqual(target(0x180270B2F), 0x180271E24)
                self.assertEqual(target(0x180270B3A), 0x180271E24)
                self.assertEqual(target(0x180270B47), 0x180270B77)
                self.assertEqual(target(0x180270B72), 0x180271E2A)
                self.assertEqual(target(0x180270B7B), 0x180270B9B)
                self.assertEqual(target(0x180270B96), 0x180271E2D)
                self.assertEqual(target(0x180270BD7), 0x180271E11)
                self.assertEqual(target(0x180270C0F), 0x180270C32)
                self.assertEqual(target(0x180270C2D), 0x180271E30)
                self.assertEqual(target(0x180270C5F), 0x180270C80)
                self.assertEqual(target(0x180270C89), 0x180270C9C)
                self.assertEqual(target(0x180270DE0), 0x180270DFE)
                self.assertEqual(target(0x180270E04), 0x180271DC3)
                self.assertEqual(target(0x180271DC6), 0x180271DDF)
                self.assertEqual(target(0x180271DF6), 0x180271E2D)
                self.assertEqual(by_address[0x180271E2D].bytes, bytes.fromhex("458bf7"))
                self.assertEqual(
                    [insn.address for insn in instructions if insn.bytes == bytes.fromhex("41be01000000")],
                    [0x180270B6C, 0x180270C27, 0x180270CA3])
                nonzero_return = {
                    0x180270C27, 0x1802714DC, 0x1802716AF, 0x1802716B2, 0x180271E27,
                    0x180271E2A, 0x180271E30}
                sources = []
                entries = []
                span = (0x180270E0A, 0x180271DC3)
                for insn in instructions:
                    if not insn.mnemonic.startswith("j") or not insn.op_str.startswith("0x"):
                        continue
                    destination = int(insn.op_str, 16)
                    if destination in nonzero_return:
                        sources.append(insn.address)
                    if span[0] <= destination < span[1] and not span[0] <= insn.address < span[1]:
                        entries.append(insn.address)
                self.assertEqual(entries, [0x180270DE8, 0x180270DF5, 0x180270DFC])
                self.assertIn(0x180270B72, sources)
                self.assertIn(0x180270C2D, sources)
                outside = [
                    address for address in sources
                    if address not in {0x180270B72, 0x180270C2D, 0x180270C8E, 0x180270C9A}
                    and not span[0] <= address < span[1]
                    and not 0x180271DC8 <= address < 0x180271DDF]
                self.assertEqual(outside, [])

                def writes_r15(insn):
                    return insn.mnemonic not in {"cmp", "test", "push", "pop"} and insn.op_str.startswith("r15")

                self.assertEqual(
                    [insn.address for insn in instructions
                     if 0x180270DA4 < insn.address < 0x180271E2D and writes_r15(insn)],
                    [0x1802714DC, 0x1802714E2, 0x1802716AF, 0x1802716B5,
                     0x180271E1F, 0x180271E24, 0x180271E2A])
                self.assertEqual(by_address[0x180271E1F].bytes, bytes.fromhex("4533ff"))
                self.assertEqual(by_address[0x180271E24].bytes, bytes.fromhex("4533ff"))
                sends = []
                for insn in instructions:
                    if insn.bytes[:2] != b"\xff\x15":
                        continue
                    slot = insn.address + 6 + struct.unpack_from("<i", insn.bytes, 2)[0]
                    if menu_imports.get(slot) == "SendMessageA":
                        sends.append(insn.address)
                self.assertEqual(sends, [
                    0x180270D2E, 0x180270D88, 0x1802713BA, 0x180271671,
                    0x1802719A5, 0x180271A65, 0x180271CD4])
                edx_constants = (bytes.fromhex("ba57010000"), bytes.fromhex("418d511f"))
                self.assertTrue(all(
                    bytes(instructions[instructions.index(by_address[site]) - 2].bytes) in edx_constants
                    for site in sends))
                cleanup = next(item.struct for item in menu.DIRECTORY_ENTRY_EXCEPTION
                               if item.struct.BeginAddress <= 0x47ECE0 < item.struct.EndAddress)
                self.assertEqual(cleanup.BeginAddress, 0x47ECE0)
                self.assertFalse(any(
                    "r14" in insn.op_str for insn in decoder.disasm(
                        menu.get_data(cleanup.BeginAddress, cleanup.EndAddress - cleanup.BeginAddress),
                        0x180000000 + cleanup.BeginAddress)))
                self.assertEqual(image.get_data(0x63A4E6, 24), bytes.fromhex(
                    "84c0752e488d8fd00c0000488bd34c8b0141ff90900a0000"))
                self.assertEqual(0x14063A4EA + 0x2E, 0x14063A518)
                self.assertEqual(image.get_data(0x63A4FE, 5), bytes.fromhex("83f8017515"))
                self.assertEqual(0x14063A503 + 0x15, 0x14063A518)
                self.assertEqual(image.get_data(0x63A518, 15), bytes.fromhex(
                    "8b43082d00010000a9fbffffff7506"))
                self.assertEqual(0x14063A527 + 6, 0x14063A52D)
                self.assertEqual(image.get_data(0x63A542, 5), bytes.fromhex("e9e95d1400"))
                self.assertEqual(0x14063A547 + struct.unpack("<i", bytes.fromhex("e95d1400"))[0],
                                 0x140780330)
                thunk = image.get_data(0x780330, 6)
                self.assertEqual(thunk[:2], b"\xff\x25")
                self.assertEqual(
                    imports[0x140780336 + struct.unpack_from("<i", thunk, 2)[0]],
                    (b"mfc140.dll", None, 11812))
                export = library.DIRECTORY_ENTRY_EXPORT.struct
                pretranslate = struct.unpack("<I", library.get_data(
                    export.AddressOfFunctions + (11812 - export.Base) * 4, 4))[0]
                self.assertEqual(pretranslate, 0x2AB5A0)
                self.assertEqual(library.get_data(0x2AB5DD, 12), bytes.fromhex(
                    "488b8f200100004885c9741b"))
                self.assertEqual(0x1802AB5E9 + 0x1B, 0x1802AB604)
                self.assertEqual(library.get_data(0x2AB5EF, 7), bytes.fromhex("488b80b8000000"))
                self.assertLess(0x1802AB5F6, 0x1802AB604)
                self.assertEqual(image.get_data(0x630050, 5), bytes.fromhex("e88bfeffff"))
                self.assertEqual(0x140630055 + struct.unpack("<i", bytes.fromhex("8bfeffff"))[0],
                                 0x14062FEE0)
                self.assertEqual(image.get_data(0x62FEFB, 5), bytes.fromhex("e80c041500"))
                self.assertEqual(0x14062FF00 + struct.unpack("<i", bytes.fromhex("0c041500"))[0],
                                 0x14078030C)
                frame_thunk = image.get_data(0x78030C, 6)
                self.assertEqual(frame_thunk[:2], b"\xff\x25")
                self.assertEqual(
                    imports[0x140780312 + struct.unpack_from("<i", frame_thunk, 2)[0]],
                    (b"mfc140.dll", None, 549))
                frame_ctor = struct.unpack("<I", library.get_data(
                    export.AddressOfFunctions + (549 - export.Base) * 4, 4))[0]
                self.assertEqual(frame_ctor, 0x2AB100)
                self.assertEqual(library.get_data(0x2AB109, 5), bytes.fromhex("e89263ffff"))
                self.assertEqual(0x1802AB10E + struct.unpack("<i", bytes.fromhex("9263ffff"))[0],
                                 0x1802A14A0)
                self.assertEqual(library.get_data(0x2A14D7, 3), bytes.fromhex("4533f6"))
                self.assertEqual(library.get_data(0x2A157A, 7), bytes.fromhex("4c89b720010000"))

                def qword_stores(pe, base, vtable_rva, slots):
                    starts = [item.struct.BeginAddress for item in pe.DIRECTORY_ENTRY_EXCEPTION]
                    ends = [item.struct.EndAddress for item in pe.DIRECTORY_ENTRY_EXCEPTION]
                    seen = set()
                    stores = []
                    detailed = Cs(CS_ARCH_X86, CS_MODE_64)
                    detailed.detail = True
                    needle = bytes.fromhex("20010000")
                    for index in range(slots):
                        pointer = struct.unpack("<Q", pe.get_data(vtable_rva + index * 8, 8))[0]
                        rva = pointer - base
                        place = bisect.bisect_right(starts, rva) - 1
                        if place < 0 or rva >= ends[place] or starts[place] in seen:
                            continue
                        seen.add(starts[place])
                        body = pe.get_data(starts[place], ends[place] - starts[place])
                        if needle not in body:
                            continue
                        covered = 0
                        for insn in detailed.disasm(body, base + starts[place]):
                            covered = insn.address + insn.size
                            for operand in insn.operands:
                                if (operand.type == X86_OP_MEM and operand.mem.disp == 0x120
                                        and operand.access & CS_AC_WRITE
                                        and "qword" in insn.op_str and "rsp" not in insn.op_str):
                                    stores.append(insn.address)
                        self.assertGreater(covered, base + starts[place] + body.find(needle))
                    return stores

                self.assertEqual(qword_stores(library, 0x180000000, 0x340A28, 114), [])
                self.assertEqual(qword_stores(library, 0x180000000, 0x342078, 116), [])
                self.assertEqual(qword_stores(image, IMAGE_BASE, 0xE8DC48, 116), [])
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_view_message_map_inserts_the_document_list_on_wm_create(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        library_bytes = (ROOT / "v3d_files_" / "mfc140.dll").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        self.assertEqual(hashlib.sha256(library_bytes).hexdigest(),
                         "0cf26008fae0cb61dfe49e1c3fc17e0dd860be011d9a6a64b452f56335bafbfe")
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image, pefile.PE(
                    data=library_bytes, fast_load=True) as library:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                library.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]])
                imports = {
                    item.address: (entry.dll, item.name.decode() if item.name else None, item.ordinal)
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                library_imports = {
                    item.address: item.name.decode() if item.name else None
                    for entry in library.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                getter = struct.unpack("<Q", image.get_data(0xEAC650 + 0x60, 8))[0]
                self.assertEqual(getter, 0x1406AC2D0)
                self.assertEqual(image.get_data(0x6AC2D0, 5), bytes.fromhex("e9eb010000"))
                self.assertEqual(0x1406AC2D5 + struct.unpack("<i", bytes.fromhex("eb010000"))[0],
                                 0x1406AC4C0)
                self.assertEqual(image.get_data(0x6AC4C0, 7), bytes.fromhex("488d05b9098000"))
                message_map = 0x1406AC4C7 + struct.unpack("<i", bytes.fromhex("b9098000"))[0]
                self.assertEqual(message_map, 0x140EACE80)
                base_getter, entries = struct.unpack("<QQ", image.get_data(message_map - IMAGE_BASE, 16))
                self.assertEqual(base_getter, 0x1407805A6)
                messages = []
                cursor = entries
                while True:
                    record = struct.unpack("<IIIIQQ", image.get_data(cursor - IMAGE_BASE, 32))
                    if record == (0, 0, 0, 0, 0, 0):
                        break
                    messages.append(record[0])
                    cursor += 32
                    self.assertLess(len(messages), 80)
                self.assertEqual(len(messages), 33)
                self.assertNotIn(1, messages)
                thunk = image.get_data(0x7805A6, 6)
                self.assertEqual(thunk[:2], b"\xff\x25")
                self.assertEqual(
                    imports[0x1407805AC + struct.unpack_from("<i", thunk, 2)[0]],
                    (b"mfc140.dll", None, 7215))
                export = library.DIRECTORY_ENTRY_EXPORT.struct
                form_getter = struct.unpack("<I", library.get_data(
                    export.AddressOfFunctions + (7215 - export.Base) * 4, 4))[0]
                self.assertEqual(form_getter, 0x27EE70)
                self.assertEqual(library.get_data(0x27EE70, 8), bytes.fromhex("488d05d9ad0b00c3"))
                form_map = 0x18027EE77 + struct.unpack("<i", bytes.fromhex("d9ad0b00"))[0]
                self.assertEqual(form_map, 0x180339C50)
                form_base, form_entries = struct.unpack("<QQ", library.get_data(form_map - 0x180000000, 16))
                self.assertEqual(form_base, 0x18028BE90)
                form_messages = []
                cursor = form_entries
                create_handler = None
                while True:
                    record = struct.unpack("<IIIIQQ", library.get_data(cursor - 0x180000000, 32))
                    if record == (0, 0, 0, 0, 0, 0):
                        break
                    form_messages.append(record[0])
                    if record[0] == 1:
                        create_handler = record[5]
                    cursor += 32
                self.assertEqual(form_messages, [7, 1, 792, 272])
                self.assertEqual(create_handler, 0x18027F230)
                self.assertEqual(library.get_data(0x27F230, 15), bytes.fromhex(
                    "488b8138010000488902e9d1cdffff"))
                self.assertEqual(0x18027F23F + struct.unpack("<i", bytes.fromhex("d1cdffff"))[0],
                                 0x18027C010)
                self.assertEqual(library.get_data(0x27C020, 12), bytes.fromhex(
                    "e84b33010083f8ff75040bc0"))
                self.assertEqual(0x18027C025 + struct.unpack("<i", bytes.fromhex("4b330100"))[0],
                                 0x18028F370)
                self.assertEqual(0x18027C02A + 4, 0x18027C02E)
                self.assertEqual(library.get_data(0x27C02E, 20), bytes.fromhex(
                    "488b074885c07411488b48084885c97408488bd3"))
                self.assertEqual(library.get_data(0x27C042, 5), bytes.fromhex("e8593afaff"))
                self.assertEqual(0x18027C047 + struct.unpack("<i", bytes.fromhex("593afaff"))[0],
                                 0x18021FAA0)
                self.assertEqual(library.get_data(0x21FAB0, 16), bytes.fromhex(
                    "4883c158e8176001004889bbe8000000"))
                self.assertEqual(0x18021FAB9 + struct.unpack("<i", bytes.fromhex("17600100"))[0],
                                 0x180235AD0)
                self.assertEqual(library.get_data(0x235A34, 4), bytes.fromhex("48ff4318"))
                self.assertEqual(0x58 + 0x18, 0x70)
                self.assertEqual(library.get_data(0x235AEC, 4), bytes.fromhex("48895810"))
                self.assertEqual(library.get_data(0x21FAC3, 10), bytes.fromhex(
                    "488b07488b80f0000000"))
                changed = struct.unpack("<Q", image.get_data(0xEA3868 + 0xF0, 8))[0]
                self.assertEqual(changed, 0x14077FE08)
                changed_thunk = image.get_data(0x77FE08, 6)
                self.assertEqual(changed_thunk[:2], b"\xff\x25")
                self.assertEqual(
                    imports[0x14077FE0E + struct.unpack_from("<i", changed_thunk, 2)[0]],
                    (b"mfc140.dll", None, 8734))
                changed_view = struct.unpack("<I", library.get_data(
                    export.AddressOfFunctions + (8734 - export.Base) * 4, 4))[0]
                self.assertEqual(changed_view, 0x21E240)
                self.assertEqual(library.get_data(0x21E240, 8), bytes.fromhex("4883797000751583"))
                self.assertEqual(0x18021E247 + 0x15, 0x18021E25C)
                self.assertEqual(library.get_data(0x21E25C, 10), bytes.fromhex("488b01488b80e0010000"))
                self.assertEqual(library.get_data(0x27F050, 12), bytes.fromhex("48895c241055565741564157"))
                self.assertEqual(library.get_data(0x27F05C, 5), bytes.fromhex("488d6c24e9"))
                self.assertEqual(0x7F - (0x30 + 0x17), 0x38)
                self.assertEqual(library.get_data(0x27F076, 25), bytes.fromhex(
                    "488b457f488bf9488b7567418bd94c8b7d6f48898138010000"))
                self.assertLess(0x18027F088, 0x18027F0EF)
                self.assertEqual(library.get_data(0x27F0EF, 5), bytes.fromhex("e83cc4f8ff"))
                self.assertEqual(0x18027F0F4 + struct.unpack("<i", bytes.fromhex("3cc4f8ff"))[0],
                                 0x18020B530)
                self.assertLess(0x18027F0EF, 0x18027F105)
                self.assertEqual(library.get_data(0x27F105, 8), bytes.fromhex("4883a73801000000"))
                self.assertEqual(library.get_data(0x20B719, 5), bytes.fromhex("e812440800"))
                self.assertEqual(0x18020B71E + struct.unpack("<i", bytes.fromhex("12440800"))[0],
                                 0x18028FB30)
                self.assertEqual(library.get_data(0x20B730, 5), bytes.fromhex("e85b0a0000"))
                self.assertEqual(0x18020B735 + struct.unpack("<i", bytes.fromhex("5b0a0000"))[0],
                                 0x18020C190)
                self.assertLess(0x18020B719, 0x18020B730)

                def library_import(address):
                    raw_call = library.get_data(address - 0x180000000, 6)
                    self.assertEqual(raw_call[:2], b"\xff\x15")
                    return library_imports[address + 6 + struct.unpack_from("<i", raw_call, 2)[0]]

                self.assertEqual(library_import(0x18020C1FE), "CreateDialogIndirectParamA")
                self.assertEqual(library.get_data(0x28FB78, 4), bytes.fromhex("418d4805"))
                self.assertEqual(library.get_data(0x28FB6E, 7), bytes.fromhex("488d15ebfcffff"))
                self.assertEqual(0x18028FB75 + struct.unpack("<i", bytes.fromhex("ebfcffff"))[0],
                                 0x18028F860)
                self.assertEqual(library.get_data(0x28F8BE, 5), bytes.fromhex("83fb03740b"))
                self.assertEqual(0x18028F8C3 + 0x0B, 0x18028F8CE)
                self.assertEqual(library.get_data(0x28F9C3, 8), bytes.fromhex("bafcffffff488bcf"))
                self.assertEqual(library_import(0x18028F9CB), "SetWindowLongPtrA")
                self.assertEqual(library.get_data(0x28F9BC, 4), bytes.fromhex("488b5870"))
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_wm_create_reaches_the_form_view_message_map(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        library_bytes = (ROOT / "v3d_files_" / "mfc140.dll").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        self.assertEqual(hashlib.sha256(library_bytes).hexdigest(),
                         "0cf26008fae0cb61dfe49e1c3fc17e0dd860be011d9a6a64b452f56335bafbfe")
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image, pefile.PE(
                    data=library_bytes, fast_load=True) as library:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                library.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]])
                imports = {
                    item.address: (entry.dll, item.name.decode() if item.name else None, item.ordinal)
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                library_imports = {
                    item.address: item.name.decode() if item.name else None
                    for entry in library.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                export = library.DIRECTORY_ENTRY_EXPORT.struct

                def library_import(address):
                    raw_call = library.get_data(address - 0x180000000, 6)
                    self.assertEqual(raw_call[:2], b"\xff\x15")
                    return library_imports[address + 6 + struct.unpack_from("<i", raw_call, 2)[0]]

                def export_rva(ordinal):
                    index = ordinal - export.Base
                    self.assertGreaterEqual(index, 0)
                    self.assertLess(index, export.NumberOfFunctions)
                    return struct.unpack("<I", library.get_data(
                        export.AddressOfFunctions + index * 4, 4))[0]

                def exe_thunk(address):
                    raw = image.get_data(address - IMAGE_BASE, 6)
                    self.assertEqual(raw[:2], b"\xff\x25")
                    return imports[address + 6 + struct.unpack_from("<i", raw, 2)[0]]

                self.assertEqual(image.get_data(0x6AB597, 10), bytes.fromhex("ba2b080000e8c94f0d00"))
                self.assertEqual(0x1406AB5A1 + struct.unpack("<i", bytes.fromhex("c94f0d00"))[0],
                                 0x14078056A)
                self.assertLess(0x1406AB59C, 0x1406AB5A2)
                self.assertEqual(exe_thunk(0x14078056A), (b"mfc140.dll", None, 499))
                self.assertEqual(export_rva(499), 0x27EF30)
                self.assertEqual(library.get_data(0x27EF3F, 5), bytes.fromhex("e81cd60000"))
                self.assertEqual(0x18027EF44 + struct.unpack("<i", bytes.fromhex("1cd60000"))[0],
                                 0x18028C560)
                self.assertEqual(library.get_data(0x28C569, 5), bytes.fromhex("e862f9feff"))
                self.assertEqual(0x18028C56E + struct.unpack("<i", bytes.fromhex("62f9feff"))[0],
                                 0x18027BED0)
                self.assertEqual(library.get_data(0x27BED9, 5), bytes.fromhex("e8b22e0100"))
                self.assertEqual(0x18027BEDE + struct.unpack("<i", bytes.fromhex("b22e0100"))[0],
                                 0x18028ED90)
                self.assertEqual(library.get_data(0x28ED9B, 5), bytes.fromhex("e820000000"))
                self.assertEqual(0x18028EDA0 + struct.unpack("<i", bytes.fromhex("20000000"))[0],
                                 0x18028EDC0)
                self.assertEqual(library.get_data(0x28EDD5, 5), bytes.fromhex("e84623f5ff"))
                self.assertEqual(0x18028EDDA + struct.unpack("<i", bytes.fromhex("4623f5ff"))[0],
                                 0x1801E1120)
                self.assertEqual(library.get_data(0x1E1126, 12), bytes.fromhex(
                    "488bd9e8c26ff5ff48894338"))
                self.assertEqual(0x1801E112E + struct.unpack("<i", bytes.fromhex("c26ff5ff"))[0],
                                 0x1801380F0)

                def rip_target(rva, size, displacement):
                    return 0x180000000 + rva + size + struct.unpack("<i", bytes.fromhex(displacement))[0]

                self.assertEqual(rip_target(0x1380F4, 7, "f5010000"), 0x1801382F0)
                self.assertEqual(rip_target(0x1380FB, 7, "deb12b00"), 0x1803F32E0)
                self.assertEqual(library.get_data(0x13810C, 9), bytes.fromhex("488b40084885c07518"))
                self.assertEqual(0x180138115 + 0x18, 0x18013812D)
                self.assertEqual(rip_target(0x138115, 7, "74010000"), 0x180138290)
                self.assertEqual(library.get_data(0x1382C1, 7), bytes.fromhex("4c8d0578fdffff"))
                self.assertEqual(rip_target(0x1382C1, 7, "78fdffff"), 0x180138040)
                self.assertEqual(library.get_data(0x137A48, 3), bytes.fromhex("498bf8"))
                self.assertEqual(library.get_data(0x137AD2, 4), bytes.fromhex("49897e70"))
                self.assertEqual(library.get_data(0x13808C, 5), bytes.fromhex("e85f751500"))
                self.assertEqual(0x180138091 + struct.unpack("<i", bytes.fromhex("5f751500"))[0],
                                 0x18028F5F0)
                self.assertEqual(library.get_data(0x27E9, 7), bytes.fromhex("4c8d0570202b00"))
                self.assertEqual(rip_target(0x27E9, 7, "70202b00"), 0x1802B4860)
                self.assertEqual(library.get_data(0x2801, 5), bytes.fromhex("e81a521300"))
                self.assertEqual(0x180002806 + struct.unpack("<i", bytes.fromhex("1a521300"))[0],
                                 0x180137A20)
                self.assertEqual(library.get_data(0x2B48A3, 5), bytes.fromhex("e848adfdff"))
                self.assertEqual(0x1802B48A8 + struct.unpack("<i", bytes.fromhex("48adfdff"))[0],
                                 0x18028F5F0)

                self.assertEqual(library.get_data(0x20B716, 8), bytes.fromhex("488bcfe812440800"))
                self.assertLess(0x18020B719, 0x18020B730)
                self.assertEqual(rip_target(0x28FB3D, 7, "ac87eaff"), 0x1801382F0)
                self.assertEqual(rip_target(0x28FB44, 7, "95371600"), 0x1803F32E0)
                self.assertEqual(library.get_data(0x28FB82, 13), bytes.fromhex(
                    "488943484885c0741548897b28"))
                self.assertEqual(library_import(0x18028FB7C), "SetWindowsHookExA")
                self.assertEqual(rip_target(0x28F89C, 7, "4d8aeaff"), 0x1801382F0)
                self.assertEqual(rip_target(0x28F8A3, 7, "363a1600"), 0x1803F32E0)
                self.assertEqual(library.get_data(0x28F8D1, 14), bytes.fromhex(
                    "4c8b7028e81688eaff4d85f67517"))
                self.assertEqual(0x18028F8DA + struct.unpack("<i", bytes.fromhex("1688eaff"))[0],
                                 0x1801380F0)
                self.assertEqual(0x18028F8DF + 0x17, 0x18028F8F6)
                self.assertEqual(library.get_data(0x28F96B, 9), bytes.fromhex("4d85f60f8485000000"))
                self.assertEqual(0x18028F96E + 6, 0x18028F974)
                self.assertEqual(0x18028F974 + struct.unpack("<i", bytes.fromhex("85000000"))[0],
                                 0x18028F9F9)
                self.assertEqual(library.get_data(0x28F974, 14), bytes.fromhex(
                    "498b5638488d4c2430e82e7feaff"))
                self.assertEqual(0x18028F982 + struct.unpack("<i", bytes.fromhex("2e7feaff"))[0],
                                 0x1801378B0)
                self.assertEqual(library.get_data(0x28F989, 5), bytes.fromhex("e872fbffff"))
                self.assertEqual(0x18028F98E + struct.unpack("<i", bytes.fromhex("72fbffff"))[0],
                                 0x18028F500)
                self.assertLess(0x18028F989, 0x18028F9BC)
                self.assertEqual(library.get_data(0x28F9D9, 4), bytes.fromhex("4c896628"))

                self.assertEqual(library.get_data(0x28F51E, 24), bytes.fromhex(
                    "b901000000e8a0feffff488bd748897e40488bd8488d4828"))
                self.assertEqual(0x18028F528 + struct.unpack("<i", bytes.fromhex("a0feffff"))[0],
                                 0x18028F3C8)
                self.assertEqual(library.get_data(0x28F536, 5), bytes.fromhex("e8d575faff"))
                self.assertEqual(0x18028F53B + struct.unpack("<i", bytes.fromhex("d575faff"))[0],
                                 0x180236B10)
                self.assertEqual(library.get_data(0x236B77, 4), bytes.fromhex("498d4010"))
                self.assertEqual(library.get_data(0x28F541, 3), bytes.fromhex("488930"))
                self.assertEqual(library.get_data(0x28F4D9, 7), bytes.fromhex("33c9e8e8feffff"))
                self.assertEqual(0x18028F4E0 + struct.unpack("<i", bytes.fromhex("e8feffff"))[0],
                                 0x18028F3C8)
                self.assertEqual(library.get_data(0x28F4EA, 12), bytes.fromhex("4883c128488bd3e86a75faff"))
                self.assertEqual(0x18028F4F6 + struct.unpack("<i", bytes.fromhex("6a75faff"))[0],
                                 0x180236A60)
                self.assertEqual(library.get_data(0x236AD3, 4), bytes.fromhex("488b4010"))

                self.assertEqual(library.get_data(0x28F61E, 16), bytes.fromhex(
                    "e8adfeffff4885c0741e483958407518"))
                self.assertEqual(0x18028F623 + struct.unpack("<i", bytes.fromhex("adfeffff"))[0],
                                 0x18028F4D0)
                self.assertEqual(0x18028F62E + 0x18, 0x18028F646)
                self.assertEqual(library.get_data(0x28F63F, 5), bytes.fromhex("e8ecfaffff"))
                self.assertEqual(0x18028F644 + struct.unpack("<i", bytes.fromhex("ecfaffff"))[0],
                                 0x18028F130)
                self.assertEqual(library.get_data(0x28F1F0, 5), bytes.fromhex("83fe02751e"))
                self.assertEqual(0x18028F1F5 + 0x1E, 0x18028F213)
                self.assertEqual(library.get_data(0x28F21E, 8), bytes.fromhex("81fe10010000751d"))
                self.assertEqual(0x18028F226 + 0x1D, 0x18028F243)
                self.assertNotIn(1, (2, 0x110))
                self.assertEqual(library.get_data(0x28F243, 21), bytes.fromhex(
                    "488b074d8bcf4d8bc48bd6488bcf488b8038020000"))

                self.assertEqual(struct.unpack("<Q", image.get_data(0xEAC650 + 0x238, 8))[0], 0x14077F856)
                self.assertEqual(exe_thunk(0x14077F856), (b"mfc140.dll", None, 14128))
                self.assertEqual(export_rva(14128), 0x291A60)
                self.assertEqual(library.get_data(0x291A90, 15), bytes.fromhex(
                    "488b80400200008beaff1551d10300"))
                self.assertEqual(library.get_data(0x291AA1, 2), bytes.fromhex("751d"))
                self.assertEqual(struct.unpack("<Q", image.get_data(0xEAC650 + 0x240, 8))[0], 0x14077F62E)
                self.assertEqual(exe_thunk(0x14077F62E), (b"mfc140.dll", None, 11575))
                self.assertEqual(export_rva(11575), 0x291AE0)
                self.assertEqual(library.get_data(0x291B0C, 12), bytes.fromhex("498bf14d8be0448bf24c8bf9"))
                self.assertEqual(library.get_data(0x291B26, 5), bytes.fromhex("bb01000000"))
                self.assertEqual(library.get_data(0x291B56, 5), bytes.fromhex("443bf37523"))
                self.assertEqual(0x180291B5B + 0x23, 0x180291B7E)
                self.assertEqual(library.get_data(0x291B79, 9), bytes.fromhex("e8625300004183fe4e"))
                self.assertEqual(library.get_data(0x291C76, 22), bytes.fromhex(
                    "4183fe05743e4183fe0f74214183fe140f8597000000"))
                self.assertEqual(0x180291C8C + struct.unpack("<i", bytes.fromhex("97000000"))[0],
                                 0x180291D23)
                self.assertEqual(library.get_data(0x291D23, 12), bytes.fromhex(
                    "498b07498bcf488b4060ff15"))
                self.assertEqual(library.get_data(0x291DDF, 2), bytes.fromhex("33d2"))
                self.assertEqual(library.get_data(0x291E00, 15), bytes.fromhex(
                    "443937750a3957047505395708760d"))
                self.assertEqual(library.get_data(0x291DA9, 8), bytes.fromhex("488b5f18488b4f10"))
                self.assertEqual(library.get_data(0x291DDC, 5), bytes.fromhex("488b0f33d2"))
                self.assertEqual(library.get_data(0x291E25, 3), bytes.fromhex("488bc1"))
                self.assertEqual(struct.unpack("<Q", image.get_data(0xEAC650 + 0x60, 8))[0], 0x1406AC2D0)
                self.assertEqual(image.get_data(0x6AC2D0, 5), bytes.fromhex("e9eb010000"))
                self.assertEqual(0x1406AC2D5 + struct.unpack("<i", bytes.fromhex("eb010000"))[0],
                                 0x1406AC4C0)
                self.assertEqual(image.get_data(0x6AC4C0, 7), bytes.fromhex("488d05b9098000"))
                self.assertEqual(0x1406AC4C7 + struct.unpack("<i", bytes.fromhex("b9098000"))[0],
                                 0x140EACE80)
                self.assertEqual(struct.unpack("<Q", image.get_data(0xEACE80, 8))[0], 0x1407805A6)
                self.assertEqual(exe_thunk(0x1407805A6), (b"mfc140.dll", None, 7215))
                self.assertEqual(export_rva(7215), 0x27EE70)
                self.assertEqual(library.get_data(0x27EE70, 8), bytes.fromhex("488d05d9ad0b00c3"))
                form_map = 0x18027EE77 + struct.unpack("<i", bytes.fromhex("d9ad0b00"))[0]
                self.assertEqual(form_map, 0x180339C50)
                _, form_entries = struct.unpack("<QQ", library.get_data(form_map - 0x180000000, 16))
                create_entry = None
                cursor = form_entries
                for _ in range(8):
                    record = struct.unpack("<IIIIQQ", library.get_data(cursor - 0x180000000, 32))
                    if record[0] == 1:
                        create_entry = record
                        break
                    cursor += 32
                self.assertEqual(create_entry, (1, 0, 0, 0, 0xD, 0x18027F230))
                self.assertEqual(0xD - 1, 0x0C)
                self.assertEqual(library.get_data(0x2926BC + 0x0C * 4, 4), bytes.fromhex("08202900"))
                self.assertEqual(0x180000000 + struct.unpack("<I", bytes.fromhex("08202900"))[0], 0x180292008)
                self.assertEqual(library.get_data(0x292008, 8), bytes.fromhex("488bd6e906ffffff"))
                self.assertEqual(0x180292010 + struct.unpack("<i", bytes.fromhex("06ffffff"))[0],
                                 0x180291F16)
                self.assertEqual(library.get_data(0x291F16, 6), bytes.fromhex("498bcf488bc3"))
                self.assertEqual(library.get_data(0x291F22, 7), bytes.fromhex("4898e975070000"))
                self.assertEqual(0x180291F29 + struct.unpack("<i", bytes.fromhex("75070000"))[0],
                                 0x18029269E)
                self.assertEqual(library.get_data(0x29269E, 5), bytes.fromhex("ba01000000"))
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_document_close_does_not_join_the_skip_producer(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        library_bytes = (ROOT / "v3d_files_" / "mfc140.dll").read_bytes()
        base_tools = (ROOT / "v3d_files_" / "BaseTools.dll").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        self.assertEqual(hashlib.sha256(library_bytes).hexdigest(),
                         "0cf26008fae0cb61dfe49e1c3fc17e0dd860be011d9a6a64b452f56335bafbfe")
        self.assertEqual(hashlib.sha256(base_tools).hexdigest(),
                         "a41b4b00cf464da7da886f2303e6161f4474bda29b32793d39e4c6cfc39547f8")
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image, pefile.PE(
                    data=library_bytes, fast_load=True) as library, pefile.PE(
                    data=base_tools, fast_load=True) as tools:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
                library.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]])
                tools.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]])
                imports = {
                    item.address: (entry.dll, item.name.decode() if item.name else None, item.ordinal)
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                library_imports = {
                    item.address: item.name.decode() if item.name else None
                    for entry in library.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                self.assertEqual(struct.unpack("<QQQ", image.get_data(0xEA8A48, 24)), (
                    0x14069A8F0, 0x1406A1C80, 0x14076DB80))
                self.assertEqual(image.get_data(0x76DB80, 6), bytes.fromhex("ff2512595e00"))
                start_iat = 0x14076DB86 + struct.unpack("<i", bytes.fromhex("12595e00"))[0]
                self.assertEqual(imports[start_iat], (
                    b"BaseTools.dll", "?Start@CViThread@@UEAA_NXZ", None))
                self.assertEqual(tools.get_data(0x7E070, 7), bytes.fromhex("488b0148ff6008"))
                self.assertEqual(image.get_data(0x6A1D2F, 21), bytes.fromhex(
                    "80b82d380000017507e863000000eb05e88c030000"))
                self.assertEqual(0x1406A1D3D + struct.unpack("<i", bytes.fromhex("63000000"))[0],
                                 0x1406A1DA0)
                self.assertEqual(0x1406A1D44 + struct.unpack("<i", bytes.fromhex("8c030000"))[0],
                                 0x1406A20D0)
                self.assertEqual(image.get_data(0x6A1F8C, 25), bytes.fromhex(
                    "c6433201488bcbe838f6ffff488d8848250000488b01ff5008"))
                self.assertEqual(0x1406A1F98 + struct.unpack("<i", bytes.fromhex("38f6ffff"))[0],
                                 0x1406A15D0)
                self.assertEqual(image.get_data(0x6A20AE, 2), bytes.fromhex("33c0"))
                end_call = image.get_data(0x6A1D6B, 5)
                self.assertEqual(end_call[0], 0xE8)
                end_thunk = 0x1406A1D70 + struct.unpack_from("<i", end_call, 1)[0]
                self.assertEqual(end_thunk, 0x140780288)
                thunk = image.get_data(end_thunk - IMAGE_BASE, 6)
                self.assertEqual(thunk[:2], b"\xff\x25")
                end_iat = end_thunk + 6 + struct.unpack_from("<i", thunk, 2)[0]
                self.assertEqual(imports[end_iat], (b"mfc140.dll", None, 2175))
                ordinal_rva = struct.unpack("<I", library.get_data(
                    library.DIRECTORY_ENTRY_EXPORT.struct.AddressOfFunctions
                    + (2175 - library.DIRECTORY_ENTRY_EXPORT.struct.Base) * 4, 4))[0]
                self.assertEqual(ordinal_rva, 0x278770)
                tail = library.get_data(0x2787E6, 7)
                self.assertEqual(tail[:3], bytes.fromhex("48ff25"))
                endthread = 0x1802787ED + struct.unpack_from("<i", tail, 3)[0]
                self.assertEqual(library_imports[endthread], "_endthreadex")

                text = next(section for section in image.sections if section.Name.startswith(b".text"))
                text_data = text.get_data()
                text_base = IMAGE_BASE + text.VirtualAddress

                direct_calls = {
                    0x1406A20D0: [], 0x1406A5010: [], 0x1406A06B0: [], 0x1406920F0: []}
                for index in range(len(text_data) - 5):
                    if text_data[index] not in (0xE8, 0xE9):
                        continue
                    destination = text_base + index + 5 + struct.unpack_from(
                        "<i", text_data, index + 1)[0]
                    if destination in direct_calls:
                        direct_calls[destination].append(text_base + index)
                self.assertEqual(direct_calls[0x1406A20D0], [0x1406A1D3F])
                self.assertEqual(direct_calls[0x1406A5010], [0x1406A378C])
                self.assertEqual(direct_calls[0x1406A06B0], [0x1406A52B5])
                self.assertEqual(direct_calls[0x1406920F0], [0x14068DA61])
                self.assertEqual(image.get_data(0x68DA4C, 21), bytes.fromhex(
                    "48c1e8106683f84e7538b8cfb1000066443bc0752d"))
                self.assertEqual(image.get_data(0x6921F2, 33), bytes.fromhex(
                    "4533c0488d942480000000488b8b68380000ff1566126c00"
                    "3c017413b9f4010000"))
                stop_iat = 0x14069220A + struct.unpack("<i", bytes.fromhex("66126c00"))[0]
                self.assertEqual(imports[stop_iat][1], "?Stop@CViThread@@QEAA_NAEAKK@Z")
                self.assertEqual(0x140692218 + struct.unpack("<i", bytes.fromhex("d868f5ff"))[0],
                                 0x1405E8AF0)
                self.assertEqual(image.get_data(0x5E8B13, 4), bytes.fromhex("c7442420"))
                self.assertEqual(image.get_data(0x5E8B25, 6)[:2], b"\xff\x15")
                peek_iat = 0x1405E8B2B + struct.unpack("<i", image.get_data(0x5E8B27, 4))[0]
                self.assertEqual(imports[peek_iat][1], "PeekMessageA")
                translate_iat = 0x1405E8B3B + struct.unpack("<i", image.get_data(0x5E8B37, 4))[0]
                dispatch_iat = 0x1405E8B46 + struct.unpack("<i", image.get_data(0x5E8B42, 4))[0]
                sleep_iat = 0x1405E8B70 + struct.unpack("<i", image.get_data(0x5E8B6C, 4))[0]
                self.assertEqual(imports[translate_iat][1], "TranslateMessage")
                self.assertEqual(imports[dispatch_iat][1], "DispatchMessageA")
                self.assertEqual(imports[sleep_iat][1], "Sleep")

                close = next(item.struct for item in image.DIRECTORY_ENTRY_EXCEPTION
                             if item.struct.BeginAddress == 0x68D9D0)
                destructor = next(item.struct for item in image.DIRECTORY_ENTRY_EXCEPTION
                                  if item.struct.BeginAddress == 0x67FC20)
                for bounds in (close, destructor):
                    body = text_data[bounds.BeginAddress - text.VirtualAddress:
                                     bounds.EndAddress - text.VirtualAddress]
                    for index in range(len(body) - 5):
                        if body[index] != 0xE8:
                            continue
                        site = IMAGE_BASE + bounds.BeginAddress + index
                        destination = site + 5 + struct.unpack_from("<i", body, index + 1)[0]
                        self.assertNotIn(destination, {0x1406920F0, 0x140680D70, 0x140680C00})
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_close_does_not_set_the_production_stop_flag(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        library_bytes = (ROOT / "v3d_files_" / "mfc140.dll").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        self.assertEqual(hashlib.sha256(library_bytes).hexdigest(),
                         "0cf26008fae0cb61dfe49e1c3fc17e0dd860be011d9a6a64b452f56335bafbfe")
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image, pefile.PE(
                    data=library_bytes, fast_load=True) as library:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
                library.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]])
                imports = {
                    item.address: (entry.dll, item.name.decode() if item.name else None, item.ordinal)
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                self.assertEqual(0x2548 + 0x12E6, 0x382E)
                constructor = image.get_data(0x67DEE4, 14)
                self.assertEqual(constructor, bytes.fromhex("488d056d5c820048898648250000"))
                vtable = 0x14067DEEB + struct.unpack_from("<i", constructor, 3)[0]
                self.assertEqual(vtable, 0x140EA3B58)
                destructor = image.get_data(0x67FC5B, 14)
                self.assertEqual(destructor, bytes.fromhex("488d05f63e820048898148250000"))
                self.assertEqual(0x14067FC62 + struct.unpack_from("<i", destructor, 3)[0], vtable)
                self.assertEqual(struct.unpack("<QQQ", image.get_data(0xEA3B58, 24)), (
                    0x140691C50, 0x140680C00, 0x140680D70))
                self.assertEqual(image.get_data(0x680C7D, 7), bytes.fromhex("80bfe612000001"))
                self.assertEqual(image.get_data(0x680C8F, 7), bytes.fromhex("c687e612000001"))
                self.assertEqual(image.get_data(0x680CB0, 7), bytes.fromhex("c74310cfb10000"))
                post = image.get_data(0x680CE5, 16)
                self.assertEqual(post, bytes.fromhex("4c8bcb4533c0418d504eff150baf6d00"))
                post_iat = 0x140680CF5 + struct.unpack_from("<i", post, 12)[0]
                self.assertEqual(imports[post_iat][1], "PostMessageA")
                self.assertEqual(image.get_data(0x69203B, 7), bytes.fromhex("c6862e38000000"))
                self.assertEqual(image.get_data(0x6A45C1, 14), bytes.fromhex(
                    "80b82e38000001750541c6463201"))
                leave = image.get_data(0x6A45E6, 12)
                self.assertEqual(leave, bytes.fromhex("41807e3200757ce97ee1ffff"))
                self.assertEqual(0x1406A45F2 + struct.unpack_from("<i", leave, 8)[0], 0x1406A2770)

                text = next(section for section in image.sections if section.Name.startswith(b".text"))
                text_data = text.get_data()
                text_base = IMAGE_BASE + text.VirtualAddress

                def displacement_sites(displacement: int) -> list[int]:
                    needle = struct.pack("<I", displacement)
                    sites = []
                    start = 0
                    while True:
                        index = text_data.find(needle, start)
                        if index < 0:
                            return sites
                        if text_data[index - 1] not in (0xE8, 0xE9):
                            sites.append(text_base + index)
                        start = index + 1

                self.assertEqual(displacement_sites(0x12E6), [
                    0x140680C7F, 0x140680C91, 0x140697C17])
                for call_site, call_target in ((0x1404827D5, 0x140483AC0), (0x1406B56D5, 0x1406B69C0)):
                    relative = text_data[call_site - text_base + 1:call_site - text_base + 5]
                    self.assertEqual(call_site + 5 + struct.unpack("<i", relative)[0], call_target)
                    self.assertEqual(struct.unpack("<i", relative)[0], 0x12E6)
                self.assertEqual(image.get_data(0x697C15, 7), bytes.fromhex("c686e612000000"))
                self.assertEqual(displacement_sites(0x382E), [
                    0x14069203D, 0x1406A45C3, 0x1406AF570])
                decoder = Cs(CS_ARCH_X86, CS_MODE_64)
                zero_fills = (
                    (0x14065BC12, bytes.fromhex("33db"), 0x14065BD0B,
                     bytes.fromhex("899f2c380000"), ("ebx", "rbx", "bx", "bl", "bh")),
                    (0x14065BDF4, bytes.fromhex("33db"), 0x14065BEE2,
                     bytes.fromhex("899e2c380000"), ("ebx", "rbx", "bx", "bl", "bh")),
                    (0x14065EF1F, bytes.fromhex("4533ff"), 0x14065F368,
                     bytes.fromhex("4489be2c380000"), ("r15", "r15d", "r15w", "r15b")),
                    (0x14067DF59, bytes.fromhex("4533f6"), 0x14067E17B,
                     bytes.fromhex("664489b62d380000"), ("r14", "r14d", "r14w", "r14b")),
                )
                for clear_at, clear_bytes, store_at, store_bytes, names in zero_fills:
                    self.assertEqual(image.get_data(clear_at - IMAGE_BASE, len(clear_bytes)), clear_bytes)
                    self.assertEqual(image.get_data(store_at - IMAGE_BASE, len(store_bytes)), store_bytes)
                    span = text_data[clear_at - text_base:store_at - text_base]
                    for instruction in decoder.disasm(span, clear_at):
                        if instruction.address == clear_at:
                            continue
                        destination = instruction.op_str.split(",", 1)[0].strip()
                        self.assertNotIn(destination, names)

                self.assertEqual(struct.unpack("<Q", image.get_data(0xEA3868 + 0x1B8, 8))[0],
                                 0x14077FE7A)
                self.assertEqual(struct.unpack("<Q", image.get_data(0xEA3868 + 0x1C0, 8))[0],
                                 0x14077FE80)
                self.assertEqual(image.get_data(0x77FE7A, 6), bytes.fromhex("ff2508f75d00"))
                can_close_iat = 0x14077FE80 + struct.unpack("<i", bytes.fromhex("08f75d00"))[0]
                save_iat = 0x14077FE86 + struct.unpack("<i", image.get_data(0x77FE82, 4))[0]
                self.assertEqual(imports[can_close_iat], (b"mfc140.dll", None, 2660))
                self.assertEqual(imports[save_iat], (b"mfc140.dll", None, 12588))
                can_close_rva = struct.unpack("<I", library.get_data(
                    library.DIRECTORY_ENTRY_EXPORT.struct.AddressOfFunctions
                    + (2660 - library.DIRECTORY_ENTRY_EXPORT.struct.Base) * 4, 4))[0]
                self.assertEqual(can_close_rva, 0x21E400)
                can_close = library.get_data(can_close_rva, 115)
                self.assertEqual(can_close, bytes.fromhex(
                    "40534883ec20488b01488bd9488b80e0000000ff15d7070b004889442430"
                    "4885c0488b03488bcb7437488b80e8000000488d542430ff15b5070b0048"
                    "8bc8e82d4607004885c0740983b8ec000000007f0848837c243000ebc8b8"
                    "01000000eb0d488b80c0010000ff1583070b004883c4205bc3"))
                self.assertEqual(can_close.find(struct.pack("<I", 0x382E)), -1)
                self.assertEqual(can_close.find(struct.pack("<I", 0x3868)), -1)

                child_map = library.get_data(0x342050, 16)
                self.assertEqual(child_map, bytes.fromhex("90142a8001000000f01e348001000000"))
                getter = struct.unpack_from("<Q", child_map)[0]
                self.assertEqual(getter, 0x1802A1490)
                self.assertEqual(library.get_data(0x2A1490, 8), bytes.fromhex("488d0579f50900c3"))
                self.assertEqual(0x1802A1497 + struct.unpack("<i", bytes.fromhex("79f50900"))[0],
                                 0x180340A10)
                frame_map = library.get_data(0x340A10, 16)
                self.assertEqual(struct.unpack_from("<Q", frame_map, 8)[0], 0x180340DC0)
                close_entry = library.get_data(0x340F80, 32)
                self.assertEqual(close_entry, bytes.fromhex(
                    "100000000000000000000000000000001300000000000000a02a2a8001000000"))
                self.assertEqual(struct.unpack_from("<Q", close_entry, 24)[0], 0x1802A2AA0)
                self.assertEqual(library.get_data(0x2A2AE0, 16), bytes.fromhex(
                    "488b08488bd7488b81b8010000488bcb"))
                self.assertEqual(library.get_data(0x2A2C81, 7), bytes.fromhex("488b8018010000"))

                close = next(item.struct for item in image.DIRECTORY_ENTRY_EXCEPTION
                             if item.struct.BeginAddress == 0x68D9D0)
                body = text_data[close.BeginAddress - text.VirtualAddress:
                                 close.EndAddress - text.VirtualAddress]
                for displacement in (0x12E6, 0x2548, 0x382E, 0x3868):
                    self.assertEqual(body.find(struct.pack("<I", displacement)), -1)
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_close_posts_the_non_stopping_view_message(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
                imports = {
                    item.address: (entry.dll, item.name.decode() if item.name else None, item.ordinal)
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                text = next(section for section in image.sections if section.Name.startswith(b".text"))
                text_data = text.get_data()
                text_base = IMAGE_BASE + text.VirtualAddress

                def target_of(site: int) -> int:
                    relative = text_data[site - text_base + 1:site - text_base + 5]
                    return site + 5 + struct.unpack("<i", relative)[0]

                self.assertEqual(target_of(0x14068DA1F), 0x1404E03F0)
                self.assertEqual(target_of(0x14068DA31), 0x14077FE26)
                self.assertLess(0x14068DA1F, 0x14068DA31)
                thunk = image.get_data(0x77FE26, 6)
                self.assertEqual(thunk[:2], b"\xff\x25")
                close_iat = 0x14077FE2C + struct.unpack_from("<i", thunk, 2)[0]
                self.assertEqual(imports[close_iat], (b"mfc140.dll", None, 8850))

                gate = image.get_data(0x4E03F6, 28)
                self.assertEqual(gate, bytes.fromhex(
                    "80b93008000000488bf90f850401000048895c2438c6813008000001"))
                self.assertEqual(0x1404E0406 + struct.unpack_from("<i", gate, 12)[0], 0x1404E050A)
                for site in (0x1404E0470, 0x1404E04E3):
                    posting = image.get_data(site - IMAGE_BASE, 22)
                    self.assertEqual(posting[:16], bytes.fromhex(
                        "488b48404533c9ba2c050000458d4106"))
                    self.assertEqual(posting[16:18], b"\xff\x15")
                    iat = site + 22 + struct.unpack_from("<i", posting, 18)[0]
                    self.assertEqual(imports[iat][1], "PostMessageA")

                entries = 0x140EACA40
                posted = None
                for index in range(40):
                    msg, _code, _nid, _nlast, _sig, pfn = struct.unpack(
                        "<IIIIQQ", image.get_data(entries - IMAGE_BASE + index * 32, 32))
                    if msg == 0 and pfn == 0:
                        break
                    if msg == 0x52C:
                        posted = pfn
                self.assertEqual(posted, 0x1406B0C00)
                self.assertEqual(image.get_data(0x6B0C25, 4), bytes.fromhex("488d5aff"))
                self.assertEqual(image.get_data(0x6B0CD4, 29), bytes.fromhex(
                    "4883fb070f8716060000488d0d1bf394ff8b849944136b004803c1ffe0"))
                table = struct.unpack("<8I", image.get_data(0x6B1344, 32))
                self.assertEqual(IMAGE_BASE + table[1], 0x1406B0FEC)
                self.assertEqual(IMAGE_BASE + table[5], 0x1406B1232)
                stop_arm = text_data[0x1406B0FEC - text_base:0x1406B1053 - text_base]
                close_arm = text_data[0x1406B1232 - text_base:0x1406B12B2 - text_base]
                self.assertIn(bytes.fromhex("4881c148250000488b01ff5008"), stop_arm)
                self.assertNotIn(bytes.fromhex("4881c148250000"), close_arm)

                def direct_calls(blob: bytes, origin: int) -> set[int]:
                    found = set()
                    for index in range(len(blob) - 5):
                        if blob[index] != 0xE8:
                            continue
                        found.add(origin + index + 5 + struct.unpack_from("<i", blob, index + 1)[0])
                    return found

                self.assertTrue(direct_calls(close_arm, 0x1406B1232).isdisjoint(
                    {0x140680C00, 0x140680D70, 0x1406920F0}))
                for callee in (0x140697CE0, 0x1406B3100, 0x1406319F0):
                    bounds = next(item.struct for item in image.DIRECTORY_ENTRY_EXCEPTION
                                  if item.struct.BeginAddress == callee - IMAGE_BASE)
                    body = text_data[bounds.BeginAddress - text.VirtualAddress:
                                     bounds.EndAddress - text.VirtualAddress]
                    self.assertTrue(direct_calls(
                        body, IMAGE_BASE + bounds.BeginAddress).isdisjoint(
                        {0x140680C00, 0x140680D70, 0x1406920F0}))
                    for displacement in (0x12E6, 0x2548, 0x382E, 0x3868):
                        self.assertEqual(body.find(struct.pack("<I", displacement)), -1)
                send = image.get_data(0x6B1298, 26)
                self.assertEqual(send[:14], bytes.fromhex("4533c9ba1101000041b802e10000"))
                self.assertEqual(send[14:18], bytes.fromhex("488b4e40"))
                self.assertEqual(send[18:20], b"\xff\x15")
                send_iat = 0x1406B12B0 + struct.unpack_from("<i", send, 20)[0]
                self.assertEqual(imports[send_iat][1], "SendMessageA")
                self.assertEqual(image.get_data(0x68DAA0, 10), bytes.fromhex("488b0148ffa018010000"))
                self.assertEqual(struct.unpack("<Q", image.get_data(0xEA3868 + 0x118, 8))[0],
                                 0x14068D9D0)
                self.assertEqual(image.get_data(0x6B18B0, 12), bytes.fromhex("4533c0418d5001e944f3ffff"))
                self.assertEqual(target_of(0x1406B18B7), 0x1406B0C00)
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_stop_command_is_a_child_button_of_the_production_view(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        library_bytes = (ROOT / "v3d_files_" / "mfc140.dll").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        self.assertEqual(hashlib.sha256(library_bytes).hexdigest(),
                         "0cf26008fae0cb61dfe49e1c3fc17e0dd860be011d9a6a64b452f56335bafbfe")
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image, pefile.PE(
                    data=library_bytes, fast_load=True) as library:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
                library.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]])
                imports = {
                    item.address: (entry.dll, item.name.decode() if item.name else None, item.ordinal)
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                text = next(section for section in image.sections if section.Name.startswith(b".text"))
                text_data = text.get_data()
                text_base = IMAGE_BASE + text.VirtualAddress

                def target_of(site: int) -> int:
                    relative = text_data[site - text_base + 1:site - text_base + 5]
                    return site + 5 + struct.unpack("<i", relative)[0]

                view_store = image.get_data(0x6AB5A2, 10)
                self.assertEqual(view_store, bytes.fromhex("488d05a7108000488907"))
                self.assertEqual(0x1406AB5A9 + struct.unpack_from("<i", view_store, 3)[0], 0x140EAC650)
                self.assertEqual(image.get_data(0x6AB630, 12), bytes.fromhex("488d8fc8090000e894feffff"))
                self.assertEqual(target_of(0x1406AB637), 0x1406AB4D0)
                command_store = image.get_data(0x6AB4EC, 10)
                self.assertEqual(command_store, bytes.fromhex("488d05ad427f00488903"))
                self.assertEqual(0x1406AB4F3 + struct.unpack_from("<i", command_store, 3)[0], 0x140E9F7A0)
                self.assertEqual(struct.unpack("<Q", image.get_data(0xE9F7A0 + 0xB8, 8))[0], 0x14077F52C)
                self.assertEqual(struct.unpack("<Q", image.get_data(0xED1D38 + 0xB8, 8))[0], 0x14077F52C)
                self.assertEqual(image.get_data(0x77F52C, 6)[:2], b"\xff\x25")
                create_iat = 0x14077F532 + struct.unpack_from("<i", image.get_data(0x77F52C, 6), 2)[0]
                self.assertEqual(imports[create_iat], (b"mfc140.dll", None, 3165))
                button_thunk = image.get_data(0x7805CA, 6)
                self.assertEqual(button_thunk[:2], b"\xff\x25")
                button_iat = 0x1407805D0 + struct.unpack_from("<i", button_thunk, 2)[0]
                self.assertEqual(imports[button_iat], (b"mfc140.dll", None, 3051))

                header, entries = struct.unpack("<QQ", image.get_data(0xE9FBE0, 16))
                self.assertEqual(entries, 0x140E9FA80)
                command = struct.unpack("<IIIIQQ", image.get_data(0xE9FAA0, 32))
                created = struct.unpack("<IIIIQQ", image.get_data(0xE9FBA0, 32))
                self.assertEqual(command, (0x111, 0, 0xB1CF, 0xB1CF, 0x3A, 0x140677B30))
                self.assertEqual(created[:1] + created[-1:], (1, 0x140677B70))
                self.assertEqual(target_of(0x140677B8E), 0x1406770B0)
                button = image.get_data(0x677217, 0x3B)
                self.assertEqual(button[:11], bytes.fromhex("c7442428cfb100004c8db3"))
                self.assertEqual(struct.unpack_from("<I", button, 11)[0], 0x1AA8)
                self.assertEqual(button[-6:], bytes.fromhex("ff90d8020000"))
                poster = image.get_data(0x677B30, 0x3D)
                self.assertEqual(poster[9:13], bytes.fromhex("488b4940"))
                self.assertEqual(poster[13:15], b"\xff\x15")
                parent_iat = 0x140677B43 + struct.unpack_from("<i", poster, 15)[0]
                self.assertEqual(imports[parent_iat], (b"USER32.dll", "GetParent", None))
                self.assertEqual(poster[34:45], bytes.fromhex("ba2c05000041b802000000"))
                self.assertEqual(poster[45:49], bytes.fromhex("488b4840"))
                self.assertEqual(poster[54:57], b"\x48\xff\x25")
                post_iat = 0x140677B6D + struct.unpack_from("<i", poster, 57)[0]
                self.assertEqual(imports[post_iat], (b"USER32.dll", "PostMessageA", None))

                self.assertEqual(image.get_data(0x6AC8A7, 3), bytes.fromhex("4c8bf1"))
                create = image.get_data(0x6AC96C, 0x47)
                self.assertEqual(create[:9], bytes.fromhex("33d2498d9ec8090000"))
                self.assertEqual(create[31:38], bytes.fromhex("4c8d05460b8000"))
                class_name = 0x1406AC992 + struct.unpack_from("<i", create, 34)[0]
                self.assertEqual(image.get_data(class_name - IMAGE_BASE, 17), b"PROD_VIEW_COMMAND")
                self.assertEqual(create[38:46], bytes.fromhex("c7442430d40b0000"))
                self.assertEqual(create[46:52], bytes.fromhex("41b900000050"))
                self.assertEqual(create[52:57], bytes.fromhex("4c89742428"))
                self.assertEqual(create[-6:], bytes.fromhex("ff90b8000000"))
                from capstone.x86 import X86_OP_REG, X86_REG_R14, X86_REG_R15, X86_REG_RSI
                decoder = Cs(CS_ARCH_X86, CS_MODE_64)
                decoder.detail = True

                def preserved(begin: int, end: int, reg: int, assigned: int) -> None:
                    seen = False
                    for ins in decoder.disasm(text_data[begin - text_base:end - text_base], begin):
                        writes = any(op.type == X86_OP_REG and op.access & CS_AC_WRITE and op.reg == reg
                                     for op in ins.operands)
                        if ins.address == assigned:
                            self.assertTrue(writes)
                            seen = True
                        elif seen and writes:
                            self.fail(f"{reg:#x} rewritten at {ins.address:#x}")
                    self.assertTrue(seen)

                preserved(0x1406AC880, 0x1406AC9B3, X86_REG_R14, 0x1406AC8A7)
                for call, owner, assigned, reg, move in (
                    (0x1406B0020, 0x1406AF770, 0x1406AF794, X86_REG_R15, bytes.fromhex("4c8bf9498bcf")),
                    (0x1406B1B0E, 0x1406B19D0, 0x1406B19F0, X86_REG_RSI, bytes.fromhex("488bf1488bce")),
                    (0x1406B1CF3, 0x1406B19D0, 0x1406B19F0, X86_REG_RSI, bytes.fromhex("488bf1488bce")),
                    (0x1406B3909, 0x1406B3760, 0x1406B3780, X86_REG_RSI, bytes.fromhex("488bf1488bce")),
                ):
                    self.assertEqual(image.get_data(assigned - IMAGE_BASE, 3), move[:3])
                    self.assertEqual(image.get_data(call - IMAGE_BASE - 3, 3), move[3:])
                    self.assertEqual(target_of(call), 0x1406AC880)
                    preserved(owner, call, reg, assigned)
                self.assertEqual(struct.unpack("<Q", image.get_data(0xEAC978, 8))[0], 0x1406AF770)

                exports = struct.unpack("<IIHHIIIIIII", library.get_data(
                    library.OPTIONAL_HEADER.DATA_DIRECTORY[0].VirtualAddress, 40))
                for ordinal, expected in (
                    (3051, bytes.fromhex(
                        "4c8bdc4883ec58498363e000448b942488000000488b01458953d8"
                        "4c8b9424800000004d8953d0488b80b80000004d894bc8458bc8"
                        "4c8bc2488d158dfa0a00ff156b6403004883c458c3")),
                    (3165, bytes.fromhex(
                        "488b8424a800000033db418bf9498be84c8bf2488bf14885c07404"
                        "488b5840488b8424a00000000fbaef1e")),
                ):
                    self.assertTrue(0 <= ordinal - exports[5] < exports[6])
                    rva = struct.unpack("<I", library.get_data(
                        exports[8] + 4 * (ordinal - exports[5]), 4))[0]
                    body = library.get_data(rva if ordinal == 3051 else rva + 0x19, len(expected))
                    self.assertEqual(body, expected)
                wrapper = library.get_data(
                    struct.unpack("<I", library.get_data(exports[8] + 4 * (3051 - exports[5]), 4))[0],
                    len(bytes.fromhex(
                        "4c8bdc4883ec58498363e000448b942488000000488b01458953d8"
                        "4c8b9424800000004d8953d0488b80b80000004d894bc8458bc8"
                        "4c8bc2488d158dfa0a00ff156b6403004883c458c3")))
                leaf = 0x18029877F + struct.unpack_from("<i", wrapper, wrapper.index(b"\x48\x8d\x15") + 3)[0]
                self.assertEqual(library.get_data(leaf - 0x180000000, 7), b"BUTTON\x00")
                dispatch = 0x180298785 + struct.unpack_from("<i", wrapper, wrapper.index(b"\xff\x15") + 2)[0]
                self.assertEqual(struct.unpack("<Q", library.get_data(dispatch - 0x180000000, 8))[0], 0x1802BF060)
                self.assertEqual(library.get_data(0x2BF060, 2), b"\xff\xe0")

                needle = struct.pack("<I", 0xB1CF)
                sites = []
                cursor = 0
                while True:
                    found = text_data.find(needle, cursor)
                    if found < 0:
                        break
                    sites.append(text_base + found)
                    cursor = found + 1
                self.assertEqual(sites, [0x14067721B, 0x140680CB3, 0x14068DA57])
                self.assertEqual(struct.unpack("<Q", image.get_data(0xEA3868 + 0x28, 8))[0], 0x14068DA40)
                notify = image.get_data(0x68DA40, 0x26)
                self.assertEqual(notify[20:33], bytes.fromhex("7538b8cfb1000066443bc0752d"))
                self.assertEqual(target_of(0x14068DA61), 0x1406920F0)
                creators = []
                for index in range(len(text_data) - 5):
                    if text_data[index] != 0xE8:
                        continue
                    if text_base + index + 5 + struct.unpack_from("<i", text_data, index + 1)[0] == 0x1406770B0:
                        creators.append(text_base + index)
                self.assertEqual(creators, [0x140677B8E])
                self.assertEqual(header, 0x140675F80)
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_close_call_closure_does_not_call_ask_to_stop(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        with pefile.PE(data=source, fast_load=True) as image:
            image.parse_data_directories(directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
            text = next(section for section in image.sections if section.Name.startswith(b".text"))
            text_data = text.get_data()
            text_base = IMAGE_BASE + text.VirtualAddress
            functions = sorted(
                (IMAGE_BASE + item.struct.BeginAddress, IMAGE_BASE + item.struct.EndAddress)
                for item in image.DIRECTORY_ENTRY_EXCEPTION)
            starts = [begin for begin, _end in functions]
            edges: dict[int, set[int]] = {}
            for index in range(len(text_data) - 5):
                if text_data[index] not in (0xE8, 0xE9):
                    continue
                site = text_base + index
                owner_index = bisect.bisect_right(starts, site) - 1
                begin, end = functions[owner_index]
                if not begin <= site < end:
                    continue
                edges.setdefault(begin, set()).add(site + 5 + struct.unpack_from("<i", text_data, index + 1)[0])
            roots = (0x14068D9D0, 0x14067FC20, 0x1406AF270, 0x1404E03F0, 0x14068DA40)
            self.assertTrue(all(root in starts for root in roots))
            closure = set()
            pending = list(roots)
            while pending:
                function = pending.pop()
                if function in closure:
                    continue
                closure.add(function)
                for dest in edges.get(function, ()):
                    dest_index = bisect.bisect_right(starts, dest) - 1
                    dest_begin, dest_end = functions[dest_index]
                    if dest_begin <= dest < dest_end and dest_begin not in closure:
                        pending.append(dest_begin)
            self.assertTrue({0x140680C00, 0x1406A1C80, 0x1406A20D0, 0x1406A1DA0,
                             0x140677B30, 0x1404C2640, 0x14075DF50, 0x140682FF0}.isdisjoint(closure))
            stop_callers = {function for function, dests in edges.items()
                            if function in closure and 0x1406920F0 in dests}
            self.assertEqual(stop_callers, {0x14068DA40})
            displacement = struct.pack("<I", 0x2548)
            command = struct.pack("<I", 0xB1CF)
            displacement_sites = []
            command_sites = []
            for begin, end in functions:
                if begin not in closure:
                    continue
                blob = text_data[begin - text_base:end - text_base]
                cursor = 0
                while True:
                    found = blob.find(displacement, cursor)
                    if found < 0:
                        break
                    displacement_sites.append(begin + found)
                    cursor = found + 1
                cursor = 0
                while True:
                    found = blob.find(command, cursor)
                    if found < 0:
                        break
                    command_sites.append(begin + found)
                    cursor = found + 1
            self.assertEqual(displacement_sites, [0x14067FC65])
            self.assertEqual(command_sites, [0x14068DA57])
            store = image.get_data(0x67FC5B, 14)
            self.assertEqual(store, bytes.fromhex("488d05f63e820048898148250000"))
            self.assertEqual(0x14067FC62 + struct.unpack_from("<i", store, 3)[0], 0x140EA3B58)
            self.assertEqual(struct.unpack("<Q", image.get_data(0xEA3B58 + 8, 8))[0], 0x140680C00)
            self.assertEqual(image.get_data(0x67FCF3, 10), bytes.fromhex("488b01418d5703ff5008"))
            self.assertEqual(image.get_data(0x67FCDE, 7), bytes.fromhex("488b8b78580000"))

    def test_view_destruction_calls_ccapm_without_ask_to_stop(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
                imports = {
                    item.address: (entry.dll.lower(), item.name.decode() if item.name else None, item.ordinal)
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                text = next(section for section in image.sections if section.Name.startswith(b".text"))
                text_data = text.get_data()
                text_base = IMAGE_BASE + text.VirtualAddress

                def target_of(site: int) -> int:
                    return site + 5 + struct.unpack_from("<i", text_data, site - text_base + 1)[0]

                def rip_target(site: int) -> int:
                    return site + 7 + struct.unpack_from("<i", text_data, site - text_base + 3)[0]

                self.assertEqual(image.get_data(0x6AF2CB, 33), bytes.fromhex(
                    "488b86e80000008b8824390000894c2440c74424440b000000c744244c01000000"))
                self.assertEqual(target_of(0x1406AF2EC), 0x14077F7F6)
                state_thunk = image.get_data(0x77F7F6, 6)
                self.assertEqual(state_thunk[:2], b"\xff\x25")
                state_iat = 0x14077F7FC + struct.unpack_from("<i", state_thunk, 2)[0]
                self.assertEqual(imports[state_iat], (b"mfc140.dll", None, 2207))
                self.assertEqual(image.get_data(0x6AF2F1, 20), bytes.fromhex(
                    "896c24204c8d0df45da2004c8d05cd5da20033d2"))
                self.assertEqual(image.get_data(rip_target(0x1406AF2F5) - IMAGE_BASE + 0x10, 17),
                                 b".?AVCAVisionApp@@")
                self.assertEqual(image.get_data(rip_target(0x1406AF2FC) - IMAGE_BASE + 0x10, 13),
                                 b".?AVCWinApp@@")
                self.assertEqual(image.get_data(0x6AF305, 4), bytes.fromhex("488b4808"))
                self.assertEqual(target_of(0x1406AF309), 0x1407A6238)
                cast_thunk = image.get_data(0x7A6238, 6)
                self.assertEqual(cast_thunk[:2], b"\xff\x25")
                cast_iat = 0x1407A623E + struct.unpack_from("<i", cast_thunk, 2)[0]
                self.assertEqual(imports[cast_iat][1], "__RTDynamicCast")
                self.assertEqual(image.get_data(0x6AF30E, 45), bytes.fromhex(
                    "488d90a8010000488d88b00100004885d2480f44cd48896c2470488b01"
                    "4c8d442470488d542438ff9098010000"))
                self.assertEqual(struct.unpack("<Q", image.get_data(0xEDDBD0 + 0x198, 8))[0], 0x14075D6B0)
                self.assertEqual(struct.unpack("<Q", image.get_data(0xEDDBD0 + 0xE0, 8))[0], 0x14075D010)
                self.assertEqual(image.get_data(0x75D010, 0x28), bytes.fromhex(
                    "488b81f0020000482b81e802000048c1f8033bd07d0f488b81e80200004863d2488b04d0c333c0c3"))
                self.assertEqual(image.get_data(0x75D709, 37), bytes.fromhex(
                    "488b068b5308488bceff90e00000004885c00f842504000083b828390000040f8518040000"))
                self.assertEqual(0x14075D721 + struct.unpack_from("<i", image.get_data(0x75D71D, 4), 0)[0],
                                 0x14075DB46)
                self.assertEqual(0x14075D72E + struct.unpack_from("<i", image.get_data(0x75D72A, 4), 0)[0],
                                 0x14075DB46)
                self.assertEqual(image.get_data(0x75DB46, 19), bytes.fromhex(
                    "488d8e700200004d8bc6488d55d8e8b73eebff"))
                self.assertEqual(target_of(0x14075DB54), 0x140611A10)
                self.assertEqual(image.get_data(0x611A10, 0x21), bytes.fromhex(
                    "4883ec284d8bc84883c1084c8bc2488d15dbfbffffe8c6efffffb0014883c428c3"))
                self.assertEqual(target_of(0x140611A25), 0x1406109F0)
                self.assertEqual(image.get_data(0x610A1B, 4), bytes.fromhex("4883c120"))
                enter = image.get_data(0x610A1F, 6)
                self.assertEqual(enter[:2], b"\xff\x15")
                self.assertEqual(imports[0x140610A25 + struct.unpack_from("<i", enter, 2)[0]][:2],
                                 (b"kernel32.dll", "EnterCriticalSection"))
                self.assertEqual(image.get_data(0x610ABE, 16), bytes.fromhex(
                    "488b5d10482b5d0848c1fb03488d4d20"))
                leave = image.get_data(0x610ACE, 6)
                self.assertEqual(leave[:2], b"\xff\x15")
                self.assertEqual(imports[0x140610AD4 + struct.unpack_from("<i", leave, 2)[0]][:2],
                                 (b"kernel32.dll", "LeaveCriticalSection"))
                member = image.get_data(0x6109F0, 0x140610AEF - 0x1406109F0)
                self.assertEqual(member.find(struct.pack("<I", 0x2548)), -1)
                self.assertEqual(member.find(struct.pack("<I", 0xB1CF)), -1)
                self.assertEqual(image.get_data(0x4CE018, 31), bytes.fromhex(
                    "488d0551b79600488907488d8f78010000ff15e110890090488d8fa8010000"))
                self.assertEqual(0x1404CE01F + struct.unpack_from("<i", image.get_data(0x4CE018, 7), 3)[0],
                                 0x140E39770)
                self.assertEqual(target_of(0x1404CE037), 0x14075AA80)
                functions = sorted(
                    (IMAGE_BASE + item.struct.BeginAddress, IMAGE_BASE + item.struct.EndAddress)
                    for item in image.DIRECTORY_ENTRY_EXCEPTION)
                starts = [begin for begin, _end in functions]
                edges: dict[int, set[int]] = {}
                for index in range(len(text_data) - 5):
                    if text_data[index] not in (0xE8, 0xE9):
                        continue
                    site = text_base + index
                    owner_index = bisect.bisect_right(starts, site) - 1
                    begin, end = functions[owner_index]
                    if not begin <= site < end:
                        continue
                    edges.setdefault(begin, set()).add(
                        site + 5 + struct.unpack_from("<i", text_data, index + 1)[0])
                closure = set()
                pending = [0x14075D6B0]
                while pending:
                    function = pending.pop()
                    if function in closure:
                        continue
                    closure.add(function)
                    for dest in edges.get(function, ()):
                        dest_index = bisect.bisect_right(starts, dest) - 1
                        dest_begin, dest_end = functions[dest_index]
                        if dest_begin <= dest < dest_end and dest_begin not in closure:
                            pending.append(dest_begin)
                self.assertIn(0x140611A10, closure)
                self.assertIn(0x1406109F0, closure)
                self.assertTrue({0x140680C00, 0x1406920F0, 0x1404C2640, 0x1406A20D0}.isdisjoint(closure))
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_view_destruction_notifies_vmc_listener_without_stopping(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
                imports = {
                    item.address: (entry.dll.lower(), item.name.decode() if item.name else None, item.ordinal)
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                text = next(section for section in image.sections if section.Name.startswith(b".text"))
                text_data = text.get_data()
                text_base = IMAGE_BASE + text.VirtualAddress

                def target_of(site: int) -> int:
                    return site + 5 + struct.unpack_from("<i", text_data, site - text_base + 1)[0]

                def iat_of(site: int) -> int:
                    return site + 6 + struct.unpack_from("<i", text_data, site - text_base + 2)[0]

                listener_lea = image.get_data(0x6AB5AC, 14)
                self.assertEqual(listener_lea, bytes.fromhex("488d052d14800048898760010000"))
                listener_vtable = 0x1406AB5B3 + struct.unpack_from("<i", listener_lea, 3)[0]
                self.assertEqual(listener_vtable, 0x140EAC9E0)
                locator = struct.unpack("<Q", image.get_data(listener_vtable - IMAGE_BASE - 8, 8))[0]
                self.assertEqual(locator, 0x140F13CD0)
                signature, offset, _cd_offset, descriptor, hierarchy, _self_rva = struct.unpack(
                    "<6I", image.get_data(locator - IMAGE_BASE, 24))
                self.assertEqual((signature, offset), (1, 0x160))
                self.assertEqual(image.get_string_at_rva(descriptor + 16), b".?AVCProductionView@@")
                base_count, base_array = struct.unpack("<II", image.get_data(hierarchy + 8, 8))
                listener_bases = []
                for index in range(base_count):
                    base = struct.unpack("<I", image.get_data(base_array + index * 4, 4))[0]
                    type_rva, _contained, member = struct.unpack("<III", image.get_data(base, 12))
                    listener_bases.append((image.get_string_at_rva(type_rva + 16), member))
                self.assertIn((b".?AVIVMachineControllerListener@@", 0x160), listener_bases)
                for slot in (0, 8, 0x10, 0x28, 0x30, 0x38):
                    self.assertEqual(
                        struct.unpack("<Q", image.get_data(listener_vtable - IMAGE_BASE + slot, 8))[0],
                        0x140611CE0)
                self.assertEqual(image.get_data(0x611CE0, 3), b"\x32\xc0\xc3")
                self.assertEqual(
                    struct.unpack("<Q", image.get_data(listener_vtable - IMAGE_BASE + 0x40, 8))[0],
                    0x1406B2CB0)
                self.assertEqual(image.get_data(0x6B2CB0, 7), bytes.fromhex("44894158b001c3"))
                self.assertEqual(
                    struct.unpack("<Q", image.get_data(listener_vtable - IMAGE_BASE + 0x18, 8))[0],
                    0x140746700)
                self.assertEqual(imports[iat_of(0x140746707)][:2], (b"mfc140.dll", None))
                self.assertEqual(imports[iat_of(0x140746707)][2], 1032)
                self.assertEqual(
                    struct.unpack("<Q", image.get_data(listener_vtable - IMAGE_BASE + 0x20, 8))[0],
                    0x140611CC0)
                self.assertEqual(target_of(0x140611CC7), 0x1405586B0)

                self.assertEqual(
                    struct.unpack("<Q", image.get_data(0xEA3868 + 0x230, 8))[0], 0x14045C520)
                self.assertEqual(image.get_data(0x45C520, 8), bytes.fromhex("488b81e8190000c3"))
                self.assertEqual(image.get_data(0x540E58, 7), bytes.fromhex("488991e8190000"))
                for site, import_name in (
                        (0x14069730F, "GetCurrent"),
                        (0x14069739F, "GetByLaneIndex"),
                        (0x140697430, "GetCurrent")):
                    imported = imports[iat_of(site)]
                    self.assertEqual(imported[0], b"vivirtualmachinebuilder.dll")
                    self.assertIn(import_name, imported[1])
                    self.assertEqual(target_of(site + 12), 0x140540E40)

                self.assertEqual(image.get_data(0x6AF2DC, 8), bytes.fromhex("c74424440b000000"))
                self.assertEqual(image.get_data(0x75D6E9, 6), bytes.fromhex("8b430c8945e4"))
                decoder = Cs(CS_ARCH_X86, CS_MODE_64)
                inserted = []
                for insn in decoder.disasm(text_data[0x14075D72E - text_base:0x14075DA87 - text_base], 0x14075D72E):
                    if insn.mnemonic == "mov" and insn.op_str.startswith("dword ptr [rbp + 0x30],"):
                        inserted.append(int(insn.op_str.rsplit(", ", 1)[1], 16))
                self.assertEqual(inserted, [5, 6, 7, 8, 0xA, 0xD, 0xE, 0xF, 0x10, 0x12, 0x19, 3, 0xB])
                self.assertEqual(0x14075DAEB + text_data[0x14075DAEA - text_base], 0x14075DB5A)
                self.assertEqual(target_of(0x14075DB54), 0x140611A10)
                self.assertLess(0x14075DB54, 0x14075DB5A)

                self.assertEqual(image.get_data(0x6AF847, 47), bytes.fromhex(
                    "498b8fe8000000488b01ff90300200004c8b00498d9760010000488bc8"
                    "41ff50084d8bafe80000004d89bd38580000"))
                self.assertEqual(image.get_data(0x6AF39E, 54), bytes.fromhex(
                    "488b8ee8000000488b01ff90300200004885c07421488b8ee8000000"
                    "488b01ff90300200004c8b00488d9660010000488bc841ff5010"))
                self.assertEqual(imports[iat_of(0x14077FF6A)][:2], (b"mfc140.dll", None))
                self.assertEqual(imports[iat_of(0x14077FF6A)][2], 357)
                self.assertEqual(image.get_data(0x6AF34D, 8), bytes.fromhex("488b01ba01000000"))
                self.assertEqual(image.get_data(0x6AF355, 3), bytes.fromhex("ff5008"))

                functions = sorted(
                    (IMAGE_BASE + item.struct.BeginAddress, IMAGE_BASE + item.struct.EndAddress)
                    for item in image.DIRECTORY_ENTRY_EXCEPTION)
                starts = [begin for begin, _end in functions]
                edges: dict[int, set[int]] = {}
                for index in range(len(text_data) - 5):
                    if text_data[index] not in (0xE8, 0xE9):
                        continue
                    site = text_base + index
                    owner_index = bisect.bisect_right(starts, site) - 1
                    begin, end = functions[owner_index]
                    if not begin <= site < end:
                        continue
                    edges.setdefault(begin, set()).add(
                        site + 5 + struct.unpack_from("<i", text_data, index + 1)[0])
                closure = set()
                pending = [0x140611CC0, 0x140746700, 0x1405586B0, 0x1406B2CB0]
                while pending:
                    function = pending.pop()
                    owner_index = bisect.bisect_right(starts, function) - 1
                    begin, end = functions[owner_index]
                    if not begin <= function < end or begin in closure:
                        continue
                    closure.add(begin)
                    body = text_data[begin - text_base:end - text_base]
                    self.assertEqual(body.find(struct.pack("<I", 0x2548)), -1)
                    self.assertEqual(body.find(struct.pack("<I", 0x382E)), -1)
                    self.assertEqual(body.find(struct.pack("<I", 0xB1CF)), -1)
                    for dest in edges.get(begin, ()):
                        pending.append(dest)
                self.assertTrue({0x140680C00, 0x1406920F0, 0x1406A1C80, 0x1406A20D0}.isdisjoint(closure))
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_destroy_vmc_slot_detaches_listener_without_stopping(self) -> None:
        builder_hash = "5e808e294d1f19fa7b8bd5e2d994d4820963d5c1fdea064e572457c9597679b7"
        machine_hash = "5b62adea102b62a272860bfba72cb787bf74bd006f44fe97453df5121efeeb60"
        builder = (ROOT / "v3d_files_" / "ViVirtualMachineBuilder.dll").read_bytes()
        machine = (ROOT / "v3d_files_" / "ViVirtualMachine.dll").read_bytes()
        self.assertEqual(len(builder), 1013248)
        self.assertEqual(len(machine), 1144320)
        self.assertEqual(hashlib.sha256(builder).hexdigest(), builder_hash)
        self.assertEqual(hashlib.sha256(machine).hexdigest(), machine_hash)
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=builder, fast_load=True) as image:
                self.assertEqual(image.FILE_HEADER.Machine, 0x8664)
                self.assertEqual(image.OPTIONAL_HEADER.Magic, 0x20B)
                self.assertEqual(image.OPTIONAL_HEADER.ImageBase, 0x180000000)
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                imports = {
                    item.address: (entry.dll.lower(), item.name.decode() if item.name else None)
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                thunk = image.get_data(0x75A3C, 6)
                self.assertEqual(thunk, bytes.fromhex("ff2546cf0200"))
                iat = 0x180075A42 + struct.unpack_from("<i", thunk, 2)[0]
                self.assertEqual(
                    imports[iat],
                    (b"vivirtualmachine.dll", "??0CVMachineController@@QEAA@I@Z"))
            with pefile.PE(data=machine, fast_load=True) as image:
                self.assertEqual(image.FILE_HEADER.Machine, 0x8664)
                self.assertEqual(image.OPTIONAL_HEADER.Magic, 0x20B)
                self.assertEqual(image.OPTIONAL_HEADER.ImageBase, 0x180000000)
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                imports = {
                    item.address: (entry.dll.lower(), item.name.decode() if item.name else None, item.ordinal)
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                base = 0x180000000
                text = next(section for section in image.sections if section.Name.startswith(b".text"))
                text_data = text.get_data()
                text_base = base + text.VirtualAddress
                constructor = image.get_data(0x689A4, 3)
                self.assertEqual(constructor, b"\x48\x8b\xf1")
                store = image.get_data(0x689D5, 10)
                self.assertEqual(store[:3], b"\x48\x8d\x05")
                self.assertEqual(store[7:], b"\x48\x89\x06")
                vtable = 0x1800689DC + struct.unpack_from("<i", store, 3)[0]
                self.assertEqual(vtable, 0x1800CEDA8)
                self.assertEqual(struct.unpack("<Q", image.get_data(vtable - base + 8, 8))[0], 0x18006EA00)
                self.assertEqual(struct.unpack("<Q", image.get_data(vtable - base + 0x10, 8))[0], 0x1800547B0)
                locator = struct.unpack("<Q", image.get_data(vtable - base - 8, 8))[0]
                signature, offset, _cd_offset, descriptor, _hierarchy, _self_rva = struct.unpack(
                    "<6I", image.get_data(locator - base, 24))
                self.assertEqual((signature, offset), (1, 0))
                self.assertEqual(image.get_string_at_rva(descriptor + 16), b".?AVCVMachineController@@")
                detach = image.get_data(0x547B0, 0x8E)
                self.assertEqual(detach, bytes.fromhex(
                    "48895c24104889742418574883ec204032ff488bda488bf14885d2745d"
                    "4883c12048896c2430ff156c5f0600488b4610488b4e08483bc874320f"
                    "1f800000000048391974094883c108483bc875f2483bc87418488d5108"
                    "4c8bc04c2bc2ff152561060048834610f840b701488d4e20ff151b5f06"
                    "00488b6c2430488b5c2438400fb6c7488b7424404883c4205fc3"))
                calls = []
                for index in range(len(detach) - 6):
                    if detach[index:index + 2] != b"\xff\x15":
                        continue
                    site = 0x1800547B0 + index
                    iat = site + 6 + struct.unpack_from("<i", detach, index + 2)[0]
                    calls.append(imports[iat][:2])
                self.assertEqual(calls, [
                    (b"kernel32.dll", "EnterCriticalSection"),
                    (b"vcruntime140.dll", "memmove"),
                    (b"kernel32.dll", "LeaveCriticalSection"),
                ])
                self.assertEqual(detach.find(b"\xe8"), -1)
                attach = text_data[0x18006EA20 - text_base:0x18006EA27 - text_base]
                self.assertEqual(attach[:3], b"\x48\xff\x25")
                attach_iat = 0x18006EA27 + struct.unpack_from("<i", attach, 3)[0]
                self.assertEqual(imports[attach_iat][:2], (b"kernel32.dll", "QueueUserWorkItem"))
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_destroy_brush_destructor_does_not_stop_production(self) -> None:
        mfc_hash = "0cf26008fae0cb61dfe49e1c3fc17e0dd860be011d9a6a64b452f56335bafbfe"
        library_bytes = (ROOT / "v3d_files_" / "mfc140.dll").read_bytes()
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(len(library_bytes), 5784856)
        self.assertEqual(hashlib.sha256(library_bytes).hexdigest(), mfc_hash)
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=library_bytes, fast_load=True) as library, pefile.PE(
                    data=source, fast_load=True) as image:
                self.assertEqual(library.OPTIONAL_HEADER.ImageBase, 0x180000000)
                library.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                library_imports = {
                    item.address: (entry.dll.lower(), item.name.decode() if item.name else None)
                    for entry in library.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                exe_imports = {
                    item.address: (entry.dll.lower(), item.name.decode() if item.name else None, item.ordinal)
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                directory = library.OPTIONAL_HEADER.DATA_DIRECTORY[0]
                exports = struct.unpack("<IIHHIIIIIII", library.get_data(directory.VirtualAddress, 40))
                ordinal_base, count, _names, table = exports[5:9]
                constructor_rva = struct.unpack(
                    "<I", library.get_data(table + (357 - ordinal_base) * 4, 4))[0]
                self.assertEqual(constructor_rva, 0x2A8EA0)
                constructor = library.get_data(0x2A8EB6, 23)
                self.assertEqual(constructor[:5], bytes.fromhex("4883610800"))
                self.assertEqual(constructor[5:8], b"\x48\x8d\x05")
                self.assertEqual(constructor[12:15], b"\x48\x89\x01")
                self.assertEqual(constructor[15:17], b"\x8b\xca")
                self.assertEqual(constructor[17:19], b"\xff\x15")
                vtable = 0x1802A8EC2 + struct.unpack_from("<i", constructor, 8)[0]
                self.assertEqual(vtable, 0x1802E4778)
                brush_iat = 0x1802A8ECD + struct.unpack_from("<i", constructor, 19)[0]
                self.assertEqual(library_imports[brush_iat], (b"gdi32.dll", "CreateSolidBrush"))
                locator = struct.unpack("<Q", library.get_data(vtable - 0x180000000 - 8, 8))[0]
                signature, offset, _cd_offset, descriptor, _hierarchy, _self_rva = struct.unpack(
                    "<6I", library.get_data(locator - 0x180000000, 24))
                self.assertEqual((signature, offset), (1, 0))
                self.assertEqual(library.get_string_at_rva(descriptor + 16), b".?AVCBrush@@")
                self.assertEqual(
                    struct.unpack("<Q", library.get_data(vtable - 0x180000000 + 8, 8))[0],
                    0x1802B4990)
                branch = library.get_data(0x2B49AE, 10)
                self.assertEqual(branch, bytes.fromhex("8bf283e601f6c2027436"))
                self.assertEqual(0x1802B49B8 + branch[9], 0x1802B49EE)
                delete_call = library.get_data(0x2B49F8, 5)
                self.assertEqual(delete_call[0], 0xE8)
                self.assertEqual(
                    0x1802B49FD + struct.unpack_from("<i", delete_call, 1)[0], 0x18001CD80)
                free_call = library.get_data(0x2B4A0B, 6)
                self.assertEqual(free_call[:2], b"\xff\x15")
                free_iat = 0x1802B4A11 + struct.unpack_from("<i", free_call, 2)[0]
                self.assertEqual(
                    library_imports[free_iat],
                    (b"api-ms-win-crt-heap-l1-1-0.dll", "free"))
                base_vtable = library.get_data(0x1CDA2, 7)
                self.assertEqual(base_vtable[:3], b"\x48\x8d\x05")
                gdi_vtable = 0x18001CDA9 + struct.unpack_from("<i", base_vtable, 3)[0]
                gdi_locator = struct.unpack("<Q", library.get_data(gdi_vtable - 0x180000000 - 8, 8))[0]
                _signature, gdi_offset, _cd_offset, gdi_descriptor, _hierarchy, _self_rva = struct.unpack(
                    "<6I", library.get_data(gdi_locator - 0x180000000, 24))
                self.assertEqual(gdi_offset, 0)
                self.assertEqual(library.get_string_at_rva(gdi_descriptor + 16), b".?AVCGdiObject@@")
                detach_call = library.get_data(0x2A8DA2, 5)
                self.assertEqual(detach_call[0], 0xE8)
                self.assertEqual(
                    0x1802A8DA7 + struct.unpack_from("<i", detach_call, 1)[0], 0x1802A8D40)
                delete_jump = library.get_data(0x2A8DAE, 7)
                self.assertEqual(delete_jump[:3], b"\x48\xff\x25")
                delete_iat = 0x1802A8DB5 + struct.unpack_from("<i", delete_jump, 3)[0]
                self.assertEqual(library_imports[delete_iat], (b"gdi32.dll", "DeleteObject"))
                free_ordinal = struct.unpack(
                    "<I", library.get_data(table + (1487 - ordinal_base) * 4, 4))[0]
                self.assertEqual(free_ordinal, 0x3490)
                self.assertEqual(library.get_data(0x3490, 3), b"\x48\xff\x25")

                base = 0x180000000
                text = next(section for section in library.sections if section.Name.startswith(b".text"))
                text_data = text.get_data()
                text_base = base + text.VirtualAddress
                functions = sorted(
                    (base + item.struct.BeginAddress, base + item.struct.EndAddress)
                    for item in library.DIRECTORY_ENTRY_EXCEPTION)
                starts = [begin for begin, _end in functions]
                edges: dict[int, set[int]] = {}
                for index in range(len(text_data) - 5):
                    if text_data[index] not in (0xE8, 0xE9):
                        continue
                    site = text_base + index
                    owner_index = bisect.bisect_right(starts, site) - 1
                    begin, end = functions[owner_index]
                    if not begin <= site < end:
                        continue
                    edges.setdefault(begin, set()).add(
                        site + 5 + struct.unpack_from("<i", text_data, index + 1)[0])
                imported_names = set()
                closure = set()
                pending = [0x1802B4990]
                while pending:
                    function = pending.pop()
                    owner_index = bisect.bisect_right(starts, function) - 1
                    begin, end = functions[owner_index]
                    if not begin <= function < end or begin in closure:
                        continue
                    closure.add(begin)
                    body = text_data[begin - text_base:end - text_base]
                    for index in range(len(body) - 6):
                        site = begin + index
                        if body[index:index + 2] == b"\xff\x15":
                            iat = site + 6 + struct.unpack_from("<i", body, index + 2)[0]
                            imported = library_imports.get(iat)
                            if imported is None:
                                slot = struct.unpack("<Q", library.get_data(iat - base, 8))[0]
                                self.assertEqual(library.get_data(slot - base, 2), b"\xff\xe0")
                            else:
                                imported_names.add(imported)
                        elif body[index:index + 3] == b"\x48\xff\x25":
                            iat = site + 7 + struct.unpack_from("<i", body, index + 3)[0]
                            imported_names.add(library_imports[iat])
                    for dest in edges.get(begin, ()):
                        pending.append(dest)
                self.assertIn((b"gdi32.dll", "DeleteObject"), imported_names)
                self.assertIn((b"api-ms-win-crt-heap-l1-1-0.dll", "free"), imported_names)
                self.assertTrue(all(dll != b"user32.dll" for dll, _name in imported_names))

                exe_text = next(section for section in image.sections if section.Name.startswith(b".text"))
                exe_data = exe_text.get_data()
                exe_base = IMAGE_BASE + exe_text.VirtualAddress

                def exe_target(site: int) -> int:
                    return site + 5 + struct.unpack_from("<i", exe_data, site - exe_base + 1)[0]

                def exe_iat(site: int) -> int:
                    return site + 6 + struct.unpack_from("<i", exe_data, site - exe_base + 2)[0]

                self.assertEqual(image.get_data(0x6AF2A2, 2), b"\x33\xed")
                self.assertEqual(image.get_data(0x6AF384, 3), b"\x48\x89\x2b")
                self.assertEqual(exe_imports[exe_iat(0x14077FF6A)][2], 357)
                self.assertEqual(image.get_data(0x6AF876, 3), b"\x45\x33\xf6")
                stores = []
                colors = []
                sys_colors = []
                recent = []
                for insn in Cs(CS_ARCH_X86, CS_MODE_64).disasm(
                        exe_data[0x1406AF876 - exe_base:0x1406AFAC0 - exe_base], 0x1406AF876):
                    recent.append(insn)
                    del recent[:-4]
                    if insn.mnemonic == "mov" and insn.op_str.startswith("qword ptr [r15 + 0x60"):
                        stores.append(insn.op_str)
                    if insn.mnemonic == "call" and exe_target(insn.address) == 0x14077FF6A:
                        setup = [item.op_str for item in recent[:-1]]
                        if "edx, eax" in setup:
                            sys_colors.append(insn.address)
                        else:
                            colors.append(next(
                                int(item.op_str.split(", ", 1)[1], 16)
                                for item in recent if item.op_str.startswith("edx, 0x")))
                self.assertEqual(colors, [0x2922C4, 0x628E2C, 0x2DEBF4, 0xDCDCDC, 0xFFFFFF, 0xFFFFFF])
                self.assertEqual(sys_colors, [0x1406AF9D2, 0x1406AFA0C, 0x1406AFA46, 0x1406AFAAF])
                for site in (0x1406AF9C7, 0x1406AFA01, 0x1406AFA3B, 0x1406AFAA4):
                    self.assertEqual(exe_imports[exe_iat(site)][:2], (b"user32.dll", "GetSysColor"))
                self.assertEqual(stores, [
                    "qword ptr [r15 + 0x60b0], r14",
                    "qword ptr [r15 + 0x60b8], r14",
                    "qword ptr [r15 + 0x60c0], r14",
                    "qword ptr [r15 + 0x60c8], r14",
                    "qword ptr [r15 + 0x60d0], r14",
                    "qword ptr [r15 + 0x60c8], rax",
                    "qword ptr [r15 + 0x60b8], rax",
                    "qword ptr [r15 + 0x60c0], rax",
                    "qword ptr [r15 + 0x60b0], rax",
                    "qword ptr [r15 + 0x60d0], rax",
                    "qword ptr [r15 + 0x60d8], r14",
                    "qword ptr [r15 + 0x60e0], r14",
                    "qword ptr [r15 + 0x60e8], r14",
                    "qword ptr [r15 + 0x60f0], r14",
                    "qword ptr [r15 + 0x60f8], r14",
                    "qword ptr [r15 + 0x60d8], rax",
                    "qword ptr [r15 + 0x60e0], rax",
                    "qword ptr [r15 + 0x60e8], rax",
                    "qword ptr [r15 + 0x60f0], rax",
                    "qword ptr [r15 + 0x60f8], rax",
                ])
                self.assertEqual(exe_imports[exe_iat(0x1406AF398)][:2], (b"user32.dll", "KillTimer"))
                self.assertEqual(exe_imports[exe_iat(0x14077FBB0)][2], 9117)
                self.assertEqual(exe_imports[exe_iat(0x14077F4AE)][2], 1487)
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_production_document_allocation_frees_after_array_release(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        library_bytes = (ROOT / "v3d_files_" / "mfc140.dll").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        self.assertEqual(
            hashlib.sha256(library_bytes).hexdigest(),
            "0cf26008fae0cb61dfe49e1c3fc17e0dd860be011d9a6a64b452f56335bafbfe")
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image, pefile.PE(
                    data=library_bytes, fast_load=True) as library:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                library.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                exe_imports = {
                    item.address: (entry.dll.lower(), item.name.decode() if item.name else None, item.ordinal)
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                library_imports = {
                    item.address: (entry.dll.lower(), item.name.decode() if item.name else None)
                    for entry in library.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                name, size, schema, factory = struct.unpack(
                    "<QIIQ", image.get_data(0xEA3830, 24))
                self.assertEqual(image.get_string_at_rva(name - IMAGE_BASE), b"CProductionDoc")
                self.assertEqual((size, schema, factory), (0x61F8, 0xFFFF, 0x140684F40))
                pointer = struct.pack("<Q", factory)
                holders = []
                for section in image.sections:
                    data = section.get_data()
                    start = 0
                    while True:
                        found = data.find(pointer, start)
                        if found < 0:
                            break
                        holders.append(IMAGE_BASE + section.VirtualAddress + found)
                        start = found + 1
                self.assertEqual(holders, [0x140EA3840])
                text = next(section for section in image.sections if section.Name.startswith(b".text"))
                text_data = text.get_data()
                text_base = IMAGE_BASE + text.VirtualAddress
                callers = []
                for index in range(len(text_data) - 5):
                    if text_data[index] != 0xE8:
                        continue
                    site = text_base + index
                    if site + 5 + struct.unpack_from("<i", text_data, index + 1)[0] == factory:
                        callers.append(site)
                self.assertEqual(callers, [])
                self.assertEqual(image.get_data(0x684F4D, 5), bytes.fromhex("b9f8610000"))
                self.assertEqual(
                    0x140684F57 + struct.unpack_from("<i", image.get_data(0x684F53, 4), 0)[0],
                    0x14076D550)
                self.assertEqual(image.get_data(0x684F5C, 3), b"\x48\x85\xc0")
                self.assertEqual(image.get_data(0x684F5F, 2), b"\x74\x0b")
                self.assertEqual(
                    0x140684F69 + struct.unpack_from("<i", image.get_data(0x684F65, 4), 0)[0],
                    0x14067DEA0)
                self.assertEqual(image.get_data(0x684F6C, 2), b"\x33\xc0")
                allocator = image.get_data(0x76D559, 6)
                self.assertEqual(allocator[:2], b"\xff\x15")
                allocator_iat = 0x14076D55F + struct.unpack_from("<i", allocator, 2)[0]
                self.assertEqual(
                    exe_imports[allocator_iat][:2],
                    (b"api-ms-win-crt-heap-l1-1-0.dll", "malloc"))
                self.assertEqual(image.get_data(0x51E15D, 12), bytes.fromhex(
                    "488d8ee0230000e85d1c2600"))
                self.assertEqual(exe_imports[0x140000000 + 0x77FDC6 + 6 + struct.unpack_from(
                    "<i", image.get_data(0x77FDC8, 4), 0)[0]][2], 973)
                self.assertEqual(image.get_data(0x51FD33, 12), bytes.fromhex(
                    "488d8fe0230000e899002600"))
                self.assertEqual(exe_imports[0x140000000 + 0x77FDD8 + 6 + struct.unpack_from(
                    "<i", image.get_data(0x77FDDA, 4), 0)[0]][2], 1439)
                self.assertEqual(
                    0x1406807F4 + struct.unpack_from("<i", image.get_data(0x6807F0, 4), 0)[0],
                    0x14067FC20)
                self.assertEqual(image.get_data(0x6807F4, 6), bytes.fromhex("40f6c7017426"))
                self.assertEqual(exe_imports[0x140000000 + 0x77F4AE + 6 + struct.unpack_from(
                    "<i", image.get_data(0x77F4B0, 4), 0)[0]][2], 1487)
                self.assertEqual(
                    struct.unpack("<Q", image.get_data(0xEA3868 + 8, 8))[0], 0x1406807E0)
                directory = library.OPTIONAL_HEADER.DATA_DIRECTORY[0]
                exports = struct.unpack("<IIHHIIIIIII", library.get_data(directory.VirtualAddress, 40))
                ordinal_base, _count, _names, table = exports[5:9]
                self.assertEqual(
                    struct.unpack("<I", library.get_data(table + (973 - ordinal_base) * 4, 4))[0],
                    0x1D8230)
                self.assertEqual(library.get_data(0x1D823A, 22), bytes.fromhex(
                    "33c048894108488941204889411848894110488bc1c3"))
                array_vtable = 0x1801D8237 + struct.unpack_from("<i", library.get_data(0x1D8233, 4), 0)[0]
                locator = struct.unpack("<Q", library.get_data(array_vtable - 0x180000000 - 8, 8))[0]
                signature, offset, _cd_offset, descriptor, _hierarchy, _self_rva = struct.unpack(
                    "<6I", library.get_data(locator - 0x180000000, 24))
                self.assertEqual((signature, offset), (1, 0))
                self.assertEqual(library.get_string_at_rva(descriptor + 16), b".?AVCUIntArray@@")
                self.assertEqual(
                    struct.unpack("<I", library.get_data(table + (1439 - ordinal_base) * 4, 4))[0],
                    0x1D8250)
                release = library.get_data(0x1D825A, 11)
                self.assertEqual(release[:4], bytes.fromhex("488b4908"))
                self.assertEqual(release[4:7], b"\x48\xff\x25")
                release_iat = 0x1801D8265 + struct.unpack_from("<i", release, 7)[0]
                self.assertEqual(
                    library_imports[release_iat],
                    (b"api-ms-win-crt-heap-l1-1-0.dll", "free"))
                self.assertEqual(library.get_data(0x21F964, 12), bytes.fromhex(
                    "ba01000000488bcb488b4008"))
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_document_destructor_clears_published_slot_before_free(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        with pefile.PE(data=source, fast_load=True) as image:
            self.assertEqual(struct.unpack("<Q", image.get_data(0xEDDBD0 + 0xE0, 8))[0], 0x14075D010)
            self.assertEqual(struct.unpack("<Q", image.get_data(0xEDDBD0 + 0xE8, 8))[0], 0x14075D040)
            self.assertEqual(image.get_data(0x75D056, 14), bytes.fromhex("488b81e80200004863d24c8904d0"))
            self.assertEqual(image.get_data(0x75D064, 3), bytes.fromhex("b001c3"))
            self.assertEqual(image.get_data(0x6A1612, 7), bytes.fromhex("8b93c00e000048"))
            self.assertEqual(image.get_data(0x6A1629, 7), bytes.fromhex("48ffa0e0000000"))
            self.assertEqual(image.get_data(0x6972D9, 3), b"\x83\xfe\x02")
            low_branch = image.get_data(0x6972DC, 6)
            self.assertEqual(low_branch[:2], b"\x0f\x8e")
            self.assertEqual(0x1406972E2 + struct.unpack_from("<i", low_branch, 2)[0], 0x14069738B)
            self.assertEqual(image.get_data(0x6972EE, 15), bytes.fromhex("4c8bc78d56fd498bceff90e8000000"))
            self.assertEqual(image.get_data(0x6972FD, 9), bytes.fromhex("8d46fd898724390000"))
            self.assertEqual(image.get_data(0x69738B, 9), bytes.fromhex("8d46ff898724390000"))
            self.assertEqual(image.get_data(0x6973B3, 12), bytes.fromhex("4c8bc78b9724390000498bce"))
            self.assertEqual(image.get_data(0x6973BF, 6), bytes.fromhex("ff90e8000000"))
            self.assertEqual(image.get_data(0x691FF8, 9), bytes.fromhex("8b9624390000488bc8"))
            self.assertEqual(
                0x140692006 + struct.unpack_from("<i", image.get_data(0x692002, 4), 0)[0],
                0x1406A9890)
            self.assertLess(0x140692001, 0x14069201B)
            self.assertEqual(image.get_data(0x6A98A4, 2), b"\x8b\xfa")
            equal_skip = image.get_data(0x6A98F6, 12)
            self.assertEqual(equal_skip[:6], bytes.fromhex("39bbc00e0000"))
            self.assertEqual(equal_skip[6:8], b"\x0f\x84")
            skip_target = 0x1406A9902 + struct.unpack_from("<i", equal_skip, 8)[0]
            self.assertEqual(image.get_data(0x6A997E, 6), bytes.fromhex("89bbc00e0000"))
            self.assertGreater(skip_target, 0x1406A997E)
            self.assertEqual(image.get_data(0x67FDB7, 15), bytes.fromhex(
                "4533c08b9324390000ff90e8000000"))
            self.assertEqual(image.get_data(0x680028, 1), b"\xe9")
            self.assertEqual(
                0x14068002D + struct.unpack_from("<i", image.get_data(0x680029, 4), 0)[0],
                0x14051FBF0)
            self.assertLess(0x14067FDC0, 0x140680028)

    def test_production_cycle_reloads_document_before_stop_check(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        with pefile.PE(data=source, fast_load=True) as image:
            self.assertEqual(image.get_data(0x6A20FF, 3), b"\x4c\x8b\xf1")
            self.assertEqual(image.get_data(0x6A2770, 7), bytes.fromhex("c6857007000000"))
            boundary = image.get_data(0x6A45B9, 57)
            self.assertEqual(boundary, bytes.fromhex(
                "498bcee80fd0ffff80b82e38000001750541c6463201"
                "498bcee8f9cfffff488bc833d2e80f2bffff488b742478"
                "41807e3200757ce97ee1ffff"))
            self.assertEqual(
                0x1406A45C1 + struct.unpack_from("<i", boundary, 4)[0], 0x1406A15D0)
            self.assertEqual(
                0x1406A45D7 + struct.unpack_from("<i", boundary, 26)[0], 0x1406A15D0)
            self.assertEqual(
                0x1406A45E1 + struct.unpack_from("<i", boundary, 36)[0], 0x1406970F0)
            self.assertEqual(
                0x1406A45F2 + struct.unpack_from("<i", boundary, 53)[0], 0x1406A2770)
            self.assertEqual(image.get_data(0x75D024, 2), b"\x7d\x0f")
            self.assertEqual(image.get_data(0x75D035, 3), b"\x33\xc0\xc3")
            self.assertEqual(image.get_data(0x75D030, 4), bytes.fromhex("488b04d0"))
            self.assertEqual(image.get_data(0x6970FA, 3), b"\x48\x8b\x01")

    def test_production_cycle_does_not_stop_on_null_document(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        with pefile.PE(data=source, fast_load=True) as image:
            image.parse_data_directories(directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
            functions = sorted(
                (IMAGE_BASE + entry.struct.BeginAddress, IMAGE_BASE + entry.struct.EndAddress)
                for entry in image.DIRECTORY_ENTRY_EXCEPTION)
            begins = [begin for begin, _end in functions]
            begin, end = functions[bisect.bisect_right(begins, 0x1406A20D0) - 1]
            self.assertEqual((begin, end), (0x1406A20D0, 0x1406A4947))
            section = next(item for item in image.sections if item.Name.startswith(b".text"))
            text = section.get_data()
            text_base = IMAGE_BASE + section.VirtualAddress
            insns = list(Cs(CS_ARCH_X86, CS_MODE_64).disasm(
                text[begin - text_base:end - text_base], begin))
            reloads = []
            for index, insn in enumerate(insns):
                if insn.mnemonic != "call" or not insn.bytes or insn.bytes[0] != 0xE8:
                    continue
                if insn.address + 5 + struct.unpack_from("<i", insn.bytes, 1)[0] != 0x1406A15D0:
                    continue
                nxt = insns[index + 1]
                self.assertFalse(nxt.mnemonic == "test" and "rax" in nxt.op_str)
                self.assertFalse(nxt.mnemonic.startswith("j") and nxt.mnemonic != "jmp")
                self.assertNotEqual(nxt.op_str.split(",", 1)[0], "rax")
                reloads.append(nxt)
            self.assertEqual(len(reloads), 99)
            stop_check = next(item for item in reloads if item.address == 0x1406A45C1)
            self.assertEqual(stop_check.op_str, "byte ptr [rax + 0x382e], 1")
            self.assertEqual(image.get_data(0x6A45C1, 14), bytes.fromhex(
                "80b82e38000001750541c6463201"))
            self.assertEqual(image.get_data(0x6970F0, 10), bytes.fromhex("48895c2410574883ec20"))
            self.assertEqual(image.get_data(0x697103, 6), bytes.fromhex("ff90e0000000"))
            self.assertEqual(image.get_data(0x697119, 6), bytes.fromhex("ff90e8000000"))
            self.assertEqual(
                0x14069712B + struct.unpack_from("<i", image.get_data(0x697126, 5), 1)[0],
                0x1406B36F0)
            self.assertEqual(image.get_data(0x6B36F0, 7), bytes.fromhex("488b81e8000000"))
            self.assertEqual(image.get_data(0x6B36F7, 7), bytes.fromhex("448b8028390000"))
            self.assertEqual(image.get_data(0x6B3706, 2), b"\x77\x12")
            self.assertEqual(0x1406B3708 + 0x12, 0x1406B371A)
            self.assertEqual(image.get_data(0x6B3708, 6), bytes.fromhex("889158600000"))
            self.assertEqual(image.get_data(0x6B371A, 1), b"\xc3")

    def test_production_cycle_does_not_keep_the_document_across_the_back_edge(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        pefile.MAX_IMPORT_SYMBOLS = 65536
        with pefile.PE(data=source, fast_load=True) as image:
            image.parse_data_directories(directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
            imports = {
                item.address: item.name.decode() if item.name else str(item.ordinal)
                for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
            cast = image.get_data(0x7A6238, 6)
            self.assertEqual(cast[:2], b"\xff\x25")
            cast_iat = 0x1407A623E + struct.unpack_from("<i", cast, 2)[0]
            self.assertEqual(imports[cast_iat], "__RTDynamicCast")
            self.assertEqual(
                0x1406A21C4 + struct.unpack_from("<i", image.get_data(0x6A21BF, 5), 1)[0],
                0x1407A6238)
            self.assertEqual(image.get_data(0x6A21C4, 26), bytes.fromhex(
                "488d88a8010000488db0b00100004885c9490f44f44889742478"))
            self.assertEqual(image.get_data(0x6A2790, 5), bytes.fromhex("488b742478"))
            self.assertEqual(image.get_data(0x6A27A6, 4), bytes.fromhex("8b5c2468"))
            self.assertEqual(image.get_data(0x6A280B, 4), bytes.fromhex("498b7e18"))
            reload = image.get_data(0x6A2819, 10)
            self.assertEqual(reload[:3], b"\x49\x8b\xce")
            self.assertEqual(0x1406A2821 + struct.unpack_from("<i", reload, 4)[0], 0x1406A15D0)
            self.assertEqual(image.get_data(0x6A2821, 3), b"\x4c\x8b\xc0")
            section = next(item for item in image.sections if item.Name.startswith(b".text"))
            text = section.get_data()
            text_base = IMAGE_BASE + section.VirtualAddress
            decoder = Cs(CS_ARCH_X86, CS_MODE_64)
            decoder.detail = True
            insns = list(decoder.disasm(
                text[0x1406A20D0 - text_base:0x1406A4947 - text_base], 0x1406A20D0))
            slot_writes = [
                insn.address for insn in insns
                if insn.op_str.startswith("qword ptr [rsp + 0x78],")]
            self.assertEqual(slot_writes, [0x1406A21D9])
            call_idxs = [
                index for index, insn in enumerate(insns)
                if insn.mnemonic == "call" and insn.bytes and insn.bytes[0] == 0xE8
                and insn.address + 5 + struct.unpack_from("<i", insn.bytes, 1)[0] == 0x1406A15D0]
            saved = []
            for index in call_idxs:
                limit = next((item for item in call_idxs if item > index), len(insns))
                live = True
                for insn in insns[index + 1:limit]:
                    if insn.mnemonic == "call":
                        break
                    reads, writes = insn.regs_access()
                    if live and insn.mnemonic == "mov" and insn.op_str == "rbx, rax":
                        saved.append(insn.address)
                    if live and insn.mnemonic == "mov" and "ptr" in insn.op_str and insn.op_str.endswith(", rax"):
                        saved.append(insn.address)
                    if X86_REG_RAX in writes or X86_REG_EAX in writes:
                        live = False
            self.assertEqual(saved, [0x1406A4462])
            pair = image.get_data(0x6A4428, 83)
            self.assertEqual(pair[:3], b"\x48\x8b\xd8")
            self.assertEqual(pair[-2:], b"\xb3\x01")
            self.assertLess(0x1406A4479, 0x1406A45ED)
            self.assertEqual(image.get_data(0x6A43AE, 2), b"\x74\x78")
            self.assertEqual(0x1406A43B0 + 0x78, 0x1406A4428)
            interior = image.get_data(0x6A44F5, 7)
            self.assertEqual(interior, bytes.fromhex("488d98a8160000"))
            self.assertEqual(image.get_data(0x6A4518, 3), b"\x48\x8b\xcb")

    def test_view_deletion_does_not_clear_the_reloaded_binding(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        with pefile.PE(data=source, fast_load=True) as image:
            image.parse_data_directories(directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
            functions = {
                IMAGE_BASE + entry.struct.BeginAddress: IMAGE_BASE + entry.struct.EndAddress
                for entry in image.DIRECTORY_ENTRY_EXCEPTION}
            self.assertEqual(functions[0x1406ABF00], 0x1406ABF4E)
            self.assertEqual(functions[0x1406ABC60], 0x1406ABE95)
            wrapper = image.get_data(0x6ABF0F, 25)
            self.assertEqual(0x1406ABF14 + struct.unpack_from("<i", wrapper, 1)[0], 0x1406ABC60)
            self.assertEqual(wrapper[5:9], b"\x40\xf6\xc7\x01")
            self.assertEqual(0x1406ABF28 + struct.unpack_from("<i", wrapper, 21)[0], 0x14077F4AE)
            section = next(item for item in image.sections if item.Name.startswith(b".text"))
            text = section.get_data()
            text_base = IMAGE_BASE + section.VirtualAddress
            decoder = Cs(CS_ARCH_X86, CS_MODE_64)
            decoder.detail = True
            spans = [(0x1406ABC60, 0x1406ABE95)]
            body = list(decoder.disasm(text[0x1406ABC60 - text_base:0x1406ABE95 - text_base], 0x1406ABC60))
            for insn in body:
                if insn.mnemonic == "call" and insn.bytes and insn.bytes[0] == 0xE8:
                    target = insn.address + 5 + struct.unpack_from("<i", insn.bytes, 1)[0]
                    if target in functions:
                        spans.append((target, functions[target]))
            self.assertEqual(body[-1].mnemonic, "jmp")
            self.assertEqual(body[-1].address + body[-1].size
                             + struct.unpack_from("<i", bytes(body[-1].bytes), 1)[0], 0x140780570)
            for begin, end in spans:
                for insn in decoder.disasm(text[begin - text_base:end - text_base], begin):
                    for operand in insn.operands:
                        if operand.type == X86_OP_MEM and operand.mem.disp == 0x5838:
                            self.fail(f"{insn.address:#x} uses document+0x5838")

    def test_document_destructor_releases_the_array_without_a_message_pump(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        pefile.MAX_IMPORT_SYMBOLS = 65536
        with pefile.PE(data=source, fast_load=True) as image:
            image.parse_data_directories(directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
            imports = {
                item.address: entry.dll.lower()
                for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
            functions = sorted(
                (IMAGE_BASE + entry.struct.BeginAddress, IMAGE_BASE + entry.struct.EndAddress)
                for entry in image.DIRECTORY_ENTRY_EXCEPTION)
            begins = [begin for begin, _end in functions]
            section = next(item for item in image.sections if item.Name.startswith(b".text"))
            text = section.get_data()
            text_base = IMAGE_BASE + section.VirtualAddress
            decoder = Cs(CS_ARCH_X86, CS_MODE_64)
            seen = set()
            user32 = []
            pending = [0x14067FC20]
            while pending:
                site = pending.pop()
                owner = bisect.bisect_right(begins, site) - 1
                begin, end = functions[owner]
                if not begin <= site < end or begin in seen:
                    continue
                seen.add(begin)
                for insn in decoder.disasm(text[begin - text_base:end - text_base], begin):
                    if insn.mnemonic == "call" and insn.bytes[:1] == b"\xe8":
                        pending.append(insn.address + 5 + struct.unpack_from("<i", insn.bytes, 1)[0])
                    elif insn.mnemonic == "jmp" and insn.bytes[:1] == b"\xe9":
                        pending.append(insn.address + 5 + struct.unpack_from("<i", insn.bytes, 1)[0])
                    elif insn.bytes[:2] == b"\xff\x15":
                        iat = insn.address + 6 + struct.unpack_from("<i", insn.bytes, 2)[0]
                        if imports.get(iat) == b"user32.dll":
                            user32.append(insn.address)
            self.assertIn(0x14051FBF0, seen)
            self.assertNotIn(0x1405E8AF0, seen)
            self.assertEqual(user32, [])
            release = image.get_data(0x51FD33, 12)
            self.assertEqual(release[:7], bytes.fromhex("488d8fe0230000"))
            self.assertEqual(0x14051FD3F + struct.unpack_from("<i", release, 8)[0], 0x14077FDD8)

    def test_embedded_cao_destructor_runs_after_the_array_buffer_is_freed(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        pefile.MAX_IMPORT_SYMBOLS = 65536
        with pefile.PE(data=source, fast_load=True) as image:
            image.parse_data_directories(directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
            imports = {
                item.address: (entry.dll.lower(), item.name.decode() if item.name else str(item.ordinal))
                for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
            self.assertEqual(image.get_data(0x51FC03, 3), b"\x48\x8b\xf9")
            self.assertLess(0x14051FD3A, 0x14051FEF2)
            site = image.get_data(0x51FEEB, 14)
            self.assertEqual(site[:7], bytes.fromhex("488d8f80010000"))
            self.assertEqual(site[7:9], b"\xff\x15")
            iat = 0x14051FEF8 + struct.unpack_from("<i", site, 9)[0]
            self.assertEqual(imports[iat], (b"vitdatacad.dll", "??1CDataCao@@UEAA@XZ"))
            self.assertEqual(image.get_data(0x51FEF9, 3), b"\x48\x8b\xcf")
            tail = image.get_data(0x51FF05, 5)
            self.assertEqual(0x14051FF0A + struct.unpack_from("<i", tail, 1)[0], 0x14077FE8C)
            thunk = image.get_data(0x77FE8C, 6)
            self.assertEqual(thunk[:2], b"\xff\x25")
            thunk_iat = 0x14077FE92 + struct.unpack_from("<i", thunk, 2)[0]
            self.assertEqual(imports[thunk_iat][1], "1104")

    def test_published_document_is_constructed_before_the_zero_mode_publish(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        pefile.MAX_IMPORT_SYMBOLS = 65536
        with pefile.PE(data=source, fast_load=True) as image:
            image.parse_data_directories(directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
            imports = {
                item.address: (entry.dll.lower(), item.name.decode() if item.name else str(item.ordinal))
                for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
            functions = sorted(
                (IMAGE_BASE + entry.struct.BeginAddress, IMAGE_BASE + entry.struct.EndAddress)
                for entry in image.DIRECTORY_ENTRY_EXCEPTION)
            ctor = image.get_data(0x67DEC6, 5)
            self.assertEqual(0x14067DECB + struct.unpack_from("<i", ctor, 1)[0], 0x14051DF90)
            self.assertEqual(image.get_data(0x67DEDD, 4), bytes.fromhex("48898680010000")[:4])
            self.assertEqual(image.get_data(0x67DEDD, 7), bytes.fromhex("48898680010000"))
            base_ctor = image.get_data(0x51DFBE, 13)
            self.assertEqual(base_ctor[:7], bytes.fromhex("488d8e80010000"))
            self.assertEqual(base_ctor[7:9], b"\xff\x15")
            iat = 0x14051DFCB + struct.unpack_from("<i", base_ctor, 9)[0]
            self.assertEqual(imports[iat], (b"vitdatacad.dll", "??0CDataCao@@QEAA@XZ"))
            self.assertLess(0x14051DFC5, 0x14051E15D)
            self.assertEqual(image.get_data(0x69727A, 2), b"\x33\xdb")
            branch = image.get_data(0x6972CB, 8)
            self.assertEqual(branch[:2], b"\x85\xf6")
            self.assertEqual(0x1406972D3 + struct.unpack_from("<i", branch, 4)[0], 0x140697426)
            self.assertEqual(image.get_data(0x697426, 7), bytes.fromhex("48899f24390000"))
            self.assertEqual(image.get_data(0x697444, 14), bytes.fromhex("4c8bc733d2498bceff90e8000000"))
            caller = image.get_data(0x68DACF, 7)
            self.assertEqual(caller[:2], b"\x33\xd2")
            self.assertEqual(0x14068DAD6 + struct.unpack_from("<i", caller, 3)[0], 0x140697200)
            section = next(item for item in image.sections if item.Name.startswith(b".text"))
            text = section.get_data()
            text_base = IMAGE_BASE + section.VirtualAddress
            inside = []
            for begin, end in functions:
                if end <= 0x14067DEA0 or begin >= 0x14067F87A:
                    continue
                body = text[begin - text_base:end - text_base]
                for index in range(len(body) - 5):
                    if body[index] != 0xE8:
                        continue
                    site = begin + index
                    if site + 5 + struct.unpack_from("<i", body, index + 1)[0] == 0x140697200:
                        inside.append(site)
            self.assertEqual(inside, [])

    def test_document_slot_108_publishes_before_it_mentions_the_stop_subobject(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        with pefile.PE(data=source, fast_load=True) as image:
            image.parse_data_directories(directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
            self.assertEqual(
                int.from_bytes(image.get_data(0xEA3868 + 0x108, 8), "little"), 0x14068DC20)
            functions = {
                IMAGE_BASE + entry.struct.BeginAddress: IMAGE_BASE + entry.struct.EndAddress
                for entry in image.DIRECTORY_ENTRY_EXCEPTION}
            self.assertEqual(functions[0x14068DC20], 0x14068EDFE)
            self.assertEqual(image.get_data(0x68DC51, 3), b"\x48\x8b\xf1")
            publish = image.get_data(0x68DC96, 10)
            self.assertEqual(publish[:5], bytes.fromhex("8bd0488bce"))
            self.assertEqual(0x14068DCA0 + int.from_bytes(publish[6:10], "little", signed=True), 0x140697200)
            self.assertLess(0x14068DC9B, 0x14068E35C)
            later = image.get_data(0x68E359, 16)
            self.assertEqual(later, bytes.fromhex("488b01488d9648250000ff9040010000"))
            section = next(item for item in image.sections if item.Name.startswith(b".text"))
            text = section.get_data()
            text_base = IMAGE_BASE + section.VirtualAddress
            body = text[0x14068DC20 - text_base:0x14068EDFE - text_base]
            stops = []
            for index in range(len(body) - 5):
                if body[index] != 0xE8:
                    continue
                target = 0x14068DC20 + index + 5 + int.from_bytes(body[index + 1:index + 5], "little", signed=True)
                if target in (0x1406920F0, 0x140691C80):
                    stops.append(target)
            self.assertEqual(stops, [])

    def test_production_stop_restarts_only_after_the_thread_slot_is_cleared(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        pefile.MAX_IMPORT_SYMBOLS = 65536
        with pefile.PE(data=source, fast_load=True) as image:
            image.parse_data_directories(directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
            imports = {
                item.address: (entry.dll.lower(), item.name.decode() if item.name else str(item.ordinal))
                for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
            functions = {
                IMAGE_BASE + entry.struct.BeginAddress: IMAGE_BASE + entry.struct.EndAddress
                for entry in image.DIRECTORY_ENTRY_EXCEPTION}
            self.assertEqual(functions[0x1406920F0], 0x1406923F9)
            self.assertEqual(image.get_data(0x6921E0, 2), b"\x33\xf6")
            stop = image.get_data(0x6921FD, 16)
            self.assertEqual(stop[:7], bytes.fromhex("488b8b68380000"))
            self.assertEqual(stop[7:9], b"\xff\x15")
            iat = 0x14069220A + int.from_bytes(stop[9:13], "little", signed=True)
            self.assertEqual(imports[iat], (b"basetools.dll", "?Stop@CViThread@@QEAA_NAEAKK@Z"))
            self.assertEqual(stop[13:16], b"\x3c\x01\x74")
            self.assertEqual(image.get_data(0x69224E, 7), bytes.fromhex("4889b368380000"))
            self.assertEqual(image.get_data(0x69234C, 9), bytes.fromhex("80bb81380000017535"))
            restart = image.get_data(0x69237D, 8)
            self.assertEqual(restart[:3], b"\x48\x8b\xcb")
            self.assertEqual(0x140692385 + int.from_bytes(restart[4:8], "little", signed=True), 0x140691C80)
            self.assertLess(0x140692204, 0x14069224E)
            self.assertLess(0x14069224E, 0x140692380)
            section = next(item for item in image.sections if item.Name.startswith(b".text"))
            text = section.get_data()
            text_base = IMAGE_BASE + section.VirtualAddress
            callers = []
            for begin, end in functions.items():
                body = text[begin - text_base:end - text_base]
                for index in range(len(body) - 5):
                    if body[index] != 0xE8:
                        continue
                    site = begin + index
                    if site + 5 + int.from_bytes(body[index + 1:index + 5], "little", signed=True) == 0x140691C80:
                        callers.append(site)
            self.assertEqual(sorted(callers), [0x140692380, 0x1406B0FC6, 0x14075EF33])

    def test_production_start_leaves_an_existing_thread_running(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        with pefile.PE(data=source, fast_load=True) as image:
            self.assertEqual(image.get_data(0x691E88, 10), bytes.fromhex("4883be68380000007411"))
            self.assertEqual(0x140691E92 + 0x11, 0x140691EA3)
            occupied = image.get_data(0x691E9E, 5)
            self.assertEqual(occupied[0], 0xE9)
            self.assertEqual(0x140691EA3 + int.from_bytes(occupied[1:5], "little", signed=True), 0x1406920B9)
            self.assertLess(0x140691EA3, 0x140691FF1)
            self.assertLess(0x140691FF1, 0x1406920B9)
            self.assertEqual(image.get_data(0x691FF1, 7), bytes.fromhex("48898668380000"))
            self.assertEqual(image.get_data(0x6920C3, 2), b"\x32\xdb")
            image.parse_data_directories(directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
            functions = {
                IMAGE_BASE + entry.struct.BeginAddress: IMAGE_BASE + entry.struct.EndAddress
                for entry in image.DIRECTORY_ENTRY_EXCEPTION}
            self.assertEqual(functions[0x140691C80], 0x1406920E4)
            section = next(item for item in image.sections if item.Name.startswith(b".text"))
            decoder = Cs(CS_ARCH_X86, CS_MODE_64)
            body = section.get_data()[0x691C80:0x6920E4]
            stops = [
                insn.address for insn in decoder.disasm(body, 0x140691C80)
                if insn.bytes[:1] == b"\xe8"
                and insn.address + 5 + int.from_bytes(insn.bytes[1:5], "little", signed=True) == 0x1406920F0]
            self.assertEqual(stops, [])

    def test_document_destructor_releases_controller_without_stopping(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        machine = (ROOT / "v3d_files_" / "ViVirtualMachine.dll").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        self.assertEqual(
            hashlib.sha256(machine).hexdigest(),
            "5b62adea102b62a272860bfba72cb787bf74bd006f44fe97453df5121efeeb60")
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
                imports = {
                    item.address: item.name.decode() if item.name else str(item.ordinal)
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                self.assertEqual(image.get_data(0x51E3BA, 9), bytes.fromhex("33db48899ee8190000"))
                self.assertEqual(image.get_data(0x51FC2D, 7), bytes.fromhex("488b8fe8190000"))
                self.assertEqual(image.get_data(0x51FC34, 5), bytes.fromhex("4885c97452"))
                self.assertEqual(0x14051FC39 + 0x52, 0x14051FC8B)
                self.assertEqual(image.get_data(0x51FC4D, 6), bytes.fromhex("ff9090010000"))
                self.assertEqual(image.get_data(0x51FC63, 5), bytes.fromhex("f00fc14308"))
                self.assertEqual(image.get_data(0x51FC73, 3), bytes.fromhex("ff5008"))
                self.assertEqual(image.get_data(0x51FC87, 3), bytes.fromhex("ff5010"))
                current = image.get_data(0x69730F, 6)
                self.assertEqual(current[:2], b"\xff\x15")
                self.assertEqual(
                    imports[0x140697315 + struct.unpack_from("<i", current, 2)[0]],
                    "?GetCurrent@CVMC_ListSingleton@@QEBAPEAVIVMachineController@ViVMachineController@@XZ")
                self.assertEqual(image.get_data(0x697315, 11), bytes.fromhex("488bd0488bcfe8209beaff"))
                self.assertEqual(
                    0x140697320 + struct.unpack_from("<i", image.get_data(0x69731C, 4))[0],
                    0x140540E40)
                functions = {
                    IMAGE_BASE + entry.struct.BeginAddress: IMAGE_BASE + entry.struct.EndAddress
                    for entry in image.DIRECTORY_ENTRY_EXCEPTION}
                end = functions[0x14051FBF0]
                self.assertGreater(end, 0x14051FC87)
                section = next(item for item in image.sections if item.Name.startswith(b".text"))
                body = section.get_data()[0x51FBF0:end - IMAGE_BASE]
                decoder = Cs(CS_ARCH_X86, CS_MODE_64)
                stops = [
                    insn.address for insn in decoder.disasm(body, 0x14051FBF0)
                    if insn.bytes[:1] == b"\xe8"
                    and insn.address + 5 + int.from_bytes(insn.bytes[1:5], "little", signed=True) == 0x1406920F0]
                self.assertEqual(stops, [])
            with pefile.PE(data=machine, fast_load=True) as image:
                self.assertEqual(image.OPTIONAL_HEADER.ImageBase, 0x180000000)
                self.assertEqual(image.get_data(0x689A4, 3), bytes.fromhex("488bf1"))
                self.assertEqual(image.get_data(0x689D5, 7), bytes.fromhex("488d05cc630600"))
                self.assertEqual(0x1800689DC + 0x663CC, 0x1800CEDA8)
                self.assertEqual(image.get_data(0x689DC, 3), bytes.fromhex("488906"))
                self.assertLess(0x1800689BB, 0x1800689DC)
                self.assertEqual(image.get_data(0xCEF38, 8), bytes.fromhex("404e078001000000"))
                self.assertEqual(image.get_data(0x74E40, 17), bytes.fromhex("488b8970080000488b0148ffa020020000"))
                self.assertEqual(image.get_data(0x58C50, 17), bytes.fromhex("488b8918010000488b0148ffa020020000"))
                self.assertEqual(image.get_data(0xC83D8, 8), bytes.fromhex("483e0d8001000000"))
                self.assertEqual(image.get_data(0xC8600, 8), bytes.fromhex("f4cd078001000000"))
                self.assertEqual(image.get_data(0xD3E54, 4), bytes.fromhex("10e50f00"))
                self.assertEqual(image.get_data(0xFE520, 28), b".?AVIAcquisitionController@@")
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                imports = {
                    item.address: item.name.decode() if item.name else str(item.ordinal)
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                pure = image.get_data(0x7CDF4, 6)
                self.assertEqual(pure, bytes.fromhex("ff252edb0300"))
                self.assertEqual(imports[0x18007CDFA + struct.unpack_from("<i", pure, 2)[0]], "_purecall")
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_document_destructor_destroys_the_5878_array_without_stopping(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        with pefile.PE(data=source, fast_load=True) as image:
            self.assertEqual(image.get_data(0x67FCDE, 7), bytes.fromhex("488b8b78580000"))
            self.assertEqual(image.get_data(0x67FCE5, 3), bytes.fromhex("4533ff"))
            self.assertEqual(image.get_data(0x67FCF6, 4), bytes.fromhex("418d5703"))
            self.assertEqual(image.get_data(0x67FCFA, 3), bytes.fromhex("ff5008"))
            self.assertEqual(image.get_data(0x67FD0A, 7), bytes.fromhex("4c89bb78580000"))
            self.assertLess(0x14067FCFA, 0x14067FD0A)
            self.assertEqual(image.get_data(0xE9E8C0, 8), struct.pack("<Q", 0x1406803C0))
            self.assertEqual(image.get_data(0x6803DE, 4), bytes.fromhex("f6c20274"))
            scalar = image.get_data(0x6803E3, 7)
            self.assertEqual(scalar[:3], b"\x4c\x8d\x0d")
            self.assertEqual(0x1406803EA + struct.unpack_from("<i", scalar, 3)[0], 0x14066E530)
            image.parse_data_directories(directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
            functions = {
                IMAGE_BASE + entry.struct.BeginAddress: IMAGE_BASE + entry.struct.EndAddress
                for entry in image.DIRECTORY_ENTRY_EXCEPTION}
            end = functions[0x14066E530]
            section = next(item for item in image.sections if item.Name.startswith(b".text"))
            decoder = Cs(CS_ARCH_X86, CS_MODE_64)
            body = section.get_data()[0x66E530:end - IMAGE_BASE]
            stops = [
                insn.address for insn in decoder.disasm(body, 0x14066E530)
                if insn.bytes[:1] == b"\xe8"
                and insn.address + 5 + int.from_bytes(insn.bytes[1:5], "little", signed=True) == 0x1406920F0]
            self.assertEqual(stops, [])

    def test_anomaly_element_destructor_does_not_join_production(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        support = (ROOT / "v3d_files_" / "StructSupport.dll").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        self.assertEqual(len(support), 2256384)
        self.assertEqual(
            hashlib.sha256(support).hexdigest(),
            "d6270dbe5c97b5ed1000c2541c1e8d495d7db6be184e45d6495d7fad75e0f832")
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                imports = {
                    item.address: (entry.dll.lower(), item.name.decode() if item.name else None)
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                self.assertEqual(image.get_data(0x66E573, 16), bytes.fromhex("33d2488bcbff5008904881c370030000"))
                thunk = image.get_data(0x45A61F, 6)
                self.assertEqual(thunk, bytes.fromhex("ff152b159000"))
                self.assertEqual(
                    imports[0x14045A625 + struct.unpack_from("<i", thunk, 2)[0]],
                    (b"structsupport.dll", "??1CAnomalieProd@@UEAA@XZ"))
            with pefile.PE(data=support, fast_load=True) as image:
                self.assertEqual(image.OPTIONAL_HEADER.ImageBase, 0x180000000)
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                imports = {
                    item.address: entry.dll.lower()
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                self.assertEqual(image.get_data(0x8D684, 5)[0], 0xE9)
                self.assertEqual(
                    0x18008D689 + struct.unpack_from("<i", image.get_data(0x8D685, 4))[0],
                    0x18008D550)
                section = next(item for item in image.sections if item.Name.startswith(b".text"))
                text = section.get_data()
                text_base = 0x180000000 + section.VirtualAddress
                decoder = Cs(CS_ARCH_X86, CS_MODE_64)
                dlls = []
                for begin, end in ((0x18008D610, 0x18008D689), (0x18008D550, 0x18008D601)):
                    body = text[begin - text_base:end - text_base]
                    for insn in decoder.disasm(body, begin):
                        if insn.bytes[:2] != b"\xff\x15":
                            continue
                        slot = insn.address + 6 + int.from_bytes(insn.bytes[2:6], "little", signed=True)
                        dlls.append(imports[slot])
                self.assertTrue(dlls)
                self.assertTrue(all(item != b"user32.dll" for item in dlls))
                self.assertNotIn(b"vision3d.exe", dlls)
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_async_kill_waits_on_its_own_thread_handle(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        tools = (ROOT / "v3d_files_" / "BaseTools.dll").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        self.assertEqual(len(tools), 1910272)
        self.assertEqual(
            hashlib.sha256(tools).hexdigest(),
            "a41b4b00cf464da7da886f2303e6161f4474bda29b32793d39e4c6cfc39547f8")
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                imports = {
                    item.address: item.name.decode() if item.name else str(item.ordinal)
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                self.assertEqual(image.get_data(0x67FD44, 7), bytes.fromhex("488d8b28610000"))
                thunk = image.get_data(0x67FD4B, 6)
                self.assertEqual(thunk[:2], b"\xff\x15")
                self.assertEqual(
                    imports[0x14067FD51 + struct.unpack_from("<i", thunk, 2)[0]],
                    "?Kill@CAsynchCommandExecution@@QEAA_NXZ")
            with pefile.PE(data=tools, fast_load=True) as image:
                self.assertEqual(image.OPTIONAL_HEADER.ImageBase, 0x180000000)
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                imports = {
                    item.address: item.name.decode() if item.name else str(item.ordinal)
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                self.assertEqual(image.get_data(0x71AC, 4), bytes.fromhex("80790801"))
                branch = image.get_data(0x71B0, 6)
                self.assertEqual(branch[:2], b"\x0f\x85")
                self.assertEqual(
                    0x1800071B6 + struct.unpack_from("<i", branch, 2)[0], 0x180007254)
                self.assertEqual(image.get_data(0x7469, 11), bytes.fromhex("ba50c30000488b4b10ff15"))
                wait = image.get_data(0x7472, 6)
                self.assertEqual(
                    imports[0x180007478 + struct.unpack_from("<i", wait, 2)[0]],
                    "WaitForSingleObject")
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_destructor_closes_event_and_semaphore_not_the_thread_slot(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
                imports = {
                    item.address: item.name.decode() if item.name else str(item.ordinal)
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                event = image.get_data(0x67E1EE, 6)
                semaphore = image.get_data(0x67E27D, 6)
                self.assertEqual(event[:2], b"\xff\x15")
                self.assertEqual(semaphore[:2], b"\xff\x15")
                self.assertEqual(imports[0x14067E1F4 + struct.unpack_from("<i", event, 2)[0]], "CreateEventA")
                self.assertEqual(imports[0x14067E283 + struct.unpack_from("<i", semaphore, 2)[0]], "CreateSemaphoreA")
                self.assertEqual(image.get_data(0x67E1F4, 7), bytes.fromhex("48898678380000"))
                self.assertEqual(image.get_data(0x67E217, 7), bytes.fromhex("4c89b668380000"))
                self.assertEqual(image.get_data(0x67E283, 7), bytes.fromhex("48898690380000"))
                self.assertLess(0x14067E1F4, 0x14067E217)
                self.assertLess(0x14067E217, 0x14067E283)
                self.assertEqual(image.get_data(0x67FD52, 7), bytes.fromhex("488b8b90380000"))
                self.assertEqual(image.get_data(0x67FD60, 7), bytes.fromhex("488b8b78380000"))
                self.assertEqual(image.get_data(0x67FD73, 7), bytes.fromhex("4c89bb78380000"))
                functions = {
                    IMAGE_BASE + entry.struct.BeginAddress: IMAGE_BASE + entry.struct.EndAddress
                    for entry in image.DIRECTORY_ENTRY_EXCEPTION}
                end = functions[0x14067FC20]
                section = next(item for item in image.sections if item.Name.startswith(b".text"))
                body = section.get_data()[0x67FC20:end - IMAGE_BASE]
                self.assertEqual(body.find(bytes.fromhex("68380000")), -1)
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_on_close_document_tails_to_view_teardown_without_stopping(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
                imports = {
                    item.address: (entry.dll.lower(), item.ordinal)
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                first = image.get_data(0x68D9DD, 5)
                second = image.get_data(0x68D9E9, 5)
                third = image.get_data(0x68DA1F, 5)
                tail = image.get_data(0x68DA31, 5)
                self.assertEqual(first[0], 0xE8)
                self.assertEqual(second[0], 0xE8)
                self.assertEqual(third[0], 0xE8)
                self.assertEqual(0x14068D9E2 + struct.unpack_from("<i", first, 1)[0], 0x1406928D0)
                self.assertEqual(image.get_data(0x68D9E2, 7), bytes.fromhex("488b8f50380000"))
                self.assertEqual(0x14068D9EE + struct.unpack_from("<i", second, 1)[0], 0x14063B430)
                self.assertEqual(0x14068DA24 + struct.unpack_from("<i", third, 1)[0], 0x1404E03F0)
                self.assertEqual(tail[0], 0xE9)
                self.assertEqual(0x14068DA36 + struct.unpack_from("<i", tail, 1)[0], 0x14077FE26)
                thunk = image.get_data(0x77FE26, 6)
                self.assertEqual(thunk[:2], b"\xff\x25")
                self.assertEqual(imports[0x14077FE2C + struct.unpack_from("<i", thunk, 2)[0]], (b"mfc140.dll", 8850))
                self.assertLess(0x14068D9DD, 0x14068D9E9)
                self.assertLess(0x14068D9E9, 0x14068DA1F)
                self.assertLess(0x14068DA1F, 0x14068DA31)
                functions = {
                    IMAGE_BASE + entry.struct.BeginAddress: IMAGE_BASE + entry.struct.EndAddress
                    for entry in image.DIRECTORY_ENTRY_EXCEPTION}
                section = next(item for item in image.sections if item.Name.startswith(b".text"))
                text = section.get_data()
                text_base = IMAGE_BASE + section.VirtualAddress
                decoder = Cs(CS_ARCH_X86, CS_MODE_64)
                stops = []
                for begin in (0x1406928D0, 0x14063B430, 0x1404E03F0):
                    end = functions[begin]
                    body = text[begin - text_base:end - text_base]
                    stops.extend(
                        insn.address for insn in decoder.disasm(body, begin)
                        if insn.bytes[:1] == b"\xe8"
                        and insn.address + 5 + int.from_bytes(insn.bytes[1:5], "little", signed=True) == 0x1406920F0)
                self.assertEqual(stops, [])
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_close_waits_on_the_app_object_not_the_production_thread(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                imports = {
                    item.address: item.name.decode() if item.name else str(item.ordinal)
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                call = image.get_data(0x67E2A4, 5)
                self.assertEqual(0x14067E2A9 + struct.unpack_from("<i", call, 1)[0], 0x14077F7F6)
                self.assertEqual(image.get_data(0x67E2A9, 15), bytes.fromhex("488b4808488b414048898650380000"))
                self.assertEqual(image.get_data(0x63B466, 19), bytes.fromhex("83bf78580000007448488b8f7058000083caff"))
                self.assertEqual(0x14063B46F + 0x48, 0x14063B4B7)
                wait = image.get_data(0x63B479, 6)
                self.assertEqual(wait[:2], b"\xff\x15")
                self.assertEqual(imports[0x14063B47F + struct.unpack_from("<i", wait, 2)[0]], "WaitForSingleObject")
                self.assertNotEqual(0x3850, 0x3868)
                self.assertNotEqual(0x5870, 0x3868)
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_close_pumps_after_waiting_on_the_supervisor_semaphore(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
                imports = {
                    item.address: (entry.dll.lower(), item.name.decode() if item.name else str(item.ordinal))
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                site = image.get_data(0x63B4B7, 12)
                self.assertEqual(site[:7], bytes.fromhex("488d8fb0560000"))
                self.assertEqual(0x14063B4C3 + struct.unpack_from("<i", site, 8)[0], 0x14064B880)
                self.assertEqual(image.get_data(0x64B89D, 10), bytes.fromhex("83caff488b8918010000"))
                wait = image.get_data(0x64B8A7, 6)
                self.assertEqual(wait[:2], b"\xff\x15")
                self.assertEqual(imports[0x14064B8AD + struct.unpack_from("<i", wait, 2)[0]], (b"kernel32.dll", "WaitForSingleObject"))
                pump = image.get_data(0x64B8FB, 6)
                self.assertEqual(pump[:2], b"\xff\x15")
                self.assertEqual(imports[0x14064B901 + struct.unpack_from("<i", pump, 2)[0]], (b"dytools0.dll", "?DoEvents@@YAXXZ"))
                functions = {
                    IMAGE_BASE + entry.struct.BeginAddress: IMAGE_BASE + entry.struct.EndAddress
                    for entry in image.DIRECTORY_ENTRY_EXCEPTION}
                end = functions[0x14064B880]
                section = next(item for item in image.sections if item.Name.startswith(b".text"))
                body = section.get_data()[0x64B880:end - IMAGE_BASE]
                self.assertEqual(body.find(bytes.fromhex("68380000")), -1)
                self.assertEqual(image.get_data(0x63B47F, 6), bytes.fromhex("ff8768580000"))
                self.assertEqual(image.get_data(0x63B485, 22), bytes.fromhex(
                    "4533c0488b8f70580000418d50013997685800007516"))
                self.assertEqual(0x14063B49B + 0x16, 0x14063B4B1)
                release = image.get_data(0x63B4AA, 7)
                self.assertEqual(release[:3], bytes.fromhex("48ff25"))
                self.assertEqual(imports[0x14063B4B1 + struct.unpack_from("<i", release, 3)[0]], (b"kernel32.dll", "ReleaseSemaphore"))
                paired = image.get_data(0x63B4B1, 6)
                self.assertEqual(paired[:2], b"\xff\x15")
                self.assertEqual(imports[0x14063B4B7 + struct.unpack_from("<i", paired, 2)[0]], (b"kernel32.dll", "ReleaseSemaphore"))
                self.assertEqual(image.get_data(0x63ACB4, 13), bytes.fromhex("4533c9ba0100000033c9448bc2"))
                create = image.get_data(0x63ACC1, 6)
                self.assertEqual(create[:2], b"\xff\x15")
                self.assertEqual(imports[0x14063ACC7 + struct.unpack_from("<i", create, 2)[0]], (b"kernel32.dll", "CreateSemaphoreA"))
                self.assertEqual(image.get_data(0x63ACC7, 7), bytes.fromhex("49898570580000"))
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_embedded_stop_nulls_the_producer_and_joins_the_other_thread(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                imports = {
                    item.address: (entry.dll.lower(), item.name.decode() if item.name else str(item.ordinal))
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                slot = int.from_bytes(image.get_data(0xEA3B68, 8), "little")
                self.assertEqual(slot, 0x140680D70)
                self.assertEqual(0x2548 + 0x1320, 0x3868)
                self.assertEqual(0x2548 + 0x1318, 0x3860)
                self.assertEqual(image.get_data(0x680DCB, 11), bytes.fromhex("48c7832013000000000000"))
                self.assertEqual(image.get_data(0x680E1B, 7), bytes.fromhex("488b8b18130000"))
                stop = image.get_data(0x680E22, 6)
                self.assertEqual(stop[:2], b"\xff\x15")
                self.assertEqual(
                    imports[0x140680E28 + struct.unpack_from("<i", stop, 2)[0]],
                    (b"basetools.dll", "?Stop@CViThread@@QEAA_NAEAKK@Z"))
                self.assertEqual(image.get_data(0x680E98, 7), bytes.fromhex("488d8bb8daffff"))
                self.assertEqual(image.get_data(0x6B1039, 13), bytes.fromhex("4881c148250000488b01ff5008"))
                self.assertEqual(image.get_data(0x6922AB, 7), bytes.fromhex("488b8b60380000"))
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_production_stop_is_reached_only_through_the_command_slot(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        with pefile.PE(data=source, fast_load=True) as image:
            image.parse_data_directories(directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
            self.assertEqual(int.from_bytes(image.get_data(0xEA3890, 8), "little"), 0x14068DA40)
            self.assertEqual(image.get_data(0x68DA46, 32), bytes.fromhex(
                "418bc0498bd948c1e8106683f84e7538b8cfb1000066443bc0752de88a460000"))
            self.assertEqual(0x14068DA66 + 0x468A, 0x1406920F0)
            self.assertEqual(source.find((0x1406920F0).to_bytes(8, "little")), -1)
            functions = {
                entry.struct.BeginAddress: entry.struct.EndAddress
                for entry in image.DIRECTORY_ENTRY_EXCEPTION}
            section = next(item for item in image.sections if item.Name.startswith(b".text"))
            base = section.VirtualAddress
            blob = section.get_data()
            decoder = Cs(CS_ARCH_X86, CS_MODE_64)
            for begin in (0x68D9D0, 0x67FC20, 0x6AF270, 0x4E03F0, 0x6B0C00):
                body = blob[begin - base:functions[begin] - base]
                calls = [
                    insn.address + insn.size + int.from_bytes(insn.bytes[1:5], "little", signed=True)
                    for insn in decoder.disasm(body, IMAGE_BASE + begin)
                    if insn.bytes and insn.bytes[0] == 0xE8]
                self.assertNotIn(0x1406920F0, calls)
                self.assertNotIn(0x14068DA40, calls)

    def test_close_does_not_join_the_communication_thread(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        with pefile.PE(data=source, fast_load=True) as image:
            image.parse_data_directories(directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
            self.assertEqual(image.get_data(0x691F28, 5), bytes.fromhex("b948000000"))
            site = image.get_data(0x691F3B, 26)
            self.assertEqual(site, bytes.fromhex("488bd6488bc8e8daa3feff488bc8eb03498bcc48898e60380000"))
            self.assertEqual(0x140691F46 + struct.unpack_from("<i", site, 7)[0], 0x14067C320)
            self.assertEqual(int.from_bytes(image.get_data(0xEA1CD8, 8), "little"), 0x14067C480)
            functions = {
                entry.struct.BeginAddress: entry.struct.EndAddress
                for entry in image.DIRECTORY_ENTRY_EXCEPTION}
            section = next(item for item in image.sections if item.Name.startswith(b".text"))
            blob = section.get_data()
            base = section.VirtualAddress
            for begin in (0x68D9D0, 0x67FC20, 0x6AF270, 0x4E03F0, 0x6B0C00):
                body = blob[begin - base:functions[begin] - base]
                self.assertEqual(body.find(bytes.fromhex("60380000")), -1)

    def test_third_skip_post_uses_the_saved_object_document(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        with pefile.PE(data=source, fast_load=True) as image:
            self.assertEqual(image.get_data(0x7368DB, 4), bytes.fromhex("48894808"))
            self.assertEqual(image.get_data(0x7368EA, 7), bytes.fromhex("488da808f9ffff"))
            self.assertEqual(0x700 - 0x6F8, 8)
            self.assertEqual(image.get_data(0x736CBC, 7), bytes.fromhex("4c8bbd00070000"))
            self.assertEqual(image.get_data(0x736FD0, 11), bytes.fromhex("498b4710488b8838580000"))
            self.assertEqual(image.get_data(0x735150, 4), bytes.fromhex("4c894110"))
            self.assertEqual(image.get_data(0x66DC00, 4), bytes.fromhex("4c8b4728"))
            self.assertEqual(int.from_bytes(image.get_data(0xEA8A28, 8), "little"), 0x14066DB40)
            self.assertEqual(0xEA8A28 - 0xEA8A10, 0x18)
            reload = image.get_data(0x69FD6D, 11)
            self.assertEqual(reload[:3], bytes.fromhex("488bcd"))
            self.assertEqual(0x14069FD75 + struct.unpack_from("<i", reload, 4)[0], 0x1406A15D0)
            self.assertEqual(reload[8:], bytes.fromhex("4c8bc0"))

    def test_worker_document_is_copied_from_the_accessor_before_treat(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        with pefile.PE(data=source, fast_load=True) as image:
            image.parse_data_directories(directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
            self.assertEqual(image.get_data(0x699804, 4), bytes.fromhex("48894728"))
            filled = image.get_data(0x6A6B92, 8)
            self.assertEqual(filled[:3], bytes.fromhex("488bce"))
            self.assertEqual(0x1406A6B9A + struct.unpack_from("<i", filled, 4)[0], 0x1406A15D0)
            self.assertEqual(image.get_data(0x6A6B9B, 8), bytes.fromhex("4c897d2848894530"))
            handoff = image.get_data(0x6A6BBC, 16)
            self.assertEqual(handoff[:11], bytes.fromhex("488d8ec80e0000488d5528"))
            self.assertEqual(0x1406A6BCC + struct.unpack_from("<i", handoff, 12)[0], 0x1406A4980)
            self.assertEqual(image.get_data(0x6A49D7, 8), bytes.fromhex("498b460848894328"))
            functions = {
                entry.struct.BeginAddress: entry.struct.EndAddress
                for entry in image.DIRECTORY_ENTRY_EXCEPTION}
            section = next(item for item in image.sections if item.Name.startswith(b".text"))
            blob = section.get_data()
            base = section.VirtualAddress
            decoder = Cs(CS_ARCH_X86, CS_MODE_64)
            for begin in (0x68D9D0, 0x67FC20, 0x6AF270, 0x4E03F0, 0x6B0C00):
                body = blob[begin - base:functions[begin] - base]
                calls = [
                    insn.address + insn.size + int.from_bytes(insn.bytes[1:5], "little", signed=True)
                    for insn in decoder.disasm(body, IMAGE_BASE + begin)
                    if insn.bytes and insn.bytes[0] == 0xE8]
                self.assertNotIn(0x1406A4980, calls)

    def test_production_stop_deletes_the_workers_after_the_join(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        with pefile.PE(data=source, fast_load=True) as image:
            image.parse_data_directories(directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
            self.assertEqual(image.get_data(0x6921E0, 2), bytes.fromhex("33f6"))
            self.assertEqual(
                image.get_data(0x692238, 22),
                bytes.fromhex("488b8b683800004885c97411488b01ba01000000ff10"))
            self.assertEqual(image.get_data(0x69224E, 7), bytes.fromhex("4889b368380000"))
            self.assertEqual(int.from_bytes(image.get_data(0xEA8A48, 8), "little"), 0x14069A8F0)
            deleting = image.get_data(0x69A8FC, 8)
            self.assertEqual(deleting[:3], bytes.fromhex("488bf9"))
            self.assertEqual(0x14069A904 + struct.unpack_from("<i", deleting, 4)[0], 0x14069A320)
            pool = image.get_data(0x69A448, 12)
            self.assertEqual(pool[:7], bytes.fromhex("488d8fc80e0000"))
            self.assertEqual(0x14069A454 + struct.unpack_from("<i", pool, 8)[0], 0x14069A1A0)
            self.assertEqual(0x14069A1CB + struct.unpack_from("<i", image.get_data(0x69A1C6, 5), 1)[0], 0x140655980)
            self.assertEqual(
                image.get_data(0x6559A0, 25),
                bytes.fromhex("488b47088bd6488b0cd04885c9740a488b01ba01000000ff10"))
            self.assertEqual(int.from_bytes(image.get_data(0xEA8A10, 8), "little"), 0x14069A890)
            worker = image.get_data(0x69A8BC, 8)
            self.assertEqual(worker[:3], bytes.fromhex("488bce"))
            self.assertEqual(0x14069A8C4 + struct.unpack_from("<i", worker, 4)[0], 0x14069A110)
            functions = {
                entry.struct.BeginAddress: entry.struct.EndAddress
                for entry in image.DIRECTORY_ENTRY_EXCEPTION}
            section = next(item for item in image.sections if item.Name.startswith(b".text"))
            blob = section.get_data()
            base = section.VirtualAddress
            decoder = Cs(CS_ARCH_X86, CS_MODE_64)
            for begin in (0x68D9D0, 0x67FC20, 0x6AF270, 0x4E03F0, 0x6B0C00):
                body = blob[begin - base:functions[begin] - base]
                calls = [
                    insn.address + insn.size + int.from_bytes(insn.bytes[1:5], "little", signed=True)
                    for insn in decoder.disasm(body, IMAGE_BASE + begin)
                    if insn.bytes and insn.bytes[0] == 0xE8]
                self.assertNotIn(0x1406920F0, calls)
                self.assertNotIn(0x140655980, calls)

    def test_production_cycle_does_not_use_the_close_semaphore(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        pefile.MAX_IMPORT_SYMBOLS = 65536
        try:
            self._production_cycle_does_not_use_the_close_semaphore(source)
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def _production_cycle_does_not_use_the_close_semaphore(self, source: bytes) -> None:
        with pefile.PE(data=source, fast_load=True) as image:
            image.parse_data_directories(directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"],
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
            self.assertEqual(image.get_data(0x630075, 2), bytes.fromhex("33f6"))
            self.assertEqual(image.get_data(0x630242, 7), bytes.fromhex("4889b770580000"))
            closed = image.get_data(0x6304F9, 19)
            self.assertEqual(closed[:12], bytes.fromhex("488b89705800004885c97412"))
            self.assertEqual(closed[12], 0xFF)
            self.assertEqual(closed[13], 0x15)
            slot = 0x14063050B + struct.unpack_from("<i", closed, 14)[0]
            self.assertEqual(slot, 0x140D551C0)
            self.assertEqual(image.get_data(0x63050C, 11), bytes.fromhex("48c7877058000000000000"))
            imported = {
                item.address: item.name
                for lib in image.DIRECTORY_ENTRY_IMPORT
                for item in lib.imports}
            self.assertEqual(imported[slot], b"CloseHandle")
            functions = {
                entry.struct.BeginAddress: entry.struct.EndAddress
                for entry in image.DIRECTORY_ENTRY_EXCEPTION}
            section = next(item for item in image.sections if item.Name.startswith(b".text"))
            blob = section.get_data()
            base = section.VirtualAddress
            for begin in (0x6A20D0, 0x66DB40, 0x6A6A30, 0x7368D0):
                self.assertNotIn(bytes.fromhex("70580000"), blob[begin - base:functions[begin] - base])
            decoder = Cs(CS_ARCH_X86, CS_MODE_64)
            body = blob[0x6A20D0 - base:functions[0x6A20D0] - base]
            calls = [
                insn.address + insn.size + int.from_bytes(insn.bytes[1:5], "little", signed=True)
                for insn in decoder.disasm(body, IMAGE_BASE + 0x6A20D0)
                if insn.bytes and insn.bytes[0] == 0xE8]
            self.assertNotIn(0x14063B430, calls)

    def test_destructor_callees_do_not_join_the_producer(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        pefile.MAX_IMPORT_SYMBOLS = 65536
        try:
            self._destructor_callees_do_not_join_the_producer(source)
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def _destructor_callees_do_not_join_the_producer(self, source: bytes) -> None:
        with pefile.PE(data=source, fast_load=True) as image:
            image.parse_data_directories(directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"],
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
            serial = image.get_data(0x67FFD6, 12)
            self.assertEqual(serial[:7], bytes.fromhex("488d8bb82e0000"))
            self.assertEqual(0x14067FFE2 + struct.unpack_from("<i", serial, 8)[0], 0x1405B1720)
            other = image.get_data(0x67FFFF, 12)
            self.assertEqual(other[:7], bytes.fromhex("488d8b50250000"))
            self.assertEqual(0x14068000B + struct.unpack_from("<i", other, 8)[0], 0x1405B1720)
            tail = image.get_data(0x5B172A, 7)
            self.assertEqual(tail[:3], bytes.fromhex("48ff25"))
            slot = 0x1405B1731 + struct.unpack_from("<i", tail, 3)[0]
            imported = {
                item.address: item.name
                for lib in image.DIRECTORY_ENTRY_IMPORT
                for item in lib.imports}
            self.assertEqual(imported[slot], b"??1CSerialDriver@@UEAA@XZ")
            freed = image.get_data(0x67FE49, 12)
            self.assertEqual(freed[:7], bytes.fromhex("488d8bc8600000"))
            self.assertEqual(0x14067FE55 + struct.unpack_from("<i", freed, 8)[0], 0x1405CC080)
            empty = image.get_data(0x67FE56, 12)
            self.assertEqual(empty[:7], bytes.fromhex("488d8b78600000"))
            self.assertEqual(0x14067FE62 + struct.unpack_from("<i", empty, 8)[0], 0x140662340)
            self.assertEqual(image.get_data(0x662340, 3), bytes.fromhex("c20000"))
            functions = {
                entry.struct.BeginAddress: entry.struct.EndAddress
                for entry in image.DIRECTORY_ENTRY_EXCEPTION}
            section = next(item for item in image.sections if item.Name.startswith(b".text"))
            blob = section.get_data()
            base = section.VirtualAddress
            decoder = Cs(CS_ARCH_X86, CS_MODE_64)
            destructor = blob[0x67FC20 - base:functions[0x67FC20] - base]
            for insn in decoder.disasm(destructor, IMAGE_BASE + 0x67FC20):
                raw = insn.bytes
                if not raw:
                    continue
                iat = None
                if raw[:2] == b"\xff\x15" and len(raw) >= 6:
                    iat = insn.address + insn.size + int.from_bytes(raw[2:6], "little", signed=True)
                elif raw[:3] == b"\x48\xff\x15" and len(raw) >= 7:
                    iat = insn.address + insn.size + int.from_bytes(raw[3:7], "little", signed=True)
                if iat is None:
                    continue
                name = imported.get(iat) or b""
                self.assertNotIn(b"WaitForSingleObject", name)
                self.assertNotIn(b"Stop@CViThread", name)
            stops = {
                0x1406920F0, 0x140680C00, 0x140680D70, 0x14068DA40,
                0x14069A110, 0x140655980}
            pending = [
                (0x527B50, 0), (0x698F60, 0), (0x57BE20, 0), (0x675460, 0),
                (0x67F8C0, 0), (0x66E530, 0), (0x6C3BF0, 0), (0x698D60, 0),
                (0x6928D0, 0), (0x4E03F0, 0)]
            seen = set()
            while pending:
                begin, depth = pending.pop()
                if begin in seen or begin not in functions or depth > 1:
                    continue
                seen.add(begin)
                body = blob[begin - base:functions[begin] - base]
                self.assertNotIn(bytes.fromhex("68380000"), body)
                self.assertNotIn(bytes.fromhex("60380000"), body)
                for insn in decoder.disasm(body, IMAGE_BASE + begin):
                    raw = insn.bytes
                    if not raw:
                        continue
                    if raw[0] == 0xE8 and len(raw) >= 5:
                        target = insn.address + insn.size + int.from_bytes(raw[1:5], "little", signed=True)
                        self.assertNotIn(target, stops)
                        if depth == 0:
                            pending.append((target - IMAGE_BASE, 1))
                    elif raw[:2] == b"\xff\x15" and len(raw) >= 6:
                        iat = insn.address + insn.size + int.from_bytes(raw[2:6], "little", signed=True)
                        self.assertNotEqual(iat, 0x140D53470)
                    elif raw[:3] == b"\x48\xff\x15" and len(raw) >= 7:
                        iat = insn.address + insn.size + int.from_bytes(raw[3:7], "little", signed=True)
                        self.assertNotEqual(iat, 0x140D53470)


    def test_stop_byte_displacement_is_cleared_by_production_start(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        with pefile.PE(data=source, fast_load=True) as image:
            image.parse_data_directories(directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
            self.assertEqual(image.get_data(0x69203B, 7), bytes.fromhex("c6862e38000000"))
            self.assertEqual(image.get_data(0x6A45C1, 7), bytes.fromhex("80b82e38000001"))
            self.assertEqual(image.get_data(0x6AF56E, 8), bytes.fromhex("80b82e3800000175"))
            call = image.get_data(0x6B1043, 16)
            self.assertEqual(call[:3], bytes.fromhex("ff5008"))
            self.assertEqual(call[3:6], bytes.fromhex("488bce"))
            self.assertEqual(0x1406B104E + struct.unpack_from("<i", call, 7)[0], 0x1406AF4D0)
            functions = {
                entry.struct.BeginAddress: entry.struct.EndAddress
                for entry in image.DIRECTORY_ENTRY_EXCEPTION}
            section = next(item for item in image.sections if item.Name.startswith(b".text"))
            blob = section.get_data()
            base = section.VirtualAddress
            for begin in (0x68D9D0, 0x67FC20, 0x6AF270, 0x6B0C00):
                self.assertNotIn(bytes.fromhex("2e380000"), blob[begin - base:functions[begin] - base])
            self.assertNotIn(bytes.fromhex("2e380000"), image.get_data(0x4E03F0, 0x160))

    def test_close_does_not_call_the_embedded_stop_callers(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        with pefile.PE(data=source, fast_load=True) as image:
            image.parse_data_directories(directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
            site = image.get_data(0x6A467D, 21)
            self.assertEqual(site[:3], bytes.fromhex("498bce"))
            self.assertEqual(0x1406A4685 + struct.unpack_from("<i", site, 4)[0], 0x1406A15D0)
            self.assertEqual(site[8:], bytes.fromhex("488d8848250000488b01ff5008"))
            branch = image.get_data(0x6A45E7, 11)
            self.assertEqual(branch[:4], bytes.fromhex("807e3200"))
            self.assertEqual(0x1406A45ED + branch[5], 0x1406A4669)
            self.assertEqual(0x1406A45F2 + struct.unpack_from("<i", branch, 7)[0], 0x1406A2770)
            functions = {
                entry.struct.BeginAddress: entry.struct.EndAddress
                for entry in image.DIRECTORY_ENTRY_EXCEPTION}
            section = next(item for item in image.sections if item.Name.startswith(b".text"))
            blob = section.get_data()
            base = section.VirtualAddress
            decoder = Cs(CS_ARCH_X86, CS_MODE_64)
            callers = {
                0x1404C2640, 0x1405CB880, 0x140682FF0, 0x1406A1DA0,
                0x1406A20D0, 0x14075EFD0}
            for begin in (0x68D9D0, 0x67FC20, 0x6AF270, 0x6B0C00):
                body = blob[begin - base:functions[begin] - base]
                calls = {
                    insn.address + insn.size + int.from_bytes(insn.bytes[1:5], "little", signed=True)
                    for insn in decoder.disasm(body, IMAGE_BASE + begin)
                    if insn.bytes and insn.bytes[0] == 0xE8}
                self.assertFalse(calls & callers)
                for target in calls:
                    begin_callee = target - IMAGE_BASE
                    if begin_callee not in functions:
                        continue
                    nested_body = blob[begin_callee - base:functions[begin_callee] - base]
                    nested = {
                        insn.address + insn.size + int.from_bytes(insn.bytes[1:5], "little", signed=True)
                        for insn in decoder.disasm(nested_body, target)
                        if insn.bytes and insn.bytes[0] == 0xE8}
                    self.assertFalse(nested & callers)
            poster = blob[0x4E03F0 - base:0x4E03F0 - base + 0x160]
            poster_calls = {
                insn.address + insn.size + int.from_bytes(insn.bytes[1:5], "little", signed=True)
                for insn in decoder.disasm(poster, IMAGE_BASE + 0x4E03F0)
                if insn.bytes and insn.bytes[0] == 0xE8}
            self.assertFalse(poster_calls & callers)
            for target in poster_calls:
                begin_callee = target - IMAGE_BASE
                if begin_callee not in functions:
                    continue
                nested_body = blob[begin_callee - base:functions[begin_callee] - base]
                nested = {
                    insn.address + insn.size + int.from_bytes(insn.bytes[1:5], "little", signed=True)
                    for insn in decoder.disasm(nested_body, target)
                    if insn.bytes and insn.bytes[0] == 0xE8}
                self.assertFalse(nested & callers)

    def test_pre_destroy_document_slot_returns_immediately(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        mfc = (ROOT / "v3d_files_" / "mfc140.dll").read_bytes()
        self.assertEqual(hashlib.sha256(mfc).hexdigest(),
                         "0cf26008fae0cb61dfe49e1c3fc17e0dd860be011d9a6a64b452f56335bafbfe")
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        pefile.MAX_IMPORT_SYMBOLS = 65536
        try:
            with pefile.PE(data=source, fast_load=True) as image:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                self.assertEqual(int.from_bytes(image.get_data(0xEA3868 + 0x1C8, 8), "little"), 0x14077FE86)
                thunk = image.get_data(0x77FE86, 6)
                self.assertEqual(thunk[:2], bytes.fromhex("ff25"))
                slot = 0x14077FE8C + struct.unpack_from("<i", thunk, 2)[0]
                imported = {
                    item.address: item.ordinal
                    for lib in image.DIRECTORY_ENTRY_IMPORT
                    for item in lib.imports}
                self.assertEqual(imported[slot], 11723)
            with pefile.PE(data=mfc, fast_load=True) as library:
                self.assertEqual(library.get_data(0x21F8FD, 7), bytes.fromhex("488b81c8010000"))
                self.assertEqual(library.get_data(0x21F910, 7), bytes.fromhex("488b81d0000000"))
                self.assertLess(0x21F8FD, 0x21F910)
                directory = library.OPTIONAL_HEADER.DATA_DIRECTORY[0]
                header = library.get_data(directory.VirtualAddress, 40)
                base, _count, _names, functions, _names_rva, _ordinals = struct.unpack_from("<IIIIII", header, 16)
                index = 11723 - base
                function = struct.unpack_from("<I", library.get_data(functions + index * 4, 4))[0]
                self.assertEqual(library.get_data(function, 3), bytes.fromhex("c20000"))
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_view_destructor_stops_the_cad_engine_only(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        pefile.MAX_IMPORT_SYMBOLS = 65536
        try:
            with pefile.PE(data=source, fast_load=True) as image:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                loaded = image.get_data(0x6ABC90, 18)
                self.assertEqual(loaded[:10], bytes.fromhex("488b89700100004885c9"))
                self.assertEqual(loaded[12:14], bytes.fromhex("ff15"))
                slot = 0x1406ABCA2 + struct.unpack_from("<i", loaded, 14)[0]
                imported = {
                    item.address: item.name
                    for lib in image.DIRECTORY_ENTRY_IMPORT
                    for item in lib.imports}
                self.assertEqual(imported[slot], b"?StopEngine@CCadEngine@@QEAA_NXZ")
                functions = {
                    entry.struct.BeginAddress: entry.struct.EndAddress
                    for entry in image.DIRECTORY_ENTRY_EXCEPTION}
                section = next(item for item in image.sections if item.Name.startswith(b".text"))
                blob = section.get_data()
                base = section.VirtualAddress
                body = blob[0x6ABC60 - base:functions[0x6ABC60] - base]
                self.assertNotIn(bytes.fromhex("68380000"), body)
                decoder = Cs(CS_ARCH_X86, CS_MODE_64)
                calls = [
                    insn.address + insn.size + int.from_bytes(insn.bytes[1:5], "little", signed=True)
                    for insn in decoder.disasm(body, IMAGE_BASE + 0x6ABC60)
                    if insn.bytes and insn.bytes[0] == 0xE8]
                self.assertNotIn(0x1406920F0, calls)
                for target in calls:
                    begin = target - IMAGE_BASE
                    if begin not in functions:
                        continue
                    callee = blob[begin - base:functions[begin] - base]
                    self.assertNotIn(bytes.fromhex("68380000"), callee)
                    nested = [
                        insn.address + insn.size + int.from_bytes(insn.bytes[1:5], "little", signed=True)
                        for insn in decoder.disasm(callee, target)
                        if insn.bytes and insn.bytes[0] == 0xE8]
                    self.assertNotIn(0x1406920F0, nested)
                    self.assertNotIn(0x140680C00, nested)
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_view_destructor_thunks_do_not_join_the_producer(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        mfc = (ROOT / "v3d_files_" / "mfc140.dll").read_bytes()
        self.assertEqual(hashlib.sha256(mfc).hexdigest(),
                         "0cf26008fae0cb61dfe49e1c3fc17e0dd860be011d9a6a64b452f56335bafbfe")
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        pefile.MAX_IMPORT_SYMBOLS = 65536
        try:
            with pefile.PE(data=source, fast_load=True) as image:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                imported = {
                    item.address: item.ordinal
                    for lib in image.DIRECTORY_ENTRY_IMPORT
                    for item in lib.imports}
                delete_site = image.get_data(0x6ABD1B, 10)
                self.assertEqual(delete_site[:5], bytes.fromhex("488bc833d2"))
                self.assertEqual(0x1406ABD25 + struct.unpack_from("<i", delete_site, 6)[0], 0x14077F928)
                window_site = image.get_data(0x6ABD45, 12)
                self.assertEqual(window_site[:7], bytes.fromhex("488d8b186f0000"))
                self.assertEqual(0x1406ABD51 + struct.unpack_from("<i", window_site, 8)[0], 0x14077F880)
                free_site = image.get_data(0x6ABD52, 12)
                self.assertEqual(free_site[:7], bytes.fromhex("488d8bc86e0000"))
                self.assertEqual(0x1406ABD5E + struct.unpack_from("<i", free_site, 8)[0], 0x14077F7B4)
                release = image.get_data(0x6ABE3F, 7)
                self.assertEqual(release, bytes.fromhex("488bbbb0010000"))
                self.assertNotEqual(0x1B0, 0x3868)
                for thunk, ordinal in ((0x77F928, 12215), (0x77F880, 1421), (0x77F7B4, 1425)):
                    raw = image.get_data(thunk, 6)
                    self.assertEqual(raw[:2], bytes.fromhex("ff25"))
                    self.assertEqual(imported[IMAGE_BASE + thunk + 6 + struct.unpack_from("<i", raw, 2)[0]], ordinal)
            with pefile.PE(data=mfc, fast_load=True) as library:
                library.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                names = {
                    item.address: item.name
                    for lib in library.DIRECTORY_ENTRY_IMPORT
                    for item in lib.imports}
                opened = library.get_data(0x22BA50, 5)
                self.assertEqual(opened, bytes.fromhex("4885d27445"))
                self.assertEqual(0x18022BA55 + opened[4], 0x18022BA9A)
                delete_call = library.get_data(0x22BA9A, 6)
                self.assertEqual(delete_call[:2], bytes.fromhex("ff15"))
                self.assertEqual(names[0x18022BAA0 + struct.unpack_from("<i", delete_call, 2)[0]], b"DeleteFileA")
                hwnd = library.get_data(0x2902F3, 6)
                self.assertEqual(hwnd, bytes.fromhex("488b4f404885"))
                destroy = library.get_data(0x290311, 6)
                self.assertEqual(destroy[:2], bytes.fromhex("ff15"))
                self.assertEqual(names[0x180290317 + struct.unpack_from("<i", destroy, 2)[0]], b"DestroyWindow")
                freed = library.get_data(0x1D79CF, 6)
                self.assertEqual(freed[:4], bytes.fromhex("488b4b08"))
                self.assertEqual(freed[4:6], bytes.fromhex("ff15"))
                self.assertEqual(names[0x1801D79D9 + struct.unpack_from("<i", library.get_data(0x1D79D3, 6), 2)[0]], b"free")
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_memory_check_failure_reaches_ask_to_stop_without_close(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        mfc = (ROOT / "v3d_files_" / "mfc140.dll").read_bytes()
        self.assertEqual(hashlib.sha256(mfc).hexdigest(),
                         "0cf26008fae0cb61dfe49e1c3fc17e0dd860be011d9a6a64b452f56335bafbfe")
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        pefile.MAX_IMPORT_SYMBOLS = 65536
        try:
            with pefile.PE(data=source, fast_load=True) as image:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                call = image.get_data(0x6A279A, 12)
                self.assertEqual(call[:3], bytes.fromhex("498bce"))
                self.assertEqual(0x1406A27A2 + struct.unpack_from("<i", call, 4)[0], 0x14069C770)
                self.assertEqual(call[8:10], bytes.fromhex("84c0"))
                self.assertEqual(0x1406A27A6 + call[11], 0x1406A280B)
                label = image.get_data(0x69C7E9, 7)
                self.assertEqual(label[:3], bytes.fromhex("4c8d05"))
                text = 0x14069C7F0 + struct.unpack_from("<i", label, 3)[0]
                self.assertEqual(image.get_data(text - IMAGE_BASE, 31), b"CheckAvailableMemory() failed.\x00")
                choice = image.get_data(0x6A27C3, 14)
                self.assertEqual(choice[:2], bytes.fromhex("8b05"))
                self.assertEqual(0x1406A27C9 + struct.unpack_from("<i", choice, 2)[0], 0x1411697C4)
                self.assertEqual(choice[6:10], bytes.fromhex("85c00f84"))
                self.assertEqual(0x1406A27D1 + struct.unpack_from("<i", choice, 10)[0], 0x1406A45F2)
                data = next(item for item in image.sections if item.Name.startswith(b".data"))
                self.assertGreaterEqual(0x11697C4 - data.VirtualAddress, data.SizeOfRawData)
                later = image.get_data(0x6A475A, 6)
                self.assertEqual(later[:2], bytes.fromhex("393d"))
                self.assertEqual(0x1406A4760 + struct.unpack_from("<i", later, 2)[0], 0x1411697C4)
                store = image.get_data(0x6A45F2, 9)
                self.assertEqual(store[:7], bytes.fromhex("6641c746310001"))
                self.assertEqual(store[7], 0xEB)
                self.assertEqual(0x1406A45FB + store[8], 0x1406A466D)
                slot = int.from_bytes(image.get_data(0xE397C8, 8), "little")
                self.assertEqual(slot, 0x14077F4F6)
                thunk = image.get_data(0x77F4F6, 6)
                self.assertEqual(thunk[:2], bytes.fromhex("ff25"))
                imported = {
                    item.address: item.ordinal
                    for lib in image.DIRECTORY_ENTRY_IMPORT
                    for item in lib.imports}
                self.assertEqual(imported[0x14077F4FC + struct.unpack_from("<i", thunk, 2)[0]], 7430)
                functions = {
                    entry.struct.BeginAddress: entry.struct.EndAddress
                    for entry in image.DIRECTORY_ENTRY_EXCEPTION}
                section = next(item for item in image.sections if item.Name.startswith(b".text"))
                blob = section.get_data()
                base = section.VirtualAddress
                decoder = Cs(CS_ARCH_X86, CS_MODE_64)
                for begin in (0x68D9D0, 0x67FC20, 0x6AF270, 0x6B0C00):
                    body = blob[begin - base:functions[begin] - base]
                    calls = {
                        insn.address + insn.size + int.from_bytes(insn.bytes[1:5], "little", signed=True)
                        for insn in decoder.disasm(body, IMAGE_BASE + begin)
                        if insn.bytes and insn.bytes[0] == 0xE8}
                    self.assertNotIn(0x14069C770, calls)
                    for target in calls:
                        begin_callee = target - IMAGE_BASE
                        if begin_callee not in functions:
                            continue
                        nested_body = blob[begin_callee - base:functions[begin_callee] - base]
                        nested = {
                            insn.address + insn.size + int.from_bytes(insn.bytes[1:5], "little", signed=True)
                            for insn in decoder.disasm(nested_body, target)
                            if insn.bytes and insn.bytes[0] == 0xE8}
                        self.assertNotIn(0x14069C770, nested)
                poster = blob[0x4E03F0 - base:0x4E03F0 - base + 0x160]
                poster_calls = {
                    insn.address + insn.size + int.from_bytes(insn.bytes[1:5], "little", signed=True)
                    for insn in decoder.disasm(poster, IMAGE_BASE + 0x4E03F0)
                    if insn.bytes and insn.bytes[0] == 0xE8}
                self.assertNotIn(0x14069C770, poster_calls)
            with pefile.PE(data=mfc, fast_load=True) as library:
                directory = library.OPTIONAL_HEADER.DATA_DIRECTORY[0]
                header = library.get_data(directory.VirtualAddress, 40)
                export_base, _count, _names, functions_rva, _names_rva, _ordinals = struct.unpack_from("<IIIIII", header, 16)
                function = struct.unpack_from("<I", library.get_data(functions_rva + (7430 - export_base) * 4, 4))[0]
                self.assertEqual(library.get_data(function, 6), bytes.fromhex("b84a9c0280c3"))
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_base_destructor_clears_listed_views_after_the_array_free(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        mfc = (ROOT / "v3d_files_" / "mfc140.dll").read_bytes()
        self.assertEqual(hashlib.sha256(mfc).hexdigest(),
                         "0cf26008fae0cb61dfe49e1c3fc17e0dd860be011d9a6a64b452f56335bafbfe")
        with pefile.PE(data=source, fast_load=True) as image:
            self.assertLess(0x51FD33, 0x51FF05)
        with pefile.PE(data=mfc, fast_load=True) as library:
            directory = library.OPTIONAL_HEADER.DATA_DIRECTORY[0]
            header = library.get_data(directory.VirtualAddress, 40)
            export_base, _count, _names, functions_rva, _names_rva, _ordinals = struct.unpack_from("<IIIIII", header, 16)
            function = struct.unpack_from("<I", library.get_data(functions_rva + (1104 - export_base) * 4, 4))[0]
            self.assertEqual(function, 0x21DFE0)
            self.assertEqual(library.get_data(function + 0x14, 8), bytes.fromhex("488bd9e8a4010000"))
            self.assertEqual(0x18021DFFC + struct.unpack_from("<i", library.get_data(function + 0x17, 5), 1)[0], 0x18021E1A0)
            walk = library.get_data(0x21E1B4, 17)
            self.assertEqual(walk[:4], bytes.fromhex("488d4b58"))
            self.assertEqual(0x18021E1BD + struct.unpack_from("<i", walk, 5)[0], 0x180235BC0)
            self.assertEqual(walk[9:], bytes.fromhex("4883a0e800000000"))
            self.assertEqual(library.get_data(0x21E1A0, 0x37).find(bytes.fromhex("38580000")), -1)
            self.assertEqual(library.get_data(0x235BD7, 4), bytes.fromhex("488b5a10"))
            release = library.get_data(0x235BF0, 8)
            self.assertEqual(0x180235BF5 + struct.unpack_from("<i", release, 1)[0], 0x180235A50)
            self.assertEqual(release[5:], bytes.fromhex("488bc3"))

    def test_document_connection_list_is_not_the_production_thread(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        mfc = (ROOT / "v3d_files_" / "mfc140.dll").read_bytes()
        self.assertEqual(hashlib.sha256(mfc).hexdigest(),
                         "0cf26008fae0cb61dfe49e1c3fc17e0dd860be011d9a6a64b452f56335bafbfe")
        pefile.MAX_IMPORT_SYMBOLS = 65536
        for path in (ROOT / "v3d_files_").iterdir():
            if path.suffix.lower() not in {".dll", ".exe"} or path.name.lower() == "mfc140.dll":
                continue
            with pefile.PE(data=path.read_bytes(), fast_load=True) as image:
                if image.OPTIONAL_HEADER.Magic != 0x20B:
                    continue
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                if not hasattr(image, "DIRECTORY_ENTRY_IMPORT"):
                    continue
                ordinals = [
                    item.ordinal
                    for entry in image.DIRECTORY_ENTRY_IMPORT
                    if b"mfc140" in entry.dll.lower()
                    for item in entry.imports]
                self.assertNotIn(2525, ordinals)
        with pefile.PE(data=mfc, fast_load=True) as library:
            self.assertEqual(library.get_data(0x21DE8A, 2), bytes.fromhex("33ff"))
            self.assertEqual(library.get_data(0x21DEFF, 7), bytes.fromhex("4889bbe0000000"))
            self.assertEqual(library.get_data(0x2211A5, 7), bytes.fromhex("488b99e0000000"))
            self.assertEqual(library.get_data(0x2211B6, 10), bytes.fromhex("488b4910488b1b4885c9"))
            self.assertEqual(library.get_data(0x2211C5, 5), bytes.fromhex("ba01000000"))
            self.assertEqual(library.get_data(0x221190, 0x64).find(bytes.fromhex("68380000")), -1)
            clear = library.get_data(0x23D4BB, 14)
            self.assertEqual(clear[:9], bytes.fromhex("4533c083caff488bcb"))
            self.assertEqual(0x18023D4C9 + struct.unpack_from("<i", clear, 10)[0], 0x18023FB80)
            branch = library.get_data(0x23FB9D, 9)
            self.assertEqual(branch[:3], bytes.fromhex("4d85c0"))
            self.assertEqual(branch[3:5], bytes.fromhex("0f84"))
            self.assertEqual(0x18023FBA6 + struct.unpack_from("<i", branch, 5)[0], 0x18023FC49)
            call = library.get_data(0x21DFFD, 22)
            self.assertEqual(call[:4], bytes.fromhex("488b4b50"))
            self.assertEqual(call[15:22], bytes.fromhex("488b80d0000000"))
            self.assertEqual(struct.unpack_from("<Q", library.get_data(0x32FDB8, 8))[0], 0x180228E70)
            self.assertEqual(library.get_data(0x228E70, 5), bytes.fromhex("4883625000"))
            unlink = library.get_data(0x228E96, 5)
            self.assertEqual(0x180228E9B + struct.unpack_from("<i", unlink, 1)[0], 0x180235D10)
            self.assertEqual(library.get_data(0x228E70, 0x2B).find(bytes.fromhex("68380000")), -1)
            self.assertEqual(library.get_data(0x21DF76, 7), bytes.fromhex("4889bbb8000000"))
            self.assertEqual(library.get_data(0x21DFB5, 7), bytes.fromhex("4889bb78010000"))
            self.assertEqual(library.get_data(0x21DECE, 7), bytes.fromhex("4889bbd0000000"))
            release = library.get_data(0x21E0A6, 19)
            self.assertEqual(release[:7], bytes.fromhex("488b8bd0000000"))
            self.assertEqual(release[12:19], bytes.fromhex("488b01488b4010"))
            self.assertEqual(library.get_data(0x21E034, 8), bytes.fromhex("4883a3b800000000"))
            self.assertEqual(library.get_data(0x21E067, 8), bytes.fromhex("4883a37801000000"))
            self.assertEqual(library.get_data(0x21E01A, 0xB0).find(bytes.fromhex("68380000")), -1)

    def test_document_vtable_does_not_store_the_release_fields(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        mfc = (ROOT / "v3d_files_" / "mfc140.dll").read_bytes()
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        pefile.MAX_IMPORT_SYMBOLS = 65536
        try:
            with pefile.PE(data=source, fast_load=True) as image, pefile.PE(data=mfc, fast_load=True) as library:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                library.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
                functions = {
                    entry.struct.BeginAddress: entry.struct.EndAddress
                    for entry in image.DIRECTORY_ENTRY_EXCEPTION}
                mfc_functions = {
                    entry.struct.BeginAddress: entry.struct.EndAddress
                    for entry in library.DIRECTORY_ENTRY_EXCEPTION}
                imported = {
                    item.address: item.ordinal
                    for lib in image.DIRECTORY_ENTRY_IMPORT
                    if lib.dll.decode().lower().startswith("mfc")
                    for item in lib.imports}
                export = library.DIRECTORY_ENTRY_EXPORT
                ordinal_base = export.struct.Base
                addresses = library.get_data(
                    export.struct.AddressOfFunctions, export.struct.NumberOfFunctions * 4)
                call = image.get_data(0x67E006, 12)
                self.assertEqual(call[:7], bytes.fromhex("488d8e88580000"))
                self.assertEqual(0x14067E00D + 5 + struct.unpack_from("<i", call, 8)[0], 0x14066E1D0)
                nested = image.get_data(0x66E1F0, 7)
                self.assertEqual(nested[:3], bytes.fromhex("488d05"))
                self.assertNotEqual(
                    0x14066E1F7 + struct.unpack_from("<i", nested, 3)[0], 0x140EA3868)
                self.assertEqual(image.get_data(0x66E203, 2), bytes.fromhex("33f6"))
                self.assertEqual(image.get_data(0x66E2C5, 7), bytes.fromhex("4889b778010000"))
                decoder = Cs(CS_ARCH_X86, CS_MODE_64)
                decoder.detail = True
                constructor = image.get_data(0x67DEA0, functions[0x67DEA0] - 0x67DEA0)
                for instruction in decoder.disasm(constructor, 0x14067DEA0):
                    for operand in instruction.operands:
                        if operand.type == X86_OP_MEM:
                            self.assertNotIn(operand.mem.disp, (0xB8, 0xD0, 0x178))
                text = next(section for section in image.sections if section.Name.startswith(b".text"))
                text_lo = 0x140000000 + text.VirtualAddress
                text_hi = text_lo + text.Misc_VirtualSize
                slots = 0
                for index in range(0x60):
                    target = struct.unpack_from("<Q", image.get_data(0xEA3868 + index * 8, 8))[0]
                    if not text_lo <= target < text_hi:
                        break
                    slots += 1
                    opening = image.get_data(target - 0x140000000, 7)
                    if opening[0] == 0xFF and opening[1] == 0x25:
                        slot = target + 6 + struct.unpack_from("<i", opening, 2)[0]
                        ordinal = imported[slot]
                        rva = struct.unpack_from("<I", addresses, (ordinal - ordinal_base) * 4)[0]
                        end = mfc_functions.get(rva, rva + 0x20)
                        body = library.get_data(rva, min(end - rva, 0x20))
                        base = 0x180000000
                    else:
                        rva = target - 0x140000000
                        end = functions.get(rva)
                        body = image.get_data(rva, (end - rva) if end is not None else 0x40)
                        base = 0x140000000
                    for instruction in decoder.disasm(body, base + rva):
                        if instruction.mnemonic == "ret":
                            break
                        if instruction.mnemonic != "mov" or not instruction.op_str.startswith("qword"):
                            continue
                        for operand in instruction.operands:
                            if operand.type != X86_OP_MEM or operand.mem.disp not in (0xB8, 0xD0, 0x178):
                                continue
                            self.assertIn(decoder.reg_name(operand.mem.base), ("rsp", "rbp"))
                self.assertEqual(slots, 83)
                self.assertEqual(image.get_data(0x4D2863, 3), bytes.fromhex("4c8be9"))
                self.assertEqual(struct.unpack_from("<Q", image.get_data(0xE39820, 8))[0], 0x1404D2820)
                self.assertEqual(0x140E39770 + 0xB0, 0x140E39820)
                writer = image.get_data(0x4D33F9, 8)
                self.assertEqual(writer[:3], bytes.fromhex("498bcd"))
                self.assertEqual(0x1404D3401 + struct.unpack_from("<i", writer, 4)[0], 0x14077F9FA)
                app_ctor = image.get_data(0x4CE00D, 5)
                self.assertEqual(app_ctor, bytes.fromhex("488bf933d2"))
                app_vtable = image.get_data(0x4CE018, 7)
                self.assertEqual(0x1404CE01F + struct.unpack_from("<i", app_vtable, 3)[0], 0x140E39770)
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_communication_thread_does_not_stop_the_producer(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        pefile.MAX_IMPORT_SYMBOLS = 65536
        try:
            with pefile.PE(data=source, fast_load=True) as image:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                imported = {
                    item.address: item.name
                    for lib in image.DIRECTORY_ENTRY_IMPORT
                    for item in lib.imports}
                wait = image.get_data(0x67C514, 16)
                self.assertEqual(wait, bytes.fromhex("4183c9ff4533c0488d542438418d4803"))
                wait_slot = 0x14067C52A + struct.unpack_from("<i", image.get_data(0x67C526, 4))[0]
                self.assertEqual(imported[wait_slot], b"WaitForMultipleObjects")
                release = image.get_data(0x67CC64, 18)
                self.assertEqual(release, bytes.fromhex("488b4b204533c0418d5001488b8990380000"))
                release_slot = 0x14067CC7C + struct.unpack_from("<i", image.get_data(0x67CC78, 4))[0]
                self.assertEqual(imported[release_slot], b"ReleaseSemaphore")
                self.assertEqual(image.get_data(0x691C9F, 3), bytes.fromhex("488bf1"))
                caller = image.get_data(0x691F3B, 11)
                self.assertEqual(caller[:6], bytes.fromhex("488bd6488bc8"))
                self.assertEqual(0x140691F46 + struct.unpack_from("<i", caller, 7)[0], 0x14067C320)
                self.assertEqual(image.get_data(0x67C32A, 6), bytes.fromhex("488bda488bf9"))
                self.assertEqual(image.get_data(0x67C33D, 4), bytes.fromhex("48895f20"))
                functions = {
                    entry.struct.BeginAddress: entry.struct.EndAddress
                    for entry in image.DIRECTORY_ENTRY_EXCEPTION}
                stops = {0x1406920F0, 0x140680C00, 0x14068DA40}
                decoder = Cs(CS_ARCH_X86, CS_MODE_64)
                for begin in (0x67C480, 0x67C630, 0x67C7B0, 0x68B8A0, 0x685D70, 0x64E110):
                    body = image.get_data(begin, functions[begin] - begin)
                    self.assertEqual(body.find(bytes.fromhex("68380000")), -1)
                    for instruction in decoder.disasm(body, 0x140000000 + begin):
                        raw = instruction.bytes
                        if raw and raw[0] == 0xE8 and len(raw) >= 5:
                            target = instruction.address + 5 + int.from_bytes(raw[1:5], "little", signed=True)
                            self.assertNotIn(target, stops)
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_view_map_size_and_erase_do_not_stop_the_producer(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        library_bytes = (ROOT / "v3d_files_" / "mfc140.dll").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        pefile.MAX_IMPORT_SYMBOLS = 65536
        try:
            with pefile.PE(data=source, fast_load=True) as image, pefile.PE(
                    data=library_bytes, fast_load=True) as library:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                library.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]])
                imported = {
                    item.address: item.ordinal
                    for lib in image.DIRECTORY_ENTRY_IMPORT
                    for item in lib.imports}
                _, entries = struct.unpack("<QQ", image.get_data(0xEACE80, 16))
                found = {}
                cursor = entries
                while True:
                    record = struct.unpack("<IIIIQQ", image.get_data(cursor - IMAGE_BASE, 32))
                    if record == (0, 0, 0, 0, 0, 0):
                        break
                    found.setdefault(record[0], record[5])
                    cursor += 32
                self.assertNotIn(0x10, found)
                self.assertEqual(found[2], 0x1406AF270)
                self.assertEqual(found[0x14], 0x1406AF450)
                self.assertEqual(found[5], 0x14078055E)
                thunk = image.get_data(0x78055E, 6)
                self.assertEqual(thunk[:2], b"\xff\x25")
                self.assertEqual(imported[0x140780564 + struct.unpack_from("<i", thunk, 2)[0]], 11222)
                export = library.DIRECTORY_ENTRY_EXPORT.struct
                rva = struct.unpack("<I", library.get_data(
                    export.AddressOfFunctions + (11222 - export.Base) * 4, 4))[0]
                self.assertEqual(rva, 0x28D060)
                call = library.get_data(0x28D069, 5)
                self.assertEqual(0x18028D06E + struct.unpack_from("<i", call, 1)[0], 0x18028F370)
                functions = {
                    entry.struct.BeginAddress: entry.struct.EndAddress
                    for entry in image.DIRECTORY_ENTRY_EXCEPTION}
                body = image.get_data(0x6AF450, functions[0x6AF450] - 0x6AF450)
                self.assertEqual(body.find(bytes.fromhex("68380000")), -1)
                decoder = Cs(CS_ARCH_X86, CS_MODE_64)
                stops = {0x1406920F0, 0x140680C00, 0x14068DA40}
                for instruction in decoder.disasm(body, 0x1406AF450):
                    raw = instruction.bytes
                    if raw and raw[0] == 0xE8 and len(raw) >= 5:
                        target = instruction.address + 5 + int.from_bytes(raw[1:5], "little", signed=True)
                        self.assertNotIn(target, stops)
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_posted_87d0_reads_the_document_without_stopping(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        pefile.MAX_IMPORT_SYMBOLS = 65536
        try:
            with pefile.PE(data=source, fast_load=True) as image:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                imported = {
                    item.address: item.name
                    for lib in image.DIRECTORY_ENTRY_IMPORT
                    for item in lib.imports}
                _, entries = struct.unpack("<QQ", image.get_data(0xEACE80, 16))
                handler = None
                cursor = entries
                while True:
                    record = struct.unpack("<IIIIQQ", image.get_data(cursor - IMAGE_BASE, 32))
                    if record == (0, 0, 0, 0, 0, 0):
                        break
                    if record[0] == 0x87D0:
                        handler = record[5]
                    cursor += 32
                self.assertEqual(handler, 0x1406B0710)
                self.assertEqual(image.get_data(0x6B0746, 7), bytes.fromhex("498b86e8000000"))
                self.assertEqual(image.get_data(0x6B0787, 7), bytes.fromhex("80bd2d38000001"))
                call = image.get_data(0x6B0958, 5)
                self.assertEqual(0x1406B095D + struct.unpack_from("<i", call, 1)[0], 0x140677BA0)
                self.assertEqual(image.get_data(0x677BC9, 2), bytes.fromhex("33d2"))
                self.assertEqual(image.get_data(0x677BD7, 7), bytes.fromhex("4881c140050000"))
                self.assertEqual(image.get_data(0x677BDE, 5)[0], 0xE9)
                self.assertEqual(0x140677BE3 + struct.unpack_from("<i", image.get_data(0x677BDF, 4))[0], 0x140742500)
                invalidate = image.get_data(0x74251E, 16)
                self.assertEqual(invalidate[:4], bytes.fromhex("488b4940"))
                slot = 0x14074252E + struct.unpack_from("<i", invalidate, 12)[0]
                self.assertEqual(imported[slot], b"InvalidateRect")
                functions = {
                    entry.struct.BeginAddress: entry.struct.EndAddress
                    for entry in image.DIRECTORY_ENTRY_EXCEPTION}
                body = image.get_data(0x6B0710, functions[0x6B0710] - 0x6B0710)
                self.assertEqual(body.find(bytes.fromhex("68380000")), -1)
                decoder = Cs(CS_ARCH_X86, CS_MODE_64)
                stops = {0x1406920F0, 0x140680C00, 0x14068DA40}
                for instruction in decoder.disasm(body, 0x1406B0710):
                    raw = instruction.bytes
                    if raw and raw[0] == 0xE8 and len(raw) >= 5:
                        target = instruction.address + 5 + int.from_bytes(raw[1:5], "little", signed=True)
                        self.assertNotIn(target, stops)
                self.assertEqual(image.get_data(0x6B07C1, 7), bytes.fromhex("498b8ea0600000"))
                self.assertEqual(image.get_data(0x6B07D3, 3), bytes.fromhex("ff5008"))
                self.assertEqual(image.get_data(0x6B07E8, 13), bytes.fromhex("498b8ea0600000488b01ff5010"))
                lea = image.get_data(0x6AB7AA, 7)
                self.assertEqual(0x1406AB7B1 + struct.unpack_from("<i", lea, 3)[0], 0x140EAC5B8)
                self.assertEqual(struct.unpack("<QQQ", image.get_data(0xEAC5B8, 24)),
                                 (0x1406ABF50, 0x14076D652, 0x14076D658))
                lock = image.get_data(0x76D652, 6)
                unlock = image.get_data(0x76D658, 6)
                self.assertEqual(imported[0x14076D658 + struct.unpack_from("<i", lock, 2)[0]],
                                 b"?lock@ccSemaphore@@UEAA_NN@Z")
                self.assertEqual(imported[0x14076D65E + struct.unpack_from("<i", unlock, 2)[0]],
                                 b"?unlock@ccSemaphore@@UEAAXXZ")
                self.assertEqual(image.get_data(0x6B0864, 24),
                                 bytes.fromhex("498dbe104c0000488d8f200100004c8b01488bd041ff5010"))
                member = image.get_data(0x67AC70, 19)
                self.assertEqual(member[:12], bytes.fromhex("ba01000000488d8f20010000"))
                self.assertEqual(imported[0x14067AC82 + struct.unpack_from("<i", member, 14)[0]],
                                 b"??0CDPoint@@QEAA@XZ")
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit
        tools_bytes = (ROOT / "v3d_files_" / "BaseTools.dll").read_bytes()
        self.assertEqual(hashlib.sha256(tools_bytes).hexdigest(),
                         "a41b4b00cf464da7da886f2303e6161f4474bda29b32793d39e4c6cfc39547f8")
        with pefile.PE(data=tools_bytes, fast_load=True) as tools:
            self.assertEqual(tools.get_data(0x390B5, 7), bytes.fromhex("488d05c46e0b00"))
            self.assertEqual(0x1800390BC + struct.unpack("<i", bytes.fromhex("c46e0b00"))[0], 0x1800EFF80)
            self.assertEqual(struct.unpack("<Q", tools.get_data(0xEFF90, 8))[0], 0x180039320)
            self.assertEqual(tools.get_data(0x39320, 0x14),
                             bytes.fromhex("488b421048894110488b421848894118488bc1c3"))

    def test_timer_id_1_reads_the_document_and_destroy_kills_id_5(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        pefile.MAX_IMPORT_SYMBOLS = 65536
        try:
            with pefile.PE(data=source, fast_load=True) as image:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                imported = {
                    item.address: item.name
                    for lib in image.DIRECTORY_ENTRY_IMPORT
                    for item in lib.imports}
                _, entries = struct.unpack("<QQ", image.get_data(0xEACE80, 16))
                handler = None
                cursor = entries
                while True:
                    record = struct.unpack("<IIIIQQ", image.get_data(cursor - IMAGE_BASE, 32))
                    if record == (0, 0, 0, 0, 0, 0):
                        break
                    if record[0] == 0x113:
                        handler = record[5]
                    cursor += 32
                self.assertEqual(handler, 0x1406B1F20)
                self.assertEqual(image.get_data(0x6B1F53, 7), bytes.fromhex("488b83e8000000"))
                self.assertEqual(image.get_data(0x6B1FC7, 6), bytes.fromhex("4883ff017549"))
                self.assertEqual(image.get_data(0x6B1FCD, 7), bytes.fromhex("488b8ba0600000"))
                self.assertEqual(image.get_data(0x6B1FDF, 3), bytes.fromhex("ff5008"))
                functions = {
                    entry.struct.BeginAddress: entry.struct.EndAddress
                    for entry in image.DIRECTORY_ENTRY_EXCEPTION}
                body = image.get_data(0x6B1F20, functions[0x6B1F20] - 0x6B1F20)
                self.assertEqual(body.find(bytes.fromhex("68380000")), -1)
                decoder = Cs(CS_ARCH_X86, CS_MODE_64)
                stops = {0x1406920F0, 0x140680C00, 0x14068DA40}
                for instruction in decoder.disasm(body, 0x1406B1F20):
                    raw = instruction.bytes
                    if raw and raw[0] == 0xE8 and len(raw) >= 5:
                        target = instruction.address + 5 + int.from_bytes(raw[1:5], "little", signed=True)
                        self.assertNotIn(target, stops)
                kill = image.get_data(0x6AF391, 13)
                self.assertEqual(kill[:3], bytes.fromhex("8d5705"))
                self.assertEqual(kill[3:7], bytes.fromhex("488b4e40"))
                self.assertEqual(imported[0x1406AF39E + struct.unpack_from("<i", kill, 9)[0]], b"KillTimer")
                for rva in (0x68D9D0, 0x67FC20, 0x6ABC60):
                    span = image.get_data(rva, functions[rva] - rva)
                    for instruction in decoder.disasm(span, IMAGE_BASE + rva):
                        raw = instruction.bytes
                        if raw and len(raw) >= 6 and raw[0] == 0xFF and raw[1] == 0x15:
                            slot = instruction.address + 6 + int.from_bytes(raw[2:6], "little", signed=True)
                            self.assertNotEqual(imported.get(slot), b"KillTimer")
                self.assertEqual(struct.unpack("<Q", image.get_data(0xEAC650, 8))[0], 0x1406AC4B0)
                self.assertEqual(struct.unpack("<Q", image.get_data(0xEAC978, 8))[0], 0x1406AF770)
                self.assertEqual(0xEAC978 - 0xEAC650, 0x328)
                name = image.get_data(0x6AF797, 7)
                self.assertEqual(0x1406AF79E + struct.unpack_from("<i", name, 3)[0], 0x140EACEA0)
                self.assertEqual(image.get_data(0xEACEA0, 32), b"CProductionView::OnInitialUpdate")
                self.assertEqual(image.get_data(0x6B012D, 13), bytes.fromhex("4533c9418d510141b8e8030000"))
                self.assertEqual(image.get_data(0x6B0144, 11), bytes.fromhex("4533c9418d5108458d4132"))
                self.assertEqual(image.get_data(0x6B0159, 14), bytes.fromhex("498b87e800000080b82d38000000"))
                branch = image.get_data(0x6B0167, 6)
                self.assertEqual(branch[:2], bytes.fromhex("0f85"))
                self.assertEqual(0x1406B016D + struct.unpack_from("<i", branch, 2)[0], 0x1406B0230)
                self.assertEqual(image.get_data(0x6B0230, 8), bytes.fromhex("4983bfe800000000"))
                initial = image.get_data(0x6AF770, functions[0x6AF770] - 0x6AF770)
                self.assertEqual(initial.find(bytes.fromhex("68380000")), -1)
                for instruction in decoder.disasm(initial, 0x1406AF770):
                    raw = instruction.bytes
                    if raw and raw[0] == 0xE8 and len(raw) >= 5:
                        target = instruction.address + 5 + int.from_bytes(raw[1:5], "little", signed=True)
                        self.assertNotIn(target, stops)
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit


    def test_only_document_slot_28_calls_production_stop(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        stops = {0x1406920F0, 0x140680C00, 0x14068DA40}
        with pefile.PE(data=source, fast_load=True) as image:
            image.parse_data_directories(directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
            functions = {
                entry.struct.BeginAddress: entry.struct.EndAddress
                for entry in image.DIRECTORY_ENTRY_EXCEPTION}
            text = next(section for section in image.sections if section.Name.startswith(b".text"))
            text_lo = text.VirtualAddress
            text_hi = text_lo + text.Misc_VirtualSize
            decoder = Cs(CS_ARCH_X86, CS_MODE_64)

            def hits(base):
                found = []
                offset = 0
                while offset < 0x800:
                    slot = struct.unpack("<Q", image.get_data(base + offset, 8))[0]
                    rva = slot - IMAGE_BASE
                    if not (text_lo <= rva < text_hi):
                        return found, offset // 8
                    if rva in functions:
                        body = image.get_data(rva, functions[rva] - rva)
                        address = slot
                    else:
                        body = image.get_data(rva, 0x20)
                        address = slot
                    for instruction in decoder.disasm(body, address):
                        raw = instruction.bytes
                        if raw and raw[0] in (0xE8, 0xE9) and len(raw) >= 5:
                            target = instruction.address + 5 + int.from_bytes(raw[1:5], "little", signed=True)
                            if target in stops:
                                found.append((offset, slot, target))
                        if rva not in functions and instruction.mnemonic in ("ret", "jmp"):
                            break
                    offset += 8
                self.fail("vtable did not end")

            document_hits, document_count = hits(0xEA3868)
            view_hits, view_count = hits(0xEAC650)
            self.assertEqual(document_count, 83)
            self.assertEqual(view_count, 113)
            self.assertEqual(document_hits, [(0x28, 0x14068DA40, 0x1406920F0)])
            self.assertEqual(view_hits, [])

    def test_ccapm_slot_1c8_calls_ask_to_stop_only_after_a_high_mode(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        self.assertEqual(source.count(struct.pack("<Q", 0x14075EFD0)), 1)
        with pefile.PE(data=source, fast_load=True) as image:
            image.parse_data_directories(directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
            functions = {
                entry.struct.BeginAddress: entry.struct.EndAddress
                for entry in image.DIRECTORY_ENTRY_EXCEPTION}
            self.assertEqual(struct.unpack("<Q", image.get_data(0xEDDBD0 + 0x1C8, 8))[0], 0x14075EFD0)
            sequence = image.get_data(0x75F05C, 0x21)
            self.assertEqual(sequence[:5], bytes.fromhex("83f8067e20"))
            self.assertEqual(0x14075F061 + 0x20, 0x14075F081)
            self.assertEqual(sequence[5:12], bytes.fromhex("488d4ef8488b01"))
            self.assertEqual(sequence[14:20], bytes.fromhex("ff90e0000000"))
            self.assertEqual(sequence[20:], bytes.fromhex("488d8848250000488b01ff5008"))
            for rva, size in (
                    (0x68D9D0, functions[0x68D9D0] - 0x68D9D0),
                    (0x67FC20, functions[0x67FC20] - 0x67FC20),
                    (0x6AF270, functions[0x6AF270] - 0x6AF270),
                    (0x6ABC60, functions[0x6ABC60] - 0x6ABC60),
                    (0x6B0C00, functions[0x6B0C00] - 0x6B0C00),
                    (0x4E03F0, 0x160)):
                self.assertEqual(image.get_data(rva, size).find(bytes.fromhex("c8010000")), -1)

    def test_doc_compose_constructor_does_not_call_ask_to_stop(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        with pefile.PE(data=source, fast_load=True) as image:
            self.assertEqual(image.get_data(0xE774F0, 12), b"CDocCompose\x00")
            self.assertEqual(struct.unpack("<Q", image.get_data(0xE76010, 8))[0], 0x140E774F0)
            self.assertEqual(struct.unpack("<Q", image.get_data(0xE76020, 8))[0], 0x1405D1A20)
            self.assertEqual(image.get_data(0x5D1A2D, 5), bytes.fromhex("b9c0510000"))
            call = image.get_data(0x5D1A44, 5)
            self.assertEqual(0x1405D1A49 + struct.unpack_from("<i", call, 1)[0], 0x1405CB880)
            store = image.get_data(0x5CB8CB, 14)
            self.assertEqual(store[:3], bytes.fromhex("488d05"))
            self.assertEqual(0x1405CB8D2 + struct.unpack_from("<i", store, 3)[0], 0x140E76370)
            self.assertEqual(store[7:], bytes.fromhex("49898648250000"))
            self.assertEqual(struct.unpack("<Q", image.get_data(0xE76378, 8))[0], 0x140611CE0)
            self.assertNotEqual(0x140611CE0, 0x140680C00)
            self.assertEqual(image.get_data(0x5CBB2B, 10), bytes.fromhex("498d9648250000ff5008"))

    def test_ccapm_slot_b0_calls_ask_to_stop_only_for_ebx_4(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        with pefile.PE(data=source, fast_load=True) as image:
            image.parse_data_directories(directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
            functions = {
                entry.struct.BeginAddress: entry.struct.EndAddress
                for entry in image.DIRECTORY_ENTRY_EXCEPTION}
            self.assertEqual(struct.unpack("<Q", image.get_data(0xEDDBD0 + 0xB0, 8))[0], 0x14075DEE0)
            thunk = image.get_data(0x75DEE0, 9)
            self.assertEqual(thunk[:4], bytes.fromhex("4883c110"))
            self.assertEqual(0x14075DEE9 + struct.unpack_from("<i", thunk, 5)[0], 0x1404C7580)
            self.assertEqual(image.get_data(0x4C75E0, 12), bytes.fromhex("488b4310482b430848c1f807"))
            compare = image.get_data(0x4C75EC, 6)
            self.assertEqual(compare, bytes.fromhex("4883f8027327"))
            self.assertEqual(0x1404C75F2 + 0x27, 0x1404C7619)
            call = image.get_data(0x4C7622, 9)
            self.assertEqual(call[:4], bytes.fromhex("488b4b08"))
            self.assertEqual(0x1404C762B + struct.unpack_from("<i", call, 5)[0], 0x1404C2640)
            self.assertEqual(image.get_data(0x4C73EA, 18), bytes.fromhex("83fb047518498d8d48250000488b01ff5008"))
            decoder = Cs(CS_ARCH_X86, CS_MODE_64)
            for rva, size in (
                    (0x68D9D0, functions[0x68D9D0] - 0x68D9D0),
                    (0x67FC20, functions[0x67FC20] - 0x67FC20),
                    (0x6AF270, functions[0x6AF270] - 0x6AF270),
                    (0x6ABC60, functions[0x6ABC60] - 0x6ABC60),
                    (0x6B0C00, functions[0x6B0C00] - 0x6B0C00),
                    (0x4E03F0, 0x160)):
                for instruction in decoder.disasm(image.get_data(rva, size), IMAGE_BASE + rva):
                    if instruction.mnemonic == "call" and instruction.op_str.endswith("+ 0xb0]"):
                        self.fail(hex(instruction.address))

    def test_queued_2548_callback_is_not_called_by_kill(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        tools_bytes = (ROOT / "v3d_files_" / "BaseTools.dll").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        self.assertEqual(hashlib.sha256(tools_bytes).hexdigest(),
                         "a41b4b00cf464da7da886f2303e6161f4474bda29b32793d39e4c6cfc39547f8")
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        pefile.MAX_IMPORT_SYMBOLS = 65536
        try:
            with pefile.PE(data=source, fast_load=True) as image, pefile.PE(
                    data=tools_bytes, fast_load=True) as tools:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
                imported = {
                    item.address: item.name
                    for lib in image.DIRECTORY_ENTRY_IMPORT
                    for item in lib.imports}
                lea = image.get_data(0x68D593, 7)
                self.assertEqual(lea[:3], bytes.fromhex("488d05"))
                self.assertEqual(0x14068D59A + struct.unpack_from("<i", lea, 3)[0], 0x140682FF0)
                call = image.get_data(0x6A43B3, 5)
                self.assertEqual(0x1406A43B8 + struct.unpack_from("<i", call, 1)[0], 0x14068D550)
                self.assertEqual(image.get_data(0x68D5FD, 4), bytes.fromhex("4883c801"))
                enqueue = image.get_data(0x68D6D7, 20)
                self.assertEqual(enqueue[:7], bytes.fromhex("488d8b28610000"))
                self.assertEqual(imported[0x14068D6EB + struct.unpack_from("<i", enqueue, 16)[0]],
                                 b"?EnqueueCommand@CAsynchCommandExecution@@QEAA_NVCCommandContainer@@_N@Z")
                self.assertEqual(image.get_data(0x683217, 22),
                                 bytes.fromhex("83bb180e0000017527488d8b48250000488b01ff5008"))
                functions = {
                    entry.struct.BeginAddress: entry.struct.EndAddress
                    for entry in image.DIRECTORY_ENTRY_EXCEPTION}
                kill = image.get_data(0x67FD44, 13)
                self.assertEqual(kill[:7], bytes.fromhex("488d8b28610000"))
                self.assertEqual(imported[0x14067FD51 + struct.unpack_from("<i", kill, 9)[0]],
                                 b"?Kill@CAsynchCommandExecution@@QEAA_NXZ")
                self.assertEqual(tools.get_data(0x71EC, 4), bytes.fromhex("a801751c"))
                self.assertEqual(0x1800071F0 + 0x1C, 0x18000720C)
                self.assertEqual(image.get_data(0x68D9D0, functions[0x68D9D0] - 0x68D9D0).find(
                    bytes.fromhex("28610000")), -1)
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_byte_382d_does_not_abort_the_running_producer(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        pefile.MAX_IMPORT_SYMBOLS = 65536
        try:
            image = pefile.PE(data=source, fast_load=True)
            image.parse_data_directories(directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
            imports = {
                item.address: item.name.decode() if item.name else None
                for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
            producer = next(item.struct for item in image.DIRECTORY_ENTRY_EXCEPTION
                            if item.struct.BeginAddress == 0x6A20D0)
            self.assertEqual(producer.EndAddress - producer.BeginAddress, 0x2877)
            self.assertEqual(image.get_data(0x6A20D0, 0x2877).find(bytes.fromhex("2d380000")), -1)
            self.assertEqual(image.get_data(0x6921E0, 2), bytes.fromhex("33f6"))
            self.assertEqual(image.get_data(0x69234C, 44), bytes.fromhex(
                "80bb813800000175354088b3813800004038b32d3800000f94c088832d380000"
                "4533c933d2458d4101488bcb"))
            self.assertEqual(0x140692355 + 0x35, 0x14069238A)
            restart = image.get_data(0x692380, 5)
            self.assertEqual(restart[0], 0xE8)
            self.assertEqual(0x140692385 + struct.unpack_from("<i", restart, 1)[0], 0x140691C80)
            self.assertEqual(image.get_data(0x691D01, 3), bytes.fromhex("4533e4"))
            self.assertEqual(image.get_data(0x691F1F, 9), bytes.fromhex("80be2d380000017443"))
            self.assertEqual(0x140691F28 + 0x43, 0x140691F6B)
            self.assertEqual(image.get_data(0x691F6B, 7), bytes.fromhex("4c89a660380000"))
            self.assertEqual(image.get_data(0x691F83, 11), bytes.fromhex("80be2d38000000490f44df"))
            span = image.get_data(0x691F6B, 0x691FF1 - 0x691F6B)
            for instruction in Cs(CS_ARCH_X86, CS_MODE_64).disasm(span, 0x140691F6B):
                self.assertNotEqual(instruction.mnemonic, "ret")
                if instruction.mnemonic == "jmp":
                    self.assertLessEqual(int(instruction.op_str, 16), 0x140691FF1)
            self.assertEqual(image.get_data(0x691FF1, 7), bytes.fromhex("48898668380000"))
            self.assertEqual(image.get_data(0x692006, 7), bytes.fromhex("488b8e68380000"))
            self.assertEqual(image.get_data(0x692018, 6), bytes.fromhex("488b01ff5010"))
            kept = image.get_data(0x691D04, 0x691F6B - 0x691D04)
            for instruction in Cs(CS_ARCH_X86, CS_MODE_64).disasm(kept, 0x140691D04):
                destination = instruction.op_str.split(",", 1)[0].strip()
                self.assertNotIn(destination, ("r12", "r12d", "r12w", "r12b"))
            self.assertEqual(struct.unpack("<Q", image.get_data(0xEA3968, 8))[0], 0x14068DAB0)
            self.assertEqual(0xEA3968 - 0xEA3868, 0x100)
            self.assertEqual(image.get_data(0x68DBE2, 13), bytes.fromhex("0fb68898010000888b2d380000"))
            self.assertEqual(image.get_data(0x68DBC9, 14), bytes.fromhex("4c8d0d2075a4004c8d05f974a400"))
            self.assertEqual(0x14068DBD0 + struct.unpack("<i", bytes.fromhex("2075a400"))[0], 0x1410D50F0)
            self.assertEqual(0x14068DBD7 + struct.unpack("<i", bytes.fromhex("f974a400"))[0], 0x1410D50D0)
            self.assertEqual(image.get_data(0x10D5100, 18), b".?AVCAVisionApp@@\x00")
            self.assertEqual(image.get_data(0x10D50E0, 14), b".?AVCWinApp@@\x00")
            cast = image.get_data(0x68DBDD, 5)
            self.assertEqual(cast[0], 0xE8)
            thunk = 0x14068DBE2 + struct.unpack_from("<i", cast, 1)[0]
            self.assertEqual(thunk, 0x1407A6238)
            slot = image.get_data(thunk - IMAGE_BASE, 6)
            self.assertEqual(slot[:2], b"\xff\x25")
            self.assertEqual(imports[thunk + 6 + struct.unpack_from("<i", slot, 2)[0]], "__RTDynamicCast")
            decoder = Cs(CS_ARCH_X86, CS_MODE_64)
            spans = {0x1404E03F0: 0x160}
            for item in image.DIRECTORY_ENTRY_EXCEPTION:
                start = IMAGE_BASE + item.struct.BeginAddress
                if start in (0x14068D9D0, 0x14067FC20, 0x1406AF270, 0x1406ABC60, 0x1406B0C00):
                    spans[start] = item.struct.EndAddress - item.struct.BeginAddress
            self.assertEqual(set(spans), {
                0x1404E03F0, 0x14068D9D0, 0x14067FC20, 0x1406AF270, 0x1406ABC60, 0x1406B0C00})
            for start, size in spans.items():
                for instruction in decoder.disasm(image.get_data(start - IMAGE_BASE, size), start):
                    if instruction.mnemonic in ("call", "jmp") and instruction.op_str.endswith("+ 0x100]"):
                        self.fail(hex(instruction.address))
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_reload_doc_flag_restarts_workers_without_close(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        image = pefile.PE(data=source, fast_load=True)
        image.parse_data_directories(directories=[
            pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
        text = next(section for section in image.sections if section.Name.startswith(b".text"))
        text_data = text.get_data()
        text_base = IMAGE_BASE + text.VirtualAddress
        needle = bytes.fromhex("30580000")
        sites = []
        start = 0
        while True:
            index = text_data.find(needle, start)
            if index < 0:
                break
            if text_data[index - 1] not in (0xE8, 0xE9):
                sites.append(text_base + index)
            start = index + 1
        self.assertEqual(sites, [0x14067E257, 0x14068BD63, 0x14068BD69, 0x140692BCD])
        self.assertEqual(image.get_data(0x67E254, 7), bytes.fromhex("4488b630580000"))
        self.assertEqual(image.get_data(0x692BCB, 7), bytes.fromhex("c6863058000001"))
        self.assertEqual(image.get_data(0x68BD60, 15), bytes.fromhex("0fb68130580000c6813058000000c3"))
        reload_doc = next(item.struct for item in image.DIRECTORY_ENTRY_EXCEPTION
                          if item.struct.BeginAddress == 0x692AF0)
        self.assertLess(reload_doc.BeginAddress, 0x692BCB)
        self.assertLess(0x692BCB, reload_doc.EndAddress)
        self.assertEqual(image.get_data(0x69C8F4, 16), bytes.fromhex("488bcfe8d44c0000488bc8e85cf4feff"))
        self.assertEqual(0x14069C8FC + struct.unpack("<i", bytes.fromhex("d44c0000"))[0], 0x1406A15D0)
        self.assertEqual(0x14069C904 + struct.unpack("<i", bytes.fromhex("5cf4feff"))[0], 0x14068BD60)
        self.assertEqual(image.get_data(0x69C904, 2), bytes.fromhex("84c0"))
        self.assertEqual(image.get_data(0x69C90E, 14), bytes.fromhex("33d2488d8fc80e0000e8b4d00000"))
        self.assertEqual(0x14069C91C + struct.unpack("<i", bytes.fromhex("b4d00000"))[0], 0x1406A99D0)
        self.assertEqual(image.get_data(0x6A99F2, 10), bytes.fromhex("3b51387470e884bffaff"))
        self.assertEqual(0x1406A99FC + struct.unpack("<i", bytes.fromhex("84bffaff"))[0], 0x140655980)
        producer = next(item.struct for item in image.DIRECTORY_ENTRY_EXCEPTION
                        if item.struct.BeginAddress == 0x6A20D0)
        blob = image.get_data(producer.BeginAddress, producer.EndAddress - producer.BeginAddress)
        calls = []
        for index in range(len(blob) - 5):
            if blob[index] != 0xE8:
                continue
            dest = IMAGE_BASE + producer.BeginAddress + index + 5 + struct.unpack_from("<i", blob, index + 1)[0]
            if dest == 0x14069C890:
                calls.append(IMAGE_BASE + producer.BeginAddress + index)
        self.assertEqual(calls, [0x1406A28F5, 0x1406A319F])
        checker_next = list(Cs(CS_ARCH_X86, CS_MODE_64).disasm(image.get_data(0x6A28FA, 16), 0x1406A28FA))
        self.assertEqual(checker_next[0].mnemonic, "cmp")
        self.assertIn("0x770", checker_next[0].op_str)
        self.assertNotIn("0x5830", checker_next[0].op_str)
        spans = {0x1404E03F0: 0x160}
        for item in image.DIRECTORY_ENTRY_EXCEPTION:
            start = IMAGE_BASE + item.struct.BeginAddress
            if start in (0x14068D9D0, 0x14067FC20, 0x1406AF270, 0x1406ABC60, 0x1406B0C00):
                spans[start] = item.struct.EndAddress - item.struct.BeginAddress
        for origin, size in spans.items():
            body = image.get_data(origin - IMAGE_BASE, size)
            for index in range(len(body) - 5):
                if body[index] != 0xE8:
                    continue
                dest = origin + index + 5 + struct.unpack_from("<i", body, index + 1)[0]
                self.assertNotIn(dest, (0x140692AF0, 0x14069C890))

    def test_only_production_stop_joins_the_document_producer(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        pefile.MAX_IMPORT_SYMBOLS = 65536
        try:
            image = pefile.PE(data=source, fast_load=True)
            image.parse_data_directories(directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
            imports = {
                item.address: item.name.decode() if item.name else None
                for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
            text = next(section for section in image.sections if section.Name.startswith(b".text"))
            text_data = text.get_data()
            text_base = IMAGE_BASE + text.VirtualAddress
            sites = []
            start = 0
            while True:
                index = text_data.find(b"\xff\x15", start)
                if index < 0 or index + 6 > len(text_data):
                    break
                iat = text_base + index + 6 + struct.unpack_from("<i", text_data, index + 2)[0]
                if iat == 0x140D53470:
                    sites.append(text_base + index)
                start = index + 1
            self.assertEqual(sites, [
                0x1404E30D5, 0x14062951C, 0x1406530B0, 0x140653190, 0x140680E22,
                0x140692204, 0x1406922B2, 0x14069A13D, 0x1406E8F45])
            self.assertEqual(imports[0x140D53470], "?Stop@CViThread@@QEAA_NAEAKK@Z")
            functions = {
                IMAGE_BASE + item.struct.BeginAddress: IMAGE_BASE + item.struct.EndAddress
                for item in image.DIRECTORY_ENTRY_EXCEPTION}
            owners = {}
            for site in sites:
                owners[site] = next(origin for origin, end in functions.items() if origin <= site < end)
            self.assertEqual(owners[0x140692204], 0x1406920F0)
            self.assertEqual(owners[0x1406922B2], 0x1406920F0)
            producer = image.get_data(0x6920F0, functions[0x1406920F0] - 0x1406920F0)
            self.assertNotEqual(producer.find(bytes.fromhex("488b8b68380000")), -1)
            for origin in (0x1404E3070, 0x140629490, 0x140653080, 0x140653160,
                           0x140680D70, 0x14069A110, 0x1406E8EE0):
                body = image.get_data(origin - IMAGE_BASE, functions[origin] - origin)
                self.assertEqual(body.find(bytes.fromhex("68380000")), -1, hex(origin))
            self.assertEqual(image.get_data(0x4E30C0, 7), bytes.fromhex("488b89b0410000"))
            self.assertEqual(image.get_data(0x62950C, 7), bytes.fromhex("488d8ff0000000"))
            self.assertEqual(image.get_data(0x6E8F30, 7), bytes.fromhex("488b89400a0000"))
            self.assertEqual(image.get_data(0x6530A7, 9), bytes.fromhex("4183c8ff488d542440"))
            self.assertEqual(image.get_data(0x653187, 9), bytes.fromhex("4183c8ff488d542440"))

            def rtti_name(vtable: int) -> bytes:
                locator = struct.unpack("<Q", image.get_data(vtable - IMAGE_BASE - 8, 8))[0]
                descriptor = struct.unpack("<I", image.get_data(locator - IMAGE_BASE + 12, 4))[0]
                blob = image.get_data(descriptor, 96)
                begin = blob.find(b".?A")
                return blob[begin:blob.find(b"\x00", begin)]

            self.assertEqual(image.get_data(0x4E308C, 7), bytes.fromhex("488d058dad9500"))
            self.assertEqual(0x1404E3093 + struct.unpack("<i", bytes.fromhex("8dad9500"))[0], 0x140E3DE20)
            self.assertEqual(rtti_name(0x140E3DE20), b".?AVCCAD_Zone2D_PropSheet@@")
            self.assertEqual(image.get_data(0x6E8EFC, 7), bytes.fromhex("488d0555297d00"))
            self.assertEqual(0x1406E8F03 + struct.unpack("<i", bytes.fromhex("55297d00"))[0], 0x140EBB858)
            self.assertEqual(rtti_name(0x140EBB858), b".?AVCWizardGenericElement@@")
            self.assertEqual(image.get_data(0x653097, 7), bytes.fromhex("488d05025d8400"))
            self.assertEqual(0x14065309E + struct.unpack("<i", bytes.fromhex("025d8400"))[0], 0x140E98DA0)
            self.assertEqual(rtti_name(0x140E98DA0),
                             b".?AV?$CViThread4Pool@VCPCBR_Data2DInit@@VCWorkingDataImage@@@@")
            self.assertEqual(image.get_data(0x653177, 7), bytes.fromhex("488d059a5c8400"))
            self.assertEqual(0x14065317E + struct.unpack("<i", bytes.fromhex("9a5c8400"))[0], 0x140E98E18)
            self.assertEqual(rtti_name(0x140E98E18),
                             b".?AV?$CViThread4Pool@VCPCBR_Data3DInit@@VCWorkingDataImage@@@@")
            self.assertEqual(image.get_data(0x6294AC, 7), bytes.fromhex("488d159d1b8600"))
            self.assertEqual(0x1406294B3 + struct.unpack("<i", bytes.fromhex("9d1b8600"))[0], 0x140E8B050)
            self.assertEqual(image.get_data(0xE8B050, 23), b"CLogManagerView::Close\x00")
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_stop_waits_on_the_thread_handle_and_close_does_not(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        library = (ROOT / "v3d_files_" / "BaseTools.dll").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        self.assertEqual(hashlib.sha256(library).hexdigest(),
                         "a41b4b00cf464da7da886f2303e6161f4474bda29b32793d39e4c6cfc39547f8")
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        pefile.MAX_IMPORT_SYMBOLS = 65536
        try:
            image = pefile.PE(data=source, fast_load=True)
            tools = pefile.PE(data=library, fast_load=True)
            image.parse_data_directories(directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
            tools.parse_data_directories(directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
            imports = {
                item.address: item.name.decode() if item.name else None
                for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
            tool_imports = {
                item.address: item.name.decode() if item.name else None
                for entry in tools.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
            self.assertEqual(tools.get_data(0x7E1AA, 19), bytes.fromhex(
                "4883790800418bf8488bd97447488b4918ff15"))
            self.assertEqual(tools.get_data(0x7E1C1, 12), bytes.fromhex("488b4b088bd7488b4958ff15"))
            self.assertEqual(tools.get_data(0x7E147, 4), bytes.fromhex("48894308"))
            self.assertEqual(tools.get_data(0x7E171, 10), bytes.fromhex("488b4b08488b4958ff15"))
            self.assertEqual(tools.get_data(0x1E880, 5), bytes.fromhex("488b4118c3"))
            for call, name in ((0x18007E1BB, "SetEvent"), (0x18007E1CB, "WaitForSingleObject"),
                               (0x18007E179, "ResumeThread")):
                slot = tools.get_data(call - 0x180000000, 6)
                self.assertEqual(slot[:2], b"\xff\x15")
                self.assertEqual(tool_imports[call + 6 + struct.unpack_from("<i", slot, 2)[0]], name)
            text = next(section for section in image.sections if section.Name.startswith(b".text"))
            text_data = text.get_data()
            for pattern, count in (
                    (bytes.fromhex("4c89b6d8610000"), 1),
                    (bytes.fromhex("488986d8610000"), 1),
                    (bytes.fromhex("488b8bd8610000"), 1)):
                found = 0
                start = 0
                while True:
                    index = text_data.find(pattern, start)
                    if index < 0:
                        break
                    found += 1
                    start = index + 1
                self.assertEqual(found, count)
            self.assertEqual(image.get_data(0x67E183, 7), bytes.fromhex("4c89b6d8610000"))
            self.assertEqual(image.get_data(0x692006, 18), bytes.fromhex(
                "488b8e68380000488b4118488986d8610000"))
            self.assertEqual(image.get_data(0x692198, 9), bytes.fromhex("33d2488b8bd8610000"))
            wait = image.get_data(0x6921A1, 6)
            self.assertEqual(wait[:2], b"\xff\x15")
            self.assertEqual(imports[0x1406921A7 + struct.unpack_from("<i", wait, 2)[0]],
                             "WaitForSingleObject")
            spans = {0x1404E03F0: 0x160}
            for item in image.DIRECTORY_ENTRY_EXCEPTION:
                origin = IMAGE_BASE + item.struct.BeginAddress
                if origin in (0x14068D9D0, 0x14067FC20, 0x1406AF270, 0x1406ABC60, 0x1406B0C00):
                    spans[origin] = item.struct.EndAddress - item.struct.BeginAddress
            for origin, size in spans.items():
                self.assertEqual(image.get_data(origin - IMAGE_BASE, size).find(bytes.fromhex("d8610000")), -1)
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_grey_zone_destructor_frees_the_worker_without_clearing_the_document(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        image = pefile.PE(data=source, fast_load=True)
        image.parse_data_directories(directories=[
            pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
        self.assertEqual(struct.unpack("<Q", image.get_data(0xEA8A10, 8))[0], 0x14069A890)
        self.assertEqual(image.get_data(0x6997FE, 10), bytes.fromhex("33c04889472048894728"))
        self.assertEqual(image.get_data(0x6A49D7, 8), bytes.fromhex("498b460848894328"))
        functions = {
            IMAGE_BASE + item.struct.BeginAddress: IMAGE_BASE + item.struct.EndAddress
            for item in image.DIRECTORY_ENTRY_EXCEPTION}
        decoder = Cs(CS_ARCH_X86, CS_MODE_64)
        decoder.detail = True
        body = image.get_data(0x69A890, functions[0x14069A890] - 0x14069A890)
        for instruction in decoder.disasm(body, 0x14069A890):
            if not instruction.mnemonic.startswith("mov") or len(instruction.operands) != 2:
                continue
            destination = instruction.operands[0]
            if destination.type != 3 or destination.mem.disp != 0x28:
                continue
            self.assertIn(instruction.reg_name(destination.mem.base), ("rsp", "rbp"))
        stop = image.get_data(0x69A8BF, 5)
        self.assertEqual(stop[0], 0xE8)
        self.assertEqual(0x14069A8C4 + struct.unpack_from("<i", stop, 1)[0], 0x14069A110)
        self.assertEqual(image.get_data(0x69A8C4, 15), bytes.fromhex("40f6c701740dbad8000000488bcee8"))
        free = image.get_data(0x69A8D2, 5)
        self.assertEqual(free[0], 0xE8)
        self.assertEqual(0x14069A8D7 + struct.unpack_from("<i", free, 1)[0], 0x1404556C0)
        text = next(section for section in image.sections if section.Name.startswith(b".text"))
        text_data = text.get_data()
        text_base = IMAGE_BASE + text.VirtualAddress
        callers = []
        start = 0
        while True:
            index = text_data.find(b"\xe8", start)
            if index < 0 or index + 5 > len(text_data):
                break
            if text_base + index + 5 + struct.unpack_from("<i", text_data, index + 1)[0] == 0x14069A890:
                callers.append(text_base + index)
            start = index + 1
        self.assertEqual(callers, [])
        spans = {0x1404E03F0: 0x160}
        for item in image.DIRECTORY_ENTRY_EXCEPTION:
            origin = IMAGE_BASE + item.struct.BeginAddress
            if origin in (0x14068D9D0, 0x14067FC20, 0x1406AF270, 0x1406ABC60, 0x1406B0C00):
                spans[origin] = item.struct.EndAddress - item.struct.BeginAddress
        for origin, size in spans.items():
            blob = image.get_data(origin - IMAGE_BASE, size)
            for index in range(len(blob) - 5):
                if blob[index] != 0xE8:
                    continue
                dest = origin + index + 5 + struct.unpack_from("<i", blob, index + 1)[0]
                self.assertNotEqual(dest, 0x140655980)

    def test_close_does_not_wake_or_join_an_idle_grey_zone_worker(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        pefile.MAX_IMPORT_SYMBOLS = 65536
        image = pefile.PE(data=source, fast_load=True)
        image.parse_data_directories(directories=[
            pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
            pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
        imports = {}
        for entry in image.DIRECTORY_ENTRY_IMPORT:
            for imported in entry.imports:
                if imported.name:
                    imports[imported.address] = imported.name.decode()
        self.assertEqual(image.get_data(0x6A1AD0, 19), bytes.fromhex("488b83a0000000488945cf488b4318488945d7"))
        self.assertEqual(image.get_data(0x6A1B60, 15), bytes.fromhex("4183c9ff4533c0488d55cf418d4802"))
        wait = image.get_data(0x6A1B6F, 6)
        self.assertEqual(wait[:2], b"\xff\x15")
        self.assertEqual(imports[0x1406A1B75 + struct.unpack_from("<i", wait, 2)[0]], "WaitForMultipleObjects")
        self.assertEqual(image.get_data(0x6A1B79, 9), bytes.fromhex("85c0743b83f801741b"))
        self.assertEqual(0x1406A1B7D + 0x3B, 0x1406A1BB8)
        self.assertEqual(0x1406A1B82 + 0x1B, 0x1406A1B9D)
        self.assertEqual(image.get_data(0x6A1B94, 7), bytes.fromhex("c683b000000000"))
        self.assertEqual(image.get_data(0x6A1BE4, 9), bytes.fromhex("80bbb000000001755d"))
        self.assertEqual(0x1406A1BED + 0x5D, 0x1406A1C4A)
        self.assertEqual(image.get_data(0x6A1C03, 9), bytes.fromhex("488b03488bcbff5018"))
        self.assertEqual(image.get_data(0x66DBFC, 11), bytes.fromhex("4c8b4f204c8b4728488b57"))
        treat = image.get_data(0x66DC10, 5)
        self.assertEqual(treat[0], 0xE8)
        self.assertEqual(0x14066DC15 + struct.unpack_from("<i", treat, 1)[0], 0x140735120)
        self.assertEqual(image.get_data(0x66DBA1, 2), bytes.fromhex("33f6"))
        self.assertEqual(image.get_data(0x66DCB8, 4), bytes.fromhex("48897758"))
        decoder = Cs(CS_ARCH_X86, CS_MODE_64)
        decoder.detail = True
        for instruction in decoder.disasm(image.get_data(0x66DBA3, 0x66DCB8 - 0x66DBA3), 0x14066DBA3):
            _read, written = instruction.regs_access()
            self.assertFalse(any(instruction.reg_name(reg) in ("rsi", "esi", "si") for reg in written))
        self.assertEqual(image.get_data(0x69FBF4, 9), bytes.fromhex("488d8fc80e0000b201"))
        pooled = image.get_data(0x69FBFD, 5)
        self.assertEqual(pooled[0], 0xE8)
        self.assertEqual(0x14069FC02 + struct.unpack_from("<i", pooled, 1)[0], 0x1406A1660)
        self.assertEqual(image.get_data(0x69FC3B, 7), bytes.fromhex("488d5e78488bcb"))
        section = image.get_data(0x69FC42, 6)
        self.assertEqual(section[:2], b"\xff\x15")
        self.assertEqual(imports[0x14069FC48 + struct.unpack_from("<i", section, 2)[0]], "EnterCriticalSection")
        self.assertEqual(
            image.get_data(0x69FC48, 25),
            bytes.fromhex("0f104424380f1146500f104c24480f114e60488b8ea0000000"))
        signal = image.get_data(0x69FC61, 6)
        self.assertEqual(signal[:2], b"\xff\x15")
        self.assertEqual(imports[0x14069FC67 + struct.unpack_from("<i", signal, 2)[0]], "SetEvent")
        text = next(item for item in image.sections if item.Name.startswith(b".text"))
        text_data = text.get_data()
        text_base = IMAGE_BASE + text.VirtualAddress
        signaled = []
        for rex in (0x48, 0x49):
            for modrm in range(0x88, 0x90):
                pattern = bytes([rex, 0x8B, modrm]) + bytes.fromhex("a0000000")
                start = 0
                while True:
                    index = text_data.find(pattern, start)
                    if index < 0:
                        break
                    if text_data[index + 7:index + 9] == b"\xff\x15":
                        signaled.append(text_base + index)
                    start = index + 1
        self.assertEqual(signaled, [0x14069FC5A])
        wanted = (0x1406A6A30, 0x1406A88E0, 0x14069FB80, 0x1406A1660)
        callers = {target: [] for target in wanted}
        start = 0
        while True:
            index = text_data.find(b"\xe8", start)
            if index < 0 or index + 5 > len(text_data):
                break
            dest = text_base + index + 5 + struct.unpack_from("<i", text_data, index + 1)[0]
            if dest in callers:
                callers[dest].append(text_base + index)
            start = index + 1
        self.assertEqual(callers[0x1406A6A30], [0x1406A39EA])
        self.assertEqual(callers[0x1406A88E0], [0x1406A701F])
        self.assertEqual(callers[0x14069FB80], [0x1406A8F32, 0x1406A9104])
        self.assertEqual(callers[0x1406A1660], [0x14069FBFD])
        functions = {
            IMAGE_BASE + item.struct.BeginAddress: IMAGE_BASE + item.struct.EndAddress
            for item in image.DIRECTORY_ENTRY_EXCEPTION}
        self.assertTrue(0x1406A20D0 <= 0x1406A39EA < functions[0x1406A20D0])
        spans = {0x1404E03F0: 0x160}
        for item in image.DIRECTORY_ENTRY_EXCEPTION:
            origin = IMAGE_BASE + item.struct.BeginAddress
            if origin in (0x14068D9D0, 0x14067FC20, 0x1406AF270, 0x1406ABC60, 0x1406B0C00):
                spans[origin] = item.struct.EndAddress - item.struct.BeginAddress
        for origin, size in spans.items():
            blob = image.get_data(origin - IMAGE_BASE, size)
            for index in range(len(blob) - 5):
                if blob[index] != 0xE8:
                    continue
                dest = origin + index + 5 + struct.unpack_from("<i", blob, index + 1)[0]
                self.assertNotIn(dest, wanted)

    def test_worker_completion_event_has_no_waiter(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        pefile.MAX_IMPORT_SYMBOLS = 65536
        image = pefile.PE(data=source, fast_load=True)
        image.parse_data_directories(directories=[
            pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
            pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
        imports = {}
        for entry in image.DIRECTORY_ENTRY_IMPORT:
            for imported in entry.imports:
                if imported.name:
                    imports[imported.address] = imported.name.decode()

        def import_at(address: int) -> str:
            call = image.get_data(address - IMAGE_BASE, 6)
            self.assertEqual(call[:2], b"\xff\x15")
            return imports[address + 6 + struct.unpack_from("<i", call, 2)[0]]

        self.assertEqual(
            image.get_data(0x69982E, 23),
            bytes.fromhex("4533c94533c033d233c9ff15e2b76b00488987a0000000"))
        self.assertEqual(import_at(0x140699838), "CreateEventA")
        self.assertEqual(
            image.get_data(0x69984C, 39),
            bytes.fromhex("4533c9ba0100000033c9448bc2ff15c1b76b00488987a8000000488d4f78ff1548b76b00488bcf"))
        self.assertEqual(import_at(0x140699859), "CreateEventA")
        self.assertEqual(import_at(0x14069986A), "InitializeCriticalSection")
        self.assertEqual(import_at(0x140699873), "?Start@CViThread@@UEAA_NXZ")
        self.assertEqual(image.get_data(0x6A9A0D, 4), bytes.fromhex("4c8d7f20"))
        self.assertEqual(image.get_data(0x6A9A52, 11), bytes.fromhex("488b82a80000004889040b"))
        self.assertEqual(image.get_data(0x6A1724, 9), bytes.fromhex("488d5520488d4c2438"))
        copied = image.get_data(0x6A172D, 5)
        self.assertEqual(copied[0], 0xE8)
        self.assertEqual(0x1406A1732 + struct.unpack_from("<i", copied, 1)[0], 0x140653BB0)
        self.assertEqual(image.get_data(0x6A17A5, 7), bytes.fromhex("4c89a2b8000000"))
        text = next(item for item in image.sections if item.Name.startswith(b".text"))
        text_data = text.get_data()
        text_base = IMAGE_BASE + text.VirtualAddress
        functions = sorted(
            (IMAGE_BASE + item.struct.BeginAddress, IMAGE_BASE + item.struct.EndAddress)
            for item in image.DIRECTORY_ENTRY_EXCEPTION)
        wait_iats = {slot for slot, name in imports.items()
                     if name in ("WaitForSingleObject", "WaitForMultipleObjects")}

        def owner(address: int) -> int:
            low = 0
            high = len(functions)
            while low < high:
                mid = (low + high) // 2
                if functions[mid][0] <= address:
                    low = mid + 1
                else:
                    high = mid
            if low == 0:
                return 0
            begin, end = functions[low - 1]
            return begin if address < end else 0

        waiting = set()
        start = 0
        while True:
            index = text_data.find(b"\xff\x15", start)
            if index < 0 or index + 6 > len(text_data):
                break
            slot = text_base + index + 6 + struct.unpack_from("<i", text_data, index + 2)[0]
            if slot in wait_iats:
                waiting.add(owner(text_base + index))
            start = index + 1
        loads = []
        pattern = bytes.fromhex("b8000000")
        start = 0
        while True:
            index = text_data.find(pattern, start)
            if index < 3:
                if index < 0:
                    break
                start = index + 1
                continue
            if text_data[index - 3] in (0x48, 0x49, 0x4C, 0x4D) and text_data[index - 2] == 0x8B and text_data[index - 1] >= 0x80:
                loads.append(text_base + index - 3)
            start = index + 1
        self.assertEqual([item for item in loads if owner(item) in waiting], [0x1406A1C0F])
        self.assertEqual(image.get_data(0x6A1C0F, 7), bytes.fromhex("488b8bb8000000"))
        self.assertEqual(import_at(0x1406A1C16), "SetEvent")

    def test_selector_timeout_skips_a_busy_worker(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        image = pefile.PE(data=source, fast_load=True)
        self.assertEqual(0xEC8 + 0x3C, 0xF04)
        self.assertEqual(image.get_data(0x699B6A, 7), bytes.fromhex("488d9fc80e0000"))
        self.assertEqual(image.get_data(0x699A5F, 3), bytes.fromhex("4533f6"))
        self.assertEqual(image.get_data(0x699BA6, 4), bytes.fromhex("4c897338"))
        filled = image.get_data(0x699D87, 5)
        self.assertEqual(filled[0], 0xE8)
        self.assertEqual(0x140699D8C + struct.unpack_from("<i", filled, 1)[0], 0x14058C930)
        self.assertEqual(image.get_data(0x699D8C, 7), bytes.fromhex("8b542440488bcb"))
        resize = image.get_data(0x699D93, 5)
        self.assertEqual(resize[0], 0xE8)
        self.assertEqual(0x140699D98 + struct.unpack_from("<i", resize, 1)[0], 0x1406A99D0)
        self.assertEqual(image.get_data(0x699D98, 14), bytes.fromhex("6944244ce80300008987040f0000"))
        self.assertEqual(
            image.get_data(0x6A1732, 27),
            bytes.fromhex("488b4c2440488b742438482bce48c1f903448b4d3c4533c0488bd6"))
        self.assertEqual(image.get_data(0x6A1753, 9), bytes.fromhex("8bf83d02010000745a"))
        self.assertEqual(0x1406A175C + 0x5A, 0x1406A17B6)
        self.assertLess(0x1406A17A5, 0x1406A17B6)
        self.assertEqual(image.get_data(0x6A17A5, 7), bytes.fromhex("4c89a2b8000000"))

    def test_close_does_not_call_the_cao_reset_site(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        image = pefile.PE(data=source, fast_load=True)
        image.parse_data_directories(directories=[
            pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
        text = next(item for item in image.sections if item.Name.startswith(b".text"))
        text_data = text.get_data()
        text_base = IMAGE_BASE + text.VirtualAddress
        callers = []
        start = 0
        while True:
            index = text_data.find(b"\xe8", start)
            if index < 0 or index + 5 > len(text_data):
                break
            if text_base + index + 5 + struct.unpack_from("<i", text_data, index + 1)[0] == 0x140541050:
                callers.append(text_base + index)
            start = index + 1
        self.assertEqual(callers, [0x1404AEBE9, 0x14068F7D7, 0x1406937D7, 0x1406A085E, 0x1406A2D87])
        functions = {
            IMAGE_BASE + item.struct.BeginAddress: IMAGE_BASE + item.struct.EndAddress
            for item in image.DIRECTORY_ENTRY_EXCEPTION}
        self.assertTrue(0x1406A06B0 <= 0x1406A085E < functions[0x1406A06B0])
        self.assertTrue(0x1406A20D0 <= 0x1406A2D87 < functions[0x1406A20D0])
        self.assertTrue(0x140692AF0 <= 0x1406937D7 < functions[0x140692AF0])
        spans = {0x1404E03F0: 0x160}
        for item in image.DIRECTORY_ENTRY_EXCEPTION:
            origin = IMAGE_BASE + item.struct.BeginAddress
            if origin in (0x14068D9D0, 0x14067FC20, 0x1406AF270, 0x1406ABC60, 0x1406B0C00):
                spans[origin] = item.struct.EndAddress - item.struct.BeginAddress
        for origin, size in spans.items():
            blob = image.get_data(origin - IMAGE_BASE, size)
            for index in range(len(blob) - 5):
                if blob[index] != 0xE8:
                    continue
                dest = origin + index + 5 + struct.unpack_from("<i", blob, index + 1)[0]
                self.assertNotEqual(dest, 0x140541050)

    def test_close_does_not_call_the_nonproducer_reset_parents(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        image = pefile.PE(data=source, fast_load=True)
        image.parse_data_directories(directories=[
            pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
        self.assertEqual(struct.unpack_from("<Q", image.get_data(0xEA3970, 8))[0], 0x14068DC20)
        self.assertEqual(struct.unpack_from("<Q", image.get_data(0xEA3968, 8))[0], 0x14068DAB0)
        self.assertEqual(image.get_data(0x68DC4E, 6), bytes.fromhex("4c8bf2488bf1"))
        self.assertEqual(image.get_data(0x68DC61, 7), bytes.fromhex("4489a144380000"))
        call = image.get_data(0x68DC98, 8)
        self.assertEqual(call[:4], bytes.fromhex("488bcee8"))
        self.assertEqual(0x14068DCA0 + struct.unpack_from("<i", call, 4)[0], 0x140697200)
        call = image.get_data(0x68E278, 8)
        self.assertEqual(call[:4], bytes.fromhex("488bcee8"))
        self.assertEqual(0x14068E280 + struct.unpack_from("<i", call, 4)[0], 0x14068F0F0)
        parent = next(item for item in image.DIRECTORY_ENTRY_EXCEPTION
                      if IMAGE_BASE + item.struct.BeginAddress == 0x14068DC20)
        body = image.get_data(0x68DC20, parent.struct.EndAddress - parent.struct.BeginAddress)
        self.assertEqual(body.find(bytes.fromhex("68380000")), -1)
        self.assertEqual(struct.unpack_from("<Q", image.get_data(0xEDDBD0 + 0xB0, 8))[0], 0x14075DEE0)
        self.assertEqual(struct.unpack_from("<Q", image.get_data(0xEDDC50, 8))[0], 0x14075AD60)
        thunk = image.get_data(0x75AD60, 9)
        self.assertEqual(thunk[:5], bytes.fromhex("4883c110e9"))
        self.assertEqual(0x14075AD69 + struct.unpack_from("<i", thunk, 5)[0], 0x1404AECD0)
        self.assertEqual(image.get_data(0x4AED20, 16), bytes.fromhex("488b4310482b430848c1f8074883f802"))
        call = image.get_data(0x4AED59, 12)
        self.assertEqual(call[:8], bytes.fromhex("488bd7488b4b08e8"))
        self.assertEqual(0x1404AED65 + struct.unpack_from("<i", call, 8)[0], 0x1404AE9D0)
        call = image.get_data(0x4AEBE6, 8)
        self.assertEqual(call[:4], bytes.fromhex("488bcee8"))
        self.assertEqual(0x1404AEBEE + struct.unpack_from("<i", call, 4)[0], 0x140541050)
        functions = {
            IMAGE_BASE + item.struct.BeginAddress: IMAGE_BASE + item.struct.EndAddress
            for item in image.DIRECTORY_ENTRY_EXCEPTION}
        spans = {0x1404E03F0: 0x160}
        for origin in (0x14068D9D0, 0x14067FC20, 0x1406AF270, 0x1406ABC60, 0x1406B0C00):
            spans[origin] = functions[origin] - origin
        for origin, size in spans.items():
            blob = image.get_data(origin - IMAGE_BASE, size)
            for disp in (bytes.fromhex("08010000"), bytes.fromhex("80000000")):
                index = 0
                while True:
                    found = blob.find(disp, index)
                    if found < 0:
                        break
                    if found >= 2 and blob[found - 2] == 0xFF and (blob[found - 1] & 0xC0) == 0x80 and ((blob[found - 1] >> 3) & 7) in (2, 4):
                        self.fail(hex(origin + found - 2))
                    index = found + 1

    def test_skip_refresh_reads_the_document_array_without_a_close_check(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        image = pefile.PE(data=source, fast_load=True)
        image.parse_data_directories(directories=[
            pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
        self.assertEqual(image.get_data(0x6ADB33, 8), bytes.fromhex("488b8be8000000e8"))
        call = image.get_data(0x6ADB3A, 5)
        self.assertEqual(0x1406ADB3F + struct.unpack_from("<i", call, 1)[0], 0x140541040)
        self.assertEqual(image.get_data(0x541040, 8), bytes.fromhex("488d81e0230000c3"))
        self.assertEqual(image.get_data(0x6ADB3F, 9), bytes.fromhex("488bf833f648397010"))
        branch = image.get_data(0x6ADB48, 2)
        self.assertEqual(branch[0], 0x7E)
        self.assertGreater(0x1406ADB4A + struct.unpack_from("<b", branch, 1)[0], 0x1406ADB6B)
        self.assertEqual(image.get_data(0x6ADB67, 8), bytes.fromhex("488b4708448b0498"))
        refresh = next(item for item in image.DIRECTORY_ENTRY_EXCEPTION
                       if IMAGE_BASE + item.struct.BeginAddress == 0x1406ADAF0)
        body = image.get_data(0x6ADAF0, refresh.struct.EndAddress - refresh.struct.BeginAddress)
        for displacement in (bytes.fromhex("2d380000"), bytes.fromhex("2e380000"), bytes.fromhex("38580000")):
            self.assertEqual(body.find(displacement), -1)
        prelude = next(item for item in image.DIRECTORY_ENTRY_EXCEPTION
                       if IMAGE_BASE + item.struct.BeginAddress == 0x14067AB20)
        prelude_body = image.get_data(0x67AB20, prelude.struct.EndAddress - prelude.struct.BeginAddress)
        self.assertEqual(prelude_body.find(bytes.fromhex("68380000")), -1)

    def test_second_refresh_caller_is_not_on_the_close_path(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        image = pefile.PE(data=source, fast_load=True)
        image.parse_data_directories(directories=[
            pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
        self.assertEqual(image.get_data(0x6B0700, 5), bytes.fromhex("4883ec28e8"))
        self.assertEqual(0x1406B0709 + struct.unpack_from("<i", image.get_data(0x6B0705, 4))[0], 0x1406ADAF0)
        self.assertEqual(image.get_data(0x6B0709, 6), bytes.fromhex("33c04883c428"))
        self.assertEqual(image.get_data(0x6971BA, 24), bytes.fromhex("488b018bfa488bd9ff90e000000048894424304885c0741b"))
        call = image.get_data(0x6971DD, 6)
        self.assertEqual(call, bytes.fromhex("ff90e8000000"))
        call = image.get_data(0x6971E3, 10)
        self.assertEqual(call[:6], bytes.fromhex("488bc88bd7e8"))
        self.assertEqual(0x1406971ED + struct.unpack_from("<i", call, 6)[0], 0x1406B3760)
        call = image.get_data(0x6B3B3C, 8)
        self.assertEqual(call[:4], bytes.fromhex("488bcee8"))
        self.assertEqual(0x1406B3B44 + struct.unpack_from("<i", call, 4)[0], 0x1406ADAF0)
        self.assertEqual(image.get_data(0x6B3B44, 15), bytes.fromhex("41b9050100004533c033d2488b4e40"))
        text = next(item for item in image.sections if item.Name.startswith(b".text"))
        text_data = text.get_data()
        text_base = IMAGE_BASE + text.VirtualAddress
        callers = []
        start = 0
        while True:
            index = text_data.find(b"\xe8", start)
            if index < 0 or index + 5 > len(text_data):
                break
            if text_base + index + 5 + struct.unpack_from("<i", text_data, index + 1)[0] == 0x1406971B0:
                callers.append(text_base + index)
            start = index + 1
        self.assertEqual(callers, [0x1404DB44A, 0x1404DC8CA, 0x1404DC95C, 0x1404DCE1C, 0x1404DCED7, 0x1404DD4A5])
        functions = {
            IMAGE_BASE + item.struct.BeginAddress: IMAGE_BASE + item.struct.EndAddress
            for item in image.DIRECTORY_ENTRY_EXCEPTION}
        for origin, size in (
            (0x1406971B0, functions[0x1406971B0] - 0x1406971B0),
            (0x1406B3760, functions[0x1406B3760] - 0x1406B3760)):
            self.assertEqual(image.get_data(origin - IMAGE_BASE, size).find(bytes.fromhex("68380000")), -1)
        spans = {0x1404E03F0: 0x160}
        for origin in (0x14068D9D0, 0x14067FC20, 0x1406AF270, 0x1406ABC60, 0x1406B0C00):
            spans[origin] = functions[origin] - origin
        for origin, size in spans.items():
            blob = image.get_data(origin - IMAGE_BASE, size)
            for index in range(len(blob) - 5):
                if blob[index] != 0xE8:
                    continue
                dest = origin + index + 5 + struct.unpack_from("<i", blob, index + 1)[0]
                self.assertNotIn(dest, (0x1406971B0, 0x1406B3760))

    def test_close_does_not_write_the_poster_enable_dword(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        image = pefile.PE(data=source, fast_load=True)
        image.parse_data_directories(directories=[
            pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
        self.assertEqual(image.get_data(0x6A52A9, 9), bytes.fromhex("83b878390000017552"))
        self.assertEqual(0x1406A52B2 + 0x52, 0x1406A5304)
        self.assertLess(0x1406A52B5, 0x1406A5304)
        call = image.get_data(0x6A52B2, 8)
        self.assertEqual(call[:4], bytes.fromhex("488bcfe8"))
        self.assertEqual(0x1406A52BA + struct.unpack_from("<i", call, 4)[0], 0x1406A06B0)
        poster = next(item for item in image.DIRECTORY_ENTRY_EXCEPTION
                      if IMAGE_BASE + item.struct.BeginAddress == 0x1406A06B0)
        poster_body = image.get_data(0x6A06B0, poster.struct.EndAddress - poster.struct.BeginAddress)
        self.assertEqual(poster_body.find(bytes.fromhex("78390000")), -1)
        self.assertEqual(image.get_data(0x67E1D6, 7), bytes.fromhex("4489b678390000"))
        self.assertTrue(0x14067DF59 < 0x14067E1D6 < 0x14067F60E)
        self.assertEqual(image.get_data(0x6A34A1, 6), bytes.fromhex("89b078390000"))
        self.assertEqual(image.get_data(0x6A3758, 8), bytes.fromhex("d3e2899078390000"))
        self.assertEqual(image.get_data(0x69A9FC, 3), bytes.fromhex("4533ff"))
        self.assertEqual(image.get_data(0x69AAAF, 7), bytes.fromhex("4489b878390000"))
        branch = image.get_data(0x69AAA1, 6)
        self.assertEqual(branch[0], 0x0F)
        self.assertEqual(branch[1], 0x84)
        self.assertGreater(0x14069AAA7 + struct.unpack_from("<i", branch, 2)[0], 0x14069AAAF)
        text = next(item for item in image.sections if item.Name.startswith(b".text"))
        text_data = text.get_data()
        text_base = IMAGE_BASE + text.VirtualAddress
        callers = []
        start = 0
        while True:
            index = text_data.find(b"\xe8", start)
            if index < 0 or index + 5 > len(text_data):
                break
            if text_base + index + 5 + struct.unpack_from("<i", text_data, index + 1)[0] == 0x14069A9C0:
                callers.append(text_base + index)
            start = index + 1
        self.assertEqual(callers, [0x1406A2E5E])
        self.assertTrue(0x1406A20D0 <= 0x1406A2E5E < 0x1406A20D0 + 0x2877)
        functions = {
            IMAGE_BASE + item.struct.BeginAddress: IMAGE_BASE + item.struct.EndAddress
            for item in image.DIRECTORY_ENTRY_EXCEPTION}
        spans = {0x1404E03F0: 0x160}
        for origin in (0x14068D9D0, 0x14067FC20, 0x1406AF270, 0x1406ABC60, 0x1406B0C00):
            spans[origin] = functions[origin] - origin
        for origin, size in spans.items():
            self.assertEqual(image.get_data(origin - IMAGE_BASE, size).find(bytes.fromhex("78390000")), -1)

    def test_poster_one_return_posts_after_the_slot_reset(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        image = pefile.PE(data=source, fast_load=True)
        image.parse_data_directories(directories=[
            pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
        self.assertEqual(image.get_data(0x6A0834, 7), bytes.fromhex("488b1f488bcee8"))
        call = image.get_data(0x6A083A, 5)
        self.assertEqual(0x1406A083F + struct.unpack_from("<i", call, 1)[0], 0x1406A15D0)
        self.assertEqual(image.get_data(0x6A083F, 16), bytes.fromhex("488bd0488bcfff93800000003c010f84"))
        self.assertEqual(0x1406A0853 + struct.unpack_from("<i", image.get_data(0x6A084F, 4))[0], 0x1406A1056)
        self.assertLess(0x1406A085E, 0x1406A1056)
        call = image.get_data(0x6A085B, 8)
        self.assertEqual(call[:4], bytes.fromhex("488bc8e8"))
        self.assertEqual(0x1406A0863 + struct.unpack_from("<i", call, 4)[0], 0x140541050)
        self.assertEqual(image.get_data(0x6A1056, 4), bytes.fromhex("488bcee8"))
        self.assertEqual(0x1406A105E + struct.unpack_from("<i", image.get_data(0x6A105A, 4))[0], 0x1406A15D0)
        self.assertEqual(image.get_data(0x6A105E, 15), bytes.fromhex("488b88385800004533c94533c08b15"))
        self.assertEqual(image.get_data(0x4AEBB6, 2), bytes.fromhex("32c0"))
        self.assertLess(0x1404AEBB8, 0x1404AEBE9)
        call = image.get_data(0x4AEBE6, 8)
        self.assertEqual(call[:4], bytes.fromhex("488bcee8"))
        self.assertEqual(0x1404AEBEE + struct.unpack_from("<i", call, 4)[0], 0x140541050)
        self.assertLess(0x1404AEBE9, 0x1404AEC17)
        self.assertLess(0x1404AEC17, 0x1404AEC91)
        self.assertEqual(image.get_data(0x4AEC91, 2), bytes.fromhex("b001"))
        body = image.get_data(0x4AE9D0, 0x300)
        self.assertEqual(body.count(bytes.fromhex("b001")), 1)
        functions = {
            IMAGE_BASE + item.struct.BeginAddress: IMAGE_BASE + item.struct.EndAddress
            for item in image.DIRECTORY_ENTRY_EXCEPTION}
        spans = {0x1404E03F0: 0x160}
        for origin in (0x14068D9D0, 0x14067FC20, 0x1406AF270, 0x1406ABC60, 0x1406B0C00):
            spans[origin] = functions[origin] - origin
        for origin, size in spans.items():
            blob = image.get_data(origin - IMAGE_BASE, size)
            for index in range(len(blob) - 5):
                if blob[index] != 0xE8:
                    continue
                dest = origin + index + 5 + struct.unpack_from("<i", blob, index + 1)[0]
                self.assertNotEqual(dest, 0x1406A06B0)

    def test_skip_poster_returns_without_waiting(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        image = pefile.PE(data=source, fast_load=True)
        pefile.MAX_IMPORT_SYMBOLS = 65536
        image.parse_data_directories(directories=[
            pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
        self.assertEqual(image.get_data(0x6A1016, 5), bytes.fromhex("4183fd0375"))
        self.assertEqual(0x1406A101C + image.get_data(0x6A101B, 1)[0], 0x1406A1047)
        self.assertLess(0x1406A103B, 0x1406A1047)
        self.assertEqual(image.get_data(0x6A1024, 7), bytes.fromhex("488b8838580000"))
        self.assertEqual(image.get_data(0x6A1041, 6), bytes.fromhex("41bd03000000"))
        self.assertEqual(image.get_data(0x6A1094, 3), bytes.fromhex("418bc5"))
        names = {}
        for entry in image.DIRECTORY_ENTRY_IMPORT:
            for imported in entry.imports:
                if imported.address is not None:
                    names[imported.address] = imported.name
        for call, nxt in ((0x1406A103B, 0x1406A1041), (0x1406A1075, 0x1406A107B)):
            self.assertEqual(image.get_data(call - IMAGE_BASE, 2), bytes.fromhex("ff15"))
            disp = struct.unpack_from("<i", image.get_data(call + 2 - IMAGE_BASE, 4))[0]
            self.assertEqual(names[nxt + disp], b"PostMessageA")
        tail = image.get_data(0x6A107B, 0x1406A10BA - 0x1406A107B)
        self.assertEqual(tail.count(bytes.fromhex("ff15")), 2)
        for call, nxt, name in (
                (0x1406A1083, 0x1406A1089, b"??1CBenchManagerFunction@@UEAA@XZ"),
                (0x1406A108E, 0x1406A1094, b"??1CLogManagerFunctionML@@UEAA@XZ")):
            disp = struct.unpack_from("<i", image.get_data(call + 2 - IMAGE_BASE, 4))[0]
            self.assertEqual(names[nxt + disp], name)
        self.assertIn(bytes.fromhex("c3"), tail)

    def test_grey_zone_post_returns_without_clearing_its_flag(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        image = pefile.PE(data=source, fast_load=True)
        pefile.MAX_IMPORT_SYMBOLS = 65536
        image.parse_data_directories(directories=[
            pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
            pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
        self.assertEqual(image.get_data(0x67E4CD, 6), bytes.fromhex("888635380000"))
        self.assertEqual(image.get_data(0x736F4B, 9), bytes.fromhex("80b935380000010f85"))
        self.assertGreater(0x140736F58 + struct.unpack_from("<i", image.get_data(0x736F54, 4))[0], 0x140736FEB)
        text = next(item for item in image.sections if item.Name.startswith(b".text"))
        text_data = text.get_data()
        text_base = IMAGE_BASE + text.VirtualAddress
        sites = []
        start = 0
        needle = bytes.fromhex("35380000")
        while True:
            found = text_data.find(needle, start)
            if found < 0:
                break
            if found == 0 or text_data[found - 1] not in (0xE8, 0xE9):
                sites.append(text_base + found)
            start = found + 1
        self.assertEqual(sites, [0x14067E4CF, 0x14067E4EF, 0x140736F4D])
        self.assertEqual(text_data[0x67E4CD - text.VirtualAddress], 0x88)
        self.assertEqual(image.get_data(0x736FD4, 7), bytes.fromhex("488b8838580000"))
        self.assertEqual(image.get_data(0x736FEB, 2), bytes.fromhex("ff15"))
        names = {}
        for entry in image.DIRECTORY_ENTRY_IMPORT:
            for imported in entry.imports:
                if imported.address is not None:
                    names[imported.address] = imported.name
        disp = struct.unpack_from("<i", image.get_data(0x736FED, 4))[0]
        self.assertEqual(names[0x140736FF1 + disp], b"PostMessageA")
        jump = image.get_data(0x736FF1, 5)
        self.assertEqual(jump[0], 0xE9)
        self.assertEqual(0x140736FF6 + struct.unpack_from("<i", jump, 1)[0], 0x14073742D)
        self.assertEqual(image.get_data(0x73742D, 4), bytes.fromhex("488d4d08"))
        self.assertEqual(image.get_data(0x7374B2, 3), bytes.fromhex("418bc4"))
        functions = {
            IMAGE_BASE + item.struct.BeginAddress: IMAGE_BASE + item.struct.EndAddress
            for item in image.DIRECTORY_ENTRY_EXCEPTION}
        spans = {0x1404E03F0: 0x160}
        for origin in (0x14068D9D0, 0x14067FC20, 0x1406AF270, 0x1406ABC60, 0x1406B0C00):
            spans[origin] = functions[origin] - origin
        for origin, size in spans.items():
            self.assertEqual(image.get_data(origin - IMAGE_BASE, size).find(bytes.fromhex("35380000")), -1)

    def test_grey_zone_post_callers_do_not_check_the_producer_stop(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        image = pefile.PE(data=source, fast_load=True)
        image.parse_data_directories(directories=[
            pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
        text = next(item for item in image.sections if item.Name.startswith(b".text"))
        text_data = text.get_data()
        text_base = IMAGE_BASE + text.VirtualAddress
        callers = {0x1407368D0: [], 0x1407354B0: [], 0x140735F10: [], 0x14069FCD0: []}
        start = 0
        while True:
            index = text_data.find(b"\xe8", start)
            if index < 0 or index + 5 > len(text_data):
                break
            dest = text_base + index + 5 + struct.unpack_from("<i", text_data, index + 1)[0]
            if dest in callers:
                callers[dest].append(text_base + index)
            start = index + 1
        self.assertEqual(callers[0x1407368D0], [0x1407356A1])
        self.assertEqual(callers[0x1407354B0], [0x140736796])
        self.assertEqual(callers[0x140735F10], [0x14066DC2A, 0x14069FDAA])
        self.assertEqual(callers[0x14069FCD0], [0x14069FC94, 0x1406A8EDA, 0x1406A90E1])
        functions = {
            IMAGE_BASE + item.struct.BeginAddress: IMAGE_BASE + item.struct.EndAddress
            for item in image.DIRECTORY_ENTRY_EXCEPTION}
        self.assertTrue(0x14066DB40 <= 0x14066DC2A < functions[0x14066DB40])
        self.assertTrue(0x14069FB80 <= 0x14069FC94 < functions[0x14069FB80])
        self.assertTrue(0x1406A88E0 <= 0x1406A8EDA < functions[0x1406A88E0])
        for origin in (0x140735F10, 0x1407354B0, 0x14069FCD0):
            body = image.get_data(origin - IMAGE_BASE, functions[origin] - origin)
            self.assertEqual(body.find(bytes.fromhex("68380000")), -1)
            self.assertEqual(body.find(bytes.fromhex("2e380000")), -1)
        spans = {0x1404E03F0: 0x160}
        for origin in (0x14068D9D0, 0x14067FC20, 0x1406AF270, 0x1406ABC60, 0x1406B0C00):
            spans[origin] = functions[origin] - origin
        for origin, size in spans.items():
            blob = image.get_data(origin - IMAGE_BASE, size)
            for index in range(len(blob) - 5):
                if blob[index] != 0xE8:
                    continue
                dest = origin + index + 5 + struct.unpack_from("<i", blob, index + 1)[0]
                self.assertNotIn(dest, callers)

    def test_close_call_levels_do_not_wait_on_the_producer(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        image = pefile.PE(data=source, fast_load=True)
        pefile.MAX_IMPORT_SYMBOLS = 65536
        image.parse_data_directories(directories=[
            pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
            pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
        names = {}
        for entry in image.DIRECTORY_ENTRY_IMPORT:
            for imported in entry.imports:
                if imported.address is not None:
                    names[imported.address] = imported.name or b""
        functions = {
            IMAGE_BASE + item.struct.BeginAddress: IMAGE_BASE + item.struct.EndAddress
            for item in image.DIRECTORY_ENTRY_EXCEPTION}

        def direct_calls(origin: int, size: int) -> list[int]:
            blob = image.get_data(origin - IMAGE_BASE, size)
            found = []
            for index in range(len(blob) - 5):
                if blob[index] not in (0xE8, 0xE9):
                    continue
                found.append(origin + index + 5 + struct.unpack_from("<i", blob, index + 1)[0])
            return found

        destructor_calls = [dest for dest in direct_calls(0x14067FC20, functions[0x14067FC20] - 0x14067FC20) if dest in functions]
        self.assertGreaterEqual(len(destructor_calls), 1)
        for dest in destructor_calls:
            body = image.get_data(dest - IMAGE_BASE, functions[dest] - dest)
            for index in range(len(body) - 6):
                if body[index:index + 2] != b"\xff\x15":
                    continue
                slot = dest + index + 6 + struct.unpack_from("<i", body, index + 2)[0]
                self.assertNotIn(b"WaitForSingleObject", names.get(slot, b""))
        roots = [0x14068D9D0, 0x14067FC20, 0x1406AF270, 0x1406ABC60, 0x1406B0C00, 0x1404E03F0]
        seen = set()
        level = set(roots)
        waiters = set()
        for _depth in range(3):
            nxt = set()
            for origin in level:
                if origin in seen or origin not in functions and origin != 0x1404E03F0:
                    continue
                seen.add(origin)
                size = 0x160 if origin == 0x1404E03F0 else functions[origin] - origin
                body = image.get_data(origin - IMAGE_BASE, size)
                for index in range(len(body) - 6):
                    if body[index:index + 2] != b"\xff\x15":
                        continue
                    slot = origin + index + 6 + struct.unpack_from("<i", body, index + 2)[0]
                    name = names.get(slot, b"")
                    self.assertNotIn(b"Stop@CViThread", name)
                    if name == b"WaitForSingleObject":
                        waiters.add(origin)
                nxt.update(dest for dest in direct_calls(origin, size) if dest in functions)
            level = nxt
        self.assertEqual(waiters, {0x14063B430, 0x14064B880, 0x1406AE120, 0x1406AE950})
        for origin in waiters:
            body = image.get_data(origin - IMAGE_BASE, functions[origin] - origin)
            self.assertEqual(body.find(bytes.fromhex("68380000")), -1)

    def test_close_without_the_command_switch_does_not_call_slot_28(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        image = pefile.PE(data=source, fast_load=True)
        image.parse_data_directories(directories=[
            pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
        functions = {
            IMAGE_BASE + item.struct.BeginAddress: IMAGE_BASE + item.struct.EndAddress
            for item in image.DIRECTORY_ENTRY_EXCEPTION}

        def direct_calls(origin: int, size: int) -> list[int]:
            blob = image.get_data(origin - IMAGE_BASE, size)
            found = []
            for index in range(len(blob) - 5):
                if blob[index] not in (0xE8, 0xE9):
                    continue
                found.append(origin + index + 5 + struct.unpack_from("<i", blob, index + 1)[0])
            return found

        roots = {0x14068D9D0, 0x14067FC20, 0x1406AF270, 0x1406ABC60, 0x1404E03F0}
        seen: set[int] = set()
        level = set(roots)
        for _depth in range(3):
            nxt: set[int] = set()
            for origin in level:
                if origin in seen or (origin not in functions and origin != 0x1404E03F0):
                    continue
                seen.add(origin)
                size = 0x160 if origin == 0x1404E03F0 else functions[origin] - origin
                nxt.update(dest for dest in direct_calls(origin, size) if dest in functions)
            level = nxt
        self.assertEqual(len(seen), 43)
        self.assertTrue(roots <= seen)
        for blocked in (0x1406920F0, 0x140680C00, 0x140691C80):
            self.assertNotIn(blocked, seen)
        for origin in seen:
            size = 0x160 if origin == 0x1404E03F0 else functions[origin] - origin
            blob = image.get_data(origin - IMAGE_BASE, size)
            index = 0
            while index < len(blob) - 2:
                cursor = index
                if 0x40 <= blob[cursor] <= 0x4F and cursor + 1 < len(blob) and blob[cursor + 1] == 0xFF:
                    cursor += 1
                if blob[cursor] == 0xFF and cursor + 2 < len(blob):
                    modrm = blob[cursor + 1]
                    operation = (modrm >> 3) & 7
                    mode = (modrm >> 6) & 3
                    if operation in (2, 4) and mode == 1 and blob[cursor + 2] == 0x28:
                        self.fail(hex(origin + index))
                    if operation in (2, 4) and mode == 2 and cursor + 6 <= len(blob):
                        if struct.unpack_from("<i", blob, cursor + 2)[0] == 0x28:
                            self.fail(hex(origin + index))
                index += 1

    def test_close_virtual_helpers_do_not_stop_the_producer(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        image = pefile.PE(data=source, fast_load=True)
        image.parse_data_directories(directories=[
            pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
        call = image.get_data(0x67FEFA, 12)
        self.assertEqual(call[:7], bytes.fromhex("488d8b88580000"))
        self.assertEqual(call[7], 0xE8)
        self.assertEqual(0x14067FF06 + struct.unpack_from("<i", call, 8)[0], 0x14066E530)
        self.assertEqual(image.get_data(0x66E55B, 11), bytes.fromhex("488b7120488b5918483bde"))
        self.assertEqual(image.get_data(0x66E570, 11), bytes.fromhex("488b0333d2488bcbff5008"))
        self.assertEqual(image.get_data(0x66E57C, 7), bytes.fromhex("4881c370030000"))
        self.assertEqual(image.get_data(0x7402BE, 20), bytes.fromhex("488b8b580100004885c9740c488b01ba01000000"))
        self.assertEqual(image.get_data(0x7402D2, 3), bytes.fromhex("ff5008"))
        self.assertEqual(image.get_data(0x5795E3, 8), bytes.fromhex("83c8fff00fc1430c"))
        functions = {
            IMAGE_BASE + item.struct.BeginAddress: IMAGE_BASE + item.struct.EndAddress
            for item in image.DIRECTORY_ENTRY_EXCEPTION}
        for origin in (0x14066E530, 0x140740280, 0x14045F700, 0x140579580):
            body = image.get_data(origin - IMAGE_BASE, functions[origin] - origin)
            self.assertEqual(body.find(bytes.fromhex("68380000")), -1)

    def test_close_refcount_and_bitmap_helpers_do_not_stop_the_producer(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        mfc = (ROOT / "v3d_files_" / "mfc140.dll").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        self.assertEqual(
            hashlib.sha256(mfc).hexdigest(),
            "0cf26008fae0cb61dfe49e1c3fc17e0dd860be011d9a6a64b452f56335bafbfe")
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            image = pefile.PE(data=source, fast_load=True)
            image.parse_data_directories(directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
            imports = {
                item.address: (entry.dll.lower(), item.name.decode() if item.name else item.ordinal)
                for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
            lea = image.get_data(0x572712, 7)
            self.assertEqual(lea[:3], bytes.fromhex("488d0d"))
            self.assertEqual(0x140572719 + struct.unpack_from("<i", lea, 3)[0], 0x140E5F9E0)
            self.assertEqual(image.get_data(0x572704, 14), bytes.fromhex("c7400801000000c7400c01000000"))
            self.assertEqual(image.get_data(0x572719, 7), bytes.fromhex("48890848897810"))
            self.assertEqual(struct.unpack_from("<Q", image.get_data(0xE5F9E8, 8))[0], 0x1405BC830)
            self.assertEqual(struct.unpack_from("<Q", image.get_data(0xE5F9F0, 8))[0], 0x140446570)
            self.assertEqual(
                image.get_data(0x5BC830, 21),
                bytes.fromhex("488b49104885c9740c488b01ba0100000048ff6008"))
            self.assertEqual(image.get_data(0x446570, 16), bytes.fromhex("4885c9740b488b01ba0100000048ff20"))
            free_jump = image.get_data(0x4556C0, 5)
            self.assertEqual(free_jump[0], 0xE9)
            self.assertEqual(0x1404556C5 + struct.unpack_from("<i", free_jump, 1)[0], 0x14077F4AE)
            thunk = image.get_data(0x77F4AE, 6)
            self.assertEqual(thunk[:2], b"\xff\x25")
            self.assertEqual(imports[0x14077F4B4 + struct.unpack_from("<i", thunk, 2)[0]], (b"mfc140.dll", 1487))
            bitmap = image.get_data(0x742117, 7)
            self.assertEqual(bitmap[:3], bytes.fromhex("488d05"))
            self.assertEqual(0x14074211E + struct.unpack_from("<i", bitmap, 3)[0], 0x140E6C8C0)
            self.assertEqual(image.get_data(0x74211E, 3), bytes.fromhex("488906"))
            self.assertEqual(struct.unpack_from("<Q", image.get_data(0xE6C8C8, 8))[0], 0x1405B07A0)
            call = image.get_data(0x5B071A, 5)
            self.assertEqual(call[0], 0xE8)
            self.assertEqual(0x1405B071F + struct.unpack_from("<i", call, 1)[0], 0x14077FF5E)
            ordinal = image.get_data(0x77FF5E, 6)
            self.assertEqual(ordinal[:2], b"\xff\x25")
            self.assertEqual(imports[0x14077FF64 + struct.unpack_from("<i", ordinal, 2)[0]], (b"mfc140.dll", 3748))
            library = pefile.PE(data=mfc, fast_load=True)
            self.assertEqual(library.OPTIONAL_HEADER.ImageBase, 0x180000000)
            library.parse_data_directories(directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
            library_imports = {
                item.address: (entry.dll.lower(), item.name.decode() if item.name else item.ordinal)
                for entry in library.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
            self.assertEqual(library.get_data(0x2A8D94, 7), bytes.fromhex("48837908007507"))
            delete = library.get_data(0x2A8DAE, 7)
            self.assertEqual(delete[:3], bytes.fromhex("48ff25"))
            self.assertEqual(
                library_imports[0x1802A8DB5 + struct.unpack_from("<i", delete, 3)[0]],
                (b"gdi32.dll", "DeleteObject"))
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_cao_destructor_and_cad_engine_stop_do_not_join_the_producer(self) -> None:
        cad = (ROOT / "v3d_files_" / "CadEngineModule.dll").read_bytes()
        vit = (ROOT / "v3d_files_" / "VitDataCAD.dll").read_bytes()
        mfc = (ROOT / "v3d_files_" / "mfc140.dll").read_bytes()
        self.assertEqual(hashlib.sha256(cad).hexdigest(),
                         "3523eb0f721a6b6e1ac59c0b7b1c9f429f82fb1ab17435f8f65c79a686f18da4")
        self.assertEqual(len(cad), 370176)
        self.assertEqual(hashlib.sha256(vit).hexdigest(),
                         "0cb969e8ae45b199afa1f378d5d18aeed93db04d43a3b8a0b380ce9f71d12a78")
        self.assertEqual(len(vit), 3566080)
        self.assertEqual(hashlib.sha256(mfc).hexdigest(),
                         "0cf26008fae0cb61dfe49e1c3fc17e0dd860be011d9a6a64b452f56335bafbfe")
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=cad, fast_load=True) as image:
                self.assertEqual(image.OPTIONAL_HEADER.ImageBase, 0x180000000)
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                imports = {
                    item.address: (entry.dll.lower(), item.name.decode() if item.name else item.ordinal)
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                self.assertEqual(image.get_data(0x492A, 9), bytes.fromhex("33c048898338010000"))
                self.assertEqual(image.get_data(0x7E32, 5), bytes.fromhex("b918030000"))
                self.assertEqual(image.get_data(0x7E4F, 7), bytes.fromhex("48898338010000"))
                section = next(item for item in image.sections if item.Name.startswith(b".text"))
                text = section.get_data()
                self.assertEqual(text.count(bytes.fromhex("48898338010000")), 2)
                self.assertEqual(text.count(bytes.fromhex("48c7833801000000000000")), 1)
                post = image.get_data(0x7F1A, 13)
                self.assertEqual(post[:7], bytes.fromhex("418d51128b4860"))
                self.assertEqual(post[7:9], b"\xff\x15")
                self.assertEqual(
                    imports[0x180007F27 + struct.unpack_from("<i", post, 9)[0]],
                    (b"user32.dll", "PostThreadMessageA"))
                wait = image.get_data(0x7F2E, 13)
                self.assertEqual(wait[:7], bytes.fromhex("83caff488b4958"))
                self.assertEqual(wait[7:9], b"\xff\x15")
                self.assertEqual(
                    imports[0x180007F3B + struct.unpack_from("<i", wait, 9)[0]],
                    (b"kernel32.dll", "WaitForSingleObject"))
                self.assertEqual(image.get_data(0x7F52, 11), bytes.fromhex("48c7833801000000000000"))
                vtable = image.get_data(0xEA24, 7)
                self.assertEqual(vtable[:3], bytes.fromhex("488d05"))
                self.assertEqual(0x18000EA2B + struct.unpack_from("<i", vtable, 3)[0], 0x180031418)
                column = struct.unpack_from("<Q", image.get_data(0x31418 - 8, 8))[0]
                descriptor = struct.unpack_from("<I", image.get_data(column - 0x180000000 + 12, 4))[0]
                name = image.get_data(descriptor, 0x40)
                start = name.find(b".?AV")
                self.assertEqual(name[start:name.find(b"\x00", start)], b".?AVCCadEngineThread@@")
                starter = image.get_data(0x271A4, 6)
                self.assertEqual(starter[:2], b"\xff\x25")
                self.assertEqual(
                    imports[0x1800271AA + struct.unpack_from("<i", starter, 2)[0]],
                    (b"mfc140.dll", 3529))
            with pefile.PE(data=mfc, fast_load=True) as library:
                self.assertEqual(library.OPTIONAL_HEADER.ImageBase, 0x180000000)
                library.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                library_imports = {
                    item.address: item.name.decode() if item.name else item.ordinal
                    for entry in library.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                self.assertEqual(library.get_data(0x278B25, 4), bytes.fromhex("488d4360"))
                created = library.get_data(0x278B46, 10)
                self.assertEqual(created[:2], b"\xff\x15")
                self.assertEqual(
                    library_imports[0x180278B4C + struct.unpack_from("<i", created, 2)[0]],
                    "_beginthreadex")
                self.assertEqual(created[6:], bytes.fromhex("48894358"))
            with pefile.PE(data=vit, fast_load=True) as image:
                self.assertEqual(image.OPTIONAL_HEADER.ImageBase, 0x180000000)
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
                imports = {
                    item.address: (entry.dll.lower(), (item.name or b"").decode())
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                tail = image.get_data(0x8EF29, 5)
                self.assertEqual(tail[0], 0xE9)
                self.assertEqual(0x18008EF2E + struct.unpack_from("<i", tail, 1)[0], 0x18005EB50)
                functions = {
                    0x180000000 + item.struct.BeginAddress: 0x180000000 + item.struct.EndAddress
                    for item in image.DIRECTORY_ENTRY_EXCEPTION}
                decoder = Cs(CS_ARCH_X86, CS_MODE_64)
                level = {0x18008ED90}
                seen = set()
                for _depth in range(3):
                    nxt = set()
                    for origin in level:
                        if origin in seen or origin not in functions:
                            continue
                        seen.add(origin)
                        body = image.get_data(origin - 0x180000000, functions[origin] - origin)
                        self.assertEqual(body.find(bytes.fromhex("68380000")), -1)
                        for insn in decoder.disasm(body, origin):
                            if insn.bytes[:1] in (b"\xe8", b"\xe9"):
                                nxt.add(insn.address + insn.size + int.from_bytes(
                                    insn.bytes[1:5], "little", signed=True))
                            elif insn.bytes[:2] == b"\xff\x15":
                                slot = insn.address + 6 + int.from_bytes(insn.bytes[2:6], "little", signed=True)
                                dll, symbol = imports[slot]
                                self.assertNotIn("stop@cvithread", symbol.lower())
                                self.assertNotIn("waitfor", symbol.lower())
                                self.assertNotEqual(dll, b"vision3d.exe")
                    level = nxt
                self.assertGreater(len(seen), 1)
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_macro_pointer_vector_destructor_does_not_join_the_producer(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        vit = (ROOT / "v3d_files_" / "VitDataCAD.dll").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        self.assertEqual(hashlib.sha256(vit).hexdigest(),
                         "0cb969e8ae45b199afa1f378d5d18aeed93db04d43a3b8a0b380ce9f71d12a78")
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                imports = {
                    item.address: (entry.dll.lower(), (item.name or b"").decode())
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                lea = image.get_data(0x534148, 7)
                self.assertEqual(lea[:3], b"\x48\x8d\x05")
                self.assertEqual(0x14053414F + struct.unpack_from("<i", lea, 3)[0], 0x140E4D398)
                self.assertEqual(image.get_data(0x53414F, 3), bytes.fromhex("498906"))
                self.assertEqual(image.get_data(0x53416F, 7), bytes.fromhex("488d9e78240000"))
                self.assertEqual(image.get_data(0x5341E8, 3), bytes.fromhex("4c8930"))
                self.assertEqual(image.get_data(0x5341EB, 5), bytes.fromhex("4883430808"))
                self.assertEqual(struct.unpack_from("<Q", image.get_data(0xE4D3A0, 8))[0], 0x140521B30)
                col = struct.unpack_from("<Q", image.get_data(0xE4D390, 8))[0]
                type_rva = struct.unpack_from("<I", image.get_data(col - 0x140000000 + 12, 4))[0]
                self.assertEqual(image.get_data(type_rva + 16, 12), b".?AVCMacro@@")
                call = image.get_data(0x521B3F, 6)
                self.assertEqual(call[:2], b"\xff\x15")
                self.assertEqual(imports[0x140521B45 + struct.unpack_from("<i", call, 2)[0]],
                                 (b"vitdatacad.dll", "??1CMacro@@UEAA@XZ"))
                self.assertEqual(image.get_data(0x521B45, 15),
                                 bytes.fromhex("40f6c7017426488bcb40f6c7047513"))
                free = image.get_data(0x521B54, 5)
                self.assertEqual(free[0], 0xE8)
                self.assertEqual(0x140521B59 + struct.unpack_from("<i", free, 1)[0], 0x14077F4AE)
            with pefile.PE(data=vit, fast_load=True) as image:
                self.assertEqual(image.OPTIONAL_HEADER.ImageBase, 0x180000000)
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                imports = {
                    item.address: (entry.dll.lower(), (item.name or b"").decode())
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                functions = {
                    0x180000000 + item.struct.BeginAddress: 0x180000000 + item.struct.EndAddress
                    for item in image.DIRECTORY_ENTRY_EXCEPTION}
                decoder = Cs(CS_ARCH_X86, CS_MODE_64)
                level = {0x1800A64B0}
                seen = set()
                for _depth in range(3):
                    nxt = set()
                    for origin in level:
                        if origin in seen or origin not in functions:
                            continue
                        seen.add(origin)
                        body = image.get_data(origin - 0x180000000, functions[origin] - origin)
                        self.assertEqual(body.find(bytes.fromhex("68380000")), -1)
                        for insn in decoder.disasm(body, origin):
                            if insn.bytes[:1] in (b"\xe8", b"\xe9"):
                                nxt.add(insn.address + insn.size + int.from_bytes(
                                    insn.bytes[1:5], "little", signed=True))
                            elif insn.bytes[:2] == b"\xff\x15":
                                slot = insn.address + 6 + int.from_bytes(insn.bytes[2:6], "little", signed=True)
                                dll, symbol = imports[slot]
                                self.assertNotIn("stop@cvithread", symbol.lower())
                                self.assertNotIn("waitfor", symbol.lower())
                                self.assertNotEqual(dll, b"vision3d.exe")
                    level = nxt
                self.assertGreater(len(seen), 1)
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_cdata_cao_element_destructors_do_not_join_the_producer(self) -> None:
        vit = (ROOT / "v3d_files_" / "VitDataCAD.dll").read_bytes()
        self.assertEqual(hashlib.sha256(vit).hexdigest(),
                         "0cb969e8ae45b199afa1f378d5d18aeed93db04d43a3b8a0b380ce9f71d12a78")
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=vit, fast_load=True) as image:
                self.assertEqual(image.OPTIONAL_HEADER.ImageBase, 0x180000000)
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
                self.assertEqual(image.get_data(0x8EDC1, 18),
                                 bytes.fromhex("4983c8ff33d2498d8e780d0000e8edea0000"))
                lea = image.get_data(0xA624C, 7)
                self.assertEqual(lea[:3], b"\x48\x8d\x05")
                self.assertEqual(0x1800A6253 + struct.unpack_from("<i", lea, 3)[0], 0x180102030)
                self.assertEqual(struct.unpack_from("<Q", image.get_data(0x102038, 8))[0], 0x1800A6BD0)
                self.assertEqual(image.get_data(0x9D922, 6), bytes.fromhex("33d241ff5008"))
                self.assertEqual(image.get_data(0x925F6, 8), bytes.fromhex("ba01000000ff5008"))
                self.assertEqual(struct.unpack_from("<Q", image.get_data(0xEAA18, 8))[0], 0x1800213F0)
                imports = {
                    item.address: (entry.dll.lower(), (item.name or b"").decode())
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                functions = {
                    0x180000000 + item.struct.BeginAddress: 0x180000000 + item.struct.EndAddress
                    for item in image.DIRECTORY_ENTRY_EXCEPTION}
                names = {item.name for item in image.DIRECTORY_ENTRY_EXPORT.symbols}
                wanted = (
                    b"??_7CCAD_Base@@6B@", b"??_7CComposant@@6B@", b"??_7CMire@@6B@",
                    b"??_7CPad@@6B@", b"??_7CSkip_bloc@@6B@", b"??_7CMacro@@6B@",
                    b"??_7CDataMatrixInt@@6B@", b"??_7CGroupPad@@6B@", b"??_7CLireText@@6B@",
                    b"??_7CAD_Region@@6B@", b"??_7CCAD_OCV_Reader@@6B@", b"??_7CCAD_Trace@@6B@",
                    b"??_7CReference3D@@6B@", b"??_7CTest@@6B@", b"??_7CZone@@6B@")
                for name in wanted:
                    self.assertIn(name, names)
                slots = []
                for item in image.DIRECTORY_ENTRY_EXPORT.symbols:
                    if item.name in wanted:
                        slots.append(struct.unpack_from("<Q", image.get_data(item.address + 8, 8))[0])
                self.assertEqual(len(slots), len(wanted))
                decoder = Cs(CS_ARCH_X86, CS_MODE_64)
                level = set(slots)
                seen = set()
                for _depth in range(3):
                    nxt = set()
                    for origin in level:
                        if origin in seen or origin not in functions:
                            continue
                        seen.add(origin)
                        body = image.get_data(origin - 0x180000000, functions[origin] - origin)
                        self.assertEqual(body.find(bytes.fromhex("68380000")), -1)
                        for insn in decoder.disasm(body, origin):
                            if insn.bytes[:1] in (b"\xe8", b"\xe9"):
                                nxt.add(insn.address + insn.size + int.from_bytes(
                                    insn.bytes[1:5], "little", signed=True))
                            elif insn.bytes[:2] == b"\xff\x15":
                                slot = insn.address + 6 + int.from_bytes(insn.bytes[2:6], "little", signed=True)
                                dll, symbol = imports[slot]
                                self.assertNotIn("stop@cvithread", symbol.lower())
                                self.assertNotIn("waitfor", symbol.lower())
                                self.assertNotEqual(dll, b"vision3d.exe")
                    level = nxt
                self.assertGreater(len(seen), len(wanted))
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_skip_refresh_does_not_share_a_call_with_reset(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        vit = (ROOT / "v3d_files_" / "VitDataCAD.dll").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        self.assertEqual(hashlib.sha256(vit).hexdigest(),
                         "0cb969e8ae45b199afa1f378d5d18aeed93db04d43a3b8a0b380ce9f71d12a78")
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image:
                text = next(item for item in image.sections if item.Name.startswith(b".text"))
                data = text.get_data()
                base = IMAGE_BASE + text.VirtualAddress
                callers = {0x14067AB20: [], 0x14067A420: [], 0x140541050: []}
                index = 0
                while True:
                    found = data.find(b"\xe8", index)
                    if found < 0:
                        break
                    if found + 5 <= len(data):
                        dest = base + found + 5 + struct.unpack_from("<i", data, found + 1)[0]
                        if dest in callers:
                            callers[dest].append(base + found)
                    index = found + 1
                self.assertEqual(callers[0x14067AB20], [0x1406ADB2E])
                self.assertEqual(callers[0x14067A420], [0x1406ADB97])
                self.assertEqual(callers[0x140541050], [
                    0x1404AEBE9, 0x14068F7D7, 0x1406937D7, 0x1406A085E, 0x1406A2D87])
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
                functions = {
                    IMAGE_BASE + item.struct.BeginAddress: IMAGE_BASE + item.struct.EndAddress
                    for item in image.DIRECTORY_ENTRY_EXCEPTION}
                refresh = image.get_data(0x6ADAF0, functions[0x1406ADAF0] - 0x1406ADAF0)
                getter = refresh.find(bytes.fromhex("e80135e9ff"))
                self.assertGreaterEqual(getter, 0)
                self.assertLess(refresh.find(bytes.fromhex("e8edcffcff")), getter)
                self.assertGreater(refresh.find(bytes.fromhex("e884c8fcff")), getter)
                self.assertEqual(image.get_data(0x6ADB67, 4), bytes.fromhex("488b4708"))
                self.assertEqual(image.get_data(0x6ADBB0, 4), bytes.fromhex("483b4710"))
                decoder = Cs(CS_ARCH_X86, CS_MODE_64)
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                imports = {
                    item.address: ((entry.dll or b"").lower(), (item.name or b"").decode().lower() if item.name else "")
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                prefix = image.get_data(0x51FBF0, 0x14051FD3A - 0x14051FBF0)
                self.assertEqual(prefix.find(bytes.fromhex("68380000")), -1)
                pending = []
                for insn in decoder.disasm(prefix, 0x14051FBF0):
                    if insn.bytes[:1] in (b"\xe8", b"\xe9"):
                        pending.append(insn.address + insn.size + int.from_bytes(
                            insn.bytes[1:5], "little", signed=True))
                seen = set()
                while pending:
                    begin = pending.pop()
                    if begin not in functions or begin in seen:
                        continue
                    seen.add(begin)
                    body = image.get_data(begin - IMAGE_BASE, functions[begin] - begin)
                    self.assertEqual(body.find(bytes.fromhex("68380000")), -1)
                    for insn in decoder.disasm(body, begin):
                        if insn.bytes[:1] in (b"\xe8", b"\xe9"):
                            pending.append(insn.address + insn.size + int.from_bytes(
                                insn.bytes[1:5], "little", signed=True))
                        elif insn.bytes[:2] == b"\xff\x15":
                            slot = insn.address + 6 + int.from_bytes(insn.bytes[2:6], "little", signed=True)
                            dll, symbol = imports[slot]
                            self.assertNotIn("waitfor", symbol)
                            self.assertNotIn("stop@cvithread", symbol)
                self.assertIn(0x14053C250, seen)
                self.assertGreater(len(seen), 1)
            with pefile.PE(data=vit, fast_load=True) as image:
                self.assertEqual(image.OPTIONAL_HEADER.ImageBase, 0x180000000)
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
                exports = {
                    item.name: 0x180000000 + item.address
                    for item in image.DIRECTORY_ENTRY_EXPORT.symbols if item.name}
                imports = {
                    item.address: entry.dll.lower()
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                functions = {
                    0x180000000 + item.struct.BeginAddress: 0x180000000 + item.struct.EndAddress
                    for item in image.DIRECTORY_ENTRY_EXCEPTION}
                decoder = Cs(CS_ARCH_X86, CS_MODE_64)
                pending = [exports[b"??1CDataCao@@UEAA@XZ"]]
                seen = set()
                while pending:
                    begin = pending.pop()
                    if begin not in functions or begin in seen:
                        continue
                    seen.add(begin)
                    body = image.get_data(begin - 0x180000000, functions[begin] - begin)
                    for insn in decoder.disasm(body, begin):
                        if insn.bytes[:1] in (b"\xe8", b"\xe9"):
                            pending.append(insn.address + insn.size + int.from_bytes(
                                insn.bytes[1:5], "little", signed=True))
                        elif insn.bytes[:2] == b"\xff\x15":
                            slot = insn.address + 6 + int.from_bytes(insn.bytes[2:6], "little", signed=True)
                            self.assertNotEqual(imports[slot], b"user32.dll")
                self.assertGreater(len(seen), 1)
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_reset_mutator_does_not_lock_the_skip_array(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        mfc = (ROOT / "v3d_files_" / "mfc140.dll").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        self.assertEqual(hashlib.sha256(mfc).hexdigest(),
                         "0cf26008fae0cb61dfe49e1c3fc17e0dd860be011d9a6a64b452f56335bafbfe")
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image:
                self.assertEqual(image.get_data(0x541050, 0x28), bytes.fromhex(
                    "40534883ec20488bd94983c8ff4881c1e023000033d2"
                    "e861ed2300488bcb4883c4205be9f864feff"))
                call = image.get_data(0x541066, 5)
                self.assertEqual(call[0], 0xE8)
                self.assertEqual(0x14054106B + struct.unpack_from("<i", call, 1)[0], 0x14077FDCC)
                thunk = image.get_data(0x77FDCC, 6)
                self.assertEqual(thunk[:2], b"\xff\x25")
                slot = 0x14077FDD2 + struct.unpack_from("<i", thunk, 2)[0]
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                imports = {
                    item.address: ((entry.dll or b"").lower(), item.ordinal)
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                self.assertEqual(imports[slot], (b"mfc140.dll", 13522))
            with pefile.PE(data=mfc, fast_load=True) as image:
                self.assertEqual(image.OPTIONAL_HEADER.ImageBase, 0x180000000)
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"]])
                export = image.DIRECTORY_ENTRY_EXPORT
                rva = image.get_dword_at_rva(
                    export.struct.AddressOfFunctions + 4 * (13522 - export.struct.Base))
                self.assertEqual(rva, 0x1D6AC0)
                functions = {
                    0x180000000 + item.struct.BeginAddress: 0x180000000 + item.struct.EndAddress
                    for item in image.DIRECTORY_ENTRY_EXCEPTION}
                self.assertEqual(functions[0x1801D6AC0], 0x1801D6C33)
                zero = image.get_data(0x1D6AF3, 0x1801D6B29 - 0x1801D6AF3)
                self.assertEqual(zero, bytes.fromhex(
                    "488b49084885ed752dff15567a0f00"
                    "48895e0848895e1848895e10"
                    "488b5c2430488b6c2438488b742440488b7c24484883c420415ec3"))
                self.assertEqual(zero.count(b"\xff\x15"), 1)
                self.assertEqual(zero.find(b"\xe8"), -1)
                free_slot = 0x1801D6B02 + struct.unpack_from("<i", zero, 11)[0]
                imports = {
                    item.address: ((entry.dll or b"").lower(), (item.name or b"").decode().lower())
                    for entry in image.DIRECTORY_ENTRY_IMPORT for item in entry.imports}
                dll, symbol = imports[free_slot]
                self.assertEqual(dll, b"api-ms-win-crt-heap-l1-1-0.dll")
                self.assertEqual(symbol, "free")
                negative = image.get_data(0x1D6AE1, 9)
                self.assertEqual(negative, bytes.fromhex("4885d20f8843010000"))
                self.assertEqual(0x1801D6AEA + 0x143, 0x1801D6C2D)
                self.assertEqual(image.get_data(0x1D6C2D, 5), bytes.fromhex("e83e410500"))
                self.assertEqual(0x1801D6C32 + 0x5413E, 0x18022AD70)
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_shared_critical_sections_do_not_cover_the_skip_reload(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                functions = {
                    IMAGE_BASE + item.struct.BeginAddress: IMAGE_BASE + item.struct.EndAddress
                    for item in image.DIRECTORY_ENTRY_EXCEPTION}
                imports = {}
                for entry in image.DIRECTORY_ENTRY_IMPORT:
                    for item in entry.imports:
                        name = item.name.decode().lower() if item.name else ""
                        imports[item.address] = name
                lock_slots = {
                    addr for addr, name in imports.items()
                    if name in ("entercriticalsection", "leavecriticalsection")}
                self.assertEqual(lock_slots, {0x140D54FA8, 0x140D54FB0})
                text = next(item for item in image.sections if item.Name.startswith(b".text"))
                text_data = text.get_data()
                text_base = IMAGE_BASE + text.VirtualAddress
                thunks = {}
                index = 0
                while True:
                    found = text_data.find(b"\xff\x25", index)
                    if found < 0 or found + 6 > len(text_data):
                        break
                    addr = text_base + found
                    slot = addr + 6 + struct.unpack_from("<i", text_data, found + 2)[0]
                    if slot in lock_slots:
                        thunks[addr] = imports[slot]
                    index = found + 1
                self.assertGreaterEqual(len(thunks), 1)
                decoder = Cs(CS_ARCH_X86, CS_MODE_64)

                def closure(roots):
                    seen = set()
                    locks = []
                    pending = list(roots)
                    while pending:
                        begin = pending.pop()
                        if begin in seen or begin not in functions:
                            continue
                        seen.add(begin)
                        body = image.get_data(begin - IMAGE_BASE, functions[begin] - begin)
                        for insn in decoder.disasm(body, begin):
                            if insn.bytes[:2] == b"\xff\x15":
                                slot = insn.address + 6 + int.from_bytes(
                                    insn.bytes[2:6], "little", signed=True)
                                if slot in lock_slots:
                                    locks.append(insn.address)
                                continue
                            if insn.bytes[:1] not in (b"\xe8", b"\xe9"):
                                continue
                            dest = insn.address + insn.size + int.from_bytes(
                                insn.bytes[1:5], "little", signed=True)
                            if dest in thunks:
                                locks.append(insn.address)
                            pending.append(dest)
                    return seen, locks

                refresh, refresh_locks = closure([0x1406ADAF0])
                self.assertEqual(refresh_locks, [
                    0x140780AA8, 0x140780AE8, 0x140780B08, 0x140780C17, 0x140780C38])
                self.assertLess(0x1406ADB2E, 0x1406ADB67)
                self.assertLess(0x1406ADB67, 0x1406ADBB0)
                self.assertEqual(image.get_data(0x6ADB67, 4), bytes.fromhex("488b4708"))
                self.assertEqual(image.get_data(0x6ADBB0, 4), bytes.fromhex("483b4710"))
                holders = {}
                for site in refresh_locks:
                    begin = next(
                        entry for entry, stop in functions.items() if entry <= site < stop)
                    holders[site] = begin
                self.assertEqual(holders, {
                    0x140780AA8: 0x140780A98,
                    0x140780AE8: 0x140780A98,
                    0x140780B08: 0x140780AF8,
                    0x140780C17: 0x140780BBC,
                    0x140780C38: 0x140780BBC,
                })
                for begin in set(holders.values()):
                    body = image.get_data(begin - IMAGE_BASE, functions[begin] - begin)
                    for insn in decoder.disasm(body, begin):
                        if insn.bytes[:1] not in (b"\xe8", b"\xe9"):
                            continue
                        dest = insn.address + insn.size + int.from_bytes(
                            insn.bytes[1:5], "little", signed=True)
                        self.assertNotEqual(dest, 0x140541050)
                resets, reset_locks = closure([
                    0x1404AE9D0, 0x14068F0F0, 0x140692AF0, 0x1406A06B0, 0x1406A20D0])
                self.assertIn(0x140541050, resets)
                self.assertIn(0x140578D14, reset_locks)
                self.assertNotIn(0x140578C80, refresh)
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_cycle_post_before_reset_does_not_drain_skip_refresh(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                functions = {
                    IMAGE_BASE + item.struct.BeginAddress: IMAGE_BASE + item.struct.EndAddress
                    for item in image.DIRECTORY_ENTRY_EXCEPTION}
                imports = {}
                for entry in image.DIRECTORY_ENTRY_IMPORT:
                    for item in entry.imports:
                        name = item.name.decode().lower() if item.name else ""
                        imports[item.address] = name
                post = image.get_data(0x6A27E5, 0x15)
                self.assertEqual(post, bytes.fromhex(
                    "bad687000041b90200000041b800000100488b4940"))
                call = image.get_data(0x6A27FA, 6)
                self.assertEqual(call[:2], b"\xff\x15")
                self.assertEqual(imports[
                    0x1406A2800 + struct.unpack_from("<i", call, 2)[0]], "postmessagea")
                reset = image.get_data(0x6A2D87, 5)
                self.assertEqual(reset[0], 0xE8)
                self.assertEqual(
                    0x1406A2D8C + struct.unpack_from("<i", reset, 1)[0], 0x140541050)
                decoder = Cs(CS_ARCH_X86, CS_MODE_64)
                body = image.get_data(0x6A20D0, functions[0x1406A20D0] - 0x1406A20D0)
                between = []
                for insn in decoder.disasm(body, 0x1406A20D0):
                    if insn.address <= 0x1406A27FA or insn.address >= 0x1406A2D87:
                        continue
                    if insn.bytes[:2] != b"\xff\x15":
                        continue
                    slot = insn.address + 6 + int.from_bytes(insn.bytes[2:6], "little", signed=True)
                    between.append(imports[slot])
                for name in between:
                    self.assertNotIn("waitfor", name)
                    self.assertNotIn("sendmessage", name)
                    self.assertNotIn("entercriticalsection", name)
                rdata = next(item for item in image.sections if item.Name.startswith(b".rdata"))
                data = rdata.get_data()
                base = IMAGE_BASE + rdata.VirtualAddress
                bindings = []
                index = 0
                needle = struct.pack("<I", 0x87D6)
                while True:
                    found = data.find(needle, index)
                    if found < 0 or found + 32 > len(data):
                        break
                    message, code, first, last, sig, pfn = struct.unpack_from("<IIIIQQ", data, found)
                    if message == 0x87D6 and code == first == last == 0:
                        bindings.append(pfn)
                    index = found + 1
                self.assertEqual(bindings, [0x1406B2320])
                pending = [0x1406B2320]
                seen = set()
                while pending:
                    begin = pending.pop()
                    if begin in seen or begin not in functions:
                        continue
                    seen.add(begin)
                    handler = image.get_data(begin - IMAGE_BASE, functions[begin] - begin)
                    for insn in decoder.disasm(handler, begin):
                        if insn.bytes[:1] not in (b"\xe8", b"\xe9"):
                            continue
                        pending.append(insn.address + insn.size + int.from_bytes(
                            insn.bytes[1:5], "little", signed=True))
                self.assertNotIn(0x1406ADAF0, seen)
                self.assertNotIn(0x140541050, seen)
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_pre_reset_send_is_not_the_skip_refresh_message(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                functions = {
                    IMAGE_BASE + item.struct.BeginAddress: IMAGE_BASE + item.struct.EndAddress
                    for item in image.DIRECTORY_ENTRY_EXCEPTION}
                imports = {}
                for entry in image.DIRECTORY_ENTRY_IMPORT:
                    for item in entry.imports:
                        name = item.name.decode().lower() if item.name else ""
                        imports[item.address] = name
                text = next(item for item in image.sections if item.Name.startswith(b".text"))
                text_data = text.get_data()
                text_base = IMAGE_BASE + text.VirtualAddress

                def rip_target(site: int) -> int:
                    raw = image.get_data(site - IMAGE_BASE, 6)
                    self.assertIn(raw[:2], (b"\x8b\x15", b"\x89\x05"))
                    return site + 6 + struct.unpack_from("<i", raw, 2)[0]

                skip_guid = b"{FEA8416F-2D59-478F-BEFF-5D96AFD6A551}"
                other_guid = b"{5D5B3537-9C21-4d59-AEB5-EA30A0D68618}"
                rdata = next(item for item in image.sections if item.Name.startswith(b".rdata"))
                rdata_bytes = rdata.get_data()
                self.assertIn(skip_guid, rdata_bytes)
                self.assertIn(other_guid, rdata_bytes)
                self.assertEqual(rip_target(0x14029B671), 0x1411982C8)
                self.assertEqual(rip_target(0x1402934F1), 0x141195C40)
                self.assertEqual(rip_target(0x140398431), 0x1411DCB30)
                self.assertEqual(rip_target(0x14028A311), 0x141193470)
                self.assertEqual(rip_target(0x140685CE6), 0x141193470)
                posts = {
                    0x1406A1031: 0x141195C40,
                    0x1406A106B: 0x141195C40,
                    0x140736FE1: 0x1411DCB30,
                }
                decoder = Cs(CS_ARCH_X86, CS_MODE_64)
                for site, global_slot in posts.items():
                    self.assertEqual(rip_target(site), global_slot)
                    begin = next(
                        entry for entry, stop in functions.items() if entry <= site < stop)
                    body = image.get_data(begin - IMAGE_BASE, functions[begin] - begin)
                    insns = list(decoder.disasm(body, begin))
                    index = next(i for i, insn in enumerate(insns) if insn.address == site)
                    slot = None
                    for insn in insns[index + 1:index + 8]:
                        if insn.bytes[:2] != b"\xff\x15":
                            continue
                        slot = insn.address + 6 + int.from_bytes(
                            insn.bytes[2:6], "little", signed=True)
                        break
                    self.assertIsNotNone(slot)
                    self.assertEqual(imports[slot], "postmessagea")
                loads = []
                for index in range(len(text_data) - 6):
                    if text_data[index:index + 2] != b"\x8b\x15":
                        continue
                    site = text_base + index
                    if rip_target(site) in {0x1411982C8, 0x141195C40, 0x1411DCB30}:
                        loads.append(site)
                self.assertEqual(loads, [0x1406A1031, 0x1406A106B, 0x140736FE1])
                call = image.get_data(0x6A2B79, 5)
                self.assertEqual(call[0], 0xE8)
                self.assertEqual(0x1406A2B7E + struct.unpack_from("<i", call, 1)[0], 0x140685B70)
                self.assertLess(0x1406A2B79, 0x1406A2D87)
                pending = [0x140685B70]
                seen = set()
                while pending:
                    begin = pending.pop()
                    if begin in seen or begin not in functions:
                        continue
                    seen.add(begin)
                    body = image.get_data(begin - IMAGE_BASE, functions[begin] - begin)
                    for insn in decoder.disasm(body, begin):
                        if insn.bytes[:1] not in (b"\xe8", b"\xe9"):
                            continue
                        pending.append(insn.address + insn.size + int.from_bytes(
                            insn.bytes[1:5], "little", signed=True))
                self.assertNotIn(0x1406ADAF0, seen)
                self.assertNotIn(0x140541050, seen)
                self.assertNotIn(0x1406B0700, seen)
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit

    def test_pre_reset_wait_does_not_pump_the_skip_reader(self) -> None:
        source = (ROOT / "v3d_files_" / "Vision3D.exe").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), SOURCE_HASH)
        controller = (ROOT / "v3d_files_" / "ViVirtualMachine.dll").read_bytes()
        self.assertEqual(
            hashlib.sha256(controller).hexdigest(),
            "5b62adea102b62a272860bfba72cb787bf74bd006f44fe97453df5121efeeb60")
        import_limit = pefile.MAX_IMPORT_SYMBOLS
        try:
            pefile.MAX_IMPORT_SYMBOLS = 65536
            with pefile.PE(data=source, fast_load=True) as image:
                image.parse_data_directories(directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXCEPTION"],
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
                functions = {
                    IMAGE_BASE + item.struct.BeginAddress: IMAGE_BASE + item.struct.EndAddress
                    for item in image.DIRECTORY_ENTRY_EXCEPTION}
                imports = {}
                for entry in image.DIRECTORY_ENTRY_IMPORT:
                    for item in entry.imports:
                        name = item.name.decode().lower() if item.name else ""
                        imports[item.address] = name
                call = image.get_data(0x6A2B81, 5)
                self.assertEqual(call[0], 0xE8)
                self.assertEqual(0x1406A2B86 + struct.unpack_from("<i", call, 1)[0], 0x1406A9DB0)
                self.assertLess(0x1406A2B81, 0x1406A2D87)
                wait = image.get_data(0x6A9E5D, 0x1406A9E87 - 0x1406A9E5D)
                self.assertEqual(wait, bytes.fromhex(
                    "488b471848894597"
                    "488b87a80100004889459f"
                    "41b90a0000004533c0488d5597418d49f8"
                    "ff1509b26a00"))
                slot = 0x1406A9E87 + struct.unpack_from("<i", image.get_data(0x6A9E83, 4), 0)[0]
                self.assertEqual(imports[slot], "waitformultipleobjects")
                decoder = Cs(CS_ARCH_X86, CS_MODE_64)
                body = image.get_data(0x6A9DB0, functions[0x1406A9DB0] - 0x1406A9DB0)
                names = []
                pending = [0x1406A9DB0]
                seen = set()
                for insn in decoder.disasm(body, 0x1406A9DB0):
                    if insn.bytes[:2] != b"\xff\x15":
                        continue
                    slot = insn.address + 6 + int.from_bytes(insn.bytes[2:6], "little", signed=True)
                    names.append(imports[slot])
                self.assertNotIn("sendmessagea", names)
                self.assertNotIn("peekmessagea", names)
                self.assertNotIn("dispatchmessagea", names)
                while pending:
                    begin = pending.pop()
                    if begin in seen or begin not in functions:
                        continue
                    seen.add(begin)
                    callee = image.get_data(begin - IMAGE_BASE, functions[begin] - begin)
                    for insn in decoder.disasm(callee, begin):
                        if insn.bytes[:1] not in (b"\xe8", b"\xe9"):
                            continue
                        pending.append(insn.address + insn.size + int.from_bytes(
                            insn.bytes[1:5], "little", signed=True))
                self.assertNotIn(0x1406ADAF0, seen)
                self.assertNotIn(0x1406B0700, seen)
            with pefile.PE(data=controller, fast_load=True) as image:
                self.assertEqual(image.OPTIONAL_HEADER.ImageBase, 0x180000000)
                slot = struct.unpack_from("<Q", image.get_data(0xCEDA8 + 0x30, 8))[0]
                self.assertEqual(slot, 0x180070ED0)
                self.assertEqual(image.get_data(0x70ED0, 11), bytes.fromhex(
                    "488b81600800008b4010c3"))
        finally:
            pefile.MAX_IMPORT_SYMBOLS = import_limit


class DrainGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.functions = verified_functions()

    def test_stock_wait_failed_discards_tracking_and_returns_success(self) -> None:
        emulator = DrainEmulator(self.functions, guarded=False, count=2,
                                 wait_results=[0xFFFFFFFF])
        self.assertEqual(emulator.run(DRAIN), 1)
        self.assertEqual(emulator.closed, emulator.handles)
        self.assertEqual(emulator.clear_count, 1)
        self.assertEqual(emulator.read(POOL + 0x78), 0)

    def test_guard_all_nonzero_results_preserve_tracking_and_return_false(self) -> None:
        for result in (0x102, 0xFFFFFFFF, 0x80, 1):
            for prior_success in (False, True):
                with self.subTest(result=result, prior_success=prior_success):
                    outcomes = [0, result] if prior_success else [result]
                    emulator = DrainEmulator(self.functions, guarded=True, count=65,
                                             wait_results=outcomes)
                    self.assertEqual(emulator.run(DRAIN), 0)
                    self.assertEqual(emulator.closed, [])
                    self.assertEqual(emulator.clear_count, 0)
                    self.assertEqual(emulator.wait_results, [])
                    self.assertEqual(len(emulator.batches), 2 if prior_success else 1)
                    self.assertEqual(bytes(emulator.cpu.mem_read(FIXTURE, 0x20000)), emulator.before)

    def test_guard_preserves_stock_successful_batched_waits(self) -> None:
        for count in (0, 1, 64, 65, 129):
            with self.subTest(count=count):
                outcomes = [0] * ((count + 63) // 64)
                stock = DrainEmulator(self.functions, guarded=False, count=count,
                                     wait_results=outcomes)
                guarded = DrainEmulator(self.functions, guarded=True, count=count,
                                       wait_results=outcomes)
                self.assertEqual(guarded.run(DRAIN), 1)
                self.assertEqual(stock.run(DRAIN), 1)
                self.assertEqual(guarded.batches, stock.batches)
                self.assertEqual(guarded.closed, guarded.handles)
                self.assertEqual(guarded.closed, stock.closed)
                self.assertEqual(guarded.clear_count, stock.clear_count)
                self.assertEqual(bytes(guarded.cpu.mem_read(FIXTURE, 0x20000)),
                                 bytes(stock.cpu.mem_read(FIXTURE, 0x20000)))


if __name__ == "__main__":
    unittest.main(verbosity=2)