# Correct Vision3D build — Feature 1 map

Confirmed 2026-09-14. Do **not** reuse addresses from `C:\VIT` (70.05.51.00 / 2019-09-20).

## Qualification waiver, 2026-09-22

The user removed the isolated Windows 7 Embedded x64 environment requirement
and accepted proceeding with the associated qualification risk. See
[W7-QUAL-01](plans/robust_patch_revision_2a.md#w7-qual-01---accepted-qualification-waiver).
Native target compatibility, unwind/exception dispatch, owner-state selection,
and callback-retirement qualification remain **waived - unverified**, not passed.
Unavailable target testing no longer blocks progress by itself. Available offline
checks and remaining implementation contracts still apply; no native execution,
installation, or production release is authorized by this waiver. Historical
statements requiring isolated target qualification are superseded within this
scope; recorded observations and failures are unchanged.

## Synchronous exception cleanup, 2026-09-22

The offline verifier now pins the synchronous body's C++ unwind/IP-state maps
and executes 15 bounded cleanup-action fixtures. Stock cleanup destroys local
vector storage and routes string/logger destruction; no selected action directly
performs the explicit inspection-slot release. Exceptional slot ownership and
outer caller containment remain unresolved, not inferred from local destruction.
Imported and virtual destructors are stubbed; native exception dispatch is not
tested and remains covered by W7-QUAL-01. This local-cleanup checkpoint passed
36 tests. No Rev6 artifact or installation change was made. See the
[cleanup evidence](plans/robust_patch_revision_2a_status.md#synchronous-c-exception-cleanup-evidence-2026-09-22).

## Slot retirement and caller unwind, 2026-09-22

Latest verifier: **39 tests pass in 17.189 seconds**. Twenty bounded release and
deletion cases demonstrate decrement-before-delete, repeated-release risk,
storage-helper failures before unlocking/retirement, and an ignored semaphore
failure. The immediate dispatcher and receiver have no local catch. Imported
storage operations and higher handlers remain unverified; these passing tests
record failure counterexamples, not a cleared exception gate or native failures.
No binary changes or new hooks were made, and W7-QUAL-01 is unchanged. See
[slot-retirement evidence](plans/robust_patch_revision_2a_status.md#synchronous-slot-retirement-and-caller-unwind-2026-09-22).

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

Matching-version `BaseTools.dll` was supplied by the user as the original file
on 2026-09-21. Product/FileVersion **70.06.59.00**, size 1,910,272 bytes,
SHA-256 `a41b4b00cf464da7da886f2303e6161f4474bda29b32793d39e4c6cfc39547f8`,
image base `0x180000000`, AMD64. Its exact exported
`?Stop@CViThread@@QEAA_NAEAKK@Z` is at RVA `0x7e1a0` (ordinal 1151).
This version/export match and user-supplied provenance do not independently
establish the DLL deployed on any station. See
[the static stop evidence](maps/rev2a_basetools_stop.json).

Matching-version `ViVirtualMachine.dll` and `ViVirtualMachineBuilder.dll`
were supplied on 2026-09-23. Both are AMD64, Product/FileVersion
**70.06.59.00**, preferred base `0x180000000`, and neither has an
Authenticode signature. Builder size 1,013,248 bytes, SHA-256
`5e808e294d1f19fa7b8bd5e2d994d4820963d5c1fdea064e572457c9597679b7`.
Machine size 1,144,320 bytes, SHA-256
`5b62adea102b62a272860bfba72cb787bf74bd006f44fe97453df5121efeeb60`.
The builder forwards `CVMachineController::CVMachineController` into the
machine DLL. These copies were not loaded or executed, and their paths do
not establish the station's loaded modules. See the destroy-path detach
evidence in [document lifecycle](maps/document-lifecycle.md).

Ghidra project (analyzed):

`C:\Users\s_sme\Documents\Projects\vision_3d_skips\v3d_files_uncomp\V3D_SKIP.gpr`

Programs in project: `/Vision3D.exe` (138 607 functions), `/AvVTraitLib.dll` (144 752 functions). Both `Analyzed=true`.

## Lifecycle evidence additions (2026-09-22)

Manual-skip writer continuation for the exact EXE hash above:
[explicit stores](maps/rev2a_skip_policy_stores.json),
[registry and sampled writers](maps/rev2a_skip_policy_writers.json),
[single-lane paths](maps/rev2a_skip_policy_single_lane.json),
[dialog stores and production continuation](maps/rev2a_skip_policy_dialog_stores.json),
and [permission-gated dialog handler](maps/rev2a_skip_policy_dialog_handler.json).
RegistryRead `0x1404ddcd0` assigns `Production.ManualSkipLane1 != 0` at
`0x1404de097`; dialog command `0x820` sets dialog `+0xa40` at `0x1405c4b23`,
and standard start copies it to application `+0x18d` at `0x1404dbb56`.
Remote single start clears the byte at `0x1404d4564`. Single-lane operation
alone therefore does not supply a zero-policy invariant. Four bounded registry
conversion fixtures pass; no native target execution, policy restriction,
patch-site expansion, or gate promotion is implied. See
[scope and limitations](maps/document-lifecycle.md#manual-skip-policy-writers).

Reset/reuse continuation for the exact EXE hash above:
[reset callers](maps/rev2a_skip_reset_callers.json) retain PrepareExecData
`0x14068f0f0`, ReloadDoc `0x140692af0`, and HandlerProduction `0x1406a20d0`.
Preparation decision `0x14068f74e..0x14068f7dc` selects no reset, reapplication
at `0x14068f7ca`, or reset at `0x14068f7d7`. The new
[reapply extraction](maps/rev2a_skip_prepare_reapply.json), `0x14052e910`,
queries membership at `0x14052e9d3`/`0x14052eafc` and invokes CAD virtual
`+0xd8`. ReloadDoc resets at `0x1406937d7` and restores snapshot entries at
`0x140693811`. The cycle-start branch at `0x1406a2d7a` bypasses reset
`0x1406a2d87` when lane-zero application byte `+0x18d` is nonzero.
Stock bytes and bounded decision fixtures are checked in the existing verifier;
see [limitations and next proof](maps/document-lifecycle.md#reset-and-reuse-boundaries).
This does not promote the reset/reuse gate or change the approved patch design.

Station-supplied [mfc140.dll](v3d_files_/mfc140.dll) intake: AMD64/PE32+,
version `14.23.27820.0`, size 5,784,856, preferred base `0x180000000`, SHA-256
`0cf26008fae0cb61dfe49e1c3fc17e0dd860be011d9a6a64b452f56335bafbfe`.
Host Authenticode: Valid/Microsoft. Ordinal 3959/8850/11881 RVAs are
`0x21ab10`/`0x21f890`/`0x279280`; raw export and stock-EXE import checks pass.
The [intake record](maps/rev2a_mfc140_station_intake.json) supersedes the
acquisition deferral, not lifecycle proof. Original installed path and loaded
module identity remain unverified. At intake no DLL loading, Ghidra import,
target execution, or binary modification occurred; that run passed 24 tests.
Subsequent [MFC static analysis](maps/document-lifecycle.md#station-mfc-static-analysis)
used separate project `MFC140_STATION`, with PDB analyzers, Function ID, and
Decompiler Parameter ID disabled. Analysis completed in 151 seconds. Import
consulted host dependency/export metadata; inferred names are not proof of
station dependencies. Twenty-eight reports retain 51 byte-verified functions: the
unfiltered pump, nested modal-pump path, guarded base close, bound virtuals,
application recovery receiver, production-frame destruction, and view teardown.
The constructor proves document vtable `0x140ea3868`, correcting the previous
eight-byte-late anchor; close is at `+0x118`, deleting wrapper at `+0x8`.
The production frame factory installs vtable `0x140ea1720`; `+0xd0` binds
ordinal 3803 / `0x1802abb20`, which sends `WM_MDIDESTROY`. Application
`+0x208` binds ordinal 5167 / `0x1801d0230`, whose cached paths preserve
`+0x120` even with feature bits clear. The allocated receiver's close methods
perform recovery bookkeeping. The production-view vtable `0x140eac650` binds
inherited `WM_NCDESTROY` to deleting-wrapper dispatch through `+0x250`.
The destructor chain reaches MFC `RemoveView`, which unlinks/decrements the
view list before clearing `view+0xe8` at `0x18021fb0d`, then notifies document
slot `+0xf0`. Clearing auto-delete flag `+0x120` selects frame-count updates
instead of close; it does not suppress all callbacks. Actual pool/block-release,
document-update, and iterator instructions now run in six fixtures. For an empty
list with auto-delete disabled, all three frame-update passes return without
visibility or frame calls. Other cases cover hidden views with visibility stubbed;
the imported allocator remains stubbed.

Window detach `0x18028f560` calls noncreating map lookup `0x18028f3c8` and
key removal `0x180236b90` before clearing HWND `+0x40` and field `+0xd0`.
Thirteen fixtures execute cached or fresh module/thread-state selection, actual map mutation,
and empty-map bucket/block cleanup, checking missing/colliding keys and
zero/one/two-block release. Freed storage is overwritten by allocator stubs;
the HWND and document fields stay live during cleanup. A decoy TLS state is
untouched. Windows TLS, critical-section calls, CRT division, and allocation
remain stubbed. Nine thread-slot cases separately check cached, missing, invalid,
and unallocated state, stopping before factories, allocation, or failure handling.
The fresh-state case executes factory, zero-filled allocation wrapper, constructor,
and publication into an existing TLS array. A two-case constructor test proves
map `+0x28` is preserved; its initial zero comes from allocation. In two constructed
owner-mismatch cases, detach clears the view and returns the HWND while another
slot's owning map retains its entry. Successful initialization is therefore not
ownership recovery. Correct owner-thread/module/map selection must be established
on the target; no station occurrence of this mismatch is asserted. TLS growth,
default-module fallback, and native allocation/exception handling are unqualified.
Windows delivery of this static detach path and live callback retirement remain
unresolved. Full suite: **34 tests pass in 5.578 seconds**,
including six stubbed MFC pump scenarios, thirteen cached receiver cases, and
three frame destruction cases, plus the six integrated detach cases, thirteen window
map cases, nine thread-slot cases, two constructor cases, and six document-callback
branch cases. The constructor, import-binding, and detach tests passed in 0.332 seconds. OS delivery and
earlier teardown reentry remain unproved.
No native DLL execution, modified PE, or Rev6 builder was produced.
The same verifier later passes **41 tests in 17.701 seconds**, including the
`CMainFrame` title-slot and active-document checks in
[document lifecycle](maps/document-lifecycle.md).
That result does not pass a lifecycle gate.
It now passes **42 tests in 17.815 seconds**. The added check binds the
system `mdiclient` created at frame `+0x1d8` and reproduces, on this
development host's user32 only, `WM_DESTROY` of an MDI child before
`WM_MDIDESTROY` returns. That does not identify the production view's parent
and does not pass a lifecycle gate.
The same verifier then passes **43 tests in 18.301 seconds**. The added check
covers the supplied `AvImgBuffer.dll`: `CZoneStorage` construction can throw
`bad allocation` after `SlotDelete` has entered its critical section and
before it leaves. That does not pass exception containment.
It then passes **44 tests in 20.423 seconds**. The added check covers the
supplied `HwCommonTools.dll`: receiver unwind state 16 destroys the live
`CZoneData` through a noexcept destructor with no catch. That does not pass
exception containment.
It then passes **45 tests in 21.204 seconds**. The added check parents the
production view dialog to the `CProductionChild` HWND. The view's destroy
clears that child's `+0x170`; the title read uses the top frame's separate
field. That does not pass a lifecycle gate.
It then passes **46 tests in 20.760 seconds**. The added check follows
`CProductionView` from template `+0xc0` through the create context and
`MDICREATESTRUCT+0x30` into `OnCreateClient`. That does not pass a lifecycle
gate.
It then passes **47 tests in 21.272 seconds**. The added check shows the
title function reads the frame's own `+0x170` first and skips the active
child's document when that read is non-null. The view destroy clears the
child frame, and the EXE does not import SetActiveView. The title still
returns the production document when the top frame's own field holds that
view. That does not pass a lifecycle gate.
It then passes **48 tests in 21.366 seconds**. The added check shows the
production templates register `CProductionDoc`, whose slot `+0x320` calls
ordinals 1504 and 1032. The helper that writes `+0x170` from document
`+0x258` is the `CDocProcess` slot, registered under resource ids `0x7c8`,
`0x7ca`, and `0x7cb`. That does not pass a lifecycle gate.
It then passes **49 tests in 21.312 seconds**. The added check follows the
production view's print-preview slot through ordinal 9697. Its
SetActiveView call uses the nearest `CFrameWnd`; `CProductionChild` derives
from `CMDIChildWnd` and `CFrameWnd`, so that path selects the child frame.
That does not pass a lifecycle gate.
It then passes **50 tests in 21.303 seconds**. A development-host user32
probe confirms that `DestroyWindow` removes an already queued instance of
the exact registered SKIP message and that a later post to the stale HWND
fails. This is not Windows 7 qualification and does not cover producer-side
object dereferences or posts racing before destruction. No lifecycle gate
is promoted.
It then passes **51 tests in 23.948 seconds**. The added check shows the
constructor stores zero at `document+0x5838`, `OnInitialUpdate` is the only
later write and stores the view, and the three SKIP posts use that pointer's
HWND without testing it. Production close destroys listed view frames before
the destructor releases the skip arrays. An empty view list can still reach
that destructor. No lifecycle gate is promoted.
It then passes **52 tests in 24.325 seconds**. The added check shows a null
HWND post is a thread message. The SKIP handler occurs only in the production
view map, and the application map has no registered-message entry. On this
development host `DispatchMessageA` does not deliver that thread message to a
window procedure. The embedded menu-bar pretranslate and a nonzero
`frame+0x120` can still observe it. No lifecycle gate is promoted.
It then passes **53 tests in 28.805 seconds**. The added check shows
`CExtMenuControlBar` slot `+0xa90` returns zero for a registered id and its
`SendMessageA` sites use `0x157` or `WM_CANCELMODE`. `CMainFrame` then
tail-jumps ordinal 11812, which calls `[frame+0x120]+0xb8` only when that
qword is nonzero. Construction stores zero, and the three frame vtables do
not store a replacement. No lifecycle gate is promoted.
It then passes **54 tests in 29.330 seconds**. The added check shows the
production view map has no `WM_CREATE` entry and bases on the `CFormView`
map. That handler restores the create context from `view+0x138` and jumps to
`CView::OnCreate`, which calls `AddView` when the context document is
non-null. `AddView` links the view and increments `document+0x70` before
ordinal 8734 selects the non-close slot. `CFormView::Create` installs a
`WH_CBT` hook and saves the create context before
`CreateDialogIndirectParamA`. The procedure stored at module-state `+0x70`
is the remaining delivery link. No lifecycle gate is promoted.
It then passes **55 tests in 29.461 seconds**. The added check shows the
create hook stores the view at thread-state `+0x28`, attaches its HWND, and
subclasses to module-state `+0x70`. The view constructor stores
`AfxGetModuleState()` at `+0x38`. The process state and the DLL static state
store procedures that call `AfxWndProc`. Message 1 reaches `CWnd::OnWndMsg`,
follows the production map's base, and calls the `CFormView` `WM_CREATE`
handler. No lifecycle gate is promoted.

Target OS, user reported: Windows 7 Embedded x64. Development-host tests are
not station validation. The previously supplied `mfc140.dll` version 14.0.24210.0, size
4,705,072 bytes, SHA-256
`f8becf698ba1068cfc32e72e210215a1ed4368cdd5f21ea45bf393677dbd77c6`
is x86 (`Machine=0x014c`, PE32, image base `0x10000000`), not AMD64. It is
rejected as the dependency of the mapped x64 EXE and was not imported.
Its ordinal 8850/11881 RVAs `0x95c80`/`0x278ee0` are recorded only for intake,
not as evidence of the x64 pump or close implementations. See
[the intake record](maps/document-lifecycle.md#supplied-mfc-intake-2026-09-22).

The [document lifecycle map](maps/document-lifecycle.md) records the retained
publication, live SKIP-array access, UI-command, supervisor pump, and teardown
addresses for this exact EXE. Supporting descendant entries are `0x1404e0b60`,
`0x140697ab0`, and `0x1406abfe0`. The
[helper `0x140675f90`](maps/rev2a_skip_posted_ui_helper.json) tail-calls
`InvalidateRect` via IAT `0x140d5bc90` on HWND at `view+0x8b0`.

The [document constructor `0x14067dea0`](maps/rev2a_skip_document_sheet_construction.json)
calls sheet constructor `0x1406c3a30` at `0x14067dfef` with `document+0x3990`.
Its [vtable installation](maps/rev2a_skip_embedded_window_binding.json) at
`0x1406c3a5d` writes `0x140eb0360`; RTTI pointer `0x140eb0358` selects locator
`0x140f14428`, identifying `SkipProductionElmt_Sheet`. The
[sheet destructor](maps/rev2a_skip_embedded_window_destructor.json) is `0x1406c3bf0`.
Slot `0x140eb0640` (`+0x2e0`) selects
[thunk `0x14077f754`](maps/rev2a_skip_embedded_window_virtual.json), IAT
`0x140d5ec88`, `mfc140.dll` ordinal 3959, labeled `CPropertySheet::DoModal`.
These records use the exact stock EXE hash above and resolve static bindings
only; the supplied MFC's corresponding static paths are now mapped above.
Live runtime behavior remains unverified and no gate is promoted.

Supplied `DyTools0.dll`: AMD64, size 2,742,784, image base `0x180000000`, SHA-256
`f5421b5509236d6a5ba7b20c6e764f0af5e0be131bf2b08e2bbe774ac805767e`.
EXE call `0x14064b8fb` uses IAT `0x140d53fc0` for `?DoEvents@@YAXXZ`, DLL export
ordinal 1468 at `0x1800772b0`. Peeks at `0x1800772c9` / `0x1800772fe` are
unfiltered; thread lookup is `0x1800772d3`, virtual `+0xc8` call `0x1800772e3`.
See the [stock-byte-verified body](maps/rev2a_skip_doevents.json).

Application vtable `0x140e39770` (installed at `0x1404ce01f`) maps `+0xc8` to
`0x14077f982`, IAT `0x140d5fd20`, `mfc140.dll` ordinal 11881. Base document-close
thunk `0x14077fe26` maps IAT `0x140d5f5f8` to MFC ordinal 8850. These are import
bindings; the supplied station MFC bodies have subsequently been analyzed as
recorded above. Loaded-module identity and runtime behavior remain unverified.
The historical 20-method run included five bounded DoEvents fixtures; the
current 32-method result supersedes it. No lifecycle gate or runtime
qualification is claimed.

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

## Review-station handoff anchors (70.06.59.00)

Static mapping confirms that `CMsgPanelProd::SendPanelToReviewStation` is a
message-field setter, not a file-transfer function.

| Stage | VA | Confirmed behavior |
| --- | --- | --- |
| Review gate | `0x140674820` | Writes `CProdCarte+0x40` |
| Serialized gate call | `0x14069b4d8` | CAPM commit calls review gate |
| Prepare messages | `0x14068fab0` | Builds panel result and consumes route byte |
| Route-field call | `0x140690572` | Calls `0x14067c710` |
| Mark for repair | `0x14067c710` | Stores inverted value at `CMsgPanelProd+0x0c` |
| Results event | `0x14067c5b0` | Wakes communication thread |
| Communication handler | `0x14067c480` | Calls `SendResults` at `0x14067c56c` |
| Send results | `0x14067c7b0` | Sends ready anomaly images, then panel message |
| Network wrapper | `0x14064e110` | Calls imported `CTalkToSuperviseur::Send` |

Review images come from `CAnomalie+0x188` memory populated by
`CVitImgFileRecorderHelper::Save` with mask `0x4`; `.ois` (`0x1`) and `.otr`
(`0x2`) writes are separate recorder branches. Full map:
[`maps/review-station-handoff.md`](maps/review-station-handoff.md).

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
