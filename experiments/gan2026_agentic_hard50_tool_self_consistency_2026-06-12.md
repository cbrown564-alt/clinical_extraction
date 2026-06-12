# Gan 2026 Agentic Hard50 Tool Self-Consistency

Date: 2026-06-12

## Experiment Unit

- Work class: E2 four-call boundary-guide-only tool self-consistency.
- Rows: 50
- Condition: `single_agent_tools_self_consistency_boundary_guide_only`
- Reference condition: `single_self_consistency_temperature`
- Mode: `live`
- Model: `openai/gpt-4.1-mini`
- Prompt version: `gan2026_agentic_matched_budget_prompt_v1`
- JSONL artifact: `experiments\gan2026_agentic_hard50_tool_self_consistency_2026-06-12.jsonl`

## Summary

- Model calls attempted: 200
- Decision records: 200
- Call failures: 0
- Parse/schema/label failures: 0
- Purist: 34/50
- Pragmatic: 35/50
- Wins vs reference: 4
- Losses vs reference: 2

## Gate

- Status: `reject_tool_self_consistency`
- Interpretation: Four-call boundary-guide self-consistency did not produce enough high-precision rescues versus self-consistency; stop the current tool-agent branch before E3/E4.

## Claim Boundary

validation-development hard50 four-call boundary-guide self-consistency; no holdout use, no row-level test inspection, and no benchmark claim

## Rows

