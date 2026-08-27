# 07 — ExECT results

Last updated: 2026-07-18

The main ExECT comparison covers diagnosis, seizure frequency, prescriptions,
and investigations.

| Method | Split | Result | Role |
| --- | --- | ---: | --- |
| Rules only, all nine entities | dev140 | strict item F1 0.3548 | Rules baseline |
| Rules only, all nine entities | dev140 | all-features macro item F1 0.6020 | Paper-derived metric development result |
| GEPA LLM only | dev140 | clinical fact F1 0.7393 | Negative comparison |
| LLM with rules (`v08`) | dev140 | clinical fact F1 0.9202 (superseded value 0.9189, pre the disclosed Diagnosis subsumption-guard fix, commit 41165adc, 2026-08-11) | Historical development control; deterministic Prescription producer and SF union do not meet decision 0040 |

## Historical three-model results

| Model | Full200 clinical fact F1 | Limit |
| --- | ---: | --- |
| GPT-4.1-mini | 0.8356 | Development-inclusive aggregate |
| DeepSeek V4 Flash, historical run | 0.8566 | Development-inclusive aggregate with incomplete runtime metadata; not final-report eligible |
| Qwen 3.6:35b, repair v02 | 0.8197 | Diagnostic aggregate |

This is not the planned six-model comparison. Full200 contains dev140 and
held-out test60, so it is not an independent holdout. The living roster is
Gemini 3.7 Flash, GPT-5.6 Luna, GPT-5.6 Sol, hosted DeepSeek V4 Flash, local Qwen
3.6:35B, and local Gemma 4 26B ([decision 0052](../decisions/0052-gemini-37-flash-holdout-six-model-slot.md)).
GPT-4.1-mini remains historical Decision 0039 evidence. DeepSeek V4 Flash uses the
`deepseek/deepseek-chat` API identifier. The retained historical row has
incomplete runtime metadata, so it does not satisfy the final condition. See
[decision 0039](../decisions/0039-final-exect-six-model-roster.md).

The historical rows also do not measure one consistent model-led method.
Prescription was supplied by the deterministic Prescription producer, and
Seizure Frequency included a union with an independent deterministic
extractor. The old Prescription and Seizure Frequency columns must not be used
as model-to-model results.

## Fixed six-model results

All six selected models completed the same decision-0041 one-call pipeline with
prompt `exectv2_hybrid_key_family_event_ledger_v0.9.24`, Diagnosis/Prescription
`default` / `default` assembly ([decision 0045](../decisions/0045-exect-default-policy-not-joint-combined.md)),
and the internal clinical fact recovery scorer (`clinical_headline`).

| Model | dev140 F1 | test60 F1 | Test operational result |
| --- | ---: | ---: | --- |
| Gemini 3.7 Flash | 0.9010 | 0.8459 | 59/59; live successor cell, `reasoning_effort=low` |
| GPT-5.6 Luna | 0.8965 | 0.8156 | 59/59; current-stack no-call |
| GPT-5.6 Sol | 0.9032 | 0.8289 | 59/59; current-stack no-call; paper method identity |
| DeepSeek V4 Flash | 0.9084 | 0.8292 | 59/59; current-stack no-call on 0731 sidecars |
| Qwen 3.6:35B | 0.8477 | 0.7970 | 59/59; current-stack no-call |
| Gemma 4 26B | 0.8046 | 0.7415 | 59/59; current-stack no-call; two empty-event letters scored empty |

Dev140 permits development inspection; test60 is frozen aggregate-only. The
test result is retained holdout evidence for this internal scorer, not the
published ExECT benchmark or clinical validation. Qwen and Gemma have the same
retained aggregate status as the four hosted conditions. Their provider route,
local runtime, and parse behavior remain explicit comparison caveats. See the
[hosted protocol and result](../experiments/exectv2/reliability/exectv2_hosted_test60_protocol_2026-07-15.md).

## Corrected model-led architecture candidates

[Decision 0040](../decisions/0040-final-exect-llm-with-rules-family-ownership.md)
requires the named model to supply the candidate facts for all four main
families. It permits attributable deterministic correction but prohibits the
Prescription substitution and Seizure Frequency extractor union.

A no-call full200 aggregate audit produced these candidate compatibility
scores from saved outputs:

| Model | Overall | Diagnosis | SF headline | SF `state_profile` | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| GPT-4.1-mini | 0.8171 | 0.8583 | 0.6501 | 0.7813 | 0.8700 | 0.8614 |
| DeepSeek V4 Flash API run, incomplete runtime metadata | 0.8543 | 0.8789 | 0.7146 | 0.8085 | 0.9057 | 0.9091 |
| Qwen 3.6:35B, repair v02 | 0.8234 | 0.8520 | 0.6343 | 0.7812 | 0.9220 | 0.8548 |

