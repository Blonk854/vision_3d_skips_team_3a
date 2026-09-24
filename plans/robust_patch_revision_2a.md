# Robust Feature 1 Patch Revision 2a

## Decision and scope

Architectural review: agree with the overall approach, subject to the entry and
release gates below. Retaining rev5's CAO ownership, immediate stock skip,
serialized reconciliation, five patch sites, and unchanged transport is the
best reasonable architecture supported by the inspected evidence. A rewrite,
configurable threshold, larger context table, or transport change is not
justified.

Deployment scope, confirmed by the user on 2026-09-22: single-lane machines only.
Dual-lane machines are unsupported and excluded from deployment and validation.
Cross-lane coverage is not an entry or release gate; F1-H is not applicable.
Single-lane operation still requires worker/callback quiescence, concurrent
subpanel isolation, vector ownership, and safe CAO retirement and reuse.

### W7-QUAL-01 - Accepted qualification waiver

On 2026-09-22 the user requested removal of the isolated Windows 7 Embedded
environment requirement and stated willingness to sign off on the risk. Record
this instruction as accepted risk for proceeding without that qualification,
not as a completed test or a separate signed production-release approval.

Availability of an isolated Windows 7 Embedded x64 environment, native target
unwind/exception-dispatch tests, and target owner-state/callback-retirement traces
is no longer an entry or release prerequisite. Their status is **waived -
unverified**, not passed. This includes the unavailable native qualification
portion of R7 and section 4 step 8. Do not recreate the removed prerequisite by
requiring equivalent target traces under another name.

Accepted residual risks include unverified target compatibility, wrong owner-state
selection, delayed callbacks accessing retired storage, and exception cleanup
causing crashes, hangs, or incorrect inspection/review results. Development-host
tests and emulation do not establish absence of those risks on the target.

Keep source-byte/identity checks, available offline verification, static ownership
analysis, and failure/cleanup checks. This waiver does not waive known defects,
failed tests, or the remaining implementation contracts. It does not authorize
native execution, fault injection, installation, new hooks, or production release.
Candidate approval, station identity checks, trial controls, rollback, and release
sign-off remain separate requirements. Earlier isolated-target prerequisites in
historical records are superseded only within this waiver's scope.

This is an implementation plan, not approval to run a patched executable on a
production station. The review was static: it did not regenerate a binary,
rerun emulation, execute Vision3D, or validate Windows exception dispatch.

## Review findings incorporated

### R1 - Blocker: terminal failure must not mean committed

- Issue: rev5 uses ordered state comparisons such as `state >= 2` in worker and
  finalizer behavior. A new failure value of 4 would therefore be interpreted as
  committed unless every consumer changes.
- Why it matters: a failed stock skip could clear defect fields and affect review
  routing without a confirmed successful `SkipSubPanel` return.
- Risk if unaddressed: high correctness and data-integrity risk.
- Improvement: use the explicit state table in section 2 and exact committed-state
  membership in assembly, model, verifier, reconciliation, notification, and reset.

### R2 - Significant: cleanup and partial-mutation semantics need exact contracts

- Issue: rev5 cleanup resets a recorded winner to open even if success may already
  have been published. Reconciliation also mutates records incrementally, so an
  exception can leave an idempotent but partial update.
- Why it matters: retrying a possibly partial stock mutation is unsafe; demoting a
  committed state can duplicate skip insertion. A partial reconciliation must not
  be mistaken for complete reconciliation.
- Risk if unaddressed: high; duplicate mutation, inconsistent records, leaked
  ownership, or incorrect notification can result.
- Improvement: publish `failed-disabled` only from `claiming`, never demote states
  2 or 3, make ownership cleanup idempotent, and keep reconciliation state at 2
  until the complete walk succeeds. A reconciliation exception increments a
  process-lifetime failure counter, sets a local sticky flag, suppresses UI posting,
  propagates the exception, and requires containment. A later normal invocation may
  revalidate and repeat the idempotent field writes before atomically publishing 3;
  it must not free result trees or repeat `SkipSubPanel`.

### R3 - Significant: lifecycle and completion assumptions need proof obligations

- Issue: the current hook counts entries, not stable result identities. The known
  handoff order does not by itself prove worker drain, vector lifetime, or absence
  of late callbacks across CAO reuse.
- Why it matters: repeated delivery could trigger early, and stale workers could
  write into a reused context.
