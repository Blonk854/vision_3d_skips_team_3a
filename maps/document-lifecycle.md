# Production Document Lifecycle

Recorded: 2026-09-22. Vision3D 70.06.59.00, AMD64, image base `0x140000000`.
Stock EXE SHA-256:
`ccca11b2f05084b484fa5556c67f8874065dbc0b6265177d2517f81265af00f4`.
Saved Ghidra analysis and stock-byte-checked instructions only. No native target
execution or modified executable. Single-lane scope; dual-lane unsupported.

Target platform (user reported 2026-09-22): Windows 7 Embedded, 64-bit.
Offline tests run on the development host, not that station. Host-side unwind
results do not qualify Windows 7 exception handling or runtime compatibility.

## Document Bindings

| Binding | Verified behavior | Evidence |
| --- | --- | --- |
| CCAPM secondary interface, application `+0x1b0` | Getter `0x14075d010`, setter `0x14075d040`; indexed pointer slots, no local lifetime acquisition | [Getter](rev2a_skip_capm_document_accessor.json), [setter](rev2a_skip_capm_document_neighbor.json) |
| `SetProductionVMC`, `0x140697200` | Mode zero publishes document at index zero, clears index one | [Publication](rev2a_skip_capm_document_publication.json) |
| `OnNewDocument`, `0x14068dab0` | Publishes with mode zero before base new-document call | [Wrappers](rev2a_skip_document_lifecycle_wrappers.json) |
| Production view `+0xe8` | Independent document pointer used by SKIP refresh | [Refresh](rev2a_skip_ui_refresh.json) |
| Document `+0x23e0` | Live CUIntArray; data pointer `+0x23e8`, count `+0x23f0` | [Storage](rev2a_skip_ui_list_storage.json) |

Clearing CCAPM does not clear the independent view pointer. The offline callback
fixture executes the stock getter/setter and still reads through that view.
This is a counterexample to treating CCAPM clearing alone as callback retirement,
not an observed station race.

## Reset and Reuse Boundaries

The [reset callers](rev2a_skip_reset_callers.json) do not establish an
unconditional per-cycle reset boundary, even for lane zero:

- `PrepareExecData` (`0x14068f0f0`), decision `0x14068f74e` through
	`0x14068f7dc`: an empty execution vector (`+0x2448/+0x2450`, stride `0x28`)
	bypasses reset. For a nonempty vector, application byte `+0x18d == 1` and
	positive skip count `document+0x23f0` select `MajTestVectorForSkip` at
	`0x14068f7ca`; otherwise `0x14068f7d7` calls `SkipList_Reset`.
- The [reapply body](rev2a_skip_prepare_reapply.json), `0x14052e910`, queries
	`IsSkippedSubPanel` at `0x14052e9d3` and `0x14052eafc`, then calls CAD virtual
	`+0xd8` with the membership result. It also updates execution-vector flags
	and counts inspectable entries. This is not a local skip-list reset; unknown
	virtual/helper effects are not treated as proved absent.
- `ReloadDoc` (`0x140692af0`) snapshots the live skip list into a local
	CUIntArray, later resets at `0x1406937d7`, then restores saved entries with
	`SetAtGrow` at `0x140693811`. Reaching that reset does not imply the list
	remains empty or that every physical panel passes through ReloadDoc.
- `HandlerProduction` (`0x1406a20d0`) checks the same lane-zero application byte
	at `0x1406a2d68`. `0x1406a2d7a` bypasses the reset call at `0x1406a2d87` for
	every nonzero value. The join at `0x1406a2d8c` continues cycle initialization.

Two bounded stock-instruction tests in
[the verifier](../tools/verify_worker_admission.py) cover twelve preparation
decisions and four cycle-start decisions. External calls are stubbed; fixtures
prove branch selection, not whole-function success, station configuration,
worker quiescence, or absence of late callbacks. Non-boolean values are boundary
fixtures, not evidence that production assigns those values.

The proposed hook at `0x140541050` alone is therefore not yet proved to reset
patch counters before every supported reuse. The writer trace below shows that
single-lane operation alone does not guarantee application `+0x18d == 0`.
Prior-work quiescence at the cycle boundary also remains unproved. Without an
explicitly approved and verified restriction on manual-skip preservation, a
separate patch-state reset boundary needs scoped design approval; do not clear
the stock operator skip list unconditionally or introduce generation counters
without approval. The reset/reuse gate remains open.

### Manual-Skip Policy Writers

The [explicit-store scan](rev2a_skip_policy_stores.json) covers 2,639,324 saved
Listing instructions and finds ten `MOV byte ptr [register + 0x18d]` sites.
This is discovery evidence, not a complete alias analysis: wider stores, field
addresses passed to helpers, other write opcodes, and unsaved analysis are excluded.

- [RegistryRead](rev2a_skip_policy_writers.json), `0x1404ddcd0`, reads
	`Production.ManualSkipLane1`. On a successful key read, `0x1404de090` compares
	the DWORD with zero, `0x1404de094` executes `SETNZ AL`, and `0x1404de097`
	stores AL to application `+0x18d`. Lane 2 uses the separate byte `+0x18e`.
	The application initialization caller `0x1404d2820` calls this reader at
	`0x1404d2a1f`; see the [single-lane extraction](rev2a_skip_policy_single_lane.json).
- `CAVisionApp::OnProductionStartStandard` (`0x1404dba70`, identity from its
	log string) creates the dialog at `0x1405c4320`. Its constructor initializes
	dialog `+0xa40` to zero. On a non-cancel modal return, instructions
	`0x1404dbb4f/0x1404dbb56` copy that byte to application `+0x18d` before the
	mode-zero CAPM call and `ProductionStartStandard` (`0x1404dd140`). This is
	distinct from the excluded dual-side command at `0x1404dabd0`.
- The [dialog handler](rev2a_skip_policy_dialog_handler.json), `0x1405c4ae0`,
	obtains `CAVisionApp` through the same module-state/dynamic-cast sequence,
	calls the application permission check with argument 2, and, if allowed,
	stores one at dialog `+0xa40` (`0x1405c4b23`) before tail-calling
	`CExtResizableDialog::OnOK`. Raw message-map entry `0x140e72630` is
	`(WM_COMMAND, 0, 0x820, 0x820, 0x3a, 0x1405c4ae0)`.
- `CAVisionApp::LaunchSingleProdRemoteOrder` (`0x1404d4510`) explicitly clears
	application `+0x18d` at `0x1404d4564` before calling the same standard-start
	function. That is a local property of this entry path, not a guarantee for
	all single-lane starts or later writes. The other retained clears include
	preparation cancellation at `0x14068f541`.

The verifier executes the three stock registry conversion instructions for
DWORD inputs 0, 1, 2, and `0xffffffff`: results are 0, 1, 1, and 1. It also
pins the writer bodies and command-map bytes against the stock EXE. Together
with the existing cycle-decision fixture, this establishes that a permitted
nonzero policy value selects reset bypass. It does not simulate a complete
modal interaction, registry API, permission implementation, production start,
or scheduler, and does not establish the actual station setting. Single-lane
support must not silently be redefined as remote-start-only or manual-skip-disabled.

## Close and Destruction

