# Gan 2026 v0.10 Component Repair Probe

Date: 2026-06-15

This validation-only no-call probe tests deterministic fresh-component repairs after selector v0.9. It does not read locked test rows and does not make model calls.

## Experiment Unit

- Hypothesis: broad last-event/seizure-free to unknown repair may recover the unknown-boundary residual.
- Comparator: selector v0.9 saved validation replay.
- Surface: full validation750 saved-output replay, because the candidate component repair could affect many seizure-free rows and needs a regression count before any narrower design.
- Scorer: unchanged Gan-compatible Purist.
- Inspection policy: aggregate transitions and validation row records only.
- Stop rule: reject any repair with selected C->W regressions or lower selected Purist; revise only for zero-C->W selected gain.

## Baseline

- v0.9 selected Purist: 733/750
- v0.9 W->C / C->W: 36 / 0

## Rule Results

| Rule | Repairs | Selected Purist | Delta | Selected changes | Selected W->C | Selected C->W | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `seizure_free_last_event_to_unknown` | 20 | 725/750 | -8 | 14 | 3 | 11 | `reject_validation_negative` |
| `last_event_unclear_count_to_unknown` | 3 | 733/750 | 0 | 0 | 0 | 0 | `diagnostic_no_selected_gain` |
| `any_last_event_to_unknown` | 48 | 723/750 | -10 | 18 | 4 | 14 | `reject_validation_negative` |

## Interpretation

The tempting deterministic repair is not safe. The broad rules recover some supervisor-style unknown-boundary rows, but they also rewrite many validation rows where seizure-free is Purist-correct. The narrow unclear-count version makes no selected-label gains and still turns two correct fresh components into wrong fresh components.

Decision: reject broad deterministic last-event-to-unknown component repair. The next component-generation design should make the model emit an explicit ambiguity classification before rendering the final label, rather than relying on a profile-string rewrite.
