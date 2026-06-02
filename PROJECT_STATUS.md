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
- Month-bucket duration-selection ablations are complete through graph-gated
  v2. v0 fixed 18/18 enriched duration target rows but caused 27
  already-correct regressions; gated v1 preserved the 18/18 target corrections
  while leaving 4/232 regression-panel changes. Graph-gated v2 uses graph
  metadata instead of validation row tags, preserves 18/18 target corrections,
  and leaves 0/232 broad-regression label changes. It remains a validation-only
  diagnostic and is not production projection policy.
- A strong LLM-heavy alternative is now required and protocolized: `llm_heavy_clinical_frequency_reasoner` makes the model responsible for extraction, clinical normalization proposal, aggregation/selection, and final schema representation, while deterministic code validates, scores, and applies named benchmark-alignment adapters only.
- `llm_heavy_clinical_frequency_reasoner_v1` passed the validation50 output-contract gate but failed validation250 as an LLM-heavy final-label candidate. Validation50 was 50/50 structured, 48/50 selected evidence exact, and 41/50 raw Purist. Validation250 was 237/250 structured, 230/250 selected evidence exact, 188/250 raw Purist, and 219/250 selected-evidence-arithmetic Purist; the arithmetic layer remains attribution-diagnostic only.
- The next-task review found LLM-heavy v1 failure families in schema enum drift,
  selected-event trace mismatches, raw-label grammar/rendering, bimonthly and
  compact-interval semantics, cluster-axis flattening, vague-count handling, and
  conditional/perimenstrual boundary answers. Treat v2 as a redesign starting at
  validation25, not a continuation run.
- Accepted synthetic unknown8 v1 boundary nodes have now been replayed for coverage accounting only: baseline representability was 0/8 and diagnostic merge representability was 8/8; unchanged projection still missed one row, keeping projection/arbitration separate.
- Routine LLM experiments use cache-first `gan2026-llm-experiment --pipeline ...`; saved-output replay is reserved for explicit offline artifact analysis.
- Qwen 3.6/Ollama setup lane is complete for endpoint routing but not yet validation-ladder ready. Verified local tags `qwen3.6:35b` and `qwen3.6:27b`; adopted `qwen3.6:35b` as the intended strong-local tag; routed DSPy/LiteLLM through native `ollama_chat/qwen3.6:35b` at `http://localhost:11434` with `think=false`; documented and rejected the OpenAI-compatible `/v1/chat/completions` route for Qwen reasoning models; recorded hardware/model metadata and registered a validation1 setup smoke. The validation1 smoke had 0 call failures and nonempty output, but Qwen returned Python-style single-quoted output plus a `final_selector` shape, so v5 remains blocked on prompt hardening or a named schema-repair ablation before validation5/25.
- The simplified schema branch is now the active local-model transfer lane. It
  keeps rich diagnostics as deterministic sidecars but reduces the raw model
  contract to `answer` plus `supporting_facts` in
  `llm_only_minimal_evidence_selector_v0`. This is intended to test whether
  local models can reliably emit answer state and exact evidence before asking
  them to satisfy the full v5 claim-table selector.
- First hosted simplified-contract baseline is recorded:
  `llm_only_minimal_evidence_selector_v0` on GPT-4.1 mini validation25 live
  produced 25/25 minimal records, 0 call failures, 0 invalid JSON/schema
  failures, no alias repairs, answer evidence exact in 24/25 rows,
  supporting-fact evidence exact in 49/50 facts, raw minimal-answer Purist and
  Pragmatic 2/25 because source-near answers are mostly scorer-unparsable,
  strict-format 15/25, and frozen clean scorer-facing 16/25 Purist and
  Pragmatic. Derived state and review projection were complete for 25/25 rows;
  scorer-facing normalization with monthly frequency was complete for 16/25.
  Error analysis found the main gap versus claim-table v4/v5 is not evidence
  selection but the missing parser-ready `final_label` conversion field; see
  `experiments/gan2026_minimal_evidence_selector_validation25_error_analysis_2026-06-01.md`.
