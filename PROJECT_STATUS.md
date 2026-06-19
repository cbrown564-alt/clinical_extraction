# Project Status

Last updated: 2026-06-19

## Active Objective

ExECTv2 Plan 11 now optimizes exactly four indicators:
`Diagnosis`, `SeizureFrequency`, `Prescription`, and `Investigations`.
Success requires core F1 `>0.900` for each on the predeclared development
headline using a hybrid pipeline: one LLM call per letter for candidate
generation/selection, then deterministic normalization and projection with
explicit attribution. Rapid iteration uses `gpt-4.1-mini`; the destination
model is local `ollama_chat/qwen3.6:35b` via Ollama with thinking disabled.
ADR 0031 clarifies that the Diagnosis target headline is the projected
`concept_only` clinical-fact score after deterministic normalization/projection,
not raw surface-form or assertion-weighted capture; repeated Diagnosis mentions
of the same projected fact count once per letter.

## Current Dev140 Readout

Five-family Plan 11 headline: deterministic_all9 `0.604`, hybrid_all_entities
`0.550`, llm_only_all_entities `0.422`.

The predeclared routed ladder ran on `pilot25 -> dev140` without model calls.
On the routed four-family surface, single-pass LLM is `0.4313`,
hybrid_all_entities is `0.5684`, and family-routed is `0.5592` CUI-free /
`0.5952` CUI-projected with exact evidence `1.0000`. This clears the dev gate
against the single-pass baseline but is labeled `llm_first_with_hybrid_sf_route`
because the SF route uses deterministic candidate/projection and
unknown-suppression layers.

A no-call focused Diagnosis replay now exists for dev only. It improves the
routed four-family CUI-free headline to `0.7081`, with Diagnosis `0.7127`, but
the current routed Diagnosis baseline remains weak at `0.2898`; treat the
focused lane as qualified architecture evidence, not solved Diagnosis or
full-200/test authorization.

ADR `0030-four-exact-indicators-drive-exectv2-plan11.md` freezes the current
target surface and says error analysis should exclude non-target ExECT families
unless a later ADR expands the scope.

The ADR 0030 target-only report is now generated at
`docs/experiments/exectv2/key_entities/exectv2_adr0030_target_indicator_report_20260619.md`.
Best current dev140 F1 by target: Diagnosis `0.7302` (deterministic all9),
SeizureFrequency `0.7277` (deterministic all9), Prescription `0.9072`
(deterministic all9, already above target), and Investigations `0.7475`
(single-pass LLM). The current focused routed assembly remains below target on
all four (`0.7127` / `0.6321` / `0.7472` / `0.7475`).

First compliant single-call target-only runner exists. On dev10,
`exectv2_target_indicators_single_call_v0.2` with `gpt-4.1-mini` reached
overall `0.6043`, with D `0.2857`, SF `0.5000`, P `0.9189`, I `0.8333`.
The v0.4 no-call reprojection of the saved v0.3 raw outputs applies the ADR
0031 Diagnosis scoring definition and uses the projected clinical-recovery
layer for the target readout: overall `0.6667`, with D `0.4242`, SF `0.5405`,
P `0.9143`, I `0.8333`. This proves the one-call architecture and
normalization/projection loop, but the corrected error view shows Diagnosis
and SF remain candidate-recall/selection problems, not just representation
problems.

The best target single-call development readout is now v0.21 live dev25 on
`gpt-4.1-mini`. It clears all four ADR 0030 indicators with the projected
headline definitions: overall `0.9317`, Diagnosis `0.9360`,
SeizureFrequency `0.9057`, Prescription `0.9367`, and Investigations `0.9500`.
This is a hybrid target pipeline: the single LLM call owns candidate generation
and selection, then deterministic normalization/projection repairs
scorer-facing clinical facts. Diagnosis is scored after projection with the
`concept_only` clinical-fact score, not raw span wording or assertion-weighted
capture. SeizureFrequency is scored after deterministic seizure-state
normalization/projection, following the Gan frequency pattern.

Supporting no-call projection artifacts show the development path. v0.19
reprojected v0.17 live raw cleared all four with overall `0.9556`; v0.21
reprojected v0.19 live raw cleared all four with overall `0.9474`, Diagnosis
`0.9224`, SeizureFrequency `0.9615`, Prescription `0.9744`, and
Investigations `0.9268`. Earlier v0.16/v0.17/v0.19 live runs were useful
residual probes but did not clear all four simultaneously.

