# Gan 2026 Agentic Structured-Event Consensus: Unanimous Exact-Label Replay

Date: 2026-06-13

## Experiment Unit

- Work class: validation-development no-call replay over the promoted `hybrid_structured_events` substrate.
- Hypothesis: tools and multiple agents should improve the already-strong structured-event/rules stack by acting as a calibrated selector, not by replacing it.
- Tool-backed floor: deterministic top candidate from `experiments\gan2026_hybrid_rules_candidates_llm_adjudicator_validation750_gpt41mini_v02_cluster_diary_candidate_recall_live_2026-06-02.jsonl`.
- Agent votes: saved structured-event final labels from GPT-4.1-mini, Qwen3-235B-A22B with the recent unresolved-burden patch, and DeepSeek.
- Rows: 750
- Split: `validation`, manifest `gan2026_split_v1`.
- Condition: `rules_tool_plus_structured_event_unanimous_exact_label_v0`
- Policy: keep the deterministic tool baseline unless all three structured-event agents emit the same non-null exact final label and that label differs from the baseline.
- Mode: no-call replay; no new model calls, no holdout rows, no row-level test inspection.

## Comprehensive Error Analysis Basis

- Deterministic top baseline: 697/750 Purist.
- GPT structured events alone: 661/750 Purist.
- Qwen structured events plus narrow recent unresolved-burden patch: 640/750 Purist.
- DeepSeek structured events alone: 622/750 Purist.
- Oracle if choosing between deterministic top and GPT structured events: 737/750 Purist.
- Oracle if choosing among deterministic top plus the three structured-event agents: 740/750 Purist.
- Oracle with additional direct/canonical saved outputs included: 743/750 Purist.
- Design inference: the missing ingredient is selective adjudication. Broad replacement regresses too many correct deterministic rows, but unanimous structured-event agreement contains enough signal to recover validation errors.

## Summary

- Baseline Purist: 697/750 (0.9293)
- Consensus Purist: 708/750 (0.9440)
- Baseline Pragmatic: 704/750 (0.9387)
- Consensus Pragmatic: 713/750 (0.9507)
- Changed labels: 122
- Wrong-to-correct: 27
- Correct-to-wrong: 16
- Correct-to-correct changes: 681
- Wrong-to-wrong changes: 26
- Net Purist gain: 11
- Changed-label precision: 0.2213
- Decision reasons: `{'consensus_matches_baseline': 342, 'no_unanimous_exact_label': 286, 'accepted_unanimous_exact_label': 122}`

## Interpretation

This is the first multi-agent structured-event selector in this branch to clear 700/750 on the locked validation split: 708/750 Purist. The result supports the reset principle: retain the successful deterministic and structured-event machinery, then use agents as a high-agreement adjudication layer over already-rendered labels.

The selector is deliberately simple and inspectable. It rejects two-agent majorities because the error analysis showed those policies were net-negative; exact unanimity sacrifices recall for enough precision to beat the deterministic floor by 11 rows. The main remaining weakness is regression cost: 16 correct deterministic rows are lost, so the next iteration should target hard-slice gating or regression filters rather than adding more broad agent calls.

## Claim Boundary

Validation-development no-call replay only. The replay uses saved deterministic-tool and structured-event artifacts; gold labels are used only for post-hoc scoring and error analysis. This supports a future live tool-calling/multi-agent pipeline design, but it is not a holdout claim and not evidence that unrestricted multi-agent prompting is superior under matched live-call budgets.
