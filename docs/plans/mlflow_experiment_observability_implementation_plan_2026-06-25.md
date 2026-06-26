# MLflow Experiment Observability Implementation Plan

Date: 2026-06-25  
Scope: local-first MLflow tracking for Gan 2026 and ExECTv2 experiment observability  
Protocol boundary: `experiments/registry.jsonl` remains the canonical claim-of-record; MLflow is an index, comparison, artifact, and optional trace layer. No locked holdout or ExECTv2 full-200 row-level trace logging is authorized by this plan.

Rationalisation status, 2026-06-25: future infrastructure. Start only with
Phase 0-1 after the current reporting/run-surfacing sequence is stable. MLflow
must remain optional observability; the registry, run index, and reports remain
canonical. See `docs/plans/recent_plan_rationalisation_2026-06-25.md`.

Implementation status, 2026-06-26: Phase 0-1 and the Phase 2 dry-run path are
complete. The repo now has ADR 0034, an optional `mlops` dependency, gitignored
local MLflow state, `src/clinical_extraction/core/mlflow_tracking.py`, and
`src/clinical_extraction/core/mlflow_registry_sync.py` with
`scripts/sync_registry_to_mlflow.py` / `clinical-extraction-mlflow-sync`.
Dry-run sync loads typed registry rows, emits MLflow payload summaries, and
keeps restricted row-level artifacts pointer-only. MLflow is still not the
claim-of-record.

## Objective

Add MLflow to this project as a lightweight research-MLOps layer that makes
existing experiment work easier to search, compare, reproduce, and debug without
weakening the project protocol.

MLflow should answer operational questions quickly:

- Which runs used the same candidate architecture, split, scorer, and model?
- Which run artifacts, configs, reports, and predeclarations belong together?
- Which model-swap rows are comparable, and which are diagnostic-only?
- Where did parse/schema/call failures appear?
- What changed between a promoted row, a rejected row, and a repair attempt?
- How much latency/cost/runtime instability did a model introduce?

MLflow should not become the authority for paper claims. The durable research
record remains:

```text
predeclaration/report Markdown
raw JSONL/JSON artifacts
experiments/registry.jsonl
experiments/RUN_INDEX.md
PROJECT_STATUS.md when a durable decision changes
```

## Current Repo Fit

The project already has the right scientific substrate:

- locked split manifests;
- predeclarations and audit protocols;
- typed run-registry entries;
- human-readable `RUN_INDEX.md`;
- JSONL row artifacts;
- reliability scorecards;
- component-impact and attribution reports;
- an Observatory frontend over the registry and selected artifacts.

MLflow adds a searchable experiment UI and a standard run metadata surface. It
should mirror and enrich the existing artifacts rather than replacing them.

## Research Claims Protected

This plan protects four project claims:

- **Transparency:** MLflow links every run to artifacts, configs, reports,
  evidence-validity summaries, and operational failure counts.
- **Generalisation discipline:** split, surface, row-inspection policy, replay
  status, and claim boundary are first-class tags.
- **Attribution discipline:** MLflow records whether a run is `rules_only`,
  `llm_only`, `hybrid`, `analysis_only`, or diagnostic, and does not collapse
  deterministic repair into model credit.
- **Operational reproducibility:** model endpoint, provider, local runtime,
  quantization, prompt/program version, git state, cache/reuse state, latency,
  and failure modes are captured consistently.

## MLflow Features To Use

Use these MLflow capabilities first:

