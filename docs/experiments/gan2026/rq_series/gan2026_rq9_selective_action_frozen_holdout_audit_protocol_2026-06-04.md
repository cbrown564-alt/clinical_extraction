> **Superseded for navigation —** canonical summary: [`COMPONENT_MECHANICS_CANON.md`](../COMPONENT_MECHANICS_CANON.md). Full detail retained below.

# Gan 2026 RQ9 Selective-Action Frozen Holdout Audit Protocol

- Date: 2026-06-04
- Research question: RQ9 abstention and human review
- Router: `gan2026_rq9_selective_action_router_v3`
- Source candidate: `hybrid_adjudicator_with_adapters`
- Source artifact:
  `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl`
- Split manifest: `gan2026_split_v1`
- Holdout surface: locked `test` split, 450 rows

## Decision

Freeze a holdout-facing audit protocol for the RQ9 selective-action policy
before any locked-test use. This protocol does not run holdout and does not
authorize row-level locked-test inspection. It defines the only conditions under
which a future RQ9 holdout audit would be interpretable.

The audit question is whether the validation-frozen selective-action policy can
separate prediction-bearing, abstention, human-review, and monitoring cases on
locked test without tuning. It is not a final pipeline promotion, scorer update,
gold rewrite, production policy, or benchmark-comparable claim.

## Frozen Claim Language

Any future result under this protocol must be described as:

- a frozen holdout audit of a validation-developed RQ9 selective-action policy;
- a selective-action result around a saved hybrid source candidate, not an
  LLM-first extraction result;
- a coverage, selective-accuracy, abstention, review, and monitoring audit, not
  a whole-pipeline F1 optimization;
- not benchmark-comparable unless a separate benchmark-replication protocol is
  written before reporting.

If the router, source candidate, scorer, prompt, model, projection policy,
boundary policy, monitoring policy, or split manifest changes after this
protocol, cancel this audit and return to validation.

## Frozen Evidence Base

Use these validation-development artifacts as the frozen basis:

- RQ9 evaluation contract:
  ``
- RQ9 validation answer:
  ``
- Unknown/drop-attack boundary policy:
  ``
- Trigger-context narrowing predeclaration:
  ``
- Last-event boundary decision:
  `experiments/gan2026_rq9_last_event_boundary_decision_2026-06-04.*`
- Cluster/convention monitoring predeclaration and artifact:
  ``
  and `experiments/gan2026_rq9_cluster_convention_monitoring_2026-06-04.*`
- V3 router artifacts:
  `experiments/gan2026_rq9_selective_action_router_v3_2026-06-04.*`
- V3 pressure-point artifacts:
  `experiments/gan2026_rq9_selective_action_router_v3_pressure_points_2026-06-04.*`

The validation-frozen v3 router covers 716/750 rows, abstains on 26, routes 8
to human review, routes 0 to extraction-error analysis, and has covered-row
Purist accuracy 0.9469. The cluster/convention monitoring artifact keeps all
115 eligible rows prediction-bearing while marking 61 as high-priority verifier
monitoring and 54 as routine monitoring.

## Frozen Router Policy

Every eligible holdout row must receive exactly one action:

- `predict`
- `abstain`
- `human_review`
- `extraction_error_analysis`

The v3 router policy is frozen as:

- predict ordinary frequency, seizure-free, no-reference, stable `unknown`,
  cluster/convention, and gold-blinded trigger-context rows;
- abstain true trigger-only or unquantified trigger-conditioned rows;
- abstain missing-denominator-anchor rows;
- route last-event boundary rows to human review;
- keep cluster/convention rows prediction-bearing and assign verifier
  monitoring priority separately from router action.

The router must not use gold labels, gold references, human audit classes,
test correctness, or row-level test failure status as inputs.

## Frozen Source Candidate

The prediction-bearing source candidate is `hybrid_adjudicator_with_adapters`
from the saved validation source artifact named above. Before any locked-test
run, the test artifact must record the corresponding runnable source-candidate
entry point, layer name, prompt/model or no-call mode, scorer module, and output
paths.

No new source candidate, fallback label, repair path, normalization rule,
projection rule, scorer mapping, model setting, cache setting, or prompt text may
be introduced for locked test under this protocol.

## Monitoring Slices

The following slices are frozen for holdout aggregate reporting. Slice
membership must be computed without reading row-level test failures.

Router action slices:

- `predict`
- `abstain`
- `human_review`
- `extraction_error_analysis`

Primary reason slices:

- `plain_predictable_frequency`
- `plain_predictable_seizure_free`
- `plain_no_reference`
- `unknown_frequency_unquantified`
- `trigger_conditioned_frequency`
- `missing_denominator_anchor`
- `last_event_boundary`

Cluster/convention monitoring slices:

- all prediction-bearing rows with `cluster_or_per_cluster_convention`
- `cluster_structured_prediction`
- `plain_frequency_with_cluster_context`
- `seizure_free_with_cluster_context`
- `sentinel_no_reference_with_cluster_context`
- `high_priority_verifier_monitoring`
- `routine_monitoring`

