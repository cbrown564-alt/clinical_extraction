# Documentation

The active project is a synthetic longitudinal epilepsy benchmark for cohort
identification and longitudinal analysis. The first phase is restructuring this
repository while preserving the existing Gan and ExECT evidence.

Start with the [project plan](plans/ACTIVE_ROADMAP.md), then use
[navigation](NAVIGATION.md) to find the current owner for a subject.
[Project status](../PROJECT_STATUS.md) is the local execution view.

The plan contains the proposed whole-repository structure and migration checks.
Most material still occupies its previous location. New target folders are created
when their first artifact is ready, not as empty placeholders.

| Current location | Role during transition |
| --- | --- |
| `plans/ACTIVE_ROADMAP.md` | Current scope, migration map and phased timeline |
| `paper/` (in `docs/`) | Existing manuscript methods, decisions and claim context (to be migrated in next slice) |
| `publications/dissertation/` | Tracked dissertation manuscript sources, TeX templates, and supporting materials |
| `research/` | Existing study protocols, interpretation and writing sources |
| `design/`, `reference/`, `runbooks/` | Shared or dataset-specific guidance; scope checked before reuse |
| `architecture/` | Generated explanation of existing implemented methods |
| `history/` | Historical decision context |
| `canon/`, `decisions/`, older plans | Superseded guidance awaiting the mapped file-level consolidation |

The new annotation design is not governed by older Gan/ExECT output conventions.
Existing benchmark split, scoring and evidence safeguards still apply.
