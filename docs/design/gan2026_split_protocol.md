# Gan 2026 data split rules

The full 1,500-row dataset must not be used as one development set. The fixed
split definition is `data/Gan (2026)/splits/gan2026_split_v1.json`.

## Train: 300 rows

Use only for GEPA or another optimizer that needs training examples. Do not use
these rows for manual prompt tuning, rule tuning, error analysis, or ordinary
development reporting.

## Validation: 750 rows

This is the development split. Row review is allowed. Use it for rules, prompts,
component removal, error analysis, scorer diagnostics, and model choice.

Model runs normally grow in this order:

1. 25 rows to catch call, parse, schema, evidence, and score-format failures;
2. 50 rows to compare a stable prompt or model condition;
3. 250 rows when the 50-row result gives a specific reason for a larger test;
4. all 750 rows only when the result will settle an important decision or enter
   a durable paper comparison.

When aggregate validation scores stop distinguishing candidates, test a named
failure type, hard-case subset, paraphrase set, component removal, or review
policy. Before another broad run, state the question, comparison, rows that may
be inspected, and stop rule. “See whether the score improves” is insufficient.

## Test: 450 rows

This is the locked holdout.

- Do not inspect row-level failures during development.
- Do not change prompts, rules, normalization, evidence selection, model,
  thresholds, or repairs based on the result.
- Run only after code, prompts, model, scorer, split version, and row policy have
  been fixed in a pre-run protocol.
- If the aggregate result reveals a problem, record it. Any fix begins a new
  validation cycle and requires a clearly separate future holdout evaluation.

## Split definition

`gan2026_split_v1` is deterministic and stratified by `gold_label_kind` and
`row_ok`. It records the source SHA-256, seed, row counts, source row indices,
and stratum counts. Do not edit or regenerate it to improve a result. A future
change requires a new version and a reason.

## Reporting

- Optimizer work on train, with or without validation, is optimizer development.
- Validation results are development results.
- Test results are holdout results only when the pre-run protocol was followed
  and no tuning follows.
- Call a result benchmark-comparable only when data, split, scorer, and
  replication procedure match the benchmark claim.
