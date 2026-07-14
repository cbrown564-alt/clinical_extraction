# 03 — Evidence and frozen artifacts

Last updated: 2026-07-14

## Authority

Use this order when records disagree:

1. present artifact plus recomputed hash;
2. [retained evidence manifest](../experiments/retained_evidence_manifest.md);
3. the claims register and scoring canon;
4. current source and tests;
5. the retained run registry.

Deleted experiment history remains available in Git. It is not active evidence.

## Split boundaries

| Split | Row inspection | Permitted use |
| --- | --- | --- |
| ExECT dev140 | Allowed | Development, replay, and permitted error analysis |
| Gan validation750 | Allowed | Development comparison and component analysis |
| ExECT full200 | Aggregate only | Development-inclusive audit; not independent holdout evidence |
| Gan test450 | Forbidden | Frozen aggregate citation only |

Normal project commands must not expose Gan test450 or ExECT test60 rows for
development.

## Retention rule

A machine artifact remains only when the manifest selects it or an executable
reference closure needs it. A document remains when it is:

- a canonical owner;
- a current design, decision, or runbook;
- a manuscript source; or
- a manifest-selected evidence report.

Do not keep redirect stubs, duplicate syntheses, generated row dossiers, or
candidate narratives. Do not rename manifest-selected paths without updating
their hashes and rerunning both evidence checks.

## Verification

```sh
source .venv/bin/activate
python scripts/check_retained_evidence_manifest.py
python scripts/verify_reference_evidence.py
```

