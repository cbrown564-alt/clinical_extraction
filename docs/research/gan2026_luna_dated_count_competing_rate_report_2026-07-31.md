# Luna dated-count + competing-rate floor on `validation750`

Date: 2026-07-31  
Status: development answer; absorbed into final Gan LLM-with-rules ruleset  
Protocol: [dated-count protocol](../experiments/gan2026/gan2026_luna_dated_count_competing_rate_protocol_2026-07-31.md)

## Answer

Two narrow deterministic floors recover the dated-count `no_reference`
demotions and the typical-over-YTD competing-rate miss that the projection
floor left open. No-call replay of saved Luna A/B/C raw outputs through
`hybrid_full_stack` yields net Purist gains on all three variants, rescues
named exemplars 14587, 14628, and 2748 on every variant, and lifts the
48-row persistent residual by 10–11 rows. Prompt text and scorers were not
changed.

## What changed

| Module | Change | Portability |
| --- | --- | --- |
| Benchmark repair | `N in/within M months` → `N per M month` | `benchmark_format` |
| Evidence window | accept `within` for single-count-over-window | `seizure_frequency` |
| Dated-sequence repair | mine `note_text` when events lack **two distinct** calendar months | `seizure_frequency` |
| Hybrid repair stack | prefer typical/usual recurring rate over YTD observation total | `seizure_frequency` |

Builds on the projection + anti-regression floor already in the working tree.
The C×14628 miss was a false-positive “two dated mentions” from repeating
June 2015 in one event; distinct-month collapse restores note mining.

## Results (no-call Luna A/B/C replay)

Comparator: original saved A/B/C finals (not post-projection-only).

| Variant | Before | After | Δ | W→C | C→W | Persistent-48 rescued |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A `v0.5` | 646/750 | 661/750 | +15 | 20 | 5 | 10 |
| B `luna_rate` | 656/750 | 668/750 | +12 | 16 | 4 | 10 |
| C `luna_current` | 666/750 | 676/750 | +10 | 16 | 6 | 11 |

Named exemplars after floors (all three variants):

| Row | Gold | Before | After |
| ---: | --- | --- | --- |
| 14587 | `2 per 3 month` | `no seizure frequency reference` | `2 per 3 month` |
| 14628 | `2 per 2 month` | `no seizure frequency reference` | `2 per 2 month` |
| 2748 | `1 per month` | `7 per 10 month` | `1 per month` |
| 1030 / 2459 / 2932 / 5837 / 10097 / 10237 | (projection set) | wrong | correct |

## Mechanism

1. **In-period counts are already rates.** `2 in 3 months` is a legal
   windowed rate; projecting it before the unknown/no-reference sink keeps
   14587 scorable without new clinical selection.
2. **Dated sequences need two months, not two mentions.** When the model
   extracts only the second event’s month, note mining recovers the first
   Month–Year pair (14628).
3. **Typical recurring beats YTD totals.** When the ledger already states a
   usual monthly/weekly rate and selection is a so-far-this-year total,
   prefer the typical rate (2748).

## Regressions

Correct-to-wrong remains small (4–6/variant). Shared patterns:

- dated-sequence projection on gold-`unknown` rows (e.g. 14025, 4771);
- competing-rate / usual-interval preference over gold observation totals
  (16719, 16750);
- seizure-free overwrite on one A row (16084);
- cadence dual-form on gold-`unknown, multiple per cluster` (1317).

Net gain stays positive on every variant. These are development watch items,
not a stop-rule failure.

## Artifacts

- [replay_summary.json](../../experiments/gan2026_luna_dated_count_competing_rate_20260731/replay_summary.json)
- [changed_rows.jsonl](../../experiments/gan2026_luna_dated_count_competing_rate_20260731/changed_rows.jsonl)
- Tests: `tests/test_gan2026_dated_count_competing_rate_floor.py`

## Claim boundary

Development hybrid artifact from no-call replay of saved Luna A/B/C
`validation750` outputs. Not holdout evidence, not clinical validation, and
not authorization to retarget the frozen six-model v0.5 panel in place.
`test450` was not inspected.

## Cross-model guard narrowing (same day)

Six-model no-call replay of the stacked floors showed Qwen net-negative and
DeepSeek paying for singleton cluster dual-form. A first broad diary-override
package overshot (Sol/test450 losses). The retained narrow guards are:

1. bare `1 cluster per …` cadence collapses to `unknown` (2+/multiple keep dual form);
2. typical-over-YTD requires explicit year-to-date selection language;
3. diary may overwrite only explicit current-month seizure-free selections.

After those guards, six-model `validation750` Purist deltas vs the frozen panel
are approximately: mini `+9`, Luna `+14`, Sol `+4`, DeepSeek `+8`, Qwen `-3`,
Gemma `+4`. Hosted `test450` aggregates stay non-negative. Luna A/B/C named
exemplars still pass (`+14/+12/+9`). Remaining Qwen C→W is mostly weak
week-rate vs diary and `N in M months` on gold-`unknown` (7198)—not safely
closed without broader damage.

Artifact:
[six-model replay](../../experiments/gan2026_six_model_current_floors_replay_20260731/replay_summary.json).

## Decision / next

Answer under the protocol stop rule. As of 2026-07-31 these floors plus the
narrow guards are part of the **final Gan LLM-with-rules ruleset**; further
rule tuning for this comparison is closed unless a new predeclared study
reopens it. See
[six-model comparison](six_model_comparison_report_2026-07-18.md).
Do not pursue broad diary override of `1`/`multiple` per week. Remaining
residual is still selection-heavy (multi-semiology totals such as 1880, false
seizure-free vs unknown) and would need a separate prompt/selection study.
