"""Build the hardened Vision3D 70.06.59 threshold-skip revision.

The injected implementation is deliberately scoped to this exact executable
and its matching result DLLs.  It uses:

* one atomic counter/state context per live CDataCaoTraitement (CAO);
* one winning SkipSubPanel caller per sub-panel;
* the final, stock-merged defect mask;
* worker-local normalization after the current anomaly's stock RazRes; and
* non-destructive serial reconciliation before review routing.

The patch fails open to stock Vision3D behavior if its context table is full or
if serial reconciliation encounters an invalid production/anomaly layout.
"""
from __future__ import annotations

import hashlib
import pathlib
import struct
import sys

try:
    from keystone import KS_ARCH_X86, KS_MODE_64, Ks, KsError
except ImportError as exc:  # pragma: no cover - exercised on clean builders
    raise SystemExit(
        "keystone-engine 0.9.2 is required; run "
        "'python -m pip install -r tools/requirements.txt'"
    ) from exc


IMAGE_BASE = 0x140000000
TEXT_VA = 0x1000
TEXT_RAW = 0x400

SOURCE_SHA256 = "ccca11b2f05084b484fa5556c67f8874065dbc0b6265177d2517f81265af00f4"
AVVTRAIT_SHA256 = "0f9f68b118112cea87e1735995776934d8d009e3d6d39a8a58562e3fa3e3e5f7"
STRUCTSUPPORT_SHA256 = (
    "d6270dbe5c97b5ed1000c2541c1e8d495d7db6be184e45d6495d7fad75e0f832"
)
EXPECTED_OUTPUT_SHA256 = (
    "0ef39ff59e216bb7e9a45f6cb7ee505eac0822f6c4939d8ff1a8e04197675c13"
)

# Hook after the stock supplemental-mask merge and current-anomaly RazRes.
COUNT_HOOK = 0x140736F47
COUNT_HOOK_RET = 0x140736F52
COUNT_HOOK_ORIG = bytes.fromhex("498b4f1080b93538000001")
EXECUTE_ONE_EARLY_EXIT = 0x14073742D

RESET_HOOK = 0x140541050
RESET_CONT = 0x140541056
RESET_ORIG = bytes.fromhex("40534883ec20")

# Replace the stock call, preserving RCX=CProdCarte, with a serial wrapper.
FINAL_CALL = 0x14069B4D8
FINAL_CALL_ORIG = bytes.fromhex("e84393fdff")
SHOULD_REVIEW = 0x140674820
GET_CAO = 0x1406A15D0

STOCK_SKIP_CALL = 0x140736FCB
STOCK_SKIP_CALL_ORIG = bytes.fromhex("e8b0a0e0ff")

REVIEW_ROUTE_TEST = 0x1406748C5
REVIEW_ROUTE_ORIG = bytes.fromhex("f70498fffeffff")
REVIEW_ROUTE_PATCH = bytes.fromhex("f70498ffffffff")

SKIPSUB = 0x140541080
POSTMESSAGE_IAT = 0x140D5BC00
SKIP_UI_MESSAGE = 0x1411DCB30

MISSING_PERCENT = 30
MIN_INSPECTED = 10

# Added sections.  The RW section has no file payload.
CODE_RVA = 0x1C98000
CODE_SIZE = 0x2000
DATA_RVA = CODE_RVA + CODE_SIZE
DATA_SIZE = 0x29000
CAVE = IMAGE_BASE + CODE_RVA
DATA_VA = IMAGE_BASE + DATA_RVA

COUNT_CAVE = CAVE + 0x000
RESET_CAVE = CAVE + 0x500
FINAL_CAVE = CAVE + 0x700
EXCEPTION_HANDLER_CAVE = CAVE + 0xB00
COUNT_EXCEPTION_HANDLER_CAVE = CAVE + 0xB40
STOCK_SKIP_CAVE = CAVE + 0xC00
STOCK_SKIP_EXCEPTION_CAVE = CAVE + 0xE00

COUNT_UNWIND_OFFSET = 0x1F00
RESET_UNWIND_OFFSET = 0x1F10
FINAL_UNWIND_OFFSET = 0x1F20
STOCK_SKIP_UNWIND_OFFSET = 0x1F50

# Eight independent CAO contexts.  A stock CAO already owns the mutable skip
# list and production-zone array, so it is the correct isolation/lifecycle key.
CONTEXT_COUNT = 8
SUBPANEL_SLOTS = 1024
CELL_SIZE = 16
CONTEXT_HEADER = 0x20
CONTEXT_STRIDE = 0x5000
GLOBAL_TABLE_LOCK = CONTEXT_COUNT * CONTEXT_STRIDE
GLOBAL_UNSUPPORTED = GLOBAL_TABLE_LOCK + 4
GLOBAL_FULL = GLOBAL_TABLE_LOCK + 8
CONTEXT_STATUS = 0x08
CONTEXT_FLAGS = 0x0C
CONTEXT_DIAGNOSTIC = 0x10
CONTEXT_REFCOUNT = 0x14
CONTEXT_SKIP_LOCK = 0x18
CONTEXT_CELLS = CONTEXT_HEADER

CELL_INSPECTED = 0x00
CELL_MISSING = 0x04
CELL_STATE = 0x08

