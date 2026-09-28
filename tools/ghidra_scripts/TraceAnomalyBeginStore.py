#!/usr/bin/env python3
"""Read-only: decompile anomaly-vector alloc/free candidates and find * 0x370 sites."""
import os
from pathlib import Path

os.environ["JAVA_HOME_OVERRIDE"] = (
    r"C:\Users\s_sme\Documents\ghidra_12.1_PUBLIC_20260513\ghidra_12.1_PUBLIC"
    r"\OpenJDK25U-jdk_x64_windows_hotspot_25.0.3_9\jdk-25.0.3+9"
)

import pyghidra

pyghidra.start(
    install_dir=r"C:\Users\s_sme\Documents\ghidra_12.1_PUBLIC_20260513\ghidra_12.1_PUBLIC"
)

import jpype

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

PROJECT_DIR = Path(
    r"C:\Users\s_sme\Documents\VS_Project_LapTop\vision_3d_skips - team 3a\v3d_files_uncomp_copy"
)
OUT = Path(
    r"C:\Users\s_sme\Documents\VS_Project_LapTop\vision_3d_skips - team 3a\maps\vector_ownership\anomaly_begin_store_trace.txt"
)
TARGETS = [0x140672810]


def addr(program, value):
    return program.getAddressFactory().getDefaultAddressSpace().getAddress(value)


def refs_to(program, target):
    lines = []
    for ref in program.getReferenceManager().getReferencesTo(target):
        src = ref.getFromAddress()
        func = program.getFunctionManager().getFunctionContaining(src)
        name = func.getName() if func else "?"
        entry = func.getEntryPoint() if func else None
        lines.append(
            f"  {src} {ref.getReferenceType()} from {name}@{entry}"
        )
    return lines


def filtered(code):
    keep = []
    for line in code.splitlines():
        low = line.lower()
        if any(
            token in low
            for token in (
                "0x18",
                "0x20",
                "0x28",
                "0x370",
                "0x6e",
                "operator_new",
                "operator new",
                "malloc",
                "param_1[3]",
                "param_1[4]",
                "param_1[5]",
                "fun_",
            )
        ):
            keep.append(line.rstrip())
    return keep


def main():
    project = pyghidra.open_project(PROJECT_DIR, "V3D_SKIP", create=False)
    program, consumer = pyghidra.consume_program(project, "/Vision3D.exe")
    try:
        monitor = ConsoleTaskMonitor()
        iface = DecompInterface()
        iface.toggleCCode(True)
        iface.toggleSyntaxTree(False)
        if not iface.openProgram(program):
            print("decompiler open failed", iface.getLastMessage())
            return 1
        chunks = []
        try:
            memory = program.getMemory()
            start = program.getMinAddress()
            needles = []
            for needle in needles:
                pattern = jpype.JArray(jpype.JByte)(list(needle))
                found = start
                chunks.append(f"===== string {needle!r} =====")
                while True:
                    found = memory.findBytes(found, pattern, None, True, monitor)
                    if found is None:
                        break
                    chunks.append(f"at {found}")
                    for ref in program.getReferenceManager().getReferencesTo(found):
                        src = ref.getFromAddress()
                        func = program.getFunctionManager().getFunctionContaining(src)
                        chunks.append(
                            f"  xref {src} from {func.getName() if func else '?'}@{func.getEntryPoint() if func else None}"
                        )
                    found = found.add(1)
            # Also decompile the vector deallocator and its callers' callees that look like allocators.
            for value in (0x1405315A0,):
                target = addr(program, value)
                func = program.getFunctionManager().getFunctionAt(target)
                chunks.append(f"===== {hex(value)} {func.getName() if func else None} =====")
                if func is not None:
                    result = iface.decompileFunction(func, 90, monitor)
                    if result.decompileCompleted():
                        lines = result.getDecompiledFunction().getC().splitlines()
                        for index, line in enumerate(lines):
                            if "FUN_140674570" in line:
                                for extra in lines[max(0, index - 12):index + 3]:
                                    chunks.append(extra.rstrip())
        finally:
            iface.dispose()
            program.release(consumer)
        OUT.write_text("\n".join(chunks), encoding="utf-8")
        print("WROTE", OUT, "lines", len(chunks))
        return 0
    finally:
        project.close()


if __name__ == "__main__":
    raise SystemExit(main())
