# Follow Vision3D registered-message DAT_ globals to real handlers.
# @category Vision3D
# @runtime PyGhidra

#@runtime PyGhidra

import json
import os
import struct

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

OUT = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps\Vision3D_vitgrid_msg_consumers.json"
DECOMP_DIR = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps\decomp"

# One init function per click message (from prior extract); double-click LBTN is key.
INITS = {
    "LBTNDBL": "1401bcd00",
    "LBTNDWN": "1401bcd20",
    "LBTNUP": "1401bcd40",
}


def main():
    os.makedirs(DECOMP_DIR, exist_ok=True)
    program = currentProgram
    decomp = DecompInterface()
    decomp.openProgram(program)
    monitor = ConsoleTaskMonitor()
    listing = program.getListing()
    rm = program.getReferenceManager()

    rows = []
    for label, init_s in INITS.items():
        init_fn = getFunctionAt(toAddr(init_s))
        # Find data writes from init function -> DAT_ holding registered msg
        dat_addrs = set()
        if init_fn is not None:
            body = init_fn.getBody()
            addrs = body.getAddresses(True)
            while addrs.hasNext():
                a = addrs.next()
                for ref in rm.getReferencesFrom(a):
                    if ref.getReferenceType().isWrite() or ref.getReferenceType().isData():
                        dat_addrs.add(str(ref.getToAddress()))
        # Also parse decomp for DAT_
        res = decomp.decompileFunction(init_fn, 30, monitor) if init_fn else None
        c = (
            res.getDecompiledFunction().getC()
            if res and res.getDecompiledFunction()
            else ""
        )
        for token in c.replace("(", " ").replace(")", " ").replace("=", " ").split():
            if token.startswith("DAT_"):
                dat_addrs.add(token[4:] if False else token.replace("DAT_", ""))
                # keep both forms
                try:
                    dat_addrs.add(token.split("_", 1)[1])
                except Exception:
                    pass

        # Normalize addresses
        norms = []
        for d in list(dat_addrs):
            try:
                if d.startswith("DAT_"):
                    norms.append(toAddr(d[4:]))
                else:
                    norms.append(toAddr(d))
            except Exception:
                continue

        consumers = []
        for dat in norms:
            for ref in rm.getReferencesTo(dat):
                fn = getFunctionContaining(ref.getFromAddress())
                if fn is None:
                    continue
                entry = str(fn.getEntryPoint())
                if entry == init_s:
                    continue
                consumers.append(
                    {
                        "dat": str(dat),
                        "from": str(ref.getFromAddress()),
                        "type": str(ref.getReferenceType()),
                        "function": fn.getName(True),
                        "entry": entry,
                        "body": int(fn.getBody().getNumAddresses()),
                    }
                )

        # Decompile largest consumers
        consumers.sort(key=lambda x: -x["body"])
        dumped = []
        seen = set()
        for cons in consumers[:8]:
            if cons["entry"] in seen:
                continue
            seen.add(cons["entry"])
            fn = getFunctionAt(toAddr(cons["entry"]))
            res = decomp.decompileFunction(fn, 90, monitor)
            cc = (
                res.getDecompiledFunction().getC()
                if res and res.getDecompiledFunction()
                else ""
            )
            path = os.path.join(
                DECOMP_DIR,
                "Vision3D_msgconsumer_%s_%s.c" % (label, cons["entry"].replace(":", "")),
            )
            with open(path, "w", encoding="utf-8") as out:
                out.write("// %s consumer of %s @ %s\n\n%s" % (label, cons["dat"], cons["entry"], cc))
            dumped.append({"entry": cons["entry"], "function": cons["function"], "path": path, "c_bytes": len(cc)})

        rows.append(
            {
                "label": label,
                "init": init_s,
                "init_decomp": c,
                "dat_candidates": [str(x) for x in norms],
                "consumers": consumers[:40],
                "dumped": dumped,
            }
        )
        print(label, "consumers", len(consumers), "dumped", len(dumped))

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    print("WROTE", OUT)
    decomp.dispose()


if __name__ == "__main__":
    main()
else:
    main()