| Entry | Verified local sequence | Evidence |
| --- | --- | --- |
| `0x14068ee00`, document vtable `+0x110` | Posts WM_COMMAND `0xb24c`, returns one; override name unresolved | [Overrides](rev2a_skip_document_close_overrides.json) |
| `0x1406b1840` | Handler for that command; application/document conditions precede further calls | [Command handler](rev2a_skip_document_posted_command.json) |
| `OnCloseDocument`, `0x14068d9d0`, vtable `+0x118` | RegistrySave, supervisor helper, application notification, tail-call MFC base close | [Overrides](rev2a_skip_document_close_overrides.json) |
| `RegistrySave`, `0x1406928d0` | Reads live SKIP count and entries before supervisor helper | [Close helpers](rev2a_skip_document_close_helpers.json) |
| `0x14063b430` | Conditional semaphore/counter path and supervisor disconnect; wait result unchecked | [Close helpers](rev2a_skip_document_close_helpers.json) |
| `0x14064b880` | Unchecked wait, optional wait box, busy-loop Sleep/DoEvents, disconnect, release | [Nested helpers](rev2a_skip_document_close_nested.json) |
| `0x1404e03f0` | Posts message `0x52c`, wParam 6, to document views; no delivery acknowledgement | [Close helpers](rev2a_skip_document_close_helpers.json) |
| Deleting wrapper `0x1406807e0` | Calls destructor before testing deletion flags; no local pre-destructor barrier | [Wrappers](rev2a_skip_document_lifecycle_wrappers.json) |
| Destructor `0x14067fc20` | DeleteVector, DeleteCadTab, async-command Kill, handle closes, then CCAPM clear | [Destruction](rev2a_skip_capm_document_publication.json) |

The document vtable starts at `0x140ea3868`: constructor instructions
`0x14067decc` / `0x14067ded3` load that address and store it to the receiver.
The earlier `0x140ea3870` anchor was eight bytes late, at the deleting-wrapper
entry. Correct slots are deleting wrapper `+0x8`, new document `+0x100`, open
document `+0x108`, unresolved posted-command override `+0x110`, and close
`+0x118`. The verifier now pins the constructor write as well as these pointers.
Slot identity alone must not infer another receiver's type or an override name.

The [posted UI-command descendants](rev2a_skip_close_command_descendants.json)
do not establish a production-stop or document-close barrier. Application check
`0x1404e0b60` reads production/password configuration and may show
`CPassword_Edit::DoModal`. On the permitted path, `0x140697ab0` reparents a
window and calls a document-embedded receiver's virtual slot `+0x2e0`;
`0x1406abfe0` calls `0x140675f90` and then `RedrawWindow` with flags `0x105`.

### Posted Command Bindings

The [four-instruction helper](rev2a_skip_posted_ui_helper.json) at `0x140675f90`
loads HWND from receiver `+0x40` and tail-calls
`InvalidateRect(HWND, NULL, TRUE)` through IAT `0x140d5bc90`. Its caller passes
`view+0x870`, so the HWND is at `view+0x8b0`. There is no local worker stop,
wait, storage mutation, or lifetime barrier. This does not establish the absence
of reentry in the subsequent redraw or the surrounding command.

A development-host user32 probe registers the exact SKIP message
`{FEA8416F-2D59-478F-BEFF-5D96AFD6A551}`, posts it to a hidden test window,
and confirms it is queued with `PeekMessage(PM_NOREMOVE)`. After
`DestroyWindow`, a filtered `PeekMessage(PM_REMOVE)` finds no such message,
`IsWindow` is false, and a new `PostMessage` to the stale HWND fails. The test
does not load Vision3D and does not qualify Windows 7. It excludes
post-destruction dispatch on this host; it does not exclude a producer racing
before destruction, a stale producer-side view/document dereference, or
synchronous reentry while the receiver still exists.

Both producers load that HWND from `[CAO+0x5838]+0x40` and call `PostMessageA`
with wParam and lParam zero. Each post first resolves the CAO through
`0x1406a15d0`, a fresh module-state lookup, so the read targets the current
document's never-cleared `+0x5838` field rather than a cached view pointer. If
that lookup returns a document whose view was already freed, the read is a use
of freed storage. The sites are `0x1406a103b`, `0x1406a1075`, and
`0x140736feb`, all through IAT `0x140d5bc00`. The sequences do not test the
view pointer, the HWND, or the return value. The document constructor clears
`r14` at `0x14067df59` and stores it at `+0x5838` (`0x14067f60e`). No
instruction in that span writes `r14`, and no branch enters the span after the
clear or jumps past the store. `r14` is nonvolatile, so the calls in that
span return it unchanged and the store writes zero. `OnInitialUpdate`
`0x1406af770`, view slot `+0x328`, copies `this` to `r15` and stores that view
at `[view+0xe8]+0x5838`. The EXE `.text` section has two writes of displacement
`0x5838`: that constructor store and this publisher. Refresh `0x1406adaf0` has direct calls from the
message handler at `0x1406b0704` and from `0x1406b3b3f`.

Production `OnCloseDocument` `0x14068d9d0` tail-jumps MFC ordinal 8850. While
`document+0x70` is nonzero, that function takes the view at
`[[document+0x60]+0x10]`, calls `GetParentFrame`, and calls frame slot `+0xd0`
through the CFG stub `jmp rax` at `0x1802bf060`. `CProductionChild` slot
`+0xd0` is ordinal 3803, the `WM_MDIDESTROY` send. An empty list branches to
`0x18021f927`, skipping that loop. After the loop, nonzero `document+0x120`
calls document slot `+0x8`. That deleting wrapper calls `0x14067fc20`, which
tail-jumps `0x14051fbf0`. The base destructor releases `+0x2448` through
`0x14051ff90` and then `+0x23e0` through ordinal 1439. On this close path the
listed frames are destroyed before the skip arrays are released. With the host
probe, a SKIP message already queued to one of those HWNDs is retired before
that release. The production view message map has 33 entries and no
`WM_CREATE`. Its base is ordinal 7215, the `CFormView` map. That map's
`WM_CREATE` handler copies `view+0x138` into `lpCreateParams` and jumps to
`CView::OnCreate` at `0x18027c010`. After `CWnd::OnCreate` returns a value
other than -1, a create context whose document pointer is non-null calls
`AddView` `0x18021faa0`. `AddView` inserts on the list at `document+0x58`.
The node allocator increments `[list+0x18]`, which is `document+0x70`, and
the node then stores the view. `AddView` stores the document at `view+0xe8`
and calls slot `+0xf0`. The production slot is ordinal 8734, which selects
slot `+0x1e0` when the count is nonzero. `CFormView::Create` stores its
seventh argument at `+0x138` before the call that reaches
`CreateDialogIndirectParamA`, and installs a `WH_CBT` hook first. The installer
stores the view at the same thread state `+0x28` before that dialog call. On
`HCBT_CREATEWND`, when that field is nonzero, the hook pushes `view+0x38`,
stores the HWND at `view+0x40`, inserts the view in the permanent handle map,
and calls `SetWindowLongPtrA` with `GWLP_WNDPROC` and module-state `+0x70`.
The production view constructor calls `CFormView`'s constructor, and that
chain reaches `0x1801e1120`, which stores `AfxGetModuleState()` at `+0x38`.
A null thread module pointer selects the process state. Its constructor stores
`0x180138040` at `+0x70`, and the DLL static constructor stores `0x1802b4860`
there. Both procedures call `AfxWndProc` `0x18028f5f0`. After the permanent
map returns an object whose `+0x40` equals the HWND, `AfxCallWndProc` calls
slot `+0x238` with message 1. The production slot is `CWnd::WindowProc`, and
its `+0x240` slot is `CWnd::OnWndMsg`. Message 1 reaches `GetMessageMap` at
slot `+0x60` and follows the base map. The `CFormView` entry has signature
`0xd` and calls `0x18027f230`. A later `RemoveView`, or a create whose context
has no document, can still leave the list empty. A post can still arrive while
the HWND exists, and the never-cleared `+0x5838` field can still be read after
detach. The callback-retirement gate stays blocked.

