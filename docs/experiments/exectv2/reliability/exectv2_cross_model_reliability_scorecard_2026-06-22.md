# ExECTv2 Cross-Model Reliability Scorecard

Date: 2026-06-22

Computed refresh: 2026-06-25

Scope: Phase 1 no-call scorecard for the ExECTv2 final comparison set. This
extends the v08 reliability language to completed DeepSeek/Qwen dev140
diagnostics without claiming that low-burden abstention is complete. The
2026-06-25 refresh adds computed dev140 reliability tables from saved artifacts,
aggregate-only full-200 calibration and robustness validation audits, a completed
review-routing validation readout, a deterministic robustness preflight, and
selected GPT-4.1-mini 2-call no-SF-adjudicator self-consistency panels; it does
not emit full-200 row-level details or inspect holdout rows. The same-core
model-swap freeze is now complete on dev140 for GPT-4.1-mini, DeepSeek chat,
and Qwen 3.6 35B. Older non-GPT rows remain historical diagnostics rather than
final model-swap evidence; the completed same-core comparison is dev140
evidence with an operational-stability caveat because Qwen produced one call
failure and twelve parse/schema failures.

## Evidence Set

| Role | Candidate | Surface | Overall F1 | Decision |
| --- | --- | --- | ---: | --- |
| Performance control | `exectv2_holistic_finding_assembly_v08_dev140` | dev140 `headline_target` | 0.9152 | Control |
| Simplicity control | `exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140` | dev140 `headline_target` | 0.9059 | Control |
| Hosted non-GPT comparator | `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140` | dev140 `headline_target` | 0.9174 | Diagnostic, do not promote |
| Local-model comparator | `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140` | dev140 `headline_target` | 0.9001 | Diagnostic, do not promote |
| Same-core GPT reference | `exectv2_2call_no_sf_adjudicator_gpt41mini_dev140` | dev140 `clinical_headline` | 0.8396 | Frozen-core reference |
| Same-core DeepSeek swap | `exectv2_2call_no_sf_adjudicator_deepseek_dev140` | dev140 `clinical_headline` | 0.8596 | Complete; operational caveat: 1 parse/schema failure |
| Same-core Qwen swap | `exectv2_2call_no_sf_adjudicator_qwen36_dev140` | dev140 `clinical_headline` | 0.8018 | Complete; operational caveat: 1 call failure and 12 parse/schema failures |

## Latest-Run Check

The latest DeepSeek/Qwen rows are tracked by surface, not blended:

| Surface | Latest DeepSeek | Latest Qwen | Policy |
| --- | --- | --- | --- |
| Rich-schema reliability scorecard | `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140` (`0.9174`) | `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140` (`0.9001`) | Retain as same-surface comparators. |
| Active LLM-only de-duplicated facts | `decision_table_sf_inv` DeepSeek chat dev140 (`0.745` clinical-headline F1) | `decision_table_sf_inv` Qwen 3.6 side-server dev140 (`0.697` computed, reported as `0.694` in Phase 6 closeout) | Report separately; different claim surface. |
| Frozen same-core model swap | `exectv2_2call_no_sf_adjudicator_deepseek_dev140` (`0.8596`) | `exectv2_2call_no_sf_adjudicator_qwen36_dev140` (`0.8018`) | Use as completed dev140 same-core model evidence with the operational-stability caveat from the readiness artifact; do not advance to full-200 without a fresh aggregate-only predeclaration. |

## Ten-Dimension Scorecard

Coverage score: `5` = strong current evidence; `1` = absent or only anecdotal.

