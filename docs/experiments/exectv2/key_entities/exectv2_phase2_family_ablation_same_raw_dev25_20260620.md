# ExECTv2 Phase 2 Same-Raw Projection-Family Ablation

Date: 2026-06-20

No model calls. Re-projects the genuine v0.39 live LLM `raw_output` through current v0.42 deterministic projection under each quarantine switch configuration, then scores the same dev25 letters.

- Source artifact: `exectv2_target_indicators_single_call_v039_live_dev25_qwen36_35b_ollama_cpu_ctx16384_20260619.jsonl`
- Rows: 25 (dev split)
- Note: v0.39 live raw_output is the genuine untouched model output; the v0.40-v0.42 reproject artifacts store post-projection raw and are unsuitable as the same-raw source.

## Surfaces

- `headline`: cui_projected_headline_scores (lenient redefined key)
- `benchmark`: cui_audit benchmark_f1_after_cui_projection (paper-comparable)
- `dx_fidelity`: Diagnosis.concept_negation companion
- `sf_fidelity`: SeizureFrequency.active_rate_fidelity companion

## Configuration Scores

| Config | Headline | Benchmark | Dx concept_negation | SF active_rate_fidelity | Family fires |
| --- | ---: | ---: | ---: | ---: | ---: |
| `baseline` | 0.9675 | 0.3663 | 0.9877 | 0.6207 | 0 |
| `audit_all` | 0.9839 | 0.3913 | 0.9877 | 0.6667 | 7 |
| `projected_christmas_point_to_month_date` | 0.9675 | 0.3663 | 0.9877 | 0.6207 | 1 |
| `projected_diagnosis_context_to_controlled_sf_state` | 0.9675 | 0.3723 | 0.9877 | 0.6207 | 1 |
| `projected_diagnosis_context_to_frequent_myoclonic_jerks` | 0.9675 | 0.3663 | 0.9877 | 0.6207 | 1 |
| `projected_diagnosis_context_to_remote_last_seizures_state` | 0.9717 | 0.3723 | 0.9877 | 0.6207 | 1 |
| `projected_four_since_last_clinic` | 0.9675 | 0.3663 | 0.9877 | 0.6207 | 1 |
| `projected_infrequent_context_state` | 0.9717 | 0.3723 | 0.9877 | 0.6207 | 1 |
| `projected_several_since_last_clinic` | 0.9756 | 0.3736 | 0.9877 | 0.6667 | 1 |
| `repaired_last_event_evidence` | 0.9675 | 0.3663 | 0.9877 | 0.6207 | 0 |
| `repaired_since_last_clinic_count_evidence` | 0.9675 | 0.3663 | 0.9877 | 0.6207 | 0 |

## Per-Family Keep/Cut Verdicts

Marginal effect of enabling exactly one quarantined family versus the all-quarantined baseline.

| Family | d Headline | d Benchmark | d DxFid | d SFFid | Fires | Verdict | Reason |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `projected_christmas_point_to_month_date` | +0.0000 | +0.0000 | +0.0000 | +0.0000 | 1 | INSUFFICIENT EVIDENCE | fires but no net score movement on dev25 |
| `projected_diagnosis_context_to_controlled_sf_state` | +0.0000 | +0.0060 | +0.0000 | +0.0000 | 1 | KEEP CANDIDATE | improves the paper-comparable benchmark key |
| `projected_diagnosis_context_to_frequent_myoclonic_jerks` | +0.0000 | +0.0000 | +0.0000 | +0.0000 | 1 | INSUFFICIENT EVIDENCE | fires but no net score movement on dev25 |
| `projected_diagnosis_context_to_remote_last_seizures_state` | +0.0042 | +0.0060 | +0.0000 | +0.0000 | 1 | KEEP CANDIDATE | improves the paper-comparable benchmark key |
| `projected_four_since_last_clinic` | +0.0000 | +0.0000 | +0.0000 | +0.0000 | 1 | INSUFFICIENT EVIDENCE | fires but no net score movement on dev25 |
| `projected_infrequent_context_state` | +0.0042 | +0.0060 | +0.0000 | +0.0000 | 1 | KEEP CANDIDATE | improves the paper-comparable benchmark key |
| `projected_several_since_last_clinic` | +0.0081 | +0.0073 | +0.0000 | +0.0460 | 1 | KEEP CANDIDATE | improves the paper-comparable benchmark key |
| `repaired_last_event_evidence` | +0.0000 | +0.0000 | +0.0000 | +0.0000 | 0 | INSUFFICIENT EVIDENCE | no same-raw fire or score change on dev25 |
| `repaired_since_last_clinic_count_evidence` | +0.0000 | +0.0000 | +0.0000 | +0.0000 | 0 | INSUFFICIENT EVIDENCE | no same-raw fire or score change on dev25 |

## Interpretation

Keep candidates are families that move the paper-comparable benchmark key without degrading a clinical-fidelity companion. Families that move only the lenient headline, lower the benchmark, or hurt fidelity are cut. Families with no same-raw effect on dev25 stay quarantined as insufficient-evidence until a broader held-out surface exists.

**Single-letter caveat.** Every keep-candidate family fires on exactly one dev25 letter, so each benchmark gain rests on a single letter. This is the overfit risk the projection-family overfit audit named: a one-letter benchmark nudge cannot distinguish a clinically general projection from a benchmark-letter patch. 'Keep candidate' here means 'promote to a held-out check', not 'restore to the default pipeline'.

**Reproducibility note.** This same-raw baseline (default quarantine) scores headline 0.9675 / benchmark 0.3663 when the genuine v0.39 live raw is re-projected through v0.42 code. The published Phase 0 v0.42 artifact reads headline 0.9487 / benchmark-after-CUI 0.3816. The two differ because the v0.40-v0.42 reproject chain stored already-projected output back into `raw_output` and re-projected it at each hop. The genuine-raw re-projection is the defensible same-raw surface for this ablation; the chained artifact is double-projected.
