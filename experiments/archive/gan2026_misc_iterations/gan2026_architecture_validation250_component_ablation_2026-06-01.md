# Gan 2026 Validation250 Architecture Component Ablation

Date: 2026-06-01

This is a validation-only development interpretation on `gan2026_split_v1`. It
does not inspect holdout rows and is not a benchmark result.

Primary artifacts:

- Section table:
  `experiments/gan2026_section_claim_table_validation250_gpt41mini_v4_schema_replay_2026-06-01.md`
- Architecture 2:
  `experiments/gan2026_arch2_validation250_gpt41mini_v01_schema_replay_2026-06-01.md`
- Deterministic V1 comparator:
  `experiments/gan2026_v1_validation_ablation_2026-05-31.md`

## Executive Interpretation

Architecture 2 is currently the strongest validation candidate by metric and by
decomposition clarity, but the LLM adjudicator is not yet an independent source
of aggregate gain over deterministic top-candidate selection on the first 250
validation rows. Its value is an explicit, auditable hybrid decomposition:
deterministic rules retrieve candidates and evidence, while the LLM performs a
named selection step.

Section-claim-table v4 remains a useful LLM-first architecture, but the
validation250 evidence says revise before scale-up. It clears the 0.9000
development threshold after schema replay, yet still relies on downstream
strict/clean scorer-facing repair for three Purist rows and has semantic failure
families that matter for generalisation.

Deterministic V1 remains the essential comparator. Its validation score is high,
but the known locked-test drop means validation performance alone is not enough
to support a generalisation claim.

## Component Table

| Architecture | Condition | Purist | Pragmatic | Notes |
| --- | --- | ---: | ---: | --- |
| Section table v4 | raw final query | 228/250 | 235/250 | Prediction-bearing model output before label repair. |
| Section table v4 | strict format repair | 230/250 | 237/250 | Parser-surface repair; 31 labels changed, 2 Purist gains, 0 regressions. |
| Section table v4 | clean scorer-facing policy | 231/250 | 238/250 | Adds frozen clean policy; 33 labels changed from raw, 3 Purist gains, 0 regressions. |
| Architecture 2 | deterministic top candidate | 246/250 | 246/250 | Candidate generator plus deterministic V1 selection. |
| Architecture 2 | LLM adjudicator | 243/250 | 244/250 | Seven labels changed, 0 Purist gains, 3 Purist regressions. |
| Architecture 2 | candidate recall ceiling | 246/250 | - | Correct Purist category appears somewhere in deterministic candidates. |
| Deterministic V1 | full validation baseline | 697/750 | 704/750 | From existing deterministic validation ablation. |

## Section Table Findings

The section table has a clean architecture story: no deterministic candidates are
shown to the model, and the model builds a claim table plus final query. The
schema replay has 250/250 structured records and 0 parse failures, which is a
real improvement over the interrupted live artifact.

However, the metric stack is mixed provenance:

- Raw model final-query Purist: 228/250.
- Strict-format Purist: 230/250.
- Clean scorer-facing Purist: 231/250.
- Raw-to-clean changed rows: 33.
- Raw-wrong to clean-correct gains: 3.
- Raw-correct to clean-wrong regressions: 0.

Remaining clean Purist misses include interval collapse, cluster-axis errors,
unknown/seizure-free boundary errors, denominator mismatches, and no-reference
misses. Examples include row 1046 collapsing a count range to a point, row 3261
missing cluster count, rows 3371/3469/3534 over-selecting seizure freedom where
gold is unknown, and rows 5110/5121 missing seizure-free states.

Interpretation: section table v4 should be revised before full-validation or
holdout use. A v5 should target semantic selection and parser-ready label
discipline without expanding clean scorer-facing policy.

## Architecture 2 Findings

Architecture 2 has the best validation250 metric:

- Deterministic candidate recall ceiling: 246/250.
- Deterministic top candidate: 246/250 Purist.
- LLM adjudicator: 243/250 Purist.
- Changed labels: 7.
- Deterministic-wrong to adjudicator-correct: 0.
- Deterministic-correct to adjudicator-wrong: 3.

The changed-label pattern is informative. Four changes converted `no seizure
frequency reference` to `unknown`; these remained Purist-correct because Gan
scoring collapses both states. Three changes were regressions: lower recent GTC
count over broader current burden, longer-window aggregate over current monthly
rate, and sparse last-event signal converted into a rate.

Interpretation: the candidate generator is doing most of the metric work on this
slice. The LLM adjudicator makes semantic distinctions that may help
transparency, but the current prompt does not yet improve aggregate Purist. The
next adjudicator revision should be conservative about overriding deterministic
top when the alternative is a lower-burden subtype, longer-window aggregate, or
last-event-only rate.

## Deterministic V1 Comparator

The existing deterministic ablation remains central:

- Full validation baseline: 697/750 Purist = 0.9293.
- Locked test result: 342/450 Purist = 0.7600.
- Largest validation dependencies: portable rate expressions, temporal
  selection, seizure-free/no-event assertions, diary/log aggregation, and
  cluster arithmetic.

Interpretation: deterministic rules are powerful and transparent but brittle.
They should remain a controlled candidate/evidence substrate and an ablation
comparator, not be treated as proof of generalisable clinical reasoning by
themselves.

## Research Answer So Far

The best current decomposition is hybrid, but not because the LLM already beats
rules on aggregate validation. The evidence suggests:

1. Deterministic extraction is the strongest candidate-retrieval substrate.
2. LLM adjudication is promising for making selection explicit, but the current
   adjudicator needs guardrails against plausible but lower-priority candidates.
3. LLM-first section tables are more source-near and transparent, but need better
   selection robustness before they should face holdout.
4. Generalisation cannot be inferred from 250-row validation prefixes; full
   validation and locked-test evaluation after freeze are still required.

## Next Decisions

Architecture 2 is justified for a full-validation run because it has the
strongest 250-row validation score and a clean decomposition. Section-table v4
should not scale further until a v5 hypothesis is recorded and passes the
25/50/250 ladder. Neither architecture should use holdout rows until a freeze
artifact records the exact code, prompt, model, repair policy, and ablation
interpretation.
