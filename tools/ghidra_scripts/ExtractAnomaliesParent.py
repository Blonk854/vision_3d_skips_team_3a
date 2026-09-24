# Find parent window that owns CAnomaliesGridWnd and any registered-msg handlers.
#@category Vision3D
#@runtime PyGhidra

import json
import os

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

OUT = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps\Vision3D_anomalies_parent.json"
LOG = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps\Vision3D_anomalies_parent_log.txt"
DECOMP = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps\decomp"

def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)

def main():
    open(LOG, "w", encoding="utf-8").write("")
    os.makedirs(DECOMP, exist_ok=True)
    program = currentProgram
    fm = program.getFunctionManager()
    rm = program.getReferenceManager()
    st = program.getSymbolTable()
    decomp = DecompInterface()
    decomp.openProgram(program)
    monitor = ConsoleTaskMonitor()

    report = {"ctor_callers": [], "setparent": [], "dumped": []}

    # Who calls CAnomaliesGridWnd ctor FUN_140453090?
    ctor = getFunctionAt(toAddr("140453090"))
    for r in rm.getReferencesTo(ctor.getEntryPoint()):
        fa = r.getFromAddress()
        f = fm.getFunctionContaining(fa)
        if f is None:
            continue
        entry = format(f.getEntryPoint().getOffset(), "x")
        item = {
            "from": format(fa.getOffset(), "x"),
            "entry": entry,
            "name": f.getName(True),
            "body": f.getBody().getNumAddresses(),
            "type": str(r.getReferenceType()),
        }
        report["ctor_callers"].append(item)
        log("ctor_caller %s %s body=%d" % (entry, item["name"][:80], item["body"]))

    # Search symbols with Anomal in dialog/doc names
    for sym in st.getAllSymbols(True):
        n = sym.getName(True)
        if "Anomal" not in n:
            continue
        if any(k in n for k in ("Dlg", "Doc", "View", "Form", "Wnd", "Compose", "Review", "Repair")):
            addr = sym.getAddress()
            f = fm.getFunctionAt(addr)
            if f is None:
                f = fm.getFunctionContaining(addr)
            report.setdefault("anom_syms", []).append({
                "name": n,
                "address": format(addr.getOffset(), "x") if addr and not addr.isExternalAddress() else str(addr),
                "function": f.getName(True) if f else None,
                "entry": format(f.getEntryPoint().getOffset(), "x") if f else None,
                "body": f.getBody().getNumAddresses() if f else None,
            })

    # Decompile largest ctor callers + FUN_1404564b0 (big local vt method)
    todo = []
    for c in report["ctor_callers"]:
        if c["body"] > 40:
            todo.append(c["entry"])
    todo.append("1404564b0")
    todo.append("14045bfd0")  # used by bf10
    todo = list(dict.fromkeys(todo))
    for hx in todo:
        f = getFunctionAt(toAddr(hx))
        if f is None:
            continue
        res = decomp.decompileFunction(f, 120, monitor)
        c = res.getDecompiledFunction().getC() if res and res.getDecompiledFunction() else "// FAIL\n"
        path = os.path.join(DECOMP, "Vision3D_anomparent_%s.c" % hx)
        with open(path, "w", encoding="utf-8") as out:
            out.write("// %s @ %s\n\n%s" % (f.getName(True), hx, c[:25000]))
        report["dumped"].append({"entry": hx, "name": f.getName(True), "body": f.getBody().getNumAddresses(), "decomp": path})
        log("dump %s" % hx)

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    log("WROTE %s" % OUT)
    decomp.dispose()

if __name__ == "__main__":
    main()
else:
    main()
