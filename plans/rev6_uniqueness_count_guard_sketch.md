# Sketch — once-per-component count guard (multi-section)

Recorded 2026-10-18. Option A is implemented in Rev7
(`tools/patch_f1_missing_n_rev7.py`, `plans/rev7_multi_section_fail_open.md`).
Option B remains design-only. Depends on `plans/rev6_uniqueness_sections.md`.

## Problem

On multi-section panels, `HandlerProduction` can run `PanelInspect` twice. The
Feature-1 count cave at `0x140736f47` keys only by CAO (`[r15+0x10]`) and
sub-panel (`[rdi+0x14]`). A second section iteration that re-enters
`ExecuteOne_Component` for the same CAD component would increment
`CELL_INSPECTED` / `CELL_MISSING` again → false threshold.

## Goal

At most one Feature-1 count sample per logical component per CAO lifetime
(panel generation), without inventing a fence and without requiring a data-side
zone-partition proof first.

## Option A — multi-section fail-open (interim, smallest)

**Behavior:** if the document is multi-section, the count cave jumps to stock
`normal` (no increment, no skip trigger). Feature-1 is single-section-only.

**Detect (pick one, prove before assemble):**

| Probe | Notes |
| --- | --- |
| `IsTstMultiSection` (`0x14052e070`) on CAO | Same pred `FUN_140695200` uses; returns byte |
| Cached flag on context claim | Set once when first claiming the CAO context if `FUN_140695200(cao)==2` |

Prefer a **context flag** set on first `claim_context` / `context_found` while the
table lock is held: one CALL to `0x140695200`, store `CONTEXT_FLAGS` bit
`MULTI_SECTION=1`, then every later count on that CAO checks the bit and
fail-opens. Avoids calling the pred on every component.

**Pros:** tiny; matches follow-on “scope Feature-1 to single-section”; no seen-set
memory.  
**Cons:** multi-section stations get no threshold skip until Option B or a
data-side partition proof.

**Acceptance:** single-section F1-A–L unchanged; multi-section panel with 4/10
Missing does **not** auto-skip (document as waived / out of scope).

## Option B — seen-set once-per-component (full uniqueness)

**Behavior:** before `lock xadd` on `CELL_INSPECTED`, look up a component key in
a per-CAO seen structure. If present → `normal` (still run stock path; do not
count). If absent → insert, then existing count/threshold logic.

### Identity (load proven — see companion proof)

At the count hook (`0x140736f47` inside `ExecuteOne_Component`):

| Register / field | Role |
| --- | --- |
| `[r15+0x10]` | CAO — already the context key |
| `[rdi+0x14]` | **Sub-panel** cell index only — **not** component id |
| `rdi` / `[rbp+0x730]` | **`CCAD_Base*`** param_7 from `ExecuteAll` — proven component pointer |
| `r13` | `CAnomalie*` (RazRes target just before hook) |

**Key (for assembly once Option B lands):**

```
key = (cao, component_ptr)   ; component_ptr = rdi at cave entry
```

Proof status (`plans/rev6_uniqueness_component_id_proof.md`):

1. Exact load — **done** (`rdi` or reload `[rbp+0x730]`).
2. Same pointer across section re-entry for the same CAD part — **still open**
   (document-owned objects expected; not PE-closed).
3. Distinct parts — distinct pointers on one CAO — **accepted** for heap CAD objects.
4. Reset clears seen-set — **still required** when implementing (tie to reset cave).

If (2) fails, fall back to Option A or a field-backed id (not `+0x14`).

### Storage (illustrative — sizes not final)

Extend the existing per-CAO context (today `CONTEXT_STRIDE = 0x5000` for 1024
sub-panel cells):

| Approach | Idea | Risk |
| --- | --- | --- |
| Bitset by dense id | If `component_id ∈ [0, MAX)` | Needs proven bound |
| Fixed open-address set | e.g. 4096 × 8-byte keys + tombstones | Full → fail-open (match context-full policy) |
| Bloom | Compact | False positive = under-count (safer than over-count for threshold) |

**Policy on full / unknown id:** fail-open to stock (`normal`), same as
`context_full` / `unsupported`. Never invent a skip.

### Placement in `count_handler_source` (rev5/rev6)

Insert after context is found/claimed and cell pointer `r11` is formed, **before**
the `CELL_STATE` / `lock xadd` path:

```
; pseudo
load component_id   ; TBD proven load
test / lookup seen[cao]
jnz  table_unlock_normal   ; already counted this panel generation
insert seen[cao], component_id
; fall through to existing CELL_STATE / xadd / threshold
```

Reset path (existing reset cave that retires contexts) must zero the seen-set
when the CAO context is cleared.

### Concurrency

Keep the existing `GLOBAL_TABLE_LOCK` around lookup+insert+count, or use a
dedicated `CONTEXT_SEEN_LOCK`. Do not unlock between insert and `xadd` (would
allow double insert). Same unwind / exception contracts as rev5 count cave.

## Option C — out of sketch scope

Data-side proof that grey-zone / component sets are disjoint across sections
(`plans/rev6_uniqueness_sections.md` residual). If that closes, Options A/B are
unnecessary for uniqueness (still useful as defense in depth).

## Recommended sequence

1. ~~Land Option A~~ — Rev7 (`plans/rev7_multi_section_fail_open.md`).
2. ~~Prove component_id load~~ — done in
   `plans/rev6_uniqueness_component_id_proof.md` (`rdi` = `CCAD_Base*`).
3. **Land Option B** with `(cao, rdi)` seen-set; keep A as fallback if
   cross-section pointer aliasing is disproven.

## Non-goals

- No change to ProductionStop / SKIP snapshot / view clear (Rev6 close-path).
- No native install authorization.
- No DWORD wider-intermediate work in this sketch.
- No claim that Option A or B is implemented in
  `Updated/Vision3D_concurrency_fix_rev6.exe`.

## Related

- Residual: `plans/rev6_uniqueness_sections.md`
- Count cave today: `tools/patch_f1_missing_n_rev5.py` `count_handler_source`
- Rev6 builder wraps rev5 count: `tools/patch_f1_missing_n_rev6.py`
