import json
from pathlib import Path

p = Path(r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps\Vision3D_exe_atlas_extract.json")
d = json.loads(p.read_text(encoding="utf-8"))

keys = (
    "Prod", "Zone", "Skip", "Anomal", "CAO", "Cao", "Review", "Defect",
    "Vit", "Panel", "Carte", "Fail", "Image", "OIS", "Chart", "Report",
    "Text", "Miss", "Compose", "Library", "Model", "Trait", "Thread",
    "Msg", "Screen", "Grid", "Column", "Histo",
)
prod = [c for c in d["top_classes"] if any(x in c["class"] for x in keys)]
print("functions_total", d["functions_total"], "named", d["functions_named_non_FUN"])
print("mode_counts", d["mode_counts"])
print("product-ish classes", len(prod))
for c in prod[:80]:
    print(f"{c['count']:4d}  {c['class']}")

print("\n--- anchors ---")
for a in d["anchors"]:
    print(a["needle"], len(a["hits"]))
    for h in a["hits"][:5]:
        print("   ", h["address"], h["name"])

print("\n--- focus strings with Missing/Text/Deviation/Review/click ---")
interesting = []
for s in d["focus_strings"]:
    t = s["string"]
    if any(k in t for k in (
        "Missing", "Text", "Deviation", "Review", "click", "Click",
        "column", "Column", "failure", "Failure", "OIS", "defect", "Defect",
        "CVit", "CProd", "CMsg", "SendPanel", "ShouldIt",
    )):
        interesting.append(s)
print("interesting", len(interesting))
for s in interesting[:100]:
    print(s["address"], s["string"][:140])

# dump filtered product class index for atlas markdown
out = {
    "program": d["program"],
    "image_base": d["image_base"],
    "functions_total": d["functions_total"],
    "functions_named_non_FUN": d["functions_named_non_FUN"],
    "mode_counts": d["mode_counts"],
    "product_classes": prod,
    "anchors": d["anchors"],
    "interesting_focus_strings": interesting[:300],
}
Path(r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps\vision3d_product_index.json").write_text(
    json.dumps(out, indent=2), encoding="utf-8"
)
print("\nWROTE product index")
