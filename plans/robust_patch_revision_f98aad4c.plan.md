---
name: Robust Patch Revision
overview: Build a new hardening revision around the proven rev5 architecture while preserving the current 30%/10-sample policy and eight-context fail-open capacity. The revision will not touch review transport or add configuration; it will strengthen failure-state handling, remove legacy ambiguity, expand executable-path verification, and produce a station-test candidate only after deterministic PE and Ghidra checks pass.
todos:
  - id: freeze-contract
    content: Re-prove the five stock hook contracts and freeze the 30%/10-sample, CAO lifecycle, field ownership, and handoff ordering invariants.
    status: pending
  - id: build-rev6
    content: Implement rev6 with a terminal failed-disabled winner state, explicit diagnostics, safe cleanup semantics, and a single active generator facade.
    status: pending
  - id: expand-verifier
    content: Extend state, Unicorn, cleanup, finalizer, ABI, and historical-regression coverage before accepting the new generator.
    status: pending
  - id: validate-candidate
    content: Build deterministically, pin the new hash, verify PE/unwind/import/CFG and allowlisted diffs, then fresh-import and inspect the candidate in Ghidra.
    status: pending
  - id: document-release
    content: Update architecture and release documentation and produce the complete F1-A–L station execution and rollback run sheet.
    status: pending
isProject: false
---

# Robust Feature 1 Patch Revision

## Scope and safety contract
- Preserve the confirmed behavior: `>30% Missing` after at least `10` completed inspections, CAO-scoped counters, one `SkipSubPanel` winner, skip-only review routing, and unrelated defects remaining reviewable.
- Keep the proven five patch sites at `0x140736F47`, `0x140541050`, `0x14069B4D8`, `0x140736FCB`, and `0x1406748C5`; stop before emitting a candidate if source hashes, original bytes, register ownership, or CAPM ordering do not match.
- Preserve handoff ordering from [maps/review-station-handoff.md](C:/Users/s_sme/Documents/Projects/vision_3d_skips/maps/review-station-handoff.md): worker `SkipSubPanel` → CAPM reconciliation → review gate → prepare/event → async image and panel messages. Do not patch `PrepareResults`, `SendResults`, OIS/OTR, or network code.
- Defer F1-D configurability and context-capacity redesign. Eight contexts remain an explicit, diagnosed fail-open limit.

## Revision architecture
- Create [tools/patch_f1_missing_n_rev6.py](C:/Users/s_sme/Documents/Projects/vision_3d_skips/tools/patch_f1_missing_n_rev6.py) from the audited rev5 generator, retaining rev5 and its pinned artifact as a reproducible baseline.
- Make [tools/patch_f1_missing_n.py](C:/Users/s_sme/Documents/Projects/vision_3d_skips/tools/patch_f1_missing_n.py) a small facade for rev6 and quarantine the embedded legacy global-counter/worker-`RazRes` builder so there is one active implementation.
- Keep states `0=open`, `1=claiming`, `2=skip committed`, `3=reconciled`, and add an explicit terminal `failed-disabled` state for exceptions before commit. Waiters must fail open on that state instead of retrying a possibly partial `SkipSubPanel` or treating it as committed.
- Record separate diagnostics for unsupported ID, context exhaustion, invalid reconciliation layout, and failed winner/cleanup. Reset retirement must clear these with the CAO context only after references reach zero.
- Keep UI notification after serial reconciliation. Define and test the exact behavior already implied by rev5: one `PostMessageA` attempt per finalizer invocation; clear the posted flag on failure so a later invocation may retry; UI failure never changes skip or review routing.

## Verification-first implementation
- Expand [tools/verify_hardened_patch.py](C:/Users/s_sme/Documents/Projects/vision_3d_skips/tools/verify_hardened_patch.py) before switching the facade:
  - model threshold boundaries, duplicate completions, two CAOs/lanes, table exhaustion, IDs `1023/1024`, reset/refcount interleavings, and failed-disabled behavior;
  - emulate winner, loser, reset, stock-skip wrapper, and finalizer against a minimal fake CAO/zone/anomaly layout;
  - invoke cleanup handlers with synthetic unwind frames to verify lock/ref release and state transitions;
  - stub and count `SkipSubPanel`, `ShouldItGoToReviewStation`, and `PostMessageA`, including post failure/retry and invalid-layout paths;
  - assert ABI invariants, nonvolatile registers, stack alignment, branch destinations, no worker/global `RazRes`, and no calls into prepare/communication/recorder code.
- Add explicit regression cases for the historical failures: pre-final-mask counting, unlocked increments, duplicate CAO contexts, duplicate skip mutation, worker-side zone walk, invalid-layout double unlock, and exception-triggered retry.

## PE build and independent validation
- Keep strict source and companion DLL hashes, original-byte guards, section bounds/permissions, cave overlap checks, four sorted `RUNTIME_FUNCTION` records, unwind-only cleanup handlers, and an allowlisted byte diff.
- Separate iterative and release validation: code-only tests may build an in-memory payload without an output hash; writing the final candidate must require a newly pinned deterministic SHA-256 in rev6 and the verifier.
- Build one clearly named candidate under `Updated/`, run the generator twice, and require byte-identical output. Verify no RWX section, unchanged load-config/CFG metadata, exact import table preservation, and no source/DLL/live-`C:\VIT` writes.
- Fresh-import the candidate into a disposable Ghidra project and verify all five hook targets, injected function boundaries, call graph, and unwind handlers against [maps/production-flow.md](C:/Users/s_sme/Documents/Projects/vision_3d_skips/maps/production-flow.md). Archive address-scoped disassembly evidence under `maps/decomp/` or a candidate report.

## Documentation and station gate
- Update [README.md](C:/Users/s_sme/Documents/Projects/vision_3d_skips/README.md), [version.md](C:/Users/s_sme/Documents/Projects/vision_3d_skips/version.md), and [maps/production-flow.md](C:/Users/s_sme/Documents/Projects/vision_3d_skips/maps/production-flow.md) with the rev6 hash, handler sizes, state machine, diagnostics, failure policy, and exact verification limits.
- Produce a run sheet for F1-A–L plus the release matrix in `version.md`: 4/10 and 3/10 boundaries, good tenth result, mixed defects, skip-only review, simultaneous sub-panels, two lanes, IDs near 1023, immediate next panel, Bronco/foreign material, communication failure observations, and a 20-panel soak with cycle-time logging.
- Acceptance tiers: static/emulated pass permits candidate creation; fresh Ghidra/PE pass permits station trial; only complete station results and rollback rehearsal permit production sign-off. The stock executable remains the rollback artifact and patched binaries remain uncommitted.