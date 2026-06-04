# Gan 2026 Selective Verifier Prompt Design Live Run

Validation-development prompt-design comparison over the frozen 42-row selective-verifier surface. This does not authorize locked-test inspection, whole-pipeline promotion, or benchmark-comparable claims.

## Decision

No C->W regressions were observed; designs with W->C changes need row adjudication before any prediction-bearing use ({'support_parts_fact_check': 2, 'veto_first_safety_reviewer': 2}).

Reparse note: No-call reparse of saved raw outputs after accepting one-item action lists.

## Artifacts

- Row JSONL: `experiments/gan2026_selective_verifier_prompt_designs_live_gpt41mini_2026-06-04.jsonl`
- Summary JSON: `experiments/gan2026_selective_verifier_prompt_designs_live_gpt41mini_2026-06-04.json`
- Source predeclaration: `experiments/gan2026_selective_verifier_predeclaration_2026-06-04.jsonl`

## Metrics By Design

### `support_parts_fact_check`

| Metric | Value |
| --- | ---: |
| all evidence quotes exact rows | 41 |
| c to review vs routing rows | 8 |
| c to w vs routing rows | 0 |
| call ok rows | 42 |
| changed decision precision | 0.625 |
| changed scorable rows | 8 |
| decision changed rows | 26 |
| parse error rows | 0 |
| parse ok rows | 42 |
| row count | 42 |
| unchanged rows | 16 |
| w to c vs routing rows | 2 |
| w to review vs routing rows | 10 |

Action counts:

- `needs_review`: 20
- `use_proposed_answer`: 5
- `use_unknown`: 17

Delta counts:

- `C_to_review`: 8
- `W_to_C`: 2
- `W_to_W_changed`: 6
- `W_to_review`: 10
- `unchanged`: 16

C->W rows: 

### `veto_first_safety_reviewer`

| Metric | Value |
| --- | ---: |
| all evidence quotes exact rows | 35 |
| c to review vs routing rows | 8 |
| c to w vs routing rows | 0 |
| call ok rows | 42 |
| changed decision precision | 0.429 |
| changed scorable rows | 7 |
| decision changed rows | 23 |
| parse error rows | 0 |
| parse ok rows | 42 |
| row count | 42 |
| unchanged rows | 19 |
| w to c vs routing rows | 2 |
| w to review vs routing rows | 8 |

Action counts:

- `needs_review`: 20
- `use_proposed_answer`: 6
- `use_unknown`: 16

Delta counts:

- `C_to_review`: 8
- `W_to_C`: 2
- `W_to_W_changed`: 5
- `W_to_review`: 8
- `unchanged`: 19

C->W rows: 

## Changed Rows

| Design | Row | Action | Label | Delta | Quotes exact |
| --- | ---: | --- | --- | --- | --- |
| `veto_first_safety_reviewer` | 190 | needs_review | None | W_to_review | True |
| `support_parts_fact_check` | 190 | needs_review | None | W_to_review | True |
| `veto_first_safety_reviewer` | 338 | needs_review | None | C_to_review | True |
| `support_parts_fact_check` | 338 | needs_review | None | C_to_review | True |
| `support_parts_fact_check` | 743 | use_unknown | unknown | W_to_W_changed | True |
| `veto_first_safety_reviewer` | 869 | use_unknown | unknown | W_to_W_changed | True |
| `support_parts_fact_check` | 869 | use_unknown | unknown | W_to_W_changed | True |
| `veto_first_safety_reviewer` | 959 | needs_review | None | W_to_review | True |
| `veto_first_safety_reviewer` | 1363 | needs_review | None | W_to_review | False |
| `support_parts_fact_check` | 1363 | needs_review | None | W_to_review | True |
| `veto_first_safety_reviewer` | 1694 | needs_review | None | W_to_review | True |
| `support_parts_fact_check` | 1694 | needs_review | None | W_to_review | True |
| `support_parts_fact_check` | 2080 | needs_review | None | C_to_review | True |
| `veto_first_safety_reviewer` | 4368 | use_unknown | unknown | W_to_W_changed | True |
| `support_parts_fact_check` | 4368 | use_unknown | unknown | W_to_W_changed | True |
| `veto_first_safety_reviewer` | 5534 | needs_review | None | C_to_review | True |
| `support_parts_fact_check` | 5534 | needs_review | None | C_to_review | True |
| `support_parts_fact_check` | 5921 | needs_review | None | W_to_review | True |
| `veto_first_safety_reviewer` | 5974 | needs_review | None | C_to_review | True |
| `veto_first_safety_reviewer` | 6131 | needs_review | None | C_to_review | True |
| `veto_first_safety_reviewer` | 6153 | use_proposed_answer | 9 per 4 week | W_to_C | True |
| `support_parts_fact_check` | 6153 | use_proposed_answer | 9 per 4 week | W_to_C | True |
| `veto_first_safety_reviewer` | 6209 | needs_review | None | C_to_review | True |
| `support_parts_fact_check` | 6209 | needs_review | None | C_to_review | True |
| `support_parts_fact_check` | 6321 | needs_review | None | C_to_review | True |
| `veto_first_safety_reviewer` | 6889 | needs_review | None | C_to_review | False |
| `support_parts_fact_check` | 6889 | needs_review | None | C_to_review | True |
| `veto_first_safety_reviewer` | 7168 | needs_review | None | C_to_review | True |
| `support_parts_fact_check` | 7168 | needs_review | None | C_to_review | True |
| `veto_first_safety_reviewer` | 7615 | needs_review | None | W_to_review | False |
| `support_parts_fact_check` | 7615 | use_proposed_answer | 1 cluster per month, 3 to 6 per cluster | W_to_C | True |
| `veto_first_safety_reviewer` | 9943 | needs_review | None | W_to_review | True |
| `support_parts_fact_check` | 9943 | needs_review | None | W_to_review | True |
| `veto_first_safety_reviewer` | 10677 | use_proposed_answer | 1 per month | W_to_W_changed | True |
| `support_parts_fact_check` | 10677 | use_proposed_answer | 1 per month | W_to_W_changed | True |
| `veto_first_safety_reviewer` | 10996 | use_proposed_answer | 1 to 2 cluster per month, 4 per cluster | W_to_C | True |
| `support_parts_fact_check` | 10996 | needs_review | None | W_to_review | True |
| `support_parts_fact_check` | 11259 | use_unknown | unknown | W_to_W_changed | True |
| `support_parts_fact_check` | 12438 | needs_review | None | W_to_review | True |
| `veto_first_safety_reviewer` | 12460 | use_proposed_answer | 2 per year | W_to_W_changed | True |
| `support_parts_fact_check` | 12460 | needs_review | None | W_to_review | True |
| `veto_first_safety_reviewer` | 13209 | use_proposed_answer | unknown | W_to_W_changed | True |
| `support_parts_fact_check` | 13209 | use_unknown | unknown | W_to_W_changed | True |
| `veto_first_safety_reviewer` | 15193 | needs_review | None | C_to_review | True |
| `support_parts_fact_check` | 15193 | needs_review | None | C_to_review | True |
| `veto_first_safety_reviewer` | 15593 | needs_review | None | W_to_review | True |
| `support_parts_fact_check` | 15593 | needs_review | None | W_to_review | True |
| `veto_first_safety_reviewer` | 15672 | needs_review | None | W_to_review | True |
| `support_parts_fact_check` | 15672 | needs_review | None | W_to_review | True |
