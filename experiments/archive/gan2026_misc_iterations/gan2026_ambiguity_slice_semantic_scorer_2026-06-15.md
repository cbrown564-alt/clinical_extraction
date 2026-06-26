# Gan 2026 Ambiguity Slice Semantic / Over-Specificity Scorer

Date: 2026-06-15

Validation-only instrumentation (step 3.2 of the unknown-frequency agentic pathways doc). It re-reads the saved live ambiguity slice and scores each row on the *clinical decision* alongside Purist, to catch the two failure modes Purist is blind to. No model calls, no locked test rows, no scorer change — this is a diagnostic overlay, not a replacement for the frozen scorer.

## Why Purist is not enough here

`multiple per month`, `multiple per year`, `unknown`, and `no seizure frequency reference` all normalize to `monthly=1000.0` / `seizure_freq_unknown`. So on a gold-`unknown` row an over-specific concrete frequency scores Purist-correct purely by re-bucketing (Insight 5). Optimizing the ambiguity slice on Purist alone would credit re-bucketing as reasoning.

## Headline

- Rows scored: `22`
- Purist-correct: `12/22`
- Semantic-correct (clinical decision agrees, no re-bucketing credit): `12/22`
- Purist credit not backed by semantics: `0`
- Over-specific re-bucketing rows (Purist-correct, clinically wrong): `none`
- Class/label incoherent rows (Insight 4): `[14454, 14137]`

## Per-row

| Row | Gold | Pred | Gold decision | Pred decision | Purist | Semantic | Over-spec | Class | Class incoherent |
| ---: | --- | --- | --- | --- | :---: | :---: | :---: | --- | :---: |
| 3356 | `unknown` | `unknown` | unknown_decision | unknown_decision | yes | yes | no | `unknown_count_or_window` | no |
| 5534 | `1 per multiple month` | `unknown` | unknown_decision | unknown_decision | yes | yes | no | `last_event_only_unknown` | no |
| 6153 | `9 per month` | `9 per 4 week` | frequency_decision | frequency_decision | yes | yes | no | `explicit_count_window` | no |
| 6321 | `unknown` | `2 per 3 month` | unknown_decision | frequency_decision | no | no | no | `explicit_count_window` | no |
| 6368 | `unknown` | `3 per 6 week` | unknown_decision | frequency_decision | no | no | no | `explicit_count_window` | no |
| 6571 | `unknown` | `unknown` | unknown_decision | unknown_decision | yes | yes | no | `last_event_only_unknown` | no |
| 7168 | `unknown` | `unknown` | unknown_decision | unknown_decision | yes | yes | no | `unknown_count_or_window` | no |
| 7615 | `3 to 7 per month` | `3 to 6 per month` | frequency_decision | frequency_decision | yes | yes | no | `explicit_count_window` | no |
| 9496 | `6 per 12 month` | `6 per 12 month` | frequency_decision | frequency_decision | yes | yes | no | `explicit_count_window` | no |
| 9937 | `1 cluster per month, multiple per cluster` | `unknown` | frequency_decision | unknown_decision | no | no | no | `unknown_count_or_window` | no |
| 9943 | `1 cluster per 4 to 5 week, multiple per cluster` | `unknown` | frequency_decision | unknown_decision | no | no | no | `unknown_count_or_window` | no |
| 11216 | `unknown` | `seizure free for 4 month` | unknown_decision | seizure_free_decision | no | no | no | `explicit_seizure_free_duration` | no |
| 11254 | `unknown` | `seizure free for 3 month` | unknown_decision | seizure_free_decision | no | no | no | `explicit_seizure_free_duration` | no |
| 11272 | `unknown` | `unknown` | unknown_decision | unknown_decision | yes | yes | no | `last_event_only_unknown` | no |
| 11337 | `unknown` | `unknown` | unknown_decision | unknown_decision | yes | yes | no | `last_event_only_unknown` | no |
| 13209 | `1 per 8 month` | `1 per 4 to 5 week` | frequency_decision | frequency_decision | no | no | no | `explicit_count_window` | no |
| 13267 | `2 per 5 month` | `unknown` | frequency_decision | unknown_decision | no | no | no | `unknown_count_or_window` | no |
| 14025 | `unknown` | `2 per 6 week` | unknown_decision | frequency_decision | no | no | no | `explicit_count_window` | no |
| 14029 | `unknown` | `unknown` | unknown_decision | unknown_decision | yes | yes | no | `unknown_count_or_window` | no |
| 14137 | `unknown` | `unknown` | unknown_decision | unknown_decision | yes | yes | no | `explicit_count_window` | yes |
| 14454 | `2 per 2 month` | `2 per 2 month` | frequency_decision | frequency_decision | yes | yes | no | `last_event_only_unknown` | yes |
| 14821 | `1 per month` | `unknown` | frequency_decision | unknown_decision | no | no | no | `last_event_only_unknown` | no |

## Gold -> predicted clinical decision confusion

| Gold decision -> predicted decision | Rows |
| --- | ---: |
| frequency_decision->frequency_decision | 5 |
| frequency_decision->unknown_decision | 4 |
| unknown_decision->frequency_decision | 3 |
| unknown_decision->seizure_free_decision | 2 |
| unknown_decision->unknown_decision | 8 |

## Interpretation

No over-specific re-bucketing fires on this slice: the Purist-correct rows are genuine unknown / seizure-free / frequency calls, so the Purist-semantic gap is driven by clinical-kind mismatches (0 row(s)) rather than the Insight-5 illusion. The scorer is in place for the live run, where regeneration is far more likely to trip it. Class/label incoherence (Insight 4) fires on 2 row(s) ([14454, 14137]): the emitted ambiguity class contradicts the rendered decision, so the correct label is coming from the gate and label logic, not from a trustworthy class signal. The class field must not be used as a selector feature until this is driven to zero on the supervisor and source-near panels.
