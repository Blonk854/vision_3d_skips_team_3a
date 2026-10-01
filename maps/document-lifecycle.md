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

The direct callers of `0x140541050` are `0x1404aebe9`, `0x14068f7d7`,
`ReloadDoc` at `0x1406937d7`, the SKIP poster at `0x1406a085e`, and
`HandlerProduction` at `0x1406a2d87`. Close, the document destructor, view
destruction, and the `0x52c` handler do not call it. The non-producer parents
are document slot `+0x108` (`0x14068dc20`, the only stored pointer, at
`0x140ea3970`) and CCAPM secondary slot `+0x80`. Slot `+0x108` keeps the
document in `rsi`, calls `SetProductionVMC`, then calls `PrepareExecData`. Its
body contains no displacement `0x3868` and does not call `ProductionStop`. The
only entry to `0x1404aecd0` is the adjustor at `0x14075ad60` (`add rcx, 0x10;
jmp 0x1404aecd0`), stored at `0x140eddc50`. That function calls `0x1404ae9d0`
only when the vector at `[this+8]` has at least two `0x80`-byte elements, and
`0x1404ae9d0` resets the caller's second argument. Close bodies contain no call
through displacement `0x108` or `0x80`. The proposed hook at `0x140541050` alone is therefore not yet proved to reset
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
with wParam and lParam zero. The posts at `0x1406a103b` and `0x1406a1075`
first call `0x1406a15d0`. The post at `0x140736feb` does not. Its function
saves `rcx` at `[rsp+8]`, sets `rbp` to `rsp-0x6f8`, and later loads `r15`
from `[rbp+0x700]`, which is that saved `this`. It then reads
`[[this+0x10]+0x5838]`. The constructor `0x140735120` stores its `r8`
argument at that `+0x10` field. Caller `0x14066dc00` passes `[this+0x28]`
without calling the accessor. That caller is slot `+0x18` of vtable
`0x140ea8a10`. The base constructor `0x1406997d0` stores zero at that field.
`0x1406a6b95` calls `0x1406a15d0`, stores the result at `[rbp+0x30]`, and
`0x1406a6bc7` passes that block to `0x1406a4980` with the pool at
`thread+0xec8`. `0x1406a4980` copies `[argument+8]` to each worker's `+0x28`.
`CProcessingGreyZoneThread` slot `+0`, `0x14069a890`, stops the worker and,
when `edx` bit 0 is set, frees the `0xd8`-byte block. That destructor does not
write `+0x28`, and nothing calls it directly. Close does not call the pool
walk, so the copied document pointer stays in the worker.
The worker loop `0x1406a1a50` waits on `[worker+0xa0]` and the stop event at
`[worker+0x18]`. A zero result calls slot `+0x18`, which reads `[worker+0x28]`
and then stores zero at `[worker+0x58]`. The only `SetEvent` of a `+0xa0`
field is `0x14069fb80`. It takes the worker from the pool at `thread+0xec8`
and is reached only through `HandlerProduction`. Close does not call that
chain, so it does not wake an idle worker. It also does not wait for a worker
already inside slot `+0x18`. The constructor `0x1406997d0` creates
`[worker+0xa0]` with `CreateEventA` arguments all zero and `[worker+0xa8]`
as a manual-reset event whose initial state is signaled, then calls
`CViThread::Start`. Resize `0x1406a99d0` stores each availability handle in
the vector at `pool+0x20`. Selector `0x1406a1660` passes that copy's length
in `rcx` and `[pool+0x3c]` as the timeout. The thread constructor stores
`[rsp+0x4c] * 0x3e8` at `thread+0xf04`, the same dword. A timeout result
`0x102` skips the store to `[worker+0xb8]`, so a busy worker is not taken.
The worker signals
`+0xb8` after slot `+0x18`, and no wait in this executable loads that field.
After `ProductionStop` joins `document+0x3868`, it calls that producer's
slot `+0` with `edx` 1 while the slot is still nonzero, then stores zero.
The producer destructor calls the pool destructor at `thread+0xec8`.
`0x140655980` walks `[pool+8]` for `[pool+0x38]` entries and calls each
worker's slot `+0` with `edx` 1. That slot is `0x14069a890`, which calls
`0x14069a110`. Close does not call `ProductionStop` or `0x140655980`.
The producer can still join those workers itself. `HandlerProduction` calls
`0x14069c890`, which reads document byte `+0x5830` through `0x14068bd60` and
clears it. A nonzero value calls `0x1406a99d0` on `thread+0xec8`. When the
requested count differs from `[pool+0x38]`, that function calls `0x140655980`
and then builds new workers. The only store of 1 at `+0x5830` is `ReloadDoc`
`0x140692af0`. The constructor store at `0x14067e254` is inside the span that
writes zero at `+0x5838`. Close, the document destructor, view destruction, and
the `0x52c` handler do not call `ReloadDoc` or `0x14069c890`. The instruction
after the first checker call compares `[rbp+0x770]`, so the flag does not
itself leave the cycle.
Caller `0x14069fd70` does call `0x1406a15d0` and passes the
result. If either pointer names a document whose view was already freed, the
read is a use of freed storage. All three
sites go through IAT `0x140d5bc00`. The sequences do not test the
view pointer, the HWND, or the return value. The document constructor clears
`r14` at `0x14067df59` and stores it at `+0x5838` (`0x14067f60e`). No
instruction in that span writes `r14`, and no branch enters the span after the
clear or jumps past the store. `r14` is nonvolatile, so the calls in that
span return it unchanged and the store writes zero. `OnInitialUpdate`
`0x1406af770`, view slot `+0x328`, copies `this` to `r15` and stores that view
at `[view+0xe8]+0x5838`. The EXE `.text` section has two writes of displacement
`0x5838`: that constructor store and this publisher. Refresh `0x1406adaf0` has direct calls from the
message handler at `0x1406b0704` and from `0x1406b3b3f`. The refresh loads
`[view+0xe8]` and calls `0x140541040`, which is `lea rax, [rcx+0x23e0]; ret`.
It compares the count at `[array+0x10]`. A positive count reads `[array+8]`
and indexes a dword. The function contains no displacement `0x382d`, `0x382e`,
or `0x5838`, and it does not test the document pointer before that call. The
preceding call `0x14067ab20` contains no displacement `0x3868`.
The registered-message handler `0x1406b0700` calls that refresh and returns
0. `0x1406b3760` calls it at `0x1406b3b3f`, then `RedrawWindow` on `[view+0x40]`.
Its only direct caller is `0x1406971b0`, which calls document slot `+0xe0` and,
when that result is nonzero, slot `+0xe8`, then passes the view to
`0x1406b3760`. Neither body contains displacement `0x3868`. The six direct
callers of `0x1406971b0` are in `0x1404db330`, `0x1404dc5c0`, `0x1404dc9e0`,
and `0x1404dd140`. Close does not call `0x1406971b0` or `0x1406b3760`.
`0x1406a5010` calls the SKIP poster `0x1406a06b0` only when
`[document+0x3978]` is 1. The not-equal branch jumps to `0x1406a5304`, past
the call. The poster itself does not read that dword. The constructor stores
`r14` at `0x14067e1d6`, inside the span that starts by clearing `r14`.
`HandlerProduction` stores `esi` at `0x1406a34a1` and a shifted value at
`0x1406a375a`. `0x14069a9c0` stores `r15` there when `document+0x382d` is not
1; `r15` is cleared at `0x14069a9fc` and not written before that store. Its
only direct caller is `HandlerProduction` at `0x1406a2e5e`. Close contains no
displacement `0x3978`. The poster calls CCAPM secondary slot `+0x80` with the
document as `rdx`. `al == 1` jumps to `0x1406a1056`, past the local reset, and
that block posts through `[document+0x5838]` with no pointer test. The only
`mov al, 1` in `0x1404ae9d0` is at `0x1404aec91`, after `0x140541050` and the
later call `0x140541020`. An earlier `xor al, al` jumps to the epilogue
without that reset. The other poster arm calls `0x140541050` itself. Close
does not call the poster. The post at `0x1406a103b` runs only when `r13d` is
3; the not-equal branch skips it. Both posts are `PostMessageA`. After either
one the function destroys three stack objects and returns `r13d`. It does not
call a wait. The first post then stores 3 into `r13d`, so that return value is
3. The grey-zone post at `0x140736feb` runs only when document byte
`+0x3835` is 1. The only store of that byte is the constructor at
`0x14067e4cd`, which saves the `bool` returned by `GetValeurIni_bool`.
Close contains no displacement `0x3835`. After `PostMessageA` the function
jumps to `0x14073742d`, runs stack destructors, and returns. It does not wait.
Its only direct caller is `0x1407354b0`, whose only direct caller is
`0x140735f10`. That function is called from worker slot `+0x18` at
`0x14066dc2a` and from `0x14069fcd0` at `0x14069fdaa`. `0x14069fcd0` is called
from the worker queue `0x14069fb80` and from `0x1406a88e0`. None of
`0x140735f10`, `0x1407354b0`, or `0x14069fcd0` contains displacement `0x3868`
or `0x382e`. Close does not call these functions.

