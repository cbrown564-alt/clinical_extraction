# Gan 2026 Section-Claim-Table V4 Full-Validation Interpretation

Date: 2026-06-01

Primary run:
`experiments/gan2026_section_claim_table_validation750_gpt41mini_v4_2026-06-01.md`

This is a validation development interpretation on `gan2026_split_v1`. It is
not a holdout or benchmark result.

## Decision

Reject v4 for holdout. Revise the section-claim-table architecture before any
test-set use.

The 250-row prefix was optimistic. The full-validation result is 528/750 clean
Purist = 0.7040 and 577/750 clean Pragmatic = 0.7693. This is below
deterministic V1 and far below the validation margin needed to plausibly clear
0.8 on the locked test set.

## Full-Validation Table

| Layer | Purist | Pragmatic | Scorable |
| --- | ---: | ---: | ---: |
| Raw final query | 512/750 | 559/750 | 706/750 |
| Strict format repair | 516/750 | 564/750 | 711/750 |
| Clean scorer-facing policy | 528/750 | 577/750 | 732/750 |

Downstream repair improves the score but does not rescue the architecture:
raw-to-clean adds 16 Purist rows and 18 Pragmatic rows, while 108 rows change
downstream. The broad-validation score is therefore both too low and too mixed
in attribution for a holdout freeze.

## Component Failure Slices

| Component | Failures |
| --- | ---: |
| claim_extraction | 54 |
| scorer_format | 44 |
| final_query | 27 |
| segmentation_sectioning | 21 |
| temporality_conflict | 7 |
| parse_schema | 3 |

Most remaining errors are semantic, not schema. The schema repair work improved
the 250-row architecture gate, but full validation exposes selection and
representation failures.

## Error Distribution

| Gold kind | Misses | Total |
| --- | ---: | ---: |
| frequency | 173 | 468 |
| unknown | 33 | 100 |
| unresolved_multiple | 8 | 43 |
| seizure_free | 7 | 112 |
| no_reference | 1 | 27 |

Top failure patterns:

- Frequency rows predicted as seizure-free, especially lower-frequency current
  burdens collapsed to `currently_no_seizure`.
- Frequency rows predicted as unknown/no-reference when the model failed to
  preserve cluster cadence, diary totals, or active semiology counts.
- Cluster-axis collapse: labels such as cluster cadence plus per-cluster burden
  were flattened to ordinary rates, unknown, or lower-rate cadence only.
- Window/denominator mismatch: monthly or multi-month current rates were mapped
  to a different denominator.
- Unknown rows over-converted into seizure-free or sparse numeric rates.
- Some administrative/no-reference rows returned empty claim tables, which is
  semantically understandable but weakens the architecture gate.

## Interpretation

The flat claim-table idea remains promising for transparency, but v4 asks the
model to solve too many benchmark-specific details inside one final query. The
claim table often contains useful evidence, but the final label collapses
cluster structure, currentness, uncertainty, and denominator policy into a
single fragile model decision.

This argues for a v5 decomposition change rather than another small prompt patch:

1. preserve the claim table as a source-near representation;
2. make the final query more constrained and auditable;
3. add explicit cluster-axis fields or claim types that keep cadence and
   per-cluster burden separate;
4. require an explicit boundary decision for `unknown`, `no_reference`, and
   `seizure_free`;
5. consider a deterministic scorer-facing query over the model claim table, with
   the selector ablated as a named component.

## Research Implication

The full-validation result weakens a pure LLM-first section-table claim. It does
not invalidate the decomposition, but it shows that "model creates table and
model directly emits Gan label" is not robust enough. The better research
question for v5 is whether an LLM claim table plus constrained deterministic or
hybrid selector can preserve transparency while improving generalisation.

## Next Experiments

1. Build a v5 section-table schema with explicit cluster cadence/per-cluster
   fields and explicit boundary-state fields.
2. Add a selector ablation: model final query versus deterministic query over
   the same model claims.
3. Repeat the 25/50/250 validation ladder before any full-validation rerun.
4. Do not run section-table v4 on test.
