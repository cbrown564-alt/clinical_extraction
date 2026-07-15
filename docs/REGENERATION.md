# Reproducing selected evidence

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
