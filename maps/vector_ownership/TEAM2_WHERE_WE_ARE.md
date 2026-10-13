# Team 3a progress for Team 2

Recorded 2026-10-12 from this checkout. The numbers below are a snapshot. Recompute them before relying on them:

```
python maps/vector_ownership/team2_progress_check.py
```

Run that from the repository root. Exit 0 means the gate file, the trace frontier, and the stock bytes in `v3d_files_\Vision3D.exe` still match this brief. The script only reads. It does not open Ghidra, and it does not write the trace, the gate, or the executable.

`v3d_files_\Vision3D.exe` is the file this brief uses: 28,738,048 bytes, SHA-256 `ccca11b2f05084b484fa5556c67f8874065dbc0b6265177d2517f81265af00f4`. Image base `0x140000000`.

## Gate

`maps/vector_ownership/anomaly_vector_mutator_table.json` is unchanged. MD5 `3C05BBB66D1463CB3B7CA0F1EDC78AEB`.

| Field | Value |
| --- | --- |
| `gate_status` | `CLOSED - outer vector one-shot; inner vector FIXED-CAPACITY (no growth during panel load); synchronization risk documented` |
| `gate_requirements.outer_vector` | CLOSED. One-shot allocation in the constructor, no later stores. |
| `gate_requirements.inner_vector_growth` | CLOSED. Fixed capacity. Growth during panel load is disproved in that file. |
| `gate_requirements.synchronization` | PARTIAL. Torn-write risk remains. Destructor versus in-flight workers remains. No proved fence between the worker write and the CAPM read. |
| `synchronization_contracts.worker_to_capm.barrier` | `NONE PROVEN - no memory fence, no atomic, no lock on inner vector` |

Team 3a has not upgraded `worker_to_capm` and has not changed `gate_status`. Rev6 stays blocked on this half.

## Bytes Team 2 can re-read in the executable

The checker maps each virtual address through the PE sections and compares the file bytes. It also resolves the two indirect calls through the import directory.

| Check | Address | File bytes | What it establishes |
| --- | --- | --- | --- |
| Slot store | `0x140737411` | `f2 41 0f 11 85 b8 02 00 00` | Last `ExecuteOne_Component` slot store is `MOVSD`. First byte is `F2`, so this instruction has no `LOCK` prefix. |
| Component epilogue | `0x1407374e8` | `c3` | `ExecuteOne_Component` ends at this `RET`. The trace range `0x14073741a` through this `RET` records no `MFENCE` and no instruction whose first byte is `F0`. |
| Worker wait | `0x1406a1b6f` | `ff 15 1b 35 6b 00` | `CALL qword ptr [0x140d55090]`. That IAT slot is `KERNEL32.dll::WaitForMultipleObjects`. |
| Treatment call | `0x1406a1c09` | `ff 50 18` | `CALL qword ptr [RAX + 0x18]` inside `FUN_1406a1a50`. |
| Completion signal | `0x1406a1c16` | `ff 15 0c 34 6b 00` | `CALL qword ptr [0x140d55028]`. That IAT slot is `KERNEL32.dll::SetEvent`. The three instructions `0x1406a1c0c` through this call record no `MFENCE` and no first byte `F0`. |
| Instruction after SetEvent | `0x1406a1c1c` | `44 8b 4b 70` | `MOV R9D, dword ptr [RBX + 0x70]`. It does not read `EAX`. |
| EAX clear | `0x1406a1c6e` | `33 c0` | `XOR EAX, EAX` in the handler epilogue. It clears `EAX`. It is not a test of the `SetEvent` return. |
| Handler body end | `0x1406a1c7b` | `c3` | `FUN_1406a1a50` returns here. |
| Later return | `0x1406a1d92` | `c3` | A later `RET`, after the handler body. |
| Padding | `0x1406a1d93` .. `0x1406a1d98` | `cc cc cc cc cc cc` | Six undefined `CC` bytes. The open measurement is the last of them. |

## Frontier

Latest response: `handoff/team3_response.md`, pass `20261013T003814Z-5713b20b`.

Latest trace heading, at the end of `maps/vector_ownership/anomaly_begin_store_trace.txt`:

`Wait flag taken after the second rcx rbx jmp mov mov lea mov call mov mov lea call mov mov call nop lea call xor lea mov mov pop pop pop pop ret cc cc cc cc cc`

That section quotes one existing code unit:

- `0x1406a1d98` .. `0x1406a1d98`
- bytes `cc`
- mnemonic `??`
- full text `?? CCh`
- next byte `0x1406a1d99`

The copy project `v3d_files_uncomp_copy` had no `V3D_SKIP.lock` or `V3D_SKIP.lock~` when that response was written, and the response records `program_list_open` count 0.

Every trace line of the form `Is mnemonic MFENCE or first byte F0?` in the current file is answered `No`. The synchronization requirement stays PARTIAL because those local windows do not by themselves prove a fence on the worker-to-CAPM path.

## Sentences left incorrect on purpose

The measurement loop does not rewrite old sections. These sentences are still in the trace, and they are the wrong reading:

- `Completion signal target`: the sentence that says the lock status was reported in the response.
- `Store tail fence`: the parenthetical that places `0x140780c80`, `FUN_14066e530`, and `FUN_1406803c0` under `Element destructor call`. Those three stay with `Element count`.
- `Worker wait handles`: the count sentence.
- `Wait flag branch end`: the sentence that replaces `0x1406a1bec` with `0x1406a1bed`. `Wait flag inclusive end` is the later section that keeps both addresses.
- `Wait flag taken lea` and `Wait flag taken after ret`: the byte quotes.
- `Wait flag taken after the rsi mov` and `Wait flag taken after the r8 mov`: the first-byte sentences. In the `r8 mov` section the character before `x48` has code point 0.
- The sections for `0x1406a1d93` and `0x1406a1d94`: the sentence that says the listing returned the unit with no mnemonic. The mnemonic line in those sections is `??`.

Use the `Answer:` line of a section, then confirm the bytes with the checker, when a later sentence in that same section disagrees.

## What is still open

The outer vector and inner-vector growth gates in the JSON are closed. The synchronization half is the open half: `worker_to_capm` still has no proved memory fence, atomic, or lock on the inner vector, and document destruction still has no proved `ProductionStop` join before it frees those vectors. The live measurement is the byte at `0x1406a1d98`.
