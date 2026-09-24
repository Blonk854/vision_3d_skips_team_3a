# Revision 2a Entry-Gate Evidence

Recorded: 2026-09-21. Static saved-project and source-PE evidence only. Rev6 remains blocked.
The stock executable, active Ghidra project, rev5 reference, and live installation
were not modified. No Vision3D process or station workload was executed.

## Worker-drain finding

The candidate barrier is now identified, but its Boolean success return is **not
sufficient evidence of worker drain**. Stock `CThreadPool::WaitEndOfAllThreads`
at `0x1406a9a80` treats `WAIT_FAILED` as success. This is confirmed in extracted
instructions whose bytes match stock, not just inferred from a log message.

| Address | Verified operation |
| --- | --- |
| `0x1406a9b68` | `WaitForMultipleObjects`, wait-all, batches of at most 64 handles |
| `0x1406a9b6e` | Preserve the wait result in `R15D` |
| `0x1406a9b73` | Any nonzero result exits the wait loop |
| `0x1406a9b9a` | Close each recorded completion handle, including after unsuccessful wait |
| `0x1406a9bbb` | Call the recorded-handle array resize helper with size zero |
| `0x1406a9bc0` | Compare the preserved result only against `0x102` (`WAIT_TIMEOUT`) |
| `0x1406a9bc7` | Every other result branches to the success path |
| `0x1406a9bf8` | Set Boolean return to 1 |

Thus `WAIT_FAILED` (`0xffffffff`) is not distinguished from successful drain at
the function boundary. The timeout path reports failure, but also closes the
recorded completion handles. Closing an event handle does not join its worker.
These observations do not prove that invalid handles or timeouts occur in a
supported workload; they disprove using the Boolean alone as a universal drain
contract. The follow-up below establishes a concrete unchecked event-creation
failure path. Its occurrence on a station and system-level containment remain
unproved.

## Controlling call chain

Names below come from saved symbols or function-local log strings. Addresses
and direct call sites are retained independently of those names.

1. `HandlerProduction` (`0x1406a20d0`) calls `PanelInspect` (`0x1406a6a30`)
   at `0x1406a39ea` on the successful first-pass branch.
2. `PanelInspect` calls `ReceiveGreyZones` (`0x1406a88e0`) at `0x1406a701f`.
3. `ReceiveGreyZones` calls the pool wait at `0x1406a928c`, using the pool at
   production-thread `+0xec8`. This call is conditional on byte `+0xf58 == 1`
   and strategy DWORD `+0x17e8 != 2`; it is not an unconditional barrier.
4. A false pool-wait return sets the receive result to 2. `PanelInspect` preserves
   failure for receive result 2; other receive results can reach its success path.
5. `HandlerProduction` later calls CAPM (`0x14069b2a0`) at `0x1406a448f`.
   Its result-code branch `(result & 0xfffffffd) == 0` bypasses the CAPM block.
   The other branch includes a path that copies document `+0x5c9c` to `+0x5c98`
   and logs reuse of current result data before CAPM. Stop/error and reused-slot
   paths must be evaluated, not assumed equivalent to a successful new panel.

`HandlerProduction` has no direct Windows wait call in this extraction. The
communication waits inside CAPM occur after the review hook, as previously
documented in [review-station-handoff.md](review-station-handoff.md), and cannot
establish pre-reconciliation worker drain.

## Producer-side evidence

- `ExecuteGreyZoneAsynchronous` (`0x14069fb80`) obtains a worker from
  `GetThread` (`0x1406a1660`) or falls back to synchronous execution.
- `GetThread` creates an initially nonsignaled auto-reset event, appends it to
  the pool completion-handle array (`+0x68`, data `+0x70`, count `+0x78`), and
  assigns it to selected worker `+0xb8` under pool critical section `+0x40`.
- Dispatch writes worker zone ID/pointer at `+0x50/+0x58`, then signals worker
  `+0xa0` under its critical section `+0x78`.
