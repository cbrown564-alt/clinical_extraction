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

Default to a small working documentation set: current owners, necessary evidence,
and references or procedures with a named continuing use. Consolidate duplicated
explanations into their owner. Remove superseded plans, repeated status narratives,
and redundant indexes from the checkout when tracked Git history is sufficient.
An archive directory is not a default destination for obsolete prose: retain an
on-disk historical document only when a current method, claim, reproducibility
requirement or useful reference depends on it, and state that reason.

This policy was approved on 2026-09-13. It replaces the migration's default of
archiving superseded narrative; it does not restore the August paper-only scope.
Keep raw outputs, source identifiers, original protocols needed to interpret
results, and required provenance. Git cannot recover ignored material: preserve
sole local copies separately. Never turn private material into a tracked archive.

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
