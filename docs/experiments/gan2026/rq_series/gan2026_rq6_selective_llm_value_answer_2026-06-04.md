> **Superseded for navigation —** canonical summary: [`COMPONENT_MECHANICS_CANON.md`](../COMPONENT_MECHANICS_CANON.md). Full detail retained below.

# Gan 2026 RQ6 Selective LLM Value Answer

Date: 2026-06-04

Status: final validation-development answer with one frozen local
generalization audit. This is not an LLM-first, production, or
benchmark-comparable claim.

## Answer

RQ6 is answered for the current evidence base:

```text
The LLM adds reliable value only as a small, exact-evidence, no-regression
selective intervention behind a deterministic safety floor. Broad LLM
replacement and broad LLM/graph projection remain rejected.
```

The strongest artifact is `selective_safety_floor_gate_v0`. It combines a
gated projection layer and an LLM candidate sidecar, then preserves the
deterministic comparator unless a predeclared gate fires with exact evidence and
valid source ids.

On validation750, the final selective gate changes 21 rows, with 11
wrong-to-correct, 0 correct-to-wrong, 21/21 exact changed-row evidence, and
21/21 valid source ids. On the frozen local test450 audit, it changes 14 rows,
with 8 wrong-to-correct, 0 correct-to-wrong, 14/14 exact changed-row evidence,
and 14/14 valid source ids.

## Claim Boundary

Supporting artifacts:

- `experiments/gan2026_selective_safety_floor_gate_v0_component_evidence_audit_2026-06-03.md`
- `experiments/gan2026_selective_safety_floor_gate_v0_validation750_replay_2026-06-03.md`
- `experiments/gan2026_selective_safety_floor_gate_v0_test450_frozen_audit_first_readout_2026-06-03.md`
- ``
- `docs/design/component_evidence_attribution_architecture.md`

The frozen test readout was aggregate and predeclared-slice only. It suppresses
locked-test row-level details and must not be used for tuning. The result is a
local frozen generalization audit for this named hybrid safety-floor policy,
not a benchmark-comparable result.

## Component Trade-Offs

| Component | Surface | Changed | W->C | C->W | Precision | Interpretation |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `selective_safety_floor_gate_v0` | validation750 | 21 | 11 | 0 | 1.0000 | Strong validation selective-action answer. |
| `selective_safety_floor_gate_v0` | test450 frozen audit | 14 | 8 | 0 | 0.8889 | Strong local generalization audit, no row-level tuning. |
| `projection_boundary_state_priority_gate_v0` | test450 frozen audit | 9 | 6 | 0 | 1.0000 | Best high-precision projection gate. |
| `llm_candidate_sidecar_rescue_gate_v0` | test450 frozen audit | 6 | 3 | 0 | 0.7500 | Real LLM value, but smaller and less precise. |
| `competing_frequency_uncertainty` | test450 frozen audit | 82 | 2 | 67 | 0.0270 | Rejected broad projection policy. |
| `lowest_current_frequency` | test450 frozen audit | 77 | 6 | 50 | 0.1071 | Rejected broad projection policy. |

The sidecar value is real but should not be overstated. The final candidate is
hybrid because graph projection, deterministic safety-floor fallback, and the
LLM sidecar all contribute semantic behavior.

## Deterministic Baseline Role

The deterministic safety floor is the fixed comparator and regression shield.
RQ6 does not show that the LLM should replace deterministic rules. It shows
that exact-evidence LLM or graph-derived changes can be allowed only when they
pass a predeclared selective gate and preserve zero deterministic-correct
regressions.

## Hidden-Family Readout

Validation changed-row gains concentrate in uncertainty boundary,
seizure-free duration, current-vs-historical, and competing-semiology rows.
Frozen-test interpretation must stay at the predeclared slice level:

- `projection_gate:fired`: 9 changed, 6 W->C, 0 C->W.
- `llm_sidecar_gate:fired`: 6 changed, 3 W->C, 0 C->W.
- `gold_kind:unknown`: 3 changed, 2 W->C, 0 C->W.
- `gold_kind:unresolved_multiple`: 4 changed, 3 W->C, 0 C->W.
- `gold_kind:seizure_free`: 3 changed, 2 W->C, 0 C->W.
- `text_marker:cluster_language`: 9 changed, 5 W->C, 0 C->W.

Rate/frequency rows are weaker on the frozen audit: `gold_kind:frequency`
changed 4 rows with 1 W->C and 0 C->W. That slice should not be expanded
without a new predeclared gate.

## Transfer Confidence

| Finding | Development confidence | Holdout-transfer confidence | Reason |
| --- | --- | --- | --- |
| Selective safety-floor action is the safest current LLM-value pattern. | High | Moderate | It preserved zero C->W in validation and the frozen local audit. |
| LLM sidecar rescue has real but limited value. | Moderate | Low-to-moderate | Test450 sidecar precision is 0.7500 and depends on the safety floor. |
| Broad LLM or graph replacement is unsafe. | High | Moderate-to-high | Negative controls have severe C->W regressions. |
| Frequency/rate selective gains are weaker than boundary gains. | High | Moderate | Frozen audit precision is lower on `gold_kind:frequency`. |

## Metadata/Instrumentation Gaps

- Frozen-test hidden-family tags are not exposed beyond predeclared
  slices/markers.
- Residual frozen-test misses do not have row-level first-failure ownership in
  the public first readout.
- The sidecar is not an LLM-superiority claim because final safety depends on
  deterministic fallback and graph projection.

## Decision

RQ6 is answered:

- Accept selective no-regression LLM value behind a deterministic safety floor.
- Credit `selective_safety_floor_gate_v0` as a hybrid local frozen-audit result,
  not as an LLM-first result.
- Reject broad LLM label replacement and broad graph/LLM projection as
  reliable selective-action mechanisms.
- Require exact evidence, valid source ids, W->C/C->W accounting, and
  deterministic-correct regression accounting for every future label-changing
  LLM action.

## Next Action

Do not run another broad validation F1 experiment for RQ6. If selective action
is extended, predeclare a narrower gate for the weak frequency/rate or
cluster/convention slices and require the same no-regression accounting before
any holdout-facing use.
