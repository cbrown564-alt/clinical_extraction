# Gan 2026 Structured Candidate Family Audit

Validation-development family audit over the structured candidate panel. Gold labels are used only for validation W->C/C->W accounting. No locked-test rows are read and no holdout-facing use is authorized.

## Decision

seed_slices_only_undercoverage

## Clean Seed Slices

| Slice | Value | Rows | W->C | C->W | Precision |
| --- | --- | ---: | ---: | ---: | ---: |
| `current_to_proposed_family` | `seizure_free->unknown` | 7 | 7 | 0 | 1.0000 |
| `current_to_proposed_family` | `yearly->daily` | 5 | 5 | 0 | 1.0000 |
| `current_to_proposed_family` | `monthly->cluster` | 3 | 2 | 0 | 1.0000 |
| `current_to_proposed_family` | `seizure_free->no_reference` | 2 | 2 | 0 | 1.0000 |
| `current_to_proposed_family` | `cluster->cluster` | 29 | 1 | 0 | 1.0000 |
| `current_to_proposed_family` | `other->cluster` | 2 | 1 | 0 | 1.0000 |

## Top Slices By W->C

| Slice | Value | Rows | W->C | C->W | Net | Precision |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `event_kind` | `frequency_rate` | 271 | 11 | 55 | -44 | 0.1667 |
| `current_family` | `seizure_free` | 89 | 10 | 1 | 9 | 0.9091 |
| `proposed_family` | `daily` | 67 | 8 | 13 | -5 | 0.3810 |
| `current_to_proposed_family` | `seizure_free->unknown` | 7 | 7 | 0 | 7 | 1.0000 |
| `proposed_family` | `unknown` | 59 | 7 | 15 | -8 | 0.3182 |
| `event_kind` | `unknown_frequency` | 62 | 7 | 16 | -9 | 0.3043 |
| `current_to_proposed_family` | `yearly->daily` | 5 | 5 | 0 | 5 | 1.0000 |
| `current_family` | `yearly` | 16 | 5 | 3 | 2 | 0.6250 |
| `current_family` | `other` | 161 | 5 | 71 | -66 | 0.0658 |
| `event_kind` | `cluster_frequency` | 35 | 4 | 1 | 3 | 0.8000 |
| `proposed_family` | `cluster` | 35 | 4 | 1 | 3 | 0.8000 |
| `event_kind` | `no_reference` | 55 | 3 | 14 | -11 | 0.1765 |
| `proposed_family` | `no_reference` | 55 | 3 | 14 | -11 | 0.1765 |
| `proposed_family` | `other` | 102 | 3 | 17 | -14 | 0.1500 |
| `current_to_proposed_family` | `monthly->cluster` | 3 | 2 | 0 | 2 | 1.0000 |
| `current_to_proposed_family` | `seizure_free->no_reference` | 2 | 2 | 0 | 2 | 1.0000 |
| `current_to_proposed_family` | `other->daily` | 8 | 2 | 6 | -4 | 0.2500 |
| `current_family` | `monthly` | 42 | 2 | 11 | -9 | 0.1538 |
| `current_to_proposed_family` | `cluster->cluster` | 29 | 1 | 0 | 1 | 1.0000 |
| `current_to_proposed_family` | `other->cluster` | 2 | 1 | 0 | 1 | 1.0000 |

## Interpretation

Use the clean seed slices only as mechanism probes, not holdout-ready policy. The largest clean slice is `current_to_proposed_family=seizure_free->unknown` with 7 W->C and 0 C->W, far below the 60 W->C gate; expand through structured event generation and matched controls before any frozen test audit.

## Artifacts

- Summary JSON: `experiments/gan2026_structured_candidate_event_contract_v0_direct_labeler_family_audit_2026-06-05.json`
- Source panel JSONL: `experiments/gan2026_structured_candidate_event_contract_v0_direct_labeler_validation750_panel_2026-06-05.jsonl`
