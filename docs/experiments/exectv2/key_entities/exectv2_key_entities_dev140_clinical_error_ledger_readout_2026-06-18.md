# ExECTv2 Key-Entity dev140 Clinical Error Ledger Readout

Date: 2026-06-18  
Split: dev140  
Inputs:
`exectv2_llm_only_key_entities_structured_v05_dev140_gpt41mini_20260618`,
`exectv2_llm_diagnosis_verifier_v05_dev140_gpt41mini_20260618`,
`exectv2_llm_sf_verifier_v03_dev140_gpt41mini_20260618`

## Decision

Use the dev140 clinical-recovery ledger as the control surface for the next
architecture iteration. The dev25 prompts were too local; the next work should
target the recurring dev140 key failures rather than adding more dev25 examples.

| Entity | F1 | Precision | Recall | Main residual shape |
| --- | ---: | ---: | ---: | --- |
| Prescription | 0.777 | 0.768 | 0.788 | titration/future-dose over-emission; missed current low-dose or rescue regimens |
| Diagnosis | 0.616 | 0.680 | 0.564 | generic epilepsy and seizure-type concept misses; specificity/parent-child mismatch |
| SeizureFrequency | 0.602 | 0.594 | 0.610 | generic seizure unknown/seizure-free/active-rate states; seizure-type over-emission |
| Investigations | 0.786 | 0.752 | 0.824 | performed-only over-emission; missing result attributes for MRI/EEG |

## High-Leverage Residuals

Prescription is close enough for a focused verifier or stricter medication
projection pass. The largest false-positive families are lamotrigine titration
targets (`75 mg bd`, `25 mg daily`) being treated as current ordinary regimens.
False negatives are mostly specific current regimens and rescue midazolam. This
suggests a current-medication verifier should separate current regimen, planned
titration, previous medication, and rescue medication before rendering.

Investigations is also close. False positives are mostly modality-only outputs
such as `MRI Yes` or `EEG Yes` without result/type, while false negatives are
gold `MRI/EEG Yes Abnormal` or `MRI/EEG Yes Normal`. The next prompt should
prefer omitting result-free planned tests unless explicitly performed, and should
extract normal/abnormal results when the performed test is present.

Diagnosis requires broader redesign. The top miss is generic affirmed
`epilepsy` (`68` misses), followed by symptomatic structural focal epilepsy,
tonic-clonic seizure concepts, and focal seizure concepts. The top over-emits
are related but mismatched concepts such as `tonic clonic seizures`,
`symptomatic structural epilepsy`, absences/absence seizures, and
certainty-shifted focal epilepsy. This is a concept hierarchy and assertion
normalization problem, not just evidence coverage.

SeizureFrequency also needs broader redesign. The leading misses are generic
`seizures` states: unknown (`16`), seizure-free (`14`), and active-rate (`9`).
The leading over-emissions are generic seizure active-rate, GTC active-rate,
generic seizure unknown, and bare `seizure free`. This points to a verifier
that first classifies named frequency statements by state, then decides whether
the generic seizure state is separately annotated from the specific seizure
type.

## Next Architecture Loop

1. Start with near-target families because they can unlock an early combined
   dev140 improvement: build a Prescription/Investigations verifier over the
   single structured draft.
2. Redesign Diagnosis as a concept-normalization verifier with explicit
   hierarchy handling: generic epilepsy, symptomatic structural focal epilepsy,
   seizure-type diagnoses, certainty, and suppression of non-diagnosis symptom
   terms.
3. Redesign SeizureFrequency as a state classifier over candidate frequency
   statements, with a separate decision for generic-vs-specific seizure type
   projection.
4. Keep the single structured prompt as the source substrate until a focused
   verifier proves it should be replaced.
