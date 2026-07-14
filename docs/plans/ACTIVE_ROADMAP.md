# Active roadmap

Last updated: 2026-07-14

[Project status](../../PROJECT_STATUS.md) owns current evidence and checks.
[Paper provenance](../canon/10_paper_provenance.md) owns claim strength.

## Objective

Close the named paper evidence gaps on the verified, frozen reduced
architecture without weakening split or claim boundaries.

Gan test450 remains aggregate-only. ExECT full200 remains a
development-inclusive aggregate audit.

## Completed foundation

1. **Repository reduced.** Historical documents, artifacts, candidates,
   report/catalog machinery, and the secondary UI product were removed.
2. **Engineering gates restored.** Ruff, mypy, full pytest, prompt snapshots,
   manifest validation, and all six no-call reference replays are green; CI
   enforces the three repository-wide quality gates.
3. **Architecture frozen.** Manifest v3 pins source commit `46562134`,
   Python/dependencies, the six reference cells, and exact prompt, scorer,
   split, repair, model, runbook, and CI policies.
4. **Fresh checkout and paper synchronized.** A separate Python 3.11 checkout
   retrieved the Git LFS evidence, passed hashes and split barriers, replayed
   all six cells, passed the full suite, and reproduced the retained tables.
   The Markdown and IEEE sources now contain only manifest-retained evidence
   and explicit claim boundaries.

## Ordered evidence work

1. Build the matched Gan calls, tokens, cost, latency, hardware, and cache-policy
   comparison for the operational pass and multi-trace ceiling.
2. Reproduce ExECT normalized phrase, CUI, and full-attribute scoring on the
   paper-comparable surface.
3. Evaluate model confidence out of sample and test only predeclared bounded
   review-routing policies.
4. Complete the paper-facing annotation taxonomy and sensitivity ledger.
5. Predeclare the missing three runtime conditions, then run the frozen
   six-model comparison with one component graph and scorer.

## Boundaries

- GEPA optimization is closed; one saved LLM-only cell remains a negative
  comparator.
- Gan V12 source is removed; its aggregate ceiling report remains.
- No ExECT Wall-transfer claim is active because no selected transfer artifact
  remains.
- MLflow, the frontend, and Observatory are outside the retained deliverable.
- The five largest selected ExECT replay artifacts are immutable Git LFS
  objects with identities and retrieval metadata in the retained manifest.
- The freeze does not authorize model calls or locked-row inspection.

## Verification commands

```sh
uv sync --python 3.11 --frozen --extra dev
python scripts/check_retained_evidence_manifest.py
python scripts/verify_reference_evidence.py
python -m pytest
python -m ruff check .
python -m mypy src
```
