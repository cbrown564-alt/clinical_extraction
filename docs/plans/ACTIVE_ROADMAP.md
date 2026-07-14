# Active roadmap

Last updated: 2026-07-14

[Project status](../../PROJECT_STATUS.md) owns current evidence and checks.
[Paper claim status](../canon/10_paper_provenance.md) owns claim strength.

## Objective

Close the paper's named evidence gaps without changing the verified pipeline,
data splits, or limits on what each result supports.

Gan test450 remains aggregate-only. ExECT full200 combines development and
held-out rows, so it is not an independent holdout.

## Completed foundation

1. **Repository reduced.** Historical documents, saved outputs, unused
   candidates, reporting machinery, and the secondary UI were removed.
2. **Engineering checks restored.** Ruff, mypy, full pytest, prompt snapshots,
   retained-evidence validation, and all six reference replays pass. CI runs
   the three repository-wide checks.
3. **Pipeline fixed for new evidence.** Retained evidence index v3 records source
   commit `46562134`, Python and dependency versions, the six reference runs,
   and the exact prompt, scorer, split, repair, model, runbook, and CI policies.
4. **Clean checkout and paper checked.** A separate Python 3.11 checkout
   retrieved the Git LFS evidence, checked hashes and split restrictions,
   replayed all six runs, passed the full suite, and reproduced the tables. The
   Markdown and IEEE sources now use only selected evidence and state what each
   result can support.
5. **Gan efficiency closed with a bounded result.** On saved test450 aggregates,
   V12 gains 15 Purist-correct rows while requiring three cold model passes per
   note rather than one. Matched token, cost, latency, hardware, and cache
   telemetry was not retained, so those claims were removed instead of
   reconstructed from incompatible runs.

## Ordered evidence work

1. Reproduce ExECT normalized phrase, CUI, and full-attribute scores using the
   published metrics.
2. Evaluate model confidence out of sample and test only review policies that
   were specified before the run.
3. Complete the paper's annotation taxonomy and sensitivity record.
4. Specify the missing three runtime conditions, then run all six models with
   the same pipeline and scorer.

## Limits

- GEPA optimization is closed; one saved LLM-only run remains as a negative
  comparison.
- The source for the Gan multi-model comparator (`V12`) was removed; its
  aggregate report remains.
- No cross-task ExECT over-reading claim is active because no selected report
  supports it.
- MLflow, the frontend, and Observatory are outside the retained deliverables.
- The five largest selected ExECT replay files are immutable Git LFS objects;
  the retained evidence index records their identities and retrieval details.
- Fixing the pipeline does not authorize model calls or locked-row inspection.

## Verification commands

```sh
uv sync --python 3.11 --frozen --extra dev
python scripts/check_retained_evidence_manifest.py
python scripts/verify_reference_evidence.py
python -m pytest
python -m ruff check .
python -m mypy src
```