- Clean scorer-facing normalization is frozen unless direct-citation review justifies another family. Shared schema repair is alias-only; parser defaults belong to their task parser.
- Named repair-mode metadata is now shared beyond structured-events: claim-table score layers, hybrid adjudicator score layers, repair ablations, and component-ablation rows expose stable attribution metadata for raw, strict, clean, selected-evidence, deterministic, and hybrid gated modes.
- Package ownership boundaries are now stable under `contract/`, `deterministic/`, `selected_evidence/`, `llm/`, `hybrid/`, `reports/`, `experiments/`, and `cli/`. Phase 6 run-registry scaffolding is active: `experiments/registry.jsonl` is canonical and `experiments/RUN_INDEX.md` is the human scan surface.
- The first saved-output LLM-replacement ablation replay is complete on the
  LLM-heavy v1 validation250 artifact. Raw and format-only Purist stayed
  188/250, selected-evidence arithmetic rose to 219/250 with 32 raw-wrong to
  correct changes and one raw-correct regression, and benchmark alignment rose
  to 204/250 with 16 raw-wrong to correct changes. This confirms
  selected-evidence arithmetic as the main deterministic replacement target
  before any v2 prompt work, while decision 0005 records that arbitrary
  benchmark conventions may remain better as named deterministic adapters than
  overloaded prompt instructions.
- Decision 0006 now gates `llm_heavy_clinical_frequency_reasoner_v2` on a
  validation25 LLM-owned selected-evidence arithmetic/rendering smoke. The smoke
  must keep deterministic arithmetic as a side-car, require exact selected
  evidence and zero trace mismatches, and reject escalation if the model still
  needs deterministic semantic replacement to clear the target.
- The v2 validation25 smoke is complete and rejected for validation50
  escalation under decision 0006. Calls succeeded 25/25 and raw model-owned
  Purist was 21/25 with no deterministic selected-evidence arithmetic gap, but
  only 22/25 rows were structured/scorable, selected-evidence exact,
  rendering-operands present, and arithmetic-trace present. The next revision
  should fix output-contract compactness/exact evidence and the row 187
  selected-fact error before any broader run.
- V2 row-level error analysis narrows the revision target: 2 rows omitted
  `final_answer.selected_event_ids`, 1 row truncated into invalid JSON, 2
  otherwise-correct rows copied invalid non-selected administrative evidence,
  and 1 row converted cluster cadence into events-per-cluster. The analysis
  confirms there was no deterministic selected-evidence arithmetic rescue gap.
- `llm_heavy_clinical_frequency_reasoner_v2_compact` fixed the prior
  truncation/schema family on validation25: 25/25 structured, 0 parse/schema
  failures, 0 selected-event trace mismatches. It still rejects validation50
  escalation under decision 0006: raw labels were 23/25 scorable and 22/25
  Purist, selected evidence was exact 22/25, rendering operands/traces were
  24/25, and deterministic selected-evidence arithmetic corrected 3 raw-wrong
  rows. Remaining issues are parser-ready rendering, exact selected-evidence
  copying, row 187 cluster-cadence semantics, and an empty no-reference case.
- DSPy adapter research now points to a separate architecture rather than a v2
  patch. `llm_only_typed_adapter_reasoner` should test typed DSPy output fields
  with scoped `JSONAdapter` use, preserving v2 as the prompt/schema redesign
  path and keeping raw model-owned labels distinct from deterministic side-car
  arithmetic or benchmark adapters.
- `llm_only_typed_adapter_reasoner_v0` is now scaffolded and rejected on its
  predeclared validation25 smoke. The typed `JSONAdapter` substrate succeeded
  mechanically with 25/25 structured outputs, 0 adapter parse failures, 0 call
  failures, and 0 selected-event trace mismatches, but raw labels were only
  22/25 scorable, selected evidence was exact 19/25, event evidence exactness
  was 31/38, arithmetic traces were present 17/25, and deterministic
  selected-evidence arithmetic corrected 3 raw-wrong rows. This is useful
  adapter evidence but not a validation50 promotion.

## Key References

