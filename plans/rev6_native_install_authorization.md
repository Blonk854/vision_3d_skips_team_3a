# Rev6 native-install authorization note

Recorded 2026-10-18. This note is a **request checklist**, not approval.
Building or verifying `Updated/Vision3D_concurrency_fix_rev6.exe` does not
authorize station install, native execution, or production release.

W7-QUAL-01 (waived-unverified native qualification) remains in force. See
`plans/robust_patch_revision_2a.md` § W7-QUAL-01 and § 5.

## Scope requested (when signed)

| In scope | Out of scope |
| --- | --- |
| Controlled station **trial** of Rev6 only | Production release / fleet rollout |
| Replace **only** `Vision3D.exe` on one named single-lane station | Patching companion DLLs, INI, models, or `C:\VIT` |
| Maintenance window with production stopped | Live swap while panels are running |
| Rollback to hashed stock before reopen | Assuming binary rollback fixes data/supervisor state |

Not requested by this note: dual-lane machines, fault injection, new hooks beyond
the pinned Rev6 PE, or uniqueness/DWORD follow-ons.

## Artifact identity (rebuild before install)

| Item | Value |
| --- | --- |
| Builder | `python tools/patch_f1_missing_n_rev6.py` |
| Source | `v3d_files_/Vision3D.exe` |
| Source SHA-256 | `ccca11b2f05084b484fa5556c67f8874065dbc0b6265177d2517f81265af00f4` |
| Source size | 28,738,048 bytes |
| Candidate | `Updated/Vision3D_concurrency_fix_rev6.exe` |
| Candidate SHA-256 (local build 2026-10-18) | `172e490453a7ab064d61c8a628c085f48a190136e76c441104fe6c39175379b8` |
| Candidate size | 28,754,432 bytes |
| Companion (unchanged) | `AvVTraitLib.dll` `0f9f68b118112cea87e1735995776934d8d009e3d6d39a8a58562e3fa3e3e5f7` |
| Companion (unchanged) | `StructSupport.dll` `d6270dbe5c97b5ed1000c2541c1e8d495d7db6be184e45d6495d7fad75e0f832` |

Pre-install offline checks (must already be green on the install host):

```
python maps/vector_ownership/team2_progress_check.py
python tools/verify_hardened_patch.py --revision rev6
```

Gate MD5 at authorization draft: `8AB5FE5E5ECBAE540F8AD829E0B417E7`.
Rebuild the candidate immediately before install; if the hash differs from the
table above, record the new hash in the run sheet and do not reuse this row
blindly.

## Station constraints

1. **Single-lane only.** Dual-lane is unsupported (F1-H N/A).
2. **Named station.** Record hardware/OS/build, operator, lots, and rollback owner
   before the window.
3. **Quiesce.** Stop production; drain pending result traffic; no panel in flight.
4. **Identity.** Confirm station stock `Vision3D.exe` matches the source SHA-256
   above (or record an explicit stock baseline hash if the station already differs —
   do not install over an unknown stock).
5. **Install steps.** Stage candidate → stop Vision3D completely → retain/hash
   stock → copy only the candidate as `Vision3D.exe` → verify installed SHA-256 →
   restart. Build tools never perform installation.
6. **Companions untouched.** Do not replace DLLs/config/models in this trial.
7. **Stop triggers.** Crash/hang, wrong skip/review/lane result, release-stopping
   counter delta, missing supervisor receipt, or exceeded timing/rollback
   tolerance → stop trial, preserve logs, quarantine affected panels.

## Rollback

Rehearse with the process stopped before reopen:

1. Stop Vision3D.
2. Restore the retained stock executable (hash must match pre-install stock).
3. Confirm companion DLL and config hashes unchanged.
4. Restart; run known normal + mixed-defect smoke panels (UI / review / DB /
   supervisor).
5. Record restore elapsed time and operator sign-off.
6. Resolve pending or uncertain results through existing station procedure before
   production resumes. Binary rollback does **not** reverse data effects.

## Sign-off (blank until owner fills)

| Role | Name | Date | Decision |
| --- | --- | --- | --- |
| Trial authorizer | | | ☐ authorize controlled trial / ☐ deny |
| Rollback owner | | | ☐ rollback plan accepted |
| Station operator | | | ☐ station identity + single-lane confirmed |

Authorizing a controlled trial does **not** grant production release. Production
requires the Production tier in `plans/robust_patch_revision_2a.md` § Acceptance
tiers (matrix results, counters, timing, supervisor receipts, rollback rehearsal,
owner sign-off).

## Related

- Owner cover memo: `plans/rev6_owner_cover_memo.md` (sign-off ask only)
- Charter: `plans/rev6_close_path_charter.md`
- Inventory: `plans/rev6_close_path_inventory.md`
- Run sheet stub: `plans/rev6_station_run_sheet.md` (fill only after auth sign-off)
- Team 2 brief: `maps/vector_ownership/TEAM2_WHERE_WE_ARE.md`
- Station procedure detail: `plans/robust_patch_revision_2a.md` § 5
