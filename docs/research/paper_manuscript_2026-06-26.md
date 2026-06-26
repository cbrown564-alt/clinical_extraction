# Paper Manuscript — Results Section Draft

Date: 2026-06-26

Status: integrated results draft for the two-task reliability paper. Section 4
reports Gan 2026 (deep single-concept seizure frequency) and ExECTv2 (broad
multi-entity phenotyping) under fixed claim boundaries. This document does not
authorize holdout or full-200 row-level inspection for development.

Primary sources:

- `docs/research/gan2026/syntheses/gan2026_closeoff_report_2026-06-12.md`
- `docs/research/gan2026/retrospectives/gan2026_research_closeout_synthesis_2026-06-17.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate4_exact_aggregate_audit_2026-06-26.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate4_constrained_aggregate_audit_2026-06-26.md`
- `docs/research/exectv2_results_section_draft_2026-06-26.md`

## Claim Boundary (Both Tasks)

- Gan 2026 results use Purist/Pragmatic label accuracy on the locked `test450`
  split only as frozen aggregate evidence unless explicitly marked validation750.
- ExECTv2 results use de-duplicated `clinical_headline` recovery as the headline
  surface; strict benchmark/CUI scores remain diagnostic comparability only.
- Reliability scorecard and component-impact subsections are separate and must
  not be merged into causal component claims on either task.
- Seizure Frequency is the cross-task bridge: the deep target of Section 4.1 and
  the hardest ExECTv2 family in Section 4.2 (see `docs/design/reliability_thesis.md` §2).

---

## 4 Results

We evaluate the shared modular architecture on two complementary epilepsy-letter
tasks: deep seizure-frequency extraction (Section 4.1) and broad multi-entity
phenotyping (Section 4.2). For each task we report architecture comparison,
frozen holdout or aggregate validation evidence under declared inspection
boundaries, and—where predeclared—separate reliability and component-impact
readouts.

## 4.1 Gan 2026 Seizure-Frequency Extraction

### 4.1.1 Three-Way Architecture Comparison

On validation750, `hybrid_structured_events` combined the best LLM-using coverage
and accuracy balance among the three canonical families: the LLM extracts
source-near structured events with exact evidence spans; deterministic code owns
normalization, projection, and scoring. The deterministic canonical pipeline led
validation after de-overfitting (`673/741` Purist of rendered,
`0.908`) but showed the largest validation-to-holdout drop on the frozen
`test450` audit, supporting the portability warning that high validation score
from rules alone is incomplete generalization evidence.

**Table 1. Gan 2026 three-way comparison on validation750 (`gpt-4.1-mini`).**

| Architecture | Rendered | Purist of rendered | Pragmatic of rendered | Reading |
| --- | ---: | ---: | ---: | --- |
| `deterministic_canonical_pipeline` | 741/750 | 673/741 (0.908) | 681/741 (0.919) | High validation score; large holdout drop. |
| `hybrid` | 597/750 | 526/597 (0.881) | 545/597 (0.913) | Strong rendered accuracy; too many null/routed rows. |
| `hybrid_structured_events` | 748/750 | 661/748 (0.884) | 679/748 (0.908) | Best LLM-using validation coverage/accuracy balance. |
| `llm_only_canonical_pipeline` | 750/750 | 582/750 (0.776) | 614/750 (0.819) | Comparator; below hybrid structured events. |

**Table 2. Gan 2026 frozen `test450` aggregate audit (`gpt-4.1-mini`).**

| Architecture | Rendered | Purist of rendered | Pragmatic of rendered | Claim use |
| --- | ---: | ---: | ---: | --- |
| `deterministic_canonical_pipeline` | 450/450 | 329/450 (0.731) | 341/450 (0.758) | Frozen aggregate; validation-to-test gap warning. |
| `hybrid` | 334/450 | 269/334 (0.805) | 281/334 (0.841) | Frozen aggregate; coverage-limited. |
| `hybrid_structured_events` | 448/450 | 364/448 (0.812) | 381/448 (0.850) | Strongest frozen hybrid aggregate on rendered rows. |
| `llm_only_canonical_pipeline` | 450/450 | 326/450 (0.724) | 346/450 (0.769) | Frozen comparator row. |

The promoted close-off candidate is the single GPT structured-event pass on
`gpt-4.1-mini`, which reached `364/450` Purist (`0.809`) on locked `test450`
with the smallest validation-to-test drop among LLM-using architectures. The
full V12 fresh-evidence hybrid reached `379/450` Purist (`0.842`) but is
retained only as a high-complexity ceiling comparator, not the operational
headline system.

