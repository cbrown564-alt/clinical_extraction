# Gan 2026 LLM-Only Minimal Evidence Selector V0

Date: 2026-06-01

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a minimal model-boundary schema can capture the prediction-bearing answer and exact evidence while deterministic sidecars recover rich diagnostics.

Prediction-bearing component: model-produced `answer` object. Deterministic code validates structure and evidence, runs strict scorer-format repair and frozen clean scorer-facing policy, derives diagnostic state, and scores each layer.

Data surface: `validation` split, `gan2026_split_v1`, 25 rows.
Escalation reason: not applicable for this run size.

## Model And Prompt Metadata

- Pipeline: `gan2026_llm_only_minimal_evidence_selector_v0`
- DSPy version: `3.2.1`
- Runtime model display/API identifier: `openai/gpt-4.1-mini`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-only minimal evidence selector
- Prompt/program version: `gan2026_llm_only_minimal_evidence_selector_v0`
- Temperature: `0.0`
- Max tokens: `900`
- Mode: `live`
- DSPy cache enabled: `True`
- Reused raw model outputs: `0`
- Reuse source: `none`
- Optimizer: none
- Prompt policy taxonomy: `mes_v0.schema.shallow_json_object`, `mes_v0.evidence.exact_answer_substring`, `mes_v0.answer.source_near_text`
- Schema contract: `minimal_model_boundary_plus_derived_diagnostics_v0`
- Deterministic rule configuration: none before prediction; deterministic code validates, performs strict/frozen clean scorer-facing repair, derives diagnostics, and scores.
- Git commit: `a06170a`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_llm_only_minimal_evidence_selector_validation25_v0_2026-06-01.jsonl`

## Summary

- Minimal evidence records: 25 / 25
- Call failures: 0
- Invalid JSON failures: 0
- Schema failures: 0
- Parse/schema issues: 0
- Exact answer evidence substrings: 24 / 25
- Exact supporting-fact evidence substrings: 49 / 50
- Raw minimal-answer score: Purist 0.0800 (2 / 25), Pragmatic 0.0800 (2 / 25)
- Strict-format score: Purist 0.6000 (15 / 25), Pragmatic 0.6000 (15 / 25)
- Frozen clean scorer-facing score: Purist 0.6400 (16 / 25), Pragmatic 0.6400 (16 / 25)
- Rows changed by downstream repair layers: 21
- Answer states: {'cluster_frequency': 2, 'frequency': 23}

## Derived Diagnostic Completeness

- Derived state sidecar complete: 25 / 25
- Review projection complete: 25 / 25
- Normalization sidecar complete with monthly frequency: 16 / 25
- Fully complete scorer-facing derived diagnostics: 16 / 25
- Incomplete normalization rows are the same scorer-format/clean-normalization stress surface reflected by low raw scorable count and 16 / 25 frozen clean scorer-facing Purist/Pragmatic correctness.

## Contract And Evidence Issues

| Row | Contract issues | Evidence issues | Raw scorer-format issue |
| ---: | --- | --- | --- |
| 10 |  |  | unparsable_label: ≤ four per day (Unparsable label (raw: '≤ four per day' / normalized: '≤ four per day')) |
| 40 |  |  | unparsable_label: ≤ four seizures per week (Unparsable label (raw: '≤ four seizures per week' / normalized: '≤ four seizures per week')) |
| 79 |  |  | unparsable_label: ≤ 6 to 7 per year (Unparsable label (raw: '≤ 6 to 7 per year' / normalized: '≤ 6 to 7 per year')) |
| 103 |  |  | unparsable_label: ≤ two or four per year (Unparsable label (raw: '≤ two or four per year' / normalized: '≤ two or four per year')) |
| 156 |  |  | unparsable_label: seizures every 6 days (Unparsable label (raw: 'seizures every 6 days' / normalized: 'seizures every 6 days')) |
| 180 |  |  | unparsable_label: seizures every seven days (Unparsable label (raw: 'seizures every seven days' / normalized: 'seizures every seven days')) |
| 182 |  |  | unparsable_label: seizures are occurring every 2 days on average (Unparsable label (raw: 'seizures are occurring every 2 days on average' / normalized: 'seizures are occurring every 2 days on average')) |
| 187 |  |  | unparsable_label: events tend to cluster every seven to nine days (Unparsable cluster label: 'events tend to cluster every seven to nine days') |
| 190 |  |  | unparsable_label: clusters of brief absence episodes every 4 weeks (Unparsable cluster label: 'clusters of brief absence episodes every 4 weeks') |
| 198 |  |  | unparsable_label: seizures every 4 weeks (Unparsable label (raw: 'seizures every 4 weeks' / normalized: 'seizures every 4 weeks')) |
| 212 |  |  | unparsable_label: ongoing episodes occurring every 3 - 4 weeks (Unparsable label (raw: 'ongoing episodes occurring every 3 - 4 weeks' / normalized: 'ongoing episodes occurring every 3 to 4 weeks')) |
| 218 |  |  | unparsable_label: seizures every 3 weeks (Unparsable label (raw: 'seizures every 3 weeks' / normalized: 'seizures every 3 weeks')) |
| 243 |  | answer evidence not exact (he and his partner report that the seizures occur every four months); supporting fact evidence not exact (f1: he and his partner report that the seizures occur every four months) | unparsable_label: seizures occur every four months (Unparsable label (raw: 'seizures occur every four months' / normalized: 'seizures occur every four months')) |
| 278 |  |  | unparsable_label: multiple times in past week (Unparsable label (raw: 'multiple times in past week' / normalized: 'multiple times in past week')) |
| 280 |  |  | unparsable_label: multiple seizures in past day (Unparsable label (raw: 'multiple seizures in past day' / normalized: 'multiple seizures in past day')) |
| 338 |  |  | unparsable_label: many convulsions in past month (Unparsable label (raw: 'many convulsions in past month' / normalized: 'many convulsions in past month')) |
| 409 |  |  | unparsable_label: ≤ once per month (Unparsable label (raw: '≤ once per month' / normalized: '≤ once per month')) |
| 419 |  |  | unparsable_label: approximately twice per year (Unparsable label (raw: 'approximately twice per year' / normalized: 'approximately twice per year')) |
| 446 |  |  | unparsable_label: ≤ twice per week (Unparsable label (raw: '≤ twice per week' / normalized: '≤ twice per week')) |
| 466 |  |  | unparsable_label: 21 to 28 seizures per month (Unparsable label (raw: '21 to 28 seizures per month' / normalized: '21 to 28 seizures per month')) |
| 531 |  |  | unparsable_label: 12 to 30 per quarter (Unparsable label (raw: '12 to 30 per quarter' / normalized: '12 to 30 per quarter')) |
| 598 |  |  | unparsable_label: 1 per eight months (Unparsable label (raw: '1 per eight months' / normalized: '1 per eight months')) |
| 659 |  |  | unparsable_label: twice every 4 days (Unparsable label (raw: 'twice every 4 days' / normalized: 'twice every 4 days')) |

## Rows

| Row | State | Raw | Strict | Clean | Gold | Raw Purist | Clean Purist | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | frequency | ≤ four per day | 4 per day | 4 per day | 4 per day |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 40 | frequency | ≤ four seizures per week | ≤ 4 per week | ≤ 4 per week | 4 per week |  |  | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 79 | frequency | ≤ 6 to 7 per year | 6 to 7 per year | 6 to 7 per year | 6 to 7 per year |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 103 | frequency | ≤ two or four per year | ≤ 2 or 4 per year | ≤ 2 or 4 per year | 2 to 4 per year |  |  | cluster_axis=none; boundary_state=ordinary_frequency |
| 128 | frequency | 17 per month | 17 per month | 17 per month | 17 per month | yes | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 156 | frequency | seizures every 6 days | 1 per 6 day | 1 per 6 day | 1 per 6 day |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 180 | frequency | seizures every seven days | 1 per 7 day | 1 per 7 day | 1 per 7 day |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 182 | frequency | seizures are occurring every 2 days on average | are occurring 1 per 2 day on average | are occurring 1 per 2 day on average | 1 per 2 day |  |  | cluster_axis=none; boundary_state=ordinary_frequency |
| 187 | cluster_frequency | events tend to cluster every seven to nine days | tend to cluster every 7 to 9 day | tend to cluster every 7 to 9 day | 1 per 7 to 9 day |  |  | cluster_axis=cadence_only; boundary_state=ordinary_frequency |
| 190 | cluster_frequency | clusters of brief absence episodes every 4 weeks | clusters brief absence 1 per 4 week | clusters brief absence 1 per 4 week | 1 per 4 week |  |  | cluster_axis=cadence_only; boundary_state=ordinary_frequency |
| 198 | frequency | seizures every 4 weeks | 1 per 4 week | 1 per 4 week | 1 per 4 week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 212 | frequency | ongoing episodes occurring every 3 - 4 weeks | ongoing occurring every 3 to 4 week | ongoing occurring every 3 to 4 week | 1 per 3 to 4 week |  |  | cluster_axis=none; boundary_state=ordinary_frequency |
| 218 | frequency | seizures every 3 weeks | 1 per 3 week | 1 per 3 week | 1 per 3 week |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 243 | frequency | seizures occur every four months | occur 1 per 4 month | occur 1 per 4 month | 1 per 4 month |  |  | cluster_axis=none; boundary_state=ordinary_frequency |
| 278 | frequency | multiple times in past week | multiple times in past week | multiple times in past week | multiple per week |  |  | cluster_axis=none; boundary_state=ordinary_frequency |
| 280 | frequency | multiple seizures in past day | multiple in past day | multiple per day | multiple per day |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 338 | frequency | many convulsions in past month | many convulsions in past month | many convulsions in past month | multiple per month |  |  | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 409 | frequency | ≤ once per month | 1 per month | 1 per month | 1 per month |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 419 | frequency | approximately twice per year | 2 per year | 2 per year | 2 per year |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 446 | frequency | ≤ twice per week | 2 per week | 2 per week | 2 per week |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 466 | frequency | 21 to 28 seizures per month | 21 to 28 per month | 21 to 28 per month | 21 to 28 per month |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 467 | frequency | 9 per month | 9 per month | 9 per month | 9 per month | yes | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 531 | frequency | 12 to 30 per quarter | 12 to 30 per 3 month | 12 to 30 per 3 month | 12 to 30 per 3 month |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 598 | frequency | 1 per eight months | 1 per 8 month | 1 per 8 month | 1 per 8 month |  | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 659 | frequency | twice every 4 days | 1 per 4 day | 1 per 4 day | 2 per 4 day |  | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
