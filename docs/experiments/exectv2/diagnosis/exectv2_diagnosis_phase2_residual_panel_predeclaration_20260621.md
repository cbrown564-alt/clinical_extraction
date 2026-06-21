# ExECTv2 Diagnosis Phase 2 Residual Panel Predeclaration

- Date: `2026-06-21`
- Split: `dev` only; no locked test-row inspection.
- Control: holistic finding assembly v02 (`exectv2_holistic_finding_assembly_v02_dev140_20260621.jsonl`).
- Target model: `openai/gpt-4.1-mini`.
- Target family: `Diagnosis`, currently the weakest key-entity family.

## Objective

Phase 2 tests whether a focused GPT-4.1-mini adjudicator can repair the v02 Diagnosis residual surface without broad precision loss. The intervention is diagnosis-only. Prescription, SeizureFrequency, and Investigations remain frozen during this phase.

## Residual Panel

Build a deterministic residual-enriched panel from the v02 strict clinical-recovery error ledger. Select 25-40 dev letters by round-robin across unresolved Diagnosis residual families:

- generic epilepsy misses and over-emissions
- tonic-clonic and generalized-tonic-clonic over-emissions
- focal-family misses, especially focal epilepsy and focal seizure concepts
- secondary-generalized and named seizure-type misses
- syndrome or structural/symptomatic epilepsy misses

The residual family labels may be used for panel construction and row-level error accounting. They must not be inserted as row-specific gold hints in the LLM prompt.

## Variants

### H2 Candidate Selector

The model receives only fixed candidate sources: current v02 Diagnosis mentions, verifier mentions, decomposer mentions, and diagnosis candidate spans. It may keep, reject, or edit candidate concepts when exact evidence supports the edit. It should not freely invent concepts outside candidate evidence.

Expected benefit: reduce v02 over-emission of generic epilepsy and tonic-clonic concepts while recovering decomposer-only specific diagnoses when candidates already exist.

Expected risk: recall remains capped when no candidate source contains the missing concept.

### H3 Direct Re-Reader

The model receives the note text, the current v02 mentions, and the same policy rules, but may emit new Diagnosis concepts from exact evidence in the note.

Expected benefit: recover missed specific diagnoses absent from candidate lists.

Expected risk: broader over-emission of seizure-type or historical diagnoses.

## Gates

For each variant, report:

- panel Diagnosis concept-assertion F1, precision, recall, TP, FP, FN
- panel delta against the v02 control on the same rows
- call failures, parse failures, evidence-invalid drops, evidence validity
- row-level changed decisions and residual-family movement

Promotion criteria for a subsequent full dev140 run:

- no call failures and no blocking parse failures on the panel
- evidence validity at least `0.98`
- net Diagnosis panel F1 improvement against v02
- no broad increase in generic epilepsy or tonic-clonic over-emission
- row-level wins are clinically plausible and attributable to exact evidence

## Claim Boundary

This is a dev-only diagnostic phase. A successful panel does not establish final reliability. It only authorizes a larger dev140 ablation of the winning policy under the holistic assembly architecture.
