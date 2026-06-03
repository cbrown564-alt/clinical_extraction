# Project Status

Last updated: 2026-06-03

## Active Objective

Build a Gan 2026 seizure-frequency extraction pipeline that can reach at least
0.9000 Purist F1 on development surfaces while preserving evidence trails,
component ablations, split discipline, and conservative benchmark language.

## Current Strategy

The current leading development candidate is
`hybrid_parallel_state_candidate_reasoner` with a deterministic safety-floor
final policy. Full validation750 no-call replay of the live GPT-4.1 mini
outputs reaches 697/750 Purist (0.9293) and 704/750 Pragmatic (0.9387), with
750/750 exact selected evidence, 750/750 valid source ids, and 0
deterministic-correct regressions. Interpretation:
`experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation750_safety_floor_interpretation_2026-06-03.md`.

Attribution caveat: this is a hybrid deterministic-safety-floor development
result, not an LLM-first result. LLM-heavy Decision 0007 v1 remains a revise
lane after its validation50 failure rows.

## Guardrails

- Split `gan2026_split_v1` is locked: 300 train, 750 validation, 450 holdout.
  Validation is the development surface; locked test is not for row-level
  tuning.
- `rules_only_v1` remains the frozen transparent comparator. Do not tune it
  from locked-test audit behavior.
- Hybrid v0.2 `cluster_diary_candidate_recall` remains a frozen comparator-only
  generalization audit result.
- Treat saturated aggregate validation scores as low-information. Prefer
  hard-slice, rescue/regression, evidence-validity, component-stress, and
  frozen-audit evidence.
- Keep semantic repair, graph projection, scorer normalization, deterministic
  adapters, and production policy separately named and ablated.
- Use typed DSPy outputs with scoped `JSONAdapter` for new LLM/DSPy architectures.

## Active Priorities

1. Preserve attribution language for the achieved result: hybrid
   deterministic-safety-floor, validation development only.
2. Prepare a frozen-test audit plan only after candidate code, scorer, model,
   repair policy, and inspection policy are frozen.
3. Use component-stress/error analysis to decide whether LLM/graph overrides can
   improve beyond the deterministic safety floor without regressions.
4. Keep LLM-heavy v1 as a separate revise lane: bimonthly operands,
   weekday/vague frequency operands, `≤ N` upper-bound semantics, evidence
   contiguity, and raw-correct adapter fallback.

## Work Board

### Now

- Freeze and review the hybrid deterministic-safety-floor validation750
  artifact for claim language and final-test readiness.
- Triage the 53 remaining validation750 Purist misses only for error taxonomy
  and component-stress design, not further broad-validation tuning.

### Next

- Draft a frozen-test audit plan with predeclared aggregate/slice inspection
  policy before any holdout run.
- Decide whether to add a selective LLM/graph override gate on hard slices, with
  deterministic safety floor preserved.
- Keep Qwen/minimal-evidence-selector transfer as a secondary lane after the
  safety-floor candidate is frozen.

### Blocked

- Benchmark language and holdout analysis are blocked until replication
  comparability and locked-test discipline permit them.
- Qwen 3.6 full v5 validation ladder remains blocked until strict
  schema-compatible output or a named Qwen schema-repair ablation exists.

### Done Recently

- 2026-06-03: Added deterministic safety-floor final policy to
  `hybrid_parallel_state_candidate_reasoner` and replayed the full validation750
  live outputs. Final replay reached 697/750 Purist (0.9293), 704/750 Pragmatic
  (0.9387), 750/750 exact selected evidence, 750/750 valid source ids, 0
  deterministic-correct regressions, and 136/750 safety-floor fallbacks. This
  satisfies the >0.9000 validation development objective with hybrid
  deterministic-safety attribution.
- 2026-06-03: Ran hybrid validation50, validation250, and full validation750
  live escalations. The ungated live full-validation adapted layer reached only
  669/750 Purist (0.8920), motivating the deterministic safety-floor replay.
- 2026-06-03: Predeclared and ran LLM-heavy Decision 0007 v1 validation50.
  Live run had 50/50 structured outputs, 0 call/adapter parse failures, 47/50
  selected evidence exact, 44/50 raw Purist, 44/50 mechanical-adapter Purist,
  and 1 raw-correct-to-adapter-wrong regression. No-call replay raises
  selected evidence to 49/50, but the run fails the predeclared promotion rule;
  revise before validation250.
- 2026-06-03: Ran fresh live matched validation25 for repaired LLM-heavy and
  hybrid candidates, then replayed saved outputs through narrow contract
  repairs. LLM-heavy live reached 25/25 raw and adapted Purist with 24/25
  selected evidence exact; replay fixes row `409` malformed `≤` evidence to
  25/25. Hybrid live reached 25/25 selected evidence exact, 25/25 source ids
  valid, and 25/25 adapted Purist with two LLM-candidate schema failures;
  replay fixes `assertion_status=historical` to 25/25 structured candidates.
- 2026-06-03: Repaired the remaining hybrid selected-evidence exactness defect
  with source-checked case-only evidence canonicalization and source-type
  provenance repair. No-call replay now has 25/25 selected evidence exact,
  25/25 source ids valid, 25/25 hybrid-adjudicator Purist, and
  `promote_to_50`.
- 2026-06-03: Implemented the LLM-heavy Decision 0007 targeted contract fixes:
  source-checked repair for malformed `≤` evidence-copy artifacts and
  cluster-cadence adapter rendering as bare cadence labels. No-call replay of
  v1 saved outputs now has 25/25 selected evidence exact, 25/25 mechanical
  adapter Purist, 0 adapter regressions, and
  `promote_to_validation50_allowed_by_gate`.
- 2026-06-03: Ran live LLM-heavy Decision 0007 v1 validation25 smoke: 25/25
  structured, 0 parse/call
  failures, 25/25 raw parser labels scorable and Purist. Gate still rejects:
  selected evidence exact is 22/25 and the mechanical adapter regresses
  raw-correct cluster-cadence rows `187`, `190`.
- 2026-06-03: Implemented the LLM-heavy Decision 0007 v1 prompt/schema
  contract: exact Unicode evidence copying, clinical-kind/operand consistency,
  vague-count operands, parser-ready raw-label grammar, and v1 artifact paths.
- 2026-06-03: Completed LLM-heavy Decision 0007 validation25 contract triage.
  It identified exact-evidence escaping, operand-kind inconsistency,
  cluster-axis/vague-count issues, and 0/25 parser-ready raw labels.
- 2026-06-03: Repaired `hybrid_parallel_state_candidate_reasoner`
  source-id provenance and LLM-candidate `future` temporality schema handling.
  Replay now has 25/25 source ids valid, 25/25 structured LLM-candidate records,
  0 parse/schema failures, 24/25 selected evidence exact, and
  `promote_to_50`, pending evidence review.
- 2026-06-03: Ran live matched validation25 smokes for
  `llm_heavy_evidence_selection_with_deterministic_adapters` and
  `hybrid_parallel_state_candidate_reasoner`; neither earned validation50.

## Immediate Next Step

Run a thermonuclear/code-quality review of the safety-floor change and draft the
frozen-test audit plan before any holdout execution.
