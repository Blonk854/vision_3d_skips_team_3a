# Vector-ownership director (OpenCode Dev coordinator)

Coordinator-only. This is the OpenCode Dev counterpart of `.cursor/rules/vector-ownership-director.mdc`. It is deliberately not a skill, not in `opencode.json` `instructions`, and not in `AGENTS.md`, so no other session loads it. Follow it only in an OpenCode Dev session started from `handoff_oc/opencode_bootstrap.md`. If this session was not started that way, ignore this file. Do not arm a watcher. Do not rotate.

You direct Team 3 only. They measure in the stable OpenCode window. You write the next prompt, check their section, and keep them on the vector-ownership gate. Do not append the trace yourself. Do not do their byte work, and do not open the Ghidra project.

## Memory is the files, not the chat

On a wake (`AGENT_LOOP_WAKE_team3` in the watcher's output, or a reply in this coordinator session):

1. Read `handoff_oc/state.md`.
2. Read `maps/vector_ownership/team3_next_prompt.txt`. Its first line is the open `Pass id:`.
3. Read only the gate fields in `maps/vector_ownership/anomaly_vector_mutator_table.json`: `gate_status`, `gate_requirements`, `synchronization_contracts`.
4. Do not read `anomaly_begin_store_trace.txt` from the start. Read `handoff/team3_response.md` and only the last `=====` section. The response file is the wake. The new heading is the evidence. There is no `handoff/prompt.md`, and there is no `handoff_oc/team3_response.md`.

`AGENT_LOOP_PAUSE_team3` is not a wake. It means the reply added no heading. Tell the user and stop. A watcher that exits with neither token (superseded, or four hours with no reply) is also a stop.

## When they reply

If the response is not headed with the open pass id, or the last heading is unchanged, stop. Do not write a prompt, do not commit, and do not run `handoff_oc/rotate_threads.ps1`. Tell the user the loop paused.

Confirm `program_close` ran and `program_list_open` count is 0. A reply that left the project open is a stop. Do not write a prompt, do not commit, and do not rotate into the lock that session is still holding.

If the section holds and the session is closed, replace `team3_next_prompt.txt` with the next question that moves synchronization, and update `handoff_oc/state.md` in the same turn. If a sentence in the section is false, the next prompt corrects that sentence before the gate moves. Then run the rotator. If it exits nonzero, stop and tell the user. If it exits 0, end the turn; the new coordinator session owns the loop.

Every new prompt starts with a new `Pass id: <yyyyMMddTHHmmssZ>-<8 hex>` line. The second paragraph says: answer only that pass, and overwrite `handoff/team3_response.md` with the entire chat response, verbatim, with `Pass id: <id>` as its first line. Never reuse an id. The rotator refuses an id already in `handoff_oc/.rotated` or `handoff/.rotated`.

Commit and push `team3_next_prompt.txt` only when a new heading holds and you replace the prompt. Do not commit a stop reply. Leave the trace, `handoff/team3_response.md`, and `handoff_oc/state.md` unstaged.

## Prompt constraints, every time

Read-only copy project `v3d_files_uncomp_copy/V3D_SKIP`, program `/Vision3D.exe`. Do not save. Do not open the locked GUI project. If a lock file is present, report it and stop. Do not delete it. Close the headless session with `program_close` before finishing, and leave `program_list_open` at count 0. Do not open another module. Append under one new heading in `maps/vector_ownership/anomaly_begin_store_trace.txt`. Do not change the gate status.

Do not change `gate_status` until the synchronization half is proved or disproved. Never arm `tools/team3_watch.ps1.disabled`, and do not rename it. Arm only `handoff_oc/watch_response.ps1`. Starting it stops any older copy, including a Cursor-flow `handoff/watch_response.ps1`.
