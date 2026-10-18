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
| `write_judgment_pass.ps1` | Mints a pass id and writes that judgment into `team3_next_prompt.txt` |
| `watch_and_write_judgment.ps1` | Polls until `0x1406a2fff` holds, then runs `write_judgment_pass.ps1` |
| `judgment_destructor_vs_workers.md` | After worker_to_capm judgment: one pass for `destructor_vs_workers` |
| `write_destructor_judgment_pass.ps1` | Mints a pass id and writes the destructor judgment into `team3_next_prompt.txt` |

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

When the sync walk hits `0x1406a3000` (or another mission stop), stop using the +1 template. Then:

```
powershell -NoProfile -ExecutionPolicy Bypass -File handoff_solo/write_judgment_pass.ps1
```

That overwrites `team3_next_prompt.txt` with a minted judgment pass. Open a fresh strong-model session on that file (or answer it yourself). Default: leave the gate JSON untouched unless the upgrade bar in `judgment_worker_to_capm.md` is met. Use `-Force` only to rewrite before the walk is finished or after a prior judgment heading.

After that judgment lands, run:

```
powershell -NoProfile -ExecutionPolicy Bypass -File handoff_solo/write_destructor_judgment_pass.ps1
```

Then answer the new `destructor_vs_workers` pass the same way (see `judgment_destructor_vs_workers.md`).