MAX_PRODUCTION_ZONES = 4096
MAX_ANOMALIES_PER_ZONE = 1_000_000

_ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC_DEFAULT = _ROOT / "v3d_files_" / "Vision3D.exe"
OUT_DEFAULT = _ROOT / "Updated" / "Vision3D_concurrency_fix.exe"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def align_up(value: int, alignment: int) -> int:
    return (value + alignment - 1) & -alignment


def va_to_text_off(va: int) -> int:
    return TEXT_RAW + ((va - IMAGE_BASE) - TEXT_VA)


def rel32(src: int, dest: int) -> bytes:
    return struct.pack("<i", dest - (src + 5))


def assemble(source: str, address: int) -> bytes:
    assembler = Ks(KS_ARCH_X86, KS_MODE_64)
    try:
        encoding, _ = assembler.asm(source, addr=address)
    except KsError as exc:
        raise RuntimeError("assembly failed at 0x%X: %s" % (address, exc)) from exc
    return bytes(encoding)


def count_handler_source() -> str:
    data_delta = DATA_VA - COUNT_CAVE
    normal_delta = COUNT_HOOK_RET - COUNT_CAVE
    early_delta = EXECUTE_ONE_EARLY_EXIT - COUNT_CAVE
    return f"""
code_base:
    sub rsp, 0x38
    mov qword ptr [rsp + 0x20], 0
    mov qword ptr [rsp + 0x28], 0
    mov dword ptr [rsp + 0x30], 0

    mov r8, qword ptr [r15 + 0x10]
    test r8, r8
    jz normal
    mov r9d, dword ptr [rdi + 0x14]
    cmp r9d, {SUBPANEL_SLOTS}
    jae unsupported

    lea r10, [rip + code_base]
    add r10, {data_delta}
table_lock_spin:
    xor eax, eax
    mov edx, 1
    lock cmpxchg dword ptr [r10 + {GLOBAL_TABLE_LOCK}], edx
    jnz table_lock_spin
    mov ecx, {CONTEXT_COUNT}
    xor r11d, r11d

find_context:
    mov rax, qword ptr [r10]
    cmp rax, r8
    je context_found
    test rax, rax
    jnz next_context
    test r11, r11
    cmovz r11, r10
next_context:
    add r10, {CONTEXT_STRIDE}
    dec ecx
    jnz find_context
    test r11, r11
    jz context_full
    mov r10, r11

claim_context:
    mov qword ptr [r10], r8
    mov dword ptr [r10 + {CONTEXT_STATUS}], 1

context_found:
    cmp dword ptr [r10 + {CONTEXT_STATUS}], 1
    jne table_unlock_normal
    lock inc dword ptr [r10 + {CONTEXT_REFCOUNT}]
    mov qword ptr [rsp + 0x20], r10

    mov eax, r9d
    shl rax, 4
    lea r11, [r10 + rax + {CONTEXT_CELLS}]

    mov eax, dword ptr [r11 + {CELL_STATE}]
    test eax, eax
    jnz table_unlock_existing

    mov eax, 1
    lock xadd dword ptr [r11 + {CELL_INSPECTED}], eax
    inc eax
    test ebx, 1
    jz read_missing

    mov ecx, 1
    lock xadd dword ptr [r11 + {CELL_MISSING}], ecx
    inc ecx
    jmp have_missing
read_missing:
    mov ecx, dword ptr [r11 + {CELL_MISSING}]
have_missing:
    cmp eax, {MIN_INSPECTED}
    jb table_unlock_normal
    imul ecx, ecx, 100
    imul eax, eax, {MISSING_PERCENT}
    cmp ecx, eax
    jbe table_unlock_normal

    xor eax, eax
    mov ecx, 1
    lock cmpxchg dword ptr [r11 + {CELL_STATE}], ecx
    jnz table_unlock_existing
    lea rax, [rip + code_base]
    add rax, {data_delta}
    mov dword ptr [rax + {GLOBAL_TABLE_LOCK}], 0
    jmp trigger_winner

table_unlock_existing:
    lea rdx, [rip + code_base]
    add rdx, {data_delta}
    mov dword ptr [rdx + {GLOBAL_TABLE_LOCK}], 0

existing_state:
    cmp eax, 2
    jae mark_current_skipped
    cmp eax, 1
    jne normal
state_wait:
    mov eax, dword ptr [r11 + {CELL_STATE}]
    cmp eax, 2
    jae mark_current_skipped
    cmp eax, 1
    jne normal
    pause
    jmp state_wait

trigger_winner:
    mov qword ptr [rsp + 0x28], r11
skip_lock_spin:
    xor eax, eax
    mov edx, 1
    lock cmpxchg dword ptr [r10 + {CONTEXT_SKIP_LOCK}], edx
    jnz skip_lock_spin
    mov dword ptr [rsp + 0x30], 1
    mov rcx, r8
    mov edx, r9d
    call {SKIPSUB}
    mov r10, qword ptr [rsp + 0x20]
    mov dword ptr [r10 + {CONTEXT_SKIP_LOCK}], 0
    mov dword ptr [rsp + 0x30], 0
    mov r11, qword ptr [rsp + 0x28]
    mov eax, 2
    xchg dword ptr [r11 + {CELL_STATE}], eax

mark_current_skipped:
    mov dword ptr [r13 + 0x28], 0
    mov dword ptr [r13 + 0x2c], 1
    mov r10, qword ptr [rsp + 0x20]
    test r10, r10
    jz mark_return
    mov qword ptr [rsp + 0x20], 0
    lock dec dword ptr [r10 + {CONTEXT_REFCOUNT}]
mark_return:
    lea rax, [rip + code_base]
    add rax, {early_delta}
    mov qword ptr [rsp + 0x38], rax
    lea rsp, [rsp + 0x38]
    ret

unsupported:
    lea r10, [rip + code_base]
    add r10, {data_delta}
    lock inc dword ptr [r10 + {GLOBAL_UNSUPPORTED}]
    jmp normal

context_full:
    lock inc dword ptr [r10 + {GLOBAL_FULL - CONTEXT_COUNT * CONTEXT_STRIDE}]

table_unlock_normal:
    lea rax, [rip + code_base]
    add rax, {data_delta}
    mov dword ptr [rax + {GLOBAL_TABLE_LOCK}], 0

normal:
    mov r10, qword ptr [rsp + 0x20]
    test r10, r10
    jz normal_return
    mov qword ptr [rsp + 0x20], 0
    lock dec dword ptr [r10 + {CONTEXT_REFCOUNT}]
normal_return:
    lea rax, [rip + code_base]
    add rax, {normal_delta}
    mov qword ptr [rsp + 0x38], rax
    mov rcx, qword ptr [r15 + 0x10]
    cmp byte ptr [rcx + 0x3835], 1
    lea rsp, [rsp + 0x38]
    ret
"""


