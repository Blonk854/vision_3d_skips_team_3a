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
`C:\Users\s_sme\Documents\Projects\vision_3d_skips\v3d_files_\StructSupport.dll`

Matching `StructSupport.dll`: Product/FileVersion **70.06.59.00**, size
2,256,384 bytes, SHA-256
`d6270dbe5c97b5ed1000c2541c1e8d495d7db6be184e45d6495d7fad75e0f832`,
image base `0x180000000`.

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

Missing bit is still treated as **`0x1`** at the skip-mark test (`0x800001`).
Count only that bit toward the Missing numerator. Do not count Absent invert
(`InvertDefect_MissingComponent` exists on `CResult`).

## StructSupport.dll

| Symbol | VA |
| --- | --- |
| `CAnomalie` vtable | `0x1801274b0` |
| `CAnomalieProd` vtable | `0x180127548` |
| `CAnomalie::IsOk` | `0x1800900a0` |
| `CAnomalie::RazRes` | `0x180090840` |
| `CAnomalieProd::RazRes` | `0x1800908c0` |

Vtable slot `+0x48` is `RazRes`. `CAnomalie::IsOk` requires
`CAnomalie+0x2c == 0` and no faulty bits in `CAnomalie+0x28`.
Vision3D's existing operator-skip branch calls slot `+0x48` and then writes
skip cause `1` at `+0x2c`; the threshold handler uses the same sequence.

## Hook (unchanged idea, new VAs)

After `GetBinaryFieldDefects` at `0x140736efd` (`ebx` / `[rsp+0x74]` = mask):

1. Increment inspected count for sub-panel `[rdi+0x14]`.
2. If `(mask & 0x1) != 0`, increment its Missing count.
3. After at least 10 inspections, call `SkipSubPanel(cao, sub_panel_id)` at
   `0x140541080` when `missing * 100 > inspected * 30`.
4. Do not touch the `"SKIP"` object path at `0x140736fcb`.
5. Patch a **copy** only. Live `C:\VIT` stays read-only.

## Patch (2026-09-16)

Source (immutable): `v3d_files_\Vision3D.exe`  
SHA-256: `ccca11b2f05084b484fa5556c67f8874065dbc0b6265177d2517f81265af00f4`

Output: `Updated\Vision3D.exe`  
SHA-256: `d689eeb3d1216dd9e5c493f010dd19192bb575a07dc4fd5a4132daeb2c804a51`
Size: 28,739,072 bytes (1,024 bytes larger than source). Rebuild:
`python tools\patch_f1_missing_n.py`

| Site | VA | What |
| --- | --- | --- |
| Trampoline | `0x140736f09` | JMP `.f1code`; stolen two LEAs replayed on the non-trigger path |
| Handler | `0x141c98000` | Count results; call `SkipSubPanel`; post the stock UI refresh; normalize matching anomalies in every zone; exit through `0x14073742d` |
| `SkipList_Reset` | `0x140541050` | JMP `0x141c98300` to zero all 512 counter dwords, then replay the original prologue |
| Missing counters | `0x141c99000` | 256 dwords in `.f1data` |
| Inspected counters | `0x141c99400` | 256 dwords following the Missing counters |

**Threshold = more than 30% after at least 10 inspected parts.** Exactly 30%
continues. Percentage immediate: VA `0x141c9804f`, file `0x1B6824F` (`1e`).
Minimum-inspected immediate: VA `0x141c98035`, file `0x1B68235` (`0a`).

New section `.f1code` is RX at RVA `0x1c98000`, raw offset `0x1b68200`,
size `0x400`. `.f1data` is zero-initialized RW at RVA `0x1c99000`, size
`0x800`. `SizeOfImage` is `0x1c9a000`; no RWX section is introduced.
Two sorted `RUNTIME_FUNCTION` records are appended within existing `.pdata`
padding for the call-bearing handler frame (`0x1c98059..0x1c980f8`) and reset
frame (`0x1c98300..0x1c98324`).

On threshold, the patch calls `SkipSubPanel`, then scans the zone count represented
by `CAO+0x2448..+0x2450` against production-zone records rooted at `CAO+0x5878`
(zone stride `0x410`, anomaly stride `0x370`). Matching inspected anomalies call
virtual slot `+0x48` (`CAnomalieProd::RazRes`) and receive skip cause
`CAnomalie+0x2c = 1`. The triggering component takes the stock early cleanup
path before its Missing mask is stored. Other sub-panels are not modified.
The handler reproduces the stock UI sequence using message value
`[0x1411dcb30]` and `PostMessageA` IAT slot `0x140d5bc00`.

Static verification: source hash guard passes; independent PE parsing confirms
both new sections and permissions; all direct and indirect call/jump targets
disassemble correctly; the reset clears `0x800` bytes; strict threshold boundary
tests pass; and the failed SPC fixture has exactly 10 Missing records on
sub-panel 6. A fresh Ghidra import disassembled 66 handler instructions and 11
reset instructions. Does not patch either DLL or touch `C:\VIT`.

Station trial `trial_1` with `SKIP_TRIAL_2nd.tst` verified the 2D-style result:
sub-panel 6 was skipped and displayed as skipped at review, while deliberately
introduced failures on other sub-panels remained normal failures. The TST had
no pre-enabled optical skip marks.

The station reported zone processing of `31.834|30.589` seconds versus
approximately 4.8–5.1 seconds in nearby normal cycles. Two gaps totaling
18.094 seconds end in failed OTR attempts to open
`C:\VIT\Data\Libraries\MIAMI_3D\MIAMI_3D.bm`; another 5.146-second gap ends in
empty-histogram image errors. These timestamps locate the bulk of the delay in
fault/image/OTR processing but do not directly instrument the threshold
handler. Repair the MIAMI_3D library/OTR configuration before comparing
throughput with this deliberately taped, 21-defect panel.

The production-screen notification was added after this trial. Static checks
and a fresh Ghidra import verify its stock message target and `PostMessageA`
IAT call; the final import disassembled 66 handler instructions and 11 reset
instructions. One short station run should confirm section D now displays
sub-panel 6.
