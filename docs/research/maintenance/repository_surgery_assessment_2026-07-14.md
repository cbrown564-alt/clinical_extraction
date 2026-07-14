# Repository Surgery Assessment

Date: 2026-07-14
Status: historical closeout record
Canonical execution order: [`docs/plans/ACTIVE_ROADMAP.md`](../../plans/ACTIVE_ROADMAP.md)
Current work and evidence: [`PROJECT_STATUS.md`](../../../PROJECT_STATUS.md)

This document records why the repository needed major reduction and how it was
carried out safely. It is not a second roadmap, status board, evidence register, or
research canon. `ACTIVE_ROADMAP.md` owns sequence, `PROJECT_STATUS.md` owns
current work, and the canon documents own research claims.

## Executive conclusion

Closeout, 2026-07-14: the deletion-led reduction, engineering cleanup,
architecture freeze, fresh-checkout verification, and paper synchronization
are complete. Historical baseline language below is retained to explain the
decisions; it is not a description of the current tree. Current evidence and
next research work live in `PROJECT_STATUS.md` and `ACTIVE_ROADMAP.md`.

The repository contains a credible research contribution, but its current shape
is not maintainable. It preserves too many closed experiments as live code,
keeps large generated artifact and document collections in the main tree, and
uses tests and UI projections to perpetuate historical machinery. Several control
documents describe the intended rules, but the code and artifact graph do not
consistently enforce them.

The right response is deletion-led simplification. The target is:

- one active ExECT control and one minimal Gan operational reproduction path;
- the smallest deterministic, LLM-only, and hybrid reference configuration or
  replay contract for each task, so the central three-family comparison remains
  reproducible without retaining discarded candidates;
- the shared clinical, evidence, scoring, and data-contract code those paths use;
- the evidence required for surviving paper claims, indexed by path and hash;
- a small set of canonical documents and repeatable commands;
- a test suite that covers retained behavior instead of missing historical
  artifacts.

Do not refactor code that is likely to be deleted. Decide what survives, prove
the retained evidence, remove complete closed slices, and repair quality gates
on the smaller tree.

## Repository snapshot

The following measurements were taken from the 2026-07-14 working copy. Git
index counts include files currently marked for deletion. Directory sizes are
working-copy sizes and may include ignored caches or installed dependencies;
they are not Git payload measurements.

| Measure | Current value | Why it matters |
| --- | ---: | --- |
| Tracked files | 6,790 | Too large to understand as one active research system |
| Files under `experiments/` | 3,855 | Experiment history is more than half of the tracked file count |
| Markdown files | 2,487 | The documentation estate is itself a major maintenance system |
| Plan files | 40 | Closed and superseded choices remain prominent |
| Python files under `src/` | 665 | Far larger than the two retained research paths require |
| Python test modules | 230 | Tests encode many historical implementations and artifacts |
| `experiments/` working-copy size | 3.8 GB | Large evidence belongs in an external retained-artifact store |
| Full backend suite after the first cut | 2,500 passed, 18 failed, 2 skipped | All remaining failures concern broken ExECT report and catalog features |
| Repository-wide Ruff baseline, 2026-07-13 | 1,224 errors | The repository does not meet its declared static-quality gate |
| Mypy baseline, 2026-07-13 | 341 errors | Types do not currently protect the full installed package |

### Progress since the snapshot

The table above is historical baseline evidence, not the current tree.
Subsequent surgery has:

- rebuilt and verified the retained two-task × three-family evidence manifest;
- made all six reference cells replay without model calls;
- removed the frontend, Observatory, broken ExECT report/catalog machinery,
  completed migration tools, and orphaned supervisor runtime;
- removed closed ExECT generation-selection and verifier families as complete
  source, prompt, artifact, registry, report, and test slices;
- removed the remaining closed Gan agentic package while preserving its saved
  aggregate ceiling evidence outside the executable reference system;
- removed closed ExECT GEPA variants, stale launchers, superseded model-swap
  configs, and completed SF diagnostic drivers outside the retained replay and
  frozen six-model execution closures;
- reduced the backend to 270 typed source files;
- reduced Ruff from 1,224 findings to zero and restored it as a CI gate;
- made mypy clean on the installed source tree and restored it as a CI gate;
  and
- split seven oversized test modules by invariant while retaining the exact
  1,150-test collection.

Current counts and next work live in `PROJECT_STATUS.md`; commit history retains
the exact deletion sequence.

