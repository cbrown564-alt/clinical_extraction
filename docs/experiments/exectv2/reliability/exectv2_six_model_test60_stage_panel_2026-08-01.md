# ExECTv2 six-model test60 stage panel

Date: 2026-08-01
Status: complete; Phase A of the 0046 evidence protocol
Row policy: aggregate-only

Protocol: [primary method-comparison surface protocol](exectv2_primary_method_comparison_surface_protocol_2026-08-01.md)

Decision: [0046](../../../decisions/0046-exect-primary-method-comparison-boundary.md)

Machine panel: [panel_aggregate.json](../../../experiments/exectv2_six_model_test60_stage_panel_20260801/panel_aggregate.json)

## Question

What are aggregate `raw_lane_score` (LLM only) and final `clinical_headline` (LLM with rules) for each of the six retained ExECT `test60` conditions?

## Result

Promoted from sealed or sanitized **aggregate** JSON only. No sealed row JSONL was opened. Hosted aggregate SHA-256 values match `experiments/hosted_holdout_panels_20260715.json`. Local Qwen and Gemma sanitized aggregates drifted in hash/bytes while retaining the same public final `clinical_headline` F1; both hashes are recorded in the machine panel.

| Model | LLM only (`raw_lane_score`) | LLM with rules (final) | Δ |
| --- | ---: | ---: | ---: |
| `openai/gpt-4.1-mini` | 0.7343 | 0.7572 | +0.0229 |
| `openai/gpt-5.6-luna` | 0.7631 | 0.7950 | +0.0319 |
| `openai/gpt-5.6-sol` | 0.7771 | 0.8047 | +0.0276 |
| `deepseek/deepseek-v4-flash` | 0.7575 | 0.7881 | +0.0306 |
| `ollama_chat/qwen3.6:35b` | 0.7267 | 0.7872 | +0.0605 |
| `ollama_chat/gemma4:26b` | 0.6918 | 0.7169 | +0.0251 |

Primary method-table fill under decision 0046 remains **GPT-5.6 Sol** (raw `0.7771`, final `0.8047`). The six-model rows are model-comparison evidence.

## Claim boundary

Aggregate-only ExECT test60 stage panel promoted from sealed or sanitized aggregate JSON for decision 0046. LLM-only identity is raw_lane_score; hybrid identity is final clinical_headline / headline_target. No sealed row JSONL was opened. Not the published ExECT benchmark or clinical validation. Hosted-versus-local route differences remain disclosed. Primary method table cites Sol only.

## Next action

Phase B of the same protocol: rules-only four-family `clinical_headline` on `dev140`.
