# Authored patient 012: Laura Chen

Status: AI-authored fictional development example, version 0.2.
Challenge focus: Ambiguous semiology with unresolved diagnostic classification (epilepsy vs migraine aura).
No real patient, source seed, paid model call, independent annotation or clinical review.
Implements P2.5 against [task definition v0.2](../../../docs/longitudinal/task_definition.md).

## Clinical Persona & Story

Laura Chen is a fictional 28-year-old outpatient.
Ambiguous semiology with unresolved diagnostic classification (epilepsy vs migraine aura).

| Letter | Consultation | Available to system | Contents |
| --- | --- | --- | --- |
| L1 | 2025-03-05 | 2025-03-05 | Initial consultation record. |
| L2 | 2025-07-16 | 2025-07-16 | Second consultation record. |
| L3 | 2025-11-14 | 2025-11-14 | Third consultation record. |

## Requests and Allowed Inputs

Indices are fixed 180 days apart; each retrospective cutoff is T + 180 days.

| Index/view | Index date | Information cutoff | Included letters |
| --- | --- | --- | --- |
| T1_visit | 2025-03-05 | 2025-03-05 | L1 |
| T1_retrospective | 2025-03-05 | 2025-09-01 | L1, L2 |
| T2_visit | 2025-09-01 | 2025-09-01 | L1, L2 |
| T2_retrospective | 2025-09-01 | 2026-02-28 | L1, L2, L3 |

## Expected Answers (20 Queries)

| Query | T1 visit | T1 retrospective | T2 visit | T2 retrospective |
| --- | --- | --- | --- | --- |
| Q1 | indeterminate | indeterminate | indeterminate | indeterminate |
| Q2 | indeterminate | indeterminate | indeterminate | indeterminate |
| Q3 | indeterminate | indeterminate | indeterminate | indeterminate |
| Q4 | indeterminate | indeterminate | indeterminate | indeterminate |
| Q5 | indeterminate | indeterminate | indeterminate | indeterminate |

## Annotation coverage and limits

[annotations.json](annotations.json) contains 18 assertions and 5 relationships across all three letters.
[reference.json](reference.json) records the evidence and reason for every answer.

The 2026-09-09 correction preserves original letter bytes and repairs the
query schedule, unsupported negatives, treatment-plan interpretation and missing
annotations. Source paragraphs retain context; they are not minimal evidence spans.
This is an authoring-assistant review, not an independent annotation pass.
Uncertain dates, identity and missing outcomes remain unresolved. No expert
validation, annotation-time measurement or schema-utility experiment is claimed.
