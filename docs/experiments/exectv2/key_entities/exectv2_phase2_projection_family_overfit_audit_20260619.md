# ExECTv2 Phase 2 Projection Family Overfit Audit

Date: 2026-06-19

Original scope: analysis only. The counts below are derived from saved
per-letter `gate_warnings` in the v0.39-v0.42 local-Qwen dev25 artifacts. These
are warning-family fire counts, not a formal rule registry.

Follow-up implementation, 2026-06-19:
`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/llm/llm_target_indicators_single_call.py`
now quarantines the named one-letter target projection families by default and
exposes `audit_only_projection_replay_switches()` for same-raw replay. A
quarantined family emits `quarantined_projection_family: <family>` instead of
adding prediction-bearing mentions or applying the phrase-specific repair.

## Sources

- Status/research context: `PROJECT_STATUS.md`,
  `docs/research/contribution_thesis.md`,
  `docs/decisions/0031-diagnosis-target-core-scores-projected-clinical-facts.md`,
  `docs/research/exectv2_target_indicator_hybrid_pipeline_report_2026-06-19.md`
- Scoring/projection scripts: `scripts/phase0_key_inspect.py`,
  `scripts/phase0_dual_scoring.py`
- Projection code/tests:
  `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/llm/llm_target_indicators_single_call.py`,
  `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/scoring.py`,
  `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/benchmark_projection.py`,
  `tests/test_exectv2_target_indicators_single_call.py`
- Counted artifacts:
  `experiments/exectv2_target_indicators_single_call_v039_live_dev25_qwen36_35b_ollama_cpu_ctx16384_20260619.jsonl`,
  `experiments/exectv2_target_indicators_single_call_v040_reproject_v039live_dev25_qwen36_35b_ollama_cpu_ctx16384_20260619.jsonl`,
  `experiments/exectv2_target_indicators_single_call_v041_reproject_v040live_dev25_qwen36_35b_ollama_cpu_ctx16384_20260619.jsonl`,
  `experiments/exectv2_target_indicators_single_call_v042_reproject_v041live_dev25_qwen36_35b_ollama_cpu_ctx16384_20260619.jsonl`

## Method

Parsed each JSONL row, filtered `gate_warnings` beginning with `Diagnosis:` or
`SeizureFrequency:`, normalized the first warning token as the family name, and
counted unique dev letters plus occurrences. This reuses saved artifacts only
and makes no model calls.

Limitations:

- `gate_warnings` expose many, but not all, projection decisions. They do not
  carry version-introduction metadata.
- `active recent-event preservation` is named in the v0.42 prose but is not
  exposed as a positive warning family in the saved rows. It appears only
  indirectly through preserved active recent-event outputs, so no exact fire
  count is claimed here.
- Evidence repair hooks such as `repaired_since_last_clinic_count_evidence` and
  `repaired_last_event_evidence` are present in code/tests, but did not appear
  in the counted saved dev25 artifacts.

## Suspicious Hard-Coded Families

| Family | Saved fire count | Letters | Classification | Recommendation |
| --- | ---: | --- | --- | --- |
| `projected_four_since_last_clinic` | 1 letter in each counted artifact | `EA0002` | Letter-specific patch | Quarantine/cut before Phase 1/2 promotion. Replace only with a general number-word plus last-clinic anchor parser if needed. |
| `repaired_since_last_clinic_count_evidence` | 0 saved fires; tested only | n/a | Letter-specific evidence repair | Quarantine/cut or replace with general clause-reordering evidence repair. Current pattern is tied to "four secondary generalised seizures". |
| `repaired_last_event_evidence` | 0 saved fires; tested only | n/a | Letter-specific evidence repair | Quarantine/cut or replace with general holiday/month evidence repair. Current hook is tied to "last one being around christmas time in 2017". |
| `projected_christmas_point_to_month_date` | 1 letter in v0.40 replay | `EA0011` | Benchmark/scorer projection, high overfit risk | Keep only if generalized as holiday-to-month normalization and covered by broader tests; otherwise quarantine. |

## v0.42 Named SF Families

