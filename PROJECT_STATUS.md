# Project Status

Last updated: 2026-07-01

## Plain-language snapshot (5 bullets)

- **Two tasks:** Track 1 (Gan) extracts one label — seizure frequency — from
  synthetic letters; Track 2 (ExECT) extracts diagnosis, seizure frequency,
  prescriptions, and investigations from de-identified epilepsy letters.
- **Frozen vs active:** Gan `test450` holdout is frozen (aggregate citations only,
  no tuning); ExECTv2 holistic assembly v08 is the live production control on
  dev140 / full-200.
- **Primary scores:** Gan — **Purist** (strict matcher) on `test450`; ExECT —
  **`clinical_headline`** de-duplicated recovery (strict benchmark/CUI stays
  diagnostic).
- **Main negative findings:** Gan hit a **confident over-reading limit (The Wall)**
  — on ambiguous letters the model commits to a rate when it should abstain (~84%
  ceiling, not a tuning target). ExECT shows a **gold-quality / annotation-format
  ceiling** — many benchmark “errors” are label multiplicity or format fidelity,
  not missing clinical concepts.
- **Start here:** [collaborator onboarding (HTML)](docs/collaborator_onboarding.html)
  or [markdown](docs/collaborator_onboarding.md); term definitions in
  [plain-language glossary](docs/reference/plain_language_glossary.md).

## Active Objective

ExECTv2 is in a reliability/component-evidence phase after the Satellite 13
LLM-only plateau. `clinical_headline` de-duplicated clinical recovery is the
headline surface; strict benchmark/CUI results stay diagnostic. Paper-facing
language and results scaffolding live in `docs/research/`. Resume the
paper/results sprint from `docs/research/paper_manuscript_2026-06-26.md` and the
IEEE LaTeX draft in `literature/IEEE/IEEE-conference-template-062824/`
(markdown is ahead of the LaTeX draft as of 2026-06-30 — the LaTeX has not yet
been re-synced with the 2026-06-30 Diagnosis gold-quality revision below).

## Current Read

*Maintainer detail — dense evidence stack for people updating this board; new
collaborators should read the plain-language snapshot above first.*

Current evidence stack:

- ExECTv2 `clinical_headline` is primary. Full-200 GPT-4.1-mini v08 is `0.8502`;
  no-verifier `0.8431`; lean 2-call no-SF `0.8356` overall / `0.7525` SF.
- Same-core full-200 aggregate-only: GPT-4.1-mini `0.8356`; DeepSeek `0.8566`
  overall / `0.7602` SF with `1` accepted Diagnosis caveat; Qwen repair v02
  `0.8197` overall / `0.7020` SF with `0` call/parse failures, structured
  evidence `0.9950`, exact evidence `1.0000`.
- Reliability validation: calibration ECE `0.0432`, Brier `0.2245` vs `0.2387`;
  review routing failed (`0.9661` burden, `0.9037` catch); robustness hard-slice
  F1 `0.8336` across `414` cells; Investigations deterministic replacement is
  not ready (`0.9213` remains strongest with verifier + suppression).
- Component Impact: dev140 one-component-off readout has `16` replay-only rows;
  full200 aggregate-only replay has `9` rows across GPT-4.1-mini, DeepSeek, and
  Qwen repair v02. Full200 deltas are positive for dictionary (`+0.0186` to
  `+0.0290`), residual semantic lens (`+0.0098` to `+0.0117`), and headline
  projection (`+0.0302` to `+0.0350`); report:
  `experiments/exectv2_component_off_replay_full200_20260626.md`.
- Gan holdout evidence is frozen: v0.7 test450 `346/450` Purist, `365/450`
  Pragmatic; consensus/fresh constrained Gate 4 failed (`348/450`, precision
  `0.5909`), while exact-source Gate 4 passed only as frozen aggregate evidence
  (`359/450`, `+16`, precision `0.6000`).
- GEPA workstream closed out (06-28 to 06-30): single-pass GEPA plateaus
  ~0.73 (mini) / ~0.65 (Qwen) on dev140 `clinical_headline`, ~0.15-0.19 below
  the v08 hybrid (0.9155); root-caused to producer evidence-recall, not
  verify/arbitrate stages
  (`docs/research/exectv2_gepa_vs_hybrid_evidence_decomposition_2026-06-28.md`).
  Cross-model close-out: Qwen 3.6 35B underperforms mini on the identical
  architecture and does not clear its own hand-tuned baseline
  (`docs/research/exectv2_gepa_qwen_cross_model_2026-06-30.md`).