def reset_handler_source() -> str:
    data_delta = DATA_VA - RESET_CAVE
    clear_qwords = (CONTEXT_STRIDE - 8) // 8
    return f"""
code_base:
    push rbx
    sub rsp, 0x20
    push rdi
    mov r9, rcx

    lea r10, [rip + code_base]
    add r10, {data_delta}
table_lock_spin:
    xor eax, eax
    mov r8d, 1
    lock cmpxchg dword ptr [r10 + {GLOBAL_TABLE_LOCK}], r8d
    jnz table_lock_spin
    mov ecx, {CONTEXT_COUNT}
find_context:
    cmp qword ptr [r10], r9
    je found_context
    add r10, {CONTEXT_STRIDE}
    dec ecx
    jnz find_context
    jmp table_unlock_replay

found_context:
    cmp dword ptr [r10 + {CONTEXT_STATUS}], 1
    je retire_context
    cmp dword ptr [r10 + {CONTEXT_STATUS}], 2
    jne table_unlock_replay
    jmp retired
retire_context:
    mov dword ptr [r10 + {CONTEXT_STATUS}], 2
retired:
    lea rax, [rip + code_base]
    add rax, {data_delta}
    mov dword ptr [rax + {GLOBAL_TABLE_LOCK}], 0
wait_workers:
    cmp dword ptr [r10 + {CONTEXT_REFCOUNT}], 0
    je clear_context
    pause
    jmp wait_workers
clear_context:
    lea r11, [rip + code_base]
    add r11, {data_delta}
clear_lock_spin:
    xor eax, eax
    mov r8d, 1
    lock cmpxchg dword ptr [r11 + {GLOBAL_TABLE_LOCK}], r8d
    jnz clear_lock_spin
    cmp qword ptr [r10], r9
    jne clear_unlock_replay
    cmp dword ptr [r10 + {CONTEXT_STATUS}], 2
    jne clear_unlock_replay
    cmp dword ptr [r10 + {CONTEXT_REFCOUNT}], 0
    jne clear_unlock_replay
    lea rdi, [r10 + 8]
    xor eax, eax
    mov ecx, {clear_qwords}
    rep stosq
    mov qword ptr [r10], rax
clear_unlock_replay:
    mov dword ptr [r11 + {GLOBAL_TABLE_LOCK}], 0
    jmp replay

table_unlock_replay:
    lea rax, [rip + code_base]
    add rax, {data_delta}
    mov dword ptr [rax + {GLOBAL_TABLE_LOCK}], 0

replay:
    mov rcx, r9
    pop rdi
    jmp {RESET_CONT}
"""


