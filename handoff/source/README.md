# Local clinical extraction

This readable Python package runs two established workflows against an approved
OpenAI-compatible endpoint. Start with the Gan-derived current
seizure-frequency workflow on the bundled synthetic note.

## Two-minute seizure-frequency check

The example contains synthetic text only.

Windows PowerShell:

```powershell
.\setup.ps1
Copy-Item .env.example .env
.\.venv\Scripts\python.exe run.py check
.\.venv\Scripts\python.exe run.py seizure-frequency `
  --input examples\seizure_frequency\notes.jsonl `
  --output results.jsonl
```

macOS or Linux:

```sh
./setup.sh
cp .env.example .env
./.venv/bin/python run.py check
./.venv/bin/python run.py seizure-frequency \
  --input examples/seizure_frequency/notes.jsonl \
  --output results.jsonl
```

`check` sends one bundled synthetic note through the real seizure-frequency
prompt and response schema. It reports the requested and returned model, JSON
mode, thinking state, final-content state, and schema result.

## Endpoint settings

Edit `.env`:

```dotenv
VLLM_BASE_URL=http://127.0.0.1:8000/v1
VLLM_API_KEY=EMPTY
VLLM_MODEL=deepseek-v4-flash
VLLM_THINKING=false
```

The temporary `CLINICAL_LLM_BASE_URL`, `CLINICAL_LLM_API_KEY`, and
`CLINICAL_LLM_MODEL` aliases are accepted. If an alias and its `VLLM_*` value
disagree, the command stops. `show-config` prints non-secret resolved settings
and their sources. Notes leave this process through the configured endpoint;
the workflow is local only when that endpoint and its operators are inside the
approved boundary.

## Broader extraction

The one-call four-family workflow returns Diagnosis, Seizure Frequency,
Prescription, and Investigations findings:

```sh
./.venv/bin/python run.py clinical-findings --input notes.jsonl --output findings.jsonl
```

Run both workflows independently with:

```sh
./.venv/bin/python run.py all --input notes.jsonl --output results.jsonl
```

`all` normally makes two model calls per note. It prints the expected count
before execution and preserves one successful workflow if the other fails.
The Gan-derived `current_seizure_frequency` result and ExECT
`seizure_frequencies` findings remain separate fields.

## Inspect and recover

```sh
./.venv/bin/python run.py validate-input --input notes.jsonl
./.venv/bin/python run.py show-config
./.venv/bin/python run.py all --input notes.jsonl --output results.jsonl --resume
```

Input is UTF-8 JSONL with exactly `id` and `text`. Validation of every row,
including duplicate IDs and unknown fields, finishes before the first model
call. Completed rows are synced to a hidden partial file beside the requested
output. `--resume` reuses them only when the input hash, route, model, settings,
prompt, schema, rules, and package versions match. Use `--retry-failed` with
`--resume` to retry only failed rows.

Full prompts, raw responses, and intermediate values are excluded by default.
`--trace-output private-trace.jsonl` enables them and prints a private-data
warning. See [PRIVATE_DATA.md](docs/PRIVATE_DATA.md) before using real notes.

## Reading path

1. `run.py` — invocation and `.env` loading.
2. `clinical_extraction_local/client.py` — endpoint request.
3. The chosen `clinical_extraction_local/*/pipeline.py` — processing order.
4. Its `prompt.md` and `schema.json` — model contract.
5. The named internal deterministic files referenced by the pipeline.
6. [OUTPUTS.md](docs/OUTPUTS.md) — result and trace meanings.

More detail: [HOW_IT_WORKS.md](docs/HOW_IT_WORKS.md) and
[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).
