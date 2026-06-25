# Recent Plan Rationalisation

Date: 2026-06-25

Scope: plans created or materially updated in `docs/plans/` during the last
five days. This document is the control surface for reducing planning sprawl; the
individual plans remain as historical design records.

## Current Verdict

The plan stack should collapse to one active sequence:

1. Predeclare and, if still needed, run same-core full-200 aggregate validation
   for GPT-4.1-mini plus DeepSeek only.
2. Clean up run surfacing and labels so the frontend/Observatory comparison
   views are registry-driven and model-aware.
3. Add MLflow observability as optional infrastructure after the canonical
   registry remains visibly in charge.
4. Defer repo archival/refactor cleanup until the evidence spine and current
   reporting surfaces are stable.

Qwen is not on the operational promotion path. It remains a same-core diagnostic
row unless a separately predeclared adapter/prompt repair passes dev140.

## Plan Triage

| Plan | Status | Action |
| --- | --- | --- |
| `final_project_consolidation_implementation_plan_2026-06-22.md` | Mostly complete | Keep as historical closeout record; only the low-priority repo cleanup/refactor ideas remain. |
| `repo_simplification_plan_2026-06-22.md` | Deferred | Keep as the cleanup policy; do not start archive/delete/refactor work until current paper/reporting work is stable. |
| `exectv2_frontend_dataset_integration_implementation_plan_2026-06-22.md` | Complete, with optional resharding | No active work except optional static-data resharding. |
| `component_impact_ablation_architecture_plan_2026-06-24.md` | Complete | No active work; the live contract is the Gan/ExECTv2 component-ablation contract docs and payloads. |
| `exectv2_gpt41mini_simplification_frontier_plan_2026-06-24.md` | Complete | Accepted lean candidate is `exectv2_gpt41mini_simplification_2call_no_sf_adjudicator`; no further simplification is active. |
| `exectv2_same_core_model_swap_architecture_freeze_plan_2026-06-25.md` | Dev140 complete; full-200 predeclaration pending | Keep only the full-200 aggregate predeclaration path active, excluding Qwen from operational candidates. |
| `architecture_comparison_expansion_qwen_deepseek_2026-06-24.md` | Active but lower priority than paper/full-200 sequencing | Implement registry-driven run surfacing and labels after the paper-facing ExECTv2 sequence is stable. |
| `mlflow_experiment_observability_implementation_plan_2026-06-25.md` | Future infrastructure | Start with Phase 0-1 only after the reporting sequence is no longer moving underneath it. |

## Done Checklist

- [x] Final artifact index, cross-model closeout, architecture-selection memo,
  reliability scorecard, and `PROJECT_STATUS.md` closeout surfaces exist.
- [x] ExECTv2 frontend dataset integration is delivered; `/exectv2` redirects to
  the dataset-aware workbench and static ExECTv2 run data is generated from the
  artifact index.
- [x] Cross-dataset reliability scorecard surface and ExECTv2 reliability payload
  exist.
- [x] Gan Component Impact is consolidated to the three selected architecture
  families and backed by the component-ablation contract.
- [x] ExECTv2 Component Impact is backed by replay-only dev140 layer artifacts
  rather than reliability evidence.
- [x] GPT-4.1-mini simplification frontier is complete; the 2-call no-SF
  adjudicator candidate is accepted under the current thresholds.
- [x] Aggregate calibration validation, review-routing validation, robustness
  validation, Investigations rule ablation, and self-consistency evidence are
  recorded for the reliability scorecard.
- [x] Same-core model-swap dev140 rows exist for GPT-4.1-mini, DeepSeek, and
  Qwen, with Qwen operational instability caveated.
- [x] Qwen same-core output-contract audit and repair v01 readout exist; repair
  v01 failed the operational gate, so Qwen remains diagnostic.
- [x] Paper-facing reliability/component-evidence language exists and separates
  reliability trust evidence from component-impact delta evidence.
- [x] ExECTv2 results-section scaffold exists at
  `docs/research/exectv2_results_section_scaffold_2026-06-25.md`, including the
  same-core dev140 table and diagnostic-only Qwen caveat.

## Remaining Work, In Order

### P0: Results-Section Scaffold - Complete

Completed in `docs/research/exectv2_results_section_scaffold_2026-06-25.md`.
The scaffold includes the same-core dev140 model table: DeepSeek `0.8596`,
GPT-4.1-mini `0.8396`, Qwen `0.8018`, all on `clinical_headline`, with Qwen
clearly marked diagnostic because of operational/output-contract failures.
Strict benchmark/CUI results remain diagnostic/comparability only.

### P1: Same-Core Full-200 Predeclaration

- Draft a fresh aggregate-only predeclaration for the frozen same-core
  architecture.
- Include GPT-4.1-mini and DeepSeek as operational candidates.
- Include Qwen only as a caveated diagnostic row if it is included at all.
- Freeze candidate ids, scorer/view, stop rule, allowed aggregate outputs, and
  the no-row-inspection policy before any execution.

### P2: Registry-Driven Run Surfacing

- Implement the still-active architecture-comparison expansion after P0/P1.
- Add registry/display curation fields, remove hardcoded Gan labels where the
  registry can own them, and make Explorer selection explicit by `run_id`.
- Regenerate Component Impact/Explorer payloads so model variants do not collapse
  into a family-level "best row" heuristic.
- Keep test450 and full-200 restricted surfaces out of interactive row-level
  surfacing.

### P3: Optional MLflow Observability

- Implement MLflow Phase 0-1 only: ADR/dependency boundary, `.gitignore`, and a
  disabled-safe helper with tests.
- Treat the same-core model-swap dev140 comparison as the first mirror target
  after the helper exists.
- Keep `experiments/registry.jsonl`, `RUN_INDEX.md`, and source reports as the
  claim-of-record.

### P4: Deferred Cleanup

- Use `repo_simplification_plan_2026-06-22.md` only after P0-P3 stabilize.
- Archive superseded artifacts on a dedicated cleanup branch, with the final
  artifact index updated first.
- Refactor shared builders/metrics only when it reduces active maintenance
  burden; do not rewrite evidence history.

## Explicitly Not Active

- New Gan holdout-facing reruns or test-row analysis.
- ExECTv2 full-200 or holdout row-level failure inspection.
- Lower-burden review-routing promotion without a dev140-only redesign and fresh
  predeclaration.
- Live Investigations selective-adjudicator experiments; the current capped
  scaffold meets burden but loses too much F1.
- Additional GPT-4.1-mini simplification beyond the accepted 2-call no-SF
  adjudicator frontier point.
