# Dump CVitExtReportGridWnd message map + ID_VITREPORTGRID consumers in DyTools0.
#@category Vision3D
#@runtime PyGhidra

import json
import os
import traceback

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

OUT_DIR = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps"
LOG = os.path.join(OUT_DIR, "DyTools0_msgmap_log.txt")
OUT = os.path.join(OUT_DIR, "DyTools0_reportgrid_msgmap.json")
DECOMP = os.path.join(OUT_DIR, "decomp")


def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)


def decompile(decomp, f, monitor, path, header):
    res = decomp.decompileFunction(f, 90, monitor)
    c = res.getDecompiledFunction().getC() if res and res.getDecompiledFunction() else "// FAILED\n"
    with open(path, "w", encoding="utf-8") as out:
        out.write(header + "\n\n" + c)
    return len(c)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(DECOMP, exist_ok=True)
    open(LOG, "w", encoding="utf-8").write("")
    try:
        program = currentProgram
        fm = program.getFunctionManager()
        rm = program.getReferenceManager()
        listing = program.getListing()
        mem = program.getMemory()
        monitor = ConsoleTaskMonitor()
        decomp = DecompInterface()
        decomp.openProgram(program)
        log("program=%s" % program.getName())

        report = {"program": program.getName(), "msgmap_funcs": [], "strings": [], "dat_xrefs": []}

        # Decompile GetThisMessageMap / GetMessageMap
        for fname in ("GetThisMessageMap", "GetMessageMap"):
            for f in fm.getFunctions(True):
                n = f.getName(True)
                if "CVitExtReportGridWnd" in n and fname in n:
                    entry = format(f.getEntryPoint().getOffset(), "x")
                    path = os.path.join(DECOMP, "DyTools0_msgmap_%s_%s.c" % (fname, entry))
                    ln = decompile(decomp, f, monitor, path, "// %s @ %s" % (n, entry))
                    report["msgmap_funcs"].append({"name": n, "entry": entry, "body": f.getBody().getNumAddresses(), "decomp": path, "len": ln})
                    log("msgmap %s %s len=%d" % (fname, entry, ln))

        # Find ID_VITREPORTGRID strings and follow refs
        needles = [
            "ID_VITREPORTGRID_CLICK_LBTNDBL_INNER",
            "ID_VITREPORTGRID_CLICK_LBTNDWN_INNER",
            "ID_VITREPORTGRID_CLICK_LBTNUP_INNER",
            "ID_VITREPORTGRID_CLICK",
        ]
        for ds in listing.getDefinedData(True):
            try:
                if not ds.hasStringValue():
                    continue
                s = str(ds.getValue())
            except Exception:
                continue
            if "VITREPORTGRID" not in s and "VitReport" not in s:
                continue
            sa = ds.getAddress()
            refs = []
            for r in rm.getReferencesTo(sa):
                fa = r.getFromAddress()
                f = fm.getFunctionContaining(fa)
                refs.append({
                    "from": format(fa.getOffset(), "x"),
                    "function": f.getName(True) if f else None,
                    "entry": format(f.getEntryPoint().getOffset(), "x") if f else None,
                    "body": f.getBody().getNumAddresses() if f else None,
                })
            report["strings"].append({"string": s, "address": format(sa.getOffset(), "x"), "refs": refs})
            log("str %s refs=%d" % (s[:60], len(refs)))

            # For each tiny init, find DAT write and then READ xrefs
            for ref in refs:
                if not ref.get("entry"):
                    continue
                f = getFunctionAt(toAddr(int(ref["entry"], 16)))
                if f is None or f.getBody().getNumAddresses() > 40:
                    continue
                dats = []
                for addr in f.getBody().getAddresses(True):
                    for rr in rm.getReferencesFrom(addr):
                        if rr.getReferenceType().isWrite() and rr.isMemoryReference():
                            to = rr.getToAddress()
                            if to.getOffset() >= 0x180000000:
                                dats.append(to)
                for dat in dats:
                    dx = []
                    for rr in rm.getReferencesTo(dat):
                        fa = rr.getFromAddress()
                        ff = fm.getFunctionContaining(fa)
                        dx.append({
                            "from": format(fa.getOffset(), "x"),
                            "type": str(rr.getReferenceType()),
                            "function": ff.getName(True) if ff else None,
                            "entry": format(ff.getEntryPoint().getOffset(), "x") if ff else None,
                            "body": ff.getBody().getNumAddresses() if ff else None,
                        })
                    row = {
                        "string": s,
                        "init": ref["entry"],
                        "dat": format(dat.getOffset(), "x"),
                        "xrefs": dx,
                    }
                    report["dat_xrefs"].append(row)
                    log("dat %s xrefs=%d" % (row["dat"], len(dx)))
                    # decompile large readers
                    for x in dx:
                        if x.get("body") and x["body"] > 40 and x.get("entry"):
                            ff = getFunctionAt(toAddr(int(x["entry"], 16)))
                            if ff is None:
                                continue
                            path = os.path.join(DECOMP, "DyTools0_datread_%s.c" % x["entry"])
                            ln = decompile(decomp, ff, monitor, path, "// reader of %s via %s" % (row["dat"], s[:40]))
                            x["decomp"] = path
                            log("reader %s len=%d" % (x["entry"], ln))

        # Also dump OnClickLeftBtnDoubleInnerCell even if tiny
        for f in fm.getFunctions(True):
            n = f.getName(True)
            if n.endswith("OnClickLeftBtnDoubleInnerCell") or "OnClickLeftBtnDoubleInnerCell@" in n:
                entry = format(f.getEntryPoint().getOffset(), "x")
                path = os.path.join(DECOMP, "DyTools0_onclick_%s.c" % entry)
                decompile(decomp, f, monitor, path, "// %s @ %s" % (n, entry))
                log("dbl %s" % entry)

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
