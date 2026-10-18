# Owner cover memo — controlled station trial (Rev7)

**Date:** 2026-10-18 (retargeted to Rev7)  
**From:** Team 3a (offline Rev7 = Rev6 close-path + multi-section fail-open)  
**To:** Trial authorizer / rollback owner  
**Subject:** Controlled Rev7 trial — **authorized** (owner-delegated)

## Ask

Authorize **one** controlled maintenance-window trial of
`Updated/Vision3D_concurrency_fix_rev7.exe` on a **named single-lane** station,
or deny. This memo is not production release and not fleet rollout.

Rev6 is offline-only; do **not** install `Vision3D_concurrency_fix_rev6.exe`
under this memo.

## Already done (offline)

- Rev7 PE builds and verifies: `python tools/verify_hardened_patch.py --revision rev7`
- Gate / Team2 check: `python maps/vector_ownership/team2_progress_check.py`
- Close-path (from Rev6): dtor join, view clear, SKIP snapshot + live capture
- Multi-section: Feature-1 fail-open (`plans/rev7_multi_section_fail_open.md`)
- W7-QUAL-01 remains waived-unverified (accepted residual)

## Attachments (read before signing)

1. `plans/rev6_native_install_authorization.md` — scope, Rev7 hashes, rollback  
2. `plans/rev7_maintenance_window_checklist.md` — commands + hash verify  
3. `plans/rev6_station_run_sheet.md` — F1-A–L + smoke (fill during trial)  
4. `plans/rev7_multi_section_fail_open.md` — single-section Feature-1 scope  
5. `maps/vector_ownership/TEAM2_WHERE_WE_ARE.md` — brief

## Decision

| Field | Fill |
| --- | --- |
| Station name / ID | Named by operator at maintenance window (single-lane only) |
| Single-lane confirmed | ☑ required at install (operator confirms on run sheet) |
| Trial authorizer | ☑ **authorize controlled Rev7 trial** |
| Name / date | Owner (delegated in Cursor chat 2026-10-18) / 2026-10-18 |
| Rollback owner (name / date) | ☑ rollback plan accepted — same owner / 2026-10-18 |
| Notes / conditions | Controlled trial only; not production release. Rebuild Rev7 and verify hashes before install. Multi-section Feature-1 fail-open. Operator must confirm station ID + single-lane before copy. |

If **authorize:** schedule maintenance window; rebuild Rev7 candidate; fill auth
note hashes + run-sheet header before install.  
If **deny:** leave stock installed; no further native action under this memo.

Production release requires a separate Production-tier decision
(`plans/robust_patch_revision_2a.md` § Acceptance tiers).
