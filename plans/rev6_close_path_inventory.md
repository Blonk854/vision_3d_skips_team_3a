# Rev6 close-path VA inventory

Stock image: `v3d_files_/Vision3D.exe` SHA-256
`ccca11b2f05084b484fa5556c67f8874065dbc0b6265177d2517f81265af00f4`.

## Rev5 hooks (retain)

| Site | VA | Orig role |
| --- | --- | --- |
| Count / mask hook | `0x140736f47` | Threshold skip claim |
| SkipList_Reset entry | `0x140541050` | CAO context retire + stock reset |
| Final CAPM call | `0x14069b4d8` | Serial reconciliation wrapper |
| Stock SkipSubPanel call | `0x140736fcb` | Winning skip caller |
| Review route test | `0x1406748c5` | Route patch |

Rev5 caves live in added `.patch` code at `IMAGE_BASE+0x1C98000`.

## Rev6 close-path hooks (add)

| Site | VA | Orig bytes (prefix) | Cont VA | Role |
| --- | --- | --- | --- | --- |
| ProductionDoc_dtor | `0x14067fc20` | `4c 8b dc 57 41 56 41 57` | `0x14067fc28` | CALL `ProductionStop` then replay prologue |
| ProductionStop | `0x1406920f0` | (callee) | — | Join workers before zone free |
| View dtor | `0x1406abc60` | `48 89 4c 24 08 53 56 57` | `0x1406abc68` | Clear `document+0x5838` via `view+0xe8` |
| SKIP refresh | `0x1406adaf0` | `40 55 56 57 48 83 ec 30` | `0x1406adaf8` | Swap `document+0x23e0` to snapshot object for body |
| SkipList_Reset | `0x140541050` | (rev5) | after stock ret | Publish empty snapshot on normal return |
| SkipSubPanel wrap | `0x140736fcb` / stock cave | (rev5) | after stock skip | Recapture snapshot from live array |

## Snapshot capture set (design)

| Mutator | Entry | Capture |
| --- | --- | --- |
| SkipList_Reset | `0x140541050` | Empty after stock return |
| SkipSubPanel | via `0x140736fcb` wrap | Copy live `+0x23e0` after stock return |
| SkipList_Add | `0x140541020` | Copy live after stock (rev6 add hook) |

Other mutators from the 2026-09-24 candidate remain follow-on attach points if
skip traffic uses them on the supported single lane.

## Patch data (Rev6 additions in `.patch` data)

| Symbol | Purpose |
| --- | --- |
| `SNAP_OBJ` | Fake `CUIntArray`-shaped header (`+8` data, `+10` size) |
| `SNAP_BUF` | Copied DWORD elements |
| `SNAP_SAVE_LIVE` | Saved live `document+0x23e0` during refresh |
| `POSTER_COUNT` | Optional wait before view free (posts in flight) |

## Out of scope VAs

Worker→CAPM fence hunt, full `.text` walk, dual-lane paths.
