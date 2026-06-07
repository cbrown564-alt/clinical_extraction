# 0014: Name The New Deterministic-Canonical Stage "Evidence Trace Check", Not "Verify"

Date: 2026-06-07

## Status

Accepted.

## Decision

The new fourth stage being added to the `deterministic_canonical_pipeline`
configuration ([[0013-stage-deterministic-canonical-config-before-generalizing-its-rules]],
[[gan2026_three_way_architecture_comparison_and_cross_pollination_plan]]) is
named **Evidence Trace Check**, not `Verify`.

It wraps the existing `evidence_is_substring` check (does the selected evidence
string appear verbatim in the source note) plus the existing diagnostic-only
`AssessmentDraft`/`clinical_assessment` probe as a named, ablatable stage
output — identical behavior to today, under a new seam.

It does **not** reuse the `VerificationDecision`/`Verifier Action` vocabulary
or its `affirm`/`reject`/`abstain`/`human_review` action set (`CONTEXT.md`,
"VerificationDecision" / "Verifier Action" / "Verification Route"). Those terms
are reserved for the hybrid pipeline's verifier stage, which acts on
structurally valid `ClinicalAssessment` and projection/render objects.

## Context

The three-way comparison plan's Phase 0 calls for restructuring the
deterministic pipeline into "named, stage-owned, ablatable Extract/Normalize/
Project/Render/Verify form" — explicitly naming a `Verify` stage as part of the
target shape. But the deterministic pipeline today has no verify stage at all:
its closest analog is the `evidence_is_substring` boolean folded into
diagnostics, plus a diagnostic-only `AssessmentDraft`/`clinical_assessment`
probe wrapped in a `try/except` purely for visibility (`runner.py` lines
161-181). It has never made `affirm`/`reject`/`abstain`/`human_review`
decisions, nor routed rows for review — that machinery belongs to the hybrid
pipeline's verifier stage and operates on a `ClinicalAssessment` object the
deterministic pipeline does not produce.

## Why

Calling the new stage `Verify` and reusing `VerificationDecision`/`Verifier
Action` vocabulary would silently expand what the deterministic pipeline does —
introducing routing/affirm/reject semantics where none exist today. That is a
behavior change wearing a staging-pass costume, and it would violate
[[0013-stage-deterministic-canonical-config-before-generalizing-its-rules]]'s
"rules and behavior unchanged" guarantee for the staging pass.

"Evidence Trace Check" names exactly what the wrapped check does — using the
project's existing "evidence-trace"/"exact evidence"/"source-id validity"
vocabulary (already established across the Gan 2026 research corpus and in
`CONTEXT.md`'s "Evidence Text-Containment Check" definition for the canonical
fully-LLM comparator) — without claiming the loaded `Verify` stage's affirm/
reject/route semantics.

## Consequences

- The plan's Section 2 framing ("...Extract/Normalize/Project/Render/Verify
  form") should be read as referring to this stage by its resolved name,
  Evidence Trace Check, not literally `Verify` — `CONTEXT.md` records this
  resolution under the "Evidence Trace Check" and "Canonical Deterministic
  Pipeline" entries.
- If a future change wants the deterministic canonical pipeline to actually
  make affirm/reject/route decisions over a real `ClinicalAssessment` (i.e.
  genuine verification, not staging), that is a new behavior change requiring
  its own decision record — it cannot be folded into this staging pass or
  justified by this ADR.
- `VerificationDecision`/`Verifier Action`/`Verification Route` remain
  exclusively the hybrid pipeline's vocabulary; the deterministic canonical
  pipeline must not reuse those terms for Evidence Trace Check or its outputs.

## Related Artifacts

- [[0013-stage-deterministic-canonical-config-before-generalizing-its-rules]]
- `CONTEXT.md` — "Evidence Trace Check", "Select & Render", "VerificationDecision",
  "Verifier Action", "Verification Route"