| Feature | Use in this repo | Notes |
| --- | --- | --- |
| Tracking runs | One MLflow run per registered run or analysis artifact family. | Local `mlruns` first. |
| Experiments | Group by project surface: `clinical-extraction/exectv2`, `clinical-extraction/gan2026`, and `clinical-extraction/reliability`. | Keep names stable. |
| Params | Immutable run configuration such as candidate id, split, model, prompt version, scorer surface, row count. | Keep params concise; use artifacts for complex configs. |
| Metrics | Numeric scores and operational counters. | Family-specific metrics should use stable names. |
| Tags | Claim boundary, decision status, row-inspection policy, replay mode, registry run id. | Tags are the main query layer. |
| Artifacts | Markdown reports, summary JSON, configs, predeclarations, scorecard payloads, and selected JSONL files. | Avoid duplicating huge raw artifacts by default. |
| Parent-child runs | Group model swaps, repair ladders, and ablation families. | Parent is the comparison; children are model/candidate rows. |
| Tracing | Optional row-level LLM call observability on unrestricted dev/pilot surfaces. | Disabled by default for restricted surfaces. |
| GenAI eval datasets | Later: hard-case/golden dev sets for prompt/model regression testing. | Requires SQL backend; do not start here. |

References:

- MLflow Tracking: https://mlflow.org/docs/latest/ml/tracking/
- MLflow parent and child runs: https://mlflow.org/docs/latest/ml/traditional-ml/tutorials/hyperparameter-tuning/part1-child-runs/
- MLflow LLM tracing: https://mlflow.org/docs/latest/genai/tracing/
- MLflow GenAI evaluation: https://mlflow.org/docs/latest/genai/eval-monitor/
- MLflow evaluation datasets: https://mlflow.org/docs/latest/genai/datasets/

## Design Principles

1. **Registry first.** A run is paper-visible only if it has the existing
   registry/report artifacts. MLflow can mirror unregistered scratch runs, but
   those must be tagged `claim_status=scratch`.
2. **Local first.** Start with `mlruns/` local tracking. Add SQLite only when
   MLflow evaluation datasets or multi-user sharing are actually needed.
3. **No raw restricted traces.** Do not log row text, prompts, raw model output,
   evidence text, or row-level failure ledgers for Gan test450, ExECTv2 full-200
   aggregate-only audits, or holdout-like surfaces.
4. **Artifacts stay portable.** Existing JSONL/Markdown artifacts remain usable
   without MLflow.
5. **Schema over convention.** Add typed helper objects so every runner logs the
   same fields instead of hand-written `mlflow.log_*` calls scattered through
   the repo.
6. **No metric-only promotion.** MLflow comparison tables are convenience views;
   promotion still requires predeclared gates and claim-language review.

## Proposed Architecture

```text
runner/report builder
  -> writes existing JSONL/JSON/MD artifacts
  -> creates or updates RunRegistryEntry
  -> calls register_run(...)
  -> calls mirror_registry_entry_to_mlflow(...)
        -> logs params/tags/metrics/artifacts
        -> optionally links parent run
        -> optionally logs safe traces
```

The implementation should introduce one small shared module:

```text
src/clinical_extraction/core/mlflow_tracking.py
```

and then add thin integration points around existing registration/reporting
paths instead of rewriting runners.

## Experiment Naming

Use stable MLflow experiment names:

| MLflow experiment | Contents |
| --- | --- |
| `clinical-extraction/gan2026` | Gan pipeline runs, replay analyses, reliability scorecards, component-impact artifacts. |
| `clinical-extraction/exectv2` | ExECTv2 architecture runs, model swaps, full-200 aggregate audits, scorecards. |
| `clinical-extraction/reliability` | Cross-dataset or cross-model reliability analyses when the row is not naturally owned by one task. |
| `clinical-extraction/scratch` | Optional local scratch runs; never paper-facing. |

Avoid creating a new MLflow experiment for every date or candidate. Use tags and
params for filtering.

## Run Hierarchy

### Single Run

Use one MLflow run for a normal artifact family:

```text
run_id: exectv2_same_core_model_swap_dev140_20260625
experiment: clinical-extraction/exectv2
```

### Parent-Child Group

Use parent-child runs when a report compares multiple rows under one frozen
question:

