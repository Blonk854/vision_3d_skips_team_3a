This is a fresh coordinator session in OpenCode Dev. Read handoff_oc/director.md now and follow it for this whole session. The open question is already in maps/vector_ownership/team3_next_prompt.txt. Team 3 (the stable OpenCode window) has not answered it. Do not write another prompt. Do not message OpenCode. There is no handoff/prompt.md. The copy of handoff/team3_response.md on disk is the previous answer.

Run this with the shell tool in the background (background: true), working directory the vision_3d_skips - team 3a folder, and wait to be notified when it exits:

powershell -NoProfile -ExecutionPolicy Bypass -File "handoff_oc/watch_response.ps1"

Ignore its startup line. When it exits, read its output. AGENT_LOOP_PAUSE_team3 means Team 3 answered without a new ===== heading in the trace: tell the user, and do not write a prompt, commit, or rotate. AGENT_LOOP_WAKE_team3 is the wake: follow handoff_oc/director.md, then run in the foreground:

powershell -STA -NoProfile -ExecutionPolicy Bypass -File "handoff_oc/rotate_threads.ps1"

That script opens a new OpenCode session, closes the old one, sends one unique line of the form Pass <id>. Read maps/vector_ownership/team3_next_prompt.txt and answer only pass <id>., opens the next OpenCode Dev session with this same text, and closes this session's tab. The id is the Pass id line at the top of team3_next_prompt.txt. Do not reuse an id. The script refuses a reused id, a V3D_SKIP lock file, a rotation less than 3 minutes after the last one, and an OpenCode session that is still running. If it exits nonzero, stop and tell the user. If it exits 0, the next coordinator session owns the loop: do not arm a watcher, do not run any other command, and end your turn with one sentence saying the loop rotated.

Tell the user one sentence that this session is waiting for Team 3. Then wait.
