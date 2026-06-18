# Gan 2026 Agentic Hard50 Error Analysis And Experiment Design

Date: 2026-06-12

Status: complete validation-development design artifact. Executed through E2 on
2026-06-12; the unrun E3/E4 live designs are superseded by
`experiments/gan2026_agentic_hard50_redesign_after_e2_stop_2026-06-12.md`.

## Scope

This design responds to the fixed validation hard50 result in:

```text
experiments/gan2026_agentic_matched_budget_validation_hard50_active_conditions_live_prompt_v1_2026-06-12.md
```

It uses only validation development artifacts. It does not authorize locked-test
row inspection, scorer changes, prompt tuning from test, rule tuning from test,
or full-validation escalation.

The immediate question is narrow:

```text
Do the current tool-using and multi-agent traces contain enough high-precision
signal to justify more agentic work, or should the current branch be rejected
until tool context and role design are changed?
```

## Protocol Position

- Work class: validation hard-slice error analysis plus experiment design.
- Split: `gan2026_split_v1` validation only.
- Surface: fixed hard50 manifest,
  `experiments/gan2026_agentic_validation_hard50_manifest_2026-06-12.json`.
- Scorer: existing Gan-compatible Purist first, Pragmatic as side-car.
- Saturation context: validation25 active agentic conditions all reached
  `25/25`, so aggregate validation25 is a smoke surface, not a discriminator.
- Research claims touched: transparency, matched-budget agentic comparison,
  deterministic-tool attribution, and selective-action calibration.
- Attribution boundary: parser candidates, boundary guides, deterministic label
  repair, and normalized-label voting are not LLM-owned clinical discovery.

## Source Artifacts

| Artifact | Role |
| --- | --- |
| `experiments/gan2026_agentic_matched_budget_validation_hard50_active_conditions_live_prompt_v1_2026-06-12.jsonl` | Per-row condition traces, raw model calls, normalized votes, call-level comparisons. |
| `experiments/gan2026_agentic_matched_budget_validation_hard50_active_conditions_live_prompt_v1_2026-06-12.md` | Reported hard50 metrics and budget summary. |
| `experiments/gan2026_agentic_validation_hard50_manifest_2026-06-12.json` | Fixed validation hard50 row list and predeclared hidden-family tags. |
| `` | Phase 5/6 definitions, matched-budget requirements, and tool contracts. |
| `docs/design/gan2026_saturated_validation_protocol.md` | Controls why this design uses hard slices, selective action, and no-call replay before broader validation. |

## Current Result

| Condition | Purist | Pragmatic | Notes |
| --- | ---: | ---: | --- |
| `single_greedy` | 34/50 | 36/50 | Best hard50 condition-final result. |
| `single_self_consistency_temperature` | 32/50 | 34/50 | Same-model voting did not beat greedy on this slice. |
| `single_agent_tools` | 20/50 | 22/50 | 0 Purist wins and 12 losses versus self-consistency. |
| `multi_agent_matched` | 22/50 | 24/50 | 0 Purist wins and 10 losses versus self-consistency. |

The hard50 slice differentiates the saturated validation25 result. The current
tool-using and multi-agent variants are revise/reject signals and must not move
to full validation without passing the gates below.

## Immediate Decision

Do not promote either `single_agent_tools` or `multi_agent_matched` as currently
implemented.

The next action is E5 no-call selective fallback replay, because it can answer
whether the existing traces contain usable disagreement signal without spending
new model calls or changing prompts. If E5 cannot produce a positive
changed-label precision profile, run E1 tool-context ablation. New live
multi-agent calls are deferred until E1/E3 show that safer tool context improves
the hard slice.

Execution order:

```text
E5 -> E1 -> E2 -> E3 -> E4
```

Execution note, 2026-06-12:

- E5 found no promotable selective fallback policy.
- E1 found parser context harmful and boundary-guide-only context non-harmful.
- E2 boundary-guide self-consistency reached `34/50` Purist with `4` wins and
  `2` losses versus `single_self_consistency_temperature`, missing the
  predeclared `>=5` win gate.
