# Results: Gan rules-only three-stage Phase E

Date: 2026-08-30
Protocol: [Phase E protocol](gan_rules_only_three_stage_phase_e_protocol_2026-08-30.md)
Artifact: `experiments/gan2026_rules_only_three_stage_phase_e_20260830/dev750_summary.json`
Split: `dev750` only; `test450` never loaded. Zero model calls.
Scorer: Purist via `score_label`.

## Gates (all met)

- **E1 select identity:** default runner select label and evidence match
  `run_record` on 750/750; select remains **669/750**. Promoted
  `phase_c_candidate_config()` select remains **691/750**.
- **E2 relocated drops:** extract-time Select now appears on the ledger.
  Default-runner drop counts: rule-exclude **45**, medication/dose
  **19**, historical lead-in **23**, plus the Phase A drops (duplicate
  304, historical-rate prune 23, contained-fragment 4).
- **E3 named producers:** **0** wide-ledger rows with `rule_id="unknown"`.
- **E4 encode is not identity:** find tag ≠ encode codebook on **502**
  default-runner rows.

Cited five-cell stops stay **292 / 292 / 325**. `_gan_grid` was not
rewired.

## Stage stops

Find stop is the pre-codebook `find_tag` of the document-order-first
wide-ledger candidate, including Select-dropped rows. Encode is
codebook render + `repair_prediction_label` of that same pick. These
Purist numbers are **not** commensurate with LLM find columns.

| Arm | Find | Encode | Select |
| --- | ---: | ---: | ---: |
| Default (`run_record` identity) | **216**/750 | **577**/750 | **669**/750 |
| Promoted Phase C config | **235**/750 | **599**/750 | **691**/750 |
| Phase A (fused codebook find) | 600/750 | 600/750 | 669/750 |

Select is unchanged. Encode is no longer identical to find. Encode
fell versus Phase A (600 → 577 default) because the document-order
pick can now land on a relocated distractor or excluded span; that is
the same-pick policy, not a select regression.

## What remains fused after Phase E

Cluster, diary, and gan-shorthand still passed a finished codebook
string as `FindFact.custom_label` at the Phase E cut. That seam is
closed in [Phase E2](gan_rules_only_three_stage_phase_e2_2026-08-30.md).
Seizure-free find tags remain state-only (`seizure_free`); encode
still writes the duration codebook string from `custom_label`.

## Claim boundary

Development instrumentation on `dev750`. Not a cited-row change. Not
holdout evidence. Do not describe the new find column as a five-cell
comparable stop until a later protocol decides how to present it.
