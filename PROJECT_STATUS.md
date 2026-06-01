# Project Status

Last updated: 2026-06-01

## Active Objective

Build a Gan 2026 seizure-frequency extraction pipeline that can reach at least
0.9000 Purist F1 on development surfaces while preserving transparent evidence
trails, ablations, and conservative benchmark language.

## Current Strategy

Use Gan 2026 as the first controlled extraction surface. Keep deterministic V1 frozen as `rules_only_v1`; organize experiments by `rules_only`, `llm_only`, and `hybrid`; require each LLM/hybrid candidate to name component order, semantic ownership, repair boundaries, and ablation surfaces before holdout use.

## Recent Context

- Locked split `gan2026_split_v1`: 300 train, 750 validation, 450 holdout. LLM/DSPy work escalates 25 -> 50 -> 250 validation rows; test is not tuning.
- Deterministic V1 is the frozen comparator: 0.9293/0.9387 validation and
  0.7600/0.7867 on its one locked-test Purist/Pragmatic evaluation.
- Structured v0.5 reached 675/750 Purist = 0.9000 on full validation, but audit
  classified it as repair-heavy hybrid behavior rather than clean LLM-first.
- LLM-only claim-table selector v4 reached 231/250 clean Purist after schema replay, but full validation collapsed to 528/750 clean Purist and 577/750 clean Pragmatic. Reject v4 for holdout; redesign v5 around cluster-axis preservation, boundary-state selection, and selector ablation.
- Hybrid rules-candidates LLM adjudicator v0.1 reached 243/250 Purist and 244/250 Pragmatic on 250-row schema replay, then 680/750 Purist and 689/750 Pragmatic on full validation. It underperformed deterministic top on the same rows (697/750 Purist) because the adjudicator introduced 24 deterministic-correct regressions against 7 corrections. V0.2 validation250 live was output-contract clean but low-information on a saturated surface: deterministic top was already 246/250 Purist and Pragmatic; raw adjudicator was 245/250 Purist and 246/250 Pragmatic; conservative gated final was 244/250 Purist and 245/250 Pragmatic. The follow-up saturated-surface analysis confirmed weak prediction-bearing utility: raw changes had 1 correction and 2 regressions; gated changes had 0 corrections and 2 regressions. Treat v0.2 as revise-only and switch future saturated comparisons to hard-case panels, validation hard slices, selective-action analysis, or frozen test generalization audits.
- Reviewed synthetic hard-case component stress for hybrid adjudicator v0.2 is complete on 56 rows. Deterministic top scored 39/56 Purist, raw adjudicator 44/56, and conservative gated final 42/56; raw changes produced 5 wrong-to-correct and 0 correct-to-wrong, while gates retained 3 wrong-to-correct and 0 correct-to-wrong. Candidate recall was only 42/56 and 5 rows had schema/validation failures, so this remains revise-only. Useful signal clusters in temporal-conflict and shorthand-range cases; cluster/diary and proxy/boundary behavior needs candidate-generation and schema/gate follow-up.
- Named hybrid v0.2 `cluster_diary_candidate_recall` is implemented outside frozen deterministic V1 and rerun on the same 56-row synthetic hard-case panel. Candidate recall improved to 50/56; raw adjudicator reached 52/56 Purist with 13 wrong-to-correct and 0 correct-to-wrong; conservative gated final reached 50/56 Purist with 11 wrong-to-correct and 0 correct-to-wrong. The branch fixed all targeted cluster/diary recall misses, but remains synthetic/revise-only; remaining misses are seizure-free boundary, shorthand, proxy/boundary gate, and one schema-output row.
- Routine LLM experiments use cache-first `gan2026-llm-experiment --pipeline ...`; saved-output replay is reserved for explicit offline artifact analysis.
- Clean scorer-facing normalization is frozen unless direct-citation review justifies another family. Shared schema repair is alias-only; parser defaults belong to their task parser.
- The codebase thermonuclear review follow-up is complete: the Gan package now has stable ownership boundaries under `contract/`, `deterministic/`, `selected_evidence/`, `llm/`, `hybrid/`, `reports/`, `experiments/`, and `cli/`, while preserving public contracts and scorer behavior.
- Phase 6 run-registry scaffolding is active: `experiments/registry.jsonl` is canonical, and `experiments/RUN_INDEX.md` is the human scan surface.

## Key References

