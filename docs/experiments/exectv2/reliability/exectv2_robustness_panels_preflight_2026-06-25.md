# ExECTv2 Robustness Panels Preflight

- Generated: `2026-06-25`
- JSON: `experiments/exectv2_robustness_panels_preflight_20260625.json`
- Surface: rich-schema holistic assembly reliability scorecard
- Scorer: `headline_target clinical-recovery family cells`
- Split: `deterministic_dev_fixture_panel`
- Result type: `dev_fixture_preflight_not_validation`
- Model calls during build: `False`
- Row inspection policy: Synthetic/dev-fixture panel only. No full-200 or holdout row-level inspection, examples, residual ledgers, or note text are loaded.

This is an aggregate-only validation-ready panel preflight. It freezes the case taxonomy and proves the scorer reacts to targeted failures; it does not inspect full-200 or holdout row-level inspection surfaces.

## Coverage

| Requirement | Count |
| --- | ---: |
| `sf_current_vs_historical` | 1 |
| `sf_current_vs_future` | 1 |
| `prescription_current_vs_plan` | 1 |
| `investigations_result_state` | 1 |
| `diagnosis_assertion_hierarchy` | 2 |
| `evidence_paraphrase` | 1 |
| `evidence_deletion` | 1 |

- Minimum coverage met: `True`
- Ready for frozen candidate run: `True`
- Scorecard coverage can increase now: `False`
- Gate rationale: Panel preflight is ready, but scorecard robustness coverage can increase only after an aggregate-only frozen candidate run passes the predeclared robustness gate.

## Aggregate Arms

| Arm | Overall F1 | Schema validity | Evidence validity | Call failures | Parse failures |
| --- | ---: | ---: | ---: | ---: | ---: |
| Reference oracle | 1.0000 | 1.0000 | 1.0000 | 0 | 0 |
| Targeted failure control | 0.4444 | 1.0000 | 0.7778 | 0 | 0 |

## Family Deltas

| Arm | Family | F1 | P | R | TP | FP | FN | Companion metrics |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Reference oracle | Diagnosis | 1.0000 | 1.0000 | 1.0000 | 2 | 0 | 0 | assertion_f1=1.0000, negation_f1=1.0000 |
| Reference oracle | SeizureFrequency | 1.0000 | 1.0000 | 1.0000 | 3 | 0 | 0 | active_rate_fidelity_f1=1.0000, benchmark_with_cui_f1=1.0000 |
| Reference oracle | Prescription | 1.0000 | 1.0000 | 1.0000 | 2 | 0 | 0 | ordinary_complete_f1=1.0000, future_medication_f1=0.0000 |
| Reference oracle | Investigations | 1.0000 | 1.0000 | 1.0000 | 2 | 0 | 0 | performed_f1=1.0000, result_f1=1.0000 |
| Targeted failure control | Diagnosis | 0.5000 | 0.5000 | 0.5000 | 1 | 1 | 1 | assertion_f1=0.0000, negation_f1=0.0000 |
| Targeted failure control | SeizureFrequency | 0.3333 | 0.3333 | 0.3333 | 1 | 2 | 2 | active_rate_fidelity_f1=0.0000, benchmark_with_cui_f1=0.3333 |
| Targeted failure control | Prescription | 0.5000 | 0.5000 | 0.5000 | 1 | 1 | 1 | ordinary_complete_f1=0.5000, future_medication_f1=0.0000 |
| Targeted failure control | Investigations | 0.5000 | 0.5000 | 0.5000 | 1 | 1 | 1 | performed_f1=0.5000, result_f1=0.6667 |

## Case Catalog

| Case | Family | Perturbation | Failure mode |
| --- | --- | --- | --- |
| `sf_current_over_historical` | SeizureFrequency | `sf_current_vs_historical` | selects historical active rate instead of current state |
| `sf_current_over_future_plan` | SeizureFrequency | `sf_current_vs_future` | drops the current active-rate state because future review is mentioned |
| `rx_current_over_plan` | Prescription | `prescription_current_vs_plan` | extracts planned clobazam as a current regimen |
| `inv_pending_vs_result` | Investigations | `investigations_result_state` | treats pending MRI as performed with an unknown result |
| `dx_specific_over_generic` | Diagnosis | `diagnosis_assertion_hierarchy` | emits a generic or unsupported hierarchy diagnosis |
| `dx_negation_assertion` | Diagnosis | `diagnosis_assertion_hierarchy` | preserves concept identity but flips negation to affirmed |
| `evidence_paraphrase_sf` | SeizureFrequency | `evidence_paraphrase` | uses paraphrased non-verbatim evidence for a correct fact |
| `evidence_deletion_rx` | Prescription | `evidence_deletion` | deletes evidence while keeping the clinical fact |
