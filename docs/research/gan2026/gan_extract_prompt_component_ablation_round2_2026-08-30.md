# Gan find prompt components, round 2 (`test450`)

Date: 2026-08-30
Status: holdout aggregates complete
Owner: this file
Protocol: [round-2 protocol](gan_extract_prompt_component_ablation_round2_protocol_2026-08-30.md)
Artifact: [test450 aggregates](gan_extract_prompt_component_ablation_round2_test450_2026-08-30.json)
Holdout: aggregate-only. No letter text and no row ids.

## Question

How much of cited codebook find depends on the quote obligation, on
the closed form list versus examples alone, and on the event schema
versus a Holgate one-label ask?

## Setup

Gemini 3.7 Flash, temperature 0, new OpenRouter batches. Later
stages for the two codebook variants are no-call replay:
`gan_rules_encode` then `llm_select_after_codebook`. The Holgate
one-label row has no ledger.

The first Holgate one-label batch used the shared events/selection
DSPy signature. The model still wrote a one-field answer at
`selection.answer`. Scores below lift that field. A dedicated
one-label signature now exists for any later rerun.

| Request | Calls | Parse failures | Call failures |
| --- | ---: | ---: | ---: |
| `gan_llm_extract_holgate_label` | 450 | 0 after lift | 0 |
| `gan_llm_extract_no_evidence` | 450 | 1 | 0 |
| `gan_llm_extract_examples_only` | 450 | 0 | 0 |

The first examples-only batch hit one Gemini upstream decode error
and was resubmitted.

## Purist micro-F1 on locked `test450`

| Find request | Find | Encode | Select |
| --- | ---: | ---: | ---: |
| `gan_llm_extract` (cited) | 0.789 (355) | 0.800 (360) | **0.860** (387) |
| `gan_llm_extract_no_examples` | 0.767 (345) | 0.776 (349) | 0.822 (370) |
| `gan_llm_extract_examples_only` | 0.771 (347) | 0.776 (349) | 0.809 (364) |
| `gan_llm_extract_no_evidence` | 0.767 (345) | 0.771 (347) | 0.822 (370) |
| `gan_llm_extract_holgate_like` (`holgate_dialect_v1`) | 0.616 (277) | 0.640 (288) | 0.649 (292) |
| `gan_llm_extract_holgate_label` (`holgate_dialect_v1`) | 0.440 (198) | — | — |
| `gan_llm_extract_holgate_label` (living parser) | 0.309 (139) | — | — |

**Table.** n=450. Codebook variants use living cell 3. Holgate
one-label living find is 139; dialect find is 198, scorable 243.

## Answer

Dropping the quote obligation is a small move: find 355 → 345,
select 387 → 370. That matches the no-examples select total.

Keeping examples and dropping the closed form list is a bit costlier
at select (387 → 364) than keeping forms and dropping examples
(387 → 370). The form list is doing more work than the example
strings.

Removing the schema and quote rule from the Holgate ask drops dialect
find from 277 to 198. The event/selection object is load-bearing
even when the clinical ask is Holgate’s three steps.

Do not retune Table 1.

## Claim boundary

Holdout aggregate-only. Ablation, not a results column.
Fair: “the quote obligation is a small select lift; forms without
examples beat examples without forms; a Holgate one-label ask is
weaker than Holgate-plus-schema.”
Not allowed: treat Holgate one-label encode/select as living cell 3;
treat the first Holgate one-label batch as a clean no-adapter schema
run.
