# Decision 0048 retention slice: unserved ExECT mock-data

Date: 2026-08-02  
Status: **deleted**  
Decision: [0048](../../decisions/0048-comprehension-and-handoff-refactor.md) broader corpus triage  
Inventory: explore agent mock-data leftovers audit

## Scope

| Path | Action |
| --- | --- |
| `frontend/public/mock-data/exectv2/artifacts/exectv2_holistic_finding_assembly_v08_dev140_p7fix_gpt41mini_20260702.json` (~1.9 MB) | Deleted |
| `frontend/public/mock-data/exectv2/artifacts/` (empty after delete) | Removed |
| `frontend/public/mock-data/exectv2/component-ablation.json` (~241 KB) | Deleted |
| `frontend/public/mock-data/exectv2/component-transitions.json` (~207 KB) | Deleted |

Out of scope: root `mock-data/artifacts/` (still served; keep per earlier slice);
`registry.json` stale `artifact_paths` metadata (defer); Gan ablation mocks (kept,
retagged).

## Dependency checks

- `FrontendDataStore` globs only `mock-data/artifacts/*.json`, not
  `exectv2/artifacts/`.
- `GET /exectv2/component-ablation` and `/exectv2/component-transitions` return
  404 by design after the supervisor-path removal; no `_NAMED_RESOURCES` entry
  and no frontend fetch helpers.
- Retained-evidence manifest and six reference replays use `experiments/`
  paths for the p7fix / p7_treatment hybrid reference cell, not these mocks.
- No test imported the deleted paths.

## Decision rationale

None of the three files explained the system, demonstrated a selected method on
the supervisor path, supported a named claim, or were required to reproduce a
selected result. Canonical hybrid replay remains under `experiments/`. ExECT
component-impact evidence remains in retained experiment reports.

Recovery: Git history.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests/test_trace_explorer_frontend_api.py -q
```
