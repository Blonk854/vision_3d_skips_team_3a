Pass id: 20261018T202924Z-755a7879

## Verdict

`JOIN_ABSENT`. Leave `anomaly_vector_mutator_table.json` untouched.

Gate MD5 before and after: `3C05BBB66D1463CB3B7CA0F1EDC78AEB`.

## Question

On document destruction, does ProductionStop (`0x1406920f0`) join workers before ProductionDoc_dtor (`0x14067fc20`) frees inner vectors via DeleteVector / zone destruction?

## Method

- No `V3D_SKIP.lock` / `V3D_SKIP.lock~` at start or end.
- Opened copy project `v3d_files_uncomp_copy/V3D_SKIP`, program `/Vision3D.exe`, read-only (no save).
- Listed CALL sites in ProductionDoc_dtor; xrefs to ProductionStop; decompiled dtor and sole code caller `FUN_14068da40`.
- MCP session closed; `program_list_open` count 0. Local measure also released the program and closed the project.

## Evidence

- ProductionDoc_dtor (`FUN_14067fc20` at `0x14067fc20`, size 1037) has **no** CALL to ProductionStop (`0x1406920f0`). Decompiled C does not mention ProductionStop.
- Same body **does** call `DeleteVector` at `0x14067fd30` (`CALL 0x140527b50`) and Zone_dtor `FUN_14066e530` at `0x14067ff01` (`CALL 0x14066e530`).
- ProductionStop xrefs: DATA at `0x1412cf6f4`, DATA at `0x140fcf5b8`, and one `UNCONDITIONAL_CALL` from `0x14068da61` in `FUN_14068da40` (`0x14068da40`).
- That sole code caller is the OnCmdMsg-style override (magic `0x004EB1CF` / `0x4e` half present in its decomp); it is **not** on the ProductionDoc_dtor path.
- No other join stops workers before DeleteVector / Zone_dtor on the measured destruction path.

## Contract after this pass

JSON still claims no ProductionStop join on destruction; UAF risk if workers are in-flight remains documented. `worker_to_capm.barrier` and `gate_status` unchanged.

## Trace

Appended `===== Destructor vs workers judgment =====` … `===== END =====` to `maps/vector_ownership/anomaly_begin_store_trace.txt`.

## Locks / open programs

- Lock files in `v3d_files_uncomp_copy`: none remaining.
- `program_list_open` count: 0.
- JSON edited: no.
