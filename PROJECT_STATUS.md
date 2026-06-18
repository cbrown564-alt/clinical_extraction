# Project Status

Last updated: 2026-06-18

## Active Objective

ExECTv2 is the forward workstream, now refocused on the LLM-first essential
clinical-detail question in
`docs/plans/exectv2/11_llm_first_essential_clinical_evaluation_plan.md`. The
current key-family result should be framed as an architecture characterization,
not a benchmark-complete claim. A single candidate-ID action prompt reproduces
the current per-family dev140 readout by auditing candidate IDs and
deterministically copying selected candidates, which makes it a hybrid
comparator rather than the primary LLM-first architecture.

Use the Gan 2026 closeout discipline as the template: source-near state, exact
evidence, component attribution, benchmark-format ablations, and family-aware
promotion gates.

## Current Dev140 Readout

| Family | Current candidate | F1 | P | R | Status |
| --- | --- | ---: | ---: | ---: | --- |
| Prescription / medication | Prescription verifier v0.1 | 0.817 | 0.773 | 0.865 | Clears target |
| Investigations | Investigations verifier v0.1 | 0.872 | 0.869 | 0.875 | Clears target |
| SeizureFrequency | SF unknown suppression v0.7 | 0.782 | 0.759 | 0.807 | Partial gain |
| Diagnosis | Diagnosis reconciler v0.1 | 0.658 | 0.658 | 0.658 | Ceiling characterization |

This does not authorize a new full-200 audit.

## Recent Context

- The single structured key-family prompt is a useful evidence-grounded
  substrate, but dev25 target-clearing results did not transfer to dev140.
- Medication and Investigations now clear dev140 with focused verifier stages.
  Their success supports family-specific decision units over broad prompt
  accretion.
- Diagnosis should stop ordinary target chasing on the current candidate set.
  The convention oracle reaches only `0.791`, below the `0.8` gate, and the
  ceiling note documents the claim language.
- SF v0.7 predeclared unknown suppression improves dev140 `0.763` -> `0.782`
  after v0.6 state projection, with unknown FP `22` -> `12`, unknown FN
  unchanged at `8`, and active-rate/seizure-free recall unchanged.
- The next evaluation pass should separate LLM-owned clinical extraction from
  deterministic certainty, CUI, and benchmark-format projection.

## Active Priorities

1. Establish the essential clinical component scorer for Prescription,
   SeizureFrequency, Diagnosis, EpilepsyCause, and Investigations.
2. Audit certainty and CUI as deterministic projection layers rather than LLM
   extraction targets.
3. Replay existing single structured, deterministic, and hybrid artifacts under
   the ownership-aware layer ladder before authorizing new model calls.
4. Require benchmark-beating dev evidence before any new full-200 audit:
   overall `0.87` per-item / `0.90` per-letter, plus per-entity tables,
   evidence/schema reliability, semantic-vs-CUI gaps, and ablations.

## Work Board

### Now

- Execute the LLM-first essential clinical evaluation plan: scorer spec,
  certainty/CUI projection audits, and replay of existing artifacts.

### Next

- Decide whether a new single-call LLM-first run is necessary after replaying
  the existing single structured prompt under the refocused evaluation surface.

### Blocked

- Gan holdout-facing reruns, row-level test analysis, or post-test tuning remain
  blocked without explicit authorization and a frozen protocol.
- New ExECTv2 full-200 audits are blocked until benchmark-beating GPT-first dev
  evidence and a predeclared aggregate readout.

### Done Recently

- 2026-06-18: Completed the candidate-ID action version of the single
  family-conditioned prompt. v0.4 emits keep/reject actions over candidate IDs
  and deterministic code copies selected candidate mentions verbatim. Live
  dev140 matches current per-family prompts (`Rx 0.817`, `Dx 0.658`,
  `SF 0.782`, `Inv 0.872`) with zero call/parse failures, removing the
  full-object copy-drift failure. This is the current comparator-equivalent
  single prompt design; it does not raise Diagnosis or SF above `0.8`.
  See `docs/research/exectv2_single_prompt_design_iteration_2026-06-18.md`.
