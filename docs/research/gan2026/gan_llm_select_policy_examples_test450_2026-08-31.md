# Results: Policy-example LLM select on Gan `test450`

Date: 2026-08-31
Protocol: [protocol](gan_llm_select_policy_examples_test450_protocol_2026-08-31.md)
Artifact: [aggregates](gan_llm_select_policy_examples_test450_2026-08-31.json)
Work cell:
`scratch/holdout/paper/gan_llm_select_policy_examples/`
Split: `test450` aggregate-only. No row inspection.

## Answer

Gemini later-stage select on the saved `gan_llm_extract` ledger,
using the living policy-example prompt:

| Stop | Purist | Pragmatic |
| --- | ---: | ---: |
| Select | **383**/450 (0.8511) | **391**/450 (0.8689) |

Scorable **450**. Call failures **0**. Parse failures **0**.

This run is now the cited cell-5 select stop.

Versus the other Table 1 select stops on the same split:

| Comparator | Purist | Δ vs this cell |
| --- | ---: | ---: |
| Prior four-policy cell 5 | 357 | **+26** |
| Cited cell 4 (rule select only) | 382 | +1 |
| Cited cell 3 (rule encode + rule select) | 387 | −4 |

## Protocol notes

OpenRouter batch returned 402. The run used live sync. Credits
stopped the first pass at 399 saved rows; the remaining 51 were
called after credit was restored. The isolated work cell was not
written into `gan_llm_select_from_extract`.

## Claim boundary

Promoted cited cell 5 on aggregate-only `test450`. Table 1 LLM /
LLM / LLM is **383**/450 (0.85). `dev750` cell 5 was not rerun.
No row-level rescue or harm table.
