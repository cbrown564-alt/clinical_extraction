# ExECTv2 Reliability And Component-Evidence Paper Language

Date: 2026-06-25

Status: paper-facing consolidation note.

Primary source artifacts:

- `docs/experiments/exectv2/reliability/exectv2_cross_model_reliability_scorecard_2026-06-22.md`
- `docs/experiments/exectv2/reliability/exectv2_reliability_audit_protocol_predeclaration_2026-06-24.md`
- `docs/experiments/exectv2/reliability/exectv2_calibration_validation_audit_2026-06-25.md`
- `docs/experiments/exectv2/reliability/exectv2_review_routing_validation_audit_2026-06-24.md`
- `docs/experiments/exectv2/reliability/exectv2_robustness_validation_audit_2026-06-25.md`
- `docs/experiments/exectv2/reliability/exectv2_gpt41mini_simplification_frontier_2026-06-24.md`
- `docs/experiments/exectv2/reliability/exectv2_gpt41mini_2call_no_sf_adjudicator_deterministic_rule_roles_2026-06-24.md`
- `docs/experiments/exectv2/reliability/exectv2_investigations_rule_ablation_2026-06-25.md`
- `docs/research/exectv2_component_off_reliability_ablation_plan_2026-06-26.md`

## Purpose

This note converts the resolved ExECTv2 reliability audits into manuscript-ready
claim language. It is not a new experiment and does not change the scorecard. It
defines how to describe the evidence without blending development, aggregate
validation, holdout, and fixture-stress surfaces.

The governing distinction is:

- **Reliability evidence** asks whether a fixed system behaves consistently,
  faithfully, robustly, and with useful uncertainty signals.
- **Component-impact evidence** asks what score delta is attributable to removing
  or changing a component.

Reliability evidence can justify trust in a system. It cannot, by itself, claim
that a component caused the performance gain. Component impact requires an
ablation or same-input stage-ladder comparison.

## Claim Boundary

Use this as the compact paper claim:

> For ExECTv2, the final architecture is accompanied by a reliability scorecard
> spanning exact evidence grounding, aggregate calibration, review-routing
> diagnostics, hard-slice robustness, same-prompt consistency, cross-model
> agreement, family parity, and operational replayability. Calibration and
> robustness are supported by predeclared aggregate full-200 audits; lower-burden
> review routing was tested but not promoted; same-prompt consistency is supported
> by saved live-repeat panels for the selected lean GPT-4.1-mini candidate. These
> results are reliability evidence, not holdout performance claims and not
> component-causal ablation evidence.

Do not shorten this into "validated reliability" unless the sentence also names
the validation surface. Preferred shorthand: **aggregate full-200 reliability
evidence under a frozen row-inspection boundary**.

## Evidence Ladder

