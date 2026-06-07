# Gan 2026 Validation750 HN1 Multi-Month Contract Replay Read

Date: 2026-06-07
Author: Codex

Scope: validation-development follow-through on the first `Now` item in
`PROJECT_STATUS.md` after tightening the
`multi_month_bucket_frequency_value_recovery` contract.

This is a saved-artifact replay over validation750 only. It reassembles the
saved ClinicalAssessment drafts with the updated deterministic normalization
code, then reruns projection/render, score audit, routing, and verification
decision. It does not inspect locked test rows and does not authorize
benchmark-comparable claims.

---

## 1. Inputs

- Prior HN1 replay summary:
  `experiments/gan2026_reset_clinical_assessment_pipeline_validation750_gpt41mini_v0_hn1_multimonth_replay_2026-06-07.json`
- Refreshed contract replay summary:
  `experiments/gan2026_reset_clinical_assessment_pipeline_validation750_gpt41mini_v0_hn1_multimonth_contract_replay_2026-06-07.json`
- Refreshed score rows:
  `experiments/gan2026_reset_clinical_assessment_pipeline_validation750_gpt41mini_v0_hn1_multimonth_contract_replay_2026-06-07.score.jsonl`
- Refreshed null-slice packet:
  `experiments/gan2026_validation750_null_reduction_slices_after_hn1_multimonth_contract_2026-06-07.json`

---

## 2. Whole-Pipeline Change

Relative to the earlier HN1 replay, the tightened contract improves the saved
validation750 replay from:

- rendered rows: `592 -> 597`
- null renders: `158 -> 153`
- Purist-correct scored rows: `494 -> 500`
- routed rows: `40 -> 40`

So the contract fix is not only removing the known denominator regression. It
also converts additional saved validation rows into correct rendered labels
without expanding the routed surface.

---

## 3. Key Row Effects

The previously regressed denominator rows are now restored and correct:

- `16084`: `8 per 4 month`
- `16195`: `16 per 4 month`
- `16220`: `11 per 4 month`

The intended explicit multi-month target rows now also recover cleanly:

- `16674`: `7 per 6 month`
- `16697`: `3 per 6 month`
- `16758`: `9 per 5 month`
- `16833`: `8 per 6 month`

All eight named rows are Purist-correct on the refreshed replay.

---

## 4. Contract Read

Two implementation details matter for the improved replay:

1. explicit `this month so far` buckets now contribute the current-month span,
   and numeric current-month counts are included when present;
2. the multi-month family can now repair from the saved assessment summary
   phrase itself, not only from the selected primary candidate phrase.

Operationally, that second change matters because several saved deterministic
primary phrases remain month-first or otherwise less parser-friendly than the
assessment summary phrase even though the summary already preserves the intended
clinical fact.

---

## 5. Decision

The tightened HN1 contract is now stable enough to serve as the GPT-4.1-mini
comparator state for the next reset-native Qwen validation750 replay.

The next useful read is no longer "fix the current multi-month contract." It is
"compare the refreshed GPT comparator against Qwen and against the completed
hybrid baseline on the same reset-stage contract."
