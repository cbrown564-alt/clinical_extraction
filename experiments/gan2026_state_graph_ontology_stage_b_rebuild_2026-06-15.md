# Gan 2026 State-Graph Ontology Stage B (Rebuilt, raw_frequency-normalized)

Date: 2026-06-15

Stage B viability gate, rebuilt from the v3 section claim-table with `raw_frequency` normalization so the ontology over-inference guard is exercised on quantifying mints. Validation-only over `gan2026_split_v1`; no holdout rows, no model calls (label normalization is deterministic).

- Source claim-table: `experiments/gan2026_section_claim_table_validation25_gpt41mini_v3_2026-06-01.jsonl`
- Rebuilt graphs (replay artifact): `experiments/gan2026_state_graph_ontology_stage_b_rebuild_2026-06-15_graphs.jsonl`
- Graph builder: `llm_atomic_claim_graph_builder_v3_raw_frequency_normalized`
- Ontology: `gan2026_admissible_state_ontology_v1`
- Rows: 25

## Node admission (schema + evidence + ontology gate)

- Total atomic-claim nodes: 80
- Schema-valid (structural): 80/80
- Exact-evidence (located span): 80/80
- Semantic-valid (ontology assignment): 79/80
- Admitted as components: 79/80
- Structural rejections: 0
- Over-inference (C2 guard) rejections: 1

### Rejection reasons

| Reason | Count |
| --- | ---: |
| `over_inference_out_of_unknown:last_event_only` | 1 |

### Evidence-shape distribution

| Shape | Count |
| --- | ---: |
| `last_event_only` | 5 |
| `open_ended_since` | 4 |
| `other` | 45 |
| `quantified` | 16 |
| `vague_count` | 10 |

## resolve_label interpretability

- Rows with a decision trace: 25/25
- Rows component-localized (label attributed to admitted nodes): 25/25
- Rows defaulted to no-reference (nothing admitted): 0/25

### Final-kind distribution

| Final kind | Rows |
| --- | ---: |
| `frequency` | 13 |
| `no_reference` | 1 |
| `unknown` | 4 |
| `unresolved_multiple` | 7 |

## Gate reading

With `raw_frequency` normalized, the atomic-claim graph now mints quantifying states and the final-kind distribution is no longer uniformly `unknown` - so the component pool can contribute genuine frequency / seizure-free candidates, not only the clean `unknown`.

The C2 over-inference guard is now **exercised**: it fired 1 time(s), and every firing is an `over_inference_out_of_unknown:<shape>` rejection - a node whose `raw_frequency` parsed to a rate/seizure-free duration but whose evidence shape is unknown-only (e.g. a `last_event_only` mention). The rejected nodes are retained with provenance, never silently dropped, and the row falls through to its other admitted components.
