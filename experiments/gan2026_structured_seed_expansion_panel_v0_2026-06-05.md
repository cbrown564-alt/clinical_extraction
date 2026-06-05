# Gan 2026 Structured Seed Expansion Panel

Synthetic validation-development mechanism panel derived from clean structured seed slices. It is not validation750, not holdout, and not benchmark evidence.

## Decision

ready_for_structured_generator_smoke

## Summary

| Metric | Value |
| --- | ---: |
| rows | 180 |
| synthetic hard rows | 90 |
| synthetic control rows | 90 |
| exact evidence rows | 180 |

## Families

| Family | Total | Hard | Control |
| --- | ---: | ---: | ---: |
| `cluster_completion` | 60 | 30 | 30 |
| `seizure_free_to_unknown` | 60 | 30 | 30 |
| `yearly_to_daily` | 60 | 30 | 30 |

## Next Step

Run the next typed event generator on this synthetic hard/control panel. Promote only to validation hard/control panels if it emits hard-case candidates while suppressing matched controls with exact evidence.

## Artifacts

- Panel JSONL: `experiments/gan2026_structured_seed_expansion_panel_v0_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_structured_seed_expansion_panel_v0_2026-06-05.json`
