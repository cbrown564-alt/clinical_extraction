# Gan 2026 LLM-Reasoning Agentic Test-0.85 Experiment Plan

Date: 2026-06-13

Status: proposed next-session plan. This document does not authorize a new
`test450` run, inspect test row-level failures, or change scoring policy.

## Objective

Build and evaluate tool-calling single-agent and multi-agent Gan 2026 pipelines
that can plausibly exceed `0.85` Purist on the locked `test450` split while
relying primarily on LLM clinical reasoning over structured events, not on a
deterministic final-label floor.

The final frozen-test target is at least `383/450` Purist (`0.8511`). The current
aggregate reference points are:

- GPT `hybrid_structured_events` on `test450`: `364/450` Purist, `381/450`
  Pragmatic.
- Qwen `hybrid_structured_events` on `test450`: `337/450` Purist, `356/450`
  Pragmatic.
- Available GPT+Qwen consensus over a deterministic floor: `365/450` Purist,
  `375/450` Pragmatic.
- Deterministic floor from the rules-candidates artifact: `343/450` Purist.

The first durable target is therefore not "beat the deterministic floor." It is
to beat the best pure structured-event result by roughly 19 or more Purist rows
on a frozen final audit without tuning from test.

## Lessons From The Failed Direction

The validation consensus result was useful but not robust:

- Validation three-agent consensus: `708/750` Purist (`0.9440`).
- Closest available `test450` audit: `365/450` Purist (`0.8111`).
- The deterministic floor itself dropped from `697/750` validation Purist to
  `343/450` test Purist.

The interpretation is clear enough to guide the reset:

1. Do not use deterministic top as a prediction-bearing fallback.
2. Do not ask agents to rescue broad deterministic outputs.
3. Do keep the structured-event substrate: it is the strongest current
   architecture and exposes the right intermediate state.
4. Tools should check evidence, arithmetic, label syntax, and boundary-guide
   retrieval. They should not secretly choose the clinical interpretation.
5. Multi-agent value must be tested against matched-budget single-agent
   conditions.

## Durable Design Principles

1. **LLM-owned final clinical selection.** The prediction-bearing component must
   be an LLM reasoner or LLM coordinator selecting from structured events and
   raw evidence. Deterministic code may render a selected fact into Gan syntax,
   calculate frequency arithmetic, validate evidence substrings, and score.
2. **Structured events are the base representation.** The reasoner starts from
   `hybrid_structured_events` style event records, not from a direct final-label
   prompt and not from deterministic V1 candidates.
3. **Fallback, when needed, is LLM structured-events, not deterministic top.**
   Conservative verifier variants may keep the original structured-event final
   answer when they are uncertain, but they must not fall back to deterministic
   rules.
4. **Target named error profiles.** Each variant must name which failure family
   it is designed to improve before it runs.
5. **Small prompts plus tools beat prompt stuffing.** Boundary guidance should be
   retrieved by scenario, not pasted wholesale into every prompt.
6. **Budget fairness.** Every multi-agent pipeline must have a matched
   single-agent comparator with the same model-call, token, and tool-call budget.
7. **Attribution first.** Reports must include raw model-owned score,
   format-only repair score, selected-evidence repair score if used, and final
   score. Semantic deterministic repair cannot be hidden inside "normalization."
8. **No test tuning.** Development happens on validation hard slices,
   validation25/50/250, synthetic or adversarial panels, and full validation only
   when needed. `test450` is one frozen aggregate audit after a candidate is
   locked.

## Primary Error Profiles To Target

Use validation artifacts and validation row-level review only. Do not use test
row failures to build these slices.

| Profile | Why it matters | Targeted reasoning behavior |
| --- | --- | --- |
| `freq_category_shift` | Largest remaining structured-event validation family. | Explicit numerator, denominator, time window, and category calculation before final label. |
| `unknown_false_pos` and `no_reference` confusion | LLMs overuse boundary states when the note has awkward but real frequency evidence. | Require a positive no-reference proof before no-reference; require uncertainty proof before unknown. |
| `unknown_false_neg` | Models over-compute rates from last-event-only, uncertain, or incomplete evidence. | Preserve unknown when recurring cadence is absent. |
| `seizure_free_false_neg` | Structured events can miss the final seizure-free state from last-event-only/no-events-since language. | Distinguish no-events-since duration from ordinary historical event dates. |
| `seizure_free_false_pos` | Prior direct and agentic variants over-selected seizure-free states. | Require no conflicting current/recent frequency evidence before seizure-free. |
| `cluster_axis_error` | Cluster cadence and events-per-cluster burden are frequently collapsed or multiplied wrongly. | Separate cluster cadence from per-cluster count; multiply only when both are asserted. |
| Multiple active semiologies | Lower-frequency semiology can be selected over higher active burden. | Enumerate all current semiologies and choose the highest clinically active burden. |
| Evidence grounding gaps | Over-fire often comes with weak or non-exact evidence. | Every final state must cite exact evidence and, when needed, raw context. |

