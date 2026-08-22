# Documentation navigation

Paper source library and current owners. Campaign reports and the
numbered decision series are not listed here. Recover them from git.
The dense pointer log is [decision history](history/decisions.md).

## Current owners

| Need | Read |
| --- | --- |
| Public front door | [README](../README.md) |
| What is present, missing, and allowed to run | [project status](../PROJECT_STATUS.md) |
| Paper methods, claims, lineage, decisions | [paper keep-set](paper/README.md) |
| Paper-final cut | [scope](plans/paper_final_repo_scope_2026-08-17.md) |
| Replayable cells | [paper experiments](../paper_experiments/README.md) |
| Live runner | `python -m clinical_extraction.paper` |
| How a record moves through a selected method | [architecture](architecture/README.md) |
| Assembly Line rebuild (one fact) | [scope](plans/assembly_line_one_fact_2026-08-18.md) |

## Paper source library

Use this path to write the paper without reopening the campaign
record:

1. [Why narrative epilepsy letters are a research problem](research/paper/why_narrative_letters_are_a_research_problem_2026-08-17.md)
2. [Why evidence, uncertainty, and human review belong together](research/paper/why_evidence_uncertainty_and_human_review_belong_together_2026-08-09.md)
3. [What the two golds already decided](research/paper/what_the_two_golds_already_decided_2026-08-17.md) — diagnostic owner: [why the two programmes annotated differently](research/shared/annotation_approach_comparison_2026-08-16.md)
4. [What the two extraction tasks ask](research/shared/task_shape_framework_2026-08-06.md)
5. [What prior extraction approaches already did](research/paper/what_prior_extraction_approaches_already_did_2026-08-17.md)
6. [Why the proposed method is a model plus recorded rules](research/paper/why_hybrid_architecture_2026-08-09.md) — the proposed method; phrase lists: [Gan](research/paper/gan_gold_phrase_variants_2026-08-13.md), [ExECT](research/paper/exect_gold_phrase_variants_2026-08-13.md)
7. [Five rungs of rule help](research/paper/five_rungs_of_rule_help_2026-08-20.md) — plain-language rungs; Gan row 10 and ExECT `EA0007`
7a. [Rule catalogue](research/paper/rule_catalogue_schema_format_post_2026-08-21.md) — named schema / format / post rules on both tasks
7b. [Rules and models across stages (Gan, Gemini)](research/paper/gan_rules_and_llms_across_stages_2026-08-21.md) — Gemini Gan reading of the locked five-cell grid; ExECT is a later report
8. [How the proposed method divides the work](research/artifacts/hybrid_architecture_2026-08-10.html)
9. [Parallel performance view](research/artifacts/parallel_two_task_performance_view_2026-08-09.html) — two holdout comparisons, kept separate. Tables cite Gemini; Grok is a companion row.
10. [Gan story](research/paper/gan_story_2026-08-10.md) and [ExECT story](research/paper/exect_story_2026-08-12.md) — ExECT hybrid numbers are Compact hybrid F1; standalone Compact LLM-only is raw F1 ([methods](paper/methods.md); [cells](../paper_experiments/exect/README.md))
11. [Component roles and limits](research/artifacts/paper_source_component_roles_and_limits_2026-08-09.pptx) — prose: [failures](research/paper/failures_and_limits_2026-08-10.md)
12. [Failures and limits](research/paper/failures_and_limits_2026-08-10.md)
13. [Two reviewable cases](research/paper/reviewable_case_pair_2026-08-09.md) and the [case explorer](research/artifacts/paired_case_explorer_2026-08-09.html)
14. [Rescue source provenance](research/shared/hybrid_rescue_source_provenance_2026-08-13.md) and its [exhibit](research/artifacts/rescue_source_provenance_2026-08-13.html)
15. [Flagship 3-letter suite](research/paper/flagship_3_letter_suite_2026-08-11.md) — development letters, not holdout
16. Row-evidence workbook — cited historically; the file is not in the keep-set. Use living `paper_experiments/` scored cells for Grok development rows.
17. [Reliability view](research/artifacts/reliability_view_2026-08-10.html)
18. [How the two tasks are scored](research/paper/score_definitions_2026-08-17.md) — writing glossary, not a scoring authority
19. [Related-work source map](research/paper/related_work_seed_2026-08-17.md)

The source library explains the evidence. It does not replace
[claims](paper/claims.md) or `paper_experiments/`.
