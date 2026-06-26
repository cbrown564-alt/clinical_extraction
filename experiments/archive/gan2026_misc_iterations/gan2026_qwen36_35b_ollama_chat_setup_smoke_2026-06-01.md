# Gan 2026 Qwen 3.6 35B Ollama Setup Smoke

Date: 2026-06-01

This is a local setup and output-contract smoke, not a benchmark or holdout
result.

## Endpoint Policy

- Intended local tag: `qwen3.6:35b`
- Acceptable hardware-constrained smoke tag: `qwen3.6:27b`
- DSPy/LiteLLM identifier used for Qwen: `ollama_chat/qwen3.6:35b`
- Endpoint used by DSPy/LiteLLM: `http://localhost:11434`
- Rejected route for Qwen reasoning models: `openai/qwen3.6:35b` with
  `http://localhost:11434/v1`
- Thinking mode: disabled through `extra_body={"think": False}` in the shared
  LM builder for `ollama_chat/...` models

The OpenAI-compatible `/v1/chat/completions` route is not used for Qwen 3.6
experiments because it can return hidden reasoning while leaving final assistant
content empty, which creates parse failures unrelated to extraction quality.

## Local Model Metadata

Metadata came from Ollama HTTP endpoints on this Windows machine.

- Installed tag: `qwen3.6:35b`
- Digest: `07d35212591fc27746f0a317c975a6d68754fb38e9053d82e25f06057af28522`
- Format/family: `gguf`; `qwen35moe`
- Parameter size: `36.0B`
- Quantization: `Q4_K_M`
- Loaded context length observed from `/api/ps`: `4096`
- Loaded VRAM allocation observed from `/api/ps`: `7059572992` bytes
- Native `/api/chat` smoke latency with `think=false`: about `87848 ms`

Machine notes:

- OS: Microsoft Windows 11 Home 64-bit, version `10.0.26200`
- Machine: Dell Inc. XPS 16 9640
- RAM: about `32 GB`
- GPUs visible to Windows: Intel Arc Graphics and NVIDIA GeForce RTX 4070 Laptop
  GPU
- Python used for repo smoke: `3.13.5`

## Artifacts

- Prompt-only v5 frozen surface:
  `experiments/gan2026_llm_only_claim_table_selector_validation1_prompt_only_v5_2026-06-01.jsonl`
- Prompt-only report:
  `experiments/gan2026_llm_only_claim_table_selector_validation1_prompt_only_v5_2026-06-01.md`
- Live local Qwen validation1 smoke:
  `experiments/gan2026_llm_only_claim_table_selector_validation1_qwen36_35b_v5_ollama_chat_smoke_2026-06-01.jsonl`
- Live local Qwen report:
  `experiments/gan2026_llm_only_claim_table_selector_validation1_qwen36_35b_v5_ollama_chat_smoke_2026-06-01.md`

## Smoke Result

The corrected native Ollama route completed one validation row with:

- Call failures: `0 / 1`
- Reused raw outputs: `0 / 1`
- DSPy cache: disabled
- Structured records: `0 / 1`
- Parse/schema failures: `1 / 1`

The raw model output was nonempty, so this is not the hidden-reasoning/empty
assistant-content failure from the OpenAI-compatible route. The local Qwen model
returned a Python-style single-quoted object and used a `final_selector` shape
instead of the required strict JSON `final_query` object. Treat this as a
Qwen-specific output-contract failure on v5, not as an endpoint failure and not
as a meaningful model-quality score.

## Decision

Endpoint setup is unblocked for native Ollama chat. Do not start a validation5
or validation25 ladder until one of these is done on validation-only rows:

- prompt hardening that makes Qwen emit strict JSON and the required
  `final_query` schema; or
- an explicitly named schema-repair ablation that can repair Python-style dicts
  and selector aliases without hiding semantic changes.

Holdout policy is unchanged.
