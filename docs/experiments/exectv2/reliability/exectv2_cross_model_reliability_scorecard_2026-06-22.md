# ExECTv2 Cross-Model Reliability Scorecard

Date: 2026-06-22

Scope: Phase 0 no-call scorecard for the ExECTv2 final comparison set. This
extends the v08 reliability language to cross-model diagnostics without claiming
that calibration, abstention, robustness, or consistency are complete.

## Evidence Set

| Role | Candidate | Surface | Overall F1 | Decision |
| --- | --- | --- | ---: | --- |
| Performance control | `exectv2_holistic_finding_assembly_v08_dev140` | dev140 `headline_target` | 0.9152 | Control |
| Simplicity control | `exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140` | dev140 `headline_target` | 0.9059 | Control |
| DeepSeek comparator | `exectv2_holistic_finding_assembly_v097_deepseek_dev25` | dev25 `headline_target` | 0.8707 | Diagnostic |
| Qwen best no-call reparse | `exectv2_holistic_finding_assembly_v096_schema_repair_qwen_reparse_dev25` | dev25 `headline_target` | 0.8082 | Diagnostic |
| Qwen latest compact completion | `exectv2_holistic_finding_assembly_v097_qwencompact_dictrepair_dev25` | dev25 `headline_target` | 0.7995 | Diagnostic |

## Ten-Dimension Scorecard

Coverage score: `5` = strong current evidence; `1` = absent or only anecdotal.

| # | Dimension | Coverage | Current evidence | Gap to close |
| --- | --- | :---: | --- | --- |
| 1 | Task correctness | 4/5 | v08 clears all four dev140 families above `0.900`; v09 remains above `0.900` overall; DeepSeek/Qwen diagnostics show portability limits. | Freeze a full-200/holdout protocol before any broader claim. |
| 2 | Factuality and over-inference | 3/5 | Assembly rows preserve exact evidence, FP/FN counts, residual ledgers, and changed-row categories. DeepSeek/Qwen FP patterns are visible but not yet reduced to family-level over-inference rates. | Build per-family over-emission and miss-rate tables for all selected rows. |
| 3 | Faithfulness / exact evidence | 5/5 | v08/v09/DeepSeek/Qwen selected assemblies report exact evidence rate `1.0000` on scored mentions. JSONL rows preserve evidence text, component ownership, lane, and provenance. | Preserve exact-evidence gate for every refreshed source artifact. |
| 4 | Calibration | 2/5 | Scores and residuals exist, but no calibrated confidence model or reliability curve exists for ExECTv2. | Build no-call confidence proxies from provenance, family, evidence shape, and residual class; validate on dev only. |
| 5 | Abstention / review routing | 2/5 | No accepted abstention policy exists. Residual families identify plausible triggers but are not operationalized. | Predeclare review triggers for Diagnosis assertion/hierarchy, SF active-rate fidelity, Prescription current-vs-plan ambiguity, and Investigations result-state ambiguity. |
| 6 | Robustness | 3/5 | v08/v09 lineage rejects naive single-GPT/dictionary simplification and noisy union/intersection swaps; DeepSeek/Qwen show cross-model sensitivity. | Add perturbation or hard-slice panels before making robustness claims. |
| 7 | Consistency | 3/5 | Assembly replay is deterministic from saved artifacts. There is no cross-seed or same-prompt resampling panel for the ExECTv2 selected rows. | Run predeclared same-prompt or same-artifact consistency panels only if needed for the paper. |
| 8 | Safety and compliance | 4/5 | Dev/test boundaries are documented; deterministic semantic repairs have provenance; full-200/holdout row-level inspection is blocked without protocol. | Add automated ExECTv2 holdout/full-200 inspection guards mirroring Gan. |
| 9 | Family parity | 4/5 for v08, 2/5 cross-model | v08 clears all target families; non-GPT diagnostics expose uneven family portability, especially Diagnosis and SF. | Convert residual ledgers to subtype parity metrics within each family. |
| 10 | Operational reliability | 4/5 for replay, 3/5 source runs | v08/v09 are no-call replayable. DeepSeek assembly diagnostics are clean; Qwen compact has parse/schema failures on the assembly lens surface. | Keep source parse/call warnings separate from repaired assembly success, and define gates for future live runs. |

Mean coverage: approximately `3.4/5`. The strongest dimensions are faithfulness,
task correctness for v08, and replayability. The weakest dimensions are
calibration and review routing.

## No-Call Metrics Available Now

| Metric | Current status |
| --- | --- |
| Exact evidence rate by model/family | Available from assembly JSON lane diagnostics. |
| Evidence-valid but wrong counts | Available through FP/FN and residual ledgers, but not yet normalized into a single table for every selected row. |
| Family-level miss and over-emission | Available in `target_report.candidates[].error_analysis.per_indicator`; needs consolidation. |
| Cross-model agreement on dev25 | Feasible because DeepSeek and Qwen dev25 rows share `letter_id`, but not built in Phase 0. |
| Review triggers from provenance | Feasible from component owner, source lane, evidence validity, and residual family tags; not operationalized. |

## Residual Risk Register

| Family | Current strength | Residual risk |
| --- | --- | --- |
| Diagnosis | v08/v09 clear dev140; DeepSeek/Qwen below target | Assertion, hierarchy, and convention repairs are prediction-bearing and need explicit attribution. |
| SeizureFrequency | v08/v09 headline clears dev140 | Active-rate fidelity remains weaker; non-GPT transfer is poor. |
| Prescription | Strongest cross-model family | Current-vs-plan ambiguity and deterministic regimen repair must stay visible as semantic components. |
| Investigations | v08 clears; DeepSeek strong; Qwen mixed | Result-state ambiguity and instability under Qwen compact remain. |

## Upgrade Plan By Weak Dimension

| Dimension | Next metric needed |
| --- | --- |
| Calibration | Family-aware confidence/risk proxy with reliability bins over dev rows. |
| Abstention / review routing | Predeclared route triggers and burden/benefit table: reviewed rows, caught errors, missed errors. |
| Robustness | Frozen perturbation panel for current vs historical/future states, med plans, investigation result states, and diagnosis conventions. |
| Consistency | Same-prompt resampling or same-artifact replay stability table, separated from deterministic assembly replay. |
| Family parity | Residual subtype table by family and model, including FP, FN, evidence-valid-but-wrong, and component owner. |

## Pending Refresh

- Replace or append DeepSeek v0.9.8 only after updating the cross-model report
  and artifact index.
- Keep Qwen v0.9.6 and v0.9.7 rows separate: one is the best no-call reparse,
  the other is the latest compact completion.
- Do not add full-200 or holdout claims to this scorecard without a protocol
  that freezes scorer surface, row-inspection policy, and stop rule first.

