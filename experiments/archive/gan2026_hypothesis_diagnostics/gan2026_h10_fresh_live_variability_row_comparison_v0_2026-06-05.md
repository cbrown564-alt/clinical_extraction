# H10 Fresh Live Variability Row Comparison

Validation-development row comparison. No clinical note text is included. No locked-test rows or failures were inspected.

## Summary

- Matched rows: 20.
- Raw LLM-candidate JSON string changed: 19/20.
- Raw adjudicator JSON string changed: 19/20.
- These raw-string changes include rationale, evidence span, selected source
  ids, optional fields, and formatting; they are not necessarily clinical-label
  changes.
- LLM candidate label changed: 3/20.
- Raw adjudicator label changed: 1/20.
- Final hybrid-with-adapters label changed: 0/20.
- Raw adjudicator Purist status changed: 1/20.

## Row-Level Label Changes

| Row | Gold | Raw cand changed | Raw adj changed | LLM candidate A -> B | Raw adj A -> B | Final A -> B | Purist change? |
| ---: | --- | ---: | ---: | --- | --- | --- | ---: |
| 10 | 4 per day | Y | Y | frequent -> frequency | 4 per day -> 4 per day | 4 per day -> 4 per day |  |
| 40 | 4 per week | Y | Y | four or fewer per week -> four or fewer per week | 4 per week -> 4 per week | 4 per week -> 4 per week |  |
| 79 | 6 to 7 per year | Y | Y | ≤6-7 per year -> ≤6-7 per year | 6 to 7 per year -> 6 to 7 per year | 6 to 7 per year -> 6 to 7 per year |  |
| 103 | 2 to 4 per year | Y | Y | two to four per year -> two to four per year | 2 to 4 per year -> 2 to 4 per year | 2 to 4 per year -> 2 to 4 per year |  |
| 128 | 17 per month |  |  | 17 per month -> 17 per month | 17 per month -> 17 per month | 17 per month -> 17 per month |  |
| 156 | 1 per 6 day | Y | Y | every 6 days -> every 6 days | 1 per 6 day -> 1 per 6 day | 1 per 6 day -> 1 per 6 day |  |
| 180 | 1 per 7 day | Y | Y | seizures every 7 days -> seizures every 7 days | 1 per 7 day -> 1 per 7 day | 1 per 7 day -> 1 per 7 day |  |
| 182 | 1 per 2 day | Y | Y | every 2 days -> every 2 days | 1 per 2 day -> 1 per 2 day | 1 per 2 day -> 1 per 2 day |  |
| 187 | 1 per 7 to 9 day | Y | Y | cluster every 7-9 days -> cluster every 7-9 days | 1 per 7 to 9 day -> 1 per 7 to 9 day | 1 per 7 to 9 day -> 1 per 7 to 9 day |  |
| 190 | 1 per 4 week | Y | Y | absence cluster every 4 weeks -> absence cluster every 4 weeks | unknown -> unknown | 1 per 4 week -> 1 per 4 week |  |
| 198 | 1 per 4 week | Y | Y | every 4 weeks -> every 4 weeks | 1 per 4 week -> 1 per 4 week | 1 per 4 week -> 1 per 4 week |  |
| 212 | 1 per 3 to 4 week | Y | Y | 3-4 weeks -> 3-4 weeks | 1 per 3 to 4 week -> 1 per 3 to 4 week | 1 per 3 to 4 week -> 1 per 3 to 4 week |  |
| 218 | 1 per 3 week | Y | Y | seizures every 3 weeks -> seizures every 3 weeks | 1 per 3 week -> 1 per 3 week | 1 per 3 week -> 1 per 3 week |  |
| 243 | 1 per 4 month | Y | Y | every four months -> every four months | 1 per 4 month -> 1 per 4 month | 1 per 4 month -> 1 per 4 month |  |
| 278 | multiple per week | Y | Y | multiple times per week -> multiple times per week | multiple per week -> multiple per week | multiple per week -> multiple per week |  |
| 280 | multiple per day | Y | Y | multiple seizures per day -> multiple seizures in past day | multiple per day -> multiple per day | multiple per day -> multiple per day |  |
| 338 | multiple per month | Y | Y | many -> many | no seizure frequency reference -> no seizure frequency reference | no seizure frequency reference -> no seizure frequency reference |  |
| 409 | 1 per month | Y | Y | monthly -> ≤ once per month | 1 per month -> multiple per month | 1 per month -> 1 per month | Y |
| 419 | 2 per year | Y | Y | approximately twice per year -> approximately twice per year | 2 per year -> 2 per year | 2 per year -> 2 per year |  |
| 446 | 2 per week | Y | Y | twice per week or less -> twice per week or less | 2 per week -> 2 per week | 2 per week -> 2 per week |  |

## Rows With Label Differences

### Row 10 / gold `4 per day`

- Raw candidate changed: `True`; raw adjudicator changed: `True`.
- LLM candidate selection A: `frequent` / B: `frequency`.
- Adjudicator selection A: `4 per day` / B: `4 per day`.
- `llm_candidate_selector_raw`: `frequent` correct=None -> `frequency` correct=None.

### Row 280 / gold `multiple per day`

- Raw candidate changed: `True`; raw adjudicator changed: `True`.
- LLM candidate selection A: `multiple seizures per day` / B: `multiple seizures in past day`.
- Adjudicator selection A: `multiple per day` / B: `multiple per day`.
- `llm_candidate_selector_raw`: `multiple seizures per day` correct=None -> `multiple seizures in past day` correct=None.

### Row 409 / gold `1 per month`

- Raw candidate changed: `True`; raw adjudicator changed: `True`.
- LLM candidate selection A: `monthly` / B: `≤ once per month`.
- Adjudicator selection A: `1 per month` / B: `multiple per month`.
- `llm_candidate_selector_raw`: `monthly` correct=None -> `≤ once per month` correct=None.
- `hybrid_adjudicator_raw`: `1 per month` correct=True -> `multiple per month` correct=False.