- Worker `CProcessingGreyZoneThread::Treat` (`0x14066db40`) and synchronous
  `ExecuteGreyZoneSynchronous` (`0x14069fcd0`) both call the zone executor
  (`0x140735f10`), which calls `ExecuteAll_Components` (`0x1407354b0`).
- Their common post-execution helper (`0x14066d9e0`) is
  `CSDM<CZoneStorage>::SafeSlotRelease`. It is not itself proof that the worker
  completion event was signaled or that all callbacks have finished.
- `Treat` has a data reference at `0x140ea8a28` and no recorded direct call in
   the initial extraction. The follow-up resolves that virtual dispatch and the
   normal-return signal of worker `+0xb8`.

This narrows the multiplicity graph but does not prove unique results: retries,
section overlap, alternate dispatch, indirect callers, and reinspection remain
open. Handler reset call `0x1406a2d87 -> 0x140541050` is identified; allocation,
retirement, callback drain, and pointer reuse are still not connected.

## Follow-up: completion signal and failed-wait continuation

The stock constructor `0x140699970` installs vtable `0x140ea8a10` at
`0x140699996` / `0x14069999d`. Reading the stock PE's little-endian pointers
establishes slot `+8` (`0x140ea8a18`) as `0x1406a1a50` and slot `+0x18`
(`0x140ea8a28`) as `Treat`, `0x14066db40`. Pool construction at `0x1406a99d0`
calls this constructor and records each worker's availability event at `+0xa8`.
The base constructor `0x1406997d0` creates the work/availability events and calls
`CViThread::Start`. Dynamic vtable replacement and all runtime instances have not
been enumerated; this is the concrete construction path, not a global invariant.

`CViThread4Pool::Handler`, `0x1406a1a50`, provides the missing normal-return edge:

| Address | Verified operation |
| --- | --- |
| `0x1406a1b6f` | Wait-any on worker work event `+0xa0` and stop event `+0x18` |
| `0x1406a1be4` | Require running byte `+0xb0 == 1` before treatment |
| `0x1406a1c09` | Invoke vtable slot `+0x18`, bound above to `Treat` |
| `0x1406a1c0c` | Preserve treatment result separately in `EDI` |
| `0x1406a1c0f` | Load completion handle from worker `+0xb8` |
| `0x1406a1c16` | Call `SetEvent`; its return value is not checked |
| `0x1406a1c24` | Test the treatment result for logging, after signaling |
| `0x1406a1c51` | Signal availability event `+0xa8`, then loop or exit |

For a valid completion event and a normal `Treat` return, signaling occurs after
the synchronous zone-execution call stack returns. This is useful ordering
evidence, but does not establish that separately queued callbacks have completed.
Completion is signaled for a false treatment result too; it is not a success
status. Stop or work-wait failure clears `+0xb0`, bypasses treatment/completion
signaling, signals availability, and exits. Exceptional unwinding through `Treat`
has not been proved to signal or contain outstanding work.

### Concrete failure chain

Assume event creation fails, a previously initialized worker is available, array
growth and other intervening calls return normally, and asynchronous dispatch
plus the final pool wait are selected:

1. `GetThread` calls `CreateEventA` at `0x1406a1701`; its result is preserved in
   `R12` at `0x1406a1707` without a NULL check.
2. Availability is checked independently. On a valid worker index, `R12` is
   passed to array helper `0x140620730` at `0x1406a176c`. That helper validates
   the array index/capacity, not the handle, then stores the supplied value.
3. The same unchecked handle is assigned to worker `+0xb8` at `0x1406a17a5`.
   `GetThread` returns a worker pointer, so asynchronous dispatch does not take
   its no-worker synchronous fallback. Work can run with NULL as its completion
   handle; the worker's later `SetEvent(NULL)` cannot establish completion.
4. The final wait encounters the NULL entry and fails. Stock pool cleanup clears
   the tracked handle array and the non-timeout return path reports true.
5. At `0x1406a9291` / `0x1406a9293`, `ReceiveGreyZones` tests this true return
   and skips the failure assignment at `0x1406a92ab`. If no other receive error
   occurred, its result remains 3. Panel inspection and the handler therefore
   retain a success route toward CAPM, subject to their other branches.

