"""Rev7: Rev6 close-path plus multi-section Feature-1 fail-open (Option A).

On multi-section documents (`FUN_140695200(cao) == 2`), the count cave does not
increment cells or trigger SkipSubPanel. Single-section behavior matches Rev6.

See plans/rev6_uniqueness_count_guard_sketch.md Option A and
plans/rev6_uniqueness_component_id_proof.md.
"""
from __future__ import annotations

import pathlib
import sys

import patch_f1_missing_n_rev5 as rev5
import patch_f1_missing_n_rev6 as rev6

IMAGE_BASE = rev5.IMAGE_BASE
SOURCE_SHA256 = rev5.SOURCE_SHA256
CAVE = rev5.CAVE
COUNT_CAVE = rev5.COUNT_CAVE

# Bit 0 of CONTEXT_FLAGS is the UI-posted latch in the finalizer. Bit 1 = multi-section.
CONTEXT_FLAG_MULTI_SECTION_BIT = 1
SECTION_BOUND = 0x140695200  # returns 1 or 2

_ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC_DEFAULT = _ROOT / "v3d_files_" / "Vision3D.exe"
OUT_DEFAULT = _ROOT / "Updated" / "Vision3D_concurrency_fix_rev7.exe"

assemble = rev5.assemble
sha256 = rev5.sha256


def count_handler_source_rev7() -> str:
    """Rev5 count handler with once-per-CAO multi-section classify + fail-open."""
    data_delta = rev5.DATA_VA - COUNT_CAVE
    normal_delta = rev5.COUNT_HOOK_RET - COUNT_CAVE
    early_delta = rev5.EXECUTE_ONE_EARLY_EXIT - COUNT_CAVE
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
    cmp r9d, {rev5.SUBPANEL_SLOTS}
    jae unsupported

    lea r10, [rip + code_base]
    add r10, {data_delta}
table_lock_spin:
    xor eax, eax
    mov edx, 1
    lock cmpxchg dword ptr [r10 + {rev5.GLOBAL_TABLE_LOCK}], edx
    jnz table_lock_spin
    mov ecx, {rev5.CONTEXT_COUNT}
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
    add r10, {rev5.CONTEXT_STRIDE}
    dec ecx
    jnz find_context
    test r11, r11
    jz context_full
    mov r10, r11

claim_context:
    mov qword ptr [r10], r8
    mov dword ptr [r10 + {rev5.CONTEXT_STATUS}], 1
    mov qword ptr [rsp + 0x20], r10
    mov dword ptr [rsp + 0x30], r9d
    mov rcx, r8
    call {SECTION_BOUND}
    mov r10, qword ptr [rsp + 0x20]
    mov r9d, dword ptr [rsp + 0x30]
    mov dword ptr [rsp + 0x30], 0
    mov r8, qword ptr [r10]
    mov qword ptr [rsp + 0x20], 0
    cmp eax, 2
    jne context_found
    lock bts dword ptr [r10 + {rev5.CONTEXT_FLAGS}], {CONTEXT_FLAG_MULTI_SECTION_BIT}

context_found:
    cmp dword ptr [r10 + {rev5.CONTEXT_STATUS}], 1
    jne table_unlock_normal
    bt dword ptr [r10 + {rev5.CONTEXT_FLAGS}], {CONTEXT_FLAG_MULTI_SECTION_BIT}
    jc table_unlock_normal
    lock inc dword ptr [r10 + {rev5.CONTEXT_REFCOUNT}]
    mov qword ptr [rsp + 0x20], r10

    mov eax, r9d
    shl rax, 4
    lea r11, [r10 + rax + {rev5.CONTEXT_CELLS}]

    mov eax, dword ptr [r11 + {rev5.CELL_STATE}]
    test eax, eax
    jnz table_unlock_existing

    mov eax, 1
    lock xadd dword ptr [r11 + {rev5.CELL_INSPECTED}], eax
    inc eax
    test ebx, 1
    jz read_missing

    mov ecx, 1
    lock xadd dword ptr [r11 + {rev5.CELL_MISSING}], ecx
    inc ecx
    jmp have_missing
read_missing:
    mov ecx, dword ptr [r11 + {rev5.CELL_MISSING}]
