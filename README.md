# Clinical Extraction

Turn epilepsy clinic letters into structured clinical facts.

This repository is research code and a working demonstration. The proposed
method translates clinic letters into structured clinical facts in a designed
form, with quoted source text. A model collects the facts and evidence;
recorded rules shape them into the required form. The comparison is four methods (Rules, LLM, LLM then rules, Rules
then LLM) against stages (extract, encode, select), not an on/off
hybrid switch. The public golds are the evaluation
forms used here, not the task. Tables cite Gemini 3.7 Flash so the
story stays on the method. Grok, Luna, DeepSeek, Qwen, and Gemma are
companion rows. The recorded
object keeps the source span and a change log, not only the score.

This is a research and teaching package, not a clinical deployment claim.

The public tree is the package, tests, configs, and Demo UI fixtures. Clinic
letters, the lab notebook, experiment dumps, and the paper library stay on the
local research checkout and are not cloned.

## Results

Held-out test scores for Gemini 3.7 Flash (2 d.p.), the cited model.
Companion Grok cells stay on disk. GPT-5.6 Sol cells stay historical.
Rules are deterministic and do not use a model. That score is repeated
in every rules column.

**Gan 2026** (Purist, locked `test450`):

| | Extract | Encode | Select |
| --- | ---: | ---: | ---: |
| **Rules** | 0.73 | 0.73 | 0.73 |
| **LLM** | 0.55 | 0.65 | 0.71 |
| **LLM then rules** | 0.55 | 0.74 | 0.79 |
| **Rules then LLM** | 0.59 | 0.77 | 0.80 |

**ExECTv2** (clinical fact F1, locked `test60`):

| | Extract | Encode | Select |
| --- | ---: | ---: | ---: |
| **Rules** | 0.79 | 0.79 | 0.79 |
| **LLM** | — | — | — |
| **LLM then rules** | — | 0.78 | 0.81 |
| **Rules then LLM** | — | — | 0.81 |

Em dashes are missing locked cells, not zeros. Gan **LLM** encode and
select are later-stage Gemini cells. **LLM then rules** is the three
stops on `gan_llm_with_rules` / `exect_llm_only`. **Rules then LLM**
is the three stops on `*_pre_post`. Gan hybrid select is ledger-only.
Gemini Rules then LLM select is 358/450; Gemini LLM then rules select
is 357/450. Those living cells match the select stops. `gan_llm_only`
is not a results column.

- **Gan 2026:** Purist accuracy on the locked `test450` split (one current
  seizure-frequency label per letter). The living Grok companion LLM
  then rules select is 375/450; do not read an enveloped `v0.5` score
  into that cell.
- **ExECTv2:** de-duplicated clinical fact F1 on the locked `test60` split
  (diagnosis, seizure frequency, prescriptions, and investigations).
  LLM then rules replays `exect_llm_only`. Rules then LLM is
  `exect_llm_pre_post`. Extract stops on those raws are not all
  filled. This is the project's primary research metric for ExECT,
  not the published strict benchmark.

Scores are not interchangeable across tasks.

## Two tasks

| | Gan 2026 | ExECTv2 |
| --- | --- | --- |
| Question | What is the patient's current seizure frequency? | What diagnosis, frequency, prescriptions, and investigations does the letter support? |
| Development split | `dev750` | `dev140` |
| Locked test split | `test450` (aggregate scores only) | `test60` (aggregate scores only) |
| Primary score | Purist accuracy | Clinical fact F1 |

Each task uses the same four methods against extract / encode / select.

- **Rules** — deterministic code; one score in every stage column.
- **LLM** — parsed model ledger, then Gemini later-stage encode and
  select on Gan. ExECT later-stage encode and select are not yet run.
- **LLM then rules** — `gan_llm_with_rules` / `exect_llm_only` at
  extract, encode, and select.
- **Rules then LLM** — `*_pre_post` at extract, encode, and select.

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
