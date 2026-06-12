# Gan 2026 Agentic Hard50 Tool-Context Ablation

Date: 2026-06-12

## Experiment Unit

- Work class: E1 validation hard-slice one-call tool-context ablation.
- Rows: 50
- Split: `validation`, manifest `gan2026_split_v1`.
- Surface: fixed validation hard50 manifest.
- Mode: `live`
- Model: `openai/gpt-4.1-mini`
- Prompt version: `gan2026_agentic_matched_budget_prompt_v1`
- JSONL artifact: `experiments\gan2026_agentic_hard50_tool_context_ablation_2026-06-12.jsonl`

## Summary

- Model calls attempted: 200
- Decision records: 200
- Call failures: 0
- Parse/schema/label failures: 0

## Condition Summary

| Condition | Purist | Pragmatic | Wins vs no-tool | Losses vs no-tool | Call failures | Parse failures |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `direct_no_tool_context` | 30/50 | 31/50 | 0 | 0 | 0 | 0 |
| `direct_parser_only` | 21/50 | 22/50 | 4 | 13 | 0 | 0 |
| `direct_boundary_guide_only` | 34/50 | 35/50 | 5 | 1 | 0 | 0 |
| `direct_parser_plus_boundary_guide` | 19/50 | 21/50 | 2 | 13 | 0 | 0 |

## Gate

- Status: `revise_with_non_harmful_context`
- Non-harmful contexts: `direct_boundary_guide_only`
- Harmful contexts: `direct_parser_only, direct_parser_plus_boundary_guide`
- Interpretation: At least one tool-context variant was neutral or better than no-tool; use only the non-harmful context in E2/E3.

## Claim Boundary

validation-development hard50 tool-context ablation; no holdout use, no row-level test inspection, and no benchmark claim

## Rows

