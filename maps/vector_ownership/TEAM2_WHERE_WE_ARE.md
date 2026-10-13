# Team 3a progress for Team 2

Recorded 2026-10-12. Pull `9a19df2` or a descendant that still contains it. That commit is the measurement snapshot: `maps/vector_ownership/anomaly_begin_store_trace.txt` ends at `0x1406a1d98`, and `handoff/team3_response.md` starts with pass `20261013T003814Z-5713b20b`. The checker and this page first landed in `1ab2683`. The executable is not in git. Recompute the numbers before relying on them:

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
| Padding | `0x1406a1d93` .. `0x1406a1d99` | `cc cc cc cc cc cc cc` | Seven undefined `CC` bytes. The open measurement is the last of them. |

## Frontier

Latest response: `handoff/team3_response.md`, pass `20261013T003814Z-5713b20b`.

Latest trace heading, at the end of `maps/vector_ownership/anomaly_begin_store_trace.txt`:

`Wait flag taken after the second rcx rbx jmp mov mov lea mov call mov mov lea call mov mov call nop lea call xor lea mov mov pop pop pop pop ret cc cc cc cc cc cc`

That section quotes one existing code unit:

- `0x1406a1d99` .. `0x1406a1d99`
- bytes `cc`
- mnemonic `??`
- full text `?? CCh`
- next byte `0x1406a1d9a`

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

## Team 2, checked 2026-10-12

Their handoff copy in `handoff_Team3` answers pass `20261009T222402Z-6eb2ddbb` (§563). The open prompt there is pass `20261010T010440Z-6d5efb74` (§564), and the response file does not answer it.

`[0x140735f57, 0x140735f81)` in `v3d_files_\Vision3D.exe` matches the 42 bytes in that §563 reply: `90498b4510448b882439000040887c24204c8d8424a00300008d5710488d8c2480000000ff1537d76100`. Eight instructions. The only store is `mov byte ptr [rsp + 0x20], dil` at `0x140735f63`. The bound ends at the `call` at `0x140735f7b`. That call stays closed here.

The straight line at `0x140735f81` is `[0x140735f81, 0x140735f90)`, 3 instructions and 15 bytes, ending at `call qword ptr [rip + 0x629168]`. Zero stores. That stretch is not shown to write the loaded qword's bytes at `+0x18` or `+0x19`.

The straight line at `0x140735f90` is `[0x140735f90, 0x140735fbc)`, 6 instructions and 44 bytes, ending at `call qword ptr [rip + 0x61f45c]`. Two stores, both through `rsp`, at `0x170` and `0x180`. That stretch is not shown to write those bytes.

The straight line at `0x140735fbc` is `[0x140735fbc, 0x140735fe1)`, 6 instructions and 37 bytes, ending at `call qword ptr [rip + 0x61f617]`. One store, through `rsp`, at `0x3a0`. That stretch is not shown to write those bytes.

The straight line at `0x140735fe1` is `[0x140735fe1, 0x140736034)`, 13 instructions and 83 bytes, ending at `call qword ptr [rip + 0x61f35c]`. Three stores, all through `rsp`, at `0x170`, `0x16c`, and `0x3b8`. That stretch is not shown to write those bytes.

The straight line at `0x140736034` is `[0x140736034, 0x140736064)`, 8 instructions and 48 bytes, ending at the relative `call` at `0x14073605f`. Three stores, all through `rsp`, at `0x188`, `0x1f0`, and `0x1f8`. That stretch is not shown to write those bytes.

The straight line at `0x140736064` is `[0x140736064, 0x140736075)`, 4 instructions and 17 bytes, ending at the relative `call` at `0x140736070`. Zero stores. That stretch is not shown to write those bytes. The instruction after `0x140736070` stays unread. The full bounds are in the status note.

Their uniqueness row stays Partial. The same sentence is now in [Team 2 uniqueness check](../../plans/robust_patch_revision_2a_status.md#team-2-uniqueness-check-2026-10-12). Their reported §563 plan section and test are absent from this repo, so they were left in their tree. This does not move `gate_status` or `worker_to_capm`.

## What is still open

The outer vector and inner-vector growth gates in the JSON are closed. The synchronization half is the open half: `worker_to_capm` still has no proved memory fence, atomic, or lock on the inner vector, and document destruction still has no proved `ProductionStop` join before it frees those vectors. The live measurement is the byte at `0x1406a1d99`.
