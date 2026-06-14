# Gan 2026 Agentic Hard50 Redesign After E2 Stop

Date: 2026-06-12

Status: complete validation-cycle redesign artifact.

## Scope

This design responds to the completed fixed validation hard50 follow-up:

```text
E5 -> E1 -> E2, then stop before E3/E4
```

It supersedes only the unrun E3/E4 live designs in
`experiments/gan2026_agentic_hard50_error_analysis_experiment_design_2026-06-12.md`.
It does not change the scorer, split manifest, hard50 row list, prior run
metrics, or holdout policy.

The immediate question is now narrower:

```text
Can the boundary-guide signal be converted into high-precision, rescue-only
action without parser candidates, broad context stuffing, or multi-agent roles
that act as parallel final-labelers?
```

## Protocol Position

- Work class: validation hard-slice redesign after a failed promotion gate.
- Split: `gan2026_split_v1` validation only.
- Primary surface: fixed validation hard50 manifest,
  `experiments/gan2026_agentic_validation_hard50_manifest_2026-06-12.json`.
- Scorer: existing Gan-compatible Purist first, Pragmatic side-car.
- Saturation context: validation25 is no longer discriminative for agentic
  variants; hard-slice, replay, and targeted panels remain the useful surfaces.
- Holdout policy: no locked-test row inspection, no scorer change, and no
  holdout-facing claim.

## Evidence From E5/E1/E2

| Artifact | Finding | Design implication |
| --- | --- | --- |
| E5 selective fallback replay | No promotable saved-trace policy; eligible policies made `0` wrong-to-correct changes. | Existing `single_agent_tools` and `multi_agent_matched` traces are not enough. Do not rescue the old branch by post-hoc fallback. |
| E1 tool-context ablation | `direct_boundary_guide_only` reached `34/50` Purist with `5` wins and `1` loss versus no-tool; parser-only reached `21/50`; parser-plus-guide reached `19/50`. | Boundary guides are the only currently non-harmful tool context. Parser candidates must be excluded from new prediction-bearing prompts. |
| E2 boundary-guide self-consistency | `34/50` Purist, `35/50` Pragmatic, `4` wins and `2` losses versus `single_self_consistency_temperature`; gate required at least `5` wins and at most `2` losses. | Four calls plus boundary guides contain signal, but not enough for promotion. The next branch must be rescue-only and explicitly block boundary demotions. |

Concrete row pattern from validation hard50:

| Source | Wins | Losses |
| --- | --- | --- |
| E1 boundary-guide-only vs no-tool | `7615`, `10677`, `10996`, `15193`, `15834` | `6131` |
| E2 boundary-guide self-consistency vs reference | `6368`, `7615`, `10677`, `10996` | `5534`, `6131` |

The E2 wins are mostly cluster, high-burden, benchmark-format, and
current-versus-historical rescues. The losses are seizure-free or boundary
demotions where the safer answer should have remained the comparator.

## Redesign Principles

1. Parser candidates are prohibited from prediction-bearing prompts in this
   branch. They may appear only in no-call diagnostics or later attribution
   audits.
2. The default action is fallback to the direct or self-consistency comparator.
   New designs must earn every changed label.
3. Boundary guides should answer narrow clinical boundary questions, not dump
   many rules into the prompt.
4. The first rescue branch may only promote frequency-bearing, cluster-burden,
   or higher-current-burden answers. It may not introduce seizure-free,
   unknown, or no-reference labels over a frequency-bearing comparator.
5. Multi-agent roles, if reopened, must produce typed intermediate evidence.
   They must not be four independent final-labelers plus a coordinator.
6. No validation250 or full-validation escalation is allowed until hard50 shows
   high-precision rescues with bounded regressions.

## New Experiment Sequence

### D0 - Boundary-Guide Rescue Gate Replay

Hypothesis: the saved E1/E2 boundary-guide traces contain a narrower
rescue-only policy that was hidden by the broad E2 voting gate.

Minimal change:

- Replay saved E1 and E2 JSONL artifacts without model calls.
- Use `single_self_consistency_temperature` as the default fallback comparator
  for E2-derived policies.
- Use `direct_no_tool_context` as the default fallback comparator for E1-derived
  policies.
