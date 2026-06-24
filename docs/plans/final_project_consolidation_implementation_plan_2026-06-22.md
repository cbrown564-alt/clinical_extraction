# Final Project Consolidation Implementation Plan

Date: 2026-06-22

Scope: final-phase consolidation across Gan 2026 seizure frequency, ExECTv2
key-family extraction, and the clinical-extraction frontend. This plan assumes
the active ExECTv2 DeepSeek and Qwen runs may continue while no-call reporting,
artifact indexing, frontend adaptation, scorecard scaffolding, and repo
simplification planning proceed in parallel.

## Executive Summary

The project is entering a closeout phase. The scientific objective is no longer
open-ended metric chasing. It is to preserve the best evidence, produce clean
cross-model and cross-architecture comparisons, write paper-ready reliability
material, and then radically simplify the repository around the final system.

The highest-leverage rule for this phase is:

1. Freeze and index evidence before deleting, moving, or renaming artifacts.
2. Build reports from current canonical artifacts immediately, with clearly
   marked refresh slots for active Qwen and DeepSeek runs.
3. Treat GPT-4.1-mini v08 as the achieved ExECTv2 control unless a later
   predeclared run beats it on the same surface.
4. Treat local Qwen and DeepSeek as cross-model reliability evidence even when
   they do not match GPT-4.1-mini.
5. Make the frontend task-aware early, so ExECTv2 letters and final architecture
   results are reviewable in the app instead of only in Markdown artifacts.
6. Simplify the repo only after the evidence spine is durable.

## Current State

### Gan 2026

Gan 2026 has a mature reliability package. The most important durable artifact is
`experiments/gan2026_reliability_master_scorecard_2026-06-17.md`.

Current claim shape:

- The best Gan reliability story is not just accuracy. It is the combination of
  exact evidence, faithful-but-wrong analysis, risk-coverage, external
  calibration signals, robustness panels, semantic entropy, safety guards, and
  operational reconstruction.
- The reliability scorecard pattern is reusable for ExECTv2, but ExECTv2 should
  start with a lighter no-call version rather than reproducing every Gan driver.
- Gan holdout-facing reruns, test row-level analysis, and post-test tuning remain
  blocked without explicit authorization plus a frozen protocol.

### ExECTv2 GPT-4.1-mini Control

The achieved ExECTv2 control is:

- Candidate: `exectv2_holistic_finding_assembly_v08_dev140`
- Split: dev140
- Overall headline F1: `0.9152`
- Diagnosis: `0.9083`
- SeizureFrequency: `0.9053`
- Prescription: `0.9357`
- Investigations: `0.9132`

Canonical references:

- `configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v08_dev140.yaml`
- `docs/experiments/exectv2/key_entities/exectv2_holistic_finding_assembly_v08_dev140_20260621.md`
- `docs/experiments/exectv2/reliability/exectv2_reliability_scorecard_and_phased_plan_2026-06-21.md`
- `experiments/exectv2_holistic_finding_assembly_v08_dev140_20260621.json`
- `experiments/exectv2_holistic_finding_assembly_v08_dev140_20260621.jsonl`
- `experiments/exectv2_holistic_finding_assembly_v08_error_ledger_dev140_20260621.md`

Claim boundary: dev-only component evidence, not full-200, locked-test, or
benchmark claim.

### ExECTv2 Simplification Control

The best simplification result is:

- Candidate: `exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140`
- Split: dev140
- Overall headline F1: `0.9059`
- Structure: focused Diagnosis, focused SeizureFrequency, deterministic
  Prescription, prompt-owned Investigations

This is the cleanest evidence that the v08 architecture can be simplified while
staying above `0.900` overall. The pure single-GPT plus dictionary approach did
not clear the bar at GPT-4.1-mini (`0.7552`), which justifies retaining focused
producers for Diagnosis, SeizureFrequency, and Prescription.

### ExECTv2 DeepSeek

Latest observed durable artifact:

- Candidate: `exectv2_holistic_finding_assembly_v097_deepseek_dev25`
- Split: dev25
- Claim boundary: hosted-DeepSeek v0.9.7 full live dev25 diagnostic
- Overall clinical headline F1: `0.8707`
- Diagnosis: `0.8456`
- SeizureFrequency: `0.7586`
- Prescription: `0.9610`
- Investigations: `0.9091`
- Exact evidence rate in assembly: `1.0000`
- Source run: `experiments/exectv2_llm_only_key_entities_structured_v097_dev25_deepseek_chat_20260622.jsonl`

Interpretation: DeepSeek is operationally clean and strong on Prescription and
Investigations. Diagnosis and especially SeizureFrequency remain below the v08
target families. It is not currently a v08 replacement, but it is already useful
cross-model reliability evidence.

### ExECTv2 Qwen

Latest observed active checkpoint:

