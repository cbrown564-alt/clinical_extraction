# Clinical extraction runner

This folder is ready to run after extraction. It contains the complete Python
source for the selected LLM-with-rules pipelines; there is no package or wheel
to install.

The two tasks are:

- `gan`: one seizure-frequency answer per note, using the Gan structured-events
  prompt v0.5 and its deterministic normalization and clinical repair;
- `exect`: Diagnosis, SeizureFrequency, Prescription, and Investigations using
  the selected one-call ExECT architecture and its attributed deterministic
  processing.

It contains no datasets, gold labels, experiment outputs, caches, or API
credentials. Its outputs are operational predictions, not benchmark or
clinical-validation claims.

## First-time setup

Use Python 3.11 or newer. On Windows PowerShell, run:

```powershell
.\setup.ps1
```

That creates a local `.venv` and installs the four runtime dependencies from
`requirements.txt`. It does not install this source tree as a package.

For another shell or operating system, create a virtual environment and install
the requirements using the equivalent commands.

## Configure the endpoint

Copy `.env.example` to `.env`, then replace its three placeholder values:

```dotenv
CLINICAL_LLM_BASE_URL=https://replace-with-endpoint/v1
CLINICAL_LLM_API_KEY=replace-with-key
CLINICAL_LLM_MODEL=deepseek-v4-flash
```

The included script loads this small `.env` file automatically. Existing
environment variables take precedence.

The endpoint must implement OpenAI-compatible `POST /chat/completions` requests.
For a local endpoint that does not authenticate, use `EMPTY` only when the
server explicitly permits it.

Check the connection with a non-clinical request:

```powershell
.\.venv\Scripts\python.exe .\run_clinical_extraction.py probe
```

## Input

Input is UTF-8 JSONL. Each line must contain a unique `id` and non-empty `text`:

```json
{"id":"note-001","text":"The clinical note goes here."}
```

## Run

```powershell
.\.venv\Scripts\python.exe .\run_clinical_extraction.py gan --input notes.jsonl --output gan_predictions.jsonl
.\.venv\Scripts\python.exe .\run_clinical_extraction.py exect --input notes.jsonl --output exect_predictions.jsonl
```

Existing output files are protected. Pass `--overwrite` deliberately to replace
one. Each failed note is written with `status: "error"`; a run containing any
failure exits with status code 1.

Do not place identifiable clinical notes or API keys in command history, logs,
source control, or support messages. Use only an approved endpoint and storage
location.