- Protocol/control: `docs/design/gan2026_split_protocol.md`, `docs/design/data_contract.md`, `docs/research/contribution_thesis.md`
- Package/attribution decisions: `docs/decisions/0004-gan2026-package-organization.md`, `docs/decisions/0005-benchmark-format-rules-vs-llm-clinical-reasoning.md`, `docs/decisions/0006-validation25-llm-owned-selected-evidence-rendering-smoke.md`
- Run registry: `experiments/registry.jsonl`, `experiments/RUN_INDEX.md`
- Generalization gap: `experiments/gan2026_generalization_gap_research_report_2026-06-02.md`
- State-graph protocol and row review: `experiments/gan2026_clinical_frequency_state_graph_protocol_2026-06-02.md`, `experiments/gan2026_clinical_frequency_state_graph_row_family_review_2026-06-02.md`
- Boundary-state graph-builder: `experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_validation31_synthetic_unknown8_interpretation_2026-06-02.md`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_boundary_builder_synthetic_unknown8_v1_unknown_recall_gpt41mini_live_2026-06-02.md`
- Projection and duration diagnostics: `experiments/gan2026_hybrid_clinical_frequency_state_graph_projection_arbitration_ablation_2026-06-02.md`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_projection_ablation_2026-06-02.md`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_node_replay_2026-06-02.md`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_seizure_free_duration_enriched_projection_replay_2026-06-02.md`, `experiments/gan2026_hybrid_clinical_frequency_state_graph_month_bucket_duration_selection_decision_2026-06-02.md`, `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v0_2026-06-02.md`, `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_v1_2026-06-02.md`, `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_broad_regression_v1_2026-06-02.md`
- Graph-gated duration selection: `experiments/gan2026_state_graph_projection_ablation_month_bucket_duration_selection_graph_gated_v2_2026-06-02.md`
- Next-task review: `experiments/gan2026_next_task_review_month_bucket_gate_and_llm_heavy_v1_2026-06-02.md`
- LLM-heavy alternative: `experiments/gan2026_llm_heavy_extraction_protocol_2026-06-02.md`, `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_v0_validation25_error_analysis_2026-06-02.md`, `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation250_gpt41mini_v1_2026-06-02.md`
- LLM-heavy v2 decision smoke: `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation25_gpt41mini_v2_2026-06-02.md`
- LLM-heavy v2 error analysis: `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_v2_validation25_error_analysis_2026-06-02.md`
- LLM-heavy v2 compact rerun: `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_v2_compact_validation25_predeclaration_2026-06-02.md`, `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation25_gpt41mini_v2_compact_2026-06-02.md`
- Typed DSPy adapter architecture: `experiments/gan2026_dspy_adapter_architecture_report_2026-06-02.md`, `experiments/gan2026_llm_only_typed_adapter_reasoner_validation25_gpt41mini_v0_2026-06-02.md`
- LLM-replacement ablations: `experiments/gan2026_llm_replacement_postprocessing_ablation_design_2026-06-02.md`, `experiments/gan2026_llm_replacement_postprocessing_ablation_interpretation_2026-06-02.md`
- Saved-output replacement replay: `experiments/gan2026_llm_replacement_postprocessing_ablation_validation250_v0_2026-06-02.md`
- Full retrospective: `docs/research/gan2026_full_research_retrospective_2026-06-02.md`
- Retrospective HTML/PDF: `docs/research/gan2026_full_research_retrospective_2026-06-02.html`, `docs/research/gan2026_full_research_retrospective_2026-06-02.pdf`
- Prior LLM/hybrid comparators: `experiments/gan2026_section_claim_table_validation750_v4_interpretation_2026-06-01.md`, `experiments/gan2026_arch2_validation750_v01_interpretation_2026-06-01.md`, `experiments/gan2026_hybrid_adjudicator_v02_selective_action_report_2026-06-01.md`
- Saturated validation workflow: `docs/design/gan2026_saturated_validation_protocol.md`
- Local Ollama runbook: `docs/runbooks/windows_local_ollama.md`
- Model strategy: `docs/design/model_strategy.md`
- Review follow-up: `docs/research/codebase_thermonuclear_review_followup_2026-06-01.md`
- Intermediate schema/rationale synthesis: `docs/research/gan2026_intermediate_schema_report_2026-06-01.md`
- Simplified schema recommendation: `docs/research/gan2026_simplified_schema_recommendation_2026-06-01.md`
- Latest LLM-only v4 run/review: `experiments/gan2026_section_claim_table_validation250_gpt41mini_v4_schema_replay_2026-06-01.md`, `experiments/gan2026_section_claim_table_validation750_v4_interpretation_2026-06-01.md`
- Latest hybrid v0.1 run/reviews: `experiments/gan2026_arch2_validation250_gpt41mini_v01_schema_replay_2026-06-01.md`, `experiments/gan2026_arch2_validation250_v01_failure_review_2026-06-01.md`, `experiments/gan2026_arch2_validation750_v01_interpretation_2026-06-01.md`
- Hybrid v0.2 artifacts: `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation25_gpt41mini_v02_prompt_only_2026-06-01.md`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation25_v02_prompt_only_component_ablation_2026-06-01.md`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation25_gpt41mini_v02_live_2026-06-01.md`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation25_v02_live_component_ablation_2026-06-01.md`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation50_gpt41mini_v02_live_2026-06-01.md`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation50_v02_live_component_ablation_2026-06-01.md`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation250_gpt41mini_v02_live_2026-06-01.md`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation250_v02_live_component_ablation_2026-06-01.md`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation250_v02_audit_trail_interpretation_2026-06-01.md`, `experiments/gan2026_hybrid_adjudicator_v02_selective_action_report_2026-06-01.md`, `experiments/gan2026_hybrid_adjudicator_v02_validation_hard_slices_2026-06-01.json`
- Hybrid v0.2 saturated-surface plan: `experiments/gan2026_hybrid_adjudicator_v02_saturated_surface_evaluation_plan_2026-06-01.md`
- Qwen schema-contract risk: `docs/research/gan2026_qwen_schema_contract_risk_2026-06-01.md`