Production `OnCloseDocument` `0x14068d9d0` calls `0x1406928d0`, then
`0x14063b430` on the pointer at `document+0x3850`, then `0x1404e03f0`, and
only then tail-jumps MFC ordinal 8850. The constructor stores
`[[AfxGetModuleState()+8]+0x40]` at `+0x3850`. When that object's dword
`+0x5878` is nonzero, `0x14063b430` waits on the semaphore at
`[object+0x5870]`. `0x14063ac30` creates that semaphore with
`CreateSemaphoreA(NULL, 1, 1, NULL)`. The same close function releases it,
by a tail jump when the incremented dword at `+0x5868` equals 1 and by a
call otherwise, before `OnCloseDocument` continues. That handle is not
`document+0x3868`. The call to `0x14064b880` is the side where the
incremented counter is not 1. That helper waits on `[object+0x118]`, then
calls `DoEvents` while bits `0xc` of `[object+0x14]` are set, then
`CTalkToSuperviseur::DeConnect`. Its bytes do not mention `document+0x3868`.
None of those three functions calls `ProductionStop`. `HandlerProduction`
has no displacement `0x5870` and does not call `0x14063b430`. The
`CMainFrame` constructor stores zero at its own `+0x5870`. Its destructor
passes that qword to `CloseHandle` and then stores zero. That call does not
wait, and that field is not the producer. Before that loop calls frame slot `+0xd0`, ordinal 8850 calls document slot
`+0x1c8`. The slot is MFC ordinal 11723, and its body is `ret 0`. The ordinal's view loop runs before the document
destructor, so this prefix does not join the producer before the view is
destroyed. While
`document+0x70` is nonzero, that function takes the view at
`[[document+0x60]+0x10]`, calls `GetParentFrame`, and calls frame slot `+0xd0`
through the CFG stub `jmp rax` at `0x1802bf060`. `CProductionChild` slot
`+0xd0` is ordinal 3803, the `WM_MDIDESTROY` send. An empty list branches to
`0x18021f927`, skipping that loop. After the loop, nonzero `document+0x120`
calls document slot `+0x8`. That deleting wrapper calls `0x14067fc20`, which
tail-jumps `0x14051fbf0`. The base destructor releases `+0x2448` through
`0x14051ff90` and then `+0x23e0` through ordinal 1439. Ordinal 1439 frees the
`CUIntArray` buffer. The direct-call closure of `0x14067fc20` includes that
base destructor, imports no `user32`, and does not call the message pump
`0x1405e8af0`. Those direct calls, and one further direct-call level, do not
call `ProductionStop`, `AskToStop`, worker `Stop`, or the pool cleanup, and
their bytes do not mention `+0x3868`. The destructor body's own import
calls are not `WaitForSingleObject` or `CViThread::Stop`. Its direct function
callees contain no `WaitForSingleObject` import. Three direct-call levels
from close, the destructor, view destruction, the `0x52c` handler, and the
close poster contain no `CViThread::Stop` import. The only
`WaitForSingleObject` functions in that closure are `0x14063b430`,
`0x14064b880`, `0x1406ae120`, and `0x1406ae950`. None of those bodies contains
displacement `0x3868`. Virtual calls inside the closure are not covered by
that direct-call walk. Dropping the `0x52c` handler, three direct-call levels
from `OnCloseDocument`, the document destructor, `WM_DESTROY`, the view
destructor, and the close poster are 43 functions. That set does not include
`ProductionStop`, `AskToStop`, or `ProductionStart`, and none of those bodies
contains a call or jump through displacement `0x28`. The destructor calls
`0x14066e530` on `document+0x5888`. That helper walks `[this+0x18]` through
`[this+0x20]` in steps of `0x370` and calls slot `+8` with `edx` 0. The other
virtual helpers in that 43-function set are `0x140740280`, `0x14045f700`, and
`0x140579580`. The first two call slot `+8` with `edx` 1 on a nullable object
or on each vector pointer. `0x140579580` releases a refcount with `lock xadd`
and then calls slots `+8` and `+0x10`. None of the four bodies contains
displacement `0x3868`. The list at `CProdCarte+8` holds
`boost::detail::sp_counted_impl_p<CAnomalieProd>` control blocks. Dispose,
slot `+8`, calls `CAnomalieProd` slot `+8` with edx 1. That frees the element
through MFC ordinal 1487 after the same StructSupport destructor. Slot `+0x10`
frees the `0x18`-byte control block through the same ordinal. `CButtonST`
stores null at `+0x158`. `0x1407420c0` and `0x140742230` replace it with a
`0x10`-byte `CBitmap`. The destructor calls that object's slot `+8` with edx 1,
which is `0x1405b07a0`. It calls `0x1405b0700`, and MFC ordinal 3748 calls
`DeleteObject` when the handle at `+8` is nonzero. edx bit 0 then frees the
bitmap through ordinal 1487. The pointer vector at `document+0x2478` is filled at `0x14053416f`
with `CMacro` objects (vtable `0x140e4d398`). Slot `+8` is
`0x140521b30`, which calls `VitDataCAD.dll!CMacro::~CMacro` and then
frees the object through ordinal 1487. Three direct-call levels from
that destructor do not call `CViThread::Stop` or `WaitForSingleObject`
and do not mention `+0x3868`. The calls on `document+0x2eb8` and
`document+0x2550` tail-jump `CSerialDriver::~CSerialDriver`. The call on
`document+0x60c8` frees `[object+8]`. The call on `document+0x6078` is
`ret 0`. Before that array release, a nonzero `document+0x19e8`
calls slot `+0x190` and then drops the returned refcount. The constructor
stores zero there. `SetProductionVMC` later stores the pointer returned by
`CVMC_ListSingleton::GetCurrent`. The stock `CVMachineController` vtable
`0x1800ceda8` implements slot `+0x190` as a forward to `[controller+0x870]`
slot `+0x220`. That second slot forwards through `[proxy+0x118]` to
`IAcquisitionController` slot `+0x220`, which this DLL binds to `_purecall`.
The concrete override is not in the supplied station files. The base
destructor still does not call `ProductionStop`. A null
slot skips the call. Other virtual calls in the wider closure remain
unfollowed. The same destructor then loads `document+0x5878`. When that
pointer and the count stored ahead of it are nonzero, it calls slot `+8`
with edx 3 and afterwards stores null. Slot `+8` is the vector deleter for
the `0x410`-byte elements, and the element destructor does not call
`ProductionStop`. That walk calls `StructSupport.dll!CAnomalieProd::~CAnomalieProd` with edx 0.
The destructor releases point, string, buffer, and image members, then
tail-jumps to `0x18008d550`. Neither function imports `user32` or the
executable. The same destructor then calls `CAsynchCommandExecution::Kill`
on `document+0x6128`. When that object's byte `+8` is 1, Kill resets one
event, sets another, and waits up to `0xc350` milliseconds on the handle at
`+0x10`. That handle is not `document+0x3868`, and Kill does not call
`ProductionStop`. The constructor stores a `CreateEventA` handle at
`+0x3878` and a `CreateSemaphoreA` handle at `+0x3890`, and it stores a
separate null at `+0x3868`. The destructor closes those two handles and
never mentions displacement `0x3868`. `CloseHandle` does not wait, so the
production thread object is still not joined. The array release itself does not dispatch the SKIP callback. After that
free, the base destructor calls `CDataCao::~CDataCao` with `this` equal to
`document+0x180`, then tail-jumps to MFC ordinal 1104 with the document
pointer. `VitDataCAD.dll!CDataCao::~CDataCao` releases strings, points,
lengths, image definitions, and the recipe, then returns. Three direct-call
levels from that destructor do not call `CViThread::Stop` or
`WaitForSingleObject`, and they do not mention `document+0x3868`.
`DeleteCadTab` walks the `CCAD_Base` pointer array at `+0x1018` and calls
slot `+8` with edx 1. That slot on `CCAD_Base` runs the scalar destructor and
then frees the object. The same call on the exported element vtables
(`CComposant`, `CMire`, `CPad`, `CSkip_bloc`, `CMacro`, and the other
`Add*` types) does not call `CViThread::Stop` or `WaitForSingleObject` and
does not mention `+0x3868`. The destructor also clears the embedded `CMacro`
array at `+0xd78` with edx 0, so each element runs `CMacro::~CMacro` and is
not freed. The document block is freed only after this
call returns. The producer is still not joined before either call. Ordinal 1104 then calls `0x18021e1a0`. While `document+0x70` is nonzero, that function unlinks the head view and stores zero at `view+0xe8`. The `CUIntArray` release is before the jump, so this clear is after the skip array is freed. The walk does not write `document+0x5838`. The same ordinal then calls `0x180221190`, which reads the list at `document+0xe0` and, for each node, calls slot `+0` with edx 1 on `[node+0x10]`. The document constructor `0x18021de40` stores zero at `+0xe0`. MFC ordinal 2525 is the updater for that list, and none of the supplied station binaries imports it. Its only call inside `mfc140.dll` passes `r8` 0 and `edx` -1, which unlinks existing nodes instead of allocating one. That walk does not mention `document+0x3868`. Before the walk, a nonzero `document+0x50` is called at slot `+0xd0` with the document as the second argument. The template constructor installs vtable `0x18032fce8`, and that slot is `0x180228e70`. It stores zero at `document+0x50` and jumps to the list unlink `0x180235d10`. It does not mention `document+0x3868`. Ordinal 1104 also calls slot `+0x10` on `document+0xb8`, `document+0x178`, and `document+0xd0` when those qwords are nonzero, passing only that pointer. The constructor stores zero at all three. After the first two calls it stores zero again. None of those instructions uses displacement `0x3868`. The 83 slots of document vtable `0x140ea3868` do not store those qwords. The document constructor's call at `0x14067e00d` builds the separate object at `document+0x5888`, and that object's constructor zeros its own `+0x178`. The executable imports of the MFC functions that store `+0xb8` are ordinals 981 and 1838. Both run on the application object: ordinal 981 is called before `0x1404cdff0` installs vtable `0x140e39770`, and ordinal 1838 is app vtable slot `+0xb0`. The primary slot `+8`, `0x1406807e0`, is the deleting
destructor: it runs that destructor and, when edx bit 0 is set, calls ordinal
1487, CRT `free` of the document block. `OnCloseDocument` uses edx 1 on that
slot when `+0x120` is still nonzero after the view loop. There is no document
pool. Runtime class `0x140ea3830` is the only pointer to factory
`0x140684f40`. That factory passes `0x61f8` to `0x14076d550`, which calls
CRT `malloc`, and on success calls constructor `0x14067dea0`. A null
allocation returns zero. The base constructor calls `CDataCao::CDataCao` on `this+0x180` before it
builds the `CUIntArray` at `+0x23e0` through ordinal 973, which zeroes the
buffer pointer and the count fields before `CreateObject` returns. The
document constructor then overwrites the vtable at `+0x180`. Neither
constructor calls `SetProductionVMC`. Its zero-mode path stores 0 at
`+0x3924` and publishes that same document at setter index 0. The call with
edx 0 is outside the constructor, so the published pointer has already
finished both constructors. That publish does not join the producer.
Document slot `+0x108` is the other direct publisher. It stores `this` and
passes the mode returned by `0x1404d25e0` to `SetProductionVMC` before it
uses `document+0x2548`. That later use is an argument to `CCAPM` slot
`+0x140`, not a call to `AskToStop`. The function calls neither
`ProductionStop` nor `ProductionStart`. Same-address reuse is CRT heap reuse
after the free, and only a later factory call constructs the replacement.
Before that release, the destructor calls `CCAPM` slot `+0xe8` with r8 zero
and edx equal to `document+0x3924`. `SetProductionVMC` stores that same
index and publishes the document there: argument 2 or below uses
argument minus one, and argument 3 or 4 uses argument minus three. The
setter writes the pointer only when the index is below the vector count.
`ProductionStart` copies `document+0x3924` into the new thread at `+0xec0`
before slot `+0x10`. The producer accessor reads that thread dword and
jumps through slot `+0xe0`, which returns the published pointer. The
destructor does not clear `+0xec0`. A later accessor call therefore sees
null unless the index is out of range or a later publish replaces it.
`HandlerProduction` copies its thread argument to `r14` and the cycle at
`0x1406a2770` repeats while `thread+0x32` is zero. The function contains 99
calls to the accessor. None is followed by a test of the returned pointer or
a branch on it. The back-edge's first use is the compare of
`[document+0x382e]` with 1. The store that sets `thread+0x32` is the
equal side of that compare, so a null slot faults in the compare and the
store does not run. The not-equal side reloads and calls `0x1406970f0`
with no pointer test. That function's first read is `[document]`. It then
calls document slots `+0xe0` and `+0xe8`, `GetFirstViewPosition` and
`GetNextView`. The helper `0x1406b36f0` reads `[view+0xe8]` with no null
test. When `document+0x3928` is 3 or 4 it stores the caller's dl at
`view+0x6058` and returns. It does not write `thread+0x32`. A null slot
therefore faults before the cycle can set the stop byte. The next iteration
does not reuse a document pointer from the previous one. Before the cycle,
`__RTDynamicCast` returns the app object and its `+0x1b0` pointer is saved
at `[rsp+0x78]`; that slot is not written again. The cycle reloads it into
`rsi`, reloads a dword from `[rsp+0x68]` into `ebx`, and reloads
`thread+0x18` into `rdi` before the accessor runs. The accessor result is
then passed as `r8`. The only full document pointer kept across a later
accessor call is `rbx`, in two windows that both end before the back-edge:
one reads `[rbx+0x5c9c]` and `[rax+0x5c98]`, and the next copies
`[rbx+0x5c9c]` into `[rax+0x5c98]` and then overwrites `bl`. No accessor
result is stored to memory. A document published into the same index is
what the next check observes. Close still does not join the producer. The
reuse gate is not promoted. On this close path the
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
runs Handler. When document byte `+0x382d` is 1, Handler calls `0x1406a1da0`.
That function stores 1 at `thread+0x32`, calls `AskToStop`, and returns 0.
Otherwise Handler calls `HandlerProduction`. Both arms then call MFC ordinal
2175, whose tail is `_endthreadex`. The only direct call of `HandlerProduction`
is that not-equal arm. `HandlerProduction` contains no displacement `0x382d`,
so a running producer does not read the byte. `ProductionStop` clears `esi`
at `0x1406921e0`. When `document+0x3881` is 1 it stores 0 there and sets
`+0x382d` to 1 if that byte was 0, then calls `ProductionStart`.
`ProductionStart` still stores and starts the producer. When the byte is 1 it
stores the zeroed `r12` at `+0x3860` instead of constructing the communication
thread. The other writer is document vtable slot `+0x100`, `0x14068dab0`. It
dynamic-casts `CWinApp` to `CAVisionApp` and copies byte `+0x198` into
`document+0x382d`. Close, the document destructor, view destruction, the close
poster, and the `0x52c` handler do not call that slot.
`MakeFirstPassInspection` is the only direct caller of `ExecuteSkip`, and
`HandlerProduction` is its only direct caller. `ProductionStart`
`0x140691c80` stores the new thread at document `+0x3868` and calls slot
`+0x10`.

