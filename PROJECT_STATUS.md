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
  ladder, SF v07/v08 residual diagnostics, focused Diagnosis predeclaration and
  no-call replay, Prescription/Investigations shared-pass preservation, CUI
  projection guardrails, family-routed preflight, and blocker/runbook tests.
- SF v0.8 hard-slice panel is built from v0.7 dev140 residuals only:
  `84` residual units over `82` records, with action counts `no_action=35`,
  `drop=21`, `repair_state=12`, `repair_benchmark_format=9`,
  `repair_ownership=4`, and `add=3`. This is diagnostic-only and does not
  authorize prediction-bearing SF changes.
- Prescription/Investigations remain on the shared broad pass in the
  family-routed architecture; preflight now checks the
  `shared_broad_pass_only` preservation note before dev-ladder runs.
- CUI projection now keeps ambiguous Diagnosis residuals and five
  EpilepsyCause residual variants diagnostic-only pending the dev-only
  EpilepsyCause boundary-control predeclaration.

## Active Priorities

1. Treat routed and focused-replay results as qualified dev architecture
   evidence, not benchmark-complete claims.
2. Use the SF v0.8 hard-slice panel to make a predeclared gate decision before
   any prediction-bearing SF code.
3. Keep full-200/test and Gan-facing work blocked until explicit authorization,
   frozen protocol, and predeclared aggregate readout are present.

## Work Board

### Now

- Review `experiments/exectv2_sf_v08_hard_slice_panel_dev140_20260618.md` and
  write the SF v0.8 gate decision: either no prediction-bearing change, or one
  predeclared bucket/action class that clears attribution, non-gold-feature, and
  stop-rule checks.

### Next

- If SF v0.8 gate passes, predeclare the single dev-only implementation slice
  and acceptance readout before editing SF prediction code.
- If CUI projection resumes, run the EpilepsyCause boundary-control
  predeclaration before promoting any residual EpilepsyCause variant.
- Keep focused Diagnosis replay, P/I specialist artifacts, and CUI projection
  variants as guarded dev evidence unless fresh predeclared gates pass.

### Blocked

- Gan holdout-facing reruns, row-level test analysis, and post-test tuning need
  explicit authorization plus a frozen protocol.
- New ExECTv2 full-200 audits need benchmark-beating GPT-first dev evidence and
  a predeclared aggregate readout.

### Done Recently

- 2026-06-18: Integrated five parallel guardrail threads: SF v0.8 hard-slice
  panel and tests, focused Diagnosis claim-language test, P/I shared-pass
  preflight gate, CUI diagnostic-only deny-list plus EpilepsyCause
  boundary-control predeclaration, and blocker/protocol test coverage.
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
v0.8 predeclaration and hard-slice panel, P/I shared-pass preservation note,
CUI projection diagnostics and EpilepsyCause boundary-control predeclaration,
Plan 11 readouts, key-family synthesis, and blocker runbook before opening new
experiments.