## Active Priorities

1. Keep deterministic V1 and hybrid v0.2 `cluster_diary_candidate_recall` frozen as comparators; do not tune gates or candidate rules from the locked-test audit.
2. Build the clinical frequency state graph as a diagnostic substrate before another final-label prompt.
3. Keep semantic repair, graph projection, scorer normalization, and production policy separately named, ablated, and claimed.
4. Treat saturated validation scores as low-information; prefer hard slices, selective-action profiles, graph invariance panels, and frozen generalization audits.
5. Separate benchmark gold-normalization policy from clinical reasoning while preserving source-near traces.

## Work Board

### Now

- If returning to v2, do a saved-output row-level review of
  `v2_compact` before any new prompt change; focus on rows 182, 187, 243, 280,
  and 338 and keep deterministic selected-evidence arithmetic side-car only.
- For typed-adapter work, do row-level artifact review before any v1 revision;
  focus on the 6 selected-evidence exactness failures, 3 raw parser-incompatible
  labels, and missing arithmetic traces without adding deterministic semantic
  replacement to the primary score layer.

### Next

- Reconsider validation50 only after a revised v2 validation25 smoke passes the
  decision 0006 output-contract, evidence, trace, raw-score, and
  deterministic-gap stop rules.
- Keep claim-table v5 and v0.2 schema/gate ablations available as comparators, but do not promote them ahead of the state-graph coverage cycle.
- Redesign `llm_heavy_clinical_frequency_reasoner_v2` only after the graph-gate
  and replacement-ablation plans are recorded; start any v2 at validation25.
- After the GPT-4.1 mini minimal-contract run is recorded, run the same
  `llm_only_minimal_evidence_selector` contract on
  `ollama_chat/qwen3.6:35b` at `http://localhost:11434` with `think=false`.
  Treat the Qwen run as a local-model transfer and output-contract diagnostic,
  not as holdout evidence.
- Keep claim-table v5 as the rich hosted-model/review comparator, but do not use
  it as the default Qwen contract until the minimal evidence selector has
  established whether Qwen can reliably emit strict JSON, answer state, and
  exact evidence under a smaller schema.
- Compare the minimal evidence selector against claim-table v5 on matched
  validation rows after the GPT-4.1 mini and Qwen minimal runs exist. The main
  comparison is contract transfer and evidence validity first, then Purist and
  Pragmatic score layers.
