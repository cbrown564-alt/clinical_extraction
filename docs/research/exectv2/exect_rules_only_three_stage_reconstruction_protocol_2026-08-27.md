# Protocol: reconstruct ExECT rules-only as recognise / encode / select

Date: 2026-08-27
Status: predeclared before implementation
Brief: [three-stage reconstruction brief](exect_rules_only_three_stage_reconstruction_brief_2026-08-27.md)
Prior evidence: [inventory retune audit](exect_rules_only_inventory_retune_audit_2026-08-27.md),
[27 Aug patch](exect_rules_only_inventory_retune_2026-08-27.md)
Artifact: `experiments/exect_rules_only_three_stage_reconstruction_20260827/summary.json`

## Primary question

Does re-specifying standalone rules as three stages — a recall-first
recognise ledger, a same-fact encode registry, and an ordered
precision Select sequence — raise `dev140` exact 4-family inventory
micro F1 above the accepted 27 Aug stack (**0.8949**) without
exact-family regressions, with SeizureFrequency and Diagnosis as the
target families?

This matters because cell 3's gain came from Select reading a wide
ledger. The rules-only ledger does not exist: extractors drop and
collapse candidates before any later stage can see them.

## Data, split, inspection

- ExECTv2 `dev140`, all 140 development letters. Row and letter
  inspection permitted (development distribution).
- `test60` is not loaded, not scored, not inspected. The cited
  five-cell rules row stays **0.7725**.

## Comparator (fixed)

The accepted 27 Aug rules-only stack, exactly as
`orchestration/rules.run_letter` runs today: `extract_deterministic_all9`
(recall-first extract, Investigations per-occurrence, Diagnosis heading
aliases) → Diagnosis-only `apply_format_stack` encode →
`RULES_ONLY_SELECT_RULE_IDS` Select. `dev140` inventory F1 **0.8949**
(P 0.899 / R 0.891). No model calls in either arm.

## Candidate

A three-stage rules-only program:

1. **Recognise ledger.** A typed per-letter ledger of candidates, each
   carrying the mention, a candidate class, and the producing rule id.
   Classes: `direct` (what today's extract emits) plus deferred classes
   that today's extract discards:
   - `diagnosis_nested_ancestor`: nested parent surfaces suppressed by
     longest-first span occupancy (e.g. `epilepsy` inside
     `focal epilepsy`).
   - `sf_named_type`: seizure-type anchors with a lexicon CUI but no
     associated rate.
   - `sf_heading_state`: anchors under a frequency/seizure section
     heading with a heading-derived state.
   - `sf_seizure_free`: seizure-free statements with verbatim evidence
     that associate-or-drop currently loses.

   Deferred candidates are **not** in the selected set by default.
   This is the structural difference from the rejected emit-all
   rate-less arm (0.7909): recall lives in the ledger, precision in
   Select promotion, never blanket emission.
2. **Encode registry.** Same-fact encode only, independently
   switchable per family (Diagnosis stays on as in the comparator;
   SF, Prescription, Investigations encode are separate switches
   measured one at a time). No reselect-shaped rule enters encode.
3. **Select sequence.** An explicit ordered, independently switchable
   sequence operating on the selected set with the full ledger as
   `source_mentions`: encode-aware Diagnosis rewrites first
   (local specificity, heading phenotype), then keep-source ancestor,
   then support-gated SF promotion (promote a deferred SF candidate
   only when its state is supported by heading, seizure-free evidence,
   or named-type identity), then weak-episode drop, then any accepted
   dedupe. Order is recorded in the artifact.

## Scorer and metrics

- Primary: exact per-letter, per-family `clinical_inventory_unit_keys`,
  4-family micro F1 (`exact_clinical_inventory_scores` +
  `aggregate_scores`). No headline/Compact numbers are mixed in.
- Secondary: per-family P/R/F1/FN/FP; changed letter/family pairs with
  direction; ledger coverage (per family: gold units recoverable from
  the ledger vs from the direct set alone); Select action counts by
  rule id.

## Moves (independently stoppable)

- **M1** Ledger instrumentation only. Gate: selected output is
  mention-identical to the comparator (score unchanged at 0.8949).
- **M2** Diagnosis nested-ancestor candidates in the ledger; Select
  keep-source / local-specificity read the ledger. Gate: standard
  gates below.
- **M3** SF deferred candidate classes plus support-gated Select
  promotion and unsupported-state drop. Gate: standard gates below;
  SF family F1 must not fall below comparator SF (0.856 band).
- **M4** Per-family same-fact encode switches (SF, Prescription,
  Investigations), measured one family at a time. Any switch that
  regresses a comparator-exact letter/family stays off.

## Acceptance gates (all required for the accepted stack)

1. Aggregate `dev140` inventory F1 ≥ comparator (0.8949).
2. No letter/family pair exact under the comparator becomes non-exact.
3. No changed family with a worse FN+FP count than the comparator.
4. Each accepted Select rule and each deferred candidate class has a
   positive isolated contribution and a negative leave-one-out effect
   on the accepted stack; score-neutral additions are rejected.
5. Every Select add/promotion retains verbatim evidence from the
   letter.

## Stop rule

Accept the best gated combination; reject any move failing its gates
(recording the negative result); revise once if a gate failure has a
clear mechanism; otherwise stop with a negative or blocked-by-
instrumentation result. A defect found in the candidate starts a new
candidate; it never permits holdout inspection.

## Claim boundary

Development mechanism evidence only. No holdout number, no paper
sentence, no change to the cited **0.7725** cell. Holdout replay is
owned by
[three-stage test60 aggregate protocol](exect_rules_only_three_stage_test60_aggregate_protocol_2026-08-27.md)
(predeclared 2026-08-27; not yet executed).

## Artifact schema

`experiments/exect_rules_only_three_stage_reconstruction_20260827/summary.json`:
date, dirty-tree note, split, `holdout_loaded: false`, `model_calls: 0`,
scorer id, comparator score, per-arm overall and by-family scores,
changed letter/family pairs per arm, ledger coverage per family,
Select rule order, isolated/leave-one-out table for accepted rules,
and the accepted configuration (candidate classes, encode switches,
Select rule ids in order).
