# Team 3 pass closeout

When the user message is `Pass <id>. Read … and answer only pass <id>.`:

1. Do the question in that file for that pass id.
2. Before you stop, overwrite `handoff/team3_response.md` with your entire chat response. Replace the file; do not append. First line must be `Pass id: <id>`.
3. A chat reply alone does not finish the pass. Only the file write wakes the loop.
4. After a context rollover, write `handoff/team3_response.md` again in that turn until its first line is this pass id.
5. Append the one new `=====` section the question asks for in the trace file it names. Putting the section only in the response file does not append the trace.
6. Close the headless session with `program_close` and leave `program_list_open` at count 0 when the question says to.
