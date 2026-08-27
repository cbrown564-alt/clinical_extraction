# Gemini 3.7 Flash successor live development cells

Date: 2026-08-13
Status: complete for the two permitted development cells
Protocol: [successor protocol](six_model_gemini37flash_successor_protocol_2026-08-13.md)
Decision: [0051](../../decisions/0051-gemini-37-flash-succeeds-gpt41mini-six-model-slot.md)

Thinking is `reasoning_effort=low`. These are development candidate cells, not
Decision 0050 primary fills and not holdout.

## ExECT `dev140`

- Model: `gemini/gemini-3.7-flash`
- Prompt: `exectv2_hybrid_key_family_event_ledger_v0.9.24`
- Split: manifest `dev` (140 letters)
- Call / parse failures: 0 / 0
- Selected scorer: `clinical_headline` after default assembly

| View | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| raw_candidate | 0.8444 | 0.7640 | 0.7634 | 0.9580 | 0.9470 |
| clinical_headline | **0.8952** | 0.8715 | 0.8179 | 0.9559 | 0.9470 |

Owners: `experiments/exectv2_six_model_single_call_gemini37flash_dev140_20260813.json`
and the matching jsonl / structured / SF sidecars.

## Gan `dev750`

- Model: `gemini/gemini-3.7-flash`
- Prompt: `gan2026_hybrid_structured_events_v0.5`
- Repair: `hybrid_full_stack`
- Split: `validation` / `gan2026_split_v1` (750 rows)
- Call / parse failures: 0 / 0
- Purist **676/750 (0.9013)**
- Pragmatic **696/750 (0.9280)**

Owner:
`experiments/gan2026_six_model_current_stack_dev750_replay_20260813/gemini37flash/validation750.rows.jsonl`

That file is a live cell in the current-stack `dev750` tree. It is not a
no-call replay of an older raw.

## Holdout (aggregate-only)

Live locked-split cells, no row inspection
([holdout protocol](six_model_gemini37flash_holdout_protocol_2026-08-13.md),
[decision 0052](../../decisions/0052-gemini-37-flash-holdout-six-model-slot.md)):

| Cell | Gemini 3.7 Flash |
| --- | ---: |
| ExECT `test60` clinical headline | **0.8375** |
| Gan `test450` Purist | **373/450 (0.8289)** |
| Gan `test450` Pragmatic | 385/450 (0.8556) |

These replace GPT-4.1-mini in the living six-model hybrid panel. Sol remains
the Decision 0046 / 0050 method-identity row.

## Claim boundary

Development cells plus aggregate-only holdout. Not the published ExECT
benchmark. Not clinical validation. Not a change of Sol method identity.
