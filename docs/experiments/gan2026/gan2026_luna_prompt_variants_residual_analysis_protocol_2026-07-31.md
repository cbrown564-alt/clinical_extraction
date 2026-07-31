# Luna A/B/C residual-error analysis protocol

Date: 2026-07-31  
Status: complete; no-call development analysis  
Parent study: [Luna prompt variants](gan2026_luna_prompt_variants_dev750_protocol_2026-07-30.md)

## Primary question

On Gan `validation750`, why do Luna prompt variants A/B/C still leave a large
residual under frozen schema, repair, and scorers? Which failure mechanisms
persist across all three prompts, and which are particular to each variant?

## Fixed conditions

- Dataset / split: Gan 2026 `validation750` (`dev750`); row inspection permitted.
- Model: GPT-5.6 Luna only.
- Variants: A `v0.5`, B `v0.8_luna_rate`, C `v0.8_luna_current`.
- Repair: `hybrid_full_stack` unchanged.
- Scorer: Gan Purist primary; Pragmatic secondary.
- Call mode: no fresh model calls; replay saved A/B/C row traces.
- Locked split: `test450` remains sealed and uninspected.

## Method

1. Join the three retained `validation750.rows.jsonl` artifacts on
   `source_row_index`.
2. Score LLM-only (model-boundary `selection.final_label`) and LLM-with-rules
   (final structured label) Purist correctness per row.
3. Attach Luna clinical-subproblem labels from the matched v0.5 attribution
   artifact for slice membership.
4. Assign coarse residual themes from gold label, predicted label, selected
   evidence, and selection rationale.
5. Partition rows into persistent wrongs (wrong in A, B, and C), variant-only
   wrongs, and rescue/regress sets versus A.
6. Inspect representative development notes for each major theme.

## Required artifact

- schema: `gan2026.luna_prompt_variants_residual.v1`
- one panel row per source row with A/B/C raw/final labels, correctness,
  themes, evidence, and transitions
- summary counts for patterns, themes, slices, and mechanism buckets
- stratified exemplars with evidence and rationales

## Stop rule

- Answer: name the dominant shared residual mechanisms and the distinctive
  B/C error profiles with row-backed examples.
- Negative: only if the saved traces cannot support matched A/B/C comparison.
- Reject: any use of sealed `test450` rows or any change to scoring/repair.

## Claim boundary

Development mechanism evidence for Luna A/B/C on `validation750`. Theme labels
are analyst heuristics over saved traces, not a new gold taxonomy. This does
not authorize holdout inspection, prompt promotion into the frozen six-model
panel, or clinical validation claims.
