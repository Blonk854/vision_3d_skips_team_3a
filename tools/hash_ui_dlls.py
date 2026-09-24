import hashlib
import json
import struct
from pathlib import Path

root = Path(r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\v3d_files_")
out = Path(r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps\ui_dll_identity.json")
rows = []
for name in ("DyTools0.dll", "ProfUISm.dll"):
    p = root / name
    data = p.read_bytes()
    pe = data.find(b"PE\0\0")
    machine = magic = image_base = None
    if pe >= 0:
        machine = struct.unpack_from("<H", data, pe + 4)[0]
        opt = pe + 24
        magic = struct.unpack_from("<H", data, opt)[0]
        if magic == 0x20B:
            image_base = struct.unpack_from("<Q", data, opt + 24)[0]
        elif magic == 0x10B:
            image_base = struct.unpack_from("<I", data, opt + 28)[0]
    rows.append(
        {
            "path": str(p),
            "name": name,
            "size": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "pe_offset": pe,
            "machine": hex(machine) if machine is not None else None,
            "optional_magic": hex(magic) if magic is not None else None,
            "image_base": hex(image_base) if image_base is not None else None,
        }
    )
    print(name, rows[-1]["size"], rows[-1]["sha256"], rows[-1]["image_base"])

out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
print("WROTE", out)
