# Longitudinal epilepsy benchmark: project plan

Updated: 2026-09-08. Owner: Conor Brown.
Status: planning baseline; example and publication moves implemented, broader migration ongoing, longitudinal benchmark not implemented.

[Project status](../../PROJECT_STATUS.md) owns task progress and current checks.
This document owns scope, task order, dependencies, completion criteria, and the
repository restructuring map. [Navigation](../NAVIGATION.md) names the current
locations. Target paths below do not imply that those directories exist yet.

## Outcome and research question

Build a synthetic, patient-linked epilepsy clinic-letter dataset and a working
extraction pipeline that support cohort identification and longitudinal analysis.
Preserve what was documented at each visit and how later evidence changes the
retrospective interpretation. Demonstrate one complete path from letters to
supported facts, patient history, and a cohort answer before generating the full
corpus. Later expert annotation and real-record evaluation establish separate,
stronger forms of evidence.

Primary question: does explicit linking of evidence across clinic letters improve
time-dependent cohort answers and reconstruction of patient histories compared
with independent letter extraction and simple aggregation?

The dataset and its annotation policy are research contributions to investigate.
Neither schema superiority nor clinical usefulness has been established. Existing
Gan and ExECT results remain evidence for their original tasks only.

## Decisions and working assumptions

**Agreed direction**

- Keep both views: the account supported by letters available at a selected date,
  and the retrospective account using later evidence. Preserve earlier assertions
  rather than silently replacing them.
- Focus on cohort identification and longitudinal analysis. Predictive modelling,
  treatment recommendation, and clinical deployment are outside the first release.
- Start with synthetic letters and AI-generated provisional annotations. Seek
  expert annotation after a working demonstration; do not claim AI agreement is
  expert agreement.
- Preserve concurrent seizure patterns and frequency qualifiers. Separate epilepsy
  diagnoses from seizure types. Record past, current, planned, and conditional
  medication information without treating a plan as confirmed use.
- Restructure the repository first, including code callers, results, publications,
  examples, media, documentation, and local research material.

**Planning assumptions to test in the pilot**

- Target 300 synthetic patients, each with 2–5 letters (600–1,500 letters), assuming
  one seed per generated patient. The proposed balance is 150 ExECT-style and 150
  Gan-style patients. These are coverage targets, not estimates of population
  prevalence or a statistically powered sample size.
- Use four clinical families: epilepsy diagnosis, seizure events/patterns,
  medications, and investigations. Avoid an unrestricted patient-history family;
  add context only where a named research question needs it.
- Start with one authored three-letter patient, then a 12-patient/36-letter pilot.
  Pilot patients stay in development, even if the annotation scheme later changes.
- Conor owns scope and research decisions. An implementation contributor executes
  engineering tasks. Clinical reviewers are prospective collaborators, not assigned
  or confirmed participants. King's and Swansea are possible partners.
- No new model calls, outreach, corpus generation, or publication is part of this
  planning change. Model budgets, providers, and release destinations are selected
  in the phases that need them.

## First phase: repository restructuring

### Observed structure

Inspection on 2026-09-08 at Git base `8da94df5`, with an already dirty working tree.
Counts exclude dependency/build caches, Python caches, and `.DS_Store`. Sizes are
approximate file bytes, not disk allocation. This was a path/metadata inventory
and selected caller review; locked row contents were not inspected.

| Area | Files / tracked | Approx. MiB | Finding |
| --- | ---: | ---: | --- |
| `src/` | 417 / 417 | 3.5 | Existing package, task implementations, operational CLI, paper runners, APIs |
| `tests/` | 107 / 107 | 0.7 | Replay, paths, scoring, generated-doc and safety dependencies |
| `frontend/` | 216 / 197 | 5.1 | Workbench plus active user edits to viva/application demos |
| `docs/` | 617 / 535 | 85.4 | Current owners mixed with superseded canon, decisions, reports and generated assets |
| `paper/` | 55 / 55 | 24.0 | Manuscripts, supporting materials, templates, handbook/rubric and existing archives |
| `paper_experiments/` | 283 / 283 | 58.6 | Tracked machine evidence also read by runners, tests and frontend panels |
| `experiments/` | 2,276 / 1 | 1,342.9 | Mostly local run outputs; one tracked exception requires explicit handling |
| `scratch/` | 1,098 / 0 | 695.2 | Local working material; includes holdout-related paths, not automatically disposable |
| `data/` | 624 / 0 | 9.0 | Local input corpora and split material |
| `literature/` | 41 / 0 | 83.1 | Local source library and publishing templates |
| `media/` | 29 / 0 | 66.7 | Local clinical-letter story assets, source material and audio |
| `scripts/` | 61 / 60 | 0.6 | Checks, study runners, builders, shell/PowerShell helpers |
| `configs/` | 4 / 4 | <0.1 | Gan and ExECT study configurations |
| `examples/` | 1 / 1 | <0.1 | Three-letter Gan/vLLM walkthrough input |

