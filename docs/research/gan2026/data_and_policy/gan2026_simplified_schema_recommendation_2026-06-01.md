# Gan 2026 Simplified Schema Recommendation

Date: 2026-06-01

This is a development research report for `gan2026_split_v1`. It uses the
current schema inventory, Qwen contract-risk note, design docs, and key
experiment reports to recommend a simpler model-output schema for the next
local-model and cross-model experiments. It is not a benchmark result.

## Executive Summary

The project has good reasons for the complex intermediate schemas it has built.
They expose clinical state, evidence provenance, deterministic repair, final
selection, and attribution boundaries that would otherwise be invisible. The
problem is that the richest schemas are now being used directly as model-output
contracts. That is increasingly risky, especially for local models.

The clearest recent example is the Qwen 3.6/Ollama validation1 smoke. Native
Ollama chat returned nonempty content and appeared to understand the clinical
fact, but failed the v5 claim-table contract: invalid JSON, `final_query` as a
string instead of an object, and an invented `final_selector` sibling. This was
not primarily a clinical reasoning failure. It was an interface failure.

The recommendation is to split the schema into two layers:

1. A small model-boundary schema that asks the model for selected evidence,
   answer state, answer text, and a few optional competing facts.
2. A rich derived diagnostic record produced by deterministic validators,
   normalizers, schema repair, evidence checks, and post-hoc annotators.

In short: keep the rich microscopes, but stop asking every model to assemble the
microscope.

## Core Principles From The Existing Design

The design docs point to a stable research contract:

- Deterministic rules and LLM reasoning are controlled variables, not hidden
  implementation detail.
- Event extraction, final clinical reasoning, normalization, evidence
  validation, scoring, and repair should remain separable.
- `unknown`, `no seizure frequency reference`, seizure-free, unresolved cluster
  states, and Gan scorer sentinels must remain semantically distinct before
  scoring collapse.
- Validation is the development surface; locked test is for frozen audits only.
- Aggregate Purist/Pragmatic score is insufficient without schema validity,
  evidence validity, row-change accounting, and repair attribution.

The simplified schema must not weaken those principles. Its purpose is to move
diagnostic complexity out of the raw model-output contract, not to erase it.

## What The Experiments Show

### Complex Schemas Are Scientifically Useful

The intermediate schema report shows why the existing schemas exist:

- `rules_only_v1` exposes rule IDs, rule groups, candidate events,
  normalized events, selected evidence, and final selection.
- `hybrid_structured_events` exposes source-near model events plus a model
  selection, then makes downstream repair measurable.
- `llm_only_claim_table_selector` exposes competing claim rows and final query
  state.
- `hybrid_rules_candidates_llm_adjudicator` exposes deterministic top, raw LLM
  adjudication, conservative gates, and fallback behavior.

These are valuable development records. They let reports say where the
prediction-bearing decision happened.

### Rich Model Contracts Are Fragile

The current evidence shows several failure modes:

| Experiment family | Contract signal | Interpretation |
| --- | ---: | --- |
| Structured LLM v0.5 grouped ladder, 650 rows | 140 raw parse/schema/label failures; 65 after clean scorer-facing normalization | The model can produce useful evidence, but raw structured selection is brittle and below threshold. |
| Claim-table v4, 250-row schema replay | 250/250 structured records, 0 parse/schema/label issues | GPT-4.1 mini can satisfy a complex contract on an optimistic prefix. |
| Claim-table v4, full validation | 3 parse/schema failures, clean Purist 528/750 = 0.7040 | Schema repair was not the main broad failure; representation and final query still collapsed. |
| Claim-table v5, validation250 | 248/250 structured records, 2 parse/schema/label issues, clean Purist 227/250 = 0.9080 | v5 improved GPT-4.1 mini contract and score, but still asks the model for many constrained fields. |
| Claim-table v5, frozen test audit sample | 150/150 structured records, 0 parse/schema/label issues, clean Purist 131/150 = 0.8733 | Hosted GPT can follow the contract under a frozen audit, but the result is not schema complexity proof for local models. |
| Qwen 3.6 validation1 smoke | 0/1 structured records, invalid JSON, wrong top-level shape | The same v5 contract can fail before clinical quality is measurable. |

