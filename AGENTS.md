# Clinical Extraction

Build modular deterministic, LLM, and hybrid pipelines for structured extraction from clinical notes. Preserve component attribution, evidence, reproducibility, and conservative claims. A higher score is not useful when its cause cannot be explained.

Gan 2026 and ExECTv2 have different data and claim boundaries. Read `PROJECT_STATUS.md` before assuming which track is active; never transfer tuning or claim permissions between them.

## Document owners

Use `README.md` for the repository map, `docs/paper/README.md` for paper methods and claims, `docs/NAVIGATION.md` for the paper source library, and `PROJECT_STATUS.md` for current work. Then read the relevant owner. The paper-final cut is [`docs/plans/paper_final_repo_scope_2026-08-17.md`](docs/plans/paper_final_repo_scope_2026-08-17.md).

Do not add another roadmap, status board, evidence register, or research canon. Keep detailed results in their existing artifact or log; update `PROJECT_STATUS.md` only after its evidence owner.

## Research safeguards

- Use the repository `.venv` for all Python work.
- Record the dataset, split, row policy, scorer, model, prompt or program version, replay mode, and repair policy for each reported result.
- Never tune on locked-test rows or inspect their failures during development. A holdout defect starts a new development candidate; it does not permit holdout repair.
- Keep raw output, format repair, evidence selection, semantic deterministic repair, and scoring separable.
- Treat any rule that changes clinical meaning, event selection, sentinel state, category, timeframe, denominator, cluster meaning, or benchmark family as a semantic rule, regardless of its file location.
- Preserve source identifiers, valid evidence, permitted row-level mechanism examples, and reproducible machine-readable artifacts.
- Never present synthetic development evidence as clinical benchmark performance or validation evidence as holdout generalization.

Use the project skills whose descriptions match the task; their procedures and trigger rules belong in the skills, not here. Model-facing prompts, schemas, and field descriptions require the plain-language prompt audit.

Run focused tests while iterating. Before a broad completion claim, activate `.venv` and run the relevant combination of `python -m pytest`, `ruff check src tests`, and `mypy src`. Do not run expensive model calls, inspect locked data, or regenerate broad artifacts merely to update documentation.

Pytest tiers follow [pytest is the research-validity firewall](docs/paper/decisions/pytest-is-the-research-validity-firewall.md): plain `pytest` is the always-on firewall (`-m "not deep"`). Use `pytest -m deep` only for the capped deep allowlist. New always-on cases must pass always-on admission and should replace or narrow an existing case for the same obligation. Terms: `CONTEXT.md` Verification.
