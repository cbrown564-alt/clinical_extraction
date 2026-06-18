# Project Status

Last updated: 2026-06-18

## Active Objective

ExECTv2 is the forward Plan 11 workstream. The single all-entities LLM pass is
useful but insufficient; keep source-near state, exact evidence, component
attribution, benchmark-format ablations, and family-aware promotion gates.

## Current Dev140 Readout

Five-family Plan 11 headline: deterministic_all9 `0.604`, hybrid_all_entities
`0.550`, llm_only_all_entities `0.422`.

The predeclared routed ladder ran on `pilot25 -> dev140` without model calls.
On the routed four-family surface, single-pass LLM is `0.4313`,
hybrid_all_entities is `0.5684`, and family-routed is `0.5592` CUI-free /
`0.5952` CUI-projected with exact evidence `1.0000`. This clears the dev gate
against the single-pass baseline but is labeled `llm_first_with_hybrid_sf_route`
because the SF route uses deterministic candidate/projection and
unknown-suppression layers.

A no-call focused Diagnosis replay now exists for dev only. It improves the
routed four-family CUI-free headline to `0.7081`, with Diagnosis `0.7127`, but
the current routed Diagnosis baseline remains weak at `0.2898`; treat the
focused lane as qualified architecture evidence, not solved Diagnosis or
full-200/test authorization.

## Recent Context

- Coordinated Plan 11 follow-ups are merged into this checkout: SF route
  ladder, SF v07 residual diagnostics, focused Diagnosis predeclaration and
  no-call replay, Prescription/Investigations shared-pass preservation, CUI
  projection variants, family-routed preflight, and blocker/runbook tightening.
- SF v0.8 is predeclared as a dev140 hard-slice diagnostic only, splitting
  state, generic/named ownership, seizure-free CUI convention,
  diagnosis/context spans, and true candidate gaps before any prediction-bearing
  SF rule can be proposed.
- Prescription/Investigations remain on the shared broad pass in the
  family-routed architecture; specialist verifier artifacts need a fresh
  no-call predeclaration before replacement.
- CUI review added only projection-only benchmark-format variants. EpilepsyCause
  dev missing mappings dropped `5 -> 0`; remaining Diagnosis misses are
  ambiguous truncations such as `generalised`, `focal`, `secondary`, `drug`, and
  `symptomatic`.

## Active Priorities

1. Treat routed and focused-replay results as qualified dev architecture
   evidence, not benchmark-complete claims.
2. Build the predeclared SF v0.8 hard-slice panel before any new
   prediction-bearing SF rule.
3. Keep full-200/test and Gan-facing work blocked until explicit authorization,
   frozen protocol, and predeclared aggregate readout are present.

## Work Board

### Now

- Build the SF v0.8 hard-slice panel from dev140 residuals before changing
  prediction-bearing SF code.

### Next

- Use the focused Diagnosis replay only for dev-route evidence; do not promote
  it to solved Diagnosis or full-200/test authorization.
- Keep Prescription/Investigations on the shared broad pass unless a fresh
  predeclared no-call ablation shows regression-free improvement.
- Keep residual CUI missing mappings diagnostic-only for ambiguous Diagnosis
  bare/truncation forms; do not promote EpilepsyCause without predeclared
  dev-only boundary-control evidence.

### Blocked

- Gan holdout-facing reruns, row-level test analysis, and post-test tuning need
  explicit authorization plus a frozen protocol.
- New ExECTv2 full-200 audits need benchmark-beating GPT-first dev evidence and
  a predeclared aggregate readout.

### Done Recently

- 2026-06-18: Coordinated four worker threads and merged their outputs: SF v0.8
  hard-slice predeclaration, focused Diagnosis no-call replay, P/I shared-pass
  preservation, and conservative CUI projection additions.
- 2026-06-18: Merged coordinated Plan 11 workstreams and ran the predeclared
  family-routed comparison. Dev140 routed four-family F1 is `0.5592` CUI-free /
  `0.5952` CUI-projected, with SF `0.6321` and exact evidence `1.0000`.

## Guardrails

- Do not inspect Gan `test450` row-level failures, rationales, evidence,
  selected events, or transitions for development.
- Keep claims attribution-clean across `rules_only`, `llm_first`, and `hybrid`;
  deterministic certainty/CUI/format repairs are controlled projection layers.

## Core Artifacts

Start with the family-routed comparison, focused Diagnosis no-call replay, SF
v0.8 predeclaration, P/I shared-pass preservation note, CUI projection
diagnostics, Plan 11 readouts, key-family synthesis, and blocker runbook before
opening new experiments.
