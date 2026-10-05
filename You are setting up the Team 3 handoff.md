You are setting up the Team 3 handoff loop in
C:\Users\s_sme\Documents\VS_Project_LapTop\vision_3d_skips - team 3a.
This is the vector-ownership gate. Team 2's uniqueness files are the
mechanical model only. Do not install .cursor/rules/uniqueness-handoff.mdc.
The director rule already in this repo is .cursor/rules/vector-ownership-director.mdc.

One assignment file
maps/vector_ownership/team3_next_prompt.txt is the only prompt.
Do not create handoff/prompt.md. Do not leave a second copy of the
question anywhere else. The OpenCode line is exactly:

Continue from maps/vector_ownership/team3_next_prompt.txt

If a copied Team 2 script still says handoff/prompt.md, change that
string to the path above before the first rotation.

Files the loop uses
handoff/README.md, handoff/state.md, handoff/cursor_bootstrap.md,
handoff/watch_response.ps1, and handoff/rotate_threads.ps1 are the
loop machinery. handoff/team3_response.md is the wake file. Tailor
those files to the paths in this note before arming the watcher.
Leave tools/team3_watch.ps1 and tools/opencode_notify.ps1 stopped.
Those watch the trace and type into the same OpenCode session. A
second watcher will wake the coordinator on the old file.

What the loop does
The coordinator thread stays short. Team 3 does the byte work from
maps/vector_ownership/team3_next_prompt.txt. They overwrite
handoff/team3_response.md with their full chat response, and they
append the measurement under one new heading in
maps/vector_ownership/anomaly_begin_store_trace.txt. The response
file is how you wake. The new trace heading is the evidence you judge.
When the response file changes, you judge the reply against that
heading, write the next prompt into team3_next_prompt.txt, update
handoff/state.md, then run handoff/rotate_threads.ps1. That script
opens a new OpenCode session, closes the old one, sends the one line
above, opens a new Cursor agent, pastes handoff/cursor_bootstrap.md,
and closes the Cursor chat that just finished. The task lives in the
prompt file. The chat message stays one line so neither thread
accumulates history.

What Team 3 writes
Every prompt already tells them to append one heading to the trace,
leave the gate status untouched, and report the gate line and its MD5.
The same reply must also overwrite handoff/team3_response.md. The
trace stays append-only. The response file is overwritten so the
watcher can see one new write. Do not read the trace from the start.
On a wake, read only the last ===== section.

What you check
The response and the new heading must agree. Check the yes/no, the
cited lines, the gate line and its MD5 left untouched, and that no
lock file remains in v3d_files_uncomp_copy. If the section holds,
replace team3_next_prompt.txt with the next question that moves
synchronization. If a sentence is false, the next prompt corrects
that sentence before the gate moves. Do not change gate_status. Do
not upgrade synchronization_contracts. Do not do Team 3's byte work.
Do not append the trace yourself.

handoff/state.md is loop bookkeeping, not a second prompt. Record
whether the open prompt is unanswered, and which headings already
hold. Right now Worker to CAPM fence holds except the zero-LOCK
sentence, Destructor join holds, and the open half is still
synchronization. The same sentences stay at the bottom of
team3_next_prompt.txt so a fresh thread can read them there.

Before you touch a window
Read handoff/state.md. If it says the open prompt is unanswered and
that the team3_response.md already on disk is the previous answer, do
not judge that file and do not run rotate_threads.ps1. Check the
terminals for a powershell process already running
handoff/watch_response.ps1. If one is running, leave it. A second
watcher will wake you on the old file. Look at OpenCode. If its
button is named Stop, Team 3 is mid-run. Leave that session open.

Layout this script expects
The script places both windows at the start of every run, and
-LayoutOnly does only that. On the 1536 by 864 view of this display,
OpenCode is -2,0 807 by 870 and Cursor is 805,0 731 by 864. Cursor's
left edge is OpenCode's right edge. Do not widen Cursor over OpenCode.
OpenCode is the desktop app, process
name OpenCode. Its UI Automation tree has New session, Close tab, an edit
named Prompt, Send, and Stop while a reply is generating. Cursor is the
window whose title contains vision_3d_skips. The fresh composer is the
white chat card on the right, under the tab row, not in the bottom
follow-up box. This docked chat shows one tab header. Have only one
OpenCode session tab and one Cursor chat before a rotation. The script
closes every OpenCode tab that existed before New session. It closes a
Cursor chat only when two tab titles are visible.

