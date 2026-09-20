"""Patch Vision3D.exe Feature 1: 2D-style skip above a Missing percentage.

Writes a NEW file. Never overwrites the source PE.
Hard-coded threshold: more than 30% Missing after at least 10 inspections.

When the threshold fires, the handler:
* enters the sub-panel in Vision3D's normal runtime skip list;
* resets prior anomaly results for that sub-panel with CAnomalie::RazRes;
* marks those anomalies as skipped-by-operator;
* posts Vision3D's normal production-screen skip notification; and
* exits the triggering ExecuteOne_Component before it stores a defect.

All skipped sub-panels also participate in Vision3D's final review-routing
decision, while retaining their normal skipped-card/database status.
"""
from __future__ import annotations

import hashlib
import pathlib
import struct
import sys

IMAGE_BASE = 0x140000000
TEXT_VA = 0x1000
TEXT_RAW = 0x400
SOURCE_SHA256 = "ccca11b2f05084b484fa5556c67f8874065dbc0b6265177d2517f81265af00f4"

HOOK = 0x140736F09  # LEA RDX,[RBP-0x18]; LEA RCX,[RBP-0x78]
HOOK_RET = 0x140736F11  # original CALL after the two LEAs
HOOK_ORIG = bytes.fromhex("488d55e8488d4d88")  # 8 bytes stolen
EXECUTE_ONE_EARLY_EXIT = 0x14073742D

RESET = 0x140541050  # SkipList_Reset
RESET_CONT = 0x140541056  # MOV RBX,RCX
RESET_ORIG = bytes.fromhex("40534883ec20")  # 6 bytes stolen

REVIEW_ROUTE_TEST = 0x1406748C5
REVIEW_ROUTE_ORIG = bytes.fromhex("f70498fffeffff")  # test card anomaly,~0x100
REVIEW_ROUTE_PATCH = bytes.fromhex("f70498ffffffff")  # include skip bit 0x100

# The source PE has room for two additional section headers. Dedicated sections
# avoid relying on the 243-byte .text tail and on bytes beyond .data VirtualSize.
CODE_RVA = 0x1C98000
DATA_RVA = 0x1C99000
CAVE = IMAGE_BASE + CODE_RVA
RESET_CAVE = CAVE + 0x300
MISSING_COUNTS = IMAGE_BASE + DATA_RVA
INSPECTED_COUNTS = MISSING_COUNTS + 0x400
SKIPSUB = 0x140541080
POSTMESSAGE_IAT = 0x140D5BC00
SKIP_UI_MESSAGE = 0x1411DCB30
MISSING_PERCENT = 30
MIN_INSPECTED = 10
N_SLOTS = 256
N_COUNTER_DWORDS = N_SLOTS * 2
CODE_SECTION_SIZE = 0x400
DATA_SECTION_SIZE = 0x800
HANDLER_UNWIND_OFFSET = 0x380
RESET_UNWIND_OFFSET = 0x398

_ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC_DEFAULT = _ROOT / "v3d_files_" / "Vision3D.exe"
OUT_DEFAULT = _ROOT / "Updated" / "Vision3D.exe"


def va_to_off(va: int) -> int:
    rva = va - IMAGE_BASE
    return TEXT_RAW + (rva - TEXT_VA)


def rel32(src: int, dest: int) -> bytes:
    return struct.pack("<i", dest - (src + 5))


def rel8(src_next: int, dest: int) -> bytes:
    d = dest - src_next
    if not -128 <= d <= 127:
        raise ValueError("rel8 out of range %d" % d)
    return struct.pack("b", d)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def align_up(value: int, alignment: int) -> int:
    return (value + alignment - 1) & -alignment