`ProductionStop` `0x1406920f0` is the only direct caller of `CViThread::Stop`
on that field. The import has seven other call sites. `CCAD_Zone2D_PropSheet`
stops `[this+0x41b0]`. `CLogManagerView::Close` stops the embedded thread at
`this+0xf0`. The `CViThread4Pool` destructors for `CPCBR_Data2DInit` and
`CPCBR_Data3DInit` stop `this`. The embedded object at `document+0x2548`
stops `document+0x3860`. The worker stop `0x14069a110` stops `this`.
`CWizardGenericElement` stops `[this+0xa40]`. None of those bodies contains
displacement `0x3868`. `CViThread::Stop` signals `[this+0x18]` and waits on
`[[this+8]+0x58]`. `Start` stores that thread object at `[this+8]` and resumes
`[that+0x58]`. `GetStopEventHandle` returns `[this+0x18]`, so the waited
handle is not the stop event. `ProductionStart` copies `[thread+0x18]` to
`document+0x61d8`. `ProductionStop` waits on that copy with timeout zero
before calling `Stop`. The constructor store of that field is in the same
zeroed `r14` span as `+0x5838`. Those are the only three instructions that
use displacement `0x61d8`. Close and destruction do not. It passes timeout zero. After that join it also stops the
other `CViThread` at `document+0x3860`. `ProductionStart` allocates that
object with size `0x48`, constructs it at `0x14067c320`, and stores it at
`+0x3860` before the producer store at `+0x3868`. Vtable `0x140ea1cd0` slot
`+8` is the communication handler `0x14067c480`. It waits with `WaitForMultipleObjects` on the three handles at `this+0x18`, `this+0x40`, and `this+0x38`. The wake that calls `0x14067c7b0` ends in `ReleaseSemaphore` on `[document+0x3890]`. `ProductionStart` passes its document as the constructor's second argument, and the constructor stores that pointer at `+0x20`. The handler, both wake functions, and the three direct callees of `0x14067c7b0` do not call `ProductionStop` or `AskToStop`, and their bytes do not mention `+0x3868`. `OnCloseDocument`, the
document destructor, view `WM_DESTROY`, the close poster, and the `0x52c`
handler do not mention `+0x3860`. Slot `+0x10` of the vtable stored at
`document+0x2548` is `0x140680d70`. That method stores null at
`[this+0x1320]`, which is `document+0x3868`, and then stops `[this+0x1318]`,
which is `document+0x3860`. It does not stop the pointer it clears. The view
command handler forms that object's address at `0x1406b1039` and calls slot
`+8`, not slot `+0x10`. While Stop returns anything other than
1 it calls `0x1405e8af0(0x1f4)`, which peeks, translates, and dispatches queued
messages, then sleeps 10 milliseconds, repeating for the argument divided by
10. After that loop it stores zero at `+0x3868`. Only then, and only when
`document+0x3881` is 1, it calls `ProductionStart`. The other direct callers
of `ProductionStart` are `0x1406b0fc6` and `0x14075ef33`.
`ProductionStart` itself compares `document+0x3868` with zero at
`0x140691e88`. The occupied side jumps to `0x1406920b9`, clears the return
byte, and returns without calling `ProductionStop` and without replacing the
pointer. The store of the new thread is on the empty side only. Neither
`OnCloseDocument` nor the document destructor calls
`ProductionStop`, `BP_ProductionStop`, or `0x140680c00`. The notification
handler `0x14068da40` is document vtable slot `+0x28` and the only direct
caller of `ProductionStop`. The other 82 slots of document vtable `0x140ea3868`
do not call it, and none of the 113 slots of production-view vtable
`0x140eac650` calls `ProductionStop`, `AskToStop`, or that handler. The call runs only when the high 16 bits of `r8`
are `0x4e` and the low 16 bits are `0xb1cf`. The address of `ProductionStop`
is not stored as a pointer in the image. `OnCloseDocument`, the document
destructor, view `WM_DESTROY`, the close poster, and the `0x52c` handler do
not call that slot. Document close therefore does not join
this producer before it destroys the view. A failed Stop attempt can also
dispatch a SKIP message while Handler is still running. No callback-retirement
gate is promoted.

