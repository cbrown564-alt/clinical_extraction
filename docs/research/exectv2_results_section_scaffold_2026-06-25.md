# ExECTv2 Results-Section Scaffold

Date: 2026-06-25

Status: manuscript scaffold from resolved ExECTv2 reliability and same-core
evidence. This is not a new experiment and does not authorize any full-200 or
holdout row-level inspection.

Primary sources:

- `docs/research/exectv2_reliability_component_evidence_paper_language_2026-06-25.md`
- `docs/experiments/exectv2/reliability/exectv2_same_core_model_swap_dev140_2026-06-25.md`
- `docs/experiments/exectv2/reliability/exectv2_qwen_model_swap_output_contract_audit_2026-06-25.md`
- `docs/experiments/exectv2/reliability/exectv2_gpt41mini_simplification_frontier_2026-06-24.md`
- `docs/experiments/exectv2/reliability/exectv2_calibration_validation_audit_2026-06-25.md`
- `docs/experiments/exectv2/reliability/exectv2_review_routing_validation_audit_2026-06-24.md`
- `docs/experiments/exectv2/reliability/exectv2_robustness_validation_audit_2026-06-25.md`
- `docs/experiments/exectv2/reliability/exectv2_investigations_rule_ablation_2026-06-25.md`

## Claim Boundary

ExECTv2 results should be presented as de-duplicated clinical-fact recovery
under the `clinical_headline` view. Strict benchmark/CUI reproduction remains a
diagnostic and comparability surface, not the headline optimization target.

The reliability scorecard is trust evidence for fixed systems under declared
inspection boundaries. It is separate from component-impact evidence, which
requires component-off replay, ablation, or same-input stage-ladder deltas.

## Results Text Scaffold

### Clinical-Recovery Performance

The selected ExECTv2 clinical-finding assembly is evaluated primarily by
de-duplicated clinical-headline recovery rather than strict full-schema
annotation reproduction. On the aggregate full-200 current-code audit, the
verifier-backed GPT-4.1-mini v08-shaped architecture scored `0.8502` overall
clinical-headline F1, with family scores of Diagnosis `0.8321`,
SeizureFrequency `0.7850`, Prescription `0.8926`, and Investigations `0.9213`.
The accepted lean candidate, `exectv2_gpt41mini_simplification_2call_no_sf_adjudicator`,
reduced the full-200 call profile to `400` calls while preserving the governing
cost-performance gates: `0.8356` overall and `0.7525` SeizureFrequency F1.

Strict benchmark and CUI-oriented outputs should be reported only as secondary
diagnostics that measure compatibility with the original annotation surface.
They should not be described as the primary ExECTv2 success criterion or
directly compared with clinical-headline recovery.

| System/view | Surface | Overall | Diagnosis | SeizureFrequency | Prescription | Investigations | Claim use |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Current-code v08-shaped GPT-4.1-mini | full-200 aggregate, `clinical_headline` | 0.8502 | 0.8321 | 0.7850 | 0.8926 | 0.9213 | Aggregate architecture evidence; no row-level full-200 development claim. |
| No-verifier ablation | full-200 aggregate, `clinical_headline` | 0.8431 | 0.8410 | 0.7850 | 0.8926 | 0.8563 | Component-role comparison; Investigations verifier remains useful. |
| Accepted lean 2-call no-SF-adjudicator | full-200 aggregate, `clinical_headline` | 0.8356 | 0.8397 | 0.7525 | 0.8926 | 0.8563 | Cost-performance frontier; not proof the removed SF adjudicator has zero utility. |

### Same-Core Model-Swap Evidence

Using the frozen `exectv2_2call_no_sf_adjudicator_model_swap` core on dev140,
DeepSeek chat, GPT-4.1-mini, and Qwen 3.6 35B were compared under the same
component graph and `clinical_headline` scorer. DeepSeek produced the strongest
dev140 aggregate score, GPT-4.1-mini remained operationally clean, and Qwen
remained diagnostic because its output-contract failures prevented operational
promotion.

| Candidate | Model | Surface | Overall | Diagnosis | SeizureFrequency | Prescription | Investigations | Operational caveat |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `exectv2_2call_no_sf_adjudicator_deepseek_dev140` | DeepSeek chat | dev140 `clinical_headline` | 0.8596 | 0.8845 | 0.7658 | 0.8895 | 0.8966 | One parse/schema failure; include in next full-200 predeclaration only after freezing aggregate-only rules. |
| `exectv2_2call_no_sf_adjudicator_gpt41mini_dev140` | GPT-4.1-mini | dev140 `clinical_headline` | 0.8396 | 0.8573 | 0.7645 | 0.8895 | 0.8347 | Operationally clean dev140 row. |
| `exectv2_2call_no_sf_adjudicator_qwen36_dev140` | Qwen 3.6 35B | dev140 `clinical_headline` | 0.8018 | 0.8027 | 0.6919 | 0.8895 | 0.8354 | Diagnostic only: one call failure and twelve parse/schema failures from Qwen-specific output-contract drift. |