- SF "plateau" reframed as a gold-quality ceiling, not a model ceiling
  (SF Phases 1-7, closing in
  `docs/experiments/exectv2/seizure_frequency/exectv2_sf_canonical_metric_row_analysis_2026-06-29.md`):
  only 15/53 dev140 `state_profile` metric-errors are genuine model mistakes;
  counting only genuine errors the model is clinically defensible on 89.3% of
  letters vs the metric's 62.1%. The same row-adjudication method applied to
  Diagnosis on 2026-06-30 found the identical mechanism, more lopsided: of 209
  dev140 Diagnosis disagreements, 14.8% are genuine model error, 85.2% are gold
  multiplicity/consolidation artifacts (adjusted F1 0.6617 -> 0.9501); see
  `docs/experiments/exectv2/diagnosis/exectv2_dx_canonical_row_analysis_2026-06-30.md`
  and the manuscript revision notes in `docs/research/paper_drafts/`.

## Active Priorities

1. Treat `clinical_headline` recovery as primary; strict benchmark/CUI stays diagnostic.
2. Keep deterministic validation/projection separate from prediction-bearing facts.
3. Separate Reliability Scorecard from Component Impact by split, scorer, and inspection boundary.

## Work Board

### Now

- 2026-06-30: applying `docs/research/predecessor_lessons/` to the current
  evidence base (the packet's own absorption tables were stale relative to the
  GEPA/SF work done since 06-28). Five bounded items: (1) registry hygiene
  fixed — 247 artifact paths across 183 entries repaired, one pre-existing
  out-of-scope Gan entry left; (2) Diagnosis canonical row-adjudication (see
  Current Read above) — the highest-value finding, revises the manuscript's
  gap-mechanism claim; (3) evidence support-quality companion audit built
  (`experiments/exectv2_evidence_support_audit.py`), closing the FM1 guardrail
  that was "Partial"; (4) DeepSeek precision prompt profile probe (A5) — small,
  mechanistically clean positive (+0.0146 overall F1, precision +0.026/recall
  flat) on `docs/experiments/exectv2/reliability/exectv2_deepseek_precision_profile_probe_2026-06-30.md`;
  (5) this PROJECT_STATUS update + predecessor-lessons absorption table refresh
  + manuscript revision (in progress). The IEEE LaTeX draft has NOT yet been
  re-synced with the 2026-06-30 manuscript markdown changes — that is the next
  step before any camera-ready pass.
- Manuscript consistency pass (06-26) and the SF/Diagnosis gold-quality
  revisions (06-29, 06-30) are layered on the markdown source; the IEEE draft
  reflects only the 06-26 state. The remaining camera-ready-only items
  (author/affiliation block, acknowledgment, two-column last-page balance) are
  unaffected by the content revisions.

### Next

- **NEW 2026-07-01:** audited the whole project against the original
  supervisor brief (training-free multi-agent epilepsy-letter extraction;
  Section/Timeline + Field Extractor + Verification + Aggregator roles;
  single-prompt-vs-multi-agent reliability comparison at matched budget;
  dissertation deliverable). Research substance (evidence gates, structured
  validation, self-consistency, field-level F1, robustness, synthetic +
  de-identified data) is met or exceeded; architecture/vocabulary has
  drifted from the brief's literal framing (three-family rules/LLM-only/
  hybrid comparison instead of single-prompt-vs-multi-agent; no named
  Section/Timeline Agent; no dissertation document, only a paper-length
  manuscript). See
  `docs/research/supervisor_brief_conformance_audit_2026-07-01.md` for the
  full conformance table and
  `docs/plans/supervisor_brief_gap_closure_plan_2026-07-01.md` for the
  phased closure plan. Phase A (legibility crosswalk) DONE. Phase C
  (Section/Timeline Agent) DONE — built `exectv2/deterministic/
  section_timeline.py` and ran a dev140 ablation on SeizureFrequency +
  Investigations; **null result** (SeizureFrequency -0.0106, Investigations
  -0.0034, both within/near measurement noise), written up in
  `docs/experiments/exectv2/reliability/exectv2_section_timeline_ablation_2026-07-01.md`.
  Module kept in the codebase, not wired into production v08. Phase D
  (dissertation) confirmed out of scope — actual target is the existing
  5,000-word/8-page IEEE paper, user-owned. **Phase B DONE, revised scope**:
  the user challenged the original "cheap table" framing and it did not
  hold up — the only prior "multi-agent" artifact in this codebase
  (2026-06-12, Gan 2026) was found to hard-code tool calls and fake its
  multi-agent condition (four identical calls, cosmetic role labels).
  Rebuilt from scratch with genuine `dspy.ReAct` tool use and
  structurally-honest specialists (output schema cannot contain a final
  answer) on both tasks. **Gan 2026**
  (`docs/experiments/gan2026/agentic/gan2026_agentic_redo_results_2026-07-01.md`):
  every new architecture beat single-prompt on a hard panel (Purist
  38%→64%), dynamic orchestration beat static fan-out, neither cleared the
  strict promotion gate at n=50. **ExECTv2 SeizureFrequency**
  (`docs/experiments/exectv2/seizure_frequency/exectv2_sf_agentic_redo_results_2026-07-01.md`,
  first agentic infrastructure ever built for ExECTv2): the pattern did
  *not* transfer — single-prompt was the best performer, new architectures
  trended mildly negative (small-sample, inconclusive). Cross-task
  divergence is the honest answer to the brief's key research question —
  agentic decomposition is task-dependent, not a universal win. All four
  phases of the gap-closure plan are now complete.