`WM_NCDESTROY` clears `view+0x40` in the detach helper before it calls
deleting slot `+0x8`. A post that reads the field in that interval passes a
null HWND, and `PostMessageA` then posts a thread message. A read after the
object is deleted is a use of freed storage.
The handler pointer `0x1406b0700` and its id pointer `0x1411982c8` each occur
once in the EXE, in the production view map. The application message map at
`0x140e3a130` has 55 entries and no `0xC000` entry; its base getter is MFC
ordinal 7363. Application slot `+0xc0` is ordinal 11849, which jumps to
`0x180278440`. For a null `MSG.hwnd` that function calls `0x180278f00`, and
that walker reads the thread's message map at slot `+0x60`. The parent walk
`0x180293870` returns zero when `MSG.hwnd` is zero. MDI-child pretranslate
returns zero for a message outside `0x100`..`0x109`, because
`0x1802903f0` returns zero. On this development host, `DispatchMessageA` does
not call a window procedure for that thread message, and a peek filtered to a
live window does not see it. When `0x1404d10d0` returns zero, `CMainFrame`
calls `CExtMenuControlBar` slot `+0xa90` on the embedded object at
`frame+0xcd0`. That slot is `0x180270ae0`. A registered id misses every
return-1 comparison (`0x113`, `0x100`..`0x109`, `0x111`, and `0x222`..`0x228`).
The other jumps that keep a nonzero return sit in the span entered only for
message `0x101`, or in the `0x7b` block. The handler then returns the `r15`
value it cleared. Its `SendMessageA` sites pass `0x157` or `WM_CANCELMODE`.
A zero return falls through to MFC ordinal 11812. That function reads
`frame+0x120` and calls slot `+0xb8` only when the qword is nonzero.
`CMainFrame` construction calls ordinal 549, which calls `CFrameWnd`'s
constructor, and that constructor stores zero at `+0x120`. The `CFrameWnd`,
`CMDIFrameWnd`, and `CMainFrame` vtable bodies contain no qword store of that
displacement. Three levels of direct calls from those vtables, and four levels
from the frame constructors, reach no other function with such a store. The
callback-retirement gate stays blocked: a post can still arrive while the HWND
exists, a view list emptied by `RemoveView` can still delete the document, and
a read of `+0x5838` after the view object is freed uses freed storage.

The ExecuteSkip posts are reached only from the production thread.
`CProductionThread` vtable `0x140ea8a48` binds slot `+8` to `Handler`
`0x1406a1c80` and slot `+0x10` to `BaseTools.dll!CViThread::Start`. The
supplied BaseTools thread procedure is `mov rax,[rcx]; jmp [rax+8]`, so Start
runs Handler. Handler calls `HandlerProduction` unless document byte `+0x382d`
is 1, then calls MFC ordinal 2175, whose tail is `_endthreadex`.
`HandlerProduction` is that function's only direct caller.
`MakeFirstPassInspection` is the only direct caller of `ExecuteSkip`, and
`HandlerProduction` is its only direct caller. `ProductionStart`
`0x140691c80` stores the new thread at document `+0x3868` and calls slot
`+0x10`.

`ProductionStop` `0x1406920f0` is the only direct caller of `CViThread::Stop`
on that field. It passes timeout zero. While Stop returns anything other than
1 it calls `0x1405e8af0(0x1f4)`, which peeks, translates, and dispatches queued
messages, then sleeps 10 milliseconds, repeating for the argument divided by
10. Neither `OnCloseDocument` nor the document destructor calls
`ProductionStop`, `BP_ProductionStop`, or `0x140680c00`. The notification
handler `0x14068da40` is the only direct caller of `ProductionStop`, and it
requires notification code `0xb1cf`. Document close therefore does not join
this producer before it destroys the view. A failed Stop attempt can also
dispatch a SKIP message while Handler is still running. No callback-retirement
gate is promoted.

`AskToStop` is slot `+8` of the vtable stored at `document+0x2548`
(`0x140ea3b58`), not a primary-document slot. Called on that subobject, it
sets byte `+0x12e6`. That is document byte `+0x382e`. It then posts
`WM_NOTIFY` (`0x4e`) with code `0xb1cf` and returns. The only other memory operand using displacement `0x12e6` is
`StartProductionWithThread` clearing it.
`ProductionStart` clears the same document byte through displacement `0x382e`.
Four initialization stores also cover that byte, and each source register is
still zero: dword stores at `0x14065bd0b`, `0x14065bee2`, and `0x14065f368`,
and the constructor word store at `0x14067e17b`.
`HandlerProduction` compares `document+0x382e` with 1, sets
`CProductionThread+0x32`, and returns to the cycle head while that thread byte
is zero. The child frame's recorded base map inherits `WM_CLOSE` handler
`0x1802a2aa0`. That handler calls document slot `+0x1b8`, MFC ordinal 2660,
and then slot `+0x118`, `OnCloseDocument`. Ordinal 2660 tests a view dword at
`+0xec` or calls slot `+0x1c0`. It does not read `+0x382e` or `+0x3868`.
`OnCloseDocument` does not contain those displacements. Close can destroy the
view while `HandlerProduction` is still in the cycle. The callback-retirement
gate is not promoted.

The [document constructor](rev2a_skip_document_sheet_construction.json) at
`0x14067dea0` passes `document+0x3990` to `0x1406c3a30` at `0x14067dfef`.
That [sheet constructor](rev2a_skip_embedded_window_binding.json) installs
vtable `0x140eb0360` at `0x1406c3a5d`. Raw RTTI locator `0x140f14428`, referenced
at `0x140eb0358`, identifies `.?AVSkipProductionElmt_Sheet@@` with offset zero.
The document destructor calls the [sheet destructor](rev2a_skip_embedded_window_destructor.json)
at `0x1406c3bf0` on the same embedded offset; this corroborates the constructor
binding rather than substituting for it.

Raw vtable slot `0x140eb0640` (`+0x2e0`) points to
[thunk `0x14077f754`](rev2a_skip_embedded_window_virtual.json), labeled
`CPropertySheet::DoModal` in saved analysis. Its sole jump uses IAT
`0x140d5ec88`, independently verified as `mfc140.dll` ordinal 3959. The verifier
pins constructor arguments, vtable installation, RTTI, slot pointer, thunk
displacement, import identity, and every retained instruction against stock.
This resolves the static modal-sheet target, not its runtime dispatch, exception,
or teardown behavior. The station MFC static analysis below continues this binding.

## Reentrancy Boundary

Inside `0x14064b880`, flags `this+0x14 & 0x0c` control a loop containing
`DYTOOLS0!DoEvents` at `0x14064b8fb`. The preceding wait at `0x14064b8a7`
does not gate the loop on success. Entry from document close is conditional.

The [offline verifier](../tools/verify_worker_admission.py) executes eight
success/WAIT_FAILED, busy/idle, and visible/hidden wait-box combinations. Busy
fixtures reach a stubbed pump under both wait results; disconnect/release follow.
External calls are stubs. Actual message filtering, dispatch, exception behavior,
and production-thread ordering are not established by this test.

### Actual DoEvents Loop

The EXE IAT slot `0x140d53fc0` imports `DyTools0.dll! ?DoEvents@@YAXXZ`.
The [stock-verified DLL body](rev2a_skip_doevents.json) is the free-function
export at `0x1800772b0`, ordinal 1468, not either similarly named member export.
DLL identity: AMD64, base `0x180000000`, 2,742,784 bytes, SHA-256
`f5421b5509236d6a5ba7b20c6e764f0af5e0be131bf2b08e2bbe774ac805767e`.

The body peeks with null HWND, message range zero/zero, and PM_NOREMOVE. When a
message exists it obtains `AfxGetThread()` and calls that receiver's virtual
slot `+0xc8`. It repeats until the queue is empty, the thread is null, or the
virtual call returns false. There is no local SKIP-ID/HWND exclusion or loop cap.

The verifier checks the EXE import/DLL export bridge and executes this actual
DLL body under five bounded fixtures: empty queue, null thread, false virtual
return, one message, and two messages. Peek/thread/pump helpers remain stubs;
the fixture message IDs are synthetic, not runtime registration results.
Checks cover zero filters, call sequence, stack balance, and nonvolatile registers.

