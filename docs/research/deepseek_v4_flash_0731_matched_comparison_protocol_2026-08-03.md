# DeepSeek V4-Flash-0731 matched comparison protocol

Date: 2026-08-03  
Status: complete (aggregate synthesis; no new model calls)  
Artifact: [`experiments/deepseek_v4_flash_0731_matched_comparison_20260803.json`](../../experiments/deepseek_v4_flash_0731_matched_comparison_20260803.json)  
Report: [matched comparison report](deepseek_v4_flash_0731_matched_comparison_report_2026-08-03.md)

## Primary question

How does the 2026-07-31 DeepSeek-V4-Flash API revision (`DeepSeek-V4-Flash-0731`)
change **ruleset-matched** ExECTv2 and Gan2026 results for `llm` and
`llm_with_rules` versus the prior matched panel cells?

## Why this study

The ExECT `dev140` provider-update re-run already has a ruleset-matched diff.
Gan `test450` 0731 live aggregates also exist under `scratch/holdout/`, but
lacked a public cross-task comparison that separates frozen panel scores from
final-ruleset replay of the same prior raws. This protocol freezes that
comparison without new calls or holdout row inspection.

## Data, splits, and row policy

| Task | Split | Method surfaces | Row policy |
| --- | --- | --- | --- |
| ExECTv2 | `dev140` | `raw_lane_score` (llm), `clinical_headline` (llm_with_rules) | Development review permitted |
| ExECTv2 | `test60` | same | Aggregate-only; sealed rows uninspectable |
| Gan2026 | `test450` | llm_only v0.8; hybrid v0.5 llm_with_rules | Aggregate-only; sealed rows uninspectable |

## Comparators and candidates

| Cell | Prior (ruleset-matched where available) | 0731 candidate |
| --- | --- | --- |
| ExECT `dev140` | Current-rules no-call replay of 2026-07-15 structured outputs | Live no-cache 0731 re-run |
| ExECT `test60` | Retained six-model stage-panel DeepSeek cell | Live no-cache 0731 re-run |
| Gan llm_with_rules `test450` | Final-ruleset no-call replay of matched v0.5 DeepSeek raws (348/450) | Live hybrid_full_stack 0731 |
| Gan llm_only `test450` | **None** (no pre-0731 matched v0.5 DeepSeek llm_only test450) | Live llm_only 0731 (first matched cell) |

Frozen Gan July panel DeepSeek (344/450) is retained as historical context only.
It is not the ruleset-matched prior.

## Metrics

- ExECT: clinical fact F1 (`raw_lane_score` / `clinical_headline`).
- Gan: Purist primary; Pragmatic side-car.
- No cross-task numerical ranking. Tasks remain separate.

## Required prep (completed before report)

1. Confirm ExECT `dev140` current-rules replay equals retained panel (0.8767 /
   raw 0.7915).
2. Confirm ExECT `dev140` vs-0731 diff artifact exists and is used for family
   and letter-change counts.
3. Publish aggregate-only Gan and ExECT holdout 0731 numbers into one
   comparison JSON (this study); do not open sealed row JSONL.
4. Treat Gan ruleset-matched prior as final-ruleset replay (348), not frozen
   344 alone.
5. Explicitly mark Gan llm_only as first matched cell with no prior.
6. Render charts from the comparison JSON only.

## Stop rule

Answer with bounded provider-update deltas and gaps. Do not promote 0731 cells
into the retained six-model paper panels unless a separate promotion decision
says so.

## Claim boundary

Provider-update / development and aggregate-only holdout evidence for the named
DeepSeek API revision. Not panel replacement, Decision 0046 primary-method
fills, clinical validation, or a model-neutral ranking. Hosted DeepSeek route
and ExECT `max_tokens` amendment (16k→64k) remain disclosed.
