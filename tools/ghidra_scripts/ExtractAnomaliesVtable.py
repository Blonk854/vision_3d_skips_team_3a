# Dump CAnomaliesGridWnd vftable slots used by click path and decompile targets.
#@category Vision3D
#@runtime PyGhidra

import json
import os
import traceback

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

OUT_DIR = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps"
LOG = os.path.join(OUT_DIR, "Vision3D_anomalies_vt_log.txt")
OUT = os.path.join(OUT_DIR, "Vision3D_anomalies_vtable.json")
DECOMP = os.path.join(OUT_DIR, "decomp")

# Offsets from DyTools0 OnGbwAnalyzeCellMouseClickEvent / OnClickRightBtnUpInnerCell
SLOTS = {
    "hit_test_or_similar_0x538": 0x538,
    "OnClickLbtnUp_0x1250": 0x1250,
    "OnClickLbtnDown_0x1258": 0x1258,
    "OnClickLbtnDbl_0x1260": 0x1260,
    "OnClickRbtnUp_0x1268": 0x1268,
    "OnClickRbtnDown_0x1270": 0x1270,
    "OnClickRbtnDbl_0x1278": 0x1278,
    "OnClickMbtnUp_0x1280": 0x1280,
    "OnClickMbtnDown_0x1288": 0x1288,
    "OnClickMbtnDbl_0x1290": 0x1290,
    "context_0x1298": 0x1298,
    "hover_empty_0x12a8": 0x12a8,
    "OnGbwAnalyze_guess_scan": None,  # filled by scanning for distinctive
}


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
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(DECOMP, exist_ok=True)
    open(LOG, "w", encoding="utf-8").write("")
    try:
        program = currentProgram
        fm = program.getFunctionManager()
        st = program.getSymbolTable()
        mem = program.getMemory()
        rm = program.getReferenceManager()
        monitor = ConsoleTaskMonitor()
        decomp = DecompInterface()
        decomp.openProgram(program)
        log("program=%s" % program.getName())

        # Find vftable symbol(s)
        vtables = []
        for sym in st.getAllSymbols(True):
            n = sym.getName(True)
            if "CAnomaliesGridWnd" in n and "vftable" in n.lower():
                vtables.append((n, sym.getAddress()))
            elif n == "CAnomaliesGridWnd::vftable" or n.endswith("CAnomaliesGridWnd::`vftable'"):
                vtables.append((n, sym.getAddress()))
        # fallback: symbol iterator
        if not vtables:
            for sym in st.getSymbolIterator("CAnomaliesGridWnd", True):
                n = sym.getName(True)
                if "CAnomaliesGridWnd" not in n:
                    break
                vtables.append((n, sym.getAddress()))
                log("sym-fallback %s @ %s" % (n, sym.getAddress()))

        report = {"vtables": [], "slots": [], "dumped": []}
        for name, addr in vtables:
            report["vtables"].append({"name": name, "address": format(addr.getOffset(), "x")})
            log("vtable %s @ %s" % (name, addr))

        if not vtables:
            log("NO VTABLE FOUND")
            with open(OUT, "w", encoding="utf-8") as fh:
                json.dump(report, fh, indent=2)
            return

        # Use first vftable (primary)
        vt_name, vt_addr = vtables[0]
        # Also dump first ~0x1400/8 slots briefly for OnGbw-like bodies
        scan_hits = []
        for off in range(0, 0x1400, 8):
            try:
                pfn = u64(mem, vt_addr.add(off))
            except Exception:
                break
            if pfn < 0x140000000 or pfn > 0x142000000:
                continue
            f = getFunctionAt(toAddr("%x" % pfn))
            if f is None:
                continue
            body = f.getBody().getNumAddresses()
            n = f.getName(True)
            if body >= 40 or any(k in n for k in ("Click", "Gbw", "Mouse", "Anomal")):
                scan_hits.append({
                    "off": off,
                    "pfn": format(pfn, "x"),
                    "name": n,
                    "body": body,
                })
        report["scan_interesting"] = scan_hits
        log("scan_interesting=%d" % len(scan_hits))

        # Named slots
        for label, off in SLOTS.items():
            if off is None:
                continue
            try:
                pfn = u64(mem, vt_addr.add(off))
            except Exception as e:
                report["slots"].append({"label": label, "off": off, "error": str(e)})
                continue
            f = getFunctionAt(toAddr("%x" % pfn))
            if f is None:
                f = getFunctionContaining(toAddr("%x" % pfn))
            slot = {
                "label": label,
                "off": off,
                "pfn": format(pfn, "x"),
                "name": f.getName(True) if f else None,
                "body": f.getBody().getNumAddresses() if f else None,
            }
            report["slots"].append(slot)
            log("slot %s -> %s body=%s %s" % (label, slot["pfn"], slot["body"], slot["name"]))

        # Decompile: all named slots with body>=8 + top scan hits by body
        targets = {}
        for s in report["slots"]:
            if s.get("body") and s["body"] >= 8 and s.get("pfn"):
                targets[s["pfn"]] = s.get("name") or s["label"]
        for s in sorted(scan_hits, key=lambda x: -x["body"])[:25]:
            targets[s["pfn"]] = s["name"]

        for pfn, label in targets.items():
            f = getFunctionAt(toAddr(pfn))
            if f is None:
                continue
            res = decomp.decompileFunction(f, 120, monitor)
            c = res.getDecompiledFunction().getC() if res and res.getDecompiledFunction() else "// FAIL\n"
            path = os.path.join(DECOMP, "Vision3D_anomvt_%s.c" % pfn)
            with open(path, "w", encoding="utf-8") as out:
                out.write("// %s @ %s\n\n%s" % (label, pfn, c[:25000]))
            report["dumped"].append({
                "label": label,
                "pfn": pfn,
                "body": f.getBody().getNumAddresses(),
                "decomp": path,
                "decomp_len": len(c),
            })
            log("dump %s %s len=%d" % (pfn, label[:80], len(c)))

        # Also find callers of ctor FUN_140453090 / refs to vftable
        for vt in report["vtables"]:
            addr = toAddr(vt["address"])
            refs = []
            for r in rm.getReferencesTo(addr):
                fa = r.getFromAddress()
                f = fm.getFunctionContaining(fa)
                refs.append({
                    "from": format(fa.getOffset(), "x"),
                    "function": f.getName(True) if f else None,
                    "entry": format(f.getEntryPoint().getOffset(), "x") if f else None,
                    "body": f.getBody().getNumAddresses() if f else None,
                })
            vt["refs"] = refs
            log("vtable refs=%d" % len(refs))

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