- Risk if unaddressed: high if the assumptions are false.
- Improvement: define the completion unit and prove hook multiplicity, worker drain,
  array ownership, reset, and reuse ordering on the supported single lane before
  assembly changes.
  If duplicate delivery can occur and must not count, stop for a scoped identity
  design; do not claim that the current cell layout deduplicates.

### R4 - Significant: release-stopping diagnostics must survive CAO retirement

- Issue: context-local flags are cleared by reset, and a debugger capture cannot be
  guaranteed to win the race with normal retirement. Unsupported-ID and capacity
  events already have global counters, but winner, unknown-state, layout, cleanup,
  and reconciliation failures do not.
- Why it matters: a station trial could lose the only evidence of a safety failure
  and be accepted incorrectly.
- Risk if unaddressed: medium to high operational risk.
- Improvement: retain context-local sticky flags for detailed debugging and add
  process-lifetime atomic counters for every release-stopping failure class. Reset
  clears local detail only after zero references and never clears global counters.
  Trial acceptance uses global counter deltas; pre-reset local capture is supporting
  evidence, not the sole oracle.

### R5 - Significant: the first release hash needs a pure build/report path

- Issue: rev5 already constructs the complete PE in memory before checking its
  digest, but its `patch` operation couples first-digest discovery, approval, and
  publication behind an already pinned hash.
- Why it matters: implementers need a reproducible way to review the first complete
  rev6 image without bypassing publication guards or auto-trusting a generated hash.
- Risk if unaddressed: medium; tested and released bytes can diverge or a guard may
  be weakened for convenience.
- Improvement: extract a pure `build_candidate(source_bytes) -> (bytes, report)`
  path. A review-only command may print the complete digest and diff report but may
  not write a distributable artifact. Pin the independently approved digest in the
  generator and verifier before guarded publication.

### R6 - Significant: release verification must not depend on active assertions

- Issue: the current verifier uses Python `assert`; `python -O` or
  `PYTHONOPTIMIZE` can remove checks while PASS messages still print.
- Why it matters: release evidence could claim success without executing hash,
  model, PE, unwind, or allowlist assertions.
- Risk if unaddressed: high verification-integrity risk.
- Improvement: fail immediately when `not __debug__` and convert release-critical
  checks to explicit named validation failures. Record the exact command,
  interpreter, environment, and exit status. Add a regression that runs with `-O`
  and requires refusal rather than PASS output.

### R7 - Significant: native unwind qualification waived under W7-QUAL-01

- Issue: synthetic handler calls do not prove `RtlLookupFunctionEntry`, virtual
  unwind, or Windows exception dispatch. Allowing a station trial with merely a
  recorded unverified status exposes the station to unvalidated cleanup metadata.
- Why it matters: cleanup owns locks, references, and claim state on exceptional
  paths.
- Risk if unaddressed: high; an exception can deadlock or corrupt process state.
- Original improvement: require the isolated Windows unwind gate before station
  trial. W7-QUAL-01 supersedes the availability requirement: missing native target
  qualification is waived-unverified and does not by itself make an artifact
  offline-only. Available metadata/unwind checks remain required; an observed
  failure is not waived. Station execution still requires separate approval.

### R8 - Significant: candidate publication needs a crash-safe mechanism

- Issue: rev5 permits overwriting an unrelated destination and writes directly to
  the final path.
- Why it matters: interruption, aliases, junctions, or operator error could leave a
  partial artifact or overwrite protected evidence.
- Risk if unaddressed: medium operational and provenance risk.
- Improvement: restrict publication to the canonical `Updated` root; reject source,
  baseline, live, alias, and existing final destinations; create an exclusive temp
  file in that directory; flush, close, reread, and hash it; then rename without
  replacement. Clean only the owned temp file on failure.

### R9 - Minor: dependency and delivery evidence should match release rigor

- Issue: dependency versions are pinned but artifacts and Python architecture are
  not. Vision3D's final send log is emitted after an attempt and is not proof that
  the supervisor received the panel.
- Why it matters: toolchain provenance can affect generated bytes, and a station
  test can otherwise record attempted delivery as successful delivery.
- Risk if unaddressed: low to medium.
- Improvement: record one supported Python version/architecture and use a hashed
  release lock or retained wheel identities. For communication scenarios, require
  supervisor-side panel/image identity and count evidence; do not use the final
  Vision3D send log as the delivery oracle.

