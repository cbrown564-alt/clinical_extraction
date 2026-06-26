# Gan 2026 Phase 1 Three-Way Architecture Comparison (openai/gpt-4.1-mini, validation750)

Phase 1 three-way architecture comparison, openai/gpt-4.1-mini pass, validation750 only. No test450 read, no holdout-facing or benchmark-comparable claim. Compares six PipelineArchitecture configs on the axes that are universally meaningful (rendered/null disposition, Purist/Pragmatic-correct of rendered rows, evidence-trace validity, final-answer distribution); hybrid additionally carries a routing-taxonomy appendix that no other architecture has an analogous surface for.

## Artifacts

- Comparison JSONL: `experiments\gan2026_three_way_comparison_phase1_report_gpt41mini_validation750_2026-06-08.jsonl`
- Summary JSON: `experiments\gan2026_three_way_comparison_phase1_report_gpt41mini_validation750_2026-06-08.json`
- Model: `openai/gpt-4.1-mini`
- Split: `validation`

## Shared Comparison Table

| Architecture | Examples | Rendered | Null | Routed | Purist-correct (of rendered) | Pragmatic-correct (of rendered) | Evidence-trace valid | Source |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `deterministic` | 750 | 741 | 9 | N/A | 688 (0.928) | 695 (0.938) | 750 (1.000) | `run_split` |
| `deterministic_canonical_pipeline` | 750 | 741 | 9 | N/A | 688 (0.928) | 695 (0.938) | 750 (1.000) | `run_split` |
| `hybrid` | 750 | 589 | 160 | 42 | 500 (0.849) | 525 (0.891) | 734 (0.979) | `build_unified_pipeline_artifact_deep_replay` |
| `llm_only_direct_labeler` | 750 | 750 | 0 | N/A | 564 (0.752) | 599 (0.799) | 711 (0.948) | `run_split` |
| `hybrid_structured_events` | 750 | 748 | 2 | N/A | 661 (0.884) | 679 (0.908) | 691 (0.921) | `run_split` |
| `llm_only_canonical_pipeline` | 750 | 750 | 0 | N/A | 581 (0.775) | 626 (0.835) | 700 (0.933) | `run_split` |

Footnotes:

- Evidence-trace metrics are NOT uniform across architectures: deterministic, deterministic_canonical_pipeline, llm_only_direct_labeler, and hybrid_structured_events report `evidence_valid` (free-text substring presence in the source note); llm_only_canonical_pipeline reports the deliberately distinct `evidence_text_contained`; hybrid reports a formal CandidateSet source-id validity rate sourced from its deep-replay projection stage. These measure different things -- do not read them as comparable accuracy numbers (see the per-architecture metric table below the shared table).
- Architecture taxonomy: `hybrid_structured_events` is architecturally a hybrid, not a fully-LLM pipeline. Its LLM stage extracts structured events from raw note text; the same deterministic normalize/project/render/score stages used by `hybrid` then process that output. The name reflects its LLM extraction approach, not the presence of a deterministic downstream. Contrast with `llm_only_direct_labeler` and `llm_only_canonical_pipeline`, which complete the full extraction-to-label pass in one LLM call with no deterministic normalization. The two hybrid configs differ in their LLM task: `hybrid_structured_events` asks the LLM to extract structured events from raw text (open-text → schema); `hybrid` asks the LLM to assess a pre-extracted deterministic candidate set. Their shared deterministic downstream makes the performance gap between them a direct measure of how much the LLM task and the verification/routing layer matter.
- hybrid's row above is the only one not sourced from raw `run_split` output: its assessment-stage probe reports schema-fit diagnostics only and has no rendered/null/purist/routed numbers of its own (design doc Section 2-3). This report replays its assessment rows -- using the live-generated CandidateSets the fixed `run_split` now embeds in its own output rows, so no static-artifact dependency or 250-row scoping applies -- through projection_render -> score -> verification_route -> verification_decision (`build_unified_pipeline_artifact`). This asymmetry is the architectural fact under comparison, not a methodology artifact.

### Evidence-Trace Metric By Architecture