Local `ollama_chat/qwen3.6:35b` is now reachable but not fully solved. The installed
model is digest `07d35212591fc27746f0a317c975a6d68754fb38e9053d82e25f06057af28522`,
`36.0B`, `Q4_K_M`. GPU loading on the 8 GB RTX 4070 Laptop GPU fails with CUDA
out-of-memory, so current local runs use `CLINICAL_EXTRACTION_OLLAMA_NUM_GPU=0`
and `CLINICAL_EXTRACTION_OLLAMA_NUM_CTX=16384` via the shared `ollama_chat`
builder. v0.21 live dev1 clears all four locally, and v0.22 no-call
reprojection of v0.21 local dev5 raw clears all four (overall `0.9855`), but a
fresh v0.22 local dev5 live rerun does not reproduce: overall `0.8550`, D
`0.7887`, SF `0.7500`, P `0.8889`, I `1.0000`. v0.23 reprojects that fresh
v0.22 raw output after the same kind of deterministic normalization/projection
used in the Gan frequency work: overall `0.9577`, Diagnosis `0.9524`,
SeizureFrequency `0.9333`, Prescription `0.9474`, and Investigations `1.0000`.
This proves the residuals were mostly scorer-facing representation/projection
issues over captured facts, but the local Qwen destination still needs a fresh
v0.23 live rerun before claiming the requested reproducible `>0.900` target.

## Recent Context

- Coordinated Plan 11 follow-ups are merged into this checkout: SF route
  ladder, SF v07/v08 residual diagnostics, focused Diagnosis predeclaration and
  no-call replay, Prescription/Investigations shared-pass preservation, CUI
  projection guardrails, family-routed preflight, and blocker/runbook tests.
- SF v0.8 hard-slice panel is built from v0.7 dev140 residuals only:
  `84` residual units over `82` records, with action counts `no_action=35`,
  `drop=21`, `repair_state=12`, `repair_benchmark_format=9`,
  `repair_ownership=4`, and `add=3`. This is diagnostic-only and does not
  authorize prediction-bearing SF changes.
- Prescription/Investigations remain on the shared broad pass in the
  family-routed architecture; preflight now checks the
  `shared_broad_pass_only` preservation note before dev-ladder runs.
- CUI projection now keeps ambiguous Diagnosis residuals and five
  EpilepsyCause residual variants diagnostic-only pending the dev-only
  EpilepsyCause boundary-control predeclaration.

## Active Priorities

1. Treat routed and focused-replay results as qualified dev architecture
   evidence, not benchmark-complete claims.
2. Treat v0.21 live dev25 as the current promoted target single-call dev
   candidate; next validation should test reproducibility beyond pilot25 before
   any broader benchmark claim.
3. Stabilize the local `ollama_chat/qwen3.6:35b` candidate-generation behavior;
   the runtime path works only with CPU/off-GPU options, but fresh dev5 remains
   below target.
4. Use the SF v0.8 hard-slice panel to make a predeclared gate decision before
   any prediction-bearing SF code.

## Work Board

### Now

- Rerun local Qwen dev5 live with v0.23 (`num_gpu=0`, `num_ctx=16384`, no DSPy
  cache) to test whether the projection-cleared v0.23 no-call result
  reproduces with fresh candidate generation.
- Review `experiments/exectv2_sf_v08_hard_slice_panel_dev140_20260618.md` and
  write the SF v0.8 gate decision: either no prediction-bearing change, or one
  predeclared bucket/action class that clears attribution, non-gold-feature, and
  stop-rule checks.

### Next

- If local Qwen residuals remain candidate-selection failures, adjust prompt
  examples/policy for Qwen and rerun the slow ladder one step at a time
  (`dev1 -> dev5 -> dev25`) with `num_gpu=0`, `num_ctx=16384`, and no DSPy
  cache.
- Decide whether to fold the promoted Diagnosis enumeration lane into the
  canonical family-routed runner (replacing the shared-pass Diagnosis lane),
  with an ownership-clean preflight note; or keep it as a guarded dev candidate
  alongside the focused reconciler route pending a precision/recall comparison.
