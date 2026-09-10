# Authored patient 003: Christopher Vance

Status: AI-authored fictional development example, version 0.4.
Challenge focus: Copied boilerplate history with subtle breakthrough event appended.
No real patient, source seed, paid model call, independent annotation or clinical review.
Implements P2.5 against [task definition v0.2](../../../docs/longitudinal/task_definition.md).

## Clinical Persona & Story

Christopher Vance is a fictional 29-year-old outpatient.
Copied boilerplate history with subtle breakthrough event appended.

| Letter | Consultation | Available to system | Contents |
| --- | --- | --- | --- |
| L1 | 2025-03-01 | 2025-03-01 | Initial consultation record. |
| L2 | 2025-06-12 | 2025-06-12 | Second consultation record. |
| L3 | 2025-09-18 | 2025-09-18 | Third consultation record. |

## Requests and Allowed Inputs

Indices are fixed 180 days apart; each retrospective cutoff is T + 180 days.

| Index/view | Index date | Information cutoff | Included letters |
| --- | --- | --- | --- |
| T1_visit | 2025-03-01 | 2025-03-01 | L1 |
| T1_retrospective | 2025-03-01 | 2025-08-28 | L1, L2 |
| T2_visit | 2025-08-28 | 2025-08-28 | L1, L2 |
| T2_retrospective | 2025-08-28 | 2026-02-24 | L1, L2, L3 |

## Expected Answers (20 Queries)

| Query | T1 visit | T1 retrospective | T2 visit | T2 retrospective |
| --- | --- | --- | --- | --- |
| Q1 | ineligible | ineligible | indeterminate | ineligible |
| Q2 | ineligible | ineligible | indeterminate | ineligible |
| Q3 | indeterminate | indeterminate | indeterminate | indeterminate |
| Q4 | indeterminate | indeterminate | indeterminate | indeterminate |
| Q5 | indeterminate | indeterminate | indeterminate | indeterminate |

## Annotation coverage and limits

[annotations.json](annotations.json) contains 16 assertions and 2 relationships. Empty clinical letters are explicitly recorded in the manifest.
[reference.json](reference.json) records the evidence and reason for every answer.

The case manifest records whether this version preserves or revises authored letters.
Versioned changes cover the query schedule, unsupported negatives and treatment plans.
Source paragraphs retain context; they are not minimal evidence spans.
This is an authoring-assistant review, not an independent annotation pass.
Uncertain dates, identity and missing outcomes remain unresolved. No expert
validation, annotation-time measurement or schema-utility experiment is claimed.
