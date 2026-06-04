# Gan 2026 RQ7 Family-Indexed Component Matrix Answer

Date: 2026-06-04

Status: answered for validation-development family-indexed architecture
guidance. This is not a per-family holdout-transfer or benchmark-comparable
claim.

## Answer

RQ7 is now answered for saved validation artifacts:

```text
The architecture generalizes best by assigning each hidden-family burden to the
component that is operationally strongest there: LLM evidence gating for
source-grounding, selective LLM candidate proposal for boundary/ambiguity
exposure, rich selected state for fact carrying, and deterministic gated
projection/safety-floor policy for label-changing action.
```

The family-indexed matrix confirms the main pattern:

- `candidate_conditioned_evidence_only` is stable across hard families, with
  exact evidence at or above 0.9259 and valid source ids at 1.0000 on the major
  family memberships.
- `candidate_only` exposes useful states, but source-id/evidence quality is
  weaker on seizure-free duration, current-vs-historical, diary/log, and
  cluster rows.
- `selective_boundary_candidate_proposer_v2` is strongest exactly where it is
  supposed to be narrow: unknown boundary and seizure-free duration, with
  Purist candidate recall 1.0000 and exact-label recall 0.9231 and 0.9167
  respectively.
- `rich_selected_state_v0` carries family facts with high evidence/trace
  validity, including 1.0000 on unknown boundary and seizure-free duration, but
  source-id instrumentation is not materialized and policy checks remain
  necessary.
- `selective_safety_floor_gate_v0` is the safest action layer on validation:
  no C->W changes in the family-indexed changed rows, with strongest W->C gains
  in unknown boundary, uncertainty/ambiguity, seizure-free duration,
  current-vs-historical, and competing-semiology families.

## Claim Boundary

Supporting artifacts:

- `experiments/gan2026_rq7_family_component_matrix_2026-06-04.json`
- `experiments/gan2026_rq7_family_component_matrix_2026-06-04.md`
- `docs/research/gan2026_rq7_hidden_family_generalization_synthesis_2026-06-04.md`
- `docs/research/gan2026_rq8_efficiency_operational_reliability_answer_2026-06-04.md`
- `experiments/gan2026_rq1_rq2_component_control_matrix_2026-06-04.*`
- `experiments/gan2026_rich_selected_state_hard_panel_2026-06-04.*`
- `experiments/gan2026_selective_boundary_candidate_experiment_v2_2026-06-04.*`
- `experiments/gan2026_selective_safety_floor_gate_v0_validation750_replay_2026-06-03.*`

Families are multi-label, so row memberships are not mutually exclusive. The
frozen test readout does not expose hidden-family tags; frozen-test RQ6 remains
slice-level only. This matrix therefore supports architecture guidance, not
family-specific holdout claims.

## Family Readout

| Family | Best-supported component behavior | Residual risk |
| --- | --- | --- |
| `unknown_boundary` | Candidate-conditioned evidence exact 0.9500; rich selected state 1.0000; boundary proposer exact recall 0.9231/Purist recall 1.0000; selective safety floor 10 changed, 9 W->C, 0 C->W. | Holdout family tags missing; keep safety floor and abstention policy. |
| `uncertainty_or_ambiguity` | Candidate-conditioned evidence exact 0.9615; rich selected state 0.9667; boundary proposer exact recall 0.875/Purist recall 1.0000; selective safety floor 11 changed, 9 W->C, 0 C->W. | Ambiguity can still be benchmark-convention dominated; route/review stays important. |
| `seizure_free_duration` | Rich selected state 1.0000; boundary proposer exact recall 0.9167/Purist recall 1.0000; selective safety floor 10 changed, 8 W->C, 0 C->W. | Candidate-only evidence/source-id quality is weaker; overreach remains a broad-projection risk. |
| `current_vs_historical` | Candidate-conditioned evidence exact 0.9487/source ids 1.0000; rich selected state 0.9762; selective safety floor 8 changed, 6 W->C, 0 C->W. | Requires explicit currentness policy; direct LLM projection remains rejected. |
| `competing_semiologies` | Candidate-only exact 0.9730; rich selected state 0.9756; selective safety floor 6 changed, 5 W->C, 0 C->W. | Final event priority must be policy-mediated. |
| `rate_bucket_or_denominator` | Candidate-conditioned evidence exact/source ids 1.0000; selective safety floor 3 changed, 2 W->C, 0 C->W. | Boundary proposer exact-label recall is only 0.5000; typed operations/A2 showed denominator drift. |
| `cluster_burden` | Candidate-conditioned evidence exact/source ids 1.0000; rich selected state 1.0000; selective safety floor 2 changed, 1 W->C, 0 C->W. | Candidate proposer exact recall is 0.5000; cluster cadence vs burden remains unresolved. |
| `diary_or_log_aggregation` | Candidate-conditioned evidence exact/source ids 1.0000; selective safety floor 2 changed, 1 W->C, 0 C->W. | Small family membership and ACD policy reliance; needs explicit aggregation policy. |
| `benchmark_format_convention` | Candidate-conditioned evidence exact/source ids 1.0000; selective safety floor 3 changed, 2 W->C, 0 C->W. | RQ10 shows convention-dominated rows should not drive hidden scorer overfit. |

## Architecture Decision

The family-indexed matrix closes RQ7 as architecture guidance:

1. Keep `candidate_conditioned_evidence_only` as the default cross-family
   evidence gate.
2. Use `candidate_only` and `selective_boundary_candidate_proposer_v2` only as
   candidate-exposure components, not final selectors.
3. Carry `rich_selected_state_v0` forward as the fact/state carrier, but
   require source-id instrumentation and deterministic consistency checks.
4. Let `selective_safety_floor_gate_v0` remain the only current label-changing
   action pattern.
5. Keep cluster, diary, denominator, and benchmark-convention families behind
   explicit projection/abstention/review policies.

## Transfer Confidence

| Finding | Development confidence | Holdout-transfer confidence | Reason |
| --- | --- | --- | --- |
| Evidence gating is stable across hidden families. | High | Moderate | Hard-panel family exactness/source-id rates are strong. |
| Boundary candidate proposal is useful but narrow. | High | Low-to-moderate | Rescue slice is predeclared but validation-derived and higher-burden. |
| Rich selected state is the right fact carrier. | Moderate-to-high | Low-to-moderate | Family validity is strong, but source-id instrumentation and broader replay are incomplete. |
| Selective safety-floor action is safer than replacement. | High | Moderate | Validation family rows and frozen slice-level audit agree on no-regression behavior. |
| Cluster/diary/denominator conventions are solved. | Low | Low | These remain the families needing explicit policy or review. |

## Remaining Work

No additional broad validation experiment is needed. The remaining work is
architecture assembly under the now-answered component constraints:

- materialize source ids for rich selected-state rows;
- add deterministic consistency checks for suspicious selected states;
- keep selective verifier work limited to predeclared suspicious slices;
- predeclare any holdout-facing audit before running or inspecting locked-test
  row-level outputs.
