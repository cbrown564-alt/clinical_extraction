# Reproducing selected evidence

## Naming-refactor regeneration scope

The repository is being refactored around plain method and pipeline names. The
refactor must regenerate permitted evidence from the new baseline rather than
preserve obsolete active identifiers for compatibility.

The refactor must preserve live generation for the selected six-model ×
three-method × two-task matrix, frontend development workflows, saved/fixture
demonstrations, and exact no-call replay. “Reproduce” means protocol
reproduction for a new run plus exact replay from the retained raw output; it
does not promise identical live text from a nondeterministic provider.

This ledger is the owner for the refactor's regeneration triage. The first
initial bounded inventory is complete against frozen `c3a6fbb7`, the working
tree, Git history, and Git-LFS pointers. Dependency classification started
in the [2026-08-16 candidate table](research/maintenance/retention_candidate_table_2026-08-16.md).
The keep-set and remaining leftovers after the living-stack freeze and
the docs/scripts confident cut are in
[retention keep and leftovers](research/maintenance/retention_keep_and_leftovers_2026-08-16.md).
It does not inspect locked rows, make model
calls, or regenerate broad artifacts. Status below describes what retained
inputs support now; it does not authorize a new prediction run.

| Artifact family and paths | Owner | Status | Blocker or boundary | Scientific value | Action |
| --- | --- | --- | --- | --- | --- |
| Six reference cells in `docs/experiments/retained_evidence_manifest.json` (the three ExECT and three Gan paths listed under `reference_cells`) | Retained evidence index; claim boundary in `docs/canon/10_paper_provenance.md` | Exact no-call replay is supported by recorded closure; no new run made. | Freeze predates `c3a6fbb7`; prediction-bearing changes need a new freeze and protocol. | Minimum two-task × three-method comparison. | Keep; run narrow manifest/replay checks after the refactor slice. |
| Supporting packages: `experiments/gan2026_six_model_validation_comparison_20260718.json`, `experiments/gan2026_six_model_post_panel_attribution_20260720.json`, `experiments/shared_reliability_scorecard_20260718.json`, `experiments/exectv2_published_metric_reproduction_deterministic_all9_dev140_20260714.json`, and the review substrate under `docs/experiments/` | Manifest selection; claim status in `docs/canon/10_paper_provenance.md`; current evidence in `PROJECT_STATUS.md` | Retained no-call/deterministic packages; no fresh model results. | Some are diagnostics, aggregate-only evidence, or unstarted review substrate. | Named prompt, component, negative, safety, reliability, and limitation claims. | Keep named packages; run narrow builders only when inputs change. |
| Retired 11 Aug LFS forests (2-call, `v08` producers, July 18 v0.7 Gan rows, 13 Aug explorer replay) | Living-stack freeze `retained_comparison_architecture_20260816` | Removed from the working tree on 2026-08-16. | Decision 0046/0050 already demoted those cells. | Historical architecture evidence. | Recover from Git history. Do not restore as live slots. |
| Gan row-level LFS artifacts under `experiments/gan2026_six_model_validation_20260718/` and post-panel attribution | Living-stack freeze | Removed 2026-08-16 with the explorer tree. | `validation750` was legacy `dev750`; v0.7 post-panel was diagnostic. | Component attribution and development limits. | Recover from Git history. |
| Current closure: `src/clinical_extraction/architecture/manifests/`, `src/clinical_extraction/tasks/`, `configs/`, `tests/`, `pyproject.toml`, `uv.lock`, `scripts/check_retained_evidence_manifest.py` | Decision 0047; manifest closure records | Implemented at `c3a6fbb7`; no live run here. | Decision 0048 requires a new freeze if clinical behavior changes. | Explainable source/config/scorer/test reproduction. | Use as producer closure; prove one bounded Gan slice before spreading names. |
| Generated architecture in `docs/architecture/`, built by `scripts/build_architecture_docs.py` from manifests and teaching cases | Architecture manifests and builder; Decision 0048 | Retained and checked before baseline; not regenerated here. | Rebuild after source/name changes; do not hand-edit. | Supervisor comprehension and six-path demonstration. | Keep; run `--check` after bounded refactor. |
| Frontend and trace explorer: `frontend/` and `src/clinical_extraction/trace_explorer/`, plus fixture/trace inputs referenced by frontend tests | Decision 0048 operational surface; frontend tests | Retained requirement; no broad frontend build. | Live development and restricted validation are separate; no real-patient or locked data here. | Demonstrates selected methods and teaching workflow. | Keep selected routes/fixtures; audit callers during refactor. |
| Historical experiments and decisions: `experiments/`, `docs/experiments/`, `docs/decisions/0040-0047*.md`, focused `docs/research/` | Each decision/report; lineage in `experiments/registry.jsonl` | Mixed: selected evidence replayable; closed candidates explanatory; others unclassified. | Superseded producers/policies may not support current claims. | Rejected rules, negative studies, and design limits. | Keep named decision evidence; trace unselected candidates before deletion. |
| Removed generated/cache noise visible in `c3a6fbb7`: `.tmp/`, notebook charts, review HTML, cache-like files | Baseline cleanup commit | Retired; not retained deliverables. | No current claim or replay dependency identified. | None identified. | Leave removed; do not restore without a named owner. |
| Early HTML prototype `experiments/pipeline_flow_prototypes_20260716.html` (removed 2026-08-02) | Decision 0048 cleanup slice; [`docs/design/pipeline_trace_explorer_spec.md`](design/pipeline_trace_explorer_spec.md) | Deleted after classification; superseded by live frontend and trace explorer. | Not in manifest, registry, or six reference replays; no code or test caller. | Design decisions captured in the trace explorer specification. | Removed in cleanup commit; recover from Git history if needed. |
| `experiments/archive/gan2026_validation750_iterations/` (three Gan three-way comparison Markdown reports) | Living-stack freeze | Removed 2026-08-16; June 7 cells are no longer reference cells. | Git history is the restore. | Original run summaries for the retired mini matrix. | Leave removed. |