- **DONE 2026-07-01:** fixed the `test60` split-construction gap. The source
  dataset paper (Fonferko-Shadrach et al. 2024, *J Biomed Semantics*, DOI
  10.1186/s13326-024-00316-z) discloses "Four letters were duplicated within
  the set to test for consistency in annotations" — a deliberate, documented
  design choice by the corpus's original authors (confirmed: 4 duplicate
  pairs / 8 of 200 letters, 4%, exactly matching that statement), NOT a
  corpus integrity bug. The genuine, locally-fixable issue was narrower:
  `exectv2_split_v1.json` stratifies only by `has_seizure_frequency_mention`,
  with no identity-awareness, so it did not know to keep the paper's known
  duplicate pairs on one side of the boundary — one pair, `EA0159` (test) /
  `EA0160` (dev), landed across the frozen dev/test split. Fix: cut
  `data/ExECTv2 (2025)/splits/exectv2_split_v2.json` (dev unchanged at 140;
  `EA0159` dropped from test, so **test59** going forward), `v1` left
  untouched as historical record. `data.py`'s `DEFAULT_SPLIT_MANIFEST` still
  points at `v1`; cut over the next time a fresh test-split run is planned.
  See `docs/experiments/exectv2/exectv2_test60_split_dedupe_fix_2026-07-01.md`
  for the full audit (including a refinement: 3 of the 4 duplicate pairs show
  substantially different `.ann` annotations — consistent with genuine
  independent re-annotation for the paper's consistency check — while only
  the EA0159/EA0160 pair is near-identical) and
  `docs/plans/exectv2_exploratory_directions_implementation_plan_2026-07-01.md`
  for the implementation plan this was Phase 0 of.
