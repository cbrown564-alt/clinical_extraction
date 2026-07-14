# Active roadmap

Last updated: 2026-07-14

[Project status](../../PROJECT_STATUS.md) owns current evidence and checks.
[Paper provenance](../canon/10_paper_provenance.md) owns claim strength.

## Objective

Verify the reduced, frozen architecture from a fresh checkout, then close the
named paper evidence gaps without weakening split or claim boundaries.

Gan test450 remains aggregate-only. ExECT full200 remains a
development-inclusive aggregate audit.

## Order

1. **Engineering checks restored (complete).** Ruff, mypy, all 1,153 tests,
   prompt snapshots, manifest validation, and all six reference replays are
   green. CI enforces Ruff, mypy, and the full suite.
2. **Architecture frozen (complete).** Manifest v3 pins source commit
   `46562134`, Python/dependencies, the six reference cells, and exact prompt,
   scorer, split, repair, model, runbook, and CI policies. The freeze does not
   authorize model calls.
3. **Close from a fresh checkout.** Install, enforce split barriers, replay both
   tasks, verify hashes, rebuild surviving tables, and sync the manuscript and
   IEEE source.
4. **Run open evidence work.**
   - matched Gan calls, tokens, cost, and latency;
   - deterministic ExECT phrase/CUI/full-attribute reproduction;
   - out-of-sample model confidence and bounded review routing;
   - complete annotation taxonomy and sensitivity analysis;
   - predeclare the missing three runtime conditions, then run the frozen
     six-model comparison.

## Current boundaries

- GEPA optimization is closed; one saved LLM-only cell remains as a negative
  comparator.
- Gan V12 source is removed; its aggregate ceiling report remains.
- No ExECT Wall-transfer claim is active because no selected transfer artifact
  remains.
- MLflow, the frontend, and Observatory are outside the retained deliverable.
- Historical plans and experiment narratives are available through Git history,
  not the active documentation tree.
- The five largest selected ExECT replay artifacts are immutable Git LFS
  objects with IDs and retrieval metadata in the retained manifest.

## Completion checks

```sh
source .venv/bin/activate
python scripts/check_retained_evidence_manifest.py
python scripts/verify_reference_evidence.py
python -m pytest
python -m ruff check .
python -m mypy src
```

