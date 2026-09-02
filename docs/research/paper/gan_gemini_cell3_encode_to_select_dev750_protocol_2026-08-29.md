# Protocol: Gemini cell 3 encode→select changes on Gan `dev750`

Date: 2026-08-29
Status: completed
Owner: this file
Report:
[encode→select change analysis](gan_gemini_cell3_encode_to_select_dev750_2026-08-29.md)

## Primary question

On Gemini 3.7 Flash cell 3 (`gan_llm_extract` → `gan_rules_encode` →
`llm_select_after_codebook`) on Gan `dev750`, which rows change between
the encode stop and the select stop, and what clinical work does
select actually do?

This matters because the cited cell-3 score is the select stop. The
encode stop is a prior-stage ablation. Incremental select gain is only
interpretable if the changed rows can be grouped by mechanism, not
just by net Purist.

## Why this study

The living Gemini `dev750` rungs already record encode **608/750**
Purist and select **649/750** Purist. That +41 is an aggregate. This
study accounts every encode→select label change, names the first
select family that moved the submitted label, and inspects
representative development rows for helpful and harmful changes.

## Scope

- Dataset: Gan 2026. Split: `dev750`. Manifest: `gan2026_split_v1`.
- Row policy: development review permitted. `test450` is not loaded.
- Candidate: living cell-3 select (`llm_select` rung =
  `llm_select_after_codebook`).
- Comparator: living cell-3 encode (`llm_encode` rung =
  `gan_rules_encode`) on the same saved `gan_llm_extract` raw.
- Model: Gemini 3.7 Flash. Replay: no-call. Zero new model calls.
- Scorer: Gan Purist category accuracy (primary). Pragmatic and exact
  normalized label as secondary.
- Component under study: recorded select families after codebook
  encode. Encode is held fixed. Deterministic safety floors stay as
  already frozen in `llm_select_after_codebook`.
- Required analysis: full changed-row table; direction
  (wrong-to-correct / correct-to-wrong / wrong-stay / correct-stay);
  first changing `gan.select.*` family; kind and gold-kind
  cross-tabs; qualitative inspection of representative helpful and
  harmful rows.

## Artifact

Machine-readable changed-row ledger:

`docs/research/paper/gan_gemini_cell3_encode_to_select_dev750_changed_rows_2026-08-29.jsonl`

One row per encode→select label change. Fields: source id, gold,
encode/select labels and kinds, Purist/Pragmatic direction, first
changing select family, selected-event-id change, extract evidence
span when present.

## Stop rule

Answer from the saved rungs. Do not retune select families. Do not
inspect holdout. If hops lack a first-family owner, report that as
instrumentation, not as a new family.

## Claim boundary

Development answer on Gemini cell 3 `dev750`. It explains where the
select-stop increment comes from on this split. It does not support a
holdout letter attribution, a new five-cell number, or an LLM-select
claim. Select here is recorded rules after codebook encode.
