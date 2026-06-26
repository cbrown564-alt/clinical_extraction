# Gan 2026 Section-Claim-Table 50-Row Failure Review

Date: 2026-06-01

Surface: first 50 rows of `gan2026_split_v1` validation.

Artifact reviewed:

- `experiments/gan2026_section_claim_table_validation50_gpt41mini_2026-06-01.jsonl`

This is a development-split diagnostic review, not a holdout result or
benchmark-comparison claim.

## Decision

Do not promote `gan2026_section_claim_table_v0` to a 250-row comparison.

Keep the 50-row run as a diagnostic comparator and revise the prompt/schema
before any further section-claim-table escalation. The revision should target raw
Gan-compatible final labels and final-query edge cases, not expand deterministic
semantic repair. A new branch should restart at the 25-row smoke gate.

## Summary

The branch is useful because intermediate extraction remains inspectable:

- Schema parse: 50/50.
- Claim evidence exactness: 173/176 exact claim evidence substrings.
- Selected final evidence exactness: 48/50.
- Raw/strict/clean Purist: 25/50, 38/50, 43/50.
- Raw/strict/clean Pragmatic: 27/50, 40/50, 46/50.
- Raw scorer-format failures: 20/50.

The run is not 250-ready because raw scorer-format failures are systemic, and
the clean-policy misses include final-query reasoning errors rather than only
format dialect. This means a larger run would mostly measure known prompt/schema
defects and frozen repair behavior.

## Failure Families

### Raw Scorer-Format Labels

The raw final query often preserved source-near text instead of producing a Gan
label:

| Family | Count | Example rows |
| --- | ---: | --- |
| Upper-bound symbol or wording | 6 | 10, 40, 79, 103, 409 |
| Other unsupported surface | 6 | 338, 531, 598, 725, 731 |
| Cluster grammar emitted for ordinary frequency | 3 | 187, 190, 899 |
| Bimonthly prose | 2 | 960, 987 |
| Every-interval prose | 1 | 182 |
| Plural/unit surface | 1 | 849 |
| Vague quantity | 1 | 869 |

Many of these are legitimate source-near claim values, but they should not
survive into `final_query.final_label` when the prompt asks for a Gan-facing
answer.

### Selected-Evidence Misses

Rows 103 and 243 had invalid selected final evidence. Row 103 still scored after
clean normalization, but the selected evidence was a non-exact paraphrase with
`≤ two or four per year`. These misses support tightening final-query evidence
copying rather than adding selected-evidence repair.

### Clean-Policy Purist Misses

The remaining clean-layer misses were:

| Row | Gold | Model final label | Main issue |
| ---: | --- | --- | --- |
| 182 | `1 per 2 day` | `1 seizure every 2 days` | Format repair bug produced `1 1 per 2 day`; not a model clinical error. |
| 187 | `1 per 7 to 9 day` | `1 cluster per week` | Final query rounded an interval and introduced cluster wording. |
| 212 | `1 per 3 to 4 week` | `1 per month` | Final query rounded the source interval to a monthly category. |
| 665 | `2 per 2 week` | `2 per month` | Final query converted the denominator incorrectly. |
| 790 | `1 per 7 to 10 day` | `1 per week` | Final query rounded the source interval. |
| 959 | `1 per 2 month` | `1 to 2 per month` | Final query misread Gan `bimonthly` dialect. |
| 1165 | `5 to 7 per 3 week` | `seizure free for 6 weeks` | Final query prioritized most recent seizure-free span over recent event burden. |

Rows 212, 665, 790, 959, and 1165 are final-query edge cases explicitly
relevant to prompt/schema revision. They should not be fixed by broadening the
clean scorer-facing policy because that would cross from benchmark-format repair
into semantic correction.

## Prompt/Schema Revision Targets

A `v1` section-claim-table branch should test whether the model can keep the
claim table source-near while making the final query Gan-compatible:

- Separate `final_query.raw_selected_frequency` from `final_query.final_label`.
- Add `final_query.conversion_note` for any source-near to Gan-label conversion.
- Tell the model to preserve explicit intervals such as `every 3 - 4 weeks`,
  `twice every two weeks`, and `once every seven to ten days` as Gan labels
  rather than rounding to month/week categories.
- Tell the model that `bimonthly` in Gan synthetic letters means `1 per 2 month`
  unless the note explicitly says twice per month.
- Tell the model not to emit cluster labels unless the selected claim is truly a
  cluster-frequency label with cluster count and per-cluster burden.
- Tell the model to prefer recent quantified event burden over a short
  seizure-free span when Gan gold-style labeling describes the recent quantified
  burden.
- Require final evidence to be copied verbatim from one selected claim row.

The next experiment should be a new 25-row validation smoke. Promotion to 50
should require low raw scorer-format failures, exact selected evidence, and no
obvious final-query interval-rounding family.

## Claim Boundary

The current 50-row result should be described as:

> A section-claim-table diagnostic development artifact with strong evidence
> traceability but systemic raw final-label format failures and unresolved
> final-query edge cases.

It should not be described as a 250-ready LLM-first validation candidate.
