# Lightweight: for one LBTNDBL DAT, dump xrefs + quick qword search in .rdata/.data only.
#@category Vision3D
#@runtime PyGhidra

import json
import os

OUT = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps\Vision3D_lbtndbl_one.json"

DAT = "141158ab4"


def main():
    program = currentProgram
    fm = program.getFunctionManager()
    rm = program.getReferenceManager()
    mem = program.getMemory()
    monitor = getMonitor() if False else None
    from ghidra.util.task import ConsoleTaskMonitor
    monitor = ConsoleTaskMonitor()

    addr = toAddr(int(DAT, 16))
    row = {
        "program": program.getName(),
        "dat": DAT,
        "image_base": format(program.getImageBase().getOffset(), "x"),
        "xrefs": [],
        "blocks": [],
        "qword_hits": [],
    }

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

    off = int(DAT, 16)
    needle = bytes([(off >> (8 * i)) & 0xFF for i in range(8)])
    for block in mem.getBlocks():
        row["blocks"].append({
            "name": block.getName(),
            "start": format(block.getStart().getOffset(), "x"),
            "size": block.getSize(),
            "init": block.isInitialized(),
        })
        name = block.getName().lower()
        if not block.isInitialized():
            continue
        if name not in (".rdata", ".data", ".text", "rdata", "data"):
            # still scan common data blocks by name containing data/rdata
            if "data" not in name and "rdata" not in name:
                continue
        cur = block.getStart()
        end = block.getEnd()
        while cur.compareTo(end) <= 0:
            found = mem.findBytes(cur, end, needle, None, True, monitor)
            if found is None:
                break
            if found.getOffset() != addr.getOffset():
                row["qword_hits"].append(format(found.getOffset(), "x"))
            try:
                cur = found.add(1)
            except Exception:
                break
            if len(row["qword_hits"]) > 50:
                break

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(row, fh, indent=2)
    print("WROTE", OUT, "xrefs", len(row["xrefs"]), "hits", len(row["qword_hits"]))


if __name__ == "__main__":
    main()
else:
    main()
