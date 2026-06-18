# ExECTv2 SeizureFrequency Candidate-Span State Adjudicator v0.1 dev140

Date: 2026-06-18  
Split: dev140  
Model: `openai/gpt-4.1-mini`  
Substrate: `exectv2_llm_only_key_entities_structured_v0.5`

## Decision

Revise-only. Candidate-span/state adjudication is a better SeizureFrequency
architecture than the broad v0.4 verifier on dev140, but it still misses the
`0.8` clinical-recovery target.

| Run | F1 | P | R | Gate |
| --- | ---: | ---: | ---: | --- |
| SF verifier v0.4 dev140 | 0.623 | 0.591 | 0.658 | 0 call failures, 0 parse failures, evidence 0.9905 |
| SF state adjudicator v0.1 dev25 pilot | 0.921 | 0.906 | 0.935 | 0 call failures, 0 parse failures, evidence 1.0000 |
| SF state adjudicator v0.1 dev140 | 0.674 | 0.653 | 0.695 | 0 call failures, 0 parse failures, evidence 1.0000 |

## Interpretation

The candidate-span architecture improves dev140 SF headline F1 by `+0.051`
over v0.4 (`0.623` -> `0.674`) and keeps the engineering gate clean. This
supports the architectural path: deterministic span proposals can focus the
model on clinically meaningful state anchors while leaving final state, text
normalization, and mention selection to the LLM.

The dev25 result did not transfer. The residual ledger shows the remaining
problem is no longer evidence validity or parsing; it is generic seizure-state
precision/recall. Active-rate recall is relatively strong (`0.820`) but active
generic seizure over-emission is now the largest precision leak. Unknown states
remain weak (`F1 0.351`), especially generic seizure unknown misses.

## Residual Pattern

From `experiments/exectv2_sf_state_adjudicator_v01_residual_ledger_dev140_20260618.md`:

- Gold misses: generic seizure unknown `11`, generic seizure-free `10`, generic seizure active-rate `5`.
- Predicted over-emissions: generic seizure active-rate `18`, generic seizure-free `9`, generic seizure unknown `7`.
- State totals: active-rate `16` misses / `39` over-emissions; seizure-free `18` / `16`; unknown `23` / `14`.

## Next Loop

Do not discard the candidate-span path, but tighten it. The next SF iteration
should add a candidate reject/keep discipline for generic seizure spans, with
explicit distinction between:

- true current rate vs historical single event or previous-event reference;
- seizure-free duration/point-in-time vs bare "remains seizure free";
- qualitative unknown/change vs generic active-rate inflation;
- named seizure-type rates vs unlabelled episode/event rates.

Diagnosis remains below target separately and should continue down the planned
heading-decomposition plus narrative seizure-type collector path.
