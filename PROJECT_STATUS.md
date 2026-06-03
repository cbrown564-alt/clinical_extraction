# Project Status

Last updated: 2026-06-04

## Active Objective

Answer the Gan 2026 seizure-frequency component research questions one at a
time under exact-evidence, attribution, hidden-family, and split-discipline
constraints.

The first-pass RQ1/RQ2/RQ4 reports remain diagnostic baseline audits, but the
component-mechanics follow-up has now produced final validation-development
answers for those RQs. Active work moves to RQ5 without making any holdout or
benchmark-comparable claim.

## Current Strategy

Use saved artifacts as research instruments for clean component questions, not
whole-pipeline validation F1. Deterministic rules are frozen comparators, safety
floors, and miss-slice definers, not eligible answers for RQ1-RQ4.

Important context: hybrid safety-floor validation reached 697/750 Purist and
704/750 Pragmatic; local frozen `selective_safety_floor_gate_v0` improved
test450 from 343/450 to 351/450 Purist with 0 C->W. These remain development
or local-audit evidence, not LLM-first or benchmark claims.

## Active Question

RQ5. Deterministic Compilation/Rendering Over Fixed Selected State

Question: Given fixed candidate, evidence, selected-state, and gated projection
policy decisions, can the system render Gan-compatible labels without semantic
drift, benchmark-format leakage, or loss of exact evidence attribution?

Status: ready to protocol. RQ1/RQ2/RQ4 are now answered for
validation-development component mechanics; their claims remain validation-only
and do not authorize holdout-facing architecture promotion.

Core artifacts:
`docs/research/gan2026_llm_component_mechanics_protocol_2026-06-03.md`
`docs/research/gan2026_llm_component_mechanics_synthesis_2026-06-03.md`
`experiments/gan2026_llm_component_mechanics_rows_2026-06-03.md` and
`experiments/gan2026_llm_component_mechanics_rows_2026-06-03.jsonl`
`docs/research/gan2026_llm_component_mechanics_error_analysis_2026-06-03.md`
`docs/research/gan2026_llm_component_interpretation_policy_and_controlled_experiments_2026-06-03.md`
`experiments/gan2026_component_projection_followup_panel_2026-06-04.md`
`docs/research/gan2026_llm_component_mechanics_synthesis_2026-06-04.md`
`docs/research/gan2026_rq1_candidate_discovery_answer_2026-06-04.md`
`docs/research/gan2026_rq2_evidence_selection_answer_2026-06-04.md`
`docs/research/gan2026_rq4_projection_answer_2026-06-04.md`
`docs/research/gan2026_ambiguous_case_decision_log.md`
`docs/research/gan2026_target_rows_inspection.md`
`docs/research/gan2026_acd_projection_policy_predeclaration_2026-06-04.md`

## Guardrails

- Split `gan2026_split_v1` is locked: 300 train, 750 validation, 450 holdout.
  Validation is the development surface; locked test is not for row-level
  tuning.
- `rules_only_v1` remains the frozen transparent comparator.
- Treat saturated aggregate validation scores as low-information.
- Do not treat "deterministic top still wins" as an RQ1-RQ4 answer.
- Before promotion or LLM-superiority language, apply Decision 0008: component
  evidence matrix, exact changed-row evidence, LLM delta accounting,
  deterministic-correct regression accounting, and hidden-family breakdown.
- Broad validation or frozen-test work must answer the active component
  question, not maximize total score.
- Any holdout-facing use of LLM component conclusions needs a frozen
  predeclared audit or must keep the claim validation-only.
- Do not penalize projection-compatible phrases, faithful ambiguous facts, or
  multiple plausible candidates by default. Assign first-failure ownership
  before calling a row an LLM component failure.

## Work Board

### Now

- Write the RQ5 protocol for deterministic compilation/rendering over fixed
  selected states and explicit ACD projection-policy decisions.

### Next

- Run controlled single-task experiments for remaining owner/family slices only
  when they directly inform the RQ5 rendering protocol.
- Build the RQ5 rendering matrix with semantic-drift, benchmark-format,
  exact-evidence retention, and ACD-policy ablation fields.

### Backlog

- RQ3 schema comparison using selected evidence, sparse operands, typed operations, claim table, state graph, and possible boundary tags.
- RQ5 follow-up implementation after the rendering protocol is written.
- RQ9 abstention/coverage-accuracy protocol.
- RQ10 gold/scorer ambiguity audit.

### Blocked

- Benchmark-comparable language remains blocked; current holdout evidence is a local frozen audit only.
- Whole-pipeline architecture promotion is blocked until the relevant component questions are answered.

### Done Recently

- 2026-06-04: Wrote the final validation-development synthesis and final RQ
  answers for component mechanics: [RQ1 candidate generation](docs/research/gan2026_rq1_candidate_discovery_answer_2026-06-04.md),
  [RQ2 evidence selection](docs/research/gan2026_rq2_evidence_selection_answer_2026-06-04.md),
  [RQ4 projection](docs/research/gan2026_rq4_projection_answer_2026-06-04.md),
  and [combined synthesis](docs/research/gan2026_llm_component_mechanics_synthesis_2026-06-04.md).
  Final answers: broad LLM/graph replacement is negative; LLM candidate
  generation is selective boundary rescue only; LLM evidence components are
  exact-span/source-id support only; gated projection policies are accepted for
  named slices with 17/17 and 18/18 W->C, 0 C->W. Claims remain validation-only.
- 2026-06-04: Predeclared and implemented the production state-graph gated projection policies derived from **ACD-003 through ACD-010** in `docs/research/gan2026_acd_projection_policy_predeclaration_2026-06-04.md`, with one focused graph/projection test per ACD policy in `tests/test_gan2026_state_graph.py`. These remain validation-development projection policies, not benchmark claims.
- 2026-06-04: Catalogued and resolved all 11 backlog items of ambiguous representation cases in [gan2026_ambiguous_case_decision_log.md](file:///Users/cobro/code/clinical-extraction/docs/research/gan2026_ambiguous_case_decision_log.md) (decisions **ACD-003 through ACD-010**) and performed a detailed row-by-row clinical analysis of 16 target validation rows in [gan2026_target_rows_inspection.md](file:///Users/cobro/code/clinical-extraction/docs/research/gan2026_target_rows_inspection.md).
- 2026-06-04: Ran the frozen component-projection follow-up panel with interpretation policy applied (`experiments/gan2026_component_projection_followup_panel_2026-06-04.md`). Confirmed that gated projection rules achieved 100% precision on target slices with **0 regressions** (`boundary_state_priority` 17/17, `graph_gated_month_bucket` 18/18), while broad state graph projection and raw LLM selection caused severe regressions. Highlighted `projection_policy` as the single largest failure owner (152 rows).
- 2026-06-03: Cemented interpretation policy for the reset: projection-compatible clinical phrases, faithful ambiguous facts, and multiple plausible candidates are not LLM failures by default; added controlled experiment plan and deeper mechanism error analysis.
- 2026-06-03: Reset RQ1/RQ2/RQ4 interpretation and added the restart protocol, synthesis, and compact row artifact: 195 mechanism rows over 111 source rows. First-pass RQ reports remain source matrices but are downgraded as answers.
