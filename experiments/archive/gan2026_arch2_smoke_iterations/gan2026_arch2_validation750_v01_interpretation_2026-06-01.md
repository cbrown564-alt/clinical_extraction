# Gan 2026 Architecture 2 Full-Validation Interpretation

Date: 2026-06-01

Primary live run:
`experiments/gan2026_arch2_validation750_gpt41mini_v01_2026-06-01.md`

Schema replay:
`experiments/gan2026_arch2_validation750_gpt41mini_v01_schema_replay2_2026-06-01.md`

This is a validation development interpretation on `gan2026_split_v1`. It is
not a holdout or benchmark result.

## Decision

Revise before holdout.

Architecture 2 clears the broad-validation numeric heuristic after schema replay:
680/750 Purist = 0.9067 and 689/750 Pragmatic = 0.9187 with 750/750 decision
records and 0 parse failures. That is strong enough to keep the architecture in
contention.

It is not strong enough to freeze for test. On the same rows, the deterministic
top candidate scores 697/750 Purist = 0.9293 and 704/750 Pragmatic = 0.9387.
The LLM adjudicator improves 7 deterministic misses but regresses 24
deterministic-correct rows. The current adjudicator therefore weakens aggregate
validation performance even though it makes the prediction-bearing selection
component explicit.

## Full-Validation Table

| Condition | Purist | Pragmatic | Parse failures | Changed labels |
| --- | ---: | ---: | ---: | ---: |
| Deterministic top candidate | 697/750 | 704/750 | 0 | 0 |
| LLM adjudicator live parse | 649/750 | 658/750 | 32 | 43 |
| LLM adjudicator schema replay | 680/750 | 689/750 | 0 | 43 |
| Candidate-recall ceiling | 707/750 | - | - | - |

Schema replay is a no-call replay over saved raw outputs. It repaired nullable
string fields and enum aliases but did not change model-selected labels except
through already-recorded format repair.

## Interpretation

The decomposition is scientifically useful but not yet metrically superior. The
deterministic generator supplies a high-recall evidence substrate. The LLM
occasionally corrects deterministic overreach, including temporal and unknown
boundary cases, but it too often selects plausible lower-priority candidates:
lower recent subtype counts, longer-window aggregates, last-event-only rates, or
seizure-free candidates when current frequency evidence should remain active.

The candidate-recall ceiling is 707/750, only ten rows above deterministic top.
This means the current candidate set leaves limited room for adjudication gains
unless the LLM is nearly perfectly conservative. A useful Architecture 2 v0.2
needs either better candidate recall or a constrained adjudicator that changes
the deterministic top only for well-defined failure families.

## Research Implication

For the central decomposition question, the current result argues against a
free-form LLM adjudicator over deterministic candidates. The better hybrid
decomposition is likely:

1. deterministic candidate retrieval;
2. deterministic top as a strong default;
3. LLM adjudication only for named overreach families exposed by deterministic
   ablation, with abstention/fallback as a first-class behavior.

That would make the LLM a targeted adjudicator rather than a universal selector.

## Next Experiments

1. Build an Architecture 2 conservative-adjudicator replay that falls back to
   deterministic top unless the LLM change belongs to a named overreach family.
2. Separate changed rows by transition family: no-reference to unknown, high
   burden to lower count, seizure-free boundary, last-event-only rate, and
   long-window aggregate.
3. Improve candidate recall only through named deterministic candidate families,
   with validation ablations and portability labels.
4. Do not evaluate Architecture 2 v0.1 on test. It is a validation development
   result, not a frozen holdout candidate.
