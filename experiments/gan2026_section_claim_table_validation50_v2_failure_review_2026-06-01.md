# Gan 2026 Section-Claim-Table V2 50-Row Failure Review

Date: 2026-06-01

Surface: first 50 rows of `gan2026_split_v1` validation.

Artifacts reviewed:

- `experiments/gan2026_section_claim_table_validation50_gpt41mini_v2_2026-06-01.md`
- `experiments/gan2026_section_claim_table_validation50_gpt41mini_v2_2026-06-01.jsonl`

This is a development-split diagnostic review, not a holdout result or
benchmark-comparison claim.

## Decision

Do not promote `gan2026_section_claim_table_v2` to 250 rows.

A narrow `v3` final-query priority prompt is justified before pausing the
section-claim-table branch for ablation work. The justification is that v2
localized the main misses to model-side final-query policy and one raw
parser-ready wording issue, while preserving reviewable claim rows and exact
selected evidence. The next run should restart at the 25-row validation smoke
gate and remain diagnostic until a 50-row artifact passes the documented
decision gate.

## Summary

`gan2026_section_claim_table_v2` is a much cleaner diagnostic than v0/v1:

- Structured records: 50/50.
- Exact claim evidence substrings: 167/169.
- Exact selected final evidence substrings: 50/50.
- Raw/strict Purist: 45/50.
- Frozen-clean Purist: 46/50.
- Rows changed by downstream repair layers: 3.

The residual review target is not broad schema repair. It is whether the model's
final query can follow Gan-facing selection priority without deterministic
semantic correction.

## Reviewed Rows

| Row | Gold | V2 final label | Selected claim | Failure type |
| ---: | --- | --- | --- | --- |
| 187 | `1 per 7 to 9 day` | `2 per 2 week` | two recent nocturnal generalised tonic-clonic seizures | Final query preferred a recent count with an assumed denominator over a current explicit cluster cadence. |
| 869 | `multiple per month` | `several per month` | several events spread across most months | Raw final label used unsupported vague wording; frozen clean policy repaired it to `multiple per month`. |
| 1165 | `5 to 7 per 3 week` | `seizure free for 6 month` | subsequent six-week seizure-free span | Final query preferred current seizure-free status over the recent quantified event range. |

## Interpretation

Row 187 is not a claim-extraction failure. The table includes the correct
current cadence claim, `events tend to cluster every seven to nine days`, but
the final query selects the rarer nocturnal tonic-clonic count and invents a
`2 per 2 week` denominator. A v3 prompt should state that an explicit current
cadence normally outranks an isolated lower-burden recent subtype count unless
the note says the cadence is non-epileptic, historical, or not the Gan target.

Row 1165 is the same family from the opposite direction. The table contains the
recent quantified burden, `5 or 7 focal onset seizures in three weeks`, and the
subsequent seizure-free span. The final query chooses seizure freedom because it
is the current state, but the Gan-style answer for this family is the recent
counted range. A v3 prompt should explicitly prefer recent counted seizure
burden over a short subsequent seizure-free span when both are part of the same
current clinical interval.

Row 869 is not a clinical-selection failure. The selected claim is appropriate,
but `several per month` is not parser-ready Gan wording. A v3 prompt should
continue to keep source-near text in `raw_selected_frequency`, while requiring
`final_label` to use accepted category language such as `multiple per month` for
vague recurring monthly events.

## V3 Prompt Targets

- Preserve the v2 claim schema; do not add deterministic temporal selection.
- Strengthen final-query priority for explicit current cadences over assumed
  denominators from isolated subtype counts.
- Strengthen final-query priority for recent counted event ranges over short
  subsequent seizure-free spans in Gan-style labeling.
- Require parser-ready Gan wording in `final_label`, with source-near wording
  kept in `raw_selected_frequency` and explained in `conversion_note`.
- Keep selected evidence copied from the selected claim row.

## Stop Conditions

Pause the section-claim-table branch after v3 if a 25/50-row run still needs
deterministic semantic repair for row families like 187 or 1165. At that point
the work should shift to named LLM-replacement or hybrid ablations rather than
quietly expanding clean scorer-facing policy.
