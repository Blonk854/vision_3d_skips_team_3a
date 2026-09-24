# Dig deeper: truncated UINT msgmap ptrs + code xrefs to all VITREPORTGRID DATs.
# Also dump any function that READs those DATs.
#@category Vision3D
#@runtime PyGhidra

import json
import os

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

OUT = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps\Vision3D_vitgrid_msgmap_deep.json"
DECOMP_DIR = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps\decomp"

# From prior scan
DATS = {
    "LBTNDBL": [
        "1410e2968", "1410f7ec0", "1410fad60", "1411096e8", "14111c954",
        "141126768", "141126db8", "14114f8b8", "141152824", "141158ab4",
        "141172884", "1411a82fc",
    ],
}


def u64(mem, addr):
    v = mem.getLong(addr)
    if v < 0:
        v += 1 << 64
    return v


def main():
    program = currentProgram
    fm = program.getFunctionManager()
    rm = program.getReferenceManager()
    mem = program.getMemory()
    monitor = ConsoleTaskMonitor()
    ifc = DecompInterface()
    ifc.openProgram(program)
    os.makedirs(DECOMP_DIR, exist_ok=True)

    report = {"program": program.getName(), "dats": []}

    for label, addrs in DATS.items():
        for hx in addrs:
            addr = toAddr(int(hx, 16))
            row = {"label": label, "dat": hx, "xrefs": [], "dword_ptr_hits": [], "qword_ptr_hits": 0}

            for r in rm.getReferencesTo(addr):
                fa = r.getFromAddress()
                f = fm.getFunctionContaining(fa)
                row["xrefs"].append({
                    "from": format(fa.getOffset(), "x"),
                    "type": str(r.getReferenceType()),
                    "function": f.getName() if f else None,
                    "entry": format(f.getEntryPoint().getOffset(), "x") if f else None,
                    "body": f.getBody().getNumAddresses() if f else None,
                })

            # qword absolute
            qneedle = bytes([((int(hx, 16)) >> (8 * i)) & 0xFF for i in range(8)])
            # dword truncated (low 32 of VA) — rare but check
            dneedle = bytes([((int(hx, 16)) >> (8 * i)) & 0xFF for i in range(4)])
            # image-relative: VA - image base
            base = program.getImageBase().getOffset()
            rva = int(hx, 16) - base
            rvan = bytes([(rva >> (8 * i)) & 0xFF for i in range(4)])
            rvan8 = bytes([(rva >> (8 * i)) & 0xFF for i in range(8)])

            for name, needle in (("qword", qneedle), ("dword_va", dneedle), ("rva4", rvan), ("rva8", rvan8)):
                hits = []
                for block in mem.getBlocks():
                    if not block.isInitialized():
                        continue
                    cur = block.getStart()
                    end = block.getEnd()
                    while cur.compareTo(end) <= 0:
                        found = mem.findBytes(cur, end, needle, None, True, monitor)
                        if found is None:
                            break
                        # skip the DAT itself
                        if found.getOffset() != addr.getOffset():
                            hits.append(format(found.getOffset(), "x"))
                        try:
                            cur = found.add(1)
                        except Exception:
                            break
                        if len(hits) > 30:
                            break
                    if len(hits) > 30:
                        break
                row["%s_hits" % name] = hits
                if name == "qword":
                    row["qword_ptr_hits"] = len(hits)

            # If any interesting hits, try to resolve nearby pfn and decompile
            interest = row.get("qword_hits", []) + row.get("dword_va_hits", [])[:5] + row.get("rva8_hits", [])[:5]
            for hit_s in interest[:10]:
                hit = toAddr(int(hit_s, 16))
                cands = []
                for off in (0x08, 0x10, 0x14, 0x18, 0x1c, 0x20, 0x28):
                    try:
                        val = u64(mem, hit.add(off))
                        f = fm.getFunctionAt(toAddr(val))
                        if f is None:
                            f = fm.getFunctionContaining(toAddr(val))
                        if f is not None and f.getBody().getNumAddresses() > 20:
                            cands.append({
                                "off": off,
                                "pfn": format(val, "x"),
                                "fn": f.getName(),
                                "entry": format(f.getEntryPoint().getOffset(), "x"),
                                "body": f.getBody().getNumAddresses(),
                            })
                    except Exception:
                        pass
                if cands:
                    best = max(cands, key=lambda c: c["body"])
                    f = getFunctionAt(toAddr(int(best["entry"], 16)))
                    res = ifc.decompileFunction(f, 60, monitor)
                    if res and res.decompileCompleted():
                        text = res.getDecompiledFunction().getC()
                        outp = os.path.join(DECOMP_DIR, "Vision3D_deep_%s_%s.c" % (label, best["entry"]))
                        with open(outp, "w", encoding="utf-8") as fh:
                            fh.write("// deep hit map@%s dat=%s best=%s\n\n" % (hit_s, hx, best["entry"]))
                            fh.write(text[:15000])
                        best["decomp"] = outp
                    row.setdefault("resolved", []).append({"hit": hit_s, "best": best, "cands": cands})

            # Decompile any non-tiny xref functions
            for x in row["xrefs"]:
                if x.get("body") and x["body"] > 40 and x.get("entry"):
                    f = getFunctionAt(toAddr(int(x["entry"], 16)))
                    if f is None:
                        continue
                    res = ifc.decompileFunction(f, 60, monitor)
                    if res and res.decompileCompleted():
                        text = res.getDecompiledFunction().getC()
                        outp = os.path.join(DECOMP_DIR, "Vision3D_xref_%s_%s.c" % (label, x["entry"]))
                        with open(outp, "w", encoding="utf-8") as fh:
                            fh.write("// xref reader dat=%s from %s\n\n" % (hx, x["from"]))
                            fh.write(text[:15000])
                        x["decomp"] = outp

            report["dats"].append(row)

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    print("Wrote", OUT)
    for row in report["dats"]:
        print(row["dat"], "xrefs", len(row["xrefs"]),
              "q", len(row.get("qword_hits", [])),
              "d", len(row.get("dword_va_hits", [])),
              "r4", len(row.get("rva4_hits", [])),
              "r8", len(row.get("rva8_hits", [])),
              "resolved", len(row.get("resolved", [])))


if __name__ == "__main__":
    main()
else:
    main()
