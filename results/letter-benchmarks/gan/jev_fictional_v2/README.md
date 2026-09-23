# Jev / DeepSeek fictional pilot v2

Completed 2026-09-21. This is a small, deliberately constructed development
experiment: 14 distinct fictional letters produce 22 related conditions. It is
not clinical validation, native Gan performance or evidence of holdout generalisation.

## Results

| Measure | Jev 1.13.0 | DeepSeek Flash (documented V4.1) |
| --- | ---: | ---: |
| Correct primary selection | 20/22 | 22/22 |
| Correct scored decisions | 142/157 | 157/157 |
| Correct selection plus selected attributes | 9/22 | 22/22 |
| Sentence-role decisions | 67/67 | 67/67 |
| Returned valid choices, including unscored questions | 357/357 | 357/357 |
| Transport / parsing failures | 0 | 0 |
| Mean request wall time | 0.678 s | 10.352 s |
| Measured-token cost at peak rates (upper estimate) | US$0.002869 | US$0.080455 |

The source-only DeepSeek V4 Pro reference review cost at most US$0.022766 by
measured tokens and peak rates; combined estimate US$0.106090. These are not
provider invoices. The frozen full reservation was US$0.862983 under a US$2 cap.
Latency includes network/provider processing, with one sequential request per
provider and no repetitions; it does not establish general throughput or latency.
DeepSeek returned the `deepseek-flash` alias, not an immutable checkpoint identifier.

## Errors and robustness

Jev's 15 incorrect scored decisions occurred in 13 conditions:

- Eight inner-quantity errors supplied an individual event count when the finding
  was not a cluster and the correct value was `not_applicable`.
- Three outer-quantity errors selected the within-cluster count (6 or 11) instead
  of cluster-day recurrence (2 or 5).
- Two selection errors chose the sentence stating that current frequency was
  not discussed instead of `no_current`, despite correctly typing its role unknown.
- In the changed-count case, two further errors interpreted an observed total of
  8 seizures over 2 months as a rate with a monthly denominator.

| Condition group | Jev correct complete answers | DeepSeek correct complete answers |
| --- | ---: | ---: |
| Base, including missing candidate | 3/7 | 7/7 |
| Changed quantities | 0/3 | 3/3 |
| Paraphrases | 2/4 | 4/4 |
| Complementary current seizure types | 1/1 | 1/1 |
| Reversed candidate/question/option order | 3/7 | 7/7 |

Both models correctly abstained when the correct candidate was omitted and when
one candidate could not represent two complementary current seizure types. All
seven order pairs had identical scored choices within each model. Reversal changed
several orderings together, so it cannot isolate their individual effects. Jev's
cluster paraphrase corrected the base cluster outer-value error, illustrating
wording sensitivity without establishing its cause. Quantity substitutions exposed
additional count/rate confusion. No prompts or keys were changed after evaluation.

All returned Jev probability maps covered their option sets, but six summed to
0.99 at the returned precision. They remain unchanged. This experiment scores
choices; it neither evaluates nor establishes probability calibration.

## Reference, method and decision

Keys were authored before evaluation and checked by DeepSeek V4 Pro in a fresh
source-only context without author answers or predictions. It agreed on all 14
distinct letters. Omission/order keys are mechanical derivatives. Codex reviewed
the rationales; another person's seizures are excluded for subject identity, with
no unsupported claim that they are non-epileptic. This is independent model review,
not a clinical reference panel; the reviewer shares a provider/model family with
one comparator. Both comparators received the same state and question definitions;
DeepSeek additionally received JSON-format instructions and thinking on/low.

The final-answer metric requires the primary choice and four attributes of the
expected selected candidate. The other candidates' attribute answers are not part
of the 157 scored decisions. No-current, missing and ambiguous cases have no
selected attributes. Role decisions are separately scored. Numerical range,
word-number, cross-sentence and complete-inventory extraction remain untested.
No native Purist/Pragmatic conversion or deterministic semantic repair was used.

**Decision: do not extend the current Jev design to dev750.** The repeated
applicability and quantity-binding errors are enough to stop this candidate before
a larger run. Jev's role classification warrants a possible narrower fictional
experiment, with explicit applicability questions and separately declared rules
for assembling fields. Any conditional masking changes clinical output and must
be treated as semantic logic, not an invisible formatting fix. Such an experiment
would need a new freeze; this result remains unchanged. A future dev750 evaluation
also needs candidate-coverage assessment, reviewed references and native mapping.

## Reproduction and evidence

- [Freeze](freeze.json): exact file hashes, settings, budget and stop policy.
- [Reference review](review_comparison.json): decisions and source-grounded rationales.
- [Machine report](report.json): all rows, field/group counts, costs and response hashes.
- [Analysis](analysis.json): error counts, paired order checks and decision.
- [Verification](verification.json): offline checks and full repository checks.
- [Jev response checks](jev_response_checks.json): probability precision observations.

Raw request/response/attempt records remain local under `runs/jev_fictional_v2/`.
All 44 comparison calls plus one review call completed with no retries or repairs.
Replay is offline and byte-identical:

```sh
.venv/bin/python -m scripts.benchmarks.jev_pilot report > /tmp/jev-report.json
cmp /tmp/jev-report.json results/letter-benchmarks/gan/jev_fictional_v2/report.json
```

836 always-on tests, Ruff, mypy (422 source files), standalone runner checks,
documentation hygiene and frozen-file checks passed. Existing R8 and annotation
work was preserved. The pilot used no dev750, locked-test or patient rows.
