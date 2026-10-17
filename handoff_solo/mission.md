# Solo sync-byte mission (no director)

One OpenCode session owns the whole loop. There is no OpenCode Dev coordinator, no Cursor director, no `rotate_threads.ps1`, and no response watcher. You measure, you append evidence, you write the next pass, and you continue.

`handoff/` (Cursor director) and `handoff_oc/` (OpenCode Dev director) stay untouched. Run only one flow at a time. If either director flow is active, ignore this file.

## Goal

Finish the **synchronization half** of the vector-ownership gate by walking `.text` one raw byte at a time and appending each result under a new heading in `maps/vector_ownership/anomaly_begin_store_trace.txt`.

You are still in the synchronization half. Do not prove or disprove the gate. Do not upgrade `synchronization_contracts.worker_to_capm`. Do not change `gate_status`. Leave `maps/vector_ownership/anomaly_vector_mutator_table.json` untouched. Its MD5 must stay `3C05BBB66D1463CB3B7CA0F1EDC78AEB`.

## How each pass works

1. Read `maps/vector_ownership/team3_next_prompt.txt`. Its first line is `Pass id: <id>`. That file is the only assignment.
2. Do exactly that pass. One `memory_read`, length 1, at the address the prompt names.
3. Append exactly one new `=====` section to the trace (response text alone is not enough).
4. Overwrite `handoff/team3_response.md` with your entire reply. First line: `Pass id: <id>`.
5. Close the headless session (`program_close`, then `program_list_open` count 0).
6. If the pass held, run `handoff_solo/advance_pass.ps1` (fills the next prompt from the template; do not hand-edit placeholders), then immediately start that new pass in the same turn. Do not wait for a human. Do not open a new session unless the chat context is exhausted.

## Hard rules (every pass)

- Read-only copy project `v3d_files_uncomp_copy/V3D_SKIP`, program `/Vision3D.exe`. Do not save. Do not open the locked GUI project. Do not open another module.
- If `v3d_files_uncomp_copy/V3D_SKIP.lock` or `v3d_files_uncomp_copy/V3D_SKIP.lock~` is present: stop, report sizes and timestamps, do not delete them, do not edit the trace, do not write a next prompt.
- Raw read only: `memory_read` once. No `listing_code_unit_at`, no `memory_blocks_list`, no disassembly, no creating or clearing code/data, no quoting instructions.
- Address form: backtick + `0x` + exactly nine lowercase hex digits + backtick. Check the address string before the call.
- Valid range: `0x140001000` .. `0x140d509ff`. If the next address would leave that range, stop and tell the user the sync walk hit the bound.
- New heading = exact current last non-`END` `=====` heading from the trace, plus one space, plus one word (`bb` from the byte, or `unreadable`). Copy the heading from the file; do not rebuild it from memory.
- Gate file MD5 before and after must match. Report both.
- Never reuse a pass id. New id: UTC `yyyyMMddTHHmmssZ` + `-` + 8 lowercase hex.
- Do not arm `handoff/watch_response.ps1`, `handoff_oc/watch_response.ps1`, or anything under `tools/*.disabled`.

## Stay-on-task rules

- Do not ask for sign-off, approval, confirmation, or whether to continue.
- Do not offer plans, options, or “should I proceed?” — proceed or stop per the stop list below.
- Do not summarize the whole mission between passes. One pass closeout, then the next pass.
- Do not rewrite old trace sections. Append only.
- Do not widen scope (no other addresses, no other files, no gate edits) to look helpful.

## Stop (tell the user, do not self-advance)

Stop and end the turn when any of these hold:

- A lock file is present
- The prompt pass id does not match what you were asked to answer
- You could not append a new heading (or the last heading is unchanged after your write)
- `program_list_open` is not 0 after closeout
- Gate MD5 changed
- Next address would be outside `0x140001000` .. `0x140d509ff`
- The same failure repeats twice in a row (same stop reason)

A successful byte or a successful `unreadable` is progress. Write the next pass and continue.

## Self-advance (only after a holding pass)

1. Confirm the new trace section exists and ends with `===== END =====`, and its `Address:` matches the pass you just did.
2. Run:
   `powershell -NoProfile -ExecutionPolicy Bypass -File handoff_solo/advance_pass.ps1`
   That script checks the last trace `Address:` against the open prompt, mints a new pass id, copies the heading tail from the trace, and overwrites `team3_next_prompt.txt`. If it exits nonzero, stop and tell the user. Do not pass `-Force` unless a human asked you to repair a stuck prompt.
3. Optionally commit and push only `team3_next_prompt.txt` when the new heading holds. Leave the trace and `handoff/team3_response.md` unstaged.
4. Immediately perform the new pass in this same turn.

## Open work right now

Open pass in `team3_next_prompt.txt`: read `0x1406a1fd6` (see that file for the full text and pass id). After it holds, continue with `0x1406a1fd7`, then `+1`, until a stop condition fires.