- Run claim-table v5 only after the raw/model, strict/schema repair, constrained-selector state, and clean scorer-facing policy ablations are ready.
- Extend the saturated-surface tooling with component-stress ablations over the hard panels once the synthetic hard-case JSONL panel is label-reviewed.
- Decide whether v0.2 needs stricter gate policy, a different adjudicator task, or rejection as added complexity over deterministic top; do not tune from locked-test row-level failures.
- Design LLM-replacement ablations for deterministic post-processing modules, reporting score, repair attribution, evidence validity, and replay variance.
- If Qwen passes the minimal validation1 contract, run minimal validation5
  before any validation25 smoke and compare only against the matched GPT-4.1
  mini minimal-contract baseline.
- Consolidate remaining saved-output replay helpers into dedicated artifact-analysis modules.
- Extend named repair-mode metadata beyond structured-events where downstream repair layers blur raw, strict, clean, selected-evidence, and hybrid attribution.

### Blocked

- Final benchmark-comparison language and further holdout analysis are blocked until replication comparability is explicit and locked-test discipline permits.
- Do not run LLM-only claim-table selector beyond 250 rows until v5 passes the 25/50 ladder and a written decision justifies another 250-row diagnostic.
- Qwen 3.6 full v5 claim-table validation ladder remains blocked until
  `ollama_chat/qwen3.6:35b` produces strict schema-compatible v5 output, or
  until a named Qwen schema-repair ablation is designed and reported
  separately. Endpoint/model identity is no longer the blocker. The minimal
  evidence-selector Qwen lane is not blocked by this v5-specific constraint.

### Done Recently

- 2026-06-02: Scaffolded and ran
  `llm_only_typed_adapter_reasoner_v0` as the separate DSPy `JSONAdapter`
  architecture requested by the adapter report. The live validation25 smoke
  used typed DSPy outputs with scoped `dspy.context(lm=..., adapter=JSONAdapter())`
  and produced 25/25 structured outputs, 0 adapter parse failures, 0 call
  failures, and 0 selected-event trace mismatches. It rejects validation50
  escalation because raw labels were 22/25 scorable, selected evidence was exact
  19/25, event evidence was exact 31/38, arithmetic traces were present 17/25,
  raw model-owned Purist was 22/25, and the 25/25 selected-evidence arithmetic
  score depended on a deterministic side-car with 3 raw-wrong corrections.
- 2026-06-02: Predeclared, implemented, and ran
  `llm_heavy_clinical_frequency_reasoner_v2_compact` validation25. The compact
  contract fixed the rejected v2 schema/truncation family with 25/25 structured
  outputs and 0 parse/schema failures, but decision 0006 still rejects
  validation50 escalation: raw model-owned Purist was 22/25, raw labels were
  23/25 scorable, selected evidence was exact 22/25, rendering operands/traces
  were 24/25, and deterministic selected-evidence arithmetic reached 25/25 only
  as a side-car with 3 raw-wrong corrections. Registry/index entries now point
  to the predeclaration, JSONL, and report.
- 2026-06-02: Implemented and ran
  `llm_heavy_clinical_frequency_reasoner_v2` validation25 under decision 0006.
  The report records raw, format-only, selected-evidence-arithmetic,
  benchmark-aligned, and oracle-format layers; selected evidence was exact
  22/25, selected-event trace mismatches were 0/25, raw Purist was 21/25, and
  deterministic selected-evidence arithmetic corrected 0 raw-wrong rows. The
  run rejects validation50 escalation because structured/scorable outputs,
  selected evidence, rendering operands, and arithmetic traces were only 22/25.
- 2026-06-02: Completed row-level error analysis for the rejected v2
  validation25 smoke. Six rows require attention: two missing
  `final_answer.selected_event_ids`, one invalid JSON truncation, two invalid
  non-selected administrative evidence events, and one true cluster-cadence
  selected-fact/semantics miss. The analysis keeps the result rejected and
  points the next prompt/schema revision at compactness and cluster semantics,
  not deterministic arithmetic replacement.
