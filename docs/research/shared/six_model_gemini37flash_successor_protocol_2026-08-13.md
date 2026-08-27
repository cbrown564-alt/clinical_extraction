# Six-model successor roster: Gemini 3.7 Flash replaces GPT-4.1-mini

Date: 2026-08-13
Status: thinking level selected (`low`); live ExECT `dev140` and Gan `dev750` hybrid cells complete; Gan LLM-only `dev750`/`test450` complete ([report](../gan2026/gemini37flash_llm_only_dev750_test450_2026-08-13.md))
Decision: [0051](../../decisions/0051-gemini-37-flash-succeeds-gpt41mini-six-model-slot.md)

## Question

On the permitted development splits, how does Gemini 3.7 Flash compare with
the other five Decision 0051 conditions under the same selected
`llm_with_rules` (and matched `llm`) methods that produced the Decision 0039
panel?

This study exists to change the live roster. It is not a no-call replay of
GPT-4.1-mini raws and not a holdout measurement.

## Data and inspection

| Task | First live cell | Row policy | Out of scope |
| --- | --- | --- | --- |
| ExECTv2 | `dev140` | development row-level | `test60`, full-200 row inspection |
| Gan 2026 | `dev750` (`validation` split key) | development row-level | `test450` unless a later frozen holdout protocol exists (LLM-only: [2026-08-13 protocol](../gan2026/gemini37flash_llm_only_dev750_test450_protocol_2026-08-13.md)) |

Do not open locked holdout rows. Do not copy GPT-4.1-mini scores into a
Gemini cell.

## Successor roster

| Display name | Runtime identifier | Group | Temperature | Max tokens | Thinking |
| --- | --- | --- | ---: | ---: | --- |
| GPT-5.6 Luna | `openai/gpt-5.6-luna` | hosted OpenAI | 1 | 16,000 | provider default |
| Gemini 3.7 Flash | `gemini/gemini-3.7-flash` | hosted Gemini | 0 | 16,000 | `reasoning_effort=low` |
| GPT-5.6 Sol | `openai/gpt-5.6-sol` | hosted OpenAI Responses | 0 / omitted | 16,000 | provider default |
| DeepSeek V4 Flash | `deepseek/deepseek-v4-flash` | hosted DeepSeek | 0 | 32,000 | API default |
| Qwen 3.6:35B | `ollama_chat/qwen3.6:35b` | local Ollama | 0 | 16,000 | `think=false` |
| Gemma 4 26B | `ollama_chat/gemma4:26b` | local Ollama | 0 | 16,000 | `think=false` |

Qwen 3.8 27B is reserved and not a condition in this protocol.

Gemini credential: `GEMINI_API_KEY` in the repository `.env` or the process
environment. The factory also accepts `GOOGLE_API_KEY`. Transport is Google's
OpenAI-compatible endpoint. Cache is off.

## Thinking-level check (2026-08-13)

Same 10 ExECT `dev140` letters (`EA0002`, `EA0004`–`EA0012`), raw structured
lane only, no assembly. Official 3.7 Flash default is `medium`; `minimal`
errors; thinking cannot be turned off.

| | `low` | `medium` |
| --- | ---: | ---: |
| Wall time | 37s | 90s |
| Call / schema failures | 0 / 0 | 0 / 0 |
| Mentions | 73 | 65 |
| Clinical headline F1 | 0.924 | 0.937 |
| Precision / recall | 0.924 / 0.924 | 0.966 / 0.909 |

The F1 gap is Diagnosis only. Medium drops seizure-type mentions (higher
precision, lower recall, including a full miss of gold
`bilateral-convulsive-seizure` on EA0009). Low matches the existing
model-led inventory style. **Selected thinking level for live successor
cells: `low`.**

## Artifact locations

Live cells go under `experiments/`, not `scratch/`.

- ExECT `dev140`:
  `experiments/exectv2_six_model_single_call_gemini37flash_dev140_20260813*`
- Gan `dev750` hybrid rows, same slug/file shape as the current-stack tree:
  `experiments/gan2026_six_model_current_stack_dev750_replay_20260813/gemini37flash/validation750.rows.jsonl`
- Gan `dev750` LLM-only rows, July 18 tree:
  `experiments/gan2026_six_model_validation_20260718/gemini37flash--llm_only.jsonl`

## Fixed pipelines

- ExECT: Decision 0040 model-led families, Decision 0041 one structured
  four-family call, Decision 0045 `default`/`default` assembly, prompt
  `exectv2_hybrid_key_family_event_ledger_v0.9.24`.
- Gan hybrid: `llm_with_rules` / `hybrid_structured_events`, selected hosted
  prompt `gan2026_hybrid_structured_events_v0.5` ([decision 0043](../../decisions/0043-gan-hosted-comparison-uses-v05-prompt.md)).
- Gan LLM-only, if run: `gan2026_llm_only_canonical_pipeline_v0.8`.
- Scorers, splits, and clinical repairs stay on HEAD. A repair or scorer edit
  is a new study.

The five non-Gemini conditions already have retained sidecars. This protocol
does not require rerunning them before the Gemini cell exists. A later
no-call current-stack readout can add Gemini only after its raws exist.

## Commands

Smoke (one ExECT `dev140` letter, not a score). The smoke runner loads
manifest `dev` only; it must not slice the full corpus.

```bash
GEMINI_REASONING_EFFORT=low .venv/bin/python scripts/smoke_exectv2_six_model_condition.py \
  --config configs/exectv2/six_model_comparison/gemini37flash_dev140.json \
  --rows 1 \
  --output scratch/validation/gemini37flash_thinking/smoke_low_dev1.jsonl
```

ExECT `dev140` live cell:

```bash
GEMINI_REASONING_EFFORT=low .venv/bin/python scripts/run_exectv2_six_model_comparison.py \
  --config configs/exectv2/six_model_comparison/gemini37flash_dev140.json \
  --no-dspy-cache --generated-on 2026-08-13
```

Gan `dev750` hybrid live cell (v0.5):

```bash
GEMINI_REASONING_EFFORT=low .venv/bin/python scripts/run_gan2026_v05_hosted_condition.py \
  --prompt-version gan2026_hybrid_structured_events_v0.5 \
  --pipeline llm_with_rules \
  --split validation \
  --model gemini/gemini-3.7-flash \
  --temperature 0 \
  --max-tokens 16000 \
  --disable-dspy-cache \
  --escalation-reason "Decision 0051 successor Gemini 3.7 Flash live dev750 cell" \
  --jsonl experiments/gan2026_six_model_current_stack_dev750_replay_20260813/gemini37flash/validation750.rows.jsonl \
  --markdown experiments/gan2026_six_model_current_stack_dev750_replay_20260813/gemini37flash/validation750.report.md
```

## Claim boundary

Development candidate only until a report names dataset, split, row policy,
scorer, model, prompt, replay mode, and repair policy. Not holdout
generalization. Not clinical validation. Not a replacement of Decision 0050
primary fills. GPT-4.1-mini remains the historical 0039 cell.
