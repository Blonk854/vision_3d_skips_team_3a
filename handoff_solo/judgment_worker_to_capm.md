# Judgment pass: `worker_to_capm` (after sync-byte walk)

Use this **only after** the solo sync-byte walk has stopped at the sync-walk end (`0x1406a3000` exclusive) or another mission stop. Do **not** use `pass_template.md` or `advance_pass.ps1` for this. This is one judgment pass, not address+1.

Paste the fenced block below into a **fresh** OpenCode / strong-model session (or hand it to a human). Replace `{{PASS_ID}}` with a new id (`yyyyMMddTHHmmssZ-` + 8 hex). Do not leave braces in the pasted assignment.

## What this pass decides

Only this field, and only with evidence:

`maps/vector_ownership/anomaly_vector_mutator_table.json` → `synchronization_contracts.worker_to_capm.barrier`

Current value (must still match before you start):

`NONE PROVEN - no memory fence, no atomic, no lock on inner vector`

Gate MD5 must still be `3C05BBB66D1463CB3B7CA0F1EDC78AEB` unless this pass **explicitly** upgrades and you recompute/report the new MD5. Default outcome: **leave the JSON untouched**.

Do **not** decide `destructor_vs_workers` or change `gate_status` in this pass. Those stay for a later judgment.

## Evidence already on the table

Read before measuring again:

- `maps/vector_ownership/TEAM2_WHERE_WE_ARE.md` (path anchors; recompute with the checker if you rely on file bytes)
- Trace headings / sections covering:
  - `ExecuteOne_Component` slot store `0x140737411` and epilogue through `0x1407374e8`
  - Worker wait `0x1406a1b6f` (`WaitForMultipleObjects`)
  - Treatment call `0x1406a1c09`, SetEvent `0x1406a1c16`, handler return `0x1406a1c7b`
- The raw sync-byte strip ending at the last traced address below `0x1406a3000` (heading words are hex bytes or `unreadable`; they are not a proved fence by themselves)

Contract path under judgment:

`ExecuteOne_Component` writes `CAnomalieProd` → event signal → `CAPM_SetInspectionStatus` reads

## Upgrade bar (all must hold)

Upgrade `worker_to_capm.barrier` only if you can name **one** concrete mechanism on that path with addresses:

1. A memory fence (`MFENCE` / equivalent), **or**
2. An atomic RMW with `LOCK` (first byte `F0`) that orders the inner-vector publish, **or**
3. A lock/critical section that clearly guards the inner vector publish/read pair

And you can show it sits **between** the worker write and the CAPM read (or is the release/acquire pair that does that job).

`WaitForMultipleObjects` / `SetEvent` alone are **not** enough to upgrade. Fixed-capacity alone is **not** enough. Absence of `push_back` is already recorded under `inner_vector_locks` and does not upgrade `worker_to_capm.barrier`.

If the bar is not met: keep `NONE PROVEN…`, leave the JSON untouched, and say so.

```
Pass id: {{PASS_ID}}

Answer only pass {{PASS_ID}}. When you finish, overwrite handoff/team3_response.md with your entire chat response, verbatim, and make its first line `Pass id: {{PASS_ID}}`. Do not append to that file.

This is the worker_to_capm judgment pass after the solo sync-byte walk. Do not run handoff_solo/advance_pass.ps1. Do not mint an address+1 prompt. Do not continue the raw byte walk.

Read-only. Copy project v3d_files_uncomp_copy/V3D_SKIP, program /Vision3D.exe. Do not save. Do not open the locked GUI project. Do not open another module.

Check the lock files when you start. If either `v3d_files_uncomp_copy/V3D_SKIP.lock` or `v3d_files_uncomp_copy/V3D_SKIP.lock~` is present, stop, report both sizes and timestamps, do not delete them, and do not edit the trace or the gate JSON. When no lock file is present, open the copy project read-only. Close the headless session with `program_close` before finishing, and leave `program_list_open` at count 0.

Read maps/vector_ownership/TEAM2_WHERE_WE_ARE.md and the relevant sections of maps/vector_ownership/anomaly_begin_store_trace.txt first. Optionally run `python maps/vector_ownership/team2_progress_check.py` from the repo root (read-only).

Question: On the path ExecuteOne_Component writes CAnomalieProd -> event signal -> CAPM_SetInspectionStatus reads, is there a proved memory fence, atomic (LOCK), or lock that orders the inner-vector publish before the CAPM read?

You may use listing/decompiler/xrefs as needed for this judgment pass. Prefer confirming the known anchors:
- slot store 0x140737411 through ExecuteOne_Component RET 0x1407374e8
- wait 0x1406a1b6f, treatment 0x1406a1c09, SetEvent 0x1406a1c16, handler RET 0x1406a1c7b
- CAPM_SetInspectionStatus read side only as far as needed to see whether a fence/lock/atomic appears before the vector read

Do not scan all of .text. Do not resume the sync-byte strip.

Default action: do not edit maps/vector_ownership/anomaly_vector_mutator_table.json. Report its MD5 before and after (both must stay 3C05BBB66D1463CB3B7CA0F1EDC78AEB unless you upgrade).

Upgrade is allowed only if the upgrade bar in handoff_solo/judgment_worker_to_capm.md is fully met. If you upgrade, change only synchronization_contracts.worker_to_capm.barrier to a precise new string that names the mechanism and addresses, leave gate_status unchanged, leave destructor_vs_workers unchanged, and report the new MD5.

Append exactly one new section to maps/vector_ownership/anomaly_begin_store_trace.txt. First line: `===== Worker to CAPM judgment =====`. Last line: `===== END =====`. Inside it, write:
- `Verdict:` then one of `NONE PROVEN` or `UPGRADED` or `INCONCLUSIVE`.
- `Barrier field after this pass:` the exact string now in the JSON (or the old string if untouched).
- `Evidence:` three to eight short bullets with addresses. No novel instruction quotes beyond what you need for the verdict.
- `JSON edited:` `no` or `yes`.
- `This closes the solo sync-byte walk's follow-on judgment for worker_to_capm only.`

Do not upgrade destructor_vs_workers. Do not change gate_status. Report whether a lock file remains in v3d_files_uncomp_copy.
```
