# Gan 2026 RQ8 Efficiency And Operational Reliability Answer

Date: 2026-06-04

Status: answered for saved-artifact operational reliability and complexity.
Token, latency, retry, and cost-per-1,000-note claims remain blocked by missing
telemetry.

## Answer

RQ8 is answered with a bounded result:

```text
The operationally preferred architecture uses narrow extractive LLM components
and deterministic rendering/policy. Deep schemas and all-in-one prompts are
operationally inferior because they add burden, reduce evidence/source-id
quality, or duplicate decision ownership without solving projection.
```

The cheapest reliable primitive in the saved artifacts is
`candidate_conditioned_evidence_only`: it has 0 parse failures, valid source ids
on all rows, exact evidence on 47/50 balanced rows and 73/75 hard-panel rows,
and about one evidence span per row.

The best broad evidence locator is `gold_query_evidence_only`: it also has 0
parse failures and valid source ids on all rows, with exact evidence on 47/50
balanced and 69/75 hard-panel rows, but its burden is higher at 2.52 and 3.213
evidence spans per row.

The useful candidate proposer is selective rather than broad:
`selective_boundary_candidate_proposer_v2` has 21/22 parseable rows, 21/22 rows
with all retained evidence exact, 16/22 exact-label candidate recall, and 20/22
Purist-category candidate recall, but candidate burden is higher at 3.227
retained candidates per row.

The preferred state carrier remains `rich_selected_state_v0`, not because it is
cheaply final-label accurate, but because it is structurally reliable: 75/75
structured records, 75/75 parseable deterministic projected labels, and 3
evidence/trace boundary-error rows. It still requires deterministic consistency
checks because it overuses broad `state_kind=frequency`.

The rejected operational patterns are now clear:

- `candidate_plus_evidence_plus_projection` keeps parsing but drops exact
  evidence to 35/50 balanced and 52/75 hard rows, with valid source ids only
  0.72 and 0.76.
- `projection_only` and instruction-heavy projection parse but do not provide
  evidence/source grounding and remain unreliable as final-label components.
- `typed_operations_v0` is the negative control: 247/250 structured records and
  235/250 selected-evidence-valid rows are not enough to justify the schema.
  Even with max_tokens=10000, graph projection drops from 216/250 selected-
  evidence arithmetic Purist correctness to 208/250, with 15 selected-evidence
  correct to graph-wrong regressions and only 7 graph rescues.

## Claim Boundary

Supporting artifacts:

- `experiments/gan2026_rq8_operational_matrix_2026-06-04.json`
- `experiments/gan2026_rq8_operational_matrix_2026-06-04.md`
- `experiments/gan2026_rq1_rq2_component_control_matrix_2026-06-04.*`
- `experiments/gan2026_selective_boundary_candidate_experiment_v2_2026-06-04.*`
- `experiments/gan2026_rich_selected_state_hard_panel_2026-06-04.*`
- `experiments/gan2026_llm_only_typed_operations_reasoner_validation250_gpt41mini_v0_contractfix_max10000_2026-06-03.*`
- `experiments/gan2026_selective_safety_floor_gate_v0_validation750_replay_2026-06-03.*`
- `experiments/gan2026_selective_safety_floor_gate_v0_test450_frozen_audit_first_readout_2026-06-03.*`

This is a validation-development and saved-replay operational answer. It does
not make a benchmark-comparable claim. It does not add new model calls. It does
not inspect locked-test row-level failures.

## Operational Matrix Summary

| Component | Surface | Parse/schema failures | Exact evidence | Source ids | Burden / action |
| --- | --- | ---: | ---: | ---: | --- |
| `candidate_conditioned_evidence_only` | balanced50 | 0/50 | 0.9400 | 1.0000 | 1.02 spans/row |
| `candidate_conditioned_evidence_only` | hard75 | 0/75 | 0.9733 | 1.0000 | 1.013 spans/row |
| `gold_query_evidence_only` | balanced50 | 0/50 | 0.9400 | 1.0000 | 2.52 spans/row |
| `gold_query_evidence_only` | hard75 | 0/75 | 0.9200 | 1.0000 | 3.213 spans/row |
| `candidate_only` | balanced50 | 0/50 | 0.9400 | 0.8400 | 1.20 candidates/row |
| `candidate_only` | hard75 | 0/75 | 0.8933 | 0.9200 | 1.68 candidates/row |
| `candidate_plus_evidence_plus_projection` | balanced50 | 0/50 | 0.7000 | 0.7200 | projection label rate 0.1000 |
| `candidate_plus_evidence_plus_projection` | hard75 | 0/75 | 0.6933 | 0.7600 | projection label rate 0.1333 |
| `selective_boundary_candidate_proposer_v2` | rescue22 | 1/22 | 0.9545 | not materialized | 3.227 candidates/row |
| `rich_selected_state_v0` | hard75 | 3 boundary/trace errors | 0.9600 | not materialized | 75/75 structured |
| `typed_operations_v0` | validation250 | 3/250 | 0.9400 | not materialized | max_tokens=10000, graph delta -8 |
| `selective_safety_floor_gate_v0` | validation750 | 0/750 | 1.0000 | 1.0000 | 21 changed, 11 W->C, 0 C->W |
| `selective_safety_floor_gate_v0` | test450 frozen | 0/450 | 1.0000 | 1.0000 | 14 changed, 8 W->C, 0 C->W |

## Cost And Latency Boundary

The saved artifacts do not uniformly preserve prompt tokens, completion tokens,
wall-clock latency, retry counts, or cost. RQ8 therefore cannot honestly answer
which surviving component is cheapest per 1,000 notes in dollars or seconds.

That missing telemetry does not change the architecture choice yet because the
available reliability signals are decisive:

- narrow evidence prompts preserve exactness and source ids;
- broad bundled prompts reduce grounding quality;
- deep typed operations add complexity and negative projection delta;
- no-call selective safety-floor replay is operationally cheap after saved
  source artifacts exist.

If a future paper table needs true dollars or runtime, run a small frozen
telemetry pass over the surviving primitives only.

## Decision

RQ8 is answered for operational reliability and implementation complexity:

- Promote `candidate_conditioned_evidence_only` as the default evidence gate.
- Use `gold_query_evidence_only` only when broader evidence context is needed
  and the higher span burden is acceptable.
- Use selective candidate proposal only on named boundary/ambiguity slices.
- Carry `rich_selected_state_v0` forward as the fact/state representation, but
  require deterministic consistency checks and projection policy.
- Keep `selective_safety_floor_gate_v0` as the reliable action pattern.
- Reject all-in-one prompts and `typed_operations_v0` for the next architecture.

## Architecture Guidance

The ideal architecture after RQ1-RQ8 is:

```text
deterministic/state-graph substrate
  + selective LLM boundary candidate proposer
  + candidate-conditioned LLM evidence gate
  + rich selected-state fact carrier
  + deterministic consistency checks
  + gated deterministic projection/rendering
  + selective safety floor
  + abstain/review/monitoring policy
```

This keeps the LLM on source-grounded candidate/evidence/fact-carrying work and
keeps benchmark-facing projection, rendering, abstention, and regression
control in explicit policy layers.

## Next Action

Do not run a new broad validation experiment. Build the RQ7 family-indexed
component matrix over the now-surviving architecture components, or run a small
telemetry-only RQ8 follow-up if cost/latency numbers are required for a paper
table.
