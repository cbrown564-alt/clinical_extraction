# Gan 2026 RQ3 Rich Selected-State Hard-Panel Answer

Date: 2026-06-04

Status: validation-development component answer for the 75-row
`hidden_family_hard_panel`. This is not a broad validation, holdout, benchmark,
or F1 claim.

Protocol:
`docs/research/gan2026_rq3_rich_selected_state_protocol_2026-06-04.md`

Focused precursor:
`docs/research/gan2026_rq3_rich_selected_state_five_letter_answer_2026-06-04.md`

Artifacts:

- `experiments/gan2026_rich_selected_state_hard_panel_2026-06-04.jsonl`
- `experiments/gan2026_rich_selected_state_hard_panel_2026-06-04.md`

## Answer

The rich selected-state experiment answered the essential question positively,
but not completely:

```text
Candidate/evidence facts can be carried into a typed selected state with enough
boundary information to support deterministic projection, especially for
unknown and ambiguity boundaries. The representation is structurally reliable,
but the first renderer policy is not yet rich enough for cluster cadence,
benchmark multiple conventions, and diary aggregation.
```

This is a fundamentals result, not an F1 result. The key win is not that the
projected label matched the benchmark often enough. It is that the LLM supplied
the fields a deterministic projector needs to make principled decisions.

Hard-panel summary:

- rows: 75;
- structured selected-state records: 75/75;
- exact evidence and trace clean rows: 72/75;
- deterministic projected labels: 75/75;
- parseable projected labels: 75/75;
- boundary/parse error families: `evidence`=2, `selected_state_trace`=1;
- normalized projected-label match to gold, for orientation only: 26/75.

## What Good Means Here

Good means the selected state exposes the clinical boundary:

- current versus historical;
- asserted versus conditional;
- count and denominator when they are explicit;
- unresolved multiple wording without invented precision;
- cluster burden separately from cluster cadence;
- seizure-free claims with all-type scope and recent-event blockers;
- ambiguity fields when the note does not support a single clean rate.

By that standard, the hard panel is encouraging. The model overused
`state_kind="frequency"` on 69/75 rows, but it often put the corrective facts in
the boundary fields. That makes the broad category too weak to trust alone, but
the nested state useful.

## Strongest Result

The strongest result is unknown-boundary preservation.

Rows with gold kind `unknown` were usually rendered safely:

- `unknown`: 18/22 orientation exact;
- `unknown_boundary`: 17/20 orientation exact;
- `uncertainty_or_ambiguity`: 19/26 orientation exact.

This matters because previous component setups could select exact evidence and
still lose the reason the final answer should be unknown. Here, the model often
carried conditionality, recent-event blockers, and ambiguity into explicit
fields that the deterministic renderer could use.

Example: row 3356 had conditional events after curtailed sleep. The model still
called the state `frequency`, but it filled the conditionality note and
seizure-free blocker fields, so deterministic projection returned `unknown`.
That is the right architectural division: the LLM exposes the facts; policy
decides not to over-render them.

## Where It Breaks

The weak point is not schema validity. It is projection policy for rows where
the note contains true facts in a form the benchmark encodes with conventions:

| Hidden family | Rows | Orientation exact | Clean boundary rows | What this means |
| --- | ---: | ---: | ---: | --- |
| `cluster_burden` | 18 | 4 | 18 | Cluster facts are detected, but cadence versus per-cluster burden needs better deterministic policy. |
| `benchmark_format_convention` | 24 | 2 | 23 | The schema carries facts, but benchmark multiple/cluster conventions are still under-specified. |
| `rate_bucket_or_denominator` | 32 | 7 | 31 | Denominator fields exist, but aggregation policy is too narrow. |
| `current_vs_historical` | 39 | 16 | 38 | Currentness is often represented, but diary/current-window rendering needs policy. |
| `competing_semiologies` | 37 | 15 | 36 | Seizure-type scope is visible, but renderer policy must decide which type controls the label. |

Rows 190, 1694, and 15593 show the cluster problem. The model identified
cluster structure and per-cluster counts, but the renderer preferred safe
`unknown, ... per cluster` labels when the benchmark expected a combined cluster
cadence plus burden label. That is conservative and parseable, but incomplete.

Rows 13843, 14810, and 14821 show the seizure-free/currentness tension. The
model sometimes selected a seizure-free statement when the benchmark label was
a current frequency summary, or selected current spells when the benchmark
wanted a seizure-free duration. The schema has fields for this, but the
selection policy needs clearer precedence before projection.

Rows 3528 and 15986 show the danger of letting rate fields render too eagerly.
Row 3528 converted a vague increase into `multiple per day`; row 15986 rendered
month-specific counts as `1 to 5 per month` instead of aggregating the explicit
three-month total. Those are not parse failures; they are policy failures.

## Component Interpretation

The preferred RQ3 component is:

```text
exact evidence + rich typed selected state + deterministic renderer
```

The rejected component is:

```text
LLM direct final-label projection
```

The hard-panel run supports the bridge between those two:

- exact evidence alone is too shallow;
- a raw model label is too unsafe;
- the rich selected state preserves enough facts to let deterministic code
  abstain, render, or later apply benchmark-specific conventions.

The model should not be trusted to choose the final category by `state_kind`
alone. It should be trusted, conditionally, as a fact carrier when evidence is
exact and boundary validation passes.

## Claim Boundary

This is answered for validation-development hard-panel rows only. It does not
authorize holdout use, benchmark-comparable language, or whole-pipeline
promotion.

The hard-panel rows were chosen because they stress known failure families.
That is appropriate for component mechanism analysis and inappropriate for a
headline performance claim.

## Decision

Proceed with the rich selected-state architecture, but keep it behind
development gates:

1. Preserve `llm_only_rich_selected_state_reasoner` as the RQ3 state carrier.
2. Do not broaden to validation750 or holdout yet.
3. Add deterministic projection policies for:
   - cluster cadence plus per-cluster burden;
   - benchmark multiple conventions;
   - diary/log aggregation windows;
   - seizure-free versus current-frequency precedence;
   - vague increase or EEG/non-count phrases that must not render as rates.
4. Add consistency checks for suspicious combinations, especially
   `state_kind=frequency` plus fields that force `unknown`.

## Next Action

Write the RQ4/RQ5-facing deterministic projection-policy revision against the
saved hard-panel JSONL, using the same model outputs. The next experiment should
ask whether policy can consume the rich state better, not whether another live
LLM call can chase a higher score.