- If SF v0.8 gate passes, predeclare the single dev-only implementation slice
  and acceptance readout before editing SF prediction code.
- If CUI projection resumes, run the EpilepsyCause boundary-control
  predeclaration before promoting any residual EpilepsyCause variant.
- Keep focused Diagnosis replay, P/I specialist artifacts, and CUI projection
  variants as guarded dev evidence unless fresh predeclared gates pass.

### Blocked

- Gan holdout-facing reruns, row-level test analysis, and post-test tuning need
  explicit authorization plus a frozen protocol.
- New ExECTv2 full-200 audits need benchmark-beating GPT-first dev evidence and
  a predeclared aggregate readout.

### Done Recently

- 2026-06-19: Added v0.23 deterministic target projection rules for local Qwen
  residuals: ellipsis evidence repair, protected Diagnosis syndrome projection,
  every-N-to-M seizure-frequency projection, frequency-phrase Diagnosis
  suppression, focal-onset cross-family projection, frequency-header
  absence-like SF projection, and unanchored generic seizure-free suppression.
  Focused tests/Ruff pass. No-call replay of fresh v0.22 local Qwen dev5 raw now
  clears all four ADR 0030 indicators: overall `0.9577`, D `0.9524`,
  SF `0.9333`, P `0.9474`, I `1.0000`.
- 2026-06-19: Added the one-call ADR 0030 target-indicator runner
  (`exectv2_target_indicators_single_call_v0.2`). Dev10 `gpt-4.1-mini` pilot:
  overall `0.6043`, D `0.2857`, SF `0.5000`, P `0.9189`, I `0.8333`.
  Deterministic format normalization improved range attributes, dose units, and
  day-to-week period projection.
- 2026-06-19: Added ADR 0031 and v0.4 target-core projection for Diagnosis.
  Diagnosis scoring now projects to one clinical fact per letter after stripping
  certainty prefixes/parenthetical cause context, protecting seizure-type
  compounds, and normalizing benchmark-equivalent phrases. No-call reprojection
  of the saved v0.3 dev10 raw outputs: overall `0.6667`, D `0.4242`, SF
  `0.5405`, P `0.9143`, I `0.8333`.
- 2026-06-19: Added v0.8/v0.9 target single-call optimizations: SF-owned
  seizure-type facts recover Diagnosis recall through the projected Diagnosis
  core vocabulary; non-epilepsy Diagnosis noise is gated; asymmetric same-drug
  prescription dosing is split; planned prescriptions/investigations without
  results are dropped; prompt examples now cover zero-since SF states and
  completed-vs-planned investigations. Best dev25 readout is v0.9 no-call
  reprojection of v0.8 raw: overall `0.7365`, D `0.5879`, SF `0.6552`, P
  `0.9474`, I `0.7179`.
- 2026-06-19: Added v0.10-v0.12 target projection/prompt improvements:
  Diagnosis typo/dash/core projection, SF unique projected-state scoring,
  unknown-like SF number cleanup, non-seizure SF anchor gating, and
  investigation headline scoring that separates modality/result from EEG type.
  v0.11 live dev25 clears P/I (`0.9351`/`0.9048`); v0.12 no-call reprojection
  of v0.11 raw is the best current target artifact: overall `0.8221`, D
  `0.7313`, SF `0.7170`, P `0.9351`, I `0.9048`.
- 2026-06-19: Added v0.13/v0.14 target refinements: narrow Diagnosis aliases
  for temporal-lobe-onset and complex-partial conjunctions plus residual-focused
  prompt examples for epilepsy category headers and no-frequency SF boundaries.
  v0.14 live dev25 is now best overall at `0.8349`; v0.13 no-call remains the
  best D/SF-pair diagnostic at D `0.7799`, SF `0.7170`.
- 2026-06-19: Clarified the executable Diagnosis target definition in ADR 0031
  and target reports: Diagnosis uses the projected `concept_only` clinical-fact
  score after deterministic normalization/projection. v0.15 live dev25 recorded
  the policy in artifacts but regressed overall to `0.8161`, so v0.14/v0.13
  remain the current bests.
