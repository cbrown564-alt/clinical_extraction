# ExECTv2 Cross-Model Reliability Scorecard

Date: 2026-06-22

Computed refresh: 2026-06-24

Scope: Phase 1 no-call scorecard for the ExECTv2 final comparison set. This
extends the v08 reliability language to completed DeepSeek/Qwen dev140
diagnostics without claiming that calibration, abstention, robustness, or
consistency are complete. The 2026-06-24 refresh adds computed dev140 reliability
tables from saved artifacts only; it does not inspect full-200 or holdout rows.

## Evidence Set

| Role | Candidate | Surface | Overall F1 | Decision |
| --- | --- | --- | ---: | --- |
| Performance control | `exectv2_holistic_finding_assembly_v08_dev140` | dev140 `headline_target` | 0.9152 | Control |
| Simplicity control | `exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140` | dev140 `headline_target` | 0.9059 | Control |
| Hosted non-GPT comparator | `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140` | dev140 `headline_target` | 0.9174 | Diagnostic, do not promote |
| Local-model comparator | `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140` | dev140 `headline_target` | 0.9001 | Diagnostic, do not promote |

## Latest-Run Check

The latest DeepSeek/Qwen rows are tracked by surface, not blended:

| Surface | Latest DeepSeek | Latest Qwen | Policy |
| --- | --- | --- | --- |
| Rich-schema reliability scorecard | `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140` (`0.9174`) | `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140` (`0.9001`) | Retain as same-surface comparators. |
| Active LLM-only de-duplicated facts | `decision_table_sf_inv` DeepSeek chat dev140 (`0.745` clinical-headline F1) | `decision_table_sf_inv` Qwen 3.6 side-server dev140 (`0.697` computed, reported as `0.694` in Phase 6 closeout) | Report separately; different claim surface. |

## Ten-Dimension Scorecard

Coverage score: `5` = strong current evidence; `1` = absent or only anecdotal.

| # | Dimension | Coverage | Current evidence | Gap to close |
| --- | --- | :---: | --- | --- |
| 1 | Task correctness | 4/5 | v08 clears all four dev140 families above `0.900`; v09 remains above `0.900` overall; final DeepSeek/Qwen dev140 diagnostics reach `0.9174` and `0.9001` overall. DeepSeek still misses Diagnosis parity (`0.8898`), Qwen misses Diagnosis and SF parity, and both remain `do-not-promote`. | Freeze a full-200/holdout protocol before any broader claim. |
| 2 | Factuality and over-inference | 4/5 | Assembly rows preserve exact evidence, FP/FN counts, residual ledgers, and changed-row categories. The refresh computes per-family over-emission and miss rates for all four selected rows; Qwen Diagnosis remains the clearest pressure point (`0.1525` over-emission, `0.1347` miss rate). | Convert high-burden review triggers into lower-burden operating points. |
| 3 | Faithfulness / exact evidence | 5/5 | v08/v09/DeepSeek/Qwen selected assemblies report exact evidence rate `1.0000` on scored mentions. Source runs show evidence-validity differences: DeepSeek v0.9.10 source `0.9857`, Qwen compact source `0.9541`. JSONL rows preserve evidence text, component ownership, lane, and provenance. | Preserve exact-evidence gate for every refreshed source artifact. |
| 4 | Calibration | 3/5 | A no-call external confidence proxy now bins `1,706` dev140 candidate-family cells using family, evidence validity, source-to-final changes, confidence labels, and deterministic action burden. Expected calibration error is `0.1456`; bins are diagnostic and not yet an accepted confidence model. | Improve monotonicity and reduce circular family priors before any calibration claim. |
| 5 | Abstention / review routing | 4/5 | Predeclared triggers now produce a burden/benefit table: `1,605/1,706` reviewed cells (`0.9408` burden), catching `379/426` error cells (`0.8897`) but with `1,226` false-alarm cells. A dev-tuned lower-burden candidate reviews `1,291/1,706` cells (`0.7567`) while catching `342/426` error cells (`0.8028`). | Validate the operating point under a frozen audit protocol before promotion. |
| 6 | Robustness | 4/5 | v08/v09 lineage rejects naive single-GPT/dictionary simplification and noisy union/intersection swaps; rich-schema DeepSeek/Qwen diagnostics strengthen cross-model transfer evidence. Latest Phase 6 LLM-only runs are also reported separately: DeepSeek `0.745`, Qwen `0.697` computed clinical-headline F1. | Add perturbation or hard-slice panels before making robustness claims. |
| 7 | Consistency | 4/5 | Assembly replay is deterministic from saved artifacts. The refresh adds cross-model dev140 agreement over shared `letter_id`: pairwise clinical-headline mean Jaccard `0.8852`, exact family-cell agreement `0.8000`. There is still no cross-seed same-prompt panel. | Run predeclared same-prompt resampling only if needed for the paper. |
| 8 | Safety and compliance | 4/5 | Dev/test boundaries are documented; deterministic semantic repairs have provenance; full-200/holdout row-level inspection is blocked without protocol. | Add automated ExECTv2 holdout/full-200 inspection guards mirroring Gan. |
| 9 | Family parity | 5/5 | v08 clears all target families; final non-GPT dev140 rows expose uneven family portability with residual subtype tables. DeepSeek misses only Diagnosis (`0.8898`) on the rich-schema headline; Qwen misses Diagnosis (`0.8563`) and SF (`0.8908`) despite strong Rx/Inv. | Use subtype parity to target architecture work; do not promote non-GPT rows from aggregate F1 alone. |
| 10 | Operational reliability | 4/5 for replay, 3/5 source runs | v08/v09 are no-call replayable. DeepSeek source and assembly diagnostics are clean. Qwen source has ten parse/schema failures and the assembly reports ten parse/schema failures per family lens surface. | Keep source parse/call warnings separate from repaired assembly success, and define gates for future live runs. |

