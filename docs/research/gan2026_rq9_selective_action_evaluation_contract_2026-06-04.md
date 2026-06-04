# Gan 2026 RQ9 Selective-Action Evaluation Contract

This is a validation-development follow-up contract derived from the human Gold
Audit abstention-policy report. It defines how to score a future selective-action
router before any new prediction-bearing surface is evaluated.

It does not change scorer policy, gold labels, deterministic rules, prompts,
projection policy, locked-test behavior, or benchmark-comparable claims.

## Decision

Evaluate RQ9 as a selective-action problem, not as final-label accuracy alone.
Every eligible row must receive exactly one action:

- `predict`
- `abstain`
- `human_review`
- `extraction_error_analysis`

Rows with `predict` must carry one Gan-compatible final label. Rows with
`abstain` or `human_review` must carry one predeclared reason and a row packet
that makes the evidence, uncertainty, and projection rationale auditable.

## Evidence Base

- Human Gold Audit report:
  `docs/research/gan2026_human_gold_audit_abstention_policy_report_2026-06-04.md`
- Human audit decisions: `experiments/gold_audit_decisions.jsonl`
- Validation ambiguity worklist:
  `experiments/gan2026_validation750_gold_reference_ambiguity_review_2026-06-04.csv`
- Existing RQ9 residual-miss predeclaration:
  `docs/research/gan2026_rq9_abstention_review_predeclaration_2026-06-04.md`
- Unknown/drop-attack boundary policy:
  `docs/research/gan2026_rq9_unknown_drop_attack_boundary_policy_2026-06-04.md`
- RQ10 gold/scorer ambiguity answer:
  `docs/research/gan2026_rq10_gold_scorer_ambiguity_audit_answer_2026-06-04.md`

The human-audit input contains 140 latest unique reviewed validation rows:
94 human-`correct`, 37 human-`ambiguous`, and 9 human-`wrong`. The audit is a
development instrument for policy design, not a replacement gold standard.

## Eligible Surface

The first follow-up evaluation should use validation rows only under
`gan2026_split_v1`. It may score either:

1. a full validation750 selective-action output, or
2. a predeclared validation slice with fixed membership and a written inclusion
   rule before scoring.

The scored artifact must record the denominator explicitly:

- `eligible_rows`: all rows in the declared evaluation surface
- `covered_rows`: rows with action `predict`
- `abstained_rows`: rows with action `abstain`
- `human_review_rows`: rows with action `human_review`
- `extraction_error_analysis_rows`: rows with action `extraction_error_analysis`

Locked-test rows are excluded unless a separate frozen test predeclaration is
written before any row-level inspection.

## Allowed Reasons

Use one primary reason per non-prediction row, with optional secondary reasons
kept only for error analysis:

| Reason | Default action |
| --- | --- |
| `unknown_frequency_unquantified` | `predict` `unknown` when stable; otherwise `abstain` under the boundary policy |
| `event_type_uncertain` | `human_review` |
| `trigger_conditioned_frequency` | `abstain` |
| `missing_denominator_anchor` | `abstain` |
| `last_event_boundary` | `human_review` |
| `drop_attack_boundary` | `human_review` |
| `cluster_projection_boundary` | `human_review` |
| `competing_semiology_boundary` | `human_review` |
| `benchmark_convention_boundary` | `human_review` |
| `possible_gold_reference_issue` | `human_review` |
| `true_extraction_failure` | `extraction_error_analysis` |

The explicit `unknown` and drop-attack boundary policy is frozen in
`docs/research/gan2026_rq9_unknown_drop_attack_boundary_policy_2026-06-04.md`.
Apply that policy before scoring a router, because the human audit shows these
are the highest-risk subjective families.

## Prediction Packet Contract

Each `predict` row must include:

- `source_row_index`, split, split manifest, and router version
- final label and normalized label kind
- selected evidence as exact source substring whenever available
- selected candidate/source ids when available
- projection rationale
- reason `plain_predictable_frequency`, `plain_predictable_seizure_free`,
  `plain_no_reference`, or `unknown_frequency_unquantified`

## Abstention And Review Packet Contract

Each `abstain` or `human_review` row must include:

- `source_row_index`, split, split manifest, and router version
- action and primary reason
- exact selected evidence or a clear `no_exact_evidence` marker
- candidate events and rejected competing evidence when available
- uncertainty fields used by the router
- projection or non-projection rationale
- review packet with no gold label, gold reference, or W/C development fields

Gold labels and human-audit classes may be used only in post-routing development
accounting, never as router inputs.

## Required Metrics

Report these metrics for every scored surface:

| Metric | Definition |
| --- | --- |
| Coverage | `covered_rows / eligible_rows` |
| Abstention rate | `abstained_rows / eligible_rows` |
| Human-review rate | `human_review_rows / eligible_rows` |
| Prediction-bearing rate | `(covered_rows + extraction_error_analysis_rows) / eligible_rows` when extraction-error rows still emit labels for debugging |
| Selective accuracy | exact-label accuracy among `predict` rows only |
| Abstention precision | human-noncorrect or policy-nonpredictable rows among `abstain` rows |
| Review precision | human-noncorrect or policy-nonpredictable rows among `human_review` rows |
| Over-abstention rate | human-`correct` rows among `abstain` rows |
| Over-review rate | human-`correct` rows among `human_review` rows |
| Rescue value | unsafe predictions blocked by `abstain` or `human_review` |
| Hidden-error rate | true extraction failures routed away from `extraction_error_analysis` |
| Class-specific coverage | coverage by gold label kind and ambiguity family |

When human-audit labels are unavailable for a row, report the metric denominator
as the reviewed subset and do not impute human class.

## Minimum Slices

At minimum, report the required metrics by:

- gold label kind: `frequency`, `seizure_free`, `unknown`,
  `unresolved_multiple`, and `no_reference`
- human-audit class when available: `correct`, `ambiguous`, and `wrong`
- primary router reason
- high-yield family: unknown boundary, drop attack/event-type uncertainty,
  trigger-only evidence, last-event boundary, cluster convention, competing
  semiologies, and missing denominator/window

## Success Criteria

A selective-action router is useful only if all of the following hold on its
declared validation surface:

- selective accuracy is reported together with coverage
- abstention and human-review rates are bounded and visible
- over-abstention and over-review are measured against reviewed rows
- true extraction failures are not hidden by review routing
- review packets are gold-blinded and evidence-bearing
- no deterministic-correct regression is promoted without adjudication

No single aggregate F1, accuracy, or selective accuracy number can satisfy this
contract by itself.

## Anti-Cheating Rules

An abstain-on-all-hard-questions policy fails this contract even if selective
accuracy is high. A valid router must preserve enough prediction coverage to be
meaningful and must explain why each non-prediction row is non-predictable under
the predeclared policy.

The router must not use gold labels, benchmark references, human-audit classes,
or W/C accounting as inputs. Those fields may appear only in offline development
accounting after the action has already been produced.

## Promotion Boundary

This contract can support a validation-development RQ9 answer about whether the
system can separate predictable rows, subjective/underdetermined rows, and true
extraction failures. It does not authorize scorer changes, automatic gold
rewrites, final pipeline promotion, or locked-test claims.
