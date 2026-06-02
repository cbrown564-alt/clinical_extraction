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
- The latest duration-selection diagnostic over 18 replayed seizure-free duration graphs recovered 18/18 exact duration labels with replay-only `month_bucket_duration_selection`. This is validation-only output-surface analysis, not scorer normalization or production projection promotion.
- Routine LLM experiments use cache-first `gan2026-llm-experiment --pipeline ...`; saved-output replay is reserved for explicit offline artifact analysis.
- Clean scorer-facing normalization is frozen unless direct-citation review justifies another family. Shared schema repair is alias-only; parser defaults belong to their task parser.
- Package ownership boundaries are now stable under `contract/`, `deterministic/`, `selected_evidence/`, `llm/`, `hybrid/`, `reports/`, `experiments/`, and `cli/`. Phase 6 run-registry scaffolding is active: `experiments/registry.jsonl` is canonical and `experiments/RUN_INDEX.md` is the human scan surface.

## Key References

- Protocol/control: `docs/design/gan2026_split_protocol.md`, `docs/design/data_contract.md`, `docs/research/contribution_thesis.md`
- Package organization: `docs/decisions/0004-gan2026-package-organization.md`
- Run registry: `experiments/registry.jsonl`, `experiments/RUN_INDEX.md`
- Generalization gap: `experiments/gan2026_generalization_gap_research_report_2026-06-02.md`
- State-graph protocol and row review: `experiments/gan2026_clinical_frequency_state_graph_protocol_2026-06-02.md`, `experiments/gan2026_clinical_frequency_state_graph_row_family_review_2026-06-02.md`
- Boundary-state graph-builder: `experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_validation31_synthetic_unknown8_interpretation_2026-06-02.md`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_synthetic_unknown8_v1_unknown_recall_gpt41mini_live_2026-06-02.md`
- Projection and duration diagnostics: `experiments/gan2026_hybrid_clinical_frequency_state_graph_projection_arbitration_ablation_2026-06-02.md`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_projection_ablation_2026-06-02.md`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_node_replay_2026-06-02.md`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_enriched_projection_replay_2026-06-02.md`
- Prior LLM/hybrid comparators: `experiments/gan2026_section_claim_table_validation750_v4_interpretation_2026-06-01.md`, `experiments/gan2026_arch2_validation750_v01_interpretation_2026-06-01.md`, `experiments/gan2026_hybrid_adjudicator_v02_selective_action_report_2026-06-01.md`

## Active Priorities

1. Keep deterministic V1 and hybrid v0.2 `cluster_diary_candidate_recall` frozen as comparators; do not tune gates or candidate rules from the locked-test audit.
2. Build the clinical frequency state graph as a diagnostic substrate before another final-label prompt.
3. Keep semantic repair, graph projection, scorer normalization, and production policy separately named, ablated, and claimed.
4. Treat saturated validation scores as low-information; prefer hard slices, selective-action profiles, graph invariance panels, and frozen generalization audits.
5. Separate benchmark gold-normalization policy from clinical reasoning while preserving source-near traces.

## Work Board

### Now

- Replay accepted synthetic unknown8 v1 nodes into a diagnostic graph merge only if needed for coverage accounting; keep projection, scoring, and production policy out of scope.

### Next

- Decide whether `month_bucket_duration_selection` is only a diagnostic oracle-style selector or the seed for a separately named projection ablation.
- Keep claim-table v5 and v0.2 schema/gate ablations available as comparators, but do not promote them ahead of the state-graph coverage cycle.
- Design LLM-replacement ablations for deterministic post-processing modules, reporting score, repair attribution, evidence validity, and replay variance.
- Consolidate remaining saved-output replay helpers into dedicated artifact-analysis modules.
- Extend named repair-mode metadata beyond structured-events where downstream repair layers blur raw, strict, clean, selected-evidence, and hybrid attribution.

### Blocked

- Final benchmark-comparison language and further holdout analysis are blocked until replication comparability is explicit and locked-test discipline permits.
- Do not run LLM-only claim-table selector beyond 250 rows until v5 passes the 25/50 ladder and a written decision justifies another 250-row diagnostic.

### Done Recently

- 2026-06-02: Completed the state-graph coverage, projection, boundary-state, and seizure-free duration diagnostic cycle through validation-only replay artifacts. Key result: coverage and duration-node construction are promising, but projection/arbitration remains the current bottleneck and no production policy is promoted.
- 2026-06-02: Completed the hybrid v0.2 `cluster_diary_candidate_recall` frozen generalization audit. The result moved new development away from final-label prompt/gate tuning and toward validation-only semantic-state graph diagnostics.
- 2026-06-01: Completed the v0.2 hybrid adjudicator development cycle through validation25/50/250, saturated-surface analysis, synthetic hard-case component stress, row-level failure review, and named candidate-recall revision.
- 2026-06-01: Added intermediate-schema synthesis, saturated-validation workflow, cache-first LLM experiment CLI, cross-architecture component-ablation tooling, package-organization cleanup, and restored green Ruff, mypy, and full pytest after schema-repair and ownership-boundary work.

## Immediate Next Step

Replay accepted synthetic unknown8 v1 nodes into a diagnostic graph merge only if coverage accounting needs it; keep projection, scoring, and production policy out of scope.
