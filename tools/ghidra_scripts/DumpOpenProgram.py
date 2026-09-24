# List open programs / dump session identity for atlas work.
#@category Vision3D
#@runtime PyGhidra

import json
import os

OUT = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps\_open_program.json"

def main():
    p = currentProgram
    info = {
        "name": p.getName(),
        "path": str(p.getExecutablePath()) if p.getExecutablePath() else None,
        "image_base": format(p.getImageBase().getOffset(), "x"),
        "functions": p.getFunctionManager().getFunctionCount(),
        "memory_size": p.getMemory().getSize(),
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(info, fh, indent=2)
    print(json.dumps(info))

if __name__ == "__main__":
    main()
else:
    main()