- Source run: `experiments/exectv2_llm_only_key_entities_structured_v097_qwencompact_dev25_qwen36_35b_ollama_cuda11435_ctx12288_maxtok2500_dictrepair_20260622.jsonl`
- Checkpoint: 9 / 25 letters processed
- Prompt profile: `v0.9.7_qwen_compact`
- Model: `ollama_chat/qwen3.6:35b`
- Call failures: `0`
- Parse/schema failures: `0`
- Evidence validity rate: `0.9667`
- Clinical-recovery checkpoint F1s:
  - Prescription: `0.903`
  - Diagnosis: `0.387`
  - SeizureFrequency: `0.667`
  - Investigations: `0.889`

Earlier Qwen evidence includes a no-call v0.9.6 dev25 schema-repair reparse at
overall `0.8082`, with Diagnosis `0.8112`, SeizureFrequency `0.6429`,
Prescription `0.8608`, Investigations `0.9268`.

Interpretation: Qwen is operationally improving but not yet promotion-ready.
Its likely role is a local-model reliability and portability comparison unless
the remaining run changes trajectory sharply.

### Frontend App

The `frontend/` app is a Next 16 React app with existing observatory,
workbench, gallery, laboratory, and gold-audit views. It already has useful
building blocks for final review:

- registry-driven run selection;
- artifact loading with mock-data fallback;
- note/letter rendering with highlights;
- run comparison tables;
- row-level error gallery;
- workbench-style stage inspection.

The current limitation is that most app types, summary metrics, confusion
categories, and gallery error logic are Gan 2026 seizure-frequency-oriented.
There is no first-class ExECTv2 task model yet, and the public mock registry
contains only Gan artifacts. ExECTv2 support should therefore be an adapter and
task-model extension, not a one-off page that bypasses the existing app.

## Final-Phase Objectives

### Minimum Closeout

Complete within 1 to 2 working days:

- Preserve canonical Gan and ExECTv2 artifacts in an explicit evidence index.
- Produce ExECTv2 cross-model comparison report from current artifacts.
- Produce ExECTv2 reliability scorecard v1 using no-call metrics and known gaps.
- Make a Phase 0 frontend adaptation plan and first implementation slice for
  ExECTv2 letters plus winning architecture results.
- Update project status so the next contributor knows the canonical controls,
  active refresh slots, and cleanup boundary.
- Define repo simplification inventory and deletion/archive policy, without yet
  deleting active evidence.

### Target Closeout

Complete within 3 to 5 working days:

- Finish Qwen and DeepSeek dev25 reads and promote only if justified.
- If one non-GPT candidate has a strong enough dev25 result, predeclare and run
  a dev140 read on the same scorer surface.
- Produce a paper-facing ExECTv2 cross-model and architecture comparison table.
- Produce a paper-facing ExECTv2 reliability scorecard parallel to Gan.
- Make the winning ExECTv2 architectures available in the frontend through the
  run registry, artifact adapters, letter viewer, and result comparison views.
- Build or refactor one reusable report driver for cross-model score tables,
  artifact indexing, and reliability-scorecard inputs.
- Archive or quarantine non-canonical experiment outputs.

### Ambitious Closeout

Complete within 1 to 2 weeks if the evidence and budget justify it:

- ExECTv2 full-200 or holdout-facing aggregate audit under a frozen protocol.
- Cross-model risk and review-routing analysis using GPT, DeepSeek, and Qwen
  disagreement.
- A polished frontend reliability scorecard view showing model/architecture
  comparison, reliability dimensions, evidence validity, and family residuals.
- Reusable reliability scorecard framework shared by Gan and ExECTv2.
- Repo reduced to clean source modules, canonical configs, canonical experiment
  artifacts, paper outputs, and a compact regression test suite.

## Workstreams

## Stream A - Evidence Freeze And Artifact Index

Goal: make it impossible to lose the final evidence trail during cleanup.

Tasks:

- Create `docs/experiments/final_artifact_index_2026-06-22.md`.
- List canonical artifacts by task:
  - Gan 2026 reliability scorecard and source drivers.
  - ExECTv2 v08 control.
  - ExECTv2 v09 partial hybrid simplification.
  - ExECTv2 DeepSeek v0.9.7 dev25.
  - ExECTv2 Qwen best completed checkpoint/run after the active run finishes.
- For each artifact group, record:
  - candidate name
  - model
  - split and row count
  - scorer/view
  - JSON/JSONL/report/config paths
  - claim boundary
  - promotion decision
  - whether row-level inspection is allowed
- Add SHA-256 hashes for canonical JSON/JSONL/config files if feasible.

Acceptance criteria:

- A reader can reconstruct the final comparison set without browsing
  `experiments/`.
- Every canonical claim points to a config, report, and machine-readable output.
- Non-canonical artifacts are explicitly marked as scratch, diagnostic,
  superseded, or active.

Parallel status: complete after the Phase 1 refresh. The Qwen slot now points to
the final v0.9.22 dev140 diagnostic row.

## Stream B - ExECTv2 Cross-Model Comparison Report

Goal: create the central report now from existing artifacts, then refresh as
new Qwen/DeepSeek artifacts finish.

