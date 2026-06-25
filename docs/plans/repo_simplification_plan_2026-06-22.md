# Repo Simplification Plan

Date: 2026-06-22

Rationalisation status, 2026-06-25: deferred cleanup policy. Do not start
archive/delete/refactor work from this plan until the current evidence spine,
paper-facing ExECTv2 results scaffold, and run-surfacing work are stable. The
active sequence is centralized in
`docs/plans/recent_plan_rationalisation_2026-06-25.md`.

Scope: non-destructive cleanup plan for the final closeout phase. This plan
does not delete, move, or rename active evidence. It defines the policy and
inventory to use after the artifact index, cross-model report, and reliability
scorecard are durable.

## Cleanup Rule

Freeze and index before deleting. A file may be archived only after every final
report that depends on it points to a stable replacement path or keeps the
original path in the artifact index.

## Keep As Source

- `src/clinical_extraction/core`
- `src/clinical_extraction/tasks`
- ExECTv2 finding assembly, deterministic dictionaries/lenses, report builders,
  and runners.
- Gan 2026 canonical reliability and selected-event machinery.
- Shared epilepsy utilities and evidence/span validation helpers.
- Split manifests under `data/Gan (2026)/splits` and
  `data/ExECTv2 (2025)/splits`.
- Frontend source under `frontend/`, including ExECTv2 review adapters and
  static mock data needed for final inspection.

## Keep As Canonical Evidence

- `docs/experiments/final_artifact_index_2026-06-22.md`
- `docs/experiments/exectv2/key_entities/exectv2_cross_model_closeout_2026-06-22.md`
- `docs/experiments/exectv2/reliability/exectv2_cross_model_reliability_scorecard_2026-06-22.md`
- `docs/research/final_architecture_selection_2026-06-22.md`
- Gan reliability master scorecard and source driver outputs.
- ExECTv2 v08 config, report, JSON, JSONL, and error ledger.
- ExECTv2 v09 partial hybrid config, report, JSON, and JSONL.
- ExECTv2 selected DeepSeek/Qwen diagnostic artifacts listed in the final
  artifact index.
- Frontend generated ExECTv2 static review data when it is derived from indexed
  artifacts.

## Archive After Indexing

- Superseded Qwen prompt iterations and dev1/dev5 smoke outputs.
- Superseded ExECTv2 diagnostic lanes not referenced by the final reports.
- Old Gan exploratory runs not referenced by the Gan reliability scorecard.
- One-off build scripts whose outputs have been promoted to canonical reports,
  if a reproducible replacement command exists.
- Resume fragments that are superseded by complete JSONL/MD reports.

Suggested archive shape:

```text
archive/
  experiments/
    exectv2_superseded/
    gan2026_superseded/
  logs/
```

Do not introduce the archive move until a separate cleanup branch/PR.

## Delete Only After Index And Archive

- Local logs whose operational result is captured in a report.
- Caches and temporary scratch outputs.
- Redundant checkpoints superseded by completed JSONL artifacts.
- Abandoned temporary prompt probes.

Never delete or rename:

- v08 config/report/JSON/JSONL/error ledger;
- v09 partial hybrid config/report/JSON/JSONL;
- Gan master reliability scorecard and source JSON/MD outputs;
- selected DeepSeek/Qwen source JSONL and assembly JSON/JSONL;
- split manifests;
- docs that define claim boundaries or guardrails.

## Refactor Targets

1. Consolidate ExECTv2 report builders that parse assembly JSON into
   cross-model tables.
2. Move reusable reliability metrics into a shared module rather than one-off
   experiment scripts.
3. Expose a small CLI set:
   - run ExECTv2 key-family extraction;
   - run ExECTv2 finding assembly;
   - build ExECTv2 cross-model report;
   - build reliability scorecard;
   - run Gan canonical reliability report.
4. Collapse tests into three layers:
   - fast unit tests for schemas, dictionaries, lenses, and scoring;
   - artifact replay tests for canonical configs;
   - governance tests for split and holdout guards.

## Reproducibility Gate

Before cleanup, a fresh clone should be able to:

- install the package and frontend dependencies;
- load the final artifact index;
- reproduce the ExECTv2 cross-model table from canonical JSON files;
- load the frontend ExECTv2 review data from static mock artifacts;
- run fast replay/governance tests without requiring live model calls.

## Phase Ordering

| Phase | Allowed | Not allowed |
| --- | --- | --- |
| Phase 0 | Create reports, index, mock frontend data, and cleanup inventory | Delete, move, or rename evidence |
| Phase 1 | Refresh reports, scorecards, app registry, and mock data from completed Qwen/DeepSeek artifacts | Dev140/full-200 escalation without predeclaration |
| Phase 2 | Archive/quarantine superseded artifacts in a cleanup branch | Remove canonical artifacts |
| Phase 3 | Consolidate builders/tests and shrink public repo shape | Rewrite claim history or hide deterministic semantic repairs |
