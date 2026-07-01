> **Superseded for navigation —** canonical summary: [`VALIDATION750_CANON.md`](../VALIDATION750_CANON.md). Full detail retained below.

# Gan 2026 Validation750 Verifier Candidate Surface V6

Date: 2026-06-06

Scope: define the primary verifier-candidate surface from
`gan2026_validation750_verification_route_gpt41mini_context_repair_v6_2026-06-06.jsonl`
after excluding provenance-only routed rows.

This is validation-development mechanics work only. It does not authorize
locked-test inspection, benchmark-comparable language, or LLM-verifier
promotion.

## Decision

Use the 56-row clinical/policy routed surface as the first verifier-candidate
set.

Keep provenance-only routed rows out of the first verifier success/failure
table:

- provenance-only routed rows: `220`
- clinical/policy routed rows: `56`

Within the 56-row clinical/policy surface, keep provenance sidecars visible but
secondary:

- rows with provenance sidecar: `39`
- rows without provenance sidecar: `17`

The verifier surface should therefore be interpreted as:

1. primary action/policy ambiguity rows
2. some of those rows also carry trace-quality concerns

It should not be interpreted as an exact-trace audit benchmark.

Decision for the first verifier prompt:

- provenance sidecars stay visible on the 39 mixed clinical/policy rows
- they are secondary audit context, not the primary target of success/failure
- provenance-only routed rows remain outside the first verifier score table

## Surface Summary

Top-line split:

- total clinical/policy rows: `56`
- null-render rows: `51`
- rendered rows: `5`

Non-provenance route-family counts:

- `mixed_window_or_vague_addition`: `29`
- `cluster_axis_ambiguity`: `13`
- `cyclic_window_without_event_count`: `5`
- `unresolved_cluster_cadence_with_per_cluster_burden`: `4`
- `relative_only_trend`: `2`
- `conditional_only_trigger`: `1`
- `seizure_free_proxy_evidence_overreach`: `1`
- `rendered_label_supported_but_policy_sensitive`: `1`

## Operational Tiers

### Tier 1: Null ambiguity/action rows: 51

This is the main first-pass verifier/action-policy surface.

Family counts:

- `mixed_window_or_vague_addition`: `29`
- `cluster_axis_ambiguity`: `13`
- `cyclic_window_without_event_count`: `5`
- `relative_only_trend`: `2`
- `conditional_only_trigger`: `1`
- `seizure_free_proxy_evidence_overreach`: `1`

Interpretation:

- These are the rows where projection currently declines to emit a label.
- The key question is not "can a regex recover this?"
- The key question is "which of these are clinically unknown, abstain,
  human-review, missing upstream policy, or verifier-eligible ambiguity?"

### Tier 2: Rendered but policy-sensitive rows: 5

These should stay in the verifier candidate report, but as a separate rendered
bucket rather than the main null tail.

Rows:

- `1317`: `unknown, multiple per cluster`
- `7141`: `unknown, multiple per cluster`
- `7785`: `seizure free for 12 month`
- `10189`: `unknown, multiple per cluster`
- `10200`: `unknown, multiple per cluster`

Important note:

- all 5 are already scored Purist-correct on the current validation surface
- 4 of 5 are cluster convention rows that remain routed because cadence
  ownership is unresolved, not because the rendered label is obviously wrong

Interpretation:

- These rows are useful for verifier-policy design, especially "affirm versus
  abstain versus human review" behavior on already-rendered states.
- They should not be mixed into the null-render recovery accounting.

## Family Reads

### 1. `mixed_window_or_vague_addition`: 29 rows

Row ids:

- `5551`
- `5791`
- `6209`
- `6889`
- `12127`
- `12192`
- `12236`
- `12366`
- `12378`
- `12403`
- `12422`
- `12456`
- `12460`
- `12484`
- `12502`
- `12506`
- `12537`
- `12548`
- `12551`
- `12556`
- `12562`
- `12573`
- `12584`
- `12641`
- `12676`
- `12679`
- `12749`
- `12751`
- `12823`

Read:

- This is the largest family by far.
- These rows combine burdens across windows, semiologies, or vague summary
  forms that the reset correctly refuses to collapse automatically.
- This family is the strongest single target for the null-render/action
  taxonomy.

### 2. `cluster_axis_ambiguity`: 13 rows

Row ids:

- `1706`
- `6501`
- `9879`
- `9937`
- `10434`
- `10542`
- `10578`
- `10630`
- `15242`
- `15262`
- `16757`
- `16839`
- `16907`

Read:

- The dedicated cluster-family pass already shows these are mostly contract
  questions, not safe parser misses.
- They should remain visible as a distinct verifier slice rather than being
  folded into a general null bucket.

Reference:

- ``

### 3. `cyclic_window_without_event_count`: 5 rows

Row ids:

- `3468`
- `3469`
- `3482`
- `3493`
- `10509`

Read:

- These are timing-window or trigger rows without an owned denominator.
- They look like policy or abstention cases, not straightforward rendering
  misses.

### 4. `unresolved_cluster_cadence_with_per_cluster_burden`: 4 rows

Row ids:

- `1317`
- `7141`
- `10189`
- `10200`

Read:

- All 4 already render `unknown, multiple per cluster`.
- All 4 are Purist-correct and Pragmatic-correct on the current scored surface.
- These are best treated as rendered policy-sensitive verifier rows, not null
  recovery rows.

### 5. Small singleton/two-row families: 4 rows

`relative_only_trend`:

- `3507`
- `3512`

`conditional_only_trigger`:

- `3356`

`seizure_free_proxy_evidence_overreach`:

- `3534`

`rendered_label_supported_but_policy_sensitive`:

- `7785`

Read:

- These are small in count but important for action-policy semantics.
- They are good candidates for explicit verifier prompt examples because each
  family represents a distinct decision boundary.

## Recommended First Verifier Read

If the team wants one practical verifier report instead of several competing
surfaces, use this split:

1. **Main null action set**
   51 rows
2. **Rendered policy-sensitive set**
   5 rows
3. **Provenance-only audit set**
   keep separate; do not include in first verifier score table

For the 56-row main report, keep these columns visible:

- source row id
- non-provenance route family
- provenance sidecar present or absent
- rendered label
- normalized source phrase
- projection basis
- score status

For the first verifier prompt, include provenance sidecar fields when present:

- provenance-sidecar present or absent
- `selected_evidence_missing_exact_trace` when present
- `selected_source_id_invalid` when present

But do not let provenance sidecars redefine the decision objective. The primary
verifier task remains action over the non-provenance route family and the
current rendered/null state.

## Recommendation

Treat the verifier-candidate surface definition as complete for `context_repair_v6`.

The next deterministic step should be the null-render/action taxonomy over the
51 null rows, with the 5 rendered policy-sensitive rows kept as a separate
action-policy appendix.

Later protocol decision:

- keep the full clean `56`-row surface as the broad saved comparison packet
- for the next prompt/policy-tightening iteration, temporarily concentrate on
  the `29`-row `mixed_window_or_vague_addition` main ambiguity table
- return to the full `56`-row surface after the
  `affirm`/`reject`/`human_review`/`abstain` boundary is more stable