- Evaluate only inference-available features: final labels, normalized label
  kinds, vote counts, vote entropy, repair notes, raw decision labels, and
  whether the candidate introduces a boundary label.

Candidate policies:

| Policy | Description | Promotion eligibility |
| --- | --- | --- |
| `unanimous_frequency_or_cluster_override` | Accept E2 boundary-guide self-consistency only when all four votes normalize to the same frequency-bearing or cluster label. | Eligible. |
| `guide_and_vote_agree_override` | Accept only when E1 boundary-guide-only and E2 voted final agree after normalization and the agreed label is not seizure-free, unknown, or no-reference. | Eligible. |
| `cluster_restore_only` | Accept a boundary-guide label only when it contains explicit cluster burden and the fallback lacks cluster burden. | Eligible as a narrow hybrid rule. |
| `higher_burden_only` | Accept only frequency-bearing candidates that are strictly higher burden than a frequency-bearing fallback. | Eligible only if burden comparison uses existing label parser semantics and reports category changes. |
| `boundary_demotion_block` | Always fallback when the boundary-guide candidate introduces seizure-free, unknown, or no-reference over a frequency-bearing or cluster fallback. | Eligible as a conservative guard. |

Metrics:

- Purist and Pragmatic accuracy.
- Changed-label count.
- Wrong-to-correct and correct-to-wrong transitions.
- Changed-label precision.
- Fallback rate.
- Action counts by semantic kind transition.
- Diagnostic hidden-family summaries, clearly marked non-runtime.

Gate:

- Promote a no-call policy only if it has at least `3` net Purist gains versus
  its fallback, changed-label precision at or above `0.60`, and no more than `1`
  Purist regression.
- Any policy that uses hidden families, row IDs, gold labels, or source-order
  facts is diagnostic only.
- If no policy passes, D0 remains diagnostic and the branch moves to D1.

Expected artifacts:

```text
experiments/gan2026_agentic_hard50_boundary_guide_rescue_replay_2026-06-12.jsonl
experiments/gan2026_agentic_hard50_boundary_guide_rescue_replay_2026-06-12.md
```

Completed D0 result:

- Artifact:
  `experiments/gan2026_agentic_hard50_boundary_guide_rescue_replay_2026-06-12.md`.
- Mode: no-call replay over saved E1/E2 validation hard50 traces.
- Promoted policy: `higher_burden_only`.
- Summary: `35/50` Purist, `36/50` Pragmatic, `4` changed labels,
  `3` wrong-to-correct, `0` correct-to-wrong, net `+3`, changed-label
  precision `0.750`.
- Gate: passed the D0 no-call promotion gate. This is a validation-development
  rescue-policy signal only; it makes no holdout, benchmark, or broader
  validation claim.
- Notable diagnostic side result: `cluster_restore_only` made `2` changes, both
  wrong-to-correct, but missed the D0 net-gain gate.

### D1 - Boundary Audit Prompt V2

Hypothesis: the model needs a compact boundary audit scaffold, not parser
candidates or a larger prompt.

Minimal change:

- Add a one-call prompt variant with boundary-guide-only context.
- Require the model to emit a structured audit before the final label:
  - current frequency-bearing evidence;
  - active semiologies and relative burden;
  - cluster cadence and events-per-cluster burden;
  - seizure-free, unknown, and no-reference hazards;
  - rejected lower-burden or historical alternatives;
  - final label and supporting evidence.
- Keep model, scorer, repair, and output schema otherwise fixed.
- Do not mention validation row IDs, gold labels, or hard50 family tags in the
  prompt.

Surface and row policy:

- First run a validation micro-panel built from the already-reviewed hard50
  signal:
  `6368`, `7615`, `10677`, `10996`, `5534`, `6131`, `15193`, `15834`,
  `3356`, `4690`, `9955`, `12422`.
- The panel contains E2 rescues, E2 regressions, extra E1 rescues, and parser
  harm sentinels.
- Row IDs are for evaluation only; prompt text must remain row-agnostic.
- Rerun fixed hard50 only if the panel passes.

Metrics:

- Purist and Pragmatic accuracy.
- Wins and losses versus `single_self_consistency_temperature`.
- Boundary demotion count.
- Cluster-burden preservation count.
- Evidence exact-substring rate where the artifact supports it.
- Output-contract failures and schema/label repair counts.

Gate:

- On the micro-panel: at least `9/12` Purist correct, all E2 loss sentinels
  must avoid boundary demotion, and no parser-context dependency.
- On hard50: at least `5` wins and at most `1` loss versus
  `single_self_consistency_temperature`, or changed-label precision at or above
  `0.70` with no more than `1` regression.
- If the prompt improves only by broad over-instruction, mark it diagnostic and
  do not escalate.

Expected artifacts:

```text
experiments/gan2026_agentic_boundary_audit_prompt_v2_panel_2026-06-12.jsonl
experiments/gan2026_agentic_boundary_audit_prompt_v2_panel_2026-06-12.md
experiments/gan2026_agentic_boundary_audit_prompt_v2_hard50_2026-06-12.jsonl
experiments/gan2026_agentic_boundary_audit_prompt_v2_hard50_2026-06-12.md
```

Completed D1 result:

- Panel artifact:
  `experiments/gan2026_agentic_boundary_audit_prompt_v2_panel_2026-06-12.md`.
- Panel result after format-only audit-field repair: `10/12` Purist,
  `10/12` Pragmatic, `0` parse/schema/label failures, `0` E2 loss-sentinel
  regressions. Gate passed, authorizing the fixed hard50 run.
- Hard50 artifact:
  `experiments/gan2026_agentic_boundary_audit_prompt_v2_hard50_2026-06-12.md`.
- Hard50 result: `38/50` Purist, `38/50` Pragmatic, `8` wins and `2` losses
  versus `single_self_consistency_temperature`, `22` changed labels, changed-label
  precision `0.3636`, `0` parse/schema/label failures.
- Gate: rejected/revise after hard50. The run exceeded the rescue-count target
  but violated the max-loss gate (`2` losses; gate allowed at most `1`) and had
  low changed-label precision. Do not escalate D1 to validation250 or D3.

### D2 - Direct Plus Boundary Critic Rescue-Only

Hypothesis: boundary reasoning is useful as a critic over a direct answer, not
as a replacement labeler.

Minimal change:

- Call 1: direct no-tool final-label prediction.
- Call 2: boundary critic sees the note, direct answer, and compact boundary
  guide. It emits one action:
  - `keep`;
  - `restore_cluster_burden`;
  - `raise_current_burden`;
  - `block_boundary_demotion`;
  - `abstain`.
- Deterministic action policy:
  - accept `restore_cluster_burden` only when the critic cites cluster cadence
    and events-per-cluster evidence;
  - accept `raise_current_burden` only when the critic cites a current
    higher-burden frequency-bearing event;
  - never accept a critic override that introduces seizure-free, unknown, or
    no-reference in v1;
  - fallback to the direct answer for `keep`, `block_boundary_demotion`, and
    `abstain`.

Surface and row policy:

- Run the D1 micro-panel first.
- Run fixed hard50 only if panel output has no systemic schema, evidence, or
  over-correction failure.
- No validation250 escalation from D2 unless hard50 passes.

Metrics:

- Direct answer accuracy.
- Critic raw proposed-label accuracy.
- Conservative gated-final accuracy.
- Changed-label precision for accepted critic actions.
- Action counts by `restore_cluster_burden`, `raise_current_burden`,
  `block_boundary_demotion`, and `abstain`.
- Correct-to-wrong regressions caused by accepted critic actions.

Gate:

- Panel gate: no accepted boundary demotion and at least `4` correct accepted
  rescue actions.
- Hard50 gate: at least `5` wins and at most `1` loss versus
  `single_self_consistency_temperature`, plus changed-label precision at or
  above `0.70`.
- If raw critic helps but gated critic does not, keep the raw critic artifact as
  diagnostic and revise the action policy before any larger run.

Expected artifacts:

```text
experiments/gan2026_agentic_direct_boundary_critic_rescue_panel_2026-06-12.jsonl
experiments/gan2026_agentic_direct_boundary_critic_rescue_panel_2026-06-12.md
experiments/gan2026_agentic_direct_boundary_critic_rescue_hard50_2026-06-12.jsonl
experiments/gan2026_agentic_direct_boundary_critic_rescue_hard50_2026-06-12.md
```

