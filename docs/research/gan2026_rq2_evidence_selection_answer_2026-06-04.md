# Gan 2026 RQ2 Evidence-Selection Answer

Date: 2026-06-04

Status: Final answer for validation-development component mechanics.

## Answer

This report establishes the final evidence-selection answer for the validation-development split (`gan2026_split_v1`). 

The final RQ2 answer is:
1. **Evidence Location is Solved**: LLMs are exceptionally strong at locating the exact clinical text containing seizure-frequency references. The hybrid adjudicator (`hybrid_adjudicator_raw`) achieves **100% (750/750) exact evidence extraction** on validation750, and diagnostic claim schemas (`llm_heavy_selected_fact` and `claim_table_final_query`) achieve **95% to 98% exact evidence** rates.
2. **Clinical Choice vs. Text Search**: The main bottleneck is not finding the text, but **clinical selection and operand completeness**. The first-failure analysis shows that **109 failures** are owned by `typed_state_representation` (the schema layout or metadata completeness) and **36 failures** by `llm_clinical_selection` (choosing the incorrect fact).
3. **Over-Abstraction Regressions**: Direct unconstrained LLM selection causes severe regressions. When allowed to change clinical labels, the raw LLM selector (`llm_candidate_selector_raw`) regressed **49 baseline-correct rows** (obtaining only 7 rescues), and the hybrid adjudicator regressed **8 baseline-correct rows**.

The practical pipeline recommendation is:
- **Lock deterministic rule selection** as the default safe clinical decision substrate for main rates.
- **Deploy hybrid adjudication** solely to attach exact evidence strings and source IDs to the safe candidates, without allowing it to alter the clinical label.
- **Instrument rich schemas** (like claim tables) to preserve complete clinical operands (triggers, denominators, cluster bounds) so that the downstream projection policy has enough metadata to resolve clinical ambiguities.

## Supporting Evidence

The conclusions are backed by validation replay matrices and the **2026-06-04 follow-up panel** (654 panel rows over 371 source rows):
- [gan2026_component_projection_followup_panel_2026-06-04.md](file:///Users/cobro/code/clinical-extraction/experiments/gan2026_component_projection_followup_panel_2026-06-04.md)
- [gan2026_target_rows_inspection.md](file:///Users/cobro/code/clinical-extraction/docs/research/gan2026_target_rows_inspection.md)
- `experiments/gan2026_rq2_evidence_selection_matrix_2026-06-03.jsonl`

### Component Outcomes

| Component | Panel rows | W->C | C->W | Exact evidence rate | Rationale |
| --- | ---: | ---: | ---: | ---: | --- |
| `hybrid_adjudicator_raw` | 61 | 0 | 8 | 100% | Finds exact text but regresses 8 baseline-correct rows. |
| `llm_candidate_selector_raw` | 61 | 7 | 49 | 98.3% | Heavy regressions; unconstrained selection is unsafe. |
| `llm_heavy_selected_fact` | 95 | 0 | 0 | 98.9% | Strong diagnostic facts, but lacks source ID traces. |
| `claim_table_final_query` | 38 | 0 | 0 | 100% | Strong diagnostic query spans; excellent exactness. |

### Hidden-Family Evidence Selection Profile

Diagnostic runs on the `llm_heavy_selected_fact` surface show that exact evidence retrieval remains high across all families, but correctness drops due to missing operands:
- **Temporal Conflict & Currentness**: The LLM finds the "current month to date: 0 events" sentence exactly, but fails to capture the previous month's active rate, leading to a seizure-free overreach.
- **Cluster Burden**: The LLM extracts the cluster sentence, but drops the per-cluster count (representing it as a simple rate), losing essential cluster axes.
- **Unknown Boundaries (22/23 exact evidence but only 8/18 correct)**: The model locates the perimenstrual or sleep-deprived trigger text exactly, but is forced by the schema to project a rate, resulting in incorrect estimations instead of projecting `unknown`.

## Transfer Confidence

| Finding | Development confidence | Holdout-transfer confidence | Rationale |
| --- | --- | --- | --- |
| Hybrid adjudicator retrieves 100% exact evidence. | High | Moderate-to-high | Substring and source ID matching are simple, deterministic operations that should transfer well. |
| Unconstrained LLM selection is regressive. | High | High | Over-abstraction and denominator loss are systematic LLM properties. |
| Incomplete operands (metadata loss) cause failures. | High | Moderate-to-high | The schema contract limits the information passed to projection. |

## Decision

1. **Substrate**: Keep the deterministic top candidate as the selection substrate.
2. **Gated Evidence Spans**: Use `hybrid_adjudicator_raw` to extract exact evidence substrings and source IDs for the final clinical file, but **block it from changing labels** except under predeclared gates.
3. **Next Component**: Move to RQ4 (projection). Selected evidence is exact; the remaining regressions arise when rendering or normalising the state.
