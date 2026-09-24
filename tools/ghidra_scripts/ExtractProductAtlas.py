# Extract named product class catalog and key path anchors from an open Vision3D PE.
# @category Vision3D
# @runtime PyGhidra

#@runtime PyGhidra

import json
import os
import re
from collections import Counter, defaultdict

OUT_DIR = r"C:\Users\s_sme\Documents\Projects\vision_3d_skips\maps"

MODE_HINTS = {
    "production": re.compile(
        r"(Prod|Production|ZoneAnalysis|Skip|Anomal|Inspection|CAO|Cao|Panel|Carte)",
        re.I,
    ),
    "review": re.compile(r"(Review|Defect|Fail|ImageView|OIS|OTR|Histogram)", re.I),
    "compose": re.compile(r"(Compose|DocCompose|Editor|Wizard|TST|VisFile|Cad)", re.I),
    "library": re.compile(r"(Library|ModelFamily|Model|Trait|VTrait|MatchMaker)", re.I),
    "ui": re.compile(r"(Dialog|Dlg|View|Frame|Wnd|Screen|Chart|Table|Grid|Column)", re.I),
}


def classify(name):
    modes = []
    for mode, rx in MODE_HINTS.items():
        if rx.search(name):
            modes.append(mode)
    return modes or ["other"]


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    program = currentProgram
    fm = program.getFunctionManager()
    sm = program.getSymbolTable()
    listing = program.getListing()

    classes = Counter()
    samples = defaultdict(list)
    mode_counts = Counter()
    named = 0
    total = 0

    it = fm.getFunctions(True)
    while it.hasNext():
        f = it.next()
        total += 1
        name = f.getName(True)
        if name.startswith("FUN_") or name.startswith("thunk_FUN_"):
            continue
        named += 1
        parts = name.split("::")
        if len(parts) >= 2:
            cls = parts[-2]
            classes[cls] += 1
            if len(samples[cls]) < 8:
                samples[cls].append(
                    {"name": name, "entry": str(f.getEntryPoint())}
                )
            for mode in classify(cls + "::" + name):
                mode_counts[mode] += 1

    # Log-style class::method strings (often present even when functions stay FUN_*)
    string_hits = []
    data_it = listing.getDefinedData(True)
    while data_it.hasNext():
        data = data_it.next()
        try:
            val = data.getValue()
        except Exception:
            continue
        if val is None:
            continue
        s = str(val)
        if len(s) < 8 or len(s) > 180:
            continue
        if "::" not in s:
            continue
        if not re.match(r"^[A-Za-z_][\w:]{3,}$", s):
            continue
        if s.startswith("std::") or s.startswith("ATL::") or s.startswith("boost::"):
            continue
        string_hits.append({"string": s, "address": str(data.getAddress())})

    # Focus strings for review/table/image click paths
    focus_terms = [
        "deviation",
        "Deviation",
        "Missing",
        "missing",
        "Text",
        "column",
        "Column",
        "failure",
        "Failure",
        "Review",
        "click",
        "Click",
        "OIS",
        "image",
        "Image",
    ]
    focus_strings = []
    data_it = listing.getDefinedData(True)
    while data_it.hasNext():
        data = data_it.next()
        try:
            val = data.getValue()
        except Exception:
            continue
        if val is None:
            continue
        s = str(val)
        if not any(term in s for term in focus_terms):
            continue
        if len(s) > 240:
            continue
        focus_strings.append({"string": s, "address": str(data.getAddress())})

    # Known Feature-1 anchors if present as symbols/functions
    anchors = []
    for needle in [
        "SkipSubPanel",
        "IsSkippedSubPanel",
        "ExecuteOne_Component",
        "ExecuteAll_Components",
        "ShouldItGoToReviewStation",
        "CAPM_SetInspectionStatus",
        "ExecuteSkip",
        "GetBinaryFieldDefects",
        "ImagesAnalysis",
        "RazRes",
    ]:
        found = []
        for sym in sm.getSymbols(needle):
            found.append(
                {
                    "name": str(sym.getName(True)),
                    "address": str(sym.getAddress()),
                    "type": str(sym.getSymbolType()),
                }
            )
        # also partial
        if not found:
            for sym in sm.getSymbolIterator(needle, True):
                n = sym.getName()
                if needle.lower() not in n.lower():
                    break
                found.append(
                    {
                        "name": str(sym.getName(True)),
                        "address": str(sym.getAddress()),
                        "type": str(sym.getSymbolType()),
                    }
                )
                if len(found) >= 10:
                    break
        anchors.append({"needle": needle, "hits": found[:20]})

    payload = {
        "program": str(program.getName()),
        "language": str(program.getLanguageID()),
        "image_base": str(program.getImageBase()),
        "functions_total": total,
        "functions_named_non_FUN": named,
        "mode_counts": dict(mode_counts),
        "top_classes": [
            {"class": c, "count": n} for c, n in classes.most_common(120)
        ],
        "class_samples": {
            c: samples[c] for c, _ in classes.most_common(60)
        },
        "class_method_strings_count": len(string_hits),
        "class_method_strings_sample": string_hits[:400],
        "focus_strings_count": len(focus_strings),
        "focus_strings": focus_strings[:500],
        "anchors": anchors,
    }

    out_name = program.getName().replace(".", "_") + "_atlas_extract.json"
    out_path = os.path.join(OUT_DIR, out_name)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print("WROTE", out_path)
    print(
        "functions",
        total,
        "named",
        named,
        "classes",
        len(classes),
        "strings",
        len(string_hits),
        "focus",
        len(focus_strings),
    )


if __name__ == "__main__":
    main()
else:
    # GhidraScript entry
    main()
