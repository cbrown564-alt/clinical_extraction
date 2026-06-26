# Gan 2026 Grouped Attribution And Repair Ladder 650 V0

Date: 2026-06-01

This is a grouped interpretation of the combined 650-row no-call attribution ladder. It is a validation-development artifact, not a final holdout or benchmark result.

## Condition

- Split: `validation`, `gan2026_split_v1`
- Raw-output source: `experiments/gan2026_llm_structured_validation750_gpt41mini_v05_completion_2026-06-01.jsonl`
- Source detailed ladder: `experiments/gan2026_combined_attribution_repair_ladder650_v0_2026-06-01.json`
- JSON summary: `experiments/gan2026_grouped_attribution_repair_ladder650_v0_2026-06-01.json`
- Grouping policy: collapse small incremental deterministic modules into interpretation-level categories while preserving the clean/hybrid attribution boundary.

## Grouped Summary

| Group | Claim class | Endpoint condition | Purist | Delta vs previous group | Delta vs raw | Pragmatic | Parse/schema/label failures | Repair notes |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Raw structured LLM selection | clean_attribution_baseline | A_raw_model_selection | 0.6062 (394 / 650) | baseline | +0 (+0.0000) | 0.6338 (412 / 650) | 140 | 0 |
| Clean scorer-facing normalization | clean_attribution | C_frozen_clean_scorer_policy | 0.6738 (438 / 650) | +44 (+0.0676) | +44 (+0.0676) | 0.7308 (475 / 650) | 65 | 262 |
| Broad basic label repair bridge | hybrid_bridge | D_full_basic_gan_label_repair_bridge | 0.7092 (461 / 650) | +23 (+0.0354) | +67 (+0.1030) | 0.7369 (479 / 650) | 0 | 309 |
| Selected-evidence deterministic derivation | hybrid_repair_module | E_selected_evidence_repair | 0.8400 (546 / 650) | +85 (+0.1308) | +152 (+0.2338) | 0.8554 (556 / 650) | 0 | 378 |
| Contextual temporal and event-state modules | hybrid_repair_modules | N_full_current_stack | 0.9046 (588 / 650) | +42 (+0.0646) | +194 (+0.2984) | 0.9200 (598 / 650) | 0 | 460 |

## Group Definitions

### Raw structured LLM selection

Includes: `A_raw_model_selection`.

Model-selected final label before downstream repair.

### Clean scorer-facing normalization

Includes: `B_strict_format_only`, `C_frozen_clean_scorer_policy`.

Strict parser/format compatibility plus the frozen clean Gan scorer-facing policy.

### Broad basic label repair bridge

Includes: `D_full_basic_gan_label_repair_bridge`.

Crosses the clean boundary by allowing semantic fallback and vague-quantity remapping.

### Selected-evidence deterministic derivation

Includes: `E_selected_evidence_repair`.

Derives scorer-facing labels from the evidence span selected by the model; this is the largest deterministic jump.

### Contextual temporal and event-state modules

Includes: `F_monthly_diary_arithmetic`, `G_usual_interval_override`, `H_breakthrough_after_seizure_free`, `I_non_epileptic_override`, `J_residual_jerk_date_anchor`, `K_post_change_burst`, `L_dated_sequence`, `M_elapsed_anchor`, `N_full_current_stack`.

Groups small but meaningful deterministic modules for diary arithmetic, usual intervals, breakthrough events, non-epileptic state conversion, dated sequences, post-change bursts, and elapsed-anchor reasoning.

## Interpretation

Clean attribution ends at 438/650 Purist = 0.6738. This includes raw model selection plus format and frozen scorer-facing normalization.

The broad basic repair bridge raises this to 461/650 = 0.7092, but it crosses the clean-policy boundary because it includes semantic fallback and vague-quantity remapping.

Selected-evidence deterministic derivation is the dominant jump, reaching 546/650 = 0.8400. This is prediction-bearing deterministic work over model-selected evidence, not just formatting.

The remaining contextual temporal and event-state modules collectively raise the score to 588/650 = 0.9046. Individually many of these modules are small, but together they account for the final movement from selected-evidence repair to the full hybrid stack.

Recommended claim language: report the first two groups as the clean LLM-first attribution result, and report the later groups as a hybrid deterministic-postprocessing ladder with named module families.
