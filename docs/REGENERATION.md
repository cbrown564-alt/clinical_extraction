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

## Paper

The Markdown manuscript is `docs/research/paper_manuscript_2026-06-26.md`. The
IEEE source is under `literature/IEEE/IEEE-conference-template-062824/`. Keep
their claims and tables synchronized. Build with two `pdflatex` passes and
inspect every rendered page.
