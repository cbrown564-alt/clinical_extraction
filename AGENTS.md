# Clinical Extraction

Build modular deterministic, LLM, and hybrid pipelines for structured extraction from clinical notes. Preserve component attribution, evidence, reproducibility, and conservative claims. A higher score is not useful when its cause cannot be explained.

The exclusive current focus is the one-call evidence-grounded seizure-frequency
paper. Longitudinal prototype work, broader applications and research-paper tables
are postponed. Preserve their saved artifacts and reference semantics. The roadmap
owns current decisions; the paper outline and evaluation protocol own this study.
The study is locked to two prompts (`minimal`, `expanded`), one annotation guide
and one lenient finding score. Do not create numbered prompt, schema, guide or
scorer revisions; changes need an owner decision recorded in the owning document.
Gan 2026 and ExECTv2 retain separate labels, scoring and split permissions.
Read `PROJECT_STATUS.md` before assuming which work is active.

## Document owners

Use `README.md` for the repository map, `docs/NAVIGATION.md` for documentation owners, `docs/plans/ACTIVE_ROADMAP.md` for the project plan and repository migration, and `PROJECT_STATUS.md` for current work. Existing manuscript methods and claims remain under `publications/dissertation/notes/README.md` in the migrated layout. The August paper-final cut is historical scope for the earlier paper, not the current repository plan. Closed numbered decisions are [`docs/history/decisions.md`](docs/history/decisions.md).

Do not add another roadmap, status board, evidence register, or research canon. Keep detailed results in their existing artifact or log; update `PROJECT_STATUS.md` only after its evidence owner.

Repository reconstruction and migration are complete. Preserve source IDs, saved outputs, existing replay behavior, and local-only file boundaries during moves. Remove superseded tracked guidance when Git history suffices; retain on-disk history only for a named continuing use. Do not treat old paper-specific restrictions as requirements for the new longitudinal annotation. Existing holdout and scoring safeguards still apply.

## Research safeguards

- Use the repository `.venv` for all Python work.
- Record the dataset, split, row policy, scorer, model, prompt or program version, replay mode, and repair policy for each reported result.
- Never tune on locked-test rows or inspect their failures during development. A holdout defect starts a new development candidate; it does not permit holdout repair.
- Keep raw output, format repair, evidence selection, semantic deterministic repair, and scoring separable.
- Treat any rule that changes clinical meaning, event selection, sentinel state, category, timeframe, denominator, cluster meaning, or benchmark family as a semantic rule, regardless of its file location.
- Preserve source identifiers, valid evidence, permitted row-level mechanism examples, and reproducible machine-readable artifacts.
- Never present synthetic development evidence as clinical benchmark performance or validation evidence as holdout generalization.

Keep model-facing prompts, schemas, and field descriptions clear and task-relevant. Inspect the rendered instructions when they are generated; keep experiment metadata out unless it changes the model’s task.

Run focused tests while iterating. Before a broad completion claim, activate `.venv` and run the relevant combination of `python -m pytest`, `ruff check src tests`, and `mypy src`. Do not run expensive model calls, inspect locked data, or regenerate broad artifacts merely to update documentation.

Pytest tiers follow [pytest is the research-validity firewall](docs/runbooks/pytest-is-the-research-validity-firewall.md): plain `pytest` is the always-on firewall (`-m "not deep"`). Use `pytest -m deep` only for the capped deep allowlist. New always-on cases must pass always-on admission and should replace or narrow an existing case for the same obligation. Terms: `CONTEXT.md` Verification.