## Broad retention review: inventory-only phase

This phase may run while an ExECT prompt iteration is still active. It is an
inventory and dependency-mapping exercise only: no prompt, script, experiment
output, protocol, or source file in the active iteration may be deleted,
renamed, or collapsed until the iteration owner declares its stopping point.
The review must not make model calls or inspect locked rows.

The first inventory found a status boundary that needed resolving before any
retention decision: `PROJECT_STATUS.md` then stopped at v21, while the working
tree contained a measured v22 study and untracked v24 panel/transfer work.
Status has since been updated through `v0.9.24`. The three current-hybrid
ExECT prompt slots are assigned:
[prompt variant slots](research/exectv2/prompt_variant_slots_2026-08-16.md).
Unused structured-prompt zoo dumps, abandoned semantic-inventory /
mention-unit v1 lanes, and intermediate prune experiment dirs are
removed; Markdown prune answers for `v0.9.24` remain. The follow-on
2026-08-16 experiments dump prune kept only named owners (current-stack,
retained-manifest cells/packages, prompt slots, GEPA/v08, E5/G5 and
stage ablations, paper companions, and the Gan `dev750` current-stack
replay). All other retention families proceed in parallel.

### Initial ExECT prompt-family map

| Group | Current evidence | Provisional role | Action during inventory phase |
| --- | --- | --- | --- |
| `v0.9.24` | Selected live prompt; current six-model and replay identity | Prompt slot 1 | Keep as the live default |
| Cheap stack (`v0.9.44`) | Stacked further prune of the cheap stack; `dev140` remasure in progress | Prompt slot 2 | Keep as the cheap variant; do not promote |
| Mention-unit v2 | Fork A representation alternative; encoder pairing open | Prompt slot 3 | Keep the prompt identity; do not select an encoder |
| `v08` | Historical hybrid control owned by Decision 0046 | Reference cell; not a current-hybrid prompt | Keep the reference-cell bundle |
| v10–v27 zoo / SI / MU v1 | Intermediate drafts and abandoned lanes | Removed from working tree | Recover from Git history if needed; do not restore as live slots |

The three assigned slots and the `v08` reference cell are the live
owners. Intermediate zoo runners, dumps, and campaign notes are not
kept as parallel methods.

