# ExECTv2 SeizureFrequency Candidate-Span State Adjudicator v0.4 dev140

Date: 2026-06-18  
Split: dev140  
Model: `openai/gpt-4.1-mini`  
Substrate: `exectv2_llm_only_key_entities_structured_v0.5`

## Decision

Revise-only, but v0.4 is the current best SeizureFrequency dev140 candidate.
Typed candidate decomposition improves over v0.3 but remains below the `0.8`
clinical-recovery target.

| Run | F1 | P | R | Gate |
| --- | ---: | ---: | ---: | --- |
| SF state adjudicator v0.1 dev140 | 0.674 | 0.653 | 0.695 | 0 call failures, 0 parse failures, evidence 1.0000 |
| SF state adjudicator v0.3 dev140 | 0.681 | 0.667 | 0.695 | 0 call failures, 0 parse failures, evidence 1.0000 |
| SF state adjudicator v0.4 dev25 pilot | 0.935 | 0.935 | 0.935 | 0 call failures, 0 parse failures, evidence 1.0000 |
| SF state adjudicator v0.4 dev140 | 0.707 | 0.704 | 0.711 | 0 call failures, 0 parse failures, evidence 1.0000 |

## Interpretation

v0.4 adds typed candidate metadata before the LLM adjudication step:
generic/named active-rate, generic/named seizure-free anchor, generic/named
qualitative change, prior-event reference, unlabelled episode/event, and
diagnosis/context. This is the first SF iteration since v0.1 to produce a clear
dev140 improvement rather than local-only prompt movement.

The gain is meaningful but not sufficient. Overall F1 improves from `0.681` to
`0.707`; precision improves from `0.667` to `0.704`; recall improves from
`0.695` to `0.711`. Unknown-state F1 rises again (`0.424` -> `0.525`), while
active-rate also improves (`0.722` -> `0.746`). Seizure-free slips slightly
(`0.754` -> `0.738`) and is now the largest residual pocket.

## Residual Pattern

From `experiments/exectv2_sf_state_adjudicator_v04_residual_ledger_dev140_20260618.md`:

- Gold misses: generic seizure-free `12`, generic seizure unknown `6`, generic
  seizure active-rate `4`, generalised-tonic-clonic active-rate `4`.
- Predicted over-emissions: generic seizure active-rate `13`, generalised
  tonic-clonic active-rate `5`, generic seizure-free `5`, generic seizure
  unknown `4`.
- State totals: active-rate `17` misses / `32` over-emissions; seizure-free
  `20` / `12`; unknown `17` / `12`.

## Next Loop

Keep v0.4 as the current numeric SF candidate (`0.707`). The next SF iteration
should preserve the typed-candidate scaffold but specialize seizure-free anchors:

- distinguish true last-event/no-further-seizure anchors from previous-event
  references, driving/legal advice, and historical best periods;
- explicitly recover generic seizure-free anchors that mention no further
  seizures since clinic, medication change, surgery, date, or age range;
- keep the v0.4 generic/named active-rate split because it improved precision
  without collapsing recall.

Diagnosis remains separately below target; its latest accept/reject gate v0.1
under-recalled and needs a named seizure-type recovery lane before another
dev140 run.