The closed Gan agentic modules are no longer installed source. Some large
retained deterministic and LLM modules may still merit ordinary
maintainability work, but the oversized retained tests now have invariant-based
owners. Passing a line-count threshold does not by itself mean retained source
is coherent; further splits should follow behavior boundaries.

## High-level findings

### 1. The repository did not have a small, explicit active product

The project describes two research tracks, many pipeline families, a backend
Observatory, a frontend workbench, MLflow mirroring, report builders, artifact
registries, paper-generation paths, and extensive experiment history. The
retained manifest now identifies the active controls and minimal two-task ×
three-family reference set. Historical documents and artifacts still surround
that set, but the live Gan and ExECT source paths are now reduced to the
retained reference and execution closures.

This is the central problem. Without an explicit retained set, every historical
component appears important and every deletion looks risky. The retained set
must be narrower than the experiment history but broader than two promoted
paths: it also needs the six minimal family comparators required by the paper.

### 2. Experiment history has become installed application code

Closed deterministic, LLM-only, hybrid, agentic, verifier, rescue, selector,
and model-comparison candidates had remained under `src/clinical_extraction/`.
The classified closed Gan and ExECT source families are now removed; their
historical documents and artifacts still need reduction so they do not appear
to be supported runtime paths.

An archive directory inside the repository does not solve this problem if the
archive remains indexed, tested, rendered, or imported. Closed code must leave
the installed package. Historical source remains recoverable from version
control; reproducibility-critical artifacts belong in the retained evidence
manifest or external artifact storage.

### 3. Evidence records and the files they name disagree

The existing frozen artifact index was treated as a prerequisite for cleanup,
but the 2026-07-13 audit found that it could not reproduce much of the file and
hash graph it claimed to govern. The retained manifest has since been rebuilt
from present files and hashes. The wider registry still contains historical
rows and lineage references that must be classified during candidate deletion.

The initial 18 backend failures were concentrated in calibration,
component-ablation, cross-model reliability, final-consolidation, and
review-routing reports. They depended on missing archived ExECT iteration
artifacts or on Observatory/static frontend projections. Those broken features
and tests have been removed; the full backend suite now passes.

### 4. Research rules were clearer in prose than in code

Gan `test450` was correctly author-uninspected, but the repository contained
agent-generated row-level reports and Observatory could expose test-labelled
rows. ExECT `full200` had not been used for row-level test60 tuning, but several
documents and labels described it too much like an independent holdout.

The first surgery pass repaired this specific problem:

- 31 row-level Gan `test450` reports and three connected generators were
  removed;
- Observatory now rejects locked-test record, artifact, membership, and
  ablation access;
- the frontend neither offers nor defaults to Gan test runs;
- ExECT `full200` is consistently labelled a **development-inclusive full200
  audit**: dev140 plus held-out test60, with no row-level test60 tuning and no
  independent-holdout claim.

This pattern must become normal. Split policy, scoring policy, and claim policy
must be enforced at the loading and serving boundaries, not only described in
documents.

### 5. Documentation volume obscures document authority

The repository contains 2,487 Markdown files, including 40 plan files, a
2,840-line generated run index, and a 1,200-line live status file. Navigation
documents and canon summaries help, but they do not eliminate the cost of
contradictory status banners, superseded plans, generated narratives, duplicate
experiment reports, and historical conclusions written as current guidance.

The problem is not that research has a history. The problem is that the main
reading path makes too much of that history look active. Long-lived documents
need one of four declared roles: canonical owner, active reference, evidence
record, or archive. Agent-generated documents that serve none of those roles
must be deleted.

### 6. Tests preserve obsolete scope

The suite is large and valuable, but it also treats historical report formats,
catalog entries, frontend payloads, and candidate-specific behavior as permanent
interfaces. Several test modules exceed 1,200 lines; the two largest exceed
1,900 lines. Twenty-one large test files were explicitly exempted from the
line-count rule.

Tests must be removed with the behavior they protect. Retained tests must
concentrate on clinical semantics, split barriers, scorer correctness, evidence
validity, active pipeline replay, and a small number of end-to-end commands.

### 7. The frontend and Observatory were separate products

The Next.js frontend and FastAPI Observatory have their own adapters, static
artifacts, registries, report projections, tests, build system, and data-access
rules. They can be useful, but they are not free research documentation. If the
paper and reproducible extraction package are the deliverables, keeping a
full-stack review product creates a second product scope.

No required user workflow or retained evidence dependency justified that second
product scope. Both products and their connected report/catalog machinery have
been removed. The retained deliverables are the Python package, evidence, and
paper.

### 8. Previous cleanup optimized structure before deciding scope

