# Extract CAnomaliesGridWnd click path / message map / vtable overrides.
#@category Vision3D
#@runtime PyGhidra

import json
import os
import traceback

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

OUT_DIR = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps"
LOG = os.path.join(OUT_DIR, "Vision3D_anomalies_log.txt")
OUT = os.path.join(OUT_DIR, "Vision3D_anomalies_grid.json")
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
        st = program.getSymbolTable()
        rm = program.getReferenceManager()
        monitor = ConsoleTaskMonitor()
        decomp = DecompInterface()
        decomp.openProgram(program)
        log("program=%s" % program.getName())

        report = {"funcs": [], "vtable_syms": [], "dumped": []}
        keys = (
            "CAnomaliesGridWnd",
            "AnomaliesGrid",
            "AnomalyGrid",
        )
        it = fm.getFunctions(True)
        while it.hasNext():
            f = it.next()
            n = f.getName(True)
            if any(k in n for k in keys):
                entry = format(f.getEntryPoint().getOffset(), "x")
                body = f.getBody().getNumAddresses()
                report["funcs"].append({"name": n, "entry": entry, "body": body})
        log("funcs=%d" % len(report["funcs"]))

        # Also symbols (vtables etc.)
        for sym in st.getSymbolIterator("CAnomaliesGridWnd", True):
            n = sym.getName(True)
            if "CAnomaliesGridWnd" not in n:
                break
            report["vtable_syms"].append({
                "name": n,
                "address": format(sym.getAddress().getOffset(), "x") if not sym.isExternal() else str(sym.getAddress()),
            })
        log("syms=%d" % len(report["vtable_syms"]))

        # Decompile all CAnomaliesGridWnd methods with body>=8, prioritize Click/Message/Mouse/OIS/Image
        pri = []
        other = []
        for item in report["funcs"]:
            n = item["name"]
            if item["body"] < 8:
                continue
            bucket = pri if any(
                k in n for k in (
                    "Click", "Mouse", "Message", "OnGbw", "OIS", "Image",
                    "Open", "Show", "Select", "Column", "Row", "Anomal",
                )
            ) else other
            bucket.append(item)
        todo = pri + sorted(other, key=lambda x: -x["body"])[:30]
        log("todo=%d pri=%d" % (len(todo), len(pri)))

        for item in todo:
            f = getFunctionAt(toAddr(item["entry"]))
            if f is None:
                continue
            res = decomp.decompileFunction(f, 120, monitor)
            c = res.getDecompiledFunction().getC() if res and res.getDecompiledFunction() else "// FAIL\n"
            path = os.path.join(DECOMP, "Vision3D_anom_%s.c" % item["entry"])
            with open(path, "w", encoding="utf-8") as out:
                out.write("// %s @ %s\n\n%s" % (item["name"], item["entry"], c[:25000]))
            dumped = dict(item)
            dumped["decomp"] = path
            dumped["decomp_len"] = len(c)
            report["dumped"].append(dumped)
            log("dump %s body=%d %s" % (item["entry"], item["body"], item["name"][:90]))

        # Also search functions that mention both Anomal and Click in name more loosely
        it = fm.getFunctions(True)
        extra = []
        while it.hasNext():
            f = it.next()
            n = f.getName(True)
            if "Anomal" in n and any(k in n for k in ("Click", "Mouse", "Gbw", "Select", "Image", "OIS")):
                entry = format(f.getEntryPoint().getOffset(), "x")
                if any(d["entry"] == entry for d in report["dumped"]):
                    continue
                extra.append(f)
        for f in extra[:20]:
            entry = format(f.getEntryPoint().getOffset(), "x")
            res = decomp.decompileFunction(f, 120, monitor)
            c = res.getDecompiledFunction().getC() if res and res.getDecompiledFunction() else "// FAIL\n"
            path = os.path.join(DECOMP, "Vision3D_anomextra_%s.c" % entry)
            with open(path, "w", encoding="utf-8") as out:
                out.write("// %s @ %s\n\n%s" % (f.getName(True), entry, c[:25000]))
            report["dumped"].append({
                "name": f.getName(True),
                "entry": entry,
                "body": f.getBody().getNumAddresses(),
                "decomp": path,
                "kind": "extra",
            })
            log("extra %s %s" % (entry, f.getName(True)[:90]))

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