The important pattern is not "schemas are bad." The pattern is that schema
burden and clinical burden are currently entangled. A model can understand the
row but fail the interface. A different model can follow the interface but still
make semantic selection errors.

### Most Remaining Errors Are Semantic, Not Pure Shape

The v4 full-validation failure slices were:

| Component | Failures |
| --- | ---: |
| claim_extraction | 54 |
| scorer_format | 44 |
| final_query | 27 |
| segmentation_sectioning | 21 |
| temporality_conflict | 7 |
| parse_schema | 3 |

The v5 validation250 failure slices were:

| Component | Failures |
| --- | ---: |
| segmentation_sectioning | 15 |
| claim_extraction | 9 |
| scorer_format | 8 |
| final_query | 4 |
| parse_schema | 2 |
| temporality_conflict | 1 |

This argues against solving the whole problem by adding more required enum
fields. Some explicit fields help expose errors, but each additional required
field is also another way for local models to fail before the clinical content
can be evaluated.

### Repair Is Acceptable, But It Must Be Named

The grouped structured-LLM ladder is the clearest attribution warning:

| Group | Purist | Interpretation |
| --- | ---: | --- |
| Raw structured LLM selection | 394/650 = 0.6062 | Model-selected final label before repair |
| Clean scorer-facing normalization | 438/650 = 0.6738 | Clean LLM-first endpoint |
| Broad basic repair bridge | 461/650 = 0.7092 | Crosses into hybrid behavior |
| Selected-evidence deterministic derivation | 546/650 = 0.8400 | Largest deterministic jump |
| Contextual temporal and event-state modules | 588/650 = 0.9046 | Full repair-heavy hybrid stack |

The simplified schema should embrace repair as a named layer. The model should
emit evidence and source-near answer state; deterministic code can then derive
labels, diagnose clusters, annotate boundary state, and produce scorer-facing
records under explicit ablation conditions.

## Recommended Architecture

Use a three-tier schema architecture.

### Tier 1: Minimal Model Contract

This is the only schema the model must produce. It should be valid JSON, shallow,
and tolerant of partial uncertainty.

```json
{
  "answer": {
    "state": "frequency",
    "answer_text": "<= four per day",
    "evidence": "On the accommodation logs, the observed frequency is noted as <= four per day, with variable clustering",
    "confidence": "medium",
    "reason": "This is the current observed seizure-frequency statement."
  },
  "supporting_facts": [
    {
      "fact_id": "f1",
      "role": "selected",
      "state": "frequency",
      "fact_text": "<= four per day",
      "evidence": "On the accommodation logs, the observed frequency is noted as <= four per day, with variable clustering"
    },
    {
      "fact_id": "f2",
      "role": "context",
      "state": "cluster_context",
      "fact_text": "variable clustering",
      "evidence": "with variable clustering"
    }
  ]
}
```

Required top-level fields:

- `answer`
- `supporting_facts`

Required `answer` fields:

- `state`
- `answer_text`
- `evidence`

Optional but encouraged `answer` fields:

- `confidence`
- `reason`

Required `supporting_facts` fields:

- `fact_id`
- `role`
- `state`
- `fact_text`
- `evidence`

Suggested small enums:

- `answer.state`: `frequency`, `cluster_frequency`, `seizure_free`,
  `unknown_frequency`, `no_frequency_reference`, `last_event_only`,
  `non_seizure_or_proxy`
- `supporting_facts.role`: `selected`, `competing`, `context`, `rejected`
- `supporting_facts.state`: same as `answer.state`, plus `cluster_context`

Deliberately remove these from the raw required model contract:

- `selector_decision`
- `cluster_axis`
- `boundary_state`
- `section`
- `anchor_text`
- `raw_frequency`
- `temporality`
- `assertion_status`
- `semiology`
- `uncertainty`
- nested `final_query`

Those concepts are still useful, but they should be derived, audited, or added
as optional fields after the base contract is stable across models.

### Tier 2: Derived Diagnostic Record

After parsing the minimal record, deterministic code should create a richer
diagnostic sidecar:

