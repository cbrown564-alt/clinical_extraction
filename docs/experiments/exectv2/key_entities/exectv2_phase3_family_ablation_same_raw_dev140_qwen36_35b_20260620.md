# ExECTv2 Phase 2 Same-Raw Projection-Family Ablation

Date: 2026-06-20

No model calls. Re-projects the source live LLM `raw_output` through current v0.42 deterministic projection under each quarantine switch configuration, then scores the same source letters.

- Source artifact: `exectv2_target_indicators_single_call_v042_live_default_quarantine_dev140_qwen36_35b_ollama_autogpu_ctx16384_20260620.jsonl`
- Rows: 140 (dev split)
- Note: Live v0.42 local-Qwen dev140 raw output generated under default quarantined projection switches; replay enables one quarantined family at a time for attribution.

## Surfaces

- `headline`: cui_projected_headline_scores (lenient redefined key)
- `benchmark`: cui_audit benchmark_f1_after_cui_projection (paper-comparable)
- `dx_fidelity`: Diagnosis.concept_negation companion
- `sf_fidelity`: SeizureFrequency.active_rate_fidelity companion

## Configuration Scores

| Config | Headline | Benchmark | Dx concept_negation | SF active_rate_fidelity | Family fires |
| --- | ---: | ---: | ---: | ---: | ---: |
| `baseline` | 0.7153 | 0.2339 | 0.6693 | 0.2887 | 0 |
| `audit_all` | 0.7162 | 0.2383 | 0.6693 | 0.3093 | 7 |
| `projected_christmas_point_to_month_date` | 0.7153 | 0.2339 | 0.6693 | 0.2887 | 0 |
| `projected_diagnosis_context_to_controlled_sf_state` | 0.7153 | 0.2350 | 0.6693 | 0.2887 | 1 |
| `projected_diagnosis_context_to_frequent_myoclonic_jerks` | 0.7153 | 0.2339 | 0.6693 | 0.2887 | 1 |
| `projected_diagnosis_context_to_remote_last_seizures_state` | 0.7162 | 0.2350 | 0.6693 | 0.2887 | 1 |
| `projected_four_since_last_clinic` | 0.7153 | 0.2351 | 0.6693 | 0.2990 | 1 |
| `projected_infrequent_context_state` | 0.7153 | 0.2339 | 0.6693 | 0.2887 | 2 |
| `projected_several_since_last_clinic` | 0.7153 | 0.2351 | 0.6693 | 0.2990 | 1 |
| `repaired_last_event_evidence` | 0.7153 | 0.2339 | 0.6693 | 0.2887 | 0 |
| `repaired_since_last_clinic_count_evidence` | 0.7153 | 0.2339 | 0.6693 | 0.2887 | 0 |

## Per-Family Keep/Cut Verdicts

Marginal effect of enabling exactly one quarantined family versus the all-quarantined baseline.

| Family | d Headline | d Benchmark | d DxFid | d SFFid | Fires | Verdict | Reason |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `projected_christmas_point_to_month_date` | +0.0000 | +0.0000 | +0.0000 | +0.0000 | 0 | INSUFFICIENT EVIDENCE | no same-raw fire or score change on source rows |
| `projected_diagnosis_context_to_controlled_sf_state` | +0.0000 | +0.0011 | +0.0000 | +0.0000 | 1 | KEEP CANDIDATE | improves the paper-comparable benchmark key |
| `projected_diagnosis_context_to_frequent_myoclonic_jerks` | +0.0000 | +0.0000 | +0.0000 | +0.0000 | 1 | INSUFFICIENT EVIDENCE | fires but no net score movement on source rows |
| `projected_diagnosis_context_to_remote_last_seizures_state` | +0.0009 | +0.0011 | +0.0000 | +0.0000 | 1 | KEEP CANDIDATE | improves the paper-comparable benchmark key |
| `projected_four_since_last_clinic` | +0.0000 | +0.0012 | +0.0000 | +0.0103 | 1 | KEEP CANDIDATE | improves the paper-comparable benchmark key |
| `projected_infrequent_context_state` | +0.0000 | +0.0000 | +0.0000 | +0.0000 | 2 | INSUFFICIENT EVIDENCE | fires but no net score movement on source rows |
| `projected_several_since_last_clinic` | +0.0000 | +0.0012 | +0.0000 | +0.0103 | 1 | KEEP CANDIDATE | improves the paper-comparable benchmark key |
| `repaired_last_event_evidence` | +0.0000 | +0.0000 | +0.0000 | +0.0000 | 0 | INSUFFICIENT EVIDENCE | no same-raw fire or score change on source rows |
| `repaired_since_last_clinic_count_evidence` | +0.0000 | +0.0000 | +0.0000 | +0.0000 | 0 | INSUFFICIENT EVIDENCE | no same-raw fire or score change on source rows |

## Interpretation

Keep candidates are families that move the paper-comparable benchmark key without degrading a clinical-fidelity companion. Families that move only the lenient headline, lower the benchmark, or hurt fidelity are cut. Families with no same-raw effect stay quarantined as insufficient-evidence until a broader surface exists.

**Single-letter caveat.** Every keep-candidate family fires on exactly one source letter, so each benchmark gain rests on a single letter. This is the overfit risk the projection-family overfit audit named: a one-letter benchmark nudge cannot distinguish a clinically general projection from a benchmark-letter patch. 'Keep candidate' here means 'promote to a broader check', not 'restore to the default pipeline'.

## Promotion Decision

Do not restore any quarantined family to the default prediction pipeline.

The dev140 replay gives a broader same-raw surface than dev25, but every
positive marginal effect still comes from exactly one source letter. The effects
are also small: the best single-family benchmark deltas are `+0.0012`, and
`audit_all` moves benchmark from `0.2339` to `0.2383` while leaving the headline
essentially unchanged. This is useful attribution evidence, not promotion
evidence.

Disposition after dev140:

- Keep quarantined as audit-only candidates:
  `projected_diagnosis_context_to_controlled_sf_state`,
  `projected_diagnosis_context_to_remote_last_seizures_state`,
  `projected_four_since_last_clinic`, and
  `projected_several_since_last_clinic`.
- Keep quarantined as insufficient evidence:
  `projected_christmas_point_to_month_date`,
  `projected_diagnosis_context_to_frequent_myoclonic_jerks`,
  `projected_infrequent_context_state`, `repaired_last_event_evidence`, and
  `repaired_since_last_clinic_count_evidence`.

The next useful work is no longer projection-family promotion. It is deciding
the next architecture move from the dev140 default-quarantine output: the live
run scored headline `0.7153` and benchmark `0.2339`, with the largest shortfalls
in Diagnosis and SeizureFrequency and `SeizureFrequency.active_rate_fidelity`
only `0.2887`.

**Reproducibility note.** This same-raw baseline (default quarantine) scores headline 0.7153 / benchmark 0.2339. All marginal family effects above are within-source replays of the same saved live raw output; they should not be compared as separate live model conditions.
