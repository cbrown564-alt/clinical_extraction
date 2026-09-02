# Results: Policy-example LLM select on Gan `dev750`

Date: 2026-08-31
Protocol: [protocol](gan_llm_select_policy_examples_dev750_protocol_2026-08-31.md)
Artifact: [aggregates](gan_llm_select_policy_examples_dev750_2026-08-31.json)
Work cell:
`experiments/paper/gan_llm_select_policy_examples/`
Split: `dev750`. Development review permitted.

## Answer

Gemini later-stage select on the saved `gan_llm_extract` ledger,
using the living policy-example prompt:

| Stop | Purist | Pragmatic |
| --- | ---: | ---: |
| Select | **640**/750 (0.8533) | **655**/750 (0.8733) |

Call failures **0**. Parse failures **0**. Structured records **750**.

Versus the cited development select stops:

| Comparator | Purist | Δ vs candidate |
| --- | ---: | ---: |
| Cited cell 5 (four-policy LLM select) | 590 | **+50** |
| Cited cell 3 (rule encode + rule select) | 656 | −16 |
| Standalone rules | 691 | −51 |

Flag-only versus cited cell 5: **56** rescues, **6** harms, net **+50**.

The same prompt on promoted `test450` cell 5 is 383/450 (0.85).
This development cell is 0.85 as well, against the earlier
four-policy 0.79.

## Mechanism

Rescues are mostly month-count and diary-style rates that the
four-policy prompt left wrong. The six harms are four gold-unknown
rows now given a rate or a dated event phrase, one gold month rate
rewritten as a longer span, and one gold year rate rewritten as
`unknown`.

## Protocol notes

OpenRouter batch `batch-1788211576-CE3ULSXdBXTgoxueo38E` completed
749/750. One item failed with a Gemini TPU upstream error. Those
749 rows were salvaged. The leftover row was submitted as a second
one-item batch and succeeded. Cited `gan_llm_select_from_extract`
was then promoted as living `dev750` cell 5.

## Claim boundary

Promoted cited `dev750` cell 5. Table development LLM / LLM / LLM
is **640**/750 (0.85). Same living prompt as `test450` 383/450.
Not holdout. Not a Table 1 change.
