# Gan 2026 V1 Deterministic Test Holdout

Date: 2026-05-31

## Purpose

Evaluate the frozen deterministic-only V1 pipeline on the locked Gan 2026
`test` split after validation saturation. This is a final holdout result for
the current deterministic candidate, not a benchmark-comparable paper claim.

No test row-level text, row-level failures, or error examples were inspected for
tuning during this check.

## Command

```bash
source .venv/bin/activate
python - <<'PY'
from collections import Counter
from clinical_extraction.tasks.seizure_frequency.gan2026.data import load_records_for_split
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluate import evaluate_predictions, convert_to_categories
from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline_v1 import Gan2026PipelineV1

records = load_records_for_split("test")
pipeline = Gan2026PipelineV1()
y_true = []
y_pred = []
evidence_valid = 0
pred_kinds = Counter()
gold_kinds = Counter()
row_ok = Counter()
correct_by_row_ok = Counter()
source_indices = []

for record in records:
    result = pipeline.run(record)
    final_selection = result.diagnostics["final_selection"]
    prediction = float(final_selection["monthly_frequency"])
    y_true.append(float(record.gold_monthly_frequency))
    y_pred.append(prediction)
    evidence_valid += bool(result.diagnostics.get("evidence_valid"))
    pred_kinds[str(final_selection["final_kind"])] += 1
    gold_kinds[str(record.gold_label_kind)] += 1
    row_ok[bool(record.row_ok)] += 1
    gold_category, prediction_category = convert_to_categories(
        [record.gold_monthly_frequency, prediction],
        method="purist",
    )
    if gold_category == prediction_category:
        correct_by_row_ok[bool(record.row_ok)] += 1
    source_indices.append(record.source_row_index)

print("rows", len(records))
print("source_index_minmax", min(source_indices), max(source_indices))
print("purist", evaluate_predictions(y_true, y_pred, method="purist"))
print("pragmatic", evaluate_predictions(y_true, y_pred, method="pragmatic"))
print("evidence_valid", evidence_valid, "/", len(records))
print("gold_kinds", dict(gold_kinds))
print("prediction_kinds", dict(pred_kinds))
print("row_ok_counts", dict(row_ok))
print("correct_by_row_ok", dict(correct_by_row_ok))
PY
```

## Metrics

Rows: 450

Source row index range: 31 to 17297

Purist final holdout metrics:

| Average | Precision | Recall | F1 | Accuracy |
| --- | ---: | ---: | ---: | ---: |
| micro | 0.7600 | 0.7600 | 0.7600 | 0.7600 |
| macro | 0.7557 | 0.7812 | 0.7516 | 0.7600 |
| weighted | 0.7740 | 0.7600 | 0.7607 | 0.7600 |

Pragmatic side-car metrics:

| Average | Precision | Recall | F1 | Accuracy |
| --- | ---: | ---: | ---: | ---: |
| micro | 0.7867 | 0.7867 | 0.7867 | 0.7867 |
| macro | 0.7697 | 0.7513 | 0.7545 | 0.7867 |
| weighted | 0.7982 | 0.7867 | 0.7879 | 0.7867 |

Evidence validity: 450 / 450 selected evidence strings were exact source
substrings.

## Label Mix

Gold semantic kinds:

| Kind | Count |
| --- | ---: |
| frequency | 281 |
| seizure_free | 67 |
| unknown | 60 |
| unresolved_multiple | 26 |
| no_reference | 16 |

Prediction semantic kinds:

| Kind | Count |
| --- | ---: |
| frequency | 271 |
| no_reference | 111 |
| seizure_free | 50 |
| unresolved_multiple | 18 |

Row quality:

| `row_ok` | Rows | Correct |
| --- | ---: | ---: |
| True | 430 | 322 |
| False | 20 | 20 |

## Interpretation

The deterministic-only V1 validation result of 0.9280 Purist micro F1/accuracy
does not hold on the locked test split. The 0.7600 Purist test result is strong
for a rules-only development baseline but is clear evidence of validation-surface
overfit and brittle rule accumulation.

The selected-evidence validity result remains excellent: every final evidence
span is an exact source substring. That supports the transparency claim, but it
does not rescue the generalization claim.

The appropriate next step is not to tune from this test result. Start a new
validation-only development cycle with deterministic rule ablations, category
labels, and LLM/DSPy reasoning experiments. Treat this test score as the frozen
final-holdout result for deterministic-only V1.