Other roots: `.github/` contains CI; `logs/` is empty; `tmp/` and `.tmp/` are
local temporary output; `.trace_explorer/` is local app state. `.venv/`, tool
caches, `.skills/`, and `.worktrees/` are environment state. Keep credentials in
`.env` local; never include their values in the migration inventory.

`PROJECT_STATUS.md` and `CONTEXT.md` are ignored local files. Contrary to the old
README, much of `docs/` and all observed `paper/` files are tracked. Gitignore
patterns do not untrack existing files. A move must preserve the intended
visibility, not merely copy the old ignore rules.

### Proposed target structure

Keep one Python package and one frontend. Organise publications by output,
results by evaluation, and studies by question. Avoid a new package architecture
until the longitudinal pilot demonstrates what can actually be shared.

```text
README.md                         project entry and runnable examples
AGENTS.md                         cross-track working and evidence rules
PROJECT_STATUS.md                 local current task state
CONTEXT.md                        local glossary, narrowed during migration
pyproject.toml / uv.lock          package and pinned development environment
run.py / requirements.txt        retained external Gan runner compatibility
src/clinical_extraction/
  core/                          demonstrated shared functionality
  tasks/                         existing Gan/ExECT implementations retained
  longitudinal/                  new implementation, added with the pilot
  operational/                   supported operational entry points
  paper/                         existing benchmark replay API, initially retained
  architecture/                  existing generators and manifests
  trace_explorer/ / observatory/  retain until their consumers are classified
frontend/                         shared UI; benchmark views and new patient views
configs/{gan2026,exectv2,longitudinal}/
tests/                            current checks plus new behavior checks
scripts/{checks,benchmarks,longitudinal,publications}/
examples/{gan2026,exectv2,longitudinal}/
publications/
  dissertation/                  current paper sources, supporting materials, notes
  exect-comparison/               only when an actual manuscript is created
  longitudinal-benchmark/         only when an actual manuscript is created
results/
  letter-benchmarks/              existing paper_experiments subtree, intact initially
  longitudinal/<version>/<study>/ reviewed results and reproducibility metadata
runs/                             ignored execution outputs, organised by study
  archive/                       local historical runs required for provenance
scratch/                          ignored transient and quarantined working material
data/                             local-only; versioned release exports are separate
  sources/{gan2026,exectv2}/       source copies + preserved IDs and split provenance
  longitudinal/<version>/         generated letters, annotations, splits, QC
media/<purpose>/                  local production assets; served exports in frontend
literature/                       local reading copies; no automatic redistribution
docs/
  README.md / NAVIGATION.md       brief entry and ownership map
  plans/ACTIVE_ROADMAP.md         this plan, the sole roadmap
  longitudinal/                  annotation, generation, evaluation and task definition
  benchmarks/{gan2026,exectv2}/   retained dataset-specific policies and limitations
  design/                        shared software/evidence design
  research/{gan2026,exectv2,longitudinal,shared}/  protocols and result interpretation
  architecture/                  generated implementation reference until recategorised
  reference/                     terminology and literature synthesis
  runbooks/                      repeatable operations
  history/                       superseded guidance, scoped and dated
```

Create a directory when its first owned artifact exists. Dataset release packaging
and storage are decided after volume and sharing review; the target tree does not
authorise committing full raw runs, private source material, or hidden test gold.

### Disposition and dependency map

