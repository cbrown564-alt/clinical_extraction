# Run against a local vLLM server

This walkthrough runs the cited Gan codebook find
(`gan_llm_extract`) against your own data. The model writes frequency
labels in the allowed forms; recorded rules then encode and select.
That is cell 3. This is `clinical-extract gan`, not the source-near
ablation (`gan_llm_extract_raw`) and not `gan_llm_only`.

To use cell 5 instead (same find, then LLM select), add
`--method llm_select`. See [Cell 5](#cell-5-llm-select).

It also includes a worked example for three synthetic clinic letters. The letters are
fixed in `[examples/vllm_gan_three_letters.jsonl](examples/vllm_gan_three_letters.jsonl)`,
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

The input is JSONL with one `id` and `text` object per line. Run the cited
Gan codebook find with:

```sh
clinical-extract gan \
  --input notes.jsonl \
  --output predictions.jsonl \
  --base-url http://127.0.0.1:8000/v1 \
  --model vllm/deepseek-v4-flash
```

## The three letters


| id            | What the letter states                                                         |
| ------------- | ------------------------------------------------------------------------------ |
| `vllm-gan-01` | A current typical rate ("two focal seizures a month") and a year-to-date count |
| `vllm-gan-02` | Sustained seizure freedom since a calendar month                               |
| `vllm-gan-03` | Medication and investigations only; no frequency statement                     |


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
  "pipeline": "gan_llm_extract",
  "prompt_version": "gan_llm_extract",
  "prediction": {
    "seizure_frequency": "2 per month",
    "evidence": "Her typical pattern remains two focal seizures a month",
    "rationale": "The stated typical rate is the current frequency."
  },
  "parse_errors": [],
  "structured_record": {
    "events": [
      {
        "event_id": "e1",
        "kind": "frequency_rate",
        "raw_value": "two focal seizures a month",
        "applies_to": "focal seizures",
        "time_window": "typical pattern",
        "temporality": "current",
        "assertion_status": "asserted",
        "evidence": "Her typical pattern remains two focal seizures a month",
        "notes": null
      },
      {
        "event_id": "e2",
        "kind": "frequency_rate",
        "raw_value": "five seizures so far this year",
        "applies_to": "seizures",
        "time_window": "this year",
        "temporality": "recent",
        "assertion_status": "asserted",
        "evidence": "She has had five seizures so far this year",
        "notes": null
      }
    ],
    "selection": {
      "selected_event_ids": ["e1"],
      "final_kind": "frequency",
      "final_label": "2 per month",
      "evidence": "Her typical pattern remains two focal seizures a month",
      "confidence": "high",
      "rationale": "The stated typical rate is the current frequency."
    }
  },
  "score_projection": {
    "normalized_label": "2 per month",
    "kind": "frequency",
    "monthly_frequency": 2.03,
    "yearly_bounds": [24.33, 24.33],
    "purist_category": "seizure_freq_more1mon_less1week",
    "pragmatic_category": "seizure_frequent"
  }
}
```


| Field                          | Meaning                                                                                                                      |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| `pipeline`                     | Cited method id: `gan_llm_extract`. Not `llm_with_rules` and not the source-near ablation.                                   |
| `prompt_version`               | Request sent to the model: `gan_llm_extract` (allowed label forms).                                                          |
| `prediction.seizure_frequency` | The current frequency label after find, encode, and select                                                                |
| `prediction.evidence`          | Supporting text the pipeline cited from the letter                                                                           |
| `prediction.rationale`         | Why that label was selected                                                                                                  |
| `parse_errors`                 | Format problems from the model call, if any                                                                                  |
| `structured_record`            | Extracted events (note wording in `raw_value`) and the form-aligned selection, after repair                                  |
| `score_projection`             | The selected label mapped into Gan Purist and Pragmatic categories. This is not a gold comparison and not a benchmark score. |


A failed note uses `"status": "error"` and an `error` object instead of a
usable prediction:

```json
{
  "id": "vllm-gan-03",
  "task": "gan",
  "status": "error",
  "model": "deepseek-v4-flash",
  "pipeline": "gan_llm_extract",
  "error": {"type": "TimeoutError", "message": "Request timed out."}
}
```

On a working run you should see three rows with the same ids as the input.
`vllm-gan-01` usually reports a monthly rate. `vllm-gan-02` usually reports
seizure freedom. `vllm-gan-03` has no frequency statement, so the label is
often `unknown` or a no-reference sentinel. Those strings are not scored here
and are not a claim about holdout performance.

## Multi-Agent Pipeline

The multi-agent pipeline uses the same probe, JSONL input, and codebook find as above. The
difference is a second model call: select reads the extracted events and
their quotes, not the letter, and rules do not encode or select. This is
not `gan_llm_only` (one call that writes a label from the letter).

```sh
clinical-extract gan \
  --method llm_select \
  --input examples/vllm_gan_three_letters.jsonl \
  --output scratch/vllm_gan_three_letters.cell5.predictions.jsonl \
  --base-url http://127.0.0.1:8000/v1 \
  --model vllm/deepseek-v4-flash
```

A successful row keeps the same `id` and prediction shape. The method
fields change:

| Field | Cell 3 (default) | Cell 5 (`--method llm_select`) |
| --- | --- | --- |
| `pipeline` | `gan_llm_extract` | `gan_llm_select_from_extract` |
| `prompt_version` | `gan_llm_extract` | `gan_llm_select_policy_examples` |
| Model calls | one (find) | two (find, then select) |

The paper cites this later-stage select on Gemini. A local vLLM model
can run the same commands; that is not a paper score.