# Trace Vision3D creators / parents of CVitExtReportGridWnd and IAT thunks.
#@category Vision3D
#@runtime PyGhidra

import json
import os
import traceback

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

OUT_DIR = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps"
LOG = os.path.join(OUT_DIR, "Vision3D_grid_owners_log.txt")
OUT = os.path.join(OUT_DIR, "Vision3D_grid_owners.json")
DECOMP = os.path.join(OUT_DIR, "decomp")


def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(DECOMP, exist_ok=True)
    open(LOG, "w", encoding="utf-8").write("")
    try:
        program = currentProgram
        fm = program.getFunctionManager()
        rm = program.getReferenceManager()
        st = program.getSymbolTable()
        monitor = ConsoleTaskMonitor()
        decomp = DecompInterface()
        decomp.openProgram(program)
        log("program=%s" % program.getName())

        report = {"symbols": [], "ext_refs": [], "dumped": []}

        # Find external symbols / imports mentioning VitExtReportGrid
        for sym in st.getExternalSymbols():
            n = sym.getName(True)
            if "VitExtReportGrid" in n or "CVitExtReportGridWnd" in n:
                report["symbols"].append({"name": n, "addr": str(sym.getAddress())})

        # Also all symbols containing that string
        for sym in st.getSymbolIterator("CVitExtReportGridWnd", True):
            n = sym.getName(True)
            if "CVitExtReportGridWnd" not in n:
                break
            addr = sym.getAddress()
            refs = []
            for r in rm.getReferencesTo(addr):
                fa = r.getFromAddress()
                f = fm.getFunctionContaining(fa)
                refs.append({
                    "from": format(fa.getOffset(), "x"),
                    "type": str(r.getReferenceType()),
                    "function": f.getName(True) if f else None,
                    "entry": format(f.getEntryPoint().getOffset(), "x") if f else None,
                    "body": f.getBody().getNumAddresses() if f else None,
                })
            report["ext_refs"].append({
                "name": n,
                "address": str(addr),
                "refs": refs[:40],
                "ref_count": len(refs),
            })
            log("sym %s refs=%d" % (n[:80], len(refs)))

        # Decompile largest callers of ctor / SetParent / useful methods
        interesting_names = (
            "CVitExtReportGridWnd",
            "OnGbwAnalyzeCellMouseClickEvent",
        )
        candidates = []
        for block in report["ext_refs"]:
            for r in block["refs"]:
                if r.get("body") and r["body"] > 100 and r.get("entry"):
                    candidates.append(r)
        # unique by entry
        seen = set()
        uniq = []
        for c in sorted(candidates, key=lambda x: -x["body"]):
            if c["entry"] in seen:
                continue
            seen.add(c["entry"])
            uniq.append(c)
        for c in uniq[:15]:
            f = getFunctionAt(toAddr(c["entry"]))
            if f is None:
                continue
            res = decomp.decompileFunction(f, 90, monitor)
            text = res.getDecompiledFunction().getC() if res and res.getDecompiledFunction() else "// FAIL\n"
            path = os.path.join(DECOMP, "Vision3D_gridowner_%s.c" % c["entry"])
            with open(path, "w", encoding="utf-8") as out:
                out.write("// caller %s @ %s body=%d\n\n%s" % (
                    c["function"], c["entry"], c["body"], text[:20000]))
            c2 = dict(c)
            c2["decomp"] = path
            report["dumped"].append(c2)
            log("dump %s body=%d" % (c["entry"], c["body"]))

        with open(OUT, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2)
        log("WROTE %s" % OUT)
        decomp.dispose()
    except Exception:
        log(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
else:
    main()
