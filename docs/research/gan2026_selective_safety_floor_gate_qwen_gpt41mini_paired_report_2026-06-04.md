# Gan 2026 Selective Safety-Floor Gate Paired Model Report

Date: 2026-06-04

## Executive Finding

The paired validation ladder completed for `openai/gpt-4.1-mini` and local
`ollama_chat/qwen3.6:35b` on validation prefixes 1, 25, 50, and 250. The
selective safety-floor replay itself runs cleanly over both model families, and
the stable, valid changed rows are the same across GPT and Qwen at
validation250.

However, Qwen should not be promoted as a safe local replacement for this gate
yet. On validation250 the Qwen upstream source artifact has 6 blocking
parse/schema failures, 3 missing adjudicator records, 3 invalid selected
evidence/source-id rows, and 3 deterministic-correct regressions in the
upstream hybrid reasoner. The replay then appears to gain 3 rows over its own
Qwen baseline, but 2 of those extra gains are artifacts of missing Qwen
adjudicator labels and lack exact evidence/source-id validity. Under the
predeclared stop rules, this is a reject/revise result for the Qwen arm.

## Scope

Artifacts analyzed:

- `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation*_gpt-41-mini_paired_gate_v0_live_2026-06-03.jsonl`
- `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation*_qwen36_35b_paired_gate_v0_live_2026-06-03.jsonl`
- `experiments/gan2026_selective_safety_floor_gate_v0_validation*_gpt-41-mini_paired_replay_live_2026-06-03.json`
- `experiments/gan2026_selective_safety_floor_gate_v0_validation*_qwen36_35b_paired_replay_live_2026-06-03.json`

All runs used the same validation split order, prompt/program version
`gan2026_hybrid_parallel_state_candidate_reasoner_v0`, temperature `0.0`, max
tokens `1800`, and the frozen selective-gate validation manifest. This remains
a validation development analysis, not a holdout or production-policy claim.

## Selective Gate Replay Results

| Limit | Model | Baseline Purist | Selective Purist | Delta | Changed | Wrong to Correct | Correct to Wrong | Deterministic Regressions | Precision | Exact Evidence Changed | Valid Source IDs Changed | Fallback |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | GPT-4.1-mini | 1 | 1 | 0 | 0 | 0 | 0 | 0 |  | 0 | 0 | 1 |
| 1 | Qwen 3.6 35B | 1 | 1 | 0 | 0 | 0 | 0 | 0 |  | 0 | 0 | 1 |
| 25 | GPT-4.1-mini | 25 | 25 | 0 | 0 | 0 | 0 | 0 |  | 0 | 0 | 25 |
| 25 | Qwen 3.6 35B | 25 | 25 | 0 | 0 | 0 | 0 | 0 |  | 0 | 0 | 25 |
| 50 | GPT-4.1-mini | 50 | 50 | 0 | 0 | 0 | 0 | 0 |  | 0 | 0 | 50 |
| 50 | Qwen 3.6 35B | 50 | 50 | 0 | 0 | 0 | 0 | 0 |  | 0 | 0 | 50 |
| 250 | GPT-4.1-mini | 246 | 247 | +1 | 4 | 1 | 0 | 0 | 1.0000 | 4 | 4 | 246 |
| 250 | Qwen 3.6 35B | 243 | 246 | +3 | 6 | 3 | 0 | 0 | 1.0000 | 4 | 4 | 244 |

The raw selective-gate table makes Qwen look attractive at first glance:
`+3` Purist correction versus `+1` for GPT on validation250. That is not a
valid promotion signal, because Qwen's lower baseline is itself caused by
upstream structured-output failure.

## Upstream Model Artifact Quality

| Limit | Model | Structured LLM Candidates | Structured Adjudicator | Blocking Parse/Schema | Evidence Exact | Source IDs Valid | Upstream Deterministic Regressions | Run Outcome |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | GPT-4.1-mini | 1 | 1 | 0 | 1 | 1 | 0 | revise |
| 1 | Qwen 3.6 35B | 1 | 1 | 0 | 1 | 1 | 0 | revise |
| 25 | GPT-4.1-mini | 25 | 25 | 0 | 25 | 25 | 0 | promote_to_50 |
| 25 | Qwen 3.6 35B | 24 | 25 | 1 | 25 | 25 | 0 | promote_to_50 |
| 50 | GPT-4.1-mini | 49 | 50 | 1 | 50 | 50 | 0 | validation50_signal_result |
| 50 | Qwen 3.6 35B | 49 | 50 | 1 | 50 | 50 | 0 | validation50_signal_result |
| 250 | GPT-4.1-mini | 247 | 250 | 3 | 249 | 250 | 0 | validation250_development_result |
| 250 | Qwen 3.6 35B | 247 | 247 | 6 | 247 | 247 | 3 | reject |

This is the decisive comparison. Qwen remains close through validation50, but
the validation250 arm exposes structured-output fragility in the adjudicator
path. The three failed adjudications are all deterministic-correct rows, so the
upstream hybrid artifact fails the safety-floor contract before the selective
gate is even interpreted.

## Validation250 Row-Level Audit

At validation250, the paired replay contains 250 shared source rows. The
selective-gate final labels differ on only 3 rows:

| Row | Gold | GPT Selective Behavior | Qwen Selective Behavior | Interpretation |
| ---: | --- | --- | --- | --- |
| 1880 | `8 per 2 month` | Baseline/adjudicator already correct; no selective change | Qwen adjudicator label missing; projection changes to gold but lacks exact evidence/source-id validity | Qwen-only apparent rescue caused by source-artifact failure |
| 1979 | `6 per 2 month` | Baseline/adjudicator already correct; no selective change | Qwen adjudicator label missing; projection changes to gold but lacks exact evidence/source-id validity | Qwen-only apparent rescue caused by source-artifact failure |
| 2965 | `seizure free for 16 month` | Baseline/adjudicator correct; gate abstains under regression guard | Qwen adjudicator label missing; selective output remains `None` | Real Qwen upstream regression, not a gate gain |

Changed-row set comparison at validation250:

| Variant | GPT Changed Rows | Qwen Changed Rows | Shared | Qwen-only |
| --- | --- | --- | --- | --- |
| Projection boundary-state priority | 2907, 2932, 2938 | 1880, 1979, 2907, 2932, 2938 | 2907, 2932, 2938 | 1880, 1979 |
| LLM candidate sidecar rescue | 3356 | 3356 | 3356 |  |
| Selective safety-floor gate | 2907, 2932, 2938, 3356 | 1880, 1979, 2907, 2932, 2938, 3356 | 2907, 2932, 2938, 3356 | 1880, 1979 |

The shared changed rows are stable:

- Rows 2907, 2932, and 2938 are projection changes from exact
  seizure-free-duration labels to `seizure free for multiple year`. These are
  scorer-correct but do not create non-equivalent wrong-to-correct gains.
- Row 3356 is the substantive LLM sidecar rescue in both models:
  baseline `seizure free for multiple year`, gold `unknown`, selective output
  `unknown`, exact evidence true, source ids valid.

The Qwen-only changed rows are not trustworthy because the baseline is missing
and the changed rows lack the required provenance checks.

## Hidden-Family Interpretation

For GPT validation250, the selective gate makes 4 changed rows:

- 1 seizure-free-duration correction
- 1 uncertainty/ambiguity correction
- 1 unknown-boundary correction
- 3 unclassified projection-only scorer-equivalent changes

For Qwen validation250, the selective gate makes 6 changed rows:

- the same 4 stable changed rows as GPT
- 2 additional unclassified projection changes caused by missing adjudicator
  labels on rows 1880 and 1979

Qwen reports `changed_label_precision = 1.0000`, but that precision is
calculated over non-equivalent changed-label outcomes and does not forgive the
failed evidence/source-id precondition. The stricter safety reading is:
Qwen has 6 changed rows but only 4 with exact evidence and valid source ids.

## What This Says About the Gate

The replay script is doing useful work with local Qwen artifacts: it exposes
where the model-dependent source artifact violates the gate's assumptions.
The gate is not simply overfitting to GPT, because the valid common changes are
stable across both models.

But the current experiment also shows a weakness in the operational contract:
when the source artifact has a missing adjudicator label, the replay can report
a projection change from `None` to a correct deterministic/graph label. That is
useful diagnostically, but it must not be interpreted as a model-side clinical
rescue. The predeclared evidence/source-id stop rule catches this at reporting
time, but the gate would be cleaner if the changed-row precondition were
hardened before counting such rows as selective-gate changes.

## Decision

Decision for `ollama_chat/qwen3.6:35b`: reject for promotion under the current
paired validation250 result; revise before any full validation750 or locked-test
use.

Rationale:

- Qwen fails the upstream hybrid run gate at validation250.
- It has 3 deterministic-correct regressions in the upstream artifact.
- It has 6 blocking parse/schema failures versus 3 for GPT.
- Its 2 extra selective-gate gains are artifacts of missing adjudicator output
  and fail exact-evidence/source-id accounting.
- The one substantive LLM sidecar rescue row is shared with GPT, so Qwen does
  not yet demonstrate a distinct safe local advantage.

Decision for the selective replay method: keep as a diagnostic model-comparison
tool. It successfully separates stable gate behavior from source-artifact
quality failures.

## Recommendations

1. Harden the selective replay's changed-row eligibility so projection changes
   from an unscorable or missing baseline are reported as source-artifact
   recovery diagnostics, not selective-gate rescues.

2. Add a pre-replay source-artifact quality gate:
   require zero deterministic-correct regressions, valid source ids, exact
   selected evidence, and no missing adjudicator labels before interpreting
   selective-gate deltas as model-comparable.

3. Run a Qwen repair experiment before scaling:
   focus on rows 1880, 1979, and 2965; the likely failure mode is schema
   completion/missing `final_label`, not clinical reasoning.

4. Preserve the GPT validation250 result as the current reference:
   baseline 246/250, selective 247/250, 4 changed rows, 1 wrong-to-correct,
   0 correct-to-wrong, 0 deterministic regressions, all changed rows with exact
   evidence and valid source ids.

5. Do not run validation750 or locked-test Qwen until the validation250 source
   artifact passes the upstream safety gate.

## Bottom Line

Local Qwen can run the pipeline and matches GPT on the stable, valid selective
gate changes. It is not yet reliable enough as a source-artifact generator for
this gate. The result is promising for portability but negative for promotion:
Qwen needs schema/adjudicator hardening before this safety-floor gate can be
meaningfully compared at larger scale.
