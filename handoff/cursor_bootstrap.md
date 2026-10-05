This is a fresh coordinator thread. The open question is already in maps/vector_ownership/team3_next_prompt.txt. Team 3 has not answered it. Do not write another prompt. Do not message OpenCode. There is no handoff/prompt.md. If handoff/team3_response.md is already on disk, it is the previous answer.

Arm handoff/watch_response.ps1 in the background and notify on ^AGENT_LOOP_WAKE_team3. Ignore the startup line. When the wake line arrives, follow .cursor/rules/vector-ownership-director.mdc. Read handoff/state.md, the prompt file, the response, and only the last ===== section of maps/vector_ownership/anomaly_begin_store_trace.txt. Judge. Write the next question and state. Then run:

powershell -STA -NoProfile -ExecutionPolicy Bypass -File "handoff/rotate_threads.ps1"

That script opens a new OpenCode session, closes the old one, sends Continue from maps/vector_ownership/team3_next_prompt.txt, opens the next Cursor thread with this same text, and closes the thread that just finished.

Tell the user one sentence that this thread is waiting for Team 3. Then wait.
