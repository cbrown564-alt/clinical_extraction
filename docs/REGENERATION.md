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

This ledger is the owner for the refactor's regeneration triage. It is
provisional until the current tree, Git history, and Git LFS objects have all
been reviewed. A historical item that cannot be regenerated must be reviewed
for scientific value, the exact blocker must be recorded, and the next action
must be chosen before the item is retired.

| Artifact class | Regeneration status | Current evidence or blocker | Scientific value | Action |
| --- | --- | --- | --- | --- |
| Selected six-method evidence | pending | Current manifest and closure records identify the required source, configuration, scorer, tests, split, and saved outputs. | Primary comparison and supporting claims. | Regenerate from the new baseline and update hashes and claim records where results change. |
| Historical saved model outputs | pending | Some raw outputs are present in the working tree or Git LFS; exact replay also depends on the permitted split and the saved producer metadata. | May support historical comparisons, diagnostics, or provenance. | Review each package; regenerate when closure is complete, otherwise record value and blocker. |
| Historical deterministic experiments | pending | Many reports and machine outputs remain in `experiments/` and Git history; closure has not yet been checked. | May explain rejected rules, negative results, or design decisions. | Trace dependencies before deletion; retain only if the evidence has a current owner. |
| Generated architecture documents | pending | Current documents are generated from manifests and teaching cases. | Explains the selected implementation. | Regenerate after source naming changes and fail the build on drift. |
| Historical generated web/build output | pending | Git history contains generated output, including cache-like files; current usefulness and regeneration path are unknown. | Usually provenance or no scientific value, but must be checked. | Review history and remove when no claim or replay depends on it. |
| Retired or unreferenced artifacts | pending | A file outside the retained manifest is not automatically deletable; dependency closure is required. | Unknown until reference and claim checks are complete. | Classify, then remove as a complete vertical slice or assign an owner. |

The review covers the working tree, Git history, and Git LFS. It must not inspect
locked rows or make model calls merely to restore an old name or result. Any
new prediction-changing replay requires its own predeclared protocol and
baseline.

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
