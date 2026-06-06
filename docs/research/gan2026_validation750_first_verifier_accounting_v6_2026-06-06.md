# Gan 2026 First Verifier Post-Run Accounting V6

validation-development first action-only verifier comparison/accounting against deterministic V0.

## Summary

- Source verifier live run: `experiments\gan2026_validation750_first_verifier_live_clean29_context_repair_v6_2026-06-06.jsonl`
- Output JSON data: `experiments\gan2026_validation750_first_verifier_accounting_v6_2026-06-06.json`
- Total rows processed: 56

## Accounting By Route Bucket

### Bucket: `abstain_exemplar`

| V0 Baseline Action | Verifier Action | Count |
| --- | --- | ---: |
| `abstain` | `abstain` | 3 |
| `abstain` | `human_review` | 1 |

### Bucket: `rendered_policy_sensitive_appendix`

| V0 Baseline Action | Verifier Action | Count |
| --- | --- | ---: |
| `abstain` | `abstain` | 1 |
| `abstain` | `affirm` | 4 |

### Bucket: `upstream_policy_appendix`

| V0 Baseline Action | Verifier Action | Count |
| --- | --- | ---: |
| `abstain` | `abstain` | 17 |
| `abstain` | `human_review` | 1 |

### Bucket: `verifier_eligible_ambiguity`

| V0 Baseline Action | Verifier Action | Count |
| --- | --- | ---: |
| `abstain` | `abstain` | 8 |
| `abstain` | `affirm` | 1 |
| `abstain` | `human_review` | 15 |
| `abstain` | `reject` | 5 |

## Accounting By Report Section

### Section: `abstain_exemplar_appendix`

| V0 Baseline Action | Verifier Action | Count |
| --- | --- | ---: |
| `abstain` | `abstain` | 3 |
| `abstain` | `human_review` | 1 |

### Section: `main_ambiguity_score_table`

| V0 Baseline Action | Verifier Action | Count |
| --- | --- | ---: |
| `abstain` | `abstain` | 8 |
| `abstain` | `affirm` | 1 |
| `abstain` | `human_review` | 15 |
| `abstain` | `reject` | 5 |

### Section: `rendered_policy_sensitive_appendix`

| V0 Baseline Action | Verifier Action | Count |
| --- | --- | ---: |
| `abstain` | `abstain` | 1 |
| `abstain` | `affirm` | 4 |

### Section: `upstream_policy_appendix`

| V0 Baseline Action | Verifier Action | Count |
| --- | --- | ---: |
| `abstain` | `abstain` | 17 |
| `abstain` | `human_review` | 1 |
