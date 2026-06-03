# Project Status

Last updated: 2026-06-03

## Active Objective

Build a Gan 2026 seizure-frequency extraction pipeline that can reach at least
0.9000 Purist F1 on development surfaces while preserving evidence trails,
component ablations, split discipline, and conservative benchmark language.

## Current Strategy

Keep frozen comparators stable while revising the predeclared architecture
candidates after their repaired matched validation25 smoke comparison. The
current comparison artifact is
`experiments/gan2026_repaired_architecture_matched_validation25_comparison_2026-06-03.md`.
The first validation50 escalation was LLM-heavy Decision 0007 v1; interpretation
is
`experiments/gan2026_llm_heavy_decision0007_v1_validation50_interpretation_2026-06-03.md`.

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

1. Revise LLM-heavy v1 before validation250: bimonthly operands, weekday/vague
   frequency operands, `≤ N` upper-bound semantics, evidence contiguity, and
   raw-correct adapter fallback.
2. Decide whether hybrid validation50 should run as the robustness lane, given
   LLM-heavy validation50 failed its promotion stop rule.
3. Preserve attribution language: hybrid for semantic deterministic
   participation; LLM-heavy only for deterministic rendering from
   model-selected facts and operands.
4. Treat no-call replays as contract diagnostics, not fresh live
   evidence.

## Work Board

### Now

- Triage LLM-heavy validation50 failure rows `10`, `743`, `744`, `763`, `816`,
  `959`, and `987` before any validation250 escalation.
- Decide whether to run hybrid validation50 now or first repair the LLM-heavy
  validation50 contract.

### Next

- Run hybrid validation50 only with its own predeclaration and stop rule.
- Keep Qwen/minimal-evidence-selector transfer as a secondary lane after the
  architecture smokes clarify the output contract.

### Blocked

- Benchmark language and holdout analysis are blocked until replication
  comparability and locked-test discipline permit them.
- Qwen 3.6 full v5 validation ladder remains blocked until strict
  schema-compatible output or a named Qwen schema-repair ablation exists.

### Done Recently

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

Triage the LLM-heavy validation50 failure rows and choose whether the next live
spend should be hybrid validation50 or an LLM-heavy v2 validation25 repair
smoke.