| Current location | Proposed disposition | Dependencies and completion evidence |
| --- | --- | --- |
| Root `README.md`, `AGENTS.md`, status and glossary | Retain names; make new direction primary and old task terms explicitly scoped | One active plan; public README does not require ignored files to explain the project |
| `paper/` | Move to `publications/dissertation/`; classify draft, final, reference/template and historical material within it | TeX image/bibliography paths, supporting-material links and figure builders; build and visually inspect affected PDFs; preserve earlier output provenance |
| `paper_experiments/` | Move as one unit to `results/letter-benchmarks/` before attempting any internal split | Inventory/roster pointers, replay commands, tests, panel APIs, figure builders and stored path strings; retain schema and method IDs |
| `src/clinical_extraction/paper/` | Keep import/CLI compatibility initially; scope it as existing benchmark runners | `python -m clinical_extraction.paper`, imports and external users must keep working; no cosmetic global rename |
| `src/.../tasks/`, `core/`, `operational/` | Retain; add longitudinal implementation separately after the first example | Reuse evidence/provider/IO code only where semantics match; Gan/ExECT scoring rules cannot become universal clinical rules |
| `src/.../trace_explorer/`, `observatory/`, `architecture/` | Keep working consumers; classify overlaps before consolidation | API routes, generators, caches, demo fixtures and manifest callables; do not rewrite these systems merely to match folder labels |
| `tests/` | Retain existing checks; regroup only alongside the code they exercise | Pytest paths, fixture locations, local-corpus skips and capped deep allowlist; no mass test deletion |
| `configs/` | Retain dataset namespaces; add longitudinal configurations when executable | Embedded protocol/output paths and old full200 study configs; existence never grants permission to run locked data |
| `scripts/` | Group checks, benchmark runners, longitudinal tools and publication builders | CI, pre-commit hooks, PowerShell/shell relative roots, `scripts.*` imports and documentation commands must migrate together |
| `examples/vllm_gan_three_letters.jsonl` | Move to `examples/gan2026/`; keep pinned contents; add separately labelled longitudinal example later | `VLLM.md`, operational walkthrough, commands and tests; preserve external command compatibility during transition |
| `frontend/` | Retain application; separate benchmark results, authored simulations and extracted patient histories in the UI | Existing dirty/untracked user files are preserved; browser QA of old workbench and new patient loop; no reclassification of authored simulation as benchmark output |
| `data/` | Group source corpora and new dataset versions after loader/split references are mapped | Exact source IDs, split manifests, loaders, ignore rules; old locked rows remain sealed and are excluded from seed selection |
| `experiments/` | Sort into study run folders under ignored `runs/`; preserve referenced old runs in `runs/archive/` | Embedded artifact paths, registry entries, retained-evidence hashes and the tracked exception; scan metadata/callers, not locked row failures |
| `scratch/`, `logs/`, `tmp/`, `.tmp/`, `.trace_explorer/` | Keep local operational roles; retire only confirmed regenerable residue | Some scratch paths are holdout storage or sole saved outputs; do not delete by age/name alone; restore app indexes when paths change |
| `media/` and `docs/audio/` | Keep local source assets by purpose; archive obsolete story productions locally | Source-letter provenance, audio project dependencies, app imports/served exports; preserve local-only visibility |
| `literature/`, `docs/literature/` | Retain local reading copies; put authored synthesis under `docs/reference/` | Separate copyrighted copies, authored reviews and publication templates; do not turn ignored PDFs into tracked files during consolidation |
| `docs/paper/`, `docs/research/paper/` | Put manuscript-specific prose under publication notes; shared benchmark policies under `docs/benchmarks/`; keep research evidence under `docs/research/` | Classify file by purpose; existing Gan manuscript and wider ExECT tables have different claim owners; repair incoming links before removal |
| `docs/canon/`, `docs/decisions/` | Archive superseded guidance under `docs/history/`; migrate still-applicable safeguards into active owners | The old canon is already superseded; preserve rationale and code/test callers; avoid a second live claim register |
| `docs/design/`, `reference/`, `runbooks/` | Keep shared content; relocate dataset-only policy to its benchmark home | Some procedures contain old model/split permissions; make scope explicit before reusing |
| `docs/research/`, `docs/experiments/` | Consolidate study prose into `docs/research/<track>/`; retain required evidence; archive closed narrative | 271 research Markdown files and 73 experiment Markdown files need file-level classification; no wholesale deletion based on directory |
| `docs/architecture/` | Keep generated reference in the first migration; re-scope only through generator changes | `scripts/build_architecture_docs.py` and `tests/test_architecture_stage_manifests.py` enforce generated content |
| `docs/plans/` | This roadmap remains active; prior plans become scoped historical records | Supersede old paper-only pruning instructions; no renewed authorisation for old experiment queues |
| `.github/`, `.pre-commit-config.yaml`, `.gitignore`, package manifests | Retain; update with each affected move | Clean public-checkout CI, tracked/local boundaries, packaging and path discovery |
| `.env`, `.venv/`, caches, `.skills/`, `.worktrees/` | Keep as environment state outside content reorganisation | No credential inspection, virtualenv move, worktree deletion or dependency churn |

