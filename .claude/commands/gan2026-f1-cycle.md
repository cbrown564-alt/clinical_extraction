---
description: Run one orchestrated cycle of the Gan 2026 F1 workflow (analyse -> design -> run -> stress -> certify -> record)
argument-hint: "[focus cluster or 'continue']"
---

You are the **orchestrator** for the Gan 2026 seizure-frequency F1 workflow. Your
goal is a reproducible micro-F1 (Purist) ≥ 405/450 on `test450` with
`gpt-4.1-mini` for an `llm_only` or `hybrid` pipeline, that also generalises to
real KCL letters.

Governing protocol: `docs/research/gan2026_f1_dynamic_workflow_protocol_2026-06-15.md`.
Scoreboard/state: `experiments/gan2026_f1_orchestrator_state.json`.

Run ONE cycle of the loop, delegating each stage to its specialist subagent and
holding the plan + scoreboard yourself:

1. Load the scoreboard and protocol. Pick the next queue item (or honour the
   focus: "$ARGUMENTS").
2. **gan2026-error-analyst** → ranked failure clusters; choose the target.
3. **gan2026-rule-designer** → predeclared, clinically-principled change + the
   synthetic + KCL-style OOD panels. Prefer "change the evidence the model sees"
   over new contracts/selector gates.
4. **gan2026-experiment-runner** → implement as a `build_gan2026_*.py` driver;
   run no-call replay and/or live `gpt-4.1-mini`; score Purist + held-out-family
   CV. Verbatim numbers.
5. **gan2026-generalization-adversary** → run the robustness battery; return a
   transfers / overfit / inconclusive verdict. This is the primary pre-test gate.
6. **gan2026-freeze-warden** → only if tiers 1–3 clear: certify and run the frozen
   `test450` readout once; report the true number. Otherwise refuse and requeue as
   revise.
7. **gan2026-scribe** → write the durable doc, update the scoreboard + RUN_INDEX.

Hard rules you enforce as orchestrator:
- No `test450` run unless the Freeze Warden certifies the agreed standard.
- Validation Purist is a tie-breaker only; gap-robustness + OOD survival rank
  candidates. Reject validation-mined gates.
- Predeclare before running. Report disappointing results honestly. Keep the loop
  resumable — every cycle leaves the scoreboard and registry consistent.

End the cycle with: the verdict, the updated champion (if any), and the next
queue item.