For the application receiver specifically, the constructor installs vtable
`0x140e39770`; slot `+0xc8` points to thunk `0x14077f982`, IAT `0x140d5fd20`,
importing `mfc140.dll` ordinal 11881. Base `CDocument::OnCloseDocument` thunk
`0x14077fe26`, IAT `0x140d5f5f8`, imports ordinal 8850. The verifier retains
these exact stock bindings, but does not prove `AfxGetThread()` returns that
application object on every reachable path. The earlier runtime acquisition
blocker is superseded by the station-supplied intake below; the following
static analysis resolves those ordinal bodies without establishing live scheduling.

### Station MFC Static Analysis

The pinned station MFC was imported into the separate `MFC140_STATION` project,
leaving `V3D_SKIP` and its locks untouched. The
[configuration script](../tools/ghidra_scripts/ConfigureStationMfcAnalysis.java)
checks SHA-256, language/compiler, and image base, disables PDB analyzers,
Decompiler Parameter ID, and Function ID, and logs options and memory blocks.
[Analysis](rev2a_mfc140_analysis.log) succeeded and saved in 151 seconds under a
600-second limit with two CPUs. No native target or DLL code was executed.
The [importer](rev2a_mfc140_import.log) did consult host dependency files/export
caches and warned that cached exports might not match. It saved zero additional
programs. Inferred names/types from that metadata are not Windows 7 dependency
evidence; the conclusions below use stock bytes and EXE/ordinal bindings.

The [entrypoints](rev2a_mfc140_entrypoints.json),
[control paths](rev2a_mfc140_control_paths.json),
[modal pump](rev2a_mfc140_modal_pump.json), and
[bound virtuals](rev2a_mfc140_bound_virtuals.json) retain 15 functions, with every
instruction verified against the supplied file. Both document hooks at ordinals
3727 and 11723 share `0x180002850`, a `RET 0` body; its saved guard-related name
must not be mistaken for the semantic identity of every folded export.

**Message pump.** Ordinal 11881 jumps from `0x180279280` to `0x180278320`.
At `0x180278341`, it calls `GetMessageA(message, NULL, 0, 0)`. A zero return
stops the pump; message `0x36a` bypasses dispatch. Otherwise it calls
`0x180278500` for pretranslation and, if not consumed, `TranslateMessage` then
`DispatchMessageA`. No SKIP/WM_COMMAND-specific exclusion is present here.
Pretranslation uses thread virtual `+0xc0`; the application binding is ordinal
11849 at `0x180278fe0`, which forwards to `0x180278440`. That fallback handles
thread messages and walks window pretranslation paths. Those descendants can
consume a message, so unfiltered selection is not guaranteed callback delivery.
The body does not separately reject `GetMessageA == -1`.

**Base close.** Ordinal 8850 at `0x18021f890` has an outer state guard. On its
close path it saves document DWORD `+0x120`, clears it, and loops over attached
views. Parent-frame lookup `0x180292a70` precedes document virtual `+0x1c8`
and frame virtual `+0xd0`. It restores `+0x120`, calls document virtual
`+0x1b0` with argument 3, then `+0xf8`, and conditionally calls `+0x8` with
argument 1 if `+0x120` is nonzero. Correct EXE bindings are:

| Document slot | EXE target | MFC ordinal / body |
| --- | --- | --- |
| `+0x1c8` | `0x14077fe86` | 11723 / `0x180002850`, return only |
| `+0x1b0` | `0x14077fe74` | 9134 / `0x18021f990` |
| `+0xf8` | `0x14077fe0e` | 3727 / `0x180002850`, return only |
| `+0x8` | `0x1406807e0` | EXE deleting wrapper, known destructor sequence |

The `+0x1b0` body obtains an application-owned receiver through application
virtual `+0x208`; for argument 3 it conditionally calls that receiver's `+0xb0`
after `+0x70`. The getter and the allocated receiver's methods are now bound
below. This sequence establishes neither worker drain nor completed
view-to-document invalidation before storage release.

**Close receiver continuation.** Application `+0x208` selects EXE thunk
`0x14077fa66`, IAT `0x140d5fbf0`, ordinal 5167, and
[getter `0x1801d0230`](rev2a_mfc140_close_receiver.json). Its application
feature slots `+0x1c0` / `+0x1c8` select
[EXE bodies `0x1404e0540` / `0x1404e0510`](rev2a_skip_close_receiver_flags.json),
which return bits 0 / 1 of application DWORD `+0x14c`. Even with both bits clear,
the getter returns existing application pointer `+0x120`; it does not clear it.
It sets process-global DWORD `0x1803f3148` to 1. With feature bits set, an empty
pointer, and that global still zero, the separate allocation/initialization
branch can construct a receiver. Those conditions do not prove that the pointer
is always null on the station.

[Constructor `0x180038370`](rev2a_mfc140_close_receiver_ctor.json) installs
vtable `0x1802ea518`, labeled `CDataRecoveryHandler`. Its
[close methods](rev2a_mfc140_close_receiver_methods.json) are `+0x70` ->
`0x180038300`, reading receiver DWORD `+0x174`, and `+0xb0` -> `0x180039490`.
The latter conditionally updates recovery maps when receiver `+0x168 & 0x10`.
Its `+0xb8` -> [body `0x180039600`](rev2a_mfc140_frame_destroy.json) calls
`DeleteFileA` for a nonempty string and, after failure, calls `0x180236230`
with receiver `+0x120` and that string. This is recovery bookkeeping, not an
identified worker/callback drain. Arbitrary replacement of application `+0x120`,
allocation/initialization exceptions, and all map-helper descendants are not
covered by the cached-path fixture.

**Production frame continuation.** The retained startup template registration
uses frame getter `0x14067c2e0` alongside document getter `0x1406892a0`.
The [frame factory report](rev2a_skip_frame_factory.json) resolves runtime class
`0x140ea16e8` (`CProductionChild`) to factory `0x14067c280`. Constructor
instructions `0x14067c2ae` / `0x14067c2b5` install vtable `0x140ea1720`.
Its `+0xd0` selects thunk `0x14077fd30`, IAT `0x140d5f768`, ordinal 3803,
and [MFC body `0x1802abb20`](rev2a_mfc140_frame_destroy.json).
With no child HWND it returns zero. Otherwise it obtains the parent wrapper,
synchronously sends `WM_MDIDESTROY` (`0x221`) to the MDI client with the child
HWND in `wParam`, checks the top-level HWND, and optionally restores its style
and calls top-frame virtual `+0x358`. It returns one without using the send's
return value as a success check. This binds the production template's frame,
not every possible reparented frame. The static view destruction/detachment
continuation is now bound below. Windows delivery and completion of that path,
and pending-callback ordering, remain unproved. The `+0x358` target is the
title update below, not a document-unbinding barrier. A synchronous send alone
is not a document-lifetime barrier.

**Top-frame title slot.** [Getter `0x1802ac6a0`](rev2a_mfc140_top_frame_getter.json)
reads the child HWND at `+0x40`, calls `GetParent` twice through IAT
`0x1802ce360`, and tail-jumps to `0x18028f480`. The destroy path then uses the
returned object's primary vtable slot `+0x358`. A read-only scan of signature-1
complete-object locators in `.rdata` and `.data`, with `pSelf` equal to the
locator RVA, finds two offset-zero vtables whose class hierarchy includes
`CMDIFrameWnd`:

| Class | Vtable | Locator | Slot `+0x358` |
| --- | --- | --- | --- |
| `CMainFrame` | `0x140e8dc48` | `0x140f0fbb8` | `0x140639c80` |
| `CExtNCW<CMDIFrameWnd>` | `0x140e8ce88` | `0x140f0f7e8` | `0x140639c80` |

