# Gan 2026 Rich Selected-State Five-Letter Run

- JSONL: `experiments/gan2026_rich_selected_state_five_letter_2026-06-04.jsonl`
- Architecture: `llm_only_rich_selected_state_reasoner`
- Prompt version: `gan2026_llm_only_rich_selected_state_reasoner_v0`
- Schema version: `rich_selected_state_v0`
- Split: `validation` / `gan2026_split_v1`
- Mode: `live`
- Model: `openai/gpt-4.1-mini`
- Claim boundary: validation-development component study, not F1.

## Summary

- Rows: 5
- Structured records: 5
- Rows with parse/boundary errors: 0
- Deterministic projected labels: 5
- Deterministic projected parseable labels: 5
- Error families: `{}`

## Rows

| Row | Gold | State kind | Evidence exact | Boundary errors | Projected label |
| ---: | --- | --- | --- | --- | --- |
| 10 | `4 per day` | `frequency` | `valid` | `` | `unknown` |
| 280 | `multiple per day` | `frequency` | `valid` | `` | `multiple per day` |
| 3356 | `unknown` | `frequency` | `valid` | `` | `multiple per month` |
| 10618 | `unknown, 4 to 6 per cluster` | `frequency` | `valid` | `` | `4 to 6 per 1 day` |
| 2748 | `1 per month` | `frequency` | `valid` | `` | `1 per 1 month` |
