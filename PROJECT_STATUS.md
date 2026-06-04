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

Candidate-union and boundary-proposer artifacts are materialized. Saved union
recall improved from 25/75 deterministic rows to 47/75, with 22 saved boundary
rescues, 0 deterministic-recall losses, exact evidence/source-id rates of 1.000,
median 2 and p90 3 retained candidates. The controlled v3 live replay on the
same 22-row rescue slice is the current proposer surface: 22/22 parseable,
16/22 exact-label candidate recall, 21/22 Purist recall, 21/22 saved-rescue
evidence overlap, and 7 rejected candidates. V3 fixed rows 9943, 10996, and
12456; row 15593 remains a real model error mapping `five days without seizures
followed by a cluster` to `1 cluster per day` instead of `1 cluster per 5 day`.
The no-call selected-state replay over the gated v3 boundary-candidate union is
complete: primary v3 candidate-state projection is 16/22 on the v3 slice and
would create 6 C->W changes if promoted as a label policy; the deterministic
safety-floor replay keeps 37/75 correct with 0 W->C and 0 C->W changes. Row
15593 is carried as the known real v3 cluster-cadence model error, so v3 remains
a useful selected-state input surface but not a final-label policy.

Suspicious selected-state routing and verifier predeclaration are materialized:
44/75 rows flagged, 35 routed to `unknown`, 9 to review, 1 W->C and 6 C->W
versus the deterministic comparator. The verifier slice has 42 exact-evidence
eligible rows; rows 1695 and 6094 are excluded for non-exact evidence.

RQ9 abstention/human-review routing is predeclared from the saved RQ10 residual
miss classes. The policy covers 53 validation residual Purist misses, blocks
prediction-bearing use for 34 rows through abstention or human review, and keeps
19 rows as true extraction failures for component debugging. It does not change
labels, scorer policy, projection policy, or locked-test claims.

Human review of the validation750 gold/reference ambiguity worklist now has 140
unique adjudicated rows. The qualitative report
`docs/research/gan2026_human_gold_audit_abstention_policy_report_2026-06-04.md`
finds that `unknown`, drop-attack, trigger-only, last-event, cluster, and
since-anchor cases require an explicit abstention/human-review policy with
coverage and over-abstention accounting.

## Active Question

Candidate Union And Ambiguity Ownership

Question: should candidate breadth come from parallel deterministic and
selective LLM candidate proposal with a gated union, and should ambiguity live
inside the rich selected state before deterministic render/unknown/abstain/review
policy?

Status: candidate-union, selective boundary-candidate, suspicious-state routing,
selected-state union replay, verifier predeclarations, and RQ9 abstention/review
routing are materialized on saved artifacts. The current answer is parallel
deterministic plus gated selective boundary-candidate proposal, rich
selected-state fact carrying, and deterministic render/unknown/review policy. V3
boundary candidates should feed selected state as an input surface only;
promoting primary v3 candidate-state projection as policy would regress 6
deterministic-correct rows. A selective verifier remains a predeclared backup
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
  `selected_state_union_replay.py`, `suspicious_selected_state_routing.py`, and
  `selective_verifier_predeclaration.py`.
- Experiment outputs:
  `experiments/gan2026_candidate_union_saved_artifact_2026-06-04.*`,
  `gan2026_selective_boundary_candidate_predeclaration_2026-06-04.*`,
  `gan2026_selective_boundary_candidate_experiment_2026-06-04.*`,
  `gan2026_selected_state_union_replay_v3_2026-06-04.*`,
  `gan2026_suspicious_selected_state_routing_2026-06-04.*`, and
  `gan2026_selective_verifier_predeclaration_2026-06-04.*`.
- RQ9 abstention/review artifacts:
  `docs/research/gan2026_rq9_abstention_review_predeclaration_2026-06-04.md`
  and `experiments/gan2026_rq9_abstention_review_predeclaration_2026-06-04.*`.

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

- Convert the human Gold Audit findings into an RQ9 follow-up selective-action
  evaluation contract: coverage, selective accuracy, abstention/review rate, and
  over-abstention accounting.

### Next

- Define the explicit `unknown` and drop-attack boundary policy used by the
  selective-action router before scoring any new surface.

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

- 2026-06-04: Wrote the human Gold Audit abstention-policy report from 140
  unique manual validation worklist decisions. The report supports an explicit
  unknown/drop-attack/trigger/cluster human-review policy and requires selective
  accuracy to be paired with coverage and over-abstention metrics.
- 2026-06-04: Backfilled legacy `source_id_status` validation for the 200
  earlier `balanced_validation50` isolated-control rows in the RQ1/RQ2 component
  matrix: 142 are valid and 58 are explicitly `not_instrumented` by design
  (8 candidate-only rows emitted no candidates/source ids; projection-only emits
  fixed candidate ids rather than source ids). Completed matrix rows now have
  0/1000 missing `source_id_status`.
- 2026-06-04: Predeclared RQ9 abstention/human-review routing from RQ10 classes.
  The policy covers 53 residual validation Purist misses, blocks
  prediction-bearing use for 34 rows through abstention or review, and keeps 19
  rows as true extraction failures; no scorer, label, projection, or locked-test
  policy change is authorized.
- 2026-06-04: Completed no-call selected-state replay over the gated v3
  boundary-candidate union. Primary v3 candidate-state projection is 16/22 and
  would create 6 C->W changes if promoted; safety-floor replay remains 37/75
  with 0 W->C and 0 C->W. Row 15593 is carried as the known real v3
  cluster-cadence model error.
- 2026-06-04: Revised and ran selective boundary-candidate v1-v3 on the same
  22 validation rows. V3 is best on parse/Purist behavior: 22/22 parseable,
  16/22 exact-label recall, 21/22 Purist recall, 21/22 saved-rescue evidence
  overlap, 7 rejected candidates; it fixed rows 9943, 10996, and 12456 but not
  row 15593.
- 2026-06-04: Materialized candidate-union, selective boundary-candidate,
  suspicious-routing, and selective verifier artifacts on saved validation
  hard-panel rows.
- 2026-06-04: Completed RQ1/RQ2/RQ3/RQ4/RQ5/RQ10 development-control artifacts,
  prompt-language cleanup, projection replay, and validation750 ambiguity
  inventory.
- 2026-06-03: Reset RQ1/RQ2/RQ4 interpretation and added the mechanism
  protocol, synthesis, error analysis, and 195-row mechanism artifact.
