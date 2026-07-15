# 0040: Final ExECT LLM-with-rules family ownership

Date: 2026-07-15  
Status: accepted and implemented; architecture replay verified, final model rows not promoted

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
  Diagnosis or Prescription policies: the next predeclared candidate should
  disable Prescription residual additions and revise the Diagnosis subsumption
  and Prescription current-versus-future boundaries. See the linked component
  audit for the row-level evidence.
- The historical three-model scores remain audit evidence only. They must not
  be presented as the final model comparison.
- Decision 0032 continues to govern finding assembly, decision 0037 governs
  the primary Seizure Frequency metric, and decision 0039 governs the final
  six-model roster.

Evidence owners:

- [Diagnosis component comparison](../experiments/exectv2/diagnosis/exectv2_diagnosis_component_comparison_2026-07-14.md)
- [LLM-with-rules component audit](../experiments/exectv2/reliability/exectv2_llm_with_rules_component_audit_2026-07-14.md)
