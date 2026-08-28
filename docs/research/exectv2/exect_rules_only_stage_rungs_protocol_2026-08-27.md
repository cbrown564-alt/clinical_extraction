# Protocol: ExECT rules-only stage rungs (recognise / encode / select stops)

Date: 2026-08-27
Status: complete; see [stage rungs report](exect_rules_only_stage_rungs_2026-08-27.md)
Frozen program: `ACCEPTED_THREE_STAGE_CONFIG` in `orchestration/rules.py`
Context: [three-stage reconstruction](exect_rules_only_three_stage_reconstruction_2026-08-27.md),
[test60 aggregate replay](exect_rules_only_three_stage_test60_aggregate_2026-08-27.md)

## Primary question

What are the recognise-stop, encode-stop, and select-stop 4-family
inventory scores of the frozen promoted rules-only program on `dev140`
and `test60`, so the rules row can show distinct stage rungs the way
the LLM cells do?

This is pure instrumentation of a frozen program. No candidate is
under study, no configuration may change, and no acceptance decision
follows from the numbers. The select stop is the already-promoted
program; the other two stops are prior-stage views of the same run.

## Stage-stop definitions (fixed by the existing program)

All stops run `ACCEPTED_THREE_STAGE_CONFIG` components; each stop
reads the same single pass at a different point:

| Stop | Contents |
| --- | --- |
| recognise | Direct four-family mentions from the recognise ledger (accepted `RecogniseConfig`; deferred classes off, as promoted) |
| encode | Recognise output after per-family encode (`encode_families = {Diagnosis}`) |
| select | Full promoted program output (`comparison_projection`) |

Scorer: `clinical_inventory_unit_keys`, 4-family micro F1 plus per-family
P/R/F1. Zero model calls. No Compact/headline numbers.

## Predeclared expectations

- The select stop must reproduce the promoted rows exactly:
  **0.9167** on `dev140` and **0.8018** on `test60`. On `dev140` the
  select-stop mentions must be identical to `run_letter` output on all
  140 letters. Any mismatch stops the study (instrumentation defect);
  no promoted number changes.
- The encode stop may differ from the recognise stop only in the
  Diagnosis family. SeizureFrequency, Prescription, and Investigations
  must be identical between those two stops.
- The select stop should not lower precision versus the encode stop;
  accepted Select rules are drops plus Diagnosis keep/specificity
  moves.
- No expectation is placed on the magnitude of recognise-to-select
  deltas; they are descriptive.

## Data and inspection

| Item | Value |
| --- | --- |
| Development | `dev140` (140 letters), row policy `development_review_permitted` |
| Holdout | `test60` (59 letters, locked), row policy `aggregate_only` |
| Order | `dev140` first; `test60` only after the dev gate passes |
| Runs | One `test60` execution, three stops read from the same pass |

`test60` row-level stop outputs are sealed under
`scratch/holdout/exect_rules_only_stage_rungs_test60_20260827/` (path,
sha256, byte count only in the public artifact). The public artifact
contains aggregates only and is added to
`scripts/check_locked_aggregate_safety.py`.

## Code change

Minimal additive change: a public stage-stop reader on the existing
three-stage runner (no behavior change to `run_letter` or
`run_letter_three_stage`), pinned by a focused test that the select
stop equals `run_letter` output. Runner scripts:

- `scripts/measure_exect_rules_only_stage_rungs_dev140.py`
- `scripts/measure_exect_rules_only_stage_rungs_test60_aggregate.py`

Artifacts:

- `experiments/exect_rules_only_stage_rungs_20260827/dev140_summary.json`
- `experiments/exect_rules_only_stage_rungs_test60_aggregate_20260827.json`

## Promotion surface (after both measurements pass their gates)

1. Add `stage_rungs` blocks to
   `paper_experiments/exect/exect_rules/dev140.json` and `test60.json`.
   Cited select-stop numbers do not move.
2. The five-cell grid rules row `ablation.extract` / `ablation.encode`
   values become the measured recognise / encode stops instead of
   copies of the select score (`five_cell.py` + regenerated
   `generated.json`; curated `comparison.json` select values are
   untouched).
3. Refresh the stale `rungs.rules_only` reference in
   `paper_experiments/exect/rungs/*/{dev140,test60}/comparison.json`
   from the promoted `exect_rules` file (same derivation as
   `_comparison_summary`; currently shows the retired 0.7937 headline
   number).

## Claim boundary

Stage-stop instrumentation of the already-promoted rules program.
The cited select-stop rows (0.9167 dev / 0.8018 holdout) do not
change. Recognise/encode rungs are ablation views, not new methods
and not clinical validation. No holdout row inspection.