Known hard callers include `src/clinical_extraction/paper/{gan,exect,gan_panel,exect_panel}.py`,
`gan_cell_replay.py`, `exect_cell_replay.py`, `gan_result_figures.py`, the operational
CLI, `scripts/build_*`, `tests/test_paper_*`, panel tests, and CI's documentation
hygiene paths. Use these as starting points; Phase 0 still requires a complete
per-move caller search, including JSON metadata, TeX, TypeScript and ignored local
configuration. Do not enumerate or print locked row content to find path strings.

### Migration procedure and acceptance

1. **P0.1 Baseline and ownership.** Record dirty files, active writers, tracked and
   ignored paths, selected output hashes, replay commands and baseline check
   results. Verify the state of the previously reported September 5 hosted runs
   before moving any directory they might write to. Do not infer completion from
   the old status log. Preserve current frontend work and the user's deleted
   `FES.out`/`FES.pdf`; do not restore them to make the tree clean.
2. **P0.2 File-level disposition.** Expand the table into a migration mapping for
   each moved file: source, destination, purpose, callers, visibility, byte hash,
   and rollback location. This is a migration artifact, not a new evidence/claim
   register. Audit reference and licensing boundaries before any public export.
3. **P0.3 Representative move.** Move the pinned Gan example with its callers;
   verify the walkthrough without a paid model call. Prove the mapping/check
   approach on this bounded slice before spreading it.
4. **P0.4 Documentation and publications.** Rehome manuscript assets and obsolete
   guidance. Update TeX, builders and links in the same slice. Keep already-issued
   manuscript outputs identifiable. Do not rewrite scientific results while moving.
5. **P0.5 Results and run paths.** Introduce explicit artifact-root resolution,
   then migrate `paper_experiments/` and referenced local runs. Support one
   canonical writable location; temporary read compatibility must have a removal
   condition. Preserve raw-output bytes and version IDs; record old-to-new paths
   separately rather than silently rewriting provenance inside immutable records.
6. **P0.6 Helpers and data.** Group scripts and configs, repair CI/imports, then
   move source data only when loader and split references are covered. Keep
   public-safe manifests separate from private files. Verify ignore rules before
   adding anything to Git. Shared package and frontend roots remain in place.
7. **P0.7 Verify and close.** Compare hashes and aggregate replay outputs; verify
   supported CLI/API paths, public-checkout behavior, affected PDF builds and UI
   flows, link integrity, generated-doc consistency and package checks. Inspect
   only permitted development examples; holdout remains aggregate-only. Record
   any pre-existing failures separately and resolve migration-induced failures.

Rollback each slice using the recorded move mapping and preserved bytes; never
use a hard reset or a clean command against the user's working tree. Keep the
prior path readable until its dependent readers are migrated, then remove the
compatibility path. Hash equality proves bytes survived; it does not prove
runtime behavior, so both checks are required.

Phase 0 ends when the selected layout is implemented, required checks pass, old
results remain reproducible, the documentation has one current owner per concern,
and a new longitudinal example has an unambiguous destination. Planning this map
alone does not complete Phase 0. If a move proves disproportionately disruptive,
record a bounded retained-path exception and its reason here instead of inventing
another migration project or blocking the pilot on cosmetic package renaming.

### Migration progress

- **Slice 1 (P0.1–P0.3)** executed on 2026-09-08: baseline captured (with PID 26725
  identified as a live runner targeting `experiments/paper/gan_llm_extract_encode_select/`),
  partial file-level mapping created (covering P0.3 exact move and group proposals; full
  mapping remains in progress), and `examples/vllm_gan_three_letters.jsonl` relocated
  to `examples/gan2026/vllm_gan_three_letters.jsonl` with callers and walkthroughs updated.
  See the tracked migration record at
  [`docs/research/maintenance/repository_migration_2026-09-08.md`](../research/maintenance/repository_migration_2026-09-08.md).
