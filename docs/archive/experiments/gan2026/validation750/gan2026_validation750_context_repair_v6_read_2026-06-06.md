> **Superseded for navigation —** canonical summary: [`VALIDATION750_CANON.md`](../VALIDATION750_CANON.md). Full detail retained below.

# Gan 2026 Validation750 Context Repair V6 Read

Date: 2026-06-06

Scope: no-call comparison between
`gan2026_clinical_assessment_projection_render_validation750_gpt41mini_context_repair_v5_2026-06-06.*`
and
`gan2026_clinical_assessment_projection_render_validation750_gpt41mini_context_repair_v6_2026-06-06.*`,
including downstream score, route, and deterministic verification-decision
artifacts.

This is validation-development mechanics work only. It is not a locked-test
read and does not authorize benchmark-comparable claims.

## Later Update: provenance route expansion was partially transient

This note remains the correct read of the original V5 versus V6 route expansion
on the original `context_repair_v6` artifacts. It should now be read together
with the later candidate-trace replay and the subsequent source-id repair.

Later state changes:

- candidate-trace provenance replay removed
  `selected_evidence_missing_exact_trace` as an active residual family on that
  replay
- the remaining candidate-trace `selected_source_id_invalid` tail was later
  repaired to `0`

What remains important from this note:

- V6 genuinely improved projection/render
- provenance visibility initially broadened the route surface sharply
- verifier-facing reporting needed to split clinical/policy ambiguity from
  provenance auditing

What is no longer current:

- treating the `selected_source_id_invalid` tail as an active remaining
  verifier-adjacent surface on the repaired candidate-trace replay

## Artifacts

- Projection/render V5:
  `experiments/gan2026_clinical_assessment_projection_render_validation750_gpt41mini_context_repair_v5_2026-06-06.jsonl`
- Projection/render V6:
  `experiments/gan2026_clinical_assessment_projection_render_validation750_gpt41mini_context_repair_v6_2026-06-06.jsonl`
- Score V5:
  `experiments/gan2026_clinical_assessment_projection_score_validation750_gpt41mini_context_repair_v5_2026-06-06.jsonl`
- Score V6:
  `experiments/gan2026_clinical_assessment_projection_score_validation750_gpt41mini_context_repair_v6_2026-06-06.jsonl`
- Route V5:
  `experiments/gan2026_validation750_verification_route_gpt41mini_context_repair_v5_2026-06-06.jsonl`
- Route V6:
  `experiments/gan2026_validation750_verification_route_gpt41mini_context_repair_v6_2026-06-06.jsonl`
- Decision V5:
  `experiments/gan2026_validation750_verification_decision_gpt41mini_context_repair_v5_2026-06-06.jsonl`
- Decision V6:
  `experiments/gan2026_validation750_verification_decision_gpt41mini_context_repair_v6_2026-06-06.jsonl`

## Top-Line Delta

| Surface | V5 | V6 | Delta |
| --- | ---: | ---: | ---: |
| rendered rows | 573 | 580 | +7 |
| null renders | 177 | 170 | -7 |
| scored rows | 573 | 580 | +7 |
| Purist-correct scored rows | 482 | 488 | +6 |
| Pragmatic-correct scored rows | 514 | 520 | +6 |
| exact normalized-label matches | 414 | 418 | +4 |
| routed rows | 49 | 276 | +227 |
| V0 `abstain` rows | 49 | 276 | +227 |

Bottom line: V6 is a real mechanical improvement on projection/render, but the
route surface broadened far more than the null-render surface. The broadening is
mostly provenance-driven rather than new clinical ambiguity.

## Recovered Rows

V6 recovered exactly 7 rows that were null-rendered in V5. There were no new
null-render rows, and no previously routed rows became unrouted.

Recovered source rows:

- 2609
- 4690
- 4694
- 4700
- 4709
- 6180
- 7409

All 7 recoveries were:

- `projection_rule_id = frequency_rate_values_v0`
- `render_basis = frequency_rate`
- V5 score status `not_scored_null_rendered_label`
- V6 score status `scored`
- V6 Purist result `True`

This is clean `W->C` recovery on the refreshed surface.

Representative recovered labels:

- 2609: `occurring once per night` -> `1 per day`
- 4690: `Electrographic seizures frequent on EEG (~ten/h)` -> `multiple per day`
- 4694: `Electrographic seizures frequent on EEG (~9/h)` -> `multiple per day`
- 4700: `Electrographic seizures frequent on EEG (~4/h)` -> `multiple per day`
- 4709: `Electrographic seizures frequent on EEG (~6/h)` -> `multiple per day`
- 6180: `brief staring spells ... on several occasions each week` -> `multiple per week`
- 7409: `focal aware seizures most weeks` -> `multiple per week`

