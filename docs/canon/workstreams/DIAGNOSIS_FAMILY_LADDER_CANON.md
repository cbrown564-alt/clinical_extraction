# Diagnosis evidence summary

Last updated: 2026-07-14

This small summary exists because the retained hashed Diagnosis row-analysis
report links here.

Historical verifier and reconciler candidates are not active source or retained
evidence. The current ExECT performance control is holistic assembly v08. The
retained Diagnosis evidence for paper claims is the
[canonical row analysis](../../experiments/exectv2/diagnosis/exectv2_dx_canonical_row_analysis_2026-06-30.md),
which reports historical pre-D1 metric F1 0.6617 and internally adjusted F1
0.9501 on dev140. That adjudication used the historical
`exectv2_gepa_multifamily_dedup` run. The current retained LLM-only comparator
is the separate `exectv2_gepa_dedup` artifact; its registry record reports
concept F1 moving from 0.6624 to 0.6861 under the D1 hierarchy-aware scorer. The
[audit substrate](../../experiments/exectv2/diagnosis/exectv2_diagnosis_interpretation_audit_substrate_results_2026-07-14.md)
defines a separate 246-row union across rules-only, LLM-only, and hybrid
outputs. That union is now completely reviewed: 173 rows are classified as
representation/evaluation issues, 72 as extraction errors, and one as
uncertain. The predeclared
[component comparison](../../experiments/exectv2/diagnosis/exectv2_diagnosis_component_comparison_2026-07-14.md)
reports sensitivity views and development candidates without changing gold or
the fixed scorer. The historical adjusted result must not be applied to this
population. No candidate is promoted, and clinical-validity claims still need
independent clinical review.

Use [ExECT scoring](../04_scoring.md) for the claim boundary and
[paper provenance](../10_paper_provenance.md) for permitted wording.

