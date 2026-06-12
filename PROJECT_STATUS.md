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
- Post-voting validation25 active single-agent conditions and
  `multi_agent_matched` all reached `25/25` Purist/Pragmatic condition-final
  accuracy, making the prefix a smoke surface rather than a discriminator.
- A fixed validation hard50 slice is now predeclared from the validation-only
  atlas manifest. On that slice, `single_greedy` (`34/50` Purist) and
  same-model self-consistency (`32/50`) outperform `single_agent_tools`
  (`20/50`) and `multi_agent_matched` (`22/50`), so tool/multi-agent variants
  are revise/reject signals unless redesigned.

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
- Do not escalate current `single_agent_tools` or `multi_agent_matched` to full
  validation; they must first improve on the fixed hard50 slice without
  introducing high-cost regressions.

## Active Priorities

1. Produce the compact failure-mode comparison table for paper-facing Gan
   close-off, using the hard50 agentic result as the agentic decision gate.
2. Populate the Architecture Thesis Scorecard from existing Gan artifacts.

## Work Board

### Now

- Produce a compact failure-mode table for `hybrid_structured_events` versus
  deterministic, fully LLM, single-agent, and `multi_agent_matched` comparators;
  include the validation hard50 agentic regressions.

### Next

- Populate the Architecture Thesis Scorecard from existing Gan artifacts.

### Blocked

- Any Gan holdout-facing rerun or row-level test analysis is blocked without
  explicit frozen-protocol authorization.
- Any multi-agent superiority claim is blocked until matched-budget
  single-agent evidence is stable.
- Full-validation escalation for current tool-using or multi-agent agentic
  conditions is blocked by hard50 regressions.

### Backlog

- Run targeted validation hard-slice panels if the failure-mode table cannot
  distinguish single-agent and multi-agent mechanisms from existing artifacts.
- Redesign agentic tool/role context only if paper framing still needs an
  agentic comparison beyond the hard50 revise/reject signal.

### Done Recently

- 2026-06-12: Predeclared and ran validation hard50 active-condition agentic
  comparison:
  `experiments/gan2026_agentic_matched_budget_validation_hard50_active_conditions_live_prompt_v1_2026-06-12.md`.
  Result: `500` calls, `0` failures, `0` blocking parse/validation failures;
  condition-final Purist `single_greedy 34/50`, self-consistency `32/50`,
  `single_agent_tools 20/50`, `multi_agent_matched 22/50`. Current tool/multi
  variants should not move to full validation.
- 2026-06-12: Added deterministic normalized-label voting to
  `agentic_matched_budget`, aligned condition-final voting to parser-repaired
  decision labels, and completed validation25 single-agent/multi-agent smokes.
  Key artifacts:
  `experiments/gan2026_agentic_matched_budget_validation25_single_agent_live_prompt_v1_post_vote_2026-06-12.md`.
  Verification: focused pytest/Ruff passed; earlier full pytest was
  `1205 passed`; full-repo Ruff remains blocked by unrelated pre-existing lint
  debt.
## Core Artifacts

- `docs/research/gan2026_closeoff_report_2026-06-12.md`
- `docs/research/gan2026_agentic_pipeline_phase_plan_2026-06-12.md`
- `experiments/gan2026_agentic_matched_budget_validation25_single_agent_live_prompt_v1_post_vote_2026-06-12.md`
- `experiments/gan2026_agentic_matched_budget_validation25_multi_agent_live_prompt_v1_2026-06-12.md`
- `experiments/gan2026_agentic_matched_budget_validation_hard50_active_conditions_live_prompt_v1_2026-06-12.md`
- `experiments/gan2026_agentic_validation_hard50_manifest_2026-06-12.json`
- `experiments/gan2026_agentic_validation25_format_repair_analysis_2026-06-12.md`
