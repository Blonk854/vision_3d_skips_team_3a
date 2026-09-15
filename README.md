# Feature 1 — skip the rest of a sub-panel after N Missing fails

Pickup notes for a **new** Ghidra project on the **correct** Vision3D build.
Previous mapping used the wrong install (`C:\VIT`, labeled 70.05.51.00 / binaries dated 2019-09-20). **Re-find every address.** Keep the names and the hook idea.

This folder is only Feature 1 (runtime skip-after-N-missing). TST→VIS conversion lives elsewhere: `C:\Users\s_sme\Documents\Projects\vision_3d_update\tools\tst3vis.py`.

## Rebuild locally (no PE in git)

This repo does **not** contain `Vision3D.exe`. A patched PE on clone is what EDR (CrowdStrike) will scan.

1. Copy the 70.06.59.00 `Vision3D.exe` to `v3d_files_\Vision3D.exe` (or pass the path as argv).
2. Run: `python tools\patch_f1_missing_n.py`
3. Output: `Updated\Vision3D.exe` (created if missing). Do not commit it.

Expected source SHA-256: `ccca11b2f05084b484fa5556c67f8874065dbc0b6265177d2517f81265af00f4`  
Expected output SHA-256: `96aba771401acd55ea99849743541c1710b54e3f8e107a88bd33da7e624d6bfd`

---

## Goal

On a multi-board panel: once **more than N** components on **one sub-panel** fail as **Missing** (presence not found), skip the **rest of that sub-panel**. Other sub-panels keep running.

This is a **new production policy**. It is not in manuals or INI.

N has no setting today (acceptance **F1-D**). Do not invent a UI until the count-and-call works with a hard-coded N.

---

## What this is not

Do not confuse with existing product:

| Existing | Why it is not Feature 1 |
| --- | --- |
| Skip **marks** (`ExecuteSkip`, “Skip sub-panel when skip found”) | Needs ink/sticker/hole; not a Missing count |
| Global skip (panel 0) | All or nothing |
| Operator “Skip boards before starting production” | Manual, before the batch |
| `CTRL+S` component skip list | JEDEC / PN / refdes for the whole batch |
| TST **Absent** | Expected-missing invert per part |
| `Stop prod if missing Jedec` | Library file missing, not a part missing on the board |
| Variant “tested in missing” | Programming-time, not runtime N |
| `ComputeMissingComponent` | Editor / Compose path, not production `ExecuteOne_Component` |

**Missing** = presence test failed (expected part not found). Only that defect type counts toward N. Polarity, offset, and other fails do not.

---

## Acceptance (when we test on the correct build)

Use a TST with ≥2 sub-panels and several presence checks on each. Example N = 3.

| ID | Setup | Pass if |
| --- | --- | --- |
| F1-A | SP1 has **>N** Missing, then more untested presence checks. SP2 populated. | After the Nth Missing on SP1, remaining objects on **SP1** are not inspected (or NOT INSPECTED / skipped). SP2 fully inspected. Panel is not failed only because the skipped remainder was never tested. |
| F1-B | SP1 has **exactly N** Missing. | No auto-skip. SP1 finishes normally. |
| F1-C | Missing mixed with polarity/offset. | Only Missing counts. |
| F1-D | N configurable. | Later. No INI key today. |

Compute/skip order in `DefaultValue.ini` `[Computing]`: `Skip order`, `Mire order`, `Code order`. Note it on the correct install; do not edit live config.

---

## Ghidra — new project (correct version)

### Import these two files only

Copy them out of the **correct** install first. Do not import from the old `C:\VIT` tree unless you have confirmed that *is* the right build.

| File | Why |
| --- | --- |
| `Vision3D.exe` | Production walk + skip sink |
| `AvVtraitLib.dll` | Trait run + `GetBinaryFieldDefects` (Missing bit) |

Do **not** import the whole install. Do **not** need `VitDataCAD.dll` for this feature (that was TST serialize / VIS export).

Optional later if a call jumps out of those two: `StructSupport.dll` (mentioned next to the live trio on the old map).

### Project setup

1. New empty Ghidra project **in this folder** (or a `ghidra/` subfolder here). Do not reuse:
   - `C:\Users\s_sme\Documents\Projects\tst2vis\Giddy`
   - `tst2vis_giddro`
   Those had `Vision3D.exe` open with **0 functions** (no Auto Analyze).
2. Language: **x86:LE:64:default**, compiler **windows / Visual Studio**.
3. Import `Vision3D.exe`, then `AvVtraitLib.dll` into the **same** project.
4. Run **Auto Analyze** on both and **wait until it finishes**. Confirm Function Manager count is thousands, not zero.
5. Record on `version.md` (create when you have the files): product version string, file dates, SHA-256 of both PEs, image bases.

Ghidra install already on this PC:

`C:\Users\s_sme\Documents\ghidra_12.1_PUBLIC_20260513\ghidra_12.1_PUBLIC`

Headless MCP (already used): `C:\Users\s_sme\Documents\ghidra-headless-mcp` with Python 3.14.

### First lookups (by **name**, not old RVA)

