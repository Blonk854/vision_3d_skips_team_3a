"""Recompute Team 3a vector-ownership progress from the repo files and stock Vision3D.exe.

Run from the repository root:

    python maps/vector_ownership/team2_progress_check.py

Exit 0 means every check matched. A mismatch prints FAIL and exits 1.
The checker reads files. It does not open Ghidra and it does not write anything.
"""

from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXE = ROOT / "v3d_files_" / "Vision3D.exe"
GATE = ROOT / "maps" / "vector_ownership" / "anomaly_vector_mutator_table.json"
TRACE = ROOT / "maps" / "vector_ownership" / "anomaly_begin_store_trace.txt"
RESPONSE = ROOT / "handoff" / "team3_response.md"
IMAGE_BASE = 0x140000000

EXE_SHA256 = "ccca11b2f05084b484fa5556c67f8874065dbc0b6265177d2517f81265af00f4"
EXE_SIZE = 28_738_048
GATE_MD5 = "3C05BBB66D1463CB3B7CA0F1EDC78AEB"

SNAPSHOT_PASS = "20261013T003814Z-5713b20b"
SNAPSHOT_HEADING = (
    "Wait flag taken after the second rcx rbx jmp mov mov lea mov call "
    "mov mov lea call mov mov call nop lea call xor lea mov mov pop pop "
    "pop pop ret cc cc cc cc cc cc"
)
SNAPSHOT_FRONTIER = 0x1406A1D99

failures: list[str] = []


def check(name: str, ok: bool, detail: str) -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"{mark}  {name}: {detail}")
    if not ok:
        failures.append(name)


def parse_pe(data: bytes):
    if data[:2] != b"MZ":
        raise SystemExit("Vision3D.exe is not an MZ image")
    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    if data[e_lfanew : e_lfanew + 4] != b"PE\x00\x00":
        raise SystemExit("Vision3D.exe is not a PE image")
    coff = e_lfanew + 4
    nsections = struct.unpack_from("<H", data, coff + 2)[0]
    opt_size = struct.unpack_from("<H", data, coff + 16)[0]
    opt = coff + 20
    magic = struct.unpack_from("<H", data, opt)[0]
    if magic != 0x20B:
        raise SystemExit(f"expected PE32+ magic, got {magic:#x}")
    image_base = struct.unpack_from("<Q", data, opt + 24)[0]
    sections = []
    sec = opt + opt_size
    for i in range(nsections):
        off = sec + i * 40
        vsize, va, rawsize, rawptr = struct.unpack_from("<IIII", data, off + 8)
        sections.append((va, max(vsize, rawsize), rawptr, rawsize))
    return image_base, opt, sections


def file_off(sections, rva: int) -> int:
    for va, span, rawptr, rawsize in sections:
        if va <= rva < va + span:
            delta = rva - va
            if delta >= rawsize:
                raise SystemExit(f"RVA {rva:#x} is inside a section but past raw data")
            return rawptr + delta
    raise SystemExit(f"RVA {rva:#x} is not in any section")


def read_va(data: bytes, sections, va: int, n: int) -> bytes:
    return data[file_off(sections, va - IMAGE_BASE) : file_off(sections, va - IMAGE_BASE) + n]


def import_at_iat(data: bytes, opt: int, sections, iat_va: int) -> tuple[str, str]:
    iat_rva = iat_va - IMAGE_BASE
    import_rva, _import_size = struct.unpack_from("<II", data, opt + 112 + 8)
    cursor = file_off(sections, import_rva)
    while True:
        ilt, _ts, _fwd, name_rva, iat = struct.unpack_from("<IIIII", data, cursor)
        if ilt == 0 and name_rva == 0 and iat == 0:
            break
        dll = data[file_off(sections, name_rva) :].split(b"\x00", 1)[0].decode("ascii", "replace")
        slot = iat
        index = 0
        while True:
            val_off = file_off(sections, slot)
            val = struct.unpack_from("<Q", data, val_off)[0]
            if val == 0:
                break
            if slot == iat_rva:
                thunk_rva = ilt or iat
                thunk = struct.unpack_from("<Q", data, file_off(sections, thunk_rva + index * 8))[0]
                if thunk & (1 << 63):
                    name = f"ordinal {thunk & 0xFFFF}"
                else:
                    name_off = file_off(sections, (thunk & 0x7FFFFFFF) + 2)
                    name = data[name_off:].split(b"\x00", 1)[0].decode("ascii", "replace")
                return dll, name
            slot += 8
            index += 1
        cursor += 20
    raise SystemExit(f"no import owns IAT slot {iat_va:#x}")


def iat_slot_of_call(data: bytes, sections, call_va: int) -> int:
    raw = read_va(data, sections, call_va, 6)
    if raw[:2] != bytes.fromhex("ff15"):
        raise SystemExit(f"{call_va:#x} is {raw.hex()}, not an FF 15 call")
    disp = struct.unpack_from("<i", raw, 2)[0]
    return call_va + 6 + disp


def last_section(text: str) -> tuple[str, str]:
    matches = list(re.finditer(r"^===== (.+) =====\r?$", text, re.M))
    headings = [(m.group(1), m.start()) for m in matches if m.group(1) != "END"]
    if not headings:
        raise SystemExit("trace has no ===== heading")
    name, start = headings[-1]
    end_match = re.search(r"^===== END =====\r?$", text[start:], re.M)
    if not end_match:
        raise SystemExit("last heading has no END line")
    body = text[start : start + end_match.end()]
    return name, body