This path does not require a stale handle or speculative concurrent deletion.
It does require a real API allocation failure, which has not been induced in
Vision3D. It establishes that the inspected producer/waiter/caller chain does not
reject that failure before proceeding; it is not a trace of a station incident
or proof of a particular worker/CAPM race schedule.

Microsoft's [CreateEvent contract](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-createeventa)
specifies NULL on failure; the [wait contract](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitformultipleobjects)
defines `WAIT_FAILED`, and the [SetEvent contract](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-setevent)
specifies zero on failure. A standalone CPython 3.14.5 `ctypes.WinDLL` probe on
this Windows host confirmed:

- One owned, initially signaled event, wait-all with timeout zero: result `0`.
- One NULL handle, wait-all with timeout zero: result `0xffffffff`, last error 6.
- `SetEvent(NULL)`: result zero, last error 6 (`ERROR_INVALID_HANDLE`).

The probe set explicit Win32 signatures, used `use_last_error=True`, checked the
results with explicit failures, and closed its sole owned event in `finally`.
It did not load Vision3D, exhaust resources, inject faults into another process,
or exercise stock exception handling. Timeout still returns failure along the
inspected receiver path; that does not prove worker cancellation or safe reuse.

## Bounded containment follow-up

The user approved read-only investigation beyond the five feature hooks on
2026-09-21. This did not authorize new patch sites, implementation, target
execution, or forced termination. Four additional function bodies were extracted
without changing the extractor or saved project.

### Failure cleanup is not storage preservation

For result 0/2 at its result-code branch, `HandlerProduction` calls
`0x1406719a0` at `0x1406a44e2` (`e8b9d4fcff`). The argument is the document's
current result slot: `[document+0x5878] + sign_extend([document+0x5c9c])*0x410`.
The same helper is called at cycle start (`0x1406a2db4`). Its body resets flags,
zeroes entries, resets several end pointers, and invokes `CMemBuffer::DeleteBuffer`
and `CAnomalieProd::ImgSapinNoel_Clear` for contained anomaly records.

Thus the error path performs substantive result cleanup, not merely UI
suppression. Correcting the wait Boolean alone is not proof of preserving
resources while workers remain outstanding. Intervening indirect operations,
exact aliasing to each worker, and runtime schedules remain unresolved; no
use-after-free or station race is claimed as an observed fact. A result changed
to 2 later inside the CAPM branch can still reach CAPM, so this is not a claim
that every occurrence of status 2 bypasses CAPM.

### Pool destruction is not an established containment primitive

Pool resizing calls `0x140655980` at `0x1406a99f7`. That cleanup loops over
worker pointers, invokes each virtual deleting destructor, then closes recorded
completion handles and clears their array. Its saved direct callers do not
include the inspected receiver or production handler; error-path reachability
and exclusion of concurrent admission remain unproved.

The retained derived destructor `0x14069a890` has this verified order:

| Address | Operation |
| --- | --- |
| `0x14069a8ab` | Call `0x1406aac40` on worker `+0xc8` |
| `0x14069a8b7` | Delete the container head pointer at worker `+0xc8` |
| `0x14069a8bf` | Call base cleanup `0x14069a110` |
| `0x14069a13d` | Base calls through `0x140d53470`, saved symbol `BASETOOLS.DLL::CViThread::Stop` |
| `0x14069a150`, `0x14069a16e` | Base closes non-NULL work and availability handles |

Helper `0x1406aac40` unlinks the container, releases reference-counted values
(including virtual disposal on last references), and deletes nodes. This release
occurs before the base stop call. Whether those values alias active treatment
resources is unresolved; destruction cannot be certified as stop-before-release.

The base passes the worker, a zero-initialized output DWORD, and third argument
`0xffffffff`. After normal return it checks neither the return register nor that
output before closing handles. At this stage the external body was unresolved;
the supplied-DLL investigation below now resolves its ordinary return paths.

