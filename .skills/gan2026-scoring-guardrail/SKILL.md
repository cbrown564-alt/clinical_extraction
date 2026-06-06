---
name: gan2026-scoring-guardrail
description: Protect Gan 2026 seizure-frequency evaluation scoring in the clinical-extraction repo. Use when changing label normalization, allowed label formats, parse bounds, cluster handling, sentinel values, Purist or Pragmatic mapping, evaluation reports, row_ok policy, data splits, post-processing repair that affects labels, or claims about F1, threshold success, or benchmark comparability.
---

# Gan 2026 Scoring Guardrail

Use this skill whenever the meaning of a label, score, or benchmark claim could change. Its job is to prevent accidental evaluator drift.

## Environment

Use the `clinical-extraction-env` skill before scorer imports, focused tests,
full tests, or evaluation scripts. If `clinical_extraction` cannot be imported,
repair `.venv` / editable install before touching scorer logic.

## Required Context

Read these before modifying scoring-policy behavior:

- `docs/design/data_contract.md`
- `docs/design/gan2026_split_protocol.md`
- `docs/runbooks/gan2026_first_milestone.md`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/labels.py`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/evaluate.py`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/normalize.py` when normalization is involved
- `data/Gan (2026)/previous implementation/` when reconciling author behavior

## Contract Rules

- Preserve the distinction between numeric frequency, `unknown`, `no seizure frequency reference`, and seizure-free.
- Keep Gan-specific scoring policy inside `clinical_extraction.tasks.seizure_frequency.gan2026`.
- Treat `row_ok=False` rows as quarantine/debug-only until the benchmark protocol is explicit.
- Keep label conversion explicit and tested.
- Do not silently smooth parse failures into successful labels.
- Do not silently smooth model prediction failures into successful labels via
  semantic post-processing while still claiming the score as model-selected.
- Any evaluator behavior change needs a documented reason tied to author behavior, paper policy, or a deliberate project policy decision.
- Do not describe local synthetic results as final benchmark results.
- Use the explicit Gan split manifest for reported evaluation surfaces:
  - validation is the default development surface;
  - train is reserved for DSPy GEPA or another optimizer;
  - test is a locked final holdout and must not drive tuning.
- Do not evaluate on all 1,500 rows for ordinary candidate iteration unless the task is explicitly about whole-dataset inspection or split-policy maintenance.

## Label And Scoring Workflow

1. Add or update pytest coverage before changing behavior.
2. Compare intended behavior with the previous implementation when porting author logic.
3. Pin sentinel handling:
   - seizure-free/currently no seizure maps to zero frequency behavior.
   - unknown frequency remains distinct from no-reference rows.
   - cluster expressions preserve cluster count and per-cluster count until conversion policy is explicit.
4. Verify Purist and Pragmatic mappings after changes.
5. Update `docs/design/data_contract.md` if policy changes.
6. Run:

```bash
source .venv/bin/activate
python -m pytest
python -m ruff check .
```

## Claim Language

- Use "development result" for ordinary iteration.
- Use "validation development result" when iterating on `gan2026_split_v1` validation rows.
- Use "hybrid development artifact" when the score depends on named
  deterministic semantic repair after LLM output.
- Use "diagnostic no-call reparse" when saved raw outputs are rescored through
  changed parser, normalization, or repair code.
- Use "LLM-first validation result" only after same-raw-output attribution shows
  the metric is not primarily produced by semantic repair.
- Use "final holdout result" only for a frozen candidate evaluated on `gan2026_split_v1` test rows, with no follow-on tuning from the result.
- Use "local replication-proxy result" only after the data surface and scorer are stable and documented.
- Use "benchmark result" only when data, scorer, split, and protocol match the paper closely enough to support that claim.
- Use "not comparable yet" when evaluator, data, or split policy is unresolved.
