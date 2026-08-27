# Category-cut representative examples protocol

Date: 2026-08-08  
Status: development-only companion artifacts  
Parent: [category-cut performance](six_model_category_cut_performance_2026-08-06.md)

## Question

Can the gold-defined category cuts be explained with real development examples
showing the source text, gold answer, and the outputs of rules, LLM, and
LLM-with-rules?

For ExECT, a category means a subtype **within one clinical family**. It does
not mean a whole-letter composition bucket. Examples therefore isolate the
relevant family and subtype; cross-family letter shape is optional context.

## Data and row policy

- Gan: `validation` / `dev750` from `data/Gan (2026)/synthetic_data_subset_1500.json`.
- ExECT: `dev` / `dev140` from `data/ExECTv2 (2025)/Gold1-200_corrected_spelling`.
- Development rows may be inspected. Locked Gan `test450` and ExECT test rows
  are not opened.
- One representative row is selected for every primary category in the
  category-cut report. Gan categories remain mutually exclusive per row. ExECT
  categories may share a letter because one letter can contain several family
  subtypes. Gan `ordinary_point_rate` has two rows because it is
  the dominant bucket: one simple shared-competence case and one more involved
  diary/counting case. Selection otherwise prefers rows where the three methods
  produce visibly different answers, then uses the lowest source identifier as
  a stable tie-breaker.

## Method surfaces

- Gan rules: retained deterministic three-way rules JSONL.
- Gan LLM: retained GPT-5.6 Sol `llm_only` JSONL.
- Gan LLM-with-rules: retained GPT-5.6 Sol matched attribution rows after
  deterministic repair.
- ExECT rules: regenerated four-family deterministic letter-score JSONL.
- ExECT LLM: GPT-5.6 Sol `raw_lane_mentions`.
- ExECT LLM-with-rules: GPT-5.6 Sol `predicted_mentions`.

The reports show source excerpts around the evidence retained by the methods
and the gold annotations. Exact evidence presence is a textual provenance
check, not an independent clinical-support or validation judgment.

ExECT selection prefers a row with a visible rules / LLM / hybrid difference
inside the named family-subtype slice, then uses the lowest letter identifier
as a stable tie-breaker. The rendered comparison must not average unrelated
families into the example's conclusion.

## Artifact and report

The generator is `scripts/build_category_cut_representative_examples.py`.
It writes one JSON artifact and two Markdown reports. No model calls are made.

## Claim boundary

These are explanatory development examples, not new performance estimates,
clinical validation, or holdout evidence. A single row does not represent the
distribution of its category. Aggregate competence remains owned by the
[category-cut performance report](six_model_category_cut_performance_2026-08-06.md).
