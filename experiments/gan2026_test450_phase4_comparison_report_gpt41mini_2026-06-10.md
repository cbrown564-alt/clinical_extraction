# Gan 2026 Phase 4 Locked `test450` Aggregate Audit (openai/gpt-4.1-mini)

This report records a one-time aggregate read of the locked `test450` split for
four of six saved `PipelineArchitecture` configurations:
`deterministic_canonical_pipeline`, `hybrid`, `hybrid_structured_events`, and
`llm_only_canonical_pipeline`. The exact identifiers are retained because they
name saved configurations. The deterministic and `llm_only_direct_labeler`
configurations were excluded under the recorded plan. No row-level holdout
tuning or result-driven reruns followed. The shared table reports output
disposition and task scores; evidence checks differ by method and are not
directly comparable. Only `hybrid` has the routing results shown later.

## Saved files

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
- Method classification: `hybrid_structured_events` is an LLM-with-rules
  method. Its LLM extracts structured events from raw text; deterministic
  normalization, selection, rendering, and scoring then process them.
  `hybrid` instead asks an LLM to assess a deterministic candidate set.
  `llm_only_direct_labeler` and `llm_only_canonical_pipeline` complete clinical
  selection in the model call without deterministic normalization. The gap
  between the two LLM-with-rules configurations combines differences in the
  LLM task and in verification or routing; this aggregate report does not
  isolate those effects.
- The `hybrid` row is the only row not taken directly from raw `run_split`
  output. Its assessment probe contains schema diagnostics rather than final
  output counts. This report replays the saved candidate sets through
  `projection_render`, scoring, routing, and the final decision
  (`build_unified_pipeline_artifact`). That source difference limits direct
  comparison and is recorded here explicitly.

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

## Routing appendix for `hybrid`

No other method in this comparison has a routing step. This appendix describes
what `hybrid` does with rows it does not render directly. Its values come from
the same deep-replay output as the `hybrid` row in the shared table.

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

- This is a one-time locked `test450` aggregate read for four methods only
  (deterministic and `llm_only_direct_labeler` were excluded under the recorded
  plan).
- No row-level holdout tuning was performed and no re-runs are planned based on these results (plan Section 7 guardrails).
- Evidence-trace metrics are not uniform across architectures (see footnote and per-architecture metric table above) -- they measure different things and must not be compared as if they were one accuracy number.
- hybrid's shared-table numbers come from deep-replay, not its raw `run_split` output (see footnote above); the other three architectures' numbers come directly from their `run_split` output.