### Supplied BaseTools: import and stop contract

After a recursive workspace search found no BaseTools-named file, the user
supplied [BaseTools.dll](../v3d_files_/BaseTools.dll) as the original. It reports
Product/FileVersion 70.06.59.00, AMD64, image base `0x180000000`, size 1,910,272,
SHA-256 `a41b4b00cf464da7da886f2303e6161f4474bda29b32793d39e4c6cfc39547f8`.
Matching metadata and the exact export do not independently prove station
deployment provenance; this analysis is pinned to the supplied bytes.

The earlier negative PE import lookup was caused by `pefile` 2024.8.26's
default internal 8,192-entry limit, not by an absent import. Setting
`pefile.MAX_IMPORT_SYMBOLS = 65536` in the isolated analysis process before
import-only parsing resolves 67 descriptors and 7,636 imports without warnings.
The limit counts internal table entries, not merely the final imported symbols.

The executable's slot `0x140d53470` resolves to
`BaseTools.dll!?Stop@CViThread@@QEAA_NAEAKK@Z`. IAT and ILT slot 121 agree:
ILT RVA `0x10403e0`, bytes `749a090100000000`, hint/name RVA `0x1099a74`, hint
1150. The raw name agrees with the parsed name and the DLL's non-forwarded export
at RVA `0x7e1a0`, ordinal 1151. Import hints are not export ordinals.

Source-PE disassembly establishes the following ordinary-return behavior:

| Address | Verified operation |
| --- | --- |
| `0x18007e1aa` | Test `this+8`; NULL returns true without a wait |
| `0x18007e1bb` | `SetEvent([this+0x18])`; result ignored |
| `0x18007e1cb` | `WaitForSingleObject([[this+8]+0x58], timeout)` |
| `0x18007e1d1` | Test the full wait result; every nonzero result returns false |
| `0x18007e1f3` | On zero only, virtual deleting-destructor call on the object at `this+8` |
| `0x18007e1f6` | Clear `this+8` after that call, then return true |

The false-return path leaves the object pointer intact and does not close its
handle. There is no write to the reference output DWORD in this body. The known
base-worker caller passes `0xffffffff` as timeout, so this is an infinite Win32
wait, not a bounded recovery policy. Ignoring a failed stop signal can leave it
waiting indefinitely if the worker otherwise remains active; no such incident
was induced here.

`Start` (`0x18007e0a0`) stores its creation-helper return in `this+8` at
`0x18007e147`, then passes the nested `+0x58` handle to `ResumeThread` at
`0x18007e179`. Thus Stop waits on the handle used to resume the created thread,
not the per-work completion event. For a valid owned thread handle, successful
wait establishes thread termination. Correct ownership, no concurrent replacement,
and coverage of asynchronous descendants still require proof. The creation
helper and its MFC dependency were not expanded in this bounded pass.

The default constructor (`0x18007e000`) initializes `this+8` to NULL and stores
an unchecked auto-reset, initially nonsignaled `CreateEventA` result at `+0x18`.
The thread destructor (`0x18007e040`) closes that stop event; it does not perform
another join. These observations do not make successful Stop an inspection
success signal or its NULL-object fast path a pool-generation drain oracle.

Disposition: the import identity and Stop body are resolved for the supplied DLL.
No safe stock containment path is established: derived worker cleanup still
precedes Stop, the base ignores false, and closed admission, failed-drain caller
binding, handle ownership, and two-lane coverage remain open. Further design
must establish stop-before-release ordering and checked outcomes. No extra patch
site, binary change, DLL load, target execution, or lifecycle-gate promotion occurred.

## Arithmetic bound

Rev5 uses low-DWORD `imul` products followed by unsigned `jbe` in
[the reference generator](../tools/patch_f1_missing_n_rev5.py). Exact no-wrap bounds:

- `missing * 100`: missing at most **42,949,672**.
- `inspected * 30`: inspected at most **143,165,576**.
- A conservative common cap of 42,949,672 inspected completions is sufficient
  for both products only if `0 <= missing <= inspected` and counters have not
  wrapped. This is a mathematical bound, not an established supported limit.

