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
bounded review is complete against frozen `c3a6fbb7`, the working tree, Git
history, and Git-LFS pointers. It does not inspect locked rows, make model
calls, or regenerate broad artifacts. Status below describes what retained
inputs support now; it does not authorize a new prediction run.

| Artifact family and paths | Owner | Status | Blocker or boundary | Scientific value | Action |
| --- | --- | --- | --- | --- | --- |
| Six reference cells in `docs/experiments/retained_evidence_manifest.json` (the three ExECT and three Gan paths listed under `reference_cells`) | Retained evidence index; claim boundary in `docs/canon/10_paper_provenance.md` | Exact no-call replay is supported by recorded closure; no new run made. | Freeze predates `c3a6fbb7`; prediction-bearing changes need a new freeze and protocol. | Minimum two-task × three-method comparison. | Keep; run narrow manifest/replay checks after the refactor slice. |
| Supporting packages: `experiments/gan2026_six_model_validation_comparison_20260718.json`, `experiments/gan2026_six_model_post_panel_attribution_20260720.json`, `experiments/shared_reliability_scorecard_20260718.json`, `experiments/exectv2_published_metric_reproduction_deterministic_all9_dev140_20260714.json`, and the review substrate under `docs/experiments/` | Manifest selection; claim status in `docs/canon/10_paper_provenance.md`; current evidence in `PROJECT_STATUS.md` | Retained no-call/deterministic packages; no fresh model results. | Some are diagnostics, aggregate-only evidence, or unstarted review substrate. | Named prompt, component, negative, safety, reliability, and limitation claims. | Keep named packages; run narrow builders only when inputs change. |
| Five ExECT replay inputs tracked by Git LFS: `experiments/exectv2_2call_no_sf_adjudicator_{deepseek,gpt41mini,qwen36}_dev140_20260625.jsonl`, `experiments/exectv2_holistic_finding_assembly_v08_dev140_p7_treatment_20260702.jsonl`, and `experiments/exectv2_holistic_finding_assembly_v08_dev140_p7fix_gpt41mini_20260702.jsonl` | Git-LFS plus retained evidence manifest | Pointers and immutable object IDs present; exact replay follows `git lfs pull`. | Fresh clone needs LFS retrieval; retrieval is not regeneration. | Raw producer output for exact replay and historical architecture evidence. | Keep; retrieve and verify hashes; never replace with a model run. |
| Gan row-level LFS artifacts under `experiments/gan2026_six_model_validation_20260718/` and post-panel attribution | Git-LFS; Gan owners under `docs/experiments/gan2026/` and `docs/research/` | Retained as bounded development evidence. | `validation750` is legacy `dev750`; v0.7 post-panel output is diagnostic, not holdout evidence. | Component attribution and development limits. | Keep labels; use no-call checks only. |
| Current closure: `src/clinical_extraction/architecture/manifests/`, `src/clinical_extraction/tasks/`, `configs/`, `tests/`, `pyproject.toml`, `uv.lock`, `scripts/check_retained_evidence_manifest.py` | Decision 0047; manifest closure records | Implemented at `c3a6fbb7`; no live run here. | Decision 0048 requires a new freeze if clinical behavior changes. | Explainable source/config/scorer/test reproduction. | Use as producer closure; prove one bounded Gan slice before spreading names. |
| Generated architecture in `docs/architecture/`, built by `scripts/build_architecture_docs.py` from manifests and teaching cases | Architecture manifests and builder; Decision 0048 | Retained and checked before baseline; not regenerated here. | Rebuild after source/name changes; do not hand-edit. | Supervisor comprehension and six-path demonstration. | Keep; run `--check` after bounded refactor. |
| Frontend and fixtures: `frontend/`, `src/clinical_extraction/frontend/`, and fixture/trace inputs referenced by frontend tests | Decision 0048 operational surface; frontend tests | Retained requirement; no broad frontend build. | Live development and restricted validation are separate; no real-patient or locked data here. | Demonstrates selected methods and teaching workflow. | Keep selected routes/fixtures; audit callers during refactor. |
| Historical experiments and decisions: `experiments/`, `docs/experiments/`, `docs/decisions/0040-0047*.md`, focused `docs/research/` | Each decision/report; lineage in `experiments/registry.jsonl` | Mixed: selected evidence replayable; closed candidates explanatory; others unclassified. | Superseded producers/policies may not support current claims. | Rejected rules, negative studies, and design limits. | Keep named decision evidence; trace unselected candidates before deletion. |
| Removed generated/cache noise visible in `c3a6fbb7`: `.tmp/`, notebook charts, review HTML, cache-like files | Baseline cleanup commit | Retired; not retained deliverables. | No current claim or replay dependency identified. | None identified. | Leave removed; do not restore without a named owner. |
| Unreferenced candidates including `experiments/archive/` and `experiments/pipeline_flow_prototypes_20260716.html` | No owner until classified | Unclassified; this review does not authorize deletion. | Requires reference, claim, and producer-closure checks. | Possible historical context; unknown until traced. | Classify against manifest, decisions, claim owner, and registry; later remove only as a complete vertical slice or assign owner. |

The review covers the working tree, Git history, and Git LFS. It must not inspect
locked rows or make model calls merely to restore an old name or result. Any
new prediction-changing replay requires its own predeclared protocol and
baseline.

The inventory step is complete; cleanup and any new freeze remain open. Owner
decisions still needed are which unselected historical families prevent
misunderstanding, which generated prototypes have a current user, and when the
first plain-name source refactor is ready for replay. None authorizes locked-row
inspection or a model call.
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
