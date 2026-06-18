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

- Coordinated Plan 11 follow-ups are merged into this checkout: SF route
  ladder, SF v07 residual diagnostics, focused Diagnosis route predeclaration
  and no-call scaffold, Prescription/Investigations shared-pass guard,
  conservative CUI projection variants, family-routed preflight, and
  blocker/runbook tightening.
- The routed comparison report shows the architectural lesson: keep the broad
  LLM pass for Prescription/Investigations, treat Diagnosis as still weak
  concept selection (`0.2898` routed), and route SF through event/state logic
  (`0.6321`, up from `0.0118`).
- The SF worker found the current v07 diagnostic surface is no longer the old
  `0.6321` snapshot: it reports SF `0.7824`, `36` candidate misses, and `48`
  wrong-detail selections, with remaining residuals mixed across state,
  ownership, and benchmark-format conventions.
- Certainty and CUI remain deterministic adapter/projection layers: certainty
  accuracy is `0.81`-`1.00` by guideline-owned family, negation `0.99`-`1.00`,
  and CUI projection coverage/correctness is now `0.8905`/`0.9529` after four
  projection-only PatientHistory mappings.
- Focused verification after merge passed: family routing/preflight, benchmark
  projection/CUI diagnostics, clinical-recovery ledger, SF suppression, and SF
  state projection (`36` pytest cases), plus Ruff on touched Python paths.

## Active Priorities

1. Treat the family-routed result as a qualified dev architecture win over the
   single broad pass, not a benchmark-complete system.
2. Predeclare the SF v0.8 hard-slice before any new prediction-bearing SF rule.
3. Keep full-200/test and Gan-facing work blocked until explicit authorization,
   frozen protocol, and predeclared aggregate readout are present.

## Work Board

### Now

- Predeclare an SF v0.8 hard-slice over dev140 residuals, splitting
  `generic_named_ownership`, `state_swap`, `seizure_free_cui_convention`,
  `diagnosis_context_span`, and `true_candidate_gap` before changing
  prediction-bearing code.
- Keep the focused Diagnosis route scaffold to no-call dev replay only; do not
  treat it as a solved Diagnosis target or a full-200/test authorization.
- Preserve Prescription and Investigations on the shared broad pass unless a
  fresh predeclared ablation shows real regression-free improvement.

### Next

- Use the focused Diagnosis predeclaration/no-call scaffold only for dev-only
  replay; current routed Diagnosis is `0.2898` and remains weak until proven.
- Continue CUI missing-mapping review only for unambiguous benchmark-format
  additions; keep EpilepsyCause diagnostic unless dev-only boundary-control
  evidence shows a material architecture bottleneck.

### Blocked

- Gan holdout-facing reruns, row-level test analysis, and post-test tuning need
  explicit authorization plus a frozen protocol.
- New ExECTv2 full-200 audits need benchmark-beating GPT-first dev evidence and
  a predeclared aggregate readout.

### Done Recently

- 2026-06-18: Merged five parallel worker worktrees and reconciled overlapping
  family-routing/status edits. Focused checks passed (`36` pytest cases plus
  Ruff on touched Python paths).
- 2026-06-18: Merged the coordinated workstreams and ran the predeclared
  family-routed comparison. Dev140 routed four-family F1 is `0.5592` CUI-free
  / `0.5952` CUI-projected, with SF `0.6321` and exact evidence `1.0000`.
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
key-family synthesis, blocker runbook, focused Diagnosis predeclaration, SF v07
residual diagnostic, and coordinated-workstreams HTML report before opening new
experiments.
