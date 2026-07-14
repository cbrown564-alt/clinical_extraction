# 03 — Evidence priority and data limits

Last updated: 2026-07-14

## When records disagree

Use this order:

1. a present file whose hash has been recomputed;
2. the [retained evidence index](../experiments/retained_evidence_manifest.md);
3. current paper claim and scoring summaries;
4. current source and tests;
5. the retained run registry.

Deleted history remains available in Git but is not current evidence.

## Data splits

| Split | May rows be inspected? | Permitted use |
| --- | --- | --- |
| ExECT dev140 | Yes | Development, replay, and error analysis |
| Gan validation750 | Yes | Development comparisons and component analysis |
| ExECT full200 | No row review of test60 | Aggregate development-inclusive check; not an independent holdout |
| Gan test450 | No | Cite saved aggregate results only |

Routine commands must not expose Gan test450 or ExECT test60 rows for
development.

## What stays in the repository

A machine-readable output remains only when the retained evidence index selects
it or a selected replay needs it. A document remains when it owns a current
decision, procedure, paper section, or selected result. Do not rename a selected
path without updating its hash and rerunning both evidence checks.
