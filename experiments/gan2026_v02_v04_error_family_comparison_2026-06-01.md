# Gan 2026 v0.2/v0.4 Error-Family Comparison

Date: 2026-06-01

This is a validation development comparison on `gan2026_split_v1`. It is not a
final holdout or benchmark result.

## Experiment Unit

Question: compare the v0.2 and v0.4 structured-selector error families before
adding broader selector guidance or promoting any named semantic repair module.

Minimal change: no new model calls and no code change. This compares existing
250-row validation-prefix no-call reparse artifacts:

- `experiments/gan2026_llm_structured_validation250_gpt41mini_v02_reparse_current_2026-06-01.jsonl`
- `experiments/gan2026_llm_structured_validation250_gpt41mini_v04_reparse_current_2026-06-01.jsonl`

Data surface: first 250 rows of the validation split, `gan2026_split_v1`.

Scorer policy: existing Gan-compatible Purist category comparison from the
saved artifacts, with Pragmatic as a side-car.

Attribution caveat: both compared artifacts use the current repair layer and are
therefore repair-heavy hybrid diagnostics, not clean LLM-first completions.

## Summary

| Candidate | Purist | Pragmatic | Exact evidence | Repair notes |
| --- | ---: | ---: | ---: | ---: |
| v0.2 current reparse | 245 / 250 | 246 / 250 | 242 / 250 | 137 |
| v0.4 current reparse | 241 / 250 | 242 / 250 | 242 / 250 | 148 |

v0.4 has no aggregate advantage on this shared prefix. It fixes one v0.2 miss
but introduces five additional Purist misses. The extra guidance appears useful
for vague quantity wording, but it increases over-selection and repair-trigger
risk on competing-evidence, last-event, perimenstrual, and seizure-free cases.

## Row-Level Delta

| Row | v0.2 result | v0.4 result | Family | Interpretation |
| ---: | --- | --- | --- | --- |
| 1880 | correct: `8 per 2 month` | wrong: `multiple per week` | competing event over-selection | v0.4 chose a more frequent semiology phrase instead of the aggregate two-month diary total. |
| 1979 | correct: `3 per 2 month` | wrong: `multiple per month` | competing event over-selection | v0.4 incorporated suspected/smartwatch events rather than the countable selected total. |
| 2114 | wrong: `2 to 3 per month` | correct: `multiple per month` | vague quantity wording | v0.4 handled `several ... in the past month` better than v0.2. |
| 2992 | correct: `seizure free for 7 month` | wrong: `no seizure frequency reference` | last-event versus seizure-free state | v0.4 selected the dated last event instead of preserving the seizure-free interval. |
| 3469 | correct: `unknown` | wrong: `2 per 6 month` | perimenstrual semantic repair | v0.4 output passed through a repair path that converted an unknown perimenstrual cluster into a numeric rate. |
| 5406 | correct: `seizure free for multiple year` | wrong: `unknown` | seizure-free/no-epileptic-event state | v0.2's correctness came from semantic repair; v0.4 exposes the unresolved raw-selection weakness. |

Rows wrong in both candidates:

| Row | Gold | v0.2 | v0.4 | Family |
| ---: | --- | --- | --- | --- |
| 3534 | `unknown` | `seizure free for 7 month` | `seizure free for 7 month` | rescue-medication negation mistaken for seizure-free duration |
| 4337 | `3 per 3 month` | `3 per 6 month` | `3 per 7 month` | diary-date window arithmetic |
| 4624 | `1 per 3 to 4 day` | `unknown` | `unknown` | interval/cadence phrasing treated as cluster ambiguity |
| 5534 | `1 per multiple month` | `1 per 2 week` | `1 per 2 week` | single recent event over-normalized into fortnightly recurrence |

## Decision

Do not broaden v0.4 selector guidance as the next architecture step. It improves
a narrow vague-quantity family but worsens more clinically important selection
families on the same surface.

The next focused implementation target should be table-backed clean
scorer-facing policy only, with tests, and it should stay separate from named
semantic modules. The row families that should remain named ablated modules are:

- competing-evidence/aggregate diary selection
- last-event plus seizure-free interval reasoning
- perimenstrual and other temporal-window reconstruction
- seizure-free/no-epileptic-event state conversion
- diary-date arithmetic
- single-event-to-recurrence conversion

The clean policy slice should be allowed only where the direct-citation row
tables already show an explicit and consistent Gan scorer-facing convention.
Anything that changes semantic state should remain outside the clean LLM-first
attribution baseline.
