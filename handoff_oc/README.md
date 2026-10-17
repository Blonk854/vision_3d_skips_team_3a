# Team 3 handoff, OpenCode → OpenCode Dev

This is the OpenCode Dev version of `handoff/`. OpenCode Dev is the coordinator, in the role Cursor plays in `handoff/`. Stable OpenCode is still Team 3 and does the work. `handoff/` and the Cursor flow are unchanged. Run one flow at a time.

## What is shared with the Cursor flow

Team 3 does not know which coordinator is running, so the worker side stays in `handoff/` and is not copied here:

- `maps/vector_ownership/team3_next_prompt.txt` is the only assignment. Its first line is `Pass id: <id>`, and every new question gets a new id (`yyyyMMddTHHmmssZ-<8 hex>`).
- Team 3 overwrites `handoff/team3_response.md` (not `handoff_oc/`) with their full chat response, verbatim, with `Pass id: <id>` as its first line. They also append one heading to `maps/vector_ownership/anomaly_begin_store_trace.txt`. The response file is the wake. The new trace heading is the evidence.
- `.opencode/skills/pass-id-questions/SKILL.md` and `handoff/TEAM3_CLOSEOUT.md` (loaded by `opencode.json` `instructions`) tell Team 3 how to answer. OpenCode Dev opens the same folder, so its sessions load them too. They only apply to a `Pass <id>. Read …` message, and the coordinator never gets one.
- The watcher lease (`%LOCALAPPDATA%\vision_3d_skips-team3a\watcher.pid`) and the rotation mutex are the same for both flows, so one flow's watcher stops the other's, and the two rotators cannot run at once.

## What is OpenCode Dev specific

`opencode_bootstrap.md` replaces `handoff/cursor_bootstrap.md`. `director.md` replaces `.cursor/rules/vector-ownership-director.mdc`. On purpose, the director is not an OpenCode skill, not in `opencode.json` `instructions`, and not in `AGENTS.md`. Those reach every session, including Team 3's. Only the bootstrap tells a session to read it (`loop-runaway-2026-10-06.md` item 8).

`state.md` is this flow's place in the chain. A new coordinator session reads it together with the prompt before judging a reply. Update `state.md` in the same turn as the prompt. `handoff/state.md` is the Cursor flow's copy. If you switch flows, copy the newer one over the older one first.

`watch_response.ps1` records `handoff/team3_response.md`'s size and time and the last trace heading at startup. It looks only when a later write settles and is headed with the `Pass id:` in the prompt. If the trace has a new `=====` heading (an `END` line does not count), it prints `AGENT_LOOP_WAKE_team3`. If not, it prints `AGENT_LOOP_PAUSE_team3`. Either way it exits, and it gives up after four hours. The coordinator runs it with the OpenCode shell tool in the background. OpenCode notifies the session when the command exits, which replaces Cursor's notify-on-pattern. Starting a watcher stops the previous one, from either flow.

`rotate_threads.ps1` refuses to run while another rotation is running. It also refuses:

- a prompt without a `Pass id:` line
- a pass id already in `handoff_oc/.rotated` or `handoff/.rotated`
- any `v3d_files_uncomp_copy/V3D_SKIP.lock*` file
- a rotation less than 3 minutes after the last one in either ledger
- a Team 3 session that still shows Stop
- a missing OpenCode Dev window

Each refusal exits 1. The id is recorded in `handoff_oc/.rotated` before any clicks, so if a rotation fails partway, remove its line before re-running.

When nothing refuses, the rotator works in both windows:

1. In OpenCode, it opens a new session, closes the old one, and sends `Pass <id>. Read maps/vector_ownership/team3_next_prompt.txt and answer only pass <id>.`
2. In OpenCode Dev, it opens a new session, pastes `opencode_bootstrap.md`, sends it, and closes the coordinator tab that ran the script. It closes that tab last, after the new coordinator is sent. The old coordinator's turn ends after the rotator exits 0.

Both windows are driven through UI Automation by control name (`New session`, `Close tab`, `Prompt`, `Send`, `Stop`), not pixel offsets. The send is checked by watching for `Stop`. Before the coordinator send, it saves the prompt box to `%TEMP%\opencode_dev_before_send.png`. The first time on a layout, run `-CoordinatorOnly -StopBeforeCoordinatorSend` and check that the image shows the bootstrap text. Other switches are `-WorkerOnly` and `-StopBeforeCoordinatorClose`.

`prepare_windows.ps1` runs before a new loop. It places OpenCode on the left half of the primary work area and OpenCode Dev on the right. It then checks that each window has a session tab row at the top of the screen, a `New session` button, and a `Prompt` box above the taskbar. Open one session in each app first. The script does not message either window and does not start the watcher.

Both apps are Electron windows titled `OpenCode`. The scripts tell them apart by exact process name, `OpenCode` for Team 3 and `OpenCode Dev` for the coordinator. Do not use the wildcard `OpenCode*`, which matches both. The scripts are per-monitor DPI aware. This laptop runs at 125%.

OpenCode Dev (1.x on this machine) does not turn on Chromium's accessibility tree for plain UI Automation. Without it, prepare/rotate only see `Chrome Legacy Window` and fail looking for the content rect / Prompt. Stable OpenCode 2.x already exposes the tree. Start the coordinator with `handoff_oc/start_opencode_dev.ps1` so it launches with `--force-renderer-accessibility` (close any running OpenCode Dev first).

## Starting the loop

1. Close OpenCode Dev if it is open, then `powershell -NoProfile -ExecutionPolicy Bypass -File handoff_oc/start_opencode_dev.ps1`. Open the `vision_3d_skips - team 3a` folder, pick the coordinator model, and make sure Team 3's OpenCode has an open session.
2. `powershell -STA -NoProfile -ExecutionPolicy Bypass -File handoff_oc/prepare_windows.ps1`
3. Paste `handoff_oc/opencode_bootstrap.md` into a new OpenCode Dev session. The loop starts only when a person does this.

Commit `team3_next_prompt.txt` only when a new trace heading holds. Do not commit a stop reply.

Leave `tools/team3_watch.ps1.disabled` and `tools/opencode_notify.ps1.disabled` as they are. Do not rename them. `team3_watch` is not this watcher and has no lease, so a renamed copy is a second watcher. `tools/notify_opencode.ps1` is a separate manual click helper. Nothing in this loop calls it.

`loop-runaway-2026-10-06.md` is the post-mortem of the loop that ran away on 6 Oct. Each guard above maps to an item in it.
