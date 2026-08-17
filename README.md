# Clinical Extraction

Turn epilepsy clinic letters into structured clinical facts.

This repository is research code and a working demonstration. It compares three
ways of extracting information from clinical notes—deterministic rules, a
language model alone, and a language model with deterministic repair—on two
benchmarks. The point of the work is not only the score, but which component
improved a result and where each method fails.

This is a research and teaching package, not a clinical deployment claim.

The public tree is the package, tests, configs, and Demo UI fixtures. Clinic
letters, the lab notebook, experiment dumps, and the paper library stay on the
local research checkout and are not cloned.

## Results

Held-out test scores for GPT-5.6 Sol (2 d.p.). Rules-only is deterministic and
does not use a model.

| Method | Gan 2026 | ExECTv2 |
| --- | ---: | ---: |
| LLM with rules | — | 0.80 |
| LLM only | 0.74 | 0.77 |
| Rules only | 0.73 | 0.79 |

- **Gan 2026:** Purist accuracy on the locked `test450` split (one current
  seizure-frequency label per letter). The cited hybrid is the cleaned
  request; that holdout is not on disk yet. Do not read an enveloped
  `v0.5` score into the hybrid cell.
- **ExECTv2:** de-duplicated clinical fact F1 on the locked `test60` split
  (diagnosis, seizure frequency, prescriptions, and investigations). The
  hybrid and LLM-only rows are the same Compact ledger call. This is
  the project's primary research metric for ExECT, not the published strict
  benchmark score.

Scores are not interchangeable across tasks.

## Two tasks, three methods

| | Gan 2026 | ExECTv2 |
| --- | --- | --- |
| Question | What is the patient's current seizure frequency? | What diagnosis, frequency, prescriptions, and investigations does the letter support? |
| Development split | `dev750` | `dev140` |
| Locked test split | `test450` (aggregate scores only) | `test60` (aggregate scores only) |
| Primary score | Purist accuracy | Clinical fact F1 |

Each task uses the same three methods:

- **Rules** — deterministic code produces the clinical answer.
- **LLM** — the model produces the clinical answer.
- **LLM with rules** — the model extracts or proposes facts; deterministic code
  may normalize, select, or repair them before scoring.

## How it works

Every selected path answers the same five questions, even when a method has
more or fewer concrete stages:

```mermaid
flowchart LR
    A["1. Extract"] --> B["2. Normalize"]
    B --> C["3. Select or enrich"]
    C --> D["4. Check evidence"]
    D --> E["5. Score"]
```

1. **Extract** — rules or a model find candidate events, findings, or a
   proposed answer.
2. **Normalize** — structure and bounded format repairs make the result usable
   without silently changing the task.
3. **Select or enrich** — the named method decides or revises the clinical
   answer.
4. **Check evidence** — the system checks that cited text appears in the note
   and records which component produced the result.
5. **Score** — the task scorer turns the final representation into Gan
   categories or ExECT fact metrics.

## Try the demo

The frontend is the main interactive demonstration. It uses the bundled
fixtures under `frontend/public/mock-data/`; no local letter corpus is
required. From the repository root, use two terminals.

Windows PowerShell:

```powershell
# Terminal 1: local Python API
.venv\Scripts\python.exe -m clinical_extraction.trace_explorer.api.app

# Terminal 2: Next.js frontend
Set-Location frontend
npm ci                 # first run only
npm run dev
```

macOS or Linux:

```sh
# Terminal 1: local Python API
.venv/bin/python -m clinical_extraction.trace_explorer.api.app

# Terminal 2: Next.js frontend
cd frontend
npm ci                 # first run only
npm run dev
```

Open [http://127.0.0.1:3000/workbench](http://127.0.0.1:3000/workbench).
Saved and fixture views explain the selected methods without new model calls.
More detail is in the [frontend README](frontend/README.md).

## Setup

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,trace-ui]"
python -m pytest
```

macOS or Linux:

```sh
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev,trace-ui]"
python -m pytest
```

Use the repository virtual environment for all Python commands. Plain `pytest`
is the always-on suite. On a public clone, tests that need the local research
corpus are skipped. With a local checkout that still has `data/`, `docs/`, and
`experiments/`, the same command is the full always-on suite.
`python -m pytest -m deep` runs the optional deep tier and also needs that
local corpus.

For local Ollama runs, start with one row, then five, then 25. Record the model
route and API base in the run metadata.

### Run against a local vLLM server

Install the package, then probe an OpenAI-compatible server before processing
notes. A `vllm/<served-model>` identifier defaults to the keyless placeholder
`EMPTY`, so `--api-key` is not required for an unauthenticated local server:

```sh
python -m pip install .
clinical-extract probe \
  --base-url http://127.0.0.1:8000/v1 \
  --model vllm/deepseek-v4-flash
```

The input is JSONL with one `id` and `text` object per line. Run the selected
Gan seizure-frequency pipeline with:

```sh
clinical-extract gan \
  --input notes.jsonl \
  --output predictions.jsonl \
  --base-url http://127.0.0.1:8000/v1 \
  --model vllm/deepseek-v4-flash
```

For ExECT extraction, replace `gan` with `exect`; its default method is
`llm_with_rules`. Pass `--api-key` only when the server is configured to require
one. The value after `vllm/` must exactly match the model name returned by the
server's `/v1/models` endpoint.

A full Gan walkthrough on three synthetic letters is in [VLLM.md](VLLM.md).

## Repository layout

```text
src/clinical_extraction/   Package: loaders, pipelines, scoring, API
frontend/                  Interactive workbench and bundled Demo UI fixtures
examples/                  Pinned walkthrough inputs, including the vLLM Gan letters
configs/                   Pipeline and model configuration
tests/                     Contract and behavior checks
scripts/                   CLI helpers and experiment runners
paper_experiments/         Tracked paper fills and replayable local raws
```

A local research checkout may also have `data/`, `docs/`, `experiments/`,
`literature/`, and `media/`. Those trees are gitignored and are not part of a
public clone. Paper-facing fills are in `paper_experiments/`.
