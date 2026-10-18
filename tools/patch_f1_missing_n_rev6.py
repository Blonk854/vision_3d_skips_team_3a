"""Rev6: rev5 threshold-skip plus close-path retirement safety.

Adds:
* ProductionStop join before ProductionDoc_dtor body
* Clear document+0x5838 in the production-view destructor
* Patch-owned SKIP snapshot; refresh swaps document+0x23e0 to the snapshot
  object for the duration of the stock refresh body
* Empty snapshot publish after SkipList_Reset returns
* Live capture after SkipSubPanel (stock-skip wrap), SkipList_Add, and SkipAllSubPanels
"""
from __future__ import annotations

import pathlib
import struct
import sys

import patch_f1_missing_n_rev5 as rev5

IMAGE_BASE = rev5.IMAGE_BASE
TEXT_VA = rev5.TEXT_VA
TEXT_RAW = rev5.TEXT_RAW
SOURCE_SHA256 = rev5.SOURCE_SHA256
CAVE = rev5.CAVE
DATA_VA = rev5.DATA_VA

# Expand code so close-path caves sit after rev5 handlers; unwind moves up.
CODE_RVA = rev5.CODE_RVA
CODE_SIZE = 0x4000
DATA_RVA = CODE_RVA + CODE_SIZE
DATA_SIZE = rev5.DATA_SIZE
COUNT_UNWIND_OFFSET = 0x3F00
RESET_UNWIND_OFFSET = 0x3F10
FINAL_UNWIND_OFFSET = 0x3F20
STOCK_SKIP_UNWIND_OFFSET = 0x3F50
DTOR_UNWIND_OFFSET = 0x3F70
VIEW_UNWIND_OFFSET = 0x3F80
REFRESH_UNWIND_OFFSET = 0x3F90

DTOR_JOIN_CAVE = CAVE + 0x2000
VIEW_CLEAR_CAVE = CAVE + 0x2200
REFRESH_SNAP_CAVE = CAVE + 0x2400
CAPTURE_HELPER_CAVE = CAVE + 0x2700
ADD_CAPTURE_CAVE = CAVE + 0x2900
SKIPALL_CAPTURE_CAVE = CAVE + 0x2B00

PRODUCTION_STOP = 0x1406920F0
DTOR_HOOK = 0x14067FC20
DTOR_CONT = 0x14067FC28
DTOR_ORIG = bytes.fromhex("4c8bdc5741564157")

VIEW_DTOR_HOOK = 0x1406ABC60
VIEW_DTOR_CONT = 0x1406ABC68
VIEW_DTOR_ORIG = bytes.fromhex("48894c2408535657")

REFRESH_HOOK = 0x1406ADAF0
REFRESH_CONT = 0x1406ADAF8
REFRESH_ORIG = bytes.fromhex("405556574883ec30")

# SkipList_Add stub: add rcx,0x23e0; mov r8d,edx; mov rdx,[rcx+0x10]; jmp SetAtGrow
SKIPLIST_ADD_HOOK = 0x140541020
SKIPLIST_ADD_ORIG = bytes.fromhex("4881c1e023000044")  # 8 bytes
SETATGROW_THUNK = 0x14077FDD2

# SkipAllSubPanels — document in rcx; uses +0x23e0
SKIPALL_HOOK = 0x140540EF0
SKIPALL_ORIG = bytes.fromhex("48895c2408")  # mov [rsp+8], rbx
SKIPALL_BODY = 0x140540EFF  # after full stock prologue

DOC_SKIP_ARRAY = 0x23E0
DOC_VIEW_PTR = 0x5838
VIEW_DOC_PTR = 0xE8

# Snapshot region in the RW data section (after rev5 globals).
SNAP_BASE = rev5.GLOBAL_FULL + 0x40
SNAP_OBJ = SNAP_BASE + 0x00
SNAP_OBJ_DATA = SNAP_OBJ + 0x08
SNAP_OBJ_SIZE = SNAP_OBJ + 0x10
SNAP_BUF = SNAP_BASE + 0x40
SNAP_BUF_BYTES = 0x4000  # up to 4096 DWORDs
SNAP_SAVE_LIVE = SNAP_BASE + 0x4040
SNAP_FLAGS = SNAP_BASE + 0x4048  # bit0 = published

_ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC_DEFAULT = _ROOT / "v3d_files_" / "Vision3D.exe"
OUT_DEFAULT = _ROOT / "Updated" / "Vision3D_concurrency_fix_rev6.exe"

assemble = rev5.assemble
sha256 = rev5.sha256
align_up = rev5.align_up
va_to_text_off = rev5.va_to_text_off
rel32 = rev5.rel32
verify_companion_hashes = rev5.verify_companion_hashes


def reset_handler_source_rev6() -> str:
    """Rev5 reset cleanup, then run stock body and publish an empty snapshot."""
    data_delta = DATA_VA - rev5.RESET_CAVE
    clear_qwords = (rev5.CONTEXT_STRIDE - 8) // 8
    snap_delta = DATA_VA + SNAP_OBJ - rev5.RESET_CAVE
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
    lock cmpxchg dword ptr [r10 + {rev5.GLOBAL_TABLE_LOCK}], r8d
    jnz table_lock_spin
    mov ecx, {rev5.CONTEXT_COUNT}
find_context:
    cmp qword ptr [r10], r9
    je found_context
    add r10, {rev5.CONTEXT_STRIDE}
    dec ecx
    jnz find_context
    jmp table_unlock_replay

found_context:
    cmp dword ptr [r10 + {rev5.CONTEXT_STATUS}], 1
    je retire_context
    cmp dword ptr [r10 + {rev5.CONTEXT_STATUS}], 2
    jne table_unlock_replay
    jmp retired
retire_context:
    mov dword ptr [r10 + {rev5.CONTEXT_STATUS}], 2
retired:
    lea rax, [rip + code_base]
    add rax, {data_delta}
    mov dword ptr [rax + {rev5.GLOBAL_TABLE_LOCK}], 0
wait_workers:
    cmp dword ptr [r10 + {rev5.CONTEXT_REFCOUNT}], 0
    je clear_context
    pause
    jmp wait_workers
clear_context:
    lea r11, [rip + code_base]
    add r11, {data_delta}
clear_lock_spin:
    xor eax, eax
    mov r8d, 1
    lock cmpxchg dword ptr [r11 + {rev5.GLOBAL_TABLE_LOCK}], r8d
    jnz clear_lock_spin
    cmp qword ptr [r10], r9
    jne clear_unlock_replay
    cmp dword ptr [r10 + {rev5.CONTEXT_STATUS}], 2
    jne clear_unlock_replay
    cmp dword ptr [r10 + {rev5.CONTEXT_REFCOUNT}], 0
    jne clear_unlock_replay
    lea rdi, [r10 + 8]
    xor eax, eax
    mov ecx, {clear_qwords}
    rep stosq
    mov qword ptr [r10], rax
clear_unlock_replay:
    mov dword ptr [r11 + {rev5.GLOBAL_TABLE_LOCK}], 0
    jmp replay

table_unlock_replay:
    lea rax, [rip + code_base]
    add rax, {data_delta}
    mov dword ptr [rax + {rev5.GLOBAL_TABLE_LOCK}], 0

replay:
    mov rcx, r9
    pop rdi
    lea rax, [rip + after_stock]
    push rax
    jmp {rev5.RESET_CONT}
after_stock:
    lea rax, [rip + code_base]
    add rax, {snap_delta}
    mov qword ptr [rax + 0x08], 0
    mov dword ptr [rax + 0x10], 0
    mov dword ptr [rax + {SNAP_FLAGS - SNAP_OBJ}], 1
    add rsp, 0x20
    pop rbx
    ret
"""


def dtor_join_source() -> str:
    return f"""
code_base:
    push rcx
    sub rsp, 0x20
    call {PRODUCTION_STOP}
    add rsp, 0x20
    pop rcx
    mov r11, rsp
    push rdi
    push r14
    push r15
    jmp {DTOR_CONT}
"""


def view_clear_source() -> str:
    return f"""
