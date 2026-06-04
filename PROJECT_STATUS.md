# Project Status

Last updated: 2026-06-04

## Active Objective

Answer the Gan 2026 seizure-frequency component research questions one at a
time under exact-evidence, attribution, hidden-family, and split-discipline
constraints. No holdout or benchmark-comparable claim is authorized.

## Current Strategy

Use saved artifacts as research instruments for clean component questions, not
whole-pipeline validation F1. Deterministic rules are frozen comparators, safety
floors, and miss-slice definers, not eligible answers for RQ1-RQ4.

RQ10 is answered for saved validation replay: among 53 residual Purist misses,
23 are `underdetermined_note`, 19 are `true_extraction_failure`, and 11 are
`benchmark_convention_dominated`; 0 are strong likely gold defects. A full
validation750 gold/reference review CSV exists for manual adjudication.

RQ3 rich selected-state is answered for the focused five-row surface and the
75-row hidden-family hard panel. It supports the architecture as a typed fact
carrier, not direct LLM label rendering; no-call projection replay improved
orientation-exact labels from 26/75 to 37/75 with 0 right-to-wrong changes.

The current architecture decision is documented in
`docs/research/gan2026_candidate_union_and_ambiguity_ownership_report_2026-06-04.md`:
test parallel deterministic plus selective LLM candidate proposal with a gated
union, and keep ambiguity primarily inside the rich selected state before
deterministic render/unknown/abstain/review policy. A post-state LLM verifier is
a backup for predeclared suspicious-state slices only.

Candidate-union and boundary-proposer predeclarations are materialized on saved
artifacts: union recall improved from 25/75 deterministic rows to 47/75, with 22
saved boundary-proposal rescues, 0 deterministic-recall losses, exact
evidence/source-id rates of 1.000, median 2 and p90 3 retained candidates. The
predeclared live-call surface is exactly those 22 validation rescue rows, with a
plain prompt/schema and no final-label use.
The first controlled live boundary-proposer run on that surface completed with
22/22 calls, 20/22 parseable rows after format-only schema repair, 15/22
exact-label candidate recall, 16/22 Purist candidate recall, all retained
candidate evidence exact, median 3 and p90 4 retained candidates. This is a
revise signal: useful selective rescue, but cluster labels and enum/schema
ambiguity needed cleanup before downstream selected-state replay. The v1
predeclaration now renders enum fields as scalar "one string value" fields and
adds explicit cluster-burden support for `multiple per cluster`, cadence ranges,
and `unknown, N per cluster` labels. The controlled v1 replay on the same 22
rows produced 22/22 calls, 20/22 parseable rows, 15/22 exact-label recall, 17/22
Purist recall, 20/22 saved-rescue evidence overlap, and fewer rejected
candidates (13 vs 24), but still failed parse stability through
`assertion_status=no_reference` and still missed several exact cluster labels.
The v2 predeclaration now pins `no_reference` candidates to
`assertion_status=asserted`, keeps seizures-per-cluster out of rate count
fields, preserves exact cluster low/high burden over generic multiple flags, and
diagnostically reparses all 22 saved v1 raw outputs with 0 parse-error rows.
The controlled v2 replay completed with 22/22 calls, 21/22 parseable rows, 16/22
exact-label candidate recall, 20/22 Purist recall, 21/22 saved-rescue evidence
overlap, and 10 rejected candidates. This is directionally better than v1 but
still a revise signal before selected-state replay: row 12456 omitted required
`reason`, and cluster exact labels still miss rows 9943, 10996, and 15593.
The v3 predeclaration adds a format-only missing-`reason` repair plus explicit
cluster-cadence examples for four-to-five-week periods, one-to-two-per-month
cluster counts, and seizure-free intervals followed by a cluster. The controlled
v3 replay completed with 22/22 calls, 22/22 parseable rows, 16/22 exact-label
candidate recall, 21/22 Purist recall, 21/22 saved-rescue evidence overlap, and
7 rejected candidates. V3 fixed rows 9943, 10996, and 12456. Row 15593 remains a
real model error: it maps `five days without seizures followed by a cluster` to
`1 cluster per day` instead of `1 cluster per 5 day`; do not repair this before
selected-state replay.

Suspicious selected-state routing and verifier predeclaration are materialized:
44/75 rows flagged, 35 routed to `unknown`, 9 to review, 1 W->C and 6 C->W
versus the deterministic comparator. The verifier slice has 42 exact-evidence
eligible rows; rows 1695 and 6094 are excluded for non-exact evidence.

## Active Question

Candidate Union And Ambiguity Ownership

Question: should candidate breadth come from parallel deterministic and
selective LLM candidate proposal with a gated union, and should ambiguity live
inside the rich selected state before deterministic render/unknown/abstain/review
policy?

Status: candidate-union, selective boundary-candidate, suspicious-state routing,
and verifier predeclarations are materialized on saved artifacts. The current
answer is parallel deterministic plus gated selective boundary-candidate
proposal, rich selected-state fact carrying, and deterministic
render/unknown/review policy. A selective verifier remains a predeclared backup
for stable suspicious slices because naive deterministic unknown-routing caused
6 C->W regressions.

Core artifacts:

- Architecture report/protocols:
  `docs/research/gan2026_candidate_union_and_ambiguity_ownership_report_2026-06-04.md`,
  `gan2026_candidate_union_protocol_2026-06-04.md`, and
  `gan2026_ambiguity_ownership_protocol_2026-06-04.md`.
