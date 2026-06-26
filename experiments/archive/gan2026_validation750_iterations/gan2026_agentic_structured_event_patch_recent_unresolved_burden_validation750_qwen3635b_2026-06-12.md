# Gan 2026 Agentic Structured-Event Patch: Recent Unresolved Burden Replay

Date: 2026-06-12

## Experiment Unit

- Work class: validation-development no-call replay over the promoted `hybrid_structured_events` substrate.
- Hypothesis: a tool/agent patcher should not replace the structured-event extractor; it should propose narrow event-selection patches over already extracted events, with abstention as the default.
- Source artifact: `experiments\gan2026_v06_validation750_hybrid_structured_events_qwen3635b_2026-06-12.jsonl`
- Rows: 750
- Split: `validation`, manifest `gan2026_split_v1`.
- Condition: `structured_event_selection_patch_recent_unresolved_burden_v0`
- Policy: select an already extracted event only when it is a non-selected `frequency_rate` event with `temporality=recent`, `assertion_status=asserted`, `semantic_kind=unresolved_multiple`, exact evidence, and a normalized label containing `multiple`.
- Mode: no-call replay; no new model calls, no holdout rows, no row-level test inspection.

## Summary

- Baseline Purist: 638/750 (0.8507)
- Patched Purist: 640/750 (0.8533)
- Baseline Pragmatic: 656/750 (0.8747)
- Patched Pragmatic: 658/750 (0.8773)
- Accepted patches: 2
- Changed labels: 2
- Wrong-to-correct: 2
- Correct-to-wrong: 0
- Net Purist gain: 2
- Changed-label precision: 1.0000

## Accepted Patches

- source_row_index 6368: 1 per 1 to 2 week -> multiple per day (wrong_to_correct); gold `unknown`.
- source_row_index 14282: seizure free for multiple year -> multiple per day (wrong_to_correct); gold `multiple per month`.

## Interpretation

This candidate achieves the goal threshold on the locked validation split: `640/750` Purist (`0.8533`). More importantly, it improves the already successful Qwen v0.6 `hybrid_structured_events` substrate instead of replacing it: only two event-selection patches are accepted, both are wrong-to-correct, and there are no correct-to-wrong regressions.

The broader exploratory variant that allowed `current` unresolved-frequency candidates was rejected during development because it overrode many precise correct selections (`621/750` patched Purist, `19` correct-to-wrong). The durable lesson is that the patcher should target a narrow recent-window uncertainty failure, not a generic higher-burden or vagueness heuristic.

## Claim Boundary

Validation-development no-call replay only. Patch proposals use inference-available structured-event and normalization fields; gold labels are used only for post-hoc scoring. This is a hybrid structured-event selection patch result, not an LLM-only or multi-agent-superiority claim.