def assemble_caves() -> tuple[bytes, dict]:
    code = bytearray()
    meta: dict[str, object] = {}
    labels: dict[str, int] = {}
    fixups: list[tuple[int, int, str]] = []

    def va() -> int:
        return CAVE + len(code)

    def emit(b: bytes) -> None:
        code.extend(b)

    def mark(name: str) -> None:
        labels[name] = len(code)

    def jcc32(opcode: bytes, target: str) -> None:
        emit(opcode)
        pos = len(code)
        emit(b"\x00\x00\x00\x00")
        fixups.append((pos, 4, target))

    def jcc8(opcode: int, target: str) -> None:
        emit(bytes([opcode]))
        pos = len(code)
        emit(b"\x00")
        fixups.append((pos, 1, target))

    emit(bytes.fromhex("8b4714"))  # mov eax,[rdi+0x14]
    emit(bytes.fromhex("3d00010000"))  # cmp eax,256
    jcc32(bytes.fromhex("0f83"), "normal")  # jae normal
    emit(bytes.fromhex("4c8d05"))
    lea_at = len(code)
    emit(b"\x00\x00\x00\x00")
    struct.pack_into("<i", code, lea_at, MISSING_COUNTS - va())
    emit(bytes.fromhex("41ff848000040000"))  # inc inspected[eax]
    emit(bytes.fromhex("f7c301000000"))  # test ebx,1
    jcc32(bytes.fromhex("0f84"), "normal")  # jz normal
    emit(bytes.fromhex("41ff0480"))  # inc missing[eax]
    emit(bytes.fromhex("4183bc8000040000"))  # cmp inspected[eax],imm8
    meta["min_inspected_off_in_cave"] = len(code)
    emit(bytes([MIN_INSPECTED]))
    jcc32(bytes.fromhex("0f82"), "normal")  # jb normal
    emit(bytes.fromhex("458b1480"))  # mov r10d,missing[eax]
    emit(bytes.fromhex("456bd264"))  # imul r10d,r10d,100
    emit(bytes.fromhex("458b9c8000040000"))  # mov r11d,inspected[eax]
    emit(bytes.fromhex("456bdb"))  # imul r11d,r11d,percent
    meta["percent_off_in_cave"] = len(code)
    emit(bytes([MISSING_PERCENT]))
    emit(bytes.fromhex("453bd3"))  # cmp r10d,r11d
    jcc32(bytes.fromhex("0f86"), "normal")  # jbe normal

    # Preserve all nonvolatile registers used by the cleanup loop and reserve
    # Win64 shadow space. Six pushes preserve 16-byte call-site alignment.
    mark("handler_frame")
    emit(bytes.fromhex("535657415441554156"))  # push rbx,rsi,rdi,r12,r13,r14
    emit(bytes.fromhex("4883ec20"))  # sub rsp,20
    emit(bytes.fromhex("4189c4"))  # mov r12d,eax (sub-panel id)
    emit(bytes.fromhex("4d8b6f10"))  # mov r13,[r15+0x10] (CAO)
    emit(bytes.fromhex("4c89e9"))  # mov rcx,r13
    emit(bytes.fromhex("4489e2"))  # mov edx,r12d
    emit(b"\xe8")
    emit(rel32(va() - 1, SKIPSUB))

    # Match the stock skip-mark path's production-screen refresh.
    emit(bytes.fromhex("498b8d38580000"))  # mov rcx,[r13+0x5838]
    emit(bytes.fromhex("4533c9"))  # xor r9d,r9d
    emit(bytes.fromhex("4533c0"))  # xor r8d,r8d
    emit(bytes.fromhex("8b15"))  # mov edx,[rip+skip-ui-message]
    message_at = len(code)
    emit(b"\x00\x00\x00\x00")
    struct.pack_into("<i", code, message_at, SKIP_UI_MESSAGE - va())
    emit(bytes.fromhex("488b4940"))  # mov rcx,[rcx+0x40]
    emit(bytes.fromhex("ff15"))  # call qword [rip+PostMessageA]
    post_at = len(code)
    emit(b"\x00\x00\x00\x00")
    struct.pack_into("<i", code, post_at, POSTMESSAGE_IAT - va())

    # Walk every production zone. Matching anomalies that were already
    # inspected are reset and then marked with not-inspected cause 1, exactly
    # like ExecuteAll_Components' existing operator-skip branch.
    emit(bytes.fromhex("498bb548240000"))  # mov rsi,[r13+0x2448]
    emit(bytes.fromhex("4d8bb578580000"))  # mov r14,[r13+0x5878]
    mark("zone_loop")
    emit(bytes.fromhex("493bb550240000"))  # cmp rsi,[r13+0x2450]
    jcc8(0x73, "cleanup_done")  # jae cleanup_done
    emit(bytes.fromhex("498b5e18"))  # mov rbx,[r14+0x18]
    emit(bytes.fromhex("498b7e20"))  # mov rdi,[r14+0x20]
    mark("anomaly_loop")
    emit(bytes.fromhex("4839fb"))  # cmp rbx,rdi
    jcc8(0x73, "next_zone")  # jae next_zone
    emit(bytes.fromhex("44396308"))  # cmp [rbx+8],r12d
    jcc8(0x75, "next_anomaly")  # jne next_anomaly
    emit(bytes.fromhex("837b2c00"))  # cmp dword [rbx+0x2c],0
    jcc8(0x75, "next_anomaly")  # jne next_anomaly
    emit(bytes.fromhex("4889d9"))  # mov rcx,rbx
    emit(bytes.fromhex("488b03"))  # mov rax,[rbx]
    emit(bytes.fromhex("ff5048"))  # call qword [rax+0x48] (RazRes)
    emit(bytes.fromhex("c7432c01000000"))  # mov dword [rbx+0x2c],1
    mark("next_anomaly")
    emit(bytes.fromhex("4881c370030000"))  # add rbx,0x370
    jcc8(0xEB, "anomaly_loop")
    mark("next_zone")
    emit(bytes.fromhex("4883c628"))  # add rsi,0x28
    emit(bytes.fromhex("4981c610040000"))  # add r14,0x410
    jcc8(0xEB, "zone_loop")
    mark("cleanup_done")
    emit(bytes.fromhex("4883c420"))  # add rsp,20
    emit(bytes.fromhex("415e415d415c5f5e5b"))  # pop r14,r13,r12,rdi,rsi,rbx
    mark("handler_frame_end")
    emit(b"\xe9")
    emit(rel32(va() - 1, EXECUTE_ONE_EARLY_EXIT))

    mark("normal")
    meta["handler_frame_start"] = labels["handler_frame"]
    meta["handler_frame_end"] = labels["handler_frame_end"]
    emit(HOOK_ORIG)
    emit(b"\xe9")
    emit(rel32(va() - 1, HOOK_RET))
    meta["hook_size"] = len(code)

    for pos, size, target in fixups:
        target_va = CAVE + labels[target]
        next_va = CAVE + pos + size
        delta = target_va - next_va
        if size == 1:
            code[pos] = rel8(next_va, target_va)[0]
        else:
            struct.pack_into("<i", code, pos, delta)

    if len(code) > RESET_CAVE - CAVE:
        raise RuntimeError("handler overlaps reset cave: %d bytes" % len(code))
    code.extend(b"\xcc" * (RESET_CAVE - CAVE - len(code)))

    meta["reset_va"] = va()
    emit(bytes.fromhex("40534883ec20"))  # push rbx; sub rsp,20
    emit(bytes.fromhex("488bd9"))  # mov rbx, rcx (this)
    emit(bytes.fromhex("57"))  # push rdi
    emit(bytes.fromhex("488d3d"))
    rlea = len(code)
    emit(b"\x00\x00\x00\x00")
    struct.pack_into("<i", code, rlea, MISSING_COUNTS - va())
    emit(bytes.fromhex("33c0"))  # xor eax,eax
    emit(bytes.fromhex("b9"))  # mov ecx,qword count
    emit(struct.pack("<I", N_COUNTER_DWORDS // 2))
    emit(bytes.fromhex("f348ab"))  # rep stosq
    emit(bytes.fromhex("5f"))  # pop rdi
    emit(bytes.fromhex("488bcb"))  # mov rcx, rbx
    emit(b"\xe9")
    emit(rel32(va() - 1, RESET_CONT))
    meta["reset_frame_end"] = len(code)
    meta["cave_size"] = len(code)
    if len(code) > CODE_SECTION_SIZE:
        raise RuntimeError("code section overflow: %d bytes" % len(code))
    return bytes(code), meta


def add_feature_sections(
    data: bytearray, code: bytes, meta: dict[str, object]
) -> tuple[int, int]:
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe : pe + 4] != b"PE\x00\x00":
        raise SystemExit("not a PE image")
    number_sections = struct.unpack_from("<H", data, pe + 6)[0]
    optional_size = struct.unpack_from("<H", data, pe + 20)[0]
    optional = pe + 24
    if struct.unpack_from("<H", data, optional)[0] != 0x20B:
        raise SystemExit("expected PE32+ image")
    section_alignment = struct.unpack_from("<I", data, optional + 32)[0]
    file_alignment = struct.unpack_from("<I", data, optional + 36)[0]
    size_of_image = struct.unpack_from("<I", data, optional + 56)[0]
    size_of_headers = struct.unpack_from("<I", data, optional + 60)[0]
    exception_directory = optional + 112 + 3 * 8
    exception_rva, exception_size = struct.unpack_from(
        "<II", data, exception_directory
    )
    section_table = optional + optional_size
    new_headers_end = section_table + (number_sections + 2) * 40
    if new_headers_end > size_of_headers:
        raise SystemExit("no room for two section headers")
    if any(data[section_table + number_sections * 40 : new_headers_end]):
        raise SystemExit("new section header slots are not empty")
    if size_of_image != CODE_RVA:
        raise SystemExit(
            "unexpected SizeOfImage 0x%x (wanted 0x%x)" % (size_of_image, CODE_RVA)
        )

    sections: dict[bytes, tuple[int, ...]] = {}
    section_headers: dict[bytes, int] = {}
    for index in range(number_sections):
        address = section_table + index * 40
        values = struct.unpack_from("<8sIIIIIIHHI", data, address)
        name = values[0].rstrip(b"\x00")
        sections[name] = values[1:]
        section_headers[name] = address
    if b".pdata" not in sections:
        raise SystemExit("missing .pdata section")
    pdata = sections[b".pdata"]
    pdata_virtual_size, pdata_rva, pdata_raw_size, pdata_raw = pdata[:4]
    if exception_rva != pdata_rva or exception_size != pdata_virtual_size:
        raise SystemExit("unexpected exception directory layout")
    if exception_size % 12:
        raise SystemExit("exception directory is not a RUNTIME_FUNCTION array")
    pdata_append = pdata_raw + exception_size
    if pdata_append + 24 > pdata_raw + pdata_raw_size:
        raise SystemExit("no .pdata raw padding for injected unwind records")
    if any(data[pdata_append : pdata_append + 24]):
        raise SystemExit(".pdata append area is not empty")
    last_begin = struct.unpack_from("<I", data, pdata_append - 12)[0]
    if last_begin >= CODE_RVA:
        raise SystemExit("new runtime functions would not be sorted")

    code_raw = align_up(len(data), file_alignment)
    code_raw_size = align_up(CODE_SECTION_SIZE, file_alignment)
    if len(code) > CODE_SECTION_SIZE:
        raise SystemExit("feature code exceeds section")
    if code_raw > len(data):
        data.extend(b"\x00" * (code_raw - len(data)))
    code_payload = bytearray(code + b"\xcc" * (CODE_SECTION_SIZE - len(code)))

    # UNWIND_INFO for the trigger-only frame. Unwind codes are ordered by
    # descending prologue offset and padded to an even slot count.
    handler_unwind = bytes.fromhex(
        "010d0700"  # version 1, prologue 13, seven unwind codes
        "0d32"  # sub rsp,0x20
        "09e0"  # push r14
        "07d0"  # push r13
        "05c0"  # push r12
        "0370"  # push rdi
        "0260"  # push rsi
        "0130"  # push rbx
        "0000"  # alignment padding
    )
    reset_unwind = bytes.fromhex(
        "010a0300"  # version 1, prologue 10, three unwind codes
        "0a70"  # push rdi
        "0632"  # sub rsp,0x20
        "0230"  # push rbx
        "0000"  # alignment padding
    )
    code_payload[
        HANDLER_UNWIND_OFFSET : HANDLER_UNWIND_OFFSET + len(handler_unwind)
    ] = handler_unwind
    code_payload[RESET_UNWIND_OFFSET : RESET_UNWIND_OFFSET + len(reset_unwind)] = (
        reset_unwind
    )
    data.extend(code_payload)
    data.extend(b"\x00" * (code_raw_size - len(code_payload)))

    code_header = struct.pack(
        "<8sIIIIIIHHI",
        b".f1code\x00",
        CODE_SECTION_SIZE,
        CODE_RVA,
        code_raw_size,
        code_raw,
        0,
        0,
        0,
        0,
        0x60000020,  # code | execute | read
    )
    data_header = struct.pack(
        "<8sIIIIIIHHI",
        b".f1data\x00",
        DATA_SECTION_SIZE,
        DATA_RVA,
        0,
        0,
        0,
        0,
        0,
        0,
        0xC0000080,  # uninitialized data | read | write
    )
    header = section_table + number_sections * 40
    data[header : header + 40] = code_header
    data[header + 40 : header + 80] = data_header

    runtime_functions = (
        struct.pack(
            "<III",
            CODE_RVA + int(meta["handler_frame_start"]),
            CODE_RVA + int(meta["handler_frame_end"]),
            CODE_RVA + HANDLER_UNWIND_OFFSET,
        )
        + struct.pack(
            "<III",
            RESET_CAVE - IMAGE_BASE,
            CODE_RVA + int(meta["reset_frame_end"]),
            CODE_RVA + RESET_UNWIND_OFFSET,
        )
    )
    data[pdata_append : pdata_append + len(runtime_functions)] = runtime_functions
    struct.pack_into("<I", data, exception_directory + 4, exception_size + 24)
    struct.pack_into(
        "<I",
        data,
        section_headers[b".pdata"] + 8,
        pdata_virtual_size + 24,
    )
    struct.pack_into("<H", data, pe + 6, number_sections + 2)
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
        struct.unpack_from("<I", data, optional + 12)[0] + DATA_SECTION_SIZE,
    )
    struct.pack_into(
        "<I",
        data,
        optional + 56,
        align_up(DATA_RVA + DATA_SECTION_SIZE, section_alignment),
    )
    return code_raw, code_raw_size


