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
- The fixed validation hard50 agentic follow-up completed E5/E1/E2 and stopped
  before E3/E4. The D-series redesign supersedes unrun E3/E4 live designs and
  prohibits parser candidates as prediction-bearing prompt context:
  `experiments/gan2026_agentic_hard50_redesign_after_e2_stop_2026-06-12.md`.
- D0 no-call boundary-guide rescue replay is complete:
  `experiments/gan2026_agentic_hard50_boundary_guide_rescue_replay_2026-06-12.md`.
  `higher_burden_only` passed the D0 gate with `35/50` Purist, `36/50`
  Pragmatic, `4` changed labels, `3` wrong-to-correct, `0` correct-to-wrong,
  net `+3`, and changed-label precision `0.750`. This is validation-development
  saved-output replay only.
- D1 boundary-audit prompt v2 is complete:
  `experiments/gan2026_agentic_boundary_audit_prompt_v2_panel_2026-06-12.md`
  passed the micro-panel gate (`10/12` Purist), but
  `experiments/gan2026_agentic_boundary_audit_prompt_v2_hard50_2026-06-12.md`
  failed the hard50 gate (`38/50` Purist, `8` wins, `2` losses; max allowed
  losses was `1`). D1 must not escalate to validation250 or D3.

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
- Do not escalate current agentic conditions to full validation. Original E3/E4
  live designs remain blocked; reopened branches must follow the D-series
  rescue-only redesign and pass its hard50 gates first.

## Active Priorities

1. Decide whether to run D2 direct-plus-boundary-critic rescue-only, or stop
   reopened agentic work with D0 promoted as a no-call rescue signal and D1
   rejected on hard50.
2. Populate the Architecture Thesis Scorecard from existing Gan artifacts,
   using the compact failure-mode comparison and E5/E1/E2/D-series hard50
   artifacts as the agentic failure-family input.
3. Decide whether Gan close-off needs any optional validation750 model
   confirmations, or explicitly defer them before returning to ExECTv2.

## Work Board

### Now

- Decide whether to run D2 direct-plus-boundary-critic rescue-only or close the
  agentic branch after D1 hard50 rejection.

### Next

- Populate the Architecture Thesis Scorecard from existing Gan artifacts.
- Decide whether Gan close-off needs any optional validation750 model
  confirmations, or explicitly defer them before returning to ExECTv2.

### Blocked

- Any Gan holdout-facing rerun or row-level test analysis is blocked without
  explicit frozen-protocol authorization.
- Multi-agent superiority claims and full-validation escalation for current
  tool-using or multi-agent conditions remain blocked without stable
  matched-budget single-agent evidence and a separate frozen escalation reason.
  D0 is saved-output replay, not validation250-ready by itself.
- D1 boundary-audit prompt v2 is blocked from validation250 and D3 escalation
  because it missed the hard50 gate with `2` regressions.
- Original E3/E4 live runs are blocked by the E2 gate failure. D3 is blocked
  until D1 or D2 passes the D-series hard50 gate.

### Backlog

- If agentic work continues beyond D0, keep parser candidates out of
  prediction-bearing prompts and start with D1 boundary-audit or D2
  direct-plus-boundary-critic rescue-only designs. Do not reuse E3/E4 as-is.

### Done Recently

- 2026-06-12: Completed the D-series hard50 redesign, D0 replay, and D1
  boundary-audit prompt v2. D0 `higher_burden_only` passed as saved-output
  rescue evidence; D1 panel passed but hard50 failed (`8` wins, `2` losses).
- 2026-06-12: Executed E5/E1/E2 hard50 follow-up and stopped before E3/E4 by
  gate. Parser candidates were harmful as prompt context; boundary-guide-only
  context supplied the rescue signal used by D0.
- 2026-06-12: Produced compact paper-facing Gan failure-mode comparison table:
  `docs/research/gan2026_failure_mode_comparison_table_2026-06-12.md`.
  It consolidates Phase 3 validation750 failure counts, Phase 4 aggregate
  `test450` reads, and the validation hard50 agentic revise/reject gate without
  new holdout analysis.
- 2026-06-12: Completed validation25 smokes, deterministic normalized-label
  voting, and the fixed hard50 active-condition comparison that made the
  agentic hard-slice follow-up necessary.

## Core Artifacts

- `docs/research/gan2026_closeoff_report_2026-06-12.md`
- `docs/research/gan2026_failure_mode_comparison_table_2026-06-12.md`
- `docs/research/gan2026_agentic_pipeline_phase_plan_2026-06-12.md`
- `experiments/gan2026_agentic_hard50_redesign_after_e2_stop_2026-06-12.md`
- `experiments/gan2026_agentic_hard50_boundary_guide_rescue_replay_2026-06-12.md`
- `experiments/gan2026_agentic_boundary_audit_prompt_v2_panel_2026-06-12.md`
- `experiments/gan2026_agentic_boundary_audit_prompt_v2_hard50_2026-06-12.md`
- Agentic validation25/hard50 matched-budget, fallback, tool-context, and
  self-consistency runs are indexed in `experiments/RUN_INDEX.md`.
- `experiments/gan2026_agentic_validation_hard50_manifest_2026-06-12.json`
- `experiments/gan2026_agentic_validation25_format_repair_analysis_2026-06-12.md`