- New predeclarations:
  `docs/research/gan2026_selective_boundary_candidate_predeclaration_2026-06-04.md`
  and `docs/research/gan2026_selective_verifier_predeclaration_2026-06-04.md`.
- Artifact-analysis code:
  `candidate_union.py`, `selective_boundary_candidate_predeclaration.py`,
  `selective_boundary_candidate_experiment.py`,
  `suspicious_selected_state_routing.py`, and
  `selective_verifier_predeclaration.py`.
- Experiment outputs:
  `experiments/gan2026_candidate_union_saved_artifact_2026-06-04.*`,
  `gan2026_selective_boundary_candidate_predeclaration_2026-06-04.*`,
  `gan2026_selective_boundary_candidate_experiment_2026-06-04.*`,
  `gan2026_suspicious_selected_state_routing_2026-06-04.*`, and
  `gan2026_selective_verifier_predeclaration_2026-06-04.*`.

## Guardrails

- Split `gan2026_split_v1` is locked: 300 train, 750 validation, 450 holdout;
  locked test is not for row-level tuning.
- `rules_only_v1` remains the frozen transparent comparator.
- Treat saturated aggregate validation scores as low-information.
- Do not treat "deterministic top still wins" as an RQ1-RQ4 answer.
- Any holdout-facing use needs a frozen predeclared audit or must keep the claim
  validation-only.
- Do not change scorer/gold policy from RQ10 alone; use it to design abstention,
  review routing, or a separate policy predeclaration.
- Isolated controls must be interpreted before paired-task prompts; final F1 is
  secondary to candidate recall, evidence exactness, projection consistency,
  metadata completeness, ambiguity preservation, and regression accounting.

## Work Board

### Now

- Proceed to selected-state replay over the gated v3 boundary-candidate union,
  carrying row 15593 as a known real model cluster-cadence error.

### Next

- Predeclare RQ9 abstention/human-review routing using the RQ10 audit classes.
- Review the validation750 gold/reference ambiguity CSV and replace the
  heuristic `codex_initial_ambiguity_label` with manual adjudication.
- Fill legacy `source_id_status` validation for the 200 earlier
  `balanced_validation50` isolated-control rows that predate recursive source-id
  instrumentation.

### Backlog

- Rewrite `llm_only_minimal_evidence_selector.py` under the prompt-language
  audit before any new minimal-evidence calls.
- RQ5 follow-up implementation only if a non-state-graph selected-state surface
  exposes fixed bundles that need rendering audit.

### Blocked

- Benchmark-comparable language remains blocked; current holdout evidence is a
  local frozen audit only.
- Whole-pipeline promotion is blocked until component questions are answered.

### Done Recently

- 2026-06-04: Revised and ran selective boundary-candidate v3 on the same 22
  validation rows: 22/22 parseable, 16/22 exact-label recall, 21/22 Purist
  recall, 21/22 saved-rescue evidence overlap, 7 rejected candidates. V3 fixed
  rows 9943, 10996, and 12456; row 15593 is accepted as a real model
  cluster-cadence error rather than a prompt-repair target.
- 2026-06-04: Ran the controlled selective boundary-candidate v2 replay on the
  same 22 validation rows: 21/22 parseable, 16/22 exact-label recall, 20/22
  Purist recall, 21/22 saved-rescue evidence overlap, 10 rejected candidates.
  Directionally improved over v1 but still revise before selected-state replay.
- 2026-06-04: Revised selective boundary-candidate to v2: prompt/schema now
  pins `no_reference` assertion aliasing and exact cluster-label specificity;
  parser/rendering tests cover `assertion_status=no_reference` repair and exact
  cluster low/high burden precedence; saved v1 raw-output diagnostic reparse is
  22/22 parseable with no new model calls.
- 2026-06-04: Ran the controlled selective boundary-candidate v1 replay on the
  same 22 validation rows: 20/22 parseable, 15/22 exact-label recall, 17/22
  Purist recall, 20/22 saved-rescue evidence overlap, 13 rejected candidates;
  revise before selected-state replay.
- 2026-06-04: Revised the selective boundary-candidate prompt/schema to v1:
  scalar enum wording in rendered model inputs plus cluster-burden rendering for
  multiple-per-cluster, cadence ranges, and unknown-cadence burden labels.
- 2026-06-04: Materialized the selective boundary-candidate predeclaration:
  stop/go `go`, 22 exact saved recall-rescue validation rows, plain
  prompt/schema, max 4 proposed candidates per row, and no final-label use.
- 2026-06-04: Ran the controlled live selective boundary-candidate experiment:
  22/22 calls, 20/22 parseable rows after format repair, 15/22 exact and 16/22
  Purist candidate recall, all retained evidence exact, with cluster/schema
  misses requiring revision before selected-state replay.
- 2026-06-04: Materialized candidate-union, suspicious-routing, and selective
  verifier artifacts on saved validation hard-panel rows.
- 2026-06-04: Completed RQ1/RQ2/RQ3/RQ4/RQ5/RQ10 development-control artifacts,
  prompt-language cleanup, projection replay, and validation750 ambiguity
  inventory.
- 2026-06-03: Reset RQ1/RQ2/RQ4 interpretation and added the mechanism
  protocol, synthesis, error analysis, and 195-row mechanism artifact.