- **DONE 2026-07-01:** implemented the exploratory-review's Tier-1 items 1-4
  (`docs/plans/exectv2_exploratory_directions_implementation_plan_2026-07-01.md`
  Phases 1-2). Registry hygiene: retroactively registered 7 silently-missing
  GEPA runs (2 distinct root causes — a swallowed load-failure in
  `_register()`, and a standalone launcher family that never had a
  registration path — plus a pre-existing broken artifact-path row that was
  blocking registry validation entirely) — 244 -> 251 rows
  (`docs/research/exectv2_registry_survivorship_bias_2026-07-01.md`, which
  also corrected the item's own framing: mean chain-length-to-publication is
  only 1.12, but 40.7% of the manuscript's own citation graph has no
  registry row at all). Cost-quality table
  (`docs/research/exectv2_cost_quality_matched_split_table_2026-07-01.md`)
  confirmed the 1-2 call delta and the ~9x deterministic-stack claim, but
  found the informally-cited "hybrid +0.2 F1, ~5x split-dependent" figure
  conflates two non-commensurable comparisons (real +0.18-0.20 vs. GEPA at
  dev140-only, untestable for split-dependence; a much smaller +0.015/+0.076
  premium vs. a 2-call baseline that IS split-comparable but not robust to
  baseline-model choice). Mechanical gold-inflation heuristic
  (`docs/research/exectv2_gold_inflation_mechanical_heuristic_2026-07-01.md`)
  recovered Prescription's 7 typo cases cleanly (0 false positives) but does
  NOT generalize to SF/Diagnosis (stem-collision false positives) — a
  calibrated pre-flight rule, not a universal detector. **Verify-stage
  credit-assignment GEPA rerun**
  (`docs/research/exectv2_gepa_verify_stage_credit_assignment_2026-07-01.md`):
  froze S0 + added a stage-local accept/reject/add feedback metric
  (independent of the merged-output diff; selection score unchanged) for the
  multistage generate->verify program. Result: 0.7235 -> **0.7596** dev140
  `clinical_headline` (+0.036, precision-driven), evolved verify instructions
  turned decisively filter-shaped (vs. the prior run's reformatting drift) —
  the review's credit-assignment hypothesis is CONFIRMED qualitatively, but
  the run narrowly MISSES the pre-registered kill-criterion (needed >=
  0.761, got 0.7596, -0.0014). This nuances but does not overturn the
  06-28/06-30 GEPA close-out's "root-caused to producer evidence-recall, not
  verify/arbitrate stages" framing above — a well-credited verify stage
  clearly recovers real value within the single-model plateau, just not
  enough (on this run) to change which architecture family closes the gap
  to the v08 hybrid (0.9155).
- If the Gan consensus/fresh path is revisited for tuning or redesign, start
  from validation-only component-generation work; the holdout aggregate results
  may be cited only as frozen evaluation evidence, not used for row-level
  debugging or tuning.
- Preserve Gan consensus/fresh v0.9 constrained Gate 4 and exact-source Gate 4 as
  frozen aggregate evidence; do not tune gates, prompts, artifacts, rules,
  normalization, scorer, or model choice from them.
- Keep Investigations cost work deferred until a separate predeclaration.
- Build a test-safe UMLS-backed concept normalizer to replace the in-sample
  gold-derived stub in `deterministic/concept_normalizer.py` (acquire a real
  UMLS/MRCONSO resource for the `UmlsConceptNormalizer` placeholder).
  Deprioritized: the 2026-06-28 single-model plateau synthesis
  (`docs/research/exectv2_gepa_single_model_plateau_synthesis_2026-06-28.md`)
  found CUI is not the lever for this benchmark's surface-granularity convention.

### Blocked

- Gan holdout-facing reruns, test row analysis, and post-test tuning remain blocked
  unless separately authorized under a fresh frozen protocol.
- ExECTv2 full-200/holdout row-level inspection remains blocked; current protocols
  authorize aggregate validation outputs only.
- Lower-burden review-routing promotion is blocked by failed aggregate
  validation; any retry needs dev140-only redesign and a fresh predeclaration.

### Done Recently

- 2026-07-01: Documentation consolidation Path A — added `docs/NAVIGATION.md`,
  `docs/runbooks/documentation_lifecycle.md`, CI doc-hygiene gate; relocated
  evidence-recall case files from root `_sf_ev_recall/` and `_rx_inv_ev_recall/`
  to `docs/research/error_analysis/`; renumbered ADR 0005 JSON-dialect collision
  to `0038`; archived June "Done Recently" entries to
  `docs/research/maintenance/project_status_digest_2026-06.md`.
- 2026-06-30: Applied `docs/research/predecessor_lessons/` to the current evidence
  base. Registry hygiene (247 artifact paths repaired); Diagnosis canonical
  row-adjudication (the GEPA plateau synthesis's self-reopened question,
  answered — 85.2% of Diagnosis disagreements are gold-quality artifacts, not
  genuine model error, mirroring and exceeding the SF finding); evidence
  support-quality companion audit (closes FM1's "Partial" guardrail); DeepSeek
  precision prompt profile probe (A5, small mechanistically-clean positive);
  manuscript revised (§4.1.2, D.2, §6) to give Diagnosis the same
  gold-quality-ceiling treatment SF got on 06-29; predecessor-lessons
  absorption tables refreshed.
- 2026-06-30: ExECTv2 GEPA Qwen 3.6 35B cross-model close-out (bounded
  negative) + registry registration fix (12 malformed records flattened).
- 2026-06-29: ExECTv2 SF Phases 5-7 — feedback+demos LLM-only SF best (0.784,
  gate not cleared); changed-class row adjudication revises Phase 4's "not
  learnable" call; canonical whole-corpus metric row-analysis concludes the SF
  "wall" is a gold-quality ceiling, not a model ceiling (only 15/53 dev140
  metric-errors are genuine model mistakes).
- Earlier June entries: see
  `docs/research/maintenance/project_status_digest_2026-06.md`.

## Guardrails

- Do not describe de-duplicated `clinical_headline` recovery as a strict
  benchmark win or compare it directly to the paper's strict target.
- Do not inspect Gan `test450` row-level failures, rationales, evidence,
  selected events, or transitions for development.
- Do not inspect ExECTv2 holdout/full-200 row-level failures for development;
  the current reliability-audit protocol authorizes aggregate validation only.
- Keep deterministic projection, hybrid rescue, and verifier rejection
  provenance-stamped and separated in reported score lines.