- 2026-06-18: Implemented the candidate-backed single family-conditioned
  adjudicator. The candidate bundle/passthrough ceiling reproduces the current
  dev140 comparators (`Rx 0.817`, `Dx 0.658`, `SF 0.782`, `Inv 0.872`), and
  v0.3 clears all four families on dev25 (`Rx 0.961`, `Dx 0.838`, `SF 0.875`,
  `Inv 0.878`). Full dev140 live transfer still fails for full-object
  re-emission (`Rx 0.817`, `Dx 0.657`, `SF 0.697`, `Inv 0.876`), mostly from
  copy drift. Next single-design iteration should emit candidate-ID actions
  only and deterministically copy selected candidate mentions. See
  `docs/research/exectv2_single_prompt_design_iteration_2026-06-18.md`.
- 2026-06-18: Implemented and tested the family-conditioned event-ledger
  template through v0.1-v0.3. v0.3 looked promising on dev5 but failed the
  dev25 gate except Prescription (`Rx 0.824`, `Dx 0.405`, `SF 0.429`,
  `Inv 0.769`), so the direct-from-letter family-conditioned design is
  rejected. Carry forward a single candidate-backed family-conditioned
  adjudicator template instead. See
  `docs/research/exectv2_single_prompt_design_iteration_2026-06-18.md`.
- 2026-06-18: Iterated a Gan-inspired single all-family event-ledger prompt
  through v0.6-v0.8 on dev25 plus a stronger-model pilot. The single-call
  variant is rejected; carry forward one family-conditioned event-ledger prompt
  template instead. See
  `docs/research/exectv2_single_prompt_design_iteration_2026-06-18.md`.
- 2026-06-18: Completed the predeclared SF unknown-suppression hard-slice study.
  v0.7 drops 10 named-rule unknown over-emissions and improves SF dev140
  `0.763` -> `0.782` without active-rate or seizure-free recall regression. See
  `experiments/exectv2_hybrid_sf_unknown_suppression_v07_dev140_20260618.md`.
- 2026-06-18: Drafted the final ExECTv2 key-family architecture synthesis and
  paper-table scaffold:
  `docs/research/exectv2_final_key_family_architecture_synthesis_2026-06-18.md`.
- 2026-06-18: Predeclared the narrow SF unknown-suppression hard-slice study
  with stop rules for active-rate and seizure-free recall regression.
- 2026-06-18: Completed SF state projection v0.6. State-only/combined ablations
  improve SF dev140 `0.721` -> `0.763`; ownership-only is flat. See
  `docs/research/exectv2_sf_state_projection_v06_readout_2026-06-18.md`.
- 2026-06-18: Completed the GPT-first key-family loop through dev140 transfer,
  family-specific verifier/adjudicator experiments, convention decomposition,
  and current combined readout.
- 2026-06-17: Closed the Gan strand, completed the deterministic all-9 ExECTv2
  substrate, and built the reusable all-entity projection-gap ledger.

## Guardrails

- Do not inspect Gan `test450` row-level failures, rationales, evidence,
  selected events, or transitions for development.
- New Gan holdout-facing runs require explicit frozen-protocol authorization.
- Keep architecture claims attribution-clean across `rules_only`, `llm_only`,
  and `hybrid`.
- Treat deterministic rules and benchmark-format repairs as controlled
  variables, not hidden implementation detail.
- Treat SF v0.7 as a partial-improvement candidate, not a target-clearing
  result.
- Treat Diagnosis as ceiling/characterization evidence unless a new
  evidence-selection architecture is proposed.

## Core Artifacts

Start with
`docs/research/exectv2_final_key_family_architecture_synthesis_2026-06-18.md`;
it links the convention decomposition, SF v0.6/v0.7 readouts, Diagnosis ceiling note,
SF unknown-suppression predeclaration, combined key-family ledger, and
`experiments/RUN_INDEX.md`.
