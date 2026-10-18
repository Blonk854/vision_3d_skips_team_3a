# Rev6 close-path charter

Recorded 2026-10-18. Replaces the overkill sync-byte measurement loop as the
blocking path for Rev6. Measurement judgments already landed; they document
residual risk. They are not a reason to keep walking `.text`.

## Measurement loop

**Closed.** Do not resume `handoff_solo` address+1 or re-mint judgment prompts.
Disposition:

| Contract | Verdict | Rev6 treatment |
| --- | --- | --- |
| `worker_to_capm.barrier` | NONE PROVEN | **Residual accepted** under fixed-capacity inner vectors (growth CLOSED). No fence inventing. |
| `destructor_vs_workers` | JOIN_ABSENT | **Must patch**: join before zone free on the Rev6-owned destruction path. |
| Outer / inner growth | CLOSED | Unchanged. |

Gate JSON MD5 may change when close-path fields are updated after the patch
lands. Until then it may stay `3C05BBB66D1463CB3B7CA0F1EDC78AEB`.

## What Rev6 must patch

1. **SKIP live-array retirement** — Posted refresh must not read `document+0x23e0`
   after reset/close frees it. Patch-owned snapshot + refresh swap (see inventory).
2. **View pointer retirement** — Clear `document+0x5838` (and patch-owned view
   pair) before the production-view destructor frees the view.
3. **Anomaly zone join** — Call `ProductionStop` (`0x1406920f0`) before
   `ProductionDoc_dtor` (`0x14067fc20`) continues into DeleteVector / Zone_dtor.

## Follow-ons (not this workstream)

- Final-mask uniqueness (sections sharing a component)
- DWORD wider-intermediate product
- Native station install / W7 qualification (still waived-unverified)

## Success

`python tools/verify_hardened_patch.py --revision rev6 --code-only` passes.
Close-path hooks present in the built PE when not `--code-only`. No claim of
production readiness without a separate native authorization.
