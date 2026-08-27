# ExECTv2 Prescription lens on/off counterfactual

Date: 2026-08-06  
Status: development no-call counterfactual  
Paper-library role: ExECT counterfactual record; start with [failures and limits](../paper/failures_and_limits_2026-08-10.md)

Protocol: recovered from git history; this report is the answer.  
Parent: [cross-task hybrid mechanism synthesis](../shared/cross_task_hybrid_mechanism_synthesis_2026-08-06.md)  
Companion: [ExECT hybrid stage ablation](hybrid_stage_ablation_2026-08-06.md)  
Artifact: [`experiments/exectv2_prescription_lens_counterfactual_20260806.json`](../../experiments/exectv2_prescription_lens_counterfactual_20260806.json)

## Plain answer

mixed_metric_split: lens-off raises Prescription letter exactness and net cell rescue (60 rescue / 44 harm) but mean Prescription F1 does not improve; no default rewrite.

On 830 letter×model cells: Prescription letter exactness **0.811** (default-on) vs **0.830** (lens-off); Δ +0.019. Mean Prescription F1 **0.916** vs **0.915**; Δ -0.002. Changed cells: lens-off rescue 60, harm 44.

## Arms

| Arm | Prescription lens |
| --- | --- |
| `default_on` | selected `prescription_dictionary_v09` |
| `lens_off` | thin `PrescriptionLens` identity (study-local) |

Dx / SF / Investigations lenses, SF projection, and evidence gate stay on the selected path. Production defaults are not changed.

## Prescription letter exactness

| Arm | Exact rate | Evidence-gate pass | Top modes |
| --- | ---: | ---: | --- |
| `default_on` | 0.811 | 1.000 | `correct_nonempty` 534, `correct_empty` 139, `missed_only` 61, `extra_only` 36 |
| `lens_off` | 0.830 | 1.000 | `correct_nonempty` 562, `correct_empty` 127, `missed_only` 41, `extra_only` 36 |

## Clinical-headline F1 (mean across six models)

| Arm | Prescription F1 | Four-family F1 |
| --- | ---: | ---: |
| `default_on` | 0.916 | 0.857 |
| `lens_off` | 0.915 | 0.857 |

## Transitions (lens-off vs default-on)

| Transition | Count |
| --- | ---: |
| `unchanged` | 715 |
| `mode_reshape_same_exactness` | 11 |
| `lens_off_harm` | 44 |
| `lens_off_rescue` | 60 |

### Rescue examples (lens-off fixes default wrong)

- **EA0008 / GPT-5.6 Sol.** `missed_all` → `correct_nonempty`. Default keys []; lens-off ["('ordinary', 'lamotrigine', '75', 'mg', '2')"].
- **EA0046 / GPT-5.6 Sol.** `missed_only` → `correct_nonempty`. Default keys ["('ordinary', 'levetiracetam', '750', 'mg', '2')"]; lens-off ["('ordinary', 'levetiracetam', '750', 'mg', '2')", "('ordinary', 'phenytoin', '100', 'mg', '1')"].

### Harm examples (lens-off breaks default correct)

- **EA0038 / GPT-5.6 Sol.** `correct_nonempty` → `substituted_or_mixed`. Default keys ["('ordinary', 'carbamazepine', '400', 'mg', '1')", "('ordinary', 'carbamazepine', '400', 'mg', '1')", "('ordinary', 'carbamazepine', '200', 'mg', '1')", "('ordinary', 'zonisamide', '50', 'mg', '2')", "('ordinary', 'clobazam', '10', 'mg', '2')"]; lens-off ["('ordinary', 'carbamazepine', '400/400/200', 'mg', '3')", "('ordinary', 'zonisamide', '50', 'mg', '2')", "('ordinary', 'clobazam', '10', 'mg', '2')"].
- **EA0068 / GPT-5.6 Sol.** `correct_empty` → `empty_gold_spurious`. Default keys []; lens-off ["('rescue', 'midazolam', 'as_required')"].

## Fidelity

- Replayable pairs: 830 / 840
- Default-on Rx keys match retained predicted_mentions: 1.000

## Decision boundary

mixed_metric_split: lens-off raises Prescription letter exactness and net cell rescue (60 rescue / 44 harm) but mean Prescription F1 does not improve; no default rewrite.

This does **not** change Decision 0045/0046 defaults. A default rewrite would need a separate predeclared protocol (including holdout aggregates if promotion is intended).

## Next

1. Operational primary remains the vLLM dev10 task.
2. If policy work continues: only then predeclare a default-change candidate with holdout gates.
3. Do not merge this thin-lens arm into production manifests from this page.

## Method

- Split: ExECT `dev140`; six retained structured sidecars.
- Dual ordered replay through evidence gate.
- Primary: Prescription unit-key letter exactness.
- Secondary: mean Prescription / four-family clinical-headline F1.
- Git: `922ff314` (dirty tree).

## Claim boundary

Development Prescription lens on/off counterfactual on ExECT dev140. Study-local thin-lens arm only. Not a Decision 0046 or default-policy rewrite. Not holdout competence.
