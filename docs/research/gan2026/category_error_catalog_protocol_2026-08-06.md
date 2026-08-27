# Protocol: Gan 2026 full category error catalog

Date: 2026-08-06  
Status: complete; no-call development catalog with ablation reading  
Parent: [category-cut performance](../shared/six_model_category_cut_performance_2026-08-06.md)  
Report: [category error catalog](category_error_catalog_2026-08-06.md)

## Primary question

For **every** Gan a_priori gold bucket on `dev750`, on both `llm` and
`llm_with_rules`, which error modes dominate six-model wrongs; how do the
observable pipeline layers (raw model label → format repair → semantic rules)
erase, reshape, or amplify those modes; and what do concrete development
examples look like?

## Why it matters

Hard-slice work covered only ordinary rates and clusters. Easy and mid buckets
still have characteristic failures (especially on `llm`), and hybrid residuals
on near-ceiling buckets matter for claim wording. A mode dump alone is hard to
use; the report must make the ablation readable at a glance.

## Scope

| Item | Value |
| --- | --- |
| Split | Gan `dev750` (`validation`); development inspection permitted |
| Surfaces | `llm` (`*--llm_only.jsonl`); `llm_with_rules` (v0.5 attribution + floors patch) |
| Buckets | all a_priori gold buckets with n≥1 on `dev750` |
| Metric | Purist correctness |
| Calls | none; retained artifacts only |
| Holdout | sealed |

## Method

1. Assign each gold row to its a_priori bucket (same taxonomy as category-cut).
2. For each model × surface × bucket, count Purist wrongs by mutually exclusive
   predicted-shape error modes (bucket-aware cluster refinements retained).
3. Record raw-model-label modes on `llm` as diagnostics when they differ from
   the scored label (format-repair ablation). JSON fields may still say
   `model_boundary_*` for historical reasons.
4. Contrast pooled mode counts `llm` vs `llm_with_rules` (semantic-rules
   ablation over retained surfaces—not leave-one-repair-out).
5. Select up to two development examples per mode per bucket×surface for the
   machine artifact (consensus wrongs preferred; Sol/Luna preferred; saved
   evidence spans only). The narrative report keeps signature examples and
   points to JSON for the full catalog.
6. Emit one machine artifact and one ablation-first narrative report.

## Stop rule

Answer when every `dev750` a_priori bucket has mode counts on both surfaces,
raw-vs-scored and llm-vs-hybrid mode deltas are reported for the main
buckets, and every observed mode with at least one wrong has an artifact
example (or an explicit “no retained example” note for empty cells).

## Claim boundary

Development category error catalog. Mode labels are analyst heuristics over
saved predictions. Ablation is across retained label stages / surfaces, not a
full repair-rule factorial. Not holdout competence; not a Decision 0046 rewrite.
