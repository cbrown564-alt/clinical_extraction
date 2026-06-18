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

## Recent Context

- Coordinated workstreams are merged into this checkout: SF route ladder, SF
  ledger anchor-normalization slice, CUI projection-only additions,
  family-routed preflight, and blocker/runbook audit.
- The routed comparison report shows the architectural lesson: keep the broad
  LLM pass for Prescription/Investigations, treat Diagnosis as still weak
  concept selection (`0.2898` routed), and route SF through event/state logic
  (`0.6321`, up from `0.0118`).
- Plan 11 now separates the five-family primary headline, routed four-family
  surface, CUI-projected companion, evidence/error diagnostics, certainty
  projection, and CUI missing mappings.
- Certainty and CUI remain deterministic adapter/projection layers: certainty
  accuracy is `0.81`-`1.00` by guideline-owned family, negation `0.99`-`1.00`,
  and CUI projection coverage/correctness is now `0.8905`/`0.9529` after four
  projection-only PatientHistory mappings.
- The LLM-first row ledger has `557` nonzero row/error records: `285`
  candidate-miss, `248` wrong-detail-selection, `24` projection-gap, and `0`
  evidence-failure rows.

## Active Priorities

1. Treat the family-routed result as a qualified dev architecture win over the
   single broad pass, not a benchmark-complete system.
2. Decide whether Diagnosis gets a separate predeclared route or stays
   diagnostic while SF stabilizes.
3. Treat remaining CUI gaps as benchmark-format review work; keep full-200
   blocked until dev evidence beats comparators and a frozen protocol exists.

## Work Board

### Now

- Review residual SF route errors: F1 `0.6321`, `77` wrong-detail selections,
  and `65` candidate misses.
- Keep Prescription and Investigations on the shared broad pass unless a later
  ablation shows a real regression.
- Use the blocker runbook before any full-200/test or Gan-facing work.

### Next

- Add a focused Diagnosis route only through a fresh predeclaration; current
  routed Diagnosis is `0.2898` and remains the major non-SF weakness.
- Continue CUI missing-mapping review only for unambiguous benchmark-format
  additions; keep EpilepsyCause diagnostic unless dev-only boundary-control
  evidence shows a material architecture bottleneck.

### Blocked

- Gan holdout-facing reruns, row-level test analysis, and post-test tuning need
  explicit authorization plus a frozen protocol.
- New ExECTv2 full-200 audits need benchmark-beating GPT-first dev evidence and
  a predeclared aggregate readout.

### Done Recently

- 2026-06-18: Merged the coordinated workstreams and ran the predeclared
  family-routed comparison. Dev140 routed four-family F1 is `0.5592` CUI-free
  / `0.5952` CUI-projected, with SF `0.6321` and exact evidence `1.0000`.
- 2026-06-18: Created the HTML synthesis report for the coordinated
  `PROJECT_STATUS.md` workstreams.
- 2026-06-18: Merged Plan 11 workstreams and projection-layer cleanup: SF
  schema, routed predeclaration, row/evidence ledgers, CUI additions,
  EpilepsyCause ADR, CUI-free/CUI-projected score, certainty audit, and tests.

## Guardrails

- Do not inspect Gan `test450` row-level failures, rationales, evidence,
  selected events, or transitions for development.
- Keep claims attribution-clean across `rules_only`, `llm_first`, and `hybrid`;
  deterministic certainty/CUI/format repairs are controlled projection layers.

## Core Artifacts

Start with the family-routed comparison report, Plan 11 readout, Plan 11, final
key-family synthesis, blocker runbook, and the coordinated-workstreams HTML
report.