## Development Surfaces

### Fixed Hard50 Gate

Use the existing fixed validation hard slice:

```text
experiments/gan2026_agentic_validation_hard50_manifest_2026-06-12.json
```

This remains the first meaningful agentic decision surface after validation25
contract smoke. It is deliberately uncomfortable and should catch broad
prompt/tool over-fire before validation250.

### Family Hard Slices

Create validation-only slice manifests before running variants. Suggested
manifests:

- `unknown_no_reference_validation50`
- `seizure_free_last_event_validation50`
- `frequency_denominator_validation50`
- `cluster_axis_validation50`
- `multi_semiology_burden_validation50`

Slice membership may use validation labels and validation artifacts because this
is development data. Each slice artifact must record the trigger rule and the
source artifacts used. These slices are for mechanism testing, not final claims.

### Validation250

Use the standard locked validation250 prefix or the already established project
validation250 row policy. A candidate only reaches validation250 after passing
contract smoke and hard-slice gates.

### Test450

Run `test450` only after one candidate is frozen: prompts, tools, model IDs,
budget, aggregation, repair policy, scorer, and inspection policy. The only
allowed first readout is aggregate Purist/Pragmatic plus predeclared aggregate
slice metrics whose definitions were fixed without test row inspection.

## Shared Tool Contracts

All tools must exclude gold labels, split membership, row IDs, and deterministic
final-label choices.

### `inspect_structured_events`

Input: one saved structured-event record.

Output: compact event table with event IDs, kind, temporality, assertion,
certainty, applies-to, raw value fields, normalized candidate facts, and selected
event IDs from the original LLM structured-event pass.

Purpose: expose the strong structured-event foundation without giving a
deterministic answer.

### `fetch_evidence_context`

Input: event ID or exact evidence string plus a small context window size.

Output: exact quote and bounded surrounding note context.

Purpose: let the reasoner check whether event evidence supports the proposed
clinical interpretation.

### `calculate_frequency`

Input: a selected semantic fact: ordinary rate, range, cluster cadence plus
events per cluster, or seizure-free duration.

Output: monthly frequency, Purist/Pragmatic category, calculation trace, and
warnings. It must not choose which fact is clinically final.

### `render_gan_label`

Input: model-selected semantic fact plus calculation trace.

Output: accepted Gan label string or format error.

Purpose: benchmark formatting only.

### `validate_evidence`

Input: final evidence strings and raw note text.

Output: exact substring status and missing-evidence warnings.

### `read_boundary_guide`

Input: scenario key such as `unknown_vs_no_reference`, `cluster_axis`,
`seizure_free_conflict`, `last_event_only`, `current_vs_historical`, or
`multi_semiology`.

Output: compact split-neutral guidance. It must not contain validation or test
row answers.

## Prediction Schema

Every variant should emit a common `ReasonedFrequencyDecision` shape:

```text
{
  final_label: str,
  final_kind: "frequency" | "seizure_free" | "unknown" | "no_reference" | "unresolved_multiple",
  selected_event_ids: list[str],
  rejected_event_ids: list[str],
  evidence: list[str],
  boundary_profile: list[str],
  calculation_trace: str | null,
  clinical_rationale: str,
  uncertainty: "low" | "medium" | "high",
  tool_calls: list[ToolTrace],
  attribution: "llm_selected_tool_rendered" | "llm_selected_format_repaired" | "llm_original_structured_event_kept"
}
```

The LLM owns `final_kind`, selected event IDs, rejected event IDs, and clinical
rationale. Deterministic code can validate and render only after selection.

## Variant Families

### V0: Pure Structured-Event Comparator

Purpose: establish the exact validation25, hard50, family-slice, and
validation250 comparator for GPT structured events and, where available, Qwen and
DeepSeek structured events.

Budget: no new model calls for saved-output replay; live calls only if a missing
model/split artifact is intentionally generated.

Promotion role: comparator only. The final candidate must beat the best V0
condition, not merely the deterministic floor.

### V1: Single LLM Event Reasoner

