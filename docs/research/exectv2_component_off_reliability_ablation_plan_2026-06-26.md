# ExECTv2 Component-Off Reliability Ablation Plan

Date: 2026-06-26

Status: planning contract; not an experiment result and not authorization for
full-200 row-level inspection.

Primary sources:

- `docs/research/exectv2_reliability_component_evidence_paper_language_2026-06-25.md`
- `docs/design/exectv2_component_ablation_contract_2026-06-24.md`
- `docs/research/exectv2_results_section_scaffold_2026-06-25.md`
- `docs/experiments/exectv2/reliability/exectv2_cross_model_reliability_scorecard_2026-06-22.md`
- `docs/experiments/exectv2/reliability/exectv2_gpt41mini_simplification_frontier_2026-06-24.md`
- `docs/experiments/exectv2/reliability/exectv2_investigations_rule_ablation_2026-06-25.md`

## Purpose

The reliability scorecard language is now stable enough to plan true
component-off ablations without confusing trust evidence for component impact.
This note defines the allowed next ablation shape. It does not change the
scorecard, rerun models, inspect full-200 rows, or promote any component claim.

The governing distinction remains:

- Reliability scorecard evidence asks whether a fixed system is grounded,
  calibrated, robust, consistent, and operationally clean under a declared
  inspection boundary.
- Component-off evidence asks what aggregate score, validity, or operational
  delta occurs when one named component is removed or replaced under the same
  scorer and source-artifact boundary.

## Claim Boundary

Allowed now:

- dev140 or validation-only planning and replay over already available source
  artifacts;
- aggregate-only comparison rows with no new model calls by default;
- same-input layer-ladder or one-component-off rows whose component ownership is
  declared before results are read;
- reporting of null or negative component deltas as valid component-impact
  evidence.

Not allowed here:

- locked-test or full-200 row-level failure analysis;
- prompt, parser, scorer, deterministic-rule, threshold, or model-choice tuning
  from an aggregate component-off readout;
- describing reliability-scorecard dimensions as causal component gains;
- blending dev140 component-impact rows into full-200 reliability claims.

Any full-200 aggregate component-off audit requires a fresh predeclaration with
split, scorer, source artifacts, stop rule, row-inspection boundary, and
reporting template before execution.

## Candidate Components

| Component question | Component type | Minimum comparison | Claim if completed |
| --- | --- | --- | --- |
| Does the SeizureFrequency adjudicator add utility beyond the accepted lean two-call candidate? | `llm_producer` / adjudicator lane | Same source artifacts and `clinical_headline` scorer, with adjudicator lane present versus absent. | Cost-performance and SF-family component-impact delta only; never proof that the removed adjudicator is globally useless. |
| How much does the Investigations verifier contribute relative to deterministic suppression or direct deterministic replacement? | verifier plus deterministic suppression | Fixed Investigations source surface versus verifier-off, suppression-off, and deterministic-replacement aggregate rows. | Component-role and component-impact evidence for Investigations; no promotion of deterministic replacement unless gates are predeclared and passed. |
| What does evidence validation change? | `evidence_validation` | Source-scored mentions versus evidence-valid surface, with invalid-evidence counts reported separately from clinical F1. | Grounding guard effect; clinical-score delta is secondary to evidence-validity delta. |
| What do dictionaries, residual semantic lenses, and headline projection contribute? | `dictionary`, `semantic_lens`, `deterministic_projection` | Existing six-layer replay surfaces plus explicit one-component-off rows where replay can isolate a single layer. | Component-impact evidence only on the declared scorer and split. |

## Minimal Artifact Contract

Each ablation row must record:

- `artifact_kind`;
- candidate/run id and baseline run id;
- split, row count, scorer view, and scorer version;
- component id, component type, component portability category, and
  prediction-bearing status;
- source artifacts and whether model calls were allowed;
- row-inspection policy;
- baseline aggregate score, component-off aggregate score, overall delta, and
  family deltas;
- schema validity, evidence validity, call failures, parse failures, and any
  abstention or missing-output counts;
- claim boundary and stop rule.

The report should include a compact table plus a short claim-use paragraph for
each component. Row-level examples are allowed on development surfaces only when
the predeclaration says so; they remain disallowed for locked-test and current
full-200 aggregate-only reliability surfaces.

## Execution Order

1. Extend the existing dev140 replay contract into named one-component-off
   configs where source artifacts already contain both sides of the comparison.
2. Add tests that reject Component Impact payloads lacking component id,
   prediction-bearing status, split, scorer view, aggregate deltas, validity
   rates, and row-inspection policy.
3. Produce a dev140 or validation-only aggregate component-off readout.
4. Decide, from the predeclared aggregate readout only, whether any component is
   worth a separate full-200 aggregate-only audit.
5. If a full-200 audit is authorized, write a fresh predeclaration before
   execution and preserve the no-row-level-inspection boundary.

## Full-200 Escalation Decision

Decision recorded on 2026-06-26:
`docs/experiments/exectv2/reliability/exectv2_component_off_full200_predeclaration_2026-06-26.md`
freezes a separate full-200 aggregate-only component-off protocol for
`standard_dictionary`, `residual_semantic_lens`, and `headline_projection`.
The decision is based only on the dev140 aggregate readout at
`experiments/exectv2_component_off_replay_dev140_20260626.{json,jsonl,md}`.

`evidence_validation` is not escalated under this protocol because its dev140
clinical-score delta was `0.0000` overall and by family across the selected
single-lane holistic replays. That null result remains a grounding-guard check,
not a global claim that evidence validation is unnecessary.

The full-200 protocol remains aggregate-only and replay-only. It does not
authorize model calls, row-level full-200 failure inspection, prompt/parser/
scorer/threshold/deterministic-rule/model-choice tuning, or Reliability
Scorecard promotion language.

## Reporting Language

Preferred wording:

> Component-off ablations report aggregate deltas from removing or replacing a
> named component under a fixed scorer and source-artifact boundary. They are
> reported separately from the reliability scorecard, which tests trust
> properties of the fixed architecture rather than causal score contribution.

Do not use these ablations to say a component is unnecessary in general. Say
which scorer, split, source artifacts, and inspection boundary produced the
observed delta.
