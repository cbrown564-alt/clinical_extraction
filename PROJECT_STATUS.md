# Project Status

Last updated: 2026-06-12

## Active Objective

Close off the Gan 2026 seizure-frequency pipeline before returning to ExECTv2.

Current promoted Gan direction: `hybrid_structured_events` - an LLM extracts
structured seizure-frequency events from raw note text, then deterministic
normalization, projection, rendering, and scoring produce Gan-compatible output.

Controlling synthesis: `docs/research/gan2026_closeoff_report_2026-06-12.md`.

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
  Resume ExECTv2 only after Gan is accepted as closed for this cycle.

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

1. Mark Gan closed for this cycle unless the close-off report needs a final
   wording patch from the SE v0.6 confirmation runs.
2. Populate the Architecture Thesis Scorecard from existing Gan artifacts:
   validation performance, frozen holdout performance, validation-to-test gap,
   evidence trace caveats, and modularity/auditability signal.
3. Resume ExECTv2 planning on `dev`; hybrid all-9 is the likely next family.

## Work Board

### Now

- Decide whether the Gan close-off report needs a short addendum for the
  completed DeepSeek/Qwen SE v0.6 validation750 confirmations.
- Then mark Gan closed for this cycle and resume ExECTv2.

### Next

- Produce a compact failure-mode table for `hybrid_structured_events` versus
  deterministic and fully LLM comparators.

### Blocked

- Any Gan holdout-facing rerun or row-level test analysis is blocked without
  explicit frozen-protocol authorization.

### Backlog

- Decide whether reset-native verifier/action-policy work should continue as a
  paper-facing transparency thread after the implementation close-off.
- Revisit comparator-label preservation only if verifier reject/abstain policy
  becomes active again.
- Revisit prior-visit/event-date context only if future residual analysis shows
  broad value and a clean source contract.

### Done Recently

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