| Architecture | Metric reported |
| --- | --- |
| `deterministic` | `evidence_valid` |
| `deterministic_canonical_pipeline` | `evidence_valid` |
| `hybrid` | `candidate_set_source_id_status==valid` |
| `llm_only_direct_labeler` | `evidence_valid` |
| `hybrid_structured_events` | `evidence_valid` |
| `llm_only_canonical_pipeline` | `evidence_text_contained` |

### Final-Answer Distribution (top entries)

- `deterministic`: {'no seizure frequency reference': 106, 'seizure free for multiple year': 93, '1 per day': 32, '1 per month': 21, 'multiple per week': 16, '2 per week': 11, 'unknown': 9, '4 per day': 7, '1 per 2 day': 7, 'multiple per day': 7, '1 per week': 7, '1 per 2 month': 7}
- `deterministic_canonical_pipeline`: {'no seizure frequency reference': 106, 'seizure free for multiple year': 93, '1 per day': 32, '1 per month': 21, 'multiple per week': 16, '2 per week': 11, 'unknown': 9, '4 per day': 7, '1 per 2 day': 7, 'multiple per day': 7, '1 per week': 7, '1 per 2 month': 7}
- `hybrid`: {'None': 177, 'unknown': 63, 'no seizure frequency reference': 30, '1 per month': 23, '1 per day': 18, 'multiple per day': 12, 'multiple per week': 11, '1 per 2 day': 7, 'seizure free for 6 month': 7, '1 to 2 per month': 7, '2 per week': 6, '1 per week': 6}
- `llm_only_direct_labeler`: {'seizure free for multiple year': 113, 'unknown': 87, 'no seizure frequency reference': 59, '1 per day': 29, 'multiple per day': 26, '1 per month': 14, 'multiple per week': 12, '2 per week': 9, 'seizure free for 6 month': 9, '1 per 2 month': 8, '1 to 2 per month': 7, '2 to 3 per week': 7}
- `hybrid_structured_events`: {'seizure_freq_unknown': 186, 'seizure_freq_more1week_less1day': 144, 'seizure_freq_more1mon_less1week': 108, 'currently_no_seizure': 108, 'seizure_freq_more1per6mon_less1mon': 81, 'seizure_freq_1ormore_daily': 54, 'seizure_freq_1_per_mon': 37, 'seizure_freq_1_per_week': 12, 'seizure_freq_1_per_6mon': 10, 'seizure_freq_1_per_yr': 8, 'None': 2}
- `llm_only_canonical_pipeline`: {'unknown': 75, 'no seizure frequency reference': 46, 'seizure free for multiple year': 46, '1 per day': 27, 'multiple per day': 25, 'seizure free for 6 month': 22, 'multiple per week': 20, '1 per month': 19, 'seizure free for 3 month': 14, '2 per week': 9, 'multiple per month': 8, '1 per 2 month': 8}

## Hybrid-Only Routing Appendix

No other architecture in this comparison has a routing stage; this appendix exists to characterize what `hybrid` does with the rows it doesn't render directly, not to provide a column the other five could also fill. Drawn from the same deep-replay artifact that supplies hybrid's shared-table row above.

- Routed rows: 42 (0.071 of rendered)
- Unrouted rows: 708

### Route Family Counts

- `cluster_axis_ambiguity`: 14
- `conditional_only_trigger`: 2
- `mixed_window_or_vague_addition`: 2
- `multiple_current_primary_facts`: 1
- `relative_only_trend`: 2
- `rendered_label_supported_but_policy_sensitive`: 2
- `seizure_free_proxy_evidence_overreach`: 1
- `selected_source_id_invalid`: 15
- `unresolved_cluster_cadence_with_per_cluster_burden`: 4

### Verification Decision Action Counts

- `abstain`: 42

## What This Report Does Not Claim

- validation750-only; no `test450` read; no holdout-facing or benchmark-comparable claim.
- Evidence-trace metrics are not uniform across architectures (see footnote and per-architecture metric table above) -- they measure different things and must not be compared as if they were one accuracy number.
- hybrid's shared-table numbers come from deep-replay, not its raw `run_split` output (see footnote above); the other five architectures' numbers come directly from their `run_split` output.

