# Gan 2026 Phase 1 Three-Way Architecture Comparison (ollama_chat/qwen3.6:35b, validation750)

Phase 1 three-way architecture comparison, ollama_chat/qwen3.6:35b pass, validation750 only. No test450 read, no holdout-facing or benchmark-comparable claim. Compares six PipelineArchitecture configs on the axes that are universally meaningful (rendered/null disposition, Purist/Pragmatic-correct of rendered rows, evidence-trace validity, final-answer distribution); hybrid additionally carries a routing-taxonomy appendix that no other architecture has an analogous surface for.

## Artifacts

- Comparison JSONL: `experiments\gan2026_three_way_comparison_phase1_report_qwen3635b_validation750_2026-06-09.jsonl`
- Summary JSON: `experiments\gan2026_three_way_comparison_phase1_report_qwen3635b_validation750_2026-06-09.json`
- Model: `ollama_chat/qwen3.6:35b`
- Split: `validation`

## Shared Comparison Table

| Architecture | Examples | Rendered | Null | Routed | Purist-correct (of rendered) | Pragmatic-correct (of rendered) | Evidence-trace valid | Source |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `deterministic` | 750 | 741 | 9 | N/A | 688 (0.928) | 695 (0.938) | 750 (1.000) | `run_split` |
| `deterministic_canonical_pipeline` | 750 | 741 | 9 | N/A | 688 (0.928) | 695 (0.938) | 750 (1.000) | `run_split` |
| `hybrid` | 250 | 221 | 29 | 15 | 212 (0.959) | 215 (0.973) | 242 (0.968) | `build_unified_pipeline_artifact_deep_replay` |
| `llm_only_direct_labeler` | 750 | 749 | 1 | N/A | 550 (0.734) | 581 (0.776) | 645 (0.860) | `run_split` |
| `hybrid_structured_events` | 750 | 746 | 4 | N/A | 624 (0.836) | 646 (0.866) | 561 (0.748) | `run_split` |
| `llm_only_canonical_pipeline` | 750 | 748 | 2 | N/A | 544 (0.727) | 582 (0.778) | 574 (0.765) | `run_split` |

Footnotes:

- Evidence-trace metrics are NOT uniform across architectures: deterministic, deterministic_canonical_pipeline, llm_only_direct_labeler, and hybrid_structured_events report `evidence_valid` (free-text substring presence in the source note); llm_only_canonical_pipeline reports the deliberately distinct `evidence_text_contained`; hybrid reports a formal CandidateSet source-id validity rate sourced from its deep-replay projection stage. These measure different things -- do not read them as comparable accuracy numbers (see the per-architecture metric table below the shared table).
- Architecture taxonomy: `hybrid_structured_events` is architecturally a hybrid, not a fully-LLM pipeline. Its LLM stage extracts structured events from raw note text; the same deterministic normalize/project/render/score stages used by `hybrid` then process that output. The name reflects its LLM extraction approach, not the presence of a deterministic downstream. Contrast with `llm_only_direct_labeler` and `llm_only_canonical_pipeline`, which complete the full extraction-to-label pass in one LLM call with no deterministic normalization. The two hybrid configs differ in their LLM task: `hybrid_structured_events` asks the LLM to extract structured events from raw text (open-text → schema); `hybrid` asks the LLM to assess a pre-extracted deterministic candidate set. Their shared deterministic downstream makes the performance gap between them a direct measure of how much the LLM task and the verification/routing layer matter.
- hybrid's row above is the only one not sourced from raw `run_split` output: its assessment-stage probe reports schema-fit diagnostics only and has no rendered/null/purist/routed numbers of its own (design doc Section 2-3). This report replays its assessment rows -- using CandidateSets loaded from the static pre-computed file supplied via `--hybrid-candidate-set-path` (this run's `hybrid` artifact pre-dates the live candidate-set wiring from section 8a, so candidate sets are not embedded in the run rows; hybrid's example count reflects only the rows covered by that static file) -- through projection_render -> score -> verification_route -> verification_decision (`build_unified_pipeline_artifact`). This asymmetry is the architectural fact under comparison, not a methodology artifact.

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
- `hybrid`: {'None': 43, 'unknown': 32, '1 per day': 12, '1 per month': 11, '4 per week': 4, '1 per week': 4, '1 per 2 month': 4, 'multiple per day': 4, '1 per 2 day': 3, '9 per month': 3, '1 per 2 week': 3, 'seizure free for 12 month': 3}
- `llm_only_direct_labeler`: {'unknown': 135, 'seizure free for multiple year': 86, 'multiple per day': 52, '1 per day': 31, 'no seizure frequency reference': 30, 'multiple per week': 20, '1 per month': 16, 'seizure free for 6 month': 13, '2 to 3 per week': 9, '1 to 2 per month': 8, 'seizure free for 3 month': 8, '2 per week': 7}
- `hybrid_structured_events`: {'seizure_freq_unknown': 175, 'seizure_freq_more1week_less1day': 144, 'currently_no_seizure': 129, 'seizure_freq_more1mon_less1week': 106, 'seizure_freq_more1per6mon_less1mon': 78, 'seizure_freq_1ormore_daily': 48, 'seizure_freq_1_per_mon': 39, 'seizure_freq_1_per_week': 13, 'seizure_freq_1_per_6mon': 7, 'seizure_freq_1_per_yr': 7, 'None': 4}
- `llm_only_canonical_pipeline`: {'unknown': 157, 'seizure free for 6 month': 87, 'multiple per day': 36, '1 per day': 28, 'no seizure frequency reference': 27, 'multiple per week': 18, 'seizure free for multiple year': 18, '1 per month': 13, '1 to 2 per month': 8, '1 per 2 month': 7, '1 per 2 day': 6, '1 to 2 per week': 6}

## Hybrid-Only Routing Appendix

No other architecture in this comparison has a routing stage; this appendix exists to characterize what `hybrid` does with the rows it doesn't render directly, not to provide a column the other five could also fill. Drawn from the same deep-replay artifact that supplies hybrid's shared-table row above.

- Routed rows: 15 (0.068 of rendered)
- Unrouted rows: 235

### Route Family Counts

- `conditional_only_trigger`: 1
- `rendered_label_supported_but_policy_sensitive`: 5
- `selected_source_id_invalid`: 8
- `unresolved_cluster_cadence_with_per_cluster_burden`: 1

### Verification Decision Action Counts

- `abstain`: 15

## What This Report Does Not Claim

- validation750-only; no `test450` read; no holdout-facing or benchmark-comparable claim.
- Evidence-trace metrics are not uniform across architectures (see footnote and per-architecture metric table above) -- they measure different things and must not be compared as if they were one accuracy number.
- hybrid's shared-table numbers come from deep-replay, not its raw `run_split` output (see footnote above); the other five architectures' numbers come directly from their `run_split` output.

