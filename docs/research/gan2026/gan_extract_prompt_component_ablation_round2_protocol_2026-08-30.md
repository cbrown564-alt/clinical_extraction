# Protocol: Gan find prompt components, round 2

Date: 2026-08-30
Status: `test450` finds and cell-3 replay complete
Owner: this file
Report: [round-2 aggregates](gan_extract_prompt_component_ablation_round2_2026-08-30.md)
Related: [round 1](gan_extract_prompt_component_ablation_protocol_2026-08-30.md),
[results §D3](../../paper/sections/results.md)

## Primary question

On Gemini cell 3, how much of cited codebook find depends on (1) the
event/selection schema plus the exact-quote evidence obligation, and
(2) the closed form list versus example strings alone?

Five request parts:

| Part | Living codebook |
| --- | --- |
| Schema | Event list + selection object |
| Instructions | Full current-event policy |
| Labels | Closed `label_forms` |
| Examples | Example strings on those forms |
| Evidence | `evidence` keys plus the exact-substring instruction |

Round 1 isolated examples, written form, and the whole codebook
package. This round isolates schema/evidence and the forms-versus-
examples split.

## Candidates

All three are `paper_cell: False` ablations. Gemini 3.7 Flash,
temperature 0, new OpenRouter batches. Do not retune Table 1.

### 1. Holgate one-label floor — `gan_llm_extract_holgate_label`

Holgate three-step ask only. No event schema, no selection schema,
no `label_forms`, no examples, no `evidence` keys, no exact-quote
instruction. One JSON field: `answer`.

Scorer: `holgate_dialect_v1` on that answer. Living parser is a
companion find only. Encode and select are not this row: there is
no ledger.

### 2. Codebook minus evidence — `gan_llm_extract_no_evidence`

Cited `gan_llm_extract` with a small deletion: drop `evidence` from
the event schema and the selection schema, and drop the exact-
substring instruction. Keep events, selection, clinical
instructions, `label_forms`, and examples.

The living parser must accept a missing `evidence` key as an empty
quote. That is a scoring-floor change so the cell can replay. It
does not change the cited codebook request.

Later stages: living cell 3 (`gan_rules_encode`, then
`llm_select_after_codebook`). Question: does this make a marginal
difference at find and select?

### 3. Examples only — `gan_llm_extract_examples_only`

Cited codebook without the closed form list. Keep the example
strings as a flat `examples` array. Keep schema (including
evidence), clinical instructions, and the exact-quote rule. Rewrite
only the “allowed forms” sentences so they do not name a form list
that is no longer present.

Later stages: living cell 3. Inverse of `gan_llm_extract_no_examples`.

## What is held constant

- Dataset Gan 2026, locked `test450`, aggregate-only.
- Model Gemini 3.7 Flash, temperature 0.
- No new encode or select model calls.
- Cited codebook template unchanged.

## Comparator

Living Gemini cell 3 on the same letters:

| Stop | Purist |
| --- | ---: |
| Find | 0.789 (355) |
| Encode | 0.800 (360) |
| Select | 0.860 (387) |

Round-1 companions stay on disk: no-examples select 370; source-near
select 357 on the selected-evidence stack; Holgate-like dialect
select 292.

## Required tables

Find / encode / select Purist on `test450` for cells 2 and 3.
Find only (living and dialect) for cell 1. Parse and call failures.
Do not inspect holdout rows.

## Artifact

- `scratch/holdout/paper/gan_llm_extract_holgate_label/gemini37flash/test450/`
- `scratch/holdout/paper/gan_llm_extract_no_evidence/gemini37flash/test450/`
- `scratch/holdout/paper/gan_llm_extract_examples_only/gemini37flash/test450/`

Do not promote into `paper_experiments/gan/rungs/`.

## Commands

```bash
source .venv/bin/activate
python -m clinical_extraction.paper verify --method gan_llm_extract_holgate_label --model gemini37flash --split test450
python -m clinical_extraction.paper verify --method gan_llm_extract_no_evidence --model gemini37flash --split test450
python -m clinical_extraction.paper verify --method gan_llm_extract_examples_only --model gemini37flash --split test450
python -m clinical_extraction.paper run --method gan_llm_extract_holgate_label --model gemini37flash --split test450 --live
python -m clinical_extraction.paper run --method gan_llm_extract_no_evidence --model gemini37flash --split test450 --live
python -m clinical_extraction.paper run --method gan_llm_extract_examples_only --model gemini37flash --split test450 --live
```

## Stop rule

Answer when all three finds finish and cells 2–3 have a no-call
cell-3 replay. Negative result is allowed. Do not change Table 1.

## Claim boundary

Holdout aggregate-only. Ablation, not a results column.
Fair: “dropping the quote obligation changed find/select by …”;
“examples without the closed form list changed find/select by …”;
“a Holgate one-label ask scored … on the dialect map.”
Not allowed: retune Table 1; treat cell 1 encode/select as living
cell 3.