Cursor clicks match the Team 2 rotator: SetCursorPos, then mouse_event.
They are relative to the window's top-left, with Cursor to the right of
OpenCode.

- empty sidebar, above the New Agent label: +30, +180
- fresh composer, under the tab row: +420, +115
- left chat tab: measured from the tab row, not a fixed offset

Screenshots are physical pixels. The 1536 by 864 view is 1.25 times
smaller. The script photographs Cursor by its physical window rect,
finds the left title there, and divides by the window's scale before
it clicks. A screenshot taken at the click coordinates starts about
200 pixels inside OpenCode. It refuses to close unless two chat tabs
are visible. The toolbar at the right end of the tab row is not a tab.
-StopAfterNewAgent clicks the sidebar, sends Ctrl+Shift+L, and returns before the paste.
-ShowComposerClick clicks +420,+115 and returns before the paste.
Remeasure the tab row without closing:

powershell -STA -NoProfile -ExecutionPolicy Bypass -File "handoff/rotate_threads.ps1" -MeasureCursorTabs

  -ClickLeftTitle clicks that measured left title and returns before Ctrl+W.

  Ctrl+[ does not switch chats in this window. Do not use it.
  Ctrl+Enter force-sends in Cursor. Enter confirms the "Close Running Tab?"
  dialog after Ctrl+W.

Arm the watcher
Start it with the Shell tool, in the background, with notify_on_output.
Working directory is the repo root. Command:

powershell -NoProfile -ExecutionPolicy Bypass -File "handoff/watch_response.ps1"

block_until_ms: 0
notify_on_output pattern: ^AGENT_LOOP_WAKE_team3
notify_on_output reason: Team 3 response

The script prints "watching handoff/team3_response.md baseline=..." first.
That line is not a wake. It records the current size and write time so
the file already on disk does not count as a new reply. A wake is only
the later line that starts with AGENT_LOOP_WAKE_team3, after a write
stays still for 800 milliseconds. On that line, follow the prompt inside
it: read state, team3_next_prompt.txt, the response, and only the last
===== section of the trace; judge; write the next question and state in
the same turn; then run the rotator. Do not do Team 3's byte work.

Run the rotator only after the next prompt is on disk
Use powershell -STA. Clipboard access fails otherwise.

powershell -STA -NoProfile -ExecutionPolicy Bypass -File "handoff/rotate_threads.ps1"

OpenCode: click New session, wait until a tab name appears that was not
there before, close the old tab by its Close tab button, click the Prompt
edit, paste "Continue from maps/vector_ownership/team3_next_prompt.txt",
and press Enter. If the button is already named Stop, the send worked.
If the prompt still holds that exact line, click Send. Leave the session
alone if the new tab never appears. The old session is still the live
one in that case.

Cursor: click the blank sidebar, send Ctrl+Shift+L, click the fresh
composer, paste handoff/cursor_bootstrap.md, and send Ctrl+Enter. The
script saves C:\Users\s_sme\AppData\Local\Temp\cursor_before_send.png
before it sends. The first time on a layout, stop before the send:

powershell -STA -NoProfile -ExecutionPolicy Bypass -File "handoff/rotate_threads.ps1" -CursorOnly -StopBeforeCursorSend

Read that image. Send only if it shows "This is a fresh coordinator
thread." The script then measures the tab row, clicks the left tab's
title, and sends Ctrl+W. Enter confirms Close Running Tab. It stops
without closing if it does not see two chat tabs. Switches -OpenCodeOnly
and -StopBeforeCursorClose exist for the same kind of check.

After the new Cursor thread opens, it is told to arm this same watcher
and wait. The thread that ran the rotator closes. That is the point.

Commit and push only maps/vector_ownership/team3_next_prompt.txt when
you replace it. Leave the trace, handoff/team3_response.md, and
handoff/state.md unstaged. The trace is Team 3's.
