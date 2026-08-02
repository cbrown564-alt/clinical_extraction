# Reproducing selected evidence

## Naming-refactor regeneration scope

The repository is being refactored around plain method and pipeline names. The
refactor must regenerate permitted evidence from the new baseline rather than
preserve obsolete active identifiers for compatibility.

The refactor must preserve live generation for the selected six-model ×
three-method × two-task matrix, frontend development workflows, saved/fixture
demonstrations, and exact no-call replay. “Reproduce” means protocol
reproduction for a new run plus exact replay from the retained raw output; it
does not promise identical live text from a nondeterministic provider.

This ledger is the owner for the refactor's regeneration triage. The first
initial bounded inventory is complete against frozen `c3a6fbb7`, the working
tree, Git history, and Git-LFS pointers; dependency classification remains
open. It does not inspect locked rows, make model
calls, or regenerate broad artifacts. Status below describes what retained
inputs support now; it does not authorize a new prediction run.

| Artifact family and paths | Owner | Status | Blocker or boundary | Scientific value | Action |
| --- | --- | --- | --- | --- | --- |
| Six reference cells in `docs/experiments/retained_evidence_manifest.json` (the three ExECT and three Gan paths listed under `reference_cells`) | Retained evidence index; claim boundary in `docs/canon/10_paper_provenance.md` | Exact no-call replay is supported by recorded closure; no new run made. | Freeze predates `c3a6fbb7`; prediction-bearing changes need a new freeze and protocol. | Minimum two-task × three-method comparison. | Keep; run narrow manifest/replay checks after the refactor slice. |
| Supporting packages: `experiments/gan2026_six_model_validation_comparison_20260718.json`, `experiments/gan2026_six_model_post_panel_attribution_20260720.json`, `experiments/shared_reliability_scorecard_20260718.json`, `experiments/exectv2_published_metric_reproduction_deterministic_all9_dev140_20260714.json`, and the review substrate under `docs/experiments/` | Manifest selection; claim status in `docs/canon/10_paper_provenance.md`; current evidence in `PROJECT_STATUS.md` | Retained no-call/deterministic packages; no fresh model results. | Some are diagnostics, aggregate-only evidence, or unstarted review substrate. | Named prompt, component, negative, safety, reliability, and limitation claims. | Keep named packages; run narrow builders only when inputs change. |
| Five ExECT replay inputs tracked by Git LFS: `experiments/exectv2_2call_no_sf_adjudicator_{deepseek,gpt41mini,qwen36}_dev140_20260625.jsonl`, `experiments/exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_dev140_20260625.jsonl`, and `experiments/exectv2_holistic_finding_assembly_v08_dev140_p7_treatment_20260702.jsonl` | Git-LFS plus retained evidence manifest | Pointers and immutable object IDs present; exact replay follows `git lfs pull`. The retained `p7fix_gpt41mini` identity is a replay package whose raw closure uses the `p7_treatment` output plus `experiments/exectv2_deterministic_prescription_repair_v03_dev140_p7fix_20260702.jsonl`; it is not a fifth LFS object. | Fresh clone needs LFS retrieval; retrieval is not regeneration. The p7fix package also depends on its recorded deterministic repair closure. | Raw producer output for exact replay and historical architecture evidence. | Keep; retrieve and verify hashes; preserve the p7fix identity and p7_treatment closure; never replace either with a model run. |
| Gan row-level LFS artifacts under `experiments/gan2026_six_model_validation_20260718/` and post-panel attribution | Git-LFS; Gan owners under `docs/experiments/gan2026/` and `docs/research/` | Retained as bounded development evidence. | `validation750` is legacy `dev750`; v0.7 post-panel output is diagnostic, not holdout evidence. | Component attribution and development limits. | Keep labels; use no-call checks only. |
| Current closure: `src/clinical_extraction/architecture/manifests/`, `src/clinical_extraction/tasks/`, `configs/`, `tests/`, `pyproject.toml`, `uv.lock`, `scripts/check_retained_evidence_manifest.py` | Decision 0047; manifest closure records | Implemented at `c3a6fbb7`; no live run here. | Decision 0048 requires a new freeze if clinical behavior changes. | Explainable source/config/scorer/test reproduction. | Use as producer closure; prove one bounded Gan slice before spreading names. |
| Generated architecture in `docs/architecture/`, built by `scripts/build_architecture_docs.py` from manifests and teaching cases | Architecture manifests and builder; Decision 0048 | Retained and checked before baseline; not regenerated here. | Rebuild after source/name changes; do not hand-edit. | Supervisor comprehension and six-path demonstration. | Keep; run `--check` after bounded refactor. |
| Frontend and trace explorer: `frontend/` and `src/clinical_extraction/trace_explorer/`, plus fixture/trace inputs referenced by frontend tests | Decision 0048 operational surface; frontend tests | Retained requirement; no broad frontend build. | Live development and restricted validation are separate; no real-patient or locked data here. | Demonstrates selected methods and teaching workflow. | Keep selected routes/fixtures; audit callers during refactor. |
| Historical experiments and decisions: `experiments/`, `docs/experiments/`, `docs/decisions/0040-0047*.md`, focused `docs/research/` | Each decision/report; lineage in `experiments/registry.jsonl` | Mixed: selected evidence replayable; closed candidates explanatory; others unclassified. | Superseded producers/policies may not support current claims. | Rejected rules, negative studies, and design limits. | Keep named decision evidence; trace unselected candidates before deletion. |
| Removed generated/cache noise visible in `c3a6fbb7`: `.tmp/`, notebook charts, review HTML, cache-like files | Baseline cleanup commit | Retired; not retained deliverables. | No current claim or replay dependency identified. | None identified. | Leave removed; do not restore without a named owner. |
| Early HTML prototype `experiments/pipeline_flow_prototypes_20260716.html` (removed 2026-08-02) | Decision 0048 cleanup slice; [`docs/design/pipeline_trace_explorer_spec.md`](design/pipeline_trace_explorer_spec.md) | Deleted after classification; superseded by live frontend and trace explorer. | Not in manifest, registry, or six reference replays; no code or test caller. | Design decisions captured in the trace explorer specification. | Removed in cleanup commit; recover from Git history if needed. |
| `experiments/archive/gan2026_validation750_iterations/` (three Gan three-way comparison Markdown reports) | Retained evidence index; Gan reference cells in [`retained_evidence_manifest.json`](experiments/retained_evidence_manifest.json) | Classified 2026-08-02: **keep**. | Hashed artifacts on `gan2026_*_reference` cells; registry `artifact_paths`; manifest check fails if removed. | Original run summaries for the three Gan reference packages. | Keep; see [retention slice note](research/maintenance/retention_slice_experiments_archive_2026-08-02.md). |

