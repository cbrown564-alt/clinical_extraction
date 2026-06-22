# Project Status

Last updated: 2026-06-22

## Active Objective

Final project consolidation Phase 1 is complete. The current objective is to
run the next Qwen iteration under the new LLM repair attribution protocol:
reach ExECTv2 F1 `>0.900` on the declared development surface using only
model-preserving canonical repair, with prediction-bearing rescue repair
disabled or counted as model error.

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

The predeclared protocol now exists:
`docs/design/llm_repair_attribution_protocol_2026-06-22.md`. It separates
allowed model-preserving repair from disallowed prediction-bearing rescue
repair. The Qwen target is no longer a residual-repair headline score; it is
`>0.900` F1 on a protocol-clean `model_preserving_canonical` surface, while
rescued facts remain visible as model false negatives/false positives.

Phase 1 closeout artifacts, frontend static review data, and the clinical-
utility companion audit are current. Dataset-aware frontend integration remains
tracked in
`docs/plans/exectv2_frontend_dataset_integration_implementation_plan_2026-06-22.md`.

## Active Priorities

1. Treat v08 as the performance control and v09 partial hybrid as the
   simplification control.
2. Treat DeepSeek/Qwen dev140 as diagnostic portability evidence; resume Qwen
   only for the predeclared protocol-clean rerun objective.
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

- Design and run the next Qwen ExECTv2 development iteration under
  `docs/design/llm_repair_attribution_protocol_2026-06-22.md`, targeting
  F1 `>0.900` on the `model_preserving_canonical` surface.
- Build/report the four required Qwen score surfaces: `raw_model`,
  `schema_format`, `model_preserving_canonical`, and `hybrid_full_stack`.
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

- 2026-06-22: Added
  `docs/design/llm_repair_attribution_protocol_2026-06-22.md`, separating
  model-preserving canonical repair from prediction-bearing rescue repair and
  redefining the next Qwen target as protocol-clean F1 `>0.900`.
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
