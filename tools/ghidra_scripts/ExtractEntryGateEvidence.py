"""Extract address-scoped stock evidence without locking or changing the project."""

import argparse
from collections import deque
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import re
import struct
import sys


ROOT = Path(__file__).resolve().parents[2]
SOURCE_SHA256 = "ccca11b2f05084b484fa5556c67f8874065dbc0b6265177d2517f81265af00f4"
PROGRAMS = {
    "Vision3D.exe": {
        "sha256": SOURCE_SHA256,
        "image_base": 0x140000000,
    },
    "AvVTraitLib.dll": {
        "sha256": "0f9f68b118112cea87e1735995776934d8d009e3d6d39a8a58562e3fa3e3e5f7",
        "image_base": 0x180000000,
    },
    "DyTools0.dll": {
        "sha256": "f5421b5509236d6a5ba7b20c6e764f0af5e0be131bf2b08e2bbe774ac805767e",
        "image_base": 0x180000000,
    },
    "mfc140.dll": {
        "sha256": "0cf26008fae0cb61dfe49e1c3fc17e0dd860be011d9a6a64b452f56335bafbfe",
        "image_base": 0x180000000,
        "project_directory": "v3d_files_uncomp",
        "project_name": "MFC140_STATION",
    },
}
GHIDRA_HOME = Path(
    r"C:\Users\s_sme\Documents\ghidra_12.1_PUBLIC_20260513\ghidra_12.1_PUBLIC"
)


def file_offset_for_rva(image, rva):
    pe_offset = struct.unpack_from("<I", image, 0x3C)[0]
    section_count = struct.unpack_from("<H", image, pe_offset + 6)[0]
    optional_size = struct.unpack_from("<H", image, pe_offset + 20)[0]
    section_table = pe_offset + 24 + optional_size
    for index in range(section_count):
        section = section_table + index * 40
        virtual_size, virtual_address, raw_size, raw_offset = struct.unpack_from(
            "<IIII", image, section + 8
        )
        if virtual_address <= rva < virtual_address + max(virtual_size, raw_size):
            return raw_offset + rva - virtual_address
    raise ValueError(f"RVA is outside file-backed sections: {rva:x}")


def extract(program, addresses, monitor):
    from ghidra.app.decompiler import DecompInterface

    functions = program.getFunctionManager()
    references = program.getReferenceManager()
    listing = program.getListing()
    decompiler = DecompInterface()
    rows = []
    try:
        if not decompiler.openProgram(program):
            raise RuntimeError(str(decompiler.getLastMessage()))
        for address_text in addresses:
            monitor.checkCancelled()
            address = program.getAddressFactory().getAddress(address_text)
            if address is None:
                raise ValueError(f"Invalid address: {address_text}")
            function = functions.getFunctionContaining(address)
            if function is None:
                raise ValueError(f"No analyzed function at {address_text}")
            incoming = []
            for reference in references.getReferencesTo(function.getEntryPoint()):
                monitor.checkCancelled()
                caller = functions.getFunctionContaining(reference.getFromAddress())
                incoming.append({
                    "from": str(reference.getFromAddress()),
                    "type": str(reference.getReferenceType()),
                    "caller": str(caller.getEntryPoint()) if caller else None,
                    "caller_name": str(caller.getName(True)) if caller else None,
                })
            instructions = []
            for instruction in listing.getInstructions(function.getBody(), True):
                monitor.checkCancelled()
                outgoing = []
                for reference in references.getReferencesFrom(instruction.getAddress()):
                    destination = reference.getToAddress()
                    symbol = program.getSymbolTable().getPrimarySymbol(destination)
                    outgoing.append({
                        "to": str(destination),
                        "type": str(reference.getReferenceType()),
                        "symbol": str(symbol.getName(True)) if symbol else None,
                    })
                instructions.append({
                    "address": str(instruction.getAddress()),
                    "bytes": bytes(value & 255 for value in instruction.getBytes()).hex(),
                    "text": str(instruction),
                    "references": outgoing,
                })
            result = decompiler.decompileFunction(function, 60, monitor)
            if not result.decompileCompleted() or result.getDecompiledFunction() is None:
                raise RuntimeError(f"Decompile failed at {address_text}: {result.getErrorMessage()}")
            rows.append({
                "requested_address": address_text,
                "entry": str(function.getEntryPoint()),
                "name": str(function.getName(True)),
                "incoming": incoming,
                "instructions": instructions,
                "decompilation": str(result.getDecompiledFunction().getC()),
            })
        return rows
    finally:
        decompiler.dispose()


