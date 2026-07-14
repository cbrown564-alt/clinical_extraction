# Data records and split rules

## Gan 2026 records

The source file is `data/Gan (2026)/synthetic_data_subset_1500.json`.

The loader preserves:

- `source_row_index`: stable row identifier;
- `clinic_date`: the full note text, despite the field name;
- the source seizure-frequency label and supporting text;
- author quality flags;
- `raw`: the complete source row;
- normalized label kind, yearly bounds, and monthly frequency used by Gan scoring.

See [Gan normalization](gan2026_normalization_semantics.md) for exact conversions.

## Required behavior

- Preserve source rows unchanged in `raw`.
- Keep Gan-specific label policy inside the Gan task.
- Keep `row_ok=False` rows and retain the flag for separate analysis.
- Use the fixed split definition; never treat all 1,500 rows as routine development data.
- Add tests before changing raw-label conversion or metric mapping.
- Preserve raw semantic labels separately from scoring sentinel values.
- Keep `unknown` distinct from `no seizure frequency reference`, even though
  the Gan scorer maps both to one category.
- Do not erase a frequency-bearing prediction merely because its phrase is hard
  to format. Preserve vague frequency, hourly rates, and cluster information
  according to the tested repair rules.
- Prefer the author evaluation script when it conflicts with the CSV preparation parser.
- Keep gold normalization, strict formatting repair, and clinical deterministic
  rules as separate tested steps.

## ExECT split names

- `dev140`: development rows; inspection allowed.
- `test60`: held-out rows; no row-level development.
- `full200`: dev140 plus test60. Report aggregate behavior only and never call
  it an independent holdout.

## Open design question

Decide whether future shared schemas should keep Gan's
`FrequencyLabelKind` names or map them to broader clinical terms.
