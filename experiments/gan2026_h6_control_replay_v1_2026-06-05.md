# Gan 2026 H6 Control Replay v1

Stage 4 H6 replay sidecar. It verifies no H6 control regression from saved validation summaries and reports changed-label precision where summary-level changed-row counts are available.

## Decision

h6_control_replay_v1_passed

## Candidates

| Candidate | H6 controls | H6 regressions | Changed precision | Source decision |
| --- | ---: | ---: | ---: | --- |
| `boundary_selector_precision_revision_v1` | 0 | 0 | 1.0000 | `boundary_selector_precision_revision_v1_precision_fixed_low_coverage` |
| `h9_release_lane_ablation_v1` | 0 | 0 | 1.0000 | `h9_release_lane_ablation_v1_passed_guardrail` |
| `untagged_nonprediction_release_candidate_v0_assembled_candidate` | 37 | 0 | 1.0000 | `candidate_patch_passes_validation_no_regression_gate` |
