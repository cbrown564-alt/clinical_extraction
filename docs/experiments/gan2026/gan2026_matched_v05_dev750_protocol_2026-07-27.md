# Gan 2026 matched v0.5 six-model dev750 protocol

Date: 2026-07-27  
Status: predeclared; calls not yet started  
Decision owner: [decision 0043](../../decisions/0043-gan-hosted-comparison-uses-v05-prompt.md)

## Primary question

How do the six selected models compare on Gan dev750 when every
`llm_with_rules` condition uses the exact v0.5 structured-events prompt and the
same current non-prompt pipeline?

This panel supplies the missing development half of the selected v0.5
comparison. It replaces no historical artifact and does not authorize another
test450 run.

## Fixed conditions

- Dataset: Gan 2026.
- Split manifest: `gan2026_split_v1`.
- Split: development `validation750`; row-level analysis is permitted.
- Models: GPT-4.1-mini, GPT-5.6 Luna, GPT-5.6 Sol, DeepSeek V4 Flash,
  Qwen 3.6:35B, and Gemma 4 26B.
- Pipeline: `llm_with_rules`.
- Prompt: `gan2026_hybrid_structured_events_v0.5`.
- Prompt snapshot:
  `tests/snapshots/prompt_contracts/gan2026__hybrid_structured_events_v0.5.txt`,
  SHA-256
  `77a5575244423f989b247ff1e89930c081c0e91a3b19e0ad74687bf40eb90993`.
- Calls: one structured event call per note.
- Cache: disabled.
- Repair: current shared schema repair followed by
  `hybrid_full_stack`.
- Scores: Gan Purist primary and Pragmatic secondary.
- Trace schema: `gan2026.row_trace.v1`.
- Output root:
  `scratch/validation/gan2026_matched_v05_dev750_20260727/`.

Provider-required route, temperature, output limit, and thinking differences
remain explicit in
`configs/gan2026/six_model_v05_dev750_20260727.json`.

## Existing coverage and reuse

| Model | Existing v0.5 development output | Treatment |
| --- | --- | --- |
| GPT-4.1-mini | Historical complete 750-row artifact | Reconcile exact prompt payload and replay all saved raw outputs through the selected current stack; run fresh only if reconciliation fails |
| GPT-5.6 Luna | None | Fresh 750-row condition |
| GPT-5.6 Sol | None | Fresh 750-row condition |
| DeepSeek V4 Flash | None | Fresh 750-row condition |
| Qwen 3.6:35B | Incomplete 45-row attempt | Resume only if all 45 rows match this protocol; otherwise start fresh |
| Gemma 4 26B | None | Fresh 750-row condition |

Reused rows must retain the original raw model output. Reuse may repair schema
or render an already selected fact, but it must not make another model call or
introduce a prediction-bearing fact. Mixed fresh/replay provenance must be
reported by condition.

## Required artifact

The retained machine comparison must contain, for each model:

- exactly 750 unique manifest rows;
- prompt version and prompt snapshot hash;
- route, temperature, output limit, cache state, and replay status;
- call, parse, schema, and final-label failures;
- raw model output, parsed event ledger, selected evidence, semantic repair
  events, final answer, and score-layer trace;
- exact and grounded selected-evidence counts;
- Purist and Pragmatic totals;
- deterministic wrong-to-correct and correct-to-wrong transitions;
- first-failure owner and clinical-subproblem counts.

The narrative report must keep model selection, model-preserving
canonicalization, and prediction-bearing deterministic repair separate.

## Stop rule

Retain a complete condition regardless of score. Stop and repair only for a
transport, resume-identity, prompt-identity, or artifact-integrity failure.
Do not change the prompt, clinical rules, normalization, evidence policy, or
scorer after inspecting model performance.

The panel is complete only when all six conditions contain 750 unique rows and
the aggregate and row-level attribution artifacts reproduce from those saved
outputs.

## Claim boundary

The result will be development evidence for the named models, prompt, routes,
and repair policy. It will not be a model-neutral capability ranking, clinical
validation, or a new holdout result. The existing v0.7 development panel
remains a quarantined prompt-interaction diagnostic and must not be merged with
this panel.
