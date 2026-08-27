# Gan 2026 Agentic Redo — Results (2026-07-01)

Status: complete for Gan 2026 (Phase 1-2 of `docs/plans/proud-bubbling-ocean.md`).
Implements the predeclaration at
`docs/experiments/gan2026/agentic/gan2026_agentic_redo_predeclaration_2026-07-01.md`.
Raw data: `experiments/gan2026_agentic_redo_battery_hard50_results.jsonl` (385
rows), report: `experiments/gan2026_agentic_redo_battery_hard50_results.md`.

## What this answers

The supervisor brief's key research goal ("compare single-prompt extraction
vs multi-agent extraction under the same budget constraints") plus the
user's open question ("how good can multi-agent get vs a hybrid
architecture, and is dynamism actually load-bearing on this task"). The
project had a prior attempt at this (2026-06-12) that concluded tool-use
and multi-agent hurt (single_greedy 34/50 beat single_agent_tools 20/50 and
multi_agent_matched 22/50 on hard50) — but that "multi-agent" condition was
later found to be four identical calls to one signature with cosmetic role
labels, not genuinely differentiated agents, and tool invocation was
hard-coded in Python, never an LM decision. This redo fixes both with
`dspy.ReAct` (genuine LM-decided tool use) and specialists whose output
schema structurally cannot contain a final label.

## A mid-run bug, found and fixed before any conclusion was drawn

The first full run (temperature=0.2 uniformly across all conditions,
including `single_greedy`) produced an implausible result: `single_greedy`
scored 17/50, less than half the 06-12 baseline's 34/50, for a condition
that should be near-deterministic. Diagnosis (see git history + a targeted
50-call diagnostic, not the full 385-pair batch):

- Reran `single_greedy` alone at temperature=0.0: 19/50 — barely different
  from 17/50, ruling out temperature as the primary driver.
- Diffed every function actually exercised (`_build_prompt_input`,
  `_model_call_plans`, `_execute_model_call`, `_compare_to_gold`) between
  the exact 2026-06-12 commit and today: byte-identical. A later refactor
  (06-27) touched only an unrelated top-level dispatch wrapper this redo
  bypasses.
- The label normalizer hasn't changed since before 06-12. DSPy has stayed
  pinned at 3.2.1 throughout.
- Found instead: `runner.py::_run_model_call` discards its own
  `temperature` argument (`del model, temperature, max_tokens`) and always
  uses whatever LM is globally configured via `dspy.configure` — a
  pre-existing structural gap meaning `single_self_consistency_temperature`
  has never actually varied temperature across its 4 samples in this
  codebase, contrary to its name and this project's own stated convention
  that self-consistency must sample varying temperatures.
- No root cause fully explains the drop (most likely genuine drift in the
  hosted `gpt-4.1-mini` model over the 3 weeks since 06-12, which cannot be
  verified or fixed from here).