| Evidence type | Current ExECTv2 status | Claim strength |
| --- | --- | --- |
| Dev140 optimization/control | v08 reaches `0.9152` headline-target F1; v09 reaches `0.9059`; rich-schema DeepSeek/Qwen diagnostics reach `0.9174`/`0.9001` on the same dev140 surface. | Development and same-surface diagnostic evidence only. |
| Phase 3-6 active LLM-only transfer | DeepSeek reaches `0.745` and Qwen reaches about `0.694` clinical-headline F1 on `decision_table_sf_inv`; strict benchmark F1 remains near `0.13`. | Plateau comparator for LLM-only de-duplicated fact recovery, not the rich-schema scorecard surface. |
| Full-200 architecture audit | Current-code v08-shaped GPT-4.1-mini audit scores `0.8502` overall; selected 2-call no-SF-adjudicator lean candidate scores `0.8356` overall and `0.7525` SeizureFrequency with `400` calls. | Aggregate full-200 architecture evidence; no row-level development or holdout claim. |
| Calibration | Frozen grouped scoring rule validates with ECE `0.0432`, Brier `0.2245`, base-rate Brier `0.2387`, five monotone bins, and all four families reported. | Aggregate full-200 calibration evidence; not deployment-ready probability and not holdout calibration. |
| Review routing | High-recall point remains standing evidence (`0.9408` dev burden / `0.8897` catch). Lower-burden dev candidate (`0.7567` burden / `0.8028` catch) failed validation because validation burden rose to `0.9661` despite `0.9037` catch. | Review-risk evidence plus a null validation result; no promoted low-burden triage policy. |
| Robustness | Current-code v08 full-200 hard-slice F1 is `0.8336` across `414` eligible family cells versus `0.8503` overall and `0.8909` non-hard-slice, with schema/evidence validity `1.0000` and `0` call/parse failures. | Aggregate full-200 hard-slice validation evidence; paraphrase/deletion remains fixture-stress evidence. |
| Consistency | Selected 2-call no-SF-adjudicator candidate has hard50 temp-0 exact family-cell agreement `0.9217` / mean entropy `0.1261`; dev140 varying-temperature exact agreement `0.8857` / mean entropy `0.1905`; both have `0` call/parse failures. | Aggregate live-repeat consistency evidence; holdout/external repeat confirmation remains future work. |
| Investigations rule role | Deterministic replacement is not ready: direct + result lens `0.8563`, pending-test suppression `0.8665`, verifier-only `0.8770`, verifier + deterministic suppression `0.9213`. Selective review v04 meets `0.2000` burden but drops F1. | Component-role diagnostic evidence; no live selective-adjudicator promotion. |

## Component-Evidence Language

Use the following terms consistently:

- **Component impact**: a measured score delta from an ablation, stage ladder, or
  same-input component-off replay.
- **Reliability scorecard**: trust evidence about a fixed architecture, including
  grounding, calibration, routing, robustness, consistency, family parity, and
  operational integrity.
- **Component role**: a descriptive attribution of which component owns a
  decision, repair, verification, or projection step.
- **Component-causal claim**: a claim that a component caused a performance
  improvement. This requires component-impact evidence, not only a reliability
  scorecard.

Recommended manuscript phrasing:

> The reliability scorecard tests whether the selected ExECTv2 system is
> trustworthy under fixed scoring and inspection boundaries. It is deliberately
> separated from the Component Impact analysis: the scorecard reports calibration,
> robustness, routing, consistency, evidence validity, and family parity, while
> component impact is reserved for replayable ablations and stage-ladder deltas.

For Investigations:

> The Investigations audit shows that deterministic rules are useful as
> verification and suppression aids, but deterministic replacement of the
> verifier-backed path is not yet supported. The best aggregate result remains
> verifier plus deterministic suppression; the first capped selective-review
> scaffold satisfied the burden gate but lost too much F1 to promote.

For simplification:

> The selected lean ExECTv2 candidate reduces the full-200 call profile to `400`
> calls while staying above the governing overall and SeizureFrequency thresholds.
> This is a cost-performance frontier result. It should not be described as
> evidence that the removed SeizureFrequency adjudicator is useless; component
> utility still requires targeted component-off deltas under the same scorer.

## Do Not Say

- Do not say ExECTv2 reliability is holdout-validated.
- Do not say the calibration model is deployment-ready.
- Do not say a low-burden review policy is validated.
- Do not say fixture paraphrase/deletion stress tests are naturally observed
  full-200 failures.
- Do not merge rich-schema holistic assembly evidence with active LLM-only
  de-duplicated-fact evidence in one promotion decision.
- Do not use the reliability scorecard as proof that any single component caused
  the observed performance.

## Open Paper Work

1. ~~Convert this claim block into the ExECTv2 results section after the main
   architecture/performance table is frozen~~ — completed in
   `docs/research/exectv2_results_section_draft_2026-06-26.md`.
2. ~~Add a separate Component Impact subsection that uses only replayable
   component-off or stage-ladder evidence~~ — drafted in
   `docs/research/exectv2_results_section_scaffold_2026-06-25.md` using dev140 and
   full-200 component-off readouts; folded into the results draft.
3. Keep future holdout/external reliability claims behind a fresh predeclaration
   naming the scorer, split, row-inspection boundary, and stop rule.
