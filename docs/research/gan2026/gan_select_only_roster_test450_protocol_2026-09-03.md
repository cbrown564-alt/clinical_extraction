# Protocol: Six-model rule select without encode on Gan `test450`

Date: 2026-09-03
Status: completed 2026-09-03
Owner: this file
Result: [report](gan_select_only_roster_test450_2026-09-03.md)
Artifact: [aggregates](gan_select_only_roster_test450_2026-09-03.json)

## Question

When each living roster model's saved `gan_llm_extract` ledger is
replayed through **rule select without encode** (`llm_select_only`),
what are the locked `test450` Purist and Pragmatic aggregates, and how
do they sit between find, encode stop, Hybrid (encode + rule select),
and same-model LLM select?

## Why it matters

Table 4 (Hybrid) always runs `gan_rules_encode` before rule select.
Table H1 runs same-model LLM select with no encode. Those two finals
confound encode with the decide executor. Cell 4
(`llm_select_only`) is the missing arm: select families on, codebook
encode off. On Gemini it is already living **382**/450. This study
extends that arm to the six-model roster so encode lift and select
lift can be read separately.

## Data and inspection

| Item | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Split | `test450` (aggregate only) |
| Row policy | No new model calls. Replay saved `gan_llm_extract` raw. |
| Holdout | Do not inspect rows. Do not dump failure ids or letter text. |
| Models | Gemini 3.7 Flash, Grok 4.6, GPT-5.6 Luna, DeepSeek V4 Flash, Qwen 3.8 27B, Gemma 4 26B |
| Scorer | Purist micro-F1 (primary); Pragmatic companion |
| Repair mode | `llm_select_only` (living select families, including `last_event_well_since`; no `codebook_label_repair`) |

Do not retune prompts, rules, or temperature from holdout aggregates.
Do not retune Table 1 or Table 4 from these cells.

## Candidate

`StructuredRepairConfig.for_mode("llm_select_only")` on each model's
promoted `gan_llm_extract` rows under
`paper_experiments/gan/gan_llm_extract/{slug}/test450/rows.jsonl`
(or the living scratch fallback used by `gan_living_extract_rows_path`).

## Comparators (read-only, existing artifacts)

| Arm | Source |
| --- | --- |
| Find / encode / Hybrid select | Table 4 / `paper_experiments/gan/rungs/{slug}/test450/comparison.json` |
| Same-model LLM select | Table H1 / hosted and local policy-example select reports |
| Gemini cell-4 gate | Living five-cell `llm_select_only` **382**/450 |

## Metrics

For each model, report Purist and Pragmatic correct counts of 450 for
`llm_select_only`. Derived deltas (aggregate only):

- select alone = select-only − find
- encode at final = Hybrid − select-only
- executor (no encode) = select-only − same-model LLM select

## Stop rule

Answer when all six models have select-only aggregates and Gemini
matches living cell 4 (**382**/450 Purist). Negative if a model lacks
saved extract raw. Do not start new calls in this study.

## Claim boundary

Holdout evidence is aggregate-only. Repository / transfer
decomposition only. Not a paper row, not a six-model roster change,
not permission to retune Hybrid or Table H1. Local models remain
technical-feasibility rows on synthetic letters.