```text
parent: exectv2_2call_no_sf_adjudicator_model_swap_dev140_20260625
  child: exectv2_2call_no_sf_adjudicator_gpt41mini_dev140_20260625
  child: exectv2_2call_no_sf_adjudicator_deepseek_dev140_20260625
  child: exectv2_2call_no_sf_adjudicator_qwen36_dev140_20260625
  child: exectv2_2call_no_sf_adjudicator_qwen36_repair_v01_dev140_20260625
```

Use parent-child runs for:

- same-core model swaps;
- prompt repair ladders;
- component ablation ladders;
- calibration/review-routing/robustness panels;
- repeat/self-consistency runs.

Do not over-nest beyond one parent level unless the UI clearly benefits.

## Canonical Params

These should be logged as MLflow params when present:

| Param | Meaning |
| --- | --- |
| `registry_run_id` | Existing `RunRegistryEntry.run_id`. |
| `task` | `gan2026`, `exectv2`, or cross-dataset task label. |
| `dataset` | Dataset family, e.g. `Gan (2026)` or `ExECTv2 (2025)`. |
| `split_manifest` | Locked split manifest id or path. |
| `split` | `dev140`, `validation750`, `test450`, `full200_aggregate`, etc. |
| `row_count` | Number of rows included in the run. |
| `pipeline_family` | Existing registry `pipeline_family`. |
| `candidate_id` | Runnable/replayable candidate id. |
| `architecture_core_id` | Frozen core id for model-swap rows. |
| `model` | Runtime model display/API identifier. |
| `model_role` | Extractor, selector, adjudicator, verifier, analysis-only, etc. |
| `provider` | OpenAI, DeepSeek, Ollama, none, replay. |
| `endpoint` | Safe endpoint class, e.g. `hosted_api`, `localhost_ollama`; do not log secrets. |
| `prompt_version` | Prompt/program version when known. |
| `repair_mode` | Named deterministic/schema repair policy. |
| `scorer_surface` | `clinical_headline`, `strict_benchmark`, `purist`, `pragmatic`, etc. |
| `mode` | Live, replay, prompt-only, analysis-only. |
| `replay_status` | Existing registry replay status. |
| `git_head` | Commit hash when available. |
| `git_dirty` | `true` or `false`. |

MLflow params are immutable within a run. If a field may need correction, log it
as a tag or artifact note instead.

## Canonical Tags

Use tags as the query/governance layer:

| Tag | Allowed examples |
| --- | --- |
| `claim_status` | `scratch`, `diagnostic`, `revise`, `reject`, `promote`, `historical`, `reliability_scorecard`. |
| `claim_boundary` | `dev_only`, `validation_development`, `full200_aggregate_only`, `locked_holdout_aggregate`, `analysis_only`. |
| `row_inspection_policy` | `allowed`, `blocked`, `aggregate_only`, `not_applicable`. |
| `raw_trace_policy` | `disabled`, `metadata_only`, `redacted`, `enabled_dev_only`. |
| `artifact_policy` | `summary_only`, `selected_artifacts`, `full_artifacts`. |
| `component_ownership` | `rules_only`, `llm_only`, `hybrid`, `analysis_only`, `diagnostic_mixed`. |
| `registry_canonical` | `true` or `false`. |
| `predeclared` | `true` or `false`. |
| `same_core_comparison` | `true` or `false`. |
| `operational_candidate` | `true` or `false`. |
| `restricted_surface` | `true` or `false`. |

These tags must be derived from the existing protocol/reporting context, not
invented after looking at MLflow charts.

## Canonical Metrics

Metric names should be stable and machine-queryable. Suggested names:

### Score Metrics

```text
overall_f1
overall_precision
overall_recall
clinical_headline_f1
strict_benchmark_f1
purist_accuracy
pragmatic_accuracy
```

### Family Metrics

```text
diagnosis_f1
seizurefrequency_f1
prescription_f1
investigations_f1
patienthistory_f1
birthhistory_f1
onset_f1
whendiagnosed_f1
epilepsycause_f1
```

### Reliability Metrics

