# 0044: Use shared reliability criteria with task-specific measures

Date: 2026-07-18
Status: accepted

## Decision

Gan 2026 and ExECTv2 will be assessed with the same eight reliability
questions. Each task will use measures that match its annotation and output
structure. Cross-task synthesis will state whether measurements are directly
comparable, comparable only as evidence about the same construct, or not
comparable.

The framework will not calculate an overall reliability score, average
criterion coverage, or weighted model ranking. Missing, diagnostic, and
incompatible results remain visible.

The canonical definitions and reporting rules are in the
[reliability evaluation framework](../design/reliability_evaluation_framework.md).

## Reason

Gan is an exhaustive single-label seizure-frequency task. ExECT is a
multi-mention extraction task with four fixed clinical families in the final
comparison and no valid unknown-only denominator. Reusing each Gan transform
as an ExECT metric would change the measurement object or require unsupported
annotation assumptions.

The previous ten-row Gan scorecard also mixed task correctness, calibration,
abstention, robustness, consistency, governance, clinical-family coverage,
and runtime evidence. It remains selected historical evidence for Gan, but it
is not a shared schema.

A composite score would hide the most important limitations: missing semantic
review, zero denominators, unequal model scope, sealed row access, and runtime
conditions that are not matched. Assurance requirements therefore block or
bound claims directly instead of lowering an average.

## Fixed criteria

1. Clinical correctness and generalization.
2. Clinical selection and unsupported inference.
3. Evidence support and faithfulness.
4. Uncertainty and selective action.
5. Robustness and stability.
6. Component attribution and correction safety.
7. Coverage and clinical-slice behavior.
8. Operational reliability.

Changing this set requires an amendment to this decision.

## Consequences

- Every task-by-criterion cell has an explicit result state, including a
  visible reason and unblock condition when it is not measurable.
- Every measured result records its model and runtime scope, split,
  denominator, scorer, output stage, repair policy, row-inspection rule,
  evidence state, source, and claim boundary.
- Exact source presence and semantic support are separate measurements.
- Calibration and review routing remain separate submeasures under one
  operational question.
- Robustness subdimensions remain separate; one subdimension cannot support a
  broad robustness claim.
- Clinical-family variation is reported as coverage or slice behavior, not
  demographic fairness.
- Aggregate-only holdout results cannot emit or depend on row-level material.
- A cross-task numerical delta is allowed only for a `direct` comparison.
- New model calls, locked-row inspection, scorer changes, and rule changes are
  outside this decision.

## Rejected alternatives

### Apply the Gan scorecard unchanged to ExECT

Rejected because several rows lack an equivalent ExECT measurement object or
valid denominator. Empty-gold ExECT letters cannot be relabelled as unknown.

### Require identical metrics for both tasks

Rejected because identical arithmetic over different annotation units would
look comparable while answering different clinical questions.

### Publish a composite reliability index

Rejected because weights would be arbitrary and strong measured criteria
could conceal missing or diagnostic evidence elsewhere.

## Evidence and owners

- Work breakdown: [shared reliability framework implementation plan](../plans/reliability_framework_implementation_plan_2026-07-18.md)
- Current claims: [paper claim status](../canon/10_paper_provenance.md)
- Selected files and hashes: [retained evidence index](../experiments/retained_evidence_manifest.md)
- Current work: [active roadmap](../plans/ACTIVE_ROADMAP.md)
