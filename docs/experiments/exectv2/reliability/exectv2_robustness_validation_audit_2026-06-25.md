# ExECTv2 Robustness Validation Audit

Date: 2026-06-25

Status: aggregate-only robustness validation and stop-rule readout.

## Preflight

- Surface: rich-schema holistic assembly reliability scorecard
- Scorer: `headline_target clinical-recovery family cells`
- Split: `full-200 aggregate-only validation requested`
- Code hash: `9850e80+dirty`
- Row-inspection boundary: Aggregate hard-slice metrics and artifact inventory only; no row identifiers, note text, gold labels, predictions, evidence spans, rationales, or selected failure examples are emitted.

## Frozen Robustness Candidate

- Candidate: `exectv2_holistic_finding_assembly_v08_full200_currentcode_gpt41mini`
- Taxonomy source: `docs/experiments/exectv2/reliability/exectv2_robustness_panels_preflight_2026-06-25.md`
- Preflight split: `deterministic_dev_fixture_panel`
- Preflight minimum coverage met: `True`
- Full-200 tagging policy: Frozen regex/provenance feature tags are computed internally from saved predicted/gold mention metadata and emitted only as aggregate counts.

### Preflight Taxonomy Coverage

| Perturbation family | Fixture count |
| --- | ---: |
| `sf_current_vs_historical` | 1 |
| `sf_current_vs_future` | 1 |
| `prescription_current_vs_plan` | 1 |
| `investigations_result_state` | 1 |
| `diagnosis_assertion_hierarchy` | 2 |
| `evidence_paraphrase` | 1 |
| `evidence_deletion` | 1 |

## Validation Artifact Inventory

| Artifact | Rows | Surface | Eligibility | Reason |
| --- | ---: | --- | --- | --- |
| `experiments/exectv2_holistic_finding_assembly_v08_full200_currentcode_gpt41mini_20260624.jsonl` | 200 | current-code v08-shape rich-schema holistic assembly | eligible | Accepted for aggregate-only validation of the frozen robustness taxonomy on the current-code v08-shaped rich-schema holistic assembly surface. |

## Aggregate Validation Readout

- Artifact: `experiments/exectv2_holistic_finding_assembly_v08_full200_currentcode_gpt41mini_20260624.jsonl`
- Rows: 200
- Eligible family cells: 619
- Hard-slice family cells: 414
- Overall F1: 0.8503
- Hard-slice F1: 0.8336
- Non-hard-slice F1: 0.8909
- Hard-slice delta vs overall: -0.0167
- Schema validity: 1.0000
- Evidence validity: 1.0000
- Call failures: 0
- Parse/schema failures: 0

### Perturbation Family Counts

| Perturbation family | Full-200 cells | Primary family | F1 | Delta vs overall | Schema validity | Evidence validity |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| `sf_current_vs_historical` | 94 | SeizureFrequency | 0.7893 | -0.0610 | 1.0000 | 1.0000 |
| `sf_current_vs_future` | 5 | SeizureFrequency | 0.5882 | -0.2621 | 1.0000 | 1.0000 |
| `prescription_current_vs_plan` | 20 | Prescription | 0.7273 | -0.1230 | 1.0000 | 1.0000 |
| `investigations_result_state` | 110 | Investigations | 0.9213 | 0.0710 | 1.0000 | 1.0000 |
| `diagnosis_assertion_hierarchy` | 188 | Diagnosis | 0.8248 | -0.0255 | 1.0000 | 1.0000 |
| `evidence_paraphrase` | 0 | cross-family evidence stress | 0.0000 | -0.8503 | n/a | n/a |
| `evidence_deletion` | 0 | cross-family evidence stress | 0.0000 | -0.8503 | n/a | n/a |

### Per-Family Deltas

| Family | All cells | Overall F1 | Hard-slice cells | Hard-slice F1 | Delta vs family overall |
| --- | ---: | ---: | ---: | ---: | ---: |
| Diagnosis | 189 | 0.8238 | 188 | 0.8248 | 0.0010 |
| SeizureFrequency | 153 | 0.7992 | 96 | 0.7813 | -0.0179 |
| Prescription | 167 | 0.8926 | 20 | 0.7273 | -0.1653 |
| Investigations | 110 | 0.9213 | 110 | 0.9213 | 0.0000 |

## Stop-Rule Outcome

- Status: `completed_current_code_surface_validation`
- Validation run executed: `True`
- Promotion decision: `promoted`
- Reason: The frozen robustness taxonomy and accepted current-code full-200 artifact pass the aggregate reporting gates. Evidence paraphrase/deletion remain adversarial fixture stress evidence, not naturally observed full-200 hard-slice failures.

## Promotion Gates

| Gate | Outcome | Note |
| --- | --- | --- |
| Frozen panel run completed once | pass | Accepted current-code full-200 artifact was read once for aggregate metrics. |
| Minimum perturbation taxonomy covered | pass | Natural full-200 hard-slice counts cover SF, Prescription, Investigations, and Diagnosis; evidence paraphrase/deletion are covered by the frozen adversarial fixture preflight. |
| Overall and per-family score deltas reported | pass | Hard-slice cells reported: 414. |
| Schema and evidence validity reported | pass | Schema validity 1.0000; evidence validity 1.0000. |
| Aggregate-only row-inspection boundary preserved | pass | Report emits counts and scores only, with no row-level examples or identifiers. |

## Result

The frozen robustness taxonomy is promoted as aggregate full-200 hard-slice validation evidence for the current-code v08-shaped surface. Overall F1 is 0.8503; hard-slice F1 is 0.8336 across 414 eligible family cells. The claim does not convert adversarial evidence paraphrase/deletion fixtures into naturally observed full-200 failures.

Next action: Refresh the reliability scorecard to mark robustness as aggregate full-200 hard-slice validation evidence while keeping adversarial evidence-perturbation claims tied to the frozen preflight panel.
