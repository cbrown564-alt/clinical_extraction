# 0046: ExECT primary method comparison uses one-call Sol peers

Date: 2026-08-01  
Status: accepted  
Amends: paper-facing ExECT method identity implied by
[canon scoring](../canon/04_scoring.md) and
[paper provenance](../canon/10_paper_provenance.md)  
Does not change: [decision 0040](0040-final-exect-llm-with-rules-family-ownership.md)
family ownership, [decision 0041](0041-single-call-exect-model-comparison.md)
one-call architecture, or [decision 0045](0045-exect-default-policy-not-joint-combined.md)
`default` / `default` assembly

## Decision

The paper's **primary ExECT three-method comparison** uses:

| Method | Primary fill |
| --- | --- |
| Rules only | Sol-matched four-family `clinical_headline` / `headline_target` on deterministic rules-only predictions restricted to the four key families (all-nine extractors may run; non-key entities are excluded from this peer score only). Not the older multi-entity `clinical_recovery_scorecard` overall. |
| LLM only | GPT-5.6 Sol `raw_candidate` / `raw_lane_score` from the one-call four-family pipeline |
| LLM with rules | GPT-5.6 Sol Selected ExECT hybrid (one-call, decision 0040 / 0041, `default` / `default`) |

The comparison surface is matched four-family `clinical_headline` (Diagnosis,
Seizure Frequency, Prescription, Investigations). The nine-entity
paper-derived rules-only metrics remain a **secondary** published-metric
reference, not the three-method peer score.

Historical ExECT hybrid control (`v08`, clinical fact F1 `0.9189` on `dev140`)
is **demoted** from the primary hybrid method row. It may appear only in a
**secondary results table** with an explicit ownership caveat: it does not
satisfy decision 0040.

GEPA GPT-4.1-mini LLM-only (`0.7393`) remains a **historical / negative
architecture comparator**, not the primary peer of Sol hybrid.

## Split policy

- `dev140`: all three primary fills; rules-only is a no-call four-family
  re-score of retained deterministic outputs (row-level analysis permitted).
- `test60`: all three primary fills once aggregate-safe sources exist.
  - Sol LLM-only and Sol hybrid stage scores already exist in sealed
    aggregates; before the paper cites holdout LLM-only cells, promote a
    **public aggregate-only six-model `test60` stage panel** under
    `experiments/` with at least `raw_lane_score` vs final
    `clinical_headline` for all six models (primary table still cites Sol).
  - Rules-only four-family `clinical_headline` on `test60` is materialized as
    aggregate-only scoring (no row inspection): overall F1 `0.7154`.

Do not inspect sealed `test60` rows. Do not treat the Gan six-model LLM-only
`test450` panel as ExECT evidence.

## Why

The pipeline understandability review (finding 7) found that the manuscript's
ExECT three-method strip mixed incompatible experiments: nine-entity
rules-only published metrics, GEPA mini LLM-only, and historical `v08` hybrid
under a non-selected ownership pattern. Preferring `v08`'s higher headline
over the selected one-call architecture would make the paper's method story
false even if the number looked stronger.

Sol is the method-identity model for the primary hybrid and LLM-only rows
because it leads the retained six-model panels; the six-model tables remain
model-comparison evidence. LLM-only means `raw_lane_score`, not
`source_scored` and not GEPA, so the hybrid delta is attributable to
deterministic stages on the same Sol calls.

## Consequences

- Canon score tables, paper manuscript method rows, and architecture method
  cards that still present `v08` or GEPA as the primary ExECT hybrid /
  LLM-only peers are stale relative to this decision until updated.
- Evidence protocol A→B→C is complete (2026-08-01). Canon primary fills are
  recorded; residual manuscript wording drift remains a separate edit. `v08`
  and GEPA remain secondary / historical only.
- Do not reopen `v08` as the primary hybrid to recover `0.9189`.
- Do not put nine-entity published metrics beside Sol `0.81` / `0.89` as if
  they measured the same task.

## Evidence and glossary owners

- Evidence protocol (A → B → C):
  [primary method-comparison surface protocol](../experiments/exectv2/reliability/exectv2_primary_method_comparison_surface_protocol_2026-08-01.md)
- Phase A — public six-model `test60` stage panel:
  [stage panel report](../experiments/exectv2/reliability/exectv2_six_model_test60_stage_panel_2026-08-01.md)
  and [panel aggregate](../../experiments/exectv2_six_model_test60_stage_panel_20260801/panel_aggregate.json)
- Phase B — rules-only four-family `dev140`:
  [Phase B report](../experiments/exectv2/reliability/exectv2_rules_only_four_family_clinical_headline_dev140_2026-08-01.md)
  and [artifact](../../experiments/exectv2_rules_only_four_family_clinical_headline_dev140_20260801.json)
- Phase C — rules-only four-family aggregate-only `test60`:
  [Phase C report](../experiments/exectv2/reliability/exectv2_rules_only_four_family_clinical_headline_test60_2026-08-01.md)
  and [artifact](../../experiments/exectv2_rules_only_four_family_clinical_headline_test60_20260801.json)
- Review:
  [pipeline understandability review](../reviews/pipeline-understandability-review-2026-07-30.md)
- Selected hybrid architecture:
  [decision 0040](0040-final-exect-llm-with-rules-family-ownership.md),
  [decision 0041](0041-single-call-exect-model-comparison.md)
- Six-model panel:
  [six-model comparison report](../research/six_model_comparison_report_2026-07-18.md)
- Glossary terms: [CONTEXT.md](../../CONTEXT.md)