Hypothesis: a second LLM reasoning pass over structured events and raw evidence
can fix selection errors without deterministic fallback.

Budget: one model call after the structured-event extraction.

Inputs: structured-event record, compact event table, original structured-event
final answer, and raw evidence snippets. No deterministic top label.

Target profiles: `freq_category_shift`, `unknown_false_pos`,
`seizure_free_false_neg`, multiple semiologies.

Gate: on fixed hard50, net improvement versus V0 with no more than two
correct-to-wrong regressions. If it cannot beat V0 on hard50, do not run
validation250.

### V2: Single Tool-Calling Event Reasoner

Hypothesis: dynamic evidence, arithmetic, and guide tools let one agent reason
more carefully without a bloated prompt.

Budget: one model-owned loop, maximum four tool calls, maximum two model calls
if a final verifier call is used. Matched no-tool comparator required.

Tools: `inspect_structured_events`, `fetch_evidence_context`,
`calculate_frequency`, `render_gan_label`, `validate_evidence`,
`read_boundary_guide`.

Target profiles: denominator/range errors, cluster arithmetic, seizure-free
conflict, unknown/no-reference boundary.

Gate: must improve at least three of the five family hard slices and must not
lose aggregate hard50 versus V1.

### V3: Targeted Boundary Router With One Specialist

Hypothesis: agentic value comes from routing only genuinely hard boundary cases
to the right specialist, not from running a heavy panel on every row.

Budget: router call plus at most one specialist call. Specialist is selected
from `temporal_boundary`, `sentinel_boundary`, `cluster_burden`,
`multi_semiology_burden`, or `rate_denominator`.

Fallback: keep the original LLM structured-event final answer when the router
finds no target profile. This is an LLM fallback, not deterministic top.

Target profiles: all named profiles, especially rows with multiple extracted
events or boundary-state disagreement.

Gate: changed-label precision on validation hard slices must be at least `0.60`
against V0, with no family showing net negative change.

### V4: Verifier-First Structured-Event Correction

Hypothesis: the best generalizing intervention is not a new full selector, but a
verifier that only overrides the pure structured-event final answer when it can
prove a boundary or burden contradiction from evidence.

Budget: one verifier call, optional tool calls. No deterministic fallback.

Actions:

- `keep_original_structured_event_final`
- `replace_with_existing_event`
- `replace_with_recomputed_fact_from_selected_evidence`
- `abstain_unrenderable`

Target profiles: high-precision correction of GPT structured-event errors while
preserving the strong pure SE test behavior.

Gate: on fixed hard50, at least `+4` net Purist versus V0 and changed-label
precision at least `0.70`; on validation250, at least `+5` net Purist versus V0.

### V5: Multi-Agent Specialist Panel

Hypothesis: separate clinical specialists can reduce correlated reasoning
errors when the coordinator is forced to cite evidence and calculation traces.

Budget: matched to V2 or V3 by total model calls and tokens. Initial panel:

- temporal/sentinel specialist;
- rate and denominator specialist;
- cluster and multi-semiology burden specialist;
- coordinator/verifier.

Inputs: same structured-event record and tools as V2. No deterministic top.

Gate: must beat a matched-budget single-agent variant on fixed hard50 and at
least three family slices. If it does not, no validation250 escalation and no
multi-agent value claim.

### V6: Cross-Model LLM Reasoning Panel

Hypothesis: model diversity can help if the coordinator reasons over evidence,
not if it merely votes exact labels.

Budget: one event-reasoner call each for GPT, Qwen, and DeepSeek plus one
coordinator call. The matched single-agent comparator gets the same total call
budget through self-consistency.

Coordinator input: each model's selected events, rejected events, evidence,
calculation trace, and uncertainty. Do not include deterministic top.

Gate: must beat same-model self-consistency on hard50 and validation250. Exact
label voting alone is not sufficient because the validation consensus/test audit
already showed poor transfer.

### V7: Event-Completion Agent

Hypothesis: some structured-event errors are extraction omissions rather than
selection mistakes, especially unknown false positives and seizure-free false
negatives.

Budget: trigger detector plus one local re-extraction call over bounded raw
context, then V1 or V2 reasoner.

Allowed trigger features: empty event table, boundary final answer with nearby
frequency text, last-event-only/seizure-free conflict, non-exact evidence, or
multiple semiologies in raw text not represented in events. Triggers must be
defined on validation only.

Gate: must improve omission-heavy family slices without increasing parse/schema
failures above `2%`.

## Evaluation Ladder

### Stage 0: Contracts And Baselines

