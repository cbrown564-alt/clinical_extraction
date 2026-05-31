# Data Contract

## Immediate Dataset

Gan 2026 data lives at:

```text
data/Gan (2026)/synthetic_data_subset_1500.json
```

The initial loader treats each row as:

- `source_row_index`: stable source identifier
- `clinic_date`: full clinical note text, despite the field name
- `raw`: complete original row for gold labels and quality flags

## Contract Principles

- Preserve original rows untouched in `raw`.
- Keep benchmark-specific label policy inside `gan2026`.
- Do not silently drop rows based on quality flags until the benchmark protocol is explicit.
- Add tests before changing any conversion from raw labels to numeric rates or categories.

## Known Open Questions

- Which raw field is the canonical gold label for seizure frequency?
- Which row quality flags should define the first development/evaluation subset?
- How should no-reference, unknown, and seizure-free labels be represented in the final schema?

