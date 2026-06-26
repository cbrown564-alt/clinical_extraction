# Gan 2026 Structured Seed Validation Extractor Smoke

Validation-development smoke for typed seed event extraction. It uses validation notes in memory, writes no note text, and does not authorize locked-test or holdout-facing use.

## Decision

validation_smoke_passed_undercoverage

## Summary

| Metric | Value |
| --- | ---: |
| rows | 46 |
| hard rows | 23 |
| control rows | 23 |
| hard emit rows | 23 |
| control suppressed rows | 23 |
| exact evidence rows | 44 |
| hard exact evidence rows | 23 |
| control reference retrievable rows | 21 |
| expected action mismatches | 0 |

## Families

| Family | Rows |
| --- | ---: |
| `cluster_completion` | 10 |
| `seizure_free_to_unknown` | 26 |
| `yearly_to_daily` | 10 |

## Next Step

Broaden validation hard/control construction beyond the seed families until the typed candidate/event surface can reach at least 60 W->C, 150 prediction-bearing rows, <=5% matched-control C->W, and >=95% parse-ok plus exact-evidence rows.

## Artifacts

- Extractor JSONL: `experiments/gan2026_structured_seed_validation_extractor_v0_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_structured_seed_validation_extractor_v0_2026-06-05.json`
- Source panel JSONL: `experiments/gan2026_structured_seed_validation_panel_v0_2026-06-05.jsonl`