### Other initial component groups

| Component | First-pass candidates | Provisional handling |
| --- | --- | --- |
| Architecture | Selected one-call structured hybrid; historical `v08`; GEPA dedup LLM-only negative comparator | Treat as separate architecture slots. The GEPA package has a clear canonical owner in `docs/canon/08_gepa.md` and one retained run. Search Git history and decisions for the multi-agent work before deciding whether it has a comparable retained package. |
| Model-generation comparisons | DeepSeek V4 Flash prior versus 0731 matched comparison; Qwen 3.6 baseline versus reserved Qwen 3.8 candidate | Keep these outside the prompt cap. Each can qualify only through a named progress or follow-up question, with matched data, method, and scorer recorded. |
| Deterministic rules/projection | ExECT rules-only parity, SF projection campaign, and model-preserving/joint policy alternatives | Catalog by semantic responsibility and selected/rejected outcome. Do not retain every dated rule study when a final rule owner and one explanatory negative study cover the same decision. |

The initial path scan found no tracked multi-agent-named artifact. That is an
inventory result, not evidence that the work never existed; Git history,
decisions, and deleted-file references must be checked before closing that
branch.

### Hierarchical retention slots to resolve after the freeze

For both **ExECT** and **Gan 2026**, the system defines three core methods:
1. `llm_with_rules` (Hybrid)
2. `llm_only` (Pure model baseline)
3. `rules_only` (Deterministic baseline)

Retention and cleanup apply the three-slot cap hierarchically:

#### 1. Architecture / Pipeline Variants (up to 3 slots for `llm_with_rules`)
- **Slot 1 (Current / Selected Hybrid)**: The current production one-call structured hybrid architecture.
- **Slot 2 (GEPA Optimized / Multi-Stage Variant)**: The GEPA-optimized program or verify-stage pipeline (negative / architectural comparison).
- **Slot 3 (Agentic / Multi-Agent Variant)**: The multi-agent / ReAct ceiling evaluation pipeline.

#### 2. Prompt Variants within Current Hybrid Variant (up to 3 slots per task)
- **ExECTv2 Prompt Family** ([assignment](research/exectv2/prompt_variant_slots_2026-08-16.md)):
  - **Slot 1 (Selected Live Baseline)**: `v0.9.24` (current six-model and replay identity).
  - **Slot 2 (Cheap Stack)**: `v0.9.44` stacked further prune. Retained cheap variant. Not selected. Three-model `dev140` remasure in progress.
  - **Slot 3 (Mention-Unit Encoder)**: `exectv2_mention_unit_v2`. Representation alternative. Encoder pairing still open (`landed` default; `leftover_form` measured).
  - `v08` stays the ExECT hybrid reference cell. It is not a fourth current-hybrid prompt.
- **Gan 2026 Prompt Family**:
  - **Slot 1 (Selected 6-Model Baseline Prompt)**: `v0.5` matched panel (`experiments/gan2026_matched_v05_dev750_panel_20260727.json`, Decision 0043 / 0046 / 0050).
  - **Slot 2 (Multi-Model Ablation Prompt)**: Luna prompt variants (`experiments/gan2026_luna_prompt_variants_dev750_20260730/panel.json` / exemplar pack).
  - **Slot 3 (Model Adaptation / Negative Prompt)**: DeepSeek Unknown (`v0.8_deepseek_unknown`; UNK-slice pilot, full-750 aborted). Gemini 3.7 Flash is a roster / model-generation comparison outside the prompt cap (Decisions 0051 / 0052). Decision 0053 `final` is lineage-only.

#### 3. Deterministic Rules & Projection Variants (up to 3 slots per task)
- **Slot 1 (Production `rules_only` Pipeline)**: The standalone deterministic baseline reproducing published metrics without model calls (ExECT 9-entity parity `dev140_20260714`, Gan Purist regex/token extraction).
- **Slot 2 (Hybrid Integration & State Projection Ruleset)**: The deterministic state projection and bounded normalization layer attached to hybrid pipelines (ExECT SF state projection v0.14 & Rx/Dx bounded repairs; Gan clinical assessment assembly).
- **Slot 3 (Attribution & Component Ablation Studies)**: Component attribution, rescue provenance, and removal ablation packages (Gan Qwen/Sol rule benefit audit & 6-model post-panel attribution; ExECT component-off and removal studies).