Mean coverage: approximately `4.1/5`. The strongest dimensions are faithfulness,
family parity instrumentation, and replayability. The main remaining weaknesses
are calibration quality, review burden, and lack of perturbation/same-prompt
panels.

## No-Call Metrics Available Now

| Metric | Current status |
| --- | --- |
| Exact evidence rate by model/family | Available from assembly JSON lane diagnostics. |
| Evidence-valid but wrong counts | Computed as `computed_reliability.family_error_table[].evidence_valid_error_count`. |
| Family-level miss and over-emission | Computed for all selected rows from `target_report.candidates[].headline_scores` and residual ledgers. |
| Cross-model agreement on dev140 | Built from shared dev140 `letter_id`: mean pairwise Jaccard `0.8852`, exact family-cell agreement `0.8000`. |
| Review triggers from provenance | Operationalized as diagnostic triggers plus operating-point scan; current high-recall burden is `0.9408`, and the lower-burden dev candidate is `0.7567` burden / `0.8028` catch. |
| Latest DeepSeek/Qwen surface check | Built into `computed_reliability.latest_run_check`; Phase 6 LLM-only runs are reported separately from rich-schema reliability comparators. |

## Residual Risk Register

| Family | Current strength | Residual risk |
| --- | --- | --- |
| Diagnosis | v08/v09 clear dev140; DeepSeek `0.8898` and Qwen `0.8563` remain below target | Assertion, hierarchy, and convention repairs are prediction-bearing and need explicit attribution. |
| SeizureFrequency | v08/v09 headline clears dev140; DeepSeek reaches `0.9017`; Qwen reaches `0.8908` | Active-rate fidelity remains weaker, especially Qwen `0.3618`. |
| Prescription | Strongest cross-model family | Current-vs-plan ambiguity and deterministic regimen repair must stay visible as semantic components; final non-GPT changed-row controls still fail. |
| Investigations | v08 clears; final DeepSeek `0.9658` and Qwen `0.9579` are strong | Result-state ambiguity and repair-mediated component ownership remain important, especially because Qwen changed-row controls fail. |

## Upgrade Plan By Weak Dimension

| Dimension | Next metric needed |
| --- | --- |
| Calibration | Better-calibrated risk proxy with monotone bins and lower ECE than `0.1456`. |
| Abstention / review routing | Frozen validation of the lower-burden candidate; current diagnostic trigger set reviews `94.08%` of eligible cells, while the dev-tuned candidate reviews `75.67%`. |
| Robustness | Frozen perturbation panel for current vs historical/future states, med plans, investigation result states, and diagnosis conventions. |
| Consistency | Same-prompt resampling panel, separated from deterministic assembly replay and cross-model agreement. |
| Family parity | Use the residual subtype table to predeclare targeted architecture work. |

## Final Refresh Status

- DeepSeek v0.9.16 dev140 and Qwen v0.9.22 dev140 are now the selected non-GPT
  diagnostic architecture rows.
- Earlier DeepSeek/Qwen dev25 rows remain path evidence, but are superseded in
  the final reliability evidence set.
- Do not add full-200 or holdout claims to this scorecard without a protocol
  that freezes scorer surface, row-inspection policy, and stop rule first.
