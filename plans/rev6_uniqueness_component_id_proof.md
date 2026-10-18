# Proof — `component_id` load at final-mask hook

Recorded 2026-10-18. Offline PE + retained decomp. No patch bytes.
Source SHA-256 `ccca11b2f05084b484fa5556c67f8874065dbc0b6265177d2517f81265af00f4`.

Companion sketch: `plans/rev6_uniqueness_count_guard_sketch.md`.

## Hook

Stock site `0x140736f47` in `ExecuteOne_Component` (`0x1407368d0`):

```
mov rcx, qword ptr [r15 + 0x10]   ; CAO — existing Feature-1 context key
```

Immediately prior: `call [r13+0]` RazRes-style on `CAnomalie*` (`r13`).

## Rejected: `[rdi+0x14]` as component id

| Fact | VA / evidence |
| --- | --- |
| Early load | `0x14073698d` `mov r14d, dword ptr [rdi+0x14]` → spill `[rbp-0x6c]` |
| Use | `SkipSubPanel(cao, *(long*)(pCVar30+0x14))`; log “sub-panel #%d” |
| Count cave today | Uses `[rdi+0x14]` as **sub-panel cell index** (`SUBPANEL_SLOTS`) |

So `+0x14` is the **sub-panel index**, shared by every component on that board.
It is the right cell key and the **wrong** once-per-component key.

Also rejected: `CAnomalie+0x28` — written **after** the hook
(`*(param_4+0x28) = uVar14` in decomp) with that same sub-panel value, not a
per-part id available at `0x140736f47`.

## Proven load: `CCAD_Base*` in `rdi` / `[rbp+0x730]`

### Parameter home

x64 home for the 7th argument is `[rbp+0x730]` given
`lea rbp, [rax-0x6f8]` at `0x1407368ea`.

`ExecuteAll_Components` calls:

```
FUN_1407368d0(param_1, param_3, param_5, plVar4, param_6, param_4, plVar1);
```

`plVar1` is the `CCAD_Base` / `CComposant` from the zone component vector
(`maps/decomp/ExecuteAll_Components.c`). That pointer is param_7 → `[rbp+0x730]`.

### No overwrite of the home

In `[0x1407368d0, 0x140736f47)` the only references to `[rbp+0x730]` are reads:

| VA | Insn |
| --- | --- |
| `0x140736978` | `mov rdi, qword ptr [rbp+0x730]` |
| `0x140736c59` | `mov rdi, qword ptr [rbp+0x730]` |
| `0x140736d9f` | `mov rdi, qword ptr [rbp+0x730]` |

No store to that slot. The callee does not replace param_7.

### `rdi` at the hook

Last writer of `rdi` before `0x140736f47` is `0x140736d9f`
(`mov rdi, [rbp+0x730]`). No later `mov rdi, …` before the hook.

Therefore at the Feature-1 count cave entry (after the patched `mov rcx,[r15+0x10]`
is replaced, registers otherwise match stock):

```
component_ptr = rdi                    ; CCAD_Base*
; equivalent reload if rdi were clobbered by future cave prologue:
; component_ptr = qword ptr [rbp + 0x730]
```

Null check: fail-open to stock if `rdi == 0` (should not occur on the live path
that reaches RazRes).

## Identity meaning

| Key | Meaning |
| --- | --- |
| `cao = [r15+0x10]` | Production document / CAO context (existing) |
| `component_id = rdi` (`CCAD_Base*`) | The CAD component object being inspected |

Seen-set key for Option B: `(cao, component_ptr)` as two qwords, or
`component_ptr` alone inside an already CAO-scoped context table.

## Cross-section stability (partial)

| Claim | Status |
| --- | --- |
| Hook load is always the `CCAD_Base*` passed into this `ExecuteOne` call | **Proven** |
| That pointer is the CAD model object from `ExecuteAll`’s vector, not a per-call temp | **Proven** (argument plumbing) |
| A second section iteration that inspects the same CAD part uses the **same** pointer value | **Not PE-closed** — requires that the zone component vectors of both section passes alias the same `CCAD_Base` instances (normal for document-owned CAD; not shown by a second load here) |

If a future data pass shows section-2 vectors hold copies with different addresses,
Option B must switch to a field-backed id (still not `+0x14`) or fall back to
Option A (multi-section fail-open).

## Count-cave use (not implemented)

```
; after existing CAO context claim, before CELL_INSPECTED xadd
test rdi, rdi
jz   fail_open_normal
; lookup/insert seen[cao][rdi]
; if already present -> fail_open_normal
; else fall through to existing threshold logic
```

Preserve `[rdi+0x14]` as the sub-panel cell selector only.

## Related

- Uniqueness residual: `plans/rev6_uniqueness_sections.md`
- Guard sketch: `plans/rev6_uniqueness_count_guard_sketch.md`
- Decomps: `maps/decomp/ExecuteOne_Component.c`, `maps/decomp/ExecuteAll_Components.c`
