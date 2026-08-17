# Run against a local vLLM server
This walkthrough runs the selected Gan seizure-frequency pipeline
(`llm_with_rules`) against your own data.

It also includes a worked example for three synthetic clinic letters. The letters are
fixed in [`examples/vllm_gan_three_letters.jsonl`](examples/vllm_gan_three_letters.jsonl),
so anyone can repeat the same input. 
## What you need
1. The package installed in the repository virtual environment (see the
   [Setup](#setup)).
2. An OpenAI-compatible vLLM server. The value after `vllm/` must match the
   model name returned by the server's `/v1/models` endpoint.

This example uses `http://127.0.0.1:8000/v1` and `vllm/deepseek-v4-flash`.

Replace the host and the name after `vllm/` with your own. `--api-key` is
needed only when the server requires one; a `vllm/<served-model>` identifier
defaults to the keyless placeholder `EMPTY`.
## 
## Setup
Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install .
```

macOS or Linux:

```sh
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install .
```
## 
## Run against a local vLLM server
Install the package, then probe an OpenAI-compatible server before processing
notes. A `vllm/<served-model>` identifier defaults to the keyless placeholder
`EMPTY`, so `--api-key` is not required for an unauthenticated local server:

```sh
clinical-extract probe \
  --base-url http://127.0.0.1:8000/v1 \
  --model vllm/deepseek-v4-flash
```

A successful probe prints a JSON object to stdout:

```json
{
  "base_url": "http://127.0.0.1:8000/v1",
  "content": "{\"ok\": true}",
  "reasoning_content_present": false,
  "requested_model": "deepseek-v4-flash",
  "response_model": "deepseek-v4-flash",
  "status": "ok"
}
```

`content` is whatever the server returned to the short connectivity prompt.
`response_model` is the name the server used. If these disagree with the name
after `vllm/`, fix the identifier before extracting notes.

The input is JSONL with one `id` and `text` object per line. Run the selected
Gan seizure-frequency pipeline with:

```sh
clinical-extract gan \
  --input notes.jsonl \
  --output predictions.jsonl \
  --base-url http://127.0.0.1:8000/v1 \
  --model vllm/deepseek-v4-flash
```

## The three letters

| id | What the letter states |
| --- | --- |
| `vllm-gan-01` | A current typical rate ("two focal seizures a month") and a year-to-date count |
| `vllm-gan-02` | Sustained seizure freedom since a calendar month |
| `vllm-gan-03` | Medication and investigations only; no frequency statement |

Each line of the JSONL is one object with `id` and `text`.
## Run Gan on the three letters

```sh
clinical-extract gan \
  --input examples/vllm_gan_three_letters.jsonl \
  --output scratch/vllm_gan_three_letters.predictions.jsonl \
  --base-url http://127.0.0.1:8000/v1 \
  --model vllm/deepseek-v4-flash
```

The command writes one JSON object per input note, then prints a count:

```json
{"rows": 3, "failures": 0, "output": "scratch/vllm_gan_three_letters.predictions.jsonl"}
```

A non-zero exit means at least one row has `"status": "error"`. Pass
`--overwrite` to replace an existing output file. `scratch/` is local run
output and is not committed.

## What a prediction row looks like

Each output line keeps the input `id`. A successful row looks like this:

```json
{
  "id": "vllm-gan-01",
  "task": "gan",
  "status": "ok",
  "model": "deepseek-v4-flash",
  "pipeline": "llm_with_rules",
  "prompt_version": "gan2026_hybrid_structured_events_v0.5",
  "prediction": {
    "seizure_frequency": "2 per month",
    "evidence": "Her typical pattern remains two focal seizures a month",
    "rationale": "The stated typical rate is the current frequency."
  },
  "parse_errors": [],
  "structured_record": {}
}
```

| Field | Meaning |
| --- | --- |
| `prediction.seizure_frequency` | The current frequency label the pipeline selected |
| `prediction.evidence` | Supporting text the pipeline cited from the letter |
| `prediction.rationale` | Why that label was selected |
| `parse_errors` | Format problems from the model call, if any |
| `structured_record` | The structured events the model returned, after repair |

A failed note uses `"status": "error"` and an `error` object instead of a
usable prediction:

```json
{
  "id": "vllm-gan-03",
  "task": "gan",
  "status": "error",
  "model": "deepseek-v4-flash",
  "pipeline": "llm_with_rules",
  "error": {"type": "TimeoutError", "message": "Request timed out."}
}
```

On a working run you should see three rows with the same ids as the input.
`vllm-gan-01` usually reports a monthly rate. `vllm-gan-02` usually reports
seizure freedom. `vllm-gan-03` has no frequency statement, so the label is
often `unknown` or a no-reference sentinel. Those strings are not scored here
and are not a claim about holdout performance.
