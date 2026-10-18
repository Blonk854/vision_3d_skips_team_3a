# Team 3a progress for Team 2

Recorded 2026-10-18 (Rev6 close-path). Pull a commit that contains
`plans/rev6_close_path_charter.md` and gate MD5 `FAE48EA3F85684EF0B69A542FF06CBED`.

```
python maps/vector_ownership/team2_progress_check.py
python tools/verify_hardened_patch.py --revision rev6 --code-only
```

`v3d_files_\Vision3D.exe`: 28,738,048 bytes, SHA-256
`ccca11b2f05084b484fa5556c67f8874065dbc0b6265177d2517f81265af00f4`.

## Gate

`maps/vector_ownership/anomaly_vector_mutator_table.json` MD5
`FAE48EA3F85684EF0B69A542FF06CBED`.

| Field | Value |
| --- | --- |
| `gate_status` | CLOSED on growth; torn-write residual accepted; Rev6 close-path join/snapshot patched |
| `worker_to_capm.barrier` | **NONE PROVEN** — residual accepted under fixed-capacity |
| `destructor_vs_workers` | **Patched in Rev6** — ProductionStop at dtor entry before free |
| Late SKIP callback / `+0x5838` | **Patched in Rev6** — snapshot swap + view clear |

## Rev6 close-path (offline)

Builder: `tools/patch_f1_missing_n_rev6.py` →
`Updated/Vision3D_concurrency_fix_rev6.exe`.

| Hook | Stock VA | Role |
| --- | --- | --- |
| ProductionDoc_dtor | `0x14067fc20` | CALL `ProductionStop` (`0x1406920f0`) then stock body |
| View dtor | `0x1406abc60` | Clear `document+0x5838` via `view+0xe8` |
| SKIP refresh | `0x1406adaf0` | Swap `document+0x23e0` to patch snapshot for stock body |
| SkipList_Reset | `0x140541050` | After stock return, publish empty snapshot |
| SkipList_Add | `0x140541020` | After SetAtGrow thunk, capture live `+0x23e0` |
| SkipAllSubPanels | `0x140540ef0` | After stock body, capture live `+0x23e0` |
| SkipSubPanel wrap | `0x140736fcb` | After stock skip, capture via `rbx` document |

Charter/inventory: `plans/rev6_close_path_charter.md`,
`plans/rev6_close_path_inventory.md`.

Native install is not authorized by this brief. Owner sign-off ask:
`plans/rev6_owner_cover_memo.md`. Request checklist:
`plans/rev6_native_install_authorization.md` (unsigned).

## Follow-ons

- Final-mask uniqueness: execute-path section filter **DISPROVEN absent**; residual
  is whether section grey-zone/component sets can intersect — see
  `plans/rev6_uniqueness_sections.md` (gate row still Partial). Count-guard sketch:
  `plans/rev6_uniqueness_count_guard_sketch.md`; component id load proof:
  `plans/rev6_uniqueness_component_id_proof.md` (`rdi` = `CCAD_Base*`; not implemented)
- DWORD wider-intermediate product
- Optional ReloadDoc/RegistryRead capture if single-lane traffic needs them
- Owner sign-off on `plans/rev6_native_install_authorization.md` before any station trial
- Fill `plans/rev6_station_run_sheet.md` during that trial (stub until authorized)

## Bytes Team 2 can still re-read

The worker→CAPM stock bytes in the executable (slot store, SetEvent, waits) are
unchanged and still underwrite **NONE PROVEN**. See
`python maps/vector_ownership/team2_progress_check.py`.

## Frontier

Latest judgment response remains pass `20261018T202924Z-755a7879`
(`JOIN_ABSENT` on stock). Rev6 patch is the remediation, not a new judgment
pass. Trace last heading: `Destructor vs workers judgment`.
`team3_next_prompt.txt` is a closed stub.
