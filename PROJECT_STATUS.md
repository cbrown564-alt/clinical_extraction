# Project Status

Last updated: 2026-06-12

## Active Objective

Complete the final Gan 2026 agentic-pipeline phases before returning to
ExECTv2.

Current promoted Gan direction: `hybrid_structured_events` - an LLM extracts
structured seizure-frequency events from raw note text, then deterministic
normalization, projection, rendering, and scoring produce Gan-compatible output.

Controlling synthesis: `docs/research/gan2026_closeoff_report_2026-06-12.md`.
Next phase control surface:
`docs/research/gan2026_agentic_pipeline_phase_plan_2026-06-12.md`.

## Recent Context

- Gan 2026 now has a complete comparison spine across deterministic, hybrid,
  and LLM architectures on the shared `gan2026/runner.py` and
  `gan2026/cli/llm_pipeline_cli.py` surface.
- `hybrid_structured_events` is the best current close-off candidate:
  - GPT-4.1-mini validation750 Phase 3: `748/750` rendered,
    `661/748` Purist-correct, `679/748` Pragmatic-correct.
  - Frozen GPT-4.1-mini `test450` Phase 4 aggregate audit: `448/450`
    rendered, `364/448` Purist-correct, `381/448` Pragmatic-correct.
  - User-approved SE v0.6 validation750 confirmations completed:
    DeepSeek `622/745` Purist-correct and `646/745` Pragmatic-correct;
    Qwen `638/746` Purist-correct and `656/746` Pragmatic-correct.
- Reset-native CandidateSet hybrid remains important for the transparency and
  verifier thesis, but is not the current implementation headline: on frozen
  `test450` it scored `269/334` Purist-correct with `116` null rows and `30`
  routed rows.
- Deterministic canonical remains a useful comparator and de-overfitting lesson:
  it stayed strong on validation but dropped to `329/450` Purist-correct on
  frozen `test450`, reinforcing that validation score alone is not enough.
- ExECTv2 Phase 6 is complete and parked. The all-entity LLM-only full-200
  audit was contract-clean but not competitive: semantic overall F1 `0.084`
  per-item / `0.232` per-letter, benchmark with-CUI `0.000` / `0.000`.
- User reframed Gan as having two final phases: define and implement a
  matched-budget agentic comparison, then test tool-using single agents against
  multi-agent pipelines before Gan is accepted as closed for this cycle.

## Guardrails

- Gan split `gan2026_split_v1` is locked: 300 train, 750 validation, 450 holdout.
- Validation is development evidence, not a benchmark claim.
- Locked `test450` is aggregate-only. No row-level holdout tuning or error
  inspection is authorized.
- Any new holdout-facing Gan work requires a fresh frozen aggregate protocol and
  explicit user authorization.
- Evidence metrics are not uniform across architectures: `evidence_valid`,
  `evidence_text_contained`, and CandidateSet source-id validity are separate
  signals and should not be collapsed into one accuracy number.
- Describe `hybrid_structured_events` as hybrid LLM extraction plus
  deterministic normalization/projection, not as fully LLM-only.

## Active Priorities

1. Begin Gan Phase 6 implementation around single-agent self-consistency,
   parser-as-tool, boundary-guide retrieval, and matched-budget multi-agent
   comparison.
2. Wire the Phase 5 agentic contracts into a single experiment surface with
   budget accounting and trace emission.
3. Keep ExECTv2 parked until the agentic Gan phases are either completed or
   explicitly deferred.

## Work Board

### Now

- Wire the Phase 5 contracts into a Phase 6 runner surface for `single_greedy`,
  `single_self_consistency_temperature`, and `single_agent_tools`.
- Predeclare the first validation25 contract smoke for matched-budget
  single-agent self-consistency and parser/guide tool traces.

### Next

- Add trace schema/artifact writing for per-row model calls, tool calls,
  tool-output token estimates, final selection, and attribution layer.
