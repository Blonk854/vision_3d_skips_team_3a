# Sketch — once-per-component count guard (multi-section)

Recorded 2026-10-18. Design only. No Keystone bytes, no Rev7 generator, no PE
rebuild. Depends on `plans/rev6_uniqueness_sections.md` (execute-path section
filter absent).

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

### Identity (must prove before bytes)

At the count hook (`0x140736f47` inside `ExecuteOne_Component`):

| Register / field | Role today |
| --- | --- |
| `[r15+0x10]` | CAO — already the context key |
| `[rdi+0x14]` | Sub-panel slot index for the cell |
| `r13` | `CAnomalie*` (`mov r13, r9` at function entry) |
| Stock / decomp | `CCAD_Base` / `CComposant` carries `+0x14` used as sub-panel / identity material; written to `CAnomalie+0x28` before some exits |

**Candidate key (to prove):**

```
key = (cao, component_id)
component_id = dword or qword stable across section re-entry for the same CAD part
```

Proof obligations before assembly:

1. Name the exact load at the hook (or a short, register-safe sequence) that
   yields `component_id`.
2. Show two section iterations of the same CAD part produce the **same**
   `component_id` (pointer equality only if the object is not reconstructed).
3. Show distinct parts do not collide under the chosen width (e.g. 32-bit id in
   `0..N` vs pointer).
4. Show reset / CAO retirement clears the seen-set (tie to existing reset cave /
   context retire path).

If (2) fails for pointers, prefer a CAD index / id field over `CComposant*`.

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

1. **Land Option A** in a future Rev7 (or rev6.1) as an explicit single-section
   scope bit — unblocks a honest gate note for multi-section.
2. **Prove component_id** offline (short PE/decomp note).
3. **Land Option B** only after (2); keep A as compile-time or runtime fallback
   when id proof is missing.

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
