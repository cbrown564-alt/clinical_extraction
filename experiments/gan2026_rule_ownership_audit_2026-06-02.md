# Gan 2026 Deterministic Rule Ownership Audit

Date: 2026-06-02

This is Workstream B from the hybrid LLM/deterministic boundary report. It inventories deterministic rules and post-processing adapters and assigns component ownership for future LLM-heavy and hybrid experiments. It is a validation-development governance artifact, not a benchmark claim.

- Durable matrix: `experiments/gan2026_rule_ownership_matrix_2026-06-02.csv`
- Matrix rows: 149
- Split policy: no new data run; no test inspection; uses registry and saved experiment evidence only.
- Governing decision: `docs/decisions/0007-llm-heavy-clinical-selection-deterministic-adapters.md`

## Ownership Counts

| Proposed owner | Rows |
| --- | ---: |
| `deterministic_extraction_or_adapter` | 78 |
| `hybrid_side_car` | 39 |
| `model_instruction` | 12 |
| `research_comparison` | 20 |

## Rule Group Coverage

| Group | Rows |
| --- | ---: |
| `benchmark_repair` | 30 |
| `cluster_arithmetic` | 28 |
| `date_duration_utilities` | 1 |
| `diary_log_aggregation` | 26 |
| `gan_shorthand` | 4 |
| `gold_normalization_policy` | 7 |
| `label_parser` | 1 |
| `portable_rate_expressions` | 30 |
| `schema_repair` | 1 |
| `seizure_free_no_event_assertions` | 10 |
| `selected_evidence_arithmetic` | 1 |
| `temporal_selection` | 10 |

## Decisions

1. LLM-heavy runs do not need the raw model output to contain a parser-ready Gan label. The model owns clinical selection: the relevant fact, evidence, temporal state, competing-event choice, and operands.
2. Deterministic code should intentionally own mechanical work that frees model capacity: parser-ready formatting, unit grammar, arithmetic from model-selected operands, seizure-free duration calculation, cluster syntax rendering, and stable Gan benchmark conventions.
3. Semantic arithmetic is allowed in the primary LLM-heavy score layer when it computes from model-selected evidence or operands. If deterministic code selects a different clinical fact, the run becomes hybrid.
4. Deterministic projection or temporal selection among multiple clinical facts is hybrid behavior. It is allowed in named hybrid implementations but is not an LLM-heavy primary answer.
5. Synthetic diary/log aggregation remains research-only until portability is shown outside Gan-style notes, even when it is useful on validation rows.
6. Benchmark repair and clean gold-normalization policy stay deterministic adapters. `bimonthly`/`biweekly`-style Gan conventions should be applied automatically once the model selects the relevant evidence.

## Hard Follow-Up Decisions

- Cluster rendering: deterministic cluster syntax/rendering is acceptable when operands are model-selected; require explicit hybrid claim language when deterministic code selects burden, cadence, or which cluster fact wins.
- `adapter.month_bucket_duration_selection_graph_gated_v2`: retain as a diagnostic research comparison. Promotion would require a separate decision note because it appears to select among graph-derived states, not merely compute duration from model-selected evidence.
- Synthetic diary templates: use as hard-slice or ablation rows, not as general clinical extraction evidence until evaluated outside Gan-style letter templates.

## Claim-Language Rules

- `LLM-heavy`: the model selected the clinical fact/evidence/operands; deterministic code may render the final Gan-compatible label.
- `LLM-owned clinical selection`: the raw model output identifies the selected clinical fact, evidence, temporal state, and operands used by the deterministic adapter.
- `Hybrid`: deterministic and model components both contribute semantic selection, candidate choice, graph projection, or competing-fact arbitration.
- `Benchmark adapter`: deterministic code maps an already selected fact to Gan-compatible syntax or an arbitrary gold-label convention.
- `Research-only comparison`: deterministic logic is useful on Gan-style patterns but lacks enough portability evidence for default LLM-heavy scoring.

## Matrix Preview

| Rule ID | Group | Owner | Module |
| --- | --- | --- | --- |
| `benchmark_repair.canonicalize_seizure_free` | `benchmark_repair` | `deterministic_extraction_or_adapter` | `contract.benchmark_prediction_repair` |
| `benchmark_repair.clean_prediction_extras` | `benchmark_repair` | `deterministic_extraction_or_adapter` | `contract.benchmark_prediction_repair` |
| `benchmark_repair.cleanup_commas_final` | `benchmark_repair` | `deterministic_extraction_or_adapter` | `contract.benchmark_prediction_repair` |
| `benchmark_repair.cleanup_commas_first` | `benchmark_repair` | `deterministic_extraction_or_adapter` | `contract.benchmark_prediction_repair` |
| `benchmark_repair.compress_double_per_range` | `benchmark_repair` | `deterministic_extraction_or_adapter` | `contract.benchmark_prediction_repair` |
| `benchmark_repair.daypart_to_day` | `benchmark_repair` | `deterministic_extraction_or_adapter` | `contract.benchmark_prediction_repair` |
| `benchmark_repair.drop_per_one_final` | `benchmark_repair` | `deterministic_extraction_or_adapter` | `contract.benchmark_prediction_repair` |
| `benchmark_repair.drop_per_one_first` | `benchmark_repair` | `deterministic_extraction_or_adapter` | `contract.benchmark_prediction_repair` |
| `benchmark_repair.drop_prediction_noise` | `benchmark_repair` | `deterministic_extraction_or_adapter` | `contract.benchmark_prediction_repair` |
| `benchmark_repair.drop_times_before_per` | `benchmark_repair` | `deterministic_extraction_or_adapter` | `contract.benchmark_prediction_repair` |
| `benchmark_repair.every_each_forms` | `benchmark_repair` | `deterministic_extraction_or_adapter` | `contract.benchmark_prediction_repair` |
| `benchmark_repair.fallback_if_disallowed` | `benchmark_repair` | `deterministic_extraction_or_adapter` | `contract.benchmark_prediction_repair` |
| `benchmark_repair.final_allowed_format_repair` | `benchmark_repair` | `deterministic_extraction_or_adapter` | `contract.benchmark_prediction_repair` |
| `benchmark_repair.fix_cluster_block` | `benchmark_repair` | `deterministic_extraction_or_adapter` | `contract.benchmark_prediction_repair` |
| `benchmark_repair.inequality_to_multiple` | `benchmark_repair` | `deterministic_extraction_or_adapter` | `contract.benchmark_prediction_repair` |
| `benchmark_repair.normalize_cluster_label` | `benchmark_repair` | `deterministic_extraction_or_adapter` | `contract.benchmark_prediction_repair` |
| `benchmark_repair.normalize_cluster_label2` | `benchmark_repair` | `deterministic_extraction_or_adapter` | `contract.benchmark_prediction_repair` |
| `benchmark_repair.normalize_units_after_cluster` | `benchmark_repair` | `deterministic_extraction_or_adapter` | `contract.benchmark_prediction_repair` |
| `benchmark_repair.normalize_units_after_seizure_free` | `benchmark_repair` | `deterministic_extraction_or_adapter` | `contract.benchmark_prediction_repair` |
| `benchmark_repair.normalize_units_first` | `benchmark_repair` | `deterministic_extraction_or_adapter` | `contract.benchmark_prediction_repair` |

The CSV contains all 149 rows, including extraction rules, benchmark repair steps, clean gold-policy rules, selected-evidence adapters, and graph projection diagnostics.
