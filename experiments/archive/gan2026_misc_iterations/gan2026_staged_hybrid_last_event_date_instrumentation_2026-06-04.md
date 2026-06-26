# Gan 2026 Last-Event Date Instrumentation

Validation-development last-event duration policy for review rows. It derives auditable durations and conflict flags, but does not itself change prediction-bearing behavior, prompts, scorer policy, gold labels, locked-test behavior, verifier use, or benchmark-comparable claims.

## Summary

The review covers 8 last-event rows. 1 row contains a full date, 3 contain a partial date, and 4 contain no explicit date in the selected evidence.
Reference-date anchors are available for 8 rows.
Duration-auditable rows: 1.

## Release Readiness

Automatic release-ready rows: 0.

## Date Signal Classes

| Class | Rows |
| --- | ---: |
| `full_date_detected` | 1 |
| `no_explicit_date_in_selected_evidence` | 4 |
| `partial_date_missing_year` | 3 |

## Release Blockers

| Blocker | Rows |
| --- | ---: |
| `no_explicit_date_in_selected_evidence` | 4 |
| `partial_date_missing_year` | 3 |
| `protective_block_validation_accounting` | 1 |

## Next Step

Use duration-auditable rows only after the candidate-level promotion gate confirms no deterministic-correct regression and no evidence or source-id defect.

## Artifacts

- Date instrumentation JSONL: `experiments/gan2026_staged_hybrid_last_event_date_instrumentation_2026-06-04.jsonl`
- Date instrumentation summary JSON: `experiments/gan2026_staged_hybrid_last_event_date_instrumentation_2026-06-04.json`

## Rows

| Row | Label | Date signal | Derived duration | Blocker | Event dates | Reference dates |
| ---: | --- | --- | --- | --- | --- | --- |
| 11216 | `seizure free for 4 month` | `full_date_detected` | `seizure free for 4 month` | `protective_block_validation_accounting` | `25 December 2023` | `27 April 2024` |
| 11254 | `seizure free for multiple year` | `no_explicit_date_in_selected_evidence` | `` | `no_explicit_date_in_selected_evidence` | `` | `01 September 2021` |
| 11259 | `seizure free for multiple year` | `no_explicit_date_in_selected_evidence` | `` | `no_explicit_date_in_selected_evidence` | `` | `28 August 2018` |
| 11262 | `unknown` | `no_explicit_date_in_selected_evidence` | `` | `no_explicit_date_in_selected_evidence` | `` | `13 August 2021` |
| 11272 | `seizure free for multiple year` | `partial_date_missing_year` | `` | `partial_date_missing_year` | `20/Dec` | `23 March 2017` |
| 11282 | `unknown` | `no_explicit_date_in_selected_evidence` | `` | `no_explicit_date_in_selected_evidence` | `` | `06 November 2015` |
| 14810 | `12 per month` | `partial_date_missing_year` | `` | `partial_date_missing_year` | `12 May` | `12 June 2023` |
| 14821 | `17 per month` | `partial_date_missing_year` | `` | `partial_date_missing_year` | `17 Jul` | `17 August 2017` |