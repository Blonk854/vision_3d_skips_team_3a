# Final-mask uniqueness — sections sharing a component

Recorded 2026-10-18. Offline PE + retained decomp only. No patch bytes selected.
Does not authorize native install.

## Open question (inherited)

`HandlerProduction` can call `PanelInspect` on **two** section iterations when
`FUN_140695200` returns 2 (`IsTstMultiSection` and related pred). Prior work
proved one final-mask hit per `ExecuteOne_Component` call and one such call per
component-vector slot per zone execution. The unresolved part was whether those
two section iterations can walk the **same** component to `0x140736f47`.

## What this pass proved

### Section loop induction

| Step | VA / fact |
| --- | --- |
| Seed | `XOR ESI,ESI` then `MOV [doc+0x3978], ESI` at `0x1406a34a1` |
| Bound | `CALL 0x140695200` → 1 or 2 |
| Mid-body | `MOV R15D, 1` at `0x1406a367b`; `SHL EDX, CL` with `CL = old +0x3978`; store at `0x1406a375a` |
| Multi-section values | iteration A ends with `+0x3978 == 1`; iteration B ends with `+0x3978 == 2` |
| `PanelInspect` | `CALL 0x1406a6a30` at `0x1406a39ea` on status==3, **after** the SHL store |

### No section filter on the inspect execute path

| Function | VA | `document+0x3978` uses |
| --- | --- | --- |
| `ExecuteAll_Components` | ~`0x140735120` | **none** (whole `.text` scan) |
| `ExecuteOne_Component` | `0x1407368d0` | **none** |
| Zone executor | `0x140735f10` | log args only (`Executing` / `SKIPED` / empty strings) |
| `GetZoneAnalyse` | `0x14045c540` | **none** — indexes `[doc+0x2448)` by zone id; copies SKIPED byte from zone entry `+0x10` |

`.text` has 31 instruction sites with displacement `0x3978`. None fall inside
`ExecuteAll` / `ExecuteOne`. PanelInspect / ReceiveGreyZones uses are logging,
ConveyorNext when `section < bound`, and a grey-zone pre-count adjustment when
`bound==1` or `section==2` — not a component-vector filter before final-mask.

### SKIPED is not a live section test

Zone executor skips `ExecuteAll_Components` when `FUN_14052b850(analyse, 0x100)==1`
and analyse flag `+0x10 == 1`. That flag is copied from the zone table entry by
`GetZoneAnalyse` without reading `+0x3978`. So SKIPED is a stored zone property,
not “wrong section for this iteration” computed at the hook.

## Disposition

| Claim | Status |
| --- | --- |
| Same component cannot reach final-mask twice across section iterations | **Not established** |
| Execute path filters components by `+0x3978` | **DISPROVEN** (absent) |
| Grey-zone / zone-table sets of the two iterations are always disjoint | **STILL OPEN** (acquisition / data; ConveyorNext suggests different FOV but does not prove disjoint CAD components) |

**Gate row stays Partial**, with a sharpened residual: uniqueness for multi-section
requires either (a) a data-side proof that section iterations never share a
component that reaches `ExecuteAll_Components`, or (b) a patch-side
once-per-component (or once-per-panel) guard at the count hook.

Single-section panels (`FUN_140695200 == 1`) are outside this residual: one
section iteration only.

## Evidence pointers

- Prior multiplicity: `plans/robust_patch_revision_2a_status.md` § Final-mask multiplicity
- Maps: `maps/rev2a_final_mask_second_pass.json`, `maps/rev2a_final_mask_shift.json`,
  `maps/rev2a_entry_gate_dispatch.json` (zone executor decomp),
  `maps/rev2a_entry_gate_second_pass.json` (ReceiveGreyZones decomp)
- Source PE: SHA-256 `ccca11b2f05084b484fa5556c67f8874065dbc0b6265177d2517f81265af00f4`

## Follow-on options (not started)

1. Data-side: prove zone analyse / grey-zone membership partitions by section bit.
2. Patch-side: Feature-1 count ignores a second final-mask for the same component
   identity within a panel generation (or disable threshold on multi-section).
3. Scope: document Feature-1 as single-section-only until (1) or (2) lands.