- E3/E4 below are retained as historical planned designs. They are not
  authorized live runs unless rewritten under the rescue-only redesign in
  `experiments/gan2026_agentic_hard50_redesign_after_e2_stop_2026-06-12.md`.

## Error Analysis

### Shared Pattern

The tool and multi-agent conditions did not fail because of transport,
unscorable labels, or call failures. They failed after producing parseable
decision records.

The dominant pattern is semantic over-selection of seizure-free, unknown, or
lower-burden interpretations in rows where the direct single-agent baseline
retains the stronger current frequency-bearing answer. This implicates tool
context and role aggregation rather than the model transport layer.

### `single_agent_tools`

- Wrong rows: 30/50.
- Regressions versus `single_self_consistency_temperature`: 12.
- Rescues versus `single_self_consistency_temperature`: 0.
- Regressions versus `single_greedy`: 14.
- Rescues versus `single_greedy`: 0.

Dominant wrong-row families:

| Family | Wrong rows |
| --- | ---: |
| competing_semiologies | 14 |
| seizure_free_duration | 13 |
| current_vs_historical | 13 |
| rate_bucket_or_denominator | 12 |
| uncertainty_or_ambiguity | 12 |
| unknown_boundary | 9 |
| benchmark_format_convention | 8 |
| cluster_burden | 6 |

Common transitions:

| Gold kind -> predicted kind | Count |
| --- | ---: |
| frequency -> frequency | 12 |
| unknown -> seizure_free | 6 |
| unresolved_multiple -> seizure_free | 3 |
| unknown -> frequency | 3 |
| frequency -> unknown | 2 |
| seizure_free -> unknown | 2 |
| frequency -> seizure_free | 2 |

Interpretation: tool context is not merely failing to help; it is steering the
single agent away from the stronger full-note direct-label behavior. It often
promotes seizure-free or low-frequency interpretations in rows where the
non-tool baselines retain the correct high-burden or boundary answer. Because
`single_agent_tools` currently records a four-call budget while using one
prediction-bearing call, the next live tool experiment must separate "tool
context hurts" from "tool condition underuses its model-call budget."

### `multi_agent_matched`

- Wrong rows: 28/50.
- Regressions versus `single_self_consistency_temperature`: 10.
- Rescues versus `single_self_consistency_temperature`: 0.
- Regressions versus `single_greedy`: 12.
- Rescues versus `single_greedy`: 0.
- Role-disagreement rows: 15/50.

Dominant wrong-row families:

| Family | Wrong rows |
| --- | ---: |
| seizure_free_duration | 13 |
| uncertainty_or_ambiguity | 12 |
| current_vs_historical | 12 |
| competing_semiologies | 11 |
| rate_bucket_or_denominator | 10 |
| unknown_boundary | 9 |
| benchmark_format_convention | 8 |
| cluster_burden | 6 |

Role call-level wrong counts:

| Role | Wrong calls |
| --- | ---: |
| coordinator_agent | 29 |
| extractor_agent | 28 |
| boundary_agent | 27 |
| adjudicator_agent | 27 |

Interpretation: the current multi-agent design mostly creates parallel final
labelers, not complementary specialists. The coordinator is not a reliable
rescue layer and is slightly worse at call level than the specialist roles. Role
disagreement exists in 15/50 rows, so E5 should ask whether disagreement can be
used for selective fallback before paying for redesigned live calls.

## Experiment Sequence

### E5 - No-Call Selective Fallback Replay

Hypothesis: existing hard50 traces contain useful disagreement signal, but the
safe policy should abstain or fall back to the stronger single-agent comparator
rather than trust current tool or coordinator labels directly.

Minimal change:

- Replay the existing hard50 JSONL without model calls.
- Treat `single_self_consistency_temperature` as the default fallback comparator.
- Evaluate candidate selective policies over existing condition traces only.
- Preserve raw model labels, parser-repaired decision labels,
  normalized-vote labels, call roles, answer kinds, confidence, guide IDs, parser
  candidate kinds, and repair-event counts.

Candidate policies:

