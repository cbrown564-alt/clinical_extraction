# Deterministic Projection Rule Taxonomy

Date: 2026-06-24

This taxonomy keeps deterministic post-model behavior attributable in ExECTv2
and Gan 2026 reports. Rules are classified by both portability and score-line
ownership before they affect a reported score.

## Portability Categories

- `general`: spelling, dose units, frequency abbreviation rendering, dates,
  evidence checks, JSON/schema compatibility, and other format operations that
  are not specific to epilepsy.
- `clinical_epilepsy`: epilepsy-note conventions, rescue/PRN medication wording,
  anti-seizure-medication context, seizure terminology, and current-regimen
  wording intended to transfer beyond one benchmark.
- `seizure_frequency`: seizure-rate/state operations such as active-rate,
  seizure-free, unknown, cluster, and change-state rendering.
- `gan2026_specific`: synthetic-letter or Gan-label quirks.
- `benchmark_format`: target-output conventions such as CUI attachment,
  phrase-scope rendering, and accepted benchmark label spelling.

## Score Lines

- `llm_only_meaning_preserving_projection`: the model selected the scored
  clinical fact; deterministic code only renders benchmark convention or
  canonical format without changing medication identity, current status, dose,
  frequency, assertion, state, or fact inventory.
- `hybrid_rescue`: deterministic code would add a missed fact or complete a
  clinically meaningful omitted field. This may be useful, but it is not an
  LLM-only extraction score.
- `verifier_filtered`: deterministic code would reject, drop, or de-duplicate a
  model-emitted target fact. This may improve a final system, but the dropped
  model output remains an LLM-only false positive.

## Prescription Phase 5 Rules

| Rule | Score line | Portability | LLM-only allowed |
| --- | --- | --- | --- |
| `prescription_drugname_cui_projection` | `llm_only_meaning_preserving_projection` | `benchmark_format` | yes |
| `prescription_brand_generic_equivalence` | `llm_only_meaning_preserving_projection` | `benchmark_format` | yes |
| `prescription_frequency_abbreviation_rendering` | `llm_only_meaning_preserving_projection` | `general` | yes |
| `prescription_dose_unit_normalization` | `llm_only_meaning_preserving_projection` | `general` | yes |
| `prescription_prn_frequency_rendering` | `llm_only_meaning_preserving_projection` | `clinical_epilepsy` | yes, only when PRN/rescue is model-selected/source-stated |
| `prescription_missing_medication_rescue` | `hybrid_rescue` | `clinical_epilepsy` | no |
| `prescription_missing_dose_or_frequency_completion` | `hybrid_rescue` | `clinical_epilepsy` | no |
| `prescription_duplicate_regimen_collapse` | `verifier_filtered` | `benchmark_format` | no |
| `prescription_unsupported_medication_rejection` | `verifier_filtered` | `clinical_epilepsy` | no |

The Phase 5 pilot applies only the rules compatible with LLM-only scoring. LLM-with-rules rescue and
verifier-filtered rules are counted as separated boundary candidates and are not
blended into the LLM-only score line.
