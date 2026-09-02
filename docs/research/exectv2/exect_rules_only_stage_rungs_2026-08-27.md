# ExECT rules-only stage rungs (recognise / encode / select stops)

Date: 2026-08-27
Status: complete; rungs promoted to paper artifacts 2026-08-27
Protocol: [stage rungs protocol](exect_rules_only_stage_rungs_protocol_2026-08-27.md)
Program: `run_letter_three_stage(ACCEPTED_THREE_STAGE_CONFIG)` (frozen; unchanged)
Artifacts:
[`experiments/exect_rules_only_stage_rungs_20260827/dev140_summary.json`](../../../experiments/exect_rules_only_stage_rungs_20260827/dev140_summary.json),
[`experiments/exect_rules_only_stage_rungs_test60_aggregate_20260827.json`](../../../experiments/exect_rules_only_stage_rungs_test60_aggregate_20260827.json)
Runners: `scripts/measure_exect_rules_only_stage_rungs_dev140.py`,
`scripts/measure_exect_rules_only_stage_rungs_test60_aggregate.py`

## Answer

The rules row now has measured recognise / encode / select stops on
both splits, read from one pass of the frozen promoted program via
`three_stage_stop_mentions`. The cited select stops reproduce exactly
(**0.9167** dev140, **0.8018** test60), so no promoted headline moved.

| Stop | dev140 F1 (P / R) | test60 F1 (P / R) |
| --- | --- | --- |
| recognise | 0.9012 (0.9078 / 0.8947) | 0.7934 (0.8376 / 0.7536) |
| encode | 0.9150 (0.9222 / 0.9079) | 0.7994 (0.8439 / 0.7593) |
| select | 0.9167 (0.9256 / 0.9079) | 0.8018 (0.8494 / 0.7593) |

## Gates and predeclared invariants (all held)

- Select-stop mentions are identical to `run_letter` output on all 140
  development letters and all 59 test letters (checked in-run).
- The encode stop changed no non-Diagnosis mention on any letter.
- Select stop reproduces the promoted rows to 4 decimal places.

## Stage mechanics (aggregate)

Encode moves only Diagnosis (standard-name encode): Diagnosis F1
0.8413 → 0.8765 on `dev140`, 0.8333 → 0.8478 on `test60`. Select moves
only SeizureFrequency (the two accepted SF drops): SF F1 0.8563 →
0.8640 on `dev140`, 0.6043 → 0.6131 on `test60`. Prescription and
Investigations are constant across all three stops on both splits.
D1/D2/D3 live at recognise, so their effect is inside the recognise
rung, as in the LLM cells where prompt-side effects sit inside the
extract rung.

## Promotion

- `paper_experiments/exect/exect_rules/dev140.json` and `test60.json`
  carry `stage_rungs` blocks; cited fields unchanged.
- The five-cell grid rules row `ablation` now shows measured stops
  (0.7934 / 0.7994 vs select 0.8018) instead of copies of the select
  score (`five_cell.py::_exect_rules_stage`; regenerated
  `generated.json` and curated `comparison.json` updated).
- `scripts/refresh_exect_rung_rules_only_reference.py` refreshed the
  stale `rungs.rules_only` reference in all eight
  `paper_experiments/exect/rungs/*/{dev140,test60}/comparison.json`
  files (retired 0.9042 / 0.7937 headline numbers → promoted 0.9167 /
  0.8018 inventory numbers).
- The rules-base fingerprint fixture
  (`tests/fixtures/exectv2_rules_base_264237bd_fingerprint.json`) was
  rolled for the three-stage promotion, which had left the firewall
  test red; the retune-era hashes moved into `superseded_oracles` with
  the reconstruction evidence.

## Claim boundary

Stage-stop instrumentation of the already-promoted rules program.
Recognise and encode rungs are ablation views of the cited select
stop, not new methods and not clinical validation. `test60` rungs are
aggregate-only; sealed row outputs live under
`scratch/holdout/exect_rules_only_stage_rungs_test60_20260827/` and
were not inspected.
