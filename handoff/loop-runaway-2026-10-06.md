# Handoff loop runaway, 6 Oct 2026

Team 3’s watcher and rotator opened a new Cursor chat and a new OpenCode session about once a minute from roughly 1:20 AM to 1:50 AM ET. That burned Cursor usage and left about 100 chats titled “Team 3 response waiting” (51 of them created in the 1:00 hour; 69 completed, 31 aborted). Git history for the same window is about 30 commits, from 1:23 AM to 1:47 AM, each one a slightly different record of the same stop.

The worker did what its prompt said. The loop treated that stop as a reason to start another worker.

This note is for any team whose scripts poll a response file and then open a new chat. Check your copies against the list below. Team 3’s loop is still off.

## What the loop did

A PowerShell watcher polled `handoff/team3_response.md` every 3 seconds. When the file changed, it printed a wake line. The coordinator rewrote the assignment and `handoff/state.md`, then a rotator clicked through the UI: new OpenCode session, new Cursor agent, paste the bootstrap, try to close the old chat.

The assignment told the worker: if `v3d_files_uncomp_copy/V3D_SKIP.lock` is present, report it and stop. Do not delete it.

At 1:27:57 AM two lock files were on disk: `V3D_SKIP.lock` (239 bytes) and `V3D_SKIP.lock~` (0 bytes). Two orphaned `ghidra_headless_mcp` Python processes held them (PIDs 15256 and 9800, both started at 1:01 AM). Every new session saw the locks, wrote another “stopped at the lock” reply, and exited. That write woke the watcher. The watcher rotated. The next session saw the same locks.

Nothing in that cycle could make progress. The loop had no way to notice.

## What made it worse

These are separate bugs. Any one of them is enough to keep a stuck loop expensive.

1. A reply with no new evidence still counted as a wake. The rotator ran, a new prompt was written, and the stop was committed.
2. The rotator opened the next Cursor chat even when it failed to close the previous one. It only closed a chat when a screenshot showed two tab titles. Missed clicks left the old chats open, so the count grew without a bound.
3. Closing and opening depended on fixed pixel clicks for one 1536×864 layout (OpenCode at -2,0 807×870, Cursor at 805,0 731×864). A different DPI, window size, or a dialog in the way made the close fail, and failure still continued.
4. The coordinator rule was `alwaysApply: true`, so every chat opened in this folder joined the loop, including the measurement chats the rotator had just created.
5. The bootstrap started a watcher when it did not see one. A missed process check started a second watcher on the same file.
6. The pause line used the same prefix as the wake line. A notifier matching `^AGENT_LOOP_WAKE_...` then treated a pause as a wake.
7. The headless Ghidra process stayed alive after its client disconnected, so the project lock outlived the session. The worker rule forbade deleting that lock, which was correct, and the loop then kept scheduling workers who could only report it.

A burst of identical file timestamps while Cursor is opening or closing is the editor saving restored buffers. That happened here at 2:18 AM and again at 2:32 AM. It was not the watcher.

## What to check in your scripts

Walk the watcher, the rotator, and the rule that tells the coordinator what to do. For each item, the safe behavior is the second sentence.

1. **No progress is not a wake.** If the evidence file has no new heading after a reply, do not write a new assignment, do not commit, and do not open a chat. Pause and alert. Two identical stop replies in a row (same heading, same text once dates and times are stripped) stop the loop until a person clears the counter. Seeing the same response file twice must not increment that counter; a new write of the same stop must.
2. **A hard cap a person has to lift.** Cap total rotations and rotations per hour (Team 3 uses 10 and 10). The script must not set the status back to running by itself. One deliberate retry of the same question requires a separate human flag, and the script clears that flag when the retry is used.
3. **A minimum gap between rotations.** A few minutes (Team 3 uses 3). Charge the gap when a rotation is allowed, so a failed click cannot tight-retry.
4. **Lock files before any rotation.** If a process holds the lock, or the file cannot be opened with no share, stop and alert. Do not delete it. If nothing holds it, move it aside and pause. Do not rotate into a blocker you already know about. The worker prompt still says report a lock and stop; the coordinator is what stops scheduling.
5. **Close the old chat or abort.** If the old Cursor chat cannot be proved closed, do not open another. Keep a count that goes to 2 before the new-agent shortcut and back to 1 only after the close is proved. At 2, refuse. Open chats must not grow past 2.
6. **One watcher.** Hold a pid file with no share for the life of the process. A second copy exits. Starting a watcher from the bootstrap is only safe when that lock is the check, not a process-name glance that can miss.
7. **Pause must not look like a wake.** The wake token and the pause token need different prefixes, so a notify pattern on the wake token does not fire for a stop.
8. **The coordinator rule is not global.** `alwaysApply` stays false. Load it only for the coordinator thread (Team 3 globs `handoff/cursor_bootstrap.md`). A measurement chat must not arm a watcher or rotate.
9. **Commit only when the evidence moves.** A stop reply does not get a commit. Commit the new assignment only when a new heading is actually in the evidence file.
10. **Two switches to turn the loop on.** Renaming a script back to `.ps1` does nothing while a status field is `off`. The status field does nothing while the script is still `.disabled`. A person sets both. The scripts never flip status to `running`.
11. **Headless sessions release the project.** The worker calls `program_close` before it finishes and checks that `program_list_open` is 0. The MCP server must shut its Ghidra sessions down and exit when the client disconnects. A Python process that survives stdin EOF will keep `V3D_SKIP.lock` after the chat is gone, and item 4 will keep stopping on it.

`END` headings are not evidence headings. A matcher of the form `===== END <title> =====` must not count as a new section.

## An older watcher in this repo

`tools/team3_watch.ps1.disabled` is not the handoff watcher. It polls the trace for a new `===== END =====` line and prints `AGENT_LOOP_WAKE_TEAM3`. It has no status field, no cap, no lock check, and no pid file. That token does not match `^AGENT_LOOP_WAKE_team3`. The prompt in the dead body tells the coordinator not to write a prompt and not to run `tools/opencode_notify.ps1.disabled`. Renaming the file used to start a second watcher that `handoff/watch_response.pid` does not cover. The file now exits before that loop. `tools/opencode_notify.ps1.disabled` exits before it clicks. Leave both disabled.

The setup note used to tell every new coordinator to arm a watcher after looking through the terminal list. That list missed a running process in this incident. The pid file is the check. A new coordinator thread arms the handoff watcher only when status is `running`, and a second copy exits.

## What Team 3 changed

The guard is `handoff/loop_guard.ps1`, with checks in `handoff/test_loop_guard.ps1`. The watcher and rotator are still named `watch_response.ps1.disabled` and `rotate_threads.ps1.disabled`. `handoff/state.md` has `status: off`. Both the rename and `status: running` are required before the loop can arm, and nothing in the scripts sets that status.

The same commit turned the director rule off for every chat (`alwaysApply: false`) and told the worker to `program_close` before finishing. That commit is `42d6677` on `main`.

The MCP process-exit fix is in the separate `ghidra-headless-mcp` tree (local commit `a58c105`). It is not on the upstream remote. If you run that server, confirm a client disconnect actually ends the Python process. A server that only returns from its read loop will leave the project lock behind.

Do not turn Team 3’s loop back on from this note. The measurement it was on is still unanswered, and the loop stays off until someone sets the guard to `running` on purpose.
