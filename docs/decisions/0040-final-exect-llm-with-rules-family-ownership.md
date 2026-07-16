# 0040: Final ExECT LLM-with-rules family ownership

Date: 2026-07-15  
Status: accepted and implemented; disclosed fallback selected, final model rows not promoted

## Decision

The final ExECT model comparison uses a model-led pipeline for all four main
entity families. A method is called **LLM with rules** only when the named model
produces the candidate clinical facts and every prediction-changing
deterministic step remains visible and attributable.

| Family | Required model-owned input | Permitted deterministic work | Prohibited substitution |
| --- | --- | --- | --- |
| Diagnosis | Named model's Diagnosis concepts, assertions, and evidence | Normalize concepts; apply the accepted heading, boundary, and residual recovery rules; record every rule-added or rule-selected fact | Replacing the model's Diagnosis output with a rules-only diagnosis extractor |
| Seizure Frequency | Named model's structured seizure-frequency facts and evidence | Project model-selected operands into the state representation; suppress unsupported or contradictory states; record semantic changes as deterministic-owned | Union with an independent rules-only seizure-frequency extractor |
| Prescription | Named model's medication regimen facts and evidence | Normalize drug, dose, unit, and schedule; split supported regimens; remove unsupported facts; apply bounded regimen repair; record rule-added facts | Replacing the model's Prescription output with the deterministic all-entity extractor or deterministic-only Prescription lane |
| Investigations | Named model's investigation findings and evidence | Validate schema and exact evidence; normalize and deduplicate without selecting a different clinical finding | Replacing the model output with an independent deterministic investigation extractor |

A deterministic step that adds, removes, chooses, or changes a clinical fact is
clinical selection, even when the code calls it projection, repair, or
normalization. The final method may still be hybrid, but that decision is not
credited to the LLM. Mechanical schema and rendering repair may remain
deterministic without changing clinical ownership.

## Evidence and score boundary

The 2026-07-14 saved-output audit shows that the recorded three-model
Prescription lane was deterministic-only and the Seizure Frequency lane
included an independent deterministic extractor union. Those historical
columns therefore do not constitute a consistent model comparison.

The selected `v08` score of `0.9189` uses the same ownership pattern: a
deterministic Prescription producer and a Seizure Frequency union. It remains
a reproducible historical development control, but it does not satisfy the
final model-led family contract in this decision.

The same audit produced corrected aggregate candidates from saved full200
outputs. Durable configurations now reproduce the model origin, permitted
corrections, scores, `state_profile`, exact-evidence rate, schema/parse counts,
fact-origin counts, and deterministic regression counts through the no-call
architecture check. They remain development-inclusive, aggregate-only
architecture evidence rather than final model results.

Diagnosis development candidates remain governed by the completed dev140
component comparison. Decision 0040 defines ownership; it does not promote the
Diagnosis candidate, change gold, change a scorer, or authorize inspection of
test60 rows.

Seizure Frequency must report the `state_profile` score required by decision
0037. The older `clinical_headline` family value may be retained as a
compatibility score. Overall ExECT reporting continues to use the declared
comparison scorer and must disclose its entity-agnostic recall behavior.

## Consequences

- New six-model configurations must select the named model's Prescription
  output and its pre-union Seizure Frequency output.
- Every final fact must retain model origin, deterministic changes, evidence
  status, and the first prediction-changing owner.
- Promotion requires reproducible configurations, machine-readable aggregate
  results, exact-evidence accounting, schema/parse failures, rule-added and
  rule-removed fact counts, and regression accounting on permitted data.
- The verified replay has nonzero deterministic correct-to-wrong counts in
  Diagnosis and Prescription for all three historical conditions, and one in
  Seizure Frequency for GPT-4.1-mini and DeepSeek. Those rules are not promoted
  as a safe final policy without a permitted dev140 decision and a frozen rerun.
- The permitted dev140 decision retains Seizure Frequency projection and
  suppression plus the Investigations adapter. It does not promote the current
  Diagnosis or Prescription policies. Two bounded follow-up studies are now
  complete. The Prescription candidate removed all 23 model-correct regressions,
  produced 46 rescues, and retained 40/41 comparator rescues, but made one
  comparator-correct row wrong. The separate Diagnosis guards produced 88
  rescues with three regressions and retained 75/81 comparator rescues, but left
  the EA0117 synonym-residual regression under all three saved models. Both
  candidates failed their predeclared gates and were not independently promoted.
- A frozen joint replay then composed the already implemented bounded
  Prescription and combined Diagnosis components. The joint result reproduces
  both separate component maps exactly, produces 172 rescues with 3 regressions,
  and retains 153/160 current-policy rescues. It dominates the previous
  `decision_0040_model_preserving_dev140_v1` fallback at 161, 9, and 143/160,
  makes no fallback-correct row wrong, and improves all three saved model scores.
  `decision_0040_joint_bounded_dev140_v1` is therefore the disclosed fallback
  for the next fixed comparison. The known EA0117 Diagnosis and EA0141/Qwen
  Prescription failures remain explicit development caveats.
- The historical three-model scores remain audit evidence only. They must not
  be presented as the final model comparison.
- A predeclared GPT-4.1-mini dev140 replay tested whether the structured
  four-family output could also own final Diagnosis. The one-call candidate
  reduced final Diagnosis F1 from `0.8727` to `0.8542`, with 3 letter-level
  rescues and 11 regressions, so it failed its experimental gate. Subsequent
  [decision 0041](0041-single-call-exect-model-comparison.md) nevertheless
  selects the structured producer for the final comparison because the small
  final-F1 gain does not justify a second model pass. The negative ablation
  remains the evidence for the accepted quality tradeoff.
- The same study found that the initial six-model runner used the first 140
  alphabetically ordered letters rather than the manifest dev140 split. Only
  94 IDs overlapped. Affected live runs were stopped, their partial artifacts
  are not evidence, and the runner now selects manifest rows and rejects
  contaminated resume artifacts.
- Decision 0032 continues to govern finding assembly, decision 0037 governs
  the primary Seizure Frequency metric, and decision 0039 governs the final
  six-model roster.

Evidence owners:

- [Diagnosis component comparison](../experiments/exectv2/diagnosis/exectv2_diagnosis_component_comparison_2026-07-14.md)
- [LLM-with-rules component audit](../experiments/exectv2/reliability/exectv2_llm_with_rules_component_audit_2026-07-14.md)
- [Bounded Prescription policy result](../experiments/exectv2/reliability/exectv2_prescription_bounded_policy_candidate_2026-07-15.md)
- [Diagnosis guard ablation result](../experiments/exectv2/reliability/exectv2_diagnosis_guard_ablation_2026-07-15.md)
- [Joint bounded-policy result](../experiments/exectv2/reliability/exectv2_joint_bounded_policy_replay_2026-07-15.md)
- [GPT-4.1-mini single-call Diagnosis ablation](../experiments/exectv2/diagnosis/exectv2_gpt41mini_single_call_diagnosis_ablation_2026-07-15.md)
