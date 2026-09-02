# Rendered prompt example

Prompt id: `gan_directional_evidence_adjudication_v1`  
Purpose: plain-language and visibility-boundary check; synthetic development example only.

## Reference-text arm

```text
Decide whether the supplied evidence supports the target current seizure-frequency answer.

Use only the supplied evidence, its event grouping, the target answer, and the decision policy.
Judge the evidence as a whole for this record. Do not add facts that are not stated in the supplied evidence.
Return supported when the supplied evidence is enough to justify the target answer under the policy.
Return unsupported when the supplied evidence points to a different answer or conflicts with the target.
Return insufficient when the supplied evidence does not contain enough information to decide.
Choose one or more policy-operation tags that explain the judgment. Use none only when no named operation is needed.
Return exactly one JSON object and no markdown.

Decision policy:
- The target is the patient's current seizure-frequency state.
- Prefer current or recent statements over historical statements when the policy identifies the current state.
- When an overall current count and a subtype breakdown both appear, use the overall count for the target rather than only a subtype count.
- Represent a stated rate or range, including a cluster rate, when the supplied evidence states it clearly.
- Use seizure-free when the supplied evidence states the current seizure-free state.
- Keep frequency unknown when seizures are discussed but the frequency cannot be determined.
- Use no reference only when there is no usable seizure-frequency evidence.
- When multiple current statements cannot be reconciled under these rules, treat the target as unresolved rather than inventing a resolution.

Target answer: 1 seizure per month
Evidence arm: reference_text
Reference text: "currently having one focal seizure each month"

Return JSON with judgment, reason, and policy_operations.
```

## Pipeline-extraction arm

```text
Decide whether the supplied evidence supports the target current seizure-frequency answer.

Use only the supplied evidence, its event grouping, the target answer, and the decision policy.
Judge the evidence as a whole for this record. Do not add facts that are not stated in the supplied evidence.
Return supported when the supplied evidence is enough to justify the target answer under the policy.
Return unsupported when the supplied evidence points to a different answer or conflicts with the target.
Return insufficient when the supplied evidence does not contain enough information to decide.
Choose one or more policy-operation tags that explain the judgment. Use none only when no named operation is needed.
Return exactly one JSON object and no markdown.

Decision policy:
- The target is the patient's current seizure-frequency state.
- Prefer current or recent statements over historical statements when the policy identifies the current state.
- When an overall current count and a subtype breakdown both appear, use the overall count for the target rather than only a subtype count.
- Represent a stated rate or range, including a cluster rate, when the supplied evidence states it clearly.
- Use seizure-free when the supplied evidence states the current seizure-free state.
- Keep frequency unknown when seizures are discussed but the frequency cannot be determined.
- Use no reference only when there is no usable seizure-frequency evidence.
- When multiple current statements cannot be reconciled under these rules, treat the target as unresolved rather than inventing a resolution.

Target answer: 1 seizure per month
Evidence arm: pipeline_spans
Event group g1:
- "one focal seizure each month"

Return JSON with judgment, reason, and policy_operations.
```

The pipeline rendering intentionally contains no full letter, predicted
answer, normalized candidate label, or annotation reference. The reference
rendering intentionally contains no pipeline event record.

Expected shape only (not a collected adjudication):

```json
{"judgment":"supported","reason":"The evidence states a current rate of one focal seizure each month.","policy_operations":["target_current_state","interpret_rate_or_range"]}
```
