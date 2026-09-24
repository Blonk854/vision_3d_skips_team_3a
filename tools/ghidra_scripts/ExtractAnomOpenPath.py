# Decompile CAnomaliesGridWnd image-open helpers around FUN_14045c740.
#@category Vision3D
#@runtime PyGhidra

import json
import os
import traceback

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

OUT_DIR = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps"
LOG = os.path.join(OUT_DIR, "Vision3D_anom_open_log.txt")
OUT = os.path.join(OUT_DIR, "Vision3D_anom_open_path.json")
DECOMP = os.path.join(OUT_DIR, "decomp")

TARGETS = [
    "14045c740",  # open handler
    "14045bf10",  # get CAnomalieProd from grid
    "14045bf90",
    "1405f4730",  # open by name?
    "1405f9270",  # open alt path (bit 0x2000000)
    "1405ddc30",
    "14045c8e0",  # context menu
]


def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)


def main():
    os.makedirs(DECOMP, exist_ok=True)
    open(LOG, "w", encoding="utf-8").write("")
    try:
        program = currentProgram
        fm = program.getFunctionManager()
        rm = program.getReferenceManager()
        decomp = DecompInterface()
        decomp.openProgram(program)
        monitor = ConsoleTaskMonitor()
        report = {"targets": [], "callers_of_open": []}

        for hx in TARGETS:
            f = getFunctionAt(toAddr(hx))
            if f is None:
                log("MISSING %s" % hx)
                continue
            res = decomp.decompileFunction(f, 120, monitor)
            c = res.getDecompiledFunction().getC() if res and res.getDecompiledFunction() else "// FAIL\n"
            path = os.path.join(DECOMP, "Vision3D_anomopen_%s.c" % hx)
            with open(path, "w", encoding="utf-8") as out:
                out.write("// %s @ %s body=%d\n\n%s" % (f.getName(True), hx, f.getBody().getNumAddresses(), c[:30000]))
            item = {
                "entry": hx,
                "name": f.getName(True),
                "body": f.getBody().getNumAddresses(),
                "decomp": path,
            }
            # callers
            callers = []
            for r in rm.getReferencesTo(f.getEntryPoint()):
                if not r.getReferenceType().isCall() and not r.getReferenceType().isData():
                    # keep all
                    pass
                fa = r.getFromAddress()
                ff = fm.getFunctionContaining(fa)
                callers.append({
                    "from": format(fa.getOffset(), "x"),
                    "type": str(r.getReferenceType()),
                    "function": ff.getName(True) if ff else None,
                    "entry": format(ff.getEntryPoint().getOffset(), "x") if ff else None,
                    "body": ff.getBody().getNumAddresses() if ff else None,
                })
            item["xrefs"] = callers
            report["targets"].append(item)
            log("dump %s xrefs=%d" % (hx, len(callers)))

        # Focus callers of open handler
        open_f = getFunctionAt(toAddr("14045c740"))
        if open_f:
            for r in rm.getReferencesTo(open_f.getEntryPoint()):
                fa = r.getFromAddress()
                ff = fm.getFunctionContaining(fa)
                if ff is None:
                    continue
                entry = format(ff.getEntryPoint().getOffset(), "x")
                if entry == "14045c740":
                    continue
                res = decomp.decompileFunction(ff, 120, monitor)
                c = res.getDecompiledFunction().getC() if res and res.getDecompiledFunction() else "// FAIL\n"
                path = os.path.join(DECOMP, "Vision3D_anomcaller_%s.c" % entry)
                with open(path, "w", encoding="utf-8") as out:
                    out.write("// caller of open-handler from %s\n\n%s" % (entry, c[:25000]))
                report["callers_of_open"].append({
                    "entry": entry,
                    "name": ff.getName(True),
                    "body": ff.getBody().getNumAddresses(),
                    "decomp": path,
                })
                log("caller %s %s" % (entry, ff.getName(True)[:80]))

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
