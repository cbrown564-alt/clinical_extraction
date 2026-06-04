# Gan 2026 Ambiguity Ownership Protocol

Date: 2026-06-04

Status: pre-run validation-development protocol. This protocol authorizes
comparing embedded selected-state ambiguity against deterministic
suspicious-state routing and selective LLM verification. It is not a
holdout-transfer, production, or benchmark-comparable claim.

## Question

Should ambiguity be owned primarily by the rich LLM selected-state schema and
consumed by deterministic policy, or does a post-state LLM verifier add reliable
no-regression value on suspicious ambiguous rows?

The component question is ambiguity ownership. It is not a final F1 experiment.

## Prior Evidence

RQ3 showed that rich selected-state fields can preserve clinically useful
ambiguity, especially for unknown boundaries, conditional states,
seizure-free blockers, and competing states. The strongest signal was typed
fact carrying, not direct final-label rendering.

RQ4 showed that benchmark-facing projection must be narrow, gated,
exact-evidence backed, and metadata-explicit. Broad LLM final-label projection
is unsafe.

Therefore the primary design should embed ambiguity inside the selected state
and let deterministic policy render, choose `unknown`, abstain, or route to
review. A post-state LLM verifier is a backup component that must prove
selective no-regression value.

## Fixed Surface

- Split manifest: `gan2026_split_v1`.
- Development surface: validation only.
- Locked holdout: no row-level inspection or tuning.
- Primary rows: saved rich selected-state hard-panel rows and candidate/evidence
  rows already used in RQ1-RQ4 validation-development analysis.
- Deterministic comparator: frozen safety floor and regression-risk reference.
- No new live model calls until suspicious-state checks and verifier schema are
  materialized and computable on saved rows.

## Components Compared

### Component A: Embedded Ambiguity Fields

Use the rich selected-state output as the prediction-bearing model state. The
LLM owns typed fact carrying:

- selected evidence;
- currentness;
- assertion/certainty;
- conditionality;
- ambiguity flags;
- competing hypotheses;
- seizure-free blockers;
- denominator/window uncertainty;
- cluster cadence and burden completeness;
- reason not directly renderable.

Deterministic policy owns:

- render a Gan-compatible label;
- choose `unknown`;
- abstain;
- route to review;
- preserve evidence/source-id attribution.

### Component B: Deterministic Suspicious-State Routing

Run deterministic checks over the selected state before final rendering.
Suspicious states should be routed to `unknown`, abstention, or optional review
without a new LLM decision.

Initial suspicious-state checks:

- `state_kind=frequency` with exclusive conditionality;
- `state_kind=frequency` with ambiguity fields that block a count;
- unresolved cluster cadence with per-cluster burden only;
- seizure-free state with recent-event blocker;
- seizure-free state with non-all-type scope and current nonzero events;
- competing current rates without a selected controlling semiology;
- diary/log date list without a defined observation window;
- denominator/window mismatch;
- vague trend or qualitative change without absolute current frequency;
- selected evidence missing exact trace.

### Component C: Selective LLM Verifier

Run only on predeclared suspicious-state slices. The verifier must not silently
override deterministic policy. It may recommend:

- render as selected state;
- render as `unknown`;
- abstain/review;
- choose among explicitly listed competing hypotheses.

The verifier must provide exact evidence references and a structured reason.
It must not invent new candidates outside the provided selected state and
competing hypotheses.

## Artifact Schema

Each source-row record should include:

- `source_row_index`;
- `split`;
- `gold_label`, for development scoring only;
- `hidden_families`;
- `selected_state`;
- `selected_evidence_status`;
- `embedded_ambiguity_fields`;
- `deterministic_policy_label`;
- `deterministic_policy_action`;
- `suspicious_state_flags`;
- `suspicious_state_action`;
- `llm_verifier_input`, when eligible;
- `llm_verifier_output`, when run;
- `final_policy_under_test`;
- `w_to_c_or_c_to_w_against_comparator`;
- `first_failure_owner`;
- `claim_boundary`.

## Metrics

Primary metrics:

- ambiguity-field completeness;
- suspicious-state flag rate;
- correct `unknown` or abstention decisions;
- W->C and C->W versus deterministic policy;
- deterministic-correct regression count;
- exact-evidence/source-id preservation;
- verifier recommendation parse validity;
- verifier changed-decision precision.

Hidden-family readouts:

- unknown boundary;
- no-reference boundary;
- seizure-free duration and overreach;
- current versus historical;
- competing semiologies;
- cluster burden;
- diary/log aggregation;
- rate bucket or denominator;
- benchmark convention dominated rows.

## Decision Rules

Prefer embedded ambiguity plus deterministic policy if it preserves exact
evidence, avoids deterministic-correct regressions, and routes uncertain rows
to `unknown`, abstention, or review with clear flags.

Promote deterministic suspicious-state routing if it prevents wrong rendering
without hiding upstream selected-state failures.

Allow selective LLM verifier use only if it shows high-precision W->C changes
with zero or near-zero C->W regressions on a predeclared suspicious slice. If it
adds useful explanations but not reliable decisions, keep it as an audit/report
component rather than a prediction-bearing component.

## Negative Result Criteria

The LLM verifier should be rejected or confined to audit-only status if:

- it changes deterministic-correct rows incorrectly;
- it relies on evidence outside the selected state without a predeclared
  candidate-rescue role;
- it collapses uncertainty into overconfident final labels;
- it cannot preserve source-id/evidence attribution;
- its gains are limited to validation-specific benchmark conventions.

## Stop Rule

First run deterministic suspicious-state checks over saved rich selected-state
artifacts. Do not run a verifier until the suspicious slices are stable and the
artifact can report W->C/C->W against the frozen comparator.

If the deterministic suspicious-state pass already resolves the named ambiguity
families without regressions, the verifier remains a backup and no new model
call is needed.

## Claim Boundary

This protocol supports validation-development component analysis only. It does
not authorize locked-test inspection, whole-pipeline promotion, scorer/gold
policy change, or benchmark-comparable language.
