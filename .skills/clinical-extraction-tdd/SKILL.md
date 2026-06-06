---
name: clinical-extraction-tdd
description: Apply test-driven development in the clinical-extraction repo. Use when implementing or modifying Gan 2026 data loading, label parsing, normalization, post-processing repair, Purist or Pragmatic category mapping, scoring, schema validation, evidence checks, pipeline behavior, baselines, run records, or any repo change where tests should pin behavior before implementation.
---

# Clinical Extraction TDD

Use this skill to keep the clinical-extraction project small, reproducible, and honest. The evaluator and label policy are contract surfaces; accidental drift is expensive.

## Environment

Use the `clinical-extraction-env` skill for every Python import, pytest/Ruff run,
notebook command, or ad hoc script. Activate `.venv` before running package code;
if imports fail, repair the editable dev install before changing code.

## Workflow

1. Read the relevant contract first: `README.md`, `PROJECT_STATUS.md`, and the narrow doc under `docs/design/` or `docs/runbooks/`.
2. Identify the behavior being changed or preserved.
3. Write the smallest failing pytest first.
4. Prefer tiny hand-built fixtures for parser, scorer, schema, and evidence behavior.
5. Use the real Gan JSON only for integration tests that need loader/data-contract coverage.
6. Implement the narrowest change needed to pass.
7. Add regression cases for edge cases discovered during implementation.
8. Run the targeted test file while iterating, then run the full suite inside `.venv`.
9. Run Ruff inside `.venv` before finishing if code changed.
10. Mention any remaining untested risk in the final response.

## Repair And Normalization Tests

When testing post-processing, pin the boundary being tested:

- Format-only normalization tests must show the selected fact is preserved.
  Acceptable changes include schema compatibility, parser-compatible syntax,
  allowed unit spelling, and arithmetic over the already selected fact.
- Semantic repair tests must name the deterministic rule family and assert its
  portability category: `general`, `clinical_epilepsy`, `seizure_frequency`,
  `gan2026_specific`, or `benchmark_format`.
- Any test where repair changes Purist/Pragmatic category, sentinel state,
  selected event, denominator/window policy, cluster interpretation, or
  semantic kind must be treated as deterministic-rule coverage, not
  normalization coverage.
- Add regression tests for raw-correct to repaired-wrong risk when a repair
  family is broad enough to affect multiple row types.

## Test Surfaces

- `tests/test_gan2026_data.py`: loader shape, source row identity, quality flags, note-text field, row-count smoke tests.
- `tests/test_gan2026_labels.py`: Purist/Pragmatic category boundaries and sentinel behavior.
- Add focused files as modules mature, for example `test_gan2026_normalize.py`, `test_gan2026_evaluate.py`, `test_evidence.py`, and `test_pipeline_v1.py`.
- Add rule-taxonomy tests when deterministic rules are introduced, especially where general rules and Gan-specific rules could be confused.

## Fixture Rules

- Keep parser/scorer tests deterministic and independent from model calls.
- Do not use locked or future evaluation examples as exploratory fixtures.
- Do not rewrite tests merely to bless a candidate's current output.
- Include edge cases for `unknown`, `no seizure frequency reference`, seizure-free labels, ranges, clusters, `multiple`, denominators, and evidence substring checks.
- For deterministic rules, include tests that show the rule category and intended portability: general, clinical epilepsy, seizure-frequency, Gan-specific, or benchmark-formatting.
- For LLM pipeline tests, preserve fixtures or assertions that expose raw model
  label, format-only label, selected-evidence repair label, and final label when
  those stages exist.

## Verification Commands

Use the repo environment:

```bash
source .venv/bin/activate
python -m pytest
python -m ruff check .
```

If the environment does not exist, create it with:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```
