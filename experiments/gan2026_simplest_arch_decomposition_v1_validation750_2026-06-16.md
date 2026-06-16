# Gan 2026 — Simplest-Architecture Step-1 Decomposition (validation750)

Date: 2026-06-16

Replay-only decomposition of the V12 fresh-evidence hybrid; no model calls,
no test exposure. Source artifact:
`experiments\gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13.jsonl` (750 rows).

Plan: `docs/research/gan2026_simplest_near_ceiling_architecture_plan_2026-06-16.md`.

## Ladder-middle Purist (each layer a superset of the one above)

| Layer | Model passes | Purist | Δ vs above |
| --- | ---: | ---: | ---: |
| GPT structured-event only (`v0_reference`) | 1 | 661/750 = 0.881 | — |
| + fresh-evidence reasoner, raw | 3+reasoner | 676/750 = 0.901 | +15 |
| + format-only label repair | 3+reasoner | 676/750 = 0.901 | +0 |
| + full deterministic guard layer (`final`) | 3+reasoner | 682/750 = 0.909 | +6 |

Reasoner net vs GPT-only: **+21** rows. Deterministic guard layer net: **+6** rows.

## Where the reasoner's lift comes from (action decomposition vs GPT-only)

- Replace actions: **43 helped** (V0 wrong → final right), **22 hurt** (V0 right → final wrong), 117 neutral → net **+21**.
- Keep actions: 536 correct, 32 wrong.

## Deterministic guard layer — per-guard marginal (rows where the guard fired)

Guard ON = fall back to GPT original; guard OFF = keep the model's replacement.
Marginal = (correct with guard) − (correct without).

| Guard reason | Rows fired | Correct ON | Correct OFF | Marginal |
| --- | ---: | ---: | ---: | ---: |
| original_seizure_free_to_unknown_or_no_reference | 5 | 4 | 0 | +4 |
| unscorable_fresh_label | 2 | 2 | 0 | +2 |
| evidence_not_exact | 1 | 1 | 0 | +1 |

Total guard fallbacks fired: **8** of 750 rows (1.1%).

## Reading

- On validation750 the **reasoner's replace mechanism** is the engine of the
  lift over a single GPT structured-event pass; the **deterministic guard
  layer is near-inert here** (fires on a handful of rows).
- This does NOT clear the guards: the synthesis established that validation
  under-samples the clinical-wall cases the guards target, which are
  concentrated in test450. Guard value can only be read on test.
- The live questions for Step 2 (validation-only): does a **GPT-trace-only
  reasoner** (drop Qwen+DeepSeek from the prompt; 1 model reused) retain the
  reasoner's +21-row lift? If so, 3 models collapse to 1.