code_base:
    mov qword ptr [rsp + 8], rcx
    push rbx
    push rsi
    push rdi
    mov rbx, rcx
    mov rax, qword ptr [rbx + {VIEW_DOC_PTR}]
    test rax, rax
    jz cont
    mov qword ptr [rax + {DOC_VIEW_PTR}], 0
cont:
    jmp {VIEW_DTOR_CONT}
"""


def refresh_snap_source() -> str:
    """Run stock refresh with document+0x23e0 temporarily pointing at SNAP_OBJ."""
    snap_obj = DATA_VA + SNAP_OBJ
    save_slot = DATA_VA + SNAP_SAVE_LIVE
    return f"""
code_base:
    push rbp
    push rsi
    push rdi
    sub rsp, 0x30
    mov rbp, rcx
    lea rax, [rip + code_base]
    lea r8, [rax + {snap_obj - REFRESH_SNAP_CAVE}]
    cmp dword ptr [r8 + {SNAP_FLAGS - SNAP_OBJ}], 0
    je no_swap
    mov r9, qword ptr [rbp + {DOC_SKIP_ARRAY}]
    lea r10, [rax + {save_slot - REFRESH_SNAP_CAVE}]
    mov qword ptr [r10], r9
    mov qword ptr [rbp + {DOC_SKIP_ARRAY}], r8
    lea rax, [rip + after_body]
    push rax
    mov rcx, rbp
    jmp {REFRESH_CONT}
after_body:
    lea rax, [rip + code_base]
    lea r10, [rax + {save_slot - REFRESH_SNAP_CAVE}]
    mov r9, qword ptr [r10]
    mov qword ptr [rbp + {DOC_SKIP_ARRAY}], r9
    add rsp, 0x30
    pop rdi
    pop rsi
    pop rbp
    ret
no_swap:
    lea rax, [rip + after_body_noswap]
    push rax
    mov rcx, rbp
    jmp {REFRESH_CONT}
after_body_noswap:
    add rsp, 0x30
    pop rdi
    pop rsi
    pop rbp
    ret
"""


def capture_helper_source() -> str:
    """RCX = document. Copy live CUIntArray at +0x23e0 into SNAP_BUF/SNAP_OBJ."""
    return f"""