def final_handler_source() -> str:
    data_delta = DATA_VA - FINAL_CAVE
    message_delta = SKIP_UI_MESSAGE - FINAL_CAVE
    post_iat_delta = POSTMESSAGE_IAT - FINAL_CAVE
    return f"""
code_base:
    push rbx
    push rsi
    push rdi
    push r12
    push r13
    push r15
    sub rsp, 0x38
    mov rdi, rcx
    mov qword ptr [rsp + 0x20], 0

    mov rcx, r14
    call {GET_CAO}
    test rax, rax
    jz call_review
    mov r13, rax

    lea r12, [rip + code_base]
    add r12, {data_delta}
table_lock_spin:
    xor eax, eax
    mov edx, 1
    lock cmpxchg dword ptr [r12 + {GLOBAL_TABLE_LOCK}], edx
    jnz table_lock_spin
    mov ecx, {CONTEXT_COUNT}
find_context:
    cmp qword ptr [r12], r13
    je context_match
    add r12, {CONTEXT_STRIDE}
    dec ecx
    jnz find_context
    jmp table_unlock_review

context_match:
    cmp dword ptr [r12 + {CONTEXT_STATUS}], 1
    jne table_unlock_review
    lock inc dword ptr [r12 + {CONTEXT_REFCOUNT}]
    mov qword ptr [rsp + 0x20], r12
    lea rax, [rip + code_base]
    add rax, {data_delta}
    mov dword ptr [rax + {GLOBAL_TABLE_LOCK}], 0

    xor ebx, ebx
    xor r15d, r15d
    lea rsi, [r12 + {CONTEXT_CELLS}]
    mov ecx, {SUBPANEL_SLOTS}
scan_states:
    mov eax, dword ptr [rsi + {CELL_STATE}]
    cmp eax, 2
    jb next_state
    mov r15d, 1
    cmp eax, 2
    jne next_state
    mov ebx, 1
next_state:
    add rsi, {CELL_SIZE}
    dec ecx
    jnz scan_states
    test r15d, r15d
    jz call_review
    test ebx, ebx
    jz post_ui

    mov eax, dword ptr [r13 + 0x5880]
    test eax, eax
    jle invalid_layout
    cmp eax, {MAX_PRODUCTION_ZONES}
    ja invalid_layout
    mov dword ptr [rsp + 0x28], eax
    mov rsi, qword ptr [r13 + 0x5878]
    test rsi, rsi
    jz invalid_layout

    xor r15d, r15d
validate_zone:
    mov eax, r15d
    imul rax, rax, 0x410
    lea rdx, [rsi + rax]
    mov r8, qword ptr [rdx + 0x18]
    mov r9, qword ptr [rdx + 0x20]
    cmp r8, r9
    je validated_zone
    test r8, r8
    jz invalid_layout
    test r9, r9
    jz invalid_layout
    cmp r9, r8
    jb invalid_layout
    mov rax, r9
    sub rax, r8
    xor edx, edx
    mov ecx, 0x370
    div rcx
    test rdx, rdx
    jnz invalid_layout
    cmp rax, {MAX_ANOMALIES_PER_ZONE}
    ja invalid_layout
validated_zone:
    inc r15d
    cmp r15d, dword ptr [rsp + 0x28]
    jb validate_zone

    mov rsi, qword ptr [r13 + 0x5878]
    xor r15d, r15d
mutate_zone:
    mov eax, r15d
    imul rax, rax, 0x410
    lea rdx, [rsi + rax]
    mov rbx, qword ptr [rdx + 0x18]
    mov r9, qword ptr [rdx + 0x20]
mutate_anomaly:
    cmp rbx, r9
    jae next_mutate_zone
    cmp byte ptr [rbx + 0x280], 0
    je next_anomaly
    cmp dword ptr [rbx + 0x2c], 0
    jne next_anomaly
    mov eax, dword ptr [rbx + 8]
    cmp eax, {SUBPANEL_SLOTS}
    jae next_anomaly
    mov ecx, eax
    shl rcx, 4
    lea rdx, [r12 + rcx + {CONTEXT_CELLS}]
    cmp dword ptr [rdx + {CELL_STATE}], 2
    jb next_anomaly
    mov dword ptr [rbx + 0x28], 0
    mov dword ptr [rbx + 0x2c], 1
next_anomaly:
    add rbx, 0x370
    jmp mutate_anomaly
next_mutate_zone:
    inc r15d
    cmp r15d, dword ptr [rsp + 0x28]
    jb mutate_zone

    lea rsi, [r12 + {CONTEXT_CELLS}]
    mov ecx, {SUBPANEL_SLOTS}
publish_reconciled:
    mov eax, 2
    mov edx, 3
    lock cmpxchg dword ptr [rsi + {CELL_STATE}], edx
    add rsi, {CELL_SIZE}
    dec ecx
    jnz publish_reconciled

post_ui:
    bt dword ptr [r12 + {CONTEXT_FLAGS}], 0
    jc call_review
    mov rcx, qword ptr [r13 + 0x5838]
    test rcx, rcx
    jz call_review
    mov rcx, qword ptr [rcx + 0x40]
    test rcx, rcx
    jz call_review
    lock bts dword ptr [r12 + {CONTEXT_FLAGS}], 0
    jc call_review
    xor r9d, r9d
    xor r8d, r8d
    lea rax, [rip + code_base]
    add rax, {message_delta}
    mov edx, dword ptr [rax]
    lea rax, [rip + code_base]
    add rax, {post_iat_delta}
    call qword ptr [rax]
    test eax, eax
    jnz call_review
    lock btr dword ptr [r12 + {CONTEXT_FLAGS}], 0
    jmp call_review

invalid_layout:
    lock or dword ptr [r12 + {CONTEXT_DIAGNOSTIC}], 1
    jmp call_review

table_unlock_review:
    lea rax, [rip + code_base]
    add rax, {data_delta}
    mov dword ptr [rax + {GLOBAL_TABLE_LOCK}], 0

call_review:
    mov rax, qword ptr [rsp + 0x20]
    test rax, rax
    jz invoke_review
    mov qword ptr [rsp + 0x20], 0
    lock dec dword ptr [rax + {CONTEXT_REFCOUNT}]
invoke_review:
    mov rcx, rdi
    call {SHOULD_REVIEW}
    add rsp, 0x38
    pop r15
    pop r13
    pop r12
    pop rdi
    pop rsi
    pop rbx
    ret
"""


