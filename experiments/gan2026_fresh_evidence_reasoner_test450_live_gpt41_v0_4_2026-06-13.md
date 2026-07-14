# Gan 2026 Fresh-Evidence Reasoner

Date: 2026-06-14

This report records the fixed, aggregate-only V12 fresh-evidence holdout audit.
The model may replace the GPT structured-event final only from exact raw-note evidence.

## Experiment Unit

- Work class: V12 fresh-evidence reasoner over saved structured events.
- Rows: 450
- Split: `test`, manifest `gan2026_split_v1`.
- Mode: `live`
- Model: `openai/gpt-4.1`
- Prompt version: `gan2026_fresh_evidence_reasoner_v0_4`
- JSONL output: `experiments\gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_4_2026-06-13.jsonl`

## Summary

- Prediction-bearing rows: 450
- Model calls attempted: 450
- Call failures: 0
- Parse/schema/label failures: 0
- Fresh-evidence replace actions: 118
- Evidence-gate fallbacks: 9
- Exact evidence substrings: 423
- V0 Purist: 364/450
- V0 Pragmatic: 381/450
- Raw model Purist: 372/450
- Raw model Pragmatic: 387/450
- Format-only Purist: 372/450
- Format-only Pragmatic: 387/450
- Final Purist: 379/450
- Final Pragmatic: 394/450
- Net Purist gain vs V0: 13
- Changed-label precision vs V0: 0.3171
- Actions: `{'keep_original_structured_event_final': 332, 'replace_with_fresh_evidence_final': 118}`
- Profiles: omitted from the test report to keep the first readout aggregate-only.

## Check result

- Recorded status: `pass_contract_smoke`
- Interpretation at the time: the schema smoke check passed. Any hard-slice
  evaluation remained separate.

## Claim Boundary

This is an aggregate-only V12 `test450` audit. It reports Purist, Pragmatic,
and run-health totals only. It does not permit row-level test inspection or
post-test tuning. Any broader benchmark comparison requires separate review.

## Aggregate-Only Holdout Readout

Row-level test details are intentionally omitted from this Markdown report. Do not inspect the JSONL or row-level failures before starting a separately authorized validation-only follow-up cycle.
