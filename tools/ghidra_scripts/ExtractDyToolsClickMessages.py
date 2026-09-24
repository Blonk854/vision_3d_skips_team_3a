# Resolve CVitExtReportGridWnd click PostMessage IDs and related vtable targets.
# @category Vision3D
# @runtime PyGhidra

#@runtime PyGhidra

import json
import os
import struct

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

OUT = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps\DyTools0_click_messages.json"
DECOMP_DIR = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps\decomp"


def u32(program, addr):
    return struct.unpack("<I", bytes(getBytes(addr, 4)))[0]


def main():
    program = currentProgram
    listing = program.getListing()
    decomp = DecompInterface()
    decomp.openProgram(program)
    monitor = ConsoleTaskMonitor()

    msg_addrs = [
        "18026dde8",
        "18026ddec",
        "18026ddf0",
        "18026ddf4",
        "18026ddf8",
        "18026ddfc",
        "18026de00",
        "18026de04",
        "18026de08",
    ]
    messages = []
    for a in msg_addrs:
        addr = toAddr(a)
        val = u32(program, addr)
        refs = []
        for ref in program.getReferenceManager().getReferencesTo(addr):
            fn = getFunctionContaining(ref.getFromAddress())
            refs.append(
                {
                    "from": str(ref.getFromAddress()),
                    "function": fn.getName(True) if fn else None,
                }
            )
        messages.append({"address": a, "value": val, "value_hex": hex(val), "refs": refs[:20]})

    # Decompile likely virtual helpers near click handler by scanning symbols
    # with On*Click / cell in CVitExtReportGridWnd
    helpers = []
    fm = program.getFunctionManager()
    it = fm.getFunctions(True)
    while it.hasNext():
        f = it.next()
        name = f.getName(True)
        if "CVitExtReportGridWnd::" not in name:
            continue
        interesting = any(
            k in name
            for k in (
                "Click",
                "Mouse",
                "Cell",
                "Image",
                "OIS",
                "Open",
                "Select",
                "Row",
                "Column",
                "Notify",
            )
        )
        if not interesting:
            continue
        helpers.append({"name": name, "entry": str(f.getEntryPoint())})

    # Dump a few helper decomps
    os.makedirs(DECOMP_DIR, exist_ok=True)
    dumped = []
    for h in helpers:
        if any(
            k in h["name"]
            for k in ("Click", "Mouse", "Notify", "Image", "OIS", "Open", "Select")
        ):
            f = getFunctionAt(toAddr(h["entry"]))
            if f is None:
                continue
            res = decomp.decompileFunction(f, 60, monitor)
            c = (
                res.getDecompiledFunction().getC()
                if res and res.getDecompiledFunction()
                else ""
            )
            if not c:
                continue
            safe = h["entry"].replace(":", "")
            path = os.path.join(DECOMP_DIR, "DyTools0_vit_%s.c" % safe)
            with open(path, "w", encoding="utf-8") as out:
                out.write("// %s @ %s\n\n%s" % (h["name"], h["entry"], c))
            dumped.append({"name": h["name"], "entry": h["entry"], "path": path, "bytes": len(c)})
            if len(dumped) >= 25:
                break

    payload = {
        "program": str(program.getName()),
        "messages": messages,
        "vit_interesting_methods": helpers[:150],
        "dumped_helpers": dumped,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print("WROTE", OUT, "messages", len(messages), "helpers", len(helpers), "dumped", len(dumped))
    decomp.dispose()


if __name__ == "__main__":
    main()
else:
    main()
