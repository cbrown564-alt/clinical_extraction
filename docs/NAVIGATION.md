# Documentation Navigation

Start here when orienting in the repo. This page routes to the control plane
(Tier 1), durable design (Tier 2), paper-facing material (Tier 3), and the
long tail (Tier 4). See `docs/runbooks/documentation_lifecycle.md` for where
new documents belong and how they retire.

## Tier 1 — Control plane (read first)

| Job | Path |
| --- | --- |
| Onboarding and repo layout | [`README.md`](../README.md) |
| Active objective, work board, guardrails | [`PROJECT_STATUS.md`](../PROJECT_STATUS.md) |
| Domain vocabulary (~80 terms) | [`CONTEXT.md`](../CONTEXT.md) |
| Active experiment scan order | [`experiments/README.md`](../experiments/README.md) |
| Machine run registry | [`experiments/registry.jsonl`](../experiments/registry.jsonl) |
| Human scan of registry | [`experiments/RUN_INDEX.md`](../experiments/RUN_INDEX.md) |
| Frozen evidence spine (hashes + claim boundaries) | [`docs/experiments/final_artifact_index_2026-06-22.md`](experiments/final_artifact_index_2026-06-22.md) |
| Regenerating tracked artifacts | [`docs/REGENERATION.md`](REGENERATION.md) |
| Older status entries (rolling archive) | [`docs/research/maintenance/project_status_digest_2026-06.md`](research/maintenance/project_status_digest_2026-06.md) |

## Tier 2 — Durable design

| Job | Path |
| --- | --- |
| Architecture, data contracts, model strategy | [`docs/design/`](design/) |
| Architecture decision records | [`docs/decisions/`](decisions/) |
| Repeatable operational procedures | [`docs/runbooks/`](runbooks/) |
| Forward implementation plans | [`docs/plans/`](plans/) |
| Metric definitions | [`docs/reference/`](reference/) |

## Tier 3 — Paper and claims

| Job | Path |
| --- | --- |
| Manuscript source (markdown ahead of LaTeX) | [`docs/research/paper_manuscript_2026-06-26.md`](research/paper_manuscript_2026-06-26.md) |
| Results drafts and synthesis | [`docs/research/`](research/) |
| IEEE LaTeX draft | [`literature/IEEE/IEEE-conference-template-062824/`](../literature/IEEE/IEEE-conference-template-062824/) |
| Curated experiment narratives | [`docs/experiments/`](experiments/) |
| Row-level error-analysis case files | [`docs/research/error_analysis/`](research/error_analysis/) |

## Tier 4 — Long tail (indexed, not primary reading)

| Job | Path |
| --- | --- |
| Runnable scripts, JSON/JSONL, scorecards | [`experiments/`](../experiments/) |
| Superseded iteration notes | [`experiments/archive/`](../experiments/archive/) + [`ARCHIVE_INDEX.md`](../experiments/archive/ARCHIVE_INDEX.md) |
| External papers | [`literature/`](../literature/) and [`docs/literature/`](literature/) |

## Two-tree rule (experiments vs docs/experiments)

- **`experiments/`** — machine artifacts: JSON, JSONL, drivers, generated
  scorecards, error ledgers, and registry-linked reports that must sit beside
  their outputs.
- **`docs/experiments/`** — human-readable run narratives: predeclarations,
  pilot readouts, phase reports, and curated experiment write-ups.

New narrative markdown should land in `docs/experiments/` unless it is a
registry-linked scorecard or error ledger that must co-locate with JSON/JSONL
siblings under `experiments/`. CI enforces a frozen allowlist for
`experiments/*.md` at repo root — see `scripts/check_doc_hygiene.py`.

## Filename convention (new documents)

Use `YYYY-MM-DD` date stamps in new filenames (for example
`exectv2_foo_report_2026-07-01.md`). Legacy `YYYYMMDD` names remain valid;
do not rename frozen evidence paths without updating the artifact index.
