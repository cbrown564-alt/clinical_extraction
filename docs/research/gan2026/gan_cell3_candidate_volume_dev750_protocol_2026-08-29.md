# Protocol: Cell 3 find vs selected-evidence candidate volume on Gan `dev750`

Date: 2026-08-29
Status: completed
Owner: this file
Report:
[candidate-volume report](gan_cell3_candidate_volume_dev750_2026-08-29.md)

## Primary question

On living Gan cell 3 (`gan_llm_extract` → `gan_rules_encode` →
`llm_select_after_codebook`), how many candidate events does each of the
six roster models write at find, and how many of those events does the
same find call propose as selected evidence?

For Gemini only, does that volume differ by gold Purist or gold
Pragmatic category?

This matters because cell 3 is the only six-model row. A later-stage
score cannot be compared across models if the models do not propose
comparable find ledgers.

## Why this study

The living `dev750` rungs already store per-row `predicted_candidate_count`
(find events) and `selected_event_ids` (the find call’s selected-evidence
set). Those counts have not been reported as averages, nor broken down by
Purist or Pragmatic gold band.

## Scope

- Dataset: Gan 2026. Split: `dev750`. Manifest: `gan2026_split_v1`.
- Row policy: development review permitted. `test450` is not loaded for
  row-level work. A find-only aggregate from existing
  `comparison.json` totals is allowed as a companion; selected-evidence
  averages on holdout are omitted because those rungs have no
  `scored.jsonl`.
- Candidate: living cell-3 find (`llm_extract` rung on saved
  `gan_llm_extract` raw).
- Comparator: none. This is a volume description, not a score comparison.
- Models: the six-model roster
  (Gemini 3.7 Flash, Grok 4.6, GPT-5.6 Luna, DeepSeek V4 Flash,
  Qwen 3.8 27B, Gemma 4 26B).
- Replay: no-call. Zero new model calls.
- Scorer: unused for the primary table. Gold Purist and Pragmatic
  categories for the Gemini slice use living
  `map_purist` / `map_pragmatic` on `gold_monthly_frequency`.
- Component under study: the find call’s event list and
  `selected_event_ids`. Encode and rule select are recorded only to
  check whether selected-event ids later change.
- Required analysis: per-model mean / median / min / max find counts
  and selected-evidence counts; Gemini breakdown by gold Purist and
  gold Pragmatic category; note any extract→select selected-id change.

## Artifact

Machine-readable summary:

`docs/research/gan2026/gan_cell3_candidate_volume_dev750_2026-08-29.json`

One object with per-model aggregates and Gemini-by-gold-Purist and
Gemini-by-gold-Pragmatic tables. No letter text.

## Stop rule

Answer from the saved `dev750` rungs. Do not retune find. Do not inspect
holdout rows. If a model lacks `selected_event_ids`, report that as
instrumentation.

## Claim boundary

Development description of cell-3 find volume on `dev750`. It does not
support a holdout candidate-volume claim, a new six-model score, or an
encode/select mechanism claim.