Recommended wording:

> The same-core model-swap study suggests that the ExECTv2 component graph is
> not GPT-4.1-mini-specific: DeepSeek reached `0.8596` and GPT-4.1-mini reached
> `0.8396` clinical-headline F1 on dev140 under the frozen core. Qwen is retained
> as a diagnostic comparison only because output-contract failures, not clinical
> score alone, block operational promotion.

Do not describe Qwen as an operational candidate for the next full-200 run
unless a separately predeclared Qwen-specific repair passes dev140 on the frozen
core.

### Reliability Scorecard

The reliability scorecard should follow the main performance table, not replace
it. The current evidence supports an aggregate full-200 reliability claim under
a frozen row-inspection boundary, with no holdout or deployment-probability
claim.

| Reliability dimension | Current evidence | Manuscript claim |
| --- | --- | --- |
| Evidence grounding | Same-core rows report minimum exact evidence rate `1.0000`; robustness audit also has schema/evidence validity `1.0000`. | Outputs are evidence-grounded on the audited surfaces. |
| Calibration | Frozen grouped scoring rule validates on full-200 with ECE `0.0432`, Brier `0.2245`, and base-rate Brier `0.2387`. | Aggregate calibration evidence, not deployment-ready probability calibration. |
| Review routing | High-recall point remains standing evidence; lower-burden candidate failed validation because burden rose to `0.9661` despite `0.9037` catch. | No promoted low-burden triage policy. |
| Robustness | Current-code v08 hard-slice F1 is `0.8336` across `414` eligible family cells versus `0.8503` overall. | Aggregate hard-slice validation evidence; fixture stress remains separate. |
| Consistency | Selected lean candidate has hard50 temp-0 exact agreement `0.9217` and dev140 varying-temperature exact agreement `0.8857`. | Live-repeat consistency evidence, not holdout consistency. |
| Component role | Investigations verifier plus deterministic suppression remains strongest at `0.9213`; deterministic replacement is not ready. | Rules are useful verification/suppression aids, not validated replacements for the verifier-backed path. |

Recommended wording:

> The reliability scorecard tests whether the selected ExECTv2 system behaves
> faithfully under fixed scoring and inspection boundaries. Calibration and
> robustness have predeclared aggregate full-200 evidence; review routing has a
> useful high-recall diagnostic but no validated low-burden policy; and
> consistency is supported by saved live-repeat panels for the selected lean
> candidate. These results support trust in the fixed architecture but are not
> holdout performance claims and are not component-causal ablation evidence.

### Component Impact

Component Impact is reported separately from the reliability scorecard. Claims
are limited to aggregate replay deltas under a fixed scorer, split, and
inspection boundary.

Dev140 one-component-off replay (`16` rows) and full-200 aggregate-only replay
(`9` rows) support limited component-impact language for dictionary
normalization, residual semantic recovery, and headline projection on
`clinical_headline`. Evidence validation was structurally inert on the dev140
single-lane holistic replays and was not escalated to full-200 under the frozen
protocol.

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

Recommended wording:

> Component-impact claims are reserved for ablations and same-input replay
> deltas under a declared scorer and inspection boundary. Dictionary,
> residual-semantic, and headline-projection layers show positive aggregate
> deltas on dev140 and full-200 replay, but these results do not prove any
> component is globally required. The reliability scorecard remains separate
> because it measures trust properties of a fixed architecture rather than
> causal score contribution from individual components.

## Do Not Use As Claims

- ExECTv2 reliability is holdout-validated.
- Qwen is an operationally promoted same-core candidate.
- The calibration rule is deployment-ready.
- A low-burden review-routing policy is validated.
- Strict benchmark/CUI reproduction is the headline ExECTv2 success criterion.
- The reliability scorecard proves any individual component caused the observed
  performance.

## Next Manuscript Step

The same-core full-200 aggregate table and the component-off full-200 readout
are now frozen in this scaffold. The next manuscript step is to fold the
reliability scorecard and component-impact subsections into the main results
draft once the architecture/performance table is frozen, without merging trust
evidence into component-causal claims.