Proposed file:

`docs/experiments/exectv2/key_entities/exectv2_cross_model_closeout_2026-06-22.md`

Initial table columns:

- Candidate
- Model
- Architecture family
- Split/stage
- Calls complete
- Call failures
- Parse/schema failures
- Exact evidence rate
- Overall clinical headline F1
- Diagnosis F1
- SeizureFrequency F1
- Prescription F1
- Investigations F1
- Active-rate or strict companion surface where relevant
- Decision
- Claim boundary

Initial rows:

- GPT-4.1-mini v08 dev140 control.
- GPT-4.1-mini v09 partial hybrid dev140 simplification.
- DeepSeek v0.9.7 dev25 diagnostic.
- Qwen v0.9.6 schema-repair reparse dev25.
- Qwen v0.9.7 compact dev25 active checkpoint, marked pending until complete.

Analysis sections:

- What transfers across models.
- What does not transfer.
- Which families are model-stable.
- Which families need focused architecture.
- Why v08 remains the control.
- Why v09 partial hybrid remains the simplification option.
- What evidence would justify dev140 escalation for DeepSeek or Qwen.

Acceptance criteria:

- Current DeepSeek dev25 result is included.
- Qwen is represented without overclaiming an incomplete run.
- v08/v09 are reported as controls, not mixed with dev25 diagnostics.
- All non-GPT results are clearly marked diagnostic unless promoted by a
  predeclared gate.

Parallel status: can start immediately. Update final numbers after Qwen
finishes or after DeepSeek dev140 is run.

## Stream C - ExECTv2 Reliability Scorecard v1

Goal: convert ExECTv2 evidence into the same reliability language used for Gan,
without pretending every Gan reliability dimension is already complete.

Proposed file:

`docs/experiments/exectv2/reliability/exectv2_cross_model_reliability_scorecard_2026-06-22.md`

Dimensions:

1. Task correctness.
2. Factuality and over-inference.
3. Faithfulness / exact evidence.
4. Calibration.
5. Abstention / review routing.
6. Robustness.
7. Consistency.
8. Safety and compliance.
9. Family parity.
10. Operational reliability.

No-call v1 inputs:

- v08 assembly JSON/JSONL and error ledger.
- v09 partial hybrid report and JSON/JSONL.
- DeepSeek v0.9.7 dev25 report and JSON/JSONL.
- Qwen best completed run/reparse.
- Existing residual ledgers for Diagnosis, SeizureFrequency, Prescription, and
  Investigations.

Likely v1 coverage:

- Strong: task correctness, faithfulness, safety, family parity at headline
  level, operational parse/call reliability.
- Medium: factuality/over-inference from residual ledgers, robustness from
  ablation lineage.
- Weak: calibration, abstention/review routing, consistency. These should be
  stated as gaps unless no-call proxies are built.

Optional no-call metrics:

- Exact evidence rate by model and family.
- Evidence-valid but wrong counts.
- Family-level over-emission and miss rates from residual ledgers.
- Cross-model agreement on dev25 if row IDs align across GPT/DeepSeek/Qwen.
- Simple review triggers based on provenance and residual families:
  Diagnosis assertion/hierarchy repairs, SeizureFrequency active-rate fidelity,
  Prescription current-vs-plan ambiguity, Investigations result-state ambiguity.

Acceptance criteria:

- Uses the same ten-dimension skeleton as Gan.
- Separates dev140 controls from dev25 model diagnostics.
- Does not invent calibration or abstention claims where evidence is missing.
- Names the exact next metric needed to upgrade each weak dimension.

Parallel status: can start immediately using v08, v09, and DeepSeek dev25.
Refresh Qwen row after the active run completes.

## Stream D - Active Qwen And DeepSeek Completion Path

Goal: finish active model runs without letting them block all documentation.

DeepSeek next decisions:

- Current dev25 assembly overall `0.8707`; Diagnosis `0.8456`, SF `0.7586`,
  Prescription `0.9610`, Investigations `0.9091`.
- If the goal is strict comparability to v08, DeepSeek is not ready for dev140
  promotion because Diagnosis and SF remain under `0.900`.
- If the goal is cross-model reliability evidence, DeepSeek dev25 is already
  sufficient as a diagnostic row.
- A dev140 DeepSeek escalation should require a written reason, such as testing
  whether the dev25 SF/Dx gap narrows with more rows or producing a
  paper-facing non-GPT comparison despite known under-target families.

Qwen next decisions:

- Allow the active dev25 compact run to finish if runtime remains acceptable.
- Score assembly and error ledger immediately after completion.
- If Qwen remains below DeepSeek and v08, stop local-model prompt iteration and
  report it as a local-model portability/runtime finding.
- If Qwen unexpectedly clears meaningful dev25 gates, predeclare the dev140
  score surface and stop rule before escalation.

Promotion gates for any non-GPT dev140 run:

