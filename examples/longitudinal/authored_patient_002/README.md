# Authored patient 002: Beatrice Hall

Status: AI-authored fictional development example, version 0.3.
Challenge focus: Ordinary unchanged follow-up, stable seizure frequency, established monotherapy.
No real patient, source seed, paid model call, independent annotation or clinical review.
Implements P2.5 against [task definition v0.2](../../../docs/longitudinal/task_definition.md).

## Clinical Persona & Story

Beatrice Hall is a fictional 42-year-old outpatient.
Ordinary unchanged follow-up, stable seizure frequency, established monotherapy.

| Letter | Consultation | Available to system | Contents |
| --- | --- | --- | --- |
| L1 | 2025-02-10 | 2025-02-10 | Initial consultation record. |
| L2 | 2025-08-15 | 2025-08-15 | Second consultation record. |
| L3 | 2025-11-20 | 2025-11-20 | Administrative missed-appointment letter; no clinical update. |

## Requests and Allowed Inputs

Indices are fixed 180 days apart; each retrospective cutoff is T + 180 days.

| Index/view | Index date | Information cutoff | Included letters |
| --- | --- | --- | --- |
| T1_visit | 2025-02-10 | 2025-02-10 | L1 |
| T1_retrospective | 2025-02-10 | 2025-08-09 | L1 |
| T2_visit | 2025-08-09 | 2025-08-09 | L1 |
| T2_retrospective | 2025-08-09 | 2026-02-05 | L1, L2, L3 |

## Expected Answers (20 Queries)

| Query | T1 visit | T1 retrospective | T2 visit | T2 retrospective |
| --- | --- | --- | --- | --- |
| Q1 | eligible | eligible | indeterminate | eligible |
| Q2 | ineligible | ineligible | indeterminate | indeterminate |
| Q3 | indeterminate | indeterminate | indeterminate | indeterminate |
| Q4 | indeterminate | indeterminate | indeterminate | indeterminate |
| Q5 | indeterminate | indeterminate | indeterminate | indeterminate |

## Annotation coverage and limits

[annotations.json](annotations.json) contains 12 assertions and 1 relationships. Empty clinical letters are explicitly recorded in the manifest.
[reference.json](reference.json) records the evidence and reason for every answer.

The case manifest records whether this version preserves or revises authored letters.
Versioned changes cover the query schedule, unsupported negatives and treatment plans.
Source paragraphs retain context; they are not minimal evidence spans.
This is an authoring-assistant review, not an independent annotation pass.
Uncertain dates, identity and missing outcomes remain unresolved. No expert
validation, annotation-time measurement or schema-utility experiment is claimed.
