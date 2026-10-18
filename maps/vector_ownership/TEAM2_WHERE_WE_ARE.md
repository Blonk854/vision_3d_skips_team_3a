# Team 3a progress for Team 2

Sync point **2026-10-18 (Rev7 trial packaging)**. Pull `main` until these match,
then run the checker. If any check fails, you are not on the same tree.

## Same-tree verify (do this first)

```
git pull
python maps/vector_ownership/team2_progress_check.py
python tools/verify_hardened_patch.py --revision rev7 --code-only
```

| Pin | Value |
| --- | --- |
| Gate file | `maps/vector_ownership/anomaly_vector_mutator_table.json` |
| Gate MD5 | `239631F19B27CA0311BFA5E9186A5C14` |
| Stock `v3d_files_/Vision3D.exe` size | 28,738,048 bytes |
| Stock SHA-256 | `ccca11b2f05084b484fa5556c67f8874065dbc0b6265177d2517f81265af00f4` |
| Latest judgment pass | `20261018T202924Z-755a7879` (`JOIN_ABSENT` on stock) |
| Trial candidate (authorized, not production) | `Updated/Vision3D_concurrency_fix_rev7.exe` |
| Rev7 builder | `tools/patch_f1_missing_n_rev7.py` |
| Rev7 local build SHA-256 (rebuild before install) | `208e7f471dc7f7443ead3cc00ed3db9a7aeca51fc99e77aaf84436b851fe1d47` |
| Rev7 size | 28,754,432 bytes |

`team2_progress_check.py` exit 0 means the brief, gate MD5, stock PE identity,
judgment frontier, and worker→CAPM stock bytes match this note. The rev7
`--code-only` verifier confirms the multi-section fail-open + close-path caves
assemble; rebuild the PE locally if you need the candidate hash.

## Gate disposition

| Field | Value |
| --- | --- |
| `gate_status` | CLOSED on growth; torn-write residual accepted; Rev6 close-path join/snapshot patched |
| `worker_to_capm.barrier` | **NONE PROVEN** — residual accepted under fixed-capacity |
| `destructor_vs_workers` | **Patched in Rev6** — ProductionStop at dtor entry before free |
| Late SKIP / `+0x5838` | **Patched in Rev6** — snapshot swap + view clear |
| Feature-1 multi-section | **Rev7 fail-open** — no threshold count/skip when `FUN_140695200` → 2 |

## Offline builders

| Revision | Builder | Output | Role |
| --- | --- | --- | --- |
| Rev6 | `tools/patch_f1_missing_n_rev6.py` | `Updated/Vision3D_concurrency_fix_rev6.exe` | Close-path baseline (offline only) |
| Rev7 | `tools/patch_f1_missing_n_rev7.py` | `Updated/Vision3D_concurrency_fix_rev7.exe` | Trial candidate = Rev6 + multi-section fail-open |

### Close-path hooks (Rev6, retained in Rev7)

| Hook | Stock VA | Role |
| --- | --- | --- |
| ProductionDoc_dtor | `0x14067fc20` | CALL `ProductionStop` (`0x1406920f0`) then stock body |
| View dtor | `0x1406abc60` | Clear `document+0x5838` via `view+0xe8` |
| SKIP refresh | `0x1406adaf0` | Swap `document+0x23e0` to patch snapshot |
| SkipList_Reset | `0x140541050` | Empty snapshot after stock return |
| SkipList_Add | `0x140541020` | Capture live `+0x23e0` after SetAtGrow |
| SkipAllSubPanels | `0x140540ef0` | Capture after stock body |
| SkipSubPanel wrap | `0x140736fcb` | Capture via `rbx` document |

Charter/inventory: `plans/rev6_close_path_charter.md`,
`plans/rev6_close_path_inventory.md`.
Rev7 note: `plans/rev7_multi_section_fail_open.md`.

## Controlled trial (not production)

Owner-delegated authorization **2026-10-18** for one single-lane maintenance-window
trial of Rev7. Not fleet / production release.

| Doc | Path |
| --- | --- |
| Cover memo (authorized) | `plans/rev6_owner_cover_memo.md` |
| Auth checklist | `plans/rev6_native_install_authorization.md` |
| Window commands + hashes | `plans/rev7_maintenance_window_checklist.md` |
| Run sheet | `plans/rev6_station_run_sheet.md` |

Operator still names the station and confirms single-lane at the window before
copy. Patched binaries stay gitignored under `Updated/`.

## Follow-ons (not blocking this sync)

- Uniqueness Option B seen-set (`rdi` = `CCAD_Base*`) — sketched/proven load only:
  `plans/rev6_uniqueness_sections.md`,
  `plans/rev6_uniqueness_component_id_proof.md`,
  `plans/rev6_uniqueness_count_guard_sketch.md`
- DWORD wider-intermediate product
- Optional ReloadDoc/RegistryRead capture

## Bytes Team 2 can still re-read on stock

Worker→CAPM stock bytes (slot store, SetEvent, waits) are unchanged and still
underwrite **NONE PROVEN**. The progress checker re-reads them.

## Frontier

Latest judgment response: pass `20261018T202924Z-755a7879`
(`JOIN_ABSENT` on stock). Rev6/Rev7 are remediation patches, not a new judgment
pass. Trace last heading: `Destructor vs workers judgment`.
`team3_next_prompt.txt` is a closed stub.