- 0 call failures or explained recoverable failures.
- 0 parse/schema failures after allowed format-only repair.
- Exact evidence rate near `1.0000`, or a family-level explanation for drops.
- Clinical headline not merely above old v0.42 gates, but plausibly competitive
  with v09 partial hybrid.
- No hidden row-level holdout/full-200 inspection.

Parallel status: runs continue independently. Reporting streams B and C should
not wait.

## Stream E - Paper-Facing Architecture Selection Memo

Goal: choose the small set of architectures worth writing about.

Proposed file:

`docs/research/final_architecture_selection_2026-06-22.md`

Recommended architecture set:

- Gan 2026 canonical reliability subject: single GPT structured-event pass on
  GPT-4.1-mini v0_reference, with hybrid comparators clearly tagged.
- ExECTv2 v08 holistic finding assembly: best GPT-4.1-mini dev140 control.
- ExECTv2 v09 partial hybrid: clean simplified architecture above `0.900`.
- ExECTv2 DeepSeek v0.9.7: diagnostic cross-model comparator.
- ExECTv2 Qwen best completed run: local-model operational comparator.

Questions to answer:

- Which architecture is the performance control?
- Which architecture is the simplicity control?
- Which architecture is the model-portability evidence?
- Which components are prediction-bearing and must be ablated or described?
- Which deterministic layers are benchmark-format only?

Acceptance criteria:

- No more than 5 selected architectures.
- Every selected architecture has a claim boundary.
- Rejected or superseded architectures are summarized, not carried forward.

Parallel status: can start immediately. Qwen/DeepSeek rows can be refreshed.

## Stream F - Repo Simplification Plan

Goal: prepare aggressive cleanup without damaging evidence.

Proposed file:

`docs/plans/repo_simplification_plan_2026-06-22.md`

Cleanup categories:

- Keep as source:
  - `src/clinical_extraction/core`
  - ExECTv2 assembly, deterministic dictionary/lenses, reports, and runners
  - Gan canonical reliability and selected-event machinery
  - shared epilepsy utilities
- Keep as canonical evidence:
  - final artifact index entries
  - selected configs
  - selected JSON/JSONL/MD experiment outputs
  - final scorecards and cross-model reports
- Archive:
  - superseded Qwen prompt iterations
  - superseded ExECTv2 diagnostic lanes
  - old Gan exploratory runs not referenced by final scorecards
  - one-off build scripts whose outputs are now canonical
- Delete only after index and archive:
  - caches
  - local logs
  - redundant checkpoints
  - abandoned temporary outputs

Refactor targets:

- Consolidate report builders that parse assembly JSON into cross-model tables.
- Move reusable reliability metrics into a shared module instead of one-off
  experiment scripts.
- Expose a small CLI set:
  - run ExECTv2 key-family extraction
  - run ExECTv2 finding assembly
  - build ExECTv2 cross-model report
  - build reliability scorecard
  - run Gan canonical reliability report
- Collapse tests into three layers:
  - fast unit tests for schemas, dictionaries, lenses, scoring
  - artifact replay tests for canonical configs
  - governance tests for split/holdout guards

Acceptance criteria:

- Fresh clone can reproduce final reports from canonical artifacts.
- Experiment clutter no longer defines the repo's public shape.
- The final code path is easy to explain in the paper methods section.

Parallel status: planning can start immediately. Destructive cleanup waits until
Streams A, B, and C are complete.

## Stream G - Status And Governance Updates

Goal: keep the next working session safe and obvious.

Tasks:

- Update `PROJECT_STATUS.md` after the first evidence index and cross-model
  report are created.
- Move Qwen/DeepSeek from active run status to one of:
  - promoted
  - diagnostic comparator
  - rejected branch
  - blocked by runtime
- Record any predeclared dev140 or full-200 escalation.
- Preserve guardrails:
  - no Gan test row-level inspection
  - no ExECTv2 holdout/full-200 row-level inspection without frozen protocol
  - no benchmark/full-200 claim from dev140/dev25 evidence

Parallel status: wait until at least Stream B draft exists, then update.

## Stream H - Frontend ExECTv2 And Reliability App

Goal: extend `frontend/` so the app can inspect ExECTv2 letters and results, not
only Gan seizure-frequency runs, and so the selected winning architectures are
available in the review UI. This is Phase 0 parallel work and should not wait
for active Qwen/DeepSeek runs to finish.

Current app constraints:

- `frontend/components/observatory/useObservatoryData.ts` computes Gan-style
  Purist/Pragmatic category summaries and fixed seizure-frequency confusion
  categories.
- `frontend/lib/types.ts` has task-neutral pieces, but the run summary and
  gallery assumptions still center on Gan labels.
- `frontend/lib/api.ts` falls back to static `public/mock-data` artifacts, so a
  first ExECTv2 frontend slice can be built with generated static artifacts
  before any backend endpoint work.
- ExECTv2 assembly JSONL rows already carry `letter_id`, `gold_mentions`,
  predicted mentions by entity, evidence text, component ownership, provenance,
  source lane, source model, and score views. This is enough for a useful app
  viewer if adapted into frontend-friendly records.

