# Gan 2026 RQ1 Candidate-Discovery Answer

Date: 2026-06-04

Status: Final answer for validation-development component mechanics.

## Answer

This report establishes the final candidate-discovery answer for the validation-development split (`gan2026_split_v1`). By isolating candidate discovery from downstream selection and projection, we identify that broad candidate recall is not the primary bottleneck for the pipeline, but selective candidate proposal remains a high-value rescue mechanism.

For broad clinical extraction, the best default candidate source is the **deterministic candidate set** (or the equivalent **state-graph nodes** representability view). Both cover **96.7% (725/750)** of validation source rows under the gold-state recall definition, while keeping a lean candidate burden (median 1 candidate/note).

The **LLM candidate sidecar** (`llm_candidate_selector_raw`) should not be promoted as a broad default replacement generator. It produces double the candidate burden (2,126 candidates vs. 1,194) and introduces a massive regression rate (7 W->C vs 49 C->W in the follow-up panel). However, it has a high exact-evidence rate (98.5%) and provides significant value in a selective rescue role: on the **78 rows** classified as `candidate_generation` first failures (where deterministic rules failed to find a valid state), the LLM sidecar successfully rescues the gold state.

The final RQ1 answer is:
1. **Substrate**: Use deterministic all-candidates or state-graph nodes as the default candidate substrate (96.7% recall).
2. **Sidecar Rescue**: Deploy the LLM candidate generator selectively as a rescue proposal sidecar on slices with known boundary uncertainty, perimenstrual/catamenial limits, or complex sleep triggers, while keeping the deterministic safety floor for ordinary rates.
3. **Verifier Gate Required**: Do not expose raw LLM candidates to the selector without a verifier gate to eliminate false-positive candidates (1.37 false positives per note) and bind missing window/denominator metadata.

## Supporting Evidence

The conclusions are backed by validation replay matrices and the **2026-06-04 follow-up panel** (654 panel rows over 371 source rows):
- [gan2026_component_projection_followup_panel_2026-06-04.md](file:///Users/cobro/code/clinical-extraction/experiments/gan2026_component_projection_followup_panel_2026-06-04.md)
- [gan2026_target_rows_inspection.md](file:///Users/cobro/code/clinical-extraction/docs/research/gan2026_target_rows_inspection.md)
- `experiments/gan2026_rq1_candidate_discovery_matrix_2026-06-03.jsonl`

### Generator Trade-Offs

| Generator | Source rows | Total candidates | Recalled source rows | Recall | False positives/note | Exact evidence | Median candidates/note |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `deterministic_candidates_all` | 750 | 1,194 | 725 | 0.967 | 0.257 | 0.898 | 1 |
| `state_graph_nodes` | 750 | 1,122 | 725 | 0.967 | 0.244 | 0.891 | 1 |
| `deterministic_top_candidate` | 750 | 750 | 716 | 0.955 | 0.045 | 0.847 | 1 |
| `llm_candidate_selector_raw` | 739 | 2,126 | 642 | 0.869 | 1.365 | 0.985 | 3 |

### Hidden-Family Readout

The follow-up panel propagated hidden-family tags to refine candidate discovery weaknesses across specific clinical profiles:

- **Rate Buckets and Competing Semiologies**: Recall is extremely high (above 95%) in both deterministic and graph node sources. Candidate discovery is not the bottleneck here; failures are dominated by temporal and selection choices.
- **Seizure-Free Duration (35 failures owned by `candidate_generation`)**: Both deterministic and LLM sources struggle with capturing long-term seizure freedom when intercurrent or breakthrough events are noted.
- **Unknown Boundary (28 failures owned by `candidate_generation`)**: This remains the largest candidate discovery weakness, specifically on rows where patients experience conditional events (e.g. perimenstrual or sleep-deprived only) that are not countable.

## Transfer Confidence

| Finding | Development confidence | Holdout-transfer confidence | Rationale |
| --- | --- | --- | --- |
| Deterministic/graph nodes cover 96.7% recall. | High | Moderate | Replayed on validation750, but clinical note structure in the holdout could feature novel layouts. |
| Broad LLM candidate selection causes heavy regression. | High | High | Unconstrained LLM generation consistently collapses benchmark syntax and adds duplicate noise across validation. |
| LLM sidecar rescues candidate-generation first failures. | Moderate | Low-to-moderate | Validated on validation first-failure slices (78 rows), which might reflect validation-specific phrasing. |

## Decision

1. **Substrate**: Lock `deterministic_candidates_all` or `state_graph_nodes` as the broad candidate source.
2. **Selective Rescue**: Predeclare a gated LLM rescue proposer for the 78 first-failure rows representing unknown/seizure-free boundaries and conditional trigger cases.
3. **Next Component**: Feed the fixed candidates into RQ2 evidence selection. Candidate recall is sufficient; the main bottleneck is state attribution and projection.
