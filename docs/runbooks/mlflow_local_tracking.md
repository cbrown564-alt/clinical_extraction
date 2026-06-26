# MLflow Local Tracking Runbook

MLflow is optional local observability for ExECTv2 and Gan 2026 runs. It helps
search, compare, and navigate experiment metadata. It is not the claim-of-record.

Canonical research evidence remains:

- predeclarations and report Markdown;
- selected JSON/JSONL artifacts;
- `experiments/registry.jsonl`;
- `experiments/RUN_INDEX.md`;
- `PROJECT_STATUS.md` when a durable decision changes.

See `docs/decisions/0034-mlflow-is-optional-observability.md` and
`docs/plans/mlflow_experiment_observability_implementation_plan_2026-06-25.md`.

## Install

From the repo root:

```powershell
uv pip install -e ".[dev,mlops]"
```

The base package works without MLflow. Install `mlops` only when you want the
local tracking UI or registry mirroring.

## Quick Health Check

Run the doctor before syncing or opening the UI:

```powershell
clinical-extraction-mlflow-doctor
```

Machine-readable output:

```powershell
clinical-extraction-mlflow-doctor --json
```

The doctor reports:

- whether MLflow is installed;
- tracking URI and environment flags;
- whether `mlruns/` and `experiments/registry.jsonl` exist;
- guardrail warnings about disabled mirroring, strict mode, and artifact policy.

Exit code `1` means mirroring is not ready yet, usually because MLflow is not
installed or mirroring is disabled.

## Environment Contract

| Variable | Meaning |
| --- | --- |
| `MLFLOW_TRACKING_URI` | Standard MLflow tracking URI. Defaults to `file:<repo>/mlruns`. |
| `MLFLOW_ALLOW_FILE_STORE` | Set automatically to `true` for the default repo-local file backend required by MLflow 3. |
| `CLINICAL_EXTRACTION_MLFLOW_DISABLED` | If `1`, skip all MLflow mirroring. |
| `CLINICAL_EXTRACTION_MLFLOW_STRICT` | If `1`, MLflow logging failures fail the command. Default is non-strict. |
| `CLINICAL_EXTRACTION_MLFLOW_ARTIFACT_POLICY` | `summary_only`, `selected_artifacts`, or `full_artifacts`. |
| `CLINICAL_EXTRACTION_MLFLOW_TRACE_POLICY` | Defaults to `disabled`. Do not enable on restricted surfaces. |

PowerShell example for an explicit local store:

```powershell
$env:MLFLOW_TRACKING_URI = "file:C:/Users/cbrow/Code/clinical_extraction/mlruns"
$env:MLFLOW_ALLOW_FILE_STORE = "true"
```

## Sync Registry Rows To MLflow

The sync command plans and optionally mirrors registry rows. Registry writes
happen elsewhere; sync only reads `experiments/registry.jsonl`.

Dry-run a recent slice:

```powershell
clinical-extraction-mlflow-sync --since-date 2026-06-24
```

Dry-run one run:

```powershell
clinical-extraction-mlflow-sync --run-id exectv2_2call_no_sf_adjudicator_gpt41mini_dev140
```

Mirror the first supported parent/child comparison group:

```powershell
clinical-extraction-mlflow-sync --same-core-dev140-group --sync
```

Machine-readable dry-run plan:

```powershell
clinical-extraction-mlflow-sync --same-core-dev140-group --json
```

### Artifact Policy

By default, sync logs selected summary artifacts and keeps row-level JSONL as
pointer-only. Restricted surfaces such as Gan `test450` and ExECTv2
`full200_aggregate` only copy aggregate-safe Markdown reports directly.

To plan direct logging for large or row-level artifacts on unrestricted
surfaces:

```powershell
clinical-extraction-mlflow-sync --include-large-artifacts --run-id <run_id>
```

Do not use `--include-large-artifacts` as a default. It can bloat `mlruns/`
quickly.

### Idempotency

Re-running `--sync` reuses an existing MLflow run when one is already mirrored
for the same `registry_run_id` or parent `comparison_id`. Tags, metrics, and
selected artifacts refresh on reuse. Params stay immutable after first create.

Historical duplicate runs created before ADR 0035 are not auto-merged. Delete
local `mlruns/` only when you intentionally want a fresh mirror.

## Start The Local UI

