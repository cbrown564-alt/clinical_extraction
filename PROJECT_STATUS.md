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
- Hybrid rules-candidates LLM adjudicator v0.1 reached 243/250 Purist and 244/250 Pragmatic on 250-row schema replay, then 680/750 Purist and 689/750 Pragmatic on full validation. It underperformed deterministic top on the same rows (697/750 Purist) because the adjudicator introduced 24 deterministic-correct regressions against 7 corrections. V0.2 is now designed as a conservative gated adjudicator with deterministic fallback; do not run its 25/50/250 ladder until the component-ablation artifact is generated with deterministic top, raw LLM, and gated-final conditions.
- Routine LLM experiments use cache-first `gan2026-llm-experiment --pipeline ...`; saved-output replay is reserved for explicit offline artifact analysis.
- Clean scorer-facing normalization is frozen unless direct-citation review justifies another family. Shared schema repair is alias-only; parser defaults belong to their task parser.
- The codebase thermonuclear review follow-up is complete: the Gan package now has stable ownership boundaries under `contract/`, `deterministic/`, `selected_evidence/`, `llm/`, `hybrid/`, `reports/`, `experiments/`, and `cli/`, while preserving public contracts and scorer behavior.
- Phase 6 run-registry scaffolding is active: `experiments/registry.jsonl` is canonical, and `experiments/RUN_INDEX.md` is the human scan surface.

## Key References

- Protocol/control: `docs/design/gan2026_split_protocol.md`, `docs/design/data_contract.md`
- Package organization: `docs/decisions/0004-gan2026-package-organization.md`
- Run registry: `experiments/registry.jsonl`, `experiments/RUN_INDEX.md`
- Review follow-up: `docs/research/codebase_thermonuclear_review_followup_2026-06-01.md`
- Latest LLM-only v4 run/review: `experiments/gan2026_section_claim_table_validation250_gpt41mini_v4_schema_replay_2026-06-01.md`, `experiments/gan2026_section_claim_table_validation750_v4_interpretation_2026-06-01.md`
- Latest hybrid v0.1 run/reviews: `experiments/gan2026_arch2_validation250_gpt41mini_v01_schema_replay_2026-06-01.md`, `experiments/gan2026_arch2_validation250_v01_failure_review_2026-06-01.md`, `experiments/gan2026_arch2_validation750_v01_interpretation_2026-06-01.md`

## Active Priorities

1. Keep deterministic V1 frozen; put new deterministic behavior into named, ablated candidates.
2. Enforce the architecture gate before the metric gate; semantic repair and hybrid overreach gates need separate naming, ablation, and claim language.
3. Treat hybrid adjudicator v0.1 and LLM-only claim-table selector v4 as revise signals, not holdout candidates.
4. Separate benchmark gold-normalization policy from clinical reasoning while preserving source-near traces.
5. Keep runners cache-first and live-run oriented; move replay/retention analysis into explicit artifact-analysis modules.

## Work Board

### Now

- Generate a v0.2 prompt-only/smoke artifact and component-ablation report that separates deterministic top, raw LLM adjudicator, and conservative gated final before any 25/50/250 validation ladder.
- Generate claim-table v5 component-ablation artifacts before any 25/50/250 validation ladder; v5 now uses claim-table plus constrained selector state with cluster-axis and boundary-state fields.

### Next

- Run claim-table v5 only after the raw/model, strict/schema repair, constrained-selector state, and clean scorer-facing policy ablations are ready.
- Design LLM-replacement ablations for deterministic post-processing modules, reporting score, repair attribution, evidence validity, and replay variance.
- Consolidate remaining saved-output replay helpers into dedicated artifact-analysis modules.
- Extend named repair-mode metadata beyond structured-events where downstream repair layers blur raw, strict, clean, selected-evidence, and hybrid attribution.

### Blocked

- Final benchmark-comparison language and further holdout analysis are blocked until replication comparability is explicit and locked-test discipline permits.
- Do not run LLM-only claim-table selector beyond 250 rows until v5 passes the 25/50 ladder and a written decision justifies another 250-row diagnostic.

### Done Recently

- 2026-06-01: Rejected LLM-only claim-table selector v4 for holdout after full validation fell to 528/750 clean Purist despite stronger 250-row schema-replay results.
- 2026-06-01: Designed and implemented LLM-only claim-table selector v5 with explicit cluster-axis, boundary-state, and constrained-selector fields plus ablation-readiness metadata; no live ladder run was started.
- 2026-06-01: Designed and implemented hybrid rules-candidates LLM adjudicator v0.2 as a conservative gated adjudicator with deterministic fallback, raw-vs-gated score reporting, and component-ablation conditions.
- 2026-06-01: Completed hybrid rules-candidates LLM adjudicator v0.1 ladder and full-validation review; it clears 0.9000 in schema replay but regresses too many deterministic-correct rows to freeze.
- 2026-06-01: Added cross-architecture component-ablation tooling and the cache-first `gan2026-llm-experiment --pipeline ...` CLI.
- 2026-06-01: Restored green Ruff, mypy, and full pytest after schema-repair cleanup, broad-validation CLI gating, and task-neutral core-schema cleanup.
- 2026-06-01: Finished the codebase thermonuclear review follow-up with behavior-preserving ownership splits across deterministic extraction, selected-evidence derivation, LLM/hybrid parser/report modules, artifact IO, run metadata, registry reporting, and Gan package organization.

## Immediate Next Step

Create the validation-only v0.2 ablation artifact first, then decide whether to run the 25-row live smoke. Do not inspect holdout rows.
