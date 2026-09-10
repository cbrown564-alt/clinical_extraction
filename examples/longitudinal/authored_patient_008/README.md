# Authored patient 008: Hannah Clarke

Status: AI-authored fictional development example, version 0.2.
Challenge focus: Irregular follow-up with 18-month gap, medication discontinuation, and cluster relapse.
No real patient, source seed, paid model call, independent annotation or clinical review.
Implements P2.5 against [task definition v0.2](../../../docs/longitudinal/task_definition.md).

## Clinical Persona & Story

Hannah Clarke is a fictional 19-year-old outpatient.
Irregular follow-up with 18-month gap, medication discontinuation, and cluster relapse.

| Letter | Consultation | Available to system | Contents |
| --- | --- | --- | --- |
| L1 | 2023-08-10 | 2023-08-10 | Initial consultation record. |
| L2 | 2025-02-20 | 2025-02-20 | Second consultation record. |
| L3 | 2025-06-15 | 2025-06-15 | Third consultation record. |

## Requests and Allowed Inputs

Indices are fixed 180 days apart; each retrospective cutoff is T + 180 days.

| Index/view | Index date | Information cutoff | Included letters |
| --- | --- | --- | --- |
| T1_visit | 2023-08-10 | 2023-08-10 | L1 |
| T1_retrospective | 2023-08-10 | 2024-02-06 | L1 |
| T2_visit | 2024-02-06 | 2024-02-06 | L1 |
| T2_retrospective | 2024-02-06 | 2024-08-04 | L1 |

## Expected Answers (20 Queries)

| Query | T1 visit | T1 retrospective | T2 visit | T2 retrospective |
| --- | --- | --- | --- | --- |
| Q1 | eligible | eligible | indeterminate | indeterminate |
| Q2 | indeterminate | indeterminate | indeterminate | indeterminate |
| Q3 | indeterminate | indeterminate | indeterminate | indeterminate |
| Q4 | indeterminate | indeterminate | indeterminate | indeterminate |
| Q5 | indeterminate | indeterminate | indeterminate | indeterminate |

## Annotation coverage and limits

[annotations.json](annotations.json) contains 12 assertions and 2 relationships. Empty clinical letters are explicitly recorded in the manifest.
[reference.json](reference.json) records the evidence and reason for every answer.

The case manifest records whether this version preserves or revises authored letters.
Versioned changes cover the query schedule, unsupported negatives and treatment plans.
Source paragraphs retain context; they are not minimal evidence spans.
This is an authoring-assistant review, not an independent annotation pass.
Uncertain dates, identity and missing outcomes remain unresolved. No expert
validation, annotation-time measurement or schema-utility experiment is claimed.
