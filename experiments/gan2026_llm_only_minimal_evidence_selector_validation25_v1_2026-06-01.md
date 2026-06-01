# Gan 2026 LLM-Only Minimal Evidence Selector V1

Date: 2026-06-01

This is a validation development result on `gan2026_split_v1`. It is not a final holdout or benchmark result.

## Experiment Unit

Hypothesis: a minimal model-boundary schema can capture source-near evidence plus a parser-ready final label while deterministic sidecars recover rich diagnostics.

Prediction-bearing component: model-produced `answer.final_label`. Deterministic code validates structure and evidence, runs strict scorer-format repair and frozen clean scorer-facing policy, derives diagnostic state, and scores each layer.

Data surface: `validation` split, `gan2026_split_v1`, 25 rows.
Escalation reason: not applicable for this run size.

## Model And Prompt Metadata

- Pipeline: `gan2026_llm_only_minimal_evidence_selector_v1`
- DSPy version: `3.2.1`
- Runtime model display/API identifier: `openai/gpt-4.1-mini`
- Provider/execution: hosted OpenAI via DSPy/LiteLLM
- Model role: LLM-only minimal evidence selector
- Prompt/program version: `gan2026_llm_only_minimal_evidence_selector_v1`
- Temperature: `0.0`
- Max tokens: `900`
- Mode: `live`
- DSPy cache enabled: `False`
- Reused raw model outputs: `0`
- Reuse source: `none`
- Optimizer: none
- Prompt policy taxonomy: `mes_v1.schema.shallow_json_object`, `mes_v1.evidence.exact_answer_substring`, `mes_v1.answer.source_near_text`, `mes_v1.answer.parser_ready_final_label`
- Schema contract: `minimal_model_boundary_with_final_label_plus_derived_diagnostics_v1`
- Deterministic rule configuration: none before prediction; deterministic code validates, performs strict/frozen clean scorer-facing repair, derives diagnostics, and scores.
- Git commit: `a06170a`
- Working tree note: `dirty/uncommitted local changes`
- JSONL artifact: `experiments/gan2026_llm_only_minimal_evidence_selector_validation25_v1_2026-06-01.jsonl`

## Summary

- Minimal evidence records: 25 / 25
- Call failures: 0
- Invalid JSON failures: 0
- Schema failures: 0
- Parse/schema issues: 0
- Exact answer evidence substrings: 25 / 25
- Exact supporting-fact evidence substrings: 40 / 40
- Raw minimal-final-label score: Purist 1.0000 (25 / 25), Pragmatic 1.0000 (25 / 25)
- Strict-format score: Purist 1.0000 (25 / 25), Pragmatic 1.0000 (25 / 25)
- Frozen clean scorer-facing score: Purist 1.0000 (25 / 25), Pragmatic 1.0000 (25 / 25)
- Rows changed by downstream repair layers: 0
- Answer states: {'cluster_frequency': 2, 'frequency': 23}

## Contract And Evidence Issues

| Row | Contract issues | Evidence issues | Raw scorer-format issue |
| ---: | --- | --- | --- |
| 409 | repair: minimal_alias_shape_repair_v0 |  |  |
| 659 | repair: minimal_alias_shape_repair_v0 |  |  |

## Rows

| Row | State | Raw | Strict | Clean | Gold | Raw Purist | Clean Purist | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | frequency | 4 per day | 4 per day | 4 per day | 4 per day | yes | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 40 | frequency | 4 per week | 4 per week | 4 per week | 4 per week | yes | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 79 | frequency | 6 to 7 per year | 6 to 7 per year | 6 to 7 per year | 6 to 7 per year | yes | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 103 | frequency | 2 to 4 per year | 2 to 4 per year | 2 to 4 per year | 2 to 4 per year | yes | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 128 | frequency | 17 per month | 17 per month | 17 per month | 17 per month | yes | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 156 | frequency | 1 per 6 day | 1 per 6 day | 1 per 6 day | 1 per 6 day | yes | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 180 | frequency | 1 per 7 day | 1 per 7 day | 1 per 7 day | 1 per 7 day | yes | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 182 | frequency | 1 per 2 day | 1 per 2 day | 1 per 2 day | 1 per 2 day | yes | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 187 | cluster_frequency | 1 per 7 to 9 day | 1 per 7 to 9 day | 1 per 7 to 9 day | 1 per 7 to 9 day | yes | yes | cluster_axis=cadence_only; boundary_state=ordinary_frequency |
| 190 | cluster_frequency | 1 per 4 week | 1 per 4 week | 1 per 4 week | 1 per 4 week | yes | yes | cluster_axis=cadence_only; boundary_state=ordinary_frequency |
| 198 | frequency | 1 per 4 week | 1 per 4 week | 1 per 4 week | 1 per 4 week | yes | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 212 | frequency | 1 per 3 to 4 week | 1 per 3 to 4 week | 1 per 3 to 4 week | 1 per 3 to 4 week | yes | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 218 | frequency | 1 per 3 week | 1 per 3 week | 1 per 3 week | 1 per 3 week | yes | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 243 | frequency | 1 per 4 month | 1 per 4 month | 1 per 4 month | 1 per 4 month | yes | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 278 | frequency | multiple per week | multiple per week | multiple per week | multiple per week | yes | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 280 | frequency | multiple per day | multiple per day | multiple per day | multiple per day | yes | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 338 | frequency | multiple per month | multiple per month | multiple per month | multiple per month | yes | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 409 | frequency | 1 per month | 1 per month | 1 per month | 1 per month | yes | yes | schema_repair: fact_text copied to evidence; schema_repair: fact_text copied to evidence; cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 419 | frequency | 2 per year | 2 per year | 2 per year | 2 per year | yes | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 446 | frequency | 2 per week | 2 per week | 2 per week | 2 per week | yes | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 466 | frequency | 21 to 28 per month | 21 to 28 per month | 21 to 28 per month | 21 to 28 per month | yes | yes | cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
| 467 | frequency | 9 per month | 9 per month | 9 per month | 9 per month | yes | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 531 | frequency | 12 to 30 per 3 month | 12 to 30 per 3 month | 12 to 30 per 3 month | 12 to 30 per 3 month | yes | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 598 | frequency | 1 per 8 month | 1 per 8 month | 1 per 8 month | 1 per 8 month | yes | yes | cluster_axis=none; boundary_state=ordinary_frequency |
| 659 | frequency | 2 per 4 day | 2 per 4 day | 2 per 4 day | 2 per 4 day | yes | yes | schema_repair: cluster_context role mapped to context; cluster_axis=vague_cluster; boundary_state=ordinary_frequency |