`AskToStop` is slot `+8` of the vtable stored at `document+0x2548`
(`0x140ea3b58`), not a primary-document slot. Called on that subobject, it
sets byte `+0x12e6`. That is document byte `+0x382e`. It then posts
`WM_NOTIFY` (`0x4e`) with code `0xb1cf` and returns. The only other memory operand using displacement `0x12e6` is
`StartProductionWithThread` clearing it.
`ProductionStart` clears the same document byte through displacement `0x382e`.
The only other instructions that use displacement `0x382e` compare it with 1:
the production cycle, and `0x1406af56e`. That second compare's function is
called from the view command handler immediately after slot `+8`. Its equal
side tail-jumps MFC ordinal 4326. It does not call `ProductionStop`.
Four initialization stores also cover that byte, and each source register is
still zero: dword stores at `0x14065bd0b`, `0x14065bee2`, and `0x14065f368`,
and the constructor word store at `0x14067e17b`.
`HandlerProduction` compares `document+0x382e` with 1, sets
`CProductionThread+0x32`, and returns to the cycle head while that thread byte
is zero. The child frame's recorded base map inherits `WM_CLOSE` handler
`0x1802a2aa0`. That handler calls document slot `+0x1b8`, MFC ordinal 2660,
and then slot `+0x118`, `OnCloseDocument`. Ordinal 2660 tests a view dword at
`+0xec` or calls slot `+0x1c0`. It does not read `+0x382e` or `+0x3868`.
`OnCloseDocument` does not contain those displacements. `HandlerProduction` calls slot `+8` on the accessor result at
`0x1406a4685` only after `thread+0x32` is nonzero. The zero side jumps
to the cycle head `0x1406a2770`. That exit does not call `ProductionStop`.
`CheckAvailableMemory` `0x14069c770` can reach the same call without
`document+0x382e` already being 1. A zero return loads the dword at
`0x1411697c4`. That address is in the zero-filled tail of `.data`, and
both instruction uses are reads, so the failure stores word `0x100` at
`thread+0x31` and jumps to `0x1406a466d`. Close, destruction, view
`WM_DESTROY`, the close poster, the `0x52c` handler, and their direct
callees do not call `0x14069c770`. The stack byte at `[rbp+0x770]` is
cleared on each pass and passed to app slot `+0x58`. That slot is MFC
ordinal 7430, whose body is `mov eax, 0x80029c4a; ret`, so it does not
store the flag. The other calls of that slot on an object addressed with
`+0x2548` are in `0x1404c2640`, `0x140682ff0`, `0x1406a1da0`,
and `0x14075efd0`. `0x1405cb880` is the `CDocCompose` constructor. It stores
vtable `0x140e76370` at `+0x2548` and passes that address to slot `+8` of
`[this+0x19e8]`. Slot `+8` of the stored vtable is `0x140611ce0`, not
`AskToStop`. `CCAPM` secondary slot `+0xb0` is thunk `0x14075dee0`, which adds
`0x10` to `this` and jumps to `0x1404c7580`. When the vector at `this+8` holds
at least two `0x80`-byte elements, that function calls `0x1404c2640`. That
function calls slot `+8` at `[r13+0x2548]` when `ebx` is 4. The only instruction that takes the address of `0x140682ff0` is the `lea` in `0x14068d550`. Its only direct caller is `HandlerProduction`. That function stores the address in a callable whose manager pointer has its low bit set, then passes the callable to `CAsynchCommandExecution::EnqueueCommand` on `document+0x6128`. `0x140682ff0` calls slot `+8` at `[rbx+0x2548]` when dword `[rbx+0xe18]` is 1. The document destructor calls `Kill` on `document+0x6128`. `Kill` calls a queued manager only when that pointer's low bit is clear, so this registration is not called. `OnCloseDocument`,
the document destructor, view `WM_DESTROY`, the view destructor, the `0x52c`
handler, and the close poster do not call slot `+0xb0`. Close, destruction, view `WM_DESTROY`, the close poster,
and the `0x52c` handler do not call those functions, and neither do their direct callees. `0x14075efd0` is `CCAPM` secondary vtable slot `+0x1c8`. It calls `AskToStop` only after slot `+8` at `[this+0xf0]` returns a value greater than 6. The function has no direct caller. `OnCloseDocument`, the document destructor, view `WM_DESTROY`, the view destructor, the `0x52c` handler, and the close poster do not contain displacement `0x1c8`. Close can destroy the
view while `HandlerProduction` is still in the cycle. The callback-retirement
gate is not promoted.

