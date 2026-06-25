# Project Status

Last updated: 2026-06-25

## Active Objective

ExECTv2 is in a reliability and component-evidence phase after the Satellite 13
LLM-only plateau. `clinical_headline` de-duplicated clinical recovery is the
headline surface; strict benchmark/CUI results stay diagnostic. Paper-facing
claim language is consolidated at
`docs/research/exectv2_reliability_component_evidence_paper_language_2026-06-25.md`
and the results-section scaffold is at
`docs/research/exectv2_results_section_scaffold_2026-06-25.md`.

## Current Read

The 2026-06-25 evidence stack is:

- GPT-4.1-mini current-code v08 full-200 aggregate: verifier-backed `0.8502`
  overall `clinical_headline` F1; no-verifier ablation `0.8431`; accepted lean
  2-call no-SF-adjudicator candidate `0.8356` overall and `0.7525` SF.
- Same-core dev140 model swap: DeepSeek `0.8596`, GPT-4.1-mini `0.8396`, Qwen
  `0.8018`, all with `1.0000` exact evidence; Qwen remains diagnostic because
  of output-contract instability and failed repair v01.
- Reliability validation: calibration ECE `0.0432`, Brier `0.2245` versus
  `0.2387`; lower-burden review routing failed validation (`0.9661` burden,
  `0.9037` catch); robustness hard-slice F1 `0.8336` across `414` eligible
  family cells with schema/evidence validity `1.0000`.
- Investigations deterministic replacement is not ready: verifier +
  deterministic suppression remains strongest at `0.9213`; v04 meets `0.2000`
  burden but drops F1.
- Gan 2026 v0.7 DeepSeek Reasoner holdout aggregate is final: test450 `346/450`
  Purist, `365/450` Pragmatic, `0` call failures; no row-level test inspection
  or post-test tuning is authorized.

The same-core full-200 predeclaration now exists at
`docs/experiments/exectv2/reliability/exectv2_same_core_full200_predeclaration_2026-06-25.md`.
It freezes GPT-4.1-mini and DeepSeek as operational candidates, keeps Qwen out
of the operational candidate set, and preserves aggregate-only full-200
reporting.

## Active Priorities

1. Treat `clinical_headline` de-duplicated clinical recovery as the primary
   LLM-only optimization target; report strict benchmark results only as a
   diagnostic/comparability surface.
2. Preserve attribution discipline: the model emits every scored fact;
   deterministic code may validate evidence and perform tagged projection, but
   must not add, select, or reject clinical facts inside the LLM-only score line.
3. Keep Reliability Scorecard separate from Component Impact: reliability is
   trust evidence; component impact must be ablation/delta evidence.
4. Treat reliability-score improvements as research work: every score increase
   should name the split, scorer, inspection boundary, and whether evidence is
   dev-only, validation, full-200, or holdout.

## Work Board

### Now

- Execute and report the same-core full-200 aggregate-only audit only from
  `docs/experiments/exectv2/reliability/exectv2_same_core_full200_predeclaration_2026-06-25.md`
  if that comparison is still needed; keep Qwen excluded.
- Implement registry-driven run surfacing and labels for the
  Explorer/Component Impact surfaces after the same-core full-200 execution
  decision is settled.
- Use `docs/plans/recent_plan_rationalisation_2026-06-25.md` as the current
  sequence; defer MLflow and repo cleanup until the reporting/registry path is
  stable.

### Next

- Add registry/display curation fields, remove hardcoded Gan labels where the
  registry can own them, and make Explorer selection explicit by `run_id`.
- Regenerate Component Impact/Explorer payloads so model variants do not
  collapse into a family-level "best row" heuristic.
- If Qwen is revisited, predeclare v02 separately and decide whether invalid
  event-family dropping or valid-object extraction is format-only schema repair
  or a semantic adapter before any rerun.
- Plan true component-off reliability ablations only after scorecard language is
  stable; reliability is trust evidence, component impact is delta evidence.
- Keep MLflow observability, repo cleanup, and Investigations cost work deferred.

### Blocked

- Additional Gan holdout-facing reruns, row-level test analysis, and post-test
  tuning remain blocked after the authorized v0.7 aggregate audit unless
  separately authorized under a fresh frozen protocol.
- ExECTv2 full-200 or holdout row-level inspection remains blocked; the
  reliability-audit protocol authorizes aggregate validation outputs only.
- Qwen same-core full-200 promotion is blocked unless a Qwen-specific dev140
  adapter/prompt repair is separately predeclared and passes.
- Promotion of the lower-burden review-routing candidate is blocked by failed
  aggregate validation; any retry needs dev140-only redesign and a fresh
  predeclaration.

### Done Recently

- 2026-06-25: Drafted the same-core full-200 aggregate-only predeclaration,
  freezing GPT-4.1-mini plus DeepSeek as operational candidates and keeping
  Qwen diagnostic-only.
- 2026-06-25: Converted the paper-facing reliability/component-evidence
  language into the ExECTv2 results-section scaffold, including the same-core
  dev140 table and diagnostic-only Qwen operational caveat.
- 2026-06-25: Rationalised recent plans; active order is results scaffold,
  same-core full-200 predeclaration/execution decision, registry-driven run
  surfacing, optional MLflow, then deferred cleanup.
- 2026-06-25: Completed Qwen output-contract audit and repair v01 readout;
  repair v01 failed the operational gate at `50/140`, so Qwen remains
  diagnostic-only.
- 2026-06-25: Completed same-core dev140 model-swap readout: DeepSeek
  `0.8596`, GPT-4.1-mini `0.8396`, Qwen `0.8018`, all with `1.0000` exact
  evidence and Qwen operational caveats.
- 2026-06-25: Completed aggregate-only calibration, robustness,
  self-consistency, Investigations, and Gan v0.7 holdout audit updates; linked
  artifacts remain the source of detailed numeric evidence.
- 2026-06-24: Completed current-code v08 full-200 GPT-4.1-mini architecture and
  no-verifier audits, refreshed reliability scorecard infrastructure, and froze
  the reliability-audit protocol.
- 2026-06-22 to 2026-06-24: Completed final consolidation, ExECTv2 frontend MVP,
  cross-dataset reliability scorecard, Gan component-ablation simplification,
  and Satellite 13 Phases 0-6.

## Guardrails

- Do not describe de-duplicated `clinical_headline` recovery as a strict
  benchmark win or compare it directly to the paper's strict target.
- Do not inspect Gan `test450` row-level failures, rationales, evidence,
  selected events, or transitions for development.
- Do not inspect ExECTv2 holdout/full-200 row-level failures for development;
  the current reliability-audit protocol authorizes aggregate validation only.
- Keep deterministic projection, hybrid rescue, and verifier rejection
  provenance-stamped and separated in reported score lines.
