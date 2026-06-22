# ExECTv2 Cross-Model Reliability Scorecard

Date: 2026-06-22

Scope: Phase 0 no-call scorecard for the ExECTv2 final comparison set. This
extends the v08 reliability language to completed DeepSeek/Qwen dev140
diagnostics without claiming that calibration, abstention, robustness, or
consistency are complete.

## Evidence Set

| Role | Candidate | Surface | Overall F1 | Decision |
| --- | --- | --- | ---: | --- |
| Performance control | `exectv2_holistic_finding_assembly_v08_dev140` | dev140 `headline_target` | 0.9152 | Control |
| Simplicity control | `exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140` | dev140 `headline_target` | 0.9059 | Control |
| Hosted non-GPT comparator | `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140` | dev140 `headline_target` | 0.9010 | Diagnostic, do not promote |
| Local-model comparator | `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140` | dev140 `headline_target` | 0.9001 | Diagnostic, do not promote |

## Ten-Dimension Scorecard

Coverage score: `5` = strong current evidence; `1` = absent or only anecdotal.

| # | Dimension | Coverage | Current evidence | Gap to close |
| --- | --- | :---: | --- | --- |
| 1 | Task correctness | 4/5 | v08 clears all four dev140 families above `0.900`; v09 remains above `0.900` overall; final DeepSeek/Qwen dev140 diagnostics reach `0.9010` and `0.9001` overall but miss family/parity gates and remain `do-not-promote`. | Freeze a full-200/holdout protocol before any broader claim. |
| 2 | Factuality and over-inference | 3/5 | Assembly rows preserve exact evidence, FP/FN counts, residual ledgers, and changed-row categories. Final DeepSeek/Qwen dev140 reports include changed-row controls and error ledgers, but over-inference rates are not yet normalized across all rows. | Build per-family over-emission and miss-rate tables for all selected rows. |
| 3 | Faithfulness / exact evidence | 5/5 | v08/v09/DeepSeek/Qwen selected assemblies report exact evidence rate `1.0000` on scored mentions. Source runs show evidence-validity differences: DeepSeek v0.9.10 source `0.9857`, Qwen compact source `0.9541`. JSONL rows preserve evidence text, component ownership, lane, and provenance. | Preserve exact-evidence gate for every refreshed source artifact. |
| 4 | Calibration | 2/5 | Scores and residuals exist, but no calibrated confidence model or reliability curve exists for ExECTv2. | Build no-call confidence proxies from provenance, family, evidence shape, and residual class; validate on dev only. |
| 5 | Abstention / review routing | 2/5 | No accepted abstention policy exists. Residual families identify plausible triggers but are not operationalized. | Predeclare review triggers for Diagnosis assertion/hierarchy, SF active-rate fidelity, Prescription current-vs-plan ambiguity, and Investigations result-state ambiguity. |
| 6 | Robustness | 3/5 | v08/v09 lineage rejects naive single-GPT/dictionary simplification and noisy union/intersection swaps; final DeepSeek/Qwen dev140 diagnostics strengthen cross-model transfer evidence while exposing persistent Diagnosis/SF sensitivity. | Add perturbation or hard-slice panels before making robustness claims. |
| 7 | Consistency | 3/5 | Assembly replay is deterministic from saved artifacts. There is no cross-seed or same-prompt resampling panel for the ExECTv2 selected rows. | Run predeclared same-prompt or same-artifact consistency panels only if needed for the paper. |
| 8 | Safety and compliance | 4/5 | Dev/test boundaries are documented; deterministic semantic repairs have provenance; full-200/holdout row-level inspection is blocked without protocol. | Add automated ExECTv2 holdout/full-200 inspection guards mirroring Gan. |
| 9 | Family parity | 4/5 for v08, 3/5 cross-model | v08 clears all target families; final non-GPT dev140 rows expose uneven family portability. DeepSeek misses Dx/SF targets; Qwen misses Dx and active-rate fidelity despite strong Inv/Rx. | Convert residual ledgers to subtype parity metrics within each family. |
| 10 | Operational reliability | 4/5 for replay, 3/5 source runs | v08/v09 are no-call replayable. DeepSeek source and assembly diagnostics are clean. Qwen source has ten parse/schema failures and the assembly reports ten parse/schema failures per family lens surface. | Keep source parse/call warnings separate from repaired assembly success, and define gates for future live runs. |

Mean coverage: approximately `3.5/5`. The strongest dimensions are faithfulness,
task correctness for v08, and replayability. The weakest dimensions are
calibration and review routing.

## No-Call Metrics Available Now

| Metric | Current status |
| --- | --- |
| Exact evidence rate by model/family | Available from assembly JSON lane diagnostics. |
| Evidence-valid but wrong counts | Available through FP/FN and residual ledgers, but not yet normalized into a single table for every selected row. |
| Family-level miss and over-emission | Available in `target_report.candidates[].error_analysis.per_indicator`; needs consolidation. |
| Cross-model agreement on dev140 | Feasible because v08, v09, DeepSeek v0.9.16, and Qwen v0.9.22 share dev140 `letter_id`, but not built in Phase 0. |
| Review triggers from provenance | Feasible from component owner, source lane, evidence validity, and residual family tags; not operationalized. |

## Residual Risk Register

| Family | Current strength | Residual risk |
| --- | --- | --- |
| Diagnosis | v08/v09 clear dev140; DeepSeek `0.8828` and Qwen `0.8563` remain below target | Assertion, hierarchy, and convention repairs are prediction-bearing and need explicit attribution. |
| SeizureFrequency | v08/v09 headline clears dev140; Qwen reaches `0.8908` and DeepSeek `0.8675` | Active-rate fidelity remains weaker, especially Qwen `0.3618`. |
| Prescription | Strongest cross-model family | Current-vs-plan ambiguity and deterministic regimen repair must stay visible as semantic components; final non-GPT changed-row controls still fail. |
| Investigations | v08 clears; final DeepSeek `0.9231` and Qwen `0.9579` are strong | Result-state ambiguity and repair-mediated component ownership remain important, especially because Qwen changed-row controls fail. |

## Upgrade Plan By Weak Dimension

| Dimension | Next metric needed |
| --- | --- |
| Calibration | Family-aware confidence/risk proxy with reliability bins over dev rows. |
| Abstention / review routing | Predeclared route triggers and burden/benefit table: reviewed rows, caught errors, missed errors. |
| Robustness | Frozen perturbation panel for current vs historical/future states, med plans, investigation result states, and diagnosis conventions. |
| Consistency | Same-prompt resampling or same-artifact replay stability table, separated from deterministic assembly replay. |
| Family parity | Residual subtype table by family and model, including FP, FN, evidence-valid-but-wrong, and component owner. |

## Final Refresh Status

- DeepSeek v0.9.16 dev140 and Qwen v0.9.22 dev140 are now the selected non-GPT
  diagnostic architecture rows.
- Earlier DeepSeek/Qwen dev25 rows remain path evidence, but are superseded in
  the final reliability evidence set.
- Do not add full-200 or holdout claims to this scorecard without a protocol
  that freezes scorer surface, row-inspection policy, and stop rule first.