Counterexample: inspected = 143,165,577 and missing = 1 yields low DWORD
`inspected * 30 == 14`. The stock test sees `100 > 14` and triggers, whereas
the wide comparison is `100 > 4,294,967,310`, which is false. PowerShell UInt64
arithmetic reproduced these values. No supported workload maximum or enforcement
has been established; the arithmetic entry gate remains blocked.

## Provenance and reproduction

Source: `v3d_files_/Vision3D.exe`, 28,738,048 bytes, SHA-256
`ccca11b2f05084b484fa5556c67f8874065dbc0b6265177d2517f81265af00f4`.
The extractor checks source hash, Ghidra executable hash, x64 language, image base,
and every retained instruction byte against the PE file before writing evidence.
Decompilation types and reference completeness are not validated by byte equality.

[ExtractEntryGateEvidence.py](../tools/ghidra_scripts/ExtractEntryGateEvidence.py)
uses installed Ghidra 12.1 `DefaultProjectData(locator, false, false)` and
`getReadOnlyDomainObject(consumer, -1, monitor)`, releases the program, and closes
the project. Installed `Project-src.zip` confirms that a read-only project skips
the writable-project lock. No analysis, transaction, save, lock deletion, process
termination, or project creation was performed. Unsaved active-session analysis
is not included. Existing output filenames are refused.

Actual extraction runtime: CPython 3.14.5 AMD64, Ghidra 12.1, Java 25.0.3,
PyGhidra 3.1.0, JPype 1.7.1. These are the existing analysis toolchain versions,
not a newly qualified release toolchain. The MCP environment supplies PyGhidra;
the workspace environment supplies the existing `pefile` package. No dependency
was installed. Each JSON includes the interpreter path and arguments.

Run from the repository root, using a new output filename:

```powershell
& {
    $previousPythonPath = $env:PYTHONPATH
    try {
        $env:PYTHONPATH = "$PWD/.venv/Lib/site-packages"
        & 'C:/Users/s_sme/Documents/ghidra-headless-mcp/.venv/Scripts/python.exe' `
            tools/ghidra_scripts/ExtractEntryGateEvidence.py 0x1406a9a80 0x1406a1660 `
            --output maps/rev2a_entry_gate_pool_recheck.json
    } finally {
        $env:PYTHONPATH = $previousPythonPath
    }
}
```

Twenty-five executable function records (twenty-four distinct entry points) are
retained in eleven saved-project JSON files; the loop is repeated in the binding
extraction. A twelfth source-PE report adds four distinct BaseTools functions,
for 29 records and 28 distinct module/entry pairs overall. SHA-256 manifest:

| Evidence file | SHA-256 |
| --- | --- |
| [Initial caller, execution, reset](rev2a_entry_gate_extract.json) | `5058044df3eaf01877f617a2770e8f014fe3ee2c7ee0176fb61fe629c3eb4e11` |
| [Zone dispatcher](rev2a_entry_gate_dispatch.json) | `0b79fddab7b39b03394e48fae9bac59d1c365f27f10ec87d935da3a768b6e420` |
| [Worker and synchronous execution](rev2a_entry_gate_workers.json) | `9574442436df8fbe212dab028acba71a4b3a28ae079e7d717be5f27f462194d7` |
| [First pass and slot release](rev2a_entry_gate_completion.json) | `6d3376d87657d5587be55de73eea4a1d3c9efad1b889d0203bb5e3591a39c965` |
| [Panel inspection and dispatch](rev2a_entry_gate_second_pass.json) | `11752d290b4802fb6ac9984ce1b7b2482aeaf33cd53a288d319ee8efa7fa46b8` |
| [Pool wait and worker selection](rev2a_entry_gate_pool.json) | `a17f74e998abf8b95d7ae50db9e2ef0fb020188668ee1435d14c5d0a7ee4915a` |
| [Worker loop and destructor](rev2a_entry_gate_worker_loop.json) | `b01f321a720253b1d8962576f19de75730f6b5e148ecdfe85adc26063de57837` |
| [Vtable binding and loop](rev2a_entry_gate_worker_binding.json) | `5372993bd8e2c4140c8e4765050a6a21e6c38be9f9e3df5ed695c2111c544d31` |
| [Handle insertion and construction](rev2a_entry_gate_worker_registration.json) | `a59a427d693854d6dfea574cb54d11df858fb2bbe598e39ad93d6a0e8332b199` |
| [Result, pool, and base-worker cleanup](rev2a_containment_cleanup.json) | `10ab56150e074bc88c416b0a34bf7858203a88b9d43c5ec09c5f911274f3fef4` |
| [Derived-worker container release](rev2a_containment_worker_release.json) | `16952ef7ab3ed086bcc54a683030ee74c5cb40aa5e807183827c010a4f822bd6` |
| [BaseTools Stop and executable import binding](rev2a_basetools_stop.json) | `84a0f330fc8a3cc64d33d5ce5063d21aedb5ee1939f643d011ab9870d3d3a68c` |

