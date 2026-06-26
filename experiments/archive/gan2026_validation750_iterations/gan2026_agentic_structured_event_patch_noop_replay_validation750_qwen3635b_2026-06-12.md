# Gan 2026 Agentic Structured-Event Patch No-Op Replay

Date: 2026-06-12

## Experiment Unit

- Work class: validation-only no-call contract replay for the structured-event selection patch surface.
- Source artifact: `experiments\gan2026_v06_validation750_hybrid_structured_events_qwen3635b_2026-06-12.jsonl`
- Rows: 750
- Split: `validation`, manifest `gan2026_split_v1`.
- Condition: `structured_event_selection_patch_v0_no_proposals`
- Mode: no-call replay over saved `hybrid_structured_events` rows.
- Patch proposals: none; every row falls back to the baseline structured-event selection.

## Summary

- Baseline Purist: 638/750 (0.8507)
- Patched Purist: 638/750 (0.8507)
- Baseline Pragmatic: 656/750 (0.8747)
- Patched Pragmatic: 656/750 (0.8747)
- Accepted patches: 0
- Changed labels: 0
- Wrong-to-correct: 0
- Correct-to-wrong: 0
- Changed-label precision: 0.0000

## Interpretation

This replay verifies that the new structured-event patch wrapper preserves the promoted `hybrid_structured_events` substrate when no patch proposals are supplied. It crosses the 0.85 validation threshold only because the saved Qwen v0.6 structured-events source artifact already does (`638/750` Purist). Treat this artifact as a contract/baseline-preservation smoke, not as evidence that an agentic patch policy improves the candidate.

## Claim Boundary

Validation-development no-call replay only. No holdout rows, no row-level test inspection, no scorer change, and no benchmark-facing claim.
