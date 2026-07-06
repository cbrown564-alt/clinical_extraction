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

## Split Surface

Gan 2026 split policy lives in `docs/design/gan2026_split_protocol.md`. The locked
v1 manifest is:

```text
data/Gan (2026)/splits/gan2026_split_v1.json
```

Use validation, not the full dataset, for ordinary deterministic-rule, prompt,
ablation, and error-analysis work. Reserve train for DSPy GEPA or another optimizer
that needs training examples. Treat test as a locked final holdout and never tune
on it.

## Contract Principles

- Preserve original rows untouched in `raw`.
- Keep benchmark-specific label policy inside `gan2026`.
- Include `row_ok=False` rows in the development/evaluation surface, while retaining the flag for stratified analysis.
- Use explicit split manifests for development and holdout evaluation; do not treat
  all 1,500 rows as the default iteration surface.
- Add tests before changing any conversion from raw labels to numeric rates or categories.
- Preserve raw semantic labels separately from scoring sentinels where possible.
- Treat `unknown` and `no seizure frequency reference` as distinct raw states even though Gan scoring maps both to the unknown category.
- Do not demote a frequency-bearing prediction to `no seizure frequency reference`
  merely because the scorer-facing surface is awkward. H5 repair policy v1 keeps
  vague frequency words as unresolved-multiple labels, maps per-hour rates to
  `multiple per day`, and preserves cluster frequency content when cluster
  context is present.
- Prefer the author evaluation-script scoring policy where it conflicts with the CSV-preparation parser.
- Keep clean scorer-facing gold-normalization policy separate from strict
  benchmark-format repair and from named deterministic semantic modules. The
  first adopted validation-only policy slice is cluster-name stripping for
  cadence-only cluster labels, vague weekday cadence to `multiple per week`, and
  Gan-specific bare `bimonthly` to `1 per 2 month`; the rationale and boundary
  cases live in `docs/research/gan2026/data_and_policy/gan2026_gold_normalization_policy_question_2026-06-01.md`.

## Known Open Questions

- Whether later task-neutral schemas should reuse the Gan-specific `FrequencyLabelKind` names or map
  them into broader clinical-extraction ontology terms.