The BaseTools report is generated by static `pefile`/Capstone parsing, not by
Ghidra, and records both source identities and tool versions. Function extents
come from raw PE runtime-function entries; every byte of each contiguous extent
was decoded and independently rechecked against the DLL. Unwind metadata was not
interpreted or validated. Imports/exports were parsed with a finite 65,536-entry
limit and no warnings. No analysis project was created or modified. To reproduce
the selection, hash-check both sources, resolve the executable IAT/ILT/name at
the addresses above, and disassemble the runtime-function extents beginning at
DLL RVAs `0x7e000`, `0x7e040`, `0x7e0a0`, and `0x7e1a0`.

The extractor now accepts repeated `--references-to ADDRESS` options. It records
references to those addresses and extracts their containing functions through
the same stock-byte validation. This does not validate data bytes or make saved
reference metadata authoritative; decisive pointer values were independently
read from the stock PE. Extractor SHA-256 after this extension:
`4948e8c5dd8a1cadd1b805a46531524cc4e654cac31fb9d5186efd3cf712c76a`.
Use the environment wrapper above with these arguments and fresh output paths:

```text
0x1406a1a50 0x14069a890 --output maps/rev2a_entry_gate_worker_loop_recheck.json
0x1406a1a50 --references-to 0x140ea8a10 --output maps/rev2a_entry_gate_worker_binding_recheck.json
0x140620730 0x1406a99d0 0x1406997d0 --output maps/rev2a_entry_gate_worker_registration_recheck.json
0x1406719a0 0x140655980 0x14069a110 --output maps/rev2a_containment_cleanup_recheck.json
0x1406aac40 --output maps/rev2a_containment_worker_release_recheck.json
```

## Gate disposition

No lifecycle entry gate passes on this evidence. Required next work:

1. Extend the established normal-return signal edge to relevant callbacks,
   exceptional exits, cancellation, and handle lifetime.
2. Prove pool membership, lane ownership, dispatch/wait mode coverage, and no
   concurrent admission during the final barrier.
3. Resolve containment of the concrete unchecked event-creation failure chain.
   A scoped design review is now required before relying on the stock barrier:
   evaluate a verified stock/vendor correction or an explicitly approved narrow
   containment change. Neither adding a patch site nor weakening the entry gate
   is authorized by this investigation. A production frequency assumption or a
   successful ordinary workload does not close this failure-path obligation.
4. Complete vector-writer/lifetime, result-identity, and reset/reuse proofs;
   corroborate with authorized generation-tagged two-lane runtime traces.
5. Establish/enforce a supported arithmetic bound or approve wider arithmetic.

The current rev5 code-only and artifact verifier commands were rerun successfully;
optimized Python was refused before PASS output. Machine-code tests stub stock
calls, so they neither detect this stock wait-result gap nor prove Windows
exception dispatch or live scheduling. Rev6 assembly/publication and station
execution remain prohibited by the unmet gates.