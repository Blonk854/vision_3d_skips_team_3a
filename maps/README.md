# Vision3D program atlas (70.06.59.00)

Reference maps for safe patching. **Do not change live `C:\\VIT`.**  
Build confirmed in [`../version.md`](../version.md). Ghidra project: `v3d_files_uncomp/V3D_SKIP.gpr`.

## Scope (agreed)

Named product code in:

| PE | Role | Atlas status |
| --- | --- | --- |
| `Vision3D.exe` | UI + production / review orchestration | Core map started; anomalies-grid click mapped |
| `DyTools0.dll` | `CVitExtReportGridWnd` (report grid) | Imported + click dispatcher decompiled |
| `ProfUISm.dll` | Prof-UIS grid base | Imported; base click is not image-open |
| `AvVTraitLib.dll` | Model / trait execution | Catalog extracted |
| `StructSupport.dll` | `CAnomalie` / `CResult` defect bits | IAT + known VAs; full import still pending |

Excluded unless a path lands there: CRT, STL, MFC paint managers, Cognex, AlgoCore, etc.

## Read order

1. [architecture.md](architecture.md) — modules and mode boundaries
2. [class-index.md](class-index.md) — named classes by mode
3. [production-flow.md](production-flow.md) — inspection + Feature 1 hooks
4. [review-ui.md](review-ui.md) — failure-mode table → image (in progress)
5. [review-station-handoff.md](review-station-handoff.md) — production decision → image/panel messages → supervisor transport
6. [document-lifecycle.md](document-lifecycle.md) - document bindings, posted UI command, supervisor reentrancy, and teardown proof gaps
7. Raw extracts under this folder (`*_atlas_extract.json`, `review_click_trace.json`, `review_station_handoff.json`, `decomp/`)

## How to refresh extracts

With `V3D_SKIP` open in headless MCP (or `analyzeHeadless -readOnly`):

```text
tools/ghidra_scripts/ExtractProductAtlas.py
tools/ghidra_scripts/TraceReviewClickPaths.py
tools/ghidra_scripts/DumpReviewDecomps.py
```

Then:

```powershell
.\.venv\Scripts\python.exe tools\summarize_atlas_extract.py
.\.venv\Scripts\python.exe tools\summarize_review_trace.py
```

## Safety rules for atlas-driven changes

1. Map the full path (callers + callees + data shape) before patching.
2. Prefer stock sinks (`SkipSubPanel`, review routing) over new engines.
3. Fail open to stock behavior when identity / layout validation fails.
4. Patch only copies under `Updated\`; never write `C:\VIT` until intentional.
5. Record every new VA / hash on `version.md`.
