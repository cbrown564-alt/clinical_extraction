# Project Status

Last updated: 2026-06-12

## Active Objective

Close the final Gan 2026 agentic-pipeline phases before returning to ExECTv2.

Promoted Gan direction: `hybrid_structured_events` - LLM structured-event
extraction plus deterministic normalization/projection/rendering/scoring. Control
docs: `docs/research/gan2026_closeoff_report_2026-06-12.md` and
`docs/research/gan2026_agentic_pipeline_phase_plan_2026-06-12.md`.

## Recent Context

- `hybrid_structured_events` remains the close-off candidate: GPT-4.1-mini
  validation750 `661/748` Purist rendered-correct; frozen `test450` aggregate
  audit `364/448` Purist and `381/448` Pragmatic rendered-correct.
- User-approved SE v0.6 validation750 confirmations completed: DeepSeek
  `622/745` Purist and Qwen `638/746` Purist; validation-only evidence.
- Agentic Phase 6 is now live on validation development surfaces. The
  validation25 single-agent run used condition filtering to skip cross-model and
  multi-agent calls: `150/150` decision records, `0` call failures, `0` blocking
  parse failures. Condition-final Purist: `single_greedy 24/25`,
  `single_self_consistency_temperature 25/25`, `single_agent_tools 24/25`.
- The validation25 format-repair review found underscore-separated labels and a
  bare selected-evidence rate gap behind rows `10`, `278`, and `419`. No-call
  diagnostic reparse now aligns all three active single-agent conditions on
  those rows and gives row-final `25/25` Purist/Pragmatic under the parser
  replay; live prompt v1 smoke is still required.
- ExECTv2 Phase 6/7 is complete and parked; all-entity LLM-only full-200
  semantic F1 was `0.084` per-item / `0.232` per-letter.

## Guardrails

- Gan split `gan2026_split_v1` is locked: 300 train, 750 validation, 450 holdout.
- Validation is development evidence. Locked `test450` is aggregate-only; no
  row-level holdout tuning or error inspection is authorized.
- New holdout-facing Gan work requires explicit frozen-protocol authorization.
- Keep evidence metrics architecture-specific: `evidence_valid`,
  `evidence_text_contained`, and CandidateSet source-id validity are different.
- Describe `hybrid_structured_events` as hybrid LLM extraction plus
  deterministic normalization/projection, not fully LLM-only.
- Do not claim multi-agent value until compared with a single-agent condition
  under matched model-call, token, tool-call, and aggregation budget.

## Active Priorities

1. Re-run validation25 single-agent live smoke under agentic prompt v1 and the
   updated repair contract.
2. Add deterministic normalized-label voting once the live v1 single-agent
   comparator is stable.
3. Run `multi_agent_matched` only after the single-agent comparator and
   aggregation/repair policy are stable.

## Work Board

### Now

- Re-run validation25 single-agent smoke under
  `gan2026_agentic_matched_budget_prompt_v1` and confirm call failures,
  parse/repair notes, condition-final accuracy, and any remaining disagreement
  rows.

### Next

- Add deterministic normalized-label voting once live repair attribution is
  clean.
- Compare `multi_agent_matched` only after the single-agent comparator uses the
  same model-call, token, tool-call, and aggregation budget.
- Produce a compact failure-mode table for `hybrid_structured_events` versus
  deterministic and fully LLM comparators; reuse it for agentic hard slices.

### Blocked

- Any Gan holdout-facing rerun or row-level test analysis is blocked without
  explicit frozen-protocol authorization.
- Any multi-agent superiority claim is blocked until matched-budget
  single-agent evidence is stable.

### Backlog

- Decide whether reset-native verifier/action-policy work continues after
  implementation close-off.
- Populate the Architecture Thesis Scorecard from existing Gan artifacts.

### Done Recently

- 2026-06-12: Analyzed validation25 agentic direct-label repair families and
  rows `10`, `278`, `419`; added underscore-label format repair, bare
  selected-evidence rate parsing, and agentic prompt v1. No-call diagnostic
  reparse of the saved raw outputs resolves the `3` condition-final
  disagreement rows and changes preferred row-final replay from `24/25` to
  `25/25` Purist/Pragmatic.
- 2026-06-12: Added agentic condition filtering and ran validation25
  single-agent live smoke:
  `experiments/gan2026_agentic_matched_budget_validation25_single_agent_live_2026-06-12`
  (`150` calls, `150` decision records, `0` call failures, `0` blocking parse
  failures; condition-final Purist `24/25`, `25/25`, `24/25`).
- 2026-06-12: Added live-call execution to `agentic_matched_budget` and saved
  validation1 all-condition transport smoke (`14` calls, `0` failures).
- 2026-06-12: Added Phase 6 prompt-only runner and validation25 no-call smoke;
  Phase 5 contracts and phase plan are complete.
- 2026-06-12: Completed Gan close-off synthesis and SE v0.6 validation750
  DeepSeek/Qwen confirmations.
- 2026-06-10: Completed Gan Phase 4 frozen GPT-4.1-mini `test450` aggregate
  audit; `hybrid_structured_events` led compared architectures.

## Core Artifacts

- `docs/research/gan2026_closeoff_report_2026-06-12.md`
- `docs/research/gan2026_agentic_pipeline_phase_plan_2026-06-12.md`
- `experiments/gan2026_agentic_validation25_format_repair_analysis_2026-06-12.md`
- `experiments/gan2026_agentic_matched_budget_validation25_single_agent_live_2026-06-12.md`
- `experiments/gan2026_agentic_matched_budget_validation1_live_smoke_2026-06-12.md`
- `experiments/gan2026_agentic_matched_budget_validation25_prompt_only_2026-06-12.md`
- `experiments/gan2026_test450_phase4_comparison_report_gpt41mini_2026-06-10.md`
- `experiments/gan2026_three_way_comparison_phase3_report_gpt41mini_validation750_2026-06-09.md`