- **Slice 2 (P0.4 publication materials move)** executed on 2026-09-08: all 55 tracked
  manuscript and supporting files moved intact from `paper/` to `publications/dissertation/`
  with byte parity verified, filesystem callers updated (`FIGURE_DIR` in `gan_result_figures.py`,
  template path in `test_gan_extract_label_forms_prompt.py`), active Markdown links updated,
  and PDF compilation behavior verified before/after the move.
- **Remaining Phase 0 scope**: P0.2 continuation (complete file-level migration mapping for
  remaining trees), remaining P0.4 (documentation migration: `docs/paper/`, `docs/canon/`,
  `docs/decisions/`), P0.5 (results and run paths), P0.6 (helpers and data), and P0.7 (verification
  and closure).

## Timeline and dependencies

Indicative elapsed working weeks from the start of execution, assuming one primary
researcher with implementation assistance. Re-estimate after Phase 0 and the pilot.
These are planning allowances, not committed dates. Partner review, annotation
capacity, real-data access and publication introduce external calendar time.
No deadline or model budget has been supplied.

| Phase | Window / effort allowance | Depends on | Required outcome | Accountable owner |
| --- | --- | --- | --- | --- |
| 0. Restructure repository | W1–2 / 5–10 working days | Current plan | Verified migration with replay and visibility preserved | Conor + implementation contributor |
| 1. Define research tasks | W3 / 3–5 days | P0 | Bounded questions, prior-work comparison, success criteria | Conor |
| 2. Design annotation through cases | W4–5 / 7–10 days | P1 | One worked patient, then 12-patient annotated development pilot | Conor; clinical input if available |
| 3. Build generation and QC | W6 / 4–5 days | P2 | Reproducible small generation batch, checked against final text | Implementation contributor; Conor reviews |
| 4. Complete functional prototype | W7–8 / 7–10 days | P2–3 | Letters → evidence → both patient views → cohort answer | Implementation contributor |
| 5. Review and revise pilot | W9 / 3–5 internal days plus reviewer time | P4 | Internal review and, when available, clinician feedback with decisions | Conor; prospective clinical reviewers |
| 6. Freeze and generate corpus | W10–11 / 7–10 days | P3–5 internal decisions | Versioned ~300-patient provisional corpus and sealed test partition | Conor + implementation contributor |
| 7. Compare pipelines | W12–13 / 7–10 days | P6 and frozen evaluation protocol | Reproducible component and downstream results | Conor + implementation contributor |
| 8. Obtain expert reference | W14 onward / capacity-dependent | P5 collaboration; P6 materials | Independent annotation, adjudication and reference-quality report | Clinical annotation lead, once agreed |
| 9. Release and paper | After P7; claims depend on P8 | Release checks and chosen claim level | Versioned research release and bounded manuscript | Conor; coauthors if agreed |
| 10. Evaluate real-record transfer | Separately scheduled | Partner/access arrangements; frozen candidate | Independently evaluated real longitudinal cohort | Clinical/data partner + Conor |

Phases 1–4 can proceed without a clinical partner. If external feedback is late,
internal pilot findings can support continued synthetic development; record that
clinical design review is missing. Expert-reference claims require Phase 8.
Real-record transfer claims require Phase 10. Scale-up can be delayed if the pilot
shows fundamental ambiguity or unacceptable annotation effort.

## Phase tasks and evidence of completion

### Phase 1 — Define the questions and scope

- P1.1 Compare the attached Xie, ExECT/ExECTv2, Gan, Chang and temporal-reasoning
  work with available longitudinal benchmarks. Verify bibliography and current
  publication versions. Distinguish existing longitudinal applications from
  explicit cross-letter annotation/evaluation. Do not claim first or better yet.
- P1.2 Define cohort questions, their index dates, follow-up windows, eligibility,
  missing-data policy and allowed evidence. Choose a primary downstream endpoint
  before comparing models; retain extraction/linking metrics as explanatory tests.
- P1.3 Specify the two views precisely: only information available by the cutoff
  for the visit account; later evidence permitted and attributed retrospectively.
  Clarify clinic date versus document availability date, delayed letters, and
  missing/partial dates. Known patient IDs are supplied; patient matching is out.
