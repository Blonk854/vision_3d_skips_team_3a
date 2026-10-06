This is a fresh coordinator thread. The loop guard in handoff/state.md is the switch. If status is not running, say the loop is off and stop. Do not rename the .disabled scripts. Do not arm a watcher. Do not rotate. Do not write a prompt. Do not commit.

If status is running, the open question is already in maps/vector_ownership/team3_next_prompt.txt. Team 3 has not answered it yet. Do not write another prompt. Do not message OpenCode. There is no handoff/prompt.md. If handoff/team3_response.md is already on disk, it is the previous answer.

Arm handoff/watch_response.ps1 only when status is running. The script exits if status is not running, and a second copy exits while the pid lock is held. Notify on ^AGENT_LOOP_WAKE_team3. Ignore the startup line. AGENT_LOOP_PAUSE_team3 means stop and tell the user. Do not rotate on a pause.

When the wake line arrives, follow .cursor/rules/vector-ownership-director.mdc. Read handoff/state.md, the prompt file, the response, and only the last ===== section of maps/vector_ownership/anomaly_begin_store_trace.txt. If that heading is not new, do not write a prompt, do not commit, and do not rotate. If it holds, write the next question and update state. Commit only when that new heading holds. Then run:

powershell -STA -NoProfile -ExecutionPolicy Bypass -File "handoff/rotate_threads.ps1"

That script refuses when the guard says no, when a lock is held, or when it cannot close the old Cursor chat. If it exits nonzero, stop and tell the user. It opens a new OpenCode session only after those checks, closes the old one, sends Continue from maps/vector_ownership/team3_next_prompt.txt, opens the next Cursor thread with this same text, and closes the thread that just finished. If that close fails, it stops the loop instead of leaving the extra chat.

Tell the user one sentence that this thread is waiting for Team 3. Then wait.
