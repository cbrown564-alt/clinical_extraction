# Project Status

Last updated: 2026-06-26

## Active Objective

ExECTv2 is in a reliability/component-evidence phase after the Satellite 13
LLM-only plateau. `clinical_headline` de-duplicated clinical recovery is the
headline surface; strict benchmark/CUI results stay diagnostic. Paper-facing
language and results scaffolding live in `docs/research/`. Resume the
paper/results sprint from `docs/research/paper_manuscript_2026-06-26.md` and the
IEEE LaTeX draft in `literature/IEEE/IEEE-conference-template-062824/`.

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

## Active Priorities

1. Treat `clinical_headline` recovery as primary; strict benchmark/CUI stays diagnostic.
2. Keep deterministic validation/projection separate from prediction-bearing facts.
3. Separate Reliability Scorecard from Component Impact by split, scorer, and inspection boundary.

## Work Board

### Now

- Final manuscript consistency pass on the IEEE draft: read end-to-end and
  confirm every reported number, family score, and claim-boundary phrase matches
  the provenance-anchored source artifacts (Appendix Table I) and stays
  consistent across abstract, results, and discussion.

### Next

- If the Gan consensus/fresh path is revisited for tuning or redesign, start
  from validation-only component-generation work; the holdout aggregate results
  may be cited only as frozen evaluation evidence, not used for row-level
  debugging or tuning.
- Preserve Gan consensus/fresh v0.9 constrained Gate 4 and exact-source Gate 4 as
  frozen aggregate evidence; do not tune gates, prompts, artifacts, rules,
  normalization, scorer, or model choice from them.
- Keep Investigations cost work deferred until a separate predeclaration.

### Blocked

- Gan holdout-facing reruns, test row analysis, and post-test tuning remain blocked
  unless separately authorized under a fresh frozen protocol.
- ExECTv2 full-200/holdout row-level inspection remains blocked; current protocols
  authorize aggregate validation outputs only.
- Lower-burden review-routing promotion is blocked by failed aggregate
  validation; any retry needs dev140-only redesign and a fresh predeclaration.

### Done Recently

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