def exception_cleanup_source() -> str:
    return f"""
    mov rax, qword ptr [rdx + 0x20]
    test rax, rax
    jz cleanup_done
    mov qword ptr [rdx + 0x20], 0
    lock dec dword ptr [rax + {CONTEXT_REFCOUNT}]
cleanup_done:
    mov eax, 1
    ret
"""


def count_exception_cleanup_source() -> str:
    return f"""
    mov rax, qword ptr [rdx + 0x20]
    test rax, rax
    jz cleanup_done
    cmp dword ptr [rdx + 0x30], 0
    je no_skip_lock
    mov dword ptr [rax + {CONTEXT_SKIP_LOCK}], 0
no_skip_lock:
    mov r8, qword ptr [rdx + 0x28]
    test r8, r8
    jz no_cell
    mov dword ptr [r8 + {CELL_STATE}], 0
no_cell:
    mov qword ptr [rdx + 0x20], 0
    lock dec dword ptr [rax + {CONTEXT_REFCOUNT}]
cleanup_done:
    mov eax, 1
    ret
"""


def stock_skip_wrapper_source() -> str:
    data_delta = DATA_VA - STOCK_SKIP_CAVE
    return f"""
code_base:
    push rbx
    push rsi
    sub rsp, 0x38
    mov rbx, rcx
    mov esi, edx
    mov qword ptr [rsp + 0x20], 0
    mov dword ptr [rsp + 0x28], 0
    mov dword ptr [rsp + 0x2c], 0
    mov qword ptr [rsp + 0x30], 0

    lea r10, [rip + code_base]
    add r10, {data_delta}
table_lock_spin:
    xor eax, eax
    mov edx, 1
    lock cmpxchg dword ptr [r10 + {GLOBAL_TABLE_LOCK}], edx
    jnz table_lock_spin
    mov ecx, {CONTEXT_COUNT}
find_context:
    cmp qword ptr [r10], rbx
    je context_match
    add r10, {CONTEXT_STRIDE}
    dec ecx
    jnz find_context
    jmp table_locked_call
context_match:
    cmp dword ptr [r10 + {CONTEXT_STATUS}], 1
    jne table_unlock_done
    lock inc dword ptr [r10 + {CONTEXT_REFCOUNT}]
    mov qword ptr [rsp + 0x20], r10
    jmp table_unlock_call
table_locked_call:
    lea rax, [rip + code_base]
    add rax, {data_delta}
    mov qword ptr [rsp + 0x30], rax
    mov dword ptr [rsp + 0x2c], 1
    jmp call_stock
table_unlock_call:
    lea rax, [rip + code_base]
    add rax, {data_delta}
    mov dword ptr [rax + {GLOBAL_TABLE_LOCK}], 0

    mov r10, qword ptr [rsp + 0x20]
    test r10, r10
    jz call_stock
skip_lock_spin:
    xor eax, eax
    mov edx, 1
    lock cmpxchg dword ptr [r10 + {CONTEXT_SKIP_LOCK}], edx
    jnz skip_lock_spin
    mov dword ptr [rsp + 0x28], 1
call_stock:
    mov rcx, rbx
    mov edx, esi
    call {SKIPSUB}
    jmp stock_return

table_unlock_done:
    lea rax, [rip + code_base]
    add rax, {data_delta}
    mov dword ptr [rax + {GLOBAL_TABLE_LOCK}], 0
    jmp done

stock_return:
    cmp dword ptr [rsp + 0x2c], 0
    je no_table_lock
    mov rax, qword ptr [rsp + 0x30]
    mov dword ptr [rax + {GLOBAL_TABLE_LOCK}], 0
    mov dword ptr [rsp + 0x2c], 0
no_table_lock:
    mov r10, qword ptr [rsp + 0x20]
    test r10, r10
    jz done
    mov dword ptr [r10 + {CONTEXT_SKIP_LOCK}], 0
    mov dword ptr [rsp + 0x28], 0
    mov qword ptr [rsp + 0x20], 0
    lock dec dword ptr [r10 + {CONTEXT_REFCOUNT}]
done:
    add rsp, 0x38
    pop rsi
    pop rbx
    ret
"""


def stock_skip_exception_cleanup_source() -> str:
    return f"""
    mov rax, qword ptr [rdx + 0x20]
    test rax, rax
    jz release_table
    cmp dword ptr [rdx + 0x28], 0
    je no_skip_lock
    mov dword ptr [rax + {CONTEXT_SKIP_LOCK}], 0
no_skip_lock:
    mov qword ptr [rdx + 0x20], 0
    lock dec dword ptr [rax + {CONTEXT_REFCOUNT}]
release_table:
    cmp dword ptr [rdx + 0x2c], 0
    je cleanup_done
    mov r8, qword ptr [rdx + 0x30]
    mov dword ptr [r8 + {GLOBAL_TABLE_LOCK}], 0
cleanup_done:
    mov eax, 1
    ret
"""