No separate material architecture rewrite, transport-security change, or runtime
performance optimization was established. Preserve the narrow patch scope, RX/RW
separation, source/DLL identity guards, and four currently pinned runtime packages.

## Assumptions and implementation entry gate

1. The target is Vision3D 70.06.59.00 with the exact executable,
   AvVTraitLib.dll, and StructSupport.dll hashes in `version.md`. The live
   `C:\VIT` installation is not an interchangeable source and is never modified by
   build or verification tools.
2. Rev5 is a reproducible offline baseline, not proof of live scheduling,
   Windows exception behavior, or station correctness.
3. Authorized station staff can supply representative single-lane workloads,
  supervisor-side receipt evidence, baseline measurements, rollback authority,
  and existing panel-containment procedures. An isolated Windows exception
  harness is not required under W7-QUAL-01.
4. CAPM worker drain, result uniqueness, memory ownership, and CAO reuse are
  hypotheses to assess in step 1. Unresolved implementation contracts remain stop
  conditions; missing native target qualification covered by W7-QUAL-01 is recorded
  as waived-unverified rather than recreated as a mandatory environment gate.
5. Stock `SkipSubPanel` normal return is the only available commit signal. A call
   that throws after partial stock mutation is indeterminate and is not retried.
6. Threshold configurability, including F1-D, remains deferred and requires an
   explicit accepted waiver.

## 1. Freeze contracts and baseline evidence

- Preserve stock files and the rev5 generator/artifact. Record paths, sizes,
  SHA-256 values, repository revision and worktree state, OS/architecture, exact
  Python version/architecture, and dependency artifact identities. Preserve
  unrelated worktree changes.
- Create a release dependency lock with hashes for the four packages in
  `tools/requirements.txt`, or retain and hash the exact wheels used. Install into
  an isolated environment with hash enforcement. Do not expand runtime dependencies.
- Reproduce rev5 code-only and artifact checks before modifying their reference
  implementation. Run the existing verifier normally and with `python -O`; record
  that the latter currently demonstrates the assertion hazard, then require rev6's
  verifier to refuse optimized execution.
- Re-prove the five exact stock sites:

  | Site | Contract to preserve |
  | --- | --- |
  | `0x140736F47` | Final-mask completion count; live registers/flags and both return paths |
  | `0x140541050` | CAO retirement/reset and replayed stock prologue |
  | `0x14069B4D8` | Reconciliation before stock review gate; stable owned arrays |
  | `0x140736FCB` | Stock optical-skip call serialized with threshold skip |
  | `0x1406748C5` | Include skip bit `0x100` in review routing |

- Record register and flag liveness, stack alignment, shadow space, field
  ownership, and stock exception/return behavior at every affected call boundary.
- Define an inspected sample as one completed inspection at the final-mask hook.
  Establish whether one result can reach it more than once before reset and
  distinguish duplicate delivery from legitimate reinspection.
- Prove worker drain before CAPM reconciliation, vector immutability through
  validation/mutation, no late callbacks after retirement, and reset before reuse
  of the same CAO pointer. Record evidence for the supported single lane. The downstream
  communication semaphore is not sufficient proof.
- Preserve `Missing * 100 > inspected * 30` after at least 10 completions. Prove
  DWORD arithmetic against the supported workload maximum or use justified wider
  intermediates.
- Preserve worker skip -> CAPM reconciliation -> review gate -> prepare/event ->
  asynchronous image/panel messages. Do not patch prepare, recorder, transport,
  database, OIS/OTR, or network code.

## 2. Define state, ownership, diagnostics, and failure contracts

Use named values consistently in generator, independent model, verifier, and docs:

| Value | State | Allowed behavior and transitions |
| --- | --- | --- |
| 0 | Open | Count; atomically claim `0 -> 1` once threshold qualifies |
| 1 | Claiming | One winner; waiters hold references but no table/skip lock |
| 2 | Skip committed | Stock returned normally; normalize matching results; publish `2 -> 3` only after complete reconciliation |
| 3 | Reconciled | Preserve successful skip and notification suppression |
| 4 | Failed-disabled | No retry, normalization, reconciliation, or notification until retirement |

- Success predicates are exactly `state == 2 || state == 3`. State 4 and unknown
  values never qualify by ordering. Unknown values leave patch-owned result fields
  untouched, increment a global counter, set a local flag when a context exists,
  and continue through stock behavior.
- Publish `1 -> 2` only after normal stock return. On exceptional unwind of the
  claiming winner, use a conditional `1 -> 4`; never downgrade 2 or 3.