| Policy | Description | Promotion eligibility |
| --- | --- | --- |
| `all_agree_tool_accept` | Accept `single_agent_tools` only when all available tool-context calls or vote inputs agree, otherwise fallback. | Eligible only if based on trace agreement, not hidden-family tags. |
| `all_agree_multi_accept` | Accept `multi_agent_matched` only when all four roles converge on the same normalized vote label. | Eligible. |
| `boundary_coordinator_agree` | Accept multi-agent only when boundary and coordinator agree and the label kind does not introduce a seizure-free answer over a frequency-bearing comparator. | Eligible if kind checks are inference-time features. |
| `no_seizure_free_introduction` | Reject candidate labels that introduce `seizure_free` when the fallback comparator predicts a frequency, unresolved-multiple, or unknown label. | Eligible as a conservative guard. |
| `raw_repair_disagreement_fallback` | Fallback when raw model final label, decision-record label, and normalized vote label imply different semantic kinds. | Eligible as an attribution/repair guard. |
| `manifest_family_oracle` | Use hidden-family tags to simulate family-specific abstention on seizure-free duration, competing semiologies, or cluster burden. | Diagnostic only; not promotable as an inference policy. |

Surface and row policy:

- Existing hard50 JSONL only.
- Fixed validation hard50 manifest only.
- No model calls.
- No prompt edits.
- No scorer edits.
- Hidden-family manifest tags may be used for analysis slices and oracle upper
  bounds, but not for a promotable policy.

Metrics:

- Purist and Pragmatic final accuracy for fallback comparator and each policy.
- Changed-label count.
- Wrong-to-correct and correct-to-wrong changes versus
  `single_self_consistency_temperature`.
- Net Purist gain.
- Changed-label precision: `wrong_to_correct / changed_labels`.
- Fallback/abstention rate.
- Policy action counts by answer kind transition.
- Slice summaries by manifest family, explicitly marked validation-only.
- Rows changed by semantic repair or kind-changing normalized vote.

Gate:

- A promotable selective policy must have `wrong_to_correct > correct_to_wrong`
  and at least 3 net Purist gains versus `single_self_consistency_temperature`.
- It must not depend on gold labels, hard-slice hidden families, source row IDs,
  or any feature unavailable at inference time.
- It must report correct-to-wrong regressions explicitly; more than 2 Purist
  regressions blocks promotion even if net gain is positive.
- If only the diagnostic oracle passes, record that the traces contain signal
  but the current runtime features do not expose a safe policy.

Expected artifacts:

```text
experiments/gan2026_agentic_hard50_selective_fallback_replay_2026-06-12.jsonl
experiments/gan2026_agentic_hard50_selective_fallback_replay_2026-06-12.md
```

Interpretation outcomes:

- Promote: implement the selected fallback as a conservative no-call policy and
  rerun hard50 with the same frozen trace inputs.
- Revise: keep E5 as diagnostic and run E1 to isolate the harmful tool context.
- Reject: if no policy yields positive changed-label precision, do not invest in
  current multi-agent orchestration until E1/E3/E4 redesigns exist.

### E1 - Tool Context Ablation

Hypothesis: generic parser/guide context, not agenticity itself, causes the
hard50 regressions.

Minimal change:

- Add one-call direct-label variants with:
  - no tool context;
  - parser candidates only;
  - boundary guide only;
  - parser plus boundary guide.
- Keep model, prompt shell, scoring, output schema, and deterministic
  normalized-label repair fixed.

Surface and row policy:

- Fixed validation hard50 manifest:
  `experiments/gan2026_agentic_validation_hard50_manifest_2026-06-12.json`.
- Same model family and scorer as current hard50 unless a separate model-swap
  experiment is explicitly predeclared.
- No full-validation escalation.

Metrics:

- Purist and Pragmatic condition-final accuracy.
- Regressions and rescues versus `single_greedy`.
- Regressions and rescues versus `single_self_consistency_temperature`.
- Wrong-row family counts from the fixed hard50 manifest.
- Parser candidate count and guide count per row.
- Semantic kind transitions, especially into `seizure_free` and `unknown`.

Gate:

- If parser-plus-guide is worse than no-tool and parser-only or guide-only
  isolates the harm, revise that tool path only.
