# Documentation Navigation

Start here when orienting in the repo. This page separates essential guides
(Tier 1), current design documents (Tier 2), paper and claim documents (Tier
3), and detailed records (Tier 4). See
`docs/runbooks/documentation_lifecycle.md` for where new documents belong and
how to archive them.

## Tier 1 — Read first

| Job | Path |
| --- | --- |
| Collaborator onboarding (markdown + interactive HTML) | [`collaborator_onboarding.md`](collaborator_onboarding.md) · [`collaborator_onboarding.html`](collaborator_onboarding.html) |
| Onboarding and repo layout | [`README.md`](../README.md) |
| Active objective, work board, guardrails | [`PROJECT_STATUS.md`](../PROJECT_STATUS.md) |
| Domain vocabulary (~80 terms) | [`CONTEXT.md`](../CONTEXT.md) |
| Plain-language glossary (display names, Gan vs ExECT) | [`docs/reference/plain_language_glossary.md`](reference/plain_language_glossary.md) |
| Active experiment scan order | [`experiments/README.md`](../experiments/README.md) |
| Machine run registry | [`experiments/registry.jsonl`](../experiments/registry.jsonl) |
| Retained evidence manifest (selected paths + hashes) | [`docs/experiments/retained_evidence_manifest.md`](experiments/retained_evidence_manifest.md) |
| Regenerating tracked artifacts | [`docs/REGENERATION.md`](REGENERATION.md) |
| Older status entries (rolling archive) | [`docs/research/maintenance/project_status_digest_2026-06.md`](research/maintenance/project_status_digest_2026-06.md) |
| Active roadmap (open work only) | [`docs/plans/ACTIVE_ROADMAP.md`](plans/ACTIVE_ROADMAP.md) |
| Repository surgery findings and deletion rules | [`docs/research/maintenance/repository_surgery_assessment_2026-07-14.md`](research/maintenance/repository_surgery_assessment_2026-07-14.md) |
| Narrative thread map (reading paths) | [`docs/THREAD_MAP.md`](THREAD_MAP.md) |

## Tier 1.5 — Reading by thread

Pick one thread before diving into the long tail. Each path has at most eight hops;
see [`THREAD_MAP.md`](THREAD_MAP.md) for full tables.

| Thread | Start here if you need… |
| --- | --- |
| **T1 Reliability & The Wall** | Gan ceiling, forward-observable features, wall transfer to ExECT SF |
| **T2 Clinical recovery & scoring** | `clinical_headline`, gold-quality ceiling, benchmark reconciliation |
| **T3 Architecture & components** | Pipeline stages, three families, component-off tests, candidate acceptance requirements |
| **T4 Paper & claim boundaries** | Manuscript gaps, frozen evidence, supervisor-brief conformance |
| **T5 Engineering & governance** | Registry, two-tree rule, holdout gates, doc lifecycle |

## Tier 2 — Durable design

| Job | Path |
| --- | --- |
| Architecture, data contracts, model strategy | [`docs/design/`](design/) — index: [`design/README.md`](design/README.md) |
| Architecture decision records | [`docs/decisions/`](decisions/) |
| Repeatable operational procedures | [`docs/runbooks/`](runbooks/) |
| Forward implementation plans | [`docs/plans/ACTIVE_ROADMAP.md`](plans/ACTIVE_ROADMAP.md) (historical plans in [`docs/plans/`](plans/)) |
| Metric definitions | [`docs/reference/`](reference/) |

## Tier 3 — Paper, claims, and canonical summaries