def find_pointer_hits(program, address_text, monitor):
    from jpype.types import JArray, JByte

    memory = program.getMemory()
    functions = program.getFunctionManager()
    target = program.getAddressFactory().getAddress(address_text)
    if target is None:
        raise ValueError(f"Invalid pointer target: {address_text}")
    target_offset = int(target.getOffset())
    needle = JArray(JByte)([
        value if value < 0x80 else value - 0x100
        for value in target_offset.to_bytes(8, "little")
    ])
    hits = []
    direct_references = []
    for reference in program.getReferenceManager().getReferencesTo(target):
        source = reference.getFromAddress()
        stored_value = None
        if memory.contains(source):
            stored_value = int(memory.getLong(source)) & 0xFFFFFFFFFFFFFFFF
        direct_references.append({
            "from": str(source),
            "type": str(reference.getReferenceType()),
            "stored_qword": f"{stored_value:x}" if stored_value is not None else None,
        })
    for block in memory.getBlocks():
        if not block.isInitialized():
            continue
        cursor = block.getStart()
        while cursor.compareTo(block.getEnd()) <= 0:
            monitor.checkCancelled()
            found = memory.findBytes(cursor, block.getEnd(), needle, None, True, monitor)
            if found is None:
                break
            candidate_address = found.add(8)
            candidate_offset = int(memory.getLong(candidate_address)) & 0xFFFFFFFFFFFFFFFF
            candidate = functions.getFunctionContaining(
                program.getAddressFactory().getDefaultAddressSpace().getAddress(candidate_offset)
            )
            hits.append({
                "at": str(found),
                "next_qword": f"{candidate_offset:x}",
                "next_function": str(candidate.getEntryPoint()) if candidate else None,
                "next_function_name": str(candidate.getName(True)) if candidate else None,
            })
            cursor = found.add(1)
    return {
        "address": str(target),
        "direct_references": direct_references,
        "hits": hits,
    }