## Bounded cleanup applied 2026-08-02

The first safe cleanup slice removed the 15 tracked JSON files under
`frontend/public/mock-data/run-note/validation/`. Dependency checks found no
code, route, test, retained-evidence manifest, experiment registry, or durable
documentation reference to that directory. The active `/run/note` endpoint
executes the deterministic pipeline from the request and does not load these
fixtures. The directory was introduced as frontend fallback data, but the
current frontend has no caller for it. No source, test, selected evidence,
replay input, or clinical behavior changed. Recovery is available from Git
history or by reverting the cleanup commit.

The second safe cleanup slice removed
`experiments/pipeline_flow_prototypes_20260716.html`, an early static HTML
mock of the trace explorer. Dependency checks found no code, test, manifest,
registry, or reference-replay requirement; the only durable link was the
prototype line in `docs/design/pipeline_trace_explorer_spec.md`, now retargeted
to the live Next.js frontend and generated architecture teaching surface.
Design decisions from the prototype remain in that specification. Record:
[retention slice note](research/maintenance/retention_slice_pipeline_flow_prototype_2026-08-02.md).
Recovery is available from Git history or by reverting the cleanup commit.

The third safe cleanup slice removed three candidate-only prompt draft notes
under `docs/experiments/` (ExECTv2 Luna, Gan Luna, DeepSeek unknown U).
Inbound links were retargeted to protocols, exemplar packs, research threads,
and machine compare artifacts. Record:
[retention slice note](research/maintenance/retention_slice_prompt_draft_notes_2026-08-02.md).
No protocol, exemplar pack, residual analysis, or research report was deleted.

The fourth slice audited the ExECT candidate config trees
(`configs/exectv2/model_swap/`, `configs/exectv2/diagnosis_ablation/`, and
non-reference-cell files under `configs/exectv2/finding_assembly/`). No
additional files were removed: five configs remain, each referenced by the
retained-evidence manifest, a focused replay/check script, or a focused test.
Seventy-nine sibling candidate manifests were already deleted in July 2026.
Record:
[retention slice note](research/maintenance/retention_slice_exectv2_candidate_configs_2026-08-02.md).

The fifth slice evaluated the seven tracked JSON files under
`frontend/public/mock-data/artifacts/` and retained them. `FrontendDataStore`
glob-loads that directory for `/artifacts/{run_id}` replay and for ExECT
dev140 letter allowlisting; frontend components and
`tests/test_trace_explorer_frontend_api.py` depend on those loaders. Record:
[retention slice note](research/maintenance/retention_slice_frontend_mock_artifacts_2026-08-02.md).
A later delete would require refactoring those loaders onto governed
`experiments/` sources first.

The sixth slice classified `experiments/archive/`. The directory holds exactly
three tracked Markdown companions for the Gan rules / LLM-only / hybrid
reference cells. Each is a hashed retained-evidence artifact and a registry
`artifact_path`. Decision: **keep**; do not delete under an `archive/` name
alone. Record:
[retention slice note](research/maintenance/retention_slice_experiments_archive_2026-08-02.md).

