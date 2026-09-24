# Find MFC ON_REGISTERED_MESSAGE consumers of ID_VITREPORTGRID_CLICK_*
# by resolving RegisterWindowMessage DAT targets, then scanning for
# absolute pointers to those DATs (message-map entries).
#@category Vision3D
#@runtime PyGhidra

import json
import os

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

OUT_DIR = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps"
DECOMP_DIR = os.path.join(OUT_DIR, "decomp")
OUT_JSON = os.path.join(OUT_DIR, "Vision3D_vitgrid_msgmap_handlers.json")

TARGETS = [
    "ID_VITREPORTGRID_CLICK_LBTNDBL_INNER",
    "ID_VITREPORTGRID_CLICK_LBTNDWN_INNER",
    "ID_VITREPORTGRID_CLICK_LBTNUP_INNER",
]

LABELS = {
    "ID_VITREPORTGRID_CLICK_LBTNDBL_INNER": "LBTNDBL",
    "ID_VITREPORTGRID_CLICK_LBTNDWN_INNER": "LBTNDWN",
    "ID_VITREPORTGRID_CLICK_LBTNUP_INNER": "LBTNUP",
}


def to_hex(addr):
    if addr is None:
        return None
    return format(addr.getOffset(), "x")


def find_string_addrs(program, text, monitor):
    hits = []
    listing = program.getListing()
    mem = program.getMemory()
    for ds in listing.getDefinedData(True):
        try:
            if ds.hasStringValue() and str(ds.getValue()) == text:
                hits.append(ds.getAddress())
        except Exception:
            pass
    if hits:
        return hits
    raw = (text + "\x00").encode("ascii")
    start = mem.getMinAddress()
    while True:
        found = mem.findBytes(start, raw, None, True, monitor)
        if found is None:
            break
        hits.append(found)
        start = found.add(1)
        if len(hits) > 20:
            break
    return hits


def dat_from_init(program, func):
    """Return DAT address written by RegisterWindowMessage in a tiny init."""
    if func is None:
        return None
    listing = program.getListing()
    rm = program.getReferenceManager()
    body = func.getBody()
    for cu in listing.getInstructions(body, True):
        for i in range(cu.getNumOperands()):
            for r in cu.getOperandReferences(i):
                if r.getReferenceType().isWrite() and r.isMemoryReference():
                    to = r.getToAddress()
                    if to.getOffset() >= 0x141000000:
                        return to
    for addr in body.getAddresses(True):
        for r in rm.getReferencesFrom(addr):
            if r.getReferenceType().isWrite() and r.isMemoryReference():
                to = r.getToAddress()
                if to.getOffset() >= 0x141000000:
                    return to
    return None


def find_pointer_hits(program, target_addr, monitor):
    """Scan memory for little-endian 8-byte absolute pointer to target."""
    mem = program.getMemory()
    off = target_addr.getOffset()
    needle = bytes([(off >> (8 * i)) & 0xFF for i in range(8)])
    hits = []
    for block in mem.getBlocks():
        if not block.isInitialized():
            continue
        start = block.getStart()
        end = block.getEnd()
        cur = start
        while cur.compareTo(end) <= 0:
            found = mem.findBytes(cur, end, needle, None, True, monitor)
            if found is None:
                break
            hits.append(found)
            try:
                cur = found.add(1)
            except Exception:
                break
            if len(hits) > 100:
                break
    return hits


def decompile_func(ifc, func, monitor, limit=12000):
    if func is None:
        return None
    res = ifc.decompileFunction(func, 60, monitor)
    if res is None or not res.decompileCompleted():
        return None
    text = res.getDecompiledFunction().getC()
    if text is None:
        return None
    if len(text) > limit:
        return text[:limit] + "\n/* truncated */\n"
    return text


