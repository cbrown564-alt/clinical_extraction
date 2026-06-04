# Gan 2026 Trigger-Context Release Rule Proposal

Validation-development proposed decision layer. It applies only the predeclared trigger-context release rule to the conservative staged decision layer. It does not change prompts, scorer policy, gold labels, locked-test behavior, verifier use, or benchmark-comparable claims.

## Summary

The rule releases 1 rows. The proposed decision layer has 717 prediction-bearing rows and 33 non-prediction rows.

## Metrics

| Metric | Value |
| --- | ---: |
| released rows | 1 |
| prediction bearing rows | 717 |
| non prediction rows | 33 |
| selective purist accuracy | 0.947 |
| selective pragmatic accuracy | 0.954 |

## Released Rows

| Row | Label | Evidence | Source ids |
| ---: | --- | --- | --- |
| 5977 | `multiple per 6 week` | several episodes over the past six weeks | `det:event_1, graph:sg-001` |

## Artifacts

- Release rows JSONL: `experiments/gan2026_staged_hybrid_trigger_context_release_rule_2026-06-04.jsonl`
- Proposed decision JSONL: `experiments/gan2026_staged_hybrid_trigger_context_release_proposed_decisions_2026-06-04.jsonl`
- Summary JSON: `experiments/gan2026_staged_hybrid_trigger_context_release_rule_2026-06-04.json`
