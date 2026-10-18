# Rev7 — multi-section Feature-1 fail-open (Option A)

Recorded 2026-10-18. Implements
`plans/rev6_uniqueness_count_guard_sketch.md` Option A on top of Rev6.

## Behavior

| Document | Feature-1 count / threshold skip |
| --- | --- |
| Single-section (`FUN_140695200` → 1) | Unchanged from Rev6 |
| Multi-section (`FUN_140695200` → 2) | Fail-open: no cell increment, no SkipSubPanel from the count cave |

On first CAO context claim, the count cave calls `0x140695200`. If the return is
2, it `lock bts` bit **1** of `CONTEXT_FLAGS` (bit 0 remains the UI-posted latch).
Every later count on that CAO `bt`s bit 1 and, if set, unlocks and takes the stock
`normal` path.

## Builder / artifact

```
python tools/patch_f1_missing_n_rev7.py
python tools/verify_hardened_patch.py --revision rev7
```

Output: `Updated/Vision3D_concurrency_fix_rev7.exe` (gitignored).

## Non-goals

- Option B seen-set (`CCAD_Base*` in `rdi`) — not in this revision
- Changing Rev6 close-path caves — retained unchanged

## Trial packaging

Rev7 is the unsigned station-trial candidate. See
`plans/rev6_native_install_authorization.md` and
`plans/rev6_owner_cover_memo.md`. Native install still requires owner sign-off.

## Related

- Sketch: `plans/rev6_uniqueness_count_guard_sketch.md`
- Id proof: `plans/rev6_uniqueness_component_id_proof.md`
- Sections residual: `plans/rev6_uniqueness_sections.md`