def patch(src: pathlib.Path, dst: pathlib.Path) -> dict:
    if src.resolve() == dst.resolve():
        raise SystemExit("source and destination must be different files")
    if dst.exists() and src.samefile(dst):
        raise SystemExit("source and destination must not be aliases")
    data = bytearray(src.read_bytes())
    orig_hash = sha256(bytes(data))
    if orig_hash != SOURCE_SHA256:
        raise SystemExit(
            "source hash mismatch: %s (wanted %s)" % (orig_hash, SOURCE_SHA256)
        )
    cave_blob, meta = assemble_caves()

    hook_off = va_to_off(HOOK)
    reset_off = va_to_off(RESET)
    review_route_off = va_to_off(REVIEW_ROUTE_TEST)

    if data[hook_off : hook_off + 8] != HOOK_ORIG:
        raise SystemExit(
            "hook site mismatch at 0x%x: %s"
            % (hook_off, data[hook_off : hook_off + 8].hex())
        )
    if data[reset_off : reset_off + 6] != RESET_ORIG:
        raise SystemExit(
            "reset site mismatch at 0x%x: %s"
            % (reset_off, data[reset_off : reset_off + 6].hex())
        )
    if (
        data[review_route_off : review_route_off + len(REVIEW_ROUTE_ORIG)]
        != REVIEW_ROUTE_ORIG
    ):
        raise SystemExit(
            "review-route site mismatch at 0x%x: %s"
            % (
                review_route_off,
                data[
                    review_route_off : review_route_off + len(REVIEW_ROUTE_ORIG)
                ].hex(),
            )
        )

    code_raw, code_raw_size = add_feature_sections(data, cave_blob, meta)

    jmp_hook = b"\xe9" + rel32(HOOK, CAVE) + b"\x90\x90\x90"
    if len(jmp_hook) != 8:
        raise SystemExit("hook trampoline length")
    data[hook_off : hook_off + 8] = jmp_hook

    reset_va = int(meta["reset_va"])
    jmp_reset = b"\xe9" + rel32(RESET, reset_va) + b"\x90"
    if len(jmp_reset) != 6:
        raise SystemExit("reset trampoline length")
    data[reset_off : reset_off + 6] = jmp_reset
    data[
        review_route_off : review_route_off + len(REVIEW_ROUTE_PATCH)
    ] = REVIEW_ROUTE_PATCH

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(data)
    min_inspected_file = code_raw + int(meta["min_inspected_off_in_cave"])
    percent_file = code_raw + int(meta["percent_off_in_cave"])
    info = {
        "src": str(src),
        "dst": str(dst),
        "src_sha256": orig_hash,
        "dst_sha256": sha256(bytes(data)),
        "missing_percent": MISSING_PERCENT,
        "missing_percent_file_offset": "0x%X" % percent_file,
        "missing_percent_va": "0x%X"
        % (CAVE + int(meta["percent_off_in_cave"])),
        "min_inspected": MIN_INSPECTED,
        "min_inspected_file_offset": "0x%X" % min_inspected_file,
        "min_inspected_va": "0x%X"
        % (CAVE + int(meta["min_inspected_off_in_cave"])),
        "hook_va": "0x%X" % HOOK,
        "cave_va": "0x%X" % CAVE,
        "reset_va": "0x%X" % RESET,
        "reset_cave_va": "0x%X" % reset_va,
        "review_route_test_va": "0x%X" % REVIEW_ROUTE_TEST,
        "review_route_mask_va": "0x%X" % (REVIEW_ROUTE_TEST + 3),
        "review_route_mask_file_offset": "0x%X" % (review_route_off + 3),
        "missing_counts_va": "0x%X" % MISSING_COUNTS,
        "inspected_counts_va": "0x%X" % INSPECTED_COUNTS,
        "code_section_rva": "0x%X" % CODE_RVA,
        "code_section_raw": "0x%X" % code_raw,
        "code_section_raw_size": "0x%X" % code_raw_size,
        "data_section_rva": "0x%X" % DATA_RVA,
        "cave_size": meta["cave_size"],
        "size_src": src.stat().st_size,
        "size_dst": dst.stat().st_size,
    }
    return info


def main() -> int:
    # Keep the long-standing entry point while the hardened implementation is
    # isolated in a separately reviewable module.
    try:
        from .patch_f1_missing_n_rev5 import main as hardened_main
    except ImportError:
        from patch_f1_missing_n_rev5 import main as hardened_main

    return hardened_main()


# Imports of the historical module must also receive the hardened builder.
try:
    from .patch_f1_missing_n_rev5 import patch as patch
except ImportError:
    from patch_f1_missing_n_rev5 import patch as patch


if __name__ == "__main__":
    raise SystemExit(main())
