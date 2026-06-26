# Gan 2026 Structured Seed Validation Panel

Validation-development hard/control design panel for structured seed event extraction. It reads validation rows only, omits note text from artifacts, and does not authorize holdout use.

## Decision

ready_for_validation_extractor_smoke

## Summary

| Metric | Value |
| --- | ---: |
| rows | 46 |
| hard rows | 23 |
| control rows | 23 |
| exact reference rows | 46 |

## Families

| Family | Total | Hard | Control |
| --- | ---: | ---: | ---: |
| `cluster_completion` | 10 | 5 | 5 |
| `seizure_free_to_unknown` | 26 | 13 | 13 |
| `yearly_to_daily` | 10 | 5 | 5 |

## Next Step

Run a validation extractor smoke that loads note text in memory, emits typed candidates for hard rows, suppresses matched controls, and writes only bounded row metadata plus exact evidence strings.

## Artifacts

- Panel JSONL: `experiments/gan2026_structured_seed_validation_panel_v0_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_structured_seed_validation_panel_v0_2026-06-05.json`
- Source current artifact: `experiments/gan2026_combined_change_only_switch_layer_validation750_2026-06-05.jsonl`
