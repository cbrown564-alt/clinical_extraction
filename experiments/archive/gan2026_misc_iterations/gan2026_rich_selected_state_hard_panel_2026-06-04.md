# Gan 2026 Rich Selected-State Hard-Panel Run

- JSONL: `experiments/gan2026_rich_selected_state_hard_panel_2026-06-04.jsonl`
- Architecture: `llm_only_rich_selected_state_reasoner`
- Prompt version: `gan2026_llm_only_rich_selected_state_reasoner_v0`
- Schema version: `rich_selected_state_v0`
- Split: `validation` / `gan2026_split_v1`
- Mode: `live`
- Model: `openai/gpt-4.1-mini`
- Claim boundary: validation-development component study, not F1.

## Summary

- Rows: 75
- Structured records: 75
- Rows with parse/boundary errors: 3
- Deterministic projected labels: 75
- Deterministic projected parseable labels: 75
- Error families: `{'evidence': 2, 'selected_state_trace': 1}`

## Rows

| Row | Gold | State kind | Evidence exact | Boundary errors | Projected label |
| ---: | --- | --- | --- | --- | --- |
| 190 | `1 per 4 week` | `frequency` | `valid` | `` | `unknown, 1 per cluster` |
| 278 | `multiple per week` | `frequency` | `valid` | `` | `multiple per week` |
| 338 | `multiple per month` | `frequency` | `valid` | `` | `unknown` |
| 743 | `multiple per week` | `frequency` | `valid` | `` | `unknown` |
| 744 | `multiple per week` | `frequency` | `valid` | `` | `unknown` |
| 816 | `1 per month` | `frequency` | `valid` | `` | `1 per month` |
| 869 | `multiple per month` | `frequency` | `valid` | `` | `unknown` |
| 959 | `1 per 2 month` | `frequency` | `valid` | `` | `unknown, 2 per cluster` |
| 960 | `1 per 2 month` | `frequency` | `valid` | `` | `multiple per month` |
| 987 | `1 per 2 month` | `frequency` | `valid` | `` | `unknown` |
| 1046 | `3 to 5 per month` | `frequency` | `valid` | `` | `3 to 5 per month` |
| 1317 | `unknown, multiple per cluster` | `frequency` | `valid` | `` | `unknown` |
| 1363 | `3 per day` | `frequency` | `valid` | `` | `unknown, 3 per cluster` |
| 1687 | `multiple per week` | `frequency` | `valid` | `` | `multiple per week` |
| 1694 | `1 cluster per 2 week, 3 per cluster` | `frequency` | `valid` | `` | `unknown, 3 per cluster` |
| 1695 | `multiple per month` | `frequency` | `invalid` | `evidence: invalid selected evidence` | `unknown` |
| 1706 | `multiple cluster per month, multiple per cluster` | `frequency` | `valid` | `` | `multiple per month` |
| 1707 | `multiple per week` | `frequency` | `valid` | `` | `unknown` |
| 1923 | `7 per 6 month` | `frequency` | `valid` | `` | `7 per 6 month` |
| 2080 | `multiple per month` | `frequency` | `valid` | `` | `unknown, 2 per cluster` |
| 2748 | `1 per month` | `frequency` | `valid` | `` | `1 per month` |
| 3356 | `unknown` | `frequency` | `valid` | `` | `unknown` |
| 3528 | `unknown` | `frequency` | `valid` | `` | `multiple per day` |
| 4368 | `5 per 2 month` | `frequency` | `valid` | `` | `unknown` |
| 4690 | `multiple per day` | `frequency` | `valid` | `` | `10 per day` |
| 5534 | `1 per multiple month` | `frequency` | `valid` | `` | `1 per 14 day` |
| 5921 | `1 per 6 to 8 week` | `frequency` | `valid` | `` | `unknown` |
| 5974 | `unknown` | `frequency` | `valid` | `` | `unknown` |
| 6077 | `unknown` | `frequency` | `valid` | `` | `unknown` |
| 6094 | `3 per month` | `frequency` | `invalid` | `evidence: invalid selected evidence` | `unknown, 1 to 3 per cluster` |
| 6131 | `unknown` | `frequency` | `valid` | `` | `unknown` |
| 6153 | `9 per month` | `frequency` | `valid` | `selected_state_trace: raw_source_phrase not in selected_evidence` | `unknown` |
| 6209 | `multiple per day` | `frequency` | `valid` | `` | `2 to 3 per day` |
| 6244 | `unknown` | `frequency` | `valid` | `` | `unknown` |
| 6321 | `unknown` | `frequency` | `valid` | `` | `unknown` |
| 6368 | `unknown` | `frequency` | `valid` | `` | `unknown, 1 per cluster` |
| 6501 | `unknown` | `frequency` | `valid` | `` | `unknown` |
| 6571 | `unknown` | `frequency` | `valid` | `` | `unknown` |
| 6889 | `multiple per week` | `frequency` | `valid` | `` | `unknown` |
| 6987 | `unknown` | `frequency` | `valid` | `` | `unknown` |
| 7168 | `unknown` | `frequency` | `valid` | `` | `unknown, 2 per cluster` |
| 7615 | `3 to 7 per month` | `frequency` | `valid` | `` | `unknown, 3 to 6 per cluster` |
| 9496 | `6 per 12 month` | `frequency` | `valid` | `` | `0 to 2 per month` |
| 9888 | `unknown` | `frequency` | `valid` | `` | `unknown` |
| 9937 | `1 cluster per month, multiple per cluster` | `frequency` | `valid` | `` | `multiple per week` |
| 9943 | `1 cluster per 4 to 5 week, multiple per cluster` | `frequency` | `valid` | `` | `unknown` |
| 9955 | `1 cluster per month, multiple per cluster` | `frequency` | `valid` | `` | `multiple per month` |
| 10266 | `unknown` | `unknown` | `valid` | `` | `unknown` |
| 10386 | `1 cluster per week, 2 to 3 per cluster` | `frequency` | `valid` | `` | `2 to 3 per week` |
| 10618 | `unknown, 4 to 6 per cluster` | `frequency` | `valid` | `` | `unknown, 4 to 6 per cluster` |
| 10677 | `1 cluster per month, multiple per cluster` | `frequency` | `valid` | `` | `unknown` |
| 10996 | `1 to 2 cluster per month, 4 per cluster` | `frequency` | `valid` | `` | `1 to 2 per month` |
| 11216 | `unknown` | `seizure_free` | `valid` | `` | `unknown` |
| 11254 | `unknown` | `frequency` | `valid` | `` | `unknown` |
| 11259 | `unknown` | `seizure_free` | `valid` | `` | `unknown` |
| 11272 | `unknown` | `seizure_free` | `valid` | `` | `unknown` |
| 12422 | `1 per day` | `frequency` | `valid` | `` | `4 per year` |
| 12438 | `1 per day` | `frequency` | `valid` | `` | `2 to 3 per year` |
| 12456 | `1 per day` | `frequency` | `valid` | `` | `1 per day` |
| 12460 | `1 per day` | `frequency` | `valid` | `` | `2 per year` |
| 12468 | `1 per day` | `frequency` | `valid` | `` | `4 per year` |
| 13209 | `1 per 8 month` | `frequency` | `valid` | `` | `unknown` |
| 13843 | `seizure free for multiple month` | `frequency` | `valid` | `` | `unknown` |
| 13858 | `seizure free for multiple month` | `frequency` | `valid` | `` | `unknown` |
| 13889 | `seizure free for multiple month` | `frequency` | `valid` | `` | `unknown` |
| 14025 | `unknown` | `frequency` | `valid` | `` | `unknown` |
| 14076 | `unknown` | `frequency` | `valid` | `` | `unknown` |
| 14810 | `1 per month` | `seizure_free` | `valid` | `` | `unknown` |
| 14821 | `1 per month` | `seizure_free` | `valid` | `` | `unknown` |
| 15168 | `multiple per 15 month` | `frequency` | `valid` | `` | `unknown` |
| 15193 | `multiple per 13 month` | `frequency` | `valid` | `` | `0 per 9 to 10 month` |
| 15593 | `1 cluster per 5 day, 2 to 4 per cluster` | `frequency` | `valid` | `` | `unknown, 2 to 4 per cluster` |
| 15672 | `1 per day` | `frequency` | `valid` | `` | `unknown` |
| 15834 | `5 per week` | `frequency` | `valid` | `` | `5 per week` |
| 15986 | `11 per 3 month` | `frequency` | `valid` | `` | `1 to 5 per month` |
