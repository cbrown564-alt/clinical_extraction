# Gan 2026 Fresh-Evidence Reasoner

Date: 2026-06-15

This is a frozen aggregate-only V12 fresh-evidence holdout audit artifact.
The model may replace the GPT structured-event final only from exact raw-note evidence.

## Experiment Unit

- Work class: V12 fresh-evidence reasoner over saved structured events.
- Rows: 450
- Split: `test`, manifest `gan2026_split_v1`.
- Mode: `live`
- Model: `openai/gpt-4.1`
- Prompt version: `gan2026_fresh_evidence_reasoner_v0_6`
- JSONL artifact: `experiments\gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_6_safety_v0_9_2026-06-15.jsonl`

## Summary

- Prediction-bearing rows: 449
- Model calls attempted: 450
- Call failures: 0
- Parse/schema/label failures: 0
- Fresh-evidence replace actions: 157
- Evidence-gate fallbacks: 6
- Exact evidence substrings: 423
- V0 Purist: 364/450
- V0 Pragmatic: 381/450
- Raw model Purist: 349/450
- Raw model Pragmatic: 357/450
- Format-only Purist: 349/450
- Format-only Pragmatic: 357/450
- Final Purist: 351/450
- Final Pragmatic: 362/450
- Net Purist gain vs V0: -14
- Changed-label precision vs V0: 0.2205
- Actions: `{'keep_original_structured_event_final': 293, 'replace_with_fresh_evidence_final': 157}`
- Profiles: omitted from the test report to keep the first readout aggregate-only.

## Gate

- Status: `pass_contract_smoke`
- Interpretation: Contract smoke passes; evaluate against hard-slice gates next.

## Claim Boundary

frozen aggregate-only V12 test450 audit; first readout is aggregate Purist/Pragmatic and health metrics only; no row-level test inspection, post-test tuning, or benchmark-comparable claim without separate review

## Aggregate-Only Holdout Readout

Row-level test details are intentionally omitted from this Markdown report. Do not inspect the JSONL or row-level failures before starting a separately authorized validation-only follow-up cycle.
