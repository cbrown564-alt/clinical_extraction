# Gan 2026 Component Architecture Reset Outstanding Plan

Date: 2026-06-05

Status: review questions resolved on 2026-06-06. Completed decisions,
generated artifacts, row reviews, and implementation notes have been moved to
`docs/research/gan2026_component_architecture_reset_completed_tasks_2026-06-05.md`.

This plan does not authorize new holdout work, benchmark-comparable claims, or
row-level locked-test review.

## Current Position

The reset has reached a clean verifier/action boundary:

- extraction, candidate-set, clinical-assessment, projection/render,
  score-policy, verification-route, and deterministic verification-action V0
  mechanics have all been implemented on `validation250`;
- route V6 contains 5 routed rows, all null-rendered risk families;
- `VerificationDecision` V0 emits deterministic baseline actions over those 5
  routed rows: 4 `abstain` and 1 `human_review`;
- no remaining route V6 row receives a replacement scorer-facing label.

Active mechanics artifacts:

- Projection/render:
  `experiments/gan2026_clinical_assessment_projection_render_validation250_v7.jsonl`
- Score-policy audit:
  `experiments/gan2026_clinical_assessment_projection_score_validation250_v6.jsonl`
- Verification-route report:
  `experiments/gan2026_validation250_verification_route_v6.jsonl`
- VerificationDecision baseline:
  `experiments/gan2026_validation250_verification_decision_v0.jsonl`

## Boundary Decisions To Preserve

- `Verification Route` decides whether a structurally valid row should enter
  verification.
- Deterministic `VerificationDecision` V0 is the safe baseline action harness,
  not a replacement for a future LLM verifier.
- A future LLM verifier must be evaluated against the deterministic V0 baseline.
- Verifier/action logic must not invent replacement scorer-facing labels.
- Score context is audit-only and must not choose route or action behavior.
- Comparator preservation, if added later, must be a named action policy rather
  than hidden verifier repair or projection behavior.

## Outstanding Questions

These questions were walked and resolved on 2026-06-06. The accepted decisions
are recorded in
`docs/research/gan2026_component_architecture_reset_completed_tasks_2026-06-05.md`
under:

- `LLM Verifier Evaluation Surface Decision`;
- `LLM Verifier Input Contract Decision`;
- `LLM Verifier Output Contract Decision`;
- `Comparator Preservation Deferral Decision`;
- `Validation750 And Full-Validation Counter Surface Decision`;
- `Legacy Component Rationalisation Decision`.

### 1. LLM Verifier Evaluation Surface

Question:

- Should the future LLM verifier be evaluated only on rows where
  `VerificationDecision` V0 emits `abstain` or `human_review`, or should it also
  replay rows where future V0 policies emit `affirm` or `reject`?

Recommended answer:

- For the first LLM-verifier experiment, evaluate only routed rows where V0
  emits `abstain` or `human_review`.
- Add `affirm`/`reject` replay only after there are real V0 affirm/reject rows
  or a predeclared proposed-outcome slice.

Reason:

- The current route V6 surface contains only unresolved/null-rendered risk rows.
  Asking an LLM verifier to review nonexistent proposed labels would blur the
  agreed boundary and encourage label invention.

### 2. LLM Verifier Input Contract

Question:

- What should the LLM verifier consume?

Recommended answer:

- Consume the `VerificationDecision` V0 row plus its embedded
  `Verification Route`, projection/render state, source candidate ids, route
  evidence, and exact source evidence where available.
- Do not provide gold labels, score correctness, or benchmark outcome fields as
  action inputs.
- Preserve `score_context` only in an outer audit envelope if needed.

### 3. LLM Verifier Output Contract

Question:

- What should the LLM verifier emit?

Recommended answer:

- Emit an evidence-grounded verifier action:
  `affirm`, `reject`, `abstain`, or `human_review`.
- Include cited evidence ids/spans, a concise rationale, and explicit issue
  flags.
- Do not emit scorer-facing labels.
- Do not choose among extracted candidates as a second selector.

### 4. Comparator Preservation Policy

Question:

- Is a comparator-preservation action policy needed before LLM verifier work?

Recommended answer:

- Not for current route V6.
- Revisit only if a future routed slice contains a proposed rendered outcome
  that verification rejects and a named benchmark/action policy wants to
  preserve a baseline output.

### 5. Validation750 And Full-Validation Counters

Question:

- What aggregate counters should be predeclared before scaling beyond
  `validation250`?

Recommended answer:

- Route-family counts.
- VerificationDecision action counts.
- LLM-vs-V0 action deltas.
- Rows where LLM verifier changes `abstain` or `human_review` to `affirm` or
  `reject`.
- Rows where any verifier action would affect rendered-label availability.
- Counts by projection owner and route family.

### 6. Legacy Component Rationalisation

Question:

- Which old components should be deleted, retained as audit-only, or renamed
  after the reset architecture stabilizes?

Recommended answer:

- Delay deletion until the LLM verifier comparison is complete.
- Treat H6/H9/H10 sidecars and component evidence matrix as report/audit
  surfaces unless they map cleanly to the new stage schemas.
- Keep projection, route, verifier-action, and renderer ownership explicit in
  any retained component.

## Implementation Plan

1. Decide the LLM verifier evaluation surface.
2. Define the LLM verifier input/output schema.
3. Build a saved-replay prompt or no-call dry-run artifact over route V6.
4. If live calls are allowed, predeclare route, model, prompt, cache policy, and
   allowed outputs before running them.
5. Compare LLM verifier actions against `VerificationDecision` V0.
6. Record any accepted action-policy or verifier-schema decision in the
   completed-tasks document as it is made.

## Non-Goals

- No locked-test row-level review.
- No benchmark-comparable claims from mechanics artifacts.
- No score-triggered routing or action behavior.
- No verifier-generated replacement labels.
- No new projection rule for route V6 unless a separate design decision reopens
  projection ownership.
