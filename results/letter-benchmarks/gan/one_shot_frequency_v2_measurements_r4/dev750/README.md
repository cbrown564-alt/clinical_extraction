# Paired v2 r4 dev750 results

Completed 2026-09-14. Synthetic development evidence only; this previously exposed
split does not establish held-out generalization or clinical validity.

| Outcome | Rich | Simple |
| --- | --- | --- |
| Scheduled / responses received | 750 / 750 | 750 / 750 |
| Usable first outputs | 672 (89.6%) | 740 (98.7%) |
| Purist agreement, all rows | 521/750 (69.47%; 95% CI 66.08–72.66%) | 570/750 (76.00%; 95% CI 72.82–78.92%) |
| Pragmatic agreement, all rows | 564/750 (75.20%; 95% CI 71.99–78.16%) | 620/750 (82.67%; 95% CI 79.79–85.21%) |
| Invalid schema | 72 | 0 |
| Invalid target label | 6 | 10 |
| Transport/envelope/truncation failures | 0 | 0 |

Paired rich-minus-simple differences: purist −6.53 percentage points (95% paired
bootstrap CI −8.80 to −4.40); pragmatic −7.47 points (−9.73 to −5.33). Every
scheduled row, including failed outputs and row_ok=False, remains in the denominator.
Purist agreement conditional on usable outputs is 77.53% rich and 77.03% simple;
these have different denominators and are not a comparison on the same subset.

Model: DeepSeek V4.1 Flash (`deepseek-flash`); temperature 0, thinking disabled,
4,096 maximum output tokens each, concurrency 6. Prompt: `one_shot_frequency_v2_measurements_r4`.
Native purist/pragmatic scoring via the saved normalization/label source hashes;
analysis `one_shot_analysis_v1`, Wilson absolute intervals and 10,000 paired
letter-bootstrap replicates (seed 20260913). No retries or repairs. ChatAdapter
field extraction precedes strict schema/label validation. Raw provider responses
remain available independently of extracted JSON. The API alias is mutable;
returned model identities are recorded in the aggregate.

Exactly 1,500 unique requests and first responses cover 750 paired development
notes. Offline replay reproduced the aggregate byte for byte. No test or patient
rows were evaluated. The historical approximately 0.82 score is not a matched
comparison to these dev750 results.

Conservative peak-price charge for this run: US$3.2541282. Total including v1:
US$4.4273178 of the US$10 ceiling. This is usage-based peak cache-miss accounting,
not an invoice; discounts/cache hits may make actual charges lower.

Artifacts: [aggregate](aggregate.json), [verification](verification.json).
Local raw requests/responses, attempts, development diagnostics, plan and runtime
provenance: `runs/one_shot_frequency_v2_measurements_r4/dev750/`.
Schema-error counts in verification may count multiple errors in a single response.
The rich quotation totals currently cover accepted rich outputs; they should not
be read as quotation completeness across schema-invalid outputs.

Reproduce offline (no model calls):

```sh
.venv/bin/python -m clinical_extraction.tasks.seizure_frequency.gan2026.evaluation.one_shot_measurements_dev replay
```

Verification: 830 always-on tests, Ruff and mypy (415 source files) passed.
