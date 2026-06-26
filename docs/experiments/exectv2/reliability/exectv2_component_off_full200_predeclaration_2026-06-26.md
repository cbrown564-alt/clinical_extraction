# ExECTv2 Component-Off Full-200 Aggregate Predeclaration

- Date: `2026-06-26`
- Status: completed 2026-06-26; aggregate-only replay executed once under this protocol
- Code hash at drafting: `84d6d18`
- Code hash at execution: see `experiments/exectv2_component_off_replay_full200_20260626.md`
- Final report: `experiments/exectv2_component_off_replay_full200_20260626.{json,jsonl,md}`
- Dev140 decision source: `experiments/exectv2_component_off_replay_dev140_20260626.{json,jsonl,md}`
- Planning source: `docs/research/exectv2_component_off_reliability_ablation_plan_2026-06-26.md`
- Primary surface: `clinical_headline`
- Split/scope: full-200 aggregate-only component-impact replay
- Row-inspection boundary: `aggregate_only_no_full200_or_holdout_row_level_inspection`

## Decision

The dev140 one-component-off readout warrants a separate full-200
aggregate-only predeclaration for the material component-impact layers:
`standard_dictionary`, `residual_semantic_lens`, and `headline_projection`.

It does not warrant a full-200 escalation for `evidence_validation` on this
artifact family. Evidence validation was structurally inert across the four
dev140 single-lane holistic replays, with `0.0000` overall and family deltas in
every row. That result may be reported as a grounding-guard check, not as proof
that evidence validation is globally unnecessary.

The material dev140 component deltas supporting escalation are:

| Component | Type | Prediction-bearing status | Dev140 overall delta range | Main family signal |
| --- | --- | --- | ---: | --- |
| `standard_dictionary` | `dictionary` | `conditional` | `+0.0389` to `+0.1120` | Diagnosis up to `+0.1397`; SeizureFrequency up to `+0.1728` |
| `residual_semantic_lens` | `semantic_lens` | `yes` | `+0.0175` to `+0.1041` | Investigations up to `+0.1722`; SeizureFrequency up to `+0.1505` |
| `headline_projection` | `deterministic_projection` | `no` | `+0.0283` to `+0.0446` | SeizureFrequency up to `+0.2031` |

These are component-impact signals only. They must remain separate from the
Reliability Scorecard and from strict benchmark/CUI claims.

## Frozen Component Set

The full-200 replay may evaluate only these component removals:

| Component id | Baseline surface | Component-off surface | Claim if reported |
| --- | --- | --- | --- |
| `standard_dictionary` | `dictionary_normalized` | `evidence_valid` | Conditional dictionary/benchmark-format recovery on the declared scorer and split. |
| `residual_semantic_lens` | `residual_semantic_added` | `dictionary_normalized` | Prediction-bearing semantic add/drop/replace contribution on the declared scorer and split. |
| `headline_projection` | `headline_projection` | `residual_semantic_added` | Deterministic projection/format contribution, separated from semantic fact changes. |

`evidence_validation` is excluded from this full-200 component-off protocol.
Future evidence-validation work should use an evidence-validity or grounding
stress plan, not a broad full-200 clinical-score replay justified by these
dev140 rows.

## Source-Artifact Eligibility

Execution is allowed only as replay over already available full-200 source
artifacts that expose the required component surfaces or can derive them without
new model calls and without opening row-level full-200 failures.

Eligible full-200 source families must pass an aggregate-safe preflight before
metrics are read:

- split is `full200`;
- scorer view is `clinical_headline`;
- row count is `200`;
- source artifacts contain or deterministically replay the baseline and
  component-off surfaces for each selected component;
- model calls are disabled;
- prompt, parser, scorer, threshold, entity-lens, deterministic-rule, and
  model-choice changes are disabled;
- aggregate validity slots are available for schema validity, evidence validity,
  call failures, parse failures, and missing-output counts.

If the required surfaces are missing for a candidate family, stop and report a
preflight-null result for that family. Do not create substitute full-200 model
outputs, inspect row-level failures, or tune replay code to recover a desired
component delta.

## Execution Rule

Run the full-200 component-off replay once after source-artifact eligibility is
confirmed. Infrastructure failures before metrics are read may be retried only
after recording the failure mode in the report. Once aggregate metrics are read,
any code, scorer, threshold, rule, prompt, parser, source-artifact, or model
change starts a new dev140-only development cycle and a fresh predeclaration.

## Allowed Aggregate Outputs

The final report may include:

- overall and per-family `clinical_headline` precision, recall, F1, TP, FP, and
  FN for baseline and component-off surfaces;
- overall and per-family contribution deltas;
- aggregate schema-validity, evidence-validity, call-failure, parse-failure,
  abstention, and missing-output counts;
- aggregate deterministic-action counts for the component surfaces when already
  available;
- explicit comparison to the dev140 component-off direction, labelled as
  split-specific component-impact evidence;
- stop-rule and preflight status for each source family.

The report must not include:

- full-200 row-level failure tables;
- row identifiers tied to errors;
- note text, gold labels, prediction text, evidence spans, rationales, or
  residual failure ledgers;
- prompt, parser, threshold, scorer, deterministic-rule, source-artifact, or
  model-choice tuning after seeing full-200 metrics;
- Reliability Scorecard promotion language.

## Stop Rule

If any selected component has a negative or null full-200 delta, report it as
valid component-impact evidence and stop. Do not tune from the aggregate result.

If a component has a material positive full-200 delta, the allowed claim remains
limited to the declared full-200 `clinical_headline` scorer, source-artifact
family, and aggregate-only inspection boundary. It is not a holdout result, not
a strict benchmark win, and not evidence that the component is globally required.

## Reporting Contract

The final report must include:

- this predeclaration path;
- source-artifact paths and preflight outcome;
- code hash and worktree state at execution;
- selected component ids, types, portability categories, and
  prediction-bearing status;
- row-inspection boundary statement;
- stop-rule outcome;
- aggregate metric table and validity/operational telemetry;
- explicit statement that the report is Component Impact evidence, not
  Reliability Scorecard evidence.