### 4.1.2 Frozen Holdout Aggregate Evidence (Consensus/Fresh v0.9)

Late-cycle consensus/fresh selector evidence is reported only as frozen aggregate
audits completed under predeclared Gate 4 protocols. The constrained-source audit
failed promotion bars (`348/450` selected Purist, changed-label precision
`0.5909`, `7` correct-to-wrong). The exact-source audit passed promotion bars
(`359/450` selected Purist, `+16` net Purist gain vs deterministic,
changed-label precision `0.6000`, `5` correct-to-wrong). Neither audit
authorizes post-test tuning or row-level failure inspection.

**Table 3. Gan 2026 consensus/fresh v0.9 frozen Gate 4 aggregate audits (`test450`).**

| Audit | Source symmetry | Selected Purist | Net gain vs det. | Changed-label precision | Gate outcome | Claim use |
| --- | --- | ---: | ---: | ---: | --- | --- |
| Constrained | constrained | 348/450 (0.7733) | +19 | 0.5909 | Failed | Final-evaluation evidence only. |
| Exact-source | exact | 359/450 (0.7978) | +16 | 0.6000 | Passed | Frozen exact v0.9 selector holdout over frozen source set. |

> Gan holdout-facing claims are limited to aggregate `test450` numbers under
> frozen protocols. Validation750 rows are development evidence. The
> structured-event hybrid leads the frozen three-way comparison, while the
> exact-source consensus/fresh selector records a bounded `+16` Purist holdout
> gain at `0.6000` changed-label precision. These results do not authorize
> further gate, prompt, or selector tuning from locked-test aggregates.

### 4.1.3 Bridge to ExECTv2

Seizure-frequency normalization, temporal anchoring, and seizure-free handling
developed for Gan 2026 are the direct substrate for ExECTv2 SeizureFrequency
recovery in Section 4.2. The cross-task read is not a benchmark win claim: it
tests whether the modular investment transfers to a new annotation schema and
scoring surface. ExECTv2 SeizureFrequency remains the weakest family on
`clinical_headline` despite positive full-200 aggregate recovery, which is
consistent with the deep-reasoning difficulty established in Section 4.1.

---

## 4.2 ExECTv2 Clinical-Fact Recovery

### 4.2.1 Architecture and Clinical-Headline Performance

We evaluate the selected ExECTv2 clinical-finding assembly primarily by
de-duplicated clinical-headline recovery rather than strict full-schema
annotation reproduction. On the aggregate full-200 current-code audit, the
verifier-backed GPT-4.1-mini v08-shaped architecture scored `0.8502` overall
clinical-headline F1, with family scores of Diagnosis `0.8321`,
SeizureFrequency `0.7850`, Prescription `0.8926`, and Investigations `0.9213`.
The accepted lean candidate,
`exectv2_gpt41mini_simplification_2call_no_sf_adjudicator`, reduced the
full-200 call profile to `400` calls while preserving the governing
cost-performance gates: `0.8356` overall and `0.7525` SeizureFrequency F1.

Strict benchmark and CUI-oriented outputs measure compatibility with the
original annotation surface. They are reported only as secondary diagnostics and
are not described as the primary ExECTv2 success criterion.

**Table 4. ExECTv2 architecture comparison on full-200 aggregate `clinical_headline`.**

| System/view | Surface | Overall | Diagnosis | SeizureFrequency | Prescription | Investigations | Claim use |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Current-code v08-shaped GPT-4.1-mini | full-200 aggregate, `clinical_headline` | 0.8502 | 0.8321 | 0.7850 | 0.8926 | 0.9213 | Aggregate architecture evidence; no row-level full-200 development claim. |
| No-verifier ablation | full-200 aggregate, `clinical_headline` | 0.8431 | 0.8410 | 0.7850 | 0.8926 | 0.8563 | Component-role comparison; Investigations verifier remains useful. |
| Accepted lean 2-call no-SF-adjudicator | full-200 aggregate, `clinical_headline` | 0.8356 | 0.8397 | 0.7525 | 0.8926 | 0.8563 | Cost-performance frontier; not proof the removed SF adjudicator has zero utility. |

### 4.2.2 Same-Core Model Swap

