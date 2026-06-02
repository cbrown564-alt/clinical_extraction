# Project Status

Last updated: 2026-06-02

## Active Objective

Build a Gan 2026 seizure-frequency extraction pipeline that can reach at least
0.9000 Purist F1 on development surfaces while preserving transparent evidence
trails, ablations, and conservative benchmark language.

## Current Strategy

Use Gan 2026 as the first controlled extraction surface. Keep deterministic V1
frozen as `rules_only_v1`; keep hybrid v0.2
`cluster_diary_candidate_recall` frozen as a comparator-only generalization
audit result; organize new work around validation-only
`hybrid_clinical_frequency_state_graph` diagnostics with separate coverage,
projection, invariance, and arbitration ablations.

## Recent Context

- Split `gan2026_split_v1` is locked: 300 train, 750 validation, 450 holdout. LLM/DSPy work escalates 25 -> 50 -> 250 validation rows; test is not tuning.
- Deterministic V1 remains the frozen comparator: 0.9293/0.9387 validation and 0.7600/0.7867 on its one locked-test Purist/Pragmatic evaluation.
- Structured v0.5 reached 675/750 Purist = 0.9000 on full validation, but audit classified it as repair-heavy hybrid behavior rather than clean LLM-first.
- LLM-only claim-table selector v4 reached 231/250 clean Purist after schema replay, but full validation collapsed to 528/750 clean Purist and 577/750 clean Pragmatic. Do not extend it without a v5 redesign and written decision.
- Hybrid v0.2 `cluster_diary_candidate_recall` improved the 56-row synthetic hard-case panel but did not generalize: locked-test gated final tied deterministic Purist at 343/450 and dropped Pragmatic to 353/450; full validation underperformed deterministic top at 677/750 Purist and 686/750 Pragmatic.
- State-graph validation diagnostics are the active research cycle. Validation50 oracle coverage is 47/50, projection Purist/Pragmatic F1 is 0.9600, and the validation hard-slice union has oracle coverage 219/250 with projection Purist F1 0.9160.
- Hosted boundary-state graph-builder work recovered useful unknown/unresolved-multiple coverage: validation31 produced 10/31 representability-gain candidates; synthetic unknown8 v1 produced 8/8 schema-valid, exact-evidence-valid unknown nodes. Accepted-node replay recovered representability on all 10 validation gain rows, but unchanged projection exactly matched only 6/10 labels.
- Projection remains separate from node construction. Boundary-state priority fixed 17/42 miss-only projection rows; seizure-free duration work showed node coverage can be high while unchanged projection stays at 0/18 exact duration labels.
- Month-bucket duration-selection ablations are complete through gated v1. v0 fixed 18/18 enriched duration target rows but caused 27 already-correct regressions; gated v1 preserved the 18/18 target corrections while reducing regression-panel changes to 4/232, with 0 already-correct and 0 frequency-with-seizure-free regressions. It remains revise-only pending a broader enriched-node regression panel.
- A strong LLM-heavy alternative is now required and protocolized: `llm_heavy_clinical_frequency_reasoner` makes the model responsible for extraction, clinical normalization proposal, aggregation/selection, and final schema representation, while deterministic code validates, scores, and applies named benchmark-alignment adapters only.
- `llm_heavy_clinical_frequency_reasoner_v1` passed the validation50 output-contract gate but failed validation250 as an LLM-heavy final-label candidate. Validation50 was 50/50 structured, 48/50 selected evidence exact, and 41/50 raw Purist. Validation250 was 237/250 structured, 230/250 selected evidence exact, 188/250 raw Purist, and 219/250 selected-evidence-arithmetic Purist; the arithmetic layer remains attribution-diagnostic only.
- Accepted synthetic unknown8 v1 boundary nodes have now been replayed for coverage accounting only: baseline representability was 0/8 and diagnostic merge representability was 8/8; unchanged projection still missed one row, keeping projection/arbitration separate.
- Routine LLM experiments use cache-first `gan2026-llm-experiment --pipeline ...`; saved-output replay is reserved for explicit offline artifact analysis.
- Clean scorer-facing normalization is frozen unless direct-citation review justifies another family. Shared schema repair is alias-only; parser defaults belong to their task parser.
- Named repair-mode metadata is now shared beyond structured-events: claim-table score layers, hybrid adjudicator score layers, repair ablations, and component-ablation rows expose stable attribution metadata for raw, strict, clean, selected-evidence, deterministic, and hybrid gated modes.
- Package ownership boundaries are now stable under `contract/`, `deterministic/`, `selected_evidence/`, `llm/`, `hybrid/`, `reports/`, `experiments/`, and `cli/`. Phase 6 run-registry scaffolding is active: `experiments/registry.jsonl` is canonical and `experiments/RUN_INDEX.md` is the human scan surface.

