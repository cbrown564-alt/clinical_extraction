# 0018: The Reliability Scorecard's Canonical Subject Is the `v0_reference` Single-SE-Mini Layer

Date: 2026-06-17

## Status

Accepted.

## Decision

The Gan 2026 reliability scorecard
(``) has
**one canonical subject**: the frozen production architecture — the single GPT
structured-event pass on `gpt-4.1-mini` — read per-row from the `v0_reference`
layer of the V12 fresh-evidence-reasoner artifacts
(`gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_4_2026-06-13.jsonl` and
its validation750 sibling).

Every metric in the ten-dimension scorecard is computed on that layer unless it
is **explicitly tagged** as a comparator: `[comparator: V12-full-gpt4.1]` (the
0.842 high-complexity ceiling) or `[comparator: hybrid-adjudicator]` (the rq9
selective-action router layer). Comparator numbers may appear in the paper but
must never occupy a scorecard row as if they described the subject.

Concretely:

- **Task correctness** is `v0_reference.comparison.purist_correct` (0.809 test /
  0.881 validation), not the 0.842 V12 `final` layer.
- **Faithfulness** is `v0_reference.evidence_valid`, not the full-gpt-4.1 V12
  `final`-layer figures (703/750, 423/450 exact), which become a labeled
  comparator.
- **P0.2 risk–coverage** orders rows by the [[External Risk Score]] against
  `v0_reference.comparison.purist_correct`, not the `hybrid_adjudicator_with_adapters`
  `purist_correct` carried in the rq9 router file. (The
  [[Cross-Model Agreement Count]] leg still joins in by `source_row_index`.)

## Context

The plan as first drafted printed, in a single ten-row table, numbers computed on
three different systems: 0.809 (mini single-SE) beside 0.842 (full-gpt-4.1 V12);
faithfulness 703/423 (full-gpt-4.1 V12 `final` layer); and a risk–coverage curve
sourced from the rq9 router, whose `source_layer` is
`hybrid_adjudicator_with_adapters` — a third architecture entirely, with a
non-production 697/750 = 0.929 base rate.

A four-agent audit and the project's own closeout synthesis (Provenance Caveat #5)
had already established that `build_dspy_lm` does no model aliasing, that the 0.842
hybrid and both reasoner ablations ran on **full `gpt-4.1`** (which exhausted the
OpenAI budget), and that only the single SE pass is mini-verified. The
`v0_reference` layer embedded in the V12 artifacts is byte-identical to the
standalone mini single-SE run (0/750 mismatches), so the production numbers are
recoverable per-row at no model budget.

## Why

The paper's thesis is a claim about **one** extractor — *"a clinical extractor
that knows what it cannot extract."* A scorecard whose rows are each measured on a
different architecture has no single "it" to make that claim about, and silently
mixing a full-`gpt-4.1` faithfulness number into a scorecard headlined by a mini
task score would misattribute capability the production path may not have. The
whole methodological spine of this strand — decision-effect component attribution,
reporting evidence validity separately from score, refusing to let a
deterministic-floor or higher-capability gain be silently credited elsewhere —
exists precisely to prevent this class of laundering. Canonicalizing on
`v0_reference` makes the scorecard a coherent statement about the system that is
actually frozen for go-forward use.

## Consequences

- Several dimensions whose richest existing artifacts live on the *wrong*
  architecture (faithfulness, the rq9-sourced abstention/calibration curve) must
  be **re-derived from `v0_reference`** rather than re-expressed as-is. The
  Phase 0 work is therefore more than "re-tabulate existing logs"; it is
  "re-tabulate existing logs *onto the canonical layer*."
- The 0.842 V12 stack and the hybrid-adjudicator router remain in the paper only
  as explicitly tagged comparators. The honest selling point is that the *simpler,
  mini* system is the one being characterized for reliability.
- The [[External Risk Score]]'s cross-model-agreement leg is fully available on
  validation750 but degrades to a two-agent consensus on test450, so the canonical
  subject's holdout risk–coverage replay (P1.1) is a weaker port, not an identical
  one — this asymmetry must be stated wherever the curve appears.
- Any future reliability number added to the scorecard must declare its layer; a
  number without a layer tag is not admissible.

## Related Artifacts

- `` —
  the plan this decision governs.
- `` — Provenance
  Caveat #5, the load-bearing prior.
- `experiments/gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_4_2026-06-13.jsonl`
  — carries the `v0_reference` layer (`comparison.purist_correct`,
  `evidence_valid`, `final_label`, `selected_event_ids`).
- `experiments/gan2026_agentic_structured_event_consensus_unanimous_exact_validation750_2026-06-13.jsonl`
  — `consensus_decision.votes`, source of the [[Cross-Model Agreement Count]].
- `experiments/gan2026_rq9_selective_action_router_v3_2026-06-04.jsonl` — the
  `hybrid_adjudicator_with_adapters` layer, now a tagged comparator only.
- `CONTEXT.md` — [[The Wall]], [[Forward-Observable Feature]], [[External Risk Score]],
  [[Cross-Model Agreement Count]].
