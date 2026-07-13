# Clinical Extraction agent guidance

Global guidance in `~/.codex/AGENTS.md` applies here. The rules below protect clinical and research validity.

## Product and research mandate

Build modular deterministic, LLM, and hybrid pipelines for structured extraction from clinical notes. Preserve component attribution, evidence, reproducibility, and conservative claims. A higher score is not useful if the source of the improvement cannot be explained.

The repository contains two research tracks with different data and claim boundaries. Read `PROJECT_STATUS.md` before assuming which track is active. Gan 2026 holdout evidence may be frozen while ExECTv2 remains active; never transfer tuning or claim permissions between them.

## Canonical documents

Read in this order as needed:

1. `README.md` for the repository map and current framing.
2. `docs/NAVIGATION.md` and `docs/THREAD_MAP.md` to find the shortest relevant path.
3. `docs/canon/README.md` for frozen or governing claims.
4. `PROJECT_STATUS.md` for current work and evidence freshness.
5. `docs/plans/ACTIVE_ROADMAP.md` for the active sequence.
6. The relevant design, decision, experiment, research, or runbook owner.

Do not create another roadmap, status board, evidence register, or research canon. Update the document that owns the concern and archive superseded material through the documented lifecycle.

## Environment and commands

- Use the repository `.venv` for Python, tests, scripts, notebooks, and package imports. Use `$clinical-extraction-env` when command work is involved.
- Install the package editable. Repair the environment before interpreting an import failure as a code failure.
- Run focused tests during iteration. Before a broad completion claim, run the relevant combination of:

```sh
source .venv/bin/activate
python -m pytest
ruff check .
mypy src
```

- Never run expensive model calls, inspect locked data, or regenerate broad artifacts merely to update documentation.

## Data, scoring, and evidence

- Name the dataset, split, row policy, scorer, model, prompt/program version, cache or replay mode, and repair policy for every reported result.
- Never tune from locked-test rows or inspect their failures during development. A final holdout defect starts a new development candidate; it does not license holdout repair.
- Keep raw model selection, format-only repair, selected-evidence repair, semantic deterministic repair, and final scoring separable.
- A change that alters clinical meaning, selected event, sentinel state, category, timeframe, denominator, cluster meaning, or benchmark family is a deterministic semantic rule even when placed in a parser or normalization module.
- Categorize deterministic rules as `general`, `clinical_epilepsy`, `seizure_frequency`, `gan2026_specific`, or `benchmark_format` when that distinction affects claims or ablations.
- Preserve source identifiers, evidence validity, row-level mechanism examples on permitted development data, and machine-readable artifacts that can reproduce reported tables.
- Treat inferred unions, mixed raw outputs, no-call reparses, and validation-shaped policies as diagnostic until materialized and tested under a predeclared comparison.
- Never describe synthetic development results as clinical benchmark performance or validation evidence as holdout generalization.

## Working methods

- Use `$clinical-extraction-research-loop` for experiments, research questions, ablations, robustness studies, and paper-facing interpretations.
- Use `$grill-with-docs` for consequential plans or architecture choices; these repository rules provide the clinical checklist.
- Use `$maintain-project-status` for `PROJECT_STATUS.md`; keep it current, concise, evidence-linked, and subordinate to canonical rules.
- Use the narrow safeguards when their triggers apply: scoring, TDD, component attribution, LLM delta analysis, research drift, or thermonuclear review.
- Use `$plain-language-prompt-auditor` whenever model-facing prompts, schemas, field descriptions, or DSPy signatures change.

## Completion claims

- Separate implemented, verified, validated, and promoted work.
- Near-ceiling aggregate validation is not automatic evidence of progress. Prefer hard cases, hard slices, robustness, component ablation, calibration/selective action, or a frozen holdout protocol when those answer the mechanism question better.
- Do not mark a research question answered from aggregate F1 alone. Require the stated component evidence, failure analysis, claim boundary, and transfer limits.
- Update `PROJECT_STATUS.md` only after the evidence owner is updated. Keep detailed rows, experiment tables, and chronology in their existing artifact or log.
