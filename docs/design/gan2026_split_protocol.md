# Gan 2026 Split Protocol

## Purpose

Gan 2026 development must not use the full 1,500-row synthetic dataset as a single
iteration surface. Candidate rules, prompts, DSPy modules, and reporting should be
developed against a validation split, with a locked test split reserved for final
evaluation.

The split manifest lives at:

```text
data/Gan (2026)/splits/gan2026_split_v1.json
```

Companion one-split manifests live in the same directory as `train_v1.json`,
`validation_v1.json`, and `test_v1.json`; these mirror the master manifest rows
for external scripts and manual inspection.

## Split Roles

### Train

- Count: 300 rows.
- Intended use: DSPy GEPA or another optimizer that needs training examples.
- Do not use it for manual prompt tuning, deterministic-rule tuning, exploratory
  error analysis, or reporting ordinary development results.
- If no optimizer is being trained, leave this split unused.

### Validation

- Count: 750 rows.
- Intended use: the primary development surface.
- Use this split for deterministic-rule iteration, prompt strategy comparisons,
  ablations, row-level error analysis, scorer-facing diagnostics, and model-choice
  decisions.
- Report ordinary progress as validation development results.

### Test

- Count: 450 rows.
- Intended use: locked holdout final evaluation.
- Do not inspect test row-level failures while developing.
- Do not change prompts, rules, normalization, evidence selection, DSPy programs,
  model choice, thresholds, or repair logic based on test performance.
- Run it only after a candidate and its evaluation protocol are frozen.

## Manifest Policy

`gan2026_split_v1` is deterministic and stratified by:

- `gold_label_kind`
- `row_ok`

The manifest records the source dataset SHA-256, seed, row counts, intended split
uses, source row indices, and per-split stratum counts. Source rows remain in the
original JSON; manifests contain only row identifiers and metadata.

Do not regenerate or edit `gan2026_split_v1` to improve a result. If a future
protocol change is necessary, create a new manifest version and document why the
old split is insufficient.

## Reporting Language

- Train-only or train-plus-validation optimizer work is an optimizer development
  result.
- Validation work is a development result.
- Test work is a final holdout result only if the candidate was frozen before the
  test run and no tuning follows from the result.
- Do not call any local result a benchmark result until the data surface, split,
  scorer, and replication policy are explicitly benchmark-comparable.

## Allowed Workflow

1. Develop deterministic rules, prompt strategies, and ablations on validation.
2. Use train only when running DSPy GEPA or another training/optimization procedure.
3. Freeze code, prompts, model identifiers, scorer, and split manifest version.
4. Run the locked test split once for final evaluation.
5. If test reveals a problem, record it as a final-evaluation finding. Any fix starts
   a new development cycle on validation and requires a later, clearly separated
   holdout evaluation.
