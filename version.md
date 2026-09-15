# Correct Vision3D build — Feature 1 map

Confirmed 2026-09-14. Do **not** reuse addresses from `C:\VIT` (70.05.51.00 / 2019-09-20).

## Identity

| | Vision3D.exe | AvVTraitLib.dll |
| --- | --- | --- |
| ProductVersion | **70.06.59.00** | **70.06.59.00** |
| FileVersion | 70, 06, 59, 00 | 70, 06, 59, 00 |
| Company | Vi TECHNOLOGY | Vi TECHNOLOGY |
| LastWriteTime | 2020-02-28 08:11 | 2020-02-28 08:04 |
| Size | 28,738,048 | 21,709,824 |
| SHA-256 | `ccca11b2f05084b484fa5556c67f8874065dbc0b6265177d2517f81265af00f4` | `0f9f68b118112cea87e1735995776934d8d009e3d6d39a8a58562e3fa3e3e5f7` |
| MD5 | `4977e3f0ab33cf104ad26ffa914eac51` | `c3cfb37b2e139c502c544275d491dc5a` |
| Image base | `0x140000000` | `0x180000000` |
| Language | x86:LE:64 / Visual Studio | x86:LE:64 / Visual Studio |
| PDB | `Vision3D.pdb` GUID `1155b4fd-0551-4c76-86fe-6a87542e7719` | `AvVTraitLib.pdb` GUID `36f26fce-4015-4f57-abb3-e10180fd7765` |

PE copies (import source):

`C:\Users\s_sme\Documents\Projects\vision_3d_skips\v3d_files_\Vision3D.exe`  
`C:\Users\s_sme\Documents\Projects\vision_3d_skips\v3d_files_\AvVTraitLib.dll`

Ghidra project (analyzed):

`C:\Users\s_sme\Documents\Projects\vision_3d_skips\v3d_files_uncomp\V3D_SKIP.gpr`

Programs in project: `/Vision3D.exe` (138 607 functions), `/AvVTraitLib.dll` (144 752 functions). Both `Analyzed=true`.

## Vision3D.exe — Feature 1 addresses

PDB did not name `CZoneAnalysis::*` as functions. They were found via log-string xrefs and renamed in Ghidra.

| Symbol | VA (this build) | Old 70.05.51 (do not use) |
| --- | --- | --- |
| `CZoneAnalysis::ExecuteAll_Components` | `0x1407354b0` | `0x1402dcbc0` |
| `CZoneAnalysis::ExecuteOne_Component` | `0x1407368d0`–`0x1407374e8` | `0x1402dc020` |
| `CModelFamily::ImagesAnalysis` IAT call | `0x140736e8a` → `[0x140d52850]` | `0x1402dc578` |
| `CResult::GetBinaryFieldDefects` IAT call | `0x140736efd` → `[0x140d5b198]` | `0x1402dc657` |
| Existing `SkipSubPanel` call (skip-**mark** object named `"SKIP"`) | `0x140736fcb` | `0x1402dc723` |
| `CDataCaoTraitement::SkipSubPanel` | `0x140541080`–`0x1405411b7` | `0x1400f3190` |
| `CDataCaoTraitement::IsSkippedSubPanel` | `0x14052e010`–`0x14052e066` | `0x1400d6b20` |
| `CProductionThread::ExecuteSkip` (marks — not the hook) | `0x1406a06b0` | `0x140259330` |

`SkipSubPanel` has **one** code call site: `ExecuteOne_Component` at `0x140736fcb`. That is the existing skip-mark path. Leave it alone.

Sub-panel id at that call: `edx = [rdi+0x14]` then `rcx = [r15+0x10]` (CAO). Offset **+0x14** matches the old build; the register is `rdi` here, not `r15`.

Skip-mark gate is unchanged in shape: `TEST dword [rsp+0x74], 0x800001` at `0x140736f8f` (do not call skip if Missing/`0x1` or `0x800000` is set).

`ExecuteAll_Components` still drops later objects when the component reports skipped (`"is skipped"` / `"has been skipped by operator"`). Calling `SkipSubPanel` remains the right sink for Feature 1.

## AvVTraitLib.dll

| Symbol | VA |
| --- | --- |
| `CModel::ImagesAnalysis` | `0x180504930` |
| `CModelFamily::ImagesAnalysis` (two overloads) | `0x18078ec40`, `0x18078f080` |
| `CVTrait_Chip::Run` (two overloads) | `0x1805f2b90`, `0x1805f3120` |
| `CVTrait_Chip::RunFunction_CheckPresence` | `0x1805f6280` |
| `CVTrait_Chip::RunFunction_CheckPresence3D` | `0x1805f5d30` |

**`GetBinaryFieldDefects` is not in this DLL.** Both PEs import `STRUCTSUPPORT.DLL::CResult::GetBinaryFieldDefects`. Import `StructSupport.dll` later if we need the bitfield implementation. Production still consumes the mask in `ExecuteOne_Component` after ImagesAnalysis.

Missing bit is still treated as **`0x1`** at the skip-mark test (`0x800001`). Count **only** that bit toward N. Do not count Absent invert (`InvertDefect_MissingComponent` exists on `CResult`).

## Hook (unchanged idea, new VAs)

After `GetBinaryFieldDefects` at `0x140736efd` (`ebx` / `[rsp+0x74]` = mask):

1. If `(mask & 0x1) != 0`, increment Missing count for sub-panel `[rdi+0x14]`.
2. If count **> N** (hard-coded for now), call `SkipSubPanel(cao, sub_panel_id)` at `0x140541080`.
3. Do not touch the `"SKIP"` object path at `0x140736fcb`.
4. Patch a **copy** only. Live `C:\VIT` stays read-only.

## Patch (2026-09-14)

Source (immutable): `v3d_files_\Vision3D.exe`  
SHA-256: `ccca11b2f05084b484fa5556c67f8874065dbc0b6265177d2517f81265af00f4`

Output: `Updated\Vision3D.exe`  
SHA-256: `96aba771401acd55ea99849743541c1710b54e3f8e107a88bd33da7e624d6bfd`  
Same size as source (28,738,048). Rebuild: `python tools\patch_f1_missing_n.py`

| Site | VA | What |
| --- | --- | --- |
| Trampoline | `0x140736f09` | JMP cave; stolen two LEAs replayed in cave |
| Cave | `0x140d50910` | If `ebx & 1`, `inc counts[[rdi+0x14]]`; if `> 3` call `SkipSubPanel([r15+0x10], id)` |
| `SkipList_Reset` | `0x140541050` | JMP `0x140d50980` to zero the 256 counters, then original prologue |
| Counters | `0x14120c680` | 256 dwords, last `.data` page (not in the file; BSS zeros) |

**N = 3** (skip on the 4th Missing on that sub-panel). Hex-edit the immediate at VA `0x140d50931` / file `0xD4FD31` (currently `03`).

Does not patch `AvVTraitLib.dll`. Does not touch `C:\VIT`. Runtime not tested here (needs a full install + dongle).