- 2026-06-02: Added the DSPy adapter architecture report. It records that the
  current repo uses opaque JSON-string DSPy outputs under the default adapter,
  recommends a separate `llm_only_typed_adapter_reasoner` architecture with
  typed outputs and scoped `JSONAdapter`, and preserves
  `llm_heavy_clinical_frequency_reasoner_v2` as a distinct prompt/schema
  redesign path.
- 2026-06-02: Added decision 0006, which predeclares the validation25
  LLM-owned selected-evidence arithmetic/rendering smoke for
  `llm_heavy_clinical_frequency_reasoner_v2`. It requires parser-ready raw model
  labels, exact selected evidence, auditable operands, zero selected-event trace
  mismatches, and a small deterministic-arithmetic gap before any validation50
  escalation.
- 2026-06-02: Added decision 0005 on benchmark-format rules versus LLM clinical
  reasoning. The note records that conventions such as bimonthly mapping and
  exact cluster rendering are often arbitrary gold-label choices rather than
  clinically important failures, and that teaching the model these conventions
  must be ablated for instruction overload and simple-row regressions before
  replacing explicit deterministic adapters.
- 2026-06-02: Implemented `llm_replacement_postprocessing_ablation` and ran the
  first no-call replay against the saved LLM-heavy v1 validation250 artifact.
  The runner emitted JSONL, JSON, Markdown, and registry/index metadata. The
  replay keeps raw/format-only Purist at 188/250, selected-evidence arithmetic
  at 219/250, benchmark alignment/full-stack at 204/250, selected evidence exact
  at 230/250, and trace mismatches at 9/250. It identifies
  selected-evidence arithmetic/rendering as the next LLM-owned replacement
  target and records a short interpretation note for v2 planning; no scorer,
  prompt, production policy, or holdout behavior changed.
- 2026-06-02: Recorded the LLM-replacement post-processing ablation design. The
  plan predeclares replacement targets for format/schema repair,
  selected-evidence arithmetic, benchmark alignment, state-graph node sources,
  projection/arbitration, and deterministic fallback; every replay must report
  score, repair attribution, evidence validity, replay variance, and hard-slice
  breakdown before LLM-heavy v2 prompt work resumes.
- 2026-06-02: Implemented and replayed graph-gated
  `month_bucket_duration_selection_graph_gated_v2` against the same 250-row
  validation hard-slice surface. The gate preserved 18/18 enriched duration
  corrections, left 0/232 broad-regression label changes, and blocked 46
  month-bucket replacements using graph metadata (`active_boundary_state_node`
  and `selected_rule_not_duration_normalization_v0`). This remains
  validation-only diagnostic evidence; no scorer, graph-builder, production
  projection policy, or holdout behavior changed.
- 2026-06-02: Completed the next-task review for the month-bucket broad
  regression rows and LLM-heavy v1 validation250 failures. A row-tag gate can
  block all four residual month-bucket changes without losing the 18 target
  corrections, but production promotion remains blocked on graph-metadata
  gating. LLM-heavy v1 remains rejected; v2 must address schema enum drift,
  evidence/trace discipline, raw-label grammar, bimonthly/compact intervals,
  cluster-axis preservation, vague counts, and conditional boundary answers.
- 2026-06-02: Completed the broader hard-slice family regression replay for
  gated `month_bucket_duration_selection_v1`. It preserved 18/18 enriched
  duration corrections and 0 exact-duration regressions; the 232-row regression
  panel had 4 changed labels, 0 already-correct regressions, 0
  frequency-with-seizure-free changes, and hidden-family accounting showing all
  four changes in cluster/diary plus temporal-conflict rows, with one
  unknown/no-reference boundary change. Decision remains revise-only; no
  scorer, graph-builder, production projection, or holdout change.
- 2026-06-02: Protocolized and tested the LLM-heavy track through v0
  validation25 and v1 validation50/250. v1 validation250 rejected promotion:
  13 parse/schema failures, 9 selected-event trace mismatches, raw/format-only
  Purist 188/250, and selected-evidence-arithmetic Purist 219/250 as
  diagnostic-only evidence-selection signal.
