# Dump AFX_MSGMAP for CVitExtReportGridWnd and follow entry pfn targets.
#@category Vision3D
#@runtime PyGhidra

import json
import os
import traceback

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

OUT_DIR = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps"
LOG = os.path.join(OUT_DIR, "DyTools0_afxmap_log.txt")
OUT = os.path.join(OUT_DIR, "DyTools0_afx_msgmap.json")
DECOMP = os.path.join(OUT_DIR, "decomp")

MSGMAP = 0x180262070  # from GetThisMessageMap


def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)


def u64(mem, addr):
    v = mem.getLong(addr)
    if v < 0:
        v += 1 << 64
    return v


def u32(mem, addr):
    return mem.getInt(addr) & 0xFFFFFFFF


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(DECOMP, exist_ok=True)
    open(LOG, "w", encoding="utf-8").write("")
    try:
        program = currentProgram
        fm = program.getFunctionManager()
        mem = program.getMemory()
        rm = program.getReferenceManager()
        monitor = ConsoleTaskMonitor()
        decomp = DecompInterface()
        decomp.openProgram(program)
        log("program=%s" % program.getName())

        base = toAddr("%x" % MSGMAP)
        parent_fn = u64(mem, base)           # pfnGetBaseMap
        entries = u64(mem, base.add(8))      # lpEntries
        log("msgmap parent_fn=%x entries=%x" % (parent_fn, entries))

        report = {
            "msgmap": format(MSGMAP, "x"),
            "parent_fn": format(parent_fn, "x"),
            "entries": format(entries, "x") if entries else None,
            "entries_list": [],
            "dat_xrefs": [],
        }

        # Walk AFX_MSGMAP_ENTRY until nMessage==0 sentinel.
        # Layout x64 MFC (common):
        #   UINT_PTR nMessage; // 8
        #   UINT nCode;        // 4
        #   UINT nID;          // 4
        #   UINT nLastID;      // 4
        #   UINT_PTR nSig;     // 8  (sometimes UINT 4 + pad)
        #   AFX_PMSG pfn;      // 8
        # Total often 0x20 or 0x28. Probe both.
        if entries:
            for stride in (0x20, 0x28, 0x18):
                cur = toAddr("%x" % entries)
                parsed = []
                for i in range(80):
                    try:
                        nMessage = u64(mem, cur)
                        nCode = u32(mem, cur.add(8))
                        nID = u32(mem, cur.add(12))
                        nLastID = u32(mem, cur.add(16))
                        if stride == 0x20:
                            nSig = u32(mem, cur.add(20))
                            pfn = u64(mem, cur.add(24))
                        elif stride == 0x28:
                            nSig = u64(mem, cur.add(20))
                            pfn = u64(mem, cur.add(0x20))
                        else:  # 0x18 tight guess
                            nSig = u32(mem, cur.add(16))
                            pfn = u64(mem, cur.add(0x10))
                    except Exception as e:
                        log("read_err stride=%x i=%d %s" % (stride, i, e))
                        break
                    if nMessage == 0 and pfn == 0:
                        break
                    f = getFunctionAt(toAddr("%x" % pfn)) if pfn else None
                    if f is None and pfn:
                        f = getFunctionContaining(toAddr("%x" % pfn))
                    entry = {
                        "i": i,
                        "addr": format(cur.getOffset(), "x"),
                        "nMessage": format(nMessage, "x"),
                        "nCode": nCode,
                        "nID": nID,
                        "nLastID": nLastID,
                        "nSig": nSig if stride != 0x28 else format(nSig, "x"),
                        "pfn": format(pfn, "x"),
                        "function": f.getName(True) if f else None,
                        "body": f.getBody().getNumAddresses() if f else None,
                    }
                    parsed.append(entry)
                    cur = cur.add(stride)
                report["entries_list"].append({"stride": stride, "count": len(parsed), "entries": parsed})
                log("stride=0x%x parsed=%d" % (stride, len(parsed)))

        # Prefer stride with most named functions
        best = None
        for block in report["entries_list"]:
            named = sum(1 for e in block["entries"] if e.get("function"))
            if best is None or named > best[0]:
                best = (named, block)
        if best and best[1]["entries"]:
            for e in best[1]["entries"]:
                if not e.get("function"):
                    continue
                # Decompile interesting handlers (registered msg often nMessage high / pointer)
                nmsg = int(e["nMessage"], 16)
                interesting = (
                    nmsg >= 0x180000000  # pointer to registered UINT
                    or nmsg >= 0xC000     # registered message range / WM_APP
                    or (e.get("body") or 0) > 30
                )
                if not interesting:
                    continue
                f = getFunctionAt(toAddr(e["pfn"]))
                if f is None:
                    continue
                res = decomp.decompileFunction(f, 90, monitor)
                c = res.getDecompiledFunction().getC() if res and res.getDecompiledFunction() else "// FAIL\n"
                path = os.path.join(DECOMP, "DyTools0_afxhandler_%s.c" % e["pfn"])
                with open(path, "w", encoding="utf-8") as out:
                    out.write("// msgmap nMessage=%s pfn=%s %s\n\n%s" % (
                        e["nMessage"], e["pfn"], e["function"], c))
                e["decomp"] = path
                log("handler %s %s" % (e["pfn"], e["function"]))

        # DAT xrefs for click message IDs (known from msg_init)
        for dat_hex in (
            "18026ddf0", "18026ddec", "18026dde8",
            "18026ddf4", "18026ddf8", "18026ddfc",
            "18026de00", "18026de04", "18026de08",
        ):
            addr = toAddr(dat_hex)
            xrefs = []
            for r in rm.getReferencesTo(addr):
                fa = r.getFromAddress()
                f = fm.getFunctionContaining(fa)
                xrefs.append({
                    "from": format(fa.getOffset(), "x"),
                    "type": str(r.getReferenceType()),
                    "function": f.getName(True) if f else None,
                    "entry": format(f.getEntryPoint().getOffset(), "x") if f else None,
                    "body": f.getBody().getNumAddresses() if f else None,
                })
            report["dat_xrefs"].append({"dat": dat_hex, "xrefs": xrefs})
            log("dat %s xrefs=%d" % (dat_hex, len(xrefs)))

        # Also dump qword contents at msgmap for raw visibility
        report["msgmap_raw"] = [format(u64(mem, base.add(i)), "x") for i in range(0, 0x20, 8)]

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