| Row | Final | Reference | Purist | Reference Purist | Vote counts | Parse notes |
| ---: | --- | --- | --- | --- | --- | --- |
| 3356 | `multiple per month` | `multiple per month` | yes | yes | `{'multiple per month': 4}` |  |
| 3528 | `unknown` | `multiple per day` | yes | yes | `{'unknown': 4}` |  |
| 4690 | `multiple per day` | `multiple per day` | yes | yes | `{'multiple per day': 4}` | final_label_repaired: 'unknown' -> 'multiple per day'; final_label_repaired: 'unknown' -> 'multiple per day'; final_label_repaired: 'unknown' -> 'multiple per day'; final_label_repaired: 'unknown' -> 'multiple per day' |
| 5534 | `1 per 2 month` | `1 per multiple month` | no | yes | `{'1 per 2 month': 2, '1 per multiple month': 2}` | final_label_repaired: '1 per 2 months' -> '1 per 2 month'; final_label_repaired: '1 per 2 months' -> '1 per 2 month'; final_label_repaired: '1 per several months' -> '1 per multiple month'; final_label_repaired: '1 per several months' -> '1 per multiple month' |
| 5974 | `seizure free for 1 year` | `seizure free for multiple year` | no | no | `{'seizure free for 1 year': 3, 'seizure free for multiple year': 1}` | final_label_repaired: 'seizure free 1 year' -> 'seizure free for 1 year'; final_label_repaired: 'seizure free' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free 1 year' -> 'seizure free for 1 year'; final_label_repaired: 'seizure free 1 year' -> 'seizure free for 1 year' |
| 6077 | `1 per 8 month` | `1 per year` | no | no | `{'1 per 8 month': 4}` | final_label_repaired: '1 per 8 months' -> '1 per 8 month'; final_label_repaired: '1 per 8 months' -> '1 per 8 month'; final_label_repaired: '1 per 8 months' -> '1 per 8 month'; final_label_repaired: '1 per 8 months' -> '1 per 8 month' |
| 6094 | `5 per month` | `5 per month` | no | no | `{'5 per month': 4}` |  |
| 6131 | `seizure free for 12 month` | `no seizure frequency reference` | no | yes | `{'seizure free for 12 month': 2, 'no seizure frequency reference': 2}` | final_label_repaired: 'seizure free 12 months' -> 'seizure free for 12 month'; final_label_repaired: 'seizure free 12 months' -> 'seizure free for 12 month'; final_label_repaired: 'no unprovoked seizures for over 12 months' -> 'no seizure frequency reference'; final_label_repaired: 'no unprovoked seizures for over 12 months' -> 'no seizure frequency reference' |
| 6153 | `9 per 2 month` | `9 per 4 week` | yes | yes | `{'9 per 2 month': 2, 'unknown': 1, '9 per 4 week': 1}` | final_label_repaired: 'unknown' -> '9 per 2 month'; final_label_repaired: '3 per month generalised and 6 per month focal' -> '9 per 4 week'; final_label_repaired: 'unknown' -> '9 per 2 month' |
| 6209 | `multiple per day` | `multiple per day` | yes | yes | `{'multiple per day': 4}` | final_label_repaired: 'multiple per day and 2 to 3 per month' -> 'multiple per day'; final_label_repaired: 'multiple per day and 2 to 3 per month' -> 'multiple per day'; final_label_repaired: 'multiple per day and 2 to 3 per month' -> 'multiple per day' |
| 6244 | `unknown` | `multiple per week` | yes | yes | `{'multiple per week': 1, 'unknown': 3}` |  |
| 6321 | `2 per year` | `2 per year` | no | no | `{'2 per year': 4}` |  |
| 6368 | `multiple per day` | `3 per 6 week` | yes | no | `{'multiple per day': 4}` | final_label_repaired: '3 per 6 weeks' -> 'multiple per day'; final_label_repaired: '3 per 6 weeks' -> 'multiple per day'; final_label_repaired: '3 per 6 weeks' -> 'multiple per day'; final_label_repaired: '3 per 6 weeks' -> 'multiple per day' |
| 6501 | `unknown` | `unknown` | yes | yes | `{'unknown': 4}` | final_label_repaired: 'multiple per day during clusters' -> 'unknown' |
| 6571 | `seizure free for 4 month` | `seizure free for 4 month` | no | no | `{'seizure free for 4 month': 3, 'seizure free for 3 month': 1}` | final_label_repaired: 'seizure free 4 months' -> 'seizure free for 4 month'; final_label_repaired: 'seizure free 4 months' -> 'seizure free for 4 month'; final_label_repaired: 'seizure free 3 months' -> 'seizure free for 3 month'; final_label_repaired: 'seizure free 4 months' -> 'seizure free for 4 month' |
| 6987 | `no seizure frequency reference` | `no seizure frequency reference` | yes | yes | `{'unknown': 1, 'no seizure frequency reference': 3}` | final_label_repaired: 'infrequent' -> 'no seizure frequency reference'; final_label_repaired: 'infrequent' -> 'no seizure frequency reference'; final_label_repaired: 'infrequent' -> 'no seizure frequency reference' |
| 7168 | `2 per year` | `2 per year` | no | no | `{'2 per year': 4}` |  |
| 7615 | `3 to 6 per 5 day` | `2 per year` | yes | no | `{'3 to 6 per 5 day': 3, 'no seizure frequency reference': 1}` | final_label_repaired: '3 to 6 per 5 days' -> '3 to 6 per 5 day'; final_label_repaired: 'multiple per cycle' -> 'no seizure frequency reference'; final_label_repaired: '3 to 6 per 5 days' -> '3 to 6 per 5 day'; final_label_repaired: '3 to 6 per 5 days' -> '3 to 6 per 5 day' |
| 9496 | `6 per 12 month` | `6 per 12 month` | yes | yes | `{'6 per 12 month': 4}` | final_label_repaired: '1 per month' -> '6 per 12 month'; final_label_repaired: 'multiple per month' -> '6 per 12 month'; final_label_repaired: '1 per month' -> '6 per 12 month'; final_label_repaired: 'multiple per month' -> '6 per 12 month' |
| 9888 | `no seizure frequency reference` | `no seizure frequency reference` | yes | yes | `{'no seizure frequency reference': 4}` | final_label_repaired: 'sporadic' -> 'no seizure frequency reference'; final_label_repaired: 'sporadic' -> 'no seizure frequency reference'; final_label_repaired: 'sporadic' -> 'no seizure frequency reference'; final_label_repaired: 'sporadic' -> 'no seizure frequency reference' |
| 9937 | `unknown` | `unknown` | no | no | `{'unknown': 4}` |  |
| 9943 | `1 per 4 to 5 week` | `unknown` | no | no | `{'1 per 4 to 5 week': 4}` | final_label_repaired: 'unknown' -> '1 per 4 to 5 week'; final_label_repaired: 'unknown' -> '1 per 4 to 5 week'; final_label_repaired: 'unknown' -> '1 per 4 to 5 week'; final_label_repaired: 'unknown' -> '1 per 4 to 5 week' |
| 9955 | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | yes | yes | `{'1 cluster per month, multiple per cluster': 4}` | final_label_repaired: 'unknown' -> '1 cluster per month, multiple per cluster'; final_label_repaired: 'unknown' -> '1 cluster per month, multiple per cluster'; final_label_repaired: 'unknown' -> '1 cluster per month, multiple per cluster'; final_label_repaired: 'unknown' -> '1 cluster per month, multiple per cluster' |
| 10266 | `unknown` | `unknown` | yes | yes | `{'unknown': 4}` |  |
| 10618 | `no seizure frequency reference` | `multiple per day` | yes | yes | `{'no seizure frequency reference': 2, 'multiple per day': 2}` | final_label_repaired: '4 to 6 per cluster' -> 'no seizure frequency reference'; final_label_repaired: '4 to 6 per cluster' -> 'no seizure frequency reference' |
| 10677 | `1 cluster per month, multiple per cluster` | `1 per month` | yes | no | `{'1 cluster per month, multiple per cluster': 4}` | final_label_repaired: '1 per month' -> '1 cluster per month, multiple per cluster'; final_label_repaired: '1 per month' -> '1 cluster per month, multiple per cluster'; final_label_repaired: '1 per month' -> '1 cluster per month, multiple per cluster'; final_label_repaired: '1 per month' -> '1 cluster per month, multiple per cluster' |
| 10996 | `1 to 2 cluster per month, 4 per cluster` | `1 to 2 per month` | yes | no | `{'1 to 2 cluster per month, 4 per cluster': 3, '1 to 2 per month': 1}` | final_label_repaired: '1 to 2 per month' -> '1 to 2 cluster per month, 4 per cluster'; final_label_repaired: '1 to 2 per month' -> '1 to 2 cluster per month, 4 per cluster'; final_label_repaired: '1 to 2 per month' -> '1 to 2 cluster per month, 4 per cluster' |
| 12422 | `1 per day` | `1 per day` | yes | yes | `{'1 per day': 4}` | final_label_repaired: 'nightly generalised convulsions and 4 per year tonic seizures' -> '1 per day'; final_label_repaired: 'nightly generalised convulsions and 4 per year tonic seizures' -> '1 per day'; final_label_repaired: 'nightly generalised convulsions and 4 per year tonic seizures' -> '1 per day'; final_label_repaired: 'nightly generalised convulsions and intermittent tonic seizures four times per year' -> '1 per day' |
| 12438 | `1 per day` | `1 per day` | yes | yes | `{'1 per day': 4}` | final_label_repaired: 'multiple per day' -> '1 per day'; final_label_repaired: 'nightly' -> '1 per day'; final_label_repaired: 'multiple per day' -> '1 per day'; final_label_repaired: 'nightly generalised tonic-clonic seizures' -> '1 per day' |
| 12456 | `1 per day` | `1 per day` | yes | yes | `{'1 per day': 4}` | final_label_repaired: 'multiple per day' -> '1 per day'; final_label_repaired: 'multiple per day' -> '1 per day'; final_label_repaired: 'multiple per day and 3 per year' -> '1 per day'; final_label_repaired: 'multiple per day' -> '1 per day' |
| 12460 | `1 per day` | `1 per day` | yes | yes | `{'1 per day': 4}` | final_label_repaired: 'nightly generalised convulsions and intermittent tonic seizures 2 per year' -> '1 per day'; final_label_repaired: 'nightly generalised convulsions and intermittent tonic seizures 2 per year' -> '1 per day'; final_label_repaired: 'nightly generalised convulsions and intermittent tonic seizures 2 per year' -> '1 per day'; final_label_repaired: 'nightly generalised convulsions' -> '1 per day' |
| 12468 | `1 per day` | `1 per day` | yes | yes | `{'1 per day': 4}` | final_label_repaired: 'nightly' -> '1 per day'; final_label_repaired: 'nightly' -> '1 per day'; final_label_repaired: 'nightly generalised tonic-clonic seizures' -> '1 per day'; final_label_repaired: '4 per year' -> '1 per day' |
| 13843 | `unknown` | `unknown` | no | no | `{'unknown': 4}` |  |
| 13858 | `unknown` | `unknown` | no | no | `{'unknown': 4}` |  |
| 13889 | `seizure free for multiple year` | `seizure free for multiple year` | yes | yes | `{'seizure free for multiple year': 4}` | final_label_repaired: 'unknown' -> 'seizure free for multiple year'; final_label_repaired: 'unknown' -> 'seizure free for multiple year'; final_label_repaired: 'unknown' -> 'seizure free for multiple year'; final_label_repaired: 'unknown' -> 'seizure free for multiple year' |
| 14025 | `2 per year` | `2 per year` | no | no | `{'2 per year': 4}` |  |
| 14076 | `unknown` | `unknown` | yes | yes | `{'unknown': 4}` |  |
| 14810 | `seizure free for multiple year` | `seizure free for multiple year` | no | no | `{'seizure free for multiple year': 4}` | final_label_repaired: 'seizure free 4 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free 4 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free 4 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free 4 weeks' -> 'seizure free for multiple year' |
| 14821 | `seizure free for multiple year` | `seizure free for multiple year` | no | no | `{'seizure free for multiple year': 4}` | final_label_repaired: 'seizure free 3 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free 3 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free 3 weeks' -> 'seizure free for multiple year'; final_label_repaired: 'seizure free 3 weeks' -> 'seizure free for multiple year' |
| 15168 | `multiple per day` | `no seizure frequency reference` | yes | yes | `{'multiple per day': 4}` |  |
| 15193 | `multiple per year` | `no seizure frequency reference` | yes | yes | `{'unknown': 1, 'multiple per year': 3}` | final_label_repaired: 'brief absence episodes only' -> 'unknown' |
| 15593 | `1 cluster per 5 day, 2 to 4 per cluster` | `1 cluster per 5 day, 2 to 4 per cluster` | yes | yes | `{'1 cluster per 5 day, 2 to 4 per cluster': 4}` | final_label_repaired: 'multiple per day' -> '1 cluster per 5 day, 2 to 4 per cluster'; final_label_repaired: 'multiple per day' -> '1 cluster per 5 day, 2 to 4 per cluster'; final_label_repaired: 'multiple per day' -> '1 cluster per 5 day, 2 to 4 per cluster'; final_label_repaired: '2 to 4 per day' -> '1 cluster per 5 day, 2 to 4 per cluster' |
| 15672 | `1 per day` | `1 per day` | yes | yes | `{'1 per day': 4}` | final_label_repaired: 'multiple per day' -> '1 per day'; final_label_repaired: 'multiple per day' -> '1 per day'; final_label_repaired: 'multiple per day' -> '1 per day'; final_label_repaired: 'multiple per day' -> '1 per day' |
| 15834 | `5 per week` | `5 per week` | yes | yes | `{'5 per week': 4}` |  |
| 2748 | `1 per month` | `1 per month` | yes | yes | `{'1 per month': 4}` |  |
| 4368 | `5 per 2 month` | `5 per 2 month` | yes | yes | `{'5 per 2 month': 4}` | final_label_repaired: 'multiple per month' -> '5 per 2 month'; final_label_repaired: '5 per year' -> '5 per 2 month'; final_label_repaired: '5 per year' -> '5 per 2 month'; final_label_repaired: 'multiple per month' -> '5 per 2 month' |
| 5921 | `1 per 6 to 8 week` | `1 per 6 to 8 week` | yes | yes | `{'1 per 6 to 8 week': 4}` | final_label_repaired: '1 per 6 to 8 weeks' -> '1 per 6 to 8 week'; final_label_repaired: '1 per 6 to 8 weeks' -> '1 per 6 to 8 week'; final_label_repaired: '1 per 6 to 8 weeks' -> '1 per 6 to 8 week'; final_label_repaired: '1 per 6 to 8 weeks' -> '1 per 6 to 8 week' |
| 6889 | `multiple per week` | `multiple per week` | yes | yes | `{'multiple per week': 4}` | final_label_repaired: 'several per week generalised and once every 2 to 3 weeks focal' -> 'multiple per week'; final_label_repaired: 'several per week generalised myoclonic jerks, 3 per 6 months generalised tonic–clonic, 1 per 2–3 weeks focal seizures' -> 'multiple per week'; final_label_repaired: 'several per week generalised myoclonic jerks, 3 per 6 months generalised tonic–clonic, 1 per 2–3 weeks focal seizures' -> 'multiple per week' |
| 10386 | `1 cluster per week, 2 to 3 per cluster` | `1 cluster per week, 2 to 3 per cluster` | yes | yes | `{'1 cluster per week, 2 to 3 per cluster': 4}` | final_label_repaired: 'weekly' -> '1 cluster per week, 2 to 3 per cluster'; final_label_repaired: 'weekly' -> '1 cluster per week, 2 to 3 per cluster'; final_label_repaired: 'weekly' -> '1 cluster per week, 2 to 3 per cluster'; final_label_repaired: 'weekly' -> '1 cluster per week, 2 to 3 per cluster' |
| 11216 | `seizure free for 4 month` | `seizure free for 4 month` | no | no | `{'seizure free for 4 month': 4}` | final_label_repaired: 'seizure free 4 months' -> 'seizure free for 4 month'; final_label_repaired: 'seizure free 4 months' -> 'seizure free for 4 month'; final_label_repaired: 'seizure free 4 months' -> 'seizure free for 4 month'; final_label_repaired: 'seizure free 4 months' -> 'seizure free for 4 month' |
