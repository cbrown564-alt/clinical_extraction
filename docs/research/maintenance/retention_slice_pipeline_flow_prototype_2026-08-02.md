# Retention slice: pipeline flow HTML prototype (2026-08-02)

Decision: **delete**  
Authority: [Decision 0048](../../decisions/0048-comprehension-and-handoff-refactor.md) safe retention cleanup  
Branch: `retention/0048-pipeline-flow-prototype-2026-08-02`

## Scope

| Path | Action |
| --- | --- |
| `experiments/pipeline_flow_prototypes_20260716.html` | Deleted |
| `docs/design/pipeline_trace_explorer_spec.md` | Updated prototype link → live demonstration surface |
| `docs/REGENERATION.md` | Classified row and bounded-cleanup note |

Out of scope for this slice: `experiments/archive/`, `PROJECT_STATUS.md`,
`docs/plans/ACTIVE_ROADMAP.md`.

## Artifact summary

`experiments/pipeline_flow_prototypes_20260716.html` was a single-file static
HTML mock (~50 KB) titled "Clinical extraction trace explorer." It embedded
fixture JSON for four views (evidence workbench, pipeline map, compare,
transformation ledger) over the `SYN-014` teaching letter for ExECTv2 and Gan
2026. It was created 2026-07-16 as an early UX and information-architecture
sketch before the FastAPI backend and Next.js frontend existed.

## Dependency checks

### Code and tests

Repository search for `pipeline_flow_prototypes` and `20260716.html`:

- **No** Python import, script, CI step, or test reference.
- **No** frontend bundle or public asset reference.

The operational surface is documented and implemented at:

- `frontend/` (Next.js workbench, compare, ledger, clinical review)
- `src/clinical_extraction/trace_explorer/` (API, index, adapters, fixtures)
- `docs/architecture/` (generated six-path teaching surface)

### Retained evidence and reference replays

- `docs/experiments/retained_evidence_manifest.json`: **no** entry for this path.
- Six reference cells (`exectv2_*_reference`, `gan2026_*_reference`): **no**
  dependency on the HTML file.
- `experiments/registry.jsonl`: **no** entry (grep over registry not required;
  path never appeared outside the two documentation links above).

### Documentation links before cleanup

| Document | Role |
| --- | --- |
| `docs/design/pipeline_trace_explorer_spec.md` | Prototype hyperlink in header |
| `docs/REGENERATION.md` | Unclassified triage row |
| `docs/NAVIGATION.md` | Links to spec only (not to HTML) |

## Supersession

The trace explorer specification already records every product decision taken
from the prototype (core views, ExECT/Gan sharing, split policy, stage
separation, deployment assumptions). The live stack implements those views on
backend contracts and the `SYN-014` fixture (`src/clinical_extraction/trace_explorer/fixtures/syn_014.json`).

Decision 0048 names the frontend as the primary interactive demonstration.
ACTIVE_ROADMAP (read-only for this slice) already treats the frontend as the
retained demonstration surface; this HTML was an early prototype only.

Nothing in the deleted file uniquely explained clinical behavior, scoring, or
evidence claims not already owned by the specification, architecture teaching
paths, or trace explorer code.

## Decision rationale

Delete satisfies all three cleanup gates:

1. **No code/test requirement** — zero callers outside documentation.
2. **Documentation retarget** — spec header now points to `frontend/README.md`,
   trace explorer routes, and generated architecture docs.
3. **Not retained evidence** — absent from manifest and reference replay closure.

Keeping would only duplicate a superseded mock whose design intent is fully
captured in `docs/design/pipeline_trace_explorer_spec.md`.

## Changes made

1. Removed `experiments/pipeline_flow_prototypes_20260716.html`.
2. Updated `docs/design/pipeline_trace_explorer_spec.md` header: status,
   demonstration links, last-updated date.
3. Added classified row and bounded-cleanup paragraph in `docs/REGENERATION.md`.

## Recovery

The file remains recoverable from Git history prior to the cleanup commit on
this branch.

## Verification performed

- `rg pipeline_flow_prototypes` across repository (pre-delete): two doc hits only.
- Confirmed manifest absence via `rg pipeline_flow` on
  `docs/experiments/retained_evidence_manifest.json`.
- Confirmed test tree absence via `rg` under `tests/`.
- No model calls; no locked-row inspection.