- P1.4 Resolve seed eligibility: existing ExECT `dev140` cannot supply 150 distinct
  seeds. Choose additional permitted source material, fewer unique seeds with
  disclosed reuse, or a revised allocation. Never use `test60`/`test450` to fill
  the gap. Audit source terms and duplicate lineage before generation or sharing.
- P1.5 Set the coverage matrix, model budget, sampling rationale and evidence
  thresholds for scaling. Record the 300-patient target as provisional.

Completion: one task definition and literature rationale under `docs/longitudinal/`
and `docs/reference/`; every proposed annotation field has a downstream purpose.

### Phase 2 — Design annotation through patient examples

- P2.1 Author one three-letter patient and expected answers in both views. Include
  concurrent patterns, a medication plan not enacted, and later reinterpretation.
- P2.2 Draft the minimal annotation guide. Specify patient/letter/mention IDs,
  source spans, assertion source/certainty/negation, event time versus documentation
  time, and links for repetition, updates, corrections and unresolved conflict.
- P2.3 Define family-specific meanings: seizure identity separate from diagnosis;
  bounds/ranges/count intervals separate from point rates; clusters separate from
  events per cluster; type-specific absence separate from global seizure freedom;
  drug prescription/plan/use separate; investigation request/performance/result
  separate. Missing information is not absence or cessation.
- P2.4 Define conservative linkage and conflict rules. Different time windows or
  seizure types are not contradictions. An apparent correction needs evidence;
  uncertain identity may remain unresolved. Repeated text is not independent
  corroboration. Preserve author/reporter disagreement rather than voting it away.
- P2.5 Expand to 12 patients and 36 letters covering ordinary unchanged follow-up,
  copied history, change of terminology, sparse dates, contradictory reports,
  no-reference letters, irregular follow-up and missing outcomes. Do not put every
  difficulty in every letter. Separate text-supported reference from hidden
  generation truth and record multiple acceptable answers where justified.
- P2.6 Dry-run annotation and scoring with a second independent pass. Measure
  time and disagreement by family, time field and relationship; identify costly
  fields that do not change any query. Revise before implementing the full schema.
  Audit model-facing schemas/instructions with the plain-language prompt skill.

Completion: inspectable case pack, annotation guide, provisional schema and query
answers with explicit unresolved cases. The pilot is development evidence, not
expert gold. Guide and schema have one owner each and version together.

### Phase 3 — Generate and check synthetic records

- P3.1 Specify generation as patient history → consultation documentation →
  seed-informed letter → reference checked against the finished letter. Model
  names, prompts, randomness, source lineage and revision history are recorded.
- P3.2 Separate clinical scenario from writing style. Vary length, shorthand,
  uncertainty, omissions, repeated text and consultation gaps. Do not create
  deterministic links between seed source/style and clinical outcome.
- P3.3 Implement IDs, versioning, validation, resumable generation and cost limits.
  Run one patient, five patients, then the small pilot batch; inspect each stage
  before increasing volume. Retry failures without silently dropping hard cases.
- P3.4 Check evidence spans and semantic support, temporal plausibility, bounds,
  duplicate text/seed families, contradiction provenance and query answerability.
  An independent model may flag issues but cannot establish clinical correctness.
- P3.5 Preserve raw generations, edits, rejected outputs and rejection reasons in
  local run records. Accept uncertainty where it is intended; avoid filtering the
  corpus to only cases a teacher/extractor can agree on.

Completion: regenerate a small batch from saved configuration, trace every
accepted reference to final letter evidence, and explain failed or revised cases.

### Phase 4 — Build one full user loop

- P4.1 Load letters and extract evidence-supported facts with versioned outputs.
- P4.2 Link patient-specific events and assemble both histories. Keep extraction,
  normalisation, linking, semantic repair and downstream query policy separable.
- P4.3 Implement cohort queries with explicit cutoff dates, observation windows,
  unknown/indeterminate results and supporting evidence. Do not infer treatment
  causality from before/after frequency changes.
- P4.4 Extend the existing frontend with a patient selector, ordered letters,
  visit/retrospective switch, evidence navigation, and a cohort query view. Show
  ambiguity, empty results, loading/failure and retry paths. Clearly identify
  authored examples, generated annotations and actual pipeline predictions.
