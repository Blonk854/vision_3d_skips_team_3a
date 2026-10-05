# Handoff state

Update this file in the same turn as `maps/vector_ownership/team3_next_prompt.txt`. This file is loop bookkeeping. The assignment is the prompt file. The evidence is the trace.

## Open question

Unanswered. The prompt asks Team 3 to name one LOCK-prefixed instruction in `/Vision3D.exe`, then say whether any LOCK-prefixed instruction executes on the call path in `Worker to CAPM fence`. They append under `LOCK prefix on the call path` and overwrite `handoff/team3_response.md`. `handoff/team3_response.md` is not on disk yet. Do not judge `handoff/prompt.md` or `handoff/team2_response.md`; those were Team 2's uniqueness files and are not this gate.

## Already holds

`Worker to CAPM fence` holds except the zero-LOCK sentence already corrected. `Destructor join` holds. This is still the synchronization half. Do not change `gate_status`.