#### 4. Evidence Closure Rules
The cap applies to method and prompt variants, not to the minimum evidence closure of a retained claim. A retained slot requires:
- Exactly one protocol / predeclaration.
- Exactly one concise result / report.
- One machine-readable artifact (tracked in Git or Git-LFS).
- The necessary source/config/test closure to reproduce or replay it without model calls.

All intermediate exploration variants (such as intermediate prompt drafts v10–v15, v17–v18, v20–v22) are represented by short lineage summaries and recoverable Git history rather than parallel live files.

### Planned review order

The three ExECT current-hybrid prompt slots are assigned:
[prompt variant slots](research/exectv2/prompt_variant_slots_2026-08-16.md).
Active-iteration files stay protected until a collapse slice maps
callers. All other retention work proceeds now. Owner for the filled
slots:
[candidate table](research/maintenance/retention_candidate_table_2026-08-16.md).

1. **Done for ExECT prompts:** slots are `v0.9.24`, the cheap stack,
   and mention-unit v2. Intermediate zoo drafts are pruned; Markdown
   prune answers remain.
2. **Done for every other family:** candidate table keyed by component,
   variant, protocol, result, machine artifact, source/config
   dependency, claim supported, and reason to retain.
3. **Done for closed campaign notes (2026-08-16):** uncited
   protocol+report pairs pruned (rules-only E0–E4 intermediates,
   family-lens, Luna siblings, structured-prompt bloat/convention-
   migration notes, and similar). Living paper, slot, provenance,
   E5/G5, and Decision 0053 owners remain.
4. Apply the hierarchical three-slot cap across ExECT and Gan methods,
   architecture variants, prompt families, and rules.
5. Rebind living links, run dependency and retained-evidence checks, and only
   then remove unneeded files. Git history is recovery, not a reason to skip
   the dependency audit.

## Bounded cleanup applied 2026-08-02

The first safe cleanup slice removed the 15 tracked JSON files under
`frontend/public/mock-data/run-note/validation/`. Dependency checks found no
code, route, test, retained-evidence manifest, experiment registry, or durable
documentation reference to that directory. The active `/run/note` endpoint
executes the deterministic pipeline from the request and does not load these
fixtures. The directory was introduced as frontend fallback data, but the
current frontend has no caller for it. No source, test, selected evidence,
replay input, or clinical behavior changed. Recovery is available from Git
history or by reverting the cleanup commit.

The second safe cleanup slice removed
`experiments/pipeline_flow_prototypes_20260716.html`, an early static HTML
mock of the trace explorer. Dependency checks found no code, test, manifest,
registry, or reference-replay requirement; the only durable link was the
prototype line in `docs/design/pipeline_trace_explorer_spec.md`, now retargeted
to the live Next.js frontend and generated architecture teaching surface.
Design decisions from the prototype remain in that specification. Record:
[retention candidate table](research/maintenance/retention_candidate_table_2026-08-16.md).
Recovery is available from Git history or by reverting the cleanup commit.

The third safe cleanup slice removed three candidate-only prompt draft notes
under `docs/experiments/` (ExECTv2 Luna, Gan Luna, DeepSeek unknown U).
Inbound links were retargeted to protocols, exemplar packs, research threads,
and machine compare artifacts. Record:
[retention candidate table](research/maintenance/retention_candidate_table_2026-08-16.md).
No protocol, exemplar pack, residual analysis, or research report was deleted.

The fourth slice audited the ExECT candidate config trees
(`configs/exectv2/model_swap/`, `configs/exectv2/diagnosis_ablation/`, and
non-reference-cell files under `configs/exectv2/finding_assembly/`). No
additional files were removed: five configs remain, each referenced by the
retained-evidence manifest, a focused replay/check script, or a focused test.
Seventy-nine sibling candidate manifests were already deleted in July 2026.
Record:
[retention candidate table](research/maintenance/retention_candidate_table_2026-08-16.md).

