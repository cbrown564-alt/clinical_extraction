# Gan 2026 V1 Deterministic Baseline

Date: 2026-05-31

## Purpose

First schema-shaped deterministic extraction baseline for Gan 2026 seizure-frequency
letters. This is a development result, not a benchmark claim.

The baseline extracts simple candidate events, normalizes them through the
Gan-compatible label code, records a final selection, and validates that selected
evidence is an exact source substring.

## Command

```bash
source .venv/bin/activate
python -m pytest tests/test_gan2026_pipeline_v1.py
python -m pytest
python -m ruff check .
```

The full-surface scoring used `Gan2026PipelineV1` over
`load_records_with_monthly_frequency()` and `evaluate_frequency_records(...,
method="purist")`.

## Metrics

Rows: 1,500

Purist development metrics:

| Average | Precision | Recall | F1 | Accuracy |
| --- | ---: | ---: | ---: | ---: |
| micro | 0.3120 | 0.3120 | 0.3120 | 0.3120 |
| macro | 0.4126 | 0.1895 | 0.1850 | 0.3120 |
| weighted | 0.4964 | 0.3120 | 0.2532 | 0.3120 |

Prediction semantic kinds:

| Kind | Count |
| --- | ---: |
| frequency | 193 |
| no_reference | 1,171 |
| seizure_free | 105 |
| unknown | 13 |
| unresolved_multiple | 18 |

Evidence validity: 1,500 / 1,500 selected evidence strings were exact source
substrings.

## Slices

| Slice | Correct / Total | Accuracy |
| --- | ---: | ---: |
| all | 468 / 1,500 | 0.3120 |
| gold_kind=frequency | 119 / 937 | 0.1270 |
| gold_kind=seizure_free | 34 / 223 | 0.1525 |
| gold_kind=unknown | 193 / 200 | 0.9650 |
| gold_kind=no_reference | 54 / 54 | 1.0000 |
| gold_kind=unresolved_multiple | 68 / 86 | 0.7907 |
| gold_has_cluster | 24 / 151 | 0.1589 |
| gold_has_range | 68 / 255 | 0.2667 |
| gold_has_multiple | 82 / 277 | 0.2960 |
| row_ok=True | 414 / 1,435 | 0.2885 |
| row_ok=False | 54 / 65 | 0.8308 |

The high unknown/no-reference slice score is mostly scorer collapse: both states
map to the unknown category in Gan Purist scoring. The semantic predictions show
that the baseline is over-defaulting to `no seizure frequency reference`.

## Early Failure Read

Dominant failures:

- Missed ordinary frequency evidence when counts are distributed across several
  clauses or months.
- Missed interval and date-derived rates, such as median inter-seizure interval
  or month-by-month event counts.
- Missed many seizure-free statements expressed as absence of events rather than
  an explicit duration.
- Missed cluster expressions unless phrased as a tidy cluster count plus
  per-cluster count.
- Selected seizure-free state incorrectly when a later breakthrough seizure
  created the benchmark rate.

## Next Experiment

Improve deterministic candidate recall before adding LLM reasoning:

- count distributed month lists and recent-window event totals;
- add interval patterns such as `every 4 days` and `inter-seizure interval`;
- expand seizure-free/no-event phrasing while guarding against breakthrough
  events;
- add row-level error table generation for top missed gold kinds.
