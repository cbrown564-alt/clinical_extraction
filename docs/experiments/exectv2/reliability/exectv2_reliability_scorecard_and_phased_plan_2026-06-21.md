# ExECTv2 Reliability Scorecard and Phased Plan

Date: 2026-06-21  
Canonical subject: `exectv2_holistic_finding_assembly_v08_dev140`  
Scope: dev140 component-attributed evidence only  

## Scope and Claim Boundary

This scorecard closes the renewed dev140 optimization goal: use the holistic
finding assembly architecture with GPT-4.1-mini-family producers/lenses and
row-level error analysis to push the four target families above `0.900`.

v08 achieves that target:

| Family | Official assembly F1 | Precision | Recall | Status |
| --- | ---: | ---: | ---: | --- |
| Diagnosis | 0.9083 | 0.8762 | 0.9428 | clears |
| SeizureFrequency | 0.9053 | 0.9000 | 0.9107 | clears |
| Prescription | 0.9357 | 0.9286 | 0.9430 | clears |
| Investigations | 0.9132 | 0.9380 | 0.8897 | clears |
| Overall | 0.9152 | 0.9037 | 0.9270 | clears |

This is not a benchmark, full-200, locked-test, or deployment claim. It is
dev-only component evidence over the first 140 dev rows. The residual ledgers
use stricter diagnostic surfaces for some families; the table above is the
official goal surface from the holistic assembly report.

## Reliability Scorecard

Coverage score: 5 = fully evidenced on dev140 in reliability-ready form; 1 =
absent or only anecdotal.

| # | Dimension | Cov. | Current State | Gap to Close |
| --- | ---: | :---: | --- | --- |
| 1 | Task correctness | 4/5 | All four target families clear `>0.900` on the official dev140 assembly headline; overall F1 `0.9152`. | Freeze a full-200/holdout protocol before any broader claim. |
| 2 | Factuality / over-inference | 4/5 | Exact evidence is enforced in assembly replay; residual ledgers identify over-emissions by family. | Re-express FP residuals as over-inference rates by family and subtype. |
| 3 | Faithfulness | 5/5 | v08 scored mentions all have exact source evidence; no live calls in final assembly replay. | Keep exact-evidence gate mandatory for any future source artifact. |
| 4 | Calibration | 2/5 | Family scores and residuals are measured, but no calibrated confidence or risk model exists for ExECTv2. | Build no-call failure-risk signals from provenance, evidence shape, and family/lens diagnostics. |
| 5 | Abstention / review routing | 2/5 | No abstention policy is attached to v08; all residuals are post-hoc errors. | Define review triggers from residual families: Diagnosis strict assertion, SF active-rate fidelity, Prescription current-vs-plan, Investigations result-state ambiguity. |
| 6 | Robustness | 3/5 | Each major phase included ablations against naive swaps/unions/intersections and rejected noisy gains. | Add frozen perturbation panels for current-vs-future meds, planned investigations, and diagnosis convention aliases. |
| 7 | Consistency | 3/5 | Holistic replay is deterministic and reproducible from saved JSONL artifacts; no self-consistency sampling was needed for v08. | For model-bearing lanes, run small same-prompt resampling panels only after a predeclaration. |
| 8 | Safety and compliance | 4/5 | Dev/test boundaries are documented; no holdout row-level inspection was used; semantic deterministic repairs are provenance-stamped. | Add an automated guard for ExECTv2 full-200/test row-level failure inspection, mirroring GAN. |
| 9 | Subgroup / family parity | 4/5 | Family-level targets are all above `0.900`; weakest official family is SF at `0.9053`. | Convert residual ledgers into per-subtype parity metrics within each family. |
| 10 | Operational reliability | 4/5 | Final assembly is no-call, artifact-replayable, exact-evidence checked, and covered by focused tests/Ruff. | Add a manifest-level promotion gate aligned to the renewed goal; current gate still encodes older P/I no-change checks. |

Aggregate read: mean coverage is approximately `3.5/5`. The strongest evidence
is faithfulness and task correctness on dev140. The weakest dimensions are
calibration and abstention because v08 is an extraction assembly, not yet a
risk-aware operating policy.

## Residual Risk Register

| Family | Cleared? | Main Residual Risk |
| --- | --- | --- |
| Diagnosis | yes | Official concept headline clears, but strict assertion ledger remains lower; convention/alias repairs are benchmark-format-heavy. |
| SeizureFrequency | yes | Type/state headline clears; active-rate fidelity remains a separate weaker companion and should not be overstated. |
| Prescription | yes | Current-vs-plan and split-dose edge cases remain; v08 stopped at `0.9357` rather than forcing the hoped-for `~0.95`. |
| Investigations | yes | Remaining errors are result-state ambiguity, especially EEG abnormal/normal and MRI abnormal/normal distinctions. |

## Phase Plan

### Phase 0 — No Model Calls

- Rebuild the v08 report from the manifest and verify artifact hashes.
- Convert v08 residual ledgers into family-specific over-inference/miss subtype
  tables.
- Add an updated assembly promotion gate for the renewed goal: all four family
  headlines `>0.900`, exact evidence `1.0000`, no call/parse failures, and
  explicit caveats for strict companion surfaces.
- Produce a compact dev140 reliability appendix from the v08 JSON/JSONL only.

### Phase 1 — Governed Full-200 / Holdout Readiness

- Predeclare the exact full-200 aggregate readout before opening any row-level
  failures.
- Freeze the v08 source artifacts and deterministic code hash.
- Run aggregate-only scoring first; inspect row-level full-200 failures only if
  explicitly authorized by the frozen protocol.

### Phase 2 — Targeted Fresh-Model Work

- Only if Phase 1 shows family regression, run small GPT-4.1-mini residual panels
  for the regressed family.
- Keep panels family-specific; do not use broad all-family live reruns unless
  a predeclared ablation says why.
- Any new model-bearing lane must be scored as a drop-in, union, intersection,
  and final arbitration against v08 before promotion.

## Canonical Artifacts

- v08 manifest: `configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v08_dev140.yaml`
- v08 assembly report: `docs/experiments/exectv2/key_entities/exectv2_holistic_finding_assembly_v08_dev140_20260621.md`
- v08 JSON: `experiments/exectv2_holistic_finding_assembly_v08_dev140_20260621.json`
- v08 JSONL: `experiments/exectv2_holistic_finding_assembly_v08_dev140_20260621.jsonl`
- v08 residual ledger: `experiments/exectv2_holistic_finding_assembly_v08_error_ledger_dev140_20260621.md`
- Diagnosis phase report: `docs/experiments/exectv2/key_entities/exectv2_holistic_finding_assembly_v05_diagnosis_phase4_error_analysis_20260621.md`
- SF phase report: `docs/experiments/exectv2/key_entities/exectv2_holistic_finding_assembly_v06_sf_phase1_error_analysis_20260621.md`
- Investigations phase report: `docs/experiments/exectv2/key_entities/exectv2_holistic_finding_assembly_v07_investigations_phase1_error_analysis_20260621.md`
- Prescription phase report: `docs/experiments/exectv2/key_entities/exectv2_holistic_finding_assembly_v08_prescription_phase1_error_analysis_20260621.md`