### H0 - Data Contract And Registry Extension

Tasks:

- Add a task discriminator to frontend registry records, for example
  `task: "gan2026" | "exectv2"`.
- Add ExECTv2-specific frontend types:
  - `Exectv2LetterRecord`
  - `Exectv2Mention`
  - `Exectv2AssemblyRow`
  - `Exectv2FamilyMetrics`
  - `Exectv2RunSummary`
  - `ReliabilityScorecardDimension`
- Add a small adapter that reads ExECTv2 assembly JSON/JSONL and emits:
  - one run summary;
  - one per-letter record per `letter_id`;
  - one mention table grouped by entity;
  - evidence spans derived from exact evidence text when character offsets are
    unavailable.
- Generate static frontend mock data for canonical ExECTv2 artifacts:
  - v08 dev140 control;
  - v09 partial hybrid simplification;
  - DeepSeek v0.9.7 dev25 diagnostic;
  - Qwen best completed run or active placeholder.

Acceptance criteria:

- The frontend registry can list both Gan and ExECTv2 runs without coercing
  ExECTv2 into Gan categories.
- ExECTv2 task rows have enough data to render a letter, gold mentions,
  predicted mentions, evidence, component ownership, and per-family scores.
- The static mock-data path works before any API/backend change.

### H1 - ExECTv2 Letter And Result Explorer

Tasks:

- Add a task-aware route or mode, such as `/exectv2`, `/observatory?task=exectv2`,
  or a task switch inside the current observatory.
- Reuse the existing letter renderer, but adapt the metadata:
  - `letter_id` rather than Gan `source_row_index`;
  - split/stage such as `dev140` or `dev25`;
  - selected architecture/run;
  - exact evidence status.
- Render four entity groups:
  - Diagnosis;
  - SeizureFrequency;
  - Prescription;
  - Investigations.
- For each group, show:
  - gold mentions;
  - predicted mentions;
  - evidence quote;
  - CUI/CUIPhrase and important attributes;
  - component owner and source lane;
  - match/error status when available.
- Add run switching for the winning architectures so the same letter can be
  compared across v08, v09, DeepSeek, and Qwen where row coverage overlaps.

Acceptance criteria:

- A user can open an ExECTv2 letter and inspect the final v08 predictions
  against gold.
- A user can switch to v09 partial hybrid and see what changed.
- A user can inspect DeepSeek/Qwen diagnostic runs without mixing their dev25
  row coverage with dev140 controls.
- Evidence highlights do not depend on brittle unavailable offsets; exact text
  matching is acceptable for Phase 0.

### H2 - Winning Architecture Availability

Tasks:

- Add the final selected architecture set to the frontend registry:
  - Gan canonical reliability subject;
  - ExECTv2 v08 control;
  - ExECTv2 v09 partial hybrid;
  - ExECTv2 DeepSeek diagnostic;
  - ExECTv2 Qwen best completed diagnostic.
- Add architecture metadata:
  - model;
  - pipeline family;
  - split and row count;
  - claim boundary;
  - promotion decision;
  - scorer/view;
  - artifact paths.
- Ensure the app labels diagnostic non-GPT runs as diagnostic, not promoted
  replacements.
- Add one "final set" filter or quick-select preset.

Acceptance criteria:

- The app can load the same selected architecture set named in the final
  artifact index and architecture selection memo.
- A reviewer can move from cross-model report to app inspection without hunting
  through `experiments/`.
- Active or incomplete Qwen runs are visibly marked as pending/diagnostic.

### H3 - Reliability Scorecard View

Goal: stretch, but valuable if Phase 0 time allows.

Tasks:

- Create a frontend scorecard surface fed by
  `docs/experiments/exectv2/reliability/exectv2_cross_model_reliability_scorecard_2026-06-22.md`
  or a generated JSON companion.
- Show the ten reliability dimensions:
  task correctness, factuality, faithfulness, calibration, abstention/review,
  robustness, consistency, safety, family parity, operational reliability.
- Use compact cards or rows with:
  - coverage score;
  - current evidence;
  - gap to close;
  - linked artifact/run;
  - model/family filters.
- Add visual emphasis for:
  - faithfulness/exact evidence;
  - weak dimensions such as calibration or abstention;
  - family residual risks for Diagnosis, SeizureFrequency, Prescription, and
    Investigations.

Design direction:

- Prefer a dense, research-workbench feel over a marketing dashboard.
- Use restrained color to distinguish evidence strength, risk, and diagnostic
  status.
- Avoid decorative hero treatment; this is an instrument panel for deciding
  what evidence can be trusted.

Acceptance criteria:

- The scorecard is useful even if it only starts from static JSON.
- It makes weak evidence dimensions obvious rather than hiding them.
- It is visually polished enough to use in a meeting or screenshot, but does not
  replace the source Markdown/JSON artifacts as the canonical record.