| # | Dimension | Coverage | Current evidence | Gap to close |
| --- | --- | :---: | --- | --- |
| 1 | Task correctness | 4/5 | v08 clears all four dev140 families above `0.900`; v09 remains above `0.900` overall; historical DeepSeek/Qwen dev140 diagnostics reach `0.9174` and `0.9001` overall but are not same-core model swaps. The frozen same-core dev140 comparison is complete: DeepSeek `0.8596`, GPT-4.1-mini `0.8396`, and Qwen `0.8018` overall clinical-headline F1. DeepSeek leads overall, GPT remains cleaner operationally, and Qwen lags most in SeizureFrequency (`0.6919`). | Record the dev140 model-swap result with operational caveats; review Qwen output-contract failures before any full-200 predeclaration. |
| 2 | Factuality and over-inference | 4/5 | Assembly rows preserve exact evidence, FP/FN counts, residual ledgers, and changed-row categories. The refresh computes per-family over-emission and miss rates for all four selected rows; Qwen Diagnosis remains the clearest pressure point (`0.1525` over-emission, `0.1347` miss rate). | Redesign review-risk features on dev140 if a lower-burden operating point is still needed. |
| 3 | Faithfulness / exact evidence | 5/5 | v08/v09/DeepSeek/Qwen selected assemblies report exact evidence rate `1.0000` on scored mentions. Source runs show evidence-validity differences: DeepSeek v0.9.10 source `0.9857`, Qwen compact source `0.9541`. JSONL rows preserve evidence text, component ownership, lane, and provenance. | Preserve exact-evidence gate for every refreshed source artifact. |
| 4 | Calibration | 4/5 | A grouped cross-validated no-call scoring rule now scores `1,706` dev140 candidate-family cells using only predeclared family/provenance/evidence ambiguity features, grouped by `letter_id` to avoid train/test letter leakage. Dev-only ECE is `0.0277`; Brier is `0.1774` versus `0.1874` for the grouped constant-base-rate comparator. The aggregate-only full-200 validation audit promotes the frozen scoring rule with ECE `0.0432`, Brier `0.2245` versus `0.2387` constant base-rate Brier, five populated monotone bins, and per-family ECE reported for Diagnosis (`0.1424`), SeizureFrequency (`0.1292`), Prescription (`0.1214`), and Investigations (`0.0925`). | Keep the claim limited to aggregate full-200 calibration evidence; do not call it deployment-ready probability or holdout calibration. |
| 5 | Abstention / review routing | 4/5 | Predeclared triggers produce a high-recall burden/benefit table: `1,605/1,706` reviewed cells (`0.9408` burden), catching `379/426` error cells (`0.8897`) but with `1,226` false-alarm cells. The dev-tuned lower-burden candidate reviewed `1,291/1,706` cells (`0.7567`) while catching `342/426` error cells (`0.8028`) on dev, but failed aggregate full-200 validation: validation burden rose to `0.9661` while catch was `0.9037`, so it is not promoted. | Keep the high-recall point as standing evidence; any lower-burden retry needs dev140-only feature redesign plus a fresh predeclaration. |
| 6 | Robustness | 4/5 | v08/v09 lineage rejects naive single-GPT/dictionary simplification and noisy union/intersection swaps; rich-schema DeepSeek/Qwen diagnostics strengthen cross-model transfer evidence. Latest Phase 6 LLM-only runs are also reported separately: DeepSeek `0.745`, Qwen `0.697` computed clinical-headline F1. The deterministic fixture-panel preflight covers SF current/historical/future states, prescription current/plan, investigation result state, diagnosis assertion/hierarchy, and evidence perturbations. The frozen aggregate-only full-200 robustness audit now promotes current-code v08 hard-slice evidence: overall F1 `0.8503`, hard-slice F1 `0.8336` across `414` eligible family cells, non-hard-slice F1 `0.8909`, schema/evidence validity `1.0000`, `0` call/parse failures. Evidence paraphrase/deletion remain adversarial fixture stress evidence, not naturally observed full-200 failures. | Keep the claim limited to aggregate full-200 hard-slice validation; add holdout/external perturbation confirmation only under a fresh protocol. |
| 7 | Consistency | 4/5 | Assembly replay is deterministic from saved artifacts. The refresh adds cross-model dev140 agreement over shared `letter_id`: pairwise clinical-headline mean Jaccard `0.8852`, exact family-cell agreement `0.8000`. The selected GPT-4.1-mini 2-call no-SF-adjudicator candidate now has saved live-repeat evidence: hard50 temp-0 exact family-cell agreement `0.9217` / mean entropy `0.1261`, and dev140 varying-temperature exact agreement `0.8857` / mean entropy `0.1905`, with `0` call/parse failures and raw producer variation confirming non-cache replay. | Keep the claim aggregate-only; add holdout/external repeat confirmation only under a fresh protocol. |
| 8 | Safety and compliance | 4/5 | Dev/test boundaries are documented; deterministic semantic repairs have provenance; full-200/holdout row-level inspection is blocked without protocol. | Add automated ExECTv2 holdout/full-200 inspection guards mirroring Gan. |
| 9 | Family parity | 5/5 | v08 clears all target families; historical non-GPT dev140 rows expose uneven family portability with residual subtype tables. Same-core dev140 family metrics are now available: DeepSeek Dx `0.8845`, SF `0.7658`, Rx `0.8895`, Inv `0.8966`; GPT Dx `0.8573`, SF `0.7645`, Rx `0.8895`, Inv `0.8347`; Qwen Dx `0.8027`, SF `0.6919`, Rx `0.8895`, Inv `0.8354`. | Use subtype parity to target architecture work; do not promote non-GPT rows from aggregate F1 alone. |
| 10 | Operational reliability | 4/5 for replay, 3/5 source runs | v08/v09 are no-call replayable. DeepSeek source and assembly diagnostics are clean. Qwen source has ten parse/schema failures and the assembly reports ten parse/schema failures per family lens surface. Same-core dev140 replay/live rows are complete with `1.0000` exact evidence across all models. GPT has `0` call/parse failures; DeepSeek has `0` call failures and `1` parse/schema failure; Qwen has `1` call failure and `12` parse/schema failures, so the readiness artifact blocks operational promotion. | Keep source parse/call warnings separate from repaired assembly success; review Qwen output-contract failures before any full-200 predeclaration. |

