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
| Diagnosis | Historical GEPA run under the pre-D1 scorer: metric F1 0.6617 and internally adjusted F1 0.9501; current selected LLM-only run under the hierarchy-aware scorer: F1 0.6861, not yet adjudicated |
| Seizure frequency | 62.1% metric-defensible; 89.3% internally judged clinically defensible |

The same team produced and reviewed these outputs, so the paper must state that
limitation.

The [current Diagnosis audit substrate](../experiments/exectv2/diagnosis/exectv2_diagnosis_interpretation_audit_substrate_results_2026-07-14.md)
contains 246 unreviewed union disagreements across rules-only, LLM-only, and
LLM-with-rules dev140 outputs. Do not transfer the historical 0.9501 adjustment
onto the current 0.6861 scoring surface.

No selected ExECT report tests whether the Gan unknown-versus-rate problem
transfers across tasks.
