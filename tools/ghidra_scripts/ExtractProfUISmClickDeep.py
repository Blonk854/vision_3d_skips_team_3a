# Dump ProfUISm CExtReportGridWnd::OnGbwAnalyzeCellMouseClickEvent
#@category Vision3D
#@runtime PyGhidra

import json
import os
import traceback

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

OUT_DIR = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps"
LOG = os.path.join(OUT_DIR, "ProfUISm_click_log.txt")
OUT = os.path.join(OUT_DIR, "ProfUISm_click_deep.json")
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
        monitor = ConsoleTaskMonitor()
        decomp = DecompInterface()
        decomp.openProgram(program)
        log("program=%s funcs=%d" % (program.getName(), fm.getFunctionCount()))

        keys = (
            "OnGbwAnalyzeCellMouseClickEvent",
            "OnClickLeftBtnDoubleInnerCell",
            "OnClickLeftBtnUpInnerCell",
            "OnClickLeftBtnDownInnerCell",
            "CExtReportGridWnd",
        )
        hits = []
        it = fm.getFunctions(True)
        while it.hasNext():
            f = it.next()
            n = f.getName(True)
            if any(k in n for k in keys):
                hits.append(f)
        log("hits=%d" % len(hits))

        results = []
        for f in hits:
            entry = format(f.getEntryPoint().getOffset(), "x")
            body = f.getBody().getNumAddresses()
            name = f.getName(True)
            item = {"name": name, "entry": entry, "body": body}
            want = (
                "OnGbwAnalyzeCellMouseClickEvent" in name
                or "OnClickLeftBtn" in name
            )
            if want and body >= 8:
                res = decomp.decompileFunction(f, 120, monitor)
                c = res.getDecompiledFunction().getC() if res and res.getDecompiledFunction() else "// FAIL\n"
                path = os.path.join(DECOMP, "ProfUISm_click_%s.c" % entry)
                with open(path, "w", encoding="utf-8") as out:
                    out.write("// %s @ %s\n\n%s" % (name, entry, c[:25000]))
                item["decomp"] = path
                item["decomp_len"] = len(c)
                log("wrote %s len=%d" % (path, len(c)))
            results.append(item)

        with open(OUT, "w", encoding="utf-8") as fh:
            json.dump({"program": program.getName(), "hits": results}, fh, indent=2)
        log("WROTE %s" % OUT)
        decomp.dispose()
    except Exception:
        log(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
else:
    main()
