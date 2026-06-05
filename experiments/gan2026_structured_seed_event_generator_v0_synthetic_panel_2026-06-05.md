# Gan 2026 Structured Seed Event Generator Smoke

Synthetic development smoke for a typed seed event generator. It is not validation750, not holdout, and not benchmark evidence.

## Decision

promote_to_validation_hard_control_design

## Summary

| Metric | Value |
| --- | ---: |
| rows | 180 |
| hard rows | 90 |
| control rows | 90 |
| hard emit rows | 90 |
| control suppressed rows | 90 |
| exact evidence rows | 180 |
| expected action mismatches | 0 |

## Families

| Family | Rows |
| --- | ---: |
| `cluster_completion` | 60 |
| `seizure_free_to_unknown` | 60 |
| `yearly_to_daily` | 60 |

## Next Step

Translate these synthetic recognizers into validation hard/control row selection and typed event extraction. Do not use locked test rows.

## Artifacts

- Generator JSONL: `experiments/gan2026_structured_seed_event_generator_v0_synthetic_panel_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_structured_seed_event_generator_v0_synthetic_panel_2026-06-05.json`
- Source panel JSONL: `experiments/gan2026_structured_seed_expansion_panel_v0_2026-06-05.jsonl`
