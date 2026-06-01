# Windows Local Ollama Runbook

This runbook covers repository-side preparation for running Gan 2026 LLM
experiments on a Windows laptop with a local Qwen model served by Ollama.
Install and configure Ollama separately first.

## Environment

From the repo root in PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest
```

If PowerShell blocks activation, enable scripts for the current user:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## Smoke Test Without Model Calls

Confirm the CLI, split loading, and artifact writing work before touching the
local model:

```powershell
gan2026-llm-experiment --pipeline llm_only_claim_table_selector --mode prompt-only --limit 25 --jsonl experiments\windows_prompt_only.jsonl --markdown experiments\windows_prompt_only.md
```

## Local Model Smoke Test

After Ollama is running and the Qwen model is available locally, run a small
live test through the OpenAI-compatible endpoint:

```powershell
gan2026-llm-experiment --pipeline llm_only_claim_table_selector --mode live --limit 25 --model openai/qwen-model-name --api-base http://localhost:11434/v1 --jsonl experiments\windows_qwen25.jsonl --markdown experiments\windows_qwen25.md
```

Replace `qwen-model-name` with the exact local model name reported by
`ollama list`.

## Portability Notes

- Prefer `python -m pytest`, `python -m ruff check .`, and
  `python -m mypy src tests` over shell aliases.
- Keep repo paths relative when passing artifact paths.
- Paths containing spaces, such as `data\Gan (2026)\...`, should be quoted in
  ad hoc commands.
- The LLM report records `api_base`; add quantization and hardware notes to the
  experiment report or project status when comparing local and hosted runs.
