# ExECTv2 SeizureFrequency Agentic Redo — Predeclaration (2026-07-01)

Status: **predeclared, locked before any live call.** Implements
`docs/plans/proud-bubbling-ocean.md` Phase 3, informed by the Gan 2026
result (`docs/experiments/gan2026/agentic/gan2026_agentic_redo_results_2026-07-01.md`):
every new architecture beat plain single-prompt on Gan's hard50 by a wide
accuracy margin, dynamic orchestration beat static fan-out, but nothing
cleared the strict promotion gate at n=50 — likely a statistical-power
limit at that sample size, not proof the architectures don't help.

## Why SeizureFrequency, why this is a fair transfer test

SF is ExECTv2's "bridge" entity — the same clinical concept just tested on
Gan 2026, in a different corpus, schema, and scoring regime
(`docs/design/reliability_thesis.md` §2). ExECTv2 currently has zero
agentic infrastructure; this is a from-scratch build following the exact
pattern validated on Gan 2026 (genuine `dspy.ReAct` tool use; specialists
whose output schema cannot contain a final answer).

## Tool safety check (done before building anything)

A dictionary/CUI-lookup tool (the ExECTv2 analogue of nothing in the Gan
study, but a natural "concept normalization" tool) was considered and
**rejected**: `deterministic/concept_normalizer.py`'s
`InSampleConceptNormalizer` builds its lookup table directly from gold
annotations (explicitly labeled a leaky dev-only stub in its own
docstring), and `UmlsConceptNormalizer` is unimplemented (`NotImplementedError`
in both `__init__` and `canonicalize`). Wrapping either as an agent tool
would be a real gold-label leak or simply not work. **Two tools only**,
both confirmed gold-free:

- `check_evidence_in_letter(evidence_text: str) -> dict` — wraps
  `core/evidence.py`'s `evidence_is_substring`/`grade_evidence`, bound to
  the current letter. Answers "does this candidate quote actually appear
  in the note, and how exactly (exact / repaired-artifact / case /
  whitespace / section-adjacent)."
- `read_sf_boundary_guide(query: str) -> dict` — adapted from the existing
  clinical-decision prose already written for the v08 hybrid's SF stage
  (`llm/llm_sf_state_adjudicator.py`'s `_clinical_rules`,
  `_generic_seizure_policy`, `_seizure_free_anchor_guide`,
  `_typed_candidate_guide`, `_unknown_change_recovery_lane`,
  `_state_decision_guide`) — re-keyed into named, queryable guide entries
  mirroring Gan's `read_boundary_guide` shape. This is adaptation of
  already-reviewed clinical content, not new clinical judgment.

## Conditions

- `single_greedy` — the existing `llm/llm_only_single_pass.py`
  (`DspySinglePassSFExtractor`, one `dspy.Predict` call, SF-only,
  currently `dev`-only per its own runner guard). Reused as-is, not
  rebuilt.
- `single_agent_tools_react` — `dspy.ReAct` over the same signature shape,
  tools = [`check_evidence_in_letter`, `read_sf_boundary_guide`],
  `max_iters=3` (matching the Gan budget shape: 3 ReAct turns + 1
  extraction call = 4 model calls).
- `multi_agent_d3_static` — three specialists, evidence-only output
  schema (no `mentions`/final-answer field, structurally same guarantee as
  the Gan redo):
  - `active_rate_fact_lister`: current frequency-bearing facts (count,
    range, period) only.
  - `seizure_free_hazard_lister`: seizure-free, historical, negated, or
    superseded evidence only.
  - `cluster_or_change_lister`: cluster cadence/events-per-cluster and
    frequency-*change* evidence only — deliberately targeting SF's two
    documented weak spots (cluster-axis ambiguity and the direction-blind
    "changed" class, per `docs/experiments/exectv2/seizure_frequency/exectv2_sf_canonical_metric_row_analysis_2026-06-29.md`
    and the Phase 6 row-analysis it supersedes).
  - `resolver`: final SF mention list (entity, text, attributes, evidence,
    confidence, rationale — the real ExECTv2 `SeizureFrequency` schema,
    richer than Gan's single label), must cite which specialist evidence
    it used per mention.
- `multi_agent_dynamic_orchestrator` — same three specialists plus both
  tools, wrapped as callables for a `dspy.ReAct` orchestrator,
  `max_iters=6` (same cap shape as the Gan redo).

## Scoring

Production scorer: `scoring/seizure_frequency.py::score_frequency_state`
(the same function underlying the v08 hybrid's SF `clinical_headline`
component, F1 0.9053 dev140) — **not** the `state_profile`/GEPA-verify
metric the 53-letter hard list was originally adjudicated on, so this
redo's numbers are comparable to the production headline, not to that
prior GEPA work. Per-letter F1 replaces Gan's per-row Purist/Pragmatic
correctness; win/loss is defined per letter as candidate-F1 vs
comparator-F1 (win = strictly higher, loss = strictly lower, tie
otherwise).

## Panels and staged gate

- **Smoke**: 5 dev letters, near-zero cost, all 4 conditions (0 call
  failures, coherent `dspy.ReAct` trajectories, valid mention schema
  required before spending further).
- **Hard panel**: the 53 dev140 letters already flagged as disagreement-
  bearing by the SF canonical row-adjudication
  (`exectv2_sf_canonical_metric_row_analysis_2026-06-29.md:138-192`) —
  reused as the hard slice rather than building a new one, rescored on
  `score_frequency_state` per above. This is the ExECTv2-side analogue of
  Gan's hard50.
- **Locked gate** (same shape as the Gan redo, not re-derived without
  reason): promote to the full dev140 only if, versus `single_greedy` on
  the 53-letter hard panel, **net wins ≥ 5 and losses ≤ 1** (Angle 1) or
  the dynamism comparison (`multi_agent_dynamic_orchestrator` vs
  `multi_agent_d3_static`) clears **wins ≥ 3, losses ≤ 1** (Angle 2). The
  Gan redo's own finding that this bar may be unrealistic at n≈50 is
  carried over explicitly as a lens for interpreting the result, not as
  grounds to loosen the threshold pre-hoc.

## Stop rules (same as the Gan redo)

No `test59`/`test450` use under any outcome. No row-level holdout
inspection. No tuning of tool contracts, specialist schemas, or gate
thresholds after seeing a stage's results — a failed gate is reported, not
redesigned around. Systemic failure (>10% call/parse failure at any stage)
stops progression to the next stage.

## What gets written up regardless of outcome

A dated results doc stating which stage was reached, the gate outcome, and
an honest reading against the Gan 2026 finding — including if SF shows a
different pattern than Gan (plausible, since SF's own genuine-error
composition is dominated by the "changed"/direction and cluster-boundary
classes per prior work, not a generic hard-extraction problem the Gan
panel's boundary conditions represent).
