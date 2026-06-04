# Project Status

Last updated: 2026-06-04

## Active Objective

Answer the Gan 2026 seizure-frequency component research questions under
exact-evidence, attribution, hidden-family, and split-discipline constraints.
No benchmark-comparable claim is authorized.

## Current Strategy

Use saved artifacts as research instruments for component questions, not
whole-pipeline validation F1. Deterministic rules are frozen comparators, safety
floors, and miss-slice definers, not eligible answers for RQ1-RQ4.

RQ1-RQ10 now have bounded validation-development answers or explicit claim
boundaries. RQ3 remains positive but has unresolved projection-policy work.

Important numbers: `selective_safety_floor_gate_v0` changed 21 validation750
rows with 11 W->C and 0 C->W, and 14 frozen local test450 rows with 8 W->C and
0 C->W. RQ9 v3 covers 716/750 validation rows, abstains on 26, routes 8 to
human review, and has covered-row Purist accuracy 0.9469. RQ10 found 23
`underdetermined_note`, 19 `true_extraction_failure`, 11
`benchmark_convention_dominated`, and 0 strong likely gold defects among 53
residual Purist misses.

## Active Question

Multi-Component Assembly

Status: component-home cleanup has started under ADR 0010. Source tracing and
suspicious selected-state policy now have independent component modules. The
promoted `binary_quote_highest_answer_selector` verifier also has a component
home, and the first no-call staged-hybrid assembly surface can wire selected
state union, suspicious routing, and saved verifier replay without owning their
logic. The saved assembly replay currently covers the 75-row hard panel, with
verifier coverage on the 42-row verifier slice; it is not a validation750
readout.

The validation750 input inventory now identifies three saved full-validation
surfaces that are available for assembly adaptation:
`hybrid_reasoner_replay`, `selective_safety_floor_gate_v0`, and
`rq9_selective_action_router_v3`, each at 750/750 source-row coverage. It also
marks the missing module-shaped inputs explicitly:
`rich_selected_state_fact_carrier`,
`boundary_v3_selected_state_candidates`, and full-validation
`promoted_binary_selective_verifier`. The next step is adapting the available
validation750 source-candidate, safety-floor, and router surfaces into assembly
rows while keeping the verifier slice separate until a full-validation verifier
protocol exists. That validation750 no-call assembly now exists at 750 joined
rows with all three available components present on every row, router actions
of 716 predict / 26 abstain / 8 human review, and 750/750 safety-floor rows
with exact selected evidence and valid selected source ids.

The explicit staged decision layer now exists over those assembled rows. It is
conservative: only router `predict` rows are prediction-bearing, while
`abstain` and `human_review` remain non-predictions. It has 750 rows, 716
prediction-bearing rows, 34 non-prediction rows, selective Purist accuracy
0.9469 and selective Pragmatic accuracy 0.9539 over prediction-bearing rows,
and 0 verifier rows used.

The residual non-prediction audit now explains the 34 non-prediction rows: 26
abstain and 8 human review; 24 `trigger_conditioned_frequency`, 8
`last_event_boundary`, and 2 `missing_denominator_anchor`. Development
accounting shows the blocked source candidate was Purist-correct on 19 rows
and Purist-wrong on 15 rows, with 5 non-`unknown` gold rows. This argues for a
selective abstention-pressure review before any full-validation verifier use
or promotion.

The selective abstention-pressure review is now materialized. It classifies the
34 residual non-predictions into 19 coverage-cost rows and 15 protective
blocks. Review lanes are: 2 `trigger_release_candidate`, 13
`trigger_sentinel_boundary_review`, 8 `date_policy_needed`, 2
`anchor_policy_needed`, and 9 `keep_nonprediction`. The next change should be
a predeclared gold-blinded trigger-context release rule plus a frozen
last-event date policy, not a broad verifier release.

The abstention-policy predeclaration is now frozen. It allows only the 2
`trigger_release_candidate` rows to be considered for direct behavior change
under gold-blinded criteria, allows 0 automatic last-event releases until date
instrumentation exists, keeps sentinel trigger rows in boundary review, keeps
anchor rows abstained until stable anchor extraction exists, and keeps the 9
protective blocks as non-predictions.

The trigger-context release proposal is now materialized. Of the 2 considered
trigger release candidates, the stricter evidence rule releases 1 row (`5977`)
as `multiple per 6 week`; row `6319` remains unreleased because its selected
evidence does not itself name the event target. The proposed decision layer has
717 prediction-bearing rows, 25 abstain rows, 8 human-review rows, selective
Purist accuracy 0.9470, and selective Pragmatic accuracy 0.9540. This is still
a validation-development proposal, not a promoted behavior change.

The last-event date instrumentation prerequisite is now materialized over the
8 `date_policy_needed` rows. It finds 1 row with a full date (`11216`), 3 rows
with partial dates missing a year (`11272`, `14810`, `14821`), and 4 rows with
no explicit date in the selected evidence (`11254`, `11259`, `11262`, `11282`).
All 8 rows now have source-record reference-date anchors from `Clinic Date:` or
`Sent:` headers, but automatic release-ready rows remain 0 because auditable
duration derivation and conflict checks are not implemented. Last-event rows
therefore remain blocked from prediction-bearing behavior.

Core verifier artifacts live under
`docs/research/gan2026_selective_verifier_*2026-06-04.md`.

## Guardrails

- Split `gan2026_split_v1` is locked: 300 train, 750 validation, 450 holdout.
- Locked test is not for row-level tuning.
- `rules_only_v1` remains the frozen transparent comparator.
- Treat saturated aggregate validation scores as low-information.
- Any holdout-facing use needs a frozen predeclared audit and explicit user
  authorization; do not change scorer/gold policy from RQ10 alone.
