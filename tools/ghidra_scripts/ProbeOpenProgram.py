# Dump open MCP session ids to a file for tooling.
# @category Vision3D
# @runtime PyGhidra

#@runtime PyGhidra

import json
import os

OUT = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps\_open_session_probe.txt"

def main():
    # This script runs against one open program; just record that program.
    p = currentProgram
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("name=%s\n" % p.getName())
        f.write("path=%s\n" % p.getExecutablePath())
        f.write("base=%s\n" % p.getImageBase())
        f.write("funcs=%s\n" % p.getFunctionManager().getFunctionCount(True))
    print("WROTE", OUT)

if __name__ == "__main__":
    main()
else:
    main()
