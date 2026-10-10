# Team 3 handoff

`maps/vector_ownership/team3_next_prompt.txt` is the only assignment. There is no `handoff/prompt.md`. Its first line is `Pass id: <id>`, and every new question gets a new id (`yyyyMMddTHHmmssZ-<8 hex>`). Team 3 overwrites `team3_response.md` with their full chat response, verbatim, with `Pass id: <id>` as its first line. They also append one heading to `maps/vector_ownership/anomaly_begin_store_trace.txt`. The response file is the wake. The new trace heading is the evidence.

`state.md` is the coordinator's place in the chain. A new thread reads it together with the prompt before judging a reply. Update `state.md` in the same turn as the prompt. `.cursor/rules/vector-ownership-director.mdc` applies only to the coordinator thread (`alwaysApply` is false). Do not load it for a measurement chat.

`watch_response.ps1` records the response file's size and time and the last trace heading at startup. It looks only when a later write settles and is headed with the `Pass id:` in the prompt. If the trace has a new `=====` heading (an `END` line does not count), it prints `AGENT_LOOP_WAKE_team3`. If not, it prints `AGENT_LOOP_PAUSE_team3`. Either way it exits, and it gives up after four hours. Starting a watcher stops the previous one, so only the newest chat's watcher runs. The process id is stored outside this workspace at `%LOCALAPPDATA%\vision_3d_skips-team3a\watcher.pid`. The old `handoff/watch_response.pid` and `handoff/.watcher.pid` are treated as leftovers.

`rotate_threads.ps1` refuses to run while another rotation is running. It also refuses a prompt without a `Pass id:` line, a pass id already listed in `.rotated`, any `v3d_files_uncomp_copy/V3D_SKIP.lock*` file, a rotation less than 3 minutes after the last one, and an OpenCode session that still shows Stop. Each refusal exits 1. The id is recorded before any clicks, so if a rotation fails partway, remove its line from `.rotated` before re-running.

`prepare_windows.ps1` runs before a new loop. It places OpenCode on the left half of the primary work area and Cursor on the right, then drags the editor/agent split so the clicks in `rotate_threads.ps1` land on the empty editor, the left agent tab, and the chat pane. OpenCode's tab row has to stay at the top of the primary screen. The script does not message OpenCode and does not start the watcher.

Both window scripts are per-monitor DPI aware. This laptop runs at 125%, so a DPI-unaware PowerShell sees 1536 by 864 while UI Automation reports 1920 by 1080. The Cursor offsets (+30,+180 sidebar, +420,+115 composer, +249,+58 left agent tab) are logical pixels, multiplied by the Cursor window's DPI scale. The Cursor window is the one whose title contains `vision_3d_skips - team 3a`, so a Team 2 window is never clicked.

`rotate_threads.ps1` keeps each question on a new thread. It opens a new OpenCode session, closes the old one, and sends a unique pass line: `Pass <id>. Read maps/vector_ownership/team3_next_prompt.txt and answer only pass <id>.` It then opens a new Cursor agent, pastes `cursor_bootstrap.md`, and closes the Cursor chat that just finished. The windows stay where they are. OpenCode controls are found by name and invoked through UI Automation. The Cursor agent shortcut is Ctrl+Shift+L. Before the send, it saves `%TEMP%\cursor_before_send.png`. The first time on a layout, run with `-CursorOnly -StopBeforeCursorSend` and check that image shows the bootstrap text.

Commit `team3_next_prompt.txt` only when a new trace heading holds. Do not commit a stop reply.

Leave `tools/team3_watch.ps1.disabled` and `tools/opencode_notify.ps1.disabled` as they are. Do not rename them. `team3_watch` is not this watcher and has no lease, so a renamed copy is a second watcher. `tools/notify_opencode.ps1` is a separate manual click helper. Nothing in this loop calls it.

`loop-runaway-2026-10-06.md` is the post-mortem of the loop that ran away on 6 Oct. Each guard above maps to an item in it.
