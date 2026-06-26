# Gan 2026 V1 Prompt Adjudicator Development Set

Date: 2026-05-31

This is a validation-only development artifact. It must not be treated as a held-out benchmark result and does not inspect locked test-row failures.

## Experiment Unit

Hypothesis: deterministic V1 errors that become correct when a rule family is disabled are useful seed examples for an LLM/DSPy final-selection adjudicator. The adjudicator should explain assertion status, temporality, seizure/event target, window, normalized rate, and uncertainty before accepting or overriding the deterministic final choice.

Minimal change: no scoring, rules, normalization, or prompts are changed. This step only mines existing validation ablation rows and packages deterministic V1 candidate diagnostics as prompt-development examples.

Data surface: Gan 2026 `validation` split using `gan2026_split_v1`.
Scorer policy: Gan-compatible Purist categories are carried through from the existing ablation artifact; no new evaluation is performed.

Source changed rows: `experiments/gan2026_v1_validation_ablation_changed_rows_2026-05-31.csv`
Development JSONL: `experiments/gan2026_v1_prompt_adjudicator_devset_2026-05-31.jsonl`

## Selection Policy

- Prioritize rows where deterministic V1 is wrong but an ablated condition is correct.
- Add support/control rows where deterministic V1 is correct but an ablation breaks it.
- Cap examples per ablation condition and diversify by error type, gold category, and selected-evidence type.

## Set Summary

- Examples: 16
- Lesson types: deterministic_overreach=10, deterministic_support_control=6
- Conditions: disable_cluster_arithmetic=5, disable_diary_log_aggregation=1, disable_portable_rate_expressions=3, disable_seizure_free_no_event_assertions=2, disable_temporal_selection=5

## Rows

