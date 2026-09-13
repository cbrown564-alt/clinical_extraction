# Clinical Extraction

Build modular deterministic, LLM, and hybrid pipelines for structured extraction from clinical notes. Preserve component attribution, evidence, reproducibility, and conservative claims. A higher score is not useful when its cause cannot be explained.

The active programme has three strands: a primary one-shot, evidence-grounded extraction paper emphasising locally deployable models; bounded epilepsy cohort and longitudinal applications; and staged investigation beyond epilepsy. The active roadmap owns their scope and reconstruction strategy. For longitudinal work, preserve both the account supported at each visit and later retrospective interpretations. Gan 2026 and ExECTv2 remain separate existing benchmarks; never transfer their labels, tuning permissions, or claims to the new dataset. Read `PROJECT_STATUS.md` before assuming which work is active.

## Document owners

Use `README.md` for the repository map, `docs/NAVIGATION.md` for documentation owners, `docs/plans/ACTIVE_ROADMAP.md` for the project plan and repository migration, and `PROJECT_STATUS.md` for current work. Existing manuscript methods and claims remain under `docs/paper/README.md` until the planned migration. The August paper-final cut is historical scope for the earlier paper, not the current repository plan. Closed numbered decisions are [`docs/history/decisions.md`](docs/history/decisions.md).

Do not add another roadmap, status board, evidence register, or research canon. Keep detailed results in their existing artifact or log; update `PROJECT_STATUS.md` only after its evidence owner.

The roadmap's target paths are proposals until the corresponding migration is implemented and verified. Preserve source IDs, saved outputs, existing replay behavior, and local-only file boundaries during moves. Remove superseded tracked guidance when Git history suffices; retain on-disk history only for a named continuing use. Do not treat old paper-specific restrictions as requirements for the new longitudinal annotation. Existing holdout and scoring safeguards still apply.

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

Pytest tiers follow [pytest is the research-validity firewall](docs/paper/decisions/pytest-is-the-research-validity-firewall.md): plain `pytest` is the always-on firewall (`-m "not deep"`). Use `pytest -m deep` only for the capped deep allowlist. New always-on cases must pass always-on admission and should replace or narrow an existing case for the same obligation. Terms: `CONTEXT.md` Verification.