Mean coverage: approximately `4.2/5`. The strongest dimensions are faithfulness,
family parity instrumentation, and replayability. The main remaining weaknesses
are lower-burden review-routing redesign and holdout/external confirmation;
calibration and robustness are validated only on the aggregate full-200 surface.

## No-Call Metrics Available Now

| Metric | Current status |
| --- | --- |
| Exact evidence rate by model/family | Available from assembly JSON lane diagnostics. |
| Evidence-valid but wrong counts | Computed as `computed_reliability.family_error_table[].evidence_valid_error_count`. |
| Family-level miss and over-emission | Computed for all selected rows from `target_report.candidates[].headline_scores` and residual ledgers. |
| Cross-model agreement on dev140 | Built from shared dev140 `letter_id`: mean pairwise Jaccard `0.8852`, exact family-cell agreement `0.8000`. |
| Selected-candidate same-prompt consistency | Built from saved live repeats for `exectv2_gpt41mini_simplification_2call_no_sf_adjudicator`: hard50 temp-0 exact family-cell agreement `0.9217` / mean entropy `0.1261`; dev140 varying-temperature exact agreement `0.8857` / mean entropy `0.1905`. |
| Review triggers from provenance | Operationalized as diagnostic triggers plus operating-point scan; current high-recall dev burden is `0.9408`, and the lower-burden dev candidate is `0.7567` burden / `0.8028` catch. Aggregate full-200 validation did not promote the lower-burden candidate because validation burden rose to `0.9661` despite `0.9037` catch. |
| Robustness hard-slice validation | Aggregate full-200 current-code v08 readout: `414` hard-slice family cells, hard-slice F1 `0.8336` versus overall `0.8503`, schema/evidence validity `1.0000`, and `0` call/parse failures. |
| Latest DeepSeek/Qwen surface check | Built into `computed_reliability.latest_run_check`; Phase 6 LLM-only runs are reported separately from rich-schema reliability comparators. |
| Same-core model-swap readiness | Freeze memo and configs exist at `docs/experiments/exectv2/reliability/exectv2_same_core_model_swap_freeze_2026-06-25.md` and `configs/exectv2/model_swap/`. Readiness artifact `experiments/exectv2_same_core_model_swap_dev140_20260625.json` marks architecture parity, attribution clarity, evidence validity, family parity, and claim boundary as passed; operational stability fails because completed rows total `1` call failure and `13` parse/schema failures. |

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
| Calibration | Holdout or external aggregate-only confirmation if calibration is promoted beyond the current full-200 evidence surface. |
| Abstention / review routing | Dev140-only redesign plus fresh predeclaration for any lower-burden retry; the first lower-burden validation attempt was not promoted. |
| Robustness | Holdout or external aggregate-only confirmation if robustness is promoted beyond the current full-200 hard-slice evidence surface; keep evidence perturbation claims tied to the frozen fixture panel unless a live adversarial panel is separately authorized. |
| Consistency | Optional holdout/external repeat confirmation under a fresh protocol; the selected GPT-4.1-mini candidate already has hard50 temp-0 and dev140 varying-temperature live-repeat evidence. |
| Family parity | Use the residual subtype table to predeclare targeted architecture work. |

## Final Refresh Status

- DeepSeek v0.9.16 dev140 and Qwen v0.9.22 dev140 remain selected non-GPT
  diagnostic architecture rows, not final same-core model-swap rows.
- The same-core model-swap architecture is frozen at
  `exectv2_2call_no_sf_adjudicator_model_swap`. The dev140 same-core readout is
  complete at
  `docs/experiments/exectv2/reliability/exectv2_same_core_model_swap_dev140_2026-06-25.md`:
  DeepSeek `0.8596`, GPT-4.1-mini `0.8396`, and Qwen `0.8018` overall
  clinical-headline F1, with operational stability not promoted because Qwen
  produced `1` call failure and `12` parse/schema failures.
- Earlier DeepSeek/Qwen dev25 rows remain path evidence, but are superseded in
  the final reliability evidence set.
- The selected 2-call no-SF-adjudicator GPT-4.1-mini candidate has Gan-comparable
  self-consistency evidence on hard50 temp-0 reproducibility and dev140
  varying-temperature entropy; the hard50 panel is a temp-0 reproducibility
  check, not a varying-temperature entropy panel.
- The lower-burden review-routing candidate completed aggregate full-200
  validation and is not promoted; retry work moves back to dev140-only
  risk-feature redesign under a fresh predeclaration.
- The deterministic robustness panel has been converted into a frozen
  aggregate-only full-200 hard-slice validation audit. Current-code v08 hard-slice
  F1 is `0.8336` across `414` eligible family cells, with `1.0000` schema and
  evidence validity; evidence paraphrase/deletion remain fixture stress evidence.
- Do not add full-200 or holdout claims to this scorecard without a protocol
  that freezes scorer surface, row-inspection policy, and stop rule first.
