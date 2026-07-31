# Luna projection + anti-regression floor protocol

Date: 2026-07-31  
Status: complete; absorbed into final Gan LLM-with-rules ruleset; development answer  
Parent: [residual analysis](../../research/gan2026_luna_prompt_variants_residual_analysis_2026-07-31.md)  
Report: [floor report](../../research/gan2026_luna_projection_antiregression_floor_report_2026-07-31.md)

## Primary question

On Gan `validation750`, can a narrow deterministic floor recover shared Luna
A/B/C residual rows by (1) projecting already-selected cluster/range facts into
scorable labels before unknown fallback, and (2) blocking repair families that
overwrite correct raw seizure-free or recent-count selections with historical
aggregates—without a new prompt and without rewriting the frozen six-model
panel?

## Why this study

The residual analysis found 48 rows Purist-wrong under all three Luna prompts
after `hybrid_full_stack`. Exact evidence is present. Several shared failures
are stack-local:

- cadence-only cluster labels (`3 clusters per month`) collapse to `unknown`;
- `1 or 3 per month` is unparsable while `1 to 3 per month` scores;
- correct raw seizure-free / recent-window answers are overwritten by diary or
  dated-sequence repair (rows 2932, 2459).

Prompt variants rearrange margins; they do not fix these floors.

## Fixed conditions

- Dataset / split: Gan 2026 `validation750`; row inspection permitted.
- Locked split: `test450` sealed; no inspection or tuning from it.
- Model outputs: no-call replay of retained Luna A/B/C raw outputs.
- Prompt / schema: unchanged (`v0.5`, `v0.8_luna_rate`, `v0.8_luna_current`).
- Scorer: Gan Purist primary; Pragmatic secondary.
- Comparator: current `hybrid_full_stack` before the floor package.

## Candidate

Two deterministic modules only:

1. **Projection floor** (`benchmark_format` / `seizure_frequency` as claimed):
   - cadence-only cluster → `{N} cluster per {period}, multiple per cluster`
     instead of immediate `unknown`, when no contradictory per-cluster count;
   - `N or M per {unit}` → `N to M per {unit}` when both ends are countable.
2. **Anti-regression guard** (`seizure_frequency`):
   - do not let `monthly_diary_repair` or `dated_sequence_repair` replace a
     already-parsable selected seizure-free label with a historical rate;
   - do not let `monthly_diary_repair` replace an already-parsable recent-window
     rate (day/week/fortnight-scale) with a multi-month diary aggregate when
     the selected label matches the model selection.

No competing-rate gold-policy change in this study. No B+C prompt merge.

## Readouts

Primary: matched no-call Purist on Luna A, B, and C `validation750` finals
versus the pre-floor artifacts.

Required secondary:

- change count on the 48 persistent residual rows;
- correct-to-wrong regressions versus pre-floor finals;
- rules-control regressions among rows that remain LLM+rules wrong;
- exact counts for the named exemplar rows 1030, 2459, 2932, 5837, 10097,
  10237, 14587, 14628 when present in the saved traces.

## Stop rule

- Answer: floor package gains ≥1 of the named projection/regression exemplars
  on at least two variants, with net Purist gain ≥0 on each variant and no
  large new correct-to-wrong wave.
- Negative: no net gain, or regressions cancel the named rescues.
- Revise once: if a guard is too broad, narrow the predicate and re-replay.
- Reject: any prompt change, scorer change, or `test450` inspection.

## Claim boundary

Development diagnostic / hybrid development artifact for named deterministic
floors on saved Luna A/B/C outputs. Not holdout evidence, not clinical
validation, and not authorization to retarget the frozen six-model v0.5 panel
in place.
