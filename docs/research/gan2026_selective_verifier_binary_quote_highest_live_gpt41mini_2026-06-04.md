# Gan 2026 Selective Verifier Prompt Design Live Run

Validation-development prompt-design comparison over the frozen 42-row selective-verifier surface. This does not authorize locked-test inspection, whole-pipeline promotion, or benchmark-comparable claims.

## Decision

Keep prompt designs diagnostic: at least one design introduced C->W regressions versus routing ({'binary_quote_highest_answer_selector': 3}).

## Artifacts

- Row JSONL: `experiments/gan2026_selective_verifier_binary_quote_highest_live_gpt41mini_2026-06-04.jsonl`
- Summary JSON: `experiments/gan2026_selective_verifier_binary_quote_highest_live_gpt41mini_2026-06-04.json`
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
| decision changed rows | 29 |
| changed scorable rows | 20 |
| changed decision precision | 0.650 |
| w to c vs routing rows | 7 |
| c to w vs routing rows | 3 |
| c to review vs routing rows | 7 |
| w to review vs routing rows | 2 |
| unchanged rows | 13 |

Action counts:

- `0 per 9 to 10 month`: 1
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
- `multiple per day`: 2
- `multiple per month`: 1
- `multiple per week`: 1
- `unknown`: 22
- `unknown, 3 per cluster`: 1
- `unknown, 4 to 6 per cluster`: 1

Delta counts:

- `C_to_C_changed`: 1
- `C_to_W`: 3
- `C_to_review`: 7
- `W_to_C`: 7
- `W_to_W_changed`: 9
- `W_to_review`: 2
- `unchanged`: 13

C->W rows: 6889, 7168, 15193

## Changed Rows

| Design | Row | Action | Label | Delta | Quotes exact |
| --- | ---: | --- | --- | --- | --- |
| `binary_quote_highest_answer_selector` | 190 | 1 per 4 week | 1 per 4 week | W_to_C | True |
| `binary_quote_highest_answer_selector` | 338 | multiple per month | multiple per month | C_to_C_changed | True |
| `binary_quote_highest_answer_selector` | 743 | multiple per day | multiple per day | W_to_W_changed | True |
| `binary_quote_highest_answer_selector` | 744 | multiple per week | multiple per week | W_to_W_changed | True |
| `binary_quote_highest_answer_selector` | 869 | unknown | unknown | W_to_W_changed | True |
| `binary_quote_highest_answer_selector` | 1363 | unknown, 3 per cluster | unknown, 3 per cluster | W_to_W_changed | True |
| `binary_quote_highest_answer_selector` | 1694 | 1 cluster per 2 week, 3 per cluster | 1 cluster per 2 week, 3 per cluster | W_to_C | True |
| `binary_quote_highest_answer_selector` | 3528 | unknown | None | C_to_review | True |
| `binary_quote_highest_answer_selector` | 5921 | 1 cluster per 6 to 8 week, multiple per cluster | 1 cluster per 6 to 8 week, multiple per cluster | W_to_W_changed | True |
| `binary_quote_highest_answer_selector` | 6077 | unknown | None | C_to_review | True |
| `binary_quote_highest_answer_selector` | 6153 | 9 per 4 week | 9 per 4 week | W_to_C | True |
| `binary_quote_highest_answer_selector` | 6321 | unknown | None | C_to_review | False |
| `binary_quote_highest_answer_selector` | 6571 | unknown | None | C_to_review | True |
| `binary_quote_highest_answer_selector` | 6889 | 3 per 6 month | 3 per 6 month | C_to_W | True |
| `binary_quote_highest_answer_selector` | 6987 | unknown | None | C_to_review | True |
| `binary_quote_highest_answer_selector` | 7168 | 1 cluster per year, 2 per cluster | 1 cluster per year, 2 per cluster | C_to_W | True |
| `binary_quote_highest_answer_selector` | 7615 | 1 cluster per month, 3 to 6 per cluster | 1 cluster per month, 3 to 6 per cluster | W_to_C | True |
| `binary_quote_highest_answer_selector` | 9888 | unknown | None | C_to_review | True |
| `binary_quote_highest_answer_selector` | 9943 | 1 cluster per 4 to 5 week, multiple per cluster | 1 cluster per 4 to 5 week, multiple per cluster | W_to_C | True |
| `binary_quote_highest_answer_selector` | 10618 | unknown, 4 to 6 per cluster | unknown, 4 to 6 per cluster | W_to_W_changed | True |
| `binary_quote_highest_answer_selector` | 10677 | 1 per month | 1 per month | W_to_W_changed | True |
| `binary_quote_highest_answer_selector` | 10996 | 1 to 2 cluster per month, 4 per cluster | 1 to 2 cluster per month, 4 per cluster | W_to_C | True |
| `binary_quote_highest_answer_selector` | 11259 | unknown | unknown | W_to_W_changed | True |
| `binary_quote_highest_answer_selector` | 12438 | 2 to 3 per year | None | W_to_review | True |
| `binary_quote_highest_answer_selector` | 12460 | 2 per year | None | W_to_review | True |
| `binary_quote_highest_answer_selector` | 14076 | unknown | None | C_to_review | True |
| `binary_quote_highest_answer_selector` | 15193 | 0 per 9 to 10 month | 0 per 9 to 10 month | C_to_W | True |
| `binary_quote_highest_answer_selector` | 15593 | 1 cluster per 5 day, 2 to 4 per cluster | 1 cluster per 5 day, 2 to 4 per cluster | W_to_C | True |
| `binary_quote_highest_answer_selector` | 15672 | multiple per day | multiple per day | W_to_W_changed | True |
