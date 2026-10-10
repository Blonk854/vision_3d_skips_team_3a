This is a fresh coordinator thread. The open question is already in maps/vector_ownership/team3_next_prompt.txt. Team 3 has not answered it. Do not write another prompt. Do not message OpenCode. There is no handoff/prompt.md. The copy of handoff/team3_response.md on disk is the previous answer.

Arm handoff/watch_response.ps1 in the background and notify on ^AGENT_LOOP_(WAKE|PAUSE)_team3. Ignore the startup line. AGENT_LOOP_PAUSE_team3 means Team 3 answered without a new ===== heading in the trace: tell the user, and do not write a prompt, commit, or rotate. When the wake line arrives, follow .cursor/rules/vector-ownership-director.mdc, then run:

powershell -STA -NoProfile -ExecutionPolicy Bypass -File "handoff/rotate_threads.ps1"

That script opens a new OpenCode session, closes the old one, sends one unique line of the form Pass <id>. Read maps/vector_ownership/team3_next_prompt.txt and answer only pass <id>., opens the next Cursor thread with this same text, and closes the thread that just finished. The id is the Pass id line at the top of team3_next_prompt.txt. Do not reuse an id. The script refuses a reused id, a V3D_SKIP lock file, a rotation less than 3 minutes after the last one, and an OpenCode session that is still running. If it exits nonzero, stop and tell the user.

Tell the user one sentence that this thread is waiting for Team 3. Then wait.
