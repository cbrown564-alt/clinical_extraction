# Gan 2026 Clean Attribution Format50 V0

Date: 2026-06-01

This is a validation-development no-call replay over saved v0.5 raw model outputs. It is not a final holdout or benchmark result.

## Condition

- Branch: `gan2026_clean_attribution_format50_v0`
- Claim type: `diagnostic_probe` with an `llm_first` attribution baseline
- Split: `validation`, `gan2026_split_v1`, first 50 rows
- Raw-output source: `experiments/gan2026_llm_structured_validation750_gpt41mini_v05_completion_2026-06-01.jsonl`
- Strict-format JSONL: `experiments/gan2026_clean_attribution_format50_v0_2026-06-01.jsonl`
- JSON summary: `experiments/gan2026_clean_attribution_format50_v0_2026-06-01.json`
- Allowed repair: strict format-preserving benchmark normalization only
- Disallowed repair: selected-evidence repair, monthly diary arithmetic, clinical-selection overrides, semantic fallback, no-reference/seizure-free conversion, and cluster cadence conversion

## Required Diagnostic Summary

| Condition | Purist | Pragmatic | Parse/schema/label failures | Cluster-only failures | Exact selected evidence |
| --- | ---: | ---: | ---: | ---: | ---: |
| Raw model selection | 0.6800 (34 / 50) | 0.7200 (36 / 50) | 10 | 2 | 50 / 50 |
| Strict format-preserving | 0.8200 (41 / 50) | 0.8600 (43 / 50) | 3 | 2 | 50 / 50 |

## Strict-Format Repair Impact

- Rows changed by strict-format repair: 17
- Raw-wrong to strict-format-correct improvements: 7
- Raw-correct to strict-format-wrong regressions: 0

| Row | Raw label | Strict label | Gold | Raw Purist | Strict Purist | Repair notes |
| ---: | --- | --- | --- | --- | --- | --- |
| 10 | up to 4 per day | 4 per day | 4 per day | no | yes | final_label_repaired: 'up to 4 per day' -> '4 per day' |
| 40 | ≤ 4 per week | 4 per week | 4 per week | no | yes | final_label_repaired: '≤ 4 per week' -> '4 per week' |
| 79 | ≤ 6 to 7 per year | 6 to 7 per year | 6 to 7 per year | no | yes | final_label_repaired: '≤ 6 to 7 per year' -> '6 to 7 per year' |
| 156 | 1 per 6 days | 1 per 6 day | 1 per 6 day | yes | yes | final_label_repaired: '1 per 6 days' -> '1 per 6 day' |
| 182 | 1 per 2 days | 1 per 2 day | 1 per 2 day | yes | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 190 | 1 cluster per 4 weeks | 1 cluster per 4 week | 1 per 4 week | no | no | final_label_repaired: '1 cluster per 4 weeks' -> '1 cluster per 4 week' |
| 218 | 1 per 3 weeks | 1 per 3 week | 1 per 3 week | yes | yes | final_label_repaired: '1 per 3 weeks' -> '1 per 3 week' |
| 243 | 1 per 4 months | 1 per 4 month | 1 per 4 month | yes | yes | final_label_repaired: '1 per 4 months' -> '1 per 4 month' |
| 409 | 1 per month or less | 1 per month | 1 per month | no | yes | final_label_repaired: '1 per month or less' -> '1 per month' |
| 531 | 12 to 30 per quarter | 12 to 30 per 3 month | 12 to 30 per 3 month | no | yes | final_label_repaired: '12 to 30 per quarter' -> '12 to 30 per 3 month' |
| 598 | 1 per 8 months | 1 per 8 month | 1 per 8 month | yes | yes | final_label_repaired: '1 per 8 months' -> '1 per 8 month' |
| 659 | 2 per 4 days | 2 per 4 day | 2 per 4 day | yes | yes | final_label_repaired: '2 per 4 days' -> '2 per 4 day' |
| 678 | 2 per 4 months | 2 per 4 month | 2 per 4 month | yes | yes | final_label_repaired: '2 per 4 months' -> '2 per 4 month' |
| 891 | 1 every other day | 1 per 2 day | 1 per 2 day | no | yes | final_label_repaired: '1 every other day' -> '1 per 2 day' |
| 899 | 1 per 2 weeks | 1 per 2 week | 1 per 2 week | yes | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 978 | 1 every 2 months | 1 per 2 month | 1 per 2 month | no | yes | final_label_repaired: '1 every 2 months' -> '1 per 2 month' |
| 1165 | 5 to 7 per 3 weeks | 5 to 7 per 3 week | 5 to 7 per 3 week | yes | yes | final_label_repaired: '5 to 7 per 3 weeks' -> '5 to 7 per 3 week' |

