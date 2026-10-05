# Team 3 handoff

`maps/vector_ownership/team3_next_prompt.txt` is the only assignment. There is no `handoff/prompt.md`.

Team 3 overwrites `team3_response.md` with their full chat response, verbatim. They also append one heading to `maps/vector_ownership/anomaly_begin_store_trace.txt`. The response file is the wake. The new trace heading is the evidence.

`state.md` is the coordinator's place in the loop. A new thread reads it together with `team3_next_prompt.txt` before judging a reply. Update `state.md` in the same turn as the prompt. The always-on rule is `.cursor/rules/vector-ownership-director.mdc`.

`watch_response.ps1` records the response file's size and time at startup and wakes only when a later write settles. The wake line tells the coordinator to judge, write the next prompt, and run `rotate_threads.ps1`.

`rotate_threads.ps1` keeps each question on a new thread. It opens a new OpenCode session, closes the old one, and sends `Continue from maps/vector_ownership/team3_next_prompt.txt`. It then opens a new Cursor agent, pastes `cursor_bootstrap.md`, and closes the Cursor chat that just finished. The windows stay where they are. OpenCode controls are found by name. The Cursor agent shortcut is Ctrl+Shift+L, and the new composer is clicked relative to the Cursor window. The old chat is closed by clicking the left tab's title, measured from the tab row. It does not use a fixed tab offset, and it does not close anything unless two chat tabs are visible.

Leave `tools/team3_watch.ps1` and `tools/opencode_notify.ps1` stopped while this watcher is running.
