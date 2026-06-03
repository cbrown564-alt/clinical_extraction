# Component Evidence Attribution Architecture

Last updated: 2026-06-03

## Purpose

Every candidate pipeline should be able to answer three questions without a
custom one-off analysis:

1. For each clinical subproblem, which component solved it, under what evidence
   constraints, with what regression risk, and on which distribution?
2. Which clinically meaningful decisions can the LLM make more robustly than
   deterministic rules under exact-evidence and regression constraints?
3. When the LLM changes the deterministic answer, how often is that change
   correct?

This document defines the architecture contract for those answers. It does not
replace candidate-specific experiment reports. It defines the fields, gates,
and comparison surfaces every promotion report must expose.

## Audit Object

Each candidate run should produce or be replayable into a component evidence
matrix with one row per `source_row_index`, clinical subproblem, component
decision, and score layer.

Required row fields:

| Field | Meaning |
| --- | --- |
| `task` | Clinical task, currently `seizure_frequency`. |
| `dataset` | Dataset or benchmark family, currently `gan2026`. |
| `split_manifest` | Locked split manifest, for example `gan2026_split_v1`. |
| `distribution` | `train`, `validation25`, `validation250`, `validation750`, hard slice, synthetic stress panel, or locked holdout audit. |
| `pipeline_family` | `rules_only`, `llm_only`, or `hybrid`. |
| `candidate_name` | Runnable or replayable candidate identifier. |
| `score_layer` | Named prediction layer, such as raw model, deterministic adapter, projection, safety floor, or final policy. |
| `clinical_subproblem` | The decision being audited. |
| `component_owner` | Component that made the prediction-bearing decision. |
| `evidence_constraint` | Exact-evidence requirement applied to this row. |
| `evidence_status` | `exact`, `source_near`, `invalid`, `missing`, or `not_applicable`. |
| `baseline_label` | Comparator label, usually deterministic safety floor or rules-only. |
| `candidate_label` | Candidate layer label. |
| `gold_label` | Normalized gold label under the active scoring policy. |
| `baseline_purist_correct` | Whether the comparator is Purist-correct. |
| `candidate_purist_correct` | Whether the candidate layer is Purist-correct. |
| `changed_from_baseline` | Whether the candidate label changed the comparator label. |
| `wrong_to_correct` | Baseline wrong and candidate correct. |
| `correct_to_wrong` | Baseline correct and candidate wrong. |
| `regression_family` | `deterministic_correct_regression`, `evidence_regression`, `schema_regression`, `projection_regression`, or `none`. |
| `first_failure_owner` | Earliest component that made the final row unrecoverable, when wrong. |
| `hidden_family` | Clinically meaningful slice tags such as seizure-free boundary or current-versus-historical. |

## Clinical Subproblem Taxonomy

Use the same subproblem names across reports, tests, and run artifacts:

| Subproblem | Question | Typical owners |
| --- | --- | --- |
| `candidate_generation` | Did the system expose the gold-relevant clinical state as a candidate? | deterministic rules, LLM event extractor |
| `evidence_selection` | Did it select evidence that is exact or source-near enough to support the answer? | LLM selector, deterministic span validator |
| `temporal_selection` | Did it choose current rather than historical or future/planned frequency? | LLM reasoner, deterministic temporal rules, graph projection |
| `seizure_free_boundary` | Did it distinguish seizure-free duration, unknown, and residual frequency correctly? | LLM reasoner, deterministic seizure-free rules, projection |
| `rate_denominator` | Did it expose count, window, denominator, and unit correctly? | LLM operand extractor, deterministic rate parser |
| `cluster_or_diary_aggregation` | Did it aggregate cluster or diary language without overfitting Gan templates? | deterministic rules, LLM reasoner |
| `competing_event_selection` | Did it choose the relevant seizure type or event family? | LLM clinical selector, deterministic epilepsy filters |
| `uncertainty_boundary` | Did it distinguish no-reference, possible, unknown, and asserted frequency? | LLM reasoner, deterministic uncertainty rules |
| `adapter_rendering` | Did it render an already selected fact into Gan-compatible syntax? | deterministic adapter |
| `benchmark_formatting` | Did it apply scorer-facing convention without changing clinical interpretation? | deterministic benchmark-format rule |

When a new clinically meaningful family appears, add it here before using it as
a promotion claim.