```json
{
  "model_record": "... minimal model output ...",
  "contract_diagnostics": {
    "raw_json_valid": true,
    "schema_valid": true,
    "repair_applied": false,
    "repair_policy": null,
    "extra_fields_seen": []
  },
  "evidence_diagnostics": {
    "answer_evidence_exact": true,
    "supporting_fact_evidence_exact": 2,
    "supporting_fact_evidence_total": 2
  },
  "derived_state": {
    "boundary_state": "ordinary_frequency",
    "cluster_axis": "vague_cluster",
    "temporality": "current",
    "assertion_status": "asserted",
    "selected_fact_ids": ["f1"]
  },
  "normalization": {
    "raw_selected_frequency": "<= four per day",
    "final_label": "4 per day",
    "semantic_kind": "frequency",
    "monthly_frequency": 121.6667,
    "normalization_policy": "frozen_clean_scorer_policy_v0"
  }
}
```

This preserves the v5 review surface without requiring the local model to fill
every review field correctly.

### Tier 3: Rich Review Projection

For apples-to-apples comparison with existing v5 artifacts, the derived
diagnostic record can be projected into a v5-like claim table:

- map `supporting_facts` to `claims`;
- map `answer` plus derived state to `final_query`;
- record which fields were model-emitted versus deterministically derived;
- score raw, repaired, and clean layers separately.

This projection is not the raw model output. Reports must call it a derived or
repaired view.

## Rationale

### 1. It Separates Interface Adherence From Clinical Quality

The Qwen smoke shows why this matters. A model that returns a clinically
reasonable `final_selector` but violates strict v5 shape should not be scored as
clinically incapable. The minimal schema gives local models fewer ways to fail
before their evidence choice and answer state can be measured.

### 2. It Keeps Evidence As The Central Audit Primitive

The strongest stable property across the successful schemas is evidence
traceability. V1 had 750/750 selected-evidence validity on validation. V5 had
246/250 exact selected final evidence substrings on validation250 and 145/150 on
the frozen test audit sample. The minimal schema keeps exact evidence mandatory.

### 3. It Reduces Enum Pressure

The v5 fields `cluster_axis`, `boundary_state`, and `selector_decision` are
excellent diagnostic fields for hosted GPT runs. They are also extra enum
commitments for local models. In the simplified schema, the model says the
answer state and evidence; deterministic annotators can then infer or mark
unknown for the richer axes.

### 4. It Preserves Attribution Boundaries

The architecture remains honest if reports separate:

- raw minimal model output;
- non-semantic JSON/shape repair;
- evidence validation;
- derived diagnostic annotation;
- scorer-facing label normalization;
- semantic deterministic repair modules.

This matches the contribution thesis better than forcing a local model to emit
a rich object and then silently repairing whatever shape it invents.

### 5. It Supports Both LLM-First And Hybrid Claims

If the final label comes from `answer.answer_text` plus clean scorer-facing
normalization, the claim can remain LLM-first. If deterministic code derives a
different label from selected evidence or overrides boundary state, the claim
becomes hybrid and should be ablated as such.

## What Not To Simplify Away

Do not remove these from experiment artifacts:

- raw model output text;
- exact evidence validity;
- parse/schema/label failure counts;
- raw versus repaired final labels;
- row-change counts by repair layer;
- semantic state before Gan scoring collapse;
- unknown versus no-reference distinction;
- cluster cadence versus per-cluster burden in derived diagnostics;
- model/runtime metadata, including local endpoint and thinking-mode settings;
- validation ladder stage and escalation reason.

The simplification is at the model boundary only.

## Suggested Experiment Plan

### Stage 0: Schema Definition

Create a new pipeline or schema version, for example:

`llm_only_minimal_evidence_selector_v0`

Claim type:

`llm_first` for raw answer selection, unless downstream semantic derivation is
enabled.

Prediction-bearing component:

The model-produced `answer` object.

Allowed clean layers:

- JSON parsing and strict schema validation;
- exact evidence substring validation;
- non-semantic key alias repair, if explicitly named;
- frozen clean scorer-facing normalization over `answer.answer_text`.

Named hybrid layers:

- selected-evidence deterministic derivation;
- cluster-axis reconstruction;
- boundary-state override;
- temporal/event-state modules;
- deterministic selector over supporting facts.

### Stage 1: Qwen Validation1 Contract Rescue

Run Qwen on one validation row under three named conditions:

1. `qwen_minimal_prompt_strict_json`
2. `qwen_minimal_schema_repair_alias_only`
3. `qwen_minimal_json_mode_or_constrained_decode`, if available locally

Promotion criterion:

