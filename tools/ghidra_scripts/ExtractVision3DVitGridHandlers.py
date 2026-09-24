# Find Vision3D handlers for ID_VITREPORTGRID_CLICK_* messages.
# @category Vision3D
# @runtime PyGhidra

#@runtime PyGhidra

import json
import os

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

OUT = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps\Vision3D_vitreportgrid_handlers.json"
DECOMP_DIR = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps\decomp"

NEEDLES = [
    "ID_VITREPORTGRID_CLICK_LBTNUP_INNER",
    "ID_VITREPORTGRID_CLICK_LBTNDWN_INNER",
    "ID_VITREPORTGRID_CLICK_LBTNDBL_INNER",
    "ID_VITREPORTGRID_CLICK_RBTNUP_INNER",
    "ID_VITREPORTGRID_CLICK_RBTNDWN_INNER",
    "ID_VITREPORTGRID_CLICK_RBTNDBL_INNER",
    "ID_VITREPORTGRID_CLICK_MBTNUP_INNER",
    "ID_VITREPORTGRID_CLICK_MBTNDWN_INNER",
    "ID_VITREPORTGRID_CLICK_MBTNDBL_INNER",
    "ID_VITREPORTGRID",
    "VITREPORTGRID",
]


def main():
    os.makedirs(DECOMP_DIR, exist_ok=True)
    program = currentProgram
    listing = program.getListing()
    decomp = DecompInterface()
    decomp.openProgram(program)
    monitor = ConsoleTaskMonitor()

    hits = []
    data_it = listing.getDefinedData(True)
    while data_it.hasNext():
        data = data_it.next()
        try:
            val = data.getValue()
        except Exception:
            continue
        if val is None:
            continue
        s = str(val)
        if "VITREPORTGRID" not in s and "VitReportGrid" not in s and "vitreportgrid" not in s.lower():
            continue
        addr = data.getAddress()
        refs = []
        for ref in program.getReferenceManager().getReferencesTo(addr):
            fn = getFunctionContaining(ref.getFromAddress())
            refs.append(
                {
                    "from": str(ref.getFromAddress()),
                    "function": fn.getName(True) if fn else None,
                    "entry": str(fn.getEntryPoint()) if fn else None,
                }
            )
        hits.append({"string": s, "address": str(addr), "refs": refs})

    # Decompile unique referencing functions
    seen = set()
    dumped = []
    for h in hits:
        for r in h["refs"]:
            entry = r.get("entry")
            if not entry or entry in seen:
                continue
            seen.add(entry)
            fn = getFunctionAt(toAddr(entry))
            if fn is None:
                continue
            res = decomp.decompileFunction(fn, 90, monitor)
            c = (
                res.getDecompiledFunction().getC()
                if res and res.getDecompiledFunction()
                else ""
            )
            path = os.path.join(
                DECOMP_DIR, "Vision3D_vitgrid_%s.c" % entry.replace(":", "")
            )
            with open(path, "w", encoding="utf-8") as out:
                out.write("// %s @ %s\n// string hit(s) nearby\n\n%s" % (fn.getName(True), entry, c))
            dumped.append(
                {
                    "function": fn.getName(True),
                    "entry": entry,
                    "path": path,
                    "c_bytes": len(c),
                }
            )

    payload = {"program": str(program.getName()), "string_hits": hits, "dumped": dumped}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print("WROTE", OUT, "hits", len(hits), "dumped", len(dumped))
    decomp.dispose()


if __name__ == "__main__":
    main()
else:
    main()
