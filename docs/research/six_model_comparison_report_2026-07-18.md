# Six-model comparison across ExECTv2 and Gan 2026

Date: 2026-07-18  
Status: retained-panel report with bounded development and aggregate-only holdout claims

## Executive conclusion

The project now has the same six named model conditions on its fixed ExECTv2
and Gan 2026 pipelines: GPT-4.1-mini, GPT-5.6 Luna, GPT-5.6 Sol,
thinking-enabled DeepSeek V4 Flash, Qwen 3.6:35B, and Gemma 4 26B.

The models do not form one stable cross-task ranking. Sol leads the fixed
ExECTv2 panel, while Qwen leads the matched Gan v0.7 panel. The Spearman rank
correlation between the two locked aggregate panels is only `0.20`. This is
evidence that performance is task- and pipeline-specific, not evidence that
one model is generally best.

ExECTv2's deterministic transforms improve the development aggregate for all
six models, by `+0.0773` to `+0.1083` F1 from the saved raw-candidate view to
the final `clinical_headline` view. The new no-call Seizure Frequency study
also improves state-profile F1 for every model, but records one
correct-to-wrong state-set transition for Sol. Exact source-text evidence is
`1.0` after final ExECT assembly for all six models; this establishes citation
presence, not independent clinical support.

The Gan ten-dimension reliability scorecard should not be copied mechanically
to ExECT. It is a one-subject GPT-4.1-mini audit whose transforms depend on
Gan's exhaustive single-label task. In particular, ExECT `dev140` contains no
gold letters whose Seizure Frequency state set is exactly unknown-only, so the
Gan unknown-versus-rate denominator is empty. Empty-gold ExECT letters remain
diagnostic because annotation omission cannot be treated as proof of model
over-inference.

The appropriate project-closing result is therefore this six-model comparison,
the task-specific ExECT component and operational evidence, and an explicit
negative result for the attempted cross-task over-reading measure. Independent
clinical review remains the material next requirement for clinical-validity
claims; additional model metrics cannot replace it.

## Comparison contract

The comparison is matched within each task, not across tasks.

| Field | ExECTv2 | Gan 2026 |
| --- | --- | --- |
| Development split | Manifest `dev140`; row review permitted | `validation750`; separate local Qwen/Gemma work remains development evidence |
| Locked split | `test60`; 59 loadable letters; aggregate only | `test450`; 450 rows; aggregate only |
| Calls | One structured four-family call per letter | One structured event call per note |
| Prompt | `exectv2_hybrid_key_family_event_ledger_v0.9.24` | `gan2026_hybrid_structured_events_v0.7` |
| Final repair | Selected joint bounded policy with attributable family transforms | Fixed `hybrid_full_stack` repair |
| Primary score | Internal de-duplicated `clinical_headline` F1 | Purist label accuracy |
| Claim limit | Not the published ExECT benchmark or clinical validation | Previously used locked holdout; not a pristine one-shot ranking |

Provider-required transport, temperature, token-limit, and local-runtime
differences remain part of each condition. Qwen and Gemma use local Ollama
routes and retained aggregate-only reparses for the locked panels. These
differences are provenance caveats rather than a reason to assign a lower
evidence tier, but they prevent a model-neutral capability claim.

## ExECTv2 six-model result

| Model | dev140 F1 | test60 F1 | Drop | Test rank | Test operational result |
| --- | ---: | ---: | ---: | ---: | --- |
| GPT-5.6 Sol | 0.8920 | 0.8047 | -0.0873 | 1 | 59/59; no call or blocking parse failure |
| GPT-5.6 Luna | 0.8832 | 0.7950 | -0.0882 | 2 | 59/59; no call or blocking parse failure |
| DeepSeek V4 Flash, thinking enabled | 0.8767 | 0.7881 | -0.0886 | 3 | 59/59; no call or blocking parse failure |
| Qwen 3.6:35B | 0.8571 | 0.7872 | -0.0699 | 4 | 59/59; zero call and parse/schema failures |
| GPT-4.1-mini | 0.8202 | 0.7572 | -0.0630 | 5 | 59/59; no call or blocking parse failure |
| Gemma 4 26B | 0.8016 | 0.7169 | -0.0847 | 6 | 59/59; zero call failures; six parse/schema failures |

