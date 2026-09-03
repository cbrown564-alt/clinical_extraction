# Results: Hosted same-model policy-example select on Gan `test450`

Date: 2026-09-03
Protocol: [protocol](gan_llm_select_policy_examples_hosted_test450_protocol_2026-09-03.md)
Work cells:
`scratch/holdout/paper/gan_llm_select_from_extract/<slug>/gan_llm_extract/test450`
Split: `test450` aggregate-only. No row inspection.

## Answer

The living policy-example select call, run on each hosted model's own
saved `gan_llm_extract` ledger, **raised** the Purist stop versus that
model's codebook find for DeepSeek, Grok, and Luna.

| Model | Find stop | Select stop | Δ Purist | Pragmatic select |
| --- | ---: | ---: | ---: | ---: |
| DeepSeek V4 Flash | 334/450 | **345**/450 (0.7667) | +11 | 356/450 (0.7911) |
| Grok 4.6 | 355/450 | **378**/450 (0.8400) | +23 | 394/450 (0.8756) |
| GPT-5.6 Luna | 312/450 | **335**/450 (0.7444) | +23 | 353/450 (0.7844) |
| Qwen 3.8 27B (local companion) | 315/450 | 294/450 | −21 | 312/450 |
| Gemma 4 26B (local companion) | 299/450 | 278/450 | −21 | 306/450 |
| Cited Gemini cell 5 | — | 383/450 (0.8511) | — | 391/450 |

DeepSeek: 450 scored rows after resumed live sync, 0 call failures,
0 parse failures, 449 structured records. Several rows truncated at
the living `max_tokens=8000` thinking budget; those rows were retried
by resuming the work cell without overwrite. Luna: 450 OpenAI-batch
calls, 0 call failures, 0 parse failures, 449 structured records.

Grok: 450 scored rows after several OpenRouter resume passes, 423 new
calls on top of 27 saved rows, 0 call failures, 0 parse failures, 450
structured records. OpenRouter returned intermittent `BadGatewayError`
during the run; resume without overwrite completed the cell.

## Claim boundary

Holdout aggregate-only transfer measurement. Not Table 1. Not cited
cell 5. Not a six-model roster change. Gemini remains the cited
later-stage model. No row-level rescue or harm table. No promotion.
