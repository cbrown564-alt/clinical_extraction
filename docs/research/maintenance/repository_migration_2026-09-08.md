# Repository migration and documentation reduction

Updated: 2026-09-13. This record owns completed migration evidence and recovery.
The [roadmap](../../plans/ACTIVE_ROADMAP.md) owns current decisions and next work.

## Completed reconstruction

Completed on main at `205cdb16`, with runtime/tooling in `ee8abc4a` and publication
and study moves in `397572de`; integrated into the paper branch at `2d069e69b8fb526af49cb67a81e7484b38a9eff6`.
The [disposition manifest](repository_migration_2026-09-13.json) records moves,
source hashes and visibility. Earlier detailed investigation is recoverable from
that integrated revision at this same path.

Required extraction, evaluation and inspection code has functional owners. Approved
legacy removals L1–L7/L9/L10 are applied; L8's no-install HPC/vLLM workflow remains.
Request-aware persistence and offline replay are implemented. Private source,
historical run, protected scratch and review paths deliberately remain local.
No new scientific result, model call or clinical validation followed from migration.

### Recorded migration verification

| Check | Recorded outcome at migration completion |
| --- | --- |
| Python always-on suite | 824 passed |
| Ruff / mypy | Passed; 410 source files checked by mypy |
| Clean public checkout | 736 passed, 88 corpus-dependent skips |
| Packaging and commands | Wheel build/install/import, seven fresh-process imports, five HPC checks and supported command help passed |
| Frontend | 167 tests and production build passed; demo, workbench and longitudinal browser interactions checked |
| Preservation | 1,371 evidence/example/asset/publication files checked; no machine evidence or issued asset changed |

These are dated migration results, not a claim that every later edit has been tested.
The detailed logs and pre-migration dirty-file backup remain local under
`scratch/reconstruction-2026-09-13/`. Frozen result records, issued PDFs/TeX,
source identifiers, raw outputs and local-only boundaries remain preserved.

## Paper-only documentation cut

Conor postponed longitudinal work and made the paper the exclusive focus for this
period. The earlier classification retained 343 study documents; that was too broad.
The replacement policy keeps current paper owners and necessary executable/reference
material, with original study narratives recoverable through Git.

| Scope | Before | After |
| --- | ---: | ---: |
| Tracked Markdown under docs/ | 465 | 49 |
| Removed files | — | 416 |
| Lines in removed files | — | 57,236 |

The retained set includes 19 generated architecture pages and seven paused
longitudinal policies. The roadmap and protocol were rewritten for current decisions
and next work. Navigation, lifecycle guidance and local status were shortened.
No removed prose was rehomed into publication notes or an archive. Publication
writing, frozen result README files, schemas and machine artifacts are outside the
Markdown count; their unchanged presence is explicit, not counted as deletion.

The manifest's `paper_documentation_cut` contains every retained path and every
deleted path/hash, plus links updated to the historical revision. Historical
scientific procedures remain available exactly as written, rather than replaced
with summaries that could change their meaning. Read-only historical report builders
and old retained-evidence validation may require recovery of their named prose
inputs before use; they are not current paper execution prerequisites.

### Recovery

Recovery revision: `2d069e69b8fb526af49cb67a81e7484b38a9eff6`. For any removed path:

```sh
git show 2d069e69b8fb526af49cb67a81e7484b38a9eff6:docs/path/to/original.md
```

Use the recorded original path, including directories. The manifest includes the
SHA256 of each deleted file, all of which matched committed bytes before deletion.
Current links to removed documents use the pinned GitHub revision. Frozen result
links and paths retain their original bytes; use this recovery procedure to inspect
them. Git history does not replace a backup for ignored/local-only material.

## Verification of the paper-only cut

The always-on Python suite passed (824 tests); Ruff and mypy passed (410 files).
The generated index's stale manuscript link was fixed in its generator and the
19 pages regenerated without calls; its focused suite then passed (10 tests).
Documentation hygiene, whitespace and retained-document local-link checks passed.
No source/example/result/schema/config or issued PDF/TeX/bibliography artifact
changed. Frontend tests/build were not repeated: no UI or runtime behaviour changed.

Twelve ignored Markdown files containing retired personal skills were also found
under docs/history. Their directory moved byte-for-byte to the ignored local backup
`scratch/project-history/retired-personal-skills-2026-09-12/`, preserving sole copies.
These are not tracked research documents or current project instructions. There
are now 49 Markdown files physically under docs/ as well as 49 in the retained
tracked set. No model call or sealed-row inspection occurred.
