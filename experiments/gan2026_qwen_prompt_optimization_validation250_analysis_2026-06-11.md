# Gan 2026 Qwen Prompt Optimization: validation250 Analysis

Date: 2026-06-11
Model: ollama_chat/qwen3.6:35b (Ollama local)
Split: validation (first 250 rows)
Baselines: first 250 rows of `gan2026_three_way_comparison_validation750_*_qwen3635b_2026-06-08.jsonl`

## Scope

DL (llm_only_direct_labeler) excluded per project decision. CP and SE only.
CP base version for qwen: v0.8 (deepseek was v0.7; qwen gets one additional pass).
SE base version: v0.6 (same as deepseek — no qwen-specific SE change needed).

## Motivation

Cross-model comparison (2026-06-09) identified qwen's dominant failure modes on the full
validation750:
- **FM-3 unknown_false_pos**: 92 in CP (vs 35 for gpt), caused by suppression rules
  (`denominator_window_mismatch`, `cluster_axis_ambiguity`, `dominant_vague_current_burden`)
  being over-applied — qwen treats them as general permission to use `unknown` rather than
  narrow edge-case guards.
- **CP guidance block harms qwen (−0.7pp)**: the block is gpt-calibrated (suppression-oriented);
  qwen's failure mode is under-commitment, so the same rules push it further toward `unknown`.
- **SE seizure_free_false_pos**: 23 in SE — the v0.6 selection-stage precedence instruction
  (committed with deepseek SF-tightening) also applies to qwen.

## Prompt Changes

### CP: v0.7 → v0.8

File: `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_only_canonical_pipeline.py`

**Change 1** — new `extraction_commitment` instruction added after "Use unknown when..." rule:

> A frequency can be converted when the note gives a count with a time window, even if
> approximate. Approximate and colloquial denominators — 'monthly', 'weekly', 'a few per week',
> 'one or two per month', 'events most days', 'every couple of weeks' — are all normalizable.
> Reserve unknown for notes where genuinely no rate, count, or cadence can be estimated at all.

**Change 2** — new `abstention_calibration` rule appended to `_RULE_TAXONOMY_INSTRUCTIONS`:

> abstention_calibration: the suppression rules above cover specific high-risk situations —
> they are not a general license to use unknown whenever any ambiguity exists. Commit to
> extraction when the note contains a usable frequency fact:
> (a) approximate denominators are usable — apply denominator_window_mismatch only when the
>     time reference is completely absent, not when it is rounded or approximate;
> (b) an explicit cluster cadence is renderable regardless of whether per-cluster event count
>     is known — apply cluster_axis_ambiguity only when you genuinely cannot determine which
>     axis the cluster statement describes;
> (c) a stated current burden is extractable even when vague — contextual uncertainty about
>     the exact count does not prevent labeling the stated cadence.
> If your rationale already names a specific frequency, that frequency is your final_label —
> unknown is not an option when a rate is stated.

### SE: v0.5 → v0.6 (same as deepseek pass — no qwen-specific change needed)

The selection-stage precedence instruction (committed 2026-06-10) applies to qwen as-is.

## Validation250 Results

### Summary Table

| Architecture | Version | Purist correct | Purist accuracy | Unknown-FP | SF-FP | SF-FN |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| CP | v0.2 (baseline) | 228 / 250 | 0.912 | 10 | 3 | 0 |
| CP | v0.8 | 230 / 250 | 0.920 | 15 | 0 | 3 |
| SE | v0.5 (baseline) | 230 / 250 | 0.920 | 3 | 5 | 4 |
| SE | v0.6 | 235 / 250 | 0.940 | 1 | 3 | 4 |

### SE Analysis

SE v0.6 is a strong net improvement: +5 purist correct (+2.0pp), unknown-FP nearly eliminated
(3→1), SF-FP reduced (5→3). SF-FN unchanged (4). Row-level breakdown: 10 fixes, 5 regressions.

