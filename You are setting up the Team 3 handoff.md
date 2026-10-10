The Team 3 handoff loop is already set up. This note used to describe the
old loop (loop_guard.ps1, the status block, the .disabled scripts, and
handoff/watch_response.pid). That loop was replaced on 9 Oct 2026 by
Team 2's pass-id loop, tailored for this workspace. Do not rebuild the
old one from this note.

Read handoff/README.md for how the loop works. The coordinator rule is
.cursor/rules/vector-ownership-director.mdc. It is not always on and
loads only for the coordinator thread. Do not install Team 2's
.cursor/rules/uniqueness-handoff.mdc.

maps/vector_ownership/team3_next_prompt.txt is the only assignment. Its
first line is Pass id: <id>. There is no handoff/prompt.md.

To start the loop: open OpenCode and the Cursor window for this
workspace, run handoff/prepare_windows.ps1, then paste
handoff/cursor_bootstrap.md into a new Cursor agent chat.

Leave tools/team3_watch.ps1.disabled and tools/opencode_notify.ps1.disabled
as they are. Do not rename them. handoff/loop-runaway-2026-10-06.md
explains why.