def find_indirect_slot(program, slot, monitor, byte_store=False):
    pattern = re.compile(
        rf"MOV byte ptr \[[A-Z][A-Z0-9]* \+ 0x{slot:x}\],.+" if byte_store else
        rf"(?:CALL|JMP) qword ptr \[[A-Z][A-Z0-9]* \+ 0x{slot:x}\]"
    )
    hits = []
    window = deque(maxlen=16)
    scanned = 0
    functions = program.getFunctionManager()
    for instruction in program.getListing().getInstructions(True):
        monitor.checkCancelled()
        scanned += 1
        window.append(instruction)
        text = str(instruction)
        if not pattern.fullmatch(text):
            continue
        caller = functions.getFunctionContaining(instruction.getAddress())
        hits.append({
            "address": str(instruction.getAddress()),
            "bytes": bytes(value & 255 for value in instruction.getBytes()).hex(),
            "text": text,
            "caller": str(caller.getEntryPoint()) if caller else None,
            "window": [{
                "address": str(nearby.getAddress()),
                "bytes": bytes(value & 255 for value in nearby.getBytes()).hex(),
                "text": str(nearby),
            } for nearby in window],
        })
    return {
        "slot": hex(slot),
        "scope": ("saved Listing; explicit MOV byte ptr [register + offset] only; "
              "excludes aliases, wider stores and other write opcodes" if byte_store else
              "saved Listing; explicit CALL/JMP qword ptr [register + slot] only"),
        "scanned_instructions": scanned,
        "hits": hits,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("addresses", nargs="*")
    parser.add_argument("--program", choices=PROGRAMS, default="Vision3D.exe")
    parser.add_argument("--references-to", action="append", default=[])
    parser.add_argument("--pointer-to", action="append", default=[])
    parser.add_argument("--indirect-slot", action="append", type=lambda value: int(value, 0), default=[])
    parser.add_argument("--byte-store-offset", action="append", type=lambda value: int(value, 0), default=[])
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    if arguments.output.exists():
        parser.error("Evidence output already exists; choose a new filename")
    expected = PROGRAMS[arguments.program]
    source = ROOT / "v3d_files_" / arguments.program
    source_bytes = source.read_bytes()
    source_hash = hashlib.sha256(source_bytes).hexdigest()
    if source_hash != expected["sha256"]:
        raise RuntimeError("Stock source SHA-256 mismatch")

    import pyghidra

    pyghidra.start(install_dir=GHIDRA_HOME)
    from ghidra.framework import Application
    from ghidra.framework.data import DefaultProjectData
    from ghidra.framework.model import ProjectLocator
    from java.lang import Object, System

    project = DefaultProjectData(
        ProjectLocator(str(ROOT / expected.get("project_directory", "v3d_files_uncomp")),
                       expected.get("project_name", "V3D_SKIP")), False, False
    )
    consumer = Object()
    program = None
    try:
        domain_file = project.getFile(f"/{arguments.program}")
        if domain_file is None:
            raise RuntimeError("Stock program is absent from the saved project")
        monitor = pyghidra.task_monitor(600)
        program = domain_file.getReadOnlyDomainObject(consumer, -1, monitor)
        if str(program.getExecutableSHA256()).lower() != expected["sha256"]:
            raise RuntimeError("Ghidra program source SHA-256 mismatch")
        if str(program.getLanguageID()) != "x86:LE:64:default":
            raise RuntimeError("Unexpected program language")
        image_base = expected["image_base"]
        if int(program.getImageBase().getOffset()) != image_base:
            raise RuntimeError("Unexpected program image base")
        addresses = list(arguments.addresses)
        address_references = []
        for address_text in arguments.references_to:
            address = program.getAddressFactory().getAddress(address_text)
            if address is None:
                raise ValueError(f"Invalid reference address: {address_text}")
            incoming = []
            for reference in program.getReferenceManager().getReferencesTo(address):
                monitor.checkCancelled()
                caller = program.getFunctionManager().getFunctionContaining(reference.getFromAddress())
                caller_address = str(caller.getEntryPoint()) if caller else None
                incoming.append({
                    "from": str(reference.getFromAddress()),
                    "type": str(reference.getReferenceType()),
                    "caller": caller_address,
                })
                if caller_address is not None:
                    addresses.append(caller_address)
            address_references.append({"address": str(address), "incoming": incoming})
        pointer_references = [
            find_pointer_hits(program, address_text, monitor)
            for address_text in arguments.pointer_to
        ]
        indirect_slots = [
            find_indirect_slot(program, slot, monitor)
            for slot in arguments.indirect_slot
        ]
        byte_stores = [
            find_indirect_slot(program, offset, monitor, byte_store=True)
            for offset in arguments.byte_store_offset
        ]
        addresses = list(dict.fromkeys(f"{int(address, 16):x}" for address in addresses))
        rows = extract(program, addresses, monitor)
        for row in rows:
            for instruction in row["instructions"]:
                encoded = bytes.fromhex(instruction["bytes"])
                offset = file_offset_for_rva(
                    source_bytes, int(instruction["address"], 16) - image_base
                )
                if source_bytes[offset:offset + len(encoded)] != encoded:
                    raise RuntimeError(f"Saved instruction differs from stock at {instruction['address']}")
        for scan in indirect_slots + byte_stores:
            for hit in scan["hits"]:
                for instruction in hit["window"]:
                    encoded = bytes.fromhex(instruction["bytes"])
                    offset = file_offset_for_rva(source_bytes, int(instruction["address"], 16) - image_base)
                    if source_bytes[offset:offset + len(encoded)] != encoded:
                        raise RuntimeError(f"Saved slot instruction differs from stock at {instruction['address']}")
        report = {
            "schema": 1,
            "mode": "saved-project-read-only; no analysis; no target execution",
            "source_sha256": source_hash,
            "source_size": len(source_bytes),
            "ghidra_version": str(Application.getApplicationVersion()),
            "java_version": str(System.getProperty("java.version")),
            "python": sys.version,
            "python_executable": sys.executable,
            "architecture": platform.machine(),
            "pyghidra": importlib.metadata.version("pyghidra"),
            "jpype": importlib.metadata.version("JPype1"),
            "command": sys.argv,
            "compiler": str(program.getCompilerSpec().getCompilerSpecID()),
            "function_count": int(program.getFunctionManager().getFunctionCount()),
            "instruction_bytes_match_stock": True,
            "address_references": address_references,
            "pointer_references": pointer_references,
            "indirect_slots": indirect_slots,
            "byte_stores": byte_stores,
            "limitations": [
                "Only saved analysis is visible; active-session unsaved analysis is excluded.",
                "Indirect calls and missing references are not proof of absence.",
                "Static evidence does not prove runtime scheduling or supported workload limits.",
            ],
            "functions": rows,
        }
        with arguments.output.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(report, stream, indent=2, sort_keys=True)
            stream.write("\n")
        print(f"EXTRACTED {len(rows)} functions; stock bytes verified: {arguments.output}")
    finally:
        if program is not None:
            program.release(consumer)
        project.close()


if __name__ == "__main__":
    main()