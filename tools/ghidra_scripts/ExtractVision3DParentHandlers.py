# Find Vision3D message-map / WindowProc consumers via dynamic initializer
# proximity and ON_REGISTERED_MESSAGE patterns near VITREPORTGRID inits.
# Also search for demangled handler names containing VitReport / ReportGrid / OIS open.
#@category Vision3D
#@runtime PyGhidra

import json
import os
import traceback

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

OUT_DIR = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps"
LOG = os.path.join(OUT_DIR, "Vision3D_parent_handlers_log.txt")
OUT = os.path.join(OUT_DIR, "Vision3D_parent_handlers.json")
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
        listing = program.getListing()
        monitor = ConsoleTaskMonitor()
        decomp = DecompInterface()
        decomp.openProgram(program)
        log("program=%s" % program.getName())

        report = {"program": program.getName(), "symbol_hits": [], "nearby_large": [], "dumped": []}

        # Symbol name search
        keys = (
            "VitReport", "VITREPORT", "ReportGrid", "ExtReportGrid",
            "OnClick", "OpenOIS", "ShowOIS", "LoadOIS", "OpenImage",
            "ShowImage", "FailureMode", "OnGbw",
        )
        it = fm.getFunctions(True)
        while it.hasNext():
            f = it.next()
            n = f.getName(True)
            if any(k.lower() in n.lower() for k in keys):
                body = f.getBody().getNumAddresses()
                entry = format(f.getEntryPoint().getOffset(), "x")
                report["symbol_hits"].append({"name": n, "entry": entry, "body": body})

        log("symbol_hits=%d" % len(report["symbol_hits"]))

        # For each LBTNDBL init, find large functions within +/- 0x2000 that might be handlers
        inits = []
        for ds in listing.getDefinedData(True):
            try:
                if not ds.hasStringValue():
                    continue
                s = str(ds.getValue())
            except Exception:
                continue
            if s != "ID_VITREPORTGRID_CLICK_LBTNDBL_INNER":
                continue
            for r in rm.getReferencesTo(ds.getAddress()):
                f = fm.getFunctionContaining(r.getFromAddress())
                if f and f.getBody().getNumAddresses() <= 40:
                    inits.append(f.getEntryPoint().getOffset())

        inits = sorted(set(inits))
        log("inits=%s" % [format(x, "x") for x in inits])

        for init_off in inits:
            nearby = []
            start = toAddr("%x" % max(0, init_off - 0x4000))
            end = toAddr("%x" % (init_off + 0x4000))
            funcs = fm.getFunctions(start, True)
            while funcs.hasNext():
                f = funcs.next()
                ep = f.getEntryPoint().getOffset()
                if ep > init_off + 0x4000:
                    break
                body = f.getBody().getNumAddresses()
                if body < 80:
                    continue
                nearby.append({
                    "entry": format(ep, "x"),
                    "name": f.getName(True),
                    "body": body,
                    "delta": ep - init_off,
                })
            nearby.sort(key=lambda x: abs(x["delta"]))
            report["nearby_large"].append({
                "init": format(init_off, "x"),
                "nearby": nearby[:12],
            })
            log("init %x nearby %d" % (init_off, len(nearby)))

            # Decompile top 3 nearest large funcs
            for item in nearby[:3]:
                f = getFunctionAt(toAddr(item["entry"]))
                if f is None:
                    continue
                res = decomp.decompileFunction(f, 90, monitor)
                c = res.getDecompiledFunction().getC() if res and res.getDecompiledFunction() else "// FAIL\n"
                # Only keep if mentions message / wParam / image / OIS / column-ish
                interesting = any(
                    k in c for k in (
                        "wParam", "lParam", "PostMessage", "RegisterWindow",
                        "OIS", "Image", "column", "Column", "row", "Row",
                        "defect", "Defect", "Missing", "Presence", "Text",
                    )
                )
                path = os.path.join(DECOMP, "Vision3D_nearinit_%s_%s.c" % (
                    format(init_off, "x"), item["entry"]))
                with open(path, "w", encoding="utf-8") as out:
                    out.write("// near init %x : %s body=%d interesting=%s\n\n%s" % (
                        init_off, item["name"], item["body"], interesting, c[:20000]))
                dumped = dict(item)
                dumped["init"] = format(init_off, "x")
                dumped["decomp"] = path
                dumped["interesting"] = interesting
                report["dumped"].append(dumped)
                log("dump %s interesting=%s" % (item["entry"], interesting))

        # Also decompile largest symbol_hits related to ReportGrid / VitReport / OIS
        for h in sorted(report["symbol_hits"], key=lambda x: -x["body"])[:20]:
            if h["body"] < 50:
                continue
            if not any(k in h["name"] for k in ("Report", "Vit", "OIS", "Image", "Click", "Gbw")):
                continue
            f = getFunctionAt(toAddr(h["entry"]))
            if f is None:
                continue
            res = decomp.decompileFunction(f, 90, monitor)
            c = res.getDecompiledFunction().getC() if res and res.getDecompiledFunction() else "// FAIL\n"
            path = os.path.join(DECOMP, "Vision3D_sym_%s.c" % h["entry"])
            with open(path, "w", encoding="utf-8") as out:
                out.write("// %s @ %s\n\n%s" % (h["name"], h["entry"], c[:20000]))
            report["dumped"].append({"kind": "symbol", **h, "decomp": path})
            log("symdump %s %s" % (h["entry"], h["name"][:80]))

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
