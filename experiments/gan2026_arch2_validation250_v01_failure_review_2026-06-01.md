# Gan 2026 Architecture 2 Validation250 V0.1 Failure Review

Date: 2026-06-01

Primary run:
`experiments/gan2026_arch2_validation250_gpt41mini_v01_2026-06-01.md`

Schema replay:
`experiments/gan2026_arch2_validation250_gpt41mini_v01_schema_replay_2026-06-01.md`

This is a validation development review on `gan2026_split_v1`. It is not a
holdout or benchmark result.

## Decision

Promote Architecture 2 as the strongest current validation candidate, but do not
freeze it for holdout yet.

The candidate passes the 250-row validation metric gate: the schema replay has
250/250 decision records, 0 parse failures, 243/250 Purist, and 244/250
Pragmatic. The architecture gate is also substantially cleaner than the earlier
dev-set adjudicator because the prediction-bearing component is explicit: the
LLM adjudicates deterministic candidate evidence, while deterministic code only
generates candidates, repairs output shape, and scores.

The blocker for holdout is interpretability, not aggregate score. The run shows
four candidate-recall misses and three adjudicator regressions. The next step is
a targeted failure review and ablation, not test evaluation.

## Summary

| Surface | Purist | Pragmatic | Parse failures | Candidate recall | Changed labels |
| --- | ---: | ---: | ---: | ---: | ---: |
| live 250 | 242/250 | 243/250 | 1 | 246/250 | 7 |
| schema replay | 243/250 | 244/250 | 0 | 246/250 | 7 |

The schema replay changed only non-semantic aliases, including `current to
recent` temporality. It should be reported as a no-call schema replay, not a new
model result.

## Failure Rows

| Row | Family | Deterministic | Adjudicator | Gold | Interpretation |
| ---: | --- | --- | --- | --- | --- |
| 744 | adjudicator regression | multiple per week | 1 per 8 week | multiple per week | LLM selected a lower recent GTC count over broader current burden. |
| 2748 | adjudicator regression | 1 per month | 7 per 10 month | 1 per month | LLM selected a longer-window aggregate instead of current monthly rate. |
| 3534 | adjudicator regression | unknown | 1 per year | unknown | LLM converted a sparse last-event signal into a rate. |
| 3356 | candidate recall miss | seizure free for multiple year | seizure free for multiple year | unknown | Generator lacks the needed unknown/no-reference candidate. |
| 3528 | candidate recall miss | seizure free for multiple year | seizure free for multiple year | unknown | Generator lacks the needed unknown/no-reference candidate. |
| 4690 | candidate recall miss | seizure free for multiple year | seizure free for multiple year | multiple per day | Generator misses active high-burden evidence. |
| 5534 | candidate recall miss | seizure free for multiple year | seizure free for multiple year | 1 per multiple month | Generator misses low-frequency current evidence. |

Changed but Purist-correct rows were 338, 3468, 4694, and 4771. These mostly
changed `no seizure frequency reference` to `unknown`, which is semantically more
faithful in some cases but still collapses to the same Purist category. Keep this
distinction in semantic reporting even when Purist does not penalize it.

## Interpretation

Architecture 2 is currently the cleanest answer to the decomposition question:
deterministic rules are useful as transparent candidate retrieval, while the LLM
can adjudicate the candidate set without a hidden semantic repair stack. On this
250-row validation slice, however, the LLM mostly preserves the deterministic
top candidate and occasionally worsens it. The aggregate gain over deterministic
V1 is not yet proven; the value is architectural transparency and a route to
targeted selection improvements.

The candidate-generator ceiling matters. Candidate recall is 246/250, so no
adjudicator can exceed that Purist ceiling without an escape mechanism or better
candidate generation. The four recall misses should be reviewed before prompt
tuning, because they are retrieval failures rather than reasoning failures.

## Next Experiments

1. Run an Architecture 2 component ablation on the same 250 raw outputs:
   deterministic top, LLM adjudicator, no semantic alias repair, and schema
   replay.
2. Add an adjudicator prompt revision only for broad-current-burden versus
   lower-count recent-event selection, then repeat 25/50 before another 250.
3. Review the four candidate-recall misses to decide whether they require a new
   named deterministic candidate family or an explicit LLM escape route.
4. Do not inspect holdout rows until a freeze decision is recorded after the
   validation review and ablation.
