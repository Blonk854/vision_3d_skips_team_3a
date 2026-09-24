# Minimal dump of OnGbwAnalyzeCellMouseClickEvent from DyTools0.
# @category Vision3D
# @runtime PyGhidra

#@runtime PyGhidra

import json
import os
import traceback

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

OUT_DIR = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps"
LOG = os.path.join(OUT_DIR, "DyTools0_extract_log.txt")


def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    open(LOG, "w", encoding="utf-8").write("")
    try:
        program = currentProgram
        log("program=%s base=%s" % (program.getName(), program.getImageBase()))
        fm = program.getFunctionManager()
        log("functions=%d" % fm.getFunctionCount())

        decomp = DecompInterface()
        decomp.openProgram(program)
        monitor = ConsoleTaskMonitor()

        hits = []
        it = fm.getFunctions(True)
        while it.hasNext():
            f = it.next()
            name = f.getName(True)
            if "OnGbwAnalyzeCellMouseClickEvent" in name or name.endswith(
                "OnGbwAnalyzeCellMouseClickEvent"
            ):
                hits.append(f)
            elif "MouseClick" in name and "Gbw" in name:
                hits.append(f)

        log("click_hits=%d" % len(hits))
        results = []
        decomp_dir = os.path.join(OUT_DIR, "decomp")
        os.makedirs(decomp_dir, exist_ok=True)

        for f in hits:
            entry = str(f.getEntryPoint())
            safe = entry.replace(":", "")
            path = os.path.join(decomp_dir, "DyTools0_click_%s.c" % safe)
            res = decomp.decompileFunction(f, 120, monitor)
            c = (
                res.getDecompiledFunction().getC()
                if res and res.getDecompiledFunction()
                else "// FAILED\n"
            )
            with open(path, "w", encoding="utf-8") as out:
                out.write("// %s @ %s\n\n%s" % (f.getName(True), entry, c))
            log("wrote %s size=%d" % (path, len(c)))

            callees = []
            try:
                for cfn in f.getCalledFunctions(monitor):
                    callees.append(
                        {"name": cfn.getName(True), "entry": str(cfn.getEntryPoint())}
                    )
            except Exception as e:
                log("callees_err %s" % e)

            results.append(
                {
                    "name": f.getName(True),
                    "entry": entry,
                    "body": int(f.getBody().getNumAddresses()),
                    "callees": callees,
                    "decomp": path,
                }
            )

        # List CVitExtReportGridWnd methods quickly via symbol table
        vit = []
        sm = program.getSymbolTable()
        for sym in sm.getSymbolIterator("CVitExtReportGridWnd", True):
            name = sym.getName(True)
            if not name.startswith("CVitExtReportGridWnd"):
                # prefix iterator may continue into nearby names
                if "CVitExtReportGridWnd" not in name:
                    break
            vit.append({"name": name, "address": str(sym.getAddress())})
            if len(vit) >= 120:
                break
        log("vit_symbols=%d" % len(vit))

        payload = {
            "program": str(program.getName()),
            "image_base": str(program.getImageBase()),
            "functions": fm.getFunctionCount(),
            "click_handlers": results,
            "vit_symbols_sample": vit,
        }
        out_json = os.path.join(OUT_DIR, "DyTools0_click_extract.json")
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        log("WROTE " + out_json)
        decomp.dispose()
    except Exception:
        log(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
else:
    main()
