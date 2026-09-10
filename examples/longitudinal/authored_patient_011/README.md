# Authored patient 011: Kevin O'Connor

Status: AI-authored fictional development example, version 0.3.
Challenge focus: Seizure clusters vs isolated events, testing cluster count and burden schema.
No real patient, source seed, paid model call, independent annotation or clinical review.
Implements P2.5 against [task definition v0.2](../../../docs/longitudinal/task_definition.md).

## Clinical Persona & Story

Kevin O'Connor is a fictional 45-year-old outpatient.
Seizure clusters vs isolated events, testing cluster count and burden schema.

| Letter | Consultation | Available to system | Contents |
| --- | --- | --- | --- |
| L1 | 2025-02-12 | 2025-02-12 | Initial consultation record. |
| L2 | 2025-06-20 | 2025-06-20 | Second consultation record. |
| L3 | 2025-10-10 | 2025-10-10 | Third consultation record. |

## Requests and Allowed Inputs

Indices are fixed 180 days apart; each retrospective cutoff is T + 180 days.

| Index/view | Index date | Information cutoff | Included letters |
| --- | --- | --- | --- |
| T1_visit | 2025-02-12 | 2025-02-12 | L1 |
| T1_retrospective | 2025-02-12 | 2025-08-11 | L1, L2 |
| T2_visit | 2025-08-11 | 2025-08-11 | L1, L2 |
| T2_retrospective | 2025-08-11 | 2026-02-07 | L1, L2, L3 |

## Expected Answers (20 Queries)

| Query | T1 visit | T1 retrospective | T2 visit | T2 retrospective |
| --- | --- | --- | --- | --- |
| Q1 | eligible | eligible | eligible | eligible |
| Q2 | eligible | ineligible | indeterminate | indeterminate |
| Q3 | indeterminate | indeterminate | indeterminate | indeterminate |
| Q4 | indeterminate | indeterminate | indeterminate | indeterminate |
| Q5 | indeterminate | ineligible | eligible | eligible |

## Annotation coverage and limits

[annotations.json](annotations.json) contains 16 assertions and 4 relationships. Empty clinical letters are explicitly recorded in the manifest.
[reference.json](reference.json) records the evidence and reason for every answer.

The case manifest records whether this version preserves or revises authored letters.
Versioned changes cover the query schedule, unsupported negatives and treatment plans.
Source paragraphs retain context; they are not minimal evidence spans.
This is an authoring-assistant review, not an independent annotation pass.
Uncertain dates, identity and missing outcomes remain unresolved. No expert
validation, annotation-time measurement or schema-utility experiment is claimed.
