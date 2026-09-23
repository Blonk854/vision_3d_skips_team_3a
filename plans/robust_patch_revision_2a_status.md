# Robust Patch Revision 2a - Implementation Status

Recorded: 2026-09-22

## Current decision

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

Latest offline checkpoint, 2026-09-23: **57 tests pass in 34.379 seconds**.
In addition to local cleanup coverage, 20 release/deletion cases pin mutation
before deletion, repeated-release risk, storage-helper failure boundaries, and
an ignored semaphore failure. The immediate dispatcher and receiver have no
local catch. These are regression evidence for unresolved failure handling, not
a passed exception gate; see [slot retirement](#synchronous-slot-retirement-and-caller-unwind-2026-09-22).

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
| Final-mask hook multiplicity / result uniqueness | Partial | Synchronous and worker-thread callers of the zone executor are now traced; retries, reinspection, indirect callers, and uniqueness remain unproved. See the new entry-gate evidence below. |
| Worker drain before CAPM reconciliation, supported single lane | Blocked: callback and exception containment | The stock unchecked `CreateEventA`/`WAIT_FAILED` path remains defective, but the startup-only synchronous candidate makes it unreachable from every retained executable caller on the supported lane. The export-thread descendant copies its payload before return and does not retain CAO/result pointers. Existing work, the posted UI callback, exception handling, and remaining ownership before release or reuse remain unproved. |
| Production/anomaly vector ownership and immutability | Partial | Layout and consumers are mapped; all writers, destructors, reallocators, owner, and synchronization are not established. |
| No late callbacks after CAO retirement | Blocked: live-storage dependency established | The export worker owns copied value records. The posted SKIP receiver reads the live array at `CAO+0x23e0` through production-view `+0xe8`. Bounded emulation confirms dispatch-time reads, a fault with artificially unmapped storage, and exception/fault paths during modeled reset without CAO destruction. Actual mutation/retirement synchronization and pending-message ordering remain unproved. |
| Reset before reuse of the same CAO pointer | Not found | Reset callers are mapped, but allocation, pooling, destruction, and next-panel reuse ordering are not connected. |
| DWORD arithmetic at supported workload maximum | Partial: bound only | Exact product bounds and a wraparound counterexample are recorded; no supported/enforced workload maximum proves overflow cannot occur. |

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
slot `+8`, and Handler then calls MFC ordinal 2175, which tails to
`_endthreadex`. `ProductionStart` stores this object at document `+0x3868`.
`ProductionStop` is the only direct caller of `CViThread::Stop` on that
field. Each attempt uses timeout zero. A result other than 1 calls
`0x1405e8af0(0x1f4)`, which dispatches queued messages and sleeps before
retrying, so a failed attempt can deliver SKIP while Handler is still
running. `OnCloseDocument` and the document destructor do not call
`ProductionStop`. Document close therefore does not join this producer
before view destruction. The callback-retirement gate is not promoted.

Stop flag, 2026-09-23: the cycle leaves its head only when
`CProductionThread+0x32` is nonzero. `HandlerProduction` sets that byte after
it sees document `+0x382e == 1`. `AskToStop`, slot `+8` of the vtable at
`document+0x2548`, is the only writer of 1. Initialization dword and word
stores cover the byte with a register that is still zero. AskToStop addresses
the byte as subobject `+0x12e6`, posts notification `0xb1cf`, and returns. The inherited
`WM_CLOSE` handler `0x1802a2aa0` calls MFC ordinal 2660 and then
`OnCloseDocument`. Ordinal 2660 does not read the flag or `+0x3868`, and
`OnCloseDocument` does not contain either displacement. Stock close still
does not ask the producer to leave, and does not wait for it. The
callback-retirement gate is not promoted.

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
  The producer leaves the cycle only after `AskToStop` sets document
  `+0x382e`. `WM_CLOSE` reaches `OnCloseDocument` through MFC ordinal 2660
  without setting that byte or joining `+0x3868`.
5. Native target traces for duplicate delivery, delayed workers/callbacks, vector
  identity, CAPM entry, retirement, and immediate reuse are optional under
  W7-QUAL-01. Retain available offline cases and record native gaps as unverified.
6. Document and enforce a supported workload maximum or widen threshold arithmetic.

Only after the remaining non-waived implementation contracts are satisfied should
`tools/patch_f1_missing_n_rev6.py` be created from rev5 and the assembly/state/ownership
changes begin. Do not block that decision solely on the unavailable target
qualification covered by W7-QUAL-01.