# Judgment pass: `destructor_vs_workers` (after worker_to_capm judgment)

Use this **only after** the `Worker to CAPM judgment` section is in the trace. Do **not** use `pass_template.md` or `advance_pass.ps1`. This is one judgment pass, not address+1.

Preferred: run `handoff_solo/write_destructor_judgment_pass.ps1`. That mints `{{PASS_ID}}` and overwrites `maps/vector_ownership/team3_next_prompt.txt`. Then answer that file in a fresh strong-model session.

Manual fallback: paste the fenced block below yourself, replacing `{{PASS_ID}}` with a new id (`yyyyMMddTHHmmssZ-` + 8 hex). Do not leave braces in the pasted assignment.

## What this pass decides

Only the `destructor_vs_workers` contract, and only with evidence:

`maps/vector_ownership/anomaly_vector_mutator_table.json` → `synchronization_contracts.destructor_vs_workers`

Current claim (must still match before you start unless you prove otherwise):

| Field | Value |
|-------|--------|
| `path` | `ProductionDoc_dtor frees inner vectors via Zone_dtor` |
| `join_point` | `ProductionStop (0x1406920f0) is ONLY join point` |
| `production_stop_callers` | `ONLY from document vtable slot +0x28 with magic 0x004EB1CF - NEVER from close/destruction` |
| `risk` | `Document destruction can free inner vectors while workers still writing - USE-AFTER-FREE` |
| `mitigation` | `Ensure ProductionStop called before document destruction. Current code path: document dtor calls DeleteVector WITHOUT ProductionStop join.` |

Also note `outer_vector.mutator_table` entry for `ProductionDoc_dtor` (`0x14067fc20`): `synchronization` = `NO ProductionStop join - UNSAFE if workers in-flight`.

Gate MD5 must still be `3C05BBB66D1463CB3B7CA0F1EDC78AEB` unless this pass **explicitly** edits the JSON and you recompute/report the new MD5. Default outcome: **leave the JSON untouched**.

Do **not** change `worker_to_capm.barrier` or `gate_status` in this pass.

## Evidence already on the table

Read before measuring again:

- `maps/vector_ownership/TEAM2_WHERE_WE_ARE.md`
- Trace section `===== Worker to CAPM judgment =====` (prior pass; leave it alone)
- Gate JSON `synchronization_contracts.destructor_vs_workers` and `outer_vector` destructor notes
- Optional decomps under `maps/decomp/` if present for ProductionStop / document dtor

Contract path under judgment:

`ProductionDoc_dtor` → frees inner vectors (via `DeleteVector` / zone dtor) **without** a proved `ProductionStop` join on that path

Known anchors:

- `ProductionDoc_dtor` entry `0x14067fc20`
- `ProductionStop` entry `0x1406920f0` (claimed only join point)
- Document vtable slot `+0x28` with magic `0x004EB1CF` (claimed sole ProductionStop caller context)

## Edit bar

**Default / expected:** Verdict `JOIN_ABSENT`. Leave JSON untouched. That confirms the documented UAF risk remains.

**Edit JSON only if** you prove `JOIN_PROVEN`: on every document close/destruction path that reaches inner-vector free, `ProductionStop` (`0x1406920f0`) runs **before** the free/`DeleteVector`, with addresses. Then update only `destructor_vs_workers` fields (and the matching `ProductionDoc_dtor` `synchronization` string if needed) to name that join. Leave `gate_status` and `worker_to_capm` unchanged.

Finding extra ProductionStop callers that are **not** on the destruction path does **not** by itself clear the risk. Absence of a join on the dtor path keeps `JOIN_ABSENT`.

If evidence is incomplete: `INCONCLUSIVE`, leave JSON untouched.

```
Pass id: {{PASS_ID}}

Answer only pass {{PASS_ID}}. When you finish, overwrite handoff/team3_response.md with your entire chat response, verbatim, and make its first line `Pass id: {{PASS_ID}}`. Do not append to that file.

This is the destructor_vs_workers judgment pass. Do not run handoff_solo/advance_pass.ps1. Do not mint an address+1 prompt. Do not continue the raw byte walk. Do not re-litigate worker_to_capm.

Read-only. Copy project v3d_files_uncomp_copy/V3D_SKIP, program /Vision3D.exe. Do not save. Do not open the locked GUI project. Do not open another module.

Check the lock files when you start. If either `v3d_files_uncomp_copy/V3D_SKIP.lock` or `v3d_files_uncomp_copy/V3D_SKIP.lock~` is present, stop, report both sizes and timestamps, do not delete them, and do not edit the trace or the gate JSON. When no lock file is present, open the copy project read-only. Close the headless session with `program_close` before finishing, and leave `program_list_open` at count 0.

Read maps/vector_ownership/TEAM2_WHERE_WE_ARE.md, the Worker to CAPM judgment section in maps/vector_ownership/anomaly_begin_store_trace.txt, and synchronization_contracts.destructor_vs_workers in maps/vector_ownership/anomaly_vector_mutator_table.json first.

Question: On document destruction, does ProductionStop (0x1406920f0) join workers before ProductionDoc_dtor (0x14067fc20) frees inner vectors via DeleteVector / zone destruction?

You may use listing, decompiler, xrefs, and vtable reads as needed. Prefer these checks:
- Does ProductionDoc_dtor (0x14067fc20) call ProductionStop (0x1406920f0) before DeleteVector / inner free?
- Who calls ProductionStop? Confirm or refute "ONLY from document vtable slot +0x28 with magic 0x004EB1CF - NEVER from close/destruction".
- Is there any other join that stops workers before the free on the close/destruction path?

Do not scan all of .text. Do not resume the sync-byte strip. Do not change worker_to_capm.barrier.

Default action: do not edit maps/vector_ownership/anomaly_vector_mutator_table.json. Report its MD5 before and after (both must stay 3C05BBB66D1463CB3B7CA0F1EDC78AEB unless you edit under the edit bar in handoff_solo/judgment_destructor_vs_workers.md).

If you edit, change only destructor_vs_workers (and the ProductionDoc_dtor synchronization string if required), leave gate_status and worker_to_capm unchanged, and report the new MD5.

Append exactly one new section to maps/vector_ownership/anomaly_begin_store_trace.txt. First line: `===== Destructor vs workers judgment =====`. Last line: `===== END =====`. Inside it, write:
- `Verdict:` then one of `JOIN_ABSENT` or `JOIN_PROVEN` or `INCONCLUSIVE`.
- `Contract after this pass:` one short sentence stating whether the JSON still claims no ProductionStop join on destruction.
- `Evidence:` three to eight short bullets with addresses.
- `JSON edited:` `no` or `yes`.
- `This closes the destructor_vs_workers judgment only.`

Do not change gate_status. Report whether a lock file remains in v3d_files_uncomp_copy.
```
