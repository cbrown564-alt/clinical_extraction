# Gan 2026 Source-Near Contrast Panel

Date: 2026-06-15

Validation-only paired hard-negative contract (step 3.3 of the unknown-frequency agentic pathways doc). Each pair shares surface cues but requires opposite calls, so generation is stressed on the *distinction*, not just the easy demote-to-unknown direction. It makes no model calls, reads no locked test rows, and does not change the scorer.

## Necessary, not sufficient

This is a parser/safety-gate contract: it feeds each intended decision and checks the gate preserves it. The live run showed that feeding the class in masks the hard part — the static supervisor panel passed `6/6` while live generation collapsed an explicit `2 per 5 month` (`13267`) to `unknown`. So passing this panel statically is required before, but does not substitute for, scoring live generation against the same pairs. Cluster burden is a separate generation problem (Insight 3); the cluster pair predeclares the contrast, it does not claim the renderer solves it.

## Summary

- Prompt version under development: `gan2026_fresh_evidence_reasoner_v0_6`
- Safety gate: `gan2026_fresh_evidence_safety_gate_v0_9`
- Cases passed: `6/6`
- Pairs passing both directions: `3/3`
- Failed cases: `none`
- Observed ambiguity classes: `{'cluster_axis_complete': 1, 'cluster_axis_incomplete': 1, 'explicit_count_window': 1, 'explicit_seizure_free_duration': 1, 'last_event_only_unknown': 1, 'unknown_count_or_window': 1}`

## Pairs

| Pair | Direction | Distinction | Expected label | Observed label | Expected class | Observed class | Passed |
| --- | --- | --- | --- | --- | --- | --- | :---: |
| last_event | ambiguous | last seizure date only | `unknown` | `unknown` | `last_event_only_unknown` | `last_event_only_unknown` | yes |
| last_event | determinate | last seizure date plus independently stated duration | `seizure free for 6 month` | `seizure free for 6 month` | `explicit_seizure_free_duration` | `explicit_seizure_free_duration` | yes |
| since_treatment_count | ambiguous | open-ended since-medication count | `unknown` | `unknown` | `unknown_count_or_window` | `unknown_count_or_window` | yes |
| since_treatment_count | determinate | explicit count plus defined follow-up period | `3 per 6 month` | `3 per 6 month` | `explicit_count_window` | `explicit_count_window` | yes |
| cluster_cadence | ambiguous | cluster cadence without events-per-cluster | `unknown` | `unknown` | `cluster_axis_incomplete` | `cluster_axis_incomplete` | yes |
| cluster_cadence | determinate | cluster cadence plus events-per-cluster | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `cluster_axis_complete` | `cluster_axis_complete` | yes |

## Decision

The gate preserves both directions of every contrast pair, so the panel is a clean predeclared hard-negative set for the next live run. The live run must reproduce these distinctions from raw evidence without the class fed in; only then is the ambiguity-class decision trustworthy enough to treat as a feature.