def build_code() -> tuple[bytes, dict[str, int]]:
    count = assemble(count_handler_source(), COUNT_CAVE)
    reset = assemble(reset_handler_source(), RESET_CAVE)
    final = assemble(final_handler_source(), FINAL_CAVE)
    exception_cleanup = assemble(
        exception_cleanup_source(), EXCEPTION_HANDLER_CAVE
    )
    count_exception_cleanup = assemble(
        count_exception_cleanup_source(), COUNT_EXCEPTION_HANDLER_CAVE
    )
    stock_skip = assemble(stock_skip_wrapper_source(), STOCK_SKIP_CAVE)
    stock_skip_exception = assemble(
        stock_skip_exception_cleanup_source(), STOCK_SKIP_EXCEPTION_CAVE
    )

    if len(count) > RESET_CAVE - COUNT_CAVE:
        raise RuntimeError("count handler overlaps reset handler")
    if len(reset) > FINAL_CAVE - RESET_CAVE:
        raise RuntimeError("reset handler overlaps final handler")
    if len(final) > COUNT_UNWIND_OFFSET - (FINAL_CAVE - CAVE):
        raise RuntimeError("final handler exceeds reserved finalization range")
    if len(exception_cleanup) > COUNT_UNWIND_OFFSET - (
        EXCEPTION_HANDLER_CAVE - CAVE
    ):
        raise RuntimeError("exception cleanup overlaps unwind data")
    if len(count_exception_cleanup) > COUNT_UNWIND_OFFSET - (
        COUNT_EXCEPTION_HANDLER_CAVE - CAVE
    ):
        raise RuntimeError("count exception cleanup overlaps unwind data")
    if len(stock_skip) > STOCK_SKIP_EXCEPTION_CAVE - STOCK_SKIP_CAVE:
        raise RuntimeError("stock skip wrapper overlaps its cleanup handler")
    if len(stock_skip_exception) > COUNT_UNWIND_OFFSET - (
        STOCK_SKIP_EXCEPTION_CAVE - CAVE
    ):
        raise RuntimeError("stock skip cleanup overlaps unwind data")

    payload = bytearray(b"\xCC" * CODE_SIZE)
    payload[COUNT_CAVE - CAVE : COUNT_CAVE - CAVE + len(count)] = count
    payload[RESET_CAVE - CAVE : RESET_CAVE - CAVE + len(reset)] = reset
    payload[FINAL_CAVE - CAVE : FINAL_CAVE - CAVE + len(final)] = final
    payload[
        EXCEPTION_HANDLER_CAVE - CAVE : EXCEPTION_HANDLER_CAVE
        - CAVE
        + len(exception_cleanup)
    ] = exception_cleanup
    payload[
        COUNT_EXCEPTION_HANDLER_CAVE - CAVE : COUNT_EXCEPTION_HANDLER_CAVE
        - CAVE
        + len(count_exception_cleanup)
    ] = count_exception_cleanup
    payload[
        STOCK_SKIP_CAVE - CAVE : STOCK_SKIP_CAVE - CAVE + len(stock_skip)
    ] = stock_skip
    payload[
        STOCK_SKIP_EXCEPTION_CAVE - CAVE : STOCK_SKIP_EXCEPTION_CAVE
        - CAVE
        + len(stock_skip_exception)
    ] = stock_skip_exception

    # Fixed-prologue x64 UNWIND_INFO.
    count_unwind = bytes.fromhex(
        "1104010004620000"
    ) + struct.pack("<I", COUNT_EXCEPTION_HANDLER_CAVE - IMAGE_BASE)
    reset_unwind = bytes.fromhex(
        "010603000670053201300000"
    )  # push rbx; sub rsp,20; push rdi
    final_unwind = bytes.fromhex(
        "110d0700"
        "0d62"  # sub rsp,0x38
        "09f0"  # push r15
        "07d0"  # push r13
        "05c0"  # push r12
        "0370"  # push rdi
        "0260"  # push rsi
        "0130"  # push rbx
        "0000"
    ) + struct.pack("<I", EXCEPTION_HANDLER_CAVE - IMAGE_BASE)
    stock_skip_unwind = bytes.fromhex(
        "11060300"
        "0662"  # sub rsp,0x38
        "0260"  # push rsi
        "0130"  # push rbx
        "0000"
    ) + struct.pack("<I", STOCK_SKIP_EXCEPTION_CAVE - IMAGE_BASE)
    payload[
        COUNT_UNWIND_OFFSET : COUNT_UNWIND_OFFSET + len(count_unwind)
    ] = count_unwind
    payload[
        RESET_UNWIND_OFFSET : RESET_UNWIND_OFFSET + len(reset_unwind)
    ] = reset_unwind
    payload[
        FINAL_UNWIND_OFFSET : FINAL_UNWIND_OFFSET + len(final_unwind)
    ] = final_unwind
    payload[
        STOCK_SKIP_UNWIND_OFFSET : STOCK_SKIP_UNWIND_OFFSET
        + len(stock_skip_unwind)
    ] = stock_skip_unwind
    return bytes(payload), {
        "count_size": len(count),
        "reset_size": len(reset),
        "final_size": len(final),
        "exception_cleanup_size": len(exception_cleanup),
        "count_exception_cleanup_size": len(count_exception_cleanup),
        "stock_skip_size": len(stock_skip),
        "stock_skip_exception_size": len(stock_skip_exception),
    }


