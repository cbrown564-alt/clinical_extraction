# Gan 2026 Phase 4 Frozen test450 Aggregate Audit (openai/gpt-4.1-mini)

Phase 4 frozen test450 aggregate audit, openai/gpt-4.1-mini pass. One-shot frozen aggregate read of the locked test450 split for four of the six PipelineArchitecture configs (deterministic_canonical_pipeline, hybrid v5 prompt, hybrid_structured_events, llm_only_canonical_pipeline v0.5 prompt); deterministic and llm_only_direct_labeler are intentionally excluded (plan Section 6 rationale: DCP is numerically identical to deterministic, DL consistently underperforms CP). No row-level holdout tuning and no re-runs based on these results (plan Section 7 guardrails). Compares the four architectures on the axes that are universally meaningful (rendered/null disposition, Purist/Pragmatic-correct of rendered rows, evidence-trace validity, final-answer distribution); hybrid additionally carries a routing-taxonomy appendix that no other architecture has an analogous surface for.

## Artifacts

- Comparison JSONL: `experiments\gan2026_test450_phase4_comparison_report_gpt41mini_2026-06-10.jsonl`
- Summary JSON: `experiments\gan2026_test450_phase4_comparison_report_gpt41mini_2026-06-10.json`
- Model: `openai/gpt-4.1-mini`
- Split: `test` (locked `test450`, `gan2026_split_v1`)

## Shared Comparison Table

| Architecture | Examples | Rendered | Null | Routed | Purist-correct (of rendered) | Pragmatic-correct (of rendered) | Evidence-trace valid | Source |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `deterministic_canonical_pipeline` | 450 | 450 | 0 | N/A | 329 (0.731) | 341 (0.758) | 450 (1.000) | `run_split` |
| `hybrid` | 450 | 334 | 116 | 30 | 269 (0.805) | 281 (0.841) | 438 (0.973) | `build_unified_pipeline_artifact_deep_replay` |
| `hybrid_structured_events` | 450 | 448 | 2 | N/A | 364 (0.812) | 381 (0.850) | 418 (0.929) | `run_split` |
| `llm_only_canonical_pipeline` | 450 | 450 | 0 | N/A | 326 (0.724) | 346 (0.769) | 415 (0.922) | `run_split` |

Footnotes:

- Evidence-trace metrics are NOT uniform across architectures: deterministic, deterministic_canonical_pipeline, llm_only_direct_labeler, and hybrid_structured_events report `evidence_valid` (free-text substring presence in the source note); llm_only_canonical_pipeline reports the deliberately distinct `evidence_text_contained`; hybrid reports a formal CandidateSet source-id validity rate sourced from its deep-replay projection stage. These measure different things -- do not read them as comparable accuracy numbers (see the per-architecture metric table below the shared table).
- Architecture taxonomy: `hybrid_structured_events` is architecturally a hybrid, not a fully-LLM pipeline. Its LLM stage extracts structured events from raw note text; the same deterministic normalize/project/render/score stages used by `hybrid` then process that output. The name reflects its LLM extraction approach, not the presence of a deterministic downstream. Contrast with `llm_only_direct_labeler` and `llm_only_canonical_pipeline`, which complete the full extraction-to-label pass in one LLM call with no deterministic normalization. The two hybrid configs differ in their LLM task: `hybrid_structured_events` asks the LLM to extract structured events from raw text (open-text → schema); `hybrid` asks the LLM to assess a pre-extracted deterministic candidate set. Their shared deterministic downstream makes the performance gap between them a direct measure of how much the LLM task and the verification/routing layer matter.
- hybrid's row above is the only one not sourced from raw `run_split` output: its assessment-stage probe reports schema-fit diagnostics only and has no rendered/null/purist/routed numbers of its own (design doc Section 2-3). This report replays its assessment rows -- using the live-generated CandidateSets the fixed `run_split` now embeds in its own output rows, so no static-artifact dependency or 250-row scoping applies -- through projection_render -> score -> verification_route -> verification_decision (`build_unified_pipeline_artifact`). This asymmetry is the architectural fact under comparison, not a methodology artifact.

### Evidence-Trace Metric By Architecture

| Architecture | Metric reported |
| --- | --- |
| `deterministic_canonical_pipeline` | `evidence_valid` |
| `hybrid` | `candidate_set_source_id_status==valid` |
| `hybrid_structured_events` | `evidence_valid` |
| `llm_only_canonical_pipeline` | `evidence_text_contained` |

### Final-Answer Distribution (top entries)

- `deterministic_canonical_pipeline`: {'no seizure frequency reference': 120, 'seizure free for multiple year': 39, '1 per day': 18, 'multiple per week': 10, '1 per month': 9, '2 per 3 month': 8, '1 per week': 5, '1 per 2 to 3 week': 5, '2 to 3 per week': 5, '1 per 2 month': 4, '1 per 2 to 3 month': 4, '1 per 3 month': 4}
- `hybrid`: {'None': 131, 'unknown': 39, 'no seizure frequency reference': 17, '1 per day': 13, 'multiple per week': 9, '1 per month': 6, '2 to 3 per week': 6, 'seizure free for 8 month': 5, '1 per 2 to 3 week': 5, '2 per 3 month': 5, '4 per week': 4, '1 per 2 to 3 month': 4}
- `hybrid_structured_events`: {'seizure_freq_unknown': 118, 'seizure_freq_more1week_less1day': 80, 'currently_no_seizure': 64, 'seizure_freq_more1mon_less1week': 59, 'seizure_freq_more1per6mon_less1mon': 48, 'seizure_freq_1ormore_daily': 37, 'seizure_freq_1_per_mon': 26, 'seizure_freq_1_per_yr': 8, 'seizure_freq_1_per_week': 6, 'None': 2, 'seizure_freq_1_per_6mon': 2}
- `llm_only_canonical_pipeline`: {'unknown': 59, 'no seizure frequency reference': 38, 'seizure free for multiple year': 30, 'multiple per week': 21, 'multiple per day': 12, '1 per month': 12, '1 per day': 11, 'seizure free for 3 month': 8, '2 to 3 per month': 7, '2 to 3 per week': 6, 'seizure free for 6 month': 6, '1 per 2 to 3 month': 5}

## Hybrid-Only Routing Appendix

No other architecture in this comparison has a routing stage; this appendix exists to characterize what `hybrid` does with the rows it doesn't render directly, not to provide a column the other three could also fill. Drawn from the same deep-replay artifact that supplies hybrid's shared-table row above.

- Routed rows: 30 (0.090 of rendered)
- Unrouted rows: 420

### Route Family Counts

- `cluster_axis_ambiguity`: 13
- `denominator_window_mismatch`: 1
- `relative_only_trend`: 1
- `selected_source_id_invalid`: 12
- `unresolved_cluster_cadence_with_per_cluster_burden`: 4

### Verification Decision Action Counts

- `abstain`: 30

## What This Report Does Not Claim

- This is a one-shot frozen `test450` aggregate read for four architectures only (deterministic and llm_only_direct_labeler are excluded by design -- see claim boundary above).
- No row-level holdout tuning was performed and no re-runs are planned based on these results (plan Section 7 guardrails).
- Evidence-trace metrics are not uniform across architectures (see footnote and per-architecture metric table above) -- they measure different things and must not be compared as if they were one accuracy number.
- hybrid's shared-table numbers come from deep-replay, not its raw `run_split` output (see footnote above); the other three architectures' numbers come directly from their `run_split` output.