## Parse And Cluster Failures

| Row | Final | Gold | Cluster-only | Errors |
| ---: | --- | --- | --- | --- |
| 187 | 1 cluster per week | 1 per 7 to 9 day | yes | unscorable_final_label: Unparsable cluster label: '1 cluster per week' |
| 190 | 1 cluster per 4 week | 1 per 4 week | yes | unscorable_final_label: Unparsable cluster label: '1 cluster per 4 week' |
| 744 | most weekdays | multiple per week | no | unscorable_final_label: Unparsable label (raw: 'most weekdays' / normalized: 'most weekdays') |

## Row Outcomes

| Row | Raw final | Strict final | Gold | Raw Purist | Strict Purist | Notes |
| ---: | --- | --- | --- | --- | --- | --- |
| 10 | up to 4 per day | 4 per day | 4 per day | no | yes | final_label_repaired: 'up to 4 per day' -> '4 per day' |
| 40 | ≤ 4 per week | 4 per week | 4 per week | no | yes | final_label_repaired: '≤ 4 per week' -> '4 per week' |
| 79 | ≤ 6 to 7 per year | 6 to 7 per year | 6 to 7 per year | no | yes | final_label_repaired: '≤ 6 to 7 per year' -> '6 to 7 per year' |
| 103 | 2 to 4 per year | 2 to 4 per year | 2 to 4 per year | yes | yes |  |
| 128 | 17 per month | 17 per month | 17 per month | yes | yes |  |
| 156 | 1 per 6 days | 1 per 6 day | 1 per 6 day | yes | yes | final_label_repaired: '1 per 6 days' -> '1 per 6 day' |
| 180 | 1 per week | 1 per week | 1 per 7 day | yes | yes |  |
| 182 | 1 per 2 days | 1 per 2 day | 1 per 2 day | yes | yes | final_label_repaired: '1 per 2 days' -> '1 per 2 day' |
| 187 | 1 cluster per week | 1 cluster per week | 1 per 7 to 9 day | no | no | unscorable_final_label: Unparsable cluster label: '1 cluster per week' |
| 190 | 1 cluster per 4 weeks | 1 cluster per 4 week | 1 per 4 week | no | no | final_label_repaired: '1 cluster per 4 weeks' -> '1 cluster per 4 week'; unscorable_final_label: Unparsable cluster label: '1 cluster per 4 week' |
| 198 | 1 per month | 1 per month | 1 per 4 week | yes | yes |  |
| 212 | 1 per month | 1 per month | 1 per 3 to 4 week | no | no |  |
| 218 | 1 per 3 weeks | 1 per 3 week | 1 per 3 week | yes | yes | final_label_repaired: '1 per 3 weeks' -> '1 per 3 week' |
| 243 | 1 per 4 months | 1 per 4 month | 1 per 4 month | yes | yes | final_label_repaired: '1 per 4 months' -> '1 per 4 month' |
| 278 | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 280 | multiple per day | multiple per day | multiple per day | yes | yes |  |
| 338 | multiple per month | multiple per month | multiple per month | yes | yes |  |
| 409 | 1 per month or less | 1 per month | 1 per month | no | yes | final_label_repaired: '1 per month or less' -> '1 per month' |
| 419 | 2 per year | 2 per year | 2 per year | yes | yes |  |
| 446 | 2 per week | 2 per week | 2 per week | yes | yes |  |
| 466 | 21 to 28 per month | 21 to 28 per month | 21 to 28 per month | yes | yes |  |
| 467 | 9 per month | 9 per month | 9 per month | yes | yes |  |
| 531 | 12 to 30 per quarter | 12 to 30 per 3 month | 12 to 30 per 3 month | no | yes | final_label_repaired: '12 to 30 per quarter' -> '12 to 30 per 3 month' |
| 598 | 1 per 8 months | 1 per 8 month | 1 per 8 month | yes | yes | final_label_repaired: '1 per 8 months' -> '1 per 8 month' |
| 659 | 2 per 4 days | 2 per 4 day | 2 per 4 day | yes | yes | final_label_repaired: '2 per 4 days' -> '2 per 4 day' |
| 665 | 2 per month | 2 per month | 2 per 2 week | no | no |  |
| 678 | 2 per 4 months | 2 per 4 month | 2 per 4 month | yes | yes | final_label_repaired: '2 per 4 months' -> '2 per 4 month' |
| 694 | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 704 | 2 per month | 2 per month | 2 per month | yes | yes |  |
| 725 | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 731 | 1 per day | 1 per day | 1 per day | yes | yes |  |
| 743 | multiple per week | multiple per week | multiple per week | yes | yes |  |
| 744 | most weekdays | most weekdays | multiple per week | no | no | unscorable_final_label: Unparsable label (raw: 'most weekdays' / normalized: 'most weekdays') |
| 763 | 1 per week | 1 per week | 1 per week | yes | yes |  |
| 790 | 1 per week | 1 per week | 1 per 7 to 10 day | no | no |  |
| 816 | 1 per month | 1 per month | 1 per month | yes | yes |  |
| 849 | 1 per year | 1 per year | 1 per year | yes | yes |  |
| 854 | 1 per year | 1 per year | 1 per year | yes | yes |  |
| 869 | multiple per month | multiple per month | multiple per month | yes | yes |  |
| 891 | 1 every other day | 1 per 2 day | 1 per 2 day | no | yes | final_label_repaired: '1 every other day' -> '1 per 2 day' |
| 899 | 1 per 2 weeks | 1 per 2 week | 1 per 2 week | yes | yes | final_label_repaired: '1 per 2 weeks' -> '1 per 2 week' |
| 959 | 2 per month | 2 per month | 1 per 2 month | no | no |  |
| 960 | 2 to 3 per month | 2 to 3 per month | 1 per 2 month | no | no |  |
| 978 | 1 every 2 months | 1 per 2 month | 1 per 2 month | no | yes | final_label_repaired: '1 every 2 months' -> '1 per 2 month' |
| 987 | 2 per month | 2 per month | 1 per 2 month | no | no |  |
| 1030 | 1 to 3 per month | 1 to 3 per month | 1 to 3 per month | yes | yes |  |
| 1046 | 3 to 5 per month | 3 to 5 per month | 3 to 5 per month | yes | yes |  |
| 1070 | 3 to 4 per week | 3 to 4 per week | 3 to 4 per week | yes | yes |  |
| 1094 | 3 to 5 per week | 3 to 5 per week | 3 to 5 per week | yes | yes |  |
| 1165 | 5 to 7 per 3 weeks | 5 to 7 per 3 week | 5 to 7 per 3 week | yes | yes | final_label_repaired: '5 to 7 per 3 weeks' -> '5 to 7 per 3 week' |

## Interpretation

The 50-row cleaned attribution condition preserves the 25-row signal but remains below the project threshold as a standalone LLM-first comparator. Strict-format repair improves scorer-compatible surface forms without raw-correct regressions. The remaining strict parse/schema failures are two intentional cluster-only attribution failures plus one unresolved vague-cadence label (`most weekdays`). This completes the diagnostic condition and supports moving the next work to a named architecture family rather than escalating this branch solely for metric chasing.
