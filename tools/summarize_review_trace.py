import json
from pathlib import Path

d = json.loads(Path(r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps\review_click_trace.json").read_text(encoding="utf-8"))
print("program", d["program"])
print("\n=== click_handlers ===")
for h in d.get("click_handlers", []):
    print(h.get("symbol"), h.get("address"), "refs", len(h.get("refs_to", [])))
    for r in h.get("refs_to", [])[:8]:
        print("   ", r.get("from"), r.get("function"), r.get("type"))

print("\n=== vit_report_grid_methods ===", len(d.get("vit_report_grid_methods", [])))
for m in d.get("vit_report_grid_methods", [])[:40]:
    print(" ", m["entry"], m["name"])

print("\n=== interesting_class_methods counts ===")
for cls, methods in d.get("interesting_class_methods", {}).items():
    print(f"  {cls}: {len(methods)}")
    for m in methods[:6]:
        print("   ", m["entry"], m["name"])

print("\n=== string_traces with refs ===")
for st in d.get("string_traces", []):
    hits_with_refs = [h for h in st.get("hits", []) if h.get("refs")]
    print(f"\n[{st['needle']}] hit_count={st['hit_count']} with_refs={len(hits_with_refs)}")
    for h in hits_with_refs[:6]:
        print(" ", h["address"], repr(h["string"][:80]))
        for r in h["refs"][:6]:
            print("    <-", r.get("from"), r.get("function"), r.get("type"))
