# Handoff state

Update this file in the same turn as `maps/vector_ownership/team3_next_prompt.txt`. This file is loop bookkeeping. The assignment is the prompt file. The evidence is the trace.

## Loop guard

The scripts read the block below. The loop stays stopped while `status` is `off`, `paused`, or `stopped`. A human sets `status` to `running` and renames the `.disabled` scripts before anything can arm. The scripts never set `status` back to `running`. After a pause, one more rotation of the same question requires `allow_one_resume: yes`. Two identical stop replies set `identical_stops` to 2 and refuse until a human sets that back to 0.

```text
status: off
rotations_total: 0
rotations_this_hour: 0
hour_started_utc:
last_rotation_utc:
last_heading: Completion signal target
identical_stops: 0
last_stop_fingerprint:
last_stop_stamp:
max_rotations: 10
max_per_hour: 10
min_minutes_between: 3
allow_one_resume: no
tracked_open_chats: 1
pause_reason: loop is off until a human sets status to running
```

## Open question

The loop is off. Do not write a prompt, do not rotate, and do not commit while the loop guard status is off.

The SetEvent question is still unanswered. The last heading is still `Completion signal target`. There is no `SetEvent return read` section. The reply at 2026-10-06 1:47:45 AM stopped because `V3D_SKIP.lock` (239 bytes) and `V3D_SKIP.lock~` (0 bytes) were present, both last written 2026-10-06 1:27:57 AM. Those files were removed after the runaway once no process held them. Team 3 appends under `SetEvent return read` only when both lock files are absent. If a lock file is present and a process holds it, they report it and stop. The gate file MD5 is still 3C05BBB66D1463CB3B7CA0F1EDC78AEB.

## Already holds

`Completion signal target` holds for the yes. `Completion signal fence` holds for the no. `Store tail fence` holds for the no. `Slot store prefix` holds for the no. `LEA displacement` holds. `Epilogue fence` holds for the no. `First epilogue callee` holds for the yes. `Freed pointer source` holds for the no. `Zone slot free` holds for the yes. `Destructor argument` holds for the no. `Outer array free` holds for the no. `Array element free` holds for the yes. `Element destructor call` holds for the yes. `Element count` holds for the no. `Destructor reaches stop` holds for the no. `Epilogue stop call` holds for the no. `Indirect call target` holds for unresolved. `Destructor on return` holds for the yes. `Indirect call base` holds for none. `Tail indirect call` holds for the yes. `Later lock pair` holds for the no. `Second lock operand` holds for the no. `Pointer arm store` holds for the no. `Taken arm fence` holds for the yes. `Not-taken arm fence` holds for the no. `Local split skips the call` holds for the yes. `LOCK on the compare bypass` holds for the no. `LOCK chain fall-through` holds for the no. `Destructor join` holds. This is still the synchronization half. Do not change `gate_status`.
