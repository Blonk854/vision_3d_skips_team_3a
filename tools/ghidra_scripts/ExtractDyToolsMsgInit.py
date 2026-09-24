# Dump RegisterWindowMessage init and vtable slot targets for click path.
# @category Vision3D
# @runtime PyGhidra

#@runtime PyGhidra

import json
import os

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

OUT_DIR = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps\decomp"
JSON_OUT = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps\DyTools0_msg_init.json"

TARGETS = [
    "180040af0",
    "180040b10",
    "180040b30",
    "180040b50",
    "180040b70",
    "180040b90",
    "180040bb0",
    "180040bd0",
    "180040bf0",
]


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    decomp = DecompInterface()
    decomp.openProgram(currentProgram)
    monitor = ConsoleTaskMonitor()
    rows = []
    for a in TARGETS:
        fn = getFunctionAt(toAddr(a)) or getFunctionContaining(toAddr(a))
        if fn is None:
            rows.append({"addr": a, "error": "no function"})
            continue
        res = decomp.decompileFunction(fn, 60, monitor)
        c = (
            res.getDecompiledFunction().getC()
            if res and res.getDecompiledFunction()
            else ""
        )
        path = os.path.join(OUT_DIR, "DyTools0_msginit_%s.c" % a)
        with open(path, "w", encoding="utf-8") as out:
            out.write("// %s @ %s\n\n%s" % (fn.getName(True), a, c))
        rows.append({"addr": a, "name": fn.getName(True), "path": path, "preview": c[:500]})
        print("WROTE", path)
    with open(JSON_OUT, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    print("WROTE", JSON_OUT)
    decomp.dispose()


if __name__ == "__main__":
    main()
else:
    main()
