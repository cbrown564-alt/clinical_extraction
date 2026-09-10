# Authored patient 005: Edward Davies

Status: AI-authored fictional development example, version 0.3.
Challenge focus: Sparse dates and fuzzy temporal bounds with outpatient EEG.
No real patient, source seed, paid model call, independent annotation or clinical review.
Implements P2.5 against [task definition v0.2](../../../docs/longitudinal/task_definition.md).

## Clinical Persona & Story

Edward Davies is a fictional 67-year-old outpatient.
Sparse dates and fuzzy temporal bounds with outpatient EEG.

| Letter | Consultation | Available to system | Contents |
| --- | --- | --- | --- |
| L1 | 2025-02-01 | 2025-02-01 | Initial consultation record. |
| L2 | 2025-07-02 | 2025-07-02 | Second consultation record. |
| L3 | 2025-10-15 | 2025-10-15 | Third consultation record. |

## Requests and Allowed Inputs

Indices are fixed 180 days apart; each retrospective cutoff is T + 180 days.

| Index/view | Index date | Information cutoff | Included letters |
| --- | --- | --- | --- |
| T1_visit | 2025-02-01 | 2025-02-01 | L1 |
| T1_retrospective | 2025-02-01 | 2025-07-31 | L1 |
| T2_visit | 2025-07-31 | 2025-07-31 | L1 |
| T2_retrospective | 2025-07-31 | 2026-01-27 | L1, L2, L3 |

## Expected Answers (20 Queries)

| Query | T1 visit | T1 retrospective | T2 visit | T2 retrospective |
| --- | --- | --- | --- | --- |
| Q1 | eligible | eligible | indeterminate | indeterminate |
| Q2 | ineligible | ineligible | indeterminate | indeterminate |
| Q3 | ineligible | ineligible | indeterminate | eligible |
| Q4 | indeterminate | indeterminate | indeterminate | eligible |
| Q5 | indeterminate | indeterminate | indeterminate | indeterminate |

## Annotation coverage and limits

[annotations.json](annotations.json) contains 26 assertions and 7 relationships. Empty clinical letters are explicitly recorded in the manifest.
[reference.json](reference.json) records the evidence and reason for every answer.

The case manifest records whether this version preserves or revises authored letters.
Versioned changes cover the query schedule, unsupported negatives and treatment plans.
Source paragraphs retain context; they are not minimal evidence spans.
This is an authoring-assistant review, not an independent annotation pass.
Uncertain dates, identity and missing outcomes remain unresolved. No expert
validation, annotation-time measurement or schema-utility experiment is claimed.
