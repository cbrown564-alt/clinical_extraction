# Data Contract

## Immediate Dataset

Gan 2026 data lives at:

```text
data/Gan (2026)/synthetic_data_subset_1500.json
```

The initial loader treats each row as:

- `source_row_index`: stable source identifier
- `clinic_date`: full clinical note text, despite the field name
- `check__Seizure Frequency Number.seizure_frequency_number[0]`: canonical local gold seizure-frequency label
- `check__Seizure Frequency Number.reference[-1]`: local gold evidence/reference text
- `labels_match_all_categories`, `quotes_ok_all_categories`, `row_ok`: author quality flags
- `raw`: complete original row for gold labels and quality flags
- `gold_normalized_label`, `gold_label_kind`, `gold_yearly_bounds`, `gold_monthly_frequency`:
  tested Gan-specific conversion fields that preserve raw semantic state before scoring collapse

See `docs/design/gan2026_normalization_semantics.md` for the normalization and semantic
conversion contract.

## Contract Principles

- Preserve original rows untouched in `raw`.
- Keep benchmark-specific label policy inside `gan2026`.
- Include `row_ok=False` rows in the development/evaluation surface, while retaining the flag for stratified analysis.
- Add tests before changing any conversion from raw labels to numeric rates or categories.
- Preserve raw semantic labels separately from scoring sentinels where possible.
- Treat `unknown` and `no seizure frequency reference` as distinct raw states even though Gan scoring maps both to the unknown category.
- Prefer the author evaluation-script scoring policy where it conflicts with the CSV-preparation parser.

## Known Open Questions

- Whether later task-neutral schemas should reuse the Gan-specific `FrequencyLabelKind` names or map
  them into broader clinical-extraction ontology terms.
