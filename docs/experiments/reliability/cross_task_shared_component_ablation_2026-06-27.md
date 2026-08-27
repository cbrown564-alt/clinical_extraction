# Cross-Task Shared-Component Ablation

- Generated: `2026-06-27`
- JSON: `experiments/cross_task_shared_component_ablation_2026-06-27.json`
- Harness: `scripts/cross_task_shared_component_ablation.py`
- Core module: `src/clinical_extraction/core/cross_task_component_ablation.py`
- Claim boundary: validation-side cross-task component ablation; aggregate-only replay from saved ExECTv2 dev140 and Gan 2026 validation750 outputs; no model calls or row-level inspection
- Row inspection policy: `aggregate_only`
- No model calls; reads saved dev140 / validation750 replay artifacts only.

## Result

Turning off the exact-substring `evidence_validation` check changed neither
declared validation score: contribution Δ = **0.0000** on ExECTv2 dev140 (v08
control) and Gan 2026 validation750 (deterministic `evidence_trace_check`). The
saved outputs already passed the check. This result shows score invariance for
these two replays; it does not show that evidence validation is generally
unnecessary.

Removing `standard_dictionary` on ExECTv2 or `normalize` on Gan lowered the
named scores by 0.0389 and 0.0293 respectively. These are different operations
(CUI/dictionary normalization versus Gan label normalization), so the result
does not establish one shared mechanism.

**Deferred:** date-arithmetic policy has no clean cross-task ladder rung; isolating it requires Gan one-family-off replays (`seizure_free_duration_date_instrumentation`, etc.) outside this harness.

## Primary Table (`evidence_validation`)

| Component | Task | Split | Baseline | Component-off | Δ (contribution) | Metric |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `evidence_validation` | exectv2 | dev140 | 0.8308 | 0.8308 | +0.0000 | clinical_headline_f1 |
| `evidence_validation` | gan2026 | validation | 0.9093 | 0.9093 | +0.0000 | purist_accuracy |

## Secondary Table (SF-normalization structure)

| Component | Task | Split | Baseline | Component-off | Δ (contribution) | Metric |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `standard_dictionary` | exectv2 | dev140 | 0.8697 | 0.8308 | +0.0389 | clinical_headline_f1 |
| `standard_dictionary` | gan2026 | validation | 0.6360 | 0.6067 | +0.0293 | purist_accuracy |

Contribution Δ = baseline − component-off (positive means removing the component lowers the score on this split).

## Mapping Notes

### `evidence_validation`

- ExECTv2 (exectv2_holistic_finding_assembly_v08_dev140): `evidence_valid` → `source_scored`
- Gan2026 (deterministic_canonical_pipeline): `evidence_trace_check` → `benchmark_repair`
- Gan mapping note: the deterministic method has a separate exact-substring evidence check. The LLM-with-rules and LLM-only methods place their evidence logic in `evidence_projection` or `label_repair` instead.

### `standard_dictionary`

- ExECTv2 (exectv2_holistic_finding_assembly_v08_dev140): `dictionary_normalized` → `evidence_valid`
- Gan2026 (gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07): `normalize` → `llm_selection`
- Gan mapping note: Format-level SF label normalization on LLM-with-rules structured-events; not identical to ExECTv2 CUI/dictionary normalization but the closest SF-normalization rung on the Gan ladder.

## Source files

- ExECTv2 component-off: `experiments/exectv2_component_off_replay_dev140_20260626.json`
- Gan2026 stage ladder: `experiments/gan2026_component_stage_ladder_validation_20260624.json`
- Component definitions: `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/reports/component_ablation/definitions.yaml`

## Interpretation Boundary

These rows measure whether turning off one shared component changes the declared validation-side score on each task's representative architecture. They do not prove a component is globally unnecessary, and they must not be blended into reliability-scorecard or holdout claims.
