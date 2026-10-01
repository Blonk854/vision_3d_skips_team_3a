# Robust Patch Revision 2a - Implementation Status

Recorded: 2026-09-22

## Current decision

Final-mask multiplicity, **still partial** on 2026-09-25. One component call
reaches `0x140736f47` at most once. A multi-section bound of 2 can enter
`PanelInspect` twice before reset. The finding is
[Final-mask multiplicity](#final-mask-multiplicity-2026-09-25).
The original plan still requires a uniqueness proof before assembly changes.

DWORD arithmetic remains the original plan obligation: prove the products
against a supported workload maximum, or use justified wider intermediates.
A 64-bit product candidate is recorded in
[Wider-intermediate candidate](#wider-intermediate-candidate-2026-09-25).
It is not implemented, and it does not close the gate.

Callback retirement stays blocked. Stock close, cycle-start, and reset spans
do not drain the live-array reader. A snapshot and notification candidate is
recorded in
[Snapshot and notification candidate](#snapshot-and-notification-candidate-2026-09-24).
That candidate is not implemented. Earlier sentences that leave the gate
blocked remain the disposition.

Qualification update, 2026-09-22: the user removed the isolated Windows 7
Embedded environment requirement and accepted proceeding with the associated
risk. [W7-QUAL-01](robust_patch_revision_2a.md#w7-qual-01---accepted-qualification-waiver)
records native target qualification as **waived - unverified**, not passed.
Unavailable target unwind/exception and owner-state/callback traces no longer
block progress by themselves. This supersedes earlier isolated-target prerequisites
below. Known defects, failed checks, and other implementation contracts are not
waived. Native execution, installation, and production release remain separately
authorized actions; this instruction is not a signed production-release approval.

Scope update, 2026-09-22: the user confirmed this patch will only be used on
single-lane machines. Dual-lane machines are unsupported and excluded from
deployment. Cross-lane validation is removed from the entry/release gates and
F1-H is not applicable, not passed. All remaining lifecycle, ownership, callback,
concurrency, reuse, and exception obligations apply to the supported single lane.

Rev6 assembly and candidate publication remain blocked by the unresolved,
non-waived section 1 implementation contracts, not by lack of a Windows 7 lab.
The repository proves the five stock patch locations and local hook flow, but it
does not yet prove the lifecycle and ownership assumptions required by the plan.
No rev6 executable was generated, published, installed, or executed.

The user approved expanded offline admission/drain repair beyond the five feature
hooks on 2026-09-21. Two guard candidates now pass source-verified instruction
emulation. This permission does not waive lifecycle proofs, approve publication,
or authorize native Vision3D execution. The candidates are not integrated into a
Rev6 generator and do not yet establish safe failed-drain containment.

The user subsequently approved synchronous containment with reduced parallelism.
An additional emulator-only GetThread entry replacement now forces the covered
dispatcher through its stock synchronous fallback. Nineteen tests now pass,
including actual synchronous-body instruction execution with descendant stubs
and a native Windows virtual-unwind check of non-executable copied entry bytes.
This is a startup-only admission suppression candidate, not a repair for
already-outstanding work or a passed lifecycle gate.

Recorded design, 2026-09-24: a SKIP snapshot/notification alternative for the
live-array reader is written down. The traced close paths contain no stock
barrier. Indirect calls and unexpanded virtuals stay outside the stock-barrier
claim. The production capture set is in
[Snapshot and notification candidate](#snapshot-and-notification-candidate-2026-09-24).
The callback-retirement gate stays blocked. This record does not build Rev6
or authorize a patched executable. See
[Command-view document](#command-view-document-2026-09-24).

Latest offline checkpoint, 2026-09-24: when `WaitVMC_IsStarted`
(`0x1406a9db0`) returns 1, `HandlerProduction` calls
`CProductionThread::PanelWaitCycleStart` (`0x1406a7a40`) at `0x1406a2b91`.
The return-1 arms are VMC state 6, "VMC is waiting a panel.", and state 7,
"VMC is loading a panel." Those arms log and return without the 10 ms wait.
`PanelWaitCycleStart` calls `WaitForMultipleObjects` on `[thread+0x188]`,
`[thread+0x18]`, and `[thread+0x1a8]`, with count 3, `bWaitAll` 0, and timeout
2000, or infinite when `[document+0x3848] == 1`. Its body imports neither
`SendMessageA`, `PeekMessageA`, nor `DispatchMessageA`. The first-handle arm
returns 1 and does not set `thread+0x32`. The caller stores that return in
`r12` and joins at `0x1406a2ce3`. While `thread+0x32` is not 1, that join
falls through toward `SkipList_Reset`. The wait does not drain the live-array
reader. The callback-retirement gate stays blocked.

Earlier the same day: `HandlerProduction` calls
`0x1406a9db0` at `0x1406a2b81` before `SkipList_Reset`. That function calls
slot `+0x30` of the object at `thread+0xeb8`. The only store of that field
is the second argument of `0x1406999f0`, and its only caller passes the
return of document slot `+0x230`. The controller vtable `0x1800ceda8` binds
`+0x30` to `0x180070ed0`, which reads `[controller+0x860]` and returns the
dword at `+0x10`. The default arm then calls `WaitForMultipleObjects` on
`thread+0x18` and `thread+0x1a8` with count 2, `bWaitAll` 0, and timeout 10.
The body imports neither `SendMessageA`, `PeekMessageA`, nor
`DispatchMessageA`. Its direct-call closure contains neither skip refresh
nor the skip handler. The wait does not drain the live-array reader. The
callback-retirement gate stays blocked.

Earlier the same day: the send at `0x1406a2b79` calls
`0x140685b70` before `SkipList_Reset`, but that function sends the message id
in `0x141193470`. That id is registered from `{5D5B3537-9C21-4d59-AEB5-EA30A0D68618}`,
not the skip GUID. The only value loads of the skip ids are three `PostMessageA`
sites. `0x140685b70`'s direct-call closure contains neither skip refresh nor
its handler. The send does not drain the live-array reader. The
callback-retirement gate stays blocked.

Earlier the same day: `HandlerProduction` posts message
`0x87d6` at `0x1406a27fa`, then calls `SkipList_Reset` at `0x1406a2d87`. No
wait, send, or critical-section import sits between those addresses. The only
`.rdata` map entry for `0x87d6` is handler `0x1406b2320`. Its direct-call
closure contains neither skip refresh nor `SkipList_Reset`. The post is not a
drain of the live-array reader. The callback-retirement gate stays blocked.

Earlier the same day: refresh and the five reset callers both
reach `EnterCriticalSection` inside `0x140780a98`, `0x140780af8`, and
`0x140780bbc`. Those helpers take a global section, update thread-local state,
and release it before returning. None calls `SkipList_Reset`. The live reloads
at `0x1406adb67` and `0x1406adbb0` stay in refresh, after it calls the string-list
helper. Reset's closure also enters the critical section in `0x140578c80`;
refresh never reaches that function.

Earlier the same day: `SkipList_Reset` mutates the skip array
through `mfc140.dll` ordinal 13522 with size 0 and grow-by -1. That ordinal's
zero-size path loads the data pointer, calls `free`, stores zero at `+8`,
`+0x18`, and `+0x10`, and returns. The span has no other call. The negative-size
branch is the only path to the throw. Refresh still reloads the live data
pointer and count. No shared lock covers both. The callback-retirement gate
stays blocked.

Earlier the same day: refresh rereads the live array, and the
destructor does not join the producer before freeing it. `0x1406adb67` reloads
`[array+8]` and `0x1406adbb0` reloads `[array+0x10]` on every loop iteration.
The direct-call closure of `0x14051fbf0` through the free at `0x14051fd3a`,
including `0x14053c250` and `0x140527b50`, contains no `+0x3868` displacement
and no wait or `CViThread::Stop` import. `document+0x1a90` is a name container:
its constructor is `0x14051d5f0`, and its inserter `0x140725ec0` receives
`CString` finder names. That is not a producer join.

Earlier the same day: refresh and reset do not share a call.
`0x14067ab20` and `0x14067a420` are called only from SKIP refresh `0x1406adaf0`,
on either side of `SkipList_Get`. None of the five `SkipList_Reset` callers
calls either helper. `CDataCao::~CDataCao`'s direct-call closure imports no
`user32`. That closes the shared-lock hypothesis. It does not promote callback
retirement: refresh still reads the live array, reset still mutates it, and
document close still does not join the producer. No Rev6 PE was built.

Earlier the same day, **134 tests pass in 144.958 seconds**.
The extended case is `test_cdata_cao_element_destructors_do_not_join_the_producer`.
In addition to local cleanup coverage, 20 release/deletion cases pin mutation
before deletion, repeated-release risk, storage-helper failure boundaries, and
an ignored semaphore failure. The immediate dispatcher and receiver have no
local catch. These are regression evidence for unresolved failure handling, not
a passed exception gate; see [slot retirement](#synchronous-slot-retirement-and-caller-unwind-2026-09-22).

## Snapshot design record, 2026-09-24

A snapshot/notification alternative for the SKIP reader is recorded here.
Rev6 assembly, candidate publication, and callback retirement stay blocked.
No generation counter is included. Operator skips are left stock.
`tools/verify_worker_admission.py` is unchanged.

The reader is refresh `0x1406adaf0`. It reloads the live data pointer at
`0x1406adb67` and the live count at `0x1406adbb0` on every iteration. Those
reloads use the embedded `CUIntArray` at `document+0x23e0`. A valid snapshot is
owned bytes, captured at a defined point, with the same skip membership the
stock array had at that point. After the snapshot is published, refresh reads
that buffer only. It does not dereference the live pointer or count again.

Capture runs on the mutating thread after a normal return from each retained
mutator of that array:

| Mutator | Entry | Role |
| --- | --- | --- |
| `SkipList_Reset` | `0x140541050` | `SetSize(0, -1)` through MFC ordinal 13522. The zero-size path frees the buffer and stores zero at `+8`, `+0x10`, and `+0x18`. Callers: `0x1404aebe9`, `0x14068f7d7`, `0x1406937d7`, `0x1406a085e`, `0x1406a2d87`. |
| `SkipList_Add` | `0x140541020` | Tail-calls `CUIntArray::SetAtGrow` on the same array. No local lock. |
| `ReloadDoc` restore | `0x140693811` | After reset at `0x1406937d7`, restores saved entries with `lea rcx, [rsi+0x23e0]` and a direct `CUIntArray::SetAtGrow`. This call does not go through `SkipList_Add`. |

The capture point is that normal return. Membership is the post-mutation stock
list, including an empty list after a production-cycle reset. A capture set that
stops at `SkipList_Add` misses the `ReloadDoc` restore: refresh would keep the
empty post-reset snapshot while stock grows the live array one `SetAtGrow` at a
time. Each normal `SetAtGrow` return in that loop publishes the membership stock
has at that return. `RegistrySave` (`0x1406928d0`) still reads the live count at
`+0x23f0` and the live entries at `+0x23e8` on the close path. It is not this
reader, and this contract does not yet move it onto the snapshot. A callback already
inside refresh keeps the snapshot it loaded at entry, so a reset or `SetAtGrow`
that lands mid-dispatch cannot tear the pointer and count. A throw from the
mutator leaves the previous snapshot published. The stock call is not repeated.

Publication is one release store of the snapshot pointer. Refresh acquires it
once per dispatch. An older snapshot stays allocated until every dispatch that
loaded it has returned, including a dispatch that runs after the document
destructor frees `+0x23e0` with no message pump. The producer may `PostMessageA`
again after any pump returns, including `DoEvents` at `0x14064b8fb` in
`0x14064b880`. The count that keeps an old snapshot alive is a buffer reference
count. It does not identify a panel, result, or CAO generation, and it does not
clear or rewrite operator skips.

The array snapshot does not make entry into a freed production view safe. The
three SKIP posts load `[document+0x5838]` and then `[view+0x40]` with no null
test, at `0x1406a103b`, `0x1406a1075`, and `0x140736feb`. The view destructor
frees the view through MFC ordinal 1487 without clearing `document+0x5838`.
The notification design has to publish the view pointer and HWND into
patch-owned storage when stock publishes `+0x5838`, and clear that pair in the
view destructor before the free. A poster that sees a cleared pair does not
load the document field or the view. A poster that already holds the
patch-owned pair is counted until `PostMessageA` returns, and the destructor
waits for that count before the free. The posted handler still reads the
snapshot. This count is the same kind of buffer/poster reference count, not a
generation counter. DestroyWindow retirement of a queued HWND message remains
host evidence under W7-QUAL-01 and is not the lifetime proof.

This section is the design contract. It does not select patch bytes, allocate
the snapshot, or change the five feature sites. The callback-retirement gate
is not promoted.

## Capture-set review, 2026-09-24

The recorded capture table is not every mutator of the skip `CUIntArray`.
A source-hash-checked scan of `Vision3D.exe`
`ccca11b2f05084b484fa5556c67f8874065dbc0b6265177d2517f81265af00f4` found
direct `SetSize` (MFC ordinal 13522, thunk `0x14077fdcc`) and `SetAtGrow`
(MFC ordinal 12880, thunk `0x14077fdd2`) uses of displacement `0x23e0`
outside `SkipList_Add`, `SkipList_Reset`, and the `ReloadDoc` restore.
No Rev6 PE was built.

| Site | Operation | Why it is the same array |
| --- | --- | --- |
| `0x140540ef0` | `SetSize(0, -1)`, then `SetAtGrow` | Called from `ExecuteSkip` at `0x1406a0e3a` on the `al == 1` arm, before that function's `SkipList_Add` at `0x1406a0e60`. The other arm skips this call. |
| `0x140541080` | `SetAtGrow` of the `edx` value at the live count | Only direct caller is `0x140736fcb`. That call passes `[r15+0x10]` and then loads `[[r15+0x10]+0x5838]`. The body also uses `+0x2448` and `+0x2450`. |
| `0x1405f19a0` | `SetSize(0, -1)` at `0x1405f1a1f`, then `SetAtGrow` at `0x1405f1b9f` | Callers `0x1405f5cb6` and `0x1405fb376`. The body uses `+0x23f0`, `+0x2448`, and `+0x2450`. |
| `0x1405f5660` | `SetSize(0, -1)` at `0x1405f583b` | Five direct callers: `0x1405d7e00`, `0x1405e795d`, `0x1405e7a4d`, `0x1405f514f`, `0x1405fdc69`. The body uses `+0x2448`, `+0x2450`, and `+0x2550`. |
| `0x140692600` | `SetAtGrow` at `0x140692881` | Uses `document+0x3924`. Its only direct caller is `0x14068dcef`. Thirty `int3` bytes sit between `OnCloseDocument` and that call, so this writer is not inside `OnCloseDocument`. |

A capture set that stops at the three recorded returns leaves these writes
on the live array. Refresh would keep an older snapshot while stock membership
changes. The optical-skip call at `0x140736fcb` is one of those writes.

These additional live readers are outside the refresh contract and stay on
the stock pointer and count: `0x1406746d0` (called from `0x140685669` and
`0x1406a5529`), `0x14052e010`, `0x14052dfe0`, `0x140525280`, and
`RegistrySave`. `0x1406746d0` loads `[array+8]` and `[array+0x10]` and passes
each dword to `0x140674760` with bit `0x100`. Moving only refresh does not
move them.

The constructor at `0x14051e164` is the only `+0x23e0` call of MFC ordinal
973, and the destructor at `0x14051fd3a` calls ordinal 1439. Neither is one
of the five runtime mutators above. The callback-retirement gate is not
promoted.

## Capture-point classification, 2026-09-24

Saved decompilation of the five sites is in
[skip_array_extra_mutators.c](../maps/decomp/skip_array_extra_mutators.c).
No Rev6 PE was built. This classification does not amend the recorded
capture table, and it does not close the callback-retirement gate.

| Function | Entry | What the body does |
| --- | --- | --- |
| `CDataCaoTraitement::SkipAllSubPanels` | `0x140540ef0` | `SetSize(0, -1)`, then `SetAtGrow` of ids `1` through `GetNbCartes`. The only caller is `ExecuteSkip`. The body has no `DoEvents` and no `AfxMessageBox`. |
| `CDataCaoTraitement::SkipSubPanel` | `0x140541080` | `SetAtGrow` of the argument when `IsSkippedSubPanel` is false. The only caller is `ExecuteOne_Component`. The following loop updates the execution vector and does not call `SetSize` or `SetAtGrow`. The body has no `DoEvents` and no `AfxMessageBox`. |
| `CDocCompose::AcquireAndCheckSkip` | `0x1405f19a0` | `SetSize(0, -1)`, then `SetAtGrow` of the subpanel id when `CheckSkip` succeeds and that id is nonzero. Callers are `ExecuteArray` and `ExecuteVecteur_Skip_DataMatrix` (`0x1405fb150`). This body has no `DoEvents` and no `AfxMessageBox`. |
| `CDocCompose::ExecuteArray` | `0x1405f5660` | Its own `SetSize(0, -1)` when the third argument is not `-1`, before the call to `AcquireAndCheckSkip` for a section whose flag is 0. |
| `CProductionDoc::RegistryRead` | `0x140692600` | When `CAVisionApp+0x199` is 1, `SetAtGrow` of each saved `Production.SubPanelSkip` value. This function does not call `SetSize`. Its only caller is `OnOpenDocument` at `0x14068dc20`. This body has no `DoEvents` and no `AfxMessageBox`. |

`SkipAllSubPanels`, `SkipSubPanel`, and `RegistryRead` mutate the production
document array that refresh reads. `SkipAllSubPanels` and `RegistryRead` have
the same clear-or-append shape already used for the `ReloadDoc` restore:
each normal `SetSize` or `SetAtGrow` return is a capture point. Waiting until
the outer function returns leaves an empty or partial list unpublished while
the live array changes. `SkipSubPanel` has one array mutation, so its
`SetAtGrow` return is the capture point.

`ExecuteArray` can dispatch after that `SetSize` has cleared the array. The
failure arm calls `AfxMessageBox`. The bench-iteration arm, selected through
the Validation ini value "Bench zone", calls `DoEvents` and then another
`AfxMessageBox`. Those pumps are after the clear. If refresh can run against
that object, publication has to happen at the `SetSize` return.

`ExecuteArray` and `AcquireAndCheckSkip` are `CDocCompose` methods. They use
`+0x23e0`, `+0x23f0`, `+0x2448`, and `+0x2450`. This pass does not prove that
their `this` pointer is the production view's document. They stay unresolved
for the production capture set. The three production-document writers above
are not unresolved: a capture set that omits them leaves live membership
unpublished. The callback-retirement gate is not promoted.

## Compose-document identity, 2026-09-24

`CDocCompose` and `CProductionDoc` are siblings. Neither derives from the
other. Both derive from `CDataCaoTraitement`, so displacement `+0x23e0` is
the same base-class skip array on two different object types. No Rev6 PE
was built. The program was not saved.

| Vtable | RTTI | Bases |
| --- | --- | --- |
| `0x140e76078`, stored by constructor `0x1405cb880` | `.?AVCDocCompose@@` | `CDocCompose`, `CDataCaoTraitement`, `CDocument`, `CCmdTarget`, `CObject`, `CDataCao`, `IVMachineControllerListener`, `ISDMListener<CZoneStorage>` |
| `0x140ea3868` | `.?AVCProductionDoc@@` | `CProductionDoc`, `CDataCaoTraitement`, `CDocument`, `CCmdTarget`, `CObject`, `CDataCao`, `IProductionCommander` |

`ExecuteArray` (`0x1405f5660`) copies incoming `RCX` to `RSI` at
`0x1405f56b2`. Its call at `0x1405f5cb6` passes `RSI` to
`AcquireAndCheckSkip`. The five direct callers of `ExecuteArray` each pass
their own incoming `this`.

These command handlers do not. `0x1406e64a0`, `0x1406e5e80`, and
`0x1406e6030` call `0x1407528c0` and pass the returned pointer.
`0x1407528c0` is `mov rax, [rcx+0xe8]; ret`. The last two functions are
entries in an MFC command map at `0x140ebace8` and `0x140ebad28`. The
window class that owns that map is not identified. `0x14045bf90` loads
`[rcx+0x1a00]`, passes type descriptors `.?AVCWnd@@` and
`.?AVCAnomaliesGridView@@` to `0x1407a6238`, and tail-jumps to the same
`+0xe8` load.

A view can therefore pass its document pointer into `ExecuteArray`, which
then clears and appends that object's `+0x23e0` array. This pass does not
prove that pointer is a `CDocCompose` rather than the production document.
The following section does. The callback-retirement gate is not promoted.

## Command-view document, 2026-09-24

The two command-map entries are `CTstCommandView` handlers, not production-view
handlers. The message map at `0x140ebadf0` names that class and points its
entries at `0x140ebac50`. `WM_COMMAND` `0xb21e` is `0x1406e5e80`. `WM_COMMAND`
`0xb251` is `0x1406e6030`. Both call `0x1407528c0` (`mov rax, [rcx+0xe8]; ret`)
and pass that pointer to `0x1405d7c10`. When that function reaches
`ExecuteArray`, `rcx` is still that pointer. `0x1406e64a0` is the same view:
its only caller, `0x1405e4d81`, passes the `CTstCommandView` returned by
`0x1405dc510`. No Rev6 PE was built. The program was not saved.

`CTstCommandView` is created only as row 1 of the `CUsefulSplitterWnd` embedded
in `CChild2` at `+0x1c18`. `CChild2::OnCreateClient` (`0x1404fdfe0`) passes its
create context to splitter slot `+0x2e8`, DyTools0 thunk `0x18011f31e`, MFC
ordinal 3538. That body calls `CRuntimeClass::CreateObject` and then view slot
`+0xb8` with the context as the last argument. The slot is MFC ordinal 3075,
which stores that argument at `view+0x138`. The existing `CFormView` create
path copies `+0x138` into `lpCreateParams` and `AddView` (`0x18021faa0`) stores
the context document at `view+0xe8`.

The only document template that uses `CChild2` is resource `0x7c7` in
`0x1404d2820`: document `CDocCompose`, frame `CChild2`, view `CTstCADView`.
The production templates in that same function use `CProductionDoc`,
`CProductionChild`, and `CProductionView`. The other `CChild2::GetRuntimeClass`
sites call `0x14077fbe0` (`IsKindOf`) and do not construct a frame. Row 0 is
`CTstCADView` and row 2 is `CAnomaliesGridView`; both receive that same context.
`CDocCompose` is `0x51c0` bytes and `CProductionDoc` is `0x61f8` bytes, so the
shared `+0x23e0` displacement is a different array on each object.

`ExecuteArray` and `AcquireAndCheckSkip` are not production-array mutators.
The production capture set is `SkipList_Reset`, `SkipList_Add`, the
`ReloadDoc` restore, `SkipAllSubPanels`, `SkipSubPanel`, and `RegistryRead`.
The candidate is the next section. It does not close the gate.

## Snapshot and notification candidate, 2026-09-24

Stock close, cycle-start, and reset spans do not drain refresh
`0x1406adaf0`. The snapshot and notification text below is a candidate for
the original plan's late-callback obligation. It is not implemented. No Rev6
PE was built. The program was not saved. `tools/verify_worker_admission.py`
is unchanged. The callback-retirement gate stays blocked.

A valid snapshot is patch-owned bytes holding the skip membership the
production document's `CUIntArray` at `+0x23e0` had at a capture point.
Refresh acquires that pointer once per dispatch and does not reread
`[array+8]` or `[array+0x10]`. An older snapshot stays allocated until every
dispatch that loaded it has returned. The count is a buffer reference count.
It is not a panel, result, or CAO generation, and it does not clear operator
skips.

Capture runs on the mutating thread at each normal return in this set. A throw
leaves the previous snapshot published and does not repeat the stock call.
If snapshot allocation fails after a normal return, the previous snapshot
stays published and a process-lifetime snapshot-failure counter increments.
That divergence is release-stopping. The stock mutation is left as it stands.

| Mutator | Entry | Capture point |
| --- | --- | --- |
| `SkipList_Reset` | `0x140541050` | Normal return. `SetSize(0, -1)` has emptied the array. Callers: `0x1404aebe9`, `0x14068f7d7`, `0x1406937d7`, `0x1406a085e`, `0x1406a2d87`. |
| `SkipList_Add` | `0x140541020` | Normal return of the tail `SetAtGrow`. |
| `ReloadDoc` restore | `0x140693811` | Each normal `SetAtGrow` return in the restore loop. |
| `SkipAllSubPanels` | `0x140540ef0` | Normal return of `SetSize(0, -1)`, then each normal `SetAtGrow` return. The only caller is `ExecuteSkip`. |
| `SkipSubPanel` | `0x140541080` | Normal return of its one `SetAtGrow`. The only caller is `ExecuteOne_Component` at `0x140736fcb`. |
| `RegistryRead` | `0x140692600` | Each normal `SetAtGrow` return at `0x140692881`. The only caller is `OnOpenDocument` at `0x14068dc20`. |

`ExecuteArray` (`0x1405f5660`) and `AcquireAndCheckSkip` (`0x1405f19a0`)
mutate `CDocCompose`, the document created with frame `CChild2`. They are not
in this set. The 2026-09-24 scan that found the extra sites covered direct
`SetSize` (MFC ordinal 13522, thunk `0x14077fdcc`) and `SetAtGrow` (MFC
ordinal 12880, thunk `0x14077fdd2`) uses of displacement `0x23e0`.

These stock readers stay on the live pointer and count. They are synchronous
document methods, not the posted refresh callback: `0x1406746d0`,
`IsSkippedSubPanel` `0x14052e010`, `IsSkippedAllSubPanel` `0x14052dfe0`,
`ApplySkipOnZone` `0x140525280`, and `RegistrySave`.

The three SKIP posts load `[document+0x5838]` and then `[view+0x40]` with no
null test, at `0x1406a103b`, `0x1406a1075`, and `0x140736feb`. The view
destructor frees the view through MFC ordinal 1487 without clearing
`document+0x5838`. The notification design publishes the view pointer and HWND
into patch-owned storage when stock publishes `+0x5838`, and clears that pair
in the view destructor before the free. A poster that sees a cleared pair does
not load the document field or the view. A poster that already holds the pair
is counted until `PostMessageA` returns, and the destructor waits for that
count before the free. The posted handler reads the snapshot. This count is a
buffer/poster reference count. DestroyWindow retirement of a queued HWND
message stays waived-unverified under W7-QUAL-01.

This candidate does not select patch bytes, start Rev6, pass native
qualification, or pass the other section 1 gates.

## Wider-intermediate candidate, 2026-09-25

Exact no-wrap DWORD bounds and the wraparound counterexample are already
recorded in [rev2a-entry-gates.md](../maps/rev2a-entry-gates.md). No supported
or enforced workload maximum exists. The original plan still requires one of
two outcomes: document and enforce that maximum, or widen the threshold
arithmetic. The wider-intermediate shape below is a candidate for the second
outcome. It is not implemented. No Rev6 PE was built. The program was not
saved. `tools/verify_worker_admission.py` is unchanged. Rev5 keeps low-DWORD
`imul`. The arithmetic entry gate stays open.

Candidate threshold comparison, if wider intermediates are the path taken:

- Cell counters stay DWORD. After each `lock xadd` / read, zero-extend
  `missing` and `inspected` into 64-bit registers before multiplying.
- Compare `(missing * 100)` and `(inspected * 30)` as unsigned 64-bit products,
  then apply the same unsigned threshold branch shape as rev5
  (`missing * 100 > inspected * 30` after at least 10 completions).
- Do not use 32-bit `imul` products for that compare. The counterexample
  inspected = 143,165,577 and missing = 1 must not qualify under the wide
  compare.
- DWORD counter wrap of the cell fields themselves remains a separate
  lifetime/reset concern from the product-width choice.

This candidate does not select patch bytes, start Rev6, pass native
qualification, or pass the other section 1 gates. The original plan's
arithmetic obligation is unchanged.

## Final-mask multiplicity, 2026-09-25

The final-mask site `0x140736f47` is `MOV RCX, qword ptr [R15+0x10]` inside
`ExecuteOne_Component` (`0x1407368d0`). No Rev6 PE was built. The program was
not saved. `tools/verify_worker_admission.py` is unchanged.

One call reaches that instruction at most once. The only backward jump in the
function is `JL 0x140737270` from `0x1407372cd`, and both addresses are after
the site. `ExecuteAll_Components` calls it once per vector slot from
`0x1407356a1`, inside the index loop `JC 0x140735570` from `0x140735842`.
The zone executor calls `ExecuteAll_Components` once, at `0x140736796`, after
its only backward jump. `Treat` and the synchronous body have no backward
jumps. Each calls the zone executor once.

`ReceiveGreyZones` is the only executable caller of those two bodies. Its
index loop increments `R15` and calls either the synchronous body or the
dispatcher, not both. Its later list walk does the same once per node.
`PanelInspect` is the only executable caller of `ReceiveGreyZones`, and
`HandlerProduction` calls `PanelInspect` only at `0x1406a39ea`, on the arm
where the preceding status dword is 3.

That call sits in a section loop. The log strings are `Section %d: Begin.`
and `Section %d: End.` The loop bound is the return of `0x140695200`, which
is 2 only when `IsTstMultiSection` (`0x14052e070`) returns 1 and the preceding
dword is 0; otherwise the bound is 1. The section dword at `document+0x3978`
is seeded from `ESI`, and the only `ESI` writes before that seed in this
function are `XOR ESI,ESI` at `0x1406a32f1` and `0x1406a331a`. The body then
stores `SHL` of the section value. A bound of 2 therefore admits a second
iteration before `JMP 0x1406a2770` at `0x1406a45ed`. That back edge is before
the conditional `SkipList_Reset` at `0x1406a2d87`.

The second iteration is the unresolved part. It is not yet shown whether
section 2 walks the same component vector as section 1. Data references and
indirect calls stay outside the executable-caller claim. The uniqueness gate
stays partial.

## Baseline identity

- Repository commit: `16df773e24641b44236d73a8ed9b3c548ea7a037`
- Worktree was already dirty before implementation; unrelated changes were preserved.
- Interpreter: CPython 3.14.5, 64-bit Windows AMD64
- Source SHA-256: `ccca11b2f05084b484fa5556c67f8874065dbc0b6265177d2517f81265af00f4`
- Source size: 28,738,048 bytes
- Historical rev5 SHA-256: `0ef39ff59e216bb7e9a45f6cb7ee505eac0822f6c4939d8ff1a8e04197675c13`
- Historical rev5 size: 28,746,240 bytes
- Dependencies: `tools/requirements-release-win-amd64.lock`

## Completed implementation

- Preserved the rev5 generator and artifact as the historical baseline.
- Added mandatory explicit verifier selection with `--revision rev5`.
- Refused optimized Python and nonempty `PYTHONOPTIMIZE` before verification.
- Added subprocess regressions requiring optimized and forced-failure runs to
  exit nonzero without PASS output.
- Added named policy/state model checks for exact committed membership of states
  2 and 3, failed-disabled state 4, unknown-state rejection, and no committed
  state downgrade during failure cleanup.
- Added interpreter, optimization-environment, and exit-status evidence.
- Added a Windows AMD64 hash-enforced lock for the four pinned distributions.
- Updated active README commands and marked rev5 as offline-only.

## Verified commands

```powershell
.\.venv\Scripts\python.exe .\tools\verify_hardened_patch.py --revision rev5 --code-only
.\.venv\Scripts\python.exe .\tools\verify_hardened_patch.py --revision rev5 --output .\Updated\Vision3D_concurrency_fix.exe
.\.venv\Scripts\python.exe -O .\tools\verify_hardened_patch.py --revision rev5 --code-only
.\.venv\Scripts\python.exe -m pip download --require-hashes --only-binary=:all: --no-deps -r .\tools\requirements-release-win-amd64.lock
```

Normal code-only and complete rev5 verification passed. The optimized command
failed before PASS output as required. The dependency lock resolved exactly four
hash-matching wheels.

## Entry-gate disposition

| Proof obligation | Status | Existing evidence and missing proof |
| --- | --- | --- |
| Final-mask hook multiplicity / result uniqueness | Partial | One `ExecuteOne_Component` call reaches `0x140736f47` at most once, and that call is once per component-vector slot per zone execution. `HandlerProduction` can enter `PanelInspect` on two section iterations when `0x140695200` returns 2, before the cycle back edge reaches reset. Whether those sections share a component is still open. See [Final-mask multiplicity](#final-mask-multiplicity-2026-09-25). |
| Worker drain before CAPM reconciliation, supported single lane | Blocked: callback and exception containment | The stock unchecked `CreateEventA`/`WAIT_FAILED` path remains defective, but the startup-only synchronous candidate makes it unreachable from every retained executable caller on the supported lane. The export-thread descendant copies its payload before return and does not retain CAO/result pointers. Existing work, the posted UI callback, exception handling, and remaining ownership before release or reuse remain unproved. |
| Production/anomaly vector ownership and immutability | **CLOSED** | Outer vector (CAO+0x5878) proven one-shot allocated in constructor, no later stores. Inner vector (zone+0x18/0x20/0x28) proven FIXED-CAPACITY: all panel-load-path functions decompiled (ExecuteOne_Component, ExecuteAll_Components, FUN_140735120, PV_EnvoiDesZoneComposants, CAPM_SetInspectionStatus) and verified NO push_back/resize/reserve/reallocate. Workers write pre-allocated slots; CAPM reads for reconciliation. Synchronization risks remain: torn writes (no memory fence), use-after-free in dtor (no ProductionStop join). Evidence: maps/vector_ownership/anomaly_vector_mutator_table.json, maps/decomp/*.c |
| No late callbacks after CAO retirement | Blocked: live-storage dependency established | The export worker owns copied value records. The posted SKIP receiver reads the live array at `CAO+0x23e0` through production-view `+0xe8`. Bounded emulation confirms dispatch-time reads, a fault with artificially unmapped storage, and exception/fault paths during modeled reset without CAO destruction. The view deleting destructor frees the view through ordinal 1487 without clearing `document+0x5838`, so a producer reload still names that block while the document remains published. The document destructor's direct-call closure then frees the `CUIntArray` at `+0x23e0` without a `user32` import and without calling the message pump. Before that free, a nonzero `document+0x19e8` calls slot `+0x190` and drops the returned refcount. `SetProductionVMC` stores `CVMC_ListSingleton::GetCurrent` there, and the stock controller implements that slot as a forward to `[controller+0x870]` slot `+0x220`, which forwards again to `IAcquisitionController` slot `+0x220`. That interface slot is `_purecall` in the supplied DLL. The same destructor then destroys the array at `document+0x5878` through slot `+8` with edx 3 and stores null. Its inner `0x370` objects are `CAnomalieProd`. Their destructor releases point, string, buffer, and image members and does not import `user32` or the executable. `CAsynchCommandExecution::Kill` on `document+0x6128` waits on that object's own thread handle, not on `document+0x3868`. The destructor closes the `CreateEventA` handle at `+0x3878` and the `CreateSemaphoreA` handle at `+0x3890`, and its bytes do not mention `+0x3868`. `OnCloseDocument`, before the view loop, waits on the `CreateSemaphoreA` handle at `[app+0x5870]` and releases it before returning. The wait on `app+0x57c8` and the `DoEvents` call run only when the incremented dword at `+0x5868` is not 1. Those handles are not `document+0x3868`, and the functions do not call `ProductionStop`. `HandlerProduction` has no displacement `0x5870` and does not call that wait. The `CMainFrame` destructor passes its own `+0x5870` to `CloseHandle` and stores zero; that call does not wait. Slot `+0x10` of the object at `document+0x2548` stores null at `document+0x3868` and stops the other thread at `document+0x3860`. The view command handler calls slot `+8` of that object. The base destructor does not call `ProductionStop`. The pool worker constructor stores zero at `+0x28`. `0x1406a6b95` calls `0x1406a15d0`, and `0x1406a4980` copies that result onto each worker at `thread+0xec8`. Treat reads that field. After `ProductionStop` joins `document+0x3868`, it calls producer slot `+0` with `edx` 1 while the slot is still nonzero, then stores zero. That destructor calls the pool destructor, and `0x140655980` calls each worker slot `+0` with `edx` 1. Worker slot `+0` calls `0x14069a110`. Close, destruction, view `WM_DESTROY`, the close poster, and the `0x52c` handler do not call `ProductionStop`, `0x140655980`, or `0x1406a4980`. The destructor's direct calls, and one further direct-call level, do not call `ProductionStop`, `AskToStop`, worker `Stop`, or the pool cleanup, and do not mention `+0x3868`. The destructor body's own import calls are not `WaitForSingleObject` or `CViThread::Stop`. Calls on `document+0x2eb8` and `document+0x2550` tail-jump `CSerialDriver::~CSerialDriver`. The call on `document+0x60c8` frees `[object+8]`. The call on `document+0x6078` is `ret 0`. Indirect calls inside that closure are not expanded. After the array free, the same destructor calls `CDataCao::~CDataCao` on `document+0x180` and then MFC ordinal 1104. The destructor body is not in the supplied binaries. Actual delivery of a post made before the view is freed remains unproved. |
| Reset before reuse of the same CAO pointer | Partial | `CProductionDoc` has no pool. `CreateObject` is CRT `malloc(0x61f8)` plus the constructor, which builds an empty `CUIntArray` at `+0x23e0`. The deleting destructor first stores null in the `CCAPM` slot at index `document+0x3924`, the same index `ProductionStart` copies to thread `+0xec0`, then releases the array buffer and `free`s the block. The base constructor calls `CDataCao::CDataCao` on `this+0x180` before building the empty `CUIntArray`, and the zero-mode publish of that document is outside the constructor. Document slot `+0x108` publishes through `SetProductionVMC` before mentioning `+0x2548`, and it calls neither `ProductionStop` nor `ProductionStart`. `ProductionStop` calls `ProductionStart` only after `CViThread::Stop` and after storing zero at `+0x3868`, and only when `+0x3881` is 1. `ProductionStart` returns without stopping or replacing the thread when `+0x3868` is already nonzero. Close does not call `ProductionStop`. The production cycle reloads that slot before its `+0x382e` check. All 99 accessor calls in `HandlerProduction` use the pointer with no null test. The stop byte is stored only on the equal side of that compare, so a null slot faults before the store. The not-equal side calls `0x1406970f0`, which also dereferences the document and does not write the stop byte. The next iteration reloads the app `+0x1b0` pointer saved before the cycle, not a document pointer. The only document pointer held across a later accessor call is `rbx` in two windows that both end before the back-edge, and no accessor result is stored to memory. A republished document is observed. Close still does not join the producer. |
| DWORD arithmetic at supported workload maximum | Partial: bound only | Exact product bounds and a wraparound counterexample are recorded; no supported/enforced workload maximum proves overflow cannot occur. A wider-intermediate candidate is recorded in [Wider-intermediate candidate](#wider-intermediate-candidate-2026-09-25) and is not implemented. |

## Entry-gate investigation, 2026-09-21

See [byte-verified static evidence](../maps/rev2a-entry-gates.md) for the call
chain, stock wait-result finding, arithmetic bounds, retained JSON hashes, and
reproduction commands. Eleven read-only saved-project reports contain 25
function records, covering 24 distinct executable entry points, without disturbing
the active Ghidra lock. A twelfth static PE report adds four BaseTools functions
and verifies the executable's exact Stop import. Every retained instruction was
checked against its identified source binary.

Follow-up resolved the worker loop (`0x1406a1a50`): it signals completion after
normal `Treat` return, regardless of the treatment Boolean, and ignores signal
failure. The constructor installs the matching vtable. `GetThread` and its array
helper do not reject NULL from completion-event creation, providing a concrete
failure precondition for the stock false-success wait path. A bounded standalone
Windows API probe confirmed NULL wait/SetEvent failures (error 6); it did not
execute Vision3D or demonstrate a station incident. The inspected caller chain
does not contain this failure, so the barrier contract cannot be accepted as-is.

The current code-only and complete rev5 artifact checks were rerun and passed;
`python -O` was refused before PASS output. These offline tests stub stock calls
and do not cover the newly identified stock barrier failure handling. No
lifecycle gate was promoted to pass. No rev6 code or executable was created.

## Containment design review, 2026-09-21

Disposition: the initial bounded read-only investigation was subsequently expanded
by explicit user approval to offline-tested admission/drain repair outside the five
feature hooks. Publication and target execution remain prohibited. No gate has
passed. The five feature sites remain unchanged; additional lifecycle candidates
must independently satisfy source-byte, ownership, and unwind requirements.

### Why the existing hooks do not establish containment

In [the rev5 generator](../tools/patch_f1_missing_n_rev5.py),
`count_handler_source` acquires a context reference inside the final-mask hook
and releases it before returning to stock execution. `reset_handler_source`
waits for those references, not for stock pool submissions or whole worker
lifetimes. `final_handler_source` acquires its own reference; it does not turn
the reference count into a stock admission/completion ledger.

A counterexample to relying on that count is a submitted worker paused before
its first hook: outstanding stock work is nonzero while patch references are
zero. Another gap exists after a hook releases its reference but before `Treat`
returns. These are permitted ordering examples, not observed station schedules.
An empty completion array at CAPM is also ambiguous: stock clears it after both
successful and failed waits. Neither test establishes safe reconciliation or
reuse. State 4, UI suppression, and skipping patch writes do not stop stock
workers, stock review/transport, or retirement.

### Alternatives and recommendation

| Alternative | Assessment |
| --- | --- |
| Verified vendor correction | Preferred when available; requires a supplied corrected build, fresh identity/site validation, and the same lifecycle tests. No such build is established here. |
| Reject NULL completion events only | Prevents the demonstrated admission failure if done before reservation/publication, but does not contain timeout, signal failure, exceptions, or other invalid-handle paths. Insufficient alone. |
| Return false on every unsuccessful wait only | Repairs false success but leaves workers potentially active and handles discarded. Receiver failure is not proof of cancellation or safe reuse. Insufficient alone. |
| Reuse patch reference count or poll the cleared array | Rejected as a drain oracle for the reasons above. |
| Separate admission and failed-drain containment design | Expanded offline repair approved. Two local guard experiments pass below; final patch placement and complete containment remain unproved. |

### Required contract for the proposed investigation

1. Admission must not publish work until its completion tracking is valid. On
  event-creation failure, leave no reserved worker, queue entry, or ownership
  behind. Evaluate a clean no-worker return into the existing synchronous
  fallback, but do not assume that fallback's Boolean proves inspection success.
2. Establish a closed submission set for the correct lane and panel generation.
  Accept drain only after all admitted work and relevant descendants complete;
  zero tracked entries alone is insufficient. Preserve valid batched waits.
3. Classify every unsuccessful wait as undrained, capturing the error before
  cleanup overwrites it. Do not discard tracking, release resources still used
  by workers, reconcile, hand off, or reuse the CAO on that path.
4. Locate and verify an existing stop/quarantine path that both prevents further
  admission and establishes worker quiescence before resource reuse. If none is
  available, stop the design review for a separate operational decision. Do not
  substitute forced thread/process termination, an unbounded spin, exception
  propagation alone, or a failure Boolean for a proven containment mechanism.
5. Retain process-lifetime diagnostics for admission, signaling, and drain failure;
  distinguish confirmed treatment completion from successful inspection. Prove
  cleanup and ownership for exceptions as well as ordinary returns.

Bounded next analysis: start at `GetThread` (`0x1406a1660`) and
`WaitEndOfAllThreads` (`0x1406a9a80`), then follow only their failure/admission
callers and the nearest stock stop/quiescence mechanism. These are function
anchors, not release-approved byte-patch locations. Exact candidate boundaries
and local test results are recorded below; cleanup and containment obligations
remain prerequisites for integration.

Required isolated tests for any later approved implementation: event creation
failure before dispatch; worker delayed before its first hook; timeout and
`WAIT_FAILED` with outstanding work; signal failure and exceptional treatment;
failure in a later wait batch; concurrent submission at the drain boundary;
concurrent subpanel isolation on the single lane; and attempted retirement/immediate pointer reuse after each
failure. Oracles must verify no untracked work, no premature handoff/reuse, and
correct ownership cleanup. A harness that stubs successful stock calls is not
enough. These remain integration requirements; the bounded experiments below cover
only the explicitly listed cases with stubbed helpers.

### Bounded investigation outcome

The failure-route helper `0x1406719a0`, called at `0x1406a44e2` for
handler result 0/2 at its branch, resets result fields and invokes image-buffer
deletion. A false wait return therefore does not itself preserve result storage.
This does not prove an observed race or resolve all intervening indirect calls.

Pool cleanup `0x140655980` invokes worker deleting destructors before closing
tracked completion handles. The known derived destructor clears its container
at `+0xc8` and frees its head before calling base cleanup `0x14069a110`.
Only then does the base call the saved-analysis `CViThread::Stop` symbol with
third argument `0xffffffff`, followed by closing work/availability handles
without inspecting the returned value or output DWORD on normal return.

The user subsequently supplied the original BaseTools DLL; its version matches
70.06.59.00. The initial import lookup was incomplete because `pefile` reached
its default 8,192-entry internal limit. A finite 65,536-entry bound resolved the
exact import, with raw IAT/ILT/name agreement and no import-parser warnings.
The supplied DLL exports `Stop` at `0x18007e1a0`; source hashes and its four
thread-lifecycle function bodies are retained in the
[new PE report](../maps/rev2a_basetools_stop.json).

`Stop` signals `this+0x18`, ignores signal failure, and waits on
`[[this+8]+0x58]` with the supplied timeout. Every nonzero wait result returns
false without deleting or clearing `this+8`. Zero invokes the object's virtual
deleting destructor, clears `this+8`, and returns true. An already-NULL `this+8`
also returns true without waiting. `Start` uses that same nested handle for
`ResumeThread`; the ordinary valid-owned-thread-handle path supports a join,
but pointer/handle ownership and absence of concurrent admission remain required.
The base worker destructor passes `INFINITE` and ignores Stop's false return;
its earlier derived cleanup is unchanged. Stop also does not write its reference
output DWORD in this body. It is not an independently safe pool-drain API.

No safe stock containment mechanism was established. The missing Stop body is
now resolved, but destruction is not a verified stop-before-release primitive,
and its reachability from failed drain is not established. See the
[containment evidence](../maps/rev2a-entry-gates.md) for source-verified instructions,
report hashes, and remaining ownership limits. Next design obligation: close
admission, preserve worker/result storage before stopping, check every stop/wait
outcome, and establish single-lane ownership before any release or reuse. Neither
invoking teardown nor correcting a Boolean alone satisfies that obligation.

## Offline repair experiments, 2026-09-21

[The instruction emulator](../tools/verify_worker_admission.py) verifies the stock
EXE SHA-256 and retained instruction bytes before executing GetThread, its real
asynchronous caller, and WaitEndOfAllThreads in Unicorn. Keystone assembles guard
bodies into detached emulator memory at `0x142000000`; that address is not an
identified file-backed code cave. The harness has no modified-PE output path.

| Candidate | Local effect and verified behavior |
| --- | --- |
| `0x1406a1707`, six displaced bytes `4c8be00f57c0` | Replay `mov r12,rax; xorps xmm0,xmm0`. NULL returns through the stock logger cleanup at `0x1406a180d` with RBX zero, before pool locking or mutation. Non-NULL continues at `0x1406a170d`. The stock caller takes synchronous fallback with original arguments and propagates its Boolean. |
| `0x1406a9b6e`, five displaced bytes `448bf885c0` | Replay `mov r15d,eax; test eax,eax`. Every nonzero wait result branches to lock release/false return at `0x1406a9be0`, before any handle close or tracking clear. Zero continues at `0x1406a9b73` with the original flags and batching. |

Verified commands:

```powershell
.\.venv\Scripts\python.exe .\tools\verify_worker_admission.py
.\.venv\Scripts\python.exe -O .\tools\verify_worker_admission.py
```

Normal execution passed seven test methods, including subcases for NULL-event
fallback returning either Boolean, unchanged healthy admission, failed availability
waits, drain timeout/WAIT_FAILED/abandoned/unexpected statuses, failure after one
successful batch, and successful drains of 0, 1, 64, 65, and 129 handles. The stock
counterexamples reproduce NULL registration/dispatch and WAIT_FAILED closing and
clearing tracking while returning success. Guarded failure leaves fixture storage
unchanged. Ordinary returns preserve nonvolatile GP registers, balance the stack
and modeled locks, and destroy the modeled function logger exactly once.
Optimized Python was rejected with exit 1 before running tests. VS Code reported
no errors in the harness.

These are local emulation results, not complete repair or runtime proof. Helpers,
Win32 calls, tracking mutations, logger destruction, and synchronous treatment are
stubbed; exceptions and concurrent scheduling are not executed. The valid-event
no-worker leak is preserved, not fixed. Event signaling/reservation failures,
exception ownership, diagnostic capture, file-backed placement, and native unwind
metadata remain outstanding. Most importantly, returning false while preserving
tracking still reaches a caller that can reset result storage. Neither candidate
may be integrated as a complete barrier fix until admission is closed and every
failure path prevents cleanup, handoff, and reuse before confirmed quiescence.

## Approved synchronous containment candidate, 2026-09-21

The failed-drain caller at `0x1406a928c` tests AL, logs failure, assigns R12D=2,
and rejoins normal processing at `0x1406a92b1`. The surrounding handler can clear
result storage at `0x1406a44e2`. Its common continuation includes further calls
and a cycle increment before testing the stop flag. Neither an error return nor
bypassing that single cleanup establishes containment.

Rather than introducing an unproved stop/quarantine path, the user explicitly
approved forcing this pool's work through the stock synchronous fallback,
accepting reduced parallelism. In `tools/verify_worker_admission.py`, the
`synchronous_only` candidate replaces the complete three-byte entry instruction
at `0x1406a1660` (`48 8b c4`, MOV RAX,RSP) with `31 c0 c3` (XOR EAX,EAX; RET).
It returns no worker before any prologue, logger, event, lock, or pool access.
The source SHA-256 and retained instruction bytes are checked against the stock
PE; replacement bytes exist only in Unicorn memory. The NULL-event guard and
this entry candidate are mutually exclusive test modes.

The stock dispatcher at `0x14069fb80` then follows its no-worker branch to
`0x14069fcd0`, preserving production, zone, result arguments, and Boolean return.
Four new test methods verify:

- Direct entry returns zero with pool/worker/document fixture memory unmapped,
  no helpers called, balanced stack, and preserved nonvolatile GP registers.
- The real dispatcher calls only the synchronous treatment stub across 16
  combinations of event, availability-wait, and treatment outcomes. It performs
  no modeled async admission or fixture mutation.
- Repeated dispatch does not erase pre-existing completion tracking. This is a
  retention check, not evidence that existing workers are drained or safe.
- A changed source entry instruction is rejected before candidate execution.

Validation: `python tools/verify_worker_admission.py` passed all 11 test methods;
`python -O tools/verify_worker_admission.py` refused execution with exit 1. VS Code
reported no harness errors. Use the configured workspace virtual environment.

This candidate must be installed before any affected admission starts. It is
not a hot-switch recovery mechanism: existing reservations, published jobs, or
callbacks are not canceled, joined, or made safe by returning NULL from GetThread.
The synchronous treatment body remains stubbed in these original tests; its descendants,
exception behavior, and owner lifetime are not proved.
The tests do not establish a complete receiver-to-cleanup containment path.

Replacing an entry prologue also requires explicit Windows x64 unwind validation
and compatible exception metadata; unchanged stock metadata must not be assumed
valid. No PE placement, export, native target run, or Rev6 builder was produced.
The two earlier guards remain separate experiments, not a combined release patch.

## Synchronous slot retirement and caller unwind, 2026-09-22

Source-pinned read-only reports:
[release](../maps/rev2a_synchronous_slot_release.json) retains `0x140578dd0`;
[retirement](../maps/rev2a_synchronous_slot_retirement.json) retains
`0x140578c80` and receiver list cleanup `0x14051f150`.

`SlotRelease` performs a locked DWORD decrement at `0x140578e33` on slot
`+0xc80` before calling `SlotDelete` at `0x140578e4f`. It calls deletion when
the signed remaining count is nonpositive or the force argument is set. It does
not restore the count when deletion returns false. Its selected unwind action
is logger destruction, not a compensating increment. Eleven bounded cases cover
normal shared/final references, false deletion, zero-count input, forced deletion,
failures before/after the decrement, and a repeated release. The repeated-call
fixture uses a deletion stub: it proves a second decrement and deletion call,
not the final count after real deletion, which may reset the count to zero.

`SlotDelete` has the following order on the matched-slot path:

1. Enter manager `+0x48` critical section at `0x140578d14`.
2. Find the slot in the manager's list (`+0x80`).
3. Construct a temporary `CZoneStorage`, assign it to slot `+8`, and destroy
  the temporary at `0x140578d3e`, `0x140578d50`, and `0x140578d5c`.
4. Set record `+8` to free and reset slot `+0xc80` to zero.
5. Leave the critical section at `0x140578d77`.
6. Signal manager semaphore `+0x78` at `0x140578d9f`, then return true.

PE imports resolve the three storage operations to `AvImgBuffer.dll`, and the
lock/signal operations to `KERNEL32.dll`. The return from `ReleaseSemaphore` is
ignored. A modeled false return still leaves the slot marked free and returns
true; this does not establish why a real semaphore operation would fail.

Nine deletion fixtures cover matched/missing slots, positive-reference refusal,
forced deletion, a false semaphore result, and failures in each storage helper
or the final logger destructor. In the three storage-helper failure fixtures,
the lock model remains held and the retirement stores/signal have not executed.
The exact C++ metadata has no local try-block map. Its selected actions are
logger cleanup, or temporary-storage destruction followed by logger cleanup;
there is no direct `LeaveCriticalSection` action. These are conditional failure
counterexamples with explicit successful helper stubs and Python hook failures,
not native C++ unwinds or proof that the imported operations throw on a station.
Assignment may partially mutate storage before throwing; the fixtures do not
model those internal effects or destructor-internal recovery.

The immediate exceptional-exit chains are now pinned to call bytes and FuncInfo:

| Call site | Selected cleanup chain |
| --- | --- |
| Safe release `0x14066da82` | BaseTools logger |
| Dispatcher synchronous call `0x14069fc94` | BaseTools logger |
| Receiver dispatch `0x1406a8f32` | HwCommonTools `CZoneData`, local list, bench, logger |
| Receiver dispatch `0x1406a9104` | Local list, bench, logger |

Neither immediate caller has a local try-block map. The retained local-list
helper frees list nodes and the sentinel through operator delete; it does not
directly release inspection slots. Imported destructors and handlers above the
receiver remain outside this evidence. Do not infer whole-program leakage or
exception containment from this local chain.

**Disposition:** the synchronous candidate still needs exception-safe retirement
and failure containment; an unconditional `SafeSlotRelease` retry is unsuitable.
Any repair must distinguish a consumed
reference from completed retirement and preserve critical-section ownership;
do not add a shared release hook or approve continued processing from these
fixtures alone. W7-QUAL-01 remains **waived - unverified** and unchanged.

The supplied `AvImgBuffer.dll` is AMD64, 987,648 bytes, image base
`0x180000000`, SHA-256
`6a73a7f28ff8911fd1b7693fe97e70fdbff925a57805879bbadb43b10bc90d7f`.
`SlotDelete` calls `CZoneStorage` construction, assignment, and destruction
while the manager critical section is held: enter at `0x140578d14`, construct
at `0x140578d3e`, assign at `0x140578d50`, destroy at `0x140578d5c`, and leave
at `0x140578d77`. Constructor `??0CZoneStorage@@QEAA@XZ` at `0x18005ae00` has
`__CxxFrameHandler3` unwind state and no try blocks. Its node allocator
`0x18005d360` calls `malloc` and `_callnewh`; when both fail it throws through
`_CxxThrowException` with the text `bad allocation`. That call sits in
constructor state 8 or later, so constructed members unwind and the exception
leaves the constructor. The EXE unwind map still has no
`LeaveCriticalSection` action, so this failure escapes with the lock held.
The destructor is `EHFlags` `0x5` (`/EHs` plus noexcept) and has no try blocks;
it is not the propagating path. Assignment `??4CZoneStorage@@QEAAAEAV0@AEBV0@@Z`
has no exception personality. This is a static failure path, not a station
occurrence, and it does not pass containment.

`HwCommonTools.dll` is AMD64, 423,424 bytes, image base `0x180000000`,
SHA-256 `92f6b2b9f51616162de5184cee9fdccceb1f3c798ee0b65e0886c95fdfb20f15`.
Receiver `0x1406a88e0` has no frame register. Its post-prologue stack is the
exception establisher, and `rbp+0x240` is the same slot as funclet `rdx+0x340`.
That slot is constructed by `??0CZoneData@@QEAA@_KAEBVCViUnitSize@@@Z` at
`0x1406a8da8` and explicitly destroyed at `0x1406a8fb4`. While the constructor
is still inside the call, unwind state 14 destroys a `CViUnitSize`, not
`CZoneData`. After the constructor returns, state 16 covers both the
synchronous call `0x1406a8eda` and the dispatcher call `0x1406a8f32`. That
chain destroys `CZoneData`, the local list at `0x14051f150`,
`CBenchManagerFunction`, and `CLogManagerFunctionML`. The later dispatcher
call `0x1406a9104` is state 9 and does not destroy this `CZoneData`. The
destructor `??1CZoneData@@QEAA@XZ` at `0x180024c40` has `EHFlags` `0x5`
(`/EHs` plus noexcept) and no try blocks, so it does not catch the exception
being unwound. It releases a `CROI`, strings, two reference-counted control
blocks, and the unit time, point, and size members. A throw from one of those
member destructors terminates rather than propagating. This is not a
containment barrier.

All **39 verifier tests pass in 17.189 seconds**, with no editor errors. No Rev6
binary, native target execution, installation, or production release occurred.

## Synchronous C++ exception cleanup evidence, 2026-09-22

The source-pinned synchronous body at `0x14069fcd0` has runtime-function bounds
RVAs `0x69fcd0..0x69fe55`, unwind data `0xfd4d80`, and a version-one header
`11 1f 09 00` with UHANDLER set. Its handler thunk `0x1407a6232` resolves through
IAT `0x140d5bf28` to `VCRUNTIME140.dll!__CxxFrameHandler3`. FuncInfo at
`0x140ea80b0` has magic `0x19930522`, six unwind states, ten IP-state entries,
and no local try-block map. This describes compiler-generated cleanup, not a
local catch that converts an exception into a normal failure return.

The verifier pins the complete FuncInfo, unwind map, IP-state map, and selected
cleanup bytes against the unchanged stock executable. At the existing helper
failure boundaries, metadata lookup using the call return IP minus one selects:

| Failing helper | Unwind actions, in order |
| --- | --- |
| Zone execution `0x140735f10` | `0x1407fd038` analysis cleanup, `0x1407fd01e` logger |
| Slot release `0x14066d9e0` | `0x1407fd044` string, analysis cleanup, logger |
| Normal local cleanup `0x1405586b0` | Logger only; analysis cleanup is not retried |

The analysis action passes parent-frame `+0x80` to `0x14066d9d0`, which adds
`0x18` and tail-calls the same vector cleanup `0x1405586b0` used on normal return.
That helper destroys `0x58`-byte elements through their virtual destructor,
calls allocator helper `0x1404cc4e0`, then clears the three vector pointers.
The earlier temporary-acquisition action `0x1407fd02c` instead loads the vector
pointer from parent-frame `+0xf0` and reaches the same cleanup through
`0x14067fb10`. String actions use frame `+0xe0`; logger cleanup uses `+0x50`.

Saved read-only extraction
[rev2a_synchronous_exception_cleanup.json](../maps/rev2a_synchronous_exception_cleanup.json)
retains those three local helpers and the explicit slot-release wrapper.
Fifteen Unicorn fixtures execute the real funclets, wrappers, and vector loop:
five action sequences with null, one-element, and two-element vectors. They
check object addresses, destructor/free order, pointer clearing, bounded return,
stack alignment/balance, and nonvolatile GP preservation with volatile-register
clobbering at stub boundaries. Virtual element destructors, allocator release,
CString destruction, and logger destruction are explicit successful stubs.
Funclets are invoked with a synthetic parent frame; the C++ runtime is not run.

**Scope of the finding:** local object cleanup is present and now has bounded
offline coverage. No selected action or executed local helper directly calls
the explicit `SafeSlotRelease` wrapper `0x14066d9e0`. An exception from zone
execution bypasses its normal call at `0x14069fe0d`. This is not yet proof of a
whole-program slot leak: virtual destructors and outer handlers may have further
ownership behavior. A release that throws may also have changed ownership before
throwing, so adding an unconditional retry is not justified. Exceptions inside
destructors, constructor-internal cleanup, slot ownership after exceptional exit,
and outer caller containment remain separate implementation questions.

Validation: all four `SynchronousBodyTests` pass in 3.534 seconds; the complete
offline verifier passes **36 tests in 10.321 seconds**, with no editor errors.
No executable was changed or run natively. W7-QUAL-01 remains unchanged: native
target exception qualification is **waived - unverified**, not a prerequisite.
The release operation and immediate caller checks are recorded in the newer
[slot-retirement evidence](#synchronous-slot-retirement-and-caller-unwind-2026-09-22);
their remaining implementation questions are not new target-test requirements.

## Synchronous body and entry unwind evidence, 2026-09-22

The existing verifier now loads `0x14069fcd0` from the retained workers report
and checks every instruction against the SHA-pinned stock PE. A dedicated
emulator executes the real dispatcher, replacement GetThread entry, and real
synchronous body. Configuration, construction, zone execution, the virtual
storage-manager call, slot release, cleanup, and logging remain explicit stubs.

Four zone-result/slot-release-result combinations establish this normal order:
zone execution returns, failure is logged if its AL is zero, storage-manager
lookup runs, slot release returns, local cleanup and logger destruction run,
and the synchronous body returns AL=1. Both zone failure and slot-release failure
are masked by this unconditional success result. Argument checks cover the zone,
result offset, storage receiver, storage identity, and zone identifier. The
dispatcher preserves its nonvolatile GP registers and balanced stack; no modeled
asynchronous admission occurs.

Injected harness failures at zone execution, slot release, and local cleanup
prevent a normal-return observation. These are Python hook failures, not Windows
exceptions: they do not exercise C++ cleanup, exception handlers, or native unwind
through the synchronous treatment body.

The separate Windows AMD64 test invokes `RtlVirtualUnwind` with handler type zero
against a source-verified copy of the PE in explicitly PAGE_READWRITE memory.
Neither the PE nor copied instructions or handlers execute natively. Its stock
runtime-function bounds are RVAs `0x6a1660..0x6a1837`, with unwind data at
`0xfd7bb8`; the version-one header and prologue codes are checked exactly. The
candidate's reachable entry offsets 0 and 2, and unchanged-stock controls at
offsets 0 and 3, all recover the synthetic caller RIP and RSP while preserving
nonvolatile GP and XMM6-XMM15 state. The allocation is released in `finally`.

Validation on Windows NT 10.0.19045.0, CPython 3.14.5 AMD64:

```powershell
.\.venv\Scripts\python.exe .\tools\verify_worker_admission.py
.\.venv\Scripts\python.exe -O .\tools\verify_worker_admission.py
```

The normal run passed 16 methods, including the Windows test (not skipped).
Optimized execution refused with exit 1 before tests; VS Code reported no harness
errors. A skipped native test on another platform does not reproduce this proof.
This qualifies only virtual stack recovery at the replacement entry's reachable
boundaries with the retained metadata. It does not qualify exception dispatch,
handler selection, hook unwind, production loading, or the complete release gate.

The immediate zone executor `0x140735f10` still calls virtual slots `+0x1f8` and
`+0x138`, `ExecuteAll_Components`, and `0x140735910`. Their complete lifetime
contracts are not established by the new stubbed experiment. `SafeSlotRelease`
at `0x14066d9e0` calls storage helper `0x140578dd0`; it is not evidence of joining
worker threads or callbacks. Consequently normal synchronous return, including
AL=1, remains insufficient to authorize storage retirement or reuse.

## Supported single-lane admission coverage, 2026-09-22

The verifier now locks the complete retained executable incoming-reference sets:

- GetThread `0x1406a1660` has one executable caller, the dispatcher at
  `0x14069fbfd`.
- The dispatcher `0x14069fb80` has two executable receiver call sites,
  `0x1406a8f32` and `0x1406a9104`.
- Synchronous treatment `0x14069fcd0` has the dispatcher fallback at
  `0x14069fc94` and direct receiver calls at `0x1406a8eda` and `0x1406a90e1`.

The two retained DATA references to each function have no containing caller and
are not counted as executable calls. Exact receiver instructions establish that
the first work path selects direct synchronous treatment when `[RSI+0xf58]` is
zero and otherwise selects the dispatcher unless `[RSI+0x17e8]` is nonzero. The
queued-work loop routes mode 2 directly to synchronous treatment and mode 1 to
the dispatcher; other values do not call either treatment path. Thus every
retained asynchronous admission on the supported single lane reaches GetThread,
and the startup-only `xor eax,eax; ret` replacement forces those paths through
the dispatcher's synchronous fallback. Existing direct synchronous paths need no
admission interception.

The source-byte and caller-set checks fail closed if a call site, branch, or
executable incoming reference changes. `python tools/verify_worker_admission.py`
passes all 16 methods. This closes retained single-lane admission coverage only;
it does not establish descendant quiescence, exception containment, ownership,
or safe CAO/storage retirement and reuse.

No Rev6 generator or PE was created. Single-lane startup coverage, remaining callback
quiescence, production-vector ownership, CAO reuse, and real exception containment
remain blocking. Generation-tagged target runtime evidence requires a separately
authorized isolated target run; the existing offline approval does not allow it.

## Export-thread descendant ownership, 2026-09-22

Read-only saved-project extraction resolved `CLibraryHelperExportThread::Handler`,
`PushResult`, `Start`, and `Stop` in stock `AvVTraitLib.dll`, plus the four unnamed
record construction/copy/destruction/append helpers. Every retained instruction
in [the method report](../maps/rev2a_export_thread_string_xrefs.json) and
[the record-helper report](../maps/rev2a_export_thread_records.json) matches the
identified DLL (`0f9f68b118112cea87e1735995776934d8d009e3d6d39a8a58562e3fa3e3e5f7`).

`PushResult` reads `CInputIdentity`, `CModelResult`, and `SCertifiedResults` while
holding the export object lock and appends `0x90`-byte value records. The record
copy helper constructs sixteen `CStringT` fields at offsets `0x00` through `0x78`
and copies scalar fields at `0x80` and `0x88`; its destructor releases those
sixteen strings. The handler passes the owned record vector to the export builder,
destroys each record, and resets the vector end to its beginning. It does not
defer or retain any of the three `PushResult` argument pointers.

`Start` creates the long-lived handler thread. `Stop` sets its stop flag, signals
the wait primitive, and attempts a 60-second join before its failure fallback.
That process-lifetime worker can outlive synchronous component treatment, but its
queued data cannot alias CAO/result/certification storage after `PushResult`
returns. The verifier locks this contract with stock DLL bytes and now passes all
16 methods. This closes the concrete export-thread ownership escape only; it does
not prove the posted UI callback, exception containment, or general CAO retirement.

## Posted SKIP callback dependency, 2026-09-22

The registered message GUID `{FEA8416F-2D59-478F-BEFF-5D96AFD6A551}` is
shared by seven translation-unit globals. Following only the optical sender's
global would miss the receiver. The receiver uses `DAT_1411982c8`; the complete
32-byte MFC map entry at `0x140eacd20` decodes as
`<IIIIQQ> = (0xc000, 0, 0, 0, 0x1411982c8, 0x1406b0700)`.
The verifier checks these map bytes directly against the SHA-pinned stock EXE,
independently of saved-project pointer-search metadata.

The [handler report](../maps/rev2a_skip_ui_handler.json) resolves
`0x1406b0700`, which forwards the receiver unchanged to refresh `0x1406adaf0`.
The [refresh report](../maps/rev2a_skip_ui_refresh.json) shows that it reads
the CAO pointer at view `+0xe8`, obtains its skip list, then reads the live
array count at `+0x10` and backing pointer at `+8`. Zero WPARAM/LPARAM does
not remove this dependency. Both optical treatment and `ExecuteSkip` post
the shared message to the window at `[[CAO+0x5838]+0x40]`.

The [document lifecycle report](../maps/rev2a_skip_ui_document_lifecycle.json)
connects that window to the receiver: `CProductionView::OnInitialUpdate`
(`0x1406af770`) reads view `+0xe8` and stores the view at CAO `+0x5838`.
This proves initialization binding only, not safe document replacement or
window teardown. The [storage report](../maps/rev2a_skip_ui_list_storage.json)
shows `SkipList_Get` (`0x140541040`) is simply `lea rax,[rcx+0x23e0]; ret`.
It returns embedded live storage, with no copy or lock. `SkipList_Reset`
(`0x140541050`) calls `CUIntArray::SetSize` on that array with size zero,
then calls `ClearTestVectorForSkip`. Complete caller synchronization remains open.

Two new regression methods verify retained instruction bytes, receiver mapping,
GUID agreement, initialization binding, getter/reset semantics, and bounded
execution of the real callback, refresh, and getter up to the first value read.
With UI/MFC helper calls stubbed, four imposed pre-dispatch fixtures establish:

- Unchanged storage returns the original value `17`.
- Reused array contents return the replacement value `42`.
- Rebinding view `+0xe8` returns the new document's value `42`.
- Artificially unmapping the old array storage faults with an unmapped read at
  `0x1406adb44`, the first array-count access.

These are synthetic schedules, not observed station races or proof that document
rebinding occurs on a supported path. These original four cases do not execute reset, UI delivery,
exception dispatch, teardown, or the complete refresh. Synchronous worker
containment does not drain `PostMessageA`; safe array lifetime and pending-message
ordering must still be established before reset, retirement, or reuse.

Validation: the focused callback tests passed, the full
`python tools/verify_worker_admission.py` harness passed all 18 methods, and VS Code
reported no errors in the harness. No Rev6 executable was generated and Vision3D
was not executed natively. No lifecycle gate was promoted to pass.

## Reset and in-flight callback evidence, 2026-09-22

The [reset-boundary report](../maps/rev2a_skip_reset_boundary.json) and
[remaining caller report](../maps/rev2a_skip_reset_callers.json) resolve every
retained direct executable reference to `SkipList_Reset`:

| Caller | Entry | Reset call site |
| --- | --- | --- |
| `CCOMObjectMgr::CCOMObject::AskListOfSubPanelsToSkip` | `0x1404ae9d0` | `0x1404aebe9` |
| `CProductionDoc::PrepareExecData` | `0x14068f0f0` | `0x14068f7d7` |
| `CProductionDoc::ReloadDoc` | `0x140692af0` | `0x1406937d7` |
| `ExecuteSkip` | `0x1406a06b0` | `0x1406a085e` |
| `CProductionThread::HandlerProduction` | `0x1406a20d0` | `0x1406a2d87` |

The verifier checks both the incoming-reference set and these caller instructions
against stock bytes. This is retained direct-reference coverage, not proof that
exported or indirect calls cannot occur. Caller identities are supported by
their retained logging strings. The COM method has an additional direct wrapper
at `0x1404aecd0`; its argument forwarding and CCAPM dispatch are now resolved
below, but caller-level synchronization remains unproved.

The COM method resets the list, then loops over returned subpanel identifiers and
calls `SkipList_Add` at `0x1404aec17`. The [writer report](../maps/rev2a_skip_list_add.json)
shows `SkipList_Add` (`0x140541020`) adds `0x23e0` to RCX, moves the value to R8D,
loads the array count from `+0x10` into RDX, and tail-calls
`CUIntArray::SetAtGrow`. The four-instruction wrapper has no local lock and writes
through the same embedded array used by the UI reader. This does not establish
the MFC implementation or caller-level locking. `ClearTestVectorForSkip`, called
after array reset, also clears CAD flags through virtual calls and per-entry
flags in the skip-test vector at CAO `+0x2448`; reset is not merely a UI change.

The callback emulator now includes three additional imposed schedules. It pauses
the real refresh, saves its register context, executes the stock reset wrapper
on a separate fixture stack, restores the callback context, and resumes it.
`SetSize(0)` is explicitly modeled by clearing the backing pointer and count;
`ClearTestVectorForSkip` is stubbed. The reset wrapper's arguments, helper order,
return address, and stack balance are checked. Results:

| Reset placement | Observed stock callback behavior under the model |
| --- | --- |
| Before first size check at `0x1406adb44` | Branches to empty-list completion at `0x1406adbbe`; no element read. |
| After first size check, paused at `0x1406adb50` | Reaches the `AfxThrowInvalidArgException` call site at `0x1406adbb8`; exception dispatch is not executed. |
| After bounds validation, paused at `0x1406adb67` | Reloads the modeled null backing pointer and faults on the element read at `0x1406adb6b`. |

The CAO object remains mapped throughout these three cases. Thus document
lifetime protection alone is not a sufficient contract under this model: mutation
must also be serialized with the entire callback traversal. These experiments do
not establish real scheduling, MFC allocation/free behavior, shared locks in
opaque callers, or actual station failures. The existing production library lock
is not evidence of a matching lock in this UI reader.

Validation: both focused callback methods pass with all seven scenarios, and the
full harness still passes 18 methods. VS Code reports no Python diagnostics.
Only read-only extraction, offline emulation, tests, and this ledger were changed;
no project lock was disturbed, no Rev6 PE was generated, and no native Vision3D
execution occurred. The callback gate remains blocked pending a verified common
mutation/lifetime barrier or a separately justified snapshot/notification design.

## CCAPM reset dispatch and document access, 2026-09-22

The [COM wrapper](../maps/rev2a_skip_com_wrapper.json) forwards the original
CAO argument in RDX to `0x1404ae9d0`, using the first COM object from the
manager's vector as RCX. The [adapter](../maps/rev2a_skip_com_dispatch.json)
at `0x14075ad60` adds `0x10` to RCX and tail-calls that wrapper, leaving RDX
unchanged. Stock RTTI identifies the secondary vtable at `0x140eddbd0` as
CCAPM with complete-object offset eight; slot `+0x80` points to the adapter.

The [application constructor](../maps/rev2a_skip_capm_app_binding.json)
constructs CCAPM at application `+0x1a8`. The
[CCAPM constructor](../maps/rev2a_skip_capm_table_binding.json) installs this
secondary vtable at CCAPM `+8`, matching application `+0x1b0` in `ExecuteSkip`.
At `0x1406a0845`, `ExecuteSkip` invokes slot `+0x80` with its document pointer
in RDX. AL equal to one branches to `0x1406a1056`; otherwise the path reaches
the local reset at `0x1406a085e`. This COM reset path is nested in ExecuteSkip,
not evidence of an independent asynchronous COM callback. Reentrancy and
serialization with posted UI callbacks are not established.

The production-thread accessor `0x1406a15d0` invokes secondary-interface slot
`+0xe0` with the index from thread `+0xec0`. Its resolved
[document getter](../maps/rev2a_skip_capm_document_accessor.json),
`0x14075d010`, returns a stored pointer from the array whose begin/end fields
are interface `+0x2e8/+0x2f0` (complete CCAPM `+0x2f0/+0x2f8`). It returns
zero when the signed index is at least the computed count; there is no local
negative-index rejection, copy, reference acquisition, or lock.

Adjacent slot `+0xe8` resolves to the
[document setter](../maps/rev2a_skip_capm_document_neighbor.json),
`0x14075d040`. It uses the same signed bounds comparison and directly stores
R8 into that array, returning AL one on the store path or zero otherwise.
There are no ownership or synchronization calls in this body. A bounded search
of retained Rev2a instruction reports found only an unrelated component-object
call to slot `+0xe8` at `0x1407355d1`; it does not identify a CCAPM publication
caller. This search is not exhaustive coverage of the executable.

The callback evidence tests now check these reports against the stock hash and
instruction bytes, all three virtual-slot targets, RTTI identity, constructor
binding, ExecuteSkip branch selection, and complete getter/setter instruction
sequences. Focused callback tests pass with all eight modeled schedules,
including the CCAPM-cleared schedule described below.
These checks establish pointer provenance and raw publication semantics, not
equality with a particular view's CAO, valid index provenance, document ownership,
or a mutation/retirement barrier. No lifecycle gate is promoted to pass.

## CCAPM publication and retirement, 2026-09-22

The earlier retained-report search is superseded by a bounded saved-Listing
[slot scan](../maps/rev2a_skip_document_slot_scan.json) and
[receiver windows](../maps/rev2a_skip_document_slot_windows.json).
The scan visits 2,639,324 instructions and finds 46 explicit CALL/JMP
`[register + 0xe8]` operands in 34 containing functions. Every retained
instruction window is checked against stock bytes. This is not exhaustive
indirect-call coverage: register-loaded targets, undefined code, and unsaved
project changes are outside the scan. A matching slot alone does not identify
CCAPM; inspected machine-controller and MFC view-iteration calls were false
positives.

The [publication and destruction bodies](../maps/rev2a_skip_capm_document_publication.json)
resolve actual CCAPM callers:

- `CProductionDoc::SetProductionVMC`, `0x140697200`, constructs the receiver
  at application `+0x1b0`. In its mode-zero branch it zeros document
  `+0x3924/+0x3928`, sets the current VMC, publishes the original document
  in slot zero at `0x14069744c`, then explicitly clears slot one at
  `0x14069745f`. Assembly supplies R8 zero for the second call even though
  the decompiler omits that argument. Other branches publish using mode-derived
  indices; this is not proof of which mode every supported deployment uses.
- `CProductionDoc::~CProductionDoc`, `0x14067fc20`, calls `DeleteVector`
  at `0x14067fd30`, `DeleteCadTab` at `0x14067fd3d`, and asynchronous-command
  `Kill` at `0x14067fd4b` before clearing its CCAPM slot at `0x14067fdc0`.
  Clearing uses the document index at `+0x3924` and R8 zero. This order does
  not prove a race occurs, but the later clear cannot itself establish a
  barrier before the earlier cleanup calls. Neither the setter result nor a
  pending SKIP-message drain is checked in this local clearing sequence.

The existing callback test now executes the stock setter and getter against
an imposed fixture before dispatching the stock callback: setter succeeds,
getter returns null, and the independent view binding at `+0xe8` still points
to the original document. The callback reads its original value (17). Thus
CCAPM clearing alone does not revoke that UI binding. This eighth modeled
schedule does not execute the destructor, the MFC message loop, or an actual
station teardown, and does not establish real concurrent access.

Regression assertions check publication/clearing arguments, receiver provenance,
cleanup order, and all retained function bytes. All six entry obligations remain
open. The following section resolves the direct destructor wrapper
`0x1406807e0` (call at `0x1406807ef`); publication has retained direct callers
`0x14068dab0` and `0x14068dc20`. Caller-level synchronization, view teardown,
and the relationship between document `+0x3924` and thread `+0xec0` still need
proof. No Rev6 artifact or native Vision3D execution was produced.

## Document close path and supervisor reentrancy, 2026-09-22

The [direct lifecycle wrappers](../maps/rev2a_skip_document_lifecycle_wrappers.json)
rule out a barrier in the deleting destructor wrapper: `0x1406807e0` calls
the destructor unconditionally at `0x1406807ef`, then tests deletion flags.
`OnNewDocument` (`0x14068dab0`) calls `SetProductionVMC(document, 0)` before
the MFC base implementation. This establishes mode-zero publication for this
entry, not every supported document-opening path.

Stock document-vtable bytes at constructor-installed `0x140ea3868` resolve the deletion wrapper,
new/open document methods, and [close overrides](../maps/rev2a_skip_document_close_overrides.json).
`OnCloseDocument` (`0x14068d9d0`, slot `+0x118`) calls these
[helpers](../maps/rev2a_skip_document_close_helpers.json) before tail-calling
`CDocument::OnCloseDocument` at `0x14068da31`:

- `RegistrySave` (`0x1406928d0`) reads the live SKIP count at document
  `+0x23f0` and entries through `+0x23e8`. It is another live-storage consumer,
  not a local array snapshot or drain.
- `0x14063b430`, receiving document `+0x3850`, clears strings and conditionally
  uses a semaphore, increments a counter, and disconnects the supervisor.
  Its `WaitForSingleObject` result is not checked before the increment.
- `0x1404e03f0` sets application `+0x830` and posts message `0x52c`, wParam 6,
  to document views found through CCAPM. Posting is not synchronous completion
  of those handlers and does not itself retire queued SKIP callbacks.

The [nested supervisor helper](../maps/rev2a_skip_document_close_nested.json)
`0x14064b880` waits on supervisor `+0x118`, constructs a wait box, and, while
supervisor flags `+0x14 & 0x0c` are set, calls `Sleep(50)` and imported
`DYTOOLS0!DoEvents` at `0x14064b8fb`. It then calls
`CTalkToSuperviseur::DeConnect`, releases the semaphore, and destroys the wait
box. Its wait result is also unchecked. This is a concrete message-pumping
dependency before MFC close, not proof of which messages actually dispatch.
DoEvents internals, callback filtering, and reachable supervisor states remain
unverified; the close stack cannot simply be assumed non-reentrant.

The sibling document method `0x14068ee00` posts WM_COMMAND `0xb24c` and returns
one without checking the post result. The stock message-map entry at
`0x140eacae0` points to [handler `0x1406b1840`](../maps/rev2a_skip_document_posted_command.json).
That handler has application/document conditions and additional calls; its
presence is not evidence of a completed close or callback barrier.

The verifier checks every retained function instruction against the stock PE,
the document-vtable slots, the posted-command map, and the full close override.
A new bounded test executes the actual supervisor helper in eight combinations
of successful/failed wait, busy/idle flags, and visible/hidden wait box. External
calls are stubs; the DoEvents stub clears the imposed busy bits. Both wait
results reach the same sequence, including one pump for busy cases and later
disconnect/release. Return, stack balance, and nonvolatile registers are checked.
All 19 test methods pass. This is not a native message-loop, teardown, exception,
or station test, and no entry gate is promoted.

The next lifecycle proof must establish what prevents dispatch/reentry through
the supervisor pump, and how MFC closes views and invalidates their document
bindings before deletion. A failed-wait guard in this supervisor helper alone
would not supply that proof. The six entry obligations remain open; no Rev6
generator or modified PE was produced.

## Required next evidence

Allocation/reset/reuse continuation: the
[reset-boundary map](../maps/document-lifecycle.md#reset-and-reuse-boundaries)
now establishes conditional reset in both `PrepareExecData` and the
`HandlerProduction` cycle-start path. Lane-zero application byte `+0x18d`
controls preservation: every nonzero value skips the production reset call
at `0x1406a2d87`. Preparation can also bypass reset for an empty vector or
reapply existing skips, and ReloadDoc resets then restores a saved list.
Twelve preparation and four cycle-start fixture scenarios confirm the stock
branch decisions with bounded external stubs. These are not station schedules
or a proof that any complete preparation invocation succeeds without reset.

The reset hook at `0x140541050` is not yet an unconditional per-cycle counter
reset. The [policy writer trace](../maps/document-lifecycle.md#manual-skip-policy-writers)
now identifies `+0x18d` as the lane-one manual-skip policy: RegistryRead assigns
`Production.ManualSkipLane1 != 0`, and standard production start copies the
dialog policy, whose permission-gated command `0x820` can set it to one.
Remote single-production start explicitly clears it, but single-lane support
alone does not imply remote-only operation or a zero policy. Four bounded
stock-instruction cases confirm registry DWORD conversion to 0/1; this is
not a station setting or a complete production execution trace.

Either obtain approval for and verify a manual-skip-disabled operating
restriction, or obtain scoped approval for a separate patch-state boundary;
both still require old-work quiescence before reuse. Do not force-clear stock
operator choices or silently add identity/generation machinery. No gate is
promoted and no Rev6 PE is built.

Station runtime received, 2026-09-22: the user supplied
[mfc140.dll](../v3d_files_/mfc140.dll), AMD64 MFC 14 version `14.23.27820.0`,
SHA-256 `0cf26008fae0cb61dfe49e1c3fc17e0dd860be011d9a6a64b452f56335bafbfe`.
Host Authenticode is Valid/Microsoft; architecture and EXE ordinal coverage pass.
The [intake](../maps/document-lifecycle.md#station-mfc-14-intake-2026-09-22)
supersedes the acquisition deferral. Original installed path and loaded-module
identity remain unverified. No native DLL loading occurred. The subsequent
[MFC static analysis](../maps/document-lifecycle.md#station-mfc-static-analysis)
imported a separate project and resolved ordinals 11881, 8850, and 3959.
Unfiltered pump selection and the nested modal-pump path are established;
reachable callback schedules and view/window retirement remain unproved.

Independent EXE continuation resolved both selected posted-command bindings.
The [helper](../maps/rev2a_skip_posted_ui_helper.json) at `0x140675f90` is a
four-instruction `InvalidateRect(HWND, NULL, TRUE)` wrapper, not a local stop or
lifetime barrier. The document constructor installs `SkipProductionElmt_Sheet`
at `document+0x3990`; its vtable `0x140eb0360`, slot `+0x2e0`, selects thunk
`0x14077f754`, IAT `0x140d5ec88`, `mfc140.dll` ordinal 3959, labeled
`CPropertySheet::DoModal`. The [binding chain](../maps/document-lifecycle.md#posted-command-bindings)
includes stock-verified construction, RTTI, vtable, thunk, and import checks.
Native modal dispatch/retirement remains unverified after the static MFC trace;
no runtime implementation is inferred from intake alone. Continue admission, ownership,
and allocation/reuse analysis alongside the now-available runtime. Retain the
no-Rev6-build restriction until all entry obligations pass.

Offline-programmer intake, 2026-09-22: the alternative
[mfc100.dll](../v3d_files_/mfc100.dll) is AMD64, version `10.00.40219.325`, with a
valid Microsoft Authenticode signature on the analysis host. Its embedded identity
is MFC 10, not the MFC 14 runtime imported by the mapped executable, so it cannot
resolve the pump/base-close implementation boundary. The
[intake record](../maps/document-lifecycle.md#offline-programmer-mfc-intake-2026-09-22)
retains its hash and limitations. At that earlier intake the user reported station acquisition blocked by
`Trojan:Script/Wacatac.B!ml`; no security bypass or quarantine restoration was
attempted. A vendor/offline-programmer MFC 14 artifact may provide reference
evidence, but deployed-runtime equivalence still needs separate confirmation.
No gate is promoted by this intake.

Runtime intake update, 2026-09-22: the user identifies the target as **Windows 7
Embedded x64**. The previously supplied `v3d_files_/mfc140.dll`, version
14.0.24210.0, is **x86/PE32**, not AMD64/PE32+ like the mapped Vision3D executable.
Raw headers independently agree with pefile; the
[lifecycle intake record](../maps/document-lifecycle.md#supplied-mfc-intake-2026-09-22)
retains its hash, size, and export-table checks. It is not accepted as the x64
runtime and was not imported into Ghidra. The newer AMD64 intake supersedes the
missing-file requirement; its original station location remains unverified. Do not substitute x86 ordinal bodies
or treat development-host unwind results as Windows 7 station qualification.

Latest continuation, 2026-09-22: the [lifecycle atlas](../maps/document-lifecycle.md)
now records the posted UI-command descendants and actual
[DyTools0 DoEvents body](../maps/rev2a_skip_doevents.json). The
[command descendants](../maps/rev2a_skip_close_command_descendants.json) show
password/configuration logic, window reparenting, the now-bound modal-sheet call,
and invalidation/redraw; they do not establish a close or stop barrier.

The exact EXE import at `0x140d53fc0` resolves to the DLL free-function export
`?DoEvents@@YAXXZ`, VA `0x1800772b0`, ordinal 1468. Its stock body uses unfiltered
`PeekMessageA(&message, NULL, 0, 0, PM_NOREMOVE)` selection, obtains `AfxGetThread`, and
calls thread virtual `+0xc8`. It has no local SKIP exclusion. A separate regression
checks the import/export identity, every retained DLL instruction, and five
bounded queue/thread/pump-return fixtures. Actual dispatch remains stubbed.

The application vtable `0x140e39770` maps `+0xc8` to thunk `0x14077f982`,
IAT `0x140d5fd20`, MFC ordinal 11881. Base document-close thunk `0x14077fe26`
maps IAT `0x140d5f5f8` to ordinal 8850. These stock bindings are regression-checked;
the dynamic thread receiver remains unproved. The ordinal implementations are
now retained in 28 stock-verified MFC reports. Keep pinned file identity and
user-reported provenance distinct from proof of the station's loaded module.

Current full verification: **57 test methods pass in 34.379 seconds**, including
the production-thread join check, the production stop-flag check,
the `WM_CREATE` message-map delivery case, the `WM_CREATE` view-list insertion case, the menu-bar pretranslate case, the null-HWND thread-message case, and the document-close view-list ordering case,
the template view-class context case, the production-view dialog-parent case, the receiver `CZoneData` unwind case, the zone-storage `bad allocation` case, the system-mdiclient destroy case, and the main-frame title-slot cases, plus the earlier set of
station MFC identity/import checks, corrected document-vtable anchor, close/modal
bindings, six bounded actual-pump scenarios, thirteen cached receiver cases,
three production-frame destruction cases, production-view construction/map
bindings, six integrated list/pool-release/document-update fixtures, thirteen
window/map-detach cases, nine thread-slot branch cases, two constructor cases,
and six view-list-change branch cases. Constructor, import-binding, and
window-detach tests also pass in a focused three-test run (0.332 seconds).
Actual empty-map cleanup, cached state selection, and fresh-state construction
and publication now execute. OS allocation, visibility, CRT division, Windows
TLS, and critical-section calls remain stubbed. TLS growth and exception paths
remain outside execution. This supersedes the earlier
24-method intake and historical 19-method run above. No native target execution,
modified PE, or Rev6 builder was produced, and all six entry obligations remain
open. Mapping additions are filesystem atlas/reports; the active Ghidra session
and project locks were left untouched.

MFC continuation: separate `MFC140_STATION` analysis completed in 151 seconds;
PDB analyzers, Function ID, and Decompiler Parameter ID were disabled. Import
consulted host dependency/export metadata, so inferred labels are not target
Windows 7 compatibility evidence. Fifty-one retained function bodies are byte
checked against the supplied MFC. Pump selection is unfiltered; pretranslation
may consume messages. The property-sheet loop delegates to the same thread
pump. The prior document-vtable anchor was eight bytes late; constructor
`0x14067decc` / `0x14067ded3` proves `0x140ea3868`, with close at `+0x118`.
Base MFC close calls return-only document hooks at `+0x1c8` and `+0xf8`, an
application-owned receiver path at `+0x1b0`, and conditionally the known deleting
wrapper at `+0x8`. The [close continuation](../maps/document-lifecycle.md#station-mfc-static-analysis)
now binds application `+0x208` to ordinal 5167 / `0x1801d0230`, which can
preserve application `+0x120` even with feature bits clear. Its allocated
receiver uses recovery-map/file cleanup methods, not an identified drain.
Production template frame `CProductionChild` installs `0x140ea1720`; `+0xd0`
selects ordinal 3803 / `0x1802abb20`, which synchronously sends
`WM_MDIDESTROY` and returns one without checking that send's return value.
Production view constructor `0x1406ab570` installs vtable `0x140eac650`.
Its own `WM_DESTROY` still accesses the live document; inherited `WM_NCDESTROY`
reaches deleting slot `+0x8` through `+0x250`. The destructor chain reaches
MFC `RemoveView` at `0x18021fae0`: list unlink/count reduction precedes the
`view+0xe8` clear at `0x18021fb0d`, followed by document `+0xf0` notification.
That notification selects close `+0x118` only for an empty list and nonzero
auto-delete flag `+0x120`; otherwise it selects frame-count update `+0x1e0`.
Base close clears that flag temporarily, but this does not eliminate callbacks.
Pool cleanup occurs before the pointer clear on last-view removal. Its actual
block loop is now exercised with imported `free` stubbed. The document's pinned
head/next iterators and frame-update body run after notification: with an empty
list and auto-delete disabled, all three passes return without visibility or
frame callbacks. Remaining-view cases cover hidden views only. This resolves
that bounded normal continuation, not visible-frame or earlier teardown reentry.

Before deleting the view, window detach `0x18028f560` calls noncreating map
lookup `0x18028f3c8(0)` and, when a map exists, key removal `0x180236b90`.
Actual removal bytes unlink a present HWND key before recycling the entry;
detach then clears `view+0x40` and `+0xd0`, but not `+0xe8`. Thirteen fixtures
cover absent and collision-chain cases plus zero/one/two-block singleton cleanup.
The caller ignores removal failure, so cleared fields alone are not an unbinding
oracle. Empty-map cleanup now executes actual bucket release, pointer clears,
and the block-release loop, with only the allocator stubbed in that continuation.
HWND/document fields remain live during these frees. Cached module/thread-state
selection also executes, with a decoy TLS slot left untouched and two balanced
critical-section sequences. Windows TLS and locks remain stubs, not proof of
native synchronization. Nine additional branch cases stop before state factories,
slot allocation, or failure handling. A new integrated case executes the state
factory, its zero-filled allocation wrapper, constructor, and publication into an
existing TLS array. The constructor preserves map `+0x28`; allocator zeroing
establishes its initial NULL value. Two constructed cases select a fresh or empty
cached state while another slot owns the HWND mapping. Both clear view fields and
return the old HWND without removing the owning map's entry. This disproves
initialization as an ownership-recovery mechanism, not the reachability of wrong
state on the station. Correct owner-thread/module-state/map selection is required;
successful allocation or nonzero state alone cannot replace that proof. No
cached-pointer or pending-message guarantee follows from these local tests.
The top-frame virtual `+0x358` is now bound. Getter `0x1802ac6a0` walks two
`GetParent` calls and tail-jumps to `0x18028f480`. The offset-zero
`CMDIFrameWnd` vtables found in `.rdata`/`.data` are `CMainFrame`
(`0x140e8dc48`) and `CExtNCW<CMDIFrameWnd>` (`0x140e8ce88`); both slots select
`0x140639c80`. That wrapper calls `mfc140.dll` ordinal 11444 and, when the
saved HWND still exists, tail-jumps `SendMessageA` with `WM_NCPAINT` (`0x85`).
Ordinal 11444 updates the frame title and can reach `SetWindowTextA` through
`0x1802a4700` / `0x1802b3620`. Those direct calls send synchronous window messages. Slot `+0x2e8` is ordinal
4861 on both `CMainFrame` and `CProductionChild`: it returns `view+0xe8` only
while that frame's `+0x170` is set. View `WM_DESTROY` clears `+0x170` on the
nearest frame ancestor before `CWnd::OnDestroy`. Production frames create a
system `mdiclient` and store its HWND at `frame+0x1d8`. `CProductionChild`'s
create body sends `WM_MDICREATE` to that field, either on its sixth argument
or, when that argument is null, on the current thread's main-window field at
`+0x40`. The only `mov edx, 0x221` in the MFC text is the existing destroy
send. EXE `CMDIClientWnd` does not handle that message; MFC
`CMDIClientAreaWnd` does, and CreateClient does not construct it. On this
development host's user32, not the waived Windows 7 station and not
Vision3D, `WM_MDIDESTROY` delivers `WM_DESTROY` to the MDI child and a direct
child before `SendMessage` returns. The production view's create path parents
its dialog to the `CProductionChild` HWND: child `WM_CREATE` reaches
`OnCreateClient`, which calls `CreateView` with that frame, and
`CFormView::Create` passes `[parent+0x40]` to `CreateDialogIndirectParamA`.
The constructor stores dialog id `0x82b` at view `+0x130`, so the null-template
return is not the path taken for this object. Both startup templates register
`CProductionView` at template `+0xc0`. The installed template vtable copies
that field to create-context offset 0, and `LoadFrame` places that context in
`MDICREATESTRUCT+0x30`, which `OnCreateClient` reads as the class to create.
The view's destroy clears the nearest frame, which is
this child. The title function calls `this+0x2e8` first and skips the active
child's `+0x2e8` when that result is non-null. The active child comes from
`WM_MDIGETACTIVE` (`0x229`) sent to `frame+0x1d8`. Production `OnActivateView`
does not call SetActiveView, and the EXE does not import ordinal 12856.
After the host send returns, the child fallback cannot name this view. The
title still returns the production document when the top frame's own
`+0x170` holds it. The caller that passes the MDI parent argument and the
store that publishes the main window remain open.
Virtual `+0xe0` on `frame+0x120` remains unexpanded. A temporary `CWnd` from a missing map
entry is outside this binding. See the top-frame title slot in
[document lifecycle](../maps/document-lifecycle.md).

The helper that writes `+0x170` from document `+0x258` is `CDocProcess` slot
`+0x320` (ordinal 3793). The production templates register `CProductionDoc`,
whose slot `+0x320` is `0x1406970b0` and calls ordinals 1504 and 1032.
The production view's imported non-clearing path at slot `+0x370` is ordinal
9697. It calls `GetParentFrame(this)`, keeps that frame when it is a
`CFrameWnd`, and passes it to SetActiveView. `CProductionChild` derives from
`CMDIChildWnd`, whose base is `CFrameWnd`, so this path writes the child
frame rather than the top frame.
Remaining dependencies are whether any other path stores the production view
in the top frame's `+0x170`, possible alternate/reparented frame receivers, and
actual pending-callback ordering, including reentry from `WM_SETTEXT` and
`WM_NCPAINT`. On the Windows 10 development host, a queued instance of the
exact registered SKIP message is removed by `DestroyWindow`, and a later post
to that stale HWND fails. This is not Windows 7 qualification and does not
cover producer-side object dereferences or posts racing before destruction.
The three stock posts load `[CAO+0x5838]` and then `[view+0x40]` and call
`PostMessageA` without testing the pointer, the HWND, or the return. The
posts at `0x1406a103b` and `0x1406a1075` call `0x1406a15d0` first. The post
at `0x140736feb` reads `[[this+0x10]+0x5838]`. Constructor `0x140735120` stores `r8` there. One caller passes `[this+0x28]` from vtable `0x140ea8a10` slot `+0x18`. `0x1406a6b95` reloads through `0x1406a15d0` and `0x1406a4980` copies that pointer to each worker at `thread+0xec8`. Close does not call that copy. The other caller passes the result of `0x1406a15d0`. The
constructor stores zero there, `OnInitialUpdate` stores the view, and those
are the only executable writes of displacement `0x5838`. Production
`OnCloseDocument` tail-jumps ordinal 8850, which calls frame slot `+0xd0`
for every view still in the document list before document slot `+0x8` runs
the destructor that releases `+0x2448` and `+0x23e0`. The production view map
has no `WM_CREATE` entry. The create hook subclasses the new HWND to a
procedure that calls `AfxWndProc`, and message 1 reaches `CWnd::OnWndMsg`,
which follows the production map's base and calls the `CFormView` handler.
That handler restores the create context and `AddView` links the view, then
ordinal 8734 sees a nonzero count. A list emptied by `RemoveView` skips that
destruction and can still delete the document. After detach clears `view+0x40` and before the view object is deleted, the
same post is a thread message. A read after deletion uses freed storage. The SKIP handler and
its id pointer occur only in the production view map. The application map has
no `0xC000` entry, so the thread walker does not select that handler. On this
development host `DispatchMessageA` does not call a window procedure for the
thread message. `CExtMenuControlBar` slot `+0xa90` returns zero for a
registered id and sends constant message ids, so `CMainFrame` falls through
to ordinal 11812. That ordinal calls `[frame+0x120]+0xb8` only when the qword
is nonzero. Construction stores zero, and the three frame vtables contain no
qword store of that displacement. Callback retirement stays blocked.
The emulator
cases stub OS calls. The user32 probe covers this development host only and
does not promote callback retirement. None of these findings supplies
a worker barrier or unconditional counter reset.

Producer join, 2026-09-23: ExecuteSkip is reached only from
`MakeFirstPassInspection`, which is reached only from `HandlerProduction`,
which is reached only from `CProductionThread::Handler` `0x1406a1c80`.
That function is vtable `0x140ea8a48` slot `+8`. Slot `+0x10` is
`CViThread::Start`. The supplied BaseTools thread procedure tails through
slot `+8`. When document byte `+0x382d` is 1, Handler calls `0x1406a1da0`, which calls `AskToStop` and returns 0. Otherwise it calls `HandlerProduction`. Both arms then call MFC ordinal 2175, which tails to
`_endthreadex`. `ProductionStart` stores this object at document `+0x3868`.
`ProductionStop` is the only direct caller of `CViThread::Stop` on that
field. Each attempt uses timeout zero. A result other than 1 calls
`0x1405e8af0(0x1f4)`, which dispatches queued messages and sleeps before
retrying, so a failed attempt can deliver SKIP while Handler is still
running. `OnCloseDocument` and the document destructor do not call
`ProductionStop`. Its only direct caller is document vtable slot `+0x28`,
and that call runs only when the high 16 bits of `r8` are `0x4e` and the
low 16 bits are `0xb1cf`. The address is not stored as a pointer in the
image. The same function also joins the communication thread at `document+0x3860`
after `+0x3868`. `ProductionStart` stores that `0x48`-byte object before the
producer. Close, destruction, and the `0x52c` handler do not mention
`+0x3860`. Slot `+0x10` of the object at `document+0x2548` stores null at
`+0x3868` and stops only `+0x3860`. The view command handler calls slot
`+8` of that object. Before the view loop's frame slot `+0xd0`, ordinal 8850
calls document slot `+0x1c8`. That slot is MFC ordinal 11723, whose body is
`ret 0`. The view destructor `0x1406abc60` calls `CCadEngine::StopEngine` on `view+0x170`. `StopEngine` waits on the `CCadEngineThread` handle at `[engine+0x138]+0x58` after posting message `0x12`, then stores null. `StartEngine` allocates that object, and MFC ordinal 3529 stores the `_beginthreadex` handle at `+0x58`. The EXE call does not call `ProductionStop` or mention `+0x3868`. Its direct callees do not either. Its thunks are MFC ordinals 12215, 1421, and 1425: `DeleteFileA` when `edx` is 0, `DestroyWindow` on `[view+0x6f18]+0x40`, and `free` of `[view+0x6ec8]+8`. The later `lock xadd` releases `view+0x1b0`. None of those fields is `document+0x3868`. Document close therefore does not join this producer
before view destruction. The callback-retirement gate is not promoted.

Stop flag, 2026-09-23: the back-edge returns to the cycle head while
`CProductionThread+0x32` is zero. `HandlerProduction` sets that byte after
it sees document `+0x382e == 1`. A zero return from `CheckAvailableMemory`
`0x14069c770` also stores word `0x100` at `thread+0x31` and jumps to the
`AskToStop` call. The selector dword at `0x1411697c4` is in the zero-filled
tail of `.data`, and both instruction uses are reads, so that failure takes
this arm. Close does not call `0x14069c770`. App slot `+0x58` receives the
other exit flag and is MFC ordinal 7430, `mov eax, 0x80029c4a; ret`. `AskToStop`, slot `+8` of the vtable at
`document+0x2548`, is the only writer of 1. Initialization dword and word
stores cover the byte with a register that is still zero. AskToStop addresses
the byte as subobject `+0x12e6`, posts notification `0xb1cf`, and returns. The inherited
`WM_CLOSE` handler `0x1802a2aa0` calls MFC ordinal 2660 and then
`OnCloseDocument`. Ordinal 2660 does not read the flag or `+0x3868`, and
`OnCloseDocument` does not contain either displacement. Stock close still
does not ask the producer to leave, and does not wait for it. The
callback-retirement gate is not promoted.

Close message, 2026-09-23: `OnCloseDocument` calls `0x1406928d0` and then
`0x14063b430` on `document+0x3850` before `0x1404e03f0` and the tail jump to
MFC ordinal 8850. The `+0x3850` pointer is `[[AfxGetModuleState()+8]+0x40]`, and the wait is on the `CreateSemaphoreA` handle at `[object+0x5870]`. The same function releases that semaphore before returning. The call that waits on `app+0x57c8` and calls `DoEvents` runs only when the incremented dword at `+0x5868` is not 1. Neither of those functions calls `ProductionStop`.
The helper posts `0x52c` with wParam 6
through `PostMessageA`, unless byte `+0x830` is already 1. The view handler
`0x1406b0c00` switches on wParam minus one, so wParam 6 enters `0x1406b1232`.
That arm does not call `AskToStop` or `ProductionStop`; its successful path
sends `WM_COMMAND` `0xe102`, whose document handler jumps to slot `+0x118`,
`OnCloseDocument`. The `AskToStop` arm is wParam 2. The post returns before
the view is destroyed, so this message is not a join. The callback-retirement
gate is not promoted.

Stop button, 2026-09-23: wParam 2 is posted by `0x140677b30`, the
`PROD_VIEW_COMMAND` handler for `WM_COMMAND` `0xb1cf`. That window is the
object at `view+0x9c8`. Its create passes the view as parent with style
`0x50000000`, and MFC ordinal 3165 reads the parent HWND and forces
`WS_CHILD`. `WM_CREATE` builds a `BUTTON` child whose id is `0xb1cf`, through
MFC ordinal 3051 into the same create slot. The handler then posts `0x52c`
wParam 2 to `GetParent`. `.text` contains the immediate `0xb1cf` only there,
in `AskToStop`'s notify store, and in the document `OnCmdMsg` compare that
calls `ProductionStop`. Close does not execute this create or load the command. The callback-retirement gate is not promoted.

Close closure, 2026-09-23: the direct-call closure of `OnCloseDocument`, the
document destructor, production-view `WM_DESTROY`, `0x1404e03f0`, and
`OnCmdMsg` does not contain `AskToStop`, the production handler, or the
`0xb1cf` command poster. `OnCmdMsg` is the only member that calls
`ProductionStop`. The destructor writes vtable `0x140ea3b58` at
`+0x2548` and does not call its `AskToStop` slot. The callback-retirement
gate is not promoted.

View destruction, 2026-09-23: production-view `WM_DESTROY` does make the
virtual call that closure cannot see. After MFC ordinal 2207 and
`__RTDynamicCast` from `CWinApp` to `CAVisionApp`, it calls slot `+0x198`
of the `CCAPM` secondary vtable at `app+0x1b0`. That slot is `0x14075d6b0`.
It indexes a `CCAPM` pointer vector by the document dword at `+0x3924`.
The ordinary tail calls `0x1406109f0`, which enters a critical section,
updates a pointer vector, and returns the element count. That body has no
`0x2548` displacement and no `0xb1cf` immediate. The direct-call closure of
`0x14075d6b0` does not contain `AskToStop` or `ProductionStop`. Destroy's
own code is the constant `0xb`. When the indexed entry exists and
`[entry+0x3928] == 4`, `0xb` matches the second local list and the jump to
`0x14075db5a` skips `0x140611a10`. After the `CCAPM` call, destroy calls
document slot `+0x230` (`0x14045c520`), which returns `[document+0x19e8]`.
`SetProductionVMC` stores the current or lane `IVMachineController` there.
A non-null result is then called at slot `+0x10` with `view+0x160`, the
`IVMachineControllerListener` base of `CProductionView`. Initial update
calls slot `+8` with that same listener before publishing
`document+0x5838`. The listener methods in this executable do not call
`AskToStop` or `ProductionStop`. The controller implementation is in
`ViVirtualMachine.dll`, version `70.06.59.00`. Its constructor stores
the `IVMachineController` vtable at offset 0, and slot `+0x10` is the
shared subject `Detach`. That body unlinks the listener and returns;
it does not call `AskToStop` or `ProductionStop`. The builder DLL only
forwards the constructor. The ten pointers at `view+0x60b0` through
`view+0x60f8` are `CBrush` objects constructed by `mfc140.dll` ordinal
357. Destroy calls slot `+8` with edx 1. That scalar deleting destructor
calls `DeleteObject` and CRT `free`; it does not call `AskToStop` or
`ProductionStop`. The callback-retirement gate is not promoted.

### Optional target evidence under W7-QUAL-01

Do not extend unrelated MFC helper mapping to treat these counterexamples as
closed. Correct owner-state selection on the actual single-lane teardown path
would provide additional evidence, but collecting the following target traces is
optional under W7-QUAL-01. Their absence is accepted qualification risk, not a new
entry gate. Native execution still requires separate approval; an isolated Windows
7 Embedded environment is no longer a prerequisite.

1. Establish the loaded EXE/MFC paths, hashes, module bases, and Windows 7 Embedded
  x64 build. Interpret retained addresses as preferred-base addresses and relocate
  them using the recorded loaded bases.
2. Correlate the creating/owning UI thread, current dispatch thread, HWND, view,
  and `view+0xe8` document with the same panel lifetime at SKIP dispatch and
  `WM_NCDESTROY`. Do not infer identity from reused pointer or HWND values alone.
3. At detach entry `0x18028f560` and before field clear `0x18028f58f`, record
  the selected module wrapper/state, module `+0xf8` slot, selected thread state,
  map `+0x28`, and actual HWND-to-view entry. Establish that this is the owning
  map, that removal completed, and that no state switch or reentry breaks that
  relationship. Record initialization/failure paths rather than silently excluding
  them from the evidence.
4. Correlate successful unbinding with pending/active SKIP callbacks, document
  storage release, and next-panel pointer/handle reuse. Ordinary traces support
  reachability; they do not replace delayed-callback and failure-path qualification
  or native exception/unwind tests.

Without this native evidence, record owner-state selection and callback retirement
as unverified under W7-QUAL-01. Continue available offline analysis of the existing
lifecycle contracts. Any additional lifecycle design still requires separate
approval and must preserve ownership and prevent premature release/reuse.
Forcing state initialization, swallowing allocation failure, clearing fields,
or erasing manual skips is not an acceptable substitute. No such additional hook
or ownership redesign has been implemented. Saved binaries and OS-stubbed fixtures
do not promote native qualification to passed; the waiver permits proceeding
without that qualification, subject to the remaining implementation contracts.

### Remaining entry work

1. Complete static caller and asynchronous queue/lifetime graphs for the supported single lane.
2. Qualify the approved startup-only synchronous candidate: prove all affected
  admissions are covered, no work predates activation, and synchronous treatment
  has no outstanding descendants at cleanup. Complete conditional-mode,
  exception/unwind, and single-lane admission coverage. Any remaining asynchronous path still
  requires closed admission and stop-before-release containment; the earlier
  guard tests alone are insufficient.
3. Enumerate every vector writer/reallocator/destructor and its synchronization.
4. Trace CAO allocation, retirement, reset, pooling, and pointer reuse. For the
  resolved production-view SKIP receiver, establish array mutation locking,
  document/window teardown, and pending-message ordering before storage release.
  Resolve supervisor DoEvents dispatch/reentry, MFC view teardown, and the
  remaining publication path; connect publication/clearing to the view binding
  and worker index before claiming shared document identity. CCAPM clearing
  alone leaves the modeled view binding intact, and the inspected close helpers
  do not establish a fail-closed worker/callback barrier. `ProductionStop`
  can poll `CViThread::Stop` on document `+0x3868`, but document close does
  not call it, and its retry dispatches messages before the thread exits.
  The back-edge returns to the cycle head while `thread+0x32` is zero.
  `CheckAvailableMemory` `0x14069c770` can leave that head without
  `+0x382e` already being 1: its failure stores word `0x100` at
  `thread+0x31` because the selector at `0x1411697c4` is zero-filled and
  has no store. Close does not call that function. App slot `+0x58` does
  not write the other exit flag. `AskToStop` still sets document `+0x382e`. The only store through displacement `0x382e` writes 0 inside
  `ProductionStart`. The other two uses compare the byte with 1. The view
  compare's equal side tail-jumps MFC ordinal 4326 and does not call
  `ProductionStop`. Close does not contain that displacement. The cycle calls embedded slot `+8` at `0x1406a4685` only after `thread+0x32` is nonzero. The zero side returns to the cycle head. That exit does not call `ProductionStop`. Close, destruction, view `WM_DESTROY`, the close poster, and the `0x52c` handler do not call that function or the other five functions that call the same slot, and neither do their direct callees. `WM_CLOSE` reaches `OnCloseDocument` through MFC ordinal 2660
  without setting that byte or joining `+0x3868`. Before the close helper,
  `OnCloseDocument` calls `0x1406928d0` and `0x14063b430` on `document+0x3850`.
  That pointer is `[[AfxGetModuleState()+8]+0x40]`. The wait there is on
  the `CreateSemaphoreA` handle at `[object+0x5870]`, not on `document+0x3868`.
  The same function releases that semaphore before returning. It waits on the
  semaphore at `app+0x57c8` and calls `DoEvents` only when the incremented
  dword at `+0x5868` is not 1. Neither function calls `ProductionStop`.
  `ProductionStop` also joins the communication thread at `document+0x3860` after `+0x3868`. That thread waits on its own three handles and can `ReleaseSemaphore` `[document+0x3890]`. It does not call `ProductionStop` or `AskToStop`. Close does not mention `+0x3860`. The production view map has no `WM_CLOSE` entry. Its `WM_SIZE` handler is MFC ordinal 11222, which calls `0x18028f370` and stays in `mfc140.dll`. Its `WM_ERASEBKGND` handler does not call `ProductionStop`. Message `0x87d0` loads the document from `view+0xe8` and does not call `ProductionStop`; its `edx` 7 and 8 arms call `InvalidateRect`. Its virtual calls are `ccSemaphore` lock and unlock, and a `CDPoint` copy. View message `0x113` timer id 1 also loads the document from `view+0xe8` and locks that semaphore. `OnInitialUpdate` at view slot `+0x328` arms timer ids 1 and 8 before testing `document+0x382d`. The not-equal side checks `view+0xe8` and does not call `ProductionStop`. `WM_DESTROY` kills timer id 5. Close and the document and view destructors do not call `KillTimer`. Slot `+0x10`
  at `document+0x2548` nulls `+0x3868` and stops only `+0x3860`. The view
  command handler calls slot `+8`. `CDocCompose` constructor `0x1405cb880` stores vtable `0x140e76370` at `+0x2548` and does not call `AskToStop`. `CCAPM` secondary slot `+0xb0` reaches `[r13+0x2548]` slot `+8` only when `ebx` is 4, and close does not call that slot. The only reference to `0x140682ff0` is a callable enqueued by `HandlerProduction`; the document destructor's `Kill` does not call it because the manager low bit is set. When document byte `+0x382d` is 1, `Handler` calls `0x1406a1da0`, which stores 1 at `thread+0x32`, calls `AskToStop`, and returns 0. Otherwise it calls `HandlerProduction`. Both arms then call MFC ordinal 2175. `HandlerProduction` does not read `+0x382d`. `ProductionStop` can set that byte to 1 and still calls `ProductionStart`, which still starts the producer. Document slot `+0x100` copies `CAVisionApp+0x198` into the byte, and close does not call that slot. `HandlerProduction` can join its worker pool through `0x14069c890` when document byte `+0x5830` is nonzero. The only store of 1 is `ReloadDoc`, and close does not call `ReloadDoc` or that checker. The `CViThread::Stop` import has nine sites. Only `ProductionStop` contains displacement `0x3868`. `Stop` waits on `[[this+8]+0x58]` after signaling `[this+0x18]`. `ProductionStart` copies that event to `document+0x61d8`, and only `ProductionStop` waits on the copy. Close does not use that displacement. `CProcessingGreyZoneThread` slot `+0` frees the worker without writing `+0x28`. Close does not call that destructor, so the copied document pointer remains. The worker waits on `[worker+0xa0]` and its stop event. Only `0x14069fb80`, reached from `HandlerProduction`, signals `+0xa0`. Close does not call that chain and does not wait for a worker already inside slot `+0x18`. The constructor creates `[worker+0xa0]` nonsignaled and `[worker+0xa8]` signaled, and resize stores the availability handles at `pool+0x20`. Selector `0x1406a1660` uses the copied vector length as the count and `[pool+0x3c]` as the timeout. The constructor stores `[rsp+0x4c] * 0x3e8` at `thread+0xf04`. Timeout result `0x102` skips the worker, so an in-flight callback is not joined there. The direct callers of the array reset `0x140541050` are the SKIP poster, `HandlerProduction`, `ReloadDoc`, and two other functions; close does not call it. Those two are document slot `+0x108` (`0x14068dc20`), which calls `PrepareExecData` without calling `ProductionStop`, and CCAPM secondary slot `+0x80`, whose only entry is the adjustor `0x14075ad60`. Close bodies contain neither slot call. SKIP refresh `0x1406adaf0` returns the document array at `+0x23e0` and reads an element when the count is positive, without testing the document pointer or displacements `0x382d`, `0x382e`, or `0x5838`. The other refresh caller, `0x1406b3760`, is reached only through `0x1406971b0`, and close does not call either function. The poster call in `0x1406a5010` requires `[document+0x3978] == 1`, and close does not write that dword. The poster calls CCAPM secondary slot `+0x80`; a 1 return, which is set only after that slot's reset, posts through `[document+0x5838]`, and close does not call the poster. Both posts are `PostMessageA`, and the poster returns without a wait. The grey-zone post at `0x140736feb` requires document byte `+0x3835` to be 1, that byte is stored only by the constructor, and the post returns through stack destructors without a wait. Its caller chain is `0x140735f10` to `0x1407354b0` to `0x1407368d0`, reached from worker slot `+0x18` and from `0x14069fcd0`; those functions do not read `+0x3868`, and close does not call them. Three direct-call levels from the close roots contain no `CViThread::Stop` import; their only `WaitForSingleObject` functions are the supervisor waits and the `0x52c` arms for wParam 7 and 8, and none of those bodies contains `+0x3868`. Without the `0x52c` handler, the same three levels are 43 functions and include neither `ProductionStop` nor a call through displacement `0x28`. Their remaining virtual helpers walk a `0x370`-stride vector at `document+0x5888`, delete nullable members, or release a refcount, and none contains `+0x3868`. The list at `CProdCarte+8` holds `boost::detail::sp_counted_impl_p<CAnomalieProd>`. Its dispose calls `CAnomalieProd` slot `+8` with edx 1, which runs the StructSupport destructor and frees the element through MFC ordinal 1487. The control block's other slot frees its own `0x18` bytes through that ordinal. `CButtonST+0x158` is null in the constructor; `0x1407420c0` and `0x140742230` store a `CBitmap` there. Its slot `+8` calls MFC ordinal 3748, which calls `DeleteObject` when the handle is nonzero, and then frees the `0x10`-byte object. The pointer vector at `document+0x2478` stores `CMacro` objects. Slot `+8` calls `VitDataCAD.dll!CMacro::~CMacro` and then frees the object. Three direct-call levels from that destructor do not join the producer. The worker then signals `[worker+0xb8]`, which no wait in the executable loads. `CCAPM` secondary slot `+0x1c8` is `0x14075efd0`. It calls `AskToStop` only when a prior slot `+8` returns greater than 6, it has no direct caller, and the close functions do not contain displacement `0x1c8`. Of the 83 document-vtable slots, only `+0x28` calls `ProductionStop`. None of the 113 production-view vtable slots calls it. `ProductionStop` itself is only called
  from document vtable slot `+0x28`, and only when `r8` is `0x004eb1cf`.
  Close, destruction, and the `0x52c` handler do not call that slot. The close helper posts
  view message `0x52c` with wParam 6; that switch arm does not stop the
  producer, and the MFC close jump runs before the posted handler. The
  wParam 2 arm is the `WM_COMMAND` `0xb1cf` button on the view's
  `PROD_VIEW_COMMAND` child. Close does not create that button or load
  `0xb1cf`. The direct-call closure of close and destruction does not
  reach `AskToStop`; the destructor writes that vtable at `+0x2548`
  without calling slot `+8`. `WM_DESTROY` does call `CCAPM` slot `+0x198`
  (`0x14075d6b0`) on `CAVisionApp+0x1b0`. Its ordinary tail updates a
  locked pointer vector in `0x1406109f0` and does not call `AskToStop`
  or `ProductionStop`. Destroy's code `0xb` skips that update when the
  indexed entry exists and `[entry+0x3928] == 4`. Destroy then calls
  `IVMachineController` slot `+0x10` with the listener at `view+0x160`.
  The listener methods in this executable do not stop the producer.
  `CVMachineController` slot `+0x10` in `ViVirtualMachine.dll` is a
  listener detach and does not stop the producer either. The ten
  `CBrush` objects at `view+0x60b0` through `view+0x60f8` are released
  by their deleting destructor, which calls `DeleteObject` and `free`.
  `CProductionDoc` has no pool: `CreateObject` is `malloc(0x61f8)` plus a
  constructor that builds an empty `CUIntArray` at `+0x23e0`, and the
  deleting destructor `free`s the block after releasing that buffer.
  Before the release it stores null at `CCAPM` index `document+0x3924`,
  which `ProductionStart` has copied to thread `+0xec0`. `ProductionStart`
  returns without stopping or replacing that thread when `+0x3868` is already
  nonzero, so the other two callers cannot retire it either.   The cycle reloads
  that slot before testing `+0x382e`. None of the 99 accessor calls tests
  the pointer. The end-of-iteration store runs only after that compare
  succeeds, so a null slot faults before that store. `CheckAvailableMemory`
  also dereferences the accessor result before its failure arm can set
  `thread+0x32`. The not-equal side calls
  `0x1406970f0`, which dereferences the document and does not write the
  stop byte. The next iteration does not reuse a document pointer from the
  previous one: the pointer it reloads was saved before the cycle from the
  app object at `+0x1b0`.   Two `rbx` windows hold a document across one later
  accessor call and both end before the back-edge. No accessor result is
  stored to memory. The view deleting destructor does not clear
  `document+0x5838` before ordinal 1487 frees the view, so the reloaded
  binding still names that block while the document remains published. The
  document destructor's direct-call closure then frees the array at
  `+0x23e0` without importing `user32` and without calling the message pump.
  Before that free, nonzero `document+0x19e8` calls slot `+0x190` and drops
  the returned refcount. That slot is the controller forward to
  `[controller+0x870]` slot `+0x220`, which forwards to `IAcquisitionController`
  slot `+0x220`. That interface slot is `_purecall` in the supplied DLL. The same
  destructor then destroys the array at `document+0x5878` through slot `+8`
  with edx 3 and stores null. Its inner `0x370` objects are `CAnomalieProd`.
  Their destructor releases point, string, buffer, and image members and
  does not import `user32` or the executable. `CAsynchCommandExecution::Kill`
  on `document+0x6128` waits on that object's own thread handle, not on
  `document+0x3868`. The destructor closes the event at `+0x3878` and the
  semaphore at `+0x3890`, and its bytes do not mention `+0x3868`. The base destructor does not call
  `ProductionStop`. The pool worker constructor stores zero at `+0x28`.
  `0x1406a6b95` calls `0x1406a15d0`, and `0x1406a4980` copies that result
  onto each worker at `thread+0xec8`. Treat reads that saved field.
  `OnCloseDocument`, the document destructor, view `WM_DESTROY`, the close
  poster, and the `0x52c` handler do not call `0x1406a4980`. After
  `ProductionStop` joins `document+0x3868`, it calls producer slot `+0`
  with `edx` 1 while the slot is still nonzero, then stores zero. That
  destructor calls the pool destructor at `thread+0xec8`, and `0x140655980`
  calls each worker slot `+0` with `edx` 1. That slot calls `0x14069a110`.
  Those close and destroy functions do not call `ProductionStop` or
  `0x140655980`.
  It next destroys the embedded `CDataCao` at `document+0x180` and tail-jumps
  to MFC ordinal 1104. `VitDataCAD.dll!CDataCao::~CDataCao` releases its members. Three direct-call levels from it do not call `CViThread::Stop` or `WaitForSingleObject` and do not mention `+0x3868`. `DeleteCadTab` calls slot `+8` with edx 1 on each `CCAD_Base` pointer at `+0x1018`, and the destructor clears the embedded `CMacro` array at `+0xd78` with edx 0. Those destructors do not join the producer.
  Ordinal 1104 then calls `0x18021e1a0`, which stores zero at `view+0xe8` for each view still listed. That clear is after the `CUIntArray` release and does not write `document+0x5838`. The following call, `0x180221190`, deletes `[node+0x10]` for the list at `document+0xe0`. The constructor stores zero there, no supplied binary imports ordinal 2525, and the walk does not mention `+0x3868`. A nonzero `document+0x50` is the template. Its slot `+0xd0` is `0x180228e70`, which clears that field and unlinks the document. It does not mention `+0x3868`. Slot `+0x10` on `document+0xb8`, `+0x178`, and `+0xd0` is called with only that pointer. The constructor stores zero at all three, and the first two are cleared again after the call. The 83 document vtable slots do not store those qwords. The constructor call at `0x14067e00d` builds `document+0x5888` and zeros that object's own `+0x178`. Imported MFC ordinals 981 and 1838 store `+0xb8` on the application object, whose vtable is `0x140e39770`.
5. Native target traces for duplicate delivery, delayed workers/callbacks, vector
  identity, CAPM entry, retirement, and immediate reuse are optional under
  W7-QUAL-01. Retain available offline cases and record native gaps as unverified.
6. Document and enforce a supported workload maximum or widen threshold arithmetic.

Only after the remaining non-waived implementation contracts are satisfied should
`tools/patch_f1_missing_n_rev6.py` be created from rev5 and the assembly/state/ownership
changes begin. Do not block that decision solely on the unavailable target
qualification covered by W7-QUAL-01.