- If every tool-context variant underperforms no-tool on hard50, reject dynamic
  tool context for the current paper-facing agentic comparison.
- If one context is neutral or positive, use only that context in E2/E3.

Expected artifacts:

```text
experiments/gan2026_agentic_hard50_tool_context_ablation_2026-06-12.jsonl
experiments/gan2026_agentic_hard50_tool_context_ablation_2026-06-12.md
```

### E2 - Four-Call Tool Self-Consistency

Hypothesis: `single_agent_tools` underperformed partly because it used one live
prediction-bearing call despite declaring the shared four-call budget.

Minimal change:

- Add `single_agent_tools_self_consistency`: four independent tool-context calls
  with deterministic parser-repaired label voting.
- Use the best non-harmful tool context from E1, not all tool context by default.
- Preserve raw labels, parser-repaired vote input labels, vote counts,
  repair-event counts, and call-level comparisons.

Surface and row policy:

- Run only if E1 shows at least one tool-context variant is not worse than
  no-tool.
- Fixed validation hard50 only.

Metrics:

- Purist and Pragmatic condition-final accuracy.
- Wins/losses versus `single_self_consistency_temperature`.
- Vote entropy and tie frequency.
- Raw-to-repaired semantic-kind transitions.
- Tool-call usefulness and failure counts.

Gate:

- Promote to E3 or a larger hard-slice only if it has at least 5 Purist rescues
  versus `single_self_consistency_temperature` and at most 2 Purist regressions.
- Otherwise reject the current tool-agent branch rather than spending a
  validation250/full-validation run.

Expected artifacts:

```text
experiments/gan2026_agentic_hard50_tool_self_consistency_2026-06-12.jsonl
experiments/gan2026_agentic_hard50_tool_self_consistency_2026-06-12.md
```

### E3 - Boundary-Safe Tool Prompt

Hypothesis: tool variants need an explicit anti-overwrite policy for
seizure-free, unknown/no-reference, cluster burden, and competing-semiology rows.

Minimal change:

- Add a prompt variant that requires:
  - prefer the highest current frequency-bearing evidence over remote
    seizure-free statements;
  - do not output seizure-free if any current seizure/event frequency remains;
  - preserve cluster burden when the gold-compatible answer contains both
    cluster cadence and events per cluster;
  - select the highest current active semiology unless the note explicitly says
    it is historical, negated, or not current;
  - use unknown rather than no-reference when seizure-frequency evidence exists
    but cannot be converted.

Surface and row policy:

- First run a validation micro-panel of the hard50 regression rows where a
  non-tool baseline was correct and tool or multi-agent regressed.
- Then rerun fixed hard50 only if the micro-panel has no obvious
  over-correction.
- Do not use locked-test rows.

Metrics:

- Micro-panel Purist and Pragmatic accuracy.
- New over-corrections relative to `single_greedy`.
- Semantic-kind transitions into and out of `seizure_free`, `unknown`, and
  frequency.
- Evidence exact-substring rate.

Gate:

- On the regression panel: at least 8/12 Purist correct and no more than 1 new
  over-correction relative to `single_greedy`.
- On hard50: beat `single_self_consistency_temperature` or show a high-precision
  selective-action profile.
- Otherwise revise or reject; do not escalate to validation250.

Expected artifacts:

```text
experiments/gan2026_agentic_boundary_safe_tool_prompt_panel_2026-06-12.jsonl
experiments/gan2026_agentic_boundary_safe_tool_prompt_panel_2026-06-12.md
experiments/gan2026_agentic_boundary_safe_tool_prompt_hard50_2026-06-12.jsonl
experiments/gan2026_agentic_boundary_safe_tool_prompt_hard50_2026-06-12.md
```

### E4 - Multi-Agent Role Redesign

Hypothesis: multi-agent roles need different intermediate tasks, not four final
labelers.

Minimal change:

- Replace final-label specialist roles with structured intermediate roles:
  - `frequency_hunter`: lists all current frequency-bearing facts and active
    semiologies;
  - `boundary_skeptic`: lists seizure-free, unknown, and no-reference hazards
    and whether they should block a frequency answer;
  - `cluster_semiology_auditor`: checks cluster cadence, events per cluster, and
    highest-burden semiology;
  - `coordinator`: emits one final label only after citing which role evidence
    it used and why lower-burden or seizure-free alternatives were rejected.
