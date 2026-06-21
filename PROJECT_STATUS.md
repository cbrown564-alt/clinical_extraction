# Project Status

Last updated: 2026-06-21

## Active Objective

ExECTv2 Plan 11 targets exactly four indicators: `Diagnosis`,
`SeizureFrequency`, `Prescription`, and `Investigations`. The active goal is to
use the holistic finding-assembly architecture with GPT-4.1-mini-family
producers/lenses to push each dev140 clinical-headline family above `0.900`,
prioritizing Diagnosis first and keeping row-level error analysis plus ablations
after every major phase. This remains dev-only until a broader audit protocol is
predeclared.

## Current Read

Current control: v08 holistic assembly:
`docs/experiments/exectv2/key_entities/exectv2_holistic_finding_assembly_v08_prescription_phase1_error_analysis_20260621.md`.
v08 keeps Diagnosis v05, SF v06/v08, and Investigations v07 fixed, then replaces
Prescription with deterministic regimen repair v03. Official family headlines:
Diagnosis `0.9083`, SeizureFrequency `0.9053`, Prescription `0.9357`,
Investigations `0.9132`, overall `0.9152`. The renewed dev140 goal is achieved.

Key lineage: v0.42 default-quarantine baseline headline `0.7153`; v01 holistic
finding assembly `0.8006`; v02 explicit `focal epilepsy` heading recovery
`0.8038`; v03 convention cleanup `0.8130`; v04 convention aliases `0.8278`;
v05 residual benchmark repair `0.8576` with Diagnosis `0.9083`; v06 SF union
arbitration `0.8789` with SF `0.9053`; v07 Investigations arbitration `0.8873`
with Investigations `0.9132`; v08 Prescription repair `0.9152` with all four
families above `0.900`. All are dev-only component evidence, not benchmark/full-200/test claims.

2026-06-21 v09 simplification study: a single GPT structured pass (prompt v0.9) +
`standard_dictionary` translation layer does NOT clear 0.9 (dev140
`headline_target` `0.7552`; +deterministic prescription `0.7997`). The focused
producers did real work — Prescription recall, generic-epilepsy recall, SF
arbitration. Accepted the partial hybrid
`exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140` = `0.9059`
(focused Diagnosis + SF + deterministic Prescription, GPT-only prompt-owned
Investigations), which drops v08's Investigations verifier + pending-test
arbitration stack at `-0.006` overall. Study:
`docs/experiments/exectv2/key_entities/exectv2_v09_single_gpt_simplification_study_dev140_20260621.md`.

## Active Priorities

1. Treat v08 as the achieved dev140 control and use the reliability scorecard for
   any next-step governance.
2. Keep claims attribution-clean across `rules_only`, `llm_first`, and
   `hybrid`; semantic deterministic lens behavior is prediction-bearing.
3. Do not restore quarantined projection families by default on single-letter
   benchmark nudges.
4. Treat v0.21-v0.42 "cleared four" artifacts as qualified dev evidence on a
   lenient key, not benchmark claims.
5. Any full-200 or locked-test-facing ExECTv2 audit still needs
   benchmark-beating dev evidence and a predeclared aggregate readout.

## Work Board

### Now

- Treat v08 as the current holistic assembly control.
- Use `docs/experiments/exectv2/reliability/exectv2_reliability_scorecard_and_phased_plan_2026-06-21.md`
  as the next-step plan.

### Next

- If moving beyond dev140, predeclare the exact aggregate/full-200 readout,
  scorer surfaces, runtime/model, stop rule, and no-test-inspection boundary.
### Blocked

- Gan holdout-facing reruns, row-level test analysis, and post-test tuning need
  explicit authorization plus a frozen protocol.
- New ExECTv2 full-200 audits need benchmark-beating dev evidence and a
  predeclared aggregate readout.

### Done Recently

- 2026-06-21: Completed the Gan 2026 Qwen v0.6 `hybrid_structured_events`
  repairfix frozen aggregate test450 audit. After technical recovery of
  call-failed rows, Purist micro-F1 proxy is `0.8133` (366/450), Pragmatic is
  `0.8467` (381/450), with zero call failures and no row-level test inspection
  for development. Claim as a hybrid repairfix holdout result, not an
  attribution-clean LLM-first result.
- 2026-06-21: Completed ExECTv2 v08 all-four clearance and reliability scorecard.
  Official family F1s: Diagnosis `0.9083`, SF `0.9053`, Prescription `0.9357`,
  Investigations `0.9132`; overall `0.9152`.
- 2026-06-21: Completed ExECTv2 Investigations Phase 1 / v07 pending-test
  arbitration. Official Investigations assembly headline is now `0.9132`.
- 2026-06-21: Completed ExECTv2 SeizureFrequency Phase 1 / v06 union
  arbitration. Official SF assembly headline is now `0.9053`; the direct SF
  artifact scores `0.9263`. Active-rate fidelity remains `0.5969`.
- 2026-06-21: Completed ExECTv2 Diagnosis Phase 4 / v05 residual benchmark
  repair. Diagnosis headline is now `0.9083` on the declared concept-only
  target surface; strict Diagnosis ledger is `0.8127`.
- 2026-06-21: Completed ExECTv2 Diagnosis Phase 1-3 through v04: rejected
  direct GPT-4.1-mini panel variants, accepted explicit `focal epilepsy`
  heading recovery, narrow convention cleanup, and benchmark-format alias
  repair; Diagnosis headline is now `0.8301`.
- 2026-06-20: Built and ran the no-call focused-lane component-evidence
  replay/report harness. It aligns frozen dev140 rows, preserves lane
  provenance, emits JSONL/JSON/MD artifacts, reports the declared score ladder
  and changed-row accounting, and passes the dev-only promotion gates.
- 2026-06-20: Completed the v0.42 local-Qwen dev140 default-quarantine run and
  same-raw family ablation; no quarantined projection family returned to the
  default prediction pipeline.

## Guardrails

- Do not inspect Gan `test450` row-level failures, rationales, evidence,
  selected events, or transitions for development.
- Do not inspect ExECTv2 holdout/full-200 row-level failures for development
  without explicit authorization and a frozen protocol.
- Keep deterministic certainty/CUI/format repairs as controlled projection
  layers, and record semantic add/drop/replace/select actions as
  prediction-bearing provenance.
