# Dump xrefs for all LBTNDBL DATs to JSON (no memory scan).
#@category Vision3D
#@runtime PyGhidra

import json
import os

OUT = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps\Vision3D_lbtndbl_xrefs_only.json"

DATS = [
    "1410e2968", "1410f7ec0", "1410fad60", "1411096e8", "14111c954",
    "141126768", "141126db8", "14114f8b8", "141152824", "141158ab4",
    "141172884", "1411a82fc",
]


def main():
    program = currentProgram
    fm = program.getFunctionManager()
    rm = program.getReferenceManager()
    rows = {"program": program.getName(), "dats": []}
    for hx in DATS:
        addr = toAddr(int(hx, 16))
        xrefs = []
        for r in rm.getReferencesTo(addr):
            fa = r.getFromAddress()
            f = fm.getFunctionContaining(fa)
            xrefs.append({
                "from": format(fa.getOffset(), "x"),
                "type": str(r.getReferenceType()),
                "function": f.getName() if f else None,
                "entry": format(f.getEntryPoint().getOffset(), "x") if f else None,
                "body": f.getBody().getNumAddresses() if f else None,
            })
        rows["dats"].append({"dat": hx, "xref_count": len(xrefs), "xrefs": xrefs})
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2)
    print("WROTE", OUT)
    for d in rows["dats"]:
        print(d["dat"], d["xref_count"])


if __name__ == "__main__":
    main()
else:
    main()
