# Project Status

Last updated: 2026-06-23

## Active Objective

Final project consolidation Phase 1 is complete. The Qwen repair-attribution
objective is reopened under the tightened generation-and-selection protocol:
candidate-backed Qwen default-keep adjudication is now classified as a hybrid
selector diagnostic, not an LLM-attributed extraction pass, because Qwen did not
generate the scored target facts.

## Current Read

ExECTv2 v08 remains the dev140 GPT performance control: overall `0.9155`,
Diagnosis `0.9090`, SeizureFrequency `0.9053`, Prescription `0.9357`,
Investigations `0.9132`. ExECTv2 v09 partial hybrid is the simplification
control at overall `0.9061`, not the performance control.

Final non-GPT diagnostics are complete and remain `do-not-promote`. DeepSeek
v0.9.16 dev140 refreshed replay: overall `0.9174`, Dx `0.8898`, SF `0.9017`,
Rx `0.9415`, Inv `0.9658`, raw-lane F1 `0.7498`, exact evidence `1.0000`.
Qwen v0.9.22 dev140: overall `0.9001`, Dx
`0.8563`, SF `0.8908`, Rx `0.9343`, Inv `0.9579`, exact evidence `1.0000`,
raw-lane F1 `0.6406`, with ten visible parse/schema failures on each family
lens surface. Neither justifies further dev140 or full-200 escalation without a
predeclared protocol.

Qwen repair-attribution rerun results are now recorded in
`docs/experiments/exectv2/key_entities/qwen_protocol_clean_attribution_2026-06-23.md`.
The direct compact dev25 diagnostic cleared the earlier dictionary-normalized
proxy (`0.9055`) but did not establish the final corrected protocol surface;
the declared compact dev140 run failed:
`raw_model` `0.6975`, `schema_format` `0.6975`,
`model_preserving_canonical` `0.7821`, and `hybrid_full_stack` `0.8483`.
The richer `full` prompt profile failed operationally on dev25 due repeated
truncation at `max_tokens=5000`. A candidate-backed Qwen strict-action
iteration passed dev25 on the older non-rescue surface but missed dev140
(`0.8977`; raw/schema `0.8977`, hybrid `0.9020`). A default-keep
action-contract replay over the same Qwen responses reached dev140
raw/schema/clean `0.9155` and hybrid `0.9091` on the older surface, but the
tightened protocol now treats it as candidate-backed hybrid adjudication rather
than a Qwen model-quality pass. The remaining qualifying Qwen objective is a
generation-and-selection route where Qwen emits the scored facts and then
selects among its own model-generated facts.

The predeclared protocol now exists:
`docs/design/llm_repair_attribution_protocol_2026-06-22.md`. It separates
allowed model-preserving repair from disallowed prediction-bearing rescue
repair and now also requires model-origin generation of the scored facts. The
Qwen target is no longer a residual-repair or selector-only headline score; it
is `>0.900` F1 on a protocol-clean `model_preserving_canonical` surface where
Qwen both generates and selects the prediction-bearing facts, while rescued or
candidate-copied facts remain visible as hybrid behavior.

Phase 1 closeout artifacts, frontend static review data, and the clinical-
utility companion audit are current. Dataset-aware frontend integration remains
tracked in
`docs/plans/exectv2_frontend_dataset_integration_implementation_plan_2026-06-22.md`.

## Active Priorities

1. Treat v08 as the performance control and v09 partial hybrid as the
   simplification control.
2. Treat DeepSeek/Qwen dev140 as diagnostic portability evidence; the direct
   Qwen compact and strict-action ablations failed, while candidate-backed
   default-keep Qwen adjudication is now hybrid selector evidence only.
3. Keep deterministic semantic lenses and dictionary repairs visible as
   prediction-bearing when they change clinical facts or attributes.
4. Do not count rescue-added facts toward Qwen model-quality F1; fix those
   misses in model output, prompt/schema, or model settings.
5. Do not run ExECTv2 full-200 or holdout-facing row-level analysis without a
   frozen aggregate/readout protocol.
6. Continue ExECTv2 frontend dataset integration and defer destructive cleanup
   until the final index/report set is accepted.

## Work Board

### Now

- Decide whether direct free-form Qwen extraction still needs a separate
  escalation path under the generation-and-selection protocol.
- Keep using the four required Qwen score surfaces: `raw_model`,
  `schema_format`, `model_preserving_canonical`, and `hybrid_full_stack`, with
  explicit fact-origin accounting for model-generated versus candidate-copied
  facts.
- Continue the dataset-integration frontend plan: shared dataset descriptors,
  sticky dataset selection, dataset-indexed static data, and a workbench
  `SpecimenRef` path for Gan rows and ExECTv2 letters.

### Next

- Add tests or replay checks that disallowed rescue actions do not contribute
  to the protocol-clean Qwen score.
- Review the Phase 1 closeout report set for final-paper wording and table
  shape using the new repair-attribution language.
- Start a cleanup branch that archives/quarantines superseded diagnostics only
  after the final artifact index is accepted.
- Consolidate reusable ExECTv2 report/reliability builders and add replay or
  governance tests around canonical configs.

### Blocked

- Gan holdout-facing reruns, row-level test analysis, and post-test tuning need
  explicit authorization plus a frozen protocol.
- ExECTv2 full-200 or holdout row-level inspection needs benchmark-facing
  protocol, scorer surface, stop rule, and inspection boundary.

### Done Recently

- 2026-06-23: Ran Qwen repair-attribution iteration. Dev25 reached the earlier
  dictionary-normalized proxy at `0.9055`, but dev140 failed at `0.7821` clean
  and `0.8483` hybrid; full prompt dev25 failed due truncation.
- 2026-06-23: Tightened the repair-attribution protocol to close the
  selector-only loophole: a qualifying Qwen pass must generate and select the
  scored facts, not merely select or default-keep candidate facts.
- 2026-06-23: Ran candidate-backed Qwen action iteration. Dev25 strict passed
  the older non-rescue surface at `0.9450`; dev140 strict missed at `0.8977`.
  The default-keep action contract reached dev140 `0.9155` with hybrid
  `0.9091`, but is now classified as hybrid selector evidence rather than a
  Qwen extraction pass.
- 2026-06-22: Added
  `docs/design/llm_repair_attribution_protocol_2026-06-22.md`, separating
  model-preserving canonical repair from prediction-bearing rescue repair and
  redefining the next Qwen target as protocol-clean F1 `>0.900`; the protocol
  was tightened on 2026-06-23 to require model-origin generation plus
  selection.
- 2026-06-22: Added the visual Qwen repair walkthrough at
  `docs/experiments/exectv2/key_entities/qwen_repair_examples_visual_2026-06-22.html`.
- 2026-06-22: Completed ExECTv2 clinical-utility companion, intermediate score
  surfaces, Phase 1 final consolidation refresh, and frontend static-review
  data refresh.
- 2026-06-21: Completed ExECTv2 v08 all-four clearance, reliability scorecard,
  and Gan Qwen repairfix frozen aggregate test450 audit without row-level test
  inspection for development.

## Guardrails

- Do not inspect Gan `test450` row-level failures, rationales, evidence,
  selected events, or transitions for development.
- Do not inspect ExECTv2 holdout/full-200 row-level failures for development
  without explicit authorization and a frozen protocol.
- Do not make benchmark/full-200 claims from dev140 or dev25 evidence.
- Keep deterministic certainty/CUI/format repairs and semantic add/drop/replace
  actions provenance-stamped and attribution-clean.
