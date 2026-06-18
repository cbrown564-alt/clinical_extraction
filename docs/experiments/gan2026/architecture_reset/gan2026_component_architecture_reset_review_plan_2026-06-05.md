# Gan 2026 Component Architecture Reset Outstanding Plan

Date: 2026-06-05

Status: review questions resolved on 2026-06-06. Completed decisions,
generated artifacts, row reviews, and implementation notes have been moved to
``.
The later validation750 reset-state update, post-V5 ports, value-language
decision, cluster route contract, and reset-stage component inventory are now
captured in:

- ``
- ``
- ``
- ``
- ``
- ``
- ``
- `experiments/gan2026_reset_stage_component_inventory_v0_2026-06-06.md`

This plan does not authorize new holdout work, benchmark-comparable claims, or
row-level locked-test review.

## Current Position

The original validation250 verifier/action review is complete and should now be
treated as historical context. The current reset position is the validation750
V6 development-mechanics surface:

- extraction, candidate-set, clinical-assessment, normalize/project ports,
  verification-route, and deterministic verification-action mechanics all exist
  under reset-stage ownership;
- fresh `context_repair_v6` replay reaches all 750 validation rows;
- rendered labels rose to 580 and true null renders fell to 170;
- the routed surface expanded to 276 rows, driven mainly by provenance route
  visibility rather than a clean increase in verifier-eligible clinical
  ambiguity;
- the first verifier comparison surface is therefore predeclared as the 56
  mixed clinical/policy rows, with the 220 provenance-only routes kept out of
  the first success/failure score table.

Active mechanics artifacts:

- Projection/render and score artifacts under
  `experiments/gan2026_*validation750*gpt41mini_context_repair_v6_2026-06-06.*`
- Validation750 verification-route artifacts under
  `experiments/gan2026_validation750_verification_route_gpt41mini_context_repair_v6_2026-06-06.*`
- Validation750 verification-decision artifacts under
  `experiments/gan2026_validation750_verification_decision_gpt41mini_context_repair_v6_2026-06-06.*`

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
- Provenance-only route families are audit/instrumentation debt until explicitly
  adjudicated; they are not silent promotion evidence and not the default first
  verifier score table.
- Reset-stage issue/rule language should use plain-language `values`.
- Cluster convention rendering may coexist with verification routing when
  cadence or axis ownership remains unresolved.

## Outstanding Questions

These questions were walked and resolved on 2026-06-06. The accepted decisions
are recorded in
``
under:

- `LLM Verifier Evaluation Surface Decision`;
- `LLM Verifier Input Contract Decision`;
- `LLM Verifier Output Contract Decision`;
- `Comparator Preservation Deferral Decision`;
- `Validation750 And Full-Validation Counter Surface Decision`;
- `Legacy Component Rationalisation Decision`.

The remaining live work is no longer the validation250 review checklist below.
The next durable reset tasks are:

1. Keep the 220 provenance-only routed rows out of the first verifier
   success/failure table and track them as audit/instrumentation debt.
2. Use the V6 null-action taxonomy operationally:
   - 29 verifier-eligible ambiguity rows;
   - 18 upstream policy/parser rows;
   - 4 abstain rows.
3. Use the predeclared first verifier report layout:
   - 29-row main ambiguity score table;
   - 4 abstain exemplars;
   - 18 upstream-policy appendix;
   - 5 rendered policy-sensitive appendix;
   - 220 provenance-only audit appendix.
4. Use the reset-stage component inventory to define the first component-level
   ablation report surface.

Later update:

- the primary verifier policy is now `action_only`
- the next prompt/policy iteration should focus first on the `29`-row main
  ambiguity table
- the intermediate candidate-trace `selected_source_id_invalid` residual tail
  has since been repaired to `0`

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
