# Gan 2026 Ambiguity-Aware Live Component-Generation Audit

Date: 2026-06-15

This is the decisive validation-only experiment from the unknown-frequency agentic pathways doc. It scores live `v0.7` + safety-`v0.9` ambiguity-aware fresh-evidence generation over the predeclared 22-row validation hard slice against gold and the prior component availability. It reads no locked test rows; the model calls were made on the validation split.

## Decisive Result

The selector line is saturated: an oracle over the current deterministic/consensus/fresh-v0.4 components topped out at 739/750, with 11 validation rows having no Purist-correct component at all. The only way to lift the holdout target is to make a correct component *exist* on those rows.

- No-correct rows fixed by live ambiguity-aware fresh generation: **1/11**
- Selector oracle ceiling: 739/750 -> **739/750** (delta +0)
- Recoverable rows fresh component preserved: 5/6 (regressions: [14821])
- Supervisor ambiguity panel (live): 2/6 labels Purist-correct

## No-Correct Rows (the rows that gate the ceiling)

These 11 rows had no Purist-correct deterministic, consensus, or fresh-v0.4 component. Deterministic and consensus are unchanged, so the ceiling moves only where live fresh generation is newly correct.

| Row | Band | Gold | Det/Consensus | Fresh v0.4 | Fresh v0.7 (live) | Ambiguity class | Now correct |
| ---: | --- | --- | --- | --- | --- | --- | :---: |
| 5534 | `band_unknown` | `1 per multiple month` | `seizure free for multiple year` | `1 per 2 week` | `unknown` | `last_event_only_unknown` | yes |
| 6321 | `band_unknown` | `unknown` | `1 per day` | `2 per 3 month` | `2 per 3 month` | `explicit_count_window` | no |
| 6368 | `band_unknown` | `unknown` | `1 per 1 to 2 week` | `3 per 6 week` | `3 per 6 week` | `explicit_count_window` | no |
| 6571 | `band_unknown` | `unknown` | `seizure free for multiple year` | `1 per 4 month` | `1 per 4 month` | `explicit_seizure_free_duration` | no |
| 9937 | `band_monthly` | `1 cluster per month, multiple per cluster` | `1 per multiple week` | `multiple per month` | `multiple per month` | `unknown_count_or_window` | no |
| 9943 | `band_monthly` | `1 cluster per 4 to 5 week, multiple per cluster` | `1 per 4 to 5 week` | `1 per 4 to 5 week` | `1 per 4 to 5 week` | `cluster_axis_incomplete` | no |
| 11216 | `band_unknown` | `unknown` | `seizure free for 4 month` | `seizure free for 4 month` | `seizure free for 4 month` | `explicit_seizure_free_duration` | no |
| 11254 | `band_unknown` | `unknown` | `seizure free for multiple year` | `seizure free for 3 month` | `seizure free for 3 month` | `explicit_seizure_free_duration` | no |
| 11272 | `band_unknown` | `unknown` | `seizure free for multiple year` | `seizure free for 3 month` | `seizure free for 3 month` | `explicit_seizure_free_duration` | no |
| 13209 | `band_submonthly` | `1 per 8 month` | `1 per 4 to 5 week` | `1 per 4 to 5 week` | `1 per 4 to 5 week` | `explicit_count_window` | no |
| 14025 | `band_unknown` | `unknown` | `seizure free for multiple year` | `2 per 6 week` | `2 per 6 week` | `explicit_count_window` | no |

## Recoverable Rows (regression guard)

These rows already had a correct component at v0.4 (mostly fresh-only). Live regeneration must not destroy them.

| Row | Band | Gold | Fresh v0.4 | Fresh v0.7 (live) | Prior fresh correct | Now correct |
| ---: | --- | --- | --- | --- | :---: | :---: |
| 3356 | `band_unknown` | `unknown` | `multiple per year` | `unknown` | yes | yes |
| 6153 | `band_weekly` | `9 per month` | `9 per 4 week` | `9 per 4 week` | yes | yes |
| 7168 | `band_unknown` | `unknown` | `multiple per week` | `unknown` | yes | yes |
| 7615 | `band_weekly` | `3 to 7 per month` | `3 to 6 per month` | `3 to 6 per month` | yes | yes |
| 9496 | `band_submonthly` | `6 per 12 month` | `6 per 12 month` | `6 per 12 month` | yes | yes |
| 14821 | `band_monthly` | `1 per month` | `1 per month` | `unknown` | yes | no |

## Supervisor Ambiguity Panel (live)

The six supervisor-discussed rows, now scored on live generation rather than the parser/safety-gate contract. This is the precision check: the explicit count-window cases (`14454`, `13267`) must stay frequencies while the ambiguous cases collapse to `unknown`.

| Row | Expected | Live label | Expected class | Live class | Label ok | Class match |
| ---: | --- | --- | --- | --- | :---: | :---: |
| 11272 | `unknown` | `seizure free for 3 month` | `last_event_only_unknown` | `explicit_seizure_free_duration` | no | no |
| 11337 | `unknown` | `1 per 8 week` | `unknown_count_or_window` | `explicit_count_window` | no | no |
| 13267 | `2 per 5 month` | `unknown` | `explicit_count_window` | `unknown_count_or_window` | no | no |
| 14029 | `unknown` | `unknown` | `unknown_count_or_window` | `unknown_count_or_window` | yes | yes |
| 14137 | `unknown` | `unknown` | `unknown_count_or_window` | `explicit_count_window` | yes | no |
| 14454 | `2 per 2 month` | `unknown` | `explicit_count_window` | `last_event_only_unknown` | no | no |

## Interpretation

Live ambiguity-aware fresh generation made a correct component exist on 1 of 11 previously no-correct rows, moving the selector oracle ceiling +0 to 739/750. The ceiling did not move: even with the explicit ambiguity contract, live fresh generation reproduces the same over-reading on the hard rows. This confirms the line has converged on the component-generation wall and that the next bet must change the evidence the model sees, not the decision contract layered on top. Caveat: live regeneration regressed previously-correct fresh rows [14821]; a wider replay must confirm net ceiling movement, not a local trade.
