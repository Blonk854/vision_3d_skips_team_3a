# Trace review-table click-to-image candidates in Vision3D.exe.
# @category Vision3D
# @runtime PyGhidra

#@runtime PyGhidra

import json
import os
import re

OUT_PATH = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps\review_click_trace.json"

NEEDLES = [
    "OnGbwAnalyzeCellMouseClickEvent",
    "CVitExtReportGridWnd",
    "ShouldItGoToReviewStation",
    "SendPanelToReviewStation",
    "GetReviewStation",
    "Text fault",
    "Missing",
    "SaveOIS",
    "CVitImgFileRecorderHelper",
    "CProductionDoc::ReadCurrentPanelStatusFromReview",
    "CMsgPanelProd::SendPanelToReviewStation",
    "PV_COMMAND_BTN_OIS",
    "JEDEC,Part Number,Reference Designator",
]


def refs_to_addr(program, addr, limit=40):
    rm = program.getReferenceManager()
    out = []
    for ref in rm.getReferencesTo(addr):
        from_addr = ref.getFromAddress()
        fn = getFunctionContaining(from_addr)
        out.append(
            {
                "from": str(from_addr),
                "type": str(ref.getReferenceType()),
                "function": fn.getName(True) if fn else None,
                "function_entry": str(fn.getEntryPoint()) if fn else None,
            }
        )
        if len(out) >= limit:
            break
    return out


def find_string_data(program, text):
    listing = program.getListing()
    hits = []
    it = listing.getDefinedData(True)
    while it.hasNext():
        data = it.next()
        try:
            val = data.getValue()
        except Exception:
            continue
        if val is None:
            continue
        s = str(val)
        if text in s:
            hits.append(
                {
                    "string": s[:200],
                    "address": str(data.getAddress()),
                    "exact": s == text,
                }
            )
            if len(hits) >= 30:
                break
    return hits


def function_hits(program, needle):
    fm = program.getFunctionManager()
    sm = program.getSymbolTable()
    hits = []
    for sym in sm.getSymbolIterator(needle, True):
        name = sym.getName(True)
        if needle.lower() not in name.lower():
            # SymbolIterator prefix-walk; stop when prefix diverges.
            if not name.lower().startswith(needle.lower()[: min(8, len(needle))].lower()):
                break
            continue
        addr = sym.getAddress()
        fn = getFunctionAt(addr) or getFunctionContaining(addr)
        hits.append(
            {
                "symbol": name,
                "address": str(addr),
                "function": fn.getName(True) if fn else None,
                "function_entry": str(fn.getEntryPoint()) if fn else None,
                "refs_to": refs_to_addr(program, addr, limit=25),
            }
        )
        if len(hits) >= 40:
            break
    # Also scan function names containing needle
    if len(hits) < 5:
        it = fm.getFunctions(True)
        while it.hasNext():
            f = it.next()
            name = f.getName(True)
            if needle.lower() in name.lower():
                hits.append(
                    {
                        "symbol": name,
                        "address": str(f.getEntryPoint()),
                        "function": name,
                        "function_entry": str(f.getEntryPoint()),
                        "refs_to": refs_to_addr(program, f.getEntryPoint(), limit=25),
                    }
                )
            if len(hits) >= 40:
                break
    return hits


def class_methods(program, class_name, limit=80):
    fm = program.getFunctionManager()
    methods = []
    it = fm.getFunctions(True)
    while it.hasNext():
        f = it.next()
        name = f.getName(True)
        if class_name + "::" in name or name.startswith(class_name + "::"):
            methods.append({"name": name, "entry": str(f.getEntryPoint())})
            if len(methods) >= limit:
                break
    return methods


def main():
    program = currentProgram
    results = {
        "program": str(program.getName()),
        "image_base": str(program.getImageBase()),
        "string_traces": [],
        "symbol_traces": [],
        "vit_report_grid_methods": class_methods(program, "CVitExtReportGridWnd"),
        "click_handlers": function_hits(program, "OnGbwAnalyzeCellMouseClickEvent"),
        "production_thread_symbols": function_hits(program, "CProductionThread"),
        "review_symbols": function_hits(program, "Review"),
    }

    for needle in NEEDLES:
        string_hits = find_string_data(program, needle)
        traced = []
        for hit in string_hits[:15]:
            addr = toAddr(hit["address"])
            traced.append(
                {
                    "needle": needle,
                    "string": hit["string"],
                    "address": hit["address"],
                    "exact": hit["exact"],
                    "refs": refs_to_addr(program, addr, limit=30),
                }
            )
        results["string_traces"].append(
            {"needle": needle, "hit_count": len(string_hits), "hits": traced}
        )

    # Named production/review classes from demangled symbols
    interesting_classes = [
        "CProductionThread",
        "CProductionDoc",
        "CProdCarte",
        "CMsgPanelProd",
        "CZoneAnalysis",
        "CDataCaoTraitement",
        "CVitImgFileRecorderHelper",
        "CVitExtReportGridWnd",
        "CAnomalie",
        "CAnomalieProd",
        "CDocCompose",
        "CDlgReview",
        "CReview",
    ]
    class_index = {}
    for cls in interesting_classes:
        class_index[cls] = class_methods(program, cls, limit=60)
    results["interesting_class_methods"] = class_index

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print("WROTE", OUT_PATH)
    print(
        "click_handlers",
        len(results["click_handlers"]),
        "vit_methods",
        len(results["vit_report_grid_methods"]),
        "string_needles",
        len(results["string_traces"]),
    )


if __name__ == "__main__":
    main()
else:
    main()