In `Vision3D.exe` exports / symbols:

- `CZoneAnalysis::ExecuteAll_Components`
- `CZoneAnalysis::ExecuteOne_Component`
- `CDataCaoTraitement::SkipSubPanel`
- `CDataCaoTraitement::IsSkippedSubPanel`
- `ExecuteSkip` (skip **marks** — not the hook)

In `AvVtraitLib.dll`:

- `GetBinaryFieldDefects`
- `ImagesAnalysis` (production signature uses `CRunContextModelFamily`, `CModelResult*`, `CRect*`)
- Chip example on the old build: `CVTrait_Chip::Run`

---

## Logic we already know (re-verify on the new PE)

Missing already lands in the **same function** that can call `SkipSubPanel`. Feature 1 is a **count-and-call**, not a new skip engine.

```
CZoneAnalysis::ExecuteAll_Components
  already drops later objects if the sub-panel
  "is skipped" / "has been skipped by operator"
        │
        ▼
CZoneAnalysis::ExecuteOne_Component
  ImagesAnalysis(...)          → AvVtraitLib IAT
        │
        ▼
  CVTrait_*::Run  (presence / 3D presence)
    CDefect(...) + CResult::AddDefect
        │
        ▼
  GetBinaryFieldDefects
    Missing bit = 0x1
        │
        ▼  ★ HOOK HERE
  if this result is Missing 0x1:
      missing_count[sub_panel] += 1
      if missing_count[sub_panel] > N:
          SkipSubPanel(sub_panel_id)
```

`ExecuteAll_Components` already honors “is skipped”, so once `SkipSubPanel` runs, later components on that board should be dropped.

### Sink

`CDataCaoTraitement::SkipSubPanel(long subPanelId)`

- Sub-panel id at the production call site was `edx = [r15+0x14]` on the old exe (re-check).
- Early-out: `IsSkippedSubPanel`.
- Unrelated: menu thunk that jumped to `CDocCompose::GenereVisFile` (VIS export). Do not hook that.

Skip-mark path (`ExecuteSkip`) is separate. Inside `ExecuteOne_Component` the old build also had a pack-1 SKIP object test (`r13d, 0x800001`) that already calls `SkipSubPanel`. Leave that alone. Our counter is for **component Missing**, not skip-mark objects.

### Defect bit

**Missing = `0x1`.** Do not count other bits toward N.

### Hook rules

1. After `GetBinaryFieldDefects` in `ExecuteOne_Component`.
2. Count only Missing `0x1`, per sub-panel.
3. If count **> N**, call existing `SkipSubPanel`.
4. Do not skip other sub-panels.
5. Do not count Absent-expected, polarity, offset, etc.
6. Copy of binaries / config only. **Do not patch the live install** until we intend to.

---

## Addresses from the WRONG build (hints only)

Old `C:\VIT\Vision3D.exe` image base `0x140000000`. **These will move.**

| Symbol | Old VA |
| --- | --- |
| `CZoneAnalysis::ExecuteAll_Components` | `0x1402dcbc0` |
| `CZoneAnalysis::ExecuteOne_Component` | `0x1402dc020` |
| `ImagesAnalysis` IAT site | `0x1402dc578` |
| `GetBinaryFieldDefects` site | `0x1402dc657` |
| `SkipSubPanel` call in that function | `0x1402dc723` |
| `CDataCaoTraitement::SkipSubPanel` | `0x1400f3190`–`0x1400f32cf` |
| `IsSkippedSubPanel` | `0x1400d6b20` |
| `ExecuteSkip` (marks) | `0x140259330` |

Old `AvVtraitLib.dll` image base `0x180000000`; `CVTrait_Chip::Run` was `0x1800f6e80`.

---

## Safety

- Live machine install is read-only until we explicitly patch a **copy**.
- Do not touch the Safenet / Cognex dongle.
- Do not write VIS/TST next to live `C:\VIT\Data` (use `%TEMP%` if dumping).
- Config files (`DefaultValue.ini`, `Parameters.ini`, `vit.cfg`) are reference only.

---

## Related docs (older research, still valid conceptually)

`C:\Users\s_sme\Documents\Projects\vision_3d_update\`

- `notes/feature-1-subpanel-missing-n.md` — problem, F1-A..D, “not these” list
- `experiments/feature-1-subpanel-missing.md` — station checklist
- `notes/glossary.md` — panel vs sub-panel vs skip mark vs Missing vs Absent
- `notes/inventory.md` — module names (exe / `AvVtraitLib.dll` / …)
- `notes/decision-gate.md` — originally said “no Ghidra”; we later mapped the hook anyway. This skips project **is** the Ghidra continuation.

---

## Next session

1. Confirm the **correct** Vision3D version (Help → About / release note) and hash the two PEs into `version.md`.
2. New Ghidra project here; import exe + `AvVtraitLib.dll`; Auto Analyze until function count is real.
3. Re-find `ExecuteOne_Component` and `SkipSubPanel` by name; dump the Missing bit and the call that already skips.
4. Design the N-count patch against **those** addresses. Do not paste the table above into a patch.