[Constructor `0x140630030`](rev2a_skip_top_frame_slot.json) and destructor
`0x1406304c0` install the `CMainFrame` vtable. `0x140639c80` saves `this+0x40`,
calls thunk `0x140780336`, and on `IsWindow` success tail-jumps
`SendMessageA(hwnd, 0x85, 0, 0)` (`WM_NCPAINT`). The thunk's IAT slot
`0x140d5e440` is `mfc140.dll` ordinal 11444, export RVA `0x2acb00`. The export
directory has no names. Ghidra labels that ordinal
`CMDIFrameWnd::OnUpdateFrameTitle`; the body is the evidence for that role.

[Ordinal 11444](rev2a_mfc140_update_frame_title.json) returns immediately when
style bit `0x8000` is clear. Otherwise it can call virtual `+0xe0` on the
object at frame `+0x120`, virtual `+0x2e8` on the frame and active child, and
[title writer `0x1802a4700`](rev2a_mfc140_frame_title_writer.json). The writer
concatenates strings and calls
[helper `0x1802b3620`](rev2a_mfc140_set_window_text.json), which uses
`GetWindowTextA`, `lstrcmpA`, and `SetWindowTextA`. `SetWindowTextA` and the
later `WM_NCPAINT` are synchronous window reentry. The retained title helpers
use the frame HWND and title strings; their direct calls do not receive the
production view. Virtual `+0xe0` and `+0x2e8` are not expanded here. Three
emulator cases execute the real wrapper: null `this`, a live HWND rejected by
`IsWindow`, and a live HWND that receives `WM_NCPAINT`. A sentinel at
`frame+0xe8` stays unchanged, and the wrapper does not read that field.

`0x18028f480` can still return a temporary `CWnd` when the HWND is absent from
the owning map. This slot binding applies when the returned object's primary
vtable is one of the two above. It does not prove map ownership, Windows
delivery of `WM_MDIDESTROY`, or retirement of posted SKIP messages. No
callback-retirement gate is promoted.

**Active-document read during the title update.** Ordinal 11444 calls vtable
slot `+0x2e8`. `CMainFrame`, `CExtNCW<CMDIFrameWnd>`, and `CProductionChild`
(`0x140ea1720`) all bind that slot to thunk `0x14077fc46`, IAT `0x140d5f8a0`,
ordinal 4861, RVA `0x2a3860`. [That body](rev2a_mfc140_active_document.json)
returns null when `frame+0x170` is null. Otherwise it returns `view+0xe8` and
does not write it. A null-pointer emulator run leaves the view page unmapped
and still returns null; a second run with a live view returns the stored
document pointer.

The production view's `WM_DESTROY` handler reaches thunk `0x14077fbb0`, ordinal
9117, RVA `0x27c060`, after its own document use. That body calls
`0x180292a70` and, when the returned frame's `+0x170` is this view, calls
[SetActiveView `0x1802a3790`](rev2a_mfc140_active_document.json) with a null
replacement before tail-jumping to `CWnd::OnDestroy` at `0x180290020`.
SetActiveView stores null at `+0x170` before virtual `+0x330`. The production
view binds `+0x330` to ordinal 8573, RVA `0x27f240`. On a zero activate flag
that body returns after `GetFocus`/`IsChild` helper `0x18027f2a0`; neither
function calls SetActiveView. The emulator observes the null store before the
virtual call and the field still null afterward.