```text
evidence_validity_rate
schema_validity_rate
parse_failure_count
schema_failure_count
call_failure_count
repair_count
review_burden
review_catch_rate
ece
brier
cross_model_jaccard
mean_entropy
```

### Runtime Metrics

```text
latency_seconds_total
latency_seconds_mean
tokens_input_total
tokens_output_total
tokens_total
estimated_cost_usd
rows_per_minute
```

Use `step` only for true progress series such as checkpoint metrics. Do not
fake stage ladders as training curves unless the step semantics are explicit.

## Artifact Logging Policy

Log these artifacts by default for registered/high-signal runs:

- report Markdown;
- summary JSON;
- predeclaration Markdown;
- config JSON/YAML;
- scorecard JSON payload;
- registry row snapshot;
- compact metrics table CSV/JSON when generated.

Do not log these by default:

- large raw JSONL files unless explicitly selected;
- full raw prompt/output traces;
- row-level restricted-surface failure ledgers;
- `.env`, credentials, local logs with tokens, or unredacted endpoint headers.

When raw JSONL artifacts are too large or too sensitive, log:

```text
artifact_uri_pointer.json
```

with relative repo paths, file size, SHA256, row count, and schema summary.

## Privacy And Split Guardrails

| Surface | MLflow run metadata | Artifacts | Raw traces |
| --- | --- | --- | --- |
| Gan validation/dev | Allowed. | Allowed if synthetic and not restricted by protocol. | Optional after Phase 6, redaction-reviewed. |
| Gan test450 | Aggregate metadata only. | Aggregate report only. | Forbidden. |
| ExECTv2 dev140 | Allowed. | Allowed. | Optional metadata-only first; raw trace requires explicit decision. |
| ExECTv2 full-200 aggregate audit | Aggregate metadata only. | Aggregate report/summary only. | Forbidden. |
| ExECTv2 holdout-like surface | Aggregate metadata only. | Aggregate report/summary only. | Forbidden. |
| Scratch local pilots | Allowed under `scratch`. | Local only. | Optional, never promoted directly. |

MLflow must never become a backdoor around row-inspection policy. If a surface is
aggregate-only in the research protocol, MLflow logs only aggregate-safe data.

## Implementation Phases

### Phase 0: Decision Record And Dependency Boundary

Goal: make the MLflow role explicit before code changes.

Status: complete as of 2026-06-26 via
`docs/decisions/0034-mlflow-is-optional-observability.md`, the optional
`mlops` dependency, and gitignored local MLflow state.

Work:

- Add or update a design note/ADR stating:
  - MLflow is an observability/index layer.
  - `experiments/registry.jsonl` remains canonical.
  - local tracking is the initial backend.
  - raw traces are disabled for restricted surfaces.
- Add `mlflow` as an optional dev dependency, not a required runtime dependency
  for all package users.
- Add `mlruns/` and any local SQLite store paths to `.gitignore`.

Suggested dependency shape:

```toml
[project.optional-dependencies]
mlops = [
  "mlflow>=3.0.0",
]
```

Completion gate:

- Installing `.[dev,mlops]` enables MLflow helpers.
- Importing the base package without `mlflow` still works.
- The ADR/plan explains why MLflow is not the claim-of-record.

### Phase 1: Shared MLflow Tracking Helper

Goal: centralize MLflow usage behind one typed helper.

Status: complete as of 2026-06-26 via
`src/clinical_extraction/core/mlflow_tracking.py` and
`tests/test_core_mlflow_tracking.py`.

Add:

```text
src/clinical_extraction/core/mlflow_tracking.py
tests/test_core_mlflow_tracking.py
```

Core objects:

```python
@dataclass(frozen=True)
class MlflowRunPayload:
    experiment_name: str
    run_name: str
    params: Mapping[str, str | int | float | bool | None]
    metrics: Mapping[str, int | float]
    tags: Mapping[str, str | bool]
    artifact_paths: tuple[Path, ...]
    artifact_pointer_paths: tuple[Path, ...] = ()
    parent_run_id: str | None = None
```