Parallel status: H0 and H1 can start immediately. H2 can start with v08/v09 and
DeepSeek dev25, then refresh Qwen. H3 can start from the existing ExECTv2
scorecard and be refreshed after Stream C.

## Detailed Execution Sequence

### Phase 0 - Today, While Qwen/DeepSeek Runs Continue

Can be done immediately:

- Draft Stream B cross-model report using v08, v09, DeepSeek dev25, and Qwen
  best available checkpoint/reparse.
- Draft Stream C reliability scorecard skeleton and fill stable dimensions.
- Create Stream A artifact index with placeholders for active Qwen outputs.
- Draft Stream E architecture selection memo.
- Draft Stream F repo simplification plan without deleting anything.
- Begin Stream H frontend work:
  - define task-aware frontend data contracts;
  - generate static ExECTv2 app data from v08/v09/DeepSeek artifacts;
  - add or design the ExECTv2 letter/result explorer path.
- Add a small "pending refresh" section to each report so final Qwen/DeepSeek
  numbers can be swapped in.

Do not wait for:

- Qwen dev25 completion.
- DeepSeek dev140 escalation.
- New model calls.
- Full artifact hashing.

### Phase 1 - Same Day After Active Runs Finish

Finish:

- Score any completed Qwen run through finding assembly.
- Generate real-scorer error ledger for Qwen.
- Refresh Stream B table.
- Refresh Stream C model rows and operational reliability numbers.
- Refresh frontend ExECTv2 mock data and registry rows with completed Qwen
  results.
- Decide whether DeepSeek or Qwen justifies dev140 escalation.
- If no escalation is justified, stop model iteration and move to writing.

Completion note, 2026-06-22:

- Qwen v0.9.22 dev140 was scored through finding assembly as
  `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140`.
- The Qwen real-scorer error ledger was generated at
  `experiments/exectv2_v0922_qwencompact_residualrepair_dev140_error_ledger_20260622.md`.
- Stream B and Stream C now use completed DeepSeek v0.9.16 and Qwen v0.9.22
  dev140 rows rather than pending dev25 placeholders.
- Frontend static registry, ExECTv2 run summary, and artifact mock data include
  v08, v09 partial hybrid, DeepSeek v0.9.16, and Qwen v0.9.22.
- Neither DeepSeek nor Qwen justifies promotion beyond diagnostic comparator
  status; no additional dev140/full-200 escalation is predeclared.

### Phase 2 - Next Working Day

Finish:

- Artifact hashes for canonical files.
- Final artifact index.
- Project status update.
- Architecture selection memo.
- Repo simplification plan.
- Frontend ExECTv2 MVP: v08/v09/DeepSeek/Qwen selected runs in the app, with at
  least one letter-level inspection view.
- First cleanup PR or branch that only archives/quarantines non-canonical
  outputs and removes caches/logs.

Completion note, 2026-06-24:

- Canonical hashes are present in
  `docs/experiments/final_artifact_index_2026-06-22.md`.
- The final artifact index, cross-model report, reliability scorecard,
  architecture selection memo, repo simplification plan, and `PROJECT_STATUS.md`
  are current with the completed DeepSeek/Qwen dev140 diagnostic disposition and
  later Satellite 13 plateau addendum.
- The frontend ExECTv2 MVP is available through the task-aware workbench:
  `/exectv2` redirects to `/workbench?dataset=exectv2`, with v08, v09,
  DeepSeek, and Qwen selected architectures loaded from static mock data and a
  letter-level gold/predicted/evidence inspector.
- A cleanup branch was opened as `codex/final-consolidation-phase2`. Existing
  superseded ExECTv2 rich-schema artifacts are quarantined under
  `experiments/_archive/exectv2_richschema_iterations/`, now documented by
  `experiments/_archive/README.md`. No additional canonical evidence was moved
  or deleted in this phase.

### Phase 3 - Later This Week

Finish:

- Shared report builder and reusable reliability metric code.
- Frontend reliability scorecard view.
- Test suite compression and canonical replay tests.
- Documentation cleanup.
- Optional dev140 non-GPT run if predeclared and justified.
- Optional ExECTv2 full-200 aggregate protocol, but only after the scorecard
  and controls are frozen.

Completion note, 2026-06-24:

- Added the Phase 3 shared final-consolidation builder at
  `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/reports/final_consolidation.py`.
  It parses the canonical cross-model closeout and reliability scorecard
  Markdown into structured comparison rows, ten-dimension scorecard data,
  residual risks, upgrade metrics, and weak-dimension summaries.
- Added the static generator
  `scripts/build_exectv2_reliability_scorecard_data.py`, the committed frontend
  fallback `frontend/public/mock-data/exectv2/reliability-scorecard.json`, and
  the live Observatory endpoint `/exectv2/reliability-scorecard`.
- Added the ExECTv2 reliability scorecard frontend surface on the task-aware
  Laboratory/Component Impact route. The view shows the final evidence set,
  coverage filters, weak dimensions, residual family risks, upgrade metrics,
  and source-report paths while linking back to aggregate runs and letter
  inspection.
