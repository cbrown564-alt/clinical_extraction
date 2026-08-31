# Gan find prompt-component ablations (`test450`)

Date: 2026-08-30
Status: holdout aggregates complete
Owner: this file
Protocol: [2026-08-30 protocol](gan_extract_prompt_component_ablation_protocol_2026-08-30.md)
Artifact: [test450 aggregates](gan_extract_prompt_component_ablation_test450_2026-08-30.json)
Holdout: aggregate-only. No letter text and no row ids.

## Component map

Held constant: event/selection schema, Gemini 3.7 Flash, temperature
0, living cell-3 later stages.

| Find request | Instructions | Allowed labels | Examples | Written form | Scorer | test450 select |
| --- | --- | --- | --- | --- | --- | ---: |
| `gan_llm_extract` | Full | Yes | Yes | Codebook | Living | 387 |
| `gan_llm_extract_no_examples` | Full | Yes | No | Codebook | Living | 370 |
| `gan_llm_extract_raw` | Full + informal form hint | No | No | Source-near | Living (`llm_select`) | 357 |
| `gan_llm_extract_holgate_like` | Holgate three-step | No | No | Holgate grain | `holgate_dialect_v1` | 292 |

Isolates: examples (codebook vs no-examples); written form (codebook
vs source-near); whole codebook package vs Holgate ask.

Not isolated: instructions alone. That would need Holgate ask plus
living `label_forms`. Optional cleaner written-form cell: full
instructions, no `label_forms`, and no informal `1 per day` hint.

Source-near encode/select are the promoted `gan_llm_extract_raw`
stages (selected-evidence encode, then `llm_select`), not living
`gan_rules_encode`. That codebook encoder does not rewrite letter
wording. Do not cite the scratch cell-3 replay 252 / 274 as this
row.

## Question

On Gemini cell 3, how much of cited codebook find depends on example
strings, written form, and the codebook package versus a
Holgate-style three-step ask?

## Setup

Gemini 3.7 Flash, temperature 0, new OpenRouter batches. Later stages
are no-call replay: `gan_rules_encode` then
`llm_select_after_codebook`. Base is the living codebook rung, not a
new `gan_llm_extract` call.

| Request | Calls | Parse failures | Call failures |
| --- | ---: | ---: | ---: |
| `gan_llm_extract_no_examples` | 450 | 0 | 0 |
| `gan_llm_extract_holgate_like` | 450 | 0 | 0 |

## Purist micro-F1 on locked `test450`

| Find request | Find | Encode | Select |
| --- | ---: | ---: | ---: |
| `gan_llm_extract` (cited) | 0.789 (355) | 0.800 (360) | **0.860** (387) |
| `gan_llm_extract_no_examples` | 0.767 (345) | 0.776 (349) | 0.822 (370) |
| `gan_llm_extract_raw` | 0.547 (246) | 0.744 (335) | 0.793 (357) |
| `gan_llm_extract_holgate_like` (living parser) | 0.333 (150) | 0.416 (187) | 0.429 (193) |
| `gan_llm_extract_holgate_like` (`holgate_dialect_v1`) | 0.616 (277) | 0.640 (288) | 0.649 (292) |

**Table.** n=450. Paper Table 3b uses the dialect Holgate row, not
the living-parser Holgate row, and the promoted source-near
encode/select (335 / 357), not a living-`gan_rules_encode` replay.
Source-near find is scorable on 297 letters.
Holgate-like living find is scorable on 172 letters; cell-3 select is
scorable on 228. No-examples stays scorable on 444 at every stop.
Cited codebook find is scorable on 449.

Pragmatic select: cited 396, no-examples 381, source-near 369,
Holgate-like living 202.

## Answer

Removing examples, with instructions and allowed forms kept, costs
**10** Purist letters at find and **17** at cell-3 select (387 → 370).
That is a real but bounded examples effect.

Dropping the closed label list (source-near) costs **109** letters
at find. Selected-evidence encode recovers most of the form
(246 → 335); rule select reaches 357. Living `gan_rules_encode`
must not be used as that encode stop: it assumes codebook labels
already and only moves find 246 to 252.

Replacing the codebook package with the Holgate-style three-step ask
collapses living-parser find to **150**/450 (select 193). On
`holgate_dialect_v1` the same raws are 277 / 288 / 292. That is the
codebook package versus a short literature-style query, not an
instructions-only ablation.

Do not read this as separately measured instructions, labels, and
examples. Table 1 is unchanged.

## Claim boundary

Holdout evidence, aggregate-only. Ablation, not a results column.
Fair: “examples add a small select lift given the codebook; dropping
the closed label list costs most of the remaining cell-3 score on
the living parser; stripping the codebook down to a Holgate-style
ask stays below codebook select even on a Holgate dialect scorer.”
Not allowed: “we measured the separate importance of instructions,
labels, and examples.”