Core functions:

```python
def mlflow_available() -> bool: ...
def configure_mlflow_from_env(repo_root: Path) -> None: ...
def mirror_payload_to_mlflow(payload: MlflowRunPayload) -> str | None: ...
def registry_entry_to_mlflow_payload(entry: RunRegistryEntry, ...) -> MlflowRunPayload: ...
```

Behavior:

- If MLflow is not installed, return `None` with a clear logged message.
- If `CLINICAL_EXTRACTION_MLFLOW_DISABLED=1`, do nothing.
- Default local tracking URI should be `file:<repo>/mlruns`.
- Never raise from optional MLflow logging after the core run/report has
  succeeded unless `CLINICAL_EXTRACTION_MLFLOW_STRICT=1`.

Completion gate:

- Unit tests cover payload construction, optional no-MLflow behavior, metric
  filtering, artifact path safety, and tag normalization.

### Phase 2: Registry-To-MLflow Mirror

Goal: mirror canonical registry entries into MLflow without touching live
runners.

Status: dry-run planning path complete as of 2026-06-26. The first real
parent/child write path is complete for the same-core dev140 group. Existing-run
lookup by `registry_run_id` and `comparison_id` is implemented as of 2026-06-26
via ADR 0035; broader backfill scope is explicit and non-canonical via ADR 0036.

Add a CLI or script:

```text
scripts/sync_registry_to_mlflow.py
```

or package entry point:

```text
clinical-extraction-mlflow-sync
```

Inputs:

- `--registry experiments/registry.jsonl`
- `--run-index experiments/RUN_INDEX.md`
- `--since-date YYYY-MM-DD`
- `--run-id ...`
- `--dry-run`
- `--include-large-artifacts`

Behavior:

- Load typed registry entries.
- Convert each entry into an MLflow run payload.
- Log existing artifacts if safe and present.
- Create pointer artifacts for large JSONL/raw outputs.
- Add tag `registry_canonical=true`.
- Re-running sync should not create confusing duplicates:
  - preferred: find existing run by tag `registry_run_id`;
  - if not found, create a new run;
  - if found, update tags/artifacts only where safe.

Completion gate:

- A dry run prints the MLflow experiment/run names and artifact policy. **DONE**
- The same-core dev140 parent/child group mirrors successfully with the guarded
  plan path. **DONE**
- Syncing a small temporary registry in tests creates one run with expected
  params/tags/metrics.
- Syncing twice is idempotent enough for ordinary use.

### Phase 3: Integrate With Canonical Registration

Goal: new high-signal runs mirror to MLflow automatically after registry update.

Touch points:

```text
src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/reports/registry_sync.py
src/clinical_extraction/tasks/seizure_frequency/gan2026/experiments/run_registry.py
```

Preferred integration:

- Keep `register_run(...)` responsible for registry JSONL and RUN_INDEX only.
- Add a new wrapper:

```python
def register_run_and_mirror_to_mlflow(entry: RunRegistryEntry, ...) -> None:
    register_run(entry, ...)
    mirror_registry_entry_to_mlflow(entry, ...)
```

Then update selected runners/report builders to call the wrapper.

Completion gate:

- Existing registry tests still pass.
- MLflow failures cannot corrupt `registry.jsonl` or `RUN_INDEX.md`.
- New ExECTv2/Gan registrations can opt in without forcing every historical
  helper to change at once.

### Phase 4: Parent-Child Run Support For Comparisons

Goal: model swaps and ablation families become navigable in MLflow.

Add:

```text
src/clinical_extraction/core/mlflow_groups.py
```

or keep group helpers in `core/mlflow_tracking.py` if small.

Capabilities:

- create or find a parent run by `comparison_id`;
- attach child runs with `mlflow.parentRunId`;
- log aggregate comparison metrics on the parent;
- log child model/candidate metrics on children;
- store comparison table artifact on the parent.

