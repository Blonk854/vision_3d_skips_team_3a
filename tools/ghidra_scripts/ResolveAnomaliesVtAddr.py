# Resolve CAnomaliesGridWnd::vftable address from ctor FUN_140453090 data refs.
#@category Vision3D
#@runtime PyGhidra

import json
import os
import traceback

OUT = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps\Vision3D_anomalies_vtaddr.json"
LOG = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps\Vision3D_anomalies_vtaddr_log.txt"


def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)


def main():
    open(LOG, "w", encoding="utf-8").write("")
    program = currentProgram
    fm = program.getFunctionManager()
    rm = program.getReferenceManager()
    listing = program.getListing()
    st = program.getSymbolTable()

    f = getFunctionAt(toAddr("140453090"))
    log("ctor=%s" % f)
    refs = []
    if f:
        for addr in f.getBody().getAddresses(True):
            for r in rm.getReferencesFrom(addr):
                if not r.isMemoryReference():
                    continue
                to = r.getToAddress()
                # collect .rdata targets
                refs.append({
                    "from": format(addr.getOffset(), "x"),
                    "to": format(to.getOffset(), "x"),
                    "type": str(r.getReferenceType()),
                })
    # Unique targets in likely vtable range
    targets = sorted(set(x["to"] for x in refs))
    labeled = []
    for t in targets:
        addr = toAddr(t)
        syms = list(st.getSymbols(addr))
        labeled.append({
            "to": t,
            "symbols": [s.getName(True) for s in syms],
        })
        log("ref %s syms=%s" % (t, [s.getName(True) for s in syms]))

    # Also search symbol names containing AnomaliesGrid and vftable
    vt_syms = []
    it = st.getAllSymbols(True)
    # might be slow; limit by prefix iterator
    for sym in st.getSymbolIterator("CAnomalies", True):
        n = sym.getName(True)
        if not n.startswith("CAnomalies") and "CAnomalies" not in n:
            # iterator is prefix based on getName()? keep going carefully
            pass
        if "AnomaliesGrid" in n:
            vt_syms.append({
                "name": n,
                "address": format(sym.getAddress().getOffset(), "x") if sym.getAddress() and not sym.getAddress().isExternalAddress() else str(sym.getAddress()),
            })
            log("sym %s @ %s" % (n, sym.getAddress()))
            if len(vt_syms) > 50:
                break

    report = {"ctor_refs": labeled, "vt_syms": vt_syms}
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    log("WROTE %s" % OUT)


if __name__ == "__main__":
    main()
else:
    main()
