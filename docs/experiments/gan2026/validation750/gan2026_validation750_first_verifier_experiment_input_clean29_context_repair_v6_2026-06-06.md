# Gan 2026 Validation750 First Verifier Experiment Input Clean29 V6

First verifier experiment input surface only: 29-row ambiguity core plus abstain/upstream-policy/rendered-policy appendices. Provenance-only audit rows, gold labels, correctness fields, and audit W->C/C->W counts are excluded from verifier-visible inputs.

## Decision

`ready_for_first_verifier_run`

## Artifacts

- Row JSONL: `experiments\gan2026_validation750_first_verifier_experiment_input_clean29_context_repair_v6_2026-06-06.jsonl`
- Summary JSON: `experiments\gan2026_validation750_first_verifier_experiment_input_clean29_context_repair_v6_2026-06-06.json`

## Surface

| Section | Rows |
| --- | ---: |
| Main ambiguity core | 29 |
| Abstain appendix | 4 |
| Upstream-policy appendix | 18 |
| Rendered policy-sensitive appendix | 5 |
| Provenance-only audit rows excluded | 220 |

## Input Hygiene

Verifier-visible packets contain route, assessment, projection/render, candidate evidence, and provenance sidecars only. Gold labels, score correctness fields, and audit-only W->C/C->W counts are deliberately absent.