Initial target:

```text
exectv2_same_core_model_swap_dev140_20260625
```

Status: initial target mirrored locally on 2026-06-26 as one parent run with
GPT-4.1-mini, DeepSeek, Qwen, and Qwen repair-v02 checkpoint children.

Completion gate:

- GPT-4.1-mini, DeepSeek, Qwen, and Qwen repair rows appear as children under a
  same-core parent run. **DONE**
- Parent run tags include `same_core_comparison=true`,
  `claim_boundary=dev_only`, and `row_inspection_policy=allowed`. **DONE**

### Phase 5: Runner Metadata Capture

Goal: stop relying only on final reports for operational provenance.

Add a small runtime metadata object emitted by LLM-backed runners:

```python
@dataclass(frozen=True)
class RuntimeTelemetry:
    provider: str
    endpoint_class: str
    model: str
    temperature: float | None
    max_tokens: int | None
    context_length: int | None
    quantization: str | None
    local_gpu_state: str | None
    call_failure_count: int
    parse_failure_count: int
    schema_failure_count: int
    latency_seconds_total: float | None
    tokens_input_total: int | None
    tokens_output_total: int | None
    estimated_cost_usd: float | None
```

Integrate first where the pain is greatest:

- ExECTv2 same-core model swap runner;
- Qwen repair runners;
- Gan live LLM experiment CLI;
- reliability/self-consistency runners.

Completion gate:

- MLflow can compare model quality and operational stability side by side.
- Qwen contract failures are visible as operational metrics, not buried in
  Markdown.

### Phase 6: Safe LLM Tracing Pilot

Goal: evaluate MLflow tracing usefulness without violating row policy.

Pilot scope:

- dev-only or validation-only synthetic/unrestricted runs;
- small row counts, e.g. dev25 or validation25;
- raw traces disabled by default;
- metadata-only spans first.

Trace fields allowed in first pilot:

- component name;
- model;
- prompt version;
- latency;
- token counts;
- parse/schema status;
- output contract status;
- evidence-validity boolean;
- row key hash rather than raw row id if useful.

Trace fields not allowed by default:

- note text;
- full prompt text containing note text;
- raw model output;
- evidence snippets;
- gold labels on restricted surfaces.

Completion gate:

- A dev25 trace run helps debug at least one real issue, such as parse failure,
  adapter envelope drift, or latency hotspot.
- Trace logging can be disabled globally with one env var.
- Restricted surfaces have tests or guards that prevent raw trace logging.

### Phase 7: MLflow UI Runbooks

Goal: make the tool usable in ordinary repo work.

Add:

```text
docs/runbooks/mlflow_local_tracking.md
```

Include:

- install command;
- how to sync existing registry entries;
- how to start local UI;
- recommended filters;
- how to interpret parent-child runs;
- artifact policy;
- privacy/split guardrails;
- troubleshooting for Windows/PowerShell;
- how to clean local `mlruns/` safely.

Example local commands:

```powershell
uv pip install -e ".[dev,mlops]"
$env:MLFLOW_TRACKING_URI = "file:C:/Users/cbrow/Code/clinical_extraction/mlruns"
python scripts/sync_registry_to_mlflow.py --since-date 2026-06-24
mlflow server --backend-store-uri "file:C:/Users/cbrow/Code/clinical_extraction/mlruns" --port 5000
```

If using SQLite later:

```powershell
mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlruns --port 5000
```

Completion gate:

- A researcher can open the UI and find promoted/rejected/diagnostic runs
  without knowing MLflow internals.

### Phase 8: Observatory Integration

Goal: use MLflow where it improves the Observatory without replacing the
registry API.

Possible additions:

- backend endpoint `/mlflow/status` showing configured tracking URI and whether
  MLflow is installed;
- backend endpoint `/mlflow/runs?registry_run_id=...` returning MLflow run link;
- add MLflow run URI/link to Observatory run detail cards;
- add operational metrics from MLflow only if absent from registry artifacts;
- keep registry/artifact parsing as the primary frontend data source.

