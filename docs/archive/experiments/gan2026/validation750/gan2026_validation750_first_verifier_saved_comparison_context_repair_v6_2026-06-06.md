> **Superseded for navigation —** canonical summary: [`VALIDATION750_CANON.md`](../VALIDATION750_CANON.md). Full detail retained below.

# Gan 2026 Validation750 First Verifier Saved Comparison V6

saved validation-development verifier comparison packet only; no live verifier model call, no locked-test inspection, no benchmark-comparable claim, and no replacement scorer-facing label generation are authorized

## Decision

Prepared the predeclared saved verifier comparison packet over the V6 routed surface. The first score table remains the 29-row ambiguity set, with abstain, upstream-policy, rendered-policy, and provenance-only rows kept in separate appendices.

## Artifacts

- Row JSONL: `experiments\gan2026_validation750_first_verifier_saved_comparison_context_repair_v6_2026-06-06.jsonl`
- Summary JSON: `experiments\gan2026_validation750_first_verifier_saved_comparison_context_repair_v6_2026-06-06.json`
- Route source: `experiments\gan2026_validation750_verification_route_gpt41mini_context_repair_v6_2026-06-06.jsonl`
- Decision source: `experiments\gan2026_validation750_verification_decision_gpt41mini_context_repair_v6_2026-06-06.jsonl`
- Assessment source: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation750_gpt41mini_v3nested_v3_2026-06-06.jsonl`

## Bucket Counts

| Bucket | Rows |
| --- | ---: |
| Main ambiguity score table | 29 |
| Abstain appendix | 4 |
| Upstream-policy appendix | 18 |
| Rendered policy-sensitive appendix | 5 |
| Provenance-only audit appendix | 220 |

## Provenance Sidecars

- Clinical/policy rows: 56
- With provenance sidecar: 39
- Without provenance sidecar: 17

## Main Score Table Rows

| Row | Sidecar | Rendered label | Projection basis | Score status |
| ---: | --- | --- | --- | --- |
| 5551 | present | null | `frequency_rate` | `not_scored_null_rendered_label` |
| 5791 | present | null | `frequency_rate` | `not_scored_null_rendered_label` |
| 6209 | present | null | `frequency_rate` | `not_scored_null_rendered_label` |
| 6889 | present | null | `frequency_rate` | `not_scored_null_rendered_label` |
| 12127 | present | null | `frequency_rate` | `not_scored_null_rendered_label` |
| 12192 | present | null | `frequency_rate` | `not_scored_null_rendered_label` |
| 12236 | present | null | `frequency_rate` | `not_scored_null_rendered_label` |
| 12366 | present | null | `frequency_rate` | `not_scored_null_rendered_label` |
| 12378 | present | null | `frequency_rate` | `not_scored_null_rendered_label` |
| 12403 | absent | null | `frequency_rate` | `not_scored_null_rendered_label` |
| 12422 | present | null | `frequency_rate` | `not_scored_null_rendered_label` |
| 12456 | present | null | `frequency_rate` | `not_scored_null_rendered_label` |
| 12460 | present | null | `frequency_rate` | `not_scored_null_rendered_label` |
| 12484 | present | null | `frequency_rate` | `not_scored_null_rendered_label` |
| 12502 | present | null | `frequency_rate` | `not_scored_null_rendered_label` |
| 12506 | present | null | `frequency_rate` | `not_scored_null_rendered_label` |
| 12537 | present | null | `frequency_rate` | `not_scored_null_rendered_label` |
| 12548 | present | null | `frequency_rate` | `not_scored_null_rendered_label` |
| 12551 | present | null | `frequency_rate` | `not_scored_null_rendered_label` |
| 12556 | present | null | `frequency_rate` | `not_scored_null_rendered_label` |
| 12562 | present | null | `frequency_rate` | `not_scored_null_rendered_label` |
| 12573 | present | null | `frequency_rate` | `not_scored_null_rendered_label` |
| 12584 | present | null | `frequency_rate` | `not_scored_null_rendered_label` |
| 12641 | present | null | `frequency_rate` | `not_scored_null_rendered_label` |
| 12676 | present | null | `frequency_rate` | `not_scored_null_rendered_label` |
| 12679 | present | null | `frequency_rate` | `not_scored_null_rendered_label` |
| 12749 | present | null | `frequency_rate` | `not_scored_null_rendered_label` |
| 12751 | present | null | `frequency_rate` | `not_scored_null_rendered_label` |
| 12823 | present | null | `frequency_rate` | `not_scored_null_rendered_label` |

## Packet Contract

Each saved row packet includes:

- deterministic `VerificationDecision` V0 baseline action and reasons
- embedded `Verification Route` with route families, reasons, and route evidence
- clinical-assessment state
- projection/render state
- row-local candidate evidence texts, candidate ids, and source ids
- visible provenance sidecars when present on clinical/policy rows

The model-visible packet excludes gold labels, correctness fields, and other score-derived hints.