After at least one successful sync:

```powershell
$repo = "C:/Users/cbrow/Code/clinical_extraction"
$env:MLFLOW_TRACKING_URI = "file:$repo/mlruns"
mlflow server --backend-store-uri $env:MLFLOW_TRACKING_URI --port 5000
```

Open `http://127.0.0.1:5000`.

On Windows, use forward slashes in the `file:` URI. If the UI shows no runs,
confirm the tracking URI matches the store used by `--sync`.

## Recommended Filters

Use experiment names:

| Experiment | Contents |
| --- | --- |
| `clinical-extraction/exectv2` | ExECTv2 architecture runs, model swaps, aggregate audits |
| `clinical-extraction/gan2026` | Gan pipeline runs, replay analyses, scorecards |
| `clinical-extraction/reliability` | Cross-dataset reliability analyses |

Useful tags:

- `claim_status`
- `claim_boundary`
- `row_inspection_policy`
- `registry_canonical`
- `restricted_surface`
- `same_core_comparison`

Example questions the UI should answer:

- Which same-core model-swap children share one parent?
- Which runs are `aggregate_only` versus `allowed` for row inspection?
- Which rows are diagnostic-only versus operational candidates?

## Parent-Child Runs

The supported comparison group is:

```text
parent: exectv2_same_core_model_swap_dev140_20260625
  child: exectv2_2call_no_sf_adjudicator_gpt41mini_dev140
  child: exectv2_2call_no_sf_adjudicator_deepseek_dev140
  child: exectv2_2call_no_sf_adjudicator_qwen36_dev140
  child: exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_dev140
```

Parent runs hold comparison metadata and aggregate child metrics. Child runs
carry per-model params, metrics, and selected artifacts.

## Privacy And Split Guardrails

| Surface | MLflow metadata | Artifacts | Raw traces |
| --- | --- | --- | --- |
| Gan validation/dev | Allowed | Allowed when protocol permits | Disabled by default |
| Gan test450 | Aggregate only | Aggregate report only | Forbidden |
| ExECTv2 dev140 | Allowed | Allowed | Disabled by default |
| ExECTv2 full-200 aggregate | Aggregate only | Aggregate report/summary only | Forbidden |
| Holdout-like surfaces | Aggregate only | Aggregate report/summary only | Forbidden |

MLflow must not become a backdoor around row-inspection policy. If a surface is
aggregate-only in the research protocol, MLflow logs only aggregate-safe data.

## Troubleshooting

### MLflow not installed

```powershell
uv pip install -e ".[dev,mlops]"
clinical-extraction-mlflow-doctor
```

### Mirroring disabled

```powershell
Remove-Item Env:CLINICAL_EXTRACTION_MLFLOW_DISABLED -ErrorAction SilentlyContinue
```

### UI shows no experiments

1. Run `clinical-extraction-mlflow-doctor` and confirm `mlruns/` exists.
2. Confirm `MLFLOW_TRACKING_URI` matches the sync command.
3. Re-run a known-good sync:

```powershell
clinical-extraction-mlflow-sync --same-core-dev140-group --sync
```

### MLflow 3 file-store error

If sync fails with a file-store guardrail error, set:

```powershell
$env:MLFLOW_ALLOW_FILE_STORE = "true"
```

The default repo-local helper sets this automatically when `MLFLOW_TRACKING_URI`
is unset.

### Sync succeeded but core artifacts matter more

MLflow failures are non-strict by default. Registry rows, reports, and JSONL
artifacts remain authoritative even when mirroring returns `not mirrored`.

## Clean Local State Safely

`mlruns/` is gitignored local state. Delete it only when you intentionally want
to discard local mirrored runs:

```powershell
Remove-Item -Recurse -Force .\mlruns
```

Do not delete `experiments/registry.jsonl`, report Markdown, or source JSONL
artifacts. Those are the canonical record.

If you need a fresh local mirror after cleanup:

```powershell
clinical-extraction-mlflow-sync --same-core-dev140-group --sync
```

## What Not To Do

- Do not treat MLflow charts as promotion authority.
- Do not log raw note text, prompts, model outputs, or evidence snippets.
- Do not use MLflow to inspect Gan `test450` or ExECTv2 full-200 row-level
  failures for development.
- Do not commit `mlruns/` or `mlflow.db`.