| Row | Lesson | Condition | Baseline | Ablated | Gold | Question |
| ---: | --- | --- | --- | --- | --- | --- |
| 6209 | deterministic_overreach | disable_portable_rate_expressions | seizure_freq_1ormore_daily / 1 per day | seizure_freq_unknown / no seizure frequency reference | seizure_freq_unknown / multiple per day | Does the selected frequency evidence actually describe the patient's current seizures, or should the answer remain unknown/no-reference? |
| 5921 | deterministic_overreach | disable_portable_rate_expressions | seizure_freq_1ormore_daily / 1 per day | seizure_freq_more1per6mon_less1mon / 1 per 6 to 8 week | seizure_freq_more1per6mon_less1mon / 1 per 6 to 8 week | Which candidate is the clinically current seizure-frequency rate, and which rate should be rejected as a distractor or lower-priority window? |
| 10386 | deterministic_overreach | disable_portable_rate_expressions | seizure_freq_1ormore_daily / 1 per day | seizure_freq_more1week_less1day / 1 cluster per week, 2 to 3 per cluster | seizure_freq_more1week_less1day / 1 cluster per week, 2 to 3 per cluster | Which candidate is the clinically current seizure-frequency rate, and which rate should be rejected as a distractor or lower-priority window? |
| 3356 | deterministic_overreach | disable_seizure_free_no_event_assertions | currently_no_seizure / seizure free for multiple year | seizure_freq_unknown / no seizure frequency reference | seizure_freq_unknown / unknown | Which candidate is the clinically current seizure-frequency rate, and which rate should be rejected as a distractor or lower-priority window? |
| 6131 | deterministic_overreach | disable_seizure_free_no_event_assertions | currently_no_seizure / seizure free for 6 month | seizure_freq_unknown / no seizure frequency reference | seizure_freq_unknown / unknown | Which candidate is the clinically current seizure-frequency rate, and which rate should be rejected as a distractor or lower-priority window? |
| 6889 | deterministic_overreach | disable_temporal_selection | seizure_freq_more1mon_less1week / 1 per 2 to 3 week | seizure_freq_unknown / multiple per week | seizure_freq_unknown / multiple per week | Does the selected frequency evidence actually describe the patient's current seizures, or should the answer remain unknown/no-reference? |
| 13209 | deterministic_overreach | disable_temporal_selection | seizure_freq_more1per6mon_less1mon / 1 per 4 to 5 week | seizure_freq_1_per_yr / 1 per 8 month | seizure_freq_1_per_yr / 1 per 8 month | Which candidate is the clinically current seizure-frequency rate, and which rate should be rejected as a distractor or lower-priority window? |
| 15986 | deterministic_overreach | disable_temporal_selection | seizure_freq_more1week_less1day / 1 per 5 to 7 day | seizure_freq_more1mon_less1week / 11 per 3 month | seizure_freq_more1mon_less1week / 11 per 3 month | Which candidate is the clinically current seizure-frequency rate, and which rate should be rejected as a distractor or lower-priority window? |
| 5921 | deterministic_overreach | disable_temporal_selection | seizure_freq_1ormore_daily / 1 per day | seizure_freq_more1per6mon_less1mon / 1 per 6 to 8 week | seizure_freq_more1per6mon_less1mon / 1 per 6 to 8 week | Which candidate is the clinically current seizure-frequency rate, and which rate should be rejected as a distractor or lower-priority window? |
| 10386 | deterministic_overreach | disable_temporal_selection | seizure_freq_1ormore_daily / 1 per day | seizure_freq_more1week_less1day / 1 cluster per week, 2 to 3 per cluster | seizure_freq_more1week_less1day / 1 cluster per week, 2 to 3 per cluster | Which candidate is the clinically current seizure-frequency rate, and which rate should be rejected as a distractor or lower-priority window? |
| 15242 | deterministic_support_control | disable_cluster_arithmetic | seizure_freq_1_per_mon / multiple cluster per 15 month, multiple per cluster | seizure_freq_unknown / no seizure frequency reference | seizure_freq_1_per_mon / multiple cluster per 15 month, multiple per cluster | Why is the deterministic frequency candidate necessary, and what evidence supports keeping it? |
| 10807 | deterministic_support_control | disable_cluster_arithmetic | seizure_freq_1_per_week / 2 cluster per month, multiple per cluster | currently_no_seizure / seizure free for multiple year | seizure_freq_1_per_week / 2 cluster per month, multiple per cluster | How should a seizure-free assertion be reconciled against explicit current frequency evidence? |
| 10517 | deterministic_support_control | disable_cluster_arithmetic | seizure_freq_1ormore_daily / 3 to 4 cluster per week, multiple per cluster | seizure_freq_unknown / no seizure frequency reference | seizure_freq_1ormore_daily / 3 to 4 cluster per week, multiple per cluster | Why is the deterministic frequency candidate necessary, and what evidence supports keeping it? |
| 15497 | deterministic_support_control | disable_cluster_arithmetic | seizure_freq_1ormore_daily / 1 cluster per 4 to 5 day, 5 per cluster | seizure_freq_unknown / no seizure frequency reference | seizure_freq_1ormore_daily / 1 cluster per 4 to 5 day, 5 per cluster | Why is the deterministic frequency candidate necessary, and what evidence supports keeping it? |
| 7401 | deterministic_support_control | disable_cluster_arithmetic | seizure_freq_more1mon_less1week / 2 cluster per 6 week, 1 to 2 per cluster | seizure_freq_1_per_mon / 1 to 2 per 6 week | seizure_freq_more1mon_less1week / 2 cluster per 6 week, 1 to 2 per cluster | Should the deterministic final selection be accepted or overridden after reviewing assertion, temporality, target, window, rate, and uncertainty? |
| 4337 | deterministic_support_control | disable_diary_log_aggregation | seizure_freq_1_per_mon / 3 per 3 month | currently_no_seizure / seizure free for multiple year | seizure_freq_1_per_mon / 3 per 3 month | How should a seizure-free assertion be reconciled against explicit current frequency evidence? |

## First Reasoning Experiment Scaffold

Use each JSONL record as one DSPy/example input. A first adjudicator can receive `candidate_events`, `normalized_events`, and `deterministic_final_selection`, then produce the decision-record fields listed in `adjudicator_target` plus a Gan-compatible `final_label`. Compare the adjudicated label to `reference.gold_label` on this development set only before running any broader validation pass.
