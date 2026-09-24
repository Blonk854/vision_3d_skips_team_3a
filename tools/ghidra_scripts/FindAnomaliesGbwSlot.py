# Find OnGbwAnalyzeCellMouseClickEvent slot on all CAnomaliesGridWnd vftables.
#@category Vision3D
#@runtime PyGhidra

import json
import os

OUT = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps\Vision3D_anomalies_gbw_slot.json"
LOG = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps\Vision3D_anomalies_gbw_slot_log.txt"
DECOMP = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps\decomp"

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor


def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)


def u64(mem, addr):
    v = mem.getLong(addr)
    if v < 0:
        v += 1 << 64
    return v


def main():
    open(LOG, "w", encoding="utf-8").write("")
    os.makedirs(DECOMP, exist_ok=True)
    program = currentProgram
    fm = program.getFunctionManager()
    st = program.getSymbolTable()
    mem = program.getMemory()
    decomp = DecompInterface()
    decomp.openProgram(program)
    monitor = ConsoleTaskMonitor()

    vts = []
    for sym in st.getAllSymbols(True):
        n = sym.getName(True)
        if n == "CAnomaliesGridWnd::vftable":
            vts.append(sym.getAddress())
    log("vtables=%s" % [format(a.getOffset(), "x") for a in vts])

    report = {"matches": [], "local_large": []}
    needles = ("OnGbwAnalyzeCellMouseClickEvent", "MouseClick", "AnalyzeCellMouse")
    for vt in vts:
        for off in range(0, 0x1800, 8):
            try:
                pfn = u64(mem, vt.add(off))
            except Exception:
                break
            if pfn < 0x140000000 or pfn > 0x150000000:
                continue
            f = getFunctionAt(toAddr("%x" % pfn))
            if f is None:
                continue
            n = f.getName(True)
            body = f.getBody().getNumAddresses()
            if any(k in n for k in needles):
                report["matches"].append({
                    "vt": format(vt.getOffset(), "x"),
                    "off": off,
                    "pfn": format(pfn, "x"),
                    "name": n,
                    "body": body,
                })
                log("MATCH vt=%s off=0x%x -> %s body=%d" % (vt, off, n, body))
            # Local Vision3D funcs (not IAT thunks of body 6)
            if body > 50 and pfn < 0x140800000:
                report["local_large"].append({
                    "vt": format(vt.getOffset(), "x"),
                    "off": off,
                    "pfn": format(pfn, "x"),
                    "name": n,
                    "body": body,
                })

    # unique local_large by pfn, decompile
    seen = set()
    for item in sorted(report["local_large"], key=lambda x: -x["body"]):
        if item["pfn"] in seen:
            continue
        seen.add(item["pfn"])
        f = getFunctionAt(toAddr(item["pfn"]))
        res = decomp.decompileFunction(f, 120, monitor)
        c = res.getDecompiledFunction().getC() if res and res.getDecompiledFunction() else "// FAIL\n"
        path = os.path.join(DECOMP, "Vision3D_anomlocal_%s.c" % item["pfn"])
        with open(path, "w", encoding="utf-8") as out:
            out.write("// vt off=0x%x %s @ %s\n\n%s" % (item["off"], item["name"], item["pfn"], c[:25000]))
        item["decomp"] = path
        log("local %s off=0x%x body=%d" % (item["pfn"], item["off"], item["body"]))
        if len(seen) >= 40:
            break

    # Also decompile any MATCH that is local
    for m in report["matches"]:
        if m["body"] <= 8:
            continue
        f = getFunctionAt(toAddr(m["pfn"]))
        res = decomp.decompileFunction(f, 120, monitor)
        c = res.getDecompiledFunction().getC() if res and res.getDecompiledFunction() else "// FAIL\n"
        path = os.path.join(DECOMP, "Vision3D_anomgbw_%s.c" % m["pfn"])
        with open(path, "w", encoding="utf-8") as out:
            out.write("// %s @ %s\n\n%s" % (m["name"], m["pfn"], c[:25000]))
        m["decomp"] = path

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    log("WROTE %s matches=%d locals=%d" % (OUT, len(report["matches"]), len(seen)))
    decomp.dispose()


if __name__ == "__main__":
    main()
else:
    main()
