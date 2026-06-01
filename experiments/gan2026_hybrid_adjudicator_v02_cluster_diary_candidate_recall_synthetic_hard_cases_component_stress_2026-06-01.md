# Gan 2026 Hybrid Adjudicator V0.2 Synthetic Hard-Case Component Stress

This is a reviewed synthetic development panel. It is not validation, holdout, or a benchmark claim.

- Split: `synthetic_hard_cases`
- Split manifest: `gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_2026-06-01`
- Source artifact: `experiments/gan2026_hybrid_adjudicator_v02_cluster_diary_candidate_recall_synthetic_hard_cases_gpt41mini_live_2026-06-01.jsonl`
- Candidate revision: `cluster_diary_candidate_recall`

## Component Summary

| Condition | Rows | Purist | Pragmatic | Changed | Improved | Regressed | Issues |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| deterministic_candidate_generator_top | 56 | 0.6964 | 0.7500 | 0 | 0 | 0 | 0 |
| raw_llm_adjudicator_final | 56 | 0.9286 | 0.9286 | 15 | 13 | 0 | 1 |
| conservative_llm_adjudicator_final | 56 | 0.8929 | 0.8929 | 13 | 11 | 0 | 3 |

## Failure Families

| Family | Rows | Deterministic correct | Raw correct | Gated correct | Raw W->C | Raw C->W | Gated W->C | Gated C->W |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| cluster_dual_axis | 8 | 3 | 8 | 8 | 5 | 0 | 5 | 0 |
| diary_distributed_counts | 8 | 5 | 8 | 8 | 3 | 0 | 3 | 0 |
| proxy_distractor_context | 8 | 6 | 8 | 6 | 2 | 0 | 0 | 0 |
| seizure_free_boundary | 8 | 6 | 6 | 6 | 0 | 0 | 0 | 0 |
| shorthand_ranges | 8 | 5 | 6 | 6 | 1 | 0 | 1 | 0 |
| temporal_conflict | 8 | 6 | 8 | 8 | 2 | 0 | 2 | 0 |
| unknown_no_reference_boundary | 8 | 8 | 8 | 8 | 0 | 0 | 0 | 0 |
