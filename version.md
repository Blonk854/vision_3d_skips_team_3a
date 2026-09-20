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

## Concurrency correction candidate (2026-09-20)

Current default output: `Updated\Vision3D_concurrency_fix.exe`

SHA-256: `0ef39ff59e216bb7e9a45f6cb7ee505eac0822f6c4939d8ff1a8e04197675c13`

Size: 28,746,240 bytes. The original source and both companion DLL hashes above
remain mandatory. The previous `Updated\Vision3D.exe` is preserved.

The existing entry point delegates to `tools\patch_f1_missing_n_rev5.py`:

```powershell
python -m pip install -r tools\requirements.txt
python tools\verify_hardened_patch.py --code-only
python tools\patch_f1_missing_n.py
python tools\verify_hardened_patch.py
```

Corrections:

- Worker, finalizer and optical-skip wrapper reference acquisitions now use
  `lock inc`, matching the concurrent `lock dec` releases.
- Context lookup searches every slot for a matching CAO before allocating the
  first empty slot. Retiring an earlier context cannot duplicate a later one.
- The table lock covers both count updates, threshold evaluation and claim.
  It is released before waiting for a winner, the skip lock or a stock call.
- Invalid-layout finalization jumps directly to reference release/review and
  cannot clear another thread's subsequently acquired table lock.

Hook addresses, section layout, frame prologues and unwind records are unchanged
from the historical map below. Handler byte sizes are now: worker 606, reset
240, finalizer 677, stock wrapper 317; cleanup handlers remain 27/57/61.

Validation: deterministic Unicorn instruction-level concurrency regressions,
four independently rejected defect reintroductions, complete handler decoding,
artifact/source/DLL hashes, generated payload equality and an allowlisted PE
byte diff all pass. Stock calls are stubbed during emulation. Windows exception
dispatch, live scheduling, cycle time, database/SigmaLink behavior and the
station release matrix below remain unverified for this candidate.

A fresh Ghidra 12.1 import with analysis disabled succeeded using the PE loader
and `x86:LE:64:default:windows`. The disposable project was deleted. Missing
station-library and export warnings mean this was a PE import check, not a
complete dependency validation or a new Ghidra analysis of injected code.

## Historical hardened hook and patch (2026-09-19)

Source (immutable): `v3d_files_\Vision3D.exe`  
SHA-256: `ccca11b2f05084b484fa5556c67f8874065dbc0b6265177d2517f81265af00f4`

Matching DLL guards:

- `AvVTraitLib.dll`: `0f9f68b118112cea87e1735995776934d8d009e3d6d39a8a58562e3fa3e3e5f7`
- `StructSupport.dll`: `d6270dbe5c97b5ed1000c2541c1e8d495d7db6be184e45d6495d7fad75e0f832`

Output: `Updated\Vision3D.exe`  
SHA-256: `0d1bb6fda6eb4b4a79042adf14bff0679467413c2f08183504047da7b717998e`
Size: 28,746,240 bytes (8,192 bytes larger than source).

Rebuild and verify:

```powershell
python -m pip install -r tools\requirements.txt
python tools\patch_f1_missing_n.py
python tools\verify_hardened_patch.py
```

| Site | VA | What |
| --- | --- | --- |
| Final-mask hook | `0x140736f47` | CALL `0x141c98000`; runs after supplemental defects merge and stock current-anomaly `RazRes` |
| Atomic worker handler | `0x141c98000` | CAO-scoped atomic count/claim, serialized immediate `SkipSubPanel`, current-anomaly normalization, stock early exit |
| `SkipList_Reset` | `0x140541050` | JMP `0x141c98500`; retire/wait/clear one CAO context, then replay stock prologue |
| Serial finalization call | `0x14069b4d8` | CALL `0x141c98700` before `ShouldItGoToReviewStation` |
| Unwind cleanup | `0x141c98b00` | `UNW_FLAG_UHANDLER`; releases the finalizer reference during exceptional unwind |
| Stock-skip wrapper | `0x140736fcb` → `0x141c98c00` | Routes optical-SKIP calls through the same per-CAO lock |
| Stock-wrapper cleanup | `0x141c98e00` | Releases skip/table lock and lifecycle reference during unwind |
| Review-route test | `0x1406748c5` | `0xfffffeff` → `0xffffffff`, including card skip bit `0x100` |

The threshold remains **more than 30% after at least 10 completed
inspections**. Exactly 30% continues. Evaluation occurs after every completed
inspection, including a good tenth result following early Missing results.

### Runtime state and synchronization

- Eight fixed contexts are keyed by `CDataCaoTraitement*` (the stock owner of
  the skip list and production-zone array).
