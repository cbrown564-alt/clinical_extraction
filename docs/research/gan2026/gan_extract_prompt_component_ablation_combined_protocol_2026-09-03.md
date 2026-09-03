# Protocol: Combined Gan find prompt-component ablation

Date: 2026-09-03
Status: predeclared
Owner: this file

## Primary question

On Gemini cell 3, what happens when the extraction prompt simultaneously
removes few-shot examples, the exact-substring evidence obligation, and the
closed allowed-label forms?

## Candidate

`gan_llm_extract_no_examples_no_evidence_no_forms`: retain the event and
selection schemas and the clinical policy instructions, while omitting the
`evidence` fields and quote instruction, the `label_forms` block, and all
example strings. Gemini 3.7 Flash, temperature 0, OpenRouter Batch API.

## Data and controls

- Gan 2026 locked `test450`, `gan2026_split_v1`; aggregate-only, no row or note inspection.
- Primary scorer: Purist micro-F1; Pragmatic is a companion.
- Comparator: living Gemini cell 3, find 355/450, encode 360/450, select 387/450.
- Encode and select use saved-output replay through the living cell-3 stages; no new later-stage calls.
- Parse, schema, call, abstention, and fallback events are recorded separately.
- This is an ablation, not a paper Table 1 row and is not promoted.

## Required output and stop rule

Report find, encode, and select Purist/Pragmatic aggregates, scorable counts,
parse/schema failures, and call failures. Stop when the live extract and
no-call cell-3 replay are complete; a negative result is valid. Do not inspect
holdout rows or retune from this split.

## Claim boundary

Holdout aggregate-only. The result may support only a bounded statement about
the combined prompt deletion on this named test split; it cannot attribute the
effect to any one removed component.