- 2026-06-19: Added v0.16 deterministic projection families for the target
  single-call route: epilepsy-word Diagnosis gate repair, evidence-specific
  Diagnosis projection, remote-last-seizure SF projection, vague yearly-rate
  projection, cluster splitting, unsupported zero-state drops, and unsupported
  minor-episode drops. No-call reprojection of v0.13 raw dev25 now clears all
  four targets: overall `0.9173`, D `0.9077`, SF `0.9167`, P `0.9351`, I
  `0.9048`; fresh v0.16 live dev25 did not reproduce (overall `0.8882`, D
  `0.8618`, SF `0.7778`, P `0.9610`, I `0.9500`), so this is diagnostic rather
  than promoted.
- 2026-06-19: Added v0.17-v0.21 target projection refinements, explicitly
  mirroring the Gan frequency normalize/project discipline for both Diagnosis
  and SeizureFrequency. New deterministic families include case-only evidence
  repair, several-since-last-clinic state projection, generic yearly-rate
  anchor projection, implicit every-N-period active-rate projection, controlled
  drug-change state expansion, convulsive zero-state expansion, active
  seizure-rate to Diagnosis projection, and absence-like Diagnosis gating.
  Fresh v0.21 live dev25 clears all four exact indicators: overall `0.9317`,
  D `0.9360`, SF `0.9057`, P `0.9367`, I `0.9500`.
- 2026-06-19: Brought the local Qwen target route online through native
  Ollama chat. `qwen3.6:35b` is installed but GPU startup OOMs on the 8 GB
  laptop GPU; the shared LM builder now supports environment-driven
  `num_gpu=0` and `num_ctx=16384` options. Local v0.21 dev1 clears, v0.22
  replay of local dev5 raw clears, but fresh v0.22 local dev5 remains below
  target (overall `0.8550`; D/SF/P below `0.900`, I clear).
- 2026-06-19: Added the ADR 0030 target-only report and runner. Current dev140
  best-by-indicator is D `0.7302`, SF `0.7277`, P `0.9072`, I `0.7475`; only
  Prescription currently clears `>0.900`.
- 2026-06-19: Added ADR 0030 to lock the four exact ExECTv2 target indicators
  and the `>0.900` core-F1 hybrid-pipeline objective; narrowed error analysis to
  Diagnosis, SeizureFrequency, Prescription, and Investigations.
- 2026-06-19: Ran the predeclared Diagnosis enumeration recall pass (live
  `gpt-4.1-mini`, dev ladder). Clean `llm_first` Diagnosis lane lifts routed
  Diagnosis `0.2898 -> 0.6530` and four-family `0.5592 -> 0.6835`, P `0.4162 ->
  0.6584` / R `0.2222 -> 0.6477`, P/I/SF unchanged, evidence validity `0.9953`.
  All predeclared dev140 gates passed; route PROMOTED as dev architecture
  evidence. Still below `deterministic_all9` `0.7301`; Diagnosis not solved.
  Result: `exectv2_diagnosis_enumeration_recall_pass_result_2026-06-18.md`.
- 2026-06-18: Integrated five parallel guardrail threads: SF v0.8 hard-slice
  panel and tests, focused Diagnosis claim-language test, P/I shared-pass
  preflight gate, CUI diagnostic-only deny-list plus EpilepsyCause
  boundary-control predeclaration, and blocker/protocol test coverage.
- 2026-06-18: Merged coordinated Plan 11 workstreams and ran the predeclared
  family-routed comparison. Dev140 routed four-family F1 is `0.5592` CUI-free /
  `0.5952` CUI-projected, with SF `0.6321` and exact evidence `1.0000`.

## Guardrails

- Do not inspect Gan `test450` row-level failures, rationales, evidence,
  selected events, or transitions for development.
- Keep claims attribution-clean across `rules_only`, `llm_first`, and `hybrid`;
  deterministic certainty/CUI/format repairs are controlled projection layers.

## Core Artifacts

Start with the family-routed comparison, focused Diagnosis no-call replay, SF
v0.8 predeclaration and hard-slice panel, P/I shared-pass preservation note,
CUI projection diagnostics and EpilepsyCause boundary-control predeclaration,
Plan 11 readouts, key-family synthesis, and blocker runbook before opening new
experiments.
