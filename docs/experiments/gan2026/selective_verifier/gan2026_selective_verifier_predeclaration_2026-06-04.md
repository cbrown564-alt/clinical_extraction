# Gan 2026 Selective Verifier Predeclaration

This is a pre-run validation-development contract for a selective LLM verifier. It materializes the stable suspicious slices from the saved selected-state routing artifact and does not make live model calls.

## Decision

Run a verifier only on exact-evidence suspicious rows. The predeclared surface contains 42 rows: 35 route-unknown rows and 7 route-review rows. The development-only accounting set includes 1 W->C and 6 C->W rows against the saved deterministic comparator.

## Claim Boundary

Validation-development verifier predeclaration only. No live model calls, locked-test inspection, whole-pipeline promotion, or benchmark-comparable claim are authorized.

## Eligibility Rule

Include saved suspicious selected-state rows routed to unknown or review only when selected evidence is an exact source substring. Exclude rows whose selected evidence is missing or non-exact from verifier calls.

## Allowed Recommendations

- `render_as_selected_state`
- `render_as_unknown`
- `abstain_review`
- `choose_listed_competing_hypothesis`

## Verifier Prompt Contract

You are a selective verifier for Gan 2026 seizure-frequency selected states. Use only the provided selected state, selected evidence, suspicious flags, deterministic label, and explicitly listed competing hypotheses. Do not infer new candidates from outside the provided evidence. Choose one allowed recommendation and return JSON matching the schema.

The verifier output must include `recommendation`, `recommended_label`, `chosen_competing_hypothesis`, `evidence_quotes`, `reason`, and `confidence`. Evidence quotes must be exact substrings from the provided selected evidence or competing-hypothesis text.

## Prompt Design Candidates

Two plain-language candidate designs are rendered into each row for offline inspection. They are not live-call results and are not prediction-bearing.

### `veto_first_safety_reviewer`

You are reviewing a proposed seizure-frequency answer. Use only the clinical text shown below. Decide whether the proposed answer is clearly supported. Mark the answer as unsafe if the text is vague, missing a clear count or timeframe, describes only one seizure type while another remains active, describes seizure freedom for only one seizure type, adds cluster details that are not clearly stated, or conflicts with another listed possibility. When in doubt, choose use_unknown or needs_review. Return only JSON matching the requested fields.

Output fields: `decision`, `blocking_issue`, `supporting_quotes`, `reason`, `confidence`.

### `support_parts_fact_check`

Check whether the proposed seizure-frequency answer is fully supported by the clinical text. A complete answer needs a seizure or event type, a count, a timeframe, and enough context to show it applies to the current highest seizure frequency. Do not fill in missing parts from assumptions. Return only JSON matching the requested fields.

Output fields: `seizure_or_event_type_supported`, `count_supported`, `timeframe_supported`, `current_highest_frequency_supported`, `all_required_parts_supported`, `recommended_action`, `missing_or_conflicting_parts`, `quotes`, `reason`.

## Artifacts

- Protocol: ``
- Verifier input JSONL: `experiments/gan2026_selective_verifier_predeclaration_2026-06-04.jsonl`
- Summary JSON: `experiments/gan2026_selective_verifier_predeclaration_2026-06-04.json`
- Source routing: `experiments/gan2026_suspicious_selected_state_routing_2026-06-04.jsonl`

## Metrics

| Metric | Value |
| --- | ---: |
| eligible verifier rows | 42 |
| route unknown rows | 35 |
| route review rows | 7 |
| w to c against comparator rows | 1 |
| c to w against comparator rows | 6 |
| routed to review rows | 7 |
| exact evidence rate | 1.000 |
| excluded non exact or missing evidence rows | 2 |

## Suspicious Flags

| Flag | Rows |
| --- | ---: |
| `denominator_window_mismatch` | 3 |
| `diary_log_date_list_without_defined_observation_window` | 4 |
| `frequency_with_count_blocking_ambiguity` | 29 |
| `frequency_with_exclusive_conditionality` | 5 |
| `seizure_free_non_all_type_scope_with_current_events` | 2 |
| `unresolved_cluster_cadence_with_per_cluster_burden` | 8 |
| `vague_trend_without_absolute_current_frequency` | 1 |

## Development Accounting Rule

The verifier can become prediction-bearing only if changed-decision precision is high and deterministic-correct regression count is zero or explicitly adjudicated before any further validation use.

The model input rows omit gold labels and W->C/C->W fields. Those fields remain in `development_accounting` for offline analysis after outputs are collected.