have_missing:
    cmp eax, {rev5.MIN_INSPECTED}
    jb table_unlock_normal
    imul ecx, ecx, 100
    imul eax, eax, {rev5.MISSING_PERCENT}
    cmp ecx, eax
    jbe table_unlock_normal

    xor eax, eax
    mov ecx, 1
    lock cmpxchg dword ptr [r11 + {rev5.CELL_STATE}], ecx
    jnz table_unlock_existing
    lea rax, [rip + code_base]
    add rax, {data_delta}
    mov dword ptr [rax + {rev5.GLOBAL_TABLE_LOCK}], 0
    jmp trigger_winner

table_unlock_existing:
    lea rdx, [rip + code_base]
    add rdx, {data_delta}
    mov dword ptr [rdx + {rev5.GLOBAL_TABLE_LOCK}], 0

existing_state:
    cmp eax, 2
    jae mark_current_skipped
    cmp eax, 1
    jne normal
state_wait:
    mov eax, dword ptr [r11 + {rev5.CELL_STATE}]
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
    lock cmpxchg dword ptr [r10 + {rev5.CONTEXT_SKIP_LOCK}], edx
    jnz skip_lock_spin
    mov dword ptr [rsp + 0x30], 1
    mov rcx, r8
    mov edx, r9d
    call {rev5.SKIPSUB}
    mov r10, qword ptr [rsp + 0x20]
    mov dword ptr [r10 + {rev5.CONTEXT_SKIP_LOCK}], 0
    mov dword ptr [rsp + 0x30], 0
    mov r11, qword ptr [rsp + 0x28]
    mov eax, 2
    xchg dword ptr [r11 + {rev5.CELL_STATE}], eax

mark_current_skipped:
    mov dword ptr [r13 + 0x28], 0
    mov dword ptr [r13 + 0x2c], 1
    mov r10, qword ptr [rsp + 0x20]
    test r10, r10
    jz mark_return
    mov qword ptr [rsp + 0x20], 0
    lock dec dword ptr [r10 + {rev5.CONTEXT_REFCOUNT}]
mark_return:
    lea rax, [rip + code_base]
    add rax, {early_delta}
    mov qword ptr [rsp + 0x38], rax
    lea rsp, [rsp + 0x38]
    ret

unsupported:
    lea r10, [rip + code_base]
    add r10, {data_delta}
    lock inc dword ptr [r10 + {rev5.GLOBAL_UNSUPPORTED}]
    jmp normal

context_full:
    lock inc dword ptr [r10 + {rev5.GLOBAL_FULL - rev5.CONTEXT_COUNT * rev5.CONTEXT_STRIDE}]

table_unlock_normal:
    lea rax, [rip + code_base]
    add rax, {data_delta}
    mov dword ptr [rax + {rev5.GLOBAL_TABLE_LOCK}], 0

normal:
    mov r10, qword ptr [rsp + 0x20]
    test r10, r10
    jz normal_return
    mov qword ptr [rsp + 0x20], 0
    lock dec dword ptr [r10 + {rev5.CONTEXT_REFCOUNT}]
normal_return:
    lea rax, [rip + code_base]
    add rax, {normal_delta}
    mov qword ptr [rsp + 0x38], rax
    mov rcx, qword ptr [r15 + 0x10]
    cmp byte ptr [rcx + 0x3835], 1
    lea rsp, [rsp + 0x38]
    ret
"""


def build_code() -> tuple[bytes, dict[str, int]]:
    saved = rev5.count_handler_source
    rev5.count_handler_source = count_handler_source_rev7
    try:
        return rev6.build_code()
    finally:
        rev5.count_handler_source = saved


def patch(src: pathlib.Path, dst: pathlib.Path) -> dict[str, object]:
    saved = rev5.count_handler_source
    rev5.count_handler_source = count_handler_source_rev7
    try:
        info = rev6.patch(src, dst)
    finally:
        rev5.count_handler_source = saved
    info = dict(info)
    info["revision"] = "rev7"
    info["multi_section_fail_open"] = True
    info["section_bound_va"] = "0x%X" % SECTION_BOUND
    info["context_flag_multi_section_bit"] = CONTEXT_FLAG_MULTI_SECTION_BIT
    return info


def main() -> int:
    src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else SRC_DEFAULT
    dst = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else OUT_DEFAULT
    info = patch(src, dst)
    for key, value in info.items():
        print("%s=%s" % (key, value))
    return 0


if __name__ == "__main__":
    sys.exit(main())
