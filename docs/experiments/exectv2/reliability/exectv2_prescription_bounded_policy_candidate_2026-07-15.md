# ExECTv2 bounded Prescription policy candidate result

Date: 2026-07-15  
Decision: reject under the predeclared gate; retain the implemented model-preserving fallback

## Answer

The bounded Prescription candidate is materially better than both the current
policy and the implemented fallback on the aggregate component counts, but it
does not pass the frozen zero-regression gate. It removes all 23 Prescription
correct-to-wrong changes, raises wrong-to-correct changes from 41 to 46, retains
40 of 41 comparator rescues, and retains all four demonstrated missing-regimen
rescue rows. It nevertheless makes one comparator-correct row wrong:
EA0141 under Qwen.

The candidate is therefore rejected for the next frozen comparison. No second
Prescription candidate will be tuned. The implemented
`decision_0040_model_preserving_dev140_v1` bundle remains the explicit fallback,
with its original failed rescue-retention gate disclosed. Diagnosis will be
evaluated once as a separate component before that fallback choice is frozen.

No test60 row was assembled or inspected, and no model was called.

## Fixed comparison

- Dataset and split: ExECTv2 dev140, with permitted row inspection.
- Inputs: saved GPT-4.1-mini, historical DeepSeek chat, and Qwen 3.6 35B repair
  v02 outputs.
- Comparator: current default decision-0040 model-led policy.
- Candidate: local selected-text frequency precedence, bounded preservation of
  explicitly current model facts, explicit-current residual recovery, and
  removal of the unanchored residual group.
- Fixed: candidate generation, other families, gold, evidence checks, and
  scorers.
- Primary scorer: family-local `clinical_headline_unit_keys`.

## Gate result

| Gate | Result |
|---|---:|
| Prescription correct-to-wrong below 23 | pass: 0 |
| Prescription wrong-to-correct at least 39 | pass: 46 |
| Retain at least 39 of 41 comparator rescues | pass: 40 |
| Retain all four demonstrated missing-regimen rescue rows | pass |
| Zero comparator-correct rows made wrong | **fail: 1** |
| Other families unchanged | pass: 0 changed rows |
| Exact evidence on every comparator-candidate change | pass: 34/34 |
| Retained residuals are explicit-current only | pass: 6/6 |
| No new call, parse/schema, or fallback failure | pass |

The failed row is EA0141 under Qwen. The model emitted two future Lamotrigine
targets from a start-and-titrate instruction. The comparator dropped both and
matched the empty Prescription gold. The candidate correctly rejected the
initial 25 mg start but preserved the later 75 mg twice-daily target because
the evidence contains `he is taking` after the titration instruction. This is
an exact-evidence temporal-selection error in the candidate's current guard.
The protocol forbids adding a post-replay row-, drug-, dose-, or model-specific
exception.

## Component ablations

The counts below are model-owned to final family-local directions across the
three saved outputs.

| Variant | Wrong to correct | Correct to wrong | Changed, still wrong | Residual groups retained |
|---|---:|---:|---:|---|
| Default comparator | 41 | 23 | 16 | 10 explicit-current; 9 unanchored |
| Local frequency scope only | 41 | 22 | 15 | 6 explicit-current; 9 unanchored |
| Current-selection guard only | 41 | 6 | 15 | 10 explicit-current; 9 unanchored |
| Explicit-current residual only | 46 | 18 | 12 | 10 explicit-current |
| Combined candidate | 46 | 0 | 10 | 6 explicit-current |

Local frequency scope is independently safe in this replay and removes one
regression. The current-selection guard produces the largest reduction in
harm, while the residual-group ablation supplies five additional rescues. Their
combination also changes which residual additions remain: model-owned facts
restored by local scope or current preservation no longer need duplicate
residual recovery.

The unanchored group is the harmful residual group in this study. Removing it
eliminates planned, conditional, rescue-only, and contextually incomplete
target-list additions while preserving the predeclared current-regimen rows.
This is a dev140 mechanism result, not evidence that the group is universally
unsafe.

## Demonstrated rescue retention

The combined candidate retains:

- EA0096 under historical DeepSeek and GPT-4.1-mini: the paired Topiramate
  evening dose;
- EA0127 under historical DeepSeek: Lamotrigine 100 mg twice daily from the
  medication list;
- EA0150 under Qwen: Levetiracetam 1500 mg and Lamotrigine 200 mg twice daily
  from explicit current-treatment evidence.

All retained residual additions are deterministic-owned
`explicit_current_regimen_recovery` decisions. They are hybrid facts and are
not credited to the model.

## Scores

| Saved model | Comparator overall F1 | Candidate overall F1 | Comparator Prescription F1 | Candidate Prescription F1 |
|---|---:|---:|---:|---:|
| Historical DeepSeek chat | 0.8747 | 0.8836 | 0.9268 | 0.9614 |
| GPT-4.1-mini | 0.8378 | 0.8461 | 0.8867 | 0.9193 |
| Qwen 3.6 35B repair v02 | 0.8565 | 0.8615 | 0.9481 | 0.9681 |

All aggregates improve, but they do not override the row-level gate.

## Fallback comparison and stop decision

The implemented model-preserving fallback has 35 Prescription rescues and six
Prescription correct-to-wrong changes; the bounded candidate has 46 and zero.
The bounded candidate also retains 40 of 41 old Prescription rescues, whereas
the fallback lost 11 Prescription rescues. Despite this improvement, the
predeclared zero-regression gate controls the candidate decision.

Per the user's explicit stopping preference, do not iterate on another
Prescription rule. Finish the separate Diagnosis guard evaluation, then choose
between the disclosed implemented fallback and any already implemented
component combination supported by that frozen evidence. Do not silently
promote this rejected candidate.

## Artifacts

- Protocol: `docs/experiments/exectv2/reliability/exectv2_prescription_bounded_policy_candidate_protocol_2026-07-15.md`
- Machine-readable result: `experiments/exectv2_prescription_bounded_policy_candidate_dev140_20260715.json`
- Replay: `.venv\Scripts\python.exe scripts/check_exectv2_prescription_bounded_policy_candidate.py`

## Claim boundary

This is inspected development evidence for three saved outputs. It is not
holdout evidence, cross-model validation for the unrun roster models, clinical
validation, or permission to inspect test60.
