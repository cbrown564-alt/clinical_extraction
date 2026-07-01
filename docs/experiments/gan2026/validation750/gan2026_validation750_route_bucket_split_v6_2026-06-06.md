> **Superseded for navigation —** canonical summary: [`VALIDATION750_CANON.md`](../VALIDATION750_CANON.md). Full detail retained below.

# Gan 2026 Validation750 Route Bucket Split V6

Date: 2026-06-06

Scope: bucket the routed rows in
`experiments/gan2026_validation750_verification_route_gpt41mini_context_repair_v6_2026-06-06.jsonl`
into verifier-relevant clinical/policy routes versus provenance-audit routes.

This is a validation-development mechanics read. It does not authorize locked
test use, benchmark-comparable language, or verifier promotion.

## Later Update: bucket contract stayed useful after provenance repair

This note remains the correct split for the original V6 route artifact and for
the logic behind the first verifier report shape.

Later provenance work changed the residual state:

- the candidate-trace replay collapsed the large
  `selected_evidence_missing_exact_trace` surface
- the later source-id repair removed the candidate-trace
  `selected_source_id_invalid` residual tail

So the exact historical counts below should be read as the original V6 route
snapshot, not as the current repaired candidate-trace surface.

What remains current is the operational principle:

- keep provenance-only audit rows out of the first verifier main table
- keep the clinically/policy-routed rows as the primary verifier action surface

## Source Artifact

- Route JSONL:
  `experiments/gan2026_validation750_verification_route_gpt41mini_context_repair_v6_2026-06-06.jsonl`

## Bucket Definition

Rows were split into four practical buckets:

1. `provenance_audit_rendered`
   Route families are only provenance families
   (`selected_evidence_missing_exact_trace`,
   `selected_source_id_invalid`) and a rendered label exists.
2. `provenance_audit_null`
   Route families are only provenance families and the rendered label is null.
3. `clinical_or_policy_null`
   At least one non-provenance route family is present and the rendered label is
   null.
4. `clinical_or_policy_rendered`
   At least one non-provenance route family is present and a rendered label
   exists.

## Bucket Counts

| Bucket | Rows |
| --- | ---: |
| `provenance_audit_rendered` | 172 |
| `provenance_audit_null` | 48 |
| `clinical_or_policy_null` | 51 |
| `clinical_or_policy_rendered` | 5 |
| total routed rows | 276 |

## Practical Interpretation

### 1. Provenance-audit-only rows dominate

`220 / 276` routed rows are provenance-only:

- `172` already have rendered labels
- `48` are still null-rendered

These rows are important for auditability, but they are not the same surface as
the original clinical/policy ambiguity tail. They should not silently redefine
the first LLM-verifier comparison set.

Representative rendered provenance-audit rows:

- row 10: `≤ four seizures per day` -> `4 per day`
- row 79: `≤ 6 to 7 seizures per year` -> `6 to 7 per year`
- row 1223: `3 or 4 ... this week` -> `3 to 4 per week`
- row 1486: `three focal seizures in last month` -> `3 per month`

These look clinically/projectively serviceable and are routed because the
selected-evidence trace contract is not exact enough, not because the clinical
burden is inherently unresolved.

### 2. The core verifier surface is much smaller

The clinically or policy-sensitive route surface is `56 / 276` rows:

- `51` clinical/policy null rows
- `5` clinical/policy rendered rows

This is the right candidate surface for the first verifier/action-policy read,
subject to one additional decision about whether provenance-mixed rows should
stay in or be split again.

### 3. Provenance and clinical ambiguity sometimes co-occur

`37` of the `51` clinical/policy null rows also carry
`selected_evidence_missing_exact_trace`.

Examples:

- row 1706:
  `selected_evidence_missing_exact_trace` + `cluster_axis_ambiguity`
- row 3356:
  `selected_evidence_missing_exact_trace` + `conditional_only_trigger`
- row 3512:
  `selected_evidence_missing_exact_trace` + `relative_only_trend`

So the useful next distinction is not just provenance versus non-provenance.
It is:

- provenance-only review
- clinical/policy ambiguity with provenance sidecar

## Route Families By Bucket

### `provenance_audit_rendered`

- `selected_evidence_missing_exact_trace`: 168
- `selected_source_id_invalid`: 4

### `provenance_audit_null`

- `selected_evidence_missing_exact_trace`: 43
- `selected_source_id_invalid`: 5

### `clinical_or_policy_null`

- `mixed_window_or_vague_addition`: 29
- `cluster_axis_ambiguity`: 13
- `cyclic_window_without_event_count`: 5
- `relative_only_trend`: 2
- `conditional_only_trigger`: 1
- `seizure_free_proxy_evidence_overreach`: 1

Also present as sidecars:

- `selected_evidence_missing_exact_trace`: 37

### `clinical_or_policy_rendered`

- `unresolved_cluster_cadence_with_per_cluster_burden`: 4
- `rendered_label_supported_but_policy_sensitive`: 1

Sidecar provenance appears on 2 of these 5 rows.

## Recommended Operational Split

For the next verifier planning step, use these working buckets:

1. **Primary verifier candidate surface**
   `clinical_or_policy_null` plus `clinical_or_policy_rendered`
   This is the real ambiguity and action-policy set.

2. **Provenance audit surface**
   `provenance_audit_rendered`
   These should be reviewed as exact-trace/instrumentation quality, not as a
   first-pass label/action ambiguity benchmark.

3. **Mixed null provenance surface**
   `provenance_audit_null`
   These are still null-rendered, but without a separate clinical/policy route
   family they look more like upstream instrumentation or phrase-selection
   cleanup than verifier-first work.

## Decision Boundary Suggested By V6

The first LLM-verifier comparison should not consume all 276 routed rows.

A cleaner first surface is:

- 56 clinically/policy-routed rows as the main action set
- provenance-only rows tracked separately as audit blockers or instrumentation
  debt

This preserves the reset architecture's intent:

- verifier work should address explicit ambiguity and action ownership
- provenance-only exact-trace insufficiency should remain visible without
  overwhelming the clinical route signal

## Next Step

Use the 56-row clinical/policy surface to:

1. prioritize the remaining cluster and mixed-window families
2. decide whether provenance sidecars stay attached to verifier prompts
3. keep provenance-only rows out of the first verifier success/failure table
