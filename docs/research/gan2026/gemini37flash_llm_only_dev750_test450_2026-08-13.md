# Gemini 3.7 Flash Gan LLM-only v0.8 on `dev750` and `test450`

Date: 2026-08-13
Status: complete
Protocol: [predeclared protocol](gemini37flash_llm_only_dev750_test450_protocol_2026-08-13.md)
Artifact: [`experiments/gan2026_six_model_llm_only_gemini37flash_20260813/summary.json`](../../experiments/gan2026_six_model_llm_only_gemini37flash_20260813/summary.json)
Decision: [0051](../../decisions/0051-gemini-37-flash-succeeds-gpt41mini-six-model-slot.md)

## Finding

Gemini 3.7 Flash (`reasoning_effort=low`) on the matched LLM-only pipeline
`gan2026_llm_only_canonical_pipeline_v0.8`:

| Split | Row policy | Purist | Pragmatic | Call failures | Parse/schema |
| --- | --- | ---: | ---: | ---: | ---: |
| `dev750` | development, inspectable | **578/750 (0.7707)** | 607/750 (0.8093) | 0 | 0 |
| `test450` | aggregate-only | **319/450 (0.7089)** | 340/450 (0.7556) | 0 | 1 |

These are successor-roster `llm` cells. They do not replace Decision 0050 /
0052 hybrid fills. Sol remains the paper method-identity row (Gan `test450`
LLM-only **335/450**; hybrid **380/450**). GPT-4.1-mini scores were not
copied.

## Frozen condition

| Field | Value |
| --- | --- |
| Model | `gemini/gemini-3.7-flash` |
| Thinking | `reasoning_effort=low` |
| Temperature | `0` |
| Max tokens | 16,000 |
| Cache | off |
| Pipeline | `llm` / `llm_only_canonical_pipeline` |
| Prompt | `gan2026_llm_only_canonical_pipeline_v0.8` |
| Repair | `model_selected_evidence_benchmark_adapter` |
| Scorer | Purist primary; Pragmatic side-car |
| Manifest | `gan2026_split_v1` |

Live `dev750` wall time 19.97 minutes. Live `test450` wall time 11.49 minutes.
The one `test450` parse/schema failure is left as a failure; it was not
inspected and does not license holdout repair.

## Artifacts

| Role | Path |
| --- | --- |
| `dev750` rows | `experiments/gan2026_six_model_validation_20260718/gemini37flash--llm_only.jsonl` |
| `dev750` report | `experiments/gan2026_six_model_llm_only_gemini37flash_20260813/validation750.report.md` |
| `test450` sealed dump | `scratch/holdout/gemini37flash_llm_only_20260813/gan_test450/sealed_rows.jsonl` |
| `test450` aggregate | `scratch/holdout/gemini37flash_llm_only_20260813/gan_test450/aggregate.md` |
| Explorer catalog | `frontend/public/mock-data/pipeline-families.json` |

The explorer now serves the Gemini LLM-only `dev750` cell as replay.

## Context, not a rewrite

July 18 six-model LLM-only `dev750` (historical, different models): Sol
590/750, GPT-4.1-mini 577/750, Qwen 565/750, DeepSeek 559/750, Luna 558/750,
Gemma 512/750. The 1 August LLM-only `test450` panel: Sol 335/450, DeepSeek
332/450, GPT-4.1-mini 330/450, Luna 319/450, Qwen 316/450, Gemma 305/450.

Gemini hybrid cells from the same day remain a different method: `dev750`
676/750 Purist and `test450` 373/450 Purist.

## ExECT llm-only peers (no new call)

Decision 0041/0046 LLM-only is the `raw_lane_score` of the existing one-call
packages: `dev140` **0.8444**, `test60` **0.82**.

## Claim boundary

`dev750` is inspectable development. `test450` is aggregate-only; no holdout
identifier, note, prediction, evidence, or error was inspected. Not clinical
validation. Not a replacement of Decision 0050 / 0052 hybrid fills or
Decision 0046 Sol method identity.