The June quality campaign split large files, introduced facades, moved prompt
content into YAML, added registries, and created more formal boundaries. Some
of that work improved real code. Some of it also made closed candidates easier
to keep by wrapping them in cleaner packages and compatibility layers.

The repository now needs fewer concepts, not another round of facade extraction.
Compatibility with deleted internal candidates is not a requirement.

### 9. The strongest material is identifiable and worth preserving

The data split manifests, author-provided evaluation semantics, clinical
normalization and scoring rules, evidence-span validation, component attribution,
active ExECT assembly results, frozen aggregate Gan evidence, and paper claim
boundaries form a defensible core. The surgery must protect these directly.

The existence of this core is why a large reduction is possible: the project's
value does not depend on preserving every route taken to reach it.

## Preservation rules

A file remains in the primary repository only when at least one of these is
true:

1. It is required by the selected active ExECT or Gan operational control.
2. It is required by a minimal deterministic, LLM-only, or hybrid reference
   configuration/replay for either task.
3. It enforces a clinical, scoring, evidence, or split invariant used by those
   paths.
4. It is necessary to reproduce a surviving paper table or claim.
5. It is a canonical owner document or the shortest operational guide needed by
   a new collaborator.

Preserve explicitly:

- dataset split manifests and source identifiers;
- locked-split barriers;
- scorer and label-normalization semantics required by the paper;
- evidence validity and component-provenance contracts;
- exact configs, environment metadata, paths, and hashes for retained results;
- permitted development examples needed to explain mechanisms;
- canonical claim boundaries and the manuscript source.

Do not retain a file merely because another retained file links to it. Repair
the retained document to state the durable conclusion and remove the obsolete
dependency.

## Deletion unit

Delete a closed research candidate as one vertical unit:

```text
candidate source
  + configuration and CLI entry point
  + prompt or schema used only by that candidate
  + raw and rendered artifacts
  + registry/catalog entries
  + Observatory and frontend adapters
  + candidate-specific tests
  + superseded plans and narratives
```

Partial deletion creates broken catalogs and compatibility shims. Each batch
must remove the full chain or explicitly record which retained claim still
needs part of it.

## Surgery plan

### Phase 0 — Protect evidence boundaries

Status: implemented and focused checks verified in the current working tree.

- Remove row-level Gan locked-test reports and their generators.
- Add backend and frontend barriers against locked-test serving or selection.
- Correct ExECT `full200` terminology without implying test60 tuning.
- Keep aggregate Gan holdout evidence; do not inspect clinical note text or
  locked row failures.

Exit condition: split rules are enforced in code and active documents use the
same claim language.

### Phase 1 — Name the retained system and rebuild its evidence manifest

Status: implemented. The five largest selected replay artifacts are stored as
content-addressed Git LFS objects with IDs, hashes, sizes, and retrieval
instructions in the retained manifest.

1. Select one active ExECT control and one minimal Gan operational reproduction
   path; list each import, config, scorer, artifact, report, and test closure.
2. Name the minimal deterministic, LLM-only, and hybrid reference configuration
   or replay for each task. These six cells may share code and saved outputs;
   they must not preserve superseded candidate families merely for history.
3. Map every surviving paper claim in `docs/canon/10_paper_provenance.md` to the
   smallest source and artifact set that supports it.
4. Verify every retained artifact path and compute its hash from the file that
   actually exists.
5. Store large retained artifacts outside primary Git, with immutable location,
   checksum, size, schema version, and retrieval instructions in the manifest.

Exit condition: every retained source file and artifact has a named reason to
exist; all six task/family cells are reproducible or replayable; every surviving
claim resolves to present, hashed evidence.

### Phase 2 — Remove broken report and catalog machinery

Status: implemented and verified by the passing full backend suite.

Start with the 18 failing ExECT report/catalog tests because they identify a
coherent dead or incomplete feature set:

- calibration validation;
- component-ablation replay and readout;
- cross-model reliability scorecard upgrades;
- final-consolidation and static frontend scorecards;
- review-routing validation;
- their Observatory endpoints and missing archive dependencies.

For each feature, either point it to retained evidence and prove it works, or
delete the builder, endpoint, static payload, catalog entry, and tests together.
Do not recreate missing historical artifacts merely to make the old tests pass.

Exit condition: full pytest has no failures caused by absent historical
artifacts, and no retained registry or report names a missing path.

### Phase 3 — Cut closed source-code families

Status: implemented in the current working tree. Closed Gan agentic source and
closed ExECT generation-selection, verifier, GEPA-variant, model-swap-config,
and SF-diagnostic code outside the retained closures are removed.