- Intermediate roles must not emit final labels unless their role contract
  requires a bounded candidate list.

Surface and row policy:

- Start with the same validation regression panel from E3.
- Rerun hard50 only if the panel passes.
- No full validation without the hard50 gate below.

Metrics:

- Coordinator Purist and Pragmatic accuracy.
- Intermediate evidence coverage: frequency facts, boundary hazards,
  cluster/semiology findings.
- Role disagreement reason counts.
- Wrong-to-correct and correct-to-wrong transitions versus
  `single_self_consistency_temperature`.
- Rows where coordinator cited a role but selected an unsupported final label.

Gate:

- Coordinator must be better than or equal to `single_greedy` on the regression
  panel before any hard50 run.
- On hard50, require at least 5 Purist wins versus self-consistency and at most
  2 losses.
- No full validation without meeting that gate.

Expected artifacts:

```text
experiments/gan2026_agentic_multi_agent_role_redesign_panel_2026-06-12.jsonl
experiments/gan2026_agentic_multi_agent_role_redesign_panel_2026-06-12.md
experiments/gan2026_agentic_multi_agent_role_redesign_hard50_2026-06-12.jsonl
experiments/gan2026_agentic_multi_agent_role_redesign_hard50_2026-06-12.md
```

## Attribution And Ablation Requirements

Every live LLM-backed artifact in this sequence must report:

- Raw model-selected final label.
- Decision-record final label after parser/schema repair.
- Normalized vote input label.
- Normalized vote selected label.
- Repair-event counts.
- Semantic-kind transitions introduced by repair or voting.
- Rows changed by repair.
- Raw-wrong to final-correct and raw-correct to final-wrong transitions.
- Whether parser candidates, boundary guides, or role outputs introduced the
  selected clinical fact.

Do not describe any successful tool or multi-agent result as `llm_only`.
Current and planned agentic variants are raw-model or hybrid artifacts whenever
deterministic tools, deterministic voting, or format repair affect the final
scorer-facing label.

## Artifact Metadata Contract

Each saved run or replay report must include:

- Date and git commit or working-tree note.
- Code/prompt change summary.
- Data path, split name, split manifest version, and row count.
- Hard50 manifest path and row-selection policy.
- Model identifier, provider/API identifier, temperature, max tokens, cache
  policy, and call failure count for live runs.
- Replay source JSONL path for no-call runs.
- Conditions enabled and matched-budget table.
- Scorer and mapping policy.
- Purist metrics first; Pragmatic metrics as side-car.
- Changed-label precision for selective policies.
- Parse, schema, evidence, and repair issue counts.
- Rule categories or tool categories enabled.
- DSPy/LLM stages enabled or disabled.
- Top failure slices and interpretation.
- Decision status: promote, revise, reject, or diagnostic.

If a run affects project direction, add or update an entry in
`experiments/registry.jsonl` and regenerate `experiments/RUN_INDEX.md`.

## Stop Rules

- Stop the current tool-agent branch if E1 shows every tool-context variant is
  worse than no-tool on hard50.
- Stop the current multi-agent branch if E5 finds no positive selective policy
  and E4 cannot beat `single_greedy` on the regression panel.
- Stop any live branch before validation250 unless hard50 shows high-precision
  rescues with bounded regressions.
- Do not inspect test-set row-level failures during any of these experiments.
- Do not tune scorer, label mapping, split membership, prompt wording, tool
  guides, or fallback thresholds from locked-test results.

## Claim Boundary

These are validation development experiments. They can justify revise/reject
decisions, hard-slice gates, selective-action diagnostics, and prompt/tool
redesign. They cannot support benchmark, holdout, or generalization claims.

Paper-facing language should be limited to:

```text
On a predeclared validation hard50 slice, the first matched-budget tool-using
and multi-agent variants underperformed direct single-agent baselines. Follow-up
validation-only analyses test whether existing trace disagreement can support a
conservative fallback policy and whether tool context or role design caused the
regressions.
```
