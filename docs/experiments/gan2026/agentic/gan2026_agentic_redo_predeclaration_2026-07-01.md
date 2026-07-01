# Gan 2026 Agentic Redo — Predeclaration (2026-07-01)

Status: **predeclared, locked before any live call.** Implements
`docs/plans/proud-bubbling-ocean.md` Phase 0-2. Companion to the 2026-06-12
agentic branch (`docs/design/gan2026_agentic_phase5_contracts.md`,
`experiments/archive/gan2026_misc_iterations/gan2026_agentic_hard50_redesign_after_e2_stop_2026-06-12.md`)
which this redo supersedes for the specific flaws named below — it does not
relitigate the prior branch's own findings (D0-D2 results, the
`hard50`/`validation25` panel choice) except where explicitly restated.

## Why this redo is not a repeat

The 06-12 branch's `single_agent_tools`/`multi_agent_matched` conditions
hard-coded tool invocation in Python (`runner.py::_tool_calls`) — the model
never decided whether/when to call a tool — and its "multi-agent" condition
was four identical calls to one signature with cosmetic `call_role` labels,
majority-voted. This redo fixes both: `dspy.ReAct` (confirmed present,
`dspy==3.2.1`) gives genuine LM-decided tool invocation, and Angle 2's
specialists are bounded evidence-only roles that structurally cannot emit a
final label (enforced by output schema, not just prompt instruction).

## Angle 1 — Matched budget (the brief's literal question)

**Hypothesis**: `single_agent_tools_react` (genuine LM-decided tool use)
outperforms `single_greedy` (plain single-prompt) at equal model-call
budget. Null/alternative hypothesis, explicitly allowed: no reliable
improvement, matching the user's own stated prior.

**Conditions**, one shared `AgentBudget` (`model_calls_per_row=4`,
`prompt_token_budget=2500`, `max_completion_tokens_per_call=600`,
`max_tool_calls_per_row=3`, `max_tool_output_tokens_per_row=700`,
`aggregation_budget_model_calls=1` — identical to the 06-12 budget so hard50
numbers stay directly comparable):

- `single_greedy` — 1 call, 0 tools (existing comparator, reuse as-is).
- `single_self_consistency_temperature` — 4 temperature-sampled calls,
  deterministic majority vote (existing comparator, reuse as-is).
- `single_agent_tools_react` — `gan2026/agentic/react_single_agent.py`,
  `dspy.ReAct(AgenticDecisionSignature, tools=[parser, boundary_guide],
  max_iters=3)`. 3 ReAct-loop calls + `dspy.ReAct`'s own 1
  final-extraction call = 4 model calls total; up to 3 tool calls across
  the 3 ReAct turns.

**Staged gate** (cheapest first; each stage must pass before spending on
the next):

1. **Smoke** (5 rows, near-zero cost): 0 call failures, 0 parse/schema
   failures, `dspy.ReAct` trace shows a coherent trajectory (thought/
   tool_name/tool_args/observation per turn) and reaches `finish` or
   `max_iters` cleanly.
2. **Robustness battery** (27 cases, `experiments/gan2026_robustness_battery_v1_checkpoints/`):
   report pass rate per condition; no promotion gate at this stage (the
   battery's own lesson is that passing it is necessary, not sufficient —
   a candidate passed 100% here and still regressed −106 on validation750
   in prior work), but any battery failure is grounds to stop before hard50.
3. **`hard50`** (50 real-corpus rows, `experiments/gan2026_agentic_validation_hard50_source_rows_2026-06-12.txt`):
   score Purist/Pragmatic against `single_greedy`; layer in evidence-
   validity rate, schema-validity/repair-rate, and a one-line disagreement
   read (genuine-model vs. gold-format-looking) on every flipped row.
4. **Locked promotion gate** (do not adjust after seeing results): promote
   `single_agent_tools_react` to validation750 only if, versus
   `single_greedy` on hard50, **net wins ≥ 5 and losses ≤ 1**, OR
   **changed-label precision ≥ 0.70 with no more than 1 regression** —
   the same gate shape the 06-12 D-series used (D1/D2 gates), reused
   deliberately for continuity. If neither route clears, Angle 1 stops
   here and the answer is reported as negative — this is an allowed,
   fully valid outcome of this predeclaration, not a failure to write up.
5. **If the gate passes**: validation750, scored against Table 1's existing
   rules/hybrid/LLM-only numbers (rules 0.908/0.919, hybrid 0.884/0.908,
   LLM-only 0.776/0.819 Purist/Pragmatic) for full context.

`test450` is out of scope for this predeclaration under any outcome — a
promotion past validation750 would need a separate, explicitly authorized
fresh frozen protocol.

## Angle 2 — Ceiling (open question, not budget-matched)