- Define ownership slots as `(pointer, owned-bit)` pairs for context reference,
  table lock, skip lock, and claimed cell. Clear the owned bit before or atomically
  with release so repeated cleanup cannot release another thread's ownership.
  Place ownership publication before the first potentially faulting instruction
  that depends on it. Document and test every supported fault boundary.
- Cleanup handlers are unwind-only, idempotent, and continue exception search.
  They do not swallow exceptions, resume execution, reverse stock mutation, or
  claim general memory-safety recovery.
- A stock call that throws after partial mutation is indeterminate. Publish state 4
  only if the cell is still claiming, increment the global winner-failure counter,
  preserve local diagnostics, and contain the panel. Never automatically call stock
  again. Apply the same containment rule to optical-skip wrapper exceptions.
- Reconciliation validates the complete vector before writing. During mutation,
  writes are restricted to the two idempotent fields already used by rev5. State
  remains 2 until the full walk completes, then changes atomically to 3. On unwind,
  increment the global reconciliation-failure counter, set a local flag, release
  owned references, suppress UI posting, and propagate. A later normal finalizer
  may repeat validation and idempotent writes from the beginning; no result tree is
  freed and no stock skip is repeated. The affected panel remains quarantined even
  if a later retry completes, pending review of the failure evidence.
- Invalid layout preserves state 2 and the stock skip, increments a process-lifetime
  invalid-layout counter, sets a context flag, avoids all vector writes, and follows
  stock review policy without posting patch UI.
- Retain eight contexts and IDs 0..1023. Unsupported IDs and exhaustion fail open.
  Keep process-lifetime atomic counters for unsupported ID, exhaustion, winner
  failure, optical-wrapper failure, invalid layout, reconciliation exception,
  unknown state, and cleanup invariant violation. Keep context-local sticky flags
  for detail. Verify every counter fits within the existing RW section and cannot
  overlap context storage.
- UI behavior: at most one eligible attempt per finalizer invocation, only after
  successful reconciliation and a valid target. A false return increments a global
  post-failure counter and clears the posted bit for a later eligible retry. Success
  suppresses later attempts for the lifecycle. UI outcomes never change routing or
  skip state. An exception follows the finalizer failure/containment contract.
- Do not add spin timeouts that release another thread's lock or allow concurrent
  mutation. Establish progress through ownership proof, deterministic interleavings,
  bounded harness execution, station latency limits, and the station's external
  process-hang procedure.

## 3. Implement rev6 and harden the verifier incrementally

- Create `tools/patch_f1_missing_n_rev6.py` from rev5 and preserve rev5 as the
  pinned baseline. Do not change the active facade until rev6 passes offline gates.
- Add failing model and machine-code tests for R1/R2 before assembly changes.
  Update every state consumer, including worker fast paths, waiters, reconciliation,
  notification, cleanup, diagnostics, and reset.
- Refactor the verifier to select a revision explicitly and retain a historical
  rev5 mode. Do not infer release identity, expected diff spans, runtime-function
  count, or expected semantics solely from the module under test.
- At verifier startup, reject `not __debug__` and nonempty `PYTHONOPTIMIZE`.
  Replace release-critical `assert` checks with explicit `require`/validation
  failures that identify the invariant. Print PASS only after all named checks run.
  Add a subprocess regression proving `python -O` exits nonzero without PASS.
- After rev6 passes, replace `tools/patch_f1_missing_n.py` with a documented facade.
  Check CLI/import callers and output naming before removing legacy symbols. Keep
  history in repository history or an explicitly inactive archive, not two defaults.

Required executable coverage:

| Area | Cases and assertions |
| --- | --- |
| Policy | 4/9, 3/10, 4/10, good tenth, exact 30%, mixed masks, identity contract, arithmetic maximum |
| Isolation | Two CAOs/lanes with equal IDs; simultaneous distinct subpanels; one winner per cell |
| Capacity | IDs 0, 1023, 1024, unsigned negative; eight contexts plus ninth; recovery after retirement |
| Lifecycle | Lookup after hole; reset with held refs; pointer reuse; no stale callback; absent/active/retiring wrapper |
| State | Exact handling of 0..4; unknown values; no ordered committed predicate; no committed-state downgrade |
| Failure | Pre-call, in-call, post-return/pre-publish, post-commit, partial stock mutation, no retry, repeated cleanup |
| Reconciliation | Empty/valid vectors; invalid count/pointer/order/stride/cap; injected mid-walk fault; idempotent retry; unrelated records unchanged |
| UI/review | Stock review call counts; zero/one post attempt; suppression; false-return retry/counter; absent handle; failure-only context |
| Diagnostics | Every global counter increments only for its event, survives retirement, and has no RW overlap |
| Cleanup/ABI | Owned/unowned locks; exact refcounts; every fault boundary; nonvolatile registers; live flags; shadow space; alignment; continuations |
| Verifier integrity | Normal invocation passes; `-O`/`PYTHONOPTIMIZE` refuses; a forced failed check cannot print overall PASS |