**Decision (user's call)**: abandon the historical-comparison framing
entirely. The valid comparison was never "does today's run reproduce
06-12's exact numbers" — it's "do the new conditions beat a *freshly run*,
same-session `single_greedy`/`self_consistency`, under identical settings."
That internal comparison is unaffected by whatever caused the historical
number to be unreproducible. Two real fixes were made and used for the
reported run: `single_greedy`/`single_agent_tools_react`/
`multi_agent_d3_static`/`multi_agent_dynamic_orchestrator` run at
temperature=0.0 (house convention for deterministic/best-effort
conditions); `single_self_consistency_temperature` runs at temperature=0.7
specifically (making it genuinely test sampling diversity for the first
time in this codebase, rather than silently being a near-copy of greedy).

## Results (battery=27 cases, hard50=50 rows, all conditions run fresh, same session)

| Panel | Condition | Purist | True Failures | Repair Rate |
| --- | --- | ---: | ---: | ---: |
| battery | single_greedy | 19/27 | 0/27 | 0/27 |
| battery | single_self_consistency_temperature (temp=0.7) | 18/27 | 0/27 | 0/27 |
| battery | single_agent_tools_react | 20/27 | 0/27 | 13/27 |
| battery | multi_agent_d3_static | 17/27 | 0/27 | 16/27 |
| battery | multi_agent_dynamic_orchestrator | 18/27 | 0/27 | 18/27 |
| hard50 | single_greedy | 19/50 | 0/50 | 0/50 |
| hard50 | single_self_consistency_temperature (temp=0.7) | 15/50 | 0/50 | 0/50 |
| hard50 | single_agent_tools_react | **23/50** | 1/50 | 30/50 |
| hard50 | multi_agent_d3_static | **29/50** | 5/50 | 31/50 |
| hard50 | multi_agent_dynamic_orchestrator | **32/50** | 1/50 | 35/50 |

"True failures" = no usable answer produced (call error or unparseable
final_label) — near-zero everywhere, so none of these architectures are
meaningfully less reliable in the "did it answer at all" sense. "Repair
rate" is high for the new conditions (30-35/50) but is benign format
normalization (e.g. "seizure free since 2018" → "seizure free for multiple
year") with a scored answer still produced — not a failure, per the
predeclaration's schema-validity reporting requirement.

**Win/loss vs `single_greedy` on hard50:**

| Candidate | Wins | Losses | Net |
| --- | ---: | ---: | ---: |
| single_agent_tools_react | 12 | 8 | +4 |
| multi_agent_d3_static | 14 | 4 | +10 |
| multi_agent_dynamic_orchestrator | 17 | 4 | +13 |
| multi_agent_dynamic_orchestrator vs multi_agent_d3_static | 7 | 4 | +3 |

## Predeclared gate outcomes: both FAIL, at the locked strict threshold

- Angle 1 gate (react vs greedy, hard50): wins=12, losses=8 → **FAIL**
  (needed wins≥5 **and** losses≤1).
- Angle 2 dynamism gate (dynamic orchestrator vs d3-static, hard50):
  wins=7, losses=4 → **FAIL** (needed wins≥3 **and** losses≤1).

Per the predeclaration, this is the honest, allowed, valid outcome of this
study — no gate promotes to validation750, no `test450` claim was ever in
scope. Per the predeclaration's own stop rule, gate thresholds are not
loosened after seeing results.

## The honest, two-sided reading

This is not a clean "agentic doesn't help" result, nor a clean "agentic
wins" result — both would overstate what the data supports.

**In favor of decomposition/multi-agent**: every new architecture beats
`single_greedy` by a wide accuracy margin on the harder, more
discriminating panel (+8 to +26 percentage points), with near-zero true
failure rates. `multi_agent_dynamic_orchestrator` (LM decides which
specialists to consult) beats `multi_agent_d3_static` (always runs all
three) with a positive net margin (+3), which is real, if modest, evidence
that *dynamism specifically* — not just decomposition into more calls —
is doing something on this task. This directly cuts against the user's
stated prior that dynamism wouldn't matter because the note is short enough
for a single prompt to see everything; the data suggests dynamic tool/
specialist selection recovers real accuracy a static always-run-everything
decomposition does not.

**Against a promotion claim**: none of the loss counts are small. 4-8
losses out of 50 is a real, non-trivial regression rate on individual rows,
and the strict gate (wins≥5, losses≤1) exists precisely to prevent
promoting an architecture that is "usually better but sometimes much
worse" without more evidence than one 50-row panel provides. At n=50, a
"losses≤1" bar is a demanding statistical target regardless of the true
underlying effect size — this may be a lesson about the gate design itself
(borrowed verbatim from the 06-12 D-series without re-deriving it for this
sample size) rather than about the architectures. A larger sample
(validation750-scale, which this predeclaration explicitly gates behind
passing this stage) would be needed to distinguish "real but modest
improvement with real variance" from "not actually better."

**Self-consistency's negative result is itself informative**: sampling at
genuine temperature (0.7) for the first time in this codebase's history
made `single_self_consistency_temperature` *worse* than greedy (15/50 vs
19/50) rather than better. On this task, the single most-likely completion
appears to usually already be the right one; adding sampling diversity
mostly adds noise the majority vote doesn't fully filter back out.

## What this means for the user's question

"How good can multi-agent get" — on this evidence, meaningfully better
than plain single-prompt extraction (58-64% vs 38% Purist on the hard
panel), and dynamic orchestration specifically outperforms static
decomposition. "Is dynamism load-bearing" — yes, on this evidence, though
the margin (+3 net wins) is modest enough that it should be treated as
suggestive, not conclusive, without a larger sample. Neither finding
clears this project's own strict promotion bar at n=50, which is a
statement about statistical power at this sample size as much as about the
architectures.

## Not pursued in this pass

- Validation750-scale confirmation (gated behind the (failed) hard50
  promotion gate per the locked predeclaration — a fresh predeclaration
  would be needed to run it anyway given the gate outcome, not a
  continuation of this one).
- Re-deriving the gate's win/loss thresholds for n=50 statistical power
  (flagged above as a real methodological question, not resolved here).
- ExECTv2 port (Phase 3) — informed by this result (decomposition and
  dynamic tool selection are worth porting; the gate-design lesson above
  should carry over), scoped separately.

## Artifacts

- `experiments/gan2026_agentic_redo_battery_hard50.py` (driver)
- `experiments/gan2026_agentic_redo_battery_hard50_results.jsonl` (385 rows)
- `experiments/gan2026_agentic_redo_battery_hard50_results.md` (generated report)
- `experiments/gan2026_agentic_redo_battery_hard50_results_temp0.2_confounded.{jsonl,md}`
  (archived, invalid — kept for audit trail, not for citation)
- `experiments/gan2026_agentic_redo_temperature_diagnostic.py` (the 50-call
  diagnostic that ruled out temperature as the primary cause)
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/agentic/react_single_agent.py`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/agentic/multi_agent_ceiling.py`
- `src/clinical_extraction/core/agentic_contracts.py` (ported, task-neutral)

## Guardrails respected

`test450` never read or run. No holdout row-level inspection. No gate
threshold changed after seeing results.
