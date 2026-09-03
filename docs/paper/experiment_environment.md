# Experiment environment record

Status: writing source for Results and supporting material
Owner: this file
Local device snapshot: [`hardware_details.md`](hardware_details.md) (2026-08-27)
Roster: [`paper_experiments/roster.json`](../../paper_experiments/roster.json)

Scope: execution environment for the reported paper experiments. This file
records the local orchestration machines and model routes. Hosted inference
ran on provider hardware, which is undisclosed and is not reconstructed
here. This page does not support a matched token, dollar, energy, or
latency comparison between hosted and local routes.

## Reported environment

### API-orchestrated experiments

Most hosted API experiments were initiated from the Mac mini below. The remote
provider, rather than the Mac mini, performed model inference.

| Item | Recorded value |
| --- | --- |
| Host | Apple Mac mini (Macmini9,1) |
| Processor | Apple M1, 8 CPU cores (4 performance, 4 efficiency) |
| Memory | 16 GB unified memory |
| Operating system | macOS 26.5.2 |
| Project runtime currently installed | Python 3.14.4; project requirement is Python 3.11 or later |
| Core packages currently installed | DSPy 3.2.1; LiteLLM 1.87.1; Pydantic 2.13.4 |
| Dependency record | `uv.lock` |

The six-model comparison is cell 3 only on both tasks (LLM find,
rules encode, rules select). Living request settings come from
`ModelSpec` in [`exect.py`](../../src/clinical_extraction/paper/exect.py)
(`_spec_for`). Promoted ExECT cells record the same fields in
`paper_experiments/exect/exect_llm_extract/{slug}/*/comparison.json`.
Gan cell 3 (`gan_llm_extract`) uses the same temperature, reasoning,
thinking, and local context settings, with a smaller output-token
budget.

Gemini thinking medium/high and DeepSeek thinking-off are ablations,
not this table. Later-stage LLM encode and LLM select stay Gemini
only.

| Model | Identifier | Route / transport | Temp. | Max out (ExECT / Gan) | Reasoning | Thinking | Local context | Timeout (s) |
| --- | --- | --- | ---: | ---: | --- | --- | ---: | ---: |
| Gemini 3.7 Flash (cited) | `gemini/gemini-3.7-flash` | hosted; OpenRouter batch | 0.0 | 16,000 / 5,000 | `low` | — | — | 300 |
| Grok 4.6 | `xai/grok-4.6` | hosted; OpenRouter, sync | 0.0 | 16,000 / 5,000 | `low` | — | — | 600 |
| GPT-5.6 Luna | `openai/gpt-5.6-luna` | hosted; OpenAI batch | 1.0 | 16,000 / 5,000 | `low` | — | — | 300 |
| DeepSeek V4 Flash 0731 | `deepseek/deepseek-v4-flash` | hosted; DeepSeek API, sync | 0.0 | 64,000 / 24,000 | `low` | enabled | — | 600 |
| Qwen 3.8 27B | `ollama_chat/qwen3.8:27b` | local; native Ollama chat | 0.0 | 16,000 / 5,000 | — | `think=false` | 32,768 | 900 |
| Gemma 4 26B | `ollama_chat/gemma4:26b` | local; native Ollama chat | 0.0 | 16,000 / 5,000 | — | `think=false` | 65,536 | 900 |

Luna uses temperature 1.0 because the provider rejects `0` and
accepts only its default `1` (recorded on the 2026-07-15 hosted Gan
launch). GPT-5-family reasoning routes also require `1` in DSPy.
Grok’s living setting is `0.0`. Luna stays at `1.0` because the
provider rejects `0`. Gemini, DeepSeek, Qwen, and Gemma use 0.0.
The Grok cell-3 shift versus the cited temperature-1 row is in
[Grok temperature 0](../research/gan2026/gan_grok46_temperature_0_2026-08-28.md).
The Gemini cell-3 shift versus living temperature 0 is in
[Gemini temperature 1](../research/gan2026/gan_gemini37flash_temperature_1_2026-08-28.md).
Hosted accelerators are undisclosed. Local serving is the Dell
workstation below. Cache is off for live cells (`num_retries` 2 on the
LM constructor). Retry and exact prompt or program version stay on the
promoted cell artifact.

### Local-model experiments

Qwen and Gemma extracts were served with native Ollama chat on the Dell
workstation below, not on the Mac mini. Living local settings are in
the six-model table above.

