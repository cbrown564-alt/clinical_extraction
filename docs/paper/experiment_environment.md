# Experiment environment record

Status: working record for the Results section and supporting material  
Owner: this file  
Scope: execution environment for the reported paper experiments. This file
records the local orchestration machines and model routes; it does not imply
that hosted inference ran on the local machine.

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

The promoted Gemini development artifacts identify the transport as
OpenRouter Batch. The experiment configurations record model identifier,
provider or route, temperature, output-token limit, reasoning setting, prompt
or program, split, and run metadata. The cited Gemini conditions use
temperature 0, 16,000 maximum output tokens, and low reasoning effort.

### Local-model experiments

Qwen and Gemma experiments were run locally with native Ollama chat, rather
than on the Mac mini. The configurations use temperature 0, a 16,000-token
limit, and disabled model thinking.

| Item | Recorded value |
| --- | --- |
| Host | Dell XPS 15 laptop |
| Accelerator | NVIDIA GPU with 8 GB VRAM |
| Runtime | Native Ollama chat |
| Local models | Qwen 3.8 27B; Gemma 4 26B |
| Temperature | 0 |
| Maximum output tokens | 16,000 |
| Thinking | Disabled |

## Dell specification fields to complete

Fill these fields from the Dell XPS 15 system information and the Ollama
installation that ran the local experiments.

| Needed for reproducibility | Value to add |
| --- | --- |
| Exact Dell XPS 15 model and year | TODO |
| CPU model and core count | TODO |
| Installed RAM | TODO |
| Operating system and version | TODO |
| Exact NVIDIA GPU model | TODO |
| NVIDIA driver and CUDA version, if applicable | TODO |
| Ollama version | TODO |
| Model tag and quantisation for each local model | TODO |
| Context-window setting | TODO |
| GPU-offload setting | TODO |
| Concurrent requests or batch size | TODO |

## Per-run route fields to confirm

The repository records several valid hosted routes. For each cited table or
analysis, record the route actually used rather than a generic provider name.

| Item | Value to confirm from the promoted run metadata |
| --- | --- |
| Primary Gemini intermediary | OpenRouter |
| Primary Gemini mode | Batch |
| Primary Gemini transport | `openrouter_batch` |
| Local Qwen and Gemma mode | Live native Ollama chat |
| Model identifier | Recorded per experiment |
| Temperature and output-token limit | Recorded per experiment |
| Reasoning or thinking setting | Recorded per experiment |
| Retry and timeout policy | Recorded in the runtime configuration |
| Prompt or program version | Recorded per experiment |

## Intended paper use

The main paper should state the two execution settings concisely: hosted
experiments were orchestrated on the Mac mini and local open-weight experiments
ran through Ollama on the Dell laptop. A compact table can carry the hardware,
runtime, and inference settings. The supporting material should retain the
per-run route and configuration details.