- P4.5 Evaluate linking with reference letter annotations as input as well as
  predicted input, isolating extraction errors from history reconstruction errors.
- P4.6 Run automated checks and browser QA with keyboard navigation and readable
  evidence displays. Demonstrate a later correction changes the retrospective
  answer while leaving the earlier as-known answer reproducible.

Completion: a reproducible 12-patient demonstration with one complete cohort task
and both temporal views. No clinical validation or deployment claim.

### Phase 5 — Review before large-scale generation

- P5.1 Prepare a short collaborator pack: research question, worked cases, guide,
  functioning demo, known ambiguities, annotation-time estimate and concrete ask.
- P5.2 Conor chooses contacts and authorises outreach to prospective King's or
  Swansea collaborators. No partner commitment is assumed by this plan.
- P5.3 Obtain feedback on clinical distinctions, longitudinal usefulness,
  annotation burden, plausible letters, and missing cases. Record reviewer role
  and scope; internal review remains separately labelled if experts are unavailable.
- P5.4 Revise the schema, query definitions and pilot together. Decide proceed,
  revise or reduce scope using the Phase 1 criteria. Keep disagreements visible.

Completion: recorded design decisions and remaining limitations. Unavailable
reviewers delay expert validation, not reversible prototype work.

### Phase 6 — Freeze the provisional dataset and scale

- P6.1 Freeze annotation/generation/QC versions and split policy. Split at patient
  and seed-family level; keep duplicates, paraphrases and reused seed descendants
  together. Audit pre-existing source duplication before assigning partitions.
- P6.2 Set train/development/test counts based on the final eligible patient count,
  coverage and required precision. Keep pilot cases in development. Seal test
  letters and labels from pipeline developers; route test QC through an independent
  reviewer or controlled process. Cases inspected for development cannot be test.
- P6.3 Generate in bounded batches to the agreed target; monitor cost, time, rejection
  rate, clinical scenario coverage and style balance. Record every exclusion.
- P6.4 Produce the dataset card, machine-readable manifest, checksums, generation
  provenance, data dictionary and query reference. Clearly label provisional AI
  annotations; keep hidden generation truth separate from public task inputs.
- P6.5 Review what can be shared, what stays local, and what is withheld for test
  evaluation. Do not inherit source-corpus publication permission by assumption.

Completion: a versioned, reproducible synthetic corpus with known counts,
provenance, coverage and protected splits. Expert annotation is still separate.

### Phase 7 — Compare approaches and attribute differences

- P7.1 Predeclare the primary endpoint, baseline configurations, model versions,
  prompts, scorer, failure/abstention handling and frozen test-use policy.
- P7.2 Compare latest-letter-only, independent letter extraction with simple
  aggregation, one model reading all available letters, and the linked-history
  pipeline. Give each approach the same permitted time cutoff. Where possible,
  share extraction outputs and hold models/budgets fixed to isolate linking.
- P7.3 Report extraction, qualifiers/time, linking, evidence support and downstream
  answers separately. Score both temporal views, including unresolved cases and
  unjustified certainty. Do not report only a single micro-F1 over all attributes.
- P7.4 Run ablations for cross-letter links, repeated-text handling and later
  corrections. Inspect rescues and harms on development cases only. Include style
  transfer and simpler/ordinary histories as well as difficult slices.
- P7.5 Estimate uncertainty with patient/seed-family dependence respected. Report
  subset denominators, coverage, cost, latency, parse failures and annotation source.
- P7.6 Freeze candidates before locked evaluation; report permitted aggregates.
  A discovered holdout defect starts a new development candidate/dataset version;
  it does not permit silent repair and retesting of the same claim.

Completion: machine-readable results, reproducible report, bounded interpretation
and a decision on what improved. AI-reference results measure performance against
that provisional reference; they do not establish clinical accuracy.

### Phase 8 — Establish an expert reference

- P8.1 Agree clinical reviewer roles, compensation/capacity, annotation scope,
  training examples, adjudication procedure and data handling arrangements.
- P8.2 Independently double-annotate a prespecified sample without exposing AI
  suggestions in the primary agreement measurement; use development cases for
  training. If assisted annotation is studied, report it as a separate condition.
- P8.3 Measure agreement and effort by fact family, temporal relation, patient
  linking and query answer; adjudicate disagreements and audit guideline changes.