All six retain the same rank order between `dev140` and `test60`. Their mean
absolute F1 drop is `0.0803`. This is useful aggregate transfer evidence for
the internal scorer, but the small locked split and prohibition on row
inspection prevent a robustness or failure-mechanism claim.

### ExECT component evidence

| Model | Raw candidate | Final | Deterministic-stage delta | Diagnosis | SF headline | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| GPT-4.1-mini | 0.7128 | 0.8202 | +0.1074 | 0.8470 | 0.6936 | 0.8672 | 0.8538 |
| GPT-5.6 Luna | 0.8059 | 0.8832 | +0.0773 | 0.8910 | 0.7892 | 0.9250 | 0.9202 |
| GPT-5.6 Sol | 0.8097 | 0.8920 | +0.0823 | 0.8882 | 0.8012 | 0.9432 | 0.9358 |
| DeepSeek V4 Flash, thinking enabled | 0.7915 | 0.8767 | +0.0852 | 0.8764 | 0.7610 | 0.9280 | 0.9389 |
| Qwen 3.6:35B | 0.7488 | 0.8571 | +0.1083 | 0.8720 | 0.7062 | 0.9249 | 0.9105 |
| Gemma 4 26B | 0.7010 | 0.8016 | +0.1006 | 0.8378 | 0.6226 | 0.9046 | 0.8047 |

The delta is not a model-only gain. It includes evidence filtering,
normalization, Diagnosis recovery, Seizure Frequency projection and
suppression, Prescription bounded repair, and final assembly. Prediction-
changing deterministic actions remain hybrid decisions and are not credited to
the named model.

The selected joint policy was previously characterized on three saved model
conditions: it produced 172 rescues, three regressions, and retained 153/160
rescues from the earlier policy. Those counts describe the policy-selection
study, not a six-model pooled estimate. The final per-model artifacts preserve
fact origin, deterministic provenance, evidence status, and score-stage
outputs for the six exact conditions.

## Gan matched v0.7 result

| Model | Purist | Pragmatic | Test rank | Exact evidence | Final parse/schema/label issues |
| --- | ---: | ---: | ---: | ---: | ---: |
| Qwen 3.6:35B | 367/450 (0.8156) | 380/450 (0.8444) | 1 | 363/450 | 0 |
| GPT-5.6 Sol | 358/450 (0.7956) | 376/450 (0.8356) | 2 | 449/450 | 0 |
| GPT-4.1-mini | 353/450 (0.7844) | 371/450 (0.8244) | 3 | 419/450 | 2 |
| GPT-5.6 Luna | 352/450 (0.7822) | 365/450 (0.8111) | 4 | 446/450 | 3 |
| Gemma 4 26B | 343/450 (0.7622) | 367/450 (0.8156) | 5 | 437/450 | 0 |
| DeepSeek V4 Flash, thinking enabled | 342/450 (0.7600) | 362/450 (0.8044) | 6 | 434/450 | 4 |

All six use the same v0.7 prompt, pipeline, repair policy, and scorers. Provider
transport and temperature differ, and Qwen and Gemma were retained through a
no-call aggregate reparse of sealed local outputs. Prompt v0.7 was developed
from validation failures, and test450 supported sequential aggregate runs.
Consequently this table is a matched aggregate panel, not a pristine one-shot
or general model ranking.

Exact-evidence counts are not directly comparable with ExECT's post-assembly
rate. Gan reports row-level exact evidence before its full deterministic repair
path, whereas ExECT's stated `1.0` is the final assembled mention rate. The
different measurement points must remain visible.

## New ExECT Seizure Frequency reliability result

The predeclared no-call study compared each model's structured SF mentions with
the final projected and suppressed SF mentions on the same 140 development
letters. It used the existing change-aware state transform and did not inspect
test60.