Using the frozen `exectv2_2call_no_sf_adjudicator_model_swap` core, DeepSeek
chat, GPT-4.1-mini, and Qwen 3.6 35B were compared under the same component
graph and `clinical_headline` scorer. On dev140, DeepSeek produced the
strongest aggregate score, GPT-4.1-mini remained operationally clean, and the
unrepaired Qwen row remained diagnostic because output-contract failures blocked
operational promotion. Qwen repair v02 later passed the predeclared dev140 and
full-200 aggregate gates with `0` call/parse failures in both assemblies,
providing same-core model-family evidence below the GPT-4.1-mini and DeepSeek
operational rows. The same three-model families were also compared on Gan 2026
structured events in Section 4.1.1; ExECTv2 repeats the comparison under the
shared frozen core rather than as a direct holdout transfer claim.

**Table 5. Same-core model swap on dev140 `clinical_headline`.**

| Candidate | Model | Overall | Diagnosis | SeizureFrequency | Prescription | Investigations | Operational caveat |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `exectv2_2call_no_sf_adjudicator_deepseek_dev140` | DeepSeek chat | 0.8596 | 0.8845 | 0.7658 | 0.8895 | 0.8966 | One parse/schema failure. |
| `exectv2_2call_no_sf_adjudicator_gpt41mini_dev140` | GPT-4.1-mini | 0.8396 | 0.8573 | 0.7645 | 0.8895 | 0.8347 | Operationally clean dev140 row. |
| `exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_dev140` | Qwen 3.6 35B repair v02 | 0.8319 | 0.8473 | 0.7182 | 0.8895 | 0.8755 | Passes repair gates; model-family evidence, not operational promotion over GPT/DeepSeek. |
| `exectv2_2call_no_sf_adjudicator_qwen36_dev140` | Qwen 3.6 35B (unrepaired) | 0.8018 | 0.8027 | 0.6919 | 0.8895 | 0.8354 | Diagnostic only: one call failure and twelve parse/schema failures. |

**Table 6. Same-core model swap on full-200 aggregate `clinical_headline`.**

| Candidate | Model | Overall | Diagnosis | SeizureFrequency | Prescription | Investigations | Call/parse failures | Min evidence rate |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `exectv2_2call_no_sf_adjudicator_deepseek_full200` | DeepSeek chat | 0.8566 | 0.8708 | 0.7602 | 0.8926 | 0.9091 | 0 / 1 | 1.0000 |
| `exectv2_2call_no_sf_adjudicator_gpt41mini_full200` | GPT-4.1-mini | 0.8356 | 0.8397 | 0.7525 | 0.8926 | 0.8563 | 0 / 0 | 1.0000 |
| `exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_full200` | Qwen 3.6 35B repair v02 | 0.8197 | 0.8307 | 0.7020 | 0.8926 | 0.8503 | 0 / 0 | 1.0000 |

> The same-core model-swap study suggests that the ExECTv2 component graph is
> not GPT-4.1-mini-specific: DeepSeek reached `0.8596` and GPT-4.1-mini reached
> `0.8396` clinical-headline F1 on dev140 under the frozen core, with full-200
> aggregate rows of `0.8566` and `0.8356` respectively. Qwen repair v02 provides
> additional same-core model-family evidence (`0.8319` dev140; `0.8197`
> full-200) after output-contract repair, but remains below the operational
> GPT-4.1-mini and DeepSeek rows. The unrepaired Qwen dev140 row is retained as
> a diagnostic comparator only.

### 4.2.3 Reliability Scorecard

The reliability scorecard follows the main performance tables and tests whether
the selected ExECTv2 system behaves faithfully under fixed scoring and
inspection boundaries. Current evidence supports aggregate full-200 reliability
claims with no holdout or deployment-probability claim. This scorecard is
analogous in role—but not directly comparable in metrics—to the Gan 2026
reliability re-expression in `docs/experiments/gan2026/reliability/gan2026_reliability_scorecard_and_phased_plan_2026-06-17.md`.

**Table 7. ExECTv2 reliability scorecard (aggregate full-200 under frozen row-inspection boundary).**

