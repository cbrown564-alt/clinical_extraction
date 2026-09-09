# Documentation ownership

Updated: 2026-09-08. Keep one current owner for each subject.

| Subject | Owner during repository migration |
| --- | --- |
| Current state and verification | `PROJECT_STATUS.md` (local-only) |
| Scope, work order and repository migration | `docs/plans/ACTIVE_ROADMAP.md` |
| Reading paths and current locations | `docs/NAVIGATION.md` |
| Existing manuscript argument and claim context | `docs/paper/README.md` and the section owners it names |
| Existing result inventory | `paper_experiments/inventory.json` |
| Longitudinal task, queries and pilot policy | `docs/longitudinal/task_definition.md` |
| Longitudinal literature rationale | `docs/reference/longitudinal_epilepsy_rationale.md` |
| Longitudinal annotation/generation/evaluation implementation | Future `docs/longitudinal/` owners, created when the corresponding work begins |
| Study protocol and interpretation | `docs/research/<track>/` |
| Shared software and evidence rules | `docs/design/`; source and tests own implementation facts |
| Repeatable procedure | `docs/runbooks/` |
| Historical guidance | `docs/history/` after the roadmap's file-level review |

Update an owner instead of creating a second status board, roadmap or claim log.
A future path is not a current artifact. Follow existing links until the move has
been implemented and verified, then update all affected owners in the same slice.

## Roles and retention

- **Active owner:** current decisions and requirements for one subject.
- **Reference:** useful context with an explicit scope, such as Gan normalisation.
- **Evidence record:** a dated protocol/result and its reproducible artifacts.
- **Archive:** superseded guidance or narrative, with its original date and purpose.

The new roadmap supersedes the August paper-only repository cut and earlier
blanket policies against on-disk archives. Preserve worthwhile historical context
under `docs/history/`; preserve local-only history in an ignored location. Do not
copy local experiment dumps, clinical source material or private metadata into a
tracked archive. Git history can recover tracked files, but cannot replace a
backup of ignored material.

Before moving or retiring a file, establish its purpose, consumers, tracking and
sharing boundary, replacement owner and rollback location. Preserve selected
raw outputs and source IDs. Rebind readers and links; record path remapping
separately when rewriting a saved record would change its provenance. Keep
existing retained-evidence manifests authoritative for their original snapshots.
A migration mapping records moves; it is not another research evidence register.

Archive labels do not make code dependencies disappear. Change generated docs
through their generator. Remove a duplicate or regenerable artifact only after
its source, regeneration command and lack of remaining consumers are established.
Do not delete unrelated working changes, active outputs, or sole local copies.

The completion checks are those in Phase 0 of the roadmap: content/hash checks,
replay, supported commands, affected publication/UI builds, links and visibility.
No new model run or locked-row review is needed just to tidy documentation.
