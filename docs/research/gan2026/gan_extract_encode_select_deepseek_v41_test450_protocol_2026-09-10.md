# Protocol: DeepSeek V4.1 Flash one-call on `test450`

Date: 2026-09-10
Method: `gan_llm_extract_encode_select`
Model: `deepseek_v41_flash` (`deepseek/deepseek-flash`)
Work leaf: `20260910`

## Question

What is DeepSeek V4.1 Flash Purist on the current one-call prompt, on
locked `test450`?

This is a first look at a new first-party DeepSeek Flash revision. It is
not a living roster change and not a paper-row promotion.

## Surfaces

| Split | Policy | Inspection |
| --- | --- | --- |
| `test450` | aggregate-only | do not inspect rows |

Scorer is living Gan Purist. Secondary: Pragmatic, parse/call failures.

## Candidate

Live `gan_llm_extract_encode_select` at the extra runnable spec:
thinking enabled, reasoning low, `max_tokens=24000`, temperature 0.
Official API id is `deepseek-flash`.

Comparators, aggregate only: DeepSeek V4 Flash one-call **353**/450,
DeepSeek cell-3 find **334**, Hybrid **369**.

## Stop rule

Answer when the 450-row artifact exists. Do not promote. Do not inspect
holdout rows.

## Command

```bash
source .venv/bin/activate
python -m clinical_extraction.paper run --method gan_llm_extract_encode_select \
  --model deepseek_v41_flash --split test450 --live --work-leaf 20260910
```