| Reliability dimension | Current evidence | Manuscript claim |
| --- | --- | --- |
| Evidence grounding | Same-core rows report minimum exact evidence rate `1.0000`; robustness audit also has schema/evidence validity `1.0000`. | Outputs are evidence-grounded on the audited surfaces. |
| Calibration | Frozen grouped scoring rule validates on full-200 with ECE `0.0432`, Brier `0.2245`, and base-rate Brier `0.2387`. | Aggregate calibration evidence, not deployment-ready probability calibration. |
| Review routing | High-recall point remains standing evidence; lower-burden candidate failed validation because burden rose to `0.9661` despite `0.9037` catch. | No promoted low-burden triage policy. |
| Robustness | Current-code v08 hard-slice F1 is `0.8336` across `414` eligible family cells versus `0.8503` overall. | Aggregate hard-slice validation evidence; fixture stress remains separate. |
| Consistency | Selected lean candidate has hard50 temp-0 exact agreement `0.9217` and dev140 varying-temperature exact agreement `0.8857`. | Live-repeat consistency evidence, not holdout consistency. |
| Component role | Investigations verifier plus deterministic suppression remains strongest at `0.9213`; deterministic replacement is not ready. | Rules are useful verification/suppression aids, not validated replacements for the verifier-backed path. |

> The reliability scorecard tests whether the selected ExECTv2 system behaves
> faithfully under fixed scoring and inspection boundaries. Calibration and
> robustness have predeclared aggregate full-200 evidence; review routing has a
> useful high-recall diagnostic but no validated low-burden policy; and
> consistency is supported by saved live-repeat panels for the selected lean
> candidate. These results support trust in the fixed architecture but are not
> holdout performance claims and are not component-causal ablation evidence.

### 4.2.4 Component Impact

Component impact is reported separately from the reliability scorecard. Claims
are limited to aggregate replay deltas under a fixed scorer, split, and
inspection boundary. Dev140 one-component-off replay (`16` rows) and full-200
aggregate-only replay (`9` rows) support limited component-impact language for
dictionary normalization, residual semantic recovery, and headline projection on
`clinical_headline`. Evidence validation was structurally inert on the dev140
single-lane holistic replays and was not escalated to full-200 under the frozen
protocol.

**Table 8. Component-off aggregate deltas on `clinical_headline`.**

| Component | Type | Split | Overall delta range | Main family signal | Claim boundary |
| --- | --- | --- | ---: | --- | --- |
| `standard_dictionary` | `dictionary` | dev140 | `+0.0389` to `+0.1120` | Diagnosis up to `+0.1397`; SeizureFrequency up to `+0.1728` | Conditional dictionary/benchmark-format recovery on the declared scorer. |
| `standard_dictionary` | `dictionary` | full200 | `+0.0186` to `+0.0290` | Diagnosis up to `+0.0802` | Same-core full-200 component-impact evidence only; not a holdout claim. |
| `residual_semantic_lens` | `semantic_lens` | dev140 | `+0.0175` to `+0.1041` | Investigations up to `+0.1722` | Prediction-bearing semantic add/drop/replace contribution. |
| `residual_semantic_lens` | `semantic_lens` | full200 | `+0.0098` to `+0.0117` | Diagnosis up to `+0.0310` | Full-200 aggregate replay only; no row-level inspection. |
| `headline_projection` | `deterministic_projection` | dev140 | `+0.0283` to `+0.0446` | SeizureFrequency up to `+0.2031` | Deterministic projection/format contribution. |
| `headline_projection` | `deterministic_projection` | full200 | `+0.0302` to `+0.0350` | SeizureFrequency up to `+0.1417` | Format layer only; separated from semantic fact changes. |

The no-verifier full-200 ablation and Investigations rule ablation remain
separate component-role comparisons. They should not be blended with the
layer-ladder component-off readouts above.

> Component-impact claims are reserved for ablations and same-input replay
> deltas under a declared scorer and inspection boundary. Dictionary,
> residual-semantic, and headline-projection layers show positive aggregate
> deltas on dev140 and full-200 replay, but these results do not prove any
> component is globally required. The reliability scorecard remains separate
> because it measures trust properties of a fixed architecture rather than
> causal score contribution from individual components.

## Do Not Use As Claims

- Gan or ExECTv2 holdout/full-200 reliability is deployment-validated.
- ExECTv2 de-duplicated `clinical_headline` recovery is a strict benchmark win.
- Qwen is an operationally promoted same-core ExECTv2 candidate above GPT-4.1-mini or DeepSeek.
- The ExECTv2 calibration rule is deployment-ready.
- A low-burden review-routing policy is validated on ExECTv2.
- Strict benchmark/CUI reproduction is the headline ExECTv2 success criterion.
- Either reliability scorecard proves individual component causality.
- Gan consensus/fresh constrained Gate 4 is a promoted holdout selector.
- Post-test tuning is authorized from any frozen `test450` aggregate.

## Next Manuscript Step

Fold Section 4 into the full paper LaTeX draft (methods, figures, discussion).
Keep Gan and ExECTv2 reliability/component subsections separate in the final
layout.
