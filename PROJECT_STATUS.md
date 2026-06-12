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
- Agentic Phase 6 prompt-v1 validation25 single-agent live smoke is complete:
  `150/150` decision records, `0` call failures, `0` blocking parse/validation
  failures, and all three active single-agent conditions at `25/25`
  Purist/Pragmatic condition-final accuracy. The former repair rows `10`,
  `278`, and `419` now align across conditions; row `187` still has a
  non-blocking label disagreement (`1 per 7 to 9 day` versus `2 per month`) that
  scores correct under current mapping.
- `agentic_matched_budget` now exposes deterministic normalized-label voting:
  raw model labels, normalized vote labels, vote counts, repair-event counts,
  and `raw_model_plus_deterministic_format_vote` attribution are recorded per
  condition when voting/format repair affects the final label.

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

1. Re-run validation25 single-agent smoke with deterministic voting and compare
   row `187` plus any vote/repair attribution changes.
2. Run `multi_agent_matched` only after the single-agent comparator and
   aggregation/repair policy are stable.
3. Produce the compact failure-mode comparison table for paper-facing Gan
   close-off once the agentic comparator is settled.

## Work Board

### Now

- Re-run validation25 single-agent smoke after deterministic voting; compare row
  `187` and vote/repair attribution against the prompt-v1 live artifact.

### Next

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

- Populate the Architecture Thesis Scorecard from existing Gan artifacts.

### Done Recently

- 2026-06-12: Added deterministic normalized-label voting to
  `agentic_matched_budget` with explicit raw-label, normalized-label,
  vote-count, repair-event, and attribution fields. Verification: full pytest
  `1205 passed`; touched-file Ruff passed. Full-repo Ruff remains blocked by
  unrelated pre-existing lint debt outside this change.
- 2026-06-12: Re-ran validation25 single-agent live smoke under
  `gan2026_agentic_matched_budget_prompt_v1`:
  `experiments/gan2026_agentic_matched_budget_validation25_single_agent_live_prompt_v1_2026-06-12.md`.
  Result: `150` calls, `0` failures, `0` blocking parse/validation failures,
  condition-final Purist/Pragmatic `25/25` for all three active single-agent
  conditions; row `187` remains a scoring-equivalent label disagreement.
## Core Artifacts

- `docs/research/gan2026_closeoff_report_2026-06-12.md`
- `docs/research/gan2026_agentic_pipeline_phase_plan_2026-06-12.md`
- `experiments/gan2026_agentic_matched_budget_validation25_single_agent_live_prompt_v1_2026-06-12.md`
- `experiments/gan2026_agentic_validation25_format_repair_analysis_2026-06-12.md`
