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
- The fixed validation hard50 agentic follow-up is now complete through its
  predeclared stop gate. E5 no-call selective fallback found no promotable
  policy; E1 isolated parser context as harmful and boundary-guide-only context
  as non-harmful; E2 boundary-guide self-consistency reached `34/50` Purist
  with `4` wins and `2` losses versus same-model self-consistency, missing the
  `>=5` win gate. E3/E4 were not run.
- A new validation-cycle redesign now supersedes the unrun E3/E4 live designs:
  `experiments/gan2026_agentic_hard50_redesign_after_e2_stop_2026-06-12.md`.
  It treats parser candidates as prohibited prediction-bearing prompt context
  for this branch and reframes the next work as rescue-only boundary auditing
  with explicit fallback gates.

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
- Do not escalate current `single_agent_tools`, parser-tool context,
  boundary-guide self-consistency, or `multi_agent_matched` to full validation.
  The original E3/E4 live designs remain blocked; any reopened agentic branch
  must follow the D-series rescue-only redesign and pass its hard50 gates first.

## Active Priorities

1. Decide whether to execute D0 no-call boundary-guide rescue replay from the
   D-series redesign, or defer reopened agentic work and return to close-off.
2. Populate the Architecture Thesis Scorecard from existing Gan artifacts,
   using the compact failure-mode comparison and E5/E1/E2/D-series hard50
   artifacts as the agentic failure-family input.
3. Decide whether Gan close-off needs any optional validation750 model
   confirmations, or explicitly defer them before returning to ExECTv2.

## Work Board

### Now

- Decide whether to execute D0 no-call boundary-guide rescue replay, the first
  step in the D-series rescue-only redesign.

### Next

- Populate the Architecture Thesis Scorecard from existing Gan artifacts.
- Decide whether Gan close-off needs any optional validation750 model
  confirmations, or explicitly defer them before returning to ExECTv2.

### Blocked

- Any Gan holdout-facing rerun or row-level test analysis is blocked without
  explicit frozen-protocol authorization.
- Any multi-agent superiority claim is blocked until matched-budget
  single-agent evidence is stable.
- Full-validation escalation for current tool-using or multi-agent agentic
  conditions is blocked by hard50 regressions.
- The original E3 boundary-safe prompt and E4 multi-agent role-redesign live
  runs are blocked by the E2 gate failure. D3 evidence-first role redesign is
  separately blocked until D1 or D2 passes the D-series hard50 gate.

### Backlog

- If agentic work is reopened beyond D0, keep parser candidates out of
  prediction-bearing prompts and start with D1 boundary-audit or D2
  direct-plus-boundary-critic rescue-only designs. Do not reuse E3/E4 as-is.

### Done Recently

- 2026-06-12: Iterated the agentic hard50 design after the E2 stop:
  `experiments/gan2026_agentic_hard50_redesign_after_e2_stop_2026-06-12.md`.
  The new D-series sequence is D0 no-call boundary-guide rescue replay, D1
  boundary audit prompt v2, D2 direct-plus-boundary-critic rescue-only, D3
  evidence-first roles, and D4 split-neutral boundary robustness. Parser
  candidates are excluded from prediction-bearing prompts in this branch.
- 2026-06-12: Executed E5/E1/E2 hard50 agentic follow-up and stopped before
  E3/E4 by gate:
  `experiments/gan2026_agentic_hard50_selective_fallback_replay_2026-06-12.md`,
  `experiments/gan2026_agentic_hard50_tool_context_ablation_2026-06-12.md`,
  and
  `experiments/gan2026_agentic_hard50_tool_self_consistency_2026-06-12.md`.
  E5: no promotable fallback policy (`0` promoted policies). E1:
  boundary-guide-only `34/50` Purist, no-tool `30/50`, parser-only `21/50`,
  parser-plus-guide `19/50`. E2: boundary-guide self-consistency `34/50`
  Purist, `35/50` Pragmatic, `4` wins and `2` losses versus
  `single_self_consistency_temperature`; gate required at least `5` wins and
  at most `2` losses, so E3/E4 were not run.
- 2026-06-12: Produced compact paper-facing Gan failure-mode comparison table:
  `docs/research/gan2026_failure_mode_comparison_table_2026-06-12.md`.
  It consolidates Phase 3 validation750 failure counts, Phase 4 aggregate
  `test450` reads, and the validation hard50 agentic revise/reject gate without
  new holdout analysis.
- 2026-06-12: Designed next agentic experiments from hard50 error analysis:
  `experiments/gan2026_agentic_hard50_error_analysis_experiment_design_2026-06-12.md`.
  Next action is E5 no-call selective fallback replay; E1 tool-context ablation
  follows only if no useful fallback policy exists.
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
- `docs/research/gan2026_failure_mode_comparison_table_2026-06-12.md`
- `docs/research/gan2026_agentic_pipeline_phase_plan_2026-06-12.md`
- `experiments/gan2026_agentic_matched_budget_validation25_single_agent_live_prompt_v1_post_vote_2026-06-12.md`
- `experiments/gan2026_agentic_matched_budget_validation25_multi_agent_live_prompt_v1_2026-06-12.md`
- `experiments/gan2026_agentic_matched_budget_validation_hard50_active_conditions_live_prompt_v1_2026-06-12.md`
- `experiments/gan2026_agentic_hard50_error_analysis_experiment_design_2026-06-12.md`
- `experiments/gan2026_agentic_hard50_redesign_after_e2_stop_2026-06-12.md`
- `experiments/gan2026_agentic_hard50_selective_fallback_replay_2026-06-12.md`
- `experiments/gan2026_agentic_hard50_tool_context_ablation_2026-06-12.md`
- `experiments/gan2026_agentic_hard50_tool_self_consistency_2026-06-12.md`
- `experiments/gan2026_agentic_validation_hard50_manifest_2026-06-12.json`
- `experiments/gan2026_agentic_validation25_format_repair_analysis_2026-06-12.md`