Gold-label-kind aggregate slices are allowed only as aggregate counts and
metrics:

- `frequency`
- `seizure_free`
- `unknown`
- `unresolved_multiple`
- `no_reference`

Text-pattern monitoring slices may use predeclared gold-blinded indicators:

- cluster markers: `cluster`, `clusters`, `clustered`, `per cluster`
- trigger markers: `trigger`, `provoked`, `sleep-deprived`,
  `when sleep-deprived`, `during illness`, `with missed medication`
- last-event markers: `last seizure`, `last event`, `last episode`
- uncertainty markers: `unclear`, `uncertain`, `difficult to quantify`,
  `variable`
- anchor markers: `since`, `over the past`, `in the last`, `per`, `every`

## Required Metrics

Report all metrics on the full locked-test surface and by each predeclared slice
where the denominator is nonzero:

- eligible rows;
- covered rows;
- abstained rows;
- human-review rows;
- extraction-error-analysis rows;
- coverage;
- abstention rate;
- human-review rate;
- selective accuracy among `predict` rows;
- Purist and Pragmatic counts for source candidate predictions;
- action-specific Purist and Pragmatic counts;
- wrong-to-correct and correct-to-wrong counts versus the source candidate when
  a non-prediction action blocks a source prediction;
- rescue value rate for blocked unsafe source predictions;
- over-abstention and over-review rates where reviewed human labels are
  available;
- hidden-error rate for true extraction failures routed away from
  `extraction_error_analysis`;
- exact-evidence availability;
- valid source-id availability;
- schema, parse, scorer-invalid, and missing-packet counts.

Do not report selective accuracy without coverage, abstention, human-review, and
monitoring burden.

## Pre-Run Checks

Before any locked-test command, record:

- repo commit hash and dirty-worktree status;
- split manifest path and hash;
- router version and implementation entry point;
- source-candidate version and implementation entry point;
- scorer module and Purist/Pragmatic category policy;
- boundary-policy document hashes;
- monitoring-policy document hash;
- output paths for locked-test router JSONL, summary JSON, Markdown report,
  review-packet JSONL, and monitoring JSONL;
- confirmation that locked-test row text, labels, row-level failures, and
  examples have not been inspected to tune this router;
- targeted tests or artifact validators used before execution.

If any check fails, stop. Do not run locked test.

## Allowed First Readout

The first locked-test readout may include only:

- full-surface aggregate metrics listed above;
- predeclared slice aggregate metrics listed above;
- counts of actions and primary reasons;
- monitoring counts by frozen cluster/convention group and verifier priority;
- evidence, source-id, parse, schema, scorer-invalid, and packet-validity
  aggregate counts;
- changed-action accounting versus the frozen source candidate.

The first readout must not list locked-test row ids, note text, evidence
snippets, predicted labels, gold labels, gold references, or row-level failure
examples.

## Permitted Post-Run Inspection

Row-level locked-test inspection is permitted only after the first readout has
been written and frozen. It is final-evaluation analysis, not development.

Permitted post-run inspection:

- review gold-blinded packets for rows routed to `abstain` or `human_review`;
- review monitoring packets for high-priority cluster/convention rows;
- inspect row-level failures only to write a holdout finding;
- compare packet validity against the frozen contract.

Not permitted:

- changing router logic, source-candidate logic, scorer policy, prompts, model
  settings, projection policy, boundary policy, monitoring policy, or
  normalization based on holdout rows;
- rerunning a patched candidate as the same audit;
- using row-level holdout examples for a new claim without marking the analysis
  post-hoc;
- converting monitoring priority into human-review routing after seeing test
  outcomes.

Any fix motivated by locked-test row-level review starts a new validation-cycle
candidate and requires a separate future holdout protocol.

## Stop Rules

Accept the audit as valid only if:

- every frozen input and pre-run check was recorded before execution;
- no row-level locked-test inspection occurred before the first readout;
- all rows have exactly one action;
- non-prediction packets are gold-blinded and evidence-bearing or explicitly
  marked `no_exact_evidence`;
- first-readout reporting stays aggregate and predeclared-slice only;
- no policy or implementation change is required to interpret the result.

Mark revise-only or reject if:

- the result requires a router, scorer, prompt, model, projection, boundary, or
  monitoring-policy change;
- evidence or source-id validity fails systemically;
- a high monitoring burden makes prediction-bearing cluster/convention use
  uninterpretable;
- abstention or human review hides true extraction failures;
- selective accuracy is high only because coverage collapses;
- row-level locked-test tuning is needed to make the result useful.

## Immediate Next Action

Do not run locked test from the validation RQ9 artifacts. If holdout use is
explicitly authorized later, first create or verify the runnable command against
this protocol, record the frozen inputs and pre-run checks, and only then execute
the locked-test audit.