Work from the leaves toward shared code:

1. Remove closed Gan agentic, rescue, selector, probe, alternate-reasoner, and
   state-graph candidates outside the chosen reproduction path.
2. Remove closed ExECT LLM-only, verifier, model-swap, simplification, and
   diagnostic variants outside the chosen active path.
3. Remove candidate-only YAML, prompt corpora, schemas, CLI commands, and
   compatibility exports.
4. Re-run import analysis after each batch and delete shared helpers with no
   retained consumers.
5. Collapse thin facades when only one implementation remains.

Do not preserve package layout for hypothetical future candidates. New research
can add a new module when it begins.

Exit condition met for the classified source set: `src/clinical_extraction/`
contains the shared core, the six reference cells, and the ExECT runtime needed
for the planned frozen model comparison. Saved historical evidence may still
name deleted producers; it does not keep those producers installed.

### Phase 4 — Reduce the document estate

Status: implemented. The active tree contains canonical owners, current
decisions, direct evidence records, the manuscript, and operational runbooks;
tool-generated session state and the removed Observatory notebook are gone.

Keep the shortest authoritative route:

- `README.md` for repository purpose and entry points;
- `PROJECT_STATUS.md` for current work only;
- `docs/plans/ACTIVE_ROADMAP.md` for open sequence only;
- the structural and workstream canons needed for surviving claims;
- the manuscript and its direct evidence records;
- essential data contracts, decisions, and runbooks.

Then:

1. Delete agent-generated plans, reports, syntheses, and status prose that no
   longer own a decision or support a retained claim.
2. Replace large generated indexes with machine-readable registries plus a
   short human view generated on demand.
3. Move genuinely useful history out of the default reading path. Do not keep
   duplicate archive copies in several repository directories.
4. Shorten `PROJECT_STATUS.md` to current facts, current work, next work, and
   blockers; move or delete chronology according to the documentation lifecycle.
5. Remove links to deleted candidates. Do not create redirect stubs for internal,
   unpublished material.

Exit condition: a capable new collaborator can find the active pipeline,
evidence, commands, and claim limits without reading historical plans.

### Phase 5 — Decide the fate of Observatory and the frontend

Status: implemented. Both products were removed because the deliverables are
the package, retained evidence, and paper, and no required review workflow
depended on them.

Exit condition: the UI is either gone or is a bounded product with no dependency
on deleted research history.

### Phase 6 — Rebuild tests and quality gates around the retained tree

Status: complete. Pytest, Ruff, and mypy pass, the line-count allowlist is gone,
and CI enforces the complete retained suite plus both static-quality gates.

The 2026-07-14 GitHub run `29336220397` exposed a stale workflow rather than a
retained-code regression. Its six jobs still built the deleted frontend, called
the removed line-count script and SF registry-parity test, and named a deleted
Gan candidate test in a hand-curated backend subset. CI is now one Python 3.11
job that installs the package and runs the complete pytest suite. Ruff and mypy
remain required surgery closeout commands, but are deliberately not duplicated
in CI until they are added back after the reduced tree is stable.

Running that complete suite exposed a separate artifact-prune defect: four
producer outputs required by the selected ExECT hybrid replay config had been
deleted in `cdee88e9` after one had already been restored in `5ed75d59`. The four
inputs are restored, hash-selected in the retained manifest, and covered by a
config-to-manifest regression test. Four obsolete tests for deleted Gan gap
history were replaced by two checks of the current split-authorization runbook.

1. Delete tests with deleted behavior.
2. Split remaining megatests by invariant or user-facing command.
3. Keep three test levels:
   - fast unit tests for clinical, schema, scoring, and evidence semantics;
   - artifact replay tests for the selected pipelines;
   - governance tests for split, claim, registry, and locked-data policy.
4. Remove line-count and lint allowlists. Do not move exceptions to new files.
5. Make these commands pass on a fresh checkout:

   ```sh
   source .venv/bin/activate
   python -m pytest
   python -m ruff check .
   python -m mypy src
   ```

6. If the frontend remains, also require its tests, lint, and production build.

Exit condition: all retained gates pass without historical exemptions or live
model calls.

### Phase 7 — Verify reproducibility and close the surgery

Status: complete. A separate clean checkout retrieved all Git LFS objects,
created a Python 3.11 environment from the frozen dependency policy, validated
the manifest and split barriers, replayed all six reference cells without model
calls, and passed pytest, Ruff, and mypy. The surviving paper tables and both
paper sources were then synchronized, the IEEE source compiled without layout
overflow, and every PDF page was inspected.

