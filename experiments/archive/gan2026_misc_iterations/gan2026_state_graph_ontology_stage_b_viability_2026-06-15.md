# Gan 2026 State-Graph Ontology Stage B Viability

Date: 2026-06-15

Stage B gold-free, no-model-spend viability gate for the KG-grounded component generator. Validation-only over `gan2026_split_v1`; replays saved LLM atomic-claim graphs, reads no holdout rows, and makes no model calls.

- Source artifact: `experiments/gan2026_clinical_frequency_state_graph_llm_atomic_claim_rows_validation25_2026-06-02.jsonl`
- Ontology: `gan2026_admissible_state_ontology_v1`
- Rows: 25

## Node admission (schema + evidence + ontology gate)

- Total atomic-claim nodes: 80
- Schema-valid (structural): 79/80
- Exact-evidence (located span): 79/80
- Semantic-valid (ontology assignment): 80/80
- Admitted as components: 79/80
- Structural rejections: 1
- Over-inference (C2 guard) rejections: 0

### Rejection reasons

| Reason | Count |
| --- | ---: |
| `graph_error:atomic_claim_evidence_not_exact` | 1 |

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
| `unknown` | 25 |

## Gate reading

Stage B passes its structural and interpretability sub-gates when nodes are schema-valid with exact evidence and `resolve_label` yields an interpretable, component-localized label per row. The C2 over-inference guard's sub-gate is *exercised* only if the atomic-claim builder mints quantifying (frequency / seizure-free) states for it to police.

On this artifact the guard fired **0 times**: the v3 atomic-claim builder mints every node as `unknown`/`no_reference` (zero quantifying states), so there is no quantified mint for the guard to reject. The lone rejection is structural (evidence not an exact note substring). The atomic-claim component is therefore, as built, a pure `unknown`-minter - which is exactly the clean competing `unknown` component the C2 resolution (ADR `0017`) wants for the `band_unknown` over-inference residual, but it is not yet a source of quantified components, and the guard's *rejection* mechanism stays unexercised until an atomic-claim artifact that commits per-claim quantified labels exists.
