# Gan 2026 Structured-Event Consensus: Available Two-Agent Test450 Audit

Date: 2026-06-13

## Experiment Unit

- Work class: frozen `test450` saved-output generalization audit requested after validation consensus reached `708/750` Purist.
- Candidate under audit: deterministic tool floor plus exact-label unanimity over structured-event agent outputs.
- Exact validation policy status: not fully reproducible on saved `test450` artifacts. The validation replay used GPT, Qwen v0.6 with the recent unresolved-burden patch, and DeepSeek v0.6. The repository currently has `test450` structured-event artifacts for GPT v0.5 and Qwen v0.5 only; no DeepSeek `test450` structured-event artifact is available on disk.
- Constrained audit policy: keep deterministic top unless the available GPT and patched-Qwen structured-event outputs emit the same non-null exact final label and that label differs from deterministic top.
- Data surface: `test`, manifest `gan2026_split_v1`, 450 rows.
- Inspection policy: aggregate metrics only; no test-row failure inspection, examples, or tuning.

## Source Artifacts

- Deterministic tool floor: `experiments\gan2026_hybrid_rules_candidates_llm_adjudicator_test450_gpt41mini_v02_cluster_diary_candidate_recall_live_2026-06-02.jsonl`
- GPT structured events: `experiments\gan2026_test450_phase4_frozen_audit_hybrid_structured_events_gpt41mini_2026-06-09.jsonl`
- Qwen structured events: `experiments\gan2026_hybrid_structured_events_test_qwen36_35b_max5000_live_2026-06-04.jsonl`
- Qwen patch replay: `experiments\gan2026_agentic_structured_event_patch_recent_unresolved_burden_test450_qwen3635b_2026-06-13.jsonl`
- DeepSeek structured events: not available for `test450` on disk.

## Qwen Patch Aggregate

- Baseline Qwen Purist: 337/450 (0.7489)
- Patched Qwen Purist: 337/450 (0.7489)
- Baseline Qwen Pragmatic: 356/450 (0.7911)
- Patched Qwen Pragmatic: 356/450 (0.7911)
- Accepted patches: 0
- Wrong-to-correct: 0
- Correct-to-wrong: 0
- Net Purist gain: 0

## Consensus Summary

- Deterministic floor Purist: 343/450 (0.7622)
- Constrained consensus Purist: 365/450 (0.8111)
- Deterministic floor Pragmatic: 354/450 (0.7867)
- Constrained consensus Pragmatic: 375/450 (0.8333)
- Changed labels: 114
- Wrong-to-correct: 45
- Correct-to-wrong: 23
- Correct-to-correct changes: 320
- Wrong-to-wrong changes: 62
- Net Purist gain: 22
- Changed-label precision: 0.3947
- Decision reasons: `{'consensus_matches_baseline': 182, 'accepted_unanimous_exact_label': 114, 'no_unanimous_exact_label': 154}`

## Interpretation

This constrained holdout audit supports the concern that the validation result does not transfer cleanly. The deterministic floor itself drops from `697/750` validation Purist (`0.9293`) to 343/450 test Purist (0.7622), consistent with the earlier pattern that deterministic-heavy surfaces were validation-overfit.

The available two-agent consensus does improve that weak test floor by 22 net Purist rows, but it lands at only 365/450 (0.8111), far below the validation consensus rate of `0.9440`. Its changed-label precision is 0.3947, with 23 holdout regressions. So the right conclusion is not that the 708 validation result is a robust final system; it is a validation-cycle selector signal that needs a new validation-side generalization design before any stronger claim.

## Claim Boundary

This is a final-holdout aggregate saved-output audit of the closest available constrained variant, not the exact three-agent validation policy. Gold labels are used only for aggregate scoring. No test row-level failures were inspected for tuning, and no follow-on changes should be made from this artifact without starting a new validation-only development cycle.
