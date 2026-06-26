# Gan 2026 Residual Component Diversity Audit

Date: 2026-06-15

Validation-only instrumentation (step 3.1 of the unknown-frequency agentic pathways doc). It reads the saved v0.9 residual component-generation audit, normalizes each component's label to its Purist bucket, and measures whether the deterministic, consensus, and fresh-v0.4 components fail in *correlated* (one bucket) or *independent* (split bucket) ways. No model calls, no locked test rows, no scorer change.

## Why this matters

The selector-only oracle is capped at `739/750` because `11` selected-wrong rows have no Purist-correct component at all (Insight 1). Insight 2 claims those failures are *correlated* — the three nominally independent sources share one over-reading prior. If true, a second generation pass that shares that prior buys nothing; only changing the evidence the model reads can move the ceiling. This audit tests the claim directly.

## Headline

- Selected-wrong rows audited: `17` (`11` no-correct, `6` recoverable)
- No-correct rows where all three components land in **one** Purist bucket (identically wrong): **`7/11`** (fraction `0.6364`)
- No-correct rows where at least one component breaks ranks: `4/11`

Correlated (one-bucket) no-correct rows: `[6368, 9937, 9943, 11216, 11254, 11272, 13209]`

Split (multi-bucket) no-correct rows: `[5534, 6321, 6571, 14025]`

## Agreement structure

| Subset | all_three_one_bucket | two_buckets | three_buckets |
| --- | ---: | ---: | ---: |
| all_selected_wrong | 7 | 10 | 0 |
| no_correct | 7 | 4 | 0 |
| recoverable | 0 | 6 | 0 |

## No-correct rows (the rows that gate the ceiling)

| Row | Band | Gold | Det bucket | Consensus bucket | Fresh-v0.4 bucket | Distinct | Agreement |
| ---: | --- | --- | --- | --- | --- | ---: | --- |
| 5534 | `band_unknown` | `1 per multiple month` | `currently_no_seizure` | `currently_no_seizure` | `seizure_freq_more1mon_less1week` | 2 | two_buckets |
| 6321 | `band_unknown` | `unknown` | `seizure_freq_1ormore_daily` | `seizure_freq_1ormore_daily` | `seizure_freq_more1per6mon_less1mon` | 2 | two_buckets |
| 6368 | `band_unknown` | `unknown` | `seizure_freq_more1mon_less1week` | `seizure_freq_more1mon_less1week` | `seizure_freq_more1mon_less1week` | 1 | all_three_one_bucket |
| 6571 | `band_unknown` | `unknown` | `currently_no_seizure` | `seizure_freq_more1per6mon_less1mon` | `seizure_freq_more1per6mon_less1mon` | 2 | two_buckets |
| 9937 | `band_monthly` | `1 cluster per month, multiple per cluster` | `seizure_freq_unknown` | `seizure_freq_unknown` | `seizure_freq_unknown` | 1 | all_three_one_bucket |
| 9943 | `band_monthly` | `1 cluster per 4 to 5 week, multiple per cluster` | `seizure_freq_more1per6mon_less1mon` | `seizure_freq_more1per6mon_less1mon` | `seizure_freq_more1per6mon_less1mon` | 1 | all_three_one_bucket |
| 11216 | `band_unknown` | `unknown` | `currently_no_seizure` | `currently_no_seizure` | `currently_no_seizure` | 1 | all_three_one_bucket |
| 11254 | `band_unknown` | `unknown` | `currently_no_seizure` | `currently_no_seizure` | `currently_no_seizure` | 1 | all_three_one_bucket |
| 11272 | `band_unknown` | `unknown` | `currently_no_seizure` | `currently_no_seizure` | `currently_no_seizure` | 1 | all_three_one_bucket |
| 13209 | `band_submonthly` | `1 per 8 month` | `seizure_freq_more1per6mon_less1mon` | `seizure_freq_more1per6mon_less1mon` | `seizure_freq_more1per6mon_less1mon` | 1 | all_three_one_bucket |
| 14025 | `band_unknown` | `unknown` | `currently_no_seizure` | `seizure_freq_more1mon_less1week` | `seizure_freq_more1mon_less1week` | 2 | two_buckets |

## Interpretation

Of the 11 no-correct residual rows, 7 have all three components collapsed into a single Purist bucket (fraction 0.6364). On those rows the deterministic rules, exact consensus, and V12 fresh evidence are not just wrong but *identically* wrong — independence has collapsed exactly where it would have to hold for selection or voting to help. This confirms Insight 2 quantitatively: the dominant residual mode is correlated, single-bucket over-reading, not a selection miss among diverse candidates. A second generation pass only helps if it does not share the over-reading prior — i.e. if it changes the evidence the model conditions on, not merely the decision contract layered on top. Adding another same-prior voter is expected to buy nothing on these rows. The split rows are the more tractable target for a second pass; the correlated rows need different evidence, not another vote.
