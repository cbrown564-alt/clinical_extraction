# ExECTv2 SeizureFrequency State Adjudicator v0.5 dev140

Date: 2026-06-18  
Split: dev140  
Model: `openai/gpt-4.1-mini`  
Substrate: `exectv2_llm_only_key_entities_structured_v0.5`

## Decision

Revise-only, but v0.5 replaces v0.4 as the current SeizureFrequency dev140
candidate. It improves the headline while preserving clean gates, but remains
below the `0.8` clinical-recovery target.

| Run | F1 | P | R | Gate |
| --- | ---: | ---: | ---: | --- |
| SF state adjudicator v0.4 dev140 | 0.707 | 0.704 | 0.711 | 0 call failures, 0 parse failures, evidence 1.0000 |
| SF state adjudicator v0.5 dev25 pilot | 0.918 | 0.933 | 0.903 | 0 call failures, 0 parse failures, evidence 1.0000 |
| SF state adjudicator v0.5 dev140 | 0.721 | 0.710 | 0.733 | 0 call failures, 0 parse failures, evidence 1.0000 |

## Interpretation

v0.5 keeps the typed candidate scaffold and adds a seizure-free-anchor guide:
current no-further-seizure statements, medication-change/surgery/last-clinic
anchors, and last-event date/duration anchors are separated from previous-event
references, historical best periods, driving advice, and non-seizure episodes.
It also extends the benchmark-format SF CUI lexicon for residual-supported
concept phrases such as `no further seizures`, `focal to bilateral seizures`,
`focal impaired awareness seizures`, `focal dyscognitive seizures`, and
`absence events`.

The intended slice improved. Seizure-free F1 moved from `0.738` to `0.781`, and
the overall headline moved from `0.707` to `0.721`. Active-rate also improved
from `0.746` to `0.762`. Unknown-state F1 regressed from `0.525` to `0.476`,
so the next SF loop should focus on unknown/change-state recovery without
undoing the seizure-free gains.

## Residual Pattern

From
`experiments/exectv2_sf_state_adjudicator_v05_residual_ledger_dev140_20260618.md`:

- Gold misses remain balanced across active-rate `17`, seizure-free `15`, and
  unknown `18`.
- Predicted over-emissions are active-rate `28`, seizure-free `13`, and unknown
  `15`.
- The largest residual key is generic seizures unknown-state misses, followed
  by generic seizure-free misses and generic active-rate over-emission.

## Next Loop

Keep v0.5 as the current numeric SF candidate (`0.721`). The next SF iteration
should add a constrained unknown/change-state lane:

- recover explicit generic seizure change phrases such as returned, worse,
  increased, improved, frequent, infrequent, and controlled;
- avoid converting epilepsy stability, non-seizure episodes, or treatment
  response without explicit seizure wording into unknown states;
- preserve v0.5 seizure-free rendering guidance and the finite benchmark-format
  CUI projection additions as controlled, test-covered variables.