code_base:
    push rbx
    push rsi
    push rdi
    sub rsp, 0x20
    mov rbx, rcx
    mov rsi, qword ptr [rbx + {DOC_SKIP_ARRAY}]
    test rsi, rsi
    jz publish_empty
    mov edx, dword ptr [rsi + 0x10]
    test edx, edx
    js publish_empty
    cmp edx, {SNAP_BUF_BYTES // 4}
    ja publish_empty
    mov rsi, qword ptr [rsi + 0x08]
    test rsi, rsi
    jz publish_empty
    lea rdi, [rip + code_base]
    add rdi, {DATA_VA + SNAP_BUF - CAPTURE_HELPER_CAVE}
    mov ecx, edx
    mov eax, ecx
    shl ecx, 2
    mov r8, rdi
    rep movsb
    lea rdi, [rip + code_base]
    add rdi, {DATA_VA + SNAP_OBJ - CAPTURE_HELPER_CAVE}
    mov qword ptr [rdi + 0x08], r8
    mov dword ptr [rdi + 0x10], eax
    mov dword ptr [rdi + {SNAP_FLAGS - SNAP_OBJ}], 1
    jmp done
publish_empty:
    lea rdi, [rip + code_base]
    add rdi, {DATA_VA + SNAP_OBJ - CAPTURE_HELPER_CAVE}
    mov qword ptr [rdi + 0x08], 0
    mov dword ptr [rdi + 0x10], 0
    mov dword ptr [rdi + {SNAP_FLAGS - SNAP_OBJ}], 1
done:
    add rsp, 0x20
    pop rdi
    pop rsi
    pop rbx
    ret
"""


def stock_skip_wrapper_source_rev6() -> str:
    """Rev5 SkipSubPanel wrap; capture live +0x23e0 from the same object (rbx)."""
    data_delta = DATA_VA - rev5.STOCK_SKIP_CAVE
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
    lock cmpxchg dword ptr [r10 + {rev5.GLOBAL_TABLE_LOCK}], edx
    jnz table_lock_spin
    mov ecx, {rev5.CONTEXT_COUNT}
find_context:
    cmp qword ptr [r10], rbx
    je context_match
    add r10, {rev5.CONTEXT_STRIDE}
    dec ecx
    jnz find_context
    jmp table_locked_call
context_match:
    cmp dword ptr [r10 + {rev5.CONTEXT_STATUS}], 1
    jne table_unlock_done
    lock inc dword ptr [r10 + {rev5.CONTEXT_REFCOUNT}]
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
    mov dword ptr [rax + {rev5.GLOBAL_TABLE_LOCK}], 0

    mov r10, qword ptr [rsp + 0x20]
    test r10, r10
    jz call_stock
skip_lock_spin:
    xor eax, eax
    mov edx, 1
    lock cmpxchg dword ptr [r10 + {rev5.CONTEXT_SKIP_LOCK}], edx
    jnz skip_lock_spin
    mov dword ptr [rsp + 0x28], 1
call_stock:
    mov rcx, rbx
    mov edx, esi
    call {rev5.SKIPSUB}
    jmp stock_return

table_unlock_done:
    lea rax, [rip + code_base]
    add rax, {data_delta}
    mov dword ptr [rax + {rev5.GLOBAL_TABLE_LOCK}], 0
    jmp done

stock_return:
    cmp dword ptr [rsp + 0x2c], 0
    je no_table_lock
    mov rax, qword ptr [rsp + 0x30]
    mov dword ptr [rax + {rev5.GLOBAL_TABLE_LOCK}], 0
    mov dword ptr [rsp + 0x2c], 0
no_table_lock:
    mov r10, qword ptr [rsp + 0x20]
    test r10, r10
    jz capture
    mov dword ptr [r10 + {rev5.CONTEXT_SKIP_LOCK}], 0
    mov dword ptr [rsp + 0x28], 0
    mov qword ptr [rsp + 0x20], 0
    lock dec dword ptr [r10 + {rev5.CONTEXT_REFCOUNT}]
capture:
    mov rcx, rbx
    call {CAPTURE_HELPER_CAVE}
done:
    add rsp, 0x38
    pop rsi
    pop rbx
    ret
"""


def skiplist_add_capture_source() -> str:
    """Run stock SetAtGrow path for SkipList_Add, then capture."""
    return f"""
code_base:
    push rbx
    push rsi
    sub rsp, 0x28
    mov rbx, rcx
    mov esi, edx
    mov rcx, rbx
    add rcx, {DOC_SKIP_ARRAY}
    mov r8d, esi
    mov rdx, qword ptr [rcx + 0x10]
    call {SETATGROW_THUNK}
    mov rcx, rbx
    call {CAPTURE_HELPER_CAVE}
    add rsp, 0x28
    pop rsi
    pop rbx
    ret
"""


def skipall_capture_source() -> str:
    """Run stock SkipAllSubPanels body, then capture."""
    return f"""
code_base:
    push rbx
    push rsi
    sub rsp, 0x28
    mov rbx, rcx
    mov rcx, rbx
    call skipall_stock
    mov rcx, rbx
    call {CAPTURE_HELPER_CAVE}
    add rsp, 0x28
    pop rsi
    pop rbx
    ret
skipall_stock:
    mov qword ptr [rsp + 8], rbx
    mov qword ptr [rsp + 0x10], rsi
    push rdi
    sub rsp, 0x20
    jmp {SKIPALL_BODY}
"""


_REV5_BUILD_CODE = rev5.build_code


def build_code() -> tuple[bytes, dict[str, int]]:
    # Temporarily widen rev5 layout constants used inside imported builders.
    saved = {
        "CODE_SIZE": rev5.CODE_SIZE,
        "DATA_RVA": rev5.DATA_RVA,
        "DATA_VA": rev5.DATA_VA,
        "COUNT_UNWIND_OFFSET": rev5.COUNT_UNWIND_OFFSET,
        "RESET_UNWIND_OFFSET": rev5.RESET_UNWIND_OFFSET,
        "FINAL_UNWIND_OFFSET": rev5.FINAL_UNWIND_OFFSET,
        "STOCK_SKIP_UNWIND_OFFSET": rev5.STOCK_SKIP_UNWIND_OFFSET,
        "reset_handler_source": rev5.reset_handler_source,
        "stock_skip_wrapper_source": rev5.stock_skip_wrapper_source,
    }
    rev5.CODE_SIZE = CODE_SIZE
    rev5.DATA_RVA = DATA_RVA
    rev5.DATA_VA = IMAGE_BASE + DATA_RVA
    rev5.COUNT_UNWIND_OFFSET = COUNT_UNWIND_OFFSET
    rev5.RESET_UNWIND_OFFSET = RESET_UNWIND_OFFSET
    rev5.FINAL_UNWIND_OFFSET = FINAL_UNWIND_OFFSET
    rev5.STOCK_SKIP_UNWIND_OFFSET = STOCK_SKIP_UNWIND_OFFSET
    rev5.reset_handler_source = reset_handler_source_rev6
    rev5.stock_skip_wrapper_source = stock_skip_wrapper_source_rev6

    try:
        global DATA_VA
        DATA_VA = IMAGE_BASE + DATA_RVA
        payload, sizes = _REV5_BUILD_CODE()
        payload = bytearray(payload)
        if len(payload) < CODE_SIZE:
            payload.extend(b"\xCC" * (CODE_SIZE - len(payload)))

        dtor = assemble(dtor_join_source(), DTOR_JOIN_CAVE)
        view = assemble(view_clear_source(), VIEW_CLEAR_CAVE)
        refresh = assemble(refresh_snap_source(), REFRESH_SNAP_CAVE)
        capture = assemble(capture_helper_source(), CAPTURE_HELPER_CAVE)
        add_cap = assemble(skiplist_add_capture_source(), ADD_CAPTURE_CAVE)
        skipall_cap = assemble(skipall_capture_source(), SKIPALL_CAPTURE_CAVE)

        for name, blob, start, limit in (
            ("dtor", dtor, DTOR_JOIN_CAVE, VIEW_CLEAR_CAVE),
            ("view", view, VIEW_CLEAR_CAVE, REFRESH_SNAP_CAVE),
            ("refresh", refresh, REFRESH_SNAP_CAVE, CAPTURE_HELPER_CAVE),
            ("capture", capture, CAPTURE_HELPER_CAVE, ADD_CAPTURE_CAVE),
            ("add_capture", add_cap, ADD_CAPTURE_CAVE, SKIPALL_CAPTURE_CAVE),
            (
                "skipall_capture",
                skipall_cap,
                SKIPALL_CAPTURE_CAVE,
                CAVE + COUNT_UNWIND_OFFSET,
            ),
        ):
            if len(blob) > limit - start:
                raise RuntimeError("%s handler overlaps next cave (%d > %d)" % (
                    name, len(blob), limit - start
                ))
            off = start - CAVE
            payload[off : off + len(blob)] = blob
            sizes["%s_size" % name] = len(blob)

        return bytes(payload), sizes
    finally:
        rev5.CODE_SIZE = saved["CODE_SIZE"]
        rev5.DATA_RVA = saved["DATA_RVA"]
        rev5.DATA_VA = saved["DATA_VA"]
        rev5.COUNT_UNWIND_OFFSET = saved["COUNT_UNWIND_OFFSET"]
        rev5.RESET_UNWIND_OFFSET = saved["RESET_UNWIND_OFFSET"]
        rev5.FINAL_UNWIND_OFFSET = saved["FINAL_UNWIND_OFFSET"]
        rev5.STOCK_SKIP_UNWIND_OFFSET = saved["STOCK_SKIP_UNWIND_OFFSET"]
        rev5.reset_handler_source = saved["reset_handler_source"]
        rev5.stock_skip_wrapper_source = saved["stock_skip_wrapper_source"]


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

    # Point rev5 section helpers at expanded layout for this build.
    saved = {
        "CODE_SIZE": rev5.CODE_SIZE,
        "DATA_RVA": rev5.DATA_RVA,
        "DATA_SIZE": rev5.DATA_SIZE,
        "DATA_VA": rev5.DATA_VA,
        "COUNT_UNWIND_OFFSET": rev5.COUNT_UNWIND_OFFSET,
        "RESET_UNWIND_OFFSET": rev5.RESET_UNWIND_OFFSET,
        "FINAL_UNWIND_OFFSET": rev5.FINAL_UNWIND_OFFSET,
        "STOCK_SKIP_UNWIND_OFFSET": rev5.STOCK_SKIP_UNWIND_OFFSET,
        "reset_handler_source": rev5.reset_handler_source,
        "stock_skip_wrapper_source": rev5.stock_skip_wrapper_source,
    }
    rev5.CODE_SIZE = CODE_SIZE
    rev5.DATA_RVA = DATA_RVA
    rev5.DATA_SIZE = DATA_SIZE
    rev5.DATA_VA = IMAGE_BASE + DATA_RVA
    rev5.COUNT_UNWIND_OFFSET = COUNT_UNWIND_OFFSET
    rev5.RESET_UNWIND_OFFSET = RESET_UNWIND_OFFSET
    rev5.FINAL_UNWIND_OFFSET = FINAL_UNWIND_OFFSET
    rev5.STOCK_SKIP_UNWIND_OFFSET = STOCK_SKIP_UNWIND_OFFSET
    rev5.reset_handler_source = reset_handler_source_rev6
    rev5.stock_skip_wrapper_source = stock_skip_wrapper_source_rev6

    try:
        count_off = va_to_text_off(rev5.COUNT_HOOK)
        reset_off = va_to_text_off(rev5.RESET_HOOK)
        final_off = va_to_text_off(rev5.FINAL_CALL)
        stock_skip_off = va_to_text_off(rev5.STOCK_SKIP_CALL)
        review_off = va_to_text_off(rev5.REVIEW_ROUTE_TEST)
        dtor_off = va_to_text_off(DTOR_HOOK)
        view_off = va_to_text_off(VIEW_DTOR_HOOK)
        refresh_off = va_to_text_off(REFRESH_HOOK)
        add_off = va_to_text_off(SKIPLIST_ADD_HOOK)
        skipall_off = va_to_text_off(SKIPALL_HOOK)

        expected_sites = [
            (count_off, rev5.COUNT_HOOK_ORIG, "count hook"),
            (reset_off, rev5.RESET_ORIG, "reset hook"),
            (final_off, rev5.FINAL_CALL_ORIG, "final call"),
            (stock_skip_off, rev5.STOCK_SKIP_CALL_ORIG, "stock skip call"),
            (review_off, rev5.REVIEW_ROUTE_ORIG, "review route"),
            (dtor_off, DTOR_ORIG, "dtor join"),
            (view_off, VIEW_DTOR_ORIG, "view clear"),
            (refresh_off, REFRESH_ORIG, "refresh snap"),
            (add_off, SKIPLIST_ADD_ORIG, "skiplist add"),
            (skipall_off, SKIPALL_ORIG, "skipall"),
        ]
        for offset, wanted, name in expected_sites:
            actual = bytes(data[offset : offset + len(wanted)])
            if actual != wanted:
                raise SystemExit(
                    "%s mismatch at 0x%x: %s (wanted %s)"
                    % (name, offset, actual.hex(), wanted.hex())
                )

        code_payload, sizes = build_code()
        code_raw, code_raw_size = rev5.add_sections_and_unwind(
            data, code_payload, sizes
        )

        count_patch = (
            b"\xE8"
            + rel32(rev5.COUNT_HOOK, rev5.COUNT_CAVE)
            + b"\x90" * (len(rev5.COUNT_HOOK_ORIG) - 5)
        )
        data[count_off : count_off + len(rev5.COUNT_HOOK_ORIG)] = count_patch

        reset_patch = b"\xE9" + rel32(rev5.RESET_HOOK, rev5.RESET_CAVE) + b"\x90"
        data[reset_off : reset_off + len(rev5.RESET_ORIG)] = reset_patch

        final_patch = b"\xE8" + rel32(rev5.FINAL_CALL, rev5.FINAL_CAVE)
        data[final_off : final_off + len(rev5.FINAL_CALL_ORIG)] = final_patch

        stock_skip_patch = b"\xE8" + rel32(rev5.STOCK_SKIP_CALL, rev5.STOCK_SKIP_CAVE)
        data[
            stock_skip_off : stock_skip_off + len(rev5.STOCK_SKIP_CALL_ORIG)
        ] = stock_skip_patch

        data[review_off : review_off + len(rev5.REVIEW_ROUTE_PATCH)] = (
            rev5.REVIEW_ROUTE_PATCH
        )

        dtor_patch = (
            b"\xE9"
            + rel32(DTOR_HOOK, DTOR_JOIN_CAVE)
            + b"\x90" * (len(DTOR_ORIG) - 5)
        )
        data[dtor_off : dtor_off + len(DTOR_ORIG)] = dtor_patch

        view_patch = (
            b"\xE9"
            + rel32(VIEW_DTOR_HOOK, VIEW_CLEAR_CAVE)
            + b"\x90" * (len(VIEW_DTOR_ORIG) - 5)
        )
        data[view_off : view_off + len(VIEW_DTOR_ORIG)] = view_patch

        refresh_patch = (
            b"\xE9"
            + rel32(REFRESH_HOOK, REFRESH_SNAP_CAVE)
            + b"\x90" * (len(REFRESH_ORIG) - 5)
        )
        data[refresh_off : refresh_off + len(REFRESH_ORIG)] = refresh_patch

        add_patch = (
            b"\xE9"
            + rel32(SKIPLIST_ADD_HOOK, ADD_CAPTURE_CAVE)
            + b"\x90" * (len(SKIPLIST_ADD_ORIG) - 5)
        )
        data[add_off : add_off + len(SKIPLIST_ADD_ORIG)] = add_patch

        skipall_patch = b"\xE9" + rel32(SKIPALL_HOOK, SKIPALL_CAPTURE_CAVE)
        data[skipall_off : skipall_off + len(SKIPALL_ORIG)] = skipall_patch

        output_hash = sha256(bytes(data))
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
        return {
            "revision": "rev6",
            "src": str(src),
            "dst": str(dst),
            "src_sha256": original_hash,
            "dst_sha256": output_hash,
            "companion_hashes": companion_hashes,
            "count_hook_va": "0x%X" % rev5.COUNT_HOOK,
            "dtor_join_va": "0x%X" % DTOR_HOOK,
            "dtor_handler_va": "0x%X" % DTOR_JOIN_CAVE,
            "view_clear_va": "0x%X" % VIEW_DTOR_HOOK,
            "view_handler_va": "0x%X" % VIEW_CLEAR_CAVE,
            "refresh_snap_va": "0x%X" % REFRESH_HOOK,
            "refresh_handler_va": "0x%X" % REFRESH_SNAP_CAVE,
            "capture_helper_va": "0x%X" % CAPTURE_HELPER_CAVE,
            "skiplist_add_va": "0x%X" % SKIPLIST_ADD_HOOK,
            "skiplist_add_handler_va": "0x%X" % ADD_CAPTURE_CAVE,
            "skipall_va": "0x%X" % SKIPALL_HOOK,
            "skipall_handler_va": "0x%X" % SKIPALL_CAPTURE_CAVE,
            "production_stop_va": "0x%X" % PRODUCTION_STOP,
            "code_section_rva": "0x%X" % CODE_RVA,
            "code_section_raw": "0x%X" % code_raw,
            "code_section_raw_size": "0x%X" % code_raw_size,
            "data_section_rva": "0x%X" % DATA_RVA,
            "handler_sizes": sizes,
            "size_src": len(original),
            "size_dst": len(data),
        }
    finally:
        for key, value in saved.items():
            setattr(rev5, key, value)


def main() -> int:
    src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else SRC_DEFAULT
    dst = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else OUT_DEFAULT
    info = patch(src, dst)
    for key, value in info.items():
        print("%s=%s" % (key, value))
    return 0


if __name__ == "__main__":
    sys.exit(main())
