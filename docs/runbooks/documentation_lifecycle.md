# Documentation ownership

Keep one current owner for each subject.

| Subject | Owner |
| --- | --- |
| Current state | `PROJECT_STATUS.md` |
| Work order | `docs/plans/ACTIVE_ROADMAP.md` |
| Paper claim strength | `docs/canon/10_paper_provenance.md` |
| Selected evidence and hashes | `docs/experiments/retained_evidence_manifest.json` |
| Run history | `experiments/registry.jsonl` |
| Software and data rules | `docs/design/` and `docs/decisions/` |
| Repeatable procedure | `docs/runbooks/` |
| Current-stack hybrid fills | `experiments/current_stack/latest/fills.json` |

Update an owner instead of creating a second status, roadmap, or claim log.
Add a decision record only when the reason must outlive the code change. Add an
experiment report only for a selected result or a study currently being run.

Delete superseded plans, candidate narratives, generated row files, and redirect
stubs from the active tree. Git history is the archive. Never rename or delete a
selected evidence path without updating hashes, run metadata, replay checks, and
paper claim status.
