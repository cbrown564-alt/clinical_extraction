# Protocol: local Compact ledger on ExECT Gemma then Qwen 3.8

Date: 2026-08-17

## Question

Does living Compact ledger (`exectv2_compact_ledger`) keep Gemma 4 26B and
reserved Qwen 3.8 27B inside the same development and aggregate-only holdout
bands already measured for hosted Compact remasure?

## Why this run

Hosted Compact remasure is Sol, Gemini, and DeepSeek. The six-model Compact
dump left Qwen and Gemma for a later local device. This queue is that local
device. Qwen 3.8 27B is the reserved local successor, not a Decision 0051
roster swap for Qwen 3.6:35B.

## Split and inspection

| Split | Rows | Policy |
| --- | --- | --- |
| `dev140` | 140 | Development review permitted |
| `test60` | 59 loadable letters | Aggregate only. No holdout row inspection. Live dumps stay under `scratch/holdout`. |

## Candidate and comparator

| Arm | Prompt | Source |
| --- | --- | --- |
| Control | Full ledger (`exectv2_full_ledger`) | Replay saved same-model structured sidecars |
| Candidate | Living Compact (`exectv2_compact_ledger`) | Live Ollama, resume incomplete letters |

Queue order, one model resident at a time:

1. Gemma 4 26B `dev140`
2. Gemma 4 26B `test60`
3. Qwen 3.8 27B `dev140`
4. Qwen 3.8 27B `test60`

| Model | Runtime | Temperature | `num_ctx` | Timeout |
| --- | --- | --- | --- | --- |
| Gemma 4 26B | `ollama_chat/gemma4:26b`, `think=false` | 0 | 65536 | 900s |
| Qwen 3.8 27B | `ollama_chat/qwen3.8:27b`, `think=false` | 0 | 32768 | 900s |

Full ledger controls:

- Gemma `dev140`: `experiments/exectv2_six_model_single_call_gemma4_26b_dev140_20260715_structured.jsonl`
- Gemma `test60`: `scratch/local_queue/gemma4_26b_exect/test60/gemma4_26b/gemma4_26b_structured.jsonl`
  (the current-stack copy is a Git LFS pointer on this machine)
- Qwen 3.8 `dev140`: `experiments/exectv2_six_model_single_call_qwen38_27b_dev140_20260814_structured.jsonl`
- Qwen 3.8 `test60`: `scratch/holdout/qwen38_27b_20260814/exect_test60/qwen38_27b_structured.jsonl`

If a Full ledger sidecar is missing, Compact is still collected and the
comparison is deferred. Qwen 3.8 `dev140` Full ledger was cancelled on
2026-08-15, so that cell is Compact-only until the sidecar exists.

## Scorer and stop rule

Selected ExECT hybrid clinical-fact F1, family F1, four-family letter-exact
net, plus parse and schema quality. Replay the saved Full ledger arm before
any new Compact call. Resume incomplete Compact sidecars. Do not overwrite
complete letters unless `--overwrite` is set.

Stop when every queued cell has a comparison artifact, a cell fails, or a
control sidecar is missing. A positive result is a development or
aggregate-only Compact delta, not a selected prompt and not a Decision 0050
or 0051 change.

## Artifacts

- Protocol: this file
- Runner: `scripts/run_exectv2_compact_ledger_local_dev140.py`
- Queue: `scripts/run_exectv2_compact_ledger_local_overnight.ps1`
- `dev140` study: `experiments/exectv2_compact_ledger_local_dev140_20260817/`
- `test60` public: `experiments/exectv2_compact_ledger_local_test60_20260817/`
- `test60` live dumps: `scratch/holdout/exectv2_compact_ledger_local_test60_20260817/`
