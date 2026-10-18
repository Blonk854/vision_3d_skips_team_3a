# Rev6 owner cover memo — controlled station trial

**Date:** 2026-10-18  
**From:** Team 3a (offline Rev6 close-path complete)  
**To:** Trial authorizer / rollback owner  
**Subject:** Sign-off request only — no install until signed

## Ask

Authorize **one** controlled maintenance-window trial of
`Updated/Vision3D_concurrency_fix_rev6.exe` on a **named single-lane** station,
or deny. This memo is not production release and not fleet rollout.

## Already done (offline)

- Rev6 PE builds and verifies: `python tools/verify_hardened_patch.py --revision rev6`
- Gate / Team2 check: `python maps/vector_ownership/team2_progress_check.py`
- Close-path: dtor join, view clear, SKIP snapshot + live capture
- W7-QUAL-01 remains waived-unverified (accepted residual)

## Attachments (read before signing)

1. `plans/rev6_native_install_authorization.md` — scope, hashes, rollback  
2. `plans/rev6_station_run_sheet.md` — F1-A–L + smoke (fill during trial)  
3. `maps/vector_ownership/TEAM2_WHERE_WE_ARE.md` — brief

## Decision

| Field | Fill |
| --- | --- |
| Station name / ID | |
| Single-lane confirmed | ☐ yes |
| Trial authorizer | ☐ authorize controlled trial / ☐ deny |
| Name / date | |
| Rollback owner (name / date) | ☐ rollback plan accepted |
| Notes / conditions | |

If **authorize:** schedule maintenance window; rebuild candidate; fill auth note
hashes + run-sheet header before install.  
If **deny:** leave stock installed; no further native action under this memo.

Production release requires a separate Production-tier decision
(`plans/robust_patch_revision_2a.md` § Acceptance tiers).
