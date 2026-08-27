# ExECT rules-only three-stage `test60` aggregate replay

Date: 2026-08-27
Status: complete; promoted to paper artifacts 2026-08-27
Protocol: [test60 aggregate protocol](exect_rules_only_three_stage_test60_aggregate_protocol_2026-08-27.md)
Development candidate: [three-stage reconstruction](exect_rules_only_three_stage_reconstruction_2026-08-27.md)
Artifact: [`experiments/exect_rules_only_three_stage_test60_aggregate_20260827.json`](../../../experiments/exect_rules_only_three_stage_test60_aggregate_20260827.json)

## Answer

One aggregate-only holdout replay of frozen `ACCEPTED_THREE_STAGE_CONFIG`
raises 4-family inventory micro F1 from **0.7892 to 0.8018** (+0.0126)
versus the same-run `run_letter_retune_stack` comparator (59 letters, zero model
calls). The superseded five-cell rules row was **0.7725**; the cited
row is now **0.8018** in `paper_experiments/` and the five-cell grid.
The retune-stack comparator replays at **0.7892** on this split.

Predeclared family expectations are met: Diagnosis P/R both rise
(F1 **0.8231 → 0.8478**, +0.0247); SeizureFrequency stays the binding
weakness (F1 **0.6043 → 0.6131**, +0.0088, recall unchanged at
**0.5676**); Prescription and Investigations are unchanged. Overall F1
remains well below Gemini cell 3 **0.8674**.

## Gate A

`scripts/measure_exect_rules_only_three_stage_dev140.py` on current HEAD:
comparator **0.8949**, candidate **0.9167**, zero comparator-exact
regressions. Passed.

## Aggregate results (inventory F1)

| Arm | Overall F1 | P | R |
| --- | ---: | ---: | ---: |
| Comparator (`run_letter`) | 0.7892 | 0.8317 | 0.7507 |
| Candidate (`ACCEPTED_THREE_STAGE_CONFIG`) | **0.8018** | 0.8494 | 0.7593 |
| Delta (candidate − comparator) | **+0.0126** | +0.0177 | +0.0086 |

| Family | Comparator F1 | Candidate F1 | ΔF1 | Predeclared band |
| --- | ---: | ---: | ---: | --- |
| Diagnosis | 0.8231 | 0.8478 | +0.0247 | ≥ +0.02 — met |
| SeizureFrequency | 0.6043 | 0.6131 | +0.0088 | ≤ +0.03, stay &lt; 0.70 — met |
| Prescription | 0.8395 | 0.8395 | 0.0000 | neutral — met |
| Investigations | 0.8837 | 0.8837 | 0.0000 | neutral — met |

Cell 3 reference (same split, different program): overall **0.8674**;
SeizureFrequency **0.8082** with recall **0.7973**.

## Read-through (predeclared framing)

The reconstruction **partially validates** on holdout: Diagnosis
service-context exclusion and related Select moves transfer; the
method-comparison gap vs cell 3 is **not** closed. SeizureFrequency
remains the headline weakness (candidate F1 **0.6131**). A Diagnosis-only
lift does not change the paper story about rules vs LLM recognise on
holdout.

No holdout rows were inspected. Sealed predictions:
`scratch/holdout/exect_rules_only_three_stage_test60_20260827/`.

## Claim boundary

Aggregate holdout evidence for the promoted rules program. Not
clinical validation. Cited five-cell rules row is **0.8018**.
