# Protocol: illustrated examples for hard-slice error modes

Date: 2026-08-06  
Status: complete; no-call development illustration  
Parent: [hard-slice error modes](six_model_hard_slice_error_modes_2026-08-06.md)

## Primary question

Can every primary error mode named in the hard-slice study be illustrated with
concrete development examples (ids, gold, prediction, and saved evidence or
mention attributes)?

## Method

1. Reuse the mode classifiers and retained prediction sources from the parent
   study.
2. For each mode in each in-scope slice/surface, select up to two examples.
3. Prefer consensus-wrong ids, then stronger hosted models, then unique ids.
4. Attach only saved selected-evidence spans or SF mention attributes—not full
   clinical notes.
5. Also illustrate model-boundary-only modes that the parent report treats as
   diagnostic (`incomplete_cluster_grammar`, `false_cluster_structure`,
   `other_malformed_or_unparsed`).

## Outputs

- Machine artifact with the selected examples.
- Narrative report with one short illustration block per mode.

## Claim boundary

Development illustration only. Evidence strings are model-selected spans from
retained artifacts. Not clinical validation, not holdout inspection, not a
license to tune from these rows without a new predeclared study.