`OnCloseDocument` calls `0x1404e03f0` and then tail-jumps to MFC ordinal 8850.
The helper posts message `0x52c` with wParam 6, or returns without posting when
byte `+0x830` is already 1. The production view binds `0x52c` to `0x1406b0c00`,
whose switch index is wParam minus one. wParam 6 therefore enters `0x1406b1232`.
That arm does not call `AskToStop` or `ProductionStop`. When `0x140697ce0`
returns true it sends `WM_COMMAND` `0xe102`, and the document handler for that
command jumps through slot `+0x118` back to `OnCloseDocument`. The switch arm
that calls `AskToStop` is wParam 2, at `0x1406b0fec`. Command `0xb1ce` enters
the same switch with edx 1. The posted close message is not a producer join,
and the MFC close jump runs before that handler. The callback-retirement gate
is not promoted.

The command that reaches that wParam 2 arm is control id `0xb1cf` on a
`BUTTON` child of the `PROD_VIEW_COMMAND` window. The production view
constructor `0x1406ab570` builds that object at `view+0x9c8` and stores vtable
`0x140e9f7a0`. Three view methods call `0x1406ac880` and pass the view.
`0x1406ac880` calls slot `+0xb8` with style `0x50000000`, class `PROD_VIEW_COMMAND`, and the view
as the parent argument. Slot `+0xb8` jumps to MFC ordinal 3165. In the supplied
MFC 14 DLL that ordinal reads argument 5 as a `CWnd`, takes its `+0x40` HWND,
and sets style bit 30 (`WS_CHILD`). The command window's `WM_CREATE` handler
`0x140677b70` calls `0x1406770b0`, the only direct caller of that helper. The
helper calls slot `+0x2d8` on the child at `+0x1aa8` with the command object as
parent and id `0xb1cf`. That slot is MFC ordinal 3051. It forwards the same
parent and id into the object's slot `+0xb8`, which is ordinal 3165 again, and
the class string it supplies is `BUTTON`. The command map then binds
`WM_COMMAND` `0xb1cf` to `0x140677b30`, which calls `GetParent` and posts
message `0x52c` with wParam 2 to that parent HWND. `.text` contains the
immediate `0xb1cf` only at this button create, at `AskToStop`'s notify store,
and at the document `OnCmdMsg` compare. Close does not call the button create
and does not load the command. The callback-retirement gate is not promoted.