Deliverables:

- common `ReasonedFrequencyDecision` schema;
- tool contracts and tests;
- V0 scores on validation25, fixed hard50, family hard slices, and validation250;
- report mapping which profile each row/slice is intended to test.

Stop rule: do not run agents until V0 and tool traces are reproducible.

### Stage 1: Validation25 Contract Smoke

Run V1, V2, and one multi-agent candidate on validation25.

Promotion requirements:

- schema/parse failure rate `<= 4%`;
- final evidence exact substring rate `>= 90%`;
- no systemic invalid labels;
- raw model-owned and format-only scores reported separately.

### Stage 2: Fixed Hard50 And Family Hard Slices

Run V1 through V7 selectively. Use row-level validation review to diagnose
failures, but record all changes in artifacts.

Promotion requirements to validation250:

- no candidate may be worse than V0 on fixed hard50;
- preferred candidate must improve fixed hard50 by at least `+4` net Purist or
  improve three family slices with no net-negative family;
- correct-to-wrong regressions versus V0 must be `<= 2` on fixed hard50;
- changed-label precision must be `>= 0.60` for broad selectors, `>= 0.70` for
  verifier-only selectors;
- multi-agent candidates must beat matched-budget single-agent comparators.

### Stage 3: Validation250 Development Result

Run only candidates promoted from Stage 2.

Promotion requirements:

- Purist at least `218/250` (`0.872`) or at least `+5` rows over best V0 on the
  same surface, whichever is more informative after V0 is scored;
- Pragmatic no worse than V0 by more than two rows;
- evidence exact substring rate `>= 90%`;
- model-owned or format-only score within three Purist rows of final full-repair
  score, unless the artifact is explicitly classified as hybrid deterministic
  repair;
- no single failure family accounts for a majority of regressions.

### Stage 4: Full Validation750 Freeze Check

Use this only for one or two leading candidates after validation250.

Promotion requirements for a frozen test protocol:

- beats GPT pure structured events on validation750;
- does not rely on deterministic top, deterministic candidate ranking, or
  semantic post-processing as the prediction-bearing source;
- preserves or improves hard-slice gains from Stage 2;
- has a frozen prompt/tool/model/budget/repair configuration;
- has a written test inspection policy: aggregate only on first readout.

### Stage 5: Frozen Test450 Audit

Run once after explicit authorization.

Success criterion:

- at least `383/450` Purist (`>0.85`);
- preferably also beats GPT pure structured-events Pragmatic (`381/450`) or
  explains a Purist/Pragmatic tradeoff before the run;
- no row-level test error inspection or tuning after the result.

If the candidate fails, record the result as final-evaluation evidence and start
a new validation-only cycle.

## Implementation Notes For Next Session

1. Create or reuse a shared runner under the existing Gan CLI rather than adding
   a one-off script per variant.
2. Add a `--agentic-variant` or new pipeline names such as:
   - `llm_event_reasoner`
   - `single_agent_event_tools`
   - `targeted_boundary_router`
   - `structured_event_verifier`
   - `multi_agent_event_specialists`
   - `cross_model_event_reasoning_panel`
3. Save traces per row:
   - structured-event input artifact;
   - tool calls and outputs;
   - specialist decisions;
   - final decision schema;
   - raw model final label;
   - format-only rendered label;
   - final rendered label;
   - comparison against V0 and scoring result.
4. Build validation-only hard-slice manifests before tuning prompts.
5. Keep prompt context small. Boundary guides should be retrieved by tool call.
6. Do not include deterministic top labels, candidate ranks, gold labels, row
   IDs, or split membership in prompts or tool outputs.
7. Use `.venv` for all commands and record model IDs, temperatures, token caps,
   cache policy, retries, and wall-clock cost.

## Expected Decision Outcomes

The plan should produce one of three clean outcomes:

1. **Promote a verifier or tool-reasoner.** It improves V0 on hard slices and
   validation250, then earns a frozen test audit.
2. **Reject multi-agent value.** Specialist panels fail to beat matched
   single-agent variants, but the trace artifacts become paper-relevant negative
   controls.
3. **Return to pure structured events.** If no LLM-owned reasoning layer beats
   GPT structured events without deterministic fallback, the honest close-off is
   that structured events are the durable contribution and agentic orchestration
   is not yet justified for Gan 2026.

The north star is not a clever validation ensemble. It is a model-owned,
evidence-grounded clinical selection layer that can survive a frozen aggregate
test read without borrowing its apparent strength from brittle deterministic
rules.