def main() -> int:
    print("Team 3a progress check")
    print(f"root: {ROOT}")

    exe = EXE.read_bytes()
    exe_hash = hashlib.sha256(exe).hexdigest()
    check("executable size", len(exe) == EXE_SIZE, f"{len(exe)} bytes")
    check("executable sha256", exe_hash == EXE_SHA256, exe_hash)
    image_base, opt, sections = parse_pe(exe)
    check("image base", image_base == IMAGE_BASE, hex(image_base))

    gate_bytes = GATE.read_bytes()
    gate_md5 = hashlib.md5(gate_bytes).hexdigest().upper()
    check("gate file md5", gate_md5 == GATE_MD5, gate_md5)
    gate = json.loads(gate_bytes)
    check(
        "gate status",
        gate["gate_status"].startswith("CLOSED - outer vector one-shot"),
        gate["gate_status"],
    )
    req = gate["gate_requirements"]
    check("outer vector", req["outer_vector"].startswith("CLOSED"), req["outer_vector"])
    check(
        "inner vector growth",
        req["inner_vector_growth"].startswith("CLOSED"),
        req["inner_vector_growth"],
    )
    check(
        "synchronization",
        req["synchronization"].startswith("PARTIAL"),
        req["synchronization"],
    )
    barrier = gate["synchronization_contracts"]["worker_to_capm"]["barrier"]
    check("worker-to-capm barrier", barrier.startswith("NONE PROVEN"), barrier)

    locks = list((ROOT / "v3d_files_uncomp_copy").glob("V3D_SKIP.lock*"))
    check("copy project lock", locks == [], "absent" if not locks else ", ".join(p.name for p in locks))

    response_first = RESPONSE.read_text(encoding="utf-8").splitlines()[0]
    check(
        "latest response pass",
        response_first == f"Pass id: {SNAPSHOT_PASS}",
        response_first,
    )

    text = TRACE.read_text(encoding="utf-8")
    heading, body = last_section(text)
    check("frontier heading", heading == SNAPSHOT_HEADING, heading)
    addr = re.search(r"Address: `([^`]+)` \.\. `([^`]+)`", body)
    mnemonic = re.search(r"^Mnemonic: (.+)$", body, re.M)
    byte_match = re.search(r"bytes: `([^`]+)`", body)
    check("frontier min", addr is not None and addr.group(1).lower() == "0x1406a1d99", addr.group(1) if addr else "missing")
    check("frontier max", addr is not None and addr.group(2).lower() == "0x1406a1d99", addr.group(2) if addr else "missing")
    check("frontier bytes in trace", byte_match is not None and byte_match.group(1).lower() == "cc", byte_match.group(1) if byte_match else "missing")
    check("frontier mnemonic", mnemonic is not None and mnemonic.group(1).strip() == "??", mnemonic.group(1).strip() if mnemonic else "missing")

    file_frontier = read_va(exe, sections, SNAPSHOT_FRONTIER, 1)
    check("frontier byte in exe", file_frontier == b"\xcc", file_frontier.hex())

    explicit = re.findall(r"^Is mnemonic MFENCE or first byte F0\? (.+)$", text, re.M)
    yes = [line for line in explicit if line.startswith("Yes")]
    check(
        "explicit MFENCE answers",
        explicit and not yes,
        f"{len(explicit)} question lines, {len(yes)} answered Yes",
    )

    calls = {
        "completion signal": (0x1406A1C16, "KERNEL32.dll", "SetEvent"),
        "worker wait": (0x1406A1B6F, "KERNEL32.dll", "WaitForMultipleObjects"),
    }
    for label, (va, dll, name) in calls.items():
        slot = iat_slot_of_call(exe, sections, va)
        got_dll, got_name = import_at_iat(exe, opt, sections, slot)
        check(
            label,
            got_dll.lower() == dll.lower() and got_name == name,
            f"{va:#x} -> {slot:#x} {got_dll}::{got_name}",
        )

    raw_checks = {
        "slot store has no LOCK prefix": (0x140737411, bytes.fromhex("f2410f1185b8020000")),
        "component epilogue RET": (0x1407374E8, b"\xc3"),
        "handler body RET": (0x1406A1C7B, b"\xc3"),
        "handler indirect call": (0x1406A1C09, bytes.fromhex("ff5018")),
        "SetEvent return is not read": (0x1406A1C1C, bytes.fromhex("448b4b70")),
        "epilogue clears EAX": (0x1406A1C6E, bytes.fromhex("33c0")),
        "later RET before padding": (0x1406A1D92, b"\xc3"),
        "padding after that RET": (0x1406A1D93, b"\xcc" * 6),
    }
    for label, (va, expected) in raw_checks.items():
        got = read_va(exe, sections, va, len(expected))
        check(label, got == expected, f"{va:#x} {got.hex()}")

    print()
    if failures:
        print(f"{len(failures)} check(s) failed: {', '.join(failures)}")
        return 1
    print("All checks passed. The brief matches these files and v3d_files_/Vision3D.exe.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
