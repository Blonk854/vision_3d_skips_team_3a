# Solo sync-byte flow (no director)

One OpenCode window. No OpenCode Dev, no Cursor coordinator, no rotator, no response watcher.

The agent reads a persistent mission, does the open pass in `maps/vector_ownership/team3_next_prompt.txt`, appends evidence, writes the next pass from a template, and continues in the same session.

## Files

| File | Role |
|------|------|
| `mission.md` | Goal, hard rules, stay-on-task rules, stop list, self-advance |
| `pass_template.md` | Exact text to write into `team3_next_prompt.txt` for address+1 |
| `advance_pass.ps1` | Fills the template after a holding pass (preferred over hand-editing) |
| `bootstrap.md` | Paste once into a new OpenCode session to start |
| `judgment_worker_to_capm.md` | After sync-walk end: one judgment pass for `worker_to_capm.barrier` (not address+1) |

Worker artifacts stay where they already are: `team3_next_prompt.txt`, `handoff/team3_response.md`, `anomaly_begin_store_trace.txt`. Closeout skill `handoff/TEAM3_CLOSEOUT.md` (via `opencode.json`) still applies when a `Pass <id>. Read …` line is used; this solo flow mostly drives itself from the mission after bootstrap.

## Start

1. Stop any Cursor/`handoff` or OpenCode Dev/`handoff_oc` loop (no watcher, no second director window).
2. Open this repo in one OpenCode window. Open a session.
3. Paste `handoff_solo/bootstrap.md` and send it.
4. Leave it alone until it stops (sync-walk end `0x1406a3000`, lock, `.text` safety bound, 8× `unreadable`, repeated failure, or mission stop list).

## Walk end

Primary finish line is **`0x1406a3000` (exclusive)** in `mission.md`. `advance_pass.ps1` refuses to mint a pass at or past that address. The full `.text` end (`0x140d509ff`) stays only as a safety bound.

## Do not

- Run `handoff_oc/prepare_windows.ps1` or `rotate_threads.ps1` for this flow
- Put `mission.md` into global `opencode.json` `instructions` while a director flow is still in use (it would tell Team 3 to self-advance)
- Upgrade the gate from this flow

## Later upgrade

When the sync walk hits `0x1406a3000` (or another mission stop), stop using the +1 template. Open `judgment_worker_to_capm.md`, mint a pass id, paste the fenced assignment into a fresh strong-model session (or do it yourself). Default: leave the gate JSON untouched unless the upgrade bar is met.