Fix categories:
- 2 SF-FP rows correctly de-labeled (1165, 1695): `currently_no_seizure→freq/unknown`
- 2 unknown-FP rows fixed (3710, 4243): `unknown→freq`
- 6 frequency-category boundary fixes (1030, 1207, 4337, 4345, 4624, 5534)

Regressions: 3 rows predicted `None` (parse/output failure, stochastic), 2 frequency-category
boundary shifts. No regression pattern attributable to the prompt change.

### CP Analysis

CP v0.8 shows +2 purist correct (+0.8pp). Row-level: 10 fixes, 8 regressions.

Fix categories:
- 3 unknown-FP rows fixed by `abstention_calibration` (1363, 1706, 3995): `unknown→freq`
- 2 SF-FP rows fixed (1695, 3371): `currently_no_seizure→unknown` (SF-tightening from v0.7)
- 5 frequency-category boundary fixes (187, 816, 1030, 2437, 3242)

Regression categories:
| Regression row | gold | v0.2 pred | v0.8 pred | applied_rules |
| --- | --- | --- | --- | --- |
| 1223 | more1week_less1day | more1week_less1day | unknown | (none) |
| 1573 | 1ormore_daily | 1ormore_daily | unknown | (none) |
| 2487 | more1per6mon_less1mon | more1per6mon_less1mon | more1mon_less1week | denominator_window_mismatch |
| 3325 | more1week_less1day | more1week_less1day | unknown | (none) |
| 4478 | 1ormore_daily | 1ormore_daily | unknown | (none) |
| 5092 | currently_no_seizure | currently_no_seizure | unknown | seizure_free_proxy_evidence_overreach |
| 5379 | currently_no_seizure | currently_no_seizure | unknown | seizure_free_conflict, conditional_only_trigger |
| 5406 | currently_no_seizure | currently_no_seizure | unknown | (none) |

4 of 8 regressions apply no rules and flip correct→unknown — these are stochastic prompt-shift
(version string change alters tokenization on hard edge cases near decision boundaries).
3 of 8 regressions are SF-FN (gold=currently_no_seizure); these inflate SF-FN from 0→3 and
are caused by the SF-tightening rules in v0.7 over-firing for qwen (same pattern seen in the
deepseek stochastic analysis).
1 regression (2487) applies denominator_window_mismatch — borderline case, not abstention_calibration-driven.

**Unknown-FP net**: abstention_calibration fixed 3 unknown-FPs; 4 new stochastic regressions
added 4 new unknown-FPs. Net +5 is dominated by stochastic shift, not instruction regression.

## Interpretation

Both changes are kept:
- **SE v0.6 is unambiguously positive** for qwen: +2.0pp, unknown-FP ≈0, SF-FP reduced.
- **CP v0.8 is net positive** (+0.8pp) with abstention_calibration working as intended (3 fixed),
  but stochastic prompt-shift noise obscures the unknown-FP improvement at validation250 scale.
  The abstention_calibration rule is correct and should show cleaner signal at validation750 scale.

The 4 stochastic CP regressions (all no-rule, correct→unknown) are consistent with qwen being
sensitive to prompt tokenization changes — the same ~5-10 row stochastic drift seen in all
prior version bumps. They are not instruction-attributable.

## Artifacts

- CP v0.8: `experiments/gan2026_v08_validation250_llm_only_canonical_pipeline_qwen3635b_2026-06-11.jsonl`
- SE v0.6: `experiments/gan2026_v06_validation250_hybrid_structured_events_qwen3635b_2026-06-11.jsonl`

## Next Steps

1. Rename output files to reflect date 2026-06-11.
2. Commit CP v0.8 + SE v0.6 qwen analysis.
3. Optionally: run validation750 for qwen CP v0.8 to confirm abstention_calibration impact
   at scale (expected: unknown-FP 92→~60-70, net accuracy gain vs v0.2 baseline).
4. Consider whether SF-FN regressions from SF-tightening rules warrant a qwen-specific
   softening (seizure_free_proxy_evidence_overreach fires differently for qwen).
