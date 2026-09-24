# Extract ProfUISm OnGbwAnalyzeCellMouseClickEvent implementations.
# @category Vision3D
# @runtime PyGhidra

#@runtime PyGhidra

import json
import os

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

OUT_DIR = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps"
DECOMP_DIR = os.path.join(OUT_DIR, "decomp")


def main():
    os.makedirs(DECOMP_DIR, exist_ok=True)
    program = currentProgram
    fm = program.getFunctionManager()
    decomp = DecompInterface()
    decomp.openProgram(program)
    monitor = ConsoleTaskMonitor()
    hits = []
    it = fm.getFunctions(True)
    while it.hasNext():
        f = it.next()
        name = f.getName(True)
        if "OnGbwAnalyzeCellMouseClickEvent" in name:
            hits.append(f)
    results = []
    for f in hits:
        entry = str(f.getEntryPoint())
        res = decomp.decompileFunction(f, 90, monitor)
        c = (
            res.getDecompiledFunction().getC()
            if res and res.getDecompiledFunction()
            else "// FAILED\n"
        )
        path = os.path.join(DECOMP_DIR, "ProfUISm_click_%s.c" % entry.replace(":", ""))
        with open(path, "w", encoding="utf-8") as out:
            out.write("// %s @ %s\n\n%s" % (f.getName(True), entry, c))
        results.append(
            {
                "name": f.getName(True),
                "entry": entry,
                "body": int(f.getBody().getNumAddresses()),
                "decomp": path,
                "c_bytes": len(c),
            }
        )
        print("WROTE", path, len(c))
    out_json = os.path.join(OUT_DIR, "ProfUISm_click_extract.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(
            {
                "program": str(program.getName()),
                "functions": fm.getFunctionCount(),
                "click_handlers": results,
            },
            f,
            indent=2,
        )
    print("WROTE", out_json)
    decomp.dispose()


if __name__ == "__main__":
    main()
else:
    main()
