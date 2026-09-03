# Results: Local same-model policy-example select on Gan `test450`

Date: 2026-09-03
Protocol: [protocol](gan_llm_select_policy_examples_local_test450_protocol_2026-09-02.md)
Work cells:
`scratch/holdout/paper/gan_llm_select_from_extract/<slug>/gan_llm_extract/test450`
Split: `test450` aggregate-only. No row inspection.

## Answer

The living policy-example select call, run on each local model's own
saved `gan_llm_extract` ledger, **lowered** the Purist stop versus
that model's codebook find.

| Model | Find stop | Select stop | Δ Purist | Pragmatic select |
| --- | ---: | ---: | ---: | ---: |
| Qwen 3.8 27B | 315/450 | **294**/450 (0.6533) | −21 | 312/450 (0.6933) |
| Gemma 4 26B | 299/450 | **278**/450 (0.6178) | −21 | 306/450 (0.6800) |
| Cited Gemini cell 5 | — | 383/450 (0.8511) | — | 391/450 |

Qwen: 450 calls, 0 call failures, 0 parse failures, 448 structured
records. Gemma: 450 calls, 0 call failures, 0 parse failures, 442
structured records.

## Claim boundary

Holdout aggregate-only transfer measurement. Not Table 1. Not cited
cell 5. Not a six-model roster change. Gemini remains the cited
later-stage model. No row-level rescue or harm table. No promotion.