The review covers the working tree, Git history, and Git LFS. It must not inspect
locked rows or make model calls merely to restore an old name or result. Any
new prediction-changing replay requires its own predeclared protocol and
baseline.

The initial bounded inventory and the 2026-08-02 classification wave are
complete for the named Decision 0048 cleanup candidates. The stale
fresh-evidence validation750 entry was removed from
`frontend/public/mock-data/registry.json` after both listed artifacts were
confirmed missing. The completion-gate slice removed the stale
test450 frozen-audit mock-registry entry (both listed artifacts already absent;
authoritative lineage remains in `experiments/registry.jsonl` and aggregate-only
test450 companions under `experiments/`).

### Broader corpus triage wave (2026-08-02, continued)

Inventory of mock-data leftovers, orphan docs, and 337 tracked
`experiments/` + `docs/experiments/` files. Safe deletes applied:

| Slice record | Deleted |
| --- | --- |
| [unserved ExECT mock](research/maintenance/retention_slice_unserved_exect_mock_2026-08-02.md) | Orphan p7fix mock; ExECT ablation/transitions fixtures (~2.3 MB) |
| [orphan docs](research/maintenance/retention_slice_orphan_docs_2026-08-02.md) | 5 superseded/zero-inbound docs; rejected-policy protocols **kept** for check-script negative replay |
| [experiments orphans](research/maintenance/retention_slice_experiments_orphans_2026-08-02.md) | 7 tier-1 orphans (pipeline-flow PNGs, archived Luna joint panels, superseded DeepSeek diff, Qwen retry backup) |

Scoring-lane / two-call orphan cleanup and mock-registry path retarget applied
in [scoring-lane + registry slice](research/maintenance/retention_slice_scoring_lane_and_registry_2026-08-02.md)
(~99 MB deleted; five historical registry rows point at served
`mock-data/artifacts/`). Still deferred: protocol docs outside the machine
manifest that own focused evidence threads, and optional further lane
`*_sf_state_projection_combined.jsonl` review. Retained-evidence manifest check
passes after this wave. Locked-row inspection and model calls remain
unauthorized for cleanup alone.

### Documentation corpus triage (2026-08-03)

Active-index and status thinning under Decision 0048 documentation reading-path
rules. Record:
[documentation corpus slice](research/maintenance/retention_slice_documentation_corpus_2026-08-03.md).

| Change | Disposition |
| --- | --- |
| `docs/NAVIGATION.md` | Thinned to supervisor/worker doors + evidence pointer block |
| `docs/THREAD_MAP.md` | Durable design/decision doors only in Change the implementation |
| `PROJECT_STATUS.md` | Live control panel; not an evidence catalog |
| Six orphan experiment/protocol docs | Deleted (see slice note); Git history recovery |
| Decision 0046 / 0047 | Rebound Phase A/B/C and parity summary as living owners |
| Peer research satellites | Deferred (would break links inside living-cited reports) |

The retained evidence index records selected paths, hashes, source commit, and
policy versions.

## Environment and large files

Use Python 3.11 and retrieve Git LFS objects before checking results:

```sh
uv sync --python 3.11 --frozen --extra dev
git lfs pull
```

Five large ExECT replay files use content-addressed Git LFS storage. The JSON
index records each object ID, content hash, and byte size.

## Checks

```sh
python scripts/check_retained_evidence_manifest.py
python scripts/verify_reference_evidence.py
python scripts/check_exectv2_model_led_audit.py
```

The first command checks files, hashes, sizes, run metadata, and the six selected
method results. The second replays or rescores all six without model calls.

To regenerate one result, use the entry point, configuration, scorer, data rules,
and tests listed in its `closure` record. Do not infer a producer from an old
filename. A changed selected file requires a documented reason, unchanged data
limits, new hash and size, matching run metadata, both checks, and an update to
paper claim status when the result changes.

A prediction-changing prompt, scorer, split, repair, model route, or pipeline
change requires a new recorded version. It does not authorize a model call.

## ExECT paper-derived metrics

Regenerate the additive rules-only dev140 metric artifact without model calls:

```sh
python -m clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.cli.published_metric_reproduction \
  --out-json experiments/exectv2_published_metric_reproduction_deterministic_all9_dev140_20260714.json \
  --out-md docs/experiments/exectv2/reliability/exectv2_published_metric_reproduction_results_2026-07-14.md \
  --generated-on 2026-07-14
```

This reports normalized phrase, CUI, and all-feature macro scores for all nine
entity types. It uses dev140 only and must not inspect test60 or full200 rows.

## Paper

The Markdown manuscript is `docs/research/paper_manuscript_2026-06-26.md`. The
IEEE source is under `literature/IEEE/IEEE-conference-template-062824/`. Keep
their claims and tables synchronized. Build with two `pdflatex` passes and
inspect every rendered page.