- Protocol/control: `docs/design/gan2026_split_protocol.md`, `docs/design/data_contract.md`
- Package organization: `docs/decisions/0004-gan2026-package-organization.md`
- Run registry: `experiments/registry.jsonl`, `experiments/RUN_INDEX.md`
- Saturated validation workflow: `docs/design/gan2026_saturated_validation_protocol.md`
- Review follow-up: `docs/research/codebase_thermonuclear_review_followup_2026-06-01.md`
- Intermediate schema/rationale synthesis: `docs/research/gan2026_intermediate_schema_report_2026-06-01.md`
- Latest LLM-only v4 run/review: `experiments/gan2026_section_claim_table_validation250_gpt41mini_v4_schema_replay_2026-06-01.md`, `experiments/gan2026_section_claim_table_validation750_v4_interpretation_2026-06-01.md`
- Latest hybrid v0.1 run/reviews: `experiments/gan2026_arch2_validation250_gpt41mini_v01_schema_replay_2026-06-01.md`, `experiments/gan2026_arch2_validation250_v01_failure_review_2026-06-01.md`, `experiments/gan2026_arch2_validation750_v01_interpretation_2026-06-01.md`
- Hybrid v0.2 artifacts: `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation25_gpt41mini_v02_prompt_only_2026-06-01.md`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation25_v02_prompt_only_component_ablation_2026-06-01.md`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation25_gpt41mini_v02_live_2026-06-01.md`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation25_v02_live_component_ablation_2026-06-01.md`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation50_gpt41mini_v02_live_2026-06-01.md`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation50_v02_live_component_ablation_2026-06-01.md`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation250_gpt41mini_v02_live_2026-06-01.md`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation250_v02_live_component_ablation_2026-06-01.md`, `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation250_v02_audit_trail_interpretation_2026-06-01.md`, `experiments/gan2026_hybrid_adjudicator_v02_selective_action_report_2026-06-01.md`, `experiments/gan2026_hybrid_adjudicator_v02_validation_hard_slices_2026-06-01.json`, `experiments/gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_component_stress_2026-06-01.md`, `experiments/gan2026_hybrid_adjudicator_v02_synthetic_hard_cases_failure_review_2026-06-01.md`, `experiments/gan2026_hybrid_adjudicator_v02_cluster_diary_candidate_recall_synthetic_hard_cases_component_stress_2026-06-01.md`
- Hybrid v0.2 saturated-surface plan: `experiments/gan2026_hybrid_adjudicator_v02_saturated_surface_evaluation_plan_2026-06-01.md`

## Active Priorities

1. Keep deterministic V1 frozen; put new deterministic behavior into named, ablated candidates.
2. Enforce the architecture gate before the metric gate; semantic repair and hybrid overreach gates need separate naming, ablation, and claim language.
3. Treat saturated validation scores as low-information; prefer hard cases, hard slices, selective-action profiles, and frozen generalization audits over more broad validation250 aggregates.
4. Separate benchmark gold-normalization policy from clinical reasoning while preserving source-near traces.
5. Keep runners cache-first and live-run oriented; move replay/retention analysis into explicit artifact-analysis modules.

## Work Board

### Now

- Generate claim-table v5 component-ablation artifacts before any 25/50/250 validation ladder; v5 now uses claim-table plus constrained selector state with cluster-axis and boundary-state fields.

### Next

- Run claim-table v5 only after the raw/model, strict/schema repair, constrained-selector state, and clean scorer-facing policy ablations are ready.
- Keep v0.2 schema enum repair, shorthand/seizure-free recall, and proxy/boundary gate relaxation as separate named ablations; do not mix them into the cluster/diary candidate-recall revision.
- Decide whether v0.2 should stay as a broader candidate-selection layer after the cluster/diary branch improved the synthetic hard panel, or narrow to recalled-candidate temporal/cluster/diary adjudication before any validation hard-slice follow-up.
- Design LLM-replacement ablations for deterministic post-processing modules, reporting score, repair attribution, evidence validity, and replay variance.
- Consolidate remaining saved-output replay helpers into dedicated artifact-analysis modules.
- Extend named repair-mode metadata beyond structured-events where downstream repair layers blur raw, strict, clean, selected-evidence, and hybrid attribution.

### Blocked

- Final benchmark-comparison language and further holdout analysis are blocked until replication comparability is explicit and locked-test discipline permits.
- Do not run LLM-only claim-table selector beyond 250 rows until v5 passes the 25/50 ladder and a written decision justifies another 250-row diagnostic.

### Done Recently

- 2026-06-01: Implemented named hybrid v0.2 `cluster_diary_candidate_recall` outside frozen deterministic V1 and reran the same 56-row synthetic hard-case component stress live. Candidate recall improved from 42/56 to 50/56; raw adjudicator improved from 44/56 to 52/56 Purist with 13 corrections and 0 regressions; conservative gated final improved from 42/56 to 50/56 Purist with 11 corrections and 0 regressions. Remaining misses are outside this branch: seizure-free boundary, shorthand, proxy/boundary gate, and one schema-output row.
- 2026-06-01: Reviewed v0.2 synthetic component-stress failures row by row and chose cluster/diary candidate-generation recall as the single next revision target. Schema failures are mostly enum hygiene, temporal-conflict is the cleanest adjudicator win, and two proxy boundary corrections are blocked by `unsupported_boundary_demotion_overreach`; keep those as separate named ablations.
- 2026-06-01: Ran approved hybrid adjudicator v0.2 synthetic hard-case component stress on 56 rows: deterministic top 39/56 Purist, raw adjudicator 44/56 with 5 corrections and 0 regressions, conservative gated final 42/56 with 3 corrections and 0 regressions, candidate recall 42/56, and 5 schema/validation failures; mark diagnostic/revise-only.
- 2026-06-01: Implemented v0.2 saturated-surface tooling and artifacts: JSON schemas for synthetic hard cases and validation hard slices, validation-only hard-slice generator, selective-action report over the saved validation250 v0.2 JSONL, 56-row synthetic hard-case panel draft, run-registry entry, and generated report showing raw changes 1 correction/2 regressions and gated changes 0 corrections/2 regressions.
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

Interpret whether `cluster_diary_candidate_recall` should be paired with a narrow recalled-candidate adjudicator role or followed by a separate proxy/boundary gate ablation. Do not inspect holdout rows unless the candidate and analysis policy are frozen first.