## Component Ownership Contract

Classify ownership by the decision being made, not by module location.

- `deterministic_rule`: deterministic code selected or changed the clinical
  fact, temporal state, event, or benchmark label.
- `llm_clinical_selection`: the model selected the prediction-bearing clinical
  fact and evidence.
- `deterministic_adapter`: deterministic code rendered or computed from an
  already selected fact without changing fact identity.
- `graph_projection`: deterministic graph or state projection selected among
  nodes or arbitration outputs.
- `safety_floor`: deterministic fallback preserved a comparator-correct answer
  or blocked an unsafe model change.
- `schema_repair`: format/schema repair that does not change semantic kind,
  selected fact, selected evidence, temporal state, or scorer category.
- `benchmark_format`: scoring-surface convention only.

If deterministic code selects among competing facts after an LLM call, the row
is hybrid for that subproblem even when the candidate as a whole is described
as LLM-heavy elsewhere.

## Evidence Gates

Promotion reports must state the strongest evidence gate satisfied:

| Gate | Requirement | Allowed claim |
| --- | --- | --- |
| `exact_selected_evidence` | Selected evidence is an exact source substring and source id is valid. | Component decision is source-grounded. |
| `source_near_selected_evidence` | Evidence is traceably source-near but not exact. | Diagnostic only unless predeclared. |
| `operand_trace_exact` | Adapter operands are traceable to exact selected evidence. | Deterministic adapter may be credited as mechanical. |
| `same_raw_output_replay` | Candidate and comparator use the same raw model outputs. | Post-processing attribution is clean. |
| `no_deterministic_correct_regression` | No row that deterministic baseline got right becomes wrong. | Safety-floor or change policy may be considered. |
| `changed_row_exact_evidence` | Every changed row has exact evidence and valid source id. | LLM-change precision can be interpreted. |

Rows failing the relevant gate can still be useful for debugging, but they
cannot support a robust LLM-superiority or promotion claim.

## Distribution Ladder

Name the distribution in every claim.

| Distribution | Purpose | Claim strength |
| --- | --- | --- |
| `train` | Optimizer-only or fixture development. | No generalization claim. |
| `validation25` | Smoke for schema, evidence, and catastrophic regressions. | Engineering signal only. |
| `validation250` | Development decision gate. | Candidate revise/reject/promote-to-broader-validation. |
| `validation750` | Rare broad development replay. | Strong validation result if predeclared and no-call when applicable. |
| `validation_hard_slice` | Targeted component stress under known saturated aggregates. | Strongest development evidence for component behavior. |
| `synthetic_stress_panel` | Controlled robustness check. | Mechanism evidence, not benchmark performance. |
| `locked_holdout_audit` | Frozen final audit only. | Holdout claim only if the pre-run plan was followed. |

Near-ceiling validation aggregates are not enough. Once validation is saturated,
candidate promotion should prefer hard-slice evidence, same-raw-output replay,
changed-row precision, and frozen-test audit discipline.

## Required Summaries

Every candidate promotion or architecture comparison should include:

- Component evidence matrix grouped by clinical subproblem and component owner.
- Score-layer ladder: raw model, deterministic adapter, projection or sidecar,
  safety floor, and final policy when those layers exist.
- LLM delta table against deterministic comparator:
  `changed`, `wrong_to_correct`, `correct_to_wrong`, changed-label precision,
  changed-row exact-evidence count, and deterministic-correct regressions.
- Failure ownership table: first-failure owner by distribution and hidden
  family.
- Evidence validity table: exact/source-near/missing/invalid by score layer and
  changed-row subset.
- Claim-language block naming split, model, replay mode, scorer policy, repair
  policy, and whether the result is `rules_only`, `llm_only`, `hybrid`, or
  diagnostic.

## Promotion Gate

A candidate may be promoted to the next surface only if the report answers all
three project questions for the active distribution:

1. Which subproblems improved, by component owner, under the declared evidence
   gate?
2. Which LLM-owned decisions beat the deterministic comparator without relying
   on deterministic semantic replacement?
3. Among changed deterministic answers, how many were correct changes, how many
   were regressions, and were all changed rows evidence-valid?

If any answer is unknown, the next action is instrumentation, replay, or a
targeted hard-slice diagnostic, not broader validation or holdout execution.