The direct-call closure of `OnCloseDocument`, the document destructor,
production-view `WM_DESTROY` `0x1406af270`, helper `0x1404e03f0`, and document
`OnCmdMsg` does not include `AskToStop`, `CProductionThread::Handler`,
`HandlerProduction`, the command poster `0x140677b30`, or the `CCAPM` function
`0x1404c2640`. `OnCmdMsg` is the only function in that closure that calls
`ProductionStop`. The destructor stores vtable `0x140ea3b58` at
`document+0x2548`; slot `+8` of that vtable is `AskToStop`, and the destructor
does not call it. Its later `call [rax+8]` uses the object at
`document+0x5878` with edx 3. The callback-retirement gate is not promoted.

That direct-call closure misses one virtual call inside production-view
`WM_DESTROY`. After MFC ordinal 2207, destroy calls `__RTDynamicCast` on
`[result+8]`, from `.?AVCWinApp@@` to `.?AVCAVisionApp@@`. The
`CAVisionApp` constructor `0x1404cdff0` stores vtable `0x140e39770` and
constructs `CCAPM` at `+0x1a8` through `0x14075aa80`. Destroy then calls
slot `+0x198` of the secondary vtable at `CCAPM+8` (`0x140eddbd0`), which
is `0x14075d6b0`. That function calls slot `+0xe0` (`0x14075d010`) with
edx equal to the dword it read from the view's document at `+0x3924`.
The slot indexes the pointer vector whose begin and end are
`[CCAPM+8+0x2e8]` and `[CCAPM+8+0x2f0]`. When the indexed pointer is null,
or dword `[entry+0x3928]` is not 4, it calls `0x140611a10` on
`CCAPM+0x278`. The wrapper adds 8 and calls `0x1406109f0`. That callee
takes `EnterCriticalSection` on its `+0x20`, updates a pointer vector at
`+8`/`+0x10`, returns `(end-begin)/8`, and leaves the same critical
section. Its body contains neither displacement `0x2548` nor immediate
`0xb1cf`. The direct-call closure of `0x14075d6b0` includes both helpers
and does not include `AskToStop`, `ProductionStop`, `0x1404c2640`, or
`HandlerProduction`. The callback-retirement gate is not promoted.

