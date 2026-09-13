# Protocol: Local one-call find, encode, and select

Date: 2026-09-13
Status: complete (aggregates plus `dev750` row analysis)
Owner: this file
Report: [aggregates](gan_local_one_call_encode_select_2026-09-13.md)
Guardrail: `gan2026-scoring-guardrail`
Related: [Gemini one-call `dev750`](gan_extract_encode_select_dev750_protocol_2026-09-02.md),
[local size ladder](../../paper_experiments/local_size_ladder.json)

## Primary question

On the frozen one-call prompt (`gan_llm_extract_encode_select`),
how do the six retained local models score on Gan `dev750` and
aggregate-only `test450`, and where do the smaller models break?

## Why this matters

Gemini one-call scored **657**/750 Purist on development and
**392**/450 on holdout. The living local pair (Qwen 3.8 27B,
Gemma 4 26B) was below Gemini and below those models' own cell 3
rule stack. A size-and-era ladder tests whether the gap is mostly
scale, generation, or JSON/form failure.

## Frozen candidate

Method `gan_llm_extract_encode_select`. Temperature 0. Cache off.
Native Ollama chat. Score the extract stop only (`raw_model`). No
rule encode or rule select after. Llama 2 13B is excluded: native
context is 4096 tokens and the holdout cell was 450/450 parse
failures.

Local set (not a living six-model roster swap):

| Slug | Tag | `num_ctx` |
| --- | --- | ---: |
| `llama31_8b` | `ollama_chat/llama3.1:8b` | 32768 |
| `qwen35_9b` | `ollama_chat/qwen3.5:9b` | 32768 |
| `qwen25_14b` | `ollama_chat/qwen2.5:14b` | 32768 |
| `gemma4_26b` | `ollama_chat/gemma4:26b` | 65536 |
| `qwen38_27b` | `ollama_chat/qwen3.8:27b` | 32768 |
| `qwen36_35b` | `ollama_chat/qwen3.6:35b` | 16384 |

Qwen thinking is off (`think=false`).

## Fixed comparators

| Cell | Surface | Purist |
| --- | --- | ---: |
| Gemini one-call | `dev750` | 657/750 |
| Gemini one-call | `test450` | 392/450 |
| Qwen 3.8 cell 3 select | `dev750` / `test450` | 577 / 343 |
| Gemma cell 3 select | `dev750` / `test450` | 567 / 326 |
| Qwen 3.8 cell 3 extract | `dev750` / `test450` | 505 / 315 |
| Gemma cell 3 extract | `dev750` / `test450` | 501 / 299 |

The four newer locals have no cell 3 cells in this write-up.

## Data and inspection

| Item | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Splits | `dev750` then `test450` (`gan2026_split_v1`) |
| Row policy | development review on `dev750`; aggregate-only on `test450` |
| Scorer | Purist primary; Pragmatic, parse, call, structured count |

Do not inspect `test450` rows. Do not retune the prompt from holdout.

## Required analysis

Aggregate Purist / Pragmatic / parse / structured / evidence-valid
on both splits. On `dev750` only, bucket written labels,
separate parse failure from wrong-but-parseable labels, and
attribute misses to schema, evidence, find, select, encode, or
form. Compare living locals to their cell 3 extract and select
stops. Do not inspect `test450` rows.

## Stop rule

Stop after all six local one-call cells exist on both splits and
this public write-up is saved. Cell 3 for the four newer locals is
a later study.

## Claim boundary

Local-model transfer of a frozen ablation prompt. Not Table 1. Not
a roster swap. Not a holdout generalization claim.
