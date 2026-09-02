# Results: One-call find, encode, and select on Gan `dev750`

Date: 2026-09-02
Protocol: [protocol](gan_extract_encode_select_dev750_protocol_2026-09-02.md)
Artifact: [aggregates](gan_extract_encode_select_dev750_2026-09-02.json)
Work cell:
`experiments/paper/gan_llm_extract_encode_select/gemini37flash/dev750/`
Split: `dev750`. Development review permitted.

## Answer

Gemini one-call codebook find + encode + living select cases,
scored at the extract stop (`raw_model`):

| Stop | Purist F1 | Pragmatic F1 |
| --- | ---: | ---: |
| One-call | **0.88** (657/750) | **0.90** (676/750) |

Call failures **0**. Parse failures **0**. Structured records **750**.

Versus the predeclared development stops (Purist):

| Comparator | Stop | Δ vs one-call |
| --- | ---: | ---: |
| Codebook extract (`gan_llm_extract`) | 585 (0.78) | **+72** |
| Living cell 5 (select from extract) | 640 (0.85) | **+17** |
| Cited cell 3 (rule encode + rule select) | 656 (0.87) | **+1** |
| Same prompt on `test450` (aggregate only) | 392 (0.87) | development is **+0.005** |

Flag-only changed rows:

| Comparator | Rescue | Harm | Net |
| --- | ---: | ---: | ---: |
| vs codebook extract | 90 | 18 | +72 |
| vs living cell 5 | 36 | 19 | +17 |

The holdout one-call **0.87** is not a split fluke. Development is
**0.88**, one Purist above cited cell 3.

## Mechanism

Rescues versus extract are mostly gold frequency rows (78/90),
plus cluster/unresolved-multiple (6) and seizure-free (5). That
is the living select cases doing the work extract left on the
table.

Harms versus extract (18) split evenly: nine gold-unknown rows
now given a rate, cluster, or seizure-free span, and nine gold
rates rewritten (month-count collapsed to per-year, a daily rate
replaced by a seizure-free window, cluster count dropped to a
plain rate).

Versus living cell 5 the extra rescues are still mostly
frequency (24/36) and cluster wording (6). The 19 harms repeat
the same two modes: gold-unknown filled in (5) and a current
rate overwritten by a seizure-free window or a longer span
rewritten as per-year (14).

## Claim boundary

Development measurement of the frozen one-call prompt. Ablation,
not Table 1. Not promoted. Not cell 5. Not a holdout claim. Do
not retune the prompt from `test450`.