- Added canonical replay/governance coverage in
  `tests/test_exectv2_final_consolidation.py`, including parser contract,
  static fallback parity, and API serving checks.
- No optional non-GPT dev140 rerun or full-200/holdout protocol was started;
  existing guardrails remain unchanged.

### Phase 4 - Component Ablation Story

Finish:

- Move Reliability Scorecard to its own cross-dataset app surface/tab, separate
  from Component Impact.
- Make Gan Component Impact read as an ablation surface first:
  - compare baseline vs one-component-off results;
  - show headline deltas before rule inventory detail;
  - prioritize meaningful component families over individual rule toggles.
- Define ExECTv2 component ablation infrastructure:
  - fixed component boundaries for LLM producers, dictionaries, semantic lenses,
    evidence validation, assembly/arbitration, and deterministic projection;
  - replay-only one-component-off assembly configs for v08 and v09 controls;
  - no-call score deltas by overall and family;
  - provenance tags that separate format-only projection from prediction-bearing
    semantic add/drop/replace;
  - frontend payload contract for Component Impact.
- Populate ExECTv2 Component Impact with ablation artifacts only after the replay
  surfaces exist; until then, show provenance inventory plus an explicit phase
  gap instead of implying causal impact.

Acceptance criteria:

- Reliability Scorecard exists as its own tab and works for both Gan 2026 and
  ExECTv2.
- Gan Component Impact answers "what changed when this component was removed?"
  without requiring rule-by-rule inspection first.
- ExECTv2 Component Impact no longer presents reliability evidence as component
  impact, and the missing ablation contract is documented as the next phase.
- No full-200 or holdout-facing row inspection is introduced while building
  replay ablations.

Completion note, 2026-06-24:

- Reliability Scorecard is a standalone cross-dataset surface at
  `/reliability-scorecard`, with Gan and ExECTv2 payloads served through static
  fallback and Observatory API routes.
- Gan Component Impact now runs baseline versus one-component-off rules-only
  ablations and leads with F1/accuracy deltas before component detail.
- ExECTv2 Component Impact is wired to replayable aggregate layer artifacts for
  v08, v09, DeepSeek, and Qwen; it no longer presents reliability evidence as
  component impact.
- The ExECTv2 replay-ablation contract is documented in
  `docs/design/exectv2_component_ablation_contract_2026-06-24.md`, including
  fixed component boundaries, dev140 replay scope, aggregate payload fields,
  deterministic projection separation, and no full-200 or holdout-facing
  row-level inspection.

Replay artifact note, 2026-06-24:

- Generated the ExECTv2 layered component-impact replay artifacts:
  `experiments/exectv2_component_ablation_replay_dev140_20260624.json`,
  `.jsonl`, `.md`, static frontend payload
  `frontend/public/mock-data/exectv2/component-ablation.json`, and 28 layer
  YAML configs under `configs/exectv2/ablations/`.
- The replay covers four architectures: v08 dev140 control, v09 partial-hybrid
  simplification, DeepSeek v0.9.16 dev140 diagnostic, and Qwen v0.9.22 dev140
  diagnostic.
- Each architecture is shown across seven ordered layers: raw lane candidates,
  source-scored mentions, evidence-valid mentions, dictionary normalized,
  residual semantic additions, final assembly, and headline projection.
- The most visible deltas are dictionary normalization, residual semantic
  additions, and headline projection. Final headline F1 is 0.9155 for v08,
  0.9061 for v09, 0.9174 for DeepSeek, and 0.9001 for Qwen.
- The redesigned Component Impact page now reads the aggregate payload and
  displays an architecture ladder, layer-impact matrix, and selected
  architecture details.
- The artifacts are aggregate-only, make no model calls, and introduce no
  full-200 or holdout-facing row-level inspection.

Gan comparison trim note, 2026-06-24:

- The Gan Component Impact comparison was reduced from five architectures to one
  best performer per family: `deterministic_canonical_pipeline` (0.91),
  `hybrid_structured_events` (0.89), and `llm_only_canonical_pipeline` (0.78).
- The reset-native hybrid (`hybrid`, 0.73) and the direct labeler
  (`llm_only_direct_labeler`, 0.75) were dropped as redundant — each the weaker
  sibling of the kept line on the same validation-750 basis. The two dropped
  architectures stay in the historical research record (three-way comparison,
  cross-model, closeoff) but no longer appear in the live comparison.
- `component_stage_ladder.py`, the regenerated replay artifacts, the frontend
  payload, the unit tests, and
  `docs/design/gan2026_component_ablation_contract_2026-06-24.md` were updated to
  the three-architecture set. No `test450`/holdout row-level inspection was
  introduced. The final artifact index lists only the Gan reliability package, so
  it carries no Gan component-impact architecture rows to trim.

## Parallel Work Matrix

