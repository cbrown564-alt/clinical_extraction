# Active roadmap

Last updated: 2026-07-14

[Project status](../../PROJECT_STATUS.md) owns current evidence and checks.
[Paper provenance](../canon/10_paper_provenance.md) owns claim strength.

## Objective

Finish repository surgery, freeze the reduced architecture, close the named
paper evidence gaps, and verify the result from a fresh checkout.

Gan test450 remains aggregate-only. ExECT full200 remains a
development-inclusive aggregate audit.

## Order

1. **Engineering checks restored (complete).** Ruff, mypy, all 1,150 tests,
   prompt snapshots, manifest validation, and all six reference replays are
   green. CI enforces Ruff, mypy, and the full suite.
2. **Freeze the architecture.** Record the exact prompt, scorer, split, repair,
   and model policies before new calls.
3. **Run open evidence work.**
   - matched Gan calls, tokens, cost, and latency;
   - deterministic ExECT phrase/CUI/full-attribute reproduction;
   - out-of-sample model confidence and bounded review routing;
   - complete annotation taxonomy and sensitivity analysis;
   - remaining three models in the frozen six-model comparison.
4. **Close from a fresh checkout.** Install, enforce split barriers, replay both
   tasks, verify hashes, rebuild surviving tables, and sync the manuscript and
   IEEE source.

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