- Final F1 is secondary to candidate recall, evidence exactness, projection
  consistency, metadata completeness, ambiguity preservation, and regression
  accounting.

## Work Board

### Now

- Add auditable duration derivation and conflict checks before any last-event
  automatic release; keep the trigger-context release proposal unpromoted
  pending review.

### Next

- Continue extracting prediction-bearing replay logic into component homes
  before adding it to the assembly file.
- If cost/latency/token efficiency is needed, run a telemetry-only pass over
  surviving primitives before strengthening RQ8 claims.

### Blocked

- Benchmark-comparable language remains blocked; current holdout evidence is a
  local frozen audit only.
- Whole-pipeline promotion is blocked until the family-indexed matrix is
  implemented as an auditable assembled candidate and any holdout-facing use
  has a frozen protocol.

### Done Recently

- 2026-06-04: Added the `last_event_date_instrumentation` component and
  materialized the staged-hybrid last-event date review. It covers the 8
  `date_policy_needed` rows, classifies 1 full-date row, 3 partial-date rows,
  and 4 rows with no explicit date in selected evidence. A follow-up source
  record join now finds reference-date anchors for all 8 rows, but keeps
  automatic release-ready rows at 0 until duration derivation and conflict
  checks exist.
- 2026-06-04: Added the `trigger_context_release_rule` component and
  materialized the proposed trigger-context release layer. The rule considered
  the 2 predeclared trigger release candidates and released 1 row (`5977`),
  raising the proposed prediction-bearing count from 716 to 717 while leaving
  last-event rows blocked pending date instrumentation.
- 2026-06-04: Added the `abstention_policy_predeclaration` component and
  materialized the staged-hybrid abstention-policy predeclaration. It freezes
  `trigger_context_release_rule_v0` and `last_event_date_policy_v0`, permits
  only 2 direct trigger release candidates for possible behavior change, and
  permits 0 last-event automatic releases until date instrumentation exists.
- 2026-06-04: Added the `selective_abstention_pressure` component and
  materialized the staged-hybrid pressure review: 34 rows, 19 coverage-cost
  rows, 15 protective blocks, 2 trigger release candidates, 13 trigger sentinel
  boundary reviews, 8 date-policy rows, 2 anchor-policy rows, and 9 rows to
  keep as non-predictions. It recommends a predeclared trigger-context release
  rule plus a frozen last-event date policy before behavior changes.
- 2026-06-04: Added the `residual_nonprediction_audit` component and
  materialized the staged-hybrid residual audit: 34 non-prediction rows, 26
  abstain, 8 human review, 24 trigger-conditioned rows, 8 last-event boundary
  rows, 2 missing-denominator rows, 19 blocked Purist-correct source
  candidates, and 15 blocked Purist-wrong source candidates. The recommended
  next step is selective abstention-pressure review.
- 2026-06-04: Added the `staged_decision_policy` component and materialized the
  validation750 no-call decision layer: 750 rows, 716 prediction-bearing rows,
  26 abstain, 8 human review, selective Purist accuracy 0.9469, selective
  Pragmatic accuracy 0.9539, and 0 verifier rows used.
- 2026-06-04: Materialized the validation750 no-call staged-hybrid assembly
  from the available full-validation component surfaces. The assembly has 750
  joined rows with reasoner replay, safety-floor gate, and RQ9 router present
  on every row; router actions are 716 predict, 26 abstain, and 8 human review.
  Historical reasoner prompt payload strings are omitted from the assembly
  rows.
- 2026-06-04: Added the `validation_surface_inventory` component and artifact
  for staged assembly inputs. The inventory confirms 750/750 coverage for
  `hybrid_reasoner_replay`, `selective_safety_floor_gate_v0`, and
  `rq9_selective_action_router_v3`; identifies missing module-shaped inputs for
  selected-state fact carrying, boundary-v3 selected-state candidates, and the
  promoted verifier; and records that old saved prompt payloads are historical
  evidence, not prompt text to reuse.
- 2026-06-04: Added ADR 0010 for component homes before pipeline assembly;
  extracted Gan source-trace, suspicious selected-state policy, and promoted
  selective-verifier components; added the first `staged_hybrid_assembly`
  no-call composition surface and focused component/assembly tests; materialized
  the saved assembly replay at 75 joined rows with 42 verifier rows, 0
  projection source-id inconsistencies, 7 verifier W->C, 1 verifier C->W
  (`7168`), 10 C->review, and 3 W->review.
- 2026-06-04: Adjudicated all 5 selective-verifier C->W regression rows and
  rejected v0 for prediction-bearing use; live-ran two plain-language verifier
  prompt designs, then a full-letter support-parts variant with 5 W->C and 1
  C->W, a binary quote/highest design with 7 W->C and 3 C->W, and a stronger
  binary prompt with 7 W->C, 1 C->W, and 10 C->review; promoted the stronger
  binary prompt and marked verifier prompt-design work complete for integration.
- 2026-06-04: Ran the frozen 42-row selective-verifier live readout with
  42/42 calls ok, 42/42 parseable outputs, 38/42 exact evidence-quote rows, 6
  W->C, 5 C->W, and changed-decision precision 0.522.
- 2026-06-04: Replayed staged hybrid assembly and suspicious routing with
  source-id tracing: 75/75 source-id-consistent rows, routing at 35
  `route_unknown`, 9 `route_review`, and 31 render rows.
- 2026-06-04: Added RQ6-RQ8 answers, RQ8 telemetry guard, ADR 0009, and the
  architecture readiness decision; telemetry remains incomplete at 0/21 rows.
