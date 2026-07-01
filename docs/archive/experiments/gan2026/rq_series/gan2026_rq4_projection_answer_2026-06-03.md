> **Superseded for navigation —** canonical summary: [`COMPONENT_MECHANICS_CANON.md`](../COMPONENT_MECHANICS_CANON.md). Full detail retained below.

# Gan 2026 RQ4 Projection Answer

Date: 2026-06-03

Supersession note, 2026-06-03: this report is retained as a diagnostic baseline
audit, not a completed RQ4 research answer. Its deterministic-default conclusion
falls into the validation-tuned selector trap described in
`` and is
superseded by
``.

## Answer

RQ4 is answered for saved validation replay as a development-control question.

The best broad default projection substrate remains
`deterministic_top_candidate`: 697/750 Purist-correct rows on validation750,
with no changed-row regression risk because it is the fixed comparator. The
broad `state_graph_projection` should not replace it: it is 655/750
Purist-correct, changes 49 labels, and creates 42 deterministic-correct
regressions with no wrong-to-correct gains on the same validation750 replay.

The practical RQ4 answer is therefore:

- Use deterministic top as the default scorer-facing projection substrate.
- Do not promote broad graph projection as a replacement projection policy.
- Keep hybrid adjudicator raw labels gated: it has exact/source-traced evidence,
  but its four validation750 label changes are all deterministic-correct
  regressions.
- Use graph projection policies selectively only where the state representation
  and metadata gate make the projection problem explicit: boundary-state
  priority and graph-gated month-bucket duration are useful diagnostic policies,
  not broad defaults.
- Treat claim-table and LLM-heavy selected facts as promising schema/projection
  diagnostics, not production projection layers, until they have same-surface
  source-id instrumentation and changed-row accounting.

## Supporting Artifacts

Protocol:
``

Matrix report:
`experiments/gan2026_rq4_projection_decision_matrix_2026-06-03.md`

Machine-readable matrix:
`experiments/gan2026_rq4_projection_decision_matrix_2026-06-03.jsonl`

Builder:
`src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/projection_decision_matrix.py`

The matrix has 3,250 projection-decision rows over 750 validation source rows.
It replays saved artifacts only; it makes no new model calls.

## Component Trade-Offs

| Component | Surface | Projection correct | Changed vs baseline | Wrong-to-correct | Correct-to-wrong | Evidence/source trace |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Deterministic top | validation750 | 697/750 | 0 | 0 | 0 | 635/750 exact evidence, 750/750 source ids |
| Hybrid adjudicator raw | validation750 | 693/750 | 4 | 0 | 4 | 750/750 exact evidence, 750/750 source ids |
| State graph projection | validation750 | 655/750 | 49 | 0 | 42 | 633/750 exact evidence, 750/750 source ids |
| Claim-table final query | validation25/250 diagnostic | 223/242 judged | not same-row comparable | not same-row comparable | not same-row comparable | 246/248 exact evidence, 248/248 claim ids |
| LLM-heavy selected fact | validation250 diagnostic | 203/240 judged | not same-row comparable | not same-row comparable | not same-row comparable | 242/250 exact evidence, no source-id trace |

The same-row validation750 result is decisive for the broad default: every
non-deterministic broad replacement either ties the deterministic label most of
the time or adds regressions when it changes labels. Projection is not yet a
place to spend the deterministic safety floor.

The graph-only diagnostic surfaces expose selective value:

| Policy | Surface | Result |
| --- | --- | --- |
| `boundary_state_priority` | 42 representable graph projection misses | 17/42 exact corrections, 0 regressions versus baseline on this miss-only surface |
| `graph_gated_month_bucket_duration` | 18 target duration rows plus 232 regression rows | 18/18 duration corrections, 0 changed labels on the 232-row regression panel |
| `oracle_gold_node` | 42 representable graph projection misses | 23/42 exact upper-bound corrections |

The oracle gap matters. Even when a graph can contain the gold node, a
non-oracle projection policy recovers only part of it. `boundary_state_priority`
recovers most unknown/unresolved-multiple projection misses, while
`graph_gated_month_bucket_duration` is clean for a narrow seizure-free duration
normalization surface. Neither result licenses a broad graph projection
replacement.

## Hidden-Family Readout

The strongest hidden-family readouts come from diagnostic surfaces:

- Boundary/unknown projection remains fragile. LLM-heavy selected facts are only
  8/18 Purist-correct on hidden `unknown_boundary` judged rows and 11/21 on
  `uncertainty_or_ambiguity` judged rows, despite high exact-evidence rates.
- Cluster and competing-semiology rows still need cautious projection:
  LLM-heavy selected facts are 37/49 judged rows correct for `cluster_burden`
  and 69/87 for `competing_semiologies`.
- Seizure-free duration has a clear selective graph fix when a duration
  normalizer node is present: graph-gated month-bucket duration produced 18/18
  corrections on the target duration surface and no changed labels on its
  regression panel.
- Broad state-graph projection remains weak outside the gated duration case:
  validation750 state-graph projection has 42 deterministic-correct regressions
  and no wrong-to-correct gains.

## Transfer Confidence

Development confidence is high for the broad default conclusion:
deterministic top should remain the default projection substrate on saved
validation replay.

Development confidence is moderate for selective boundary and duration graph
policies. They are mechanistically plausible and have exact node evidence on
diagnostic surfaces, but those surfaces were preselected from validation-cycle
work.

Holdout-transfer confidence is low to moderate. The result is useful for the
next component question, but it is not a holdout claim. Before any holdout-facing
use, freeze a projection policy that can only act under explicit graph metadata
gates, then run a predeclared changed-row audit with exact evidence, source-id
validity, wrong-to-correct accounting, and deterministic-correct regression
accounting.

## Metadata And Instrumentation Gaps

- Claim-table and LLM-heavy projection diagnostics are not same-row validation750
  replacements in this matrix.
- LLM-heavy selected facts lack selected source ids, so they cannot support an
  exact-source-id projection claim.
- Hidden-family tags are incomplete for the broad validation750 state-graph
  projection rows.
- The diagnostic graph policies answer projection only when the relevant graph
  node already exists; missing node construction belongs to RQ1/RQ3 rather than
  RQ4.
- Rendering and benchmark-format drift after a selected state belongs to RQ5.

## Decision

RQ4 is answered for saved validation replay:

- Default projection substrate: `deterministic_top_candidate`.
- Rejected broad replacement: `state_graph_projection`.
- Gated support component: `hybrid_adjudicator_raw` evidence only, not raw label
  changes.
- Selective diagnostic policies worth preserving for future gated experiments:
  `boundary_state_priority` for unknown/unresolved-multiple graph states and
  `graph_gated_month_bucket_duration` for seizure-free duration nodes.
- Diagnostic schema sources for later component work: claim-table final query
  and LLM-heavy selected fact.

## Next Action

Move the active question to RQ5 deterministic compilation and rendering. RQ4
shows that broad projection should stay conservative and gated; the next
separable question is whether a fixed selected state can be rendered into a
Gan-compatible label without semantic drift.