## Key References

- Protocol/control: `docs/design/gan2026_split_protocol.md`, `docs/design/data_contract.md`, `docs/research/contribution_thesis.md`
- Package organization: `docs/decisions/0004-gan2026-package-organization.md`
- Run registry: `experiments/registry.jsonl`, `experiments/RUN_INDEX.md`
- Generalization gap: `experiments/gan2026_generalization_gap_research_report_2026-06-02.md`
- State-graph protocol and row review: `experiments/gan2026_clinical_frequency_state_graph_protocol_2026-06-02.md`, `experiments/gan2026_clinical_frequency_state_graph_row_family_review_2026-06-02.md`
- Boundary-state graph-builder: `experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_validation31_synthetic_unknown8_interpretation_2026-06-02.md`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_synthetic_unknown8_v1_unknown_recall_gpt41mini_live_2026-06-02.md`
- Projection and duration diagnostics: `experiments/gan2026_hybrid_clinical_frequency_state_graph_projection_arbitration_ablation_2026-06-02.md`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_projection_ablation_2026-06-02.md`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_node_replay_2026-06-02.md`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_enriched_projection_replay_2026-06-02.md`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_month_bucket_duration_selection_decision_2026-06-02.md`, `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v0_2026-06-02.md`, `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v1_2026-06-02.md`
- LLM-heavy alternative: `experiments/gan2026_llm_heavy_extraction_protocol_2026-06-02.md`, `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_v0_validation25_error_analysis_2026-06-02.md`
- Full retrospective: `docs/research/gan2026_full_research_retrospective_2026-06-02.md`
- Retrospective HTML/PDF: `docs/research/gan2026_full_research_retrospective_2026-06-02.html`, `docs/research/gan2026_full_research_retrospective_2026-06-02.pdf`
- Prior LLM/hybrid comparators: `experiments/gan2026_section_claim_table_validation750_v4_interpretation_2026-06-01.md`, `experiments/gan2026_arch2_validation750_v01_interpretation_2026-06-01.md`, `experiments/gan2026_hybrid_adjudicator_v02_selective_action_report_2026-06-01.md`

## Active Priorities

1. Keep deterministic V1 and hybrid v0.2 `cluster_diary_candidate_recall` frozen as comparators; do not tune gates or candidate rules from the locked-test audit.
2. Build the clinical frequency state graph as a diagnostic substrate before another final-label prompt.
3. Keep semantic repair, graph projection, scorer normalization, and production policy separately named, ablated, and claimed.
4. Treat saturated validation scores as low-information; prefer hard slices, selective-action profiles, graph invariance panels, and frozen generalization audits.
5. Separate benchmark gold-normalization policy from clinical reasoning while preserving source-near traces.

## Work Board

### Now

- Design a broader enriched-node regression panel before any duration projection policy promotion.
- Review `llm_heavy_clinical_frequency_reasoner_v1` validation250 failure families before another LLM-heavy prompt revision; do not escalate this version further.

### Next

- Keep claim-table v5 and v0.2 schema/gate ablations available as comparators, but do not promote them ahead of the state-graph coverage cycle.
- Design LLM-replacement ablations for deterministic post-processing modules, reporting score, repair attribution, evidence validity, and replay variance.

### Blocked

- Final benchmark-comparison language and further holdout analysis are blocked until replication comparability is explicit and locked-test discipline permits.
- Do not run LLM-only claim-table selector beyond 250 rows until v5 passes the 25/50 ladder and a written decision justifies another 250-row diagnostic.

### Done Recently

- 2026-06-02: Completed full row-level error analysis for `llm_heavy_clinical_frequency_reasoner_v0` validation25. Key finding: raw LLM labels are 0/25 scorable, format-only is 10/25 Purist correct, selected-evidence arithmetic is 23/25 but attribution-invalid for LLM-heavy promotion, and benchmark alignment regresses 10 rows relative to arithmetic. Decision remains revise-only before validation50.
- 2026-06-02: Ran `llm_heavy_clinical_frequency_reasoner_v1` validation50 and validation250. Validation50 passed the output-contract gate after non-semantic alias repair, but validation250 rejected promotion: 13 parse/schema failures, 9 selected-event trace mismatches, raw/format-only Purist 188/250, benchmark-aligned Purist 204/250, and selected-evidence-arithmetic Purist 219/250 as diagnostic-only evidence-selection signal.
- 2026-06-02: Rendered the full research retrospective as a print-ready editorial HTML page and 16-page A4 PDF for iPad reading/markup; added a reusable renderer script.
- 2026-06-02: Implemented `llm_heavy_clinical_frequency_reasoner_v1` prompt/schema fixes from the validation25 error analysis: exact selected-event evidence contract, parser-ready final-label guidance with inequality examples, seizure-free distractor warning, `raw_clinical_summary`, multi-event rationale fields, and shape-only quantity alias repair.
- 2026-06-02: Added full research retrospective synthesizing rules-only, structured-events, claim-table, hybrid adjudicator, state-graph, and LLM-heavy work against the core contribution thesis.
- 2026-06-02: Implemented and ran `llm_heavy_clinical_frequency_reasoner_v0` validation25 schema smoke with raw, format-only, selected-evidence arithmetic, benchmark-aligned, and oracle-format score layers. Saved-output schema replay reached 24/25 structured rows and 0 selected-event trace mismatches, but selected evidence exactness was 18/25 and raw LLM scorable was 0/25; registered as revise-only before validation50.
- 2026-06-02: Added `gan2026_llm_heavy_extraction_protocol_2026-06-02.md`, defining the required LLM-heavy research track where the model owns extraction, normalization proposal, aggregation/selection, and final schema representation; deterministic behavior is limited to validation, scoring, and named benchmark adapters.
- 2026-06-02: Completed gated `month_bucket_duration_selection_v1`: preserved 18/18 target duration corrections and removed v0's already-correct and frequency-with-seizure-free regressions; 4/232 wrong-to-wrong regression changes remain, so no production policy is promoted.
- 2026-06-02: Completed `gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v0`: 18/18 target duration corrections, 0 target regressions, but 37/232 regression-panel label changes and 27 already-correct regressions. Decision: revise-only; no scorer, graph-builder, production projection, or holdout change.
- 2026-06-02: Replayed accepted synthetic unknown8 v1 boundary nodes into a diagnostic graph merge for coverage accounting only; coverage recovered to 8/8 while projection/scoring policy remained out of scope.
- 2026-06-02: Decided that replay-only `month_bucket_duration_selection` becomes a separately named projection-ablation seed; scorer normalization and production projection policy remain unchanged.
- 2026-06-02: Completed the state-graph coverage, projection, boundary-state, and seizure-free duration diagnostic cycle through validation-only replay artifacts. Key result: coverage and duration-node construction are promising, but projection/arbitration remains the current bottleneck and no production policy is promoted.
- 2026-06-02: Extended shared named repair-mode metadata from structured-events into claim-table score layers, hybrid adjudicator score layers, repair-family ablations, and component-ablation row attribution.
- 2026-06-02: Consolidated saved-output replay and artifact-ablation helpers into `gan2026/artifact_analysis`, leaving compatibility wrappers under `experiments/` and moving raw-output replay loading out of generic artifact writing helpers.
- 2026-06-02: Completed the hybrid v0.2 `cluster_diary_candidate_recall` frozen generalization audit. The result moved new development away from final-label prompt/gate tuning and toward validation-only semantic-state graph diagnostics.
- 2026-06-01: Completed the v0.2 hybrid adjudicator development cycle through validation25/50/250, saturated-surface analysis, synthetic hard-case component stress, row-level failure review, and named candidate-recall revision.
- 2026-06-01: Added intermediate-schema synthesis, saturated-validation workflow, cache-first LLM experiment CLI, cross-architecture component-ablation tooling, package-organization cleanup, and restored green Ruff, mypy, and full pytest after schema-repair and ownership-boundary work.

## Immediate Next Step

Review `llm_heavy_clinical_frequency_reasoner_v1` validation250 failure families, especially parse/schema tail failures, selected-event trace mismatches, and raw-label errors relative to selected-evidence arithmetic. Keep the broader enriched-node regression panel as the state-graph projection follow-up.
