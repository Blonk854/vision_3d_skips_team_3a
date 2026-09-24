import json
from pathlib import Path

root = Path(r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps")
for name in ("AvVTraitLib_dll_atlas_extract.json", "vision3d_product_index.json"):
    p = root / name
    if not p.exists():
        print("MISSING", p)
        continue
    d = json.loads(p.read_text(encoding="utf-8"))
    print("====", name)
    if "program" in d:
        print("program", d.get("program"), "funcs", d.get("functions_total"), "named", d.get("functions_named_non_FUN"))
        print("modes", d.get("mode_counts"))
        print("top20:")
        for c in d.get("top_classes", [])[:20]:
            print(f"  {c['count']:4d}  {c['class']}")
        print("anchors:")
        for a in d.get("anchors", []):
            print(f"  {a['needle']}: {len(a['hits'])}")
    else:
        print("keys", list(d.keys())[:20])
        print("product_classes", len(d.get("product_classes", [])))
        for c in d.get("product_classes", [])[:30]:
            print(f"  {c['count']:4d}  {c['class']}")
