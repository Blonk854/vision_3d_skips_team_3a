# Station run sheet stub (Rev7 trial candidate)

Recorded 2026-10-18; retargeted to **Rev7**. Owner authorized a controlled Rev7
trial on 2026-10-18 (`plans/rev6_owner_cover_memo.md`). Fill remaining header
fields and results during the maintenance window. Not production release.

Definitions: `README.md` Acceptance; matrix detail:
`version.md` § Station history and required release matrix;
procedure: `plans/robust_patch_revision_2a.md` § 5.
Rev7 multi-section policy: `plans/rev7_multi_section_fail_open.md`.

## Trial header (fill before window)

| Field | Value |
| --- | --- |
| Candidate revision | **Rev7** (`Vision3D_concurrency_fix_rev7.exe`) |
| Station name / ID | (operator: name at window) |
| Single-lane confirmed | ☐ yes (required at window) |
| Operator | |
| Rollback owner | Owner / 2026-10-18 (plan accepted) |
| Auth note signed | ☑ 2026-10-18 (owner-delegated) |
| Stock `Vision3D.exe` SHA-256 (pre-install) | |
| Installed candidate SHA-256 | |
| Companion DLL hashes unchanged | ☐ AvVTraitLib ☐ StructSupport |
| Maintenance window start / end | |
| Global counters at start | |

## Close-path smoke (Rev6/Rev7)

Run after install, before or interleaved with F1 cases. Record evidence paths.

| ID | Scenario | Pass if | Result | Evidence |
| --- | --- | --- | --- | --- |
| CP-1 | Open panel, skip one sub-panel, close/review | No crash; skip list / section D sane | ☐ pass ☐ fail ☐ skip | |
| CP-2 | Reset skip list / reopen next panel | No stale skip counts; no hang on open | ☐ pass ☐ fail ☐ skip | |
| CP-3 | Close production document / stop production | No AV; workers join before free (no hang) | ☐ pass ☐ fail ☐ skip | |
| CP-4 | View close after skip refresh posted | No AV on late refresh; UI returns | ☐ pass ☐ fail ☐ skip | |
| CP-5 | Multi-section panel (if available) | No Feature-1 auto-skip; no crash (Rev7 fail-open) | ☐ pass ☐ fail ☐ N/A | |

## F1-A through F1-L

TST: ≥2 sub-panels, ≥12 presence checks each; **single-section** for threshold
cases (Rev7). Note `[Computing]` skip/mire/code order from station
`DefaultValue.ini` (read-only).

| ID | Required result | Status | Lot / panel IDs | Evidence |
| --- | --- | --- | --- | --- |
| F1-A | 4/10 Missing skips SP1 at completion 10; SP2 completes | ☐ pass ☐ fail ☐ deferred | | |
| F1-B | Exactly 3/10 does not auto-skip | ☐ pass ☐ fail ☐ deferred | | |
| F1-C | All completions count; only Missing `0x1` in numerator | ☐ pass ☐ fail ☐ deferred | | |
| F1-D | Configurability | **waived / deferred** (no INI keys) | — | — |
| F1-E | >30% before 10 completions does not skip yet | ☐ pass ☐ fail ☐ deferred | | |
| F1-F | Four early Missing + good tenth still triggers at 10 | ☐ pass ☐ fail ☐ deferred | | |
| F1-G | Concurrent subpanels skip once; no crash/crossover | ☐ pass ☐ fail ☐ deferred | | |
| F1-H | Cross-lane CAO isolation | **N/A** single-lane-only | — | — |
| F1-I | Skip-only panel in section D; stops at review | ☐ pass ☐ fail ☐ deferred | | |
| F1-J | Other subpanel defects still reviewable with threshold skip | ☐ pass ☐ fail ☐ deferred | | |
| F1-K | Bronco/foreign-material: correct records/routing; no AV | ☐ pass ☐ fail ☐ deferred | | |
| F1-L | Immediate next panel: no stale counts or reset stall | ☐ pass ☐ fail ☐ deferred | | |

## Release-matrix smoke (single-lane)

From `version.md` matrix, scoped to one lane. Mark N/A only with reason.

| # | Scenario | Result | Notes / evidence |
| --- | --- | --- | --- |
| M-1 | 4/10 Missing boundary | ☐ pass ☐ fail ☐ N/A | |
| M-2 | 3/10 no-skip boundary | ☐ pass ☐ fail ☐ N/A | |
| M-3 | Good tenth after early Missing | ☐ pass ☐ fail ☐ N/A | |
| M-4 | Mixed defects (polarity/offset + Missing) | ☐ pass ☐ fail ☐ N/A | |
| M-5 | Skip-only review routing | ☐ pass ☐ fail ☐ N/A | |
| M-6 | Simultaneous sub-panels | ☐ pass ☐ fail ☐ N/A | |
| M-7 | Dual-lane / equal IDs | **N/A** unsupported | |
| M-8 | IDs near capacity boundary (if fixture exists) | ☐ pass ☐ fail ☐ N/A | |
| M-9 | Immediate next panel | ☐ pass ☐ fail ☐ N/A | |
| M-10 | Bronco/foreign-material production | ☐ pass ☐ fail ☐ N/A | |
| M-11 | ≥20-panel soak; cycle time + Vision3D logs | ☐ pass ☐ fail ☐ deferred | panels run: __ / worst cycle: __ |

## Stop / counters / rollback

| Check | Result | Evidence |
| --- | --- | --- |
| Stop triggers hit? (crash, hang, wrong skip/review, counter delta, missing supervisor receipt, tolerance) | ☐ none ☐ listed: | |
| Global counters end vs start | ☐ match ☐ delta (fail if release-stopping) | |
| Rollback rehearsal (process stopped → stock restored → hash OK → smoke) | ☐ pass ☐ fail ☐ not run | restore min: __ |
| Pending/uncertain results handled per station procedure | ☐ yes ☐ N/A | |

## Trial disposition

| Decision | ☐ continue trial ☐ stop / rollback ☐ request production-tier review (separate) |
| --- | --- |
| Operator | |
| Rollback owner | |
| Date | |

Production release is **not** granted by completing this sheet. See acceptance
tiers in `plans/robust_patch_revision_2a.md`.