| Job | Path |
| --- | --- |
| **Paper claims register (start here for claims)** | [`docs/canon/10_paper_provenance.md`](canon/10_paper_provenance.md) |
| ExECT evaluation & scoring surfaces | [`docs/canon/04_scoring.md`](canon/04_scoring.md) |
| Gan closeout & The Wall | [`docs/canon/06_gan_clinical_policy.md`](canon/06_gan_clinical_policy.md) |
| ExECT closeout / frozen evidence tables | [`docs/canon/07_exect_plan11.md`](canon/07_exect_plan11.md) |
| GEPA closed negative program | [`docs/canon/08_gepa.md`](canon/08_gepa.md) |
| **Structural canons 01–10 (index)** | [`docs/canon/README.md`](canon/README.md) |
| Gan validation750 workstream | [`docs/experiments/gan2026/VALIDATION750_CANON.md`](experiments/gan2026/VALIDATION750_CANON.md) |
| Gan RQ component mechanics | [`docs/experiments/gan2026/COMPONENT_MECHANICS_CANON.md`](experiments/gan2026/COMPONENT_MECHANICS_CANON.md) |
| ExECT holistic assembly ladder | [`docs/experiments/exectv2/key_entities/HOLISTIC_ASSEMBLY_LADDER_CANON.md`](experiments/exectv2/key_entities/HOLISTIC_ASSEMBLY_LADDER_CANON.md) |
| ExECT Diagnosis family ladder | [`docs/canon/workstreams/DIAGNOSIS_FAMILY_LADDER_CANON.md`](canon/workstreams/DIAGNOSIS_FAMILY_LADDER_CANON.md) |
| ExECT SF adjudicator ladder | [`docs/canon/workstreams/SF_ADJUDICATOR_LADDER_CANON.md`](canon/workstreams/SF_ADJUDICATOR_LADDER_CANON.md) |
| Gold case ledger (all 4 families, per-family genuine-vs-gold breakdown) | [`docs/canon/README.md`](canon/README.md#gold-case-ledger-generated-per-family) |
| Self-consistency / entropy reliability | [`docs/canon/workstreams/SELF_CONSISTENCY_RELIABILITY_CANON.md`](canon/workstreams/SELF_CONSISTENCY_RELIABILITY_CANON.md) |
| Archived iteration narratives | [`docs/archive/ARCHIVE_INDEX.md`](archive/ARCHIVE_INDEX.md) |
| Manuscript source (markdown ahead of LaTeX) | [`docs/research/paper_manuscript_2026-06-26.md`](research/paper_manuscript_2026-06-26.md) |
| Detailed claims gap analysis | [`docs/research/paper_claims_evidence_review_2026-07-01.md`](research/paper_claims_evidence_review_2026-07-01.md) |
| Results drafts and synthesis | [`docs/research/`](research/) |
| IEEE LaTeX draft | [`literature/IEEE/IEEE-conference-template-062824/`](../literature/IEEE/IEEE-conference-template-062824/) |
| Curated experiment narratives | [`docs/experiments/`](experiments/) |
| Row-level error-analysis case files | [`docs/research/error_analysis/`](research/error_analysis/) |

## Tier 4 — Detailed records (indexed, not primary reading)

| Job | Path |
| --- | --- |
| Runnable scripts, JSON/JSONL, scorecards | [`experiments/`](../experiments/) |
| Superseded machine artifacts | [`experiments/archive/`](../experiments/archive/) |
| Archived narratives | [`docs/archive/ARCHIVE_INDEX.md`](archive/ARCHIVE_INDEX.md) |
| External papers | [`literature/`](../literature/) and [`docs/literature/`](literature/) |

## Two-tree rule (experiments vs docs/experiments)

- **`experiments/`** — machine artifacts: JSON, JSONL, drivers, generated
  scorecards, error ledgers, and registry-linked reports that must sit beside
  their outputs.
- **`docs/experiments/`** — human-readable run narratives: predeclarations,
  pilot readouts, phase reports, and curated experiment write-ups.

New narrative markdown must go in `docs/experiments/` unless it is a
registry-linked scorecard or error ledger that must co-locate with JSON/JSONL
siblings under `experiments/`. CI enforces a frozen allowlist for
`experiments/*.md` at repo root — see `scripts/check_doc_hygiene.py`.

## Filename convention (new documents)

Use `YYYY-MM-DD` date stamps in new filenames (for example
`exectv2_foo_report_2026-07-01.md`). Legacy `YYYYMMDD` names remain valid;
do not rename frozen evidence paths without updating the artifact index.