def verify_companion_hashes(src: pathlib.Path) -> dict[str, str]:
    directory = src.parent
    expected = {
        "AvVTraitLib.dll": AVVTRAIT_SHA256,
        "StructSupport.dll": STRUCTSUPPORT_SHA256,
    }
    actual: dict[str, str] = {}
    for name, wanted in expected.items():
        path = directory / name
        if not path.is_file():
            raise SystemExit("missing matching companion DLL: %s" % path)
        digest = sha256(path.read_bytes())
        if digest != wanted:
            raise SystemExit(
                "%s hash mismatch: %s (wanted %s)" % (name, digest, wanted)
            )
        actual[name] = digest
    return actual


def add_sections_and_unwind(
    data: bytearray, code_payload: bytes, sizes: dict[str, int]
) -> tuple[int, int]:
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe : pe + 4] != b"PE\x00\x00":
        raise SystemExit("not a PE image")
    section_count = struct.unpack_from("<H", data, pe + 6)[0]
    optional_size = struct.unpack_from("<H", data, pe + 20)[0]
    optional = pe + 24
    if struct.unpack_from("<H", data, optional)[0] != 0x20B:
        raise SystemExit("expected PE32+ image")
    section_alignment = struct.unpack_from("<I", data, optional + 32)[0]
    file_alignment = struct.unpack_from("<I", data, optional + 36)[0]
    size_of_image = struct.unpack_from("<I", data, optional + 56)[0]
    size_of_headers = struct.unpack_from("<I", data, optional + 60)[0]
    if size_of_image != CODE_RVA:
        raise SystemExit(
            "unexpected SizeOfImage 0x%x (wanted 0x%x)" % (size_of_image, CODE_RVA)
        )

    section_table = optional + optional_size
    new_headers_end = section_table + (section_count + 2) * 40
    if new_headers_end > size_of_headers:
        raise SystemExit("no room for two section headers")
    if any(data[section_table + section_count * 40 : new_headers_end]):
        raise SystemExit("new section header slots are not empty")

    sections: dict[bytes, tuple[int, ...]] = {}
    headers: dict[bytes, int] = {}
    for index in range(section_count):
        address = section_table + index * 40
        values = struct.unpack_from("<8sIIIIIIHHI", data, address)
        name = values[0].rstrip(b"\x00")
        sections[name] = values[1:]
        headers[name] = address
    if b".pdata" not in sections:
        raise SystemExit("missing .pdata section")

    pdata = sections[b".pdata"]
    pdata_virtual_size, pdata_rva, pdata_raw_size, pdata_raw = pdata[:4]
    exception_directory = optional + 112 + 3 * 8
    exception_rva, exception_size = struct.unpack_from(
        "<II", data, exception_directory
    )
    if exception_rva != pdata_rva or exception_size != pdata_virtual_size:
        raise SystemExit("unexpected exception directory layout")
    if exception_size % 12:
        raise SystemExit("exception directory is not a RUNTIME_FUNCTION array")
    pdata_append = pdata_raw + exception_size
    runtime_size = 4 * 12
    if pdata_append + runtime_size > pdata_raw + pdata_raw_size:
        raise SystemExit("insufficient .pdata padding")
    if any(data[pdata_append : pdata_append + runtime_size]):
        raise SystemExit(".pdata append area is not empty")
    last_begin = struct.unpack_from("<I", data, pdata_append - 12)[0]
    if last_begin >= CODE_RVA:
        raise SystemExit("new runtime functions would not be sorted")

    code_raw = align_up(len(data), file_alignment)
    code_raw_size = align_up(CODE_SIZE, file_alignment)
    if code_raw > len(data):
        data.extend(b"\x00" * (code_raw - len(data)))
    data.extend(code_payload)
    data.extend(b"\x00" * (code_raw_size - len(code_payload)))

    code_header = struct.pack(
        "<8sIIIIIIHHI",
        b".f1code\x00",
        CODE_SIZE,
        CODE_RVA,
        code_raw_size,
        code_raw,
        0,
        0,
        0,
        0,
        0x60000020,
    )
    data_header = struct.pack(
        "<8sIIIIIIHHI",
        b".f1data\x00",
        DATA_SIZE,
        DATA_RVA,
        0,
        0,
        0,
        0,
        0,
        0,
        0xC0000080,
    )
    new_header = section_table + section_count * 40
    data[new_header : new_header + 40] = code_header
    data[new_header + 40 : new_header + 80] = data_header

    runtime_functions = b"".join(
        [
            struct.pack(
                "<III",
                COUNT_CAVE - IMAGE_BASE,
                COUNT_CAVE - IMAGE_BASE + sizes["count_size"],
                CODE_RVA + COUNT_UNWIND_OFFSET,
            ),
            struct.pack(
                "<III",
                RESET_CAVE - IMAGE_BASE,
                RESET_CAVE - IMAGE_BASE + sizes["reset_size"],
                CODE_RVA + RESET_UNWIND_OFFSET,
            ),
            struct.pack(
                "<III",
                FINAL_CAVE - IMAGE_BASE,
                FINAL_CAVE - IMAGE_BASE + sizes["final_size"],
                CODE_RVA + FINAL_UNWIND_OFFSET,
            ),
            struct.pack(
                "<III",
                STOCK_SKIP_CAVE - IMAGE_BASE,
                STOCK_SKIP_CAVE - IMAGE_BASE + sizes["stock_skip_size"],
                CODE_RVA + STOCK_SKIP_UNWIND_OFFSET,
            ),
        ]
    )
    data[pdata_append : pdata_append + runtime_size] = runtime_functions
    struct.pack_into("<I", data, exception_directory + 4, exception_size + runtime_size)
    struct.pack_into(
        "<I", data, headers[b".pdata"] + 8, pdata_virtual_size + runtime_size
    )

    struct.pack_into("<H", data, pe + 6, section_count + 2)
    struct.pack_into(
        "<I",
        data,
        optional + 4,
        struct.unpack_from("<I", data, optional + 4)[0] + code_raw_size,
    )
    struct.pack_into(
        "<I",
        data,
        optional + 12,
        struct.unpack_from("<I", data, optional + 12)[0] + DATA_SIZE,
    )
    struct.pack_into(
        "<I",
        data,
        optional + 56,
        align_up(DATA_RVA + DATA_SIZE, section_alignment),
    )
    return code_raw, code_raw_size