Durable decision-0040 configurations and a no-call Git-blob replay reproduce
these results, including the decision-0037 `state_profile`, exact-evidence,
schema/parse, fact-origin, and deterministic-regression records. They are
development-inclusive, aggregate-only, and unpromoted. Nonzero deterministic
correct-to-wrong counts prevent treating them as final model rows. See the
[component audit](../experiments/exectv2/reliability/exectv2_llm_with_rules_component_audit_2026-07-14.md).

The permitted dev140 mechanism analysis finds 160 wrong-to-correct, 41
correct-to-wrong, and 118 changed-still-wrong model/family rows, all with exact
evidence. Seizure Frequency has 38 rescues and zero local regressions;
Diagnosis has 18 regressions and Prescription has 23. Two bounded follow-up
studies are also complete. The Prescription candidate produced 46 rescues,
zero model-correct regressions, and 40/41 comparator-rescue retention, but made
EA0141/Qwen wrong from a comparator-correct result. The separate Diagnosis
guards produced 88 rescues and three regressions with 75/81 rescue retention,
but left the EA0117 synonym residual under all three models. Both failed their
predeclared mechanism gates. Further rule iteration is closed. A frozen joint
replay composes both implemented components exactly and is now the disclosed
fallback for the fixed comparison: 172 rescues, 3 regressions, and 153/160
current-policy rescues retained, compared with 161, 9, and 143/160 for the
previous fallback. The known component failures remain explicit caveats.
See the [dev140 regression analysis](../experiments/exectv2/reliability/exectv2_model_led_dev140_regression_analysis_2026-07-15.md),
[Prescription result](../experiments/exectv2/reliability/exectv2_prescription_bounded_policy_candidate_2026-07-15.md),
and [decision 0045](../decisions/0045-exect-default-policy-not-joint-combined.md)
for the archived Diagnosis-guard and joint-policy readouts.

The selected internal calibration result reports full200 Brier 0.2225, base-rate
Brier 0.2340, and ECE 0.0587. A separate frozen no-call replay evaluated
model-reported confidence on aggregate-only test60. Failure AUROC was 0.5394
for GPT-4.1-mini, 0.5503 for historical DeepSeek, and 0.4895 for Qwen. Neither
predeclared routing rule passed, so no confidence-based review policy was
adopted. This is negative evidence for the three saved outputs, not deployment
calibration or a final DeepSeek V4 Flash result.

## Published metric development replay

The no-call rules-only replay over all nine dev140 entity types produced macro
per-item F1 of 0.5687 for normalized phrase, 0.7144 for CUI, and 0.6020 for all
features. Macro per-letter F1 was 0.7518, 0.8534, and 0.7922 respectively. The
scorer follows the paper's entity-specific attribute policy: certainty for
Diagnosis and PatientHistory, and negation only for PatientHistory. The result verifies the
metric implementation on permitted development data; it does not reproduce the
paper's original system, annotation process, or 0.87/0.90 scores.

## Diagnosis review and development candidates

The completed 246-row dev140 Diagnosis review found 173
representation/evaluation issues, 72 extraction errors, and one uncertain row.
Keeping gold and the fixed scorer unchanged, the conservative sensitivity view
raises fixed Diagnosis F1 to 0.9344 for rules only, 0.8499 for LLM only, and
0.9789 for LLM with rules. Shared deterministic boundary fixes improve the
fixed rules-only score from 0.8599 to 0.8926, while the hybrid candidate moves
from 0.8984 to 0.9034. A fixed LLM-only prompt candidate regresses from 0.6861
to 0.6210 and is rejected. These are inspected dev140 development results; none
is promoted and test60 was not inspected. See the
[component comparison](../experiments/exectv2/diagnosis/exectv2_diagnosis_component_comparison_2026-07-14.md).

A later predeclared no-call GPT-4.1-mini ablation tested the structured
four-family output as the final Diagnosis producer under the same deterministic
policy. Diagnosis F1 fell from `0.8727` to `0.8542`; 3 letters were rescued and
11 comparator-correct letters regressed. Exact evidence remained `1.0`, but the
candidate missed named seizure diagnoses and added non-target concepts. The
candidate failed its experimental gate. Decision 0041 nevertheless selects it
for the final comparison because the small final-F1 gain does not justify a
second model pass. During pre-score validation, the study
also found that the initial six-model runner selected the first 140 sorted
letters rather than manifest dev140. Affected partial runs are excluded, and
the corrected runner now enforces manifest IDs before starting or resuming.
See the [single-call Diagnosis ablation](../experiments/exectv2/diagnosis/exectv2_gpt41mini_single_call_diagnosis_ablation_2026-07-15.md).

The common six-model panel is complete and hash-selected in the retained
evidence index. Independent clinical review is still required for
clinical-validity claims about the Diagnosis interpretation decisions.
