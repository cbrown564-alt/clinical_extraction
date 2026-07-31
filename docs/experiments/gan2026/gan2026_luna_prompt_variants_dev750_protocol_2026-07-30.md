# Gan 2026 Luna prompt-variant A/B/C protocol

Date: 2026-07-30  
Status: complete; A/B/C `validation750` panel finalized 2026-07-30  
Parent panel: [matched v0.5 dev750](gan2026_matched_v05_dev750_protocol_2026-07-27.md)  
Draft notes: [gan2026_luna_prompt_variants_draft_notes_2026-07-30.md](gan2026_luna_prompt_variants_draft_notes_2026-07-30.md)

## Primary question

For GPT-5.6 Luna alone on Gan `validation750`, how much can prompt change move
**LLM-only** and **LLM-with-rules** Purist accuracy when the event schema,
repair stack, scorers, and split stay frozen?

This is a Luna-versus-Luna development candidate. It is not a six-model
comparison and must not rewrite the frozen v0.5 panel.

## Why this study

Most Gan prompt iteration used GPT-4.1-mini. The frozen Luna v0.5 condition
already shows:

| Boundary | Luna Purist |
| --- | ---: |
| LLM-only (model boundary) | 411/750 |
| LLM with rules | 646/750 |
| Rules control alone | 697/750 |

Of Luna's 339 raw-wrong rows, 309 are rows the rules control already gets
right. Almost all wrongs still have exact evidence. The residual is clinical
selection and label construction, not quotation failure. That makes Luna a
cheap surface for testing whether prompt tuning still matters inside an
LLM-only and LLM-with-rules framework.

## Fixed conditions

- Dataset: Gan 2026.
- Split manifest: `gan2026_split_v1`.
- Split: development `validation750` (legacy id for `dev750`); row-level
  analysis is permitted.
- Locked split: `test450` remains aggregate-only and sealed. No row inspection,
  failure analysis, or prompt change from test450.
- Model: `openai/gpt-5.6-luna` only.
- Route and sampling: match the frozen Luna v0.5 dev750 condition
  (OpenAI chat via DSPy/LiteLLM, temperature `1`, max tokens `10000`, cache
  disabled) unless a provider constraint forces an explicit recorded change.
- Schema: keep the v0.5 events-plus-selection JSON contract unchanged.
- Repair: `hybrid_full_stack` unchanged for the LLM-with-rules readout.
- Scores: Gan Purist primary; Pragmatic secondary.
- Trace schema: `gan2026.row_trace.v1`.
- Output root:
  `scratch/validation/gan2026_luna_prompt_variants_dev750_20260730/`.

## Three prompt variants

| ID | Prompt identity | Strategy | Residual target |
| --- | --- | --- | --- |
| A | `gan2026_hybrid_structured_events_v0.5` | Frozen control | None; baseline |
| B | `gan2026_hybrid_structured_events_v0.8_luna_rate` | Rate and aggregation instructions | `rate_denominator`, `cluster_or_diary_aggregation` |
| C | `gan2026_hybrid_structured_events_v0.8_luna_current` | Current-state and boundary instructions | `seizure_free_boundary`, `temporal_selection`, `uncertainty_boundary`, `competing_event_selection` |

Variant A reuses the retained Luna v0.5 raw outputs for no-call replay where
possible. Variants B and C are implemented as additive instruction blocks on
the frozen v0.5 schema and are pinned by prompt-contract snapshots:

- B snapshot SHA-256 `494f1f76f8ca845e43a05e0a91956cc5b812ce4b3323379923b55003f6636a91`
- C snapshot SHA-256 `eb23c98e38bb9dfbacd40fe3604ba734cfdd926e7eb259d2e5f06c11a644238a`

Rules for B and C:

- Change model-facing instructions and field descriptions only.
- Do not change enum names, required fields, repair policy, normalization, or
  scorers.
- Do not mix B and C into a kitchen-sink prompt until one variant wins its
  target slices without harming the complementary slices.
- Do not retarget the frozen six-model panel prompt in place.

## Predeclared hard slices

Slices come from the retained Luna attribution artifact. No fresh hard-slice
generation run is required to open the study.

