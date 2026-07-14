# Documentation lifecycle

Keep one maintained owner for each concern.

| Concern | Owner |
| --- | --- |
| Current state | `PROJECT_STATUS.md` |
| Work order | `docs/plans/ACTIVE_ROADMAP.md` |
| Claim strength | `docs/canon/10_paper_provenance.md` |
| Selected evidence and hashes | `docs/experiments/retained_evidence_manifest.json` |
| Run lineage | `experiments/registry.jsonl` |
| Architecture and data rules | `docs/design/` and `docs/decisions/` |
| Repeatable procedure | `docs/runbooks/` |

## Add a document only when needed

- Update an owner instead of creating a second status, roadmap, or claim log.
- Add a decision record when the reason must outlive the implementation diff.
- Add an experiment report only when it is selected evidence or a predeclared
  study that is currently running.
- Add machine artifacts only through the registry and evidence process.

## Retire documents

Delete superseded plans, candidate narratives, generated dossiers, and redirect
stubs from the active tree. Git history is the archive. Do not create another
tracked archive directory.

Never delete or rename a manifest-selected path without updating hashes,
registry metadata, replay checks, and claim status.