Interpretation: the fresh gain came from exactly the intended frequency-family
ports: nightly cadence, per-hour normalization, and vague-with-explicit-period
recovery.

## Remaining Null Surface

The remaining 170 null renders are still concentrated in deterministic
normalization/projection gaps rather than verifier work.

Largest remaining projection issues on null rows:

- `seizure_free_duration_required`: 75
- `frequency_rate_values_incomplete`: 75
- `vague_count`: 58
- `frequency_rate_values_unparsed`: 48
- `additive_frequency_period_mismatch`: 28
- `seizure_free_duration_unparsed`: 27
- `seizure_free_since_date_anchor_unparsed`: 19
- `cluster_cadence_values_incomplete`: 18
- `cluster_frequency_values_unparsed`: 15

Interpretation:

1. The biggest unresolved family is still seizure-free duration/date handling.
2. Frequency has improved, but the residual tail is now the harder
   value-incomplete/value-unparsed slice rather than easy hourly or nightly
   phrases.
3. Additive and cluster families remain meaningful route-or-policy surfaces, not
   simple parser cleanup.

## Route Expansion

V6 routed 276 rows versus 49 in V5. The 227 newly routed rows break down as:

- `selected_evidence_missing_exact_trace`: 215
- `selected_source_id_invalid`: 9
- `unresolved_cluster_cadence_with_per_cluster_burden`: 4
- `relative_only_trend`: 2
- `conditional_only_trigger`: 1

This means the route expansion is overwhelmingly provenance-sensitive:

- 215 / 227 newly routed rows have
  `exact_trace=False | source_id_status=invalid`
- 9 / 227 have
  `exact_trace=True | source_id_status=invalid`
- only 3 newly routed rows have
  `exact_trace=True | source_id_status=valid`

Representative newly routed but otherwise strong rendered rows:

- row 10: `≤ four seizures per day` -> `4 per day`
- row 79: `≤ 6 to 7 seizures per year` -> `6 to 7 per year`
- row 1223: `3 or 4 ... this week` -> `3 to 4 per week`
- row 1486: `three focal seizures in last month` -> `3 per month`
- row 2932: `seizure-free since 29/09/2017` -> `seizure free for 9 month`

These rows are not the same kind of problem as the original null-render risk
surface. They are clinically/projectively serviceable labels that are now being
routed because the selected-evidence provenance contract is stricter and more
visible.

## What Changed In The Verifier Surface

### Stable, intended route families

These still look like real verifier or action-policy inputs:

- `mixed_window_or_vague_addition`
- `cluster_axis_ambiguity`
- `cyclic_window_without_event_count`
- `unresolved_cluster_cadence_with_per_cluster_burden`
- `relative_only_trend`
- `conditional_only_trigger`
- `seizure_free_proxy_evidence_overreach`

### Newly dominant provenance families

These need a deliberate policy decision before being treated as first-pass LLM
verifier work:

- `selected_evidence_missing_exact_trace`
- `selected_source_id_invalid`

Current evidence suggests these families are closer to instrumentation/provenance
auditing than to clinical ambiguity adjudication. They can still be routed, but
they should probably be reported separately from the core null-render verifier
surface.

## Comparison To V5 Working Read

V5 already reduced null renders materially, and V6 continued that direction
without introducing any new null rows. The important new development is not the
7 recovered rows by itself; it is that route now exposes a second class of
review surface:

1. null-render clinical/policy ambiguity
2. provenance-trace insufficiency on otherwise renderable labels

That distinction should be made explicit in subsequent reports and verifier
predeclarations.

## Recommended Next Move

1. Keep the 7 V6 recovered rows as accepted deterministic gains.
2. Treat the remaining 170 null rows as the true residual normalization and
   projection surface.
3. Split route reporting into at least two buckets:
   - clinical/policy ambiguity routes
   - provenance/exact-trace routes
4. Do not let the 215 `selected_evidence_missing_exact_trace` rows silently
   redefine the first LLM-verifier evaluation surface.
5. Historical next steps from the time of this read were:
   - refreshed residual null-render family read from V6
   - explicit adjudication of provenance-route policy
   - cluster-family pass on the still-null or still-routed cluster rows

Current follow-through:

- provenance-route policy was adjudicated by splitting provenance-only rows out
  of the first verifier main table
- the action-only verifier path is now the primary protocol
- the candidate-trace `selected_source_id_invalid` tail is no longer active

## Practical Thesis After V6

The reset is still moving in the right direction:

- fewer nulls;
- real deterministic `W->C` recovery;
- clearer issue ownership.

But V6 also shows that improved provenance visibility can expand the route
surface faster than clinical ambiguity shrinks. That is useful progress, as long
as provenance-route broadening is kept analytically distinct from the core
verifier target surface.
