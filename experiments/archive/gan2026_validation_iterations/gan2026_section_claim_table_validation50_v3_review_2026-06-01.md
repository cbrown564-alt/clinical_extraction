# Gan 2026 Section-Claim-Table V3 50-Row Review

Date: 2026-06-01

Surface: first 50 rows of `gan2026_split_v1` validation.

Artifacts reviewed:

- `experiments/gan2026_section_claim_table_validation25_gpt41mini_v3_2026-06-01.md`
- `experiments/gan2026_section_claim_table_validation25_gpt41mini_v3_2026-06-01.jsonl`
- `experiments/gan2026_section_claim_table_validation50_gpt41mini_v3_2026-06-01.md`
- `experiments/gan2026_section_claim_table_validation50_gpt41mini_v3_2026-06-01.jsonl`
- `experiments/gan2026_section_claim_table_validation50_gpt41mini_v3_rationale_replay_2026-06-01.md`
- `experiments/gan2026_section_claim_table_validation50_gpt41mini_v3_rationale_replay_2026-06-01.jsonl`

This is a validation development result, not a holdout or benchmark result.

## Decision

The no-call rationale-repair replay resolves the v3 schema blocker.

The original live 50-row artifact had one schema/parse failure from an omitted
`final_query.rationale`. The replay treats that as non-semantic schema repair:
when `rationale` is absent but exact selected evidence is present, copy the quote
from `final_query.evidence` into `rationale` and append a `conversion_note`
stating the repair. Do not add deterministic semantic selection or expand clean
scorer-facing policy for rows 187, 704, 869, or 1165.

## Summary

- 25-row smoke: 25/25 structured, 25/25 raw Purist, 25/25 clean Purist.
- 50-row diagnostic: 49/50 structured, 49/50 raw Purist, 49/50 clean Purist.
- 50-row rationale-repair replay: 50/50 structured, 50/50 raw Purist, 50/50
  clean Purist, with 50/50 raw outputs reused.
- Call failures: 0.
- Exact claim evidence substrings after replay: 154/155.
- Exact selected final evidence substrings after replay: 49/50.
- Rows changed by downstream repair layers: 1.
- Parse/schema failures after replay: 0.

## Reviewed Rows

| Row | Gold | V3 raw label | Selected evidence | Interpretation |
| ---: | --- | --- | --- | --- |
| 187 | `1 per 7 to 9 day` | `1 per 7 to 9 day` | `Since the last review, Ms Aisha Rahman reports that events tend to cluster every seven to nine days.` | Fixed. V3 selected explicit current cluster cadence over isolated recent subtype count. |
| 704 | `2 per month` | `2 per month` | `Frequency is now reported as twice a month, often clustering around the late luteal phase` | Still fixed. V3 preserved direct calendar-unit conversion and did not emit a cluster label. |
| 869 | `multiple per month` | `multiple per month` | `Diary review suggests several events spread across most months, typically brief, with occasional back-to-back occurrences on successive days.` | Fixed at raw layer. V3 used parser-ready category wording without clean-policy repair. |
| 1165 | `5 to 7 per 3 week` | `5 to 7 per 3 week` | `5 or 7 focal onset seizures in three weeks during a recent period that included an episode while travelling by air` | Fixed. V3 selected the recent counted range over the subsequent short seizure-free span. |

## Residual Issues

| Row | Issue | Impact |
| ---: | --- | --- |
| 243 | Selected evidence casing/span drift: model wrote `he and his partner...`, while the source substring differs in exact casing/context. | Label is correct, but exact evidence accounting marks claim and final query as failed. |
| 763 | Output omitted required `final_query.rationale` despite selecting `1 per week` with exact evidence. | Fixed by non-semantic schema repair in the no-call replay: rationale is the selected evidence quote and `conversion_note` records the repair. |
| 1094 | Raw `3 to 5 per 1 week` was strict-format repaired to `3 to 5 per week`. | Format-only repair; Purist correct before and after repair. |

## Interpretation

V3 resolves the reviewed model-side final-query priority failures without using
deterministic semantic selection. The no-call replay removes the schema blocker
while preserving the original model-selected labels and evidence. The remaining
known issue is one localized exact-evidence casing/span failure on row 243; it is
label-correct and reviewable, not a systemic schema or final-query failure.
