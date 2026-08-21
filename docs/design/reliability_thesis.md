# Reliability questions

Last updated: 2026-07-18

The paper-facing definitions are owned by the
[reliability evaluation framework](reliability_evaluation_framework.md). This
document keeps the research motivation and implementation constraints.

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
routing, consistency, distribution-shift, component, and runtime analyses. The
fixed ExECT package includes six-model dev140 and aggregate-only test60 results,
family and stage scores, component regressions, internal calibration, and the
historical three-model negative confidence result.

The predeclared six-model ExECT unsupported-selection analogue has a zero
unknown-only denominator, so cross-task over-reading transfer is not measurable
from current gold. Exact evidence is measured; semantic support remains open.
A stratified 48-item dev140 sample is prepared for independent review but has
no review conclusions.

## Required final outputs

For both tasks, report the eight shared criteria with task-specific measures,
component and rule-group ablations, evidence and schema validity, repair rates,
confidence results, and the source of each reported number. Keep component
effects separate from general reliability evidence and never calculate a
composite reliability score.

The paper is complete only when its stated claims match the selected evidence
and every open limitation is either answered or reported as unresolved.
