# 09 — Reliability across tasks

Last updated: 2026-07-18

Gan 2026 and ExECTv2 now use the same eight paper-facing reliability questions:

1. clinical correctness and generalization;
2. clinical selection and unsupported inference;
3. evidence support and faithfulness;
4. uncertainty and selective action;
5. robustness and stability;
6. component attribution and correction safety;
7. coverage and clinical-slice behavior; and
8. operational reliability.

The [canonical framework](../design/reliability_evaluation_framework.md)
defines the criteria, assurance gates, evidence states, row scopes, and
comparability rules. The
[machine scorecard](../../experiments/shared_reliability_scorecard_20260718.json)
and [generated report](../research/shared_reliability_scorecard_2026-07-18.md)
own the detailed results.

The tasks do not share one reliability metric. Gan is an exhaustive
single-label task; ExECT is a multi-mention extraction task. Their current
measurements are therefore `construct_only` except clinical selection and
unsupported inference, which is `not_comparable`. No cross-task numerical
delta or composite reliability score is reported.

## Maintained conclusion

Both tasks have retained evidence for all eight questions, but the evidence is
not equally complete:

- The fixed six-model panels provide task-specific correctness and aggregate
  holdout evidence. Sol leads ExECT test60 at `0.8047` clinical-headline F1;
  Qwen leads Gan test450 at `367/450` Purist.
- Exact source presence is measured separately from semantic support. The
  48-item ExECT dev140 semantic-support sample is prepared across six models
  and four families, but independent review has not started.
- Gan retains external-signal calibration and risk-coverage results for its
  named subject. ExECT retains an internal scoring-rule result and a historical
  three-model negative routing result; neither is a final six-model deployment
  policy.
- Existing robustness results cover named subdimensions. ExECT dev-to-test
  changes are not perturbation robustness, and Gan's repeated-temperature
  result remains a one-model study.
- Component results stay task-specific. The shared normalization ablation is
  `+0.0389` ExECT clinical-headline F1 and `+0.0293` Gan Purist accuracy. The
  ExECT six-model SF replay records 54 wrong-to-correct and one
  correct-to-wrong transition across 840 model-letter rows, representing 140
  unique letters.
- Clinical-family and seizure-band results are coverage evidence, not
  demographic fairness.
- Operational event counts are retained, but hosted and local conditions do
  not have matched latency, token, cost, hardware, or retry telemetry.

## Unsupported-selection boundary

The predeclared six-model ExECT `dev140` analogue has zero gold letters with the
unknown-only state set. The 41 empty-gold letters remain a separate diagnostic
because annotation omission, multiplicity, and accepted representation
differences prevent treating them as unknown after seeing the result.

Gan-to-ExECT over-reading transfer is therefore unsupported and not measurable
from the current ExECT gold. A future rate requires an independently governed,
exhaustively reviewed development substrate, not new model calls or reuse of
empty-gold rows.

## Claim boundary

The framework supports a bounded comparison of evidence about the same eight
questions. It does not establish a shared metric, a pooled capability ranking,
demographic fairness, deployment reliability, cross-task transfer, or
independent clinical validation.
