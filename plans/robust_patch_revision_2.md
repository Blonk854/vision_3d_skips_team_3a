# Robust Feature 1 Patch Revision 2

## Decision and scope

Architectural review: agree with the overall approach, subject to the gates below.
Retaining rev5's CAO ownership, immediate stock skip, serialized reconciliation,
five patch sites, and unchanged transport is the best reasonable architecture
supported by the inspected evidence. A rewrite, configurable threshold, larger
context table, or transport changes are not justified by this review.

This is an implementation plan, not approval to run a patched executable on a
production station. This review inspected source and existing evidence; it did
not regenerate a binary, rerun emulation, or validate Windows exception dispatch.

## Review findings

### R1 - Blocker: terminal failure must not mean committed

- Issue: the proposed terminal state has no value or exhaustive consumer rules.
  Rev5's worker uses `state >= 2` to normalize the current anomaly. Its finalizer
  also uses that range for notification eligibility and prior-anomaly mutation.
  Assigning failure value 4 while retaining those comparisons would treat failure
  as success. Evidence: [worker](../tools/patch_f1_missing_n_rev5.py#L245) and
  [finalizer](../tools/patch_f1_missing_n_rev5.py#L452).
- Why/risk: high correctness risk; defect fields could be cleared without a
  confirmed successful threshold skip. This is a blocker to implementation as
  written, not evidence that a nonexistent rev6 already has the defect.
- Improvement: define the transition table below; use explicit membership in
  committed states everywhere, including the model. Test state 4 and unknown
  states through workers, reconciliation, notification, and reset.

### R2 - Significant: failure and unwind guarantees are underspecified

- Issue: rev5's count cleanup unconditionally resets its recorded winner cell
  to open, including when that frame has already published success. A replacement
  must distinguish pre-commit failure from post-commit cleanup. Synthetic handler
  invocation also does not establish that Windows finds or invokes the handler.
  Evidence: [winner publication](../tools/patch_f1_missing_n_rev5.py#L260),
  [cleanup](../tools/patch_f1_missing_n_rev5.py#L617), and the validation limits in
  [version.md](../version.md#L145).
- Why/risk: high if triggered; retry, incorrect downgrade, leaked locks, stalled
  reset, or partial stock mutation could follow. Disabling retries cannot undo a
  `SkipSubPanel` that changed memory before throwing.
- Improvement: conditional `claiming -> failed-disabled`, idempotent ownership
  cleanup, preserved committed states, explicit exception propagation, and a
  Windows unwind gate before production approval. Document partial mutation as
  indeterminate, requiring station containment rather than presumed recovery.

### R3 - Significant: lifecycle and completion assumptions need proof obligations

- Issue: the plan requests duplicate-completion tests without defining whether
  duplicate means repeated delivery of one result or distinct inspections. Rev5
  increments on each open-cell hook entry and stores no result identity. Also,
  the documented handoff order alone does not prove worker drain or stable arrays
  during finalization. The cited semaphore is acquired after the review-gate hook.
  Evidence: [counter path](../tools/patch_f1_missing_n_rev5.py#L207) and
  [handoff ordering](../maps/review-station-handoff.md#L49).
- Why/risk: high if these assumptions are false; duplicate counting can trigger
  early, or late workers and reused CAO pointers can cross lifecycle boundaries.
  Neither defect is established by this review.
- Improvement: define the completion unit, prove hook multiplicity, worker drain,
  array ownership, and reset/reuse ordering. Stop for a scoped design decision if
  any proof fails; do not claim deduplication or add it speculatively.

### R4 - Significant: diagnostics cannot all have CAO reset ownership

- Issue: unsupported IDs and context exhaustion currently increment global
  counters outside the eight contexts; exhaustion can occur with no owned slot.
  The original plan says retirement clears the diagnostics with the CAO.
  Evidence: [layout](../tools/patch_f1_missing_n_rev5.py#L96) and
  [global increments](../tools/patch_f1_missing_n_rev5.py#L295).
- Why/risk: medium; resetting global evidence on one CAO retirement can hide
  failures from another lane, and unreadable or prematurely cleared diagnostics
  cannot support station acceptance or incident investigation.
- Improvement: retain atomic process-lifetime global counters and separate
  context-local sticky flags. Define a read-only debugger/dump capture procedure
  and capture local diagnostics before retirement clears them.

### R5 - Significant: first release-hash pinning needs a complete build path

- Issue: requiring the expected hash before writing any candidate is sound, but
  the stated exception only assembles an in-memory code payload. That payload is
  not the complete PE whose digest must be pinned. Rev5 checks its final digest
  before writing. Evidence: [output guard](../tools/patch_f1_missing_n_rev5.py#L1087).
- Why/risk: medium; an implementer may bypass the guard, auto-trust its own new
  digest, or lose a reproducible connection between tested and released bytes.
- Improvement: construct and validate the complete PE in memory, review its diff
  and digest, pin the approved digest, then allow candidate writing. Preserve
  independent assertions and record the already pinned dependency versions.

### R6 - Significant: the station gate needs executable acceptance and rollback

- Issue: a rollback artifact and 20-panel run are named, but deployment identity,
  stop triggers, performance tolerances, pending-result handling, and rollback
  verification are not defined. Existing docs distinguish stubbed calls from
  unverified live scheduling and station behavior.
- Why/risk: high operational impact if a station trial hangs, misroutes, or leaves
  ambiguous panel results; changing the executable cannot undo database or
  supervisor effects already produced.
- Improvement: use the staged release procedure below with approved numerical
  tolerances, a stock baseline, a stopped-process replacement, retained evidence,
  quarantined uncertain results, and a witnessed restore-and-smoke-test exercise.

### R7 - Minor: notification wording conflicts with successful-post suppression

- Issue: rev5 makes zero calls when already posted, no eligible committed state
  exists, or the window handle is unavailable. It therefore does not guarantee
  one `PostMessageA` attempt per finalizer invocation.
  Evidence: [post path](../tools/patch_f1_missing_n_rev5.py#L553).
- Why/risk: low; ambiguous tests could introduce duplicate notifications or treat
  correct suppression as a regression.
- Improvement: specify at most one eligible attempt per invocation, with retries
  after a false return and suppression after success for the CAO lifecycle.

No separate material dependency, transport-security, or architecture rewrite
finding was established. Preserve the existing four pinned Python dependencies,
hash guards, RX/RW separation, and limited patch scope. Pointer-shape checks are
not a general memory-safety guarantee; ownership proof remains necessary.

## Assumptions and implementation entry gate

1. The target is Vision3D 70.06.59.00 with the exact executable, AvVTraitLib.dll,
   and StructSupport.dll hashes in [version.md](../version.md). The live `C:\VIT`
   installation is not an interchangeable source and must not be modified by
   build or verification tools.
2. Rev5 is a reproducible, offline-validated baseline, not a production-proven
   implementation of every concurrency and exception case.
3. Authorized station staff can supply representative two-lane workloads,
   baseline measurements, Windows exception-test access, and rollback authority.
4. CAPM worker-drain, result uniqueness, memory ownership, and CAO reuse are
   hypotheses to verify in step 1, not established facts from this review.
5. Threshold configurability, including F1-D, remains explicitly deferred and
   requires a recorded waiver rather than a false claim that every F1 item passed.

## 1. Freeze contracts and baseline evidence

- Preserve the stock files and rev5 generator/artifact. Record paths, sizes,
  SHA-256 values, source revision/worktree state, OS/architecture, Python version,
  and dependencies from [tools/requirements.txt](../tools/requirements.txt).
  Preserve unrelated worktree changes.
- Reproduce existing rev5 code-only and artifact checks before changing their
  reference implementation. Record failures without silently weakening checks.
- Re-prove these five sites against the exact stock bytes:

  | Site | Contract to preserve |
  | --- | --- |
  | `0x140736F47` | Final-mask completion count; correct registers and both return paths |
  | `0x140541050` | CAO retirement/reset and replayed stock prologue |
  | `0x14069B4D8` | Reconciliation before stock review gate; stable owned arrays |
  | `0x140736FCB` | Stock optical-skip call serialized with threshold skip |
  | `0x1406748C5` | Include skip bit `0x100` in review routing |

- Record register/flag liveness, stack alignment, shadow space, field ownership,
  and the stock exception/return behavior at each affected call boundary.
- Define an inspected sample as one completed inspection at the final-mask hook.
  Establish whether a single result can reach it more than once before reset.
  Distinguish repeated delivery from legitimate reinspection. If repeated delivery
  is possible and must not count, stop and approve a bounded identity/lifecycle
  solution before implementation; the current cell layout does not deduplicate.
- Establish worker drain before CAPM reconciliation, vector immutability through
  validation and mutation, absence of late callbacks after retirement, and reset
  before reuse of the same CAO pointer. Record evidence for both lanes. The
  downstream communication semaphore is not itself this proof.
- Preserve `Missing * 100 > inspected * 30` after at least 10 completions. Prove
  DWORD counts/products fit the supported workload or use justified wider
  intermediates; add a boundary check for the established maximum.
- Keep worker skip -> CAPM reconciliation -> review gate -> prepare/event ->
  asynchronous image/panel messages. Do not patch prepare, recorder, transport,
  database, OIS/OTR, or network code.

## 2. Define the state and failure contract before assembly changes

Use named values consistently in generator, independent model, and documentation:

| Value | State | Allowed behavior and transitions |
| --- | --- | --- |
| 0 | Open | Count; atomically claim `0 -> 1` once threshold qualifies |
| 1 | Claiming | One winner; waiters hold references but no table/skip lock |
| 2 | Skip committed | Stock call returned normally; normalize matching results; `2 -> 3` after reconciliation |
| 3 | Reconciled | Preserve successful skip and notification suppression |
| 4 | Failed-disabled | No further threshold attempts or patch-driven normalization until retirement |

- Success predicates must be exactly `state == 2 || state == 3`. State 4 and
  unknown values must never qualify by ordering. Unknown values leave patch-owned
  result fields untouched, record a diagnostic, and make validation fail.
- Publish `1 -> 2` only after normal stock return. On exceptional unwind of the
  claiming winner, conditionally publish `1 -> 4`; never downgrade 2 or 3.
  Preserve atomic ordering and release only locks/references owned by the frame.
- Cleanup must clear its ownership markers before a second invocation can release
  another thread's lock or decrement a reference again. Specify acquisition and
  release instruction boundaries, including gaps between ownership changes and
  marker updates. Test the supported exception boundaries explicitly.
- Cleanup handlers remain unwind-only and continue exception search. They do not
  swallow exceptions, guarantee resumed execution, repair arbitrary access
  violations, or reverse stock mutations. Fail-open means only that surviving
  callers take the stock continuation without patch-driven defect suppression.
- A stock call that throws after partial mutation is indeterminate. Preserve
  diagnostics; contain the affected panel through approved station procedures.
  Do not automatically re-call stock to complete or undo it. Apply the same
  containment policy to exceptions from the optical-skip wrapper.
- Invalid reconciliation layout retains an already committed stock skip, sets a
  local flag, avoids the vector walk, and follows existing stock review policy.
  Do not claim prior records were reconciled. Define partial-walk unwind behavior
  without demoting committed cells or freeing result trees.
- Retain eight contexts and IDs 0..1023. Exhaustion and unsupported IDs fail open.
  Process-lifetime atomic counters cover these global events; reset of one CAO
  cannot clear them. Use context-local sticky flags for layout/winner failures,
  clearing only at retirement after zero references. Define capture timing and
  symbol/offset meanings; do not add network telemetry or file I/O to handlers.
- UI: at most one attempt per eligible finalizer invocation, only following
  successful reconciliation and with a valid target. A false API return clears
  the posted flag for a later eligible retry; success suppresses further attempts
  for that lifecycle. Define exceptional-call behavior separately; no UI outcome
  changes routing or skip state.
- Do not introduce arbitrary spin timeouts that release another thread's lock or
  permit concurrent mutation. Establish progress through ownership/drain proofs,
  interleaving tests, and station latency gates.

## 3. Implement rev6 and extend the existing verifier incrementally

- Create the rev6 generator from rev5; preserve rev5 as a pinned baseline. Keep
  tests in the existing verifier and reuse its emulator and fixtures.
- Add failing regression expectations for R1/R2 before implementing new assembly.
  Make small changes and rerun the affected checks after each change. Update all
  state consumers, not just winner cleanup.
- Extend the verifier to select the intended revision explicitly; rev5 is
  currently imported directly. Preserve a way to check the historical baseline.
  Do not derive every expected semantic result or release identity from rev6.
- After rev6 passes, replace the legacy default module with a small documented
  facade. Check CLI and import callers before removing legacy symbols. Retain
  historical implementation through repository history or an explicitly inactive
  archive, not a second executable default. Check default output naming too.
- Keep runtime dependencies unchanged. If an additional Windows-only test harness
  is necessary, isolate it from shipping handlers and document its prerequisites.

Required executable coverage:

| Area | Cases and assertions |
| --- | --- |
| Policy | 4/9, 3/10, 4/10, good tenth result, exact 30%, mixed defect masks, completion identity contract, arithmetic limit |
| Isolation | Two CAOs/lanes with equal IDs; simultaneous distinct subpanels; one threshold winner per cell |
| Capacity | IDs 0, 1023, 1024, negative/unsigned invalid ID; eight active contexts plus a ninth; recovery after retirement |
| Lifecycle | Lookup after a hole; reset during held references; pointer reuse; no stale callbacks; stock wrapper with absent/active/retiring context |
| Failure | States 4 and unknown leave sentinels intact; pre-return exception; partial stock mutation; post-commit exception; no retry or downgrade |
| Reconciliation | Empty and valid vectors; invalid count/pointer/order/stride/cap; uninspected and unrelated records unchanged; no cross-cell writes |
| UI/review | Count stock review calls on normal paths; zero/one post attempts; success suppression; false-return retry; unavailable handle; failure-only context |
| Cleanup/ABI | Repeated cleanup invocation; owned/unowned locks; exact refcounts; nonvolatile registers, flags where live, shadow space, alignment, continuations |

- Execute actual generated instructions with minimal fake CAO/zone/anomaly
  memory and sentinel regions. Explicitly stub stock calls; report that limit.
- Schedule deterministic interleavings across claim, stock return, failure
  publication, retirement, and context reuse. Require bounded completion in the
  harness and exactly-once threshold mutation, not only a passing abstract model.
- Retain mutation regressions for pre-final-mask counting, unlocked increments,
  duplicate contexts, duplicate skip mutation, worker zone walking, double unlock,
  and exception retry. Add mutations for `>=2` success and committed-state downgrade.
- Validate finalizer/reset/wrapper/cleanup paths as well as the worker. Verify
  no introduced worker/global `RazRes` or calls into prepare/communication/recorder.

## 4. Construct, pin, and independently inspect the complete artifact

1. Assemble and construct the full candidate PE in memory using the same builder
   that will write the release artifact. Validate input hashes, original bytes,
   sizes, cave overlap, and a field/offset-specific allowlist before any write.
2. Validate hooks/continuations, section bounds and RX/RW permissions, image size,
   imports/IAT, exception directory, and unchanged load-config/CFG metadata.
   Check new direct/indirect targets against the actual mitigation configuration;
   unchanged metadata alone is not proof of compatibility. Record relocation and
   signature/checksum status; do not weaken station integrity enforcement.
3. Keep four primary `RUNTIME_FUNCTION` records if the function layout remains
   unchanged; independently check sorted, nonoverlapping RVA ranges, unwind codes,
   prolog/epilog coverage and handler flags/targets. Determine whether any newly
   non-leaf helper needs its own record instead of forcing the count to four.
4. Review the complete byte diff and resulting full-PE digest. Pin the approved
   digest in rev6 and the verifier as an explicit reviewed change. No auto-pin,
   skip-hash switch, or unpinned distributable output is allowed.
5. Write a distinctly named rev6 candidate under `Updated/` only after those
   guards pass. Reject source/baseline/live paths and accidental overwrites. Build
   twice in separate fresh invocations and require identical full bytes/hashes.
   Recheck source/DLL/baseline hashes afterwards.
6. Fresh-import the exact pinned file into a disposable Ghidra project. Record
   version, loader, language, image base, and import warnings. Inspect all five
   targets, complete injected functions, cleanup entries, calls, and continuations
   against [production-flow.md](../maps/production-flow.md). A loader-only import
   is not injected-code or dependency validation. Archive address-scoped evidence.
7. Exercise actual Windows unwind lookup/virtual unwind and exception dispatch
   in an authorized isolated harness with controlled faults at representative
   call sites and prolog/body/epilog positions. Check reconstructed frames,
   nonvolatile registers, handler invocation, propagation, and ownership release.
   Direct synthetic cleanup calls remain a separate lower-tier test. If this
   gate cannot run, label it unverified and block production sign-off.

## 5. Documentation, station trial, and rollback

- Update README, version history, and production-flow documentation with revision,
  exact hash/size, handler sizes and RVA layout, states, diagnostics ownership,
  failure semantics, commands, and validation limits. Remove stale active-default
  claims without rewriting historical evidence.
- Produce a run sheet mapping every F1-A through F1-L requirement to its existing
  definition, scenario, expected result, evidence, and pass/fail/deferred status.
  Do not invent replacement meanings for those IDs. Record the F1-D waiver.

  Requirements from [README.md](../README.md#L75):

  | ID | Required result |
  | --- | --- |
  | F1-A | 4/10 skips SP1 at completion 10; populated SP2 completes |
  | F1-B | Exactly 3/10 does not auto-skip |
  | F1-C | All completed parts count; only Missing bit `0x1` enters numerator |
  | F1-D | Configurability remains deferred; record the accepted waiver |
  | F1-E | More than 30% before 10 completions does not yet auto-skip |
  | F1-F | Four early Missing results and a good tenth still trigger at 10 |
  | F1-G | Concurrent subpanels each skip once without crash or count crossover |
  | F1-H | Equal subpanel IDs on two lanes remain CAO-isolated |
  | F1-I | Skip-only panel appears in section D and stops at review |
  | F1-J | Other subpanels' defects remain reviewable alongside threshold skip |
  | F1-K | Bronco/foreign-material production has correct records/routing and no access violation |
  | F1-L | Immediate next panel has no stale counts or reset stall |

- Include the complete existing version.md station matrix: 4/10 versus 3/10,
  good tenth completion, mixed defects, skip-only review, simultaneous subpanels,
  two lanes, boundary/unsupported IDs, immediate next panel, Bronco/foreign
  material, and at least 20 representative panels. Include communication failure
  observations without changing transport semantics.
- Before trial, record station hardware/OS/build, executable and companion DLL
  hashes, model/configuration identity, operator, test lots, and rollback owner.
  Resolve the documented OTR/model/image configuration errors before comparison.
- Capture a matched stock baseline and approve numerical maximum cycle-time,
  latency-regression, and reset-delay tolerances before candidate measurements.
  Record per-panel timings, worst observed delay, crashes/hangs, diagnostics,
  expected UI/database/supervisor results, and lane isolation. Twenty panels is
  a minimum scenario run, not statistical proof of rare-race absence.
- Capture global counter deltas and local failure flags before reset using the
  documented debugger/dump procedure. Validate that the procedure actually works;
  transient memory flags alone are not an operational report.
- Deploy only in a maintenance window after stopping production and quiescing
  pending result traffic. Verify the intended station build first. Stage a copy,
  stop Vision3D completely, retain and hash its approved stock executable, install
  only the candidate executable, and verify the installed hash before restart.
  Build tools never perform this live replacement.
- Stop the trial for any crash/hang, incorrect skip/review/lane result, failure
  diagnostic, unexpected capacity exhaustion, or exceeded timing tolerance.
  Preserve logs/dumps and quarantine affected panels/results. Do not blindly
  replay pending supervisor messages or presume a binary rollback reverses data.
- Rehearse rollback with the process stopped: restore the verified station stock
  executable, confirm unchanged DLL/config identities, restart, and run known
  normal/mixed-defect smoke panels with UI/review/database checks. Record outcome,
  elapsed restore time, and operator sign-off. Resolve pending/uncertain results
  through the existing station procedure before resuming production.

## Acceptance tiers

| Tier | Required evidence | Permission |
| --- | --- | --- |
| Offline candidate | Contract gates, executable model/emulation tests, reviewed full-PE hash and deterministic diff | Write a guarded candidate in Updated only |
| Station trial | Independent PE/Ghidra inspection, recorded unwind-test status, approved run sheet and recoverable stock baseline | Authorized controlled trial; no production approval |
| Production | Windows unwind gate passed, complete applicable F1/matrix results, timing acceptance, reviewed diagnostics, successful rollback rehearsal, documented waivers and owner sign-off | Explicit production release |

Retain source, reports, dependency versions, commands, digests, and rollback
identity as release evidence. Patched binaries remain uncommitted. Any unmet
contract or gate is recorded as blocked or deferred, never converted into a pass.