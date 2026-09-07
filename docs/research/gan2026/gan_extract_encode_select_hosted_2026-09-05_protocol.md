# Protocol: one-call extract-encode-select on hosted models

Date: 2026-09-05
Method: `gan_llm_extract_encode_select`
Prompt identity: `gan_llm_extract_encode_select` (plain-fact variant in
`prompt_llm_extract_encode_select.py`)
Work leaf: `20260905`

## Question

Does the current one-call prompt, with find, encode, and select in a single
request, transfer to Gemini 3.7 Flash (new variant), GPT-5.6 Luna, and
DeepSeek V4 Flash on Gan 2026?

This is the new primary research direction. It is not a paper-row promotion.
Cited extract remains `gan_llm_extract`. Local Qwen and Gemma are out of
scope here and will be run on a separate device.

## Why it matters

The previous Gemini one-call ablation scored 657/750 on `dev750` and 392/450
on `test450`. The living prompt now uses a plain fact schema (`facts`,
`raw_value`, `normalised_label`, `selected_fact_ids`) and case-led select
rules. Luna and DeepSeek have not been measured on this method.

## Surfaces

| Split | Policy | Inspection |
| --- | --- | --- |
| `dev750` | development review permitted | allowed after the run |
| `test450` | aggregate-only companion | do not inspect rows |

Row policy is the living split manifest. Scorer is Purist micro-F1
(`row_ok` as in living Gan eval). Secondary: Pragmatic, parse/call/schema
failures.

## Candidate and comparators

Candidate: live `gan_llm_extract_encode_select` at temperature and reasoning
settings of the living roster. Luna uses OpenAI batch. Gemini uses OpenRouter batch after a 402 on
first submit (credits topped up; partial sync rows discarded). DeepSeek
is sync with thinking enabled and `max_tokens=24000`.

Fixed comparators, same model where a cell exists:

- cited extract / Hybrid decide (`gan_llm_extract` + rule select)
- same-model LLM-only decide
- prior Gemini one-call ablation (0.88 / 0.87), Gemini only

Do not overwrite promoted cells.

## Component under study

One LLM call writes facts and a current-frequency answer. Deterministic work
is format-only schema repair (`facts`/`answer` aliases to the shared
events/selection parser) plus living `raw_model` label projection. No new
select rules.

## Minimal change

No new paper cell. Isolate artifacts under work leaf `20260905`. Schema
repair may map example-taught keys (`facts`, `fact_id`, `answer`,
`selected_fact_ids`, `label`) onto the shared parser. That is format repair,
not a new clinical rule.

## Required analysis

On `dev750` only:

- parse, schema, call, and empty-response counts
- Purist / Pragmatic versus same-model Hybrid and LLM-only
- changed-row direction versus cited extract
- a short hidden-family or failure-slice note if the score moves

`test450` is headline counts only.

## Artifact schema

```
experiments/paper/gan_llm_extract_encode_select/<slug>/20260905/{rows.jsonl,comparison.json}
scratch/holdout/paper/gan_llm_extract_encode_select/<slug>/20260905/{rows.jsonl,comparison.json}
```

One row is one letter. Keep raw output, repaired payload, projected label,
and Purist/Pragmatic flags.

## Stop rule

- Answer: hosted scores exist for all three models on both splits.
- Negative: one-call is worse than same-model Hybrid with a clear mechanism.
- Revise: parse/schema failures dominate.
- Do not promote. Do not rewrite the paper story from this run.

## Claim boundary

Development and aggregate-only holdout evidence for this prompt identity.
Not Table 1. Not a six-model roster change. Not clinical validation.

## Commands

```bash
source .venv/bin/activate
python -m clinical_extraction.paper run --method gan_llm_extract_encode_select \
  --model gemini37flash --split dev750 --live --work-leaf 20260905
python -m clinical_extraction.paper run --method gan_llm_extract_encode_select \
  --model gemini37flash --split test450 --live --work-leaf 20260905
python -m clinical_extraction.paper run --method gan_llm_extract_encode_select \
  --model gpt56luna --split dev750 --live --work-leaf 20260905
python -m clinical_extraction.paper run --method gan_llm_extract_encode_select \
  --model gpt56luna --split test450 --live --work-leaf 20260905
python -m clinical_extraction.paper run --method gan_llm_extract_encode_select \
  --model deepseek_v4_flash --split dev750 --live --work-leaf 20260905
python -m clinical_extraction.paper run --method gan_llm_extract_encode_select \
  --model deepseek_v4_flash --split test450 --live --work-leaf 20260905
```

Local replay later:

```bash
python -m clinical_extraction.paper run --method gan_llm_extract_encode_select \
  --model qwen38_27b --split dev750 --live --work-leaf 20260905
python -m clinical_extraction.paper run --method gan_llm_extract_encode_select \
  --model gemma4_26b --split dev750 --live --work-leaf 20260905
```
