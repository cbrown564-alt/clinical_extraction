# Project Status

Last updated: 2026-06-04

## Active Objective

Answer the Gan 2026 seizure-frequency component research questions under
exact-evidence, attribution, hidden-family, and split-discipline constraints.
No benchmark-comparable claim is authorized.

## Current Strategy

Use saved artifacts as research instruments for component questions, not
whole-pipeline validation F1. Deterministic rules are frozen comparators, safety
floors, and miss-slice definers, not eligible answers for RQ1-RQ4.

RQ1-RQ10 now have bounded validation-development answers or explicit claim
boundaries. RQ3 remains positive but has unresolved projection-policy work.

Important numbers: `selective_safety_floor_gate_v0` changed 21 validation750
rows with 11 W->C and 0 C->W, and 14 frozen local test450 rows with 8 W->C and
0 C->W. RQ9 v3 covers 716/750 validation rows, abstains on 26, routes 8 to
human review, and has covered-row Purist accuracy 0.9469. RQ10 found 23
`underdetermined_note`, 19 `true_extraction_failure`, 11
`benchmark_convention_dominated`, and 0 strong likely gold defects among 53
residual Purist misses.

## Active Question

Selective Verifier Live Readout

Status: selective-verifier prompt design work is complete for now. The promoted
design is the stronger `binary_quote_highest_answer_selector`: on the frozen
42-row validation-development surface it had 42/42 parseable outputs, 7 W->C, 1
C->W (`7168`), 10 C->review, and 3 W->review versus routing. This is sufficient
for integration into the multi-component validation architecture; impact should
be reassessed on the full validation set after integration, not by further
prompt iteration here. Earlier verifier variants remain useful comparison
artifacts only.

Core verifier artifacts live under
`docs/research/gan2026_selective_verifier_*2026-06-04.md`.

## Guardrails

- Split `gan2026_split_v1` is locked: 300 train, 750 validation, 450 holdout.
- Locked test is not for row-level tuning.
- `rules_only_v1` remains the frozen transparent comparator.
- Treat saturated aggregate validation scores as low-information.
- Any holdout-facing use needs a frozen predeclared audit and explicit user
  authorization; do not change scorer/gold policy from RQ10 alone.
- Final F1 is secondary to candidate recall, evidence exactness, projection
  consistency, metadata completeness, ambiguity preservation, and regression
  accounting.

## Work Board

### Now

- Integrate the promoted stronger `binary_quote_highest_answer_selector` into
  the multi-component architecture as the verifier design selected from the
  42-row development surface.

### Next

- Validate the integrated multi-component architecture on the full validation
  set and reassess the verifier's net effect there.
- If cost/latency/token efficiency is needed, run a telemetry-only pass over
  surviving primitives before strengthening RQ8 claims.

### Blocked

- Benchmark-comparable language remains blocked; current holdout evidence is a
  local frozen audit only.
- Whole-pipeline promotion is blocked until the family-indexed matrix is
  implemented as an auditable assembled candidate and any holdout-facing use
  has a frozen protocol.

### Done Recently

- 2026-06-04: Adjudicated all 5 selective-verifier C->W regression rows and
  rejected v0 for prediction-bearing use; live-ran two plain-language verifier
  prompt designs, then a full-letter support-parts variant with 5 W->C and 1
  C->W, a binary quote/highest design with 7 W->C and 3 C->W, and a stronger
  binary prompt with 7 W->C, 1 C->W, and 10 C->review; promoted the stronger
  binary prompt and marked verifier prompt-design work complete for integration.
- 2026-06-04: Ran the frozen 42-row selective-verifier live readout with
  42/42 calls ok, 42/42 parseable outputs, 38/42 exact evidence-quote rows, 6
  W->C, 5 C->W, and changed-decision precision 0.522.
- 2026-06-04: Replayed staged hybrid assembly and suspicious routing with
  source-id tracing: 75/75 source-id-consistent rows, routing at 35
  `route_unknown`, 9 `route_review`, and 31 render rows.
- 2026-06-04: Added RQ6-RQ8 answers, RQ8 telemetry guard, ADR 0009, and the
  architecture readiness decision; telemetry remains incomplete at 0/21 rows.