- 2026-06-02: Added the full research retrospective and rendered it as
  print-ready HTML/PDF for iPad markup.
- 2026-06-02: Completed the state-graph coverage, projection, boundary-state,
  accepted unknown8 replay, and seizure-free duration diagnostic cycle through
  validation-only artifacts. Coverage and duration-node construction are
  promising, but projection/arbitration remains the bottleneck and no production
  policy is promoted.
- 2026-06-02: Extended shared named repair-mode metadata from structured-events into claim-table score layers, hybrid adjudicator score layers, repair-family ablations, and component-ablation row attribution.
- 2026-06-02: Consolidated saved-output replay and artifact-ablation helpers into `gan2026/artifact_analysis`, leaving compatibility wrappers under `experiments/` and moving raw-output replay loading out of generic artifact writing helpers.
- 2026-06-02: Completed the hybrid v0.2 `cluster_diary_candidate_recall` frozen generalization audit. The result moved new development away from final-label prompt/gate tuning and toward validation-only semantic-state graph diagnostics.
- 2026-06-01: Completed the v0.2 hybrid adjudicator development cycle through validation25/50/250, saturated-surface analysis, synthetic hard-case component stress, row-level failure review, and named candidate-recall revision.
- 2026-06-01: Added intermediate-schema synthesis, saturated-validation workflow, cache-first LLM experiment CLI, cross-architecture component-ablation tooling, package-organization cleanup, and restored green Ruff, mypy, and full pytest after schema-repair and ownership-boundary work.
- 2026-06-01: Implemented v0.2 saturated-surface tooling and artifacts: JSON schemas for synthetic hard cases and validation hard slices, validation-only hard-slice generator, selective-action report over the saved validation250 v0.2 JSONL, 56-row synthetic hard-case panel draft, run-registry entry, and generated report showing raw changes 1 correction/2 regressions and gated changes 0 corrections/2 regressions.
- 2026-06-01: Ran the first hosted simplified-contract baseline on this
  device after verifying `.env` OpenAI API access with a GPT-4.1 mini
  LiteLLM smoke. `llm_only_minimal_evidence_selector_v0` validation25 live
  produced 25/25 minimal records, 0 call failures, 0 invalid JSON/schema
  failures, no alias repairs, answer evidence exact in 24/25 rows,
  supporting-fact evidence exact in 49/50 facts, raw minimal-answer
  Purist/Pragmatic 2/25, strict-format 15/25, frozen clean scorer-facing
  Purist/Pragmatic 16/25, and complete derived state/review projection for
  25/25 rows. Registered the run as
  `gan2026_minimal_evidence_selector_validation25_gpt41mini_v0_2026-06-01`.
- 2026-06-01: Added minimal evidence-selector validation25 error analysis
  comparing the run against claim-table v4/v5 and structured-events v0.5 on the
  same prefix. The main failure family is scorer-facing normalization:
  all 9 minimal clean failures are unscorable-after-clean rows, while the model
  usually selected the right source text.
- 2026-06-01: Added the simplified schema recommendation and implemented
  `llm_only_minimal_evidence_selector_v0`, a minimal model-boundary pipeline
  with `answer` plus `supporting_facts`, evidence diagnostics, raw/strict/clean
  score layers, alias repair for Qwen-like selector drift, derived diagnostic
  sidecars, report output, CLI registration, and focused tests.