- Add the first no-call or prompt-only runner mode to exercise Phase 6
  orchestration without spending model calls.
- Produce a compact failure-mode table for `hybrid_structured_events` versus
  deterministic and fully LLM comparators, then reuse it to seed hard-slice
  panels for the agentic comparison.

### Blocked

- Any Gan holdout-facing rerun or row-level test analysis is blocked without
  explicit frozen-protocol authorization.
- Any claim that a multi-agent pipeline is better is blocked until it is
  compared against a single-agent condition with matched model-call, token,
  tool-call, and aggregation budget.

### Backlog

- Decide whether reset-native verifier/action-policy work should continue as a
  paper-facing transparency thread after the implementation close-off.
- Populate the Architecture Thesis Scorecard from existing Gan artifacts:
  validation performance, frozen holdout performance, validation-to-test gap,
  evidence trace caveats, and modularity/auditability signal.
- Revisit comparator-label preservation only if verifier reject/abstain policy
  becomes active again.
- Revisit prior-visit/event-date context only if future residual analysis shows
  broad value and a clean source contract.

### Done Recently

- 2026-06-12: Completed Gan Phase 5 contract scaffolding:
  `AgentBudget`/`MatchedBudgetComparison`,
  `parse_seizure_frequency_candidates`, split-neutral `read_boundary_guide`,
  tests, and `docs/design/gan2026_agentic_phase5_contracts.md`.
- 2026-06-12: Added the Gan agentic-pipeline phase plan, making matched-budget
  single-agent versus multi-agent tool-use comparison the next major Gan phase.
- 2026-06-12: Completed user-approved SE v0.6 validation750 confirmations from
  the existing validation250 prefixes: DeepSeek `622/745` Purist and Qwen
  `638/746` Purist rendered-correct validation-only results.
- 2026-06-12: Added the Gan close-off synthesis and registry entry:
  `gan2026_closeoff_report_2026-06-12`.
- 2026-06-12: Completed ExECTv2 Phase 6 LLM-only all-9 dev140 and frozen
  full-200 overall audit. Result is historical context, not the active task.
- 2026-06-10: Completed Gan Phase 4 frozen GPT-4.1-mini `test450` aggregate
  audit; `hybrid_structured_events` led the compared architectures.
- 2026-06-09: Completed Gan Phase 3 GPT-4.1-mini validation750 comparison and
  cross-model Phase 1 synthesis.
- 2026-06-07: Completed Gan repo cleanup/consolidation Phases A-G and moved
  active Gan experimentation onto the shared runner/CLI surface.

## Core Artifacts

- Gan close-off report:
  `docs/research/gan2026_closeoff_report_2026-06-12.md`
- Gan agentic-pipeline phase plan:
  `docs/research/gan2026_agentic_pipeline_phase_plan_2026-06-12.md`
- Gan agentic Phase 5 contracts:
  `docs/design/gan2026_agentic_phase5_contracts.md`
- Frozen `test450` Phase 4 comparison:
  `experiments/gan2026_test450_phase4_comparison_report_gpt41mini_2026-06-10.md`
- GPT-4.1-mini Phase 3 validation750 comparison:
  `experiments/gan2026_three_way_comparison_phase3_report_gpt41mini_validation750_2026-06-09.md`
- Cross-model comparison:
  `docs/research/gan2026_cross_model_comparison_2026-06-09.md`
- SE v0.6 validation750 confirmations:
  `experiments/gan2026_v06_validation750_hybrid_structured_events_deepseek_2026-06-12.md`;
  `experiments/gan2026_v06_validation750_hybrid_structured_events_qwen3635b_2026-06-12.md`
- Three-way architecture plan:
  `docs/research/gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07.md`
- Architecture thesis scorecard plan:
  `docs/research/gan2026_evidence_grounded_thesis_assessment_plan_2026-06-07.md`
- Repo consolidation record:
  `docs/research/gan2026_repo_consolidation_and_cleanup_plan_2026-06-07.md`