| Work item | Can run while Qwen active? | Can run while DeepSeek active? | Needs final model numbers? | Notes |
| --- | --- | --- | --- | --- |
| Artifact index skeleton | yes | yes | no | Add active-run placeholders. |
| Cross-model report draft | yes | yes | partial | Use current DeepSeek dev25 and Qwen checkpoint; refresh later. |
| Reliability scorecard skeleton | yes | yes | partial | Stable v08/v09 dimensions can be completed now. |
| v08/v09 architecture narrative | yes | yes | no | Already stable. |
| Gan reliability summary reuse | yes | yes | no | Already complete. |
| DeepSeek dev25 interpretation | yes | complete if artifact present | no | Current dev25 artifact is available. |
| Qwen final disposition | no | yes | yes | Wait for active dev25 completion or timeout. |
| Repo simplification inventory | yes | yes | no | No deletion yet. |
| Hash canonical artifacts | yes | yes | partial | Hash stable artifacts now; hash Qwen later. |
| PROJECT_STATUS update | yes | yes | partial | Best after report draft exists. |
| Frontend ExECTv2 data contract | yes | yes | no | Use v08/v09/DeepSeek now; leave Qwen refresh slot. |
| Frontend ExECTv2 letter/results viewer | yes | yes | partial | Can start with v08/v09 and add Qwen later. |
| Frontend reliability scorecard | yes | yes | partial | Can start from existing v08 scorecard; refresh after Stream C. |
| Destructive cleanup | no | no | yes | Requires artifact index and final status. |

## Decision Gates

### Gate 1 - Stop Or Continue Qwen

Stop Qwen prompt iteration if:

- completed dev25 remains below DeepSeek or v09 by a large margin;
- Diagnosis or SeizureFrequency remains below `0.800`;
- runtime is CPU-bound or operationally fragile enough to undermine final use;
- improvements come from increasingly benchmark-specific prompt repairs.

Continue or escalate only if:

- dev25 is operationally clean;
- Diagnosis and SeizureFrequency recover materially;
- the model provides distinctive portability evidence worth dev140 spend;
- the next surface is predeclared.

### Gate 2 - DeepSeek Dev140 Escalation

Escalate DeepSeek only if the purpose is explicit:

- performance escalation: not currently justified unless a prompt/profile update
  improves Diagnosis and SF;
- cross-model evidence: may be justified if a dev140 non-GPT row is needed for a
  paper table despite under-target families;
- reliability evidence: may be justified if cross-model agreement or review
  routing needs a larger aligned surface.

### Gate 3 - ExECTv2 Full-200 Or Holdout

Do not run full-200 or holdout-facing analysis until:

- candidate and deterministic code are frozen;
- scorer/view is declared;
- aggregate-only readout is specified;
- row-level inspection boundary is explicit;
- no post-run tuning from row-level failures is allowed.

## Evidence Preservation Policy

Canonical files must be preserved in place until the final artifact index exists.
After that, they may be copied or moved only with updated paths and hashes.

Never delete or rename:

- v08 config/report/JSON/JSONL/error ledger;
- v09 partial hybrid config/report/JSON/JSONL;
- Gan master reliability scorecard and its source JSON/MD outputs;
- active Qwen/DeepSeek source JSONL, assembly JSON/JSONL, and error ledgers;
- split manifests;
- docs that define claim boundaries or guardrails.

Safe to archive after indexing:

- superseded prompt-profile smoke runs;
- interrupted checkpoints superseded by completed runs;
- diagnostic artifacts not referenced in a final report;
- local logs once operational summaries are captured.

## Final Deliverables

Required:

- `docs/experiments/final_artifact_index_2026-06-22.md`
- `docs/experiments/exectv2/key_entities/exectv2_cross_model_closeout_2026-06-22.md`
- `docs/experiments/exectv2/reliability/exectv2_cross_model_reliability_scorecard_2026-06-22.md`
- `docs/research/final_architecture_selection_2026-06-22.md`
- `docs/plans/repo_simplification_plan_2026-06-22.md`
- Frontend ExECTv2 MVP in `frontend/`: task-aware registry, ExECTv2 artifact
  adapter/mock data, selected architecture runs, and letter-level result viewer
- Updated `PROJECT_STATUS.md`

Optional but valuable:

- reusable cross-model report builder
- reusable ExECTv2 reliability metric driver
- canonical artifact hash manifest
- polished frontend reliability scorecard view
- cleanup branch that archives non-canonical experiments

## Immediate Next Step

Start with Stream B, the cross-model report, and Stream H0/H1 frontend data
contract work in parallel. Stream B is the coordination surface for the evidence
set:

- It can be built from current artifacts.
- It naturally exposes missing Qwen/DeepSeek refresh slots.
- It decides which artifacts need indexing.
- It gives the reliability scorecard its subject rows.
- It prevents repo cleanup from becoming archaeology.

Stream H can begin from stable v08/v09/DeepSeek artifacts without waiting for
Qwen. After the cross-model report draft exists, create the artifact index, then
fill the reliability scorecard. Cleanup planning can proceed in parallel, but
actual deletion or movement should wait until the index and status update are
complete.