Completion gate:

- Observatory can link from a run card to the corresponding MLflow run.
- Missing MLflow setup does not break the frontend.

### Phase 9: GenAI Evaluation Datasets And Regression Sets

Goal: only after local tracking is stable, use MLflow evaluation datasets for
repeatable dev-only regression panels.

Important constraint:

- MLflow evaluation datasets require a SQL backend, so this phase should move
  from file-local tracking to local SQLite or another SQL backend.

Candidate datasets:

- ExECTv2 dev hard50;
- ExECTv2 model-swap output-contract failures;
- Gan validation hard slices;
- synthetic stress panels;
- row-policy-safe golden prompt regression panels.

Use custom scorers for:

- exact evidence;
- schema validity;
- parse validity;
- clinical-headline correctness;
- deterministic-correct regression;
- changed-row precision;
- operational success.

Completion gate:

- A prompt/model change can be evaluated against a fixed dev-only regression set
  with MLflow storing dataset identity and scores.
- No locked holdout examples are added to MLflow evaluation datasets.

## Testing Strategy

Add tests in stages:

| Test file | Coverage |
| --- | --- |
| `tests/test_core_mlflow_tracking.py` | Optional import, payload validation, tag/param/metric normalization, artifact safety. |
| `tests/test_mlflow_registry_sync.py` | Registry entry conversion, dry-run output, idempotent lookup behavior. |
| `tests/test_exectv2_mlflow_mirror.py` | ExECTv2 registry row maps to expected experiment/tags/metrics. |
| `tests/test_gan2026_mlflow_mirror.py` | Gan registry row maps to expected experiment/tags/metrics. |
| `tests/test_mlflow_trace_policy.py` | Restricted surfaces refuse raw trace logging. |

Use temporary MLflow tracking directories in tests. Do not require a running
MLflow server.

## CLI And Environment Contract

Environment variables:

| Variable | Meaning |
| --- | --- |
| `MLFLOW_TRACKING_URI` | Standard MLflow tracking URI. Defaults to local `file:<repo>/mlruns` when unset. |
| `MLFLOW_ALLOW_FILE_STORE` | Set automatically to `true` only for the default repo-local file backend required by MLflow 3. |
| `CLINICAL_EXTRACTION_MLFLOW_DISABLED` | If `1`, skip MLflow logging. |
| `CLINICAL_EXTRACTION_MLFLOW_STRICT` | If `1`, MLflow logging errors fail the command. Default is non-strict. |
| `CLINICAL_EXTRACTION_MLFLOW_ARTIFACT_POLICY` | `summary_only`, `selected_artifacts`, or `full_artifacts`. |
| `CLINICAL_EXTRACTION_MLFLOW_TRACE_POLICY` | `disabled`, `metadata_only`, `redacted`, or `enabled_dev_only`. |

Scripts/entry points:

| Command | Purpose |
| --- | --- |
| `clinical-extraction-mlflow-sync` | Mirror registry entries to MLflow. |
| `clinical-extraction-mlflow-doctor` | Print MLflow install/config/status and guardrail warnings. |
| `clinical-extraction-mlflow-clean-local` | Optional later helper for local-only cleanup with explicit confirmation. |

## Acceptance Criteria

The implementation is useful when:

1. A fresh local checkout can install optional MLflow support and sync selected
   existing registry rows.
2. The MLflow UI shows ExECTv2 and Gan runs with searchable tags for split,
   model, decision, claim boundary, row-inspection policy, and replay status.
3. Same-core model-swap runs appear grouped under one parent run.
4. Reports/configs/predeclarations are available as MLflow artifacts or pointer
   artifacts.
5. New high-signal runs can mirror automatically after registry registration.
6. Restricted surfaces cannot accidentally log raw row-level traces.
7. The project still works if MLflow is not installed.
8. `experiments/registry.jsonl` and `RUN_INDEX.md` remain the canonical record.

