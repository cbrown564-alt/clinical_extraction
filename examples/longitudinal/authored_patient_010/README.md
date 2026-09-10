# Authored patient 010: Julia Rossi

Status: AI-authored fictional development example, version 0.5.
Challenge focus: Actual medication start and titration, qualifying EEG with confirmed result.
No real patient, source seed, paid model call, independent annotation or clinical review.
Implements P2.5 against [task definition v0.2](../../../docs/longitudinal/task_definition.md).

## Clinical Persona & Story

Julia Rossi is a fictional 31-year-old outpatient.
Actual medication start and titration, qualifying EEG with confirmed result.

| Letter | Consultation | Available to system | Contents |
| --- | --- | --- | --- |
| L1 | 2025-01-18 | 2025-01-18 | Initial consultation record. |
| L2 | 2025-04-25 | 2025-04-25 | Second consultation record. |
| L3 | 2025-08-20 | 2025-08-20 | Third consultation record. |

## Requests and Allowed Inputs

Indices are fixed 180 days apart; each retrospective cutoff is T + 180 days.

| Index/view | Index date | Information cutoff | Included letters |
| --- | --- | --- | --- |
| T1_visit | 2025-01-18 | 2025-01-18 | L1 |
| T1_retrospective | 2025-01-18 | 2025-07-17 | L1, L2 |
| T2_visit | 2025-07-17 | 2025-07-17 | L1, L2 |
| T2_retrospective | 2025-07-17 | 2026-01-13 | L1, L2, L3 |

## Expected Answers (20 Queries)

| Query | T1 visit | T1 retrospective | T2 visit | T2 retrospective |
| --- | --- | --- | --- | --- |
| Q1 | eligible | eligible | indeterminate | indeterminate |
| Q2 | indeterminate | indeterminate | indeterminate | indeterminate |
| Q3 | indeterminate | eligible | indeterminate | ineligible |
| Q4 | indeterminate | indeterminate | indeterminate | indeterminate |
| Q5 | indeterminate | indeterminate | indeterminate | indeterminate |

## Annotation coverage and limits

[annotations.json](annotations.json) contains 19 assertions and 6 relationships. Empty clinical letters are explicitly recorded in the manifest.
[reference.json](reference.json) records the evidence and reason for every answer.

The case manifest records whether this version preserves or revises authored letters.
Versioned changes cover the query schedule, unsupported negatives and treatment plans.
Source paragraphs retain context; they are not minimal evidence spans.
This is an authoring-assistant review, not an independent annotation pass.
Uncertain dates, identity and missing outcomes remain unresolved. No expert
validation, annotation-time measurement or schema-utility experiment is claimed.