From a fresh checkout:

1. install the package;
2. load the split manifests without locked-row inspection;
3. run the minimal Gan path on permitted data;
4. run or replay the selected ExECT path;
5. rebuild every surviving paper table from the retained manifest;
6. verify artifact hashes and registry paths;
7. build the frontend only if it survived Phase 5;
8. update the canonical status and roadmap, then mark this assessment historical.

Exit condition: a new collaborator can reproduce the retained results using the
documented commands and cannot accidentally access locked rows through normal
project interfaces.

## Decision ledger

| Question | Current evidence | Recommended default | Owner document |
| --- | --- | --- | --- |
| Which ExECT path survives? | Holistic finding assembly v08 is the current control; the manifest names its replay closure | Keep v08, its direct replay dependencies, and the executable modules required by the frozen six-model comparison | `PROJECT_STATUS.md` |
| Which Gan path survives? | The manifest names deterministic, LLM-only, and hybrid reference cells; holdout evidence remains aggregate-only | Keep those reference closures and the operational aggregate evidence; delete other candidate families | `PROJECT_STATUS.md` and Gan canon |
| Does the full-stack Observatory survive? | No required workflow or retained evidence cell depended on it | Removed | `ACTIVE_ROADMAP.md` |
| Does the frontend survive? | It duplicated report/catalog scope without a required user workflow | Removed with Observatory | `ACTIVE_ROADMAP.md` |
| Where do large evidence artifacts live? | Five selected replay files dominate the retained tracked payload | Git LFS objects; keep canonical hashes, LFS IDs, sizes, and retrieval metadata in the retained manifest | `docs/experiments/retained_evidence_manifest.json` |
| How much generated documentation survives? | Generated documents greatly outnumber canonical owners and have already created false authority | Keep only direct evidence records needed by surviving claims; delete the rest | `docs/NAVIGATION.md` and relevant canon |

## Operating rules during surgery

- Do not run new model experiments unless a surviving claim has a predeclared,
  owner-approved evidence gap.
- Never inspect Gan `test450` or ExECT test60 row-level failures for development.
- Do not repair a dead candidate before deciding whether it survives.
- Do not add compatibility shims for internal paths being removed.
- Do not move bulk history to another tracked directory and call that reduction.
- Preserve unrelated author changes.
- Make deletion batches reviewable by research slice, not by file extension.
- Record exact verification after each batch; use *implemented*, *verified*,
  *validated*, and *promoted* precisely.

## Inspection lessons

The first deletion batches exposed several traps that were not obvious from
file names or registry decisions:

1. **Rejected candidates can own retained helpers accidentally.** Diagnosis,
   SF replay, fresh-evidence, and GEPA code imported small private functions
   from packages scheduled for deletion. Import analysis and focused tests must
   precede every removal.
2. **Replay closure is narrower than future execution closure.** Saved artifacts
   reproduce the six reference cells, but future model-comparison work still
   needs selected ExECT runtime modules. Classify both needs explicitly.
3. **A textual reference has several meanings.** An import is executable; an
   artifact path must resolve; a producer label or `supersedes` value may be
   historical provenance. Treating all matches alike either breaks code or
   erases truthful history.
4. **Registry presence is not proof of reproducibility.** Some rows named
   missing archive reports, and some report builders defaulted to absent inputs.
   Present files, hashes, and no-call replay are the stronger evidence.
5. **Prompt-bearing packages have a wide blast radius.** Deleting a prompt
   corpus or shared runner requires rendered prompt snapshots, not only the
   removed candidate's tests.
6. **Cleanup metrics need context.** Source and test counts must fall when dead
   behavior is deleted. A lower passing-test count is not a regression when the
   removed tests covered removed code and the retained replay suite remains
   green.
7. **Artifact storage is a separate decision.** The manifest proves canonical
   identity while Git LFS provides content-addressed storage for the five
   largest files; both hashes and retrieval instructions are retained.
8. **CI should name retained behavior, not surgery history.** Separate frontend,
   line-count, candidate-parity, and curated-subset jobs all became false alarms
   after their owners were deleted. During surgery, one full-suite job is easier
   to trust and harder to leave stale.

## Current handoff

Repository surgery is closed. The classified closed Gan and ExECT source
candidates are removed, the selected replay closure is manifest-protected, and
the final paper sources contain only retained evidence. Continue with the open
research evidence packages in `ACTIVE_ROADMAP.md`. Re-open cleanup scope only
when a specific retained closure or predeclared study demonstrates a concrete
need.