## What This Would Make Better

- Run comparison becomes faster and less manual.
- Operational instability becomes visible as metrics, especially for local
  Qwen/Ollama work.
- Model-swap comparisons become easier to audit because children share one
  parent context.
- Predeclarations, configs, reports, and summary metrics are easier to find.
- Observatory can link out to a standard experiment UI instead of duplicating
  every comparison feature.
- Future regression panels can become reusable evaluation datasets, once SQL
  backend support is added deliberately.

## What This Would Make More Complicated

- Two indices now exist: registry and MLflow. The registry must remain canonical.
- Local `mlruns/` can grow quickly if raw artifacts are logged indiscriminately.
- MLflow params are immutable, so metadata correction needs careful handling.
- Raw tracing can violate split/row-inspection discipline if not guarded.
- GenAI evaluation datasets add a SQL backend requirement.
- Developers need a small runbook to avoid treating MLflow charts as promotion
  authority.

## Risk Register

| Risk | Mitigation |
| --- | --- |
| MLflow becomes the claim-of-record. | Tag every mirrored run with `registry_canonical`; docs state registry/report artifacts govern claims. |
| Restricted row text leaks into traces. | Trace policy defaults to disabled; restricted-surface guards refuse raw tracing. |
| Artifact duplication bloats repo-local storage. | Default to summary artifacts and pointer artifacts; raw JSONL opt-in. |
| Runner succeeds but MLflow failure breaks workflow. | MLflow logging non-strict by default and happens after registry/report writing. |
| Metric names drift across runners. | Central metric mapping helper and tests. |
| Parent-child grouping becomes inconsistent. | Use comparison ids and helper functions, not ad hoc nested run calls. |
| SQLite migration happens too early. | File-local tracking first; SQL only for evaluation datasets or team sharing. |

## Not In Scope

- Remote hosted MLflow server.
- Model registry as a deployment gate.
- Automatic retraining.
- Cloud artifact storage.
- Production clinical monitoring.
- Logging unredacted clinical text to MLflow.
- Replacing the Observatory.
- Replacing `experiments/registry.jsonl`.
- Any new Gan test450 or ExECTv2 full-200 row-level analysis.

## Open Questions

1. Should MLflow sync backfill all existing registry entries, or only entries
   from 2026-06-24 onward where reliability/model-swap work became central?
   **Resolved in ADR 0036:** default broader backfill is `paper_facing`
   (role-filtered since 2026-06-24); wider scopes are explicit operator choices.
2. Should local MLflow artifacts copy raw JSONL files, or should pointer
   artifacts be the default forever?
3. What exact threshold makes a raw trace "safe enough" for dev-only ExECTv2
   work: synthetic-only, redacted, or metadata-only?
4. Should MLflow run ids be written back into registry entries, or should
   registry entries stay MLflow-agnostic and only MLflow tags point back?
5. Should Observatory use MLflow metrics directly, or only link to MLflow while
   continuing to parse the canonical registry/artifacts?

## Deferred First Action

As of the 2026-06-25 rationalisation pass, defer this until the paper/results,
same-core full-200-predeclaration, and registry-driven run-surfacing work are no
longer moving underneath it.

Implement Phase 0 and Phase 1:

1. Add optional `mlops` dependency and `.gitignore` entries for local MLflow
   state.
2. Add `core/mlflow_tracking.py` with optional-import behavior.
3. Add tests for payload conversion and disabled/no-MLflow behavior.
4. Add a dry-run registry sync script for one or two recent ExECTv2 reliability
   entries. **DONE** via `scripts/sync_registry_to_mlflow.py`; current registry
   rows predate 2026-06-25, so the smoke test used a known indexed full-200 run
   and confirmed JSONL pointer-only handling.

After that, mirror the same-core model-swap dev140 artifacts as the first real
MLflow group because it is the cleanest current example of why parent-child run
tracking helps.
