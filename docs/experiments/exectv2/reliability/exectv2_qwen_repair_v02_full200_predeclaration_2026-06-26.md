# ExECTv2 Qwen Repair v02 Full-200 Aggregate Predeclaration

- Date: `2026-06-26`
- Status: completed aggregate-only run on `2026-06-26`
- Candidate id: `exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_full200`
- Dev140 source: `exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_dev140`
- Architecture core: `exectv2_2call_no_sf_adjudicator_model_swap`
- Primary surface: `clinical_headline`
- Split/scope: full-200 aggregate-only validation, if run later
- Row-inspection boundary: `aggregate_only_no_full200_or_holdout_row_level_inspection`

## Decision

Qwen repair v02 is eligible for a fresh same-core full-200 aggregate-only
predeclaration because the dev140 repaired assembly passed its operational gates:
`0` call failures, `0` parse/schema failures, structured evidence validity
`0.9964`, final-lane evidence `1.0000`, and clinical-headline F1 `0.8319`.

On 2026-06-26, the fresh same-core full-200 aggregate-only run was explicitly
authorized under this predeclaration.

This decision does not retroactively add Qwen to the already executed
GPT-4.1-mini plus DeepSeek full-200 comparison. It also does not authorize
row-level full-200 failure analysis.

## Frozen Contract

The future Qwen full-200 row must keep the same same-core component graph used by
the dev140 repair v02 readout:

| Component | Owner | Policy |
| --- | --- | --- |
| `structured_key_family_event_ledger` | Qwen model | same compact output-contract repair v02 profile |
| `diagnosis_decomposer` | Qwen model | same compact output-contract repair v02 profile |
| `sf_structured_direct_adapter` | deterministic | unchanged same-core adapter |
| `sf_state_projection` | deterministic | unchanged same-core projection |
| `sf_unknown_suppression` | deterministic | unchanged same-core suppression |
| `sf_union_arbitration` | deterministic | unchanged same-core union arbitration |
| `prescription_deterministic_repair` | deterministic | unchanged Prescription repair v03 |
| `finding_assembly` | deterministic assembly | unchanged lenses, views, and scorer |

No prompt, threshold, scorer, entity lens, SF projection, Prescription repair, or
semantic adapter change may be made based on full-200 aggregate results. Any
change starts a new dev140-only cycle and a fresh predeclaration.

## Allowed Outputs

A future run may report only aggregate outputs:

- overall and per-family `clinical_headline` precision, recall, F1, TP, FP, and FN
- diagnostic strict benchmark/CUI aggregate metrics
- call-failure and parse/schema-failure counts by live producer
- schema-validity and exact-evidence aggregate rates
- aggregate Qwen repair counts, including dropped unknown-family events and
  stripped non-scored rationales
- aggregate comparison against the already recorded GPT-4.1-mini and DeepSeek
  same-core full-200 rows

The report must not emit row identifiers tied to errors, note text, gold labels,
prediction text, evidence spans, rationales, or residual failure ledgers.

## Stop Rule

If the future Qwen full-200 row has any call failure, more than one blocking
parse/schema failure, exact evidence below `0.99` in any reported family, or
overall clinical-headline F1 below the dev140-repaired evidence threshold of
`0.8000`, keep the row diagnostic-only and do not tune Qwen from full-200 output.

If the row passes, it becomes same-core model-family evidence with explicit
operational and aggregate-only boundaries, not a strict benchmark or holdout
claim.
