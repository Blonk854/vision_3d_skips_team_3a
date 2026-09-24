# Extract OnClick* / image-open related symbols from DyTools0.
#@category Vision3D
#@runtime PyGhidra

import json
import os

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

OUT = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps\DyTools0_onclick_symbols.json"
DECOMP = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps\decomp"


def main():
    program = currentProgram
    fm = program.getFunctionManager()
    st = program.getSymbolTable()
    os.makedirs(DECOMP, exist_ok=True)

    needles = [
        "OnClick",
        "OnGbwAnalyze",
        "VitExtReport",
        "ReportGrid",
        "OpenImage",
        "ShowImage",
        "OIS",
        "Failure",
        "Missing",
        "Deviation",
        "Presence",
    ]
    hits = []
    for sym in st.getAllSymbols(True):
        name = sym.getName(True)
        if any(n.lower() in name.lower() for n in needles):
            addr = sym.getAddress()
            f = fm.getFunctionAt(addr)
            if f is None:
                f = fm.getFunctionContaining(addr)
            hits.append({
                "name": name,
                "address": format(addr.getOffset(), "x") if addr and not addr.isExternalAddress() else str(addr),
                "function": f.getName() if f else None,
                "entry": format(f.getEntryPoint().getOffset(), "x") if f else None,
                "body": f.getBody().getNumAddresses() if f else None,
            })

    # Prefer click-related decompiles
    ifc = DecompInterface()
    ifc.openProgram(program)
    monitor = ConsoleTaskMonitor()
    dumped = []
    for h in hits:
        if not h.get("entry"):
            continue
        nm = h["name"]
        if "OnClick" not in nm and "OnGbwAnalyzeCellMouseClickEvent" not in nm:
            continue
        if h.get("body") is None or h["body"] < 8:
            continue
        f = getFunctionAt(toAddr(int(h["entry"], 16)))
        if f is None:
            continue
        res = ifc.decompileFunction(f, 60, monitor)
        if not res or not res.decompileCompleted():
            continue
        text = res.getDecompiledFunction().getC()
        outp = os.path.join(DECOMP, "DyTools0_onclick_%s.c" % h["entry"])
        with open(outp, "w", encoding="utf-8") as fh:
            fh.write("// %s @ %s\n\n" % (nm, h["entry"]))
            fh.write(text[:20000])
        h["decomp"] = outp
        dumped.append(h)

    report = {
        "program": program.getName(),
        "hit_count": len(hits),
        "hits": hits[:400],
        "dumped": dumped,
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    print("WROTE", OUT, "hits", len(hits), "dumped", len(dumped))
    for h in dumped:
        print("DUMP", h["name"], h["entry"], h["body"])


if __name__ == "__main__":
    main()
else:
    main()
