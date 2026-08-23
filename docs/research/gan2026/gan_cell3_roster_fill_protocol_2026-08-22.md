# Gan cell-3 roster fill protocol

Date: 2026-08-22
Status: in progress
Owner: this file
Related: [six-model roster](../../paper/decisions/six-model-roster.md),
[extract label-forms](gan_extract_label_forms_protocol_2026-08-22.md)

## Question

Do the remaining hosted roster models produce a complete cell-3
extract (`gan_llm_extract`) on the same frozen prompt as
Gemini, so rule encode and rule select can be replayed no-call?

## Why it matters

The six-model comparison is cell 3 only. Gemini already has both
splits. Grok, Luna, and DeepSeek have older Gan extracts
(`gan_llm_extract_raw`, `gan_llm_only`) that are not this row.

## Data and inspection

| Item | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Splits | `dev750` first, then aggregate-only `test450` |
| Row policy | Development review on `dev750`. Do not inspect `test450` rows. |
| Models | `grok46`, `gpt56luna`, `deepseek_v4_flash` |
| Prompt | Frozen `gan_llm_extract` |
| Repair | Extract stop only (`raw_model`) |
| Reasoning | Living paper setting (`low` for Grok and Luna). DeepSeek uses the living provider default. Max tokens 24000 for DeepSeek. |
| Work cells | `experiments/paper/gan_llm_extract/{slug}/dev750/` |
| Holdout | `scratch/holdout/paper/gan_llm_extract/{slug}/test450/` |

Qwen and Gemma are reserved for a separate local device. Do not
start later-stage LLM encode or select for these models. Do not
overwrite promoted `paper_experiments/`. One job per API.

## Stop rule

Stop each model after `dev750` writes `comparison.json`, then run
aggregate-only `test450` on the same key. Do not retune from
holdout. Promote only after both splits exist.

## Claim boundary

Development extract plus aggregate-only holdout extract. Cell-3
select scores wait for no-call rule replay. Not a Gemini headline
replacement.