| Prose family | Warning hook | Saved v0.42 fires | Letters | Classification | Recommendation |
| --- | --- | ---: | --- | --- | --- |
| Remote teenage last-seizure projection | `projected_diagnosis_context_to_remote_last_seizures_state` | 1 | `EA0010` | Letter-specific unless generalized | Quarantine as-is; phrase is hard-coded to "His last seizures were in his teenage years". |
| Later infrequent convulsive-state projection | `projected_infrequent_context_state` | 1 | `EA0011` | Letter-specific patch | Quarantine/cut; exact "infrequent focal to bilateral convulsive seizures" context. |
| Controlled-on-dose projection from Diagnosis context | `projected_diagnosis_context_to_controlled_sf_state` | 1 | `EA0022` | Benchmark/scorer projection, possibly generalizable | Keep only behind a named general "controlled on dose/drug change" family and hard-slice tests. |
| Frequent myoclonic-jerk projection | `projected_diagnosis_context_to_frequent_myoclonic_jerks` | 1 | `EA0025` | Letter-specific patch | Quarantine/cut; exact "very frequent myoclonic jerks" context. |
| Active recent-event preservation | no positive warning hook | not exposed | likely `EA0019` pattern | Missing hook | Add instrumentation before any promotion if this remains prediction-bearing. |
| Positive-rate zero-state suppression | `dropped_inconsistent_zero_state_with_active_rate` | 1 | `EA0025` | Generalizable semantic guard | Keep as a general contradiction rule if tested beyond this letter. |

## Broader Diagnosis/SF Family Counts

Highest-frequency families across saved artifacts are likely general
normalization rather than overfit:

| Family | v0.39 | v0.40 replay | v0.41 replay | v0.42 replay | Classification |
| --- | ---: | ---: | ---: | ---: | --- |
| `normalized_diagnosis_text` | 16 letters | 18 | 17 | 16 | Generalizable normalization |
| `normalized_time_period` | 13 | 13 | 13 | 9 | Generalizable normalization |
| `projected_active_rate_seizure_type_to_diagnosis` | 7 | 5 | 4 | 4 | Scorer projection; audit/ablate |
| `dropped_unsupported_episode_frequency_anchor` | 1 | 4 | 4 | 2 | Generalizable guard, but test hard cases |
| `dropped_non_epilepsy_core` | 3 | 3 | 3 | 4 | Generalizable Diagnosis gate |
| `split_range_attribute` | 3 | 3 | 3 | 3 | Generalizable format normalization |
| `normalized_seizure_frequency_text` | 2 | 2 | 3 | 1 | Mixed anchor normalization; keep guarded |
| `projected_header_parent_epilepsy` | 2 | 2 | 2 | 2 | Scorer projection; audit/ablate |

One-letter projection families that should not be promoted without quarantine or
broader tests include:

- `projected_march_range_count` (`EA0002`)
- `projected_several_since_last_clinic` (`EA0004`)
- `projected_generic_yearly_rate_anchor` (`EA0005`)
- `projected_last_event_month_year_to_zero_since` (`EA0005`)
- `projected_every_n_to_m_periods_to_one_event_rate` (`EA0007`)
- `projected_sf_context_to_focal_diagnosis` (`EA0007`)
- `split_cluster_of_seizures_state` (`EA0009`)
- `split_convulsive_zero_state` (`EA0011`)
- `projected_typed_seizure_frequency_to_diagnosis` (`EA0011`)
- `split_generalised_epilepsy_syndrome` (`EA0005`)
- `split_syndrome_to_tonic_clonic_diagnosis` (`EA0005`)
- `split_secondary_gtc_to_tonic_clonic_diagnosis` (`EA0021`)
- `split_temporal_lobe_onset_to_focal_seizures` (`EA0018`)

These are not all wrong. The risk is that each currently fires on one dev25
letter, so the evidence is insufficient to distinguish a clinically useful
projection from a benchmark-letter patch.

## Recommended Next Action

Before Phase 1/2 promotion, run same-raw ablations for the quarantined families
and decide keep/cut from attribution evidence rather than headline tuning. Keep
broad normalizers only with a small family registry or warning taxonomy, then
run any frozen held-out Phase 1 scoring with headline and benchmark keys. Add a
positive warning hook for active recent-event preservation if it remains
prediction-bearing.
