# Gan 2026 Selective Verifier Prompt Design Live Run

Validation-development prompt-design comparison over the frozen 42-row selective-verifier surface. This does not authorize locked-test inspection, whole-pipeline promotion, or benchmark-comparable claims.

## Decision

Promote the stronger `binary_quote_highest_answer_selector` verifier design for integration into the multi-component architecture. On this frozen 42-row validation-development surface it recovered 7 W->C rows, introduced 1 C->W row (`7168`), and routed 10 routing-correct rows to review. This is sufficient for the verifier prompt-design phase; reassess net impact after integration on the full validation set.

## Artifacts

- Row JSONL: `experiments/gan2026_selective_verifier_binary_quote_highest_strongprompt_live_gpt41mini_2026-06-04.jsonl`
- Summary JSON: `experiments/gan2026_selective_verifier_binary_quote_highest_strongprompt_live_gpt41mini_2026-06-04.json`
- Source predeclaration: `experiments/gan2026_selective_verifier_predeclaration_2026-06-04.jsonl`

## Metrics By Design

### `binary_quote_highest_answer_selector`

| Metric | Value |
| --- | ---: |
| row count | 42 |
| call ok rows | 42 |
| parse ok rows | 42 |
| parse error rows | 0 |
| all evidence quotes exact rows | 40 |
| decision changed rows | 34 |
| changed scorable rows | 21 |
| changed decision precision | 0.619 |
| w to c vs routing rows | 7 |
| c to w vs routing rows | 1 |
| c to review vs routing rows | 10 |
| w to review vs routing rows | 3 |
| unchanged rows | 8 |

Action counts:

- `1 cluster per 2 week, 3 per cluster`: 1
- `1 cluster per 4 to 5 week, multiple per cluster`: 1
- `1 cluster per 5 day, 2 to 4 per cluster`: 1
- `1 cluster per 6 to 8 week, multiple per cluster`: 1
- `1 cluster per month, 3 to 6 per cluster`: 1
- `1 cluster per year, 2 per cluster`: 1
- `1 per 4 week`: 1
- `1 per month`: 1
- `1 to 2 cluster per month, 4 per cluster`: 1
- `2 per year`: 1
- `2 to 3 per year`: 1
- `3 per 6 month`: 1
- `9 per 4 week`: 1
- `human_review`: 8
- `multiple per day`: 2
- `multiple per month`: 1
- `multiple per week`: 1
- `unknown`: 14
- `unknown, 2 per cluster`: 1
- `unknown, 3 per cluster`: 1
- `unknown, 4 to 6 per cluster`: 1

Delta counts:

- `C_to_C_changed`: 1
- `C_to_W`: 1
- `C_to_review`: 10
- `W_to_C`: 7
- `W_to_W_changed`: 12
- `W_to_review`: 3
- `unchanged`: 8

C->W rows: 7168

## Changed Rows

| Design | Row | Action | Label | Delta | Quotes exact |
| --- | ---: | --- | --- | --- | --- |
| `binary_quote_highest_answer_selector` | 190 | 1 per 4 week | 1 per 4 week | W_to_C | True |
| `binary_quote_highest_answer_selector` | 338 | multiple per month | multiple per month | C_to_C_changed | True |
| `binary_quote_highest_answer_selector` | 743 | multiple per day | multiple per day | W_to_W_changed | True |
| `binary_quote_highest_answer_selector` | 744 | multiple per week | multiple per week | W_to_W_changed | True |
| `binary_quote_highest_answer_selector` | 869 | unknown | unknown | W_to_W_changed | True |
| `binary_quote_highest_answer_selector` | 959 | unknown, 2 per cluster | unknown, 2 per cluster | W_to_W_changed | True |
| `binary_quote_highest_answer_selector` | 1363 | unknown, 3 per cluster | unknown, 3 per cluster | W_to_W_changed | True |
| `binary_quote_highest_answer_selector` | 1694 | 1 cluster per 2 week, 3 per cluster | 1 cluster per 2 week, 3 per cluster | W_to_C | False |
| `binary_quote_highest_answer_selector` | 2080 | human_review | None | C_to_review | True |
| `binary_quote_highest_answer_selector` | 3528 | unknown | None | C_to_review | True |
| `binary_quote_highest_answer_selector` | 4368 | unknown | unknown | W_to_W_changed | True |
| `binary_quote_highest_answer_selector` | 5534 | human_review | None | C_to_review | True |
| `binary_quote_highest_answer_selector` | 5921 | 1 cluster per 6 to 8 week, multiple per cluster | 1 cluster per 6 to 8 week, multiple per cluster | W_to_W_changed | True |
| `binary_quote_highest_answer_selector` | 6077 | human_review | None | C_to_review | True |
| `binary_quote_highest_answer_selector` | 6153 | 9 per 4 week | 9 per 4 week | W_to_C | True |
| `binary_quote_highest_answer_selector` | 6209 | human_review | None | C_to_review | True |
| `binary_quote_highest_answer_selector` | 6571 | human_review | None | C_to_review | True |
| `binary_quote_highest_answer_selector` | 6889 | 3 per 6 month | None | C_to_review | True |
| `binary_quote_highest_answer_selector` | 6987 | human_review | None | C_to_review | True |
| `binary_quote_highest_answer_selector` | 7168 | 1 cluster per year, 2 per cluster | 1 cluster per year, 2 per cluster | C_to_W | True |
| `binary_quote_highest_answer_selector` | 7615 | 1 cluster per month, 3 to 6 per cluster | 1 cluster per month, 3 to 6 per cluster | W_to_C | True |
| `binary_quote_highest_answer_selector` | 9943 | 1 cluster per 4 to 5 week, multiple per cluster | 1 cluster per 4 to 5 week, multiple per cluster | W_to_C | True |
| `binary_quote_highest_answer_selector` | 10618 | unknown, 4 to 6 per cluster | unknown, 4 to 6 per cluster | W_to_W_changed | True |
| `binary_quote_highest_answer_selector` | 10677 | 1 per month | 1 per month | W_to_W_changed | True |
| `binary_quote_highest_answer_selector` | 10996 | 1 to 2 cluster per month, 4 per cluster | 1 to 2 cluster per month, 4 per cluster | W_to_C | True |
| `binary_quote_highest_answer_selector` | 11259 | unknown | unknown | W_to_W_changed | True |
| `binary_quote_highest_answer_selector` | 12438 | 2 to 3 per year | None | W_to_review | True |
| `binary_quote_highest_answer_selector` | 12460 | 2 per year | None | W_to_review | True |
| `binary_quote_highest_answer_selector` | 13209 | unknown | unknown | W_to_W_changed | True |
| `binary_quote_highest_answer_selector` | 13843 | human_review | None | W_to_review | True |
| `binary_quote_highest_answer_selector` | 15168 | unknown | None | C_to_review | True |
| `binary_quote_highest_answer_selector` | 15193 | human_review | None | C_to_review | False |
| `binary_quote_highest_answer_selector` | 15593 | 1 cluster per 5 day, 2 to 4 per cluster | 1 cluster per 5 day, 2 to 4 per cluster | W_to_C | True |
| `binary_quote_highest_answer_selector` | 15672 | multiple per day | multiple per day | W_to_W_changed | True |