**Hypothesis**: genuinely dynamic multi-agent orchestration (the LLM
deciding which specialist sub-agents to invoke, per letter) outperforms a
static always-run-everything decomposition, and locating where either lands
relative to the hybrid ceiling (0.842 Purist "the wall" / 0.850 Pragmatic
production headline) tells us whether decomposition itself is the lever, or
whether dynamism specifically matters. Explicitly open to the user's stated
prior being correct (dynamism doesn't help because the note is short enough
that a single prompt already sees everything relevant).

**Conditions**:

- **`multi_agent_d3_static`** — resurrects the project's own never-run D3
  design verbatim: three bounded specialist roles, always all run —
  `frequency_fact_lister` (current frequency-bearing facts and active
  semiologies only), `boundary_hazard_lister` (seizure-free, unknown,
  no-reference, negation, historical hazards only), `cluster_burden_lister`
  (cluster cadence, events-per-cluster, whether cluster burden changes the
  final label) — feeding a `resolver` that must cite the specialist
  outputs it uses and explicitly reject lower-burden/boundary alternatives
  when it changes the fallback answer. **Structural constraint, not just a
  prompt instruction**: each specialist's DSPy output schema has no
  `final_label`/`answer_kind` field at all — it cannot emit a final answer
  even if instructed to, closing the exact gap that made 06-12's
  `multi_agent_matched` fake. 4 model calls total (3 specialists + 1
  resolver), 0 tool calls.
- **`multi_agent_dynamic_orchestrator`** — the real test of "LLM directs
  other LLMs": a `dspy.ReAct` orchestrator whose tools are the same three
  specialists (each specialist becomes a callable tool that, when invoked,
  makes its own LM call and returns typed evidence — never a label) plus
  the existing deterministic `parser`/`boundary_guide` tools. The
  orchestrator decides which specialists to consult (0-3 of them) based on
  its own read of the letter, then resolves to a final label itself. Capped
  at `max_iters=6` (bounding total possible model calls: up to 6
  orchestrator-reasoning turns, each turn may trigger 0-1 specialist LM
  calls, plus 1 final extraction call — worst case ~13 model calls,
  reported per-row so the actual average cost is measured, not assumed).

Both scored against `single_greedy`/hybrid ceiling on the same staged gate
as Angle 1 (smoke → battery → hard50), with one additional locked
comparison:

- **Dynamism gate**: `multi_agent_dynamic_orchestrator` is only reported as
  "dynamism matters" if it beats `multi_agent_d3_static` on hard50 by net
  wins ≥ 3, losses ≤ 1. If it does not clear this, the honest conclusion is
  that static decomposition captures whatever value decomposition offers,
  and dynamic tool selection added cost without benefit on this task — a
  legitimate, useful negative result directly answering the user's
  hypothesis.

Neither Angle 2 candidate is required to beat the hybrid ceiling to be
informative — the predeclared purpose is to locate where they land and
report that honestly, not to hit a promotion bar. `test450` is out of scope
under any outcome, same as Angle 1.

## Reliability scoring layer applied throughout

- Purist/Pragmatic accuracy (existing scorer) is the primary metric.
- Evidence-validity rate and schema/parse-failure rate reported per
  condition per stage — a condition with more failure surface (more calls,
  more tools) should not be credited as "better" if it is only avoiding
  failure less often.
- Every flipped row (win or loss vs. the relevant comparator) gets a
  one-line disagreement read before being counted as a real effect — not a
  full 4-agent canonical adjudication for every row, but enough to flag
  rows that look like gold-format artifacts rather than genuine model
  behavior, given this project has repeatedly found such artifacts inflate
  apparent error rates elsewhere (Diagnosis 93.5%, SF 61-83% H-inflated on
  ExECTv2 — the closest available precedent, cited for methodology, not as
  a Gan2026 number).

## Stop rules

- Stop before the next stage if the current stage shows systemic call or
  parse failure (more than 10% of rows) — a broken harness is not evidence
  about the architecture.
- Do not tune prompts, tool contracts, specialist schemas, or gate
  thresholds based on a stage's results. A failed gate is an outcome to
  report, not a cue to redesign and rerun the same stage.
- No `test450` use under any outcome of this predeclaration.
- No holdout-facing claim without a separate, explicitly authorized fresh
  frozen protocol.

## What gets written up regardless of outcome

Both angles produce a dated results doc (Task 15,
`docs/experiments/gan2026/agentic/gan2026_agentic_redo_results_<date>.md`)
stating, per angle: which stage was reached, the gate outcome (pass/fail
and by how much), and — critically — an honest answer to the user's
question, including if the answer is "the agentic conditions did not help
and the user's prior was correct." Negative results are reported with the
same weight as positive ones, consistent with how this project treats null
findings throughout (the SF/Diagnosis gold-quality findings, the GEPA
plateau, the Section/Timeline ablation earlier the same day).