The fifth slice evaluated the seven tracked JSON files under
`frontend/public/mock-data/artifacts/` and retained them. `FrontendDataStore`
glob-loads that directory for `/artifacts/{run_id}` replay and for ExECT
dev140 letter allowlisting; frontend components and
`tests/test_trace_explorer_frontend_api.py` depend on those loaders. Record:
[retention candidate table](research/maintenance/retention_candidate_table_2026-08-16.md).
A later delete would require refactoring those loaders onto governed
`experiments/` sources first.

The sixth slice classified `experiments/archive/`. The directory holds exactly
three tracked Markdown companions for the Gan rules / LLM-only / hybrid
reference cells. Each is a hashed retained-evidence artifact and a registry
`artifact_path`. Decision: **keep**; do not delete under an `archive/` name
alone. Record:
[retention candidate table](research/maintenance/retention_candidate_table_2026-08-16.md).

The 2026-08-14 SF extra-AR campaign cleanup kept every dated protocol,
report, and experiment JSON, deleted the uncommitted `scripts/sf_*.py`
re-export shims, and left study builders citing the production
predicate modules. Record:
[retention candidate table](research/maintenance/retention_candidate_table_2026-08-16.md).

The review covers the working tree, Git history, and Git LFS. It must not inspect
locked rows or make model calls merely to restore an old name or result. Any
new prediction-changing replay requires its own predeclared protocol and
baseline.

The initial bounded inventory and the 2026-08-02 classification wave are
complete for the named Decision 0048 cleanup candidates. The stale
fresh-evidence validation750 entry was removed from
`frontend/public/mock-data/registry.json` after both listed artifacts were
confirmed missing. The completion-gate slice removed the stale
test450 frozen-audit mock-registry entry (both listed artifacts already absent;
authoritative lineage remains in `experiments/registry.jsonl` and aggregate-only
test450 companions under `experiments/`).

### Broader corpus triage wave (2026-08-02, continued)

Inventory of mock-data leftovers, orphan docs, and 337 tracked
`experiments/` + `docs/experiments/` files. Safe deletes applied:

| Slice record | Deleted |
| --- | --- |
| unserved ExECT mock (git history) | Orphan p7fix mock; ExECT ablation/transitions fixtures (~2.3 MB) |
| orphan docs (git history) | 5 superseded/zero-inbound docs; rejected-policy protocols later pruned |
| experiments orphans (git history) | 7 tier-1 orphans (pipeline-flow PNGs, archived Luna joint panels, superseded DeepSeek diff, Qwen retry backup) |

Scoring-lane / two-call orphan cleanup and mock-registry path retarget applied
in the 2026-08-02 wave (dated slice notes are in git history; living ledger is
the [retention candidate table](research/maintenance/retention_candidate_table_2026-08-16.md))
(~99 MB deleted; five historical registry rows point at served
`mock-data/artifacts/`). Still deferred: protocol docs outside the machine
manifest that own focused evidence threads, and optional further lane
`*_sf_state_projection_combined.jsonl` review. Retained-evidence manifest check
passes after this wave. Locked-row inspection and model calls remain
unauthorized for cleanup alone.

### Documentation corpus triage (2026-08-03)

Active-index and status thinning under Decision 0048 documentation reading-path
rules. Record:
[retention candidate table](research/maintenance/retention_candidate_table_2026-08-16.md).

| Change | Disposition |
| --- | --- |
| `docs/NAVIGATION.md` | Thinned to supervisor/worker doors + evidence pointer block |
| `docs/THREAD_MAP.md` | Durable design/decision doors only in Change the implementation |
| `PROJECT_STATUS.md` | Live control panel; not an evidence catalog |
| Six orphan experiment/protocol docs | Deleted (see slice note); Git history recovery |
| Decision 0046 / 0047 | Rebound Phase A/B/C and parity summary as living owners |
| Peer research satellites | Partial cull 2026-08-03; see peer-satellite slice |

### Peer-satellite cull (2026-08-03)

Record:
[retention candidate table](research/maintenance/retention_candidate_table_2026-08-16.md).

