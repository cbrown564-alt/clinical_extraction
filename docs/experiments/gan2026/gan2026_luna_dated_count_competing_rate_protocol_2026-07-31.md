# Dated-count and competing-rate floor protocol

Date: 2026-07-31  
Status: complete; absorbed into final Gan LLM-with-rules ruleset  
Parent: [projection floor](../../research/gan2026_luna_projection_antiregression_floor_report_2026-07-31.md)  
Report: [dated-count report](../../research/gan2026_luna_dated_count_competing_rate_report_2026-07-31.md)  
Final ruleset owner: [six-model comparison](../../research/six_model_comparison_report_2026-07-18.md)

## Primary question

On Gan `validation750`, can two narrow deterministic floors recover remaining
Luna A/B/C residuals by (1) keeping dated countable windows from falling to
`no seizure frequency reference`, and (2) preferring a stated typical/usual
recurring rate over a year-to-date observation total when both are already in
the event ledger—without prompt changes or holdout inspection?

## Fixed conditions

- Split: `validation750`; row inspection permitted.
- Locked: `test450` sealed.
- Replay: no-call saved Luna A/B/C raw outputs through `hybrid_full_stack`.
- Comparator: post projection/anti-regression floor working tree.
- Scorer: Gan Purist primary.

## Candidate A — dated-count floor (`benchmark_format` / `seizure_frequency`)

1. Project `N in M months` / `N … within M months` to `N per M month` before
   unknown/no-reference fallback.
2. When the repaired label is `unknown` or `no seizure frequency reference` and
   event texts lack two **distinct** calendar months, mine `note_text` with the
   existing dated-sequence extractor (first/second seizure in Month Year).

Named exemplars: 14587 (`2 in 3 months`), 14628 (April/June pair → `2 per 2 month`).

## Candidate B — competing-rate policy (`seizure_frequency`)

When selection evidence or the repaired label is a year-to-date / “so far this
year” observation total, and another extracted event states a typical/usual
recurring rate (`monthly` / `weekly` / `per month` / `per week` with typically/
usual/at present pattern language), prefer the typical recurring rate.

Named exemplar: 2748 (YTD seven this year vs typical monthly).

Out of scope for this study: summing multi-semiology period totals (1880),
diary month-span arithmetic, and kitchen-sink B+C prompts.

## Stop rule

- Answer: dated-count rescues ≥1 of {14587,14628} on ≥2 variants with net Purist
  Δ≥0; competing-rate rescues 2748 on ≥2 variants with net Δ≥0, or is revised
  once if regressions cancel it.
- Negative: no net gain or large correct-to-wrong wave.
- Reject: prompt/scorer changes or `test450` inspection.

## Claim boundary

Development hybrid artifact on saved Luna A/B/C outputs. Not holdout evidence,
clinical validation, or frozen six-model panel rewrite.