- Execute generated instructions against minimal fake CAO/zone/anomaly memory with
  red zones and sentinels. Stub stock calls explicitly and report that limitation.
- Schedule deterministic interleavings across claim, stock return, failure publish,
  finalization, reset, and pointer reuse. Require bounded harness completion and
  exactly-once threshold mutation.
- Retain historical mutation regressions and add mutations for `>= 2` success,
  committed-state downgrade, missing ownership marker, disabled global diagnostic,
  optimized verifier execution, and nonexclusive publication.
- Validate worker, finalizer, reset, wrapper, and cleanup paths. Verify no introduced
  worker/global `RazRes` and no calls into prepare/communication/recorder code.

## 4. Build, pin, publish, and inspect the complete artifact

1. Implement a pure full-PE builder that accepts verified source bytes and returns
   candidate bytes plus a report. It performs source/DLL identity checks, original
   site checks, section and cave bounds, runtime-function construction, and the
   field/offset-specific diff calculation without filesystem publication.
2. Run the pure builder twice in fresh processes and require identical bytes,
   reports, and SHA-256. Independently review the complete diff and digest. Pin that
   approved digest as an explicit source change in rev6 and the verifier. No auto-pin,
   skip-hash option, or unpinned distributable output is allowed.
3. Validate section bounds and RX/RW permissions, image size, imports/IAT, exception
   directory, relocation status, checksum/signature state, and load-config/CFG
   metadata. Check direct/indirect targets against actual mitigations; unchanged
   metadata alone is not proof of compatibility.
4. Derive expected `RUNTIME_FUNCTION` records from an independently reviewed
   manifest. Four primary records remain expected only if the function layout still
   justifies four. Verify sorted, nonoverlapping RVA ranges, unwind codes,
   prolog/epilog coverage, flags, and handler targets. Add a record for any new
   non-leaf helper rather than forcing the old count.
5. Publish only after all guards pass. Resolve and verify that the destination is
   under the canonical `Updated` directory, is not source/baseline/live/alias, and
   does not exist. Create an exclusive same-directory temp file, write all bytes,
   flush and close, reread and verify size/hash, then rename without replacement.
   Verify the final file identity/hash and remove only the owned temp on failure.
6. Recheck source, companion DLL, baseline, and live-file identities after build.
   The build tool never writes outside `Updated` and never installs the artifact.
7. Fresh-import the exact pinned artifact into a disposable Ghidra 12.1 project.
   Record loader, language, image base, warnings, and analysis settings. Inspect all
   five sites, complete injected functions, cleanup entries, calls, continuations,
   and runtime metadata against `maps/production-flow.md`. Archive address-scoped
   evidence. A loader-only import is not dependency or behavior validation.
8. Optional native qualification, waived-unverified under W7-QUAL-01. If later
  separately authorized and available, use a Windows harness for function-table lookup,
   virtual unwind, and exception dispatch with controlled faults in representative
   prolog/body/epilog and call-site positions. Verify reconstructed frames,
   nonvolatile registers, handler invocation, propagation, exact ownership release,
   state/counter outcomes, and repeated cleanup safety. Synthetic direct calls are a
  lower-tier test. Unavailability does not block progress or trial eligibility;
  an observed failure still blocks acceptance until resolved. This step does not
  authorize a harness run or fault injection.

## 5. Documentation, station trial, and rollback

- Update README, version history, and production-flow documentation with revision,
  exact hash/size, dependency lock identity, handler/RVA layout, states, counters,
  local flags, failure semantics, commands, and validation limits. Remove stale
  active-default claims without rewriting historical evidence.