- nonempty assistant content;
- valid JSON or explicitly repaired JSON;
- valid minimal schema;
- exact answer evidence substring;
- raw/repaired distinction recorded.

Do not run validation25 until validation1 passes contract health.

### Stage 2: Cross-Model Validation25

Run the same minimal schema on GPT-4.1 mini and Qwen.

Report:

- call failures;
- invalid JSON;
- schema failures;
- invented top-level fields;
- evidence validity;
- raw final-label score;
- strict-format score;
- clean scorer-facing score;
- derived diagnostic completeness;
- changed rows by repair layer.

The primary question is contract transfer, not aggregate F1.

### Stage 3: Compare Against V5 On The Same Rows

On validation25 and validation50, compare:

- v5 raw claim table;
- minimal raw answer;
- minimal plus derived diagnostics;
- minimal plus selected-evidence deterministic derivation, if enabled.

This determines whether the extra v5 fields improve selection enough to justify
their contract cost.

### Stage 4: Only Then Consider Validation250

Escalate only if the 50-row result has no systemic schema failure family and
the report states what the 250-row run will decide.

## Reporting Template For The New Schema

Every artifact should include this table:

| Layer | Contract class | Purist | Pragmatic | JSON/schema failures | Evidence exact | Rows changed |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| raw minimal answer | clean attribution baseline |  |  |  |  |  |
| alias/JSON repair only | non-semantic repair |  |  |  |  |  |
| frozen clean scorer policy | clean attribution |  |  |  |  |  |
| derived diagnostic projection | diagnostic sidecar |  |  |  |  |  |
| selected-evidence derivation | hybrid repair |  |  |  |  |  |

And this transition table:

| Transition | Count |
| --- | ---: |
| raw correct to final correct |  |
| raw wrong to final correct |  |
| raw wrong to final wrong |  |
| raw correct to final wrong |  |

## Recommendation

Adopt the minimal evidence-selector schema as the next local-model transfer
interface. Keep v5 as the richer hosted-model and review comparator, but stop
treating v5 as the default contract for Qwen until Qwen passes a smaller JSON
contract ladder.

The project should frame this as a schema-boundary experiment:

> Can a local model reliably emit the answer state and exact evidence under a
> small contract, while deterministic sidecars recover the diagnostic fields
> needed for attribution and error analysis?

This is a better immediate question than asking whether Qwen can satisfy the
full v5 claim-table selector. The full v5 contract is useful, but for local
models it currently confounds schema adherence with clinical extraction quality.

## Source Artifacts

- ``
- ``
- ``
- ``
- ``
- ``
- ``
- `docs/research/contribution_thesis.md`
- `docs/design/architecture.md`
- `docs/design/data_contract.md`
- `docs/design/model_strategy.md`
- `docs/design/gan2026_pipeline_v1.md`
- `docs/design/gan2026_split_protocol.md`
- `docs/design/gan2026_saturated_validation_protocol.md`
- `docs/design/gan2026_normalization_semantics.md`
- `docs/design/deterministic_rule_catalogue_plan.md`
- `experiments/gan2026_v1_validation_error_analysis_2026-05-31.md`
- `experiments/gan2026_grouped_attribution_repair_ladder650_v0_2026-06-01.md`
- `experiments/gan2026_section_claim_table_validation250_gpt41mini_v4_schema_replay_2026-06-01.md`
- `experiments/gan2026_section_claim_table_validation750_v4_interpretation_2026-06-01.md`
- `experiments/gan2026_llm_only_claim_table_selector_validation25_v5_component_ablation_2026-06-01.json`
- `experiments/gan2026_llm_only_claim_table_selector_validation50_v5_max2400_component_ablation_2026-06-01.md`
- `experiments/gan2026_llm_only_claim_table_selector_validation250_gpt41mini_v5_max2400_2026-06-01.md`
- `experiments/gan2026_llm_only_claim_table_selector_validation250_v5_max2400_component_ablation_2026-06-01.md`
- `experiments/gan2026_llm_only_claim_table_selector_test450_gpt41mini_v5_max2400_2026-06-01.md`
- `experiments/gan2026_llm_only_claim_table_selector_validation1_qwen36_35b_v5_ollama_chat_smoke_2026-06-01.md`
- `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation250_gpt41mini_v02_live_2026-06-01.md`