That vector update is not the path taken for destroy's own arguments when
the indexed entry exists and `[entry+0x3928] == 4`. Destroy stores the
document dword `+0x3924` at argument `+8` and the constant `0xb` at argument
`+0xc`. `0x14075d6b0` copies `+0xc` and, on that status, builds two local
lists. The second list contains 3 and `0xb`. A match frees both lists and
jumps to `0x14075db5a`, which is after the call to `0x140611a10`. The
callback-retirement gate is not promoted.

After the `CCAPM` call returns, destroy calls document slot `+0x230`.
The production-document vtable `0x140ea3868` binds that slot to
`0x14045c520`, which returns `[this+0x19e8]`. `CProductionDoc::SetProductionVMC`
stores the current or lane `IVMachineController` from `CVMC_ListSingleton`
at that field. When the pointer is non-null, destroy calls its slot `+0x10`
with `view+0x160`. The production-view constructor installs vtable
`0x140eac9e0` there. The locator names `CProductionView` at offset `0x160`,
and the base list includes `IVMachineControllerListener` at that
displacement. Initial update `0x1406af770` calls the same getter and then
slot `+8` with `view+0x160` before it stores the view at `document+0x5838`.
Six listener slots are `xor al, al; ret`. Slot `+0x18` calls MFC ordinal
1032 and returns false. Slot `+0x20` calls `0x1405586b0` and returns false.
Slot `+0x40` stores `r8d` at listener `+0x58` and returns true. The qword
after that slot is the string `ProductionView`, so it is not another code
pointer.
The direct-call closure of those listener bodies does not include
`AskToStop`, `ProductionStop`, or `HandlerProduction`, and the bodies do
not contain displacements `0x2548` or `0x382e` or immediate `0xb1cf`.
`ViVirtualMachine.dll` implements the controller methods.
`ViVirtualMachineBuilder.dll` is AMD64, version `70.06.59.00`, size 1,013,248 bytes, SHA-256
`5e808e294d1f19fa7b8bd5e2d994d4820963d5c1fdea064e572457c9597679b7`,
preferred base `0x180000000`, and it has no Authenticode signature.
`BuildVM` allocates the controller and tail-jumps
`ViVirtualMachine.dll!CVMachineController::CVMachineController(unsigned int)`.
The implementation DLL is the same version and base, size 1,144,320 bytes,
SHA-256 `5b62adea102b62a272860bfba72cb787bf74bd006f44fe97453df5121efeeb60`,
and it is also unsigned. Neither file was loaded or executed. Its constructor
stores vtable `0x1800ceda8` at offset 0. The locator names
`CVMachineController` at offset 0, and the exported slot is the
`IVMachineController` base. Slot `+8` is `Attach`. Slot `+0x10` is the shared
subject `Detach`: under the critical section at `this+0x20` it scans the
pointer vector at `this+8`, removes the listener with `memmove`, and returns
whether an entry was removed. Its only calls are `EnterCriticalSection`,
`memmove`, and `LeaveCriticalSection`. `Attach` also inserts the listener
and then queues `QueueUserWorkItem`; destroy calls `Detach`, not that queue.
This does not join `CProductionThread`. Initial update zeroes the ten
pointers at `view+0x60b0` through `view+0x60f8`, allocates 0x10 bytes for
each, and constructs them with `mfc140.dll` ordinal 357. That export is
`CBrush::CBrush(COLORREF)`: it zeroes the handle at `+8`, stores the
`CBrush` vtable, and calls `gdi32.dll` `CreateSolidBrush`. Six colors are
immediates and four come from `user32.dll` `GetSysColor`. Destroy walks
the five pointers at `view+0x60b0` and the five at `view+0x60d8`. For a
non-null pointer it calls slot `+8` with edx 1 and then stores zero. Slot
`+8` is the scalar deleting destructor. edx 1 takes the non-vector branch,
calls the `CGdiObject` destructor, and then calls CRT `free`. That
destructor unlinks the handle from the thread GDI map and tail-jumps
`gdi32.dll` `DeleteObject`. The direct-call closure imports no `user32.dll`
entry. After the brushes, destroy calls `KillTimer`, the controller detach
above, `CView` teardown ordinal 9117, and frees its local list through
ordinal 1032 and ordinal 1487. Ordinal 1487 jumps to CRT `free`. None of
these calls is `AskToStop` or `ProductionStop`. The callback-retirement
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
`0x1406af270`, with no own `WM_NCDESTROY` entry and no `WM_CLOSE` entry.
`WM_SIZE` selects thunk `0x14078055e`, MFC ordinal 11222. That body calls
`0x18028f370` and both of its tails stay inside `mfc140.dll`. `WM_ERASEBKGND`
selects `0x1406af450`, which does not call `ProductionStop` or `AskToStop`
and does not mention `document+0x3868`. Message `0x87d0` selects `0x1406b0710`.
That handler loads the document from `view+0xe8` and compares `document+0x382d`
with 1. Its direct calls and the `edx` 7 and 8 arms, which tail-jump
`0x140742500` and call `InvalidateRect`, do not call `ProductionStop` or
`AskToStop`. The call through `[view+0x60a0]` is `ccSemaphore::lock` at slot
`+8` and `ccSemaphore::unlock` at slot `+0x10`. The call through
`[view+0x4c10+0x120]` is `CDPoint` slot `+0x10`, which copies two qwords from
its argument and returns. Message `0x113` selects `0x1406b1f20`. Timer id 1
loads the document from `view+0xe8` and calls `ccSemaphore::lock`. That arm
does not call `ProductionStop`. View vtable slot `+0x328` is
`CProductionView::OnInitialUpdate` at `0x1406af770`. It calls `SetTimer` for
ids 1 and 8 before it compares `document+0x382d` with 0. The not-equal side
jumps to a null check of `view+0xe8`. Neither side calls `ProductionStop`. `WM_DESTROY` calls `KillTimer` with id 5.
`OnCloseDocument`, the document destructor, and the view destructor do not
call `KillTimer`. The retained `+0xe0` thunk
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
`0x18027ef90`. Its first conditional call is `CCadEngine::StopEngine` on `view+0x170`. That function posts message `0x12` to the `CCadEngineThread` at `engine+0x138` and waits on that object's `+0x58`. `StartEngine` allocates the thread, and MFC ordinal 3529 stores the `_beginthreadex` handle at `+0x58` and the thread id at `+0x60`. `StopEngine` then calls that thread's slot `+8` with edx 1 and stores null. The handle is not `document+0x3868`. Ordinal 1125 then calls the engine's slot `+0` with edx 1. The function does not call `ProductionStop` or mention `document+0x3868`. Its direct callees that have exception entries do not either. Three thunks follow the temp-path calls. With `edx` zero, ordinal 12215 calls `DeleteFileA`. Ordinal 1421 runs on `view+0x6f18` and can call `DestroyWindow` on that member's `+0x40`. Ordinal 1425 frees the pointer at `[view+0x6ec8]+8`. The later `lock xadd` releases `view+0x1b0`. None of those fields is `document+0x3868`. The retained base destructors continue through `0x18028c620`
to `0x18027bf00`; the latter calls `0x18021fae0(document, view)` at
`0x18027bf84` when `view+0xe8` is nonzero. That body and its direct calls
contain no store of `document+0x5838`. The deleting wrapper `0x1406abf00`
calls this destructor and then, when edx bit 0 is set, frees the view
through ordinal 1487. `RemoveView` clears `view+0xe8` and leaves the
document's published view pointer in place. The producer reloads that
pointer from the still-published document. CAD-engine stop is not proof of
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
	destructor do not call that stop. The message `OnCloseDocument` posts
	before MFC close is `0x52c` wParam 6, and that arm does not call
	`AskToStop` or `ProductionStop`. The wParam 2 arm is reached from
	`WM_COMMAND` `0xb1cf` on the `PROD_VIEW_COMMAND` child, whose button uses
	that id. Close does not call that button's create and `.text` has no other
	immediate `0xb1cf`. The direct-call closure of close, destroy, the
	destructor, and `OnCmdMsg` does not reach `AskToStop`. The destructor
	stores the `AskToStop` vtable at `+0x2548` without calling slot `+8`.
	Production-view `WM_DESTROY` does call `CCAPM` slot `+0x198`
	(`0x14075d6b0`) on `CAVisionApp+0x1b0`. That path indexes a `CCAPM`
	pointer vector and, on the ordinary tail, updates a locked vector in
	`0x1406109f0`. Neither that function nor the direct-call closure of
	`0x14075d6b0` calls `AskToStop` or `ProductionStop`. Destroy's code
	is the constant `0xb`. When the indexed entry exists and
	`[entry+0x3928] == 4`, that code matches the function's second list
	and the vector update is skipped. Destroy then calls
	`IVMachineController` slot `+0x10` with the
	`IVMachineControllerListener` subobject at `view+0x160`. Initial
	update calls slot `+8` with the same subobject before publishing
	`document+0x5838`. The listener methods in this executable do not
	call `AskToStop` or `ProductionStop`. Slot `+0x10` of the constructed
	`CVMachineController` is a listener `Detach`: it unlinks the pointer
	under `this+0x20` and does not call `AskToStop` or `ProductionStop`.
	The implementation is in `ViVirtualMachine.dll`; the builder DLL only
	forwards the constructor. The ten pointers at `view+0x60b0` through
	`view+0x60f8` are `CBrush` objects from `mfc140.dll` ordinal 357.
	Destroy calls their slot `+8` with edx 1, which deletes the GDI brush
	and frees the object. It does not call `AskToStop` or `ProductionStop`.
	A null HWND is a thread message. The application map has no entry
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
- Shared synchronization for SKIP refresh and reset is absent. `0x14067ab20` and
	`0x14067a420` are called only from refresh `0x1406adaf0`, around `SkipList_Get`.
	The five reset callers do not call them. `CDataCao::~CDataCao`'s direct-call
	closure imports no `user32`. `SkipList_Reset` passes the array at
	`document+0x23e0` to `mfc140.dll` ordinal 13522 with size 0 and grow-by -1.
	That ordinal's zero-size path calls `free` on the data pointer and stores
	zero at `+8`, `+0x18`, and `+0x10`. It does not enter a critical section.
	The negative-size branch is what reaches the throw. Refresh still reloads
	`[array+8]` and `[array+0x10]` on the live object. Its direct-call closure
	and the reset callers both enter critical sections in `0x140780a98`,
	`0x140780af8`, and `0x140780bbc`; those helpers do not call
	`SkipList_Reset`. The reloads remain in refresh, after the string-list call.
	Reset also enters the critical section in `0x140578c80`, which refresh does
	not reach. Those three shared helpers enter a global section, update
	thread-local state, and leave before returning, so they do not cover the
	reload. `HandlerProduction` posts `0x87d6` at `0x1406a27fa` and calls
	`SkipList_Reset` at `0x1406a2d87` with no wait, send, or critical-section
	import between those addresses. The only `.rdata` entry for `0x87d6` selects
	`0x1406b2320`, whose direct-call closure contains neither refresh nor
	`SkipList_Reset`. `0x1406a2b79` does call `0x140685b70` before the reset.
	That function sends the id in `0x141193470`, registered from
	`{5D5B3537-9C21-4d59-AEB5-EA30A0D68618}`. The skip GUID's only value loads
	are `PostMessageA` at `0x1406a1031`, `0x1406a106b`, and `0x140736fe1`.
	The send's direct-call closure contains neither refresh nor `0x1406b0700`.
	`0x1406a2b81` calls `0x1406a9db0` on every fall-through toward the reset.
	That function calls slot `+0x30` of `[thread+0xeb8]`. The only store of
	that field is the second argument of `0x1406999f0`, and its only caller
	passes the return of document slot `+0x230`. Controller vtable
	`0x1800ceda8` binds `+0x30` to `0x180070ed0`, a read of
	`[[controller+0x860]+0x10]`. The default arm waits on `thread+0x18` and
	`thread+0x1a8` for 10 milliseconds with `bWaitAll` clear. The body does
	not import `SendMessageA`, `PeekMessageA`, or `DispatchMessageA`, and its
	direct-call closure contains neither refresh nor `0x1406b0700`.
	Close still does not join the producer.
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