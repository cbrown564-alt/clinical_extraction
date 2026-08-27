# Local hardware for paper results

Date: 2026-08-27
Status: writing source (not yet in the manuscript)
Owner: this file
Roster: [`paper_experiments/roster.json`](../../paper_experiments/roster.json)

Use this note when filling Results → Development Environment (or
Methods, if that is where compute is stated). It describes the
workstation that served the **local** roster models. Hosted API
hardware is undisclosed and is not reconstructed here.

This page does not support a matched token, dollar, energy, or
latency comparison between hosted and local routes.

## Device

Observed on this machine on 2026-08-27. The same GPU and VRAM were
already recorded for local six-model work on 2026-07-15
([ExECT six-model protocol](../experiments/exectv2/reliability/exectv2_six_model_comparison_protocol_2026-07-15.md)).

| Field | Value |
| --- | --- |
| Machine | Dell XPS 16 9640 |
| OS | Microsoft Windows 11 Home, 64-bit (build 10.0.26200) |
| CPU | Intel Core Ultra 9 185H, 16 cores / 22 threads (WMI base clock 2.50 GHz) |
| System RAM | 32 GB (8 × 4 GB modules at 7500 MT/s; WMI total 33,777,467,392 bytes) |
| GPU (local inference) | NVIDIA GeForce RTX 4070 Laptop GPU, 8188 MiB VRAM, compute capability 8.9 |
| NVIDIA driver | 581.95 (`nvidia-smi`); Windows adapter driver 32.0.15.8195 |
| iGPU (present, not used for roster serving) | Intel Arc Graphics |
| Storage | NVMe SK hynix PC811 1024 GB |

Partial GPU offload onto system RAM can occur for the larger local
weights. Record `size_vram` and observed offload from the run
artifact when a paper sentence needs that fact. Do not infer offload
from latency.

## Which models used this device

From the living roster, only the local route runs here. The other
four models are hosted APIs.

| Display name | Runtime identifier | Route | Device |
| --- | --- | --- | --- |
| Gemini 3.7 Flash | `gemini/gemini-3.7-flash` | hosted | Provider hardware undisclosed |
| Grok 4.6 | `xai/grok-4.6` | hosted | Provider hardware undisclosed |
| GPT-5.6 Luna | `openai/gpt-5.6-luna` | hosted | Provider hardware undisclosed |
| DeepSeek V4 Flash | `deepseek/deepseek-v4-flash` | hosted | Provider hardware undisclosed |
| Qwen 3.8 27B | `ollama_chat/qwen3.8:27b` | local | This workstation |
| Gemma 4 26B | `ollama_chat/gemma4:26b` | local | This workstation |

Historical local tag still on disk: Qwen 3.6:35B
(`ollama_chat/qwen3.6:35b`). That tag is not a living roster row.

## Local serving

| Field | Recorded value | Notes |
| --- | --- | --- |
| Server | Ollama at `http://localhost:11434` | Paper local extracts use `ollama_chat/...` |
| Ollama on this machine (2026-08-27) | 0.32.15 | Live `ollama --version` |
| Earlier frozen local panel (2026-07-15) | Ollama 0.30.10 | Qwen 3.6:35B and Gemma 4 26B identities below |
| Qwen 3.8 27B pull | Newer than 0.32.4 required | [Qwen 3.8 protocol](../research/shared/qwen38_27b_candidate_protocol_2026-08-14.md) |

Installed tags observed 2026-08-27 (paper-relevant only):

| Tag | Short ID | Size | Protocol digest / notes |
| --- | --- | --- | --- |
| `qwen3.8:27b` | `22130167c4c2` | 17 GB | Living local roster. Record quantization from the artifact if cited. |
| `gemma4:26b` | `5571076f3d70` | 17 GB | Matches 2026-07-15 digest prefix; full digest `5571076f3d70050487b26b341705799e0ab29b808164f90d20d4cf84f699d251`, Q4_K_M, reported 25.8B |
| `qwen3.6:35b` | `07d35212591f` | 23 GB | Historical. Full digest `07d35212591fc27746f0a317c975a6d68754fb38e9053d82e25f06057af28522`, Q4_K_M, reported 36.0B |

Published local context settings (not inferred from this snapshot):

- Gemma 4 26B: `think=false`, `num_ctx` 65536
- Qwen 3.8 27B: `think=false`, `num_ctx` 32768

A separate vLLM-on-WSL2 probe used this GPU on 2026-08-10
([runbook](../runbooks/local_vllm_dev10_windows_2026-08-10.md)). That
probe is not the living paper extract route.

## Draft sentence for the paper

Local open-weight extracts (Qwen 3.8 27B and Gemma 4 26B) were
served with Ollama on a Dell XPS 16 9640 running Windows 11, with an
Intel Core Ultra 9 185H, 32 GB RAM, and an NVIDIA GeForce RTX 4070
Laptop GPU (8 GB VRAM). Hosted models used provider APIs; their
accelerators are not reported. No matched cost or latency comparison
across those routes is claimed.

Confirm the Ollama version against the specific cell being cited
before locking that sentence. Living Qwen 3.8 work required a newer
server than the 0.30.10 freeze used for the July local panel.