`0x180292a70` walks parent HWNDs through `0x18028f480` until slot `+0x2b0`
returns nonzero. The production view's slot is ordinal 7881 (`xor eax, eax;
ret`). `CProductionChild` and `CMainFrame` use ordinal 7880 (`mov eax, 1;
ret`). The cleared frame is the nearest ancestor that returns nonzero, not
both frames. `CProductionChild` and `CMainFrame` keep separate `+0x170`
fields. The title call is after `SendMessage` returns. The window that receives
`WM_MDIDESTROY`, and what this development host's user32 does with it, is
recorded below. The production view's dialog parent is the child frame, also
recorded below. That clear writes the child frame's `+0x170`. The title read
uses the top frame's separate `+0x170`. Posted SKIP delivery remains open.
No callback-retirement gate is promoted.

**System mdiclient.** Both offset-zero frame vtables bind `+0x390` to thunk
`0x140780312`, IAT ordinal 3178, RVA `0x2ab4a0`.
[That body](rev2a_mfc140_mdi_client.json) calls `0x180298070` with class
`mdiclient` at `0x180351270`, extended style `0x200`, the HWND from
`this+0x40` as parent, child id `0xE900`, and stores the returned HWND at
`this+0x1d8`. The wrapper copies its class-name argument through to
`CreateWindowExA`. This DLL uses that string as the class name, not as a
`RegisterClass` argument.

`CProductionChild` binds `+0x390` to thunk `0x14077fd18`, ordinal 3093, RVA
`0x2abcb0`. The body loads its sixth argument from the incoming stack slot
at entry `rsp+0x30`. A nonzero value is the object used for the send. A null
value calls `0x1801381e0`, then reads `+0x8` and `+0x40`.
[Getter `0x1802782e0`](rev2a_mfc140_mdi_parent.json) returns thread-state
`+0x8`. `CWinThread` slot `+0xf8` is `0x180279250`: it returns `+0x48` when
that field is set, otherwise `+0x40`, otherwise
`0x18028f480(GetActiveWindow)`. The null-parent path reads `+0x40` itself, so
it uses the main-window field rather than the active-window field. The
following send is `SendMessageA([object+0x1d8], 0x220, ...)`. The caller that
supplies the sixth argument, and the store that publishes the current
thread's main window, are not established here.

The immediate `mov edx, 0x221` occurs once in `mfc140.dll` `.text`, at the
existing send in `0x1802abb20`, and does not occur in the EXE `.text`. EXE
`CMDIClientWnd` (vtable `0x140e8d938`) has a one-entry map for
`WM_ERASEBKGND` only. Its base chain is the CWnd map, which handles
`WM_DESTROY` and `WM_NCDESTROY` and has no `0x221` entry. MFC
`CMDIClientAreaWnd` does: data entry `0x1802f3da0` selects `0x18007f310`.
CreateClient does not create that class.

A development-host user32 probe, on Windows 10.0.19045 and not the waived
Windows 7 station, creates a hidden window of class `mdiclient` and sends
`WM_MDICREATE`. `GetParent` of the new child is that client. A direct child
of the MDI child then receives `WM_DESTROY` while `SendMessage(WM_MDIDESTROY)`
is still inside the client, and both HWNDs are gone when the send returns.
The system window procedure is not in the supplied binaries. The probe does
not load or execute Vision3D. The production view's parent is identified
below. The probe still does not prove that the production view's
`WM_DESTROY` clears the top frame's `+0x170` before the title update reads
it. No callback-retirement gate is promoted.

**Production view parent.** Both startup registrations at `0x1404d3605` and
`0x1404d3662` pass the `CProductionView` runtime class from `0x1406ac4b0` as
the template's view class, `CProductionChild` from `0x14067c2e0` as its frame
class, and the document class from `0x1406892a0`. The template constructor
stores those pointers at template `+0xc0`, `+0xb8`, and `+0xb0`, and installs
vtable `0x18032fce8`. Slot `+0x110` (`0x180228ed0`) calls slot `+0xf0`
(`0x180229ce0`) with the template as `this`. That body copies template `+0xc0`
to create-context offset 0, template `+0xb8` through `CreateObject`, and the
context address into `LoadFrame`. `CProductionChild` slot `+0x2e0` is ordinal
8062, `0x1802abec0`. It forwards that pointer to slot `+0x390`, which stores
it at `MDICREATESTRUCT+0x30` and sends `WM_MDICREATE`. The child `WM_CREATE`
handler reads that field and passes it to `OnCreateClient`, whose first
context pointer is the class created above.

`CProductionChild` slot `+0x60` returns an empty message map whose base is
MFC ordinal 7222, map `0x180342050`. That map's `WM_CREATE` entry is
`0x1802acaf0`. It reads `CREATESTRUCT.lpCreateParams` at offset 0, then
`MDICREATESTRUCT.lParam` at offset `0x30`, and jumps to `0x1802a2580`.
That body calls virtual `+0x350`. The child binds `+0x350` to ordinal 9003,
`0x1802a2530`. When the context and its first pointer are both non-null, it
calls `0x1802a2450` with child id `0xE900` and `this` equal to the child frame.

`0x1802a2450` creates the object named by the context's first pointer and
calls that object's `+0xb8` with style `0x50800000`, the frame object as the
parent argument, and the context. `CProductionView` binds `+0xb8` to ordinal
3075, `0x18027f050`. Its constructor calls `CFormView::CFormView` with
`0x82b`, and ordinal 499 stores that zero-extended value at view `+0x130`.
A null template returns zero before any window is created. `0x82b` is not
null, so this object takes the other path: `[parent+0x40]` is `hWndParent`
of `CreateDialogIndirectParamA`. The production view window is therefore a
child of the `CProductionChild` HWND.

The view's `WM_DESTROY` clears `+0x170` on the nearest frame ancestor. With
this parent, that ancestor is the child frame. The title update reads the
top frame's own `+0x170`. These are separate fields.

**Title read order.** Ordinal 11444 calls `this+0x2e8` before it asks which
child is active. `0x1802ab840` sends `WM_MDIGETACTIVE` (`0x229`) to
`frame+0x1d8`. `test rbx, rbx; jne` then skips the active child's `+0x2e8`
when that first call returned a document. The view destroy at `0x18027c060`
calls `GetParentFrame` and, when that frame's `+0x170` is this view, calls
SetActiveView with a null replacement. Production `OnActivateView` at
`0x18027f240` calls `0x18027f2a0`, `0x180292c40`, and `0x1802aea70`.
Vision3D.exe's import table has no ordinal 12856, so every `+0x170` writer
is inside `mfc140.dll`. On this development host, `WM_DESTROY` of a direct
child runs before `WM_MDIDESTROY` returns, and the static handler clears the
child frame. The title's child fallback therefore cannot return this view's
document after the send returns. The title still returns the production
document when the top frame's own `+0x170` is that view. That store is a
separate writer.

The production templates pass `CProductionDoc` (`0x140ea3830`, size `0x61f8`)
as their document class. Slot `+0x320` on that vtable is `0x1406970b0`, which
calls MFC ordinals 1504 and 1032. `CDocProcess` keeps ordinal 3793
(`0x18026bdc0`) at the same slot. The registrations that pass `CDocProcess`
use resource ids `0x7c8`, `0x7ca`, and `0x7cb`. The production registrations
use `0xbd1`. The helper that writes `+0x170` from document field `+0x258` is
the `CDocProcess` slot.

The production view binds slot `+0x370` to MFC ordinal 9697,
`0x18027c720`. That function calls `GetParentFrame(this)` and keeps the
result when it is a `CFrameWnd`; only a failed class test falls back through
the thread's main window. It passes that selected frame to SetActiveView.
`CProductionChild`'s runtime-class base getter resolves to ordinal 6890,
whose class is `CMDIChildWnd`; its base getter returns `CFrameWnd`.
Consequently this production print-preview path selects the child frame, not
the top frame. Posted SKIP ordering remains open. No
callback-retirement gate is promoted.

**Production view continuation.** The [view factory](rev2a_skip_view_factory.json)
binds startup getter `0x1406ac4b0` to runtime class `0x140eac618`, named
`CProductionView`, size `0x7018`, and factory `0x1406ac010`.
The [constructor](rev2a_skip_view_construction.json) installs primary vtable
`0x140eac650` at `0x1406ab5a2` / `0x1406ab5a9`.
The [teardown bindings](rev2a_skip_view_teardown_bindings.json) retain deleting
wrapper `0x1406abf00` and message-map getter `0x1406ac2d0`. Map `0x140eace80`
has 33 nonzero entries and a terminator: its own `WM_DESTROY` entry selects
`0x1406af270`, with no own `WM_NCDESTROY` entry. The retained `+0xe0` thunk
is `CScrollView::CalcWindowRect`, not a destruction hook.

The [production WM_DESTROY handler](rev2a_skip_view_destroy_handler.json)
still reads `view+0xe8`, sends an application notification through `+0x198`,
deletes two groups of five view-owned objects, kills timer 5, and conditionally
unregisters the secondary view interface through document virtual `+0x230`.
Only then, at `0x1406af3d7`, does it call thunk `0x14077fbb0`, IAT
`0x140d5fa30`, ordinal 9117 / `0x18027c060`.
That [base notification](rev2a_mfc140_view_teardown.json) handles active-view
state and calls [CWnd cleanup `0x180290020`](rev2a_mfc140_view_detach.json).
Neither retained notification body clears `view+0xe8`.

The [form-view base map](rev2a_mfc140_view_base.json) resolves through
`0x180339c50` -> `0x18033d1e0` -> `0x1803390d0` -> `0x18033d900`.
Regression checks validate each base-map getter and the full bounded entry
lists. The last map supplies `WM_NCDESTROY` handler
[`0x1802900d0`](rev2a_mfc140_view_ncdestroy.json). It calls `0x18028f560`
before view virtual `+0x250` at `0x180290259`. The production vtable binds
that slot to thunk `0x14077fb6e`, IAT `0x140d5fa88`, ordinal 11718 /
[`0x180212560`](rev2a_mfc140_view_postdestroy.json). For a nonnull receiver,
that body invokes deleting slot `+0x8` with argument 1.

The [window-detach helper `0x18028f560`](rev2a_mfc140_window_detach.json)
reads the current HWND at `view+0x40`. For a nonzero HWND it calls
[`0x18028f3c8(0)`](rev2a_mfc140_window_map_helpers.json), which reads the
thread-state map at `+0x28` without requesting map creation. A present map
selects key removal `0x180236b90(map+0x28, HWND)` before the helper clears
`view+0x40`; it then clears `view+0xd0` and returns the old HWND. It leaves
`view+0xe8` intact and ignores the key-removal result.

Thirteen fixtures execute actual detach, cached or fresh thread-state selection, key
removal, and empty-map cleanup for null HWND, absent map/table, empty bucket,
missing key, singleton, and collision-chain head/tail/middle removal. Singleton
cases cover zero, one, and two allocation blocks. Other keys remain linked.
CRT division is stubbed; its import is pinned to
`api-ms-win-crt-utility-l1-1-0.dll!ldiv`.

[Empty-map cleanup `0x1802368f0`](rev2a_mfc140_empty_window_map.json) frees
the bucket table through the pinned CRT `free` import at `0x180236902`, then
clears the table pointer at map `+0x30`. It clears count `+0x40` and free list
`+0x48`, calls the actual block-release loop `0x180275f10`, then clears the
block-chain pointer at map `+0x50`. Allocator stubs overwrite released storage;
the fixtures check saved-next-pointer use, release order, and final map fields.
The HWND, `view+0xd0`, and document pointer `view+0xe8` remain live throughout
these frees. No UI call occurs in these retained cleanup bodies; allocator
reentry and exceptional returns are not qualified.

[Thread-state accessor `0x1801381e0`](rev2a_mfc140_window_thread_state.json)
first obtains module state through `0x1801380f0`, then calls
[`0x18014f850(module+0xf8, 0x180138340)`](rev2a_mfc140_thread_state_helpers.json).
The cached module path uses the slot at `0x1803f32e0`, reads the selected
wrapper's `+0x8`, and uses that module's `+0xf8` slot for thread state. The
integrated fixture executes both lookups, placing a decoy state in another
slot and checking it remains untouched. `0x18014f850` checks slot bounds and
uses the TLS manager at `0x1803ed4f8`; its critical section is manager `+0x28`.
`EnterCriticalSection`, `TlsGetValue`, and `LeaveCriticalSection` are import-pinned
to `KERNEL32.dll` and stubbed. The cached fixture checks two balanced lock sequences,
but does not emulate mutual exclusion or actual Windows TLS.

Nine further branch cases execute `0x18014f850` with cached, negative,
out-of-range, unallocated, and empty slots; absent TLS/slot arrays; a short
thread slot array; and a missing factory. Noncached cases stop before the
factory call at `0x18014f92a`, slot allocation at `0x18014f8b0`, or non-returning
failure at `0x18014f95b`. Factory paths release the lock before reaching the
callback. The separate integrated fresh-slot case now continues through the
[factory `0x180138340` and publication `0x18014f4a0`](rev2a_mfc140_thread_state_initialization.json).
The factory calls [allocator `0x18014f120`](rev2a_mfc140_thread_state_allocator.json)
for `0x138` bytes. That wrapper requests `LocalAlloc(0x40, size)`, establishing
zero-filled storage on success; NULL reaches non-returning `0x18022ad10` at
`0x18014f13c`, not an ordinary NULL factory return. Its OS allocation is stubbed.
The [constructor `0x180137d00`](rev2a_mfc140_thread_state_constructor.json) does
not write the map field `+0x28`: a separate two-case test preserves both zero
and a nonzero initial value. Actual constructor execution therefore leaves
the fresh map NULL because of allocator zeroing, not constructor cleanup.

With an existing TLS array of sufficient size, actual publication stores the
fresh state in slot 3 under a third balanced lock sequence. No array growth or
`TlsSetValue` is needed in this case. Two integrated counterexamples put the
owning map in slot 2 and either an empty cached state or a missing state in
selected slot 3. Both return the old HWND and clear `view+0x40`/`+0xd0`, while
the owner-map entry, count, buckets, and block chain remain unchanged; `+0xe8`
also remains live. This is a constructed ownership-mismatch precondition, not
proof that the station reaches it. CFG routing is synthetic, not CFG validation.

**Decision:** successful state initialization is not an ownership-recovery
mechanism. Correct owner-thread/module-state/map selection must be proved before
detach can serve as evidence of unbinding. Nonzero cached state and cleared view
fields are both insufficient oracles. Default-module fallback `0x18014fa30` is
retained but not executed; TLS array growth/publication failure, manager creation,
native locking, allocation failure handling, and Windows exception dispatch
remain unqualified. These tests do not prove absence of cached object pointers,
handle reuse safety, or Windows message retirement.

The [production destructor](rev2a_skip_view_destructor.json), `0x1406abc60`,
stops/deletes its CAD engine and destroys many members before tail-calling
`CFormView::~CFormView` through thunk `0x140780570`, ordinal 1125 /
`0x18027ef90`. The retained base destructors continue through `0x18028c620`
to `0x18027bf00`; the latter calls `0x18021fae0(document, view)` at
`0x18027bf84` when `view+0xe8` is nonzero. CAD-engine stop is not proof of
inspection-worker drain, and earlier member/observer callbacks remain relevant.

**Document detach ordering.** [RemoveView `0x18021fae0`](rev2a_mfc140_remove_view.json)
finds the view's list node, calls [unlink `0x180235d10`](rev2a_mfc140_remove_view_helpers.json),
then clears `view+0xe8` at `0x18021fb0d`, before tail-calling document virtual
`+0xf0`. [Node release `0x180235a50`](rev2a_mfc140_view_list_release.json)
decrements document count `+0x70` and calls pool cleanup `0x1800302c0` on zero,
still before the pointer clear. Missing list membership reaches an exception
helper; successful detach must not be assumed on that path.

Document `+0xf0` binds to ordinal 8734 / `0x18021e240`. Its instructions select
close slot `+0x118` only when count `+0x70` is zero and DWORD `+0x120` is nonzero;
all other cases select `+0x1e0`. This branch distinction is obscured by the
decompiled pseudocode. Base close's temporary clearing of `+0x120` therefore
suppresses the close selection, not all callbacks. Slot `+0x1e0` binds to
ordinal 14051 / [frame-count update `0x18021e270`](rev2a_mfc140_view_frame_counts.json),
which iterates visible views, updates parent-frame counts, and invokes a frame
virtual. Document iterator slots `+0xe0` and `+0xe8` bind to ordinals 5392 and
5961, [bodies `0x18021fb40` and `0x18021fb50`](rev2a_mfc140_view_iterators.json).
The first reads the list head at document `+0x60`; the second advances the
position and returns the view stored in the node.

[Empty-list cleanup `0x1800302c0`](rev2a_mfc140_empty_view_pool.json) clears
the list count, free list, head, and tail before calling
[block release `0x180275f10`](rev2a_mfc140_view_block_release.json), then clears
the block-chain pointer at document `+0x80` on return. Block release saves each
next pointer before calling the pinned import
`api-ms-win-crt-heap-l1-1-0.dll!free`. The document pointer is still live during
these frees; allocator reentry and exceptions are not qualified.

Six fixtures now execute actual RemoveView, unlink, node/pool/block release,
document notification, frame-count update, and iterator bytes. Singleton cases
cover zero, one, and two blocks; other cases remove head/middle/tail from three
views. With auto-delete disabled and the last view removed, all three head
checks return zero, so there is no visibility query or frame callback. Remaining
views are modeled as hidden by visibility stubs. Only `free` and visibility
calls are stubbed within this continuation; the synthetic CFG trampoline routes
calls but does not test Windows CFG enforcement. Freed blocks are overwritten
to test saved-next-pointer use. Tests also check links/count, pointer ordering,
stack balance, and nonvolatile registers. Visible-view/frame descendants and
exceptional unwinding remain untested.
Six further cases check `+0xf0` selection for count 0/1 and auto-delete flag
0/1/`0xffffffff`, stopping before the selected tail call. This establishes a
local detach sequence, not Windows delivery, absence of earlier reentry,
pending-message retirement, or a complete stop-before-release barrier.

**Modal sheet.** Ordinal 3959 at `0x18021ab10` invokes the resolved
`PropertySheetA` wrapper `0x18021be8c`; the default branch then calls modal loop
`0x180296180` with flags 4 or 5. That loop uses unfiltered `PeekMessageA` and
calls `0x180278390`, which delegates to thread virtual `+0xc8` or directly to
`0x180278320` when no thread object exists. This proves a static nested path
to the same pump. Sheet continuation slot `+0x120` resolves to ordinal 2961,
`0x18021aad0`: it tests sheet `+0xa8 & 0x10` and sends message `0x476` to the
sheet HWND. The wrapper resolves `PropertySheetA` through `Comctl32.dll`;
the station's Common Controls implementation and alternate modal branch are
not analyzed. This is not a complete modal teardown or exception proof.

Two added tests pin these bindings and run six bounded Unicorn pump scenarios:
quit, synthetic registered message, WM_COMMAND, consumed pretranslation,
message `0x36a`, and an imposed error return with existing message data.
OS/pretranslation calls are stubs; tests check call order, zero filters, return,
stack balance, and nonvolatile registers. The error fixture is not evidence
of API-defined message contents after failure. Two further tests cover thirteen
cached receiver cases using the actual EXE feature-check bytes, and three frame
destruction cases with OS helpers stubbed. They check pointer preservation,
dispatch arguments/order, returns, stack balance, and nonvolatile registers;
they do not execute Windows destruction callbacks. With the production-view
binding, detach-order, and callback-decision regressions above, the 28 MFC
reports now retain 51 byte-verified functions. Full suite:
**34 tests pass in 5.578 seconds**. The constructor, import-binding, and
integrated window-detach tests also passed in a focused run of 0.332 seconds.
No station race is asserted and no entry gate is promoted.

### Station MFC 14 Intake, 2026-09-22

The user supplied [mfc140.dll](../v3d_files_/mfc140.dll) as coming from the
machine. The [pinned intake](rev2a_mfc140_station_intake.json) identifies:

- AMD64, Machine `0x8664`, PE32+ `0x020b`, preferred base `0x180000000`.
- File version `14.23.27820.0`, size 5,784,856 bytes.
- SHA-256 `0cf26008fae0cb61dfe49e1c3fc17e0dd860be011d9a6a64b452f56335bafbfe`.
- Host Authenticode status `Valid`, signer Microsoft Corporation. This is not
	a malware verdict or a Windows 7 target trust/compatibility test.
- Raw export table: base 256, 14,028 entries, no names. All MFC ordinals parsed
	from the stock EXE imports have nonzero entries in this DLL.

| EXE-bound operation | Ordinal | DLL RVA | Preferred VA |
| --- | --- | --- | --- |
| `CPropertySheet::DoModal` | 3959 | `0x21ab10` | `0x18021ab10` |
| Base document close | 8850 | `0x21f890` | `0x18021f890` |
| Application pump binding | 11881 | `0x279280` | `0x180279280` |

These three exports are not forwarders. Operation labels come from the retained
EXE bindings, not names in this DLL's ordinal-only export table. The existing
verifier now pins file hash/size/version, architecture, export addresses and
prefixes, and EXE import coverage. Full suite: 24 methods pass in 4.856 seconds.

The architecture/generation and missing-file blockers are resolved for static
investigation; the prior acquisition deferral is superseded. The original
installed path and loaded-module identity were not supplied, so exact loaded
runtime equivalence remains unverified. At intake, no native DLL loading, target
execution, Ghidra import, binary change, or security-control bypass occurred.
The later static analysis above supersedes the import/analysis status, not the
loaded-runtime limitation. Receipt of the file does not pass a lifecycle gate.

### Supplied MFC Intake, 2026-09-22

The previously supplied `v3d_files_/mfc140.dll` reported version
14.0.24210.0, size 4,705,072 bytes, SHA-256
`f8becf698ba1068cfc32e72e210215a1ed4368cdd5f21ea45bf393677dbd77c6`.
The file was no longer present at this path during the later MFC 10 intake;
the reason for its absence was not established. The identity below is historical.
Its raw PE headers and pefile both identify Machine `0x014c` (x86), PE32 magic
`0x010b`, base `0x10000000`. The mapped EXE is Machine `0x8664` (AMD64),
PE32+ magic `0x020b`. This file is therefore rejected as the runtime dependency
of that EXE; 64-bit Windows also carries 32-bit runtime files.

The raw export address table has ordinal base 256, 14,448 entries, and no names.
Ordinals 8850 and 11881 have RVAs `0x95c80` and `0x278ee0`, respectively, but
their presence does not establish matching x64 semantics. A bounded parser's
partial export listing must not be used to claim either ordinal is absent.
No Ghidra import or target execution was performed for this mismatched DLL.
The required artifact remains the AMD64 MFC DLL actually loaded by the deployed
Vision3D executable, with its original path and version/provenance.

### Offline Programmer MFC Intake, 2026-09-22

At this earlier intake, the user could not acquire the station runtime because security software flagged it as
`Trojan:Script/Wacatac.B!ml`. That report alone does not establish infection or a
false positive; the flagged station artifact was not inspected in this intake.
Do not disable protection or restore a quarantined file for this analysis.

The alternative [mfc100.dll](../v3d_files_/mfc100.dll) comes from the user's offline
programmer with Vision3D installed. Read-only header/resource inspection identifies
AMD64 (`Machine=0x8664`, PE32+ magic `0x020b`), original filename `MFC100.DLL`,
file/product version `10.00.40219.325`, and size 5,574,984 bytes. SHA-256:
`ef2e0df287af95855b6b13173259df847a2cb8a1872ba3d4573e82abd4fb9699`.
Host `Get-AuthenticodeSignature` reports `Valid`, signer Microsoft Corporation.
This signature result applies only to this supplied file, not the flagged station
artifact, and is not a comprehensive malware assessment.

Architecture matches, but runtime generation does not: the retained EXE imports
`mfc140.dll`, whereas this artifact is MFC 10. Neither renaming the file nor
reusing its export ordinals establishes MFC 14 implementation behavior. No DLL
loading, native target execution, Ghidra import, or binary modification occurred.
It is not accepted for the MFC 14 lifecycle proof and no gate is promoted.

A vendor-provided runtime or an MFC 14 copy from the offline programmer can be
assessed next. Without the station's loaded-module identity, even a signed AMD64
MFC 14 copy remains reference evidence rather than an exact deployed-runtime
match. Station acquisition was blocked at this earlier intake; the newer
station MFC 14 intake above supersedes that acquisition status.

## Unresolved Proof

- Upstream stop ordering; the resolved invalidation/modal bindings provide no stop barrier.
- Reachable thread/window pretranslation and reentry schedules during close;
	unfiltered MFC pump selection and the nested modal-pump binding are now verified.
- MFC view/window destruction and document-binding invalidation before storage release.
	Top-frame `+0x358` is a title update plus `WM_NCPAINT`, not that invalidation.
	Its document read uses `frame+0x170` and is skipped when that field is null.
	Host user32 destroys an `mdiclient` child before `WM_MDIDESTROY` returns.
	The production view dialog is parented to `CProductionChild`, so its
	destroy clears that child's `+0x170`. The title function reads the top
	frame first and consults the active child only when that read is null, so
	the child fallback cannot return this view after the send returns. The
	title still returns the production document when the top frame's own
	`+0x170` is that view. The `+0x258` helper that can write `+0x170` is
	`CDocProcess` slot `+0x320`; the production templates register
	`CProductionDoc`, which overrides that slot. Document close destroys listed
	view frames before the deleting destructor releases `+0x23e0` and `+0x2448`.
	The SKIP producers post `[CAO+0x5838]+0x40` without a pointer, HWND, or
	return check, and nothing clears that field. Posted SKIP ordering remains
	open for a message that arrives while the HWND still exists, for a view
	outside the document view list, and for a producer reading the field after
	detach. ExecuteSkip's posts run on `CProductionThread::Handler`.
	`ProductionStop` polls `CViThread::Stop` with timeout zero and can dispatch
	messages before the thread exits. `OnCloseDocument` and the document
	destructor do not call that stop. A null HWND is a thread message. The application map has no entry
	for it, and on this host `DispatchMessageA` does not call a window
	procedure. `CExtMenuControlBar` slot `+0xa90` returns zero for this registered
	id, and its sends use constant message ids. Ordinal 11812 calls
	`[frame+0x120]+0xb8` only when that qword is nonzero. Construction stores
	zero, and the three frame vtables do not store a replacement. The production
	view map has no `WM_CREATE` entry. The `CFormView` handler restores the
	create context from `view+0x138` and `AddView` links the view before
	`OnChangedViewList`. The `WH_CBT` hook subclasses the new HWND to a
	procedure that calls `AfxWndProc`, and message 1 then reaches that handler
	through `CWnd::OnWndMsg`.
- Shared synchronization for SKIP refresh, RegistrySave, reset, and destruction.
- Allocation/reuse identity and upstream admission/exception containment.

See [entry-gate evidence](rev2a-entry-gates.md) and the
[current implementation status](../plans/robust_patch_revision_2a_status.md).
These findings do not pass a Rev6 lifecycle gate.

## Mapping Access

Saved-project extraction succeeds without changing the active Ghidra project.
On 2026-09-22, two running Python processes belonged to the headless MCP launch
chain, and the project lock named this machine/user with file-channel locking.
That session is a likely lock holder, not proven handle ownership. Neither process
was stopped and neither lock was deleted. These additions are atlas files and
retained reports, not annotations saved into the active Ghidra database.

Later the same day, the previous stdio Python processes were no longer present
and the managed-server status reported stopped. A managed MCP server was started
on loopback `127.0.0.1:8765`; an explicit client `health.ping` returned
`{"message":"pong","status":"ok"}`. No project was opened or changed by this
connectivity check, and no lock files were removed. Access is through the installed
`ghidra_cli` client; direct Ghidra tools are not exposed in this chat.