# Gan 2026 RQ9 Abstention And Human-Review Predeclaration

This is a pre-run validation-development contract for abstention and human-review routing using the saved RQ10 residual-miss classes.

## Decision

Predeclare a selective-action policy over the 53 saved RQ10 residual Purist misses. The policy blocks prediction-bearing use for 34 rows through abstention or human review, and keeps 19 rows as true extraction failures for component debugging.

## Claim Boundary

Validation-development RQ9 predeclaration only. The policy defines abstention and human-review routing from saved RQ10 audit classes; it does not change scorer policy, gold labels, prompts, deterministic rules, projection policy, locked-test behavior, or benchmark-comparable claims.

## Routing Policy

| Review bucket | Action |
| --- | --- |
| `possible_gold_weakness` | `human_review_gold_reference` |
| `clinically_defensible_alternative` | `human_review_clinical_convention` |
| `benchmark_convention_dominated` | `human_review_benchmark_convention` |
| `underdetermined_note` | `abstain_or_route_unknown` |
| `true_extraction_failure` | `extraction_error_analysis` |

Priority order matters: possible gold/reference weakness and clinically defensible alternatives are routed before benchmark-convention and underdetermined-note classes, so RQ9 can separate manual review targets from ordinary extraction failures.

## Artifacts

- RQ10 answer: `docs/research/gan2026_rq10_gold_scorer_ambiguity_audit_answer_2026-06-04.md`
- RQ9 JSONL: `experiments/gan2026_rq9_abstention_review_predeclaration_2026-06-04.jsonl`
- RQ9 summary JSON: `experiments/gan2026_rq9_abstention_review_predeclaration_2026-06-04.json`
- RQ10 source audit: `experiments/gan2026_rq10_gold_scorer_ambiguity_audit_2026-06-04.jsonl`

## Metrics

| Metric | Value |
| --- | ---: |
| predeclared rows | 53 |
| prediction blocked rows | 34 |
| extraction error analysis rows | 19 |
| abstain or route unknown rows | 5 |
| human review clinical convention rows | 23 |
| human review benchmark convention rows | 3 |
| human review gold reference rows | 3 |
| exact evidence rate | 1.000 |
| rq10 hard row ambiguity rate | 0.641 |

## Review Buckets

| Bucket | Rows |
| --- | ---: |
| `benchmark_convention_dominated` | 3 |
| `clinically_defensible_alternative` | 23 |
| `possible_gold_weakness` | 3 |
| `true_extraction_failure` | 19 |
| `underdetermined_note` | 5 |

## RQ10 Primary Classes

| RQ10 class | Rows |
| --- | ---: |
| `benchmark_convention_dominated` | 11 |
| `true_extraction_failure` | 19 |
| `underdetermined_note` | 23 |

## Evaluation Contract

Use RQ9 as a selective-action evaluation: rows routed to review or abstention are success cases only when they block an unsafe final label without hiding true extraction failures. Promote no automatic label changes from this predeclaration.

Human-review packets omit gold labels, scorer categories, and W/C-style development accounting. Those fields remain only in `development_accounting` for post-routing analysis.