- 2026-06-01: Completed the Qwen 3.6/Ollama setup lane: verified native Ollama `/api/chat`, switched DSPy/LiteLLM guidance to `ollama_chat/qwen3.6:35b` with `think=false`, rejected the `/v1` OpenAI-compatible route for Qwen reasoning models, added report provenance for native Ollama, recorded local hardware/model metadata, ran prompt-only v5 plus validation1 Qwen setup smoke, and registered the artifacts. The endpoint is unblocked; Qwen v5 remains blocked on strict JSON/schema adherence.
- 2026-06-01: Logged a Qwen schema-contract risk note explaining the validation1 failure mode: Qwen selected the clinically relevant `≤ four per day` claim but emitted Python-style single-quoted output, made `final_query` a string, and invented `final_selector`, so future Qwen ladders require prompt hardening or a named schema-repair ablation before metric interpretation.
- 2026-06-01: Added a hybrid adjudicator v0.2 saturated-surface evaluation plan covering synthetic hard cases, validation hard slices aligned to deterministic dominant errors, selective-action metrics, component-stress ablations, and frozen-test generalization audit criteria.
- 2026-06-01: Added a durable intermediate-schema synthesis report comparing rules-only V1, structured-events v0.5, claim-table v5, and hybrid adjudicator v0.2, with schema rationales, experiment lessons, ablation findings, and open questions.
- 2026-06-01: Added a hybrid adjudicator v0.2 audit-trail interpretation report: the LLM adds useful semantic dissent and review text, but not a trustworthy prediction-bearing final-selection layer on saturated validation250.
- 2026-06-01: Added saturated-validation workflow docs/skill after the v0.2 validation250 run showed broad aggregate comparisons are low-information once deterministic top is near ceiling; future saturated candidates should use hard cases, hard slices, selective-action analysis, or frozen test generalization audits.
- 2026-06-01: Ran hybrid rules-candidates LLM adjudicator v0.2 validation250 live signal and component ablation: 250/250 decision records, 0 call failures, 0 parse/schema failures, deterministic top 246/250 Purist and Pragmatic, raw adjudicator 245/250 Purist and 246/250 Pragmatic, conservative gated final 244/250 Purist and 245/250 Pragmatic, 9 raw label changes, 8 gated label changes, 1 fallback, 2 deterministic-correct regressions, and 0 deterministic-wrong corrections; mark v0.2 revise-only and do not treat broad validation250 as a useful next surface.
- 2026-06-01: Ran hybrid rules-candidates LLM adjudicator v0.2 validation50 live signal and component ablation; treat as saturated-prefix diagnostic now superseded by validation250.
- 2026-06-01: Rejected LLM-only claim-table selector v4 for holdout after full validation fell to 528/750 clean Purist despite stronger 250-row schema-replay results.
- 2026-06-01: Ran hybrid rules-candidates LLM adjudicator v0.2 validation25 live smoke: 25/25 decision records, 0 call failures, 0 blocking parse/schema failures, 25/25 Purist/Pragmatic for deterministic and gated final, 0 raw/gated label changes, and 1 non-blocking final-label repair note.
- 2026-06-01: Generated hybrid rules-candidates LLM adjudicator v0.2 validation25 prompt-only and component-ablation artifacts separating deterministic top, raw adjudicator, and conservative gated final before any live ladder run.
- 2026-06-01: Designed and implemented LLM-only claim-table selector v5 with explicit cluster-axis, boundary-state, and constrained-selector fields plus ablation-readiness metadata; no live ladder run was started.
- 2026-06-01: Designed and implemented hybrid rules-candidates LLM adjudicator v0.2 as a conservative gated adjudicator with deterministic fallback, raw-vs-gated score reporting, and component-ablation conditions.
- 2026-06-01: Completed hybrid rules-candidates LLM adjudicator v0.1 ladder and full-validation review; it clears 0.9000 in schema replay but regresses too many deterministic-correct rows to freeze.
- 2026-06-01: Added cross-architecture component-ablation tooling and the cache-first `gan2026-llm-experiment --pipeline ...` CLI.
- 2026-06-01: Restored green Ruff, mypy, and full pytest after schema-repair cleanup, broad-validation CLI gating, and task-neutral core-schema cleanup.
- 2026-06-01: Finished the codebase thermonuclear review follow-up with behavior-preserving ownership splits across deterministic extraction, selected-evidence derivation, LLM/hybrid parser/report modules, artifact IO, run metadata, registry reporting, and Gan package organization.

## Immediate Next Step

Run `gan2026-llm-experiment --pipeline llm_only_minimal_evidence_selector`
on `ollama_chat/qwen3.6:35b` with native Ollama chat and `think=false`,
starting with validation1 or validation5. In parallel, treat
`llm_only_typed_adapter_reasoner_v0` as a rejected adapter smoke that needs
row-level artifact review before any v1 revision; compare Qwen only against the
matched GPT-4.1 mini minimal baseline as a local-model transfer diagnostic.
