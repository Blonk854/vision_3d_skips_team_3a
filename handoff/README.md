# Team 3 handoff

`maps/vector_ownership/team3_next_prompt.txt` is the only assignment. There is no `handoff/prompt.md`.

Team 3 overwrites `team3_response.md` with their full chat response, verbatim. They also append one heading to `maps/vector_ownership/anomaly_begin_store_trace.txt`. The response file is the wake. The new trace heading is the evidence.

`state.md` is the coordinator's place in the loop, including the loop guard block. A new thread reads it together with `team3_next_prompt.txt` before judging a reply. Update `state.md` in the same turn as the prompt. `.cursor/rules/vector-ownership-director.mdc` applies only to the coordinator thread (`alwaysApply` is false). Do not load it for a measurement chat.

The loop is off. `watch_response.ps1` and `rotate_threads.ps1` are renamed `.disabled`, and the loop guard `status` is `off`. Renaming the scripts does nothing until a human sets `status` to `running`. The scripts never set it back.

`loop_guard.ps1` is the gate. It stops at 10 rotations total and 10 in an hour. It waits at least 3 minutes between rotations. A reply that adds no `=====` heading pauses the loop and does not wake the coordinator. A second identical stop (same heading, same text aside from the clock) stops it until a human sets `identical_stops` back to 0. One resume of the same question requires `allow_one_resume: yes`. Before a rotation it checks `v3d_files_uncomp_copy/V3D_SKIP.lock*`. A live holder (ghidra, pyghidra, or the headless MCP) or an operating-system lock stops the loop. A lock nobody holds is moved to `handoff/stale_locks/` and the loop pauses instead of rotating into it.

`watch_response.ps1` records the response file's size and time at startup and looks only when a later write settles. It holds `handoff/watch_response.pid` with no share, so a second copy exits. It prints `AGENT_LOOP_WAKE_team3` only when the guard allows a new heading. A pause prints `AGENT_LOOP_PAUSE_team3` and writes `handoff/LOOP_ALERT.txt`.

`rotate_threads.ps1` runs the same guard again before it touches a window. It refuses to open a Cursor chat unless it can see exactly one chat already, and it aborts if it cannot close the old chat. `tracked_open_chats` is set to 2 before the new agent shortcut and back to 1 only after that close is proved, so a missed close cannot grow a third chat. It then opens a new OpenCode session, closes the old one, and sends `Continue from maps/vector_ownership/team3_next_prompt.txt`. The new Cursor agent is pasted `cursor_bootstrap.md`. Window placement is unchanged: OpenCode at -2,0 807 by 870 and Cursor at 805,0 731 by 864, in the 1536 by 864 view this PowerShell sees.

Commit `team3_next_prompt.txt` only when a new trace heading holds. Do not commit a stop reply.

Leave `tools/team3_watch.ps1.disabled` and `tools/opencode_notify.ps1.disabled` as they are. Do not rename them. `team3_watch` has no pid lock, so a renamed copy is a second watcher. `tools/notify_opencode.ps1` is a separate manual click helper. Nothing in this loop calls it.

`handoff/test_loop_guard.ps1` checks the gate without opening a window.
