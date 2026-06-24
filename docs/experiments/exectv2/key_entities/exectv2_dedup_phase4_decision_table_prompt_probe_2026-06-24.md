# ExECTv2 Deduplicated Clinical Facts Decision-Table Prompt Probe

Date: 2026-06-24

## Question

The Phase 4 error analysis showed several apparently prompt-addressable
failures: active-rate overcalls from qualitative seizure language, planned
investigations emitted as completed tests, rescue/contingency medication emitted
as current regimen, and diagnosis ontology/granularity confusions.

This probe tested whether clearer scorer-facing prompt guidelines can recover
meaningful headroom without changing the attribution boundary. Deterministic
code still only validates evidence, maps representation fields one-to-one, and
scores.

## Prompt Conditions

Two new prompt profiles were added:

- `decision_table`: adds explicit decision tables for all four families.
- `decision_table_sf_inv`: keeps compact prompts for Diagnosis and Prescription,
  and applies decision tables only to SeizureFrequency and Investigations.

The mixed profile was tested because the all-family decision table improved
SeizureFrequency and Investigations on dev25 but reduced Diagnosis and
Prescription recall.

## Dev25 Results

| Variant | Split | Overall | P | R | Diagnosis | SF | Rx | Inv | Evidence validity | Failures |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Phase 4 compact per-family | dev25 | 0.796 | 0.784 | 0.808 | 0.698 | 0.690 | 0.873 | 0.976 | 0.9609 | 0 |
| all-family `decision_table` | dev25 | 0.785 | 0.812 | 0.760 | 0.665 | 0.717 | 0.849 | 1.000 | 0.9587 | 0 |
| mixed `decision_table_sf_inv` | dev25 | 0.828 | 0.808 | 0.848 | 0.686 | 0.717 | 0.938 | 1.000 | 0.9624 | 0 |

Primary dev25 artifacts:

- `experiments/exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_per_family_phase4_decision_table_dev25_gpt41mini_20260624.{jsonl,md}`
- `experiments/exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_per_family_phase4_decision_table_sf_inv_dev25_gpt41mini_20260624.{jsonl,md}`

## Dev140 Confirmation

The mixed profile cleared the dev25 gate and was confirmed on dev140.

| Variant | Split | Overall | P | R | Diagnosis | SF | Rx | Inv | Evidence validity | Failures |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Phase 3 single-prompt v0.5 | dev140 | 0.710 | 0.691 | 0.729 | 0.672 | 0.558 | 0.814 | 0.832 | 0.9613 | 0 |
| mixed `decision_table_sf_inv` | dev140 | 0.729 | 0.753 | 0.707 | 0.681 | 0.556 | 0.851 | 0.883 | 0.9694 | 0 |

Primary dev140 artifact:

- `experiments/exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_per_family_phase4_decision_table_sf_inv_dev140_gpt41mini_20260624.{jsonl,md}`

Strict `model_preserving_canonical` remains diagnostic only for this route:
dev140 F1 `0.130`.

## Interpretation

The user hypothesis was partly correct: some failure modes are prompt-addressable.
The decision tables improved precision-heavy behavior on the small dev25 gate:
SeizureFrequency rose from `0.690` to `0.717`, and Investigations became
perfect on that slice. Applying the tables only to SF/Investigations preserved
the better compact behavior for Diagnosis/Prescription and produced the best
dev25 result so far (`0.828`).

The dev140 confirmation is more sobering. The mixed profile improved overall
clinical-recovery F1 from the Phase 3 dev140 plateau (`0.710`) to `0.729`, with
stronger Prescription and Investigations and a small Diagnosis gain. It did not
improve SeizureFrequency at scale (`0.558` -> `0.556`) and remains far below
the `>0.900` target.

## Conclusion

Clearer prompt guidelines recover some headroom and are worth retaining as a
comparator, but they do not resolve the core LLM-only plateau. The remaining
barrier is still prediction-bearing ontology/state selection, especially
SeizureFrequency state/unit recovery and Diagnosis granularity. Further gains
probably require either much stronger in-context ontology supervision or a
separately declared hybrid/selector-owned architecture.
