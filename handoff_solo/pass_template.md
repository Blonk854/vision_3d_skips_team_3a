# Next-pass template (sync byte walk)

Overwrite `maps/vector_ownership/team3_next_prompt.txt` with the block below.
Replace every `{{PLACEHOLDER}}`. Do not leave braces in the file.
Do not add commentary above or below the block.

Placeholders:

- `{{PASS_ID}}` — new id `yyyyMMddTHHmmssZ-` + 8 hex (example `20261017T221500Z-a1b2c3d4`)
- `{{ADDRESS}}` — next byte, e.g. `0x1406a1fd7` (nine hex digits after `0x`)
- `{{PREV_ADDRESS}}` — previous pass address, e.g. `0x1406a1fd6`
- `{{HEADING_TAIL}}` — exact ending of the current last non-`END` heading, starting at a stable mid-point you copy from the file (same style as recent prompts: from ` 89 75 67 …` through the final word). Must match the file exactly, including the newest word.

```
Pass id: {{PASS_ID}}

Answer only pass {{PASS_ID}}. When you finish, overwrite handoff/team3_response.md with your entire chat response, verbatim, and make its first line `Pass id: {{PASS_ID}}`. Do not append to that file.

Read-only. Copy project v3d_files_uncomp_copy/V3D_SKIP, program /Vision3D.exe. Do not save. Do not open the locked GUI project. Do not open another module.

Check the lock files when you start. If either `v3d_files_uncomp_copy/V3D_SKIP.lock` or `v3d_files_uncomp_copy/V3D_SKIP.lock~` is present, stop, report both sizes and timestamps, do not delete them, and do not edit the trace. When no lock file is present, open the copy project read-only. Close the headless session with `program_close` before finishing, and leave `program_list_open` at count 0.

Do not call `listing_code_unit_at`. Do not call `memory_blocks_list`. Do not disassemble. Do not call `listing_disassemble_seed` or `listing_disassemble_range`. Do not create a code unit or data. Do not clear the listing. Do not quote any instruction.

Call `memory_read` once at `{{ADDRESS}}` with length 1. Before you call it, check that the address you pass has exactly nine hex digits after `0x` and is `{{ADDRESS}}`. `{{PREV_ADDRESS}}` plus one is `{{ADDRESS}}`. It lies inside .text, between `0x140001000` and `0x140d509ff`. Append exactly one new section to `maps/vector_ownership/anomaly_begin_store_trace.txt` after that call, whether the call returns one byte or fails with MemoryAccessException. Writing the section into `handoff/team3_response.md` does not append the trace.

The current last heading is the last `=====` heading in maps/vector_ownership/anomaly_begin_store_trace.txt that is not `===== END =====`. It ends in `{{HEADING_TAIL}}`. Copy it exactly from the file. The new heading is that current last heading, copied exactly, then one space, then one word. If `memory_read` returns one byte, the word is that byte as exactly two lowercase hexadecimal digits, with no `0x` prefix. If it fails and returns no byte, the word is `unreadable`. Do not choose the word before the call returns or fails.

The first line of that section is `===== ` then the new heading then ` =====`. The last line of that section is exactly `===== END =====`. Append exactly one section.

Inside that section, write these lines:
- `Address: ` then `{{ADDRESS}}` in backticks.
- `Byte length: 1`.
- The result: the two lowercase hex digits in backticks, or that no byte was returned with the name MemoryAccessException.
- `This section records a raw read. It does not record a code unit.`
- `Mnemonic: none` and `Full text: none`.
- `This is still the synchronization half.`
Do not say that an instruction starts at any address. Write every address as a backtick, the digit 0, the letter x, lowercase hex digits, and a backtick. Do not write a null byte, a character below code point 32, or a backslash in place of a backtick. Do not rewrite the rest of the trace.

Do not upgrade synchronization_contracts.worker_to_capm. Do not change the gate status. The MD5 of maps/vector_ownership/anomaly_vector_mutator_table.json is 3C05BBB66D1463CB3B7CA0F1EDC78AEB. Leave that file untouched. Report the MD5 before and after, and whether a lock file remains in v3d_files_uncomp_copy.
```
