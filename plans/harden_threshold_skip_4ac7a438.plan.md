---
name: Harden threshold skip
overview: Replace the worker-thread global cleanup with an atomic, panel-scoped request/commit design. Preserve the confirmed requirement that every skipped subpanel routes to review, while failing open to stock Vision3D behavior whenever injected-state or structure validation fails.
todos:
  - id: prove-lifecycle
    content: Prove panel/lane identity, reset generation, final-mask hook, and serialized finalization context in stock Vision3D
    status: pending
  - id: redesign-state
    content: Implement atomic panel-scoped counters, one-shot triggering, fail-open lookup, and worker-local skip handling
    status: pending
  - id: defer-normalization
    content: Implement validated serial anomaly reconciliation and post-commit UI notification without worker-thread RazRes
    status: pending
  - id: verify-revision
    content: Build and independently verify PE flow, ABI/unwind metadata, concurrency model tests, and binary diff
    status: pending
  - id: document-acceptance
    content: Document the revision and produce the required station acceptance matrix
    status: pending
isProject: false
---

# Harden Threshold Skip

## Architecture
- Treat [`tools/patch_f1_missing_n.py`](C:/Users/s_sme/Documents/Projects/vision_3d_skips/tools/patch_f1_missing_n.py) as a new revision rather than incrementally repairing the unsafe worker sweep.
- Move the counting hook from `0x140736F09` to a verified point after Vision3D merges supplemental defects and resets the current anomaly (candidate immediately after `0x140736F44`). Count the final stock mask and avoid skipping required result plumbing.
- Add injected per-panel state keyed by a verified production object identity plus reset generation. Use fixed open-addressed contexts/cells so sparse or large subpanel IDs do not index memory directly. If identity, capacity, or lifecycle validation fails, execute stock behavior without threshold skipping.
- Use `lock xadd` for inspected/Missing counts and `lock cmpxchg` for one winning trigger. Only that winner calls `SkipSubPanel`; losing workers must never mutate the skip list or repeat UI/cleanup work.
- Remove worker-thread all-zone `RazRes`. Once a subpanel is claimed, each later worker marks only its own completed anomaly skipped and exits through the verified stock cleanup path.
- Hook the serialized production-finalization path in `CProductionThread::CAPM_SetInspectionStatus` between worker completion and `ShouldItGoToReviewStation` (`0x14069B2A0` flow). There, reconcile prior completed anomalies using non-destructive field normalization (`+0x28 = 0`, `+0x2C = 1`) rather than freeing result trees. Validate `CAO+0x5880`, the `0x410` zone stride, vector begin/end ordering, `0x370` divisibility, and `+0x280` inspected state before every mutation; abort reconciliation safely on any failed invariant.
- Post the stock production-screen message once, after reconciliation. Keep the existing `0xFFFFFEFF → 0xFFFFFFFF` routing change because the confirmed requirement is that every skipped subpanel—not only threshold skips—stops for review.
- Replace the process-global counter clear with context-specific synchronized retirement in `SkipList_Reset`; advance the generation so stale workers cannot update a reused context.

## Verification
- Extend generator checks for every new hook’s original bytes, all dependent DLL hashes, section bounds/permissions, sorted runtime-function metadata, branch targets, stack alignment, preserved registers, and expected final output hash.
- Add deterministic model tests for exact 30% boundaries, supplemental Missing bits, duplicate component execution, simultaneous threshold crossings, reset/increment interleavings, two active panel contexts with identical subpanel IDs, hash collisions/table exhaustion, invalid zone/vector metadata, and IDs beyond 255.
- Rebuild `Updated/Vision3D.exe`, independently disassemble all injected paths, fresh-import it into Ghidra, and verify only intended PE spans changed. Do not claim runtime safety until station acceptance passes.
- Update [`version.md`](C:/Users/s_sme/Documents/Projects/vision_3d_skips/version.md) and [`README.md`](C:/Users/s_sme/Documents/Projects/vision_3d_skips/README.md) with the new addresses/hash, removed `RazRes` behavior, fail-open invariants, and a station test matrix covering parallel production, two panels/lanes, process mode, manual skips, retries, abort/restart, and skip-only review.

## Safety gate
- Before emitting a deployable executable, prove the production identity/generation key and finalization hook from stock control flow. If either cannot be established, stop with the patch source and findings rather than creating another production candidate.