Completed D2 result:

- Live panel artifact:
  `experiments/gan2026_agentic_direct_boundary_critic_rescue_panel_2026-06-12.md`.
- Format-only saved-output replay artifact:
  `experiments/gan2026_agentic_direct_boundary_critic_rescue_panel_format_repair_replay_2026-06-12.md`.
- Mode: 12-row validation micro-panel, 24 live model calls, then no-call
  reparse of the same raw outputs after critic-field shape repair.
- Parser context: disabled in both calls. The critic saw only the note, direct
  answer, and fixed boundary-guide set.
- Clean replay result: direct answer `10/12` Purist, gated final `10/12`
  Purist and `10/12` Pragmatic, `0` parse/schema/label failures, `0`
  accepted rescues, `0` accepted regressions, `0` accepted boundary demotions,
  fallback on all `12/12` rows.
- Versus `single_self_consistency_temperature`: `2` wins, `0` losses, `5`
  changed labels, changed-label precision `0.400`.
- Gate: rejected/revise before hard50. D2 did not meet the panel requirement of
  at least `4` correct accepted rescue actions, so D2 hard50 is not authorized.
  This closes the D-series live branch unless a new redesign is explicitly
  proposed.

### D3 - Evidence-First Role Redesign

Hypothesis: multi-agent value, if any, should come from typed evidence coverage,
not from multiple final labels.

Minimal change:

- Replace final-label specialist roles with bounded evidence roles:
  - `frequency_fact_lister`: current frequency-bearing facts and active
    semiologies only;
  - `boundary_hazard_lister`: seizure-free, unknown, no-reference, negation,
    and historical hazards only;
  - `cluster_burden_lister`: cluster cadence, events per cluster, and whether
    cluster burden changes the final label;
  - `resolver`: one final label plus cited evidence role outputs.
- Evidence roles cannot emit final labels.
- Resolver must explicitly reject lower-burden and boundary alternatives when
  it changes the fallback answer.

Surface and row policy:

- Run only if D1 or D2 passes its hard50 gate.
- Compare against the best single-agent or two-call rescue-only condition under
  a matched budget, not against an already-rejected weak branch.
- Start on the D1 micro-panel, then fixed hard50.

Metrics:

- Resolver Purist and Pragmatic accuracy.
- Evidence-role coverage counts.
- Unsupported resolver selection count.
- Wins/losses versus both `single_self_consistency_temperature` and the best
  D1/D2 comparator.
- Cost and model-call budget per row.

Gate:

- Panel: at least equal to the best D1/D2 condition with no unsupported
  resolver selections.
- Hard50: at least `5` wins and at most `1` loss versus the matched single-agent
  comparator.
- If D3 improves over old `multi_agent_matched` but not over the matched
  D1/D2 comparator, it is diagnostic, not promoted.

Expected artifacts:

```text
experiments/gan2026_agentic_evidence_first_roles_panel_2026-06-12.jsonl
experiments/gan2026_agentic_evidence_first_roles_panel_2026-06-12.md
experiments/gan2026_agentic_evidence_first_roles_hard50_2026-06-12.jsonl
experiments/gan2026_agentic_evidence_first_roles_hard50_2026-06-12.md
```

Current status: blocked/not run. D1 failed hard50 and D2 failed the micro-panel,
so no D-series condition passed the prerequisite needed to reopen multi-agent
evidence-first roles.

### D4 - Split-Neutral Boundary Robustness Panel

Hypothesis: a design that passes hard50 should also show mechanism-level
robustness on split-neutral cases before validation250 escalation.

Minimal change:

- Create synthetic or source-near cases with predeclared labels and rationales.
- Cover:
  - current frequency versus remote seizure-free statements;
  - cluster cadence plus events-per-cluster burden;
  - multiple active semiologies with different burdens;
  - unknown frequency versus no seizure-frequency reference;
  - last-event-only statements;
  - negated or hypothetical seizure statements;
  - vague recurrence terms.
- Run the best D1/D2/D3 candidate and its matched comparator.

Metrics:

- Pairwise consistency across paraphrases.
- Purist correctness on synthetic expected labels.
- Boundary demotion rate.
- Cluster-burden preservation rate.
- Evidence containment where synthetic text supports exact spans.

Gate:

- Use D4 as a mechanism check, not benchmark evidence.
- A candidate with hard50 gains but poor D4 robustness is revise-only.
- A candidate passing hard50 and D4 may be proposed for a validation250
  development run with a separate written escalation reason.

Expected artifacts:

```text
experiments/gan2026_agentic_boundary_robustness_panel_2026-06-12.jsonl
experiments/gan2026_agentic_boundary_robustness_panel_2026-06-12.md
```

Current status: not reached. D4 is a mechanism check only after a candidate
passes hard50, and no D-series live condition passed its gate.

## Execution Order

```text
D0 -> D1 -> D2 -> D3 -> D4
```

D0, D1, and D2 are now complete. D0 `higher_burden_only` passed as
saved-output rescue evidence; D1 boundary-audit prompt v2 passed the panel but
failed the fixed hard50 gate because it had `2` regressions and low
changed-label precision. D2 direct-plus-boundary-critic failed its micro-panel:
after format-only saved-output replay it made `0` accepted rescues and fell
back on all `12/12` rows.

The D-series branch is closed with D0 as narrow saved-trace close-off evidence
and D1/D2 as rejected live-call branches. D2 hard50, D3, D4, validation250, and
holdout escalation are not authorized from this branch.

## Rejected Or Deferred Paths

- Parser-candidate prompt context is rejected for this branch because E1 showed
  strong harm on hard50.
- Broad parser-plus-guide context is rejected for this branch.
- The original E3 boundary-safe prompt and E4 multi-agent role redesign remain
  historical designs unless rewritten to satisfy this artifact's rescue-only
  and no-parser constraints.
- D2 hard50 is rejected/deferred because the D2 micro-panel failed its gate
  after format-only saved-output replay.
- D3 evidence-first roles are blocked because neither D1 nor D2 passed hard50.
- D4 split-neutral robustness is not reached because no D-series candidate
  passed hard50.
- Validation250 and full validation750 are deferred until a hard50 gate passes.
- Locked test450 remains unavailable for development or row-level analysis.

## Attribution And Reporting Requirements

Every D1-D4 live artifact must report:

- raw model final label;
- parser/schema-repaired decision label;
- normalized vote or gated-final label, when applicable;
- repair counts and semantic-kind transitions;
- raw-wrong to final-correct and raw-correct to final-wrong transitions;
- fallback, abstention, and accepted-action counts;
- whether a changed label was model-owned, guide-owned, deterministic-gate-owned,
  or mixed-provenance;
- parser context disabled status.

Do not describe any successful D-series artifact as `llm_only`. These are
hybrid or mixed-provenance development artifacts whenever deterministic repair,
voting, gating, or guide retrieval affects the final scorer-facing label.

## Stop Rules

- Stop the D-series branch if D0 and D1 both fail to produce any positive
  changed-label precision.
- Stop before D3 unless D1 or D2 passes hard50. In the current state, D1 failed
  hard50 and D2 failed before hard50, so D3 is closed unless a separate future
  redesign reopens it with a new predeclared gate.
- Stop before validation250 unless hard50 shows at least `5` wins with at most
  `1` loss versus the matched comparator or a changed-label precision profile at
  or above `0.70`.
- Stop any branch that reintroduces parser candidates into prediction-bearing
  prompts without a separate parser-context ablation.
- Do not tune prompts, tools, gates, or repair logic from locked-test results.

## Claim Boundary

This is a validation-development redesign artifact. It can authorize no-call
replay, validation micro-panel work, and fixed hard50 redesign experiments. It
cannot support benchmark, holdout, or generalization claims.

Paper-facing language should be limited to:

```text
After the first matched-budget tool and multi-agent variants regressed on a
predeclared validation hard50 slice, follow-up validation analyses showed parser
candidate context was harmful while boundary-guide-only context contained a
small rescue signal. A second validation-cycle design therefore reframed agentic
work as rescue-only boundary auditing with explicit fallback and attribution
gates, rather than broad tool context or parallel final-labeling agents.
```
