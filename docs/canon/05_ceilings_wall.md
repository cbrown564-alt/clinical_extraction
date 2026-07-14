# 05 — Observed performance limits

Last updated: 2026-07-14

## Gan: ambiguous unknown-versus-rate cases

The saved Gan reliability analysis identifies cases where available signals do
not reliably distinguish an unknown frequency from a numeric rate. On locked
test450, the multi-model comparison scored 379/450 Purist and the single-pass
system scored 364/450. These are aggregate holdout results; the rows are not a
development resource.

## ExECT: annotation and representation disagreements

Selected diagnosis and seizure-frequency analyses found many disagreements
about multiplicity or output representation rather than a clearly wrong
clinical reading.

| Entity | Selected internal result |
| --- | --- |
| Diagnosis | Metric F1 0.6617; internally adjusted F1 0.9501 |
| Seizure frequency | 62.1% metric-defensible; 89.3% internally judged clinically defensible |

The same team produced and reviewed these outputs, so the paper must state that
limitation.

No selected ExECT report tests whether the Gan unknown-versus-rate problem
transfers across tasks.