- Produce a run sheet mapping F1-A through F1-L to the existing definition,
  scenario, expected result, evidence, and pass/fail/deferred status. Record the
  accepted F1-D waiver and mark F1-H not applicable under the single-lane-only
  scope; do not invent replacement meanings.

  | ID | Required result |
  | --- | --- |
  | F1-A | 4/10 skips SP1 at completion 10; populated SP2 completes |
  | F1-B | Exactly 3/10 does not auto-skip |
  | F1-C | All completions count; only Missing bit `0x1` enters numerator |
  | F1-D | Configurability deferred with accepted waiver |
  | F1-E | More than 30% before 10 completions does not skip yet |
  | F1-F | Four early Missing results and a good tenth still trigger |
  | F1-G | Concurrent subpanels skip once without crash/crossover |
  | F1-H | Not applicable: cross-lane CAO isolation; dual-lane machines are unsupported |
  | F1-I | Skip-only panel appears in section D and stops at review |
  | F1-J | Other subpanel defects remain reviewable with threshold skip |
  | F1-K | Bronco/foreign-material records/routing are correct without access violation |
  | F1-L | Immediate next panel has no stale counts or reset stall |

- Include the station matrix from `version.md` within the single-lane-only scope:
  boundary cases, good tenth, mixed defects, skip-only review, simultaneous subpanels, boundary and
  unsupported IDs, immediate next panel, Bronco/foreign material, and at least 20
  representative panels. Twenty panels are scenario coverage, not proof that rare
  races are absent.
- Before trial, resolve documented OTR/model/image configuration errors. Record
  confirmation that the target is a single-lane machine; exclude dual-lane machines.
  Record
  station hardware/OS/build, executable/DLL/config/model hashes, operator, lots,
  rollback owner, candidate hash, and starting values of all global counters.
- Capture a matched stock baseline and approve numerical maximum cycle-time,
  latency-regression, reset-delay, and rollback-time tolerances before candidate
  measurement. Record per-panel timing, worst delay, crashes/hangs, expected UI,
  database, supervisor, and lane results.
- For communication scenarios, use supervisor-side receipt records keyed by panel
  and expected image count. Vision3D's final `sent to supervisor` log proves only an
  attempt. Preserve client failure logs as supporting evidence.
- The full offline verifier, independent PE/Ghidra inspection, deterministic build,
  rollback rehearsal plan, and approved run sheet remain required before station
  installation. Carry W7-QUAL-01 and its unverified native qualification into the
  release record; do not require an isolated Windows environment as an extra gate.
- Install only in a maintenance window after production is stopped and pending
  result traffic is quiesced. Verify station identity; stage the candidate; stop
  Vision3D completely; retain/hash stock; install only the candidate executable;
  verify installed hash before restart. Build tools never perform installation.
- Compare ending global counters with starting values. Any release-stopping delta is
  a failed trial even if the context was reset. Capture local flags/dumps where
  available, but do not depend on winning a pre-reset observation race.
- Stop for any crash/hang, incorrect skip/review/lane result, release-stopping
  counter, unexpected capacity exhaustion, missing supervisor receipt, or exceeded
  tolerance. Preserve logs/dumps and quarantine affected panels/results. Do not
  blindly replay messages or assume binary rollback reverses data effects.
- Rehearse rollback with the process stopped: restore the verified stock executable,
  confirm DLL/config identities, restart, and run known normal and mixed-defect smoke
  panels with UI/review/database/supervisor checks. Record elapsed restore time and
  operator sign-off. Resolve pending or uncertain results through the existing
  station procedure before production resumes.

## Acceptance tiers

| Tier | Required evidence | Permission |
| --- | --- | --- |
| Offline candidate | Contract proofs, hardened verifier, executable model/emulation, deterministic full-PE build, reviewed/pinned hash and diff | Publish one guarded candidate under `Updated` only |
| Station-ready | Offline tier plus independent PE/Ghidra inspection, recorded W7-QUAL-01 native qualification waiver (or subsequent qualification evidence), approved run sheet, baseline, tolerances, and rollback plan | Authorized controlled station trial only |
| Production | Complete applicable F1/matrix results, no release-stopping counter deltas, timing acceptance, supervisor-side receipt evidence, successful rollback rehearsal, documented waivers, owner sign-off | Explicit production release |

Retain source, reports, dependency identities, commands, digests, counter snapshots,
station evidence, and rollback identity as release evidence. Patched binaries remain
uncommitted. Any unmet contract or gate is blocked, deferred, or explicitly waived
within its documented scope, never converted into a pass.