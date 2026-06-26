# Gan 2026 Fresh-Evidence Safety Gate v0.4 No-Call Replay

Date: 2026-06-15

Validation-development saved-output replay only. No hosted calls, scorer changes,
holdout row inspection, or benchmark claim.

## Experiment Unit

- Work class: V12 selector hardening / saved-output replay.
- Hypothesis: V12 `unknown` replacements are not selective enough and should
  fall back to the original structured-event final unless a later validation
  design proves a safer boundary-specific selector.
- Minimal change: bump `SAFETY_GATE_VERSION` to
  `gan2026_fresh_evidence_safety_gate_v0_4` and add
  `fresh_evidence_gate_fallback: unknown_replacement_not_selective`.
- Source artifact:
  `experiments/gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13.jsonl`.
- Surface: validation750, split manifest `gan2026_split_v1`.

## Replay Summary

| Condition | Purist |
| --- | ---: |
| V0 structured-event reference | 661/750 |
| V12 v0.4 original final | 682/750 |
| V12 safety-gate v0.4 replay | 683/750 |

Safety-gate v0.4 transition profile versus V0:

| Transition | Rows |
| --- | ---: |
| correct_to_correct | 642 |
| correct_to_wrong | 19 |
| wrong_to_correct | 41 |
| wrong_to_wrong | 48 |

Gate events in the replay:

| Gate event | Rows |
| --- | ---: |
| unknown_replacement_not_selective | 14 |
| original_seizure_free_to_unknown_or_no_reference | 5 |
| evidence_not_exact | 1 |
| unscorable_fresh_label: `4 to 6 per cluster, clusters occur intermittently` | 1 |
| unscorable_fresh_label: `1 per few week` | 1 |

## Interpretation

The gate is directionally correct but too small to change the research
trajectory. It suppresses a net-negative replacement family and improves
validation750 by one Purist row, but it does not create a credible path from the
completed V12 holdout result (`379/450`) to the requested `>=405/450` Purist
threshold.

Treat this as a conservative selector hardening step and a stop signal for the
current V12 family. Further progress likely needs a new validation-only
architecture that improves clinical selection before another frozen holdout
audit.

## Source-Symmetry Side Check

After the DeepSeek `test450` structured-event artifact was filled, the exact
three-agent consensus replay became source-symmetric. Aggregate-only in-memory
replay over the locked test split produced:

- Deterministic tool floor: 343/450 Purist.
- Three-agent exact consensus: 366/450 Purist.
- Changed labels: 85.
- Wrong-to-correct: 36.
- Correct-to-wrong: 13.
- Changed-label precision: 0.4235.

This resolves the source-coverage asymmetry but does not produce a competitive
holdout candidate.