def patch(src: pathlib.Path, dst: pathlib.Path) -> dict[str, object]:
    if src.resolve() == dst.resolve():
        raise SystemExit("source and destination must be different files")
    if dst.exists() and src.samefile(dst):
        raise SystemExit("source and destination must not be aliases")

    original = src.read_bytes()
    original_hash = sha256(original)
    if original_hash != SOURCE_SHA256:
        raise SystemExit(
            "source hash mismatch: %s (wanted %s)" % (original_hash, SOURCE_SHA256)
        )
    companion_hashes = verify_companion_hashes(src)
    data = bytearray(original)

    count_off = va_to_text_off(COUNT_HOOK)
    reset_off = va_to_text_off(RESET_HOOK)
    final_off = va_to_text_off(FINAL_CALL)
    stock_skip_off = va_to_text_off(STOCK_SKIP_CALL)
    review_off = va_to_text_off(REVIEW_ROUTE_TEST)
    expected_sites = [
        (count_off, COUNT_HOOK_ORIG, "count hook"),
        (reset_off, RESET_ORIG, "reset hook"),
        (final_off, FINAL_CALL_ORIG, "final call"),
        (stock_skip_off, STOCK_SKIP_CALL_ORIG, "stock skip call"),
        (review_off, REVIEW_ROUTE_ORIG, "review route"),
    ]
    for offset, wanted, name in expected_sites:
        actual = data[offset : offset + len(wanted)]
        if actual != wanted:
            raise SystemExit(
                "%s mismatch at 0x%x: %s (wanted %s)"
                % (name, offset, actual.hex(), wanted.hex())
            )

    code_payload, sizes = build_code()
    code_raw, code_raw_size = add_sections_and_unwind(data, code_payload, sizes)

    count_patch = (
        b"\xE8"
        + rel32(COUNT_HOOK, COUNT_CAVE)
        + b"\x90" * (len(COUNT_HOOK_ORIG) - 5)
    )
    data[count_off : count_off + len(COUNT_HOOK_ORIG)] = count_patch

    reset_patch = b"\xE9" + rel32(RESET_HOOK, RESET_CAVE) + b"\x90"
    data[reset_off : reset_off + len(RESET_ORIG)] = reset_patch

    final_patch = b"\xE8" + rel32(FINAL_CALL, FINAL_CAVE)
    data[final_off : final_off + len(FINAL_CALL_ORIG)] = final_patch

    stock_skip_patch = b"\xE8" + rel32(STOCK_SKIP_CALL, STOCK_SKIP_CAVE)
    data[
        stock_skip_off : stock_skip_off + len(STOCK_SKIP_CALL_ORIG)
    ] = stock_skip_patch

    data[review_off : review_off + len(REVIEW_ROUTE_PATCH)] = REVIEW_ROUTE_PATCH

    output_hash = sha256(bytes(data))
    if output_hash != EXPECTED_OUTPUT_SHA256:
        raise SystemExit(
            "output hash mismatch: %s (wanted %s)"
            % (output_hash, EXPECTED_OUTPUT_SHA256)
        )
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(data)
    return {
        "src": str(src),
        "dst": str(dst),
        "src_sha256": original_hash,
        "dst_sha256": output_hash,
        "companion_hashes": companion_hashes,
        "missing_percent": MISSING_PERCENT,
        "min_inspected": MIN_INSPECTED,
        "count_hook_va": "0x%X" % COUNT_HOOK,
        "count_handler_va": "0x%X" % COUNT_CAVE,
        "reset_handler_va": "0x%X" % RESET_CAVE,
        "final_handler_va": "0x%X" % FINAL_CAVE,
        "stock_skip_handler_va": "0x%X" % STOCK_SKIP_CAVE,
        "review_route_va": "0x%X" % REVIEW_ROUTE_TEST,
        "code_section_rva": "0x%X" % CODE_RVA,
        "code_section_raw": "0x%X" % code_raw,
        "code_section_raw_size": "0x%X" % code_raw_size,
        "data_section_rva": "0x%X" % DATA_RVA,
        "data_section_size": "0x%X" % DATA_SIZE,
        "handler_sizes": sizes,
        "size_src": len(original),
        "size_dst": len(data),
    }


def main() -> int:
    src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else SRC_DEFAULT
    dst = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else OUT_DEFAULT
    info = patch(src, dst)
    for key, value in info.items():
        print("%s=%s" % (key, value))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
