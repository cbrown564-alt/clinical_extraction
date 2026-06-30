# Project Status

Last updated: 2026-06-30

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
- 2026-06-26: IEEE manuscript final consistency pass — verified every reported
  number, family score, and claim-boundary phrase end-to-end against the Appendix
  Table I source artifacts (Gan `test450` phase-4 audit; consensus/fresh Gate 4
  constrained `348/450 +19 0.5909` failed and exact `359/450 +16 0.6000` passed;
  ExECTv2 v08 full-200 `0.8502`; lean frontier `0.8356`/`0.7525`/`400` calls;
  calibration ECE `0.0432`/Brier `0.2245`/`0.2387`; robustness `0.8336` hard-slice
  across `414` cells vs `0.8503`; dev140 and full-200 component-off ranges;
  same-core model swap). All numbers matched. Two consistency fixes applied:
  aligned the Results task descriptor to "broad multi-entity phenotyping" (the lone
  "nine-entity" outlier against the abstract/intro "multi-entity" usage and the
  Methods/table four-family enumeration), and restored the "(of rendered)"
  qualifier on the Gan Purist/Pragmatic table headers so the table's `364/448`
  (`0.812`) reconciles with the prose's `364/450` (`0.809`). Recompiled cleanly
  (`5` pages, no undefined refs or warnings).
- 2026-06-26: IEEE manuscript prose compression — tightened Introduction, Related
  Work, Methods (inspection-boundary paragraph folded), and Discussion prose
  without changing any number, table, or claim boundary; recompiled cleanly
  (5 pages, no undefined refs).
- 2026-06-26: IEEE manuscript provenance pass — added Appendix Table I linking
  result families to source artifacts and claim boundaries, added a Methods
  pointer, and recompiled
  `literature/IEEE/IEEE-conference-template-062824/IEEE-conference-template-062824.pdf`.
- 2026-06-26: Repo cleanup closed — pass 1 archived `438` superseded notes; pass 2
  archived `1012` registry-filtered/unregistered iteration notes (`104` root
  `.md` remain active). Indexes: `experiments/README.md`,
  `experiments/archive/ARCHIVE_INDEX.md`, `docs/REGENERATION.md`,
  `docs/experiments/FROZEN_EVIDENCE_MANIFEST_2026-06-26.md`.
- 2026-06-26: Paper scaffold and Section 4 integration — IEEE TikZ figure,
  methods/results tables, appendix move, and manuscript Section 4 folded into
  LaTeX with compiled PDF.
- 2026-06-26: ExECTv2 component-off full200 replay (`9` rows; positive dictionary,
  semantic lens, headline projection deltas) and Qwen repair v02 same-core
  evidence (`0.8197` full-200; `0` call/parse failures).
- 2026-06-26: Gan consensus/fresh v0.9 gates and exact aggregate-only Gate 4
  pass; holdout results remain frozen.
- 2026-06-25 to 2026-06-26: Same-core full-200 model-swap evidence, reliability
  validations, MLflow/registry indexing.

## Guardrails

- Do not describe de-duplicated `clinical_headline` recovery as a strict
  benchmark win or compare it directly to the paper's strict target.
- Do not inspect Gan `test450` row-level failures, rationales, evidence,
  selected events, or transitions for development.
- Do not inspect ExECTv2 holdout/full-200 row-level failures for development;
  the current reliability-audit protocol authorizes aggregate validation only.
- Keep deterministic projection, hybrid rescue, and verifier rejection
  provenance-stamped and separated in reported score lines.
