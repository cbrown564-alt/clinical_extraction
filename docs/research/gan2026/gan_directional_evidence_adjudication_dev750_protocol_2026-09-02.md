# Protocol: directional source exactness and semantic-support adjudication on Gan `dev750`

Date: 2026-09-02  
Status: development-first protocol drafted; adjudication not started  
Owner: this file  
Paper decision: [paper-story simplification](../../paper/decisions/paper-story-simplification.md)  
Prompt: [model-facing adjudication prompt](gan_directional_evidence_adjudication_prompt_2026-09-02.json)  
Rendered example: [rendered prompt example](gan_directional_evidence_adjudication_rendered_example_2026-09-02.md)

## Primary question

On Gan 2026 `dev750`, how often are (A) existing annotation reference texts
and (B) pipeline-collected evidence spans exact source text, and how often do
they support the target current seizure-frequency answer under the existing
decision policy?

This is a directional soft measure of evidence quality. It is not a new gold
standard, a replacement for the Gan scorer, or a clinical validation study.

## Development-first boundary

- Dataset: Gan 2026 synthetic letters.
- Split: paper `dev750` only (machine `validation`).
- Row policy: development rows may be inspected; do not load, inspect, or
  aggregate `test450` in this study.
- Target: the already-defined Gan answer for current seizure frequency.
- Policy: use the existing plain-language current-state decision policy; do
  not create or extend policy during review.
- Model calls: none for this protocol draft. Any later adjudication call must
  be separately recorded with model, prompt version, replay/cache state, and
  call failures.
- Holdout gate: no aggregate-only held-out replay until the development
  substrate, output parser, and review rules are checked and explicitly
  accepted.

## Two evidence arms

Each row has the source letter, target answer, and provenance identifiers. The
arms are scored separately and must not be pooled into one evidence measure.

### A. Existing annotation reference

1. Deterministically test whether the stored reference is an exact substring
   of the source letter. Record `exact_substring` as `true`, `false`, or
   `missing` (with a normalized comparison only as a diagnostic, never as an
   exact match).
2. Ask the adjudicator whether the reference supports the target answer.
   Show the target answer, policy, and reference text. Do not show the
   full letter, pipeline spans, normalized labels, or predicted answer.
3. The reference is a comparator, not ground truth for span correctness. It
   may be exact, paraphrased, abbreviated, ellipsized, or missing. A missing
   or inexact reference may still be semantically sufficient, and an exact
   reference may be semantically insufficient.

### B. Pipeline extraction

1. Deterministically test every collected evidence span against the source
   letter. Record per-span exactness and an all-spans result. Empty evidence
   is recorded as `missing`/`insufficient`, not as exact.
2. Ask the adjudicator whether all supplied spans together support the target
   answer under the policy. Show raw spans and event grouping, but do not show
   model-normalized candidate labels, the pipeline predicted answer, the full
   letter, or the existing annotation reference.
3. The adjudicator may use only the supplied raw spans, grouping, target
   answer, and policy. It must not fill gaps with broader clinical reasoning.

## Review unit and development sample

The review unit is one `(source_row_index, arm)` record. Build the complete
development substrate before any adjudication calls. Preserve source-row and
evidence identifiers; never overwrite raw pipeline output or the annotation
reference.

The first pass is a pilot of 30 distinct `dev750` letters, sampled by a
predeclared stable hash of `source_row_index` after the substrate is built.
Use both arms for every selected letter. Do not replace rows after seeing
labels or adjudication output. If the pilot exposes a schema or rendering
defect, pause, fix the artifact generation, and start a new dated protocol
version; do not silently revise completed decisions.

## Model-facing output

The adjudicator returns exactly one JSON object with:

- `judgment`: `supported`, `unsupported`, or `insufficient`;
- `reason`: one concise source-based sentence;
- `policy_operations`: one or more tags from the controlled list below.

`insufficient` means the supplied material does not allow a policy-grounded
decision. Do not use it as a softer form of unsupported. Do not output
confidence, a normalized label, a replacement evidence span, or free-form
clinical advice.

Allowed policy-operation tags:

- `target_current_state`
- `choose_current_over_historical`
- `choose_overall_over_subtype`
- `interpret_rate_or_range`
- `interpret_cluster_rate`
- `interpret_seizure_free`
- `retain_unknown_when_frequency_unclear`
- `distinguish_no_reference`
- `resolve_multiple_current_statements`
- `none`

Use `none` only when the supplied evidence directly supports the target
without applying a named operation. Tags describe the policy operation that
made the support judgment; they are not new policy rules.

## Artifact schema and provenance

Create a machine-readable artifact under a dated directory, for example
`experiments/gan_directional_evidence_adjudication_dev750_20260902/`.
At minimum retain:

- `summary.json`: protocol id/version, date, commit and dirty-tree note,
  split, sample rule, row counts, prompt id/version, model/call metadata,
  and aggregate counts only after adjudication;
- `rows.jsonl`: one row per letter and arm with source-row id, target answer,
  arm, raw reference or raw grouped spans, deterministic exactness results,
  adjudication output, and provenance pointers;
- `rendered_prompts/`: the exact model-facing text sent for each arm, or a
  content-addressed equivalent.

Keep research metadata (sample ids, run ids, model, scorer, prompt version,
and stop rules) outside the model-facing payload. Keep exactness checks,
adjudication, and any later aggregation as separate fields and stages.

## Quality controls

- Inspect the rendered example for both arms before any calls.
- Verify the pipeline payload omits the full letter, predicted answer,
  normalized labels, and annotation reference.
- Verify the reference payload does not expose pipeline outputs.
- Validate JSON against the output schema; reject extra keys and invalid enum
  values.
- Run a small manual development audit of rendered inputs and parsed outputs.
- If humans are used, retain independent decisions, revisions, and any
  adjudication without rewriting the original record.

## Stop rule and claim boundary

Stop after the development pilot is rendered, schema-checked, and adjudicated
with its provenance artifact, or stop earlier if instrumentation cannot prove
the two visibility boundaries. A positive, negative, or mixed pilot result
only supports a development directional finding. It does not support
benchmark improvement, holdout generalization, span-ground-truth claims, or
clinical validity. Any held-out replay requires a new frozen protocol after
the development result and implementation assumptions are reviewed.