- Each context has 1,024 sub-panel cells with atomic inspected, Missing and
  claim state.
- One table lock serializes context lookup, insertion, retirement and reuse,
  preventing duplicate contexts for the same CAO.
- Worker and finalizer references prevent `SkipList_Reset` from clearing a
  live context. Reset first retires the context, waits for zero references,
  reacquires the table lock, validates identity/state again and then clears it.
- IDs outside `0..1023` and a full eight-context table fail open to stock
  component behavior and increment diagnostics outside all context ranges.

The threshold winner changes its cell from state 0 to 1, acquires the per-CAO
skip lock, calls stock `SkipSubPanel` immediately, releases the lock and
publishes state 2. This preserves stock scheduling behavior. Every worker that
observes state 2 clears only its own completed anomaly's defect mask, writes
skip cause 1 and returns through `0x14073742d`. Workers never walk shared zone
arrays, post UI or call global `RazRes`.

The stock optical-SKIP call at `0x140736fcb` is wrapped by the same lock.
Active contexts are reference-protected, absent contexts hold the table lock
through the stock call so no racing context can appear, and retired contexts
drop stale late calls. Unwind-only handlers release all held locks/references
and return `ExceptionContinueSearch`.

### Serialized commit

`CProductionThread::CAPM_SetInspectionStatus` is the serialized commit point.
The wrapper:

1. acquires a reference to the matching CAO context;
2. pre-validates `CAO+0x5880`, production base `CAO+0x5878`, zone stride
   `0x410`, begin/end ordering, anomaly stride `0x370` and per-zone cap;
3. sets `CAnomalie+0x28 = 0` and `CAnomalie+0x2c = 1` on matching inspected
   prior records without freeing result trees;
4. atomically publishes state 3;
5. posts message `[0x1411dcb30]` through `PostMessageA` IAT `0x140d5bc00`
   once, retrying on a failed post; and
6. calls stock `CProdCarte::ShouldItGoToReviewStation`.

The stock skip-list update occurs immediately in the worker and does not depend
on anomaly-vector layout. Validation gates only the later reconciliation walk.
Invalid layout records a diagnostic, preserves the committed stock skip and
continues through review routing without walking prior anomaly records.

### PE layout and verification

- `.f1code`: RVA `0x1c98000`, raw `0x1b68200`, size `0x2000`, RX.
- `.f1data`: RVA `0x1c9a000`, virtual size `0x29000`, no raw payload, RW.
- `SizeOfImage`: `0x1cc3000`; no RWX section.
- Four sorted `RUNTIME_FUNCTION` entries are appended in existing `.pdata`
  padding. Worker, finalizer and stock-wrapper unwind info references
  unwind-only cleanup handlers that return `ExceptionContinueSearch`.
- Generator guards original bytes at every hook, all three source hashes,
  section-header/pdata capacity and the exact final output hash.
- `tools\verify_hardened_patch.py` independently checks threshold boundaries,
  panel isolation, reset/reference behavior, section permissions, branch and
  call targets, validated reconciliation, unwind bytes/handler targets,
  and absence of worker/global `RazRes`.
- A fresh Ghidra import of the final hash disassembled 119 worker, 55 reset,
  164 finalizer, 67 stock-wrapper and 7/14/14 cleanup instructions.

The script patches neither DLL and never writes `C:\VIT`.

## Station history and required release matrix

The earlier revision passed the small-panel trial: sub-panel 6 was skipped,
shown in section D, unrelated defects remained normal, and a skip-only panel
stopped at review. The Bronco production run then exposed the old mixed-array
bound crash; this hardened revision removes that worker-side scan entirely.

Before production release, execute:

1. 4/10 Missing: skip at result 10; other sub-panels complete.
2. 3/10 Missing: no threshold skip.
3. Early Missing with a good tenth result: evaluate and skip if still above 30%.
4. Threshold skip plus unrelated defects: both representations remain correct.
5. Skip-only: section D displays it and review stops.
6. Two simultaneous threshold sub-panels: one stock skip insertion each.
7. Two lanes using identical sub-panel IDs: no count/state crossover.
8. IDs near 1,023 and an unsupported ID: supported works; unsupported fails open.
9. Immediate next-panel start: no stale counts, reset delay or context reuse.
10. Bronco/foreign-material panel in production mode: no crash and correct DB/UI.
11. Repeat at least 20 panels while monitoring cycle time and Vision3D logs.

The previous trial's long cycle remains attributable to OTR/model/image errors
(`MIAMI_3D.bm` open failures and empty histograms), not to the threshold
handler. Correct that station configuration before throughput comparison.
