# Gan 2026 Residual Non-Prediction Audit

Validation-development audit of non-prediction rows from the staged decision layer. Gold and blocked-candidate correctness are development accounting only; this does not authorize locked-test inspection, benchmark-comparable claims, or full-validation verifier use.

## Summary

The staged decision layer has 34 non-prediction rows. Development accounting says the blocked source candidate was Purist-correct on 19 rows and Purist-wrong on 15 rows.

## Actions

| Action | Rows |
| --- | ---: |
| `abstain` | 26 |
| `human_review` | 8 |

## Reasons

| Reason | Rows |
| --- | ---: |
| `last_event_boundary` | 8 |
| `missing_denominator_anchor` | 2 |
| `trigger_conditioned_frequency` | 24 |

## Next Step

Run a selective abstention-pressure review before full-validation verifier use or promotion.

## Artifacts

- Audit JSONL: `experiments/gan2026_staged_hybrid_residual_nonprediction_audit_2026-06-04.jsonl`
- Audit summary JSON: `experiments/gan2026_staged_hybrid_residual_nonprediction_audit_2026-06-04.json`

## Rows

| Row | Action | Reason | Gold | Blocked label | Blocked Purist-correct |
| ---: | --- | --- | --- | --- | --- |
| 3356 | `abstain` | `trigger_conditioned_frequency` | `unknown` | `seizure free for multiple year` | False |
| 3371 | `abstain` | `trigger_conditioned_frequency` | `unknown` | `unknown` | True |
| 3468 | `abstain` | `trigger_conditioned_frequency` | `unknown` | `no seizure frequency reference` | True |
| 3469 | `abstain` | `trigger_conditioned_frequency` | `unknown` | `unknown` | True |
| 3482 | `abstain` | `trigger_conditioned_frequency` | `unknown` | `unknown` | True |
| 3493 | `abstain` | `trigger_conditioned_frequency` | `unknown` | `no seizure frequency reference` | True |
| 4731 | `abstain` | `trigger_conditioned_frequency` | `unknown` | `no seizure frequency reference` | True |
| 5490 | `abstain` | `missing_denominator_anchor` | `unknown` | `no seizure frequency reference` | True |
| 5974 | `abstain` | `trigger_conditioned_frequency` | `unknown` | `seizure free for multiple year` | False |
| 5977 | `abstain` | `trigger_conditioned_frequency` | `unknown` | `multiple per 6 week` | True |
| 5996 | `abstain` | `trigger_conditioned_frequency` | `unknown` | `no seizure frequency reference` | True |
| 6077 | `abstain` | `trigger_conditioned_frequency` | `unknown` | `seizure free for 8 month` | False |
| 6087 | `abstain` | `trigger_conditioned_frequency` | `unknown` | `no seizure frequency reference` | True |
| 6094 | `abstain` | `trigger_conditioned_frequency` | `3 per month` | `3 per week` | False |
| 6131 | `abstain` | `trigger_conditioned_frequency` | `unknown` | `seizure free for 6 month` | False |
| 6153 | `abstain` | `trigger_conditioned_frequency` | `9 per month` | `1 per 1 to 2 week` | False |
| 6319 | `abstain` | `trigger_conditioned_frequency` | `1 per week` | `1 per week` | True |
| 6321 | `abstain` | `trigger_conditioned_frequency` | `unknown` | `1 per day` | False |
| 6368 | `abstain` | `trigger_conditioned_frequency` | `unknown` | `1 per 1 to 2 week` | False |
| 7093 | `abstain` | `trigger_conditioned_frequency` | `unknown` | `no seizure frequency reference` | True |
| 7168 | `abstain` | `trigger_conditioned_frequency` | `unknown` | `2 per year` | False |
| 9103 | `abstain` | `trigger_conditioned_frequency` | `unknown` | `no seizure frequency reference` | True |
| 9877 | `abstain` | `trigger_conditioned_frequency` | `unknown` | `no seizure frequency reference` | True |
| 9879 | `abstain` | `trigger_conditioned_frequency` | `unknown` | `no seizure frequency reference` | True |
| 11216 | `human_review` | `last_event_boundary` | `unknown` | `seizure free for 4 month` | False |
| 11254 | `human_review` | `last_event_boundary` | `unknown` | `seizure free for multiple year` | False |
| 11259 | `human_review` | `last_event_boundary` | `unknown` | `seizure free for multiple year` | False |
| 11262 | `human_review` | `last_event_boundary` | `unknown` | `unknown` | True |
| 11272 | `human_review` | `last_event_boundary` | `unknown` | `seizure free for multiple year` | False |
| 11282 | `human_review` | `last_event_boundary` | `unknown` | `unknown` | True |
| 11337 | `abstain` | `trigger_conditioned_frequency` | `unknown` | `no seizure frequency reference` | True |
| 14040 | `abstain` | `missing_denominator_anchor` | `unknown` | `no seizure frequency reference` | True |
| 14810 | `human_review` | `last_event_boundary` | `1 per month` | `12 per month` | False |
| 14821 | `human_review` | `last_event_boundary` | `1 per month` | `17 per month` | False |