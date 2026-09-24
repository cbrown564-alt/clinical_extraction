# GLiNER2.5-Decide on a local GPU

Date: 2026-09-25
Status: current
Owner: [GLiNER exploration report](../research/gan2026/gliner_decide_exploration.md)

Setup for the exploratory GLiNER runs on a Windows 11 laptop with an RTX 3070
laptop GPU (8 GB VRAM, Ampere, bf16 supported) and 32 GB RAM. No provider calls.

## Why not the Mac

On 2026-09-25 an inference run and a training smoke test ran together on the 16 GB
M1 alongside a virtual machine. Unified memory, compressor and swap filled, and
the kernel panicked (watchdog timeout). Apple Silicon is now capped
(`PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.5`) and used for smoke tests only.

**Run one model job at a time on any machine.**

## Install (PowerShell, repository root)

Use Python 3.12 (CUDA torch wheels are the most reliable there).

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e ".[dev]"
python -m pip install torch --index-url https://download.pytorch.org/whl/cu128
python -m pip install "gliner2[local,train]==2.0.0" "protobuf>=5" "sentencepiece>=0.2"
python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.is_bf16_supported())"
```

Install the CUDA torch wheel **before** gliner2, so pip keeps it instead of the
CPU-only PyPI wheel. gliner2 2.0.0 needs `transformers<5`, which pins
`huggingface-hub<1` and an older `tokenizers`. That is why it is not a project
extra: it would change the shared lock. The full test suite passes with it
installed (852 passed, 2026-09-25).

In the NVIDIA Control Panel, set **CUDA – Sysmem Fallback Policy** to *Prefer No
Sysmem Fallback* for `python.exe`. Otherwise Windows silently spills VRAM into
system RAM and a run crawls instead of failing with an out-of-memory error. Keep
the laptop on mains power with sleep disabled during runs.

## Local-only inputs to copy

These are gitignored; copy them into the same paths:

| Path | Use |
| --- | --- |
| `data/Gan (2026)/synthetic_data_subset_1500.json` | Letters and Gan labels |
| `data/Gan (2026)/splits/gan2026_split_v1.json` | Split manifest |
| `runs/seizure_frequency/reference/dev750.jsonl` | Expanded reference findings (dev750 only) |
| `runs/seizure_frequency/one_call/dev750/per_letter.json` | DeepSeek results, for descriptive pairing |

The data file contains the test rows too. The runner refuses the test split, and
nothing here reads it; do not copy the test450 annotation package. Do not copy
`runs/seizure_frequency/gliner/`: the partial Mac run must not be resumed on
CUDA (the runner refuses a device change within a run).

## Run order

```powershell
python -m scripts.benchmarks.gliner_decide check
python -m scripts.benchmarks.gliner_decide infer --condition minimal --context full
python -m scripts.benchmarks.gliner_decide score --run zs_minimal_full
python -m scripts.benchmarks.gliner_decide infer --condition minimal --context chunked
python -m scripts.benchmarks.gliner_decide score --run zs_minimal_chunked
python -m scripts.benchmarks.gliner_decide infer --condition expanded --context full
python -m scripts.benchmarks.gliner_decide score --run zs_expanded_full --pair zs_minimal_full
python -m scripts.benchmarks.gliner_decide infer --condition expanded --context chunked
python -m scripts.benchmarks.gliner_decide score --run zs_expanded_chunked --pair zs_minimal_chunked
python -m scripts.benchmarks.gliner_decide build-data
python -m scripts.benchmarks.gliner_decide train --target minimal --name smoke --lora --epochs 1 --max-steps 4 --limit 8
```

`check` prints the device, bf16 support, free VRAM and the peak memory of one
expanded letter. Training on CUDA uses batch 1 with 16 accumulation steps, bf16
and gradient checkpointing (`training.settings_for`). fp16 is never used because
DeBERTa-v3 overflows in it. On an out-of-memory error, add `--max-len 512`
before changing anything else, and record it.

Raw outputs, identities and checkpoints stay under `runs/seizure_frequency/gliner/`.
Aggregates are written to `results/letter-benchmarks/gan/gliner/`. Bring those
aggregates back to commit; keep raw runs local.