| Row | Condition | Final | Purist | Parse notes |
| ---: | --- | --- | --- | --- |
| 3356 | `direct_no_tool_context` | `multiple per month` | yes |  |
| 3356 | `direct_parser_only` | `seizure free for multiple year` | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 3356 | `direct_boundary_guide_only` | `multiple per month` | yes |  |
| 3356 | `direct_parser_plus_boundary_guide` | `seizure free for multiple year` | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 3528 | `direct_no_tool_context` | `multiple per day` | yes |  |
| 3528 | `direct_parser_only` | `unknown` | yes |  |
| 3528 | `direct_boundary_guide_only` | `unknown` | yes |  |
| 3528 | `direct_parser_plus_boundary_guide` | `multiple per day` | yes |  |
| 4690 | `direct_no_tool_context` | `multiple per day` | yes | final_label_repaired: 'unknown' -> 'multiple per day' |
| 4690 | `direct_parser_only` | `seizure free for multiple year` | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 4690 | `direct_boundary_guide_only` | `multiple per day` | yes | final_label_repaired: 'unknown' -> 'multiple per day' |
| 4690 | `direct_parser_plus_boundary_guide` | `seizure free for multiple year` | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5534 | `direct_no_tool_context` | `1 per 2 month` | no | final_label_repaired: '1 per 2 months' -> '1 per 2 month' |
| 5534 | `direct_parser_only` | `no seizure frequency reference` | yes | final_label_repaired: 'infrequent' -> 'no seizure frequency reference' |
| 5534 | `direct_boundary_guide_only` | `1 per 2 month` | no | final_label_repaired: '1 per 2 months' -> '1 per 2 month' |
| 5534 | `direct_parser_plus_boundary_guide` | `1 per 2 month` | no | final_label_repaired: '1 per 2 months' -> '1 per 2 month' |
| 5974 | `direct_no_tool_context` | `seizure free for multiple year` | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5974 | `direct_parser_only` | `seizure free for multiple year` | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 5974 | `direct_boundary_guide_only` | `seizure free for 1 year` | no | final_label_repaired: 'seizure free 1 year' -> 'seizure free for 1 year' |
| 5974 | `direct_parser_plus_boundary_guide` | `seizure free for multiple year` | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 6077 | `direct_no_tool_context` | `1 per year` | no |  |
| 6077 | `direct_parser_only` | `seizure free for 8 month` | no | final_label_repaired: 'seizure free 8 months' -> 'seizure free for 8 month' |
| 6077 | `direct_boundary_guide_only` | `1 per 8 month` | no | final_label_repaired: '1 per 8 months' -> '1 per 8 month' |
| 6077 | `direct_parser_plus_boundary_guide` | `seizure free for 8 month` | no | final_label_repaired: 'seizure free 8 months' -> 'seizure free for 8 month' |
| 6094 | `direct_no_tool_context` | `multiple per month` | no |  |
| 6094 | `direct_parser_only` | `multiple per month` | no |  |
| 6094 | `direct_boundary_guide_only` | `5 per month` | no |  |
| 6094 | `direct_parser_plus_boundary_guide` | `unknown` | no |  |
| 6131 | `direct_no_tool_context` | `no seizure frequency reference` | yes | final_label_repaired: 'no seizures for over 12 months' -> 'no seizure frequency reference' |
| 6131 | `direct_parser_only` | `seizure free for 12 month` | no | final_label_repaired: 'seizure free 12 months' -> 'seizure free for 12 month' |
| 6131 | `direct_boundary_guide_only` | `seizure free for 1 year` | no | final_label_repaired: 'seizure free 1 year' -> 'seizure free for 1 year' |
| 6131 | `direct_parser_plus_boundary_guide` | `seizure free for 12 month` | no | final_label_repaired: 'seizure free 12 months' -> 'seizure free for 12 month' |
| 6153 | `direct_no_tool_context` | `9 per 4 week` | yes | final_label_repaired: 'multiple per week' -> '9 per 4 week' |
| 6153 | `direct_parser_only` | `9 per 4 week` | yes | final_label_repaired: 'multiple per month' -> '9 per 4 week' |
| 6153 | `direct_boundary_guide_only` | `9 per 4 week` | yes | final_label_repaired: 'multiple per week' -> '9 per 4 week' |
| 6153 | `direct_parser_plus_boundary_guide` | `3 per 4 week` | no | final_label_repaired: '3 per month' -> '3 per 4 week' |
| 6209 | `direct_no_tool_context` | `multiple per day` | yes | final_label_repaired: 'multiple per day and 2 to 3 per month' -> 'multiple per day' |
| 6209 | `direct_parser_only` | `multiple per day` | yes | final_label_repaired: 'multiple per day and 2 to 3 per month' -> 'multiple per day' |
| 6209 | `direct_boundary_guide_only` | `multiple per day` | yes | final_label_repaired: 'multiple per day and 2 to 3 per month' -> 'multiple per day' |
| 6209 | `direct_parser_plus_boundary_guide` | `multiple per day` | yes | final_label_repaired: 'daily and 2 to 3 per month' -> 'multiple per day' |
| 6244 | `direct_no_tool_context` | `unknown` | yes |  |
| 6244 | `direct_parser_only` | `unknown` | yes |  |
| 6244 | `direct_boundary_guide_only` | `unknown` | yes |  |
| 6244 | `direct_parser_plus_boundary_guide` | `multiple per week` | yes |  |
| 6321 | `direct_no_tool_context` | `2 per year` | no |  |
| 6321 | `direct_parser_only` | `2 per year` | no |  |
| 6321 | `direct_boundary_guide_only` | `2 per year` | no |  |
| 6321 | `direct_parser_plus_boundary_guide` | `2 per year` | no |  |
| 6368 | `direct_no_tool_context` | `multiple per day` | yes | final_label_repaired: '3 per 6 weeks' -> 'multiple per day' |
| 6368 | `direct_parser_only` | `multiple per month` | yes |  |
| 6368 | `direct_boundary_guide_only` | `multiple per day` | yes | final_label_repaired: '3 per 6 weeks' -> 'multiple per day' |
| 6368 | `direct_parser_plus_boundary_guide` | `1 per 1 to 2 week` | no | final_label_repaired: '2 per month' -> '1 per 1 to 2 week' |
| 6501 | `direct_no_tool_context` | `multiple per day` | yes |  |
| 6501 | `direct_parser_only` | `unknown` | yes | final_label_repaired: 'multiple per day during clusters' -> 'unknown' |
| 6501 | `direct_boundary_guide_only` | `multiple per day` | yes |  |
| 6501 | `direct_parser_plus_boundary_guide` | `unknown` | yes | final_label_repaired: 'multiple per day during clusters' -> 'unknown' |
| 6571 | `direct_no_tool_context` | `seizure free for 3 month` | no | final_label_repaired: 'seizure free 3 months' -> 'seizure free for 3 month' |
| 6571 | `direct_parser_only` | `seizure free for multiple year` | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 6571 | `direct_boundary_guide_only` | `seizure free for 4 month` | no | final_label_repaired: 'seizure free 4 months' -> 'seizure free for 4 month' |
| 6571 | `direct_parser_plus_boundary_guide` | `seizure free for multiple year` | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 6987 | `direct_no_tool_context` | `no seizure frequency reference` | yes | final_label_repaired: 'infrequent' -> 'no seizure frequency reference' |
| 6987 | `direct_parser_only` | `unknown` | yes |  |
| 6987 | `direct_boundary_guide_only` | `no seizure frequency reference` | yes | final_label_repaired: 'infrequent' -> 'no seizure frequency reference' |
| 6987 | `direct_parser_plus_boundary_guide` | `unknown` | yes |  |
| 7168 | `direct_no_tool_context` | `2 per year` | no |  |
| 7168 | `direct_parser_only` | `2 per year` | no |  |
| 7168 | `direct_boundary_guide_only` | `2 per year` | no |  |
| 7168 | `direct_parser_plus_boundary_guide` | `2 per year` | no |  |
| 7615 | `direct_no_tool_context` | `no seizure frequency reference` | no | final_label_repaired: 'multiple per cycle' -> 'no seizure frequency reference' |
| 7615 | `direct_parser_only` | `2 per year` | no |  |
| 7615 | `direct_boundary_guide_only` | `3 to 6 per 5 day` | yes | final_label_repaired: '3 to 6 per 5 days' -> '3 to 6 per 5 day' |
| 7615 | `direct_parser_plus_boundary_guide` | `2 per year` | no |  |
| 9496 | `direct_no_tool_context` | `6 per 12 month` | yes | final_label_repaired: 'less than 1 per month' -> '6 per 12 month' |
| 9496 | `direct_parser_only` | `unknown` | no | final_label_repaired: 'no generalised tonic-clonic seizures since March 2018' -> 'unknown' |
| 9496 | `direct_boundary_guide_only` | `6 per 12 month` | yes | final_label_repaired: '2 per month' -> '6 per 12 month' |
| 9496 | `direct_parser_plus_boundary_guide` | `6 per 12 month` | yes | final_label_repaired: 'less than 1 per month' -> '6 per 12 month' |
| 9888 | `direct_no_tool_context` | `no seizure frequency reference` | yes | final_label_repaired: 'sporadic' -> 'no seizure frequency reference' |
| 9888 | `direct_parser_only` | `seizure free for multiple year` | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 9888 | `direct_boundary_guide_only` | `no seizure frequency reference` | yes | final_label_repaired: 'sporadic' -> 'no seizure frequency reference' |
| 9888 | `direct_parser_plus_boundary_guide` | `multiple per year` | yes |  |
| 9937 | `direct_no_tool_context` | `unknown` | no |  |
| 9937 | `direct_parser_only` | `unknown` | no |  |
| 9937 | `direct_boundary_guide_only` | `unknown` | no |  |
| 9937 | `direct_parser_plus_boundary_guide` | `unknown` | no |  |
| 9943 | `direct_no_tool_context` | `1 per 4 to 5 week` | no | final_label_repaired: 'multiple per week' -> '1 per 4 to 5 week' |
| 9943 | `direct_parser_only` | `1 per 4 to 5 week` | no | final_label_repaired: 'multiple per month' -> '1 per 4 to 5 week' |
| 9943 | `direct_boundary_guide_only` | `1 per 4 to 5 week` | no | final_label_repaired: 'unknown' -> '1 per 4 to 5 week' |
| 9943 | `direct_parser_plus_boundary_guide` | `1 per 4 to 5 week` | no | final_label_repaired: 'unknown' -> '1 per 4 to 5 week' |
| 9955 | `direct_no_tool_context` | `1 cluster per month, multiple per cluster` | yes | final_label_repaired: 'multiple per month' -> '1 cluster per month, multiple per cluster' |
| 9955 | `direct_parser_only` | `1 per month` | no | final_label_repaired: 'once per month' -> '1 per month' |
| 9955 | `direct_boundary_guide_only` | `1 cluster per month, multiple per cluster` | yes | final_label_repaired: 'unknown' -> '1 cluster per month, multiple per cluster' |
| 9955 | `direct_parser_plus_boundary_guide` | `1 per month` | no |  |
| 10266 | `direct_no_tool_context` | `unknown` | yes |  |
| 10266 | `direct_parser_only` | `unknown` | yes |  |
| 10266 | `direct_boundary_guide_only` | `unknown` | yes |  |
| 10266 | `direct_parser_plus_boundary_guide` | `unknown` | yes |  |
| 10618 | `direct_no_tool_context` | `multiple per day` | yes |  |
| 10618 | `direct_parser_only` | `multiple per day` | yes |  |
| 10618 | `direct_boundary_guide_only` | `multiple per day` | yes |  |
| 10618 | `direct_parser_plus_boundary_guide` | `multiple per day` | yes |  |
| 10677 | `direct_no_tool_context` | `1 per month` | no |  |
| 10677 | `direct_parser_only` | `1 cluster per month, multiple per cluster` | yes | final_label_repaired: '1 per month' -> '1 cluster per month, multiple per cluster' |
| 10677 | `direct_boundary_guide_only` | `1 cluster per month, multiple per cluster` | yes | final_label_repaired: '1 per month' -> '1 cluster per month, multiple per cluster' |
| 10677 | `direct_parser_plus_boundary_guide` | `1 per month` | no | final_label_repaired: 'once a month' -> '1 per month' |
| 10996 | `direct_no_tool_context` | `1 to 2 per month` | no |  |
| 10996 | `direct_parser_only` | `1 to 2 per month` | no |  |
| 10996 | `direct_boundary_guide_only` | `1 to 2 cluster per month, 4 per cluster` | yes | final_label_repaired: '1 to 2 per month' -> '1 to 2 cluster per month, 4 per cluster' |
| 10996 | `direct_parser_plus_boundary_guide` | `1 to 2 per month` | no |  |
| 12422 | `direct_no_tool_context` | `1 per day` | yes | final_label_repaired: 'nightly generalised convulsions and 4 per year tonic seizures' -> '1 per day' |
| 12422 | `direct_parser_only` | `4 per year` | no | final_label_repaired: 'four per year' -> '4 per year' |
| 12422 | `direct_boundary_guide_only` | `1 per day` | yes | final_label_repaired: 'nightly generalised convulsions and 4 per year tonic seizures' -> '1 per day' |
| 12422 | `direct_parser_plus_boundary_guide` | `4 per year` | no |  |
| 12438 | `direct_no_tool_context` | `1 per day` | yes | final_label_repaired: 'nightly generalised tonic-clonic seizures and intermittent tonic seizures 2 to 3 per year' -> '1 per day' |
| 12438 | `direct_parser_only` | `1 per day` | yes | final_label_repaired: 'nightly generalised tonic-clonic seizures and 2 to 3 per year tonic seizures' -> '1 per day' |
| 12438 | `direct_boundary_guide_only` | `1 per day` | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 12438 | `direct_parser_plus_boundary_guide` | `2 to 3 per year` | no |  |
| 12456 | `direct_no_tool_context` | `1 per day` | yes | final_label_repaired: 'nightly generalised tonic-clonic seizures and intermittent tonic seizures three times per year' -> '1 per day' |
| 12456 | `direct_parser_only` | `3 per year` | no |  |
| 12456 | `direct_boundary_guide_only` | `1 per day` | yes | final_label_repaired: 'nightly generalised tonic-clonic seizures and intermittent tonic seizures 3 per year' -> '1 per day' |
| 12456 | `direct_parser_plus_boundary_guide` | `3 per year` | no | final_label_repaired: 'three per year' -> '3 per year' |
| 12460 | `direct_no_tool_context` | `1 per day` | yes | final_label_repaired: 'nightly generalised convulsions' -> '1 per day' |
| 12460 | `direct_parser_only` | `2 per year` | no |  |
| 12460 | `direct_boundary_guide_only` | `1 per day` | yes | final_label_repaired: 'nightly generalised convulsions and tonic seizures 2 per year' -> '1 per day' |
| 12460 | `direct_parser_plus_boundary_guide` | `2 per year` | no |  |
| 12468 | `direct_no_tool_context` | `1 per day` | yes | final_label_repaired: '4 per year' -> '1 per day' |
| 12468 | `direct_parser_only` | `4 per year` | no |  |
| 12468 | `direct_boundary_guide_only` | `1 per day` | yes | final_label_repaired: '4 per year' -> '1 per day' |
| 12468 | `direct_parser_plus_boundary_guide` | `4 per year` | no |  |
| 13843 | `direct_no_tool_context` | `unknown` | no |  |
| 13843 | `direct_parser_only` | `unknown` | no |  |
| 13843 | `direct_boundary_guide_only` | `unknown` | no |  |
| 13843 | `direct_parser_plus_boundary_guide` | `unknown` | no |  |
| 13858 | `direct_no_tool_context` | `unknown` | no |  |
| 13858 | `direct_parser_only` | `seizure free for multiple year` | yes | final_label_repaired: 'unknown' -> 'seizure free for multiple year' |
| 13858 | `direct_boundary_guide_only` | `unknown` | no |  |
| 13858 | `direct_parser_plus_boundary_guide` | `unknown` | no |  |
| 13889 | `direct_no_tool_context` | `seizure free for multiple year` | yes | final_label_repaired: 'unknown' -> 'seizure free for multiple year' |
| 13889 | `direct_parser_only` | `seizure free for multiple year` | yes | final_label_repaired: 'unknown' -> 'seizure free for multiple year' |
| 13889 | `direct_boundary_guide_only` | `seizure free for multiple year` | yes | final_label_repaired: 'unknown' -> 'seizure free for multiple year' |
| 13889 | `direct_parser_plus_boundary_guide` | `seizure free for multiple year` | yes | final_label_repaired: 'unknown' -> 'seizure free for multiple year' |
| 14025 | `direct_no_tool_context` | `2 per year` | no |  |
| 14025 | `direct_parser_only` | `seizure free for multiple year` | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 14025 | `direct_boundary_guide_only` | `2 per year` | no |  |
| 14025 | `direct_parser_plus_boundary_guide` | `unknown` | yes | final_label_repaired: 'no generalised tonic–clonic seizures' -> 'unknown' |
| 14076 | `direct_no_tool_context` | `multiple per day` | yes |  |
| 14076 | `direct_parser_only` | `unknown` | yes |  |
| 14076 | `direct_boundary_guide_only` | `unknown` | yes |  |
| 14076 | `direct_parser_plus_boundary_guide` | `unknown` | yes |  |
| 14810 | `direct_no_tool_context` | `seizure free for multiple year` | no | final_label_repaired: 'seizure free 4 weeks' -> 'seizure free for multiple year' |
| 14810 | `direct_parser_only` | `seizure free for multiple year` | no | final_label_repaired: 'seizure free 4 weeks' -> 'seizure free for multiple year' |
| 14810 | `direct_boundary_guide_only` | `seizure free for multiple year` | no | final_label_repaired: 'seizure free 4 weeks' -> 'seizure free for multiple year' |
| 14810 | `direct_parser_plus_boundary_guide` | `seizure free for multiple year` | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 14821 | `direct_no_tool_context` | `seizure free for multiple year` | no | final_label_repaired: 'seizure free 3 weeks' -> 'seizure free for multiple year' |
| 14821 | `direct_parser_only` | `seizure free for multiple year` | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 14821 | `direct_boundary_guide_only` | `seizure free for multiple year` | no | final_label_repaired: 'seizure free 3 weeks' -> 'seizure free for multiple year' |
| 14821 | `direct_parser_plus_boundary_guide` | `seizure free for multiple year` | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 15168 | `direct_no_tool_context` | `multiple per day` | yes |  |
| 15168 | `direct_parser_only` | `seizure free for multiple year` | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 15168 | `direct_boundary_guide_only` | `multiple per day` | yes |  |
| 15168 | `direct_parser_plus_boundary_guide` | `seizure free for 1 year` | no | final_label_repaired: 'seizure free 1 year' -> 'seizure free for 1 year' |
| 15193 | `direct_no_tool_context` | `9 per year` | no | final_label_repaired: 'no generalised seizures since 9 per year' -> '9 per year' |
| 15193 | `direct_parser_only` | `seizure free for 1 year` | no | final_label_repaired: 'seizure free 1 year' -> 'seizure free for 1 year' |
| 15193 | `direct_boundary_guide_only` | `multiple per month` | yes |  |
| 15193 | `direct_parser_plus_boundary_guide` | `seizure free for 1 year` | no | final_label_repaired: 'seizure free 1 year' -> 'seizure free for 1 year' |
| 15593 | `direct_no_tool_context` | `1 cluster per 5 day, 2 to 4 per cluster` | yes | final_label_repaired: 'multiple per day' -> '1 cluster per 5 day, 2 to 4 per cluster' |
| 15593 | `direct_parser_only` | `2 per 6 month` | no | final_label_repaired: '2 per 6 months' -> '2 per 6 month' |
| 15593 | `direct_boundary_guide_only` | `1 cluster per 5 day, 2 to 4 per cluster` | yes | final_label_repaired: '2 to 4 per day' -> '1 cluster per 5 day, 2 to 4 per cluster' |
| 15593 | `direct_parser_plus_boundary_guide` | `2 per 6 month` | no | final_label_repaired: '2 per 6 months' -> '2 per 6 month' |
| 15672 | `direct_no_tool_context` | `1 per day` | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 15672 | `direct_parser_only` | `1 per day` | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 15672 | `direct_boundary_guide_only` | `1 per day` | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 15672 | `direct_parser_plus_boundary_guide` | `1 per day` | yes | final_label_repaired: 'multiple per day' -> '1 per day' |
| 15834 | `direct_no_tool_context` | `multiple per week` | no |  |
| 15834 | `direct_parser_only` | `5 per week` | yes |  |
| 15834 | `direct_boundary_guide_only` | `5 per week` | yes |  |
| 15834 | `direct_parser_plus_boundary_guide` | `5 per week` | yes |  |
| 2748 | `direct_no_tool_context` | `1 per month` | yes |  |
| 2748 | `direct_parser_only` | `1 per month` | yes |  |
| 2748 | `direct_boundary_guide_only` | `1 per month` | yes |  |
| 2748 | `direct_parser_plus_boundary_guide` | `1 per month` | yes |  |
| 4368 | `direct_no_tool_context` | `5 per 2 month` | yes | final_label_repaired: 'multiple per month' -> '5 per 2 month' |
| 4368 | `direct_parser_only` | `5 per 2 month` | yes | final_label_repaired: '5 per year' -> '5 per 2 month' |
| 4368 | `direct_boundary_guide_only` | `5 per 2 month` | yes | final_label_repaired: '5 per year' -> '5 per 2 month' |
| 4368 | `direct_parser_plus_boundary_guide` | `5 per 2 month` | yes | final_label_repaired: '5 per 3 months' -> '5 per 2 month' |
| 5921 | `direct_no_tool_context` | `1 per 6 to 8 week` | yes | final_label_repaired: '1 per 6 to 8 weeks' -> '1 per 6 to 8 week' |
| 5921 | `direct_parser_only` | `1 per 6 to 8 week` | yes | final_label_repaired: 'once every 6 to 8 weeks' -> '1 per 6 to 8 week' |
| 5921 | `direct_boundary_guide_only` | `1 per 6 to 8 week` | yes | final_label_repaired: '1 per 6 to 8 weeks' -> '1 per 6 to 8 week' |
| 5921 | `direct_parser_plus_boundary_guide` | `1 per 6 to 8 week` | yes | final_label_repaired: 'once every 6 to 8 weeks' -> '1 per 6 to 8 week' |
| 6889 | `direct_no_tool_context` | `multiple per week` | yes |  |
| 6889 | `direct_parser_only` | `multiple per week` | yes | final_label_repaired: 'several per week generalised and once every 2 to 3 weeks focal' -> 'multiple per week' |
| 6889 | `direct_boundary_guide_only` | `multiple per week` | yes | final_label_repaired: 'several per week generalised myoclonic jerks, 3 per 6 months generalised tonic–clonic, 1 per 2–3 weeks focal seizures' -> 'multiple per week' |
| 6889 | `direct_parser_plus_boundary_guide` | `multiple per week` | yes | final_label_repaired: 'several per week' -> 'multiple per week' |
| 10386 | `direct_no_tool_context` | `1 cluster per week, 2 to 3 per cluster` | yes | final_label_repaired: 'weekly' -> '1 cluster per week, 2 to 3 per cluster' |
| 10386 | `direct_parser_only` | `unknown` | no | final_label_repaired: 'weekly 2 to 3 per cluster' -> 'unknown' |
| 10386 | `direct_boundary_guide_only` | `1 cluster per week, 2 to 3 per cluster` | yes | final_label_repaired: 'weekly' -> '1 cluster per week, 2 to 3 per cluster' |
| 10386 | `direct_parser_plus_boundary_guide` | `2 to 3 per week` | yes |  |
| 11216 | `direct_no_tool_context` | `seizure free for 4 month` | no | final_label_repaired: 'seizure free 4 months' -> 'seizure free for 4 month' |
| 11216 | `direct_parser_only` | `seizure free for multiple year` | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 11216 | `direct_boundary_guide_only` | `seizure free for 4 month` | no | final_label_repaired: 'seizure free 4 months' -> 'seizure free for 4 month' |
| 11216 | `direct_parser_plus_boundary_guide` | `seizure free for multiple year` | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