Rebound living-cited synthesis/canon links, then deleted five satellite docs
(projection-floor report, DeepSeek holdout stub, Diagnosis interpretation
audit protocol/substrate, Diagnosis resolution protocol). Residual-analysis
report/protocol kept because machine artifacts name them. Further protocol
cull and ACTIVE_ROADMAP completed-link thinning remain deferred.

### README glance currency (2026-08-03)

Decluttered the repository front door under Decision 0048 supervisor-path
rules. `README.md` now leads with two tasks × three methods, an at-a-glance
results table that treats Gan Purist and ExECT clinical fact F1 as equal
primary strips, short system-state bullets, then the supervisor path.
Research chronology moved out of the glance layer into existing owners
(`PROJECT_STATUS.md`, comparison report, claim status). Recorded also in the
[retention candidate table](research/maintenance/retention_candidate_table_2026-08-16.md)
follow-on note. The later first-class vLLM integration retired the standalone
handoff package.

### Repository-root and stale-scorecard cleanup (2026-08-03)

Removed three unowned root-level artifact families: the static `index.html`
trace prototype and `assets/trace-hero.png`, the unlinked hosted-model notebook,
and six rendered paper pages under `tmp/pdfs/`. The maintained frontend,
canonical comparison report and paper sources supersede them. Git history is
the recovery path.

The visible per-dataset reliability-scorecard page and its backend catalog were
also retired. They described pre-selected candidate architectures, cited two
already-deleted reports, and depended on ignored files under
`experiments/_archive/`; a fresh clone could not reproduce the catalog. The
Decision 0044 shared reliability artifact, report and claim boundary remain the
current owners. Clinical fact recovery score aggregation still used by exact
replay and the selected comparison moved to
`exectv2/scoring/clinical_headline.py`; the retained-evidence manifest records
its new path and hash. No scorer behavior, prediction, split or claim changed.

Ignored local run debris was removed, including the superseded 1.18 GB
`experiments/_archive/` quarantine, GEPA optimizer internals, caches and logs.
The governed `scratch/` holdout locations were not deleted. `/tmp/` is now
ignored, the documentation-hygiene gate rejects tracked output roots, and CI
runs that gate. The pre-commit entry for the previously deleted
`scripts/check_line_counts.py` was also removed; it could not run in a clean
checkout.

The retained evidence index records selected paths, hashes, source commit, and
policy versions.

## Environment and large files

Use Python 3.11 and retrieve Git LFS objects before checking results:

```sh
uv sync --python 3.11 --frozen --extra dev
git lfs pull
```

Five large ExECT replay files use content-addressed Git LFS storage. The JSON
index records each object ID, content hash, and byte size.

## Checks

```sh
python scripts/check_retained_evidence_manifest.py
python scripts/verify_reference_evidence.py
python scripts/check_exectv2_model_led_audit.py
```

The first command checks files, hashes, sizes, run metadata, and the six selected
method results. The second replays or rescores all six without model calls.

To regenerate one result, use the entry point, configuration, scorer, data rules,
and tests listed in its `closure` record. Do not infer a producer from an old
filename. A changed selected file requires a documented reason, unchanged data
limits, new hash and size, matching run metadata, both checks, and an update to
paper claim status when the result changes.

A prediction-changing prompt, scorer, split, repair, model route, or pipeline
change requires a new recorded version. It does not authorize a model call.

## ExECT paper-derived metrics

Regenerate the additive rules-only dev140 metric artifact without model calls:

```sh
python -m clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.cli.published_metric_reproduction \
  --out-json experiments/exectv2_published_metric_reproduction_deterministic_all9_dev140_20260714.json \
  --out-md docs/experiments/exectv2/reliability/exectv2_published_metric_reproduction_results_2026-07-14.md \
  --generated-on 2026-07-14
```

This reports normalized phrase, CUI, and all-feature macro scores for all nine
entity types. It uses dev140 only and must not inspect test60 or full200 rows.

## Paper

The Markdown manuscript is `docs/research/paper/manuscript_2026-06-26.md`. The
IEEE source is under `literature/IEEE/IEEE-conference-template-062824/`. Keep
their claims and tables synchronized. Build with two `pdflatex` passes and
inspect every rendered page.