| Bundle | Clinical subproblems | Luna raw wrong | Luna unrescued final wrong |
| --- | --- | ---: | ---: |
| B target | `rate_denominator`, `cluster_or_diary_aggregation` | 232 | 54 |
| C target | `seizure_free_boundary`, `temporal_selection`, `uncertainty_boundary`, `competing_event_selection` | 107 | 45 |
| All residual | all six subproblems above | 339 | 99 |

Complementary off-target slices are scored for every variant so a B win is not
bought by damaging C, and the reverse.

## Drafting aid

Representative wrong rows for instruction drafting:

- [exemplar pack report](gan2026_luna_prompt_variants_exemplar_pack_2026-07-30.md)
- [machine pack](../../../experiments/gan2026_luna_prompt_variants_dev750_20260730/exemplar_pack.json)
  (SHA-256 `82eedfaf66a1a86a1390db2b779830b58652f367696a7021bf0be09eddd64a78`)

The pack is a drafting aid, not a mini-benchmark to overfit. After B and C are
drafted, evaluation uses the full `validation750` denominators and the
predeclared slices above.

## Required readouts

For each variant, retain matched:

1. **LLM-only** Purist and Pragmatic at the model boundary.
2. **LLM-with-rules** Purist and Pragmatic after `hybrid_full_stack`.
3. Exact and grounded selected-evidence counts.
4. Wrong-to-correct and correct-to-wrong transitions versus the model boundary.
5. First-failure owner and clinical-subproblem counts.
6. Slice tables for B-target, C-target, and all-residual denominators.
7. Prompt snapshot hash and rendered payload identity.

Primary decision metrics:

- LLM-only Purist on full `validation750`.
- LLM-only Purist on the variant's target slice bundle.
- LLM-with-rules Purist on full `validation750` as a secondary safety readout.

A variant is interesting only if LLM-only improves on its target bundle without
a material off-target loss. Aggregate LLM-with-rules gain alone is not enough
if the raw boundary does not move.

## Execution order

1. Keep A as the frozen Luna v0.5 no-call baseline.
2. Draft B from the rate/aggregation exemplars; audit for plain language.
3. Draft C from the current-state/boundary exemplars; audit for plain language.
4. Optional cheap pilot: stratified hard subset before full 750, only if the
   pilot rows and stop rule are recorded first.
5. Run B and C on full `validation750` with cache disabled.
6. Build the machine comparison artifact before the narrative report.

## Stop rule

- Answer: one of B or C improves Luna LLM-only Purist on its target bundle and
  does not worsen complementary slices enough to cancel the gain; report the
  matched LLM-with-rules effect.
- Negative: neither B nor C moves LLM-only beyond noise on its target bundle.
- Revise once: if a draft fails only from clear instruction ambiguity found in
  permitted development rows, allow one redraft per variant.
- Reject: any change that alters schema enums, repair semantics, scorers, or
  inspects `test450`.
- Do not promote a Luna-tuned prompt into the frozen six-model panel from this
  study alone.

## Required artifact

Retain a machine comparison with:

- schema version `gan2026.luna_prompt_variants_dev750.v1`;
- one row per source row per variant;
- prompt version and snapshot hash;
- raw model output, model-boundary label, final label, evidence grade;
- Purist and Pragmatic flags at both boundaries;
- clinical_subproblem and first_failure_owner;
- slice membership flags for B-target and C-target;
- claim boundary string.

Narrative report path:

`docs/experiments/gan2026/gan2026_luna_prompt_variants_dev750_2026-07-30.md`

## Claim boundary

Development evidence for Luna prompt sensitivity under a frozen Gan schema and
repair stack. It may support a bounded claim that prompt tuning still moves
LLM-only and/or LLM-with-rules answers for this model and distribution. It does
not establish general model ranking, clinical validation, holdout
generalization, or replacement of the frozen six-model v0.5 panel.

## Next action

Execute the Luna-only A/B/C comparison on `validation750` with dual LLM-only
and LLM-with-rules readouts. Reuse A from the retained Luna v0.5 artifact.
Do not inspect `test450` or rewrite the frozen six-model panel.
