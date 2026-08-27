# Local vLLM dev10 runbook (Windows workstation)

Created: 2026-08-10
Status: **executed 2026-08-10**. Claim boundary and artifact paths are in
[project status, blocked](../../PROJECT_STATUS.md#blocked-or-unvalidated).
Steps 1 and 2 were superseded in execution: the workstation has an NVIDIA
RTX 4070, so the CUDA `vllm/vllm-openai` image under Docker/WSL2 replaced the
CPU source build. Findings for `chat_template_kwargs`, thinking, and
guided JSON are in this runbook. Artifacts:
`scratch/validation/vllm-dev10.rows.jsonl` and
`scratch/validation/vllm-dev10.report.md`.
Owner task: the supervisor-endpoint leftover in
[project status](../../PROJECT_STATUS.md#blocked-or-unvalidated) and item 4
of the [active roadmap](../plans/ACTIVE_ROADMAP.md).

## Why this runbook exists

The supervisor's DeepSeek vLLM endpoint is private and will not be shared. The
original task text assumed we would probe that exact endpoint. We cannot. This
runbook substitutes a **locally served vLLM endpoint** so that the transport,
chat-template, structured-output, and artifact path can still be exercised
end to end before the supervisor's endpoint is ever available.

Read the claim boundary in [What this does and does not establish](#what-this-does-and-does-not-establish)
before recording any result. A local stand-in verifies **our side of the
contract**. It cannot verify their host, their served weights, or their
serving flags.

The macOS laptop was rejected as the host: it is an M1 with 16 GB and, at the
time of writing, 6.6 GiB free on a 99%-full volume. The 16 GiB `uv` package
cache there is not reclaimable while the `elevenlabs-mcp` server runs from
inside it. The Windows workstation (32 GB RAM, ample disk) is the host.

## Host prerequisites

vLLM does not support Windows natively. Run it under **WSL2**, not PowerShell.

1. WSL2 with Ubuntu 22.04 or 24.04:
   ```powershell
   wsl --install -d Ubuntu-24.04
   ```
2. Inside WSL, confirm memory visible to the VM is most of the 32 GB. If it is
   capped, raise it in `%UserProfile%\.wslconfig`:
   ```ini
   [wsl2]
   memory=24GB
   processors=8
   ```
   then `wsl --shutdown` and reopen.
3. Build toolchain and a supported Python. **vLLM does not support Python 3.14**;
   the macOS project venv is 3.14, which is one reason the server must be a
   separate environment. Use 3.12:
   ```sh
   sudo apt update
   sudo apt install -y build-essential cmake ninja-build python3.12 python3.12-venv git
   ```

Keep the vLLM server environment **separate from the project venv**. They
communicate over HTTP only; there is no import-level coupling, and mixing them
risks disturbing the pinned research environment.

## Step 1 — Build the vLLM CPU backend

There is no prebuilt CPU wheel; the published `vllm/vllm-openai` image is CUDA
only. Build from source:

```sh
python3.12 -m venv ~/vllm-env
source ~/vllm-env/bin/activate
pip install --upgrade pip
git clone https://github.com/vllm-project/vllm.git ~/vllm-src
cd ~/vllm-src
pip install -r requirements/cpu.txt --extra-index-url https://download.pytorch.org/whl/cpu
VLLM_TARGET_DEVICE=cpu pip install -e . --no-build-isolation
```

Expect a long compile. If it fails, record the exact error before retrying —
a build failure is a finding about the CPU backend, not a step to silently
work around.

If the workstation has an NVIDIA GPU, prefer the CUDA path instead
(`pip install vllm`) — it is faster, better tested, and closer to how the
supervisor's endpoint is almost certainly served. Record which path was used.

## Step 2 — Choose and serve the model

Serve a **thinking-capable** model so `VLLM_THINKING` is exercised rather than
ignored. `Qwen/Qwen3-1.7B` fits comfortably in 32 GB at bf16 and its chat
template implements a thinking switch. `Qwen/Qwen3-0.6B` is the fallback if
generation is too slow on CPU.

The `--served-model-name` must match exactly what we put after `vllm/` in the
model identifier — the README is explicit that the value after `vllm/` must
equal the name returned by `/v1/models`.

```sh
source ~/vllm-env/bin/activate
vllm serve Qwen/Qwen3-1.7B \
  --served-model-name qwen3-1.7b \
  --host 127.0.0.1 --port 8000 \
  --max-model-len 8192 \
  --dtype bfloat16
```

Confirm the served name before going further:

```sh
curl -s http://127.0.0.1:8000/v1/models | python3 -m json.tool
```

## Step 3 — The chat-template kwarg mismatch (expected finding)

This is the most likely real incompatibility and should be tested deliberately.

`build_dspy_lm` in
[`llm_config.py`](../../src/clinical_extraction/tasks/seizure_frequency/gan2026/llm_config.py)
sends, for every `vllm/` route:

```python
extra_body = {"chat_template_kwargs": {"thinking": <bool>}}
```

The key name `thinking` is **model-template-specific, not a vLLM-wide
setting**. DeepSeek-V3.1-style templates read `thinking`. Qwen3's template
reads `enable_thinking`. vLLM passes these kwargs into Jinja template
rendering, and an unrecognised key is **silently ignored** — no error, no
warning.

So against Qwen3, `VLLM_THINKING=false` is expected to do nothing, leaving
thinking mode on and `<think>` blocks in the output. Two consequences to watch:

- Reasoning text may leak into content and break schema parsing.
- Reasoning consumes the token budget. The `llm` pipeline defaults to 1200
  `max_tokens` and `rules` to 900; a thinking model can spend all of that
  before emitting any answer.

**Test both explicitly** and record which key the served template honours:

```sh
# expect: thinking still active, <think> present
curl -s http://127.0.0.1:8000/v1/chat/completions -H 'Content-Type: application/json' -d '{
  "model":"qwen3-1.7b","max_tokens":200,
  "messages":[{"role":"user","content":"Reply with JSON {\"ok\":true}"}],
  "chat_template_kwargs":{"thinking":false}}' | python3 -m json.tool

# expect: thinking suppressed
curl -s http://127.0.0.1:8000/v1/chat/completions -H 'Content-Type: application/json' -d '{
  "model":"qwen3-1.7b","max_tokens":200,
  "messages":[{"role":"user","content":"Reply with JSON {\"ok\":true}"}],
  "chat_template_kwargs":{"enable_thinking":false}}' | python3 -m json.tool
```

If confirmed, **do not quietly rename the key**. The correct handling is a
predeclared decision: either make the kwarg name configurable per served
template, or document that `VLLM_THINKING` only governs DeepSeek-family
templates. Either way it is a question to put to the supervisor about their
endpoint, because the same silent-ignore applies there.

## Step 4 — Synthetic probe

From the project checkout, in the **project** environment (Python 3.11–3.13;
`requires-python = ">=3.11"`):

```sh
python -m pip install -e .
clinical-extract probe \
  --base-url http://127.0.0.1:8000/v1 \
  --model vllm/qwen3-1.7b
```

The keyless default applies: `vllm/<name>` routes fall back to the `EMPTY`
placeholder, so `--api-key` is not needed for an unauthenticated local server.

[`probe_endpoint`](../../src/clinical_extraction/operational/provider.py) sends
`response_format={"type": "json_object"}`. Watch for two things:

- **Guided decoding support.** vLLM implements JSON mode through a structured
  backend (xgrammar/outlines). If it errors or is unsupported on the CPU build,
  that is a transport finding to record, not a reason to drop the constraint.
- **`reasoning_content`.** The probe reports `reasoning_content_present`.
  vLLM only splits reasoning into that field when served with a reasoning
  parser (`--reasoning-parser`). Without it, reasoning stays inline in
  `content`. Record which behaviour was observed, since it changes what the
  parsing path receives.

Record: base URL, served model name, auth mode, `VLLM_THINKING`, token limit,
returned `response_model`, and whether reasoning was split out.

## Step 5 — The fixed dev10 run

Freeze explicit row indices rather than relying on `--limit 10` and first-ten
ordering, per the README. The first ten `source_row_indices` of the Gan
`validation_v1` split (750 rows, the primary development surface) are:

```
10,40,79,103,128,156,180,182,187,190
```

These are development rows and are inspectable. Gan `test450` and ExECT
`test60` remain locked and aggregate-only — this run must not touch them.

```sh
export VLLM_BASE_URL=http://127.0.0.1:8000/v1
export VLLM_THINKING=false

gan2026-llm-experiment \
  --pipeline llm_with_rules \
  --split validation \
  --source-row-indices 10,40,79,103,128,156,180,182,187,190 \
  --model vllm/qwen3-1.7b \
  --max-tokens 5000 \
  --disable-dspy-cache \
  --jsonl scratch/validation/vllm-dev10.rows.jsonl \
  --markdown scratch/validation/vllm-dev10.report.md
```

Notes on the arguments:

- `llm_with_rules` is the selected hybrid method and defaults to 5000
  `max_tokens`, which leaves headroom if thinking cannot be suppressed. If you
  run `--pipeline llm` instead, raise `--max-tokens` above its 1200 default for
  the same reason.
- `--disable-dspy-cache` is required; the run must make real calls.
- Ten validation rows sits far below the 250-row ladder threshold, so no
  `--escalation-reason` is needed.
- The CLI refuses to overwrite existing outputs without `--overwrite-existing`.

## Step 6 — Inspect and test

Inspect the ordinary development artifacts — this is the point of the run, not
the score:

- row JSONL, including per-row `status` and any failure codes;
- raw model output and parse diagnostics;
- prompt inputs and row traces;
- checkpoints; and
- the generated Markdown report's runtime metadata block.

Then run the focused tests:

```sh
pytest tests/test_llm_config.py tests/test_operational_cli.py -v
pytest -q
```

The always-on pytest firewall (decision 0049) applies. A pre-existing
retained-evidence hash drift in the canonical comparison report was already
the sole known failure as of 2026-08-03; distinguish that from anything this
work introduces.

## What this does and does not establish

**Supports:** that `vllm/<served-model>` routes through the shared DSPy
factory to a real vLLM OpenAI-compatible server; that keyless `EMPTY` auth
works; that the canonical pipeline produces normal inspectable development
artifacts over that transport; and evidence about how `chat_template_kwargs`,
guided JSON, and `reasoning_content` actually behave on vLLM.

**Does not support:** any claim about the supervisor's endpoint, host, weights,
or serving flags; any clinical or accuracy result — Qwen3-1.7B is a transport
fixture, and its extraction quality is not evidence about anything; and any
comparison against the retained six-model results.

Record the dev10 artifact paths and this boundary in `PROJECT_STATUS.md` when
the run completes. Per the standing constraint: do not resume DeepSeek U to
750, do not expand beyond dev10 until the runtime behaviour is understood, and
never tune from sealed `test450`, Real(300), or ExECT `test60`.

## Open questions for the supervisor

These are worth asking regardless of how the local run goes, because the local
run cannot answer them:

1. Exact served model name as returned by `/v1/models`.
2. Whether the served chat template reads `thinking` or `enable_thinking`, or
   neither.
3. Whether the server runs with a `--reasoning-parser`.
4. Authentication mode, and token limit / `max-model-len`.
5. Whether guided JSON (`response_format`) is enabled on their deployment.
