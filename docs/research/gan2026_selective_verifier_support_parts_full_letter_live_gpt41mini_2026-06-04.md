# Gan 2026 Selective Verifier Prompt Design Live Run

Validation-development prompt-design comparison over the frozen 42-row selective-verifier surface. This does not authorize locked-test inspection, whole-pipeline promotion, or benchmark-comparable claims.

## Decision

Keep prompt designs diagnostic: at least one design introduced C->W regressions versus routing ({'support_parts_full_letter': 1}).

Reparse note: No-call bookkeeping reparse of saved raw outputs after call-error parse accounting fix.

## Artifacts

- Row JSONL: `experiments/gan2026_selective_verifier_support_parts_full_letter_live_gpt41mini_2026-06-04.jsonl`
- Summary JSON: `experiments/gan2026_selective_verifier_support_parts_full_letter_live_gpt41mini_2026-06-04.json`
- Source predeclaration: `experiments/gan2026_selective_verifier_predeclaration_2026-06-04.jsonl`

## Metrics By Design

### `support_parts_full_letter`

| Metric | Value |
| --- | ---: |
| row count | 42 |
| call ok rows | 41 |
| parse ok rows | 41 |
| parse error rows | 1 |
| all evidence quotes exact rows | 41 |
| decision changed rows | 24 |
| changed scorable rows | 13 |
| changed decision precision | 0.615 |
| w to c vs routing rows | 5 |
| c to w vs routing rows | 1 |
| c to review vs routing rows | 4 |
| w to review vs routing rows | 6 |
| unchanged rows | 18 |

Action counts:

- `needs_review`: 12
- `parse_error`: 1
- `use_proposed_answer`: 10
- `use_unknown`: 19

Delta counts:

- `C_to_C_changed`: 1
- `C_to_W`: 1
- `C_to_review`: 4
- `W_to_C`: 5
- `W_to_W_changed`: 7
- `W_to_review`: 6
- `unchanged`: 18

C->W rows: 6889

## Changed Rows

| Design | Row | Action | Label | Delta | Quotes exact |
| --- | ---: | --- | --- | --- | --- |
| `support_parts_full_letter` | 190 | use_proposed_answer | 1 per 4 week | W_to_C | True |
| `support_parts_full_letter` | 338 | use_proposed_answer | multiple per month | C_to_C_changed | True |
| `support_parts_full_letter` | 744 | parse_error | None | W_to_W_changed | False |
| `support_parts_full_letter` | 869 | use_unknown | unknown | W_to_W_changed | True |
| `support_parts_full_letter` | 959 | needs_review | None | W_to_review | True |
| `support_parts_full_letter` | 1363 | needs_review | None | W_to_review | True |
| `support_parts_full_letter` | 1694 | needs_review | None | W_to_review | True |
| `support_parts_full_letter` | 4368 | use_unknown | unknown | W_to_W_changed | True |
| `support_parts_full_letter` | 5921 | needs_review | None | W_to_review | True |
| `support_parts_full_letter` | 6153 | use_proposed_answer | 9 per 4 week | W_to_C | True |
| `support_parts_full_letter` | 6209 | needs_review | None | C_to_review | True |
| `support_parts_full_letter` | 6321 | needs_review | None | C_to_review | True |
| `support_parts_full_letter` | 6889 | use_proposed_answer | 3 per 6 month | C_to_W | True |
| `support_parts_full_letter` | 7168 | needs_review | None | C_to_review | True |
| `support_parts_full_letter` | 7615 | use_proposed_answer | 1 cluster per month, 3 to 6 per cluster | W_to_C | True |
| `support_parts_full_letter` | 10677 | use_proposed_answer | 1 per month | W_to_W_changed | True |
| `support_parts_full_letter` | 10996 | use_proposed_answer | 1 to 2 cluster per month, 4 per cluster | W_to_C | True |
| `support_parts_full_letter` | 11259 | use_proposed_answer | unknown | W_to_W_changed | True |
| `support_parts_full_letter` | 12438 | needs_review | None | W_to_review | True |
| `support_parts_full_letter` | 12460 | needs_review | None | W_to_review | True |
| `support_parts_full_letter` | 13209 | use_unknown | unknown | W_to_W_changed | True |
| `support_parts_full_letter` | 15193 | needs_review | None | C_to_review | True |
| `support_parts_full_letter` | 15593 | use_proposed_answer | 1 cluster per 5 day, 2 to 4 per cluster | W_to_C | True |
| `support_parts_full_letter` | 15672 | use_proposed_answer | multiple per day | W_to_W_changed | True |