- P8.4 Release a new reference version with provenance and rerun frozen systems.
  If only a subset receives expert annotation, report that subset explicitly;
  do not label all 300 patients expert-annotated.

Completion: expert-reviewed synthetic reference with measured agreement and
limitations. This does not establish transfer to real clinic records.

### Phase 9 — Publish a reproducible research package

- P9.1 Decide the release scope and destination: provisional synthetic resource or
  expert-annotated benchmark. Freeze claim wording to the evidence actually obtained.
- P9.2 Package allowed letters/annotations, splits, scorer, baselines, documentation,
  limitations and provenance; define access to held-out labels and contamination
  implications. Verify installation and examples in a clean environment.
- P9.3 Write the longitudinal paper in its own publication directory. Link claims
  to versioned results; preserve the prior dissertation and ExECT comparisons.
- P9.4 Review artifacts, source terms, identifiers, accessibility of the demo,
  reference quality and reproducibility. Conor confirms audience/destination and
  external publication before release; record version/DOI only after issued.

Completion: a released resource and manuscript with explicit synthetic/expert/real
claim boundaries. Publishing a resource is distinct from acceptance of a paper.

### Phase 10 — Evaluate transfer to real longitudinal records

- P10.1 Agree access, governance, patient-level sampling, independent annotation
  and evaluation responsibilities with a clinical partner. Raw records can remain
  at the institution with only approved aggregate outputs returned.
- P10.2 Freeze the pipeline, schema and evaluation before evaluation access. Define
  how clinical differences, missing follow-up and unavailable information are scored.
- P10.3 Report external cohort results, distribution differences and limitations.
  Keep changes motivated by real test failures in a new development protocol.

Completion: evidence on a named real cohort. Clinical workflow validation and
production deployment remain separately scoped future work.

## Owners, verification and risk controls

During migration, active pointers use existing paths. After migration, update this
map rather than leaving competing owners:

| Concern | Current or planned owner |
| --- | --- |
| Scope, timeline, migration | This document |
| Current task state and check results | `PROJECT_STATUS.md` (local-only) |
| Navigation and document roles | `docs/NAVIGATION.md`, `docs/runbooks/documentation_lifecycle.md` |
| Longitudinal task, annotation, generation, evaluation | `docs/longitudinal/` files created in Phases 1–3 |
| Existing paper argument | `docs/paper/README.md`, then publication-specific notes |
| Existing machine evidence | `paper_experiments/inventory.json`, then preserved results inventory |
| New study protocol and report | `docs/research/longitudinal/<study>/` when a study starts |
| New run records and reviewed results | local `runs/`; reviewed `results/longitudinal/` after migration |

Before broad engineering completion, activate `.venv` and run `python -m pytest`,
`python -m ruff check src tests`, `python -m mypy src`, and the documentation hygiene
check. Use the documented frontend checks and browser QA when it changes. Run only
focused checks during iteration; deep pytest is the capped allowlist, not routine.
No expensive model call, broad artifact regeneration or locked-row inspection is
needed merely to plan or document this work.

Main risks and responses:

- **Migration breaks reproducibility:** baseline hashes plus no-call replay; move
  callers and assets together; retain existing CLI and schema identities.
- **Local data becomes public:** inspect tracked status and ignore behavior before
  every move; export from an explicit reviewed allowlist, not the working tree.
- **New schema recreates annotation burden:** use one patient, then the pilot;
  measure effort/disagreement and remove fields without a question they support.
- **Generator teaches the benchmark its own assumptions:** separate hidden history,
  documented evidence, independent review, scenario/style factors and scoring.
- **Leakage through patient relatives, time or development review:** group seed
  descendants; enforce cutoff inputs; independently review sealed test material.
- **Overstated usefulness:** test cohort answers directly; distinguish synthetic
  reference agreement, expert-reviewed synthetic accuracy and real-record transfer.
- **Scope expansion:** keep prediction, broad patient-history mining, new diagnoses
  inferred from investigations, and clinical deployment outside the first release.

Pre-change tracked plans remain recoverable at `8da94df5`. The old ignored status
and glossary were preserved locally in
`scratch/project-history/2026-09-08-before-longitudinal-plan/`. Neither historical
plan text nor an old queue entry authorises resuming experiments under this plan.
