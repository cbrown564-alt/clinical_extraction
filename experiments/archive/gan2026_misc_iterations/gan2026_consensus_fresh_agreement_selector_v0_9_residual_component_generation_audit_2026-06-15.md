# Gan 2026 Selector v0.9 Residual Component-Generation Audit

Date: 2026-06-15

This is a validation-only audit over saved v0.9 selector rows. It does not read locked test rows and does not make model calls.

## Summary

- Rows: 750
- Selected correct: 733/750
- Selected wrong: 17
- Selected-wrong rows with a correct unselected component: 6
- Selected-wrong rows with no correct component available: 11
- Selector-only oracle ceiling with current components: 739/750
- Residual selector-only headroom: 6 rows
- Residual component-generation required: 11 rows
- Selected wrong by band: `{'band_monthly': 3, 'band_submonthly': 2, 'band_unknown': 10, 'band_weekly': 2}`
- Selected wrong by component availability: `{'fresh_evidence': 5, 'none': 11, 'consensus+fresh_evidence': 1}`
- Selected wrong by category: `{'cluster_burden_component_failure': 2, 'consensus_fresh_correct_but_blocked': 1, 'fresh_only_correct_candidate': 5, 'highest_semiology_or_denominator_conflict': 3, 'last_event_or_seizure_free_overinfer_unknown': 7, 'unknown_over_quantified_rate': 7}`

## Component Availability

| Components correct but not selected | Rows |
| --- | ---: |
| `fresh_evidence` | 5 |
| `none` | 11 |
| `consensus+fresh_evidence` | 1 |

## Unknown-Frequency Residual

Yujian's clarification says unknown is usually safer when either the seizure count or the relevant time period is unclear. The v0.9 residual shows this is no longer mainly a selector problem: several unknown-boundary rows still have no Purist-correct available component because all sources over-infer from last-event, seizure-free, or underspecified recent-rate evidence.

The largest no-correct residual categories are:

| Category | Rows |
| --- | ---: |
| `cluster_burden_component_failure` | 2 |
| `highest_semiology_or_denominator_conflict` | 1 |
| `last_event_or_seizure_free_overinfer_unknown` | 6 |
| `unknown_over_quantified_rate` | 5 |

## Interpretation

v0.9 leaves 17 validation rows wrong. Only 6 are still selector-addressable with the current deterministic, consensus, and fresh-evidence outputs. Even an oracle selector over these three components would top out at 739/750.

The remaining 11 rows require better component generation. The highest-value next design should teach the component layer to preserve unknown when count/window is underspecified, avoid converting last-event-only evidence into seizure-free durations, and represent cluster burden when the gold label carries a cluster axis.

Decision: revise, not freeze. Continue development on validation component generation rather than adding selector micro-gates.
