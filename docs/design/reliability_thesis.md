# Reliability questions

Last updated: 2026-07-15

The paper asks whether one modular package can produce reliable, inspectable
clinical extraction results on two epilepsy-letter tasks.

## What reliability means here

Reliability is not one score. A result must state:

- how it behaves beyond the data used to tune it;
- whether available confidence or risk signals identify likely errors;
- whether its evidence is present in the note;
- which component caused each improvement or regression;
- whether the run can be replayed from selected files.

Gan 2026 tests deep extraction of current seizure frequency. ExECTv2 tests
broader extraction of nine entity types and attributes. Seizure frequency links
the tasks because it requires count, period, temporal anchor, and seizure-free
reasoning in both datasets.

## What the code must preserve

- Shared code belongs in `core`; dataset and clinical policy stay under `tasks`.
- Loading, extraction, selection, normalization, evidence checking, and scoring
  remain separate.
- Rules are labelled by expected portability and can be removed for comparison.
- ExECT scoring uses normalized labels rather than unreliable gold character
  offsets, consistent with the published comparison method.
- Every run records the model, prompt, scorer, split, repair policy, and row rule.

## Evidence currently available

The selected Gan package includes aggregate grounding, calibration, review
routing, consistency, distribution-shift, and runtime analyses. The selected
ExECT package includes internal full200 calibration and three historical model
runs using the same component graph. The graph used a deterministic
Prescription producer and an independent Seizure Frequency extractor union,
so those family columns are not a consistent model-led comparison. These
results are not deployment calibration, an independent holdout, or proof that
one component caused the score difference.

The frozen aggregate-only test60 replay found that model-reported confidence
did not meet the predeclared informativeness and review-routing gates for any
of the three historical model outputs. No confidence-based review policy was
adopted. Cross-task unknown-versus-rate behavior, the decision-0040
architecture promotion, and a strict six-model comparison remain open.

## Required final outputs

For both tasks, report the three methods, component and rule-group ablations,
error types and examples, evidence and schema validity, repair rates, confidence
results, and the source of each reported number. Keep component effects separate
from general reliability evidence.

The paper is complete only when its stated claims match the selected evidence
and every open limitation is either answered or reported as unresolved.
