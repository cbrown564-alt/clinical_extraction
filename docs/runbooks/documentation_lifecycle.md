# Documentation Lifecycle

Operational rules for creating, locating, and retiring documents. Complements
the routing map in [`docs/NAVIGATION.md`](../NAVIGATION.md).

## Where new documents go

| Document type | Create in | Retire to | Notes |
| --- | --- | --- | --- |
| ADR | `docs/decisions/` | Never delete; supersede in place | Use next sequential number; one decision per file |
| Run narrative | `docs/experiments/` | `experiments/archive/` when registry marks superseded | Answers "what did this run do?" |
| Research synthesis | `docs/research/` | Keep; add successor doc if reframed | Answers "what did we learn?" |
| Plan | `docs/plans/` | `docs/research/maintenance/` when complete | Mark status at top of file |
| Runbook | `docs/runbooks/` | Update in place | Repeatable procedures |
| Machine artifact | `experiments/` | `experiments/archive/` notes only; JSONL stays for replay | Register in `registry.jsonl` when decision-bearing |
| Row case file | `docs/research/error_analysis/` | Keep with parent analysis doc | Never at repo root |
| Control board | `PROJECT_STATUS.md` | Monthly digest under `docs/research/maintenance/` | Rolling ~30-day "Done Recently" window |

## Two-tree rule

**Narrative in `docs/experiments/`. Machine artifacts in `experiments/`.**

Exceptions allowed at `experiments/` root only for registry-linked artifacts
that must sit beside JSON/JSONL siblings (scorecards, error ledgers, frozen
holdout audit reports). The CI allowlist in
`scripts/doc_hygiene_experiments_root_allowlist.txt` freezes the current set;
adding a new root-level `.md` requires updating that allowlist deliberately.

## Filename convention

New files: `topic_descriptor_YYYY-MM-DD.md`.

Do not rename paths referenced by `final_artifact_index_2026-06-22.md`,
`registry.jsonl`, or frozen holdout evidence without updating those indexes
first.

## PROJECT_STATUS hygiene

- **Now / Next / Blocked** — current steering only.
- **Done Recently** — last ~30 days; older entries move to a monthly digest
  under `docs/research/maintenance/project_status_digest_YYYY-MM.md`.
- **Current Read** — evidence stack snapshot; rewrite when headline numbers
  change, not on every small experiment.

## Archive policy

Follow `docs/plans/repo_simplification_plan_2026-06-22.md`:

1. Freeze and index before deleting or moving evidence.
2. Move superseded iteration **notes** to `experiments/archive/`; keep JSON/JSONL
   in place for replay.
3. Update `experiments/archive/ARCHIVE_INDEX.md` when adding buckets.

## CI gate

`scripts/check_doc_hygiene.py` runs in CI and fails when:

- A new `.md` appears at the repository root (except `README.md`,
  `CONTEXT.md`, `PROJECT_STATUS.md`).
- A directory at the repository root starts with `_`.
- A new `.md` appears under `experiments/` root outside the frozen allowlist.

To intentionally add a root-level experiment markdown file, append its basename
to `scripts/doc_hygiene_experiments_root_allowlist.txt` in the same PR and
state why it must co-locate with machine artifacts.
