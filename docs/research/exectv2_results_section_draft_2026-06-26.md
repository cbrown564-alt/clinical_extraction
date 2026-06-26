# ExECTv2 Results Section (Manuscript Draft)

Date: 2026-06-26

Status: integrated into `docs/research/paper_manuscript_2026-06-26.md` as
Section 4.2 with fixed numbering (Tables 4–8) and Gan cross-references. This
standalone draft remains the ExECTv2 source slice; it does not authorize
full-200 or holdout row-level inspection.

Primary sources:

- `docs/research/exectv2_results_section_scaffold_2026-06-25.md`
- `docs/research/exectv2_reliability_component_evidence_paper_language_2026-06-25.md`
- `docs/experiments/exectv2/reliability/exectv2_same_core_model_swap_full200_2026-06-25.md`
- `docs/experiments/exectv2/reliability/exectv2_qwen_model_swap_repair_v02_full200_readout_2026-06-26.md`
- `experiments/exectv2_component_off_replay_full200_20260626.md`

## Claim Boundary

ExECTv2 results are reported as de-duplicated clinical-fact recovery under the
`clinical_headline` view. Strict benchmark and CUI-oriented scores remain
diagnostic comparability surfaces, not the headline optimization target. The
reliability scorecard and component-impact analyses are reported in separate
subsections and must not be merged into causal component claims.

---

## 4.2 ExECTv2 Clinical-Fact Recovery

Integrated in `docs/research/paper_manuscript_2026-06-26.md`. Cross-references
Section 4.1 for the SeizureFrequency bridge and the shared three-model swap
families.

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
operational rows.

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
claims with no holdout or deployment-probability claim.

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

- ExECTv2 reliability is holdout-validated.
- Qwen is an operationally promoted same-core candidate above GPT-4.1-mini or DeepSeek.
- The calibration rule is deployment-ready.
- A low-burden review-routing policy is validated.
- Strict benchmark/CUI reproduction is the headline ExECTv2 success criterion.
- The reliability scorecard proves any individual component caused the observed
  performance.

## Next Manuscript Step

Completed 2026-06-26 in `docs/research/paper_manuscript_2026-06-26.md` as
Section 4.2 with Gan cross-references in Sections 4.1.3 and 4.2.2. Next: fold
Section 4 into the full paper LaTeX draft.
