# ExECTv2 Final Key-Family Architecture Synthesis

Date: 2026-06-18
Scope: Prescription/medication, Diagnosis, SeizureFrequency, Investigations on
dev140.
Status: paper-table scaffold and final current synthesis; not a
benchmark-complete claim.

## Bottom Line

The ExECTv2 key-family architecture is best described as a shared structured
draft plus family-specific adjudication. That architecture clears two key
families on dev140, improves a third, and exposes a ceiling in the fourth:

- Prescription/medication clears with a focused regimen verifier.
- Investigations clears with a dedicated performed/result verifier.
- SeizureFrequency improves after deterministic state projection, but remains
  below target.
- Diagnosis is a grounded clinical-selection and annotation-scope ceiling on the
  current candidate set.

The result is scientifically useful, but it is not a solved four-family
benchmark architecture.

## Paper Table 1: Current Dev140 Family Results

| Family | Current candidate | F1 | Precision | Recall | Interpretation |
| --- | --- | ---: | ---: | ---: | --- |
| Prescription / medication | Prescription verifier v0.1 | 0.817 | 0.773 | 0.865 | Clears target; compact regimen decision table transfers |
| Investigations | Investigations verifier v0.1 | 0.872 | 0.869 | 0.875 | Clears target; performed/result decomposition transfers |
| SeizureFrequency | SF state projection v0.6 | 0.763 | 0.722 | 0.807 | Partial gain; state projection helps but does not clear |
| Diagnosis | Diagnosis reconciler v0.1 | 0.658 | 0.658 | 0.658 | Ceiling/annotation-scope characterization |

Recommended caption:

> Current best ExECTv2 key-family candidates on dev140. Prescription and
> Investigations clear the target with focused verifier stages. Deterministic
> SeizureFrequency state projection improves recall but remains below target.
> Diagnosis remains below target even under generous convention-oracle analysis.

## Paper Table 2: Architecture Ownership

| Family | Shared substrate | Final selector / adjudicator | Deterministic layer | Read |
| --- | --- | --- | --- | --- |
| Prescription / medication | Single structured key-family draft | Prescription verifier v0.1 | Evidence gate + finite CUI/regimen projection | Use |
| Investigations | Single structured key-family draft | Investigations verifier v0.1 | Evidence gate + modality/result projection | Use |
| SeizureFrequency | Structured draft + candidate spans | State adjudicator v0.5 + deterministic state projection v0.6 | Evidence gate + SF state/CUI projection | Partial gain |
| Diagnosis | Verifier/decomposer candidates | Diagnosis reconciler v0.1 | Evidence gate + benchmark projection | Characterize |

Recommended caption:

> The final current architecture is hybrid in the research sense: LLM stages
> select prediction-bearing clinical candidates, while deterministic stages
> validate evidence and apply finite benchmark-format or state-projection rules.
> Decision units differ by family because the clinical recovery problem differs
> by family.

## Paper Table 3: Why dev25 Was Not Enough

| Family | dev25 target-clearing candidate | dev25 F1 | dev140 F1 | Lesson |
| --- | --- | ---: | ---: | --- |
| Prescription / medication | Single structured v0.5 | 0.897 | 0.777 | Needed focused dev140 verifier |
| Diagnosis | Diagnosis verifier v0.5 | 0.837 | 0.616 | Local prompt/gate success did not transfer |
| SeizureFrequency | SF verifier v0.3 | 0.831 | 0.602 | Needed candidate/state decomposition |
| Investigations | Single structured v0.5 | 0.837 | 0.786 | Needed dedicated performed/result verifier |

Recommended caption:

> dev25 was useful for schema safety and prompt iteration, but target-clearing
> dev25 runs did not transfer to dev140. Candidate promotion should be based on
> residual-led dev140 evidence rather than pilot success.

## Paper Table 4: Convention And Ceiling Analysis

| Family | Base F1 | Convention-oracle F1 | Achieved after projection | Crosses `0.8`? | Interpretation |
| --- | ---: | ---: | ---: | :---: | --- |
| Diagnosis | 0.658 | 0.791 | n/a | No | Convention alignment cannot legitimately clear the gate |
| SeizureFrequency | 0.721 | 0.805 | 0.763 | No | Oracle shows headroom; finite state projection recovers only part |

Recommended caption:

> Residual convention decomposition separates the two below-target families.
> SeizureFrequency has an oracle path just above `0.8`, but the predeclared
> deterministic projection reaches only `0.763`. Diagnosis remains below `0.8`
> even under a generous convention oracle.

## Claim Language

Supported:

> A single structured key-family prompt provides a useful evidence-grounded
> substrate, but reliable ExECTv2 clinical recovery requires family-specific
> verifier/adjudicator stages whose decision units match the clinical structure
> of each entity family.

Supported:

> Medication and Investigations clear the current dev140 target with focused
> verifier stages, while Diagnosis and SeizureFrequency expose harder
> concept/state ownership problems.

Supported:

> Deterministic SF state projection over adjudicator candidates improves dev140
> clinical-recovery F1 from `0.721` to `0.763`, but does not clear the `0.8`
> target; the convention oracle is an upper bound rather than achieved evidence.

Supported:

> Diagnosis evidence validity is high, but the dev140 `0.8` gate is not
> reachable through legitimate convention alignment over the current candidate
> set.

Not supported:

> The ExECTv2 key-family architecture beats the benchmark target across all four
> families.

Not supported:

> Diagnosis can reach benchmark-F1 `0.8` through another verifier or accept/reject
> gate over the current candidate set.

Not supported:

> SeizureFrequency clears `0.8` after deterministic convention projection.

## Next Work, If Any

The only metric-oriented next SF loop justified by the evidence is a narrow,
predeclared unknown-suppression hard-slice study. It should target the 22
unknown-state false positives left after v0.6 and stop if active-rate or
seizure-free recall regresses. The predeclaration is:
`docs/experiments/exectv2/seizure_frequency/exectv2_sf_unknown_suppression_hard_slice_predeclaration_2026-06-18.md`.

Diagnosis should not continue as local target chasing. A future Diagnosis
attempt would need a genuinely new evidence-selection architecture or a
different evaluation target, not another gate over the same candidate set.

Any full-200 audit remains blocked until benchmark-beating dev evidence exists
and the architecture, artifacts, metrics, and no-row-level-tuning policy are
predeclared.

## Source Artifacts

- Interim architecture report:
  `docs/research/exectv2_key_entity_architecture_research_report_2026-06-18.md`
- Residual convention decomposition:
  `docs/research/exectv2_residual_convention_decomposition_2026-06-18.md`
- SF v0.6 readout:
  `docs/research/exectv2_sf_state_projection_v06_readout_2026-06-18.md`
- SF hard-slice diagnostic:
  `experiments/exectv2_sf_v06_hard_slice_diagnostic_dev140_20260618.md`
- SF unknown-suppression predeclaration:
  `docs/experiments/exectv2/seizure_frequency/exectv2_sf_unknown_suppression_hard_slice_predeclaration_2026-06-18.md`
- Diagnosis ceiling note:
  `docs/research/exectv2_diagnosis_ceiling_note_2026-06-18.md`
- Combined key-family ledger:
  `experiments/exectv2_key_entities_clinical_error_ledger_v06sf_dev140_20260618.md`