Observed on that machine on 2026-08-27. The same GPU and VRAM were already
recorded for local six-model work on 2026-07-15
([ExECT six-model protocol](../experiments/exectv2/reliability/exectv2_six_model_comparison_protocol_2026-07-15.md)).

| Item | Recorded value |
| --- | --- |
| Machine | Dell XPS 16 9640 |
| Operating system | Microsoft Windows 11 Home, 64-bit (build 10.0.26200) |
| CPU | Intel Core Ultra 9 185H, 16 cores / 22 threads (WMI base clock 2.50 GHz) |
| System RAM | 32 GB (8 × 4 GB modules at 7500 MT/s; WMI total 33,777,467,392 bytes) |
| GPU (local inference) | NVIDIA GeForce RTX 4070 Laptop GPU, 8188 MiB VRAM, compute capability 8.9 |
| NVIDIA driver | 581.95 (`nvidia-smi`); Windows adapter driver 32.0.15.8195 |
| CUDA version | Not recorded for the native Ollama path |
| iGPU (present, not used for roster serving) | Intel Arc Graphics |
| Storage | NVMe SK hynix PC811 1024 GB |
| Runtime | Native Ollama chat at `http://localhost:11434` (`ollama_chat/...`) |
| Ollama on this machine (2026-08-27) | 0.32.15 |
| Earlier frozen local panel (2026-07-15) | Ollama 0.30.10 |
| Local models | Qwen 3.8 27B; Gemma 4 26B |

| Display name | Runtime identifier | Route | Device |
| --- | --- | --- | --- |
| Qwen 3.8 27B | `ollama_chat/qwen3.8:27b` | local | This workstation |
| Gemma 4 26B | `ollama_chat/gemma4:26b` | local | This workstation |

Historical local tag still on disk: Qwen 3.6:35B
(`ollama_chat/qwen3.6:35b`). That tag is not a living roster row.

Installed tags observed 2026-08-27 (paper-relevant only):

| Tag | Short ID | Size | Protocol digest / notes |
| --- | --- | --- | --- |
| `qwen3.8:27b` | `22130167c4c2` | 17 GB | Living local roster. Record quantization from the artifact if cited. |
| `gemma4:26b` | `5571076f3d70` | 17 GB | Matches 2026-07-15 digest prefix; full digest `5571076f3d70050487b26b341705799e0ab29b808164f90d20d4cf84f699d251`, Q4_K_M, reported 25.8B |
| `qwen3.6:35b` | `07d35212591f` | 23 GB | Historical. Full digest `07d35212591fc27746f0a317c975a6d68754fb38e9053d82e25f06057af28522`, Q4_K_M, reported 36.0B |

Published local context settings (not inferred from this snapshot):

- Gemma 4 26B: `think=false`, `num_ctx` 65536
- Qwen 3.8 27B: `think=false`, `num_ctx` 32768

Qwen 3.8 27B pull required a newer Ollama than 0.32.4
([Qwen 3.8 protocol](../research/shared/qwen38_27b_candidate_protocol_2026-08-14.md)).
Confirm the Ollama version against the specific cell being cited. Living
Qwen 3.8 work required a newer server than the 0.30.10 freeze used for the
July local panel.

Partial GPU offload onto system RAM can occur for the larger local
weights. Record `size_vram` and observed offload from the run artifact
when a paper sentence needs that fact. Do not infer offload from latency.
Concurrent request and batch size are not recorded as a claimed matched
setting.

A separate vLLM-on-WSL2 probe used this GPU on 2026-08-10
([runbook](../runbooks/local_vllm_dev10_windows_2026-08-10.md)). That
probe is not the living paper extract route.

## Per-run route fields

The six-model table is the living default. For a cited cell, keep the
route and settings from that cell’s `comparison.json` rather than a
generic provider name. Prompt or program version, split, and scorer
stay on the cell artifact.

## Intended paper use

Hosted experiments were orchestrated on the Mac mini. Local open-weight
extracts (Qwen 3.8 27B and Gemma 4 26B) were served with Ollama on a Dell
XPS 16 9640 running Windows 11, with an Intel Core Ultra 9 185H, 32 GB RAM,
and an NVIDIA GeForce RTX 4070 Laptop GPU (8 GB VRAM). Hosted models used
provider APIs; their accelerators are not reported. No matched cost or
latency comparison across those routes is claimed.