def main():
    program = currentProgram
    fm = program.getFunctionManager()
    rm = program.getReferenceManager()
    mem = program.getMemory()
    monitor = ConsoleTaskMonitor()

    ifc = DecompInterface()
    ifc.openProgram(program)
    os.makedirs(DECOMP_DIR, exist_ok=True)

    report = {"program": program.getName(), "targets": []}

    for text in TARGETS:
        label = LABELS[text]
        entry = {"label": label, "string": text, "inits": [], "dats": [], "msgmap_hits": []}
        dat_set = {}
        for sa in find_string_addrs(program, text, monitor):
            for r in rm.getReferencesTo(sa):
                from_addr = r.getFromAddress()
                func = fm.getFunctionContaining(from_addr)
                if func is None:
                    continue
                dat = dat_from_init(program, func)
                entry["inits"].append({
                    "init": to_hex(func.getEntryPoint()),
                    "name": func.getName(),
                    "string_at": to_hex(sa),
                    "dat": to_hex(dat) if dat else None,
                    "body": func.getBody().getNumAddresses(),
                })
                if dat is not None:
                    dat_set[to_hex(dat)] = dat

        seen = set()
        uniq = []
        for i in entry["inits"]:
            if i["init"] in seen:
                continue
            seen.add(i["init"])
            uniq.append(i)
        entry["inits"] = uniq
        entry["dats"] = sorted(dat_set.keys())

        for dat_hex, dat_addr in sorted(dat_set.items()):
            ptr_hits = find_pointer_hits(program, dat_addr, monitor)
            code_xrefs = []
            for r in rm.getReferencesTo(dat_addr):
                fa = r.getFromAddress()
                f = fm.getFunctionContaining(fa)
                code_xrefs.append({
                    "from": to_hex(fa),
                    "type": str(r.getReferenceType()),
                    "function": f.getName() if f else None,
                    "entry": to_hex(f.getEntryPoint()) if f else None,
                    "body": f.getBody().getNumAddresses() if f else None,
                })

            for hit in ptr_hits:
                candidates = []
                for off in (0x10, 0x18, 0x20, 0x28, 0x08):
                    try:
                        pfn_addr = hit.add(off)
                        val = mem.getLong(pfn_addr)
                        if val < 0:
                            val = val + (1 << 64)
                        target = toAddr(val)
                        f = fm.getFunctionAt(target)
                        if f is None:
                            f = fm.getFunctionContaining(target)
                        if f is not None:
                            candidates.append({
                                "pfn_offset": off,
                                "pfn": format(val, "x"),
                                "function": f.getName(),
                                "entry": to_hex(f.getEntryPoint()),
                                "body": f.getBody().getNumAddresses(),
                            })
                    except Exception as e:
                        candidates.append({"pfn_offset": off, "error": str(e)})

                hit_info = {
                    "dat": dat_hex,
                    "map_entry": to_hex(hit),
                    "code_xrefs": code_xrefs,
                    "pfn_candidates": candidates,
                }

                best = None
                for c in candidates:
                    if "entry" not in c:
                        continue
                    if best is None or (c.get("body") or 0) > (best.get("body") or 0):
                        best = c
                if best is not None:
                    f = fm.getFunctionAt(toAddr(int(best["entry"], 16)))
                    if f is None:
                        f = fm.getFunctionContaining(toAddr(int(best["entry"], 16)))
                    text_c = decompile_func(ifc, f, monitor)
                    if text_c:
                        outp = os.path.join(
                            DECOMP_DIR,
                            "Vision3D_msgmap_%s_%s.c" % (label, best["entry"]),
                        )
                        with open(outp, "w", encoding="utf-8") as fh:
                            fh.write(
                                "// %s msgmap handler of DAT_%s @ %s (map @ %s)\n\n"
                                % (label, dat_hex, best["entry"], to_hex(hit))
                            )
                            fh.write(text_c)
                        hit_info["decomp_path"] = outp
                        hit_info["decomp_function"] = best

                entry["msgmap_hits"].append(hit_info)

            readers = [x for x in code_xrefs if x.get("body") and x["body"] > 40]
            readers.sort(key=lambda x: -(x["body"] or 0))
            for x in readers[:3]:
                f = fm.getFunctionAt(toAddr(int(x["entry"], 16)))
                text_c = decompile_func(ifc, f, monitor)
                if text_c:
                    outp = os.path.join(
                        DECOMP_DIR,
                        "Vision3D_datread_%s_%s.c" % (label, x["entry"]),
                    )
                    with open(outp, "w", encoding="utf-8") as fh:
                        fh.write("// %s DAT reader @ %s\n\n" % (label, x["entry"]))
                        fh.write(text_c)

        report["targets"].append(entry)

    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    print("Wrote", OUT_JSON)
    for t in report["targets"]:
        print(t["label"], "dats=", t["dats"], "msgmap_hits=", len(t["msgmap_hits"]))


if __name__ == "__main__":
    main()
