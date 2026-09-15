"""Patch Vision3D.exe Feature 1: skip sub-panel above a Missing percentage.

Writes a NEW file. Never overwrites the source PE.
Hard-coded threshold: more than 30% Missing after at least 10 inspections.
"""
from __future__ import annotations

import hashlib
import pathlib
import struct
import sys

IMAGE_BASE = 0x140000000
TEXT_VA = 0x1000
TEXT_RAW = 0x400

HOOK = 0x140736F09  # LEA RDX,[RBP-0x18]; LEA RCX,[RBP-0x78]
HOOK_RET = 0x140736F11  # original CALL after the two LEAs
HOOK_ORIG = bytes.fromhex("488d55e8488d4d88")  # 8 bytes stolen

RESET = 0x140541050  # SkipList_Reset
RESET_CONT = 0x140541056  # MOV RBX,RCX
RESET_ORIG = bytes.fromhex("40534883ec20")  # 6 bytes stolen

CAVE = 0x140D50910  # .text raw slack after virtual size
MISSING_COUNTS = 0x14120C680  # last .data page padding, demand-zero
INSPECTED_COUNTS = MISSING_COUNTS + 0x400
SKIPSUB = 0x140541080
MISSING_PERCENT = 30
MIN_INSPECTED = 10
N_SLOTS = 256
N_COUNTER_DWORDS = N_SLOTS * 2

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


def assemble_caves() -> tuple[bytes, dict]:
    code = bytearray()
    meta: dict[str, object] = {}

    def va() -> int:
        return CAVE + len(code)

    def emit(b: bytes) -> None:
        code.extend(b)

    emit(bytes.fromhex("8b4714"))  # mov eax,[rdi+0x14]
    emit(bytes.fromhex("3d00010000"))  # cmp eax,256
    jae_at = len(code)
    emit(b"\x73\x00")
    emit(bytes.fromhex("4c8d05"))
    lea_at = len(code)
    emit(b"\x00\x00\x00\x00")
    struct.pack_into("<i", code, lea_at, MISSING_COUNTS - va())
    emit(bytes.fromhex("41ff848000040000"))  # inc inspected[eax]
    emit(bytes.fromhex("f7c301000000"))  # test ebx,1
    not_missing_at = len(code)
    emit(b"\x74\x00")
    emit(bytes.fromhex("41ff0480"))  # inc missing[eax]
    emit(bytes.fromhex("4183bc8000040000"))  # cmp inspected[eax],imm8
    meta["min_inspected_off_in_cave"] = len(code)
    emit(bytes([MIN_INSPECTED]))
    below_min_at = len(code)
    emit(b"\x72\x00")
    emit(bytes.fromhex("458b1480"))  # mov r10d,missing[eax]
    emit(bytes.fromhex("456bd264"))  # imul r10d,r10d,100
    emit(bytes.fromhex("458b9c8000040000"))  # mov r11d,inspected[eax]
    emit(bytes.fromhex("456bdb"))  # imul r11d,r11d,percent
    meta["percent_off_in_cave"] = len(code)
    emit(bytes([MISSING_PERCENT]))
    emit(bytes.fromhex("453bd3"))  # cmp r10d,r11d
    at_or_below_at = len(code)
    emit(b"\x76\x00")
    emit(bytes.fromhex("8bd0"))  # mov edx,eax
    emit(bytes.fromhex("498b4f10"))  # mov rcx,[r15+0x10]
    emit(b"\xe8")
    emit(rel32(va() - 1, SKIPSUB))
    done = va()
    code[jae_at + 1] = rel8(CAVE + jae_at + 2, done)[0]
    code[not_missing_at + 1] = rel8(CAVE + not_missing_at + 2, done)[0]
    code[below_min_at + 1] = rel8(CAVE + below_min_at + 2, done)[0]
    code[at_or_below_at + 1] = rel8(CAVE + at_or_below_at + 2, done)[0]
    emit(HOOK_ORIG)
    emit(b"\xe9")
    emit(rel32(va() - 1, HOOK_RET))
    meta["hook_size"] = len(code)
    if len(code) > 0x70:
        raise RuntimeError("hook too big %d" % len(code))
    code.extend(b"\xcc" * (0x70 - len(code)))

    meta["reset_va"] = va()
    emit(bytes.fromhex("40534883ec20"))  # push rbx; sub rsp,20
    emit(bytes.fromhex("488bd9"))  # mov rbx, rcx (this)
    emit(bytes.fromhex("4c8d05"))
    rlea = len(code)
    emit(b"\x00\x00\x00\x00")
    struct.pack_into("<i", code, rlea, MISSING_COUNTS - va())
    emit(bytes.fromhex("33c9"))  # xor ecx,ecx
    loop = va()
    emit(bytes.fromhex("41c7048800000000"))  # mov dword [r8+rcx*4], 0
    emit(bytes.fromhex("ffc1"))  # inc ecx
    emit(bytes.fromhex("81f9"))  # cmp ecx, N_SLOTS
    emit(struct.pack("<I", N_COUNTER_DWORDS))
    emit(b"\x72")  # jb loop
    emit(rel8(va() + 1, loop))
    emit(bytes.fromhex("488bcb"))  # mov rcx, rbx
    emit(b"\xe9")
    emit(rel32(va() - 1, RESET_CONT))
    meta["cave_size"] = len(code)
    return bytes(code), meta


def patch(src: pathlib.Path, dst: pathlib.Path) -> dict:
    data = bytearray(src.read_bytes())
    orig_hash = sha256(bytes(data))
    cave_blob, meta = assemble_caves()

    hook_off = va_to_off(HOOK)
    reset_off = va_to_off(RESET)
    cave_off = va_to_off(CAVE)

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
    if any(data[cave_off : cave_off + len(cave_blob)]):
        raise SystemExit("cave is not empty")

    jmp_hook = b"\xe9" + rel32(HOOK, CAVE) + b"\x90\x90\x90"
    if len(jmp_hook) != 8:
        raise SystemExit("hook trampoline length")
    data[hook_off : hook_off + 8] = jmp_hook

    reset_va = int(meta["reset_va"])
    jmp_reset = b"\xe9" + rel32(RESET, reset_va) + b"\x90"
    if len(jmp_reset) != 6:
        raise SystemExit("reset trampoline length")
    data[reset_off : reset_off + 6] = jmp_reset

    data[cave_off : cave_off + len(cave_blob)] = cave_blob

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(data)
    min_inspected_file = cave_off + int(meta["min_inspected_off_in_cave"])
    percent_file = cave_off + int(meta["percent_off_in_cave"])
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
        "missing_counts_va": "0x%X" % MISSING_COUNTS,
        "inspected_counts_va": "0x%X" % INSPECTED_COUNTS,
        "cave_size": meta["cave_size"],
        "size_src": src.stat().st_size,
        "size_dst": dst.stat().st_size,
    }
    return info


def main() -> int:
    src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else SRC_DEFAULT
    dst = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else OUT_DEFAULT
    info = patch(src, dst)
    for k, v in info.items():
        print("%s=%s" % (k, v))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