| Model | Comparator state F1 | Final state F1 | Delta | Wrong→correct | Correct→wrong |
| --- | ---: | ---: | ---: | ---: | ---: |
| GPT-4.1-mini | 0.7340 | 0.7845 | +0.0505 | 13 | 0 |
| GPT-5.6 Luna | 0.8357 | 0.8551 | +0.0194 | 4 | 0 |
| GPT-5.6 Sol | 0.8509 | 0.8603 | +0.0094 | 3 | 1 |
| DeepSeek V4 Flash, thinking enabled | 0.8104 | 0.8429 | +0.0325 | 9 | 0 |
| Qwen 3.6:35B | 0.7517 | 0.7986 | +0.0469 | 13 | 0 |
| Gemma 4 26B | 0.6894 | 0.7386 | +0.0492 | 12 | 0 |

The deterministic SF stage improves state-profile F1 for every model and
produces 54 wrong-to-correct transitions against one correct-to-wrong
transition across the six separate conditions. Pooling these transitions is
descriptive because the same 140 letters appear under every model.

The intended primary unknown-versus-rate measure cannot be estimated:
`dev140` contains zero letters whose gold state set is exactly `{unknown}`.
There are 41 empty-gold letters, but the annotation-evidence synthesis shows
that absence of an ExECT mention can reflect omission or representation policy.
Their predicted active-rate counts are therefore retained only as diagnostics.
The project must continue to mark Gan-to-ExECT over-reading transfer as
unsupported rather than replacing the denominator after observing the data.

## Reliability dimensions and final disposition

| Dimension | Six-model evidence now available | Final disposition |
| --- | --- | --- |
| Task correctness | ExECT dev/test and Gan test panels | Report all six; complete for named internal metrics |
| Factuality / over-inference | Gan result; ExECT attempted study has zero primary denominator | Retain negative measurement result; no transfer claim |
| Faithfulness | Six-model exact/grounded evidence and component provenance | Report source presence; do not call it semantic or clinical validation |
| Calibration | ExECT internal scoring-rule result; historical three-model confidence negative result | Keep as bounded evidence, not a final six-model comparison |
| Abstention / routing | Historical predeclared rules failed | Do not adopt or rerun without a product decision requiring review routing |
| Robustness | ExECT aggregate dev/test drops; Gan prompt-version diagnostics | Do not claim perturbation or distributional robustness |
| Consistency | Gan one-model repeated-temperature study only | Do not generalize to ExECT or all six models |
| Safety and compliance | Split barriers, hashes, canaries, evidence and schema tests | Treat as pipeline-level engineering verification |
| Clinical-family behavior | ExECT four-family scores for all six | Report as task slices, not demographic fairness |
| Operational reliability | Six-model failure, repair, route, and partial timing records | Report failures; reject matched cost or latency claims |

## Recommendation and completion boundary

No further broad six-model call campaign is warranted to make this report look
symmetrical with Gan's ten-row scorecard. Repeated-temperature consistency,
perturbation robustness, matched cost/latency, or six-model confidence routing
would answer new questions and require separate protocols. They are not needed
to support the paper's current bounded comparison.

The evidence now supports:

- a fixed six-model comparison on each task with explicit runtime caveats;
- component-attributed ExECT development results;
- aggregate-only locked results under the named internal scorers;
- a bounded negative conclusion that Gan's unknown-only denominator does not
  exist in the current ExECT development gold; and
- clear separation of citation presence, model selection, deterministic
  correction, and final scoring.

It does not support general model superiority, Gan-to-ExECT reliability
transfer, the published ExECT benchmark, deployment calibration, or clinical
validation. Independent clinical review remains required before strengthening
the clinical-validity claim.

## Evidence owners

- [Project status](../../PROJECT_STATUS.md)
- [Paper claim status](../canon/10_paper_provenance.md)
- [Retained evidence index](../experiments/retained_evidence_manifest.md)
- [ExECT test60 protocol](../experiments/exectv2/reliability/exectv2_hosted_test60_protocol_2026-07-15.md)
- [Gan v0.7 test450 protocol](../experiments/gan2026/gan2026_matched_v07_test450_protocol_2026-07-15.md)
- [SF over-inference protocol](../experiments/exectv2/reliability/exectv2_six_model_sf_overinference_protocol_2026-07-18.md)
- [SF over-inference result](../experiments/exectv2/reliability/exectv2_six_model_sf_overinference_2026-07-18.md)
