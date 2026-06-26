# Gan 2026 Agentic Validation25 Format-Repair Analysis

Date: 2026-06-12

## Scope

Validation-development analysis of:

`experiments/gan2026_agentic_matched_budget_validation25_single_agent_live_2026-06-12.jsonl`

No model calls were made for the replay in this note. This is a no-call
diagnostic reparse of saved validation raw outputs. It is not holdout evidence
and makes no benchmark claim.

## Finding

The saved run had `125` non-blocking direct-label repair notes across `150`
decision records (`51` unique transitions). Most were benign format cleanup:
upper-bound markers, hyphenated ranges, quarter windows, plural units, interval
phrasing, and word-number forms.

The actionable family was underscore-separated model labels. Labels such as
`multiple_per_day`, `multiple_per_week`, and `twice_per_year` fell through the
benchmark fallback path and could become `no seizure frequency reference`,
despite the model's own `answer_kind="frequency"` and frequency-bearing
evidence.

## Flagged Rows

| Row | Original condition finals | After no-call reparse |
| ---: | --- | --- |
| 10 | `single_agent_tools`: `no seizure frequency reference`; `single_greedy`: `4 per day`; `single_self_consistency_temperature`: `4 per day` | all three active single-agent conditions: `4 per day` |
| 278 | `single_agent_tools`: `multiple per week`; `single_greedy`: `no seizure frequency reference`; `single_self_consistency_temperature`: `multiple per week` | all three active single-agent conditions: `multiple per week` |
| 419 | `single_agent_tools`: `2 per year`; `single_greedy`: `no seizure frequency reference`; `single_self_consistency_temperature`: `2 per year` | all three active single-agent conditions: `2 per year` |

## Repair Decision

- Added `benchmark_repair.underscore_label_separators` to the full and
  format-preserving benchmark repair ladders.
- Added bare selected-evidence rate parsing for exact selected spans such as
  `four per day`, after word-number normalization.
- Tightened the agentic prompt contract to ask for space-separated labels and
  bumped `PROMPT_VERSION` to `gan2026_agentic_matched_budget_prompt_v1`.

## Diagnostic Replay Result

Reparsing the saved validation25 raw outputs with the updated parser changes
the preferred row-final diagnostic surface from `24/25` to `25/25` Purist and
from `24/25` to `25/25` Pragmatic.

This replay is parser/contract evidence only. The next live action is to rerun
the validation25 single-agent smoke under prompt v1 before any matched
multi-agent call spend.
