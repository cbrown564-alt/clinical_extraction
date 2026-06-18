# Project Status

Last updated: 2026-06-18

## Active Objective

ExECTv2 is the forward workstream, focused on Plan 11's LLM-first essential
clinical-detail question. The single all-entities LLM pass is useful for some
families, not a sufficient architecture. Keep Gan 2026 closeout discipline:
source-near state, exact evidence, component attribution, benchmark-format
ablations, and family-aware promotion gates.

## Current Dev140 Readout

Primary ExECTv2 essential headline is CUI-free over Prescription, SF,
Diagnosis, EpilepsyCause, and Investigations. Essential F1:
deterministic_all9 `0.604`, hybrid_all_entities `0.550`, llm_only_all_entities
`0.422`. The single LLM pass is useful for Prescription `0.747` and
Investigations `0.748`, weak for Diagnosis concept-only `0.316`, and collapsed
for SF `0.012` and EpilepsyCause `0.000`; evidence is exact for `743/743`
emitted essential mentions.

## Recent Context

- Plan 11 now separates the five-family primary headline, CUI-projected score,
  evidence/error diagnostics, certainty projection, and CUI missing mappings.
- The coordinated Plan 11 merge landed the SF event/state schema, routed
  predeclaration, row ledger, family evidence table, CUI ledger/additions,
  EpilepsyCause ADR, and HTML synthesis report.
- Certainty is a deterministic adapter-layer candidate with measured rules:
  List 2 certainty triggers plus default affirmed negation score at
  `0.81`-`1.00` certainty accuracy by guideline-owned family and `0.99`-`1.00`
  negation accuracy. It remains outside the LLM-owned headline.
- CUI is benchmark-format projection: coverage is now `0.882`, correctness
  `0.953`, with `175` missing-mapping mentions across `153` concepts after
  conservative additions.
- The LLM-first row ledger has `557` nonzero row/error records:
  `285` candidate-miss rows, `248` wrong-detail-selection rows, `24`
  projection-gap rows, and `0` evidence failures. The active failure remains
  clinical-detail selection/coverage, not evidence citation.

## Active Priorities

1. Implement the predeclared family-routed comparison only after the SF
   event/state adapter and ownership tests exist.
2. Use the row-level ledger to prioritize candidate-miss and wrong-selection
   slices before any new model calls.
3. Treat remaining CUI gaps as benchmark-format review work, not LLM clinical
   reasoning; keep full-200 blocked until dev evidence beats comparators and a
   frozen protocol is predeclared.

## Work Board

### Now

- Wire the SF event/state route to the documented layer ladder, with tests that
  prevent hidden deterministic clinical selection.
- Review the row-level essential-family ledger to choose the first SF
  candidate-miss/wrong-selection slices for adapter or prompt work.

### Next

- Run the family-routed comparison through the dev ladder only after the
  adapter/schema contract is implemented and explicitly authorized.
- Review the remaining CUI missing-mapping ledger (`153` concepts / `175`
  mentions) for safe benchmark-format additions.
- Keep EpilepsyCause diagnostic unless a predeclared dev-only boundary-control
  study shows it is a material architecture bottleneck.

### Blocked

- Gan holdout-facing reruns, row-level test analysis, or post-test tuning remain
  blocked without explicit authorization and a frozen protocol.
- New ExECTv2 full-200 audits are blocked until benchmark-beating GPT-first dev
  evidence and a predeclared aggregate readout.
- Full-suite verification is not clean at repo head: current unrelated failures
  are projection-gap total drift and Gan validation path/protocol assertions.

### Done Recently

- 2026-06-18: Merged the coordinated Plan 11 workstreams: SF schema, routed
  predeclaration, row/evidence ledgers, CUI additions, EpilepsyCause ADR, and
  HTML synthesis report.
- 2026-06-18: Completed Plan 11 projection-layer cleanup: essential-only
  CUI-free headline, CUI-projected companion score, explicit guideline-rule
  certainty/negation audit, CUI missing mappings, evidence/error summaries, and
  regression tests.
- 2026-06-18: Completed the candidate-ID action prompt, SF unknown suppression
  v0.7, and the deterministic all-9 ExECTv2 substrate.

## Guardrails

- Do not inspect Gan `test450` row-level failures, rationales, evidence,
  selected events, or transitions for development.
- Keep claims attribution-clean across `rules_only`, `llm_first`, and `hybrid`;
  deterministic certainty/CUI/format repairs are controlled projection layers.

## Core Artifacts

Start with the Plan 11 readout, Plan 11, and final key-family synthesis.
