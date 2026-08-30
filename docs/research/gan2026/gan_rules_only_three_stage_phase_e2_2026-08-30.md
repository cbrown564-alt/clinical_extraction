# Results: Gan rules-only three-stage Phase E2

Date: 2026-08-30
Protocol: [Phase E2 protocol](gan_rules_only_three_stage_phase_e2_protocol_2026-08-30.md)
Artifact: `experiments/gan2026_rules_only_three_stage_phase_e2_20260830/dev750_summary.json`
Split: `dev750` only; `test450` never loaded. Zero model calls.
Scorer: Purist via `score_label`.

## Gates (all met)

- **E1 select identity:** default runner select label and evidence match
  `run_record` on 750/750; select remains **669/750**. Promoted
  `phase_c_candidate_config()` select remains **691/750**.
- **E5 slot encode:** cluster, diary, and gan-shorthand builders emit
  `FindFact` slots with `custom_label is None`. Encode writes the
  codebook string (`cluster_period_label` / `rate_label`, including
  compact `mo` and adjective units such as `daily`). RuleSpec examples
  that fire still match their recorded `expected_label`.
- **E6 find ≠ encode:** fixtures exist where the same pick's find tag
  is pre-codebook (`cluster:…`, `{count}/{unit}`) and encode is the
  codebook form.

Cited five-cell stops stay **292 / 292 / 325**. `_gan_grid` was not
rewired.

## Stage stops

Find is still the pre-codebook `find_tag` of the document-order-first
wide-ledger candidate, including Select-dropped rows. Encode is
unchanged as codebook render + `repair_prediction_label` of that pick.
These Purist numbers are **not** commensurate with LLM find columns.

| Arm | Find | Encode | Select |
| --- | ---: | ---: | ---: |
| Default (`run_record` identity) | **109**/750 | **577**/750 | **669**/750 |
| Promoted Phase C config | **128**/750 | **599**/750 | **691**/750 |
| Phase E (cluster/diary/shorthand still codebook at find) | 216/750 | 577/750 | 669/750 |

Select and encode are unchanged from Phase E. Find fell (216 → 109
default; 235 → 128 promoted) because cluster, diary, and gan-shorthand
picks now score their slot tags against gold codebook strings. Find
tag ≠ encode codebook on **616** default-runner rows (502 in Phase E).
Relocated drop counts are unchanged.

Date-window and diary-aggregation arithmetic stay in find. Encode only
renders already-chosen slots. Fortnightly cluster periods still encode
as `fortnight`, matching the living codebook writer, not `2 week`.

## What remains fused

Seizure-free find tags are state-only (`seizure_free`); encode writes
the duration codebook string from `custom_label`. That is the remaining
builder-side codebook string.

## Claim boundary

Development instrumentation on `dev750`. Not a cited-row change. Not
holdout evidence. Do not describe the find column as a five-cell
comparable stop until a later protocol decides how to present it.
