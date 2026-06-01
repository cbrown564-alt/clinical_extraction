# Gan 2026 Intermediate Schema Report

Date: 2026-06-01

This is a durable development research report for `gan2026_split_v1`. It
describes the intermediate schemas used by the major active seizure-frequency
pipelines, why each schema exists, what the experiments have taught us so far,
and what remains unresolved. It is not a held-out benchmark claim.

## Executive Summary

The active schema designs now expose four different hypotheses about how to
extract seizure frequency from Gan 2026 synthetic clinical letters:

1. `rules_only_v1`: deterministic rules emit candidate events, normalized
   events, and a final selection. This remains the strongest validation
   comparator and the cleanest evidence-span baseline.
2. `llm_only_structured_events` v0.5: the LLM emits source-near events and a
   clinical selection. Its raw/clean attribution is still well below threshold;
   high scores arrive only after substantial deterministic post-processing.
3. `llm_only_claim_table_selector` v5: the LLM emits a flat claim table plus a
   constrained final query with explicit `cluster_axis`, `boundary_state`, and
   `selector_decision` fields. This is the current LLM-first redesign after v4
   failed broad validation.
4. `hybrid_rules_candidates_llm_adjudicator` v0.2: deterministic rules generate
   candidate evidence, an LLM adjudicates the candidates, and conservative gates
   fall back to deterministic V1 when the adjudicator overreaches.

The central finding is architectural rather than merely metric-based:
intermediate schemas are doing real scientific work. They reveal where the
prediction-bearing decision lives, whether downstream code is only formatting or
is changing clinical meaning, and which error families require temporal,
cluster, boundary-state, or evidence-selection machinery. The strongest current
paper-facing claim is therefore a controlled hybrid claim, not a pure LLM-first
claim: source-near model extraction can provide inspectable evidence and
clinical state, while named deterministic modules perform ablated temporal,
cluster, diary, and benchmark-facing transformations.

## Active Pipeline Schema Inventory

### 1. Rules-Only V1 Deterministic Comparator

Primary code:
`src/clinical_extraction/tasks/seizure_frequency/gan2026/pipeline_v1.py`

The deterministic V1 schema is:

- `candidate_events`: raw evidence candidates extracted by named deterministic
  rules.
- `normalized_events`: Gan-compatible normalized labels derived from candidate
  labels.
- `final_selection`: the selected event, score, evidence, final label, and
  rationale.
- `evidence_valid`: whether final evidence is an exact substring of the note.

Representative shape:

```json
{
  "candidate_events": [
    {
      "event_id": "event_1",
      "kind": "cluster_frequency",
      "raw_value": "2 cluster per month, 6 per cluster",
      "evidence": "Cluster days twice this month; typically six seizures in 24 h",
      "rule_id": "cluster.rate_with_size",
      "rule_group": "cluster_arithmetic",
      "portability": "seizure_frequency",
      "match_groups": {
        "count": "twice",
        "period": "month",
        "per_cluster": "six"
      }
    }
  ],
  "normalized_events": [
    {
      "event_id": "event_1",
      "normalized_label": "2 cluster per month, 6 per cluster",
      "semantic_kind": "frequency",
      "monthly_frequency": 12.1667,
      "validation_errors": []
    }
  ],
  "final_selection": {
    "final_label": "2 cluster per month, 6 per cluster",
    "selected_event_ids": ["event_1"],
    "evidence": "Cluster days twice this month; typically six seizures in 24 h",
    "selected_score": {
      "semantic_priority": 4,
      "monthly_frequency_priority": 12.1667,
      "reason": "frequency_monthly_rate"
    }
  }
}
```

Rationale:

The V1 schema makes deterministic extraction auditable at the event level. It
records which rule family fired, the exact source span, the parsed groups, the
normalized label, and the final scoring decision. This is the best schema for
rule taxonomy, ablation, and regression testing.

Pros:

- Very transparent: every candidate carries `rule_id`, `rule_group`,
  `portability`, evidence, and parser groups.
- Strong validation performance: 697/750 Purist = 0.9293 and 704/750 Pragmatic
  = 0.9387 on validation.
- Perfect selected-evidence substring validity in validation ablations.
- Good scientific control surface for deterministic-rule ablations.

Cons:

- Validation success did not transfer cleanly to locked test: 0.7600 Purist and
  0.7867 Pragmatic on the one locked holdout evaluation.
- The schema exposes candidates but does not represent all competing clinical
  interpretations as richly as an LLM claim table can.
- New rules can easily become validation-specific if not kept under strict
  portability and ablation discipline.

Implication:

V1 should remain frozen as a comparator and candidate generator. It is too
useful to discard, but its test drop means it should not be used as evidence of
broad generalization without stronger replication controls.

### 2. LLM-Only Structured Events V0.5

Primary code:
`src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_only_structured_events.py`

The structured-events schema is:

- `events`: source-near model-extracted event facts.
- `selection`: model-selected final clinical answer over those events.
- `normalized_events`: deterministic normalization attached after model output.
- repair metadata in run artifacts, including parse errors and repair notes.

Event fields include:

- `event_id`
- `kind`: `frequency_rate`, `cluster_frequency`, `seizure_free`,
  `last_event_only`, `unknown_frequency`, `no_reference`
- `raw_value`
- `applies_to`
- `time_window`
- `temporality`
- `assertion_status`
- `evidence`
- `notes`

Selection fields include:

- `selected_event_ids`
- `final_kind`
- `final_label`
- `evidence`
- `confidence`
- `rationale`

Representative shape:

```json
{
  "structured_record": {
    "events": [
      {
        "event_id": "e2",
        "kind": "frequency_rate",
        "raw_value": "<= four per day",
        "time_window": "recent (current logs)",
        "temporality": "current",
        "assertion_status": "asserted",
        "evidence": "On the accommodation logs, the observed frequency is noted as <= four per day, with variable clustering"
      }
    ],
    "selection": {
      "selected_event_ids": ["e2"],
      "final_kind": "frequency",
      "final_label": "4 per day",
      "evidence": "On the accommodation logs, the observed frequency is noted as <= four per day, with variable clustering",
      "confidence": "high",
      "rationale": "The accommodation logs provide a precise current seizure frequency estimate."
    }
  },
  "normalized_events": [
    {
      "event_id": "e2",
      "normalized_label": "4 per day",
      "semantic_kind": "frequency",
      "monthly_frequency": 121.6667,
      "repair_applied": true,
      "validation_errors": []
    }
  ]
}
```

Rationale:

This schema tests whether the model can produce a compact clinical event record
and choose a benchmark-facing answer without deterministic V1 candidates in the
prompt. It is intended to separate evidence extraction, event typing, temporal
state, and final selection.

Pros:

- More clinically expressive than direct label output.
- Gives exact evidence spans and rationales for model decisions.
- Allows attribution ladders: raw model, strict format, clean scorer-facing,
  selected-evidence repair, and full hybrid stack.
- Useful substrate for deterministic repair experiments because selected
  evidence is retained.

Cons:

- Raw structured selection is weak on broad replay: 394/650 Purist = 0.6062.
- Clean scorer-facing normalization improves to only 438/650 = 0.6738 Purist.
- The threshold-passing result depends on repair-heavy hybrid behavior:
  588/650 = 0.9046 after selected-evidence derivation plus contextual temporal
  and event-state modules.
- The event schema can hide final-query ambiguity because the final selection
  still collapses cluster axis, boundary state, and temporal conflicts into one
  `final_label`.

Implication:

Structured events are valuable as evidence and state, but current high scores
should not be described as clean LLM-first performance. The schema works best as
the front end of a hybrid stack unless raw model selection improves
substantially.

### 3. LLM-Only Claim-Table Selector V5

Primary code:
`src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_only_claim_table_selector.py`

The v5 claim-table schema is:

- `claims`: flat source-near seizure-frequency claims.
- `final_query`: constrained model selection over the claims.
- explicit state fields for cluster and boundary decisions.

Claim fields include:

- `claim_id`
- `section`
- `claim_type`: `frequency`, `cluster_frequency`, `seizure_free`,
  `last_event_only`, `unknown_frequency`, `no_reference`,
  `non_seizure_event`
- `evidence`
- `anchor_text`
- `raw_frequency`
- `cluster_axis`: `none`, `cadence_only`, `burden_only`,
  `cadence_and_burden`, `vague_cluster`
- `boundary_state`: `ordinary_frequency`, `seizure_free_interval`,
  `unknown_frequency`, `no_frequency_reference`, `non_epileptic_or_proxy`,
  `last_event_only`, `conditional_or_window_limited`
- `temporality`
- `assertion_status`
- `semiology`
- `uncertainty`

Final-query fields include:

- `selected_claim_ids`
- `selector_decision`: `select_single_claim`, `combine_same_window_claims`,
  `preserve_cluster_axis`, `boundary_unknown`, `boundary_no_reference`,
  `boundary_seizure_free`, `unresolved_conflict`
- `answer_kind`
- `cluster_axis`
- `boundary_state`
- `raw_selected_frequency`
- `final_label`
- `conversion_note`
- `evidence`
- `confidence`
- `rationale`

Representative shape:

```json
{
  "structured_record": {
    "claims": [
      {
        "claim_id": "c1",
        "section": "Neurology Clinic assessment",
        "claim_type": "frequency",
        "evidence": "the charts and his account suggest a fluctuating pattern with brief episodes most days...",
        "raw_frequency": "<= four per day",
        "cluster_axis": "vague_cluster",
        "boundary_state": "ordinary_frequency",
        "temporality": "current",
        "assertion_status": "asserted",
        "semiology": "brief episodes with sudden behavioural arrest",
        "uncertainty": "medium"
      }
    ],
    "final_query": {
      "selected_claim_ids": ["c1"],
      "selector_decision": "select_single_claim",
      "answer_kind": "frequency",
      "cluster_axis": "vague_cluster",
      "boundary_state": "ordinary_frequency",
      "raw_selected_frequency": "<= four per day",
      "final_label": "4 per day",
      "conversion_note": "Converted <= four per day to 4 per day as maximum current burden.",
      "confidence": "medium"
    }
  }
}
```

Rationale:

V5 is a direct response to v4 full-validation errors. V4's flat claim table was
promising on the 250-row prefix, but full validation showed that the final query
collapsed cluster structure, boundary states, denominators, and active
semiology counts. V5 keeps the table but makes the selector state explicit so
the final label cannot silently hide why a row became unknown, no-reference,
seizure-free, ordinary frequency, or cluster frequency.

Pros:

- Best schema for human review of competing source-local claims.
- Explicit `cluster_axis` protects cadence versus per-cluster burden.
- Explicit `boundary_state` protects unknown/no-reference/seizure-free
  distinctions.
- `selector_decision` makes the final step ablatable.
- Good fit for future model-selector versus deterministic-selector comparisons
  over the same claim table.

Cons:

- V5 is still early. Its 25-row component ablation showed 22/25 Purist and
  22/25 Pragmatic with 2 parse/validation issues and 23/25 complete selector
  state, but that prefix is too small and too saturated for promotion.
- V4 broad validation was poor despite a strong 250-row prefix: clean Purist
  fell to 528/750 = 0.7040 and clean Pragmatic to 577/750 = 0.7693.
- A richer schema increases burden on the model to fill fields consistently.
- If downstream code starts doing deterministic semantic selection over the
  claim table, the architecture becomes hybrid and must be claimed as such.

Implication:

V5 is the most promising clean LLM-first schema direction, but not yet a strong
candidate. It should proceed through the 25/50/250 ladder with raw, strict,
constrained-selector, and clean scorer-facing ablations before any broad
validation run.

### 4. Hybrid Rules-Candidates LLM Adjudicator V0.2

Primary code:
`src/clinical_extraction/tasks/seizure_frequency/gan2026/hybrid/hybrid_rules_candidates_llm_adjudicator.py`

The hybrid adjudicator schema is:

- deterministic `candidate_events`, `normalized_events`, and
  `final_selection` from V1;
- model `decision_record`;
- `conservative_gate` result;
- component scores for deterministic top, raw adjudicator, and gated final.

Decision fields include:

- `assertion_status`
- `temporality`
- `seizure_or_event_target`
- `window`
- `normalized_rate`
- `uncertainty`
- `accepted_event_ids`
- `rejected_event_ids`
- `selected_event_ids`
- `final_label`
- `rationale`

Representative shape:

```json
{
  "deterministic_diagnostics": {
    "candidate_events": [
      {
        "event_id": "event_1",
        "kind": "frequency_rate",
        "raw_value": "4 per day",
        "evidence": "four per day",
        "rule_id": "rate.direct_count_per_period"
      }
    ],
    "normalized_events": [
      {
        "event_id": "event_1",
        "normalized_label": "4 per day",
        "semantic_kind": "frequency",
        "monthly_frequency": 121.6667
      }
    ],
    "final_selection": {
      "final_label": "4 per day",
      "selected_event_ids": ["event_1"],
      "evidence": "four per day"
    }
  },
  "decision_record": {
    "accepted_event_ids": ["event_1"],
    "rejected_event_ids": [],
    "selected_event_ids": ["event_1"],
    "temporality": "current",
    "assertion_status": "asserted",
    "normalized_rate": "4 per day",
    "final_label": "4 per day",
    "uncertainty": "low"
  },
  "conservative_gate": {
    "policy_version": "hybrid_adjudicator_conservative_v0.2",
    "deterministic_final_label": "4 per day",
    "raw_adjudicator_final_label": "4 per day",
    "final_label": "4 per day",
    "used_deterministic_fallback": false,
    "fired_gates": []
  }
}
```

Rationale:

This schema tests a targeted hybrid thesis: deterministic V1 provides a
high-recall candidate set, while the LLM audits whether the deterministic top
candidate should be accepted or changed. V0.2 adds conservative gates because
v0.1 changed too many deterministic-correct rows.

Pros:

- Very explicit attribution: deterministic top, raw LLM adjudicator, and gated
  final are scored separately.
- Strong output contract: validation250 live had 230/230 decision records,
  zero call failures, and zero parse/schema/label issues.
- Candidate-set recall can be measured directly.
- Conservative gate records why fallback happened.

Cons:

- The 250-row v0.2 run was still worse than deterministic top: deterministic
  top 227/230 Purist versus gated adjudicator 225/230 Purist.
- V0.1 full validation cleared the 0.9000 heuristic after schema replay
  (680/750 Purist), but underperformed deterministic top (697/750) by
  introducing 24 deterministic-correct regressions and only 7 corrections.
- Candidate-recall ceiling in v0.1 was only 707/750, leaving little room for a
  universal adjudicator unless it is nearly perfectly conservative.
- The LLM tends to choose plausible lower-priority candidates in some cases:
  lower recent subtype counts, longer-window aggregates, last-event-only rates,
  or seizure-free/boundary interpretations when current burden remains active.

Implication:

The hybrid adjudicator is scientifically useful, but the current form does not
justify replacing deterministic top. Its future value is likely as a narrow
overreach-family adjudicator with abstention and fallback, not as a general
selector over candidates.

## Cross-Schema Critical Analysis

### Transparency

All four schemas improve on direct label prediction, but they expose different
things:

- V1 exposes deterministic mechanism and exact rule provenance.
- Structured-events exposes model event typing and final evidence selection.
- Claim-table exposes multiple competing claims before final collapse.
- Hybrid adjudicator exposes how an LLM accepts, rejects, or overrides
  deterministic candidates.

The claim-table schema is the richest human-review surface. V1 is the strongest
machine-control surface. Structured-events is a useful middle ground, but its
final selection can still be too compact. Hybrid adjudication is the clearest
attribution surface when the question is whether the LLM improves a rules
baseline.

### Attribution

The experiments show why schema design and attribution cannot be separated.
Structured-events v0.5 reaches threshold only after deterministic modules change
or derive prediction-bearing labels. Without the ladder, the same artifact could
be misdescribed as LLM-first. With the ladder, the clean endpoint is visible:
438/650 Purist = 0.6738. The hybrid endpoint is also visible: 588/650 = 0.9046.

V5 claim-table was designed specifically to prevent this kind of hidden
semantic drift. Its `selector_decision`, `cluster_axis`, and `boundary_state`
fields preserve state that otherwise disappears into `final_label`.

### Generalization

The deterministic V1 validation/test gap is the strongest generalization
warning. Validation 0.9293 Purist versus locked test 0.7600 Purist means that
high validation scores can reflect synthetic-surface fit, not robust clinical
extraction. Richer schemas may help diagnose this, but they do not guarantee
generalization by themselves.

The LLM schemas may generalize better in principle because they preserve
source-near clinical state and can avoid hard-coded surface patterns. The
current evidence does not prove that yet. V4's collapse from 231/250 clean
Purist to 528/750 clean Purist is a second warning against over-reading small
prefixes.

### Error Localization

The schemas localize different failure modes:

- V1 localizes rule-family failures: portable rates, seizure-free/no-event
  assertions, clusters, diary aggregation, temporal selection, Gan shorthand.
- Structured-events localizes raw model selection versus repair-family effects.
- Claim-table localizes claim extraction, segmentation/sectioning,
  temporality/conflict, final query, parse/schema, and scorer-format failures.
- Hybrid adjudicator localizes candidate recall, raw adjudicator changes,
  deterministic-correct regressions, and conservative-gate fallbacks.

This is the strongest argument for keeping multiple schema surfaces alive during
development. Each one acts like a different microscope.

## Experiment Findings So Far

### Deterministic V1

Validation ablation findings:

| Disabled group | Purist | Delta vs baseline |
| --- | ---: | ---: |
| none | 0.9293 | baseline |
| portable rate expressions | 0.7627 | -0.1666 |
| seizure-free/no-event assertions | 0.8107 | -0.1186 |
| cluster arithmetic | 0.8600 | -0.0693 |
| diary log aggregation | 0.8507 | -0.0786 |
| temporal selection | 0.7787 | -0.1506 |
| Gan shorthand | 0.9027 | -0.0266 |
| benchmark repair | 0.9293 | 0.0000 |

Interpretation:

V1 is not one clever regex. Its validation performance depends on several
clinically meaningful rule families. Portable rate expressions and temporal
selection are especially load-bearing. Cluster arithmetic and diary aggregation
are smaller but still important. Benchmark repair is not carrying validation
score in this ablation, which helps separate scorer grammar from clinical
reasoning.

Validation error analysis:

- 53 Purist-incorrect rows.
- 81 scorer-correct semantic mismatches.
- Main failed operations: semantic state mapping, temporal selection, assertion
  classification, candidate extraction, cluster normalization, and seizure type
  selection.
- High-risk slices: medication/status context, ranges, uncertainty,
  historical-current distinctions, clusters, multiple seizure types, relative
  dates, and negation.

### Structured LLM V0.5

Grouped attribution ladder over 650 saved-output rows:

| Group | Claim class | Purist | Pragmatic | Interpretation |
| --- | --- | ---: | ---: | --- |
| Raw structured LLM selection | clean baseline | 394/650 = 0.6062 | 0.6338 | Model final label before repair |
| Clean scorer-facing normalization | clean attribution | 438/650 = 0.6738 | 0.7308 | Strict format plus frozen clean policy |
| Broad basic label repair bridge | hybrid bridge | 461/650 = 0.7092 | 0.7369 | Crosses clean boundary |
| Selected-evidence deterministic derivation | hybrid repair | 546/650 = 0.8400 | 0.8554 | Largest deterministic jump |
| Contextual temporal/event-state modules | hybrid repair | 588/650 = 0.9046 | 0.9200 | Full hybrid stack |

Interpretation:

The model is useful at finding evidence and producing inspectable events, but
the biggest performance movement comes after the clean LLM boundary. The
selected-evidence deterministic derivation module alone adds 85 Purist-correct
rows over the previous grouped condition. The final temporal/event-state stack
adds another 42. These are not incidental formatting improvements.

### Claim-Table V4 And V5

V4 250-row schema replay:

- Structured rows: 250/250.
- Exact claim evidence: 601/608.
- Exact selected final evidence: 249/250.
- Clean Purist: 231/250 = 0.9240.
- Clean Pragmatic: 238/250 = 0.9520.

V4 full validation:

- Raw final query: 512/750 Purist.
- Strict format: 516/750 Purist.
- Clean scorer-facing: 528/750 = 0.7040 Purist.
- Component failures: claim extraction 54, scorer format 44, final query 27,
  segmentation/sectioning 21, temporality/conflict 7, parse/schema 3.

V5 25-row component ablation:

- Raw, strict, constrained-selector, and clean layers all scored 22/25 Purist
  and 22/25 Pragmatic.
- 2 parse/validation issues.
- 23/25 rows had complete selector state.

Interpretation:

The claim-table idea improved inspectability, but v4 did not generalize across
validation. V5 is a schema repair, not yet a proven model improvement. Its
explicit cluster and boundary fields are well motivated by v4 failures, but the
current 25-row result is too small and saturated to read as success.

### Hybrid Adjudicator V0.1 And V0.2

V0.1 full validation schema replay:

- LLM adjudicator: 680/750 Purist = 0.9067.
- Deterministic top on same rows: 697/750 Purist = 0.9293.
- Candidate-recall ceiling: 707/750.
- LLM improved 7 deterministic misses but regressed 24 deterministic-correct
  rows.

V0.2 validation250 live artifact:

- Actually completed 230 rows in the saved report.
- Decision records: 230/230.
- Call failures: 0.
- Parse/schema/label issues: 0.
- Candidate-set Purist recall proxy: 227/230 = 0.9870.
- Deterministic top Purist: 227/230 = 0.9870.
- Gated adjudicator Purist: 225/230 = 0.9783.
- Changed final labels: 6.
- Deterministic-wrong to adjudicator-correct: 0.
- Deterministic-correct to adjudicator-wrong: 2.

Interpretation:

The conservative schema fixed output-contract risk but not the central utility
problem. On saturated prefixes, the LLM has little room to improve deterministic
top and still makes occasional harmful changes. The schema is still useful
because it identifies the exact transition families where adjudication fails.

## Pros, Cons, And Research Implications By Schema

| Schema | Best use | Main strength | Main risk |
| --- | --- | --- | --- |
| V1 candidates/normalization/selection | Frozen comparator and rule ablation | Transparent rule provenance and strong validation | Validation overfit and rule accretion |
| Structured events | LLM evidence/event extraction studies | Compact source-near model state | High scores depend on deterministic repair |
| Claim table v5 | LLM-first decomposition and error review | Explicit competing claims, cluster axis, boundary state | More model burden; not yet broad-validated |
| Hybrid adjudicator | Attribution of LLM over deterministic candidates | Separates deterministic top, raw LLM, gated final | Limited improvement room unless recall or gates improve |

The schemas should not be treated as interchangeable. Each supports a different
research claim:

- V1 supports "transparent deterministic comparator with ablatable rule
  families."
- Structured-events supports "LLM can produce useful source-near event state,
  but current threshold performance is hybrid."
- Claim-table v5 supports "LLM-first reasoning may become more inspectable if
  final selection state is decomposed."
- Hybrid adjudicator supports "LLM adjudication over rules is measurable, but
  must be conservative and targeted."

## Open Questions

1. Can v5 claim-table preserve its schema discipline at 50 and 250 validation
   rows, or will it repeat v4's broad-validation collapse?
2. Does a deterministic selector over the same v5 model claims outperform the
   model final query, and if so, how should the architecture be claimed?
3. Which hybrid adjudicator transition families are genuinely worth LLM review?
   Current evidence argues against a universal adjudicator.
4. Can candidate recall be improved without adding validation-specific
   deterministic rules that worsen holdout generalization?
5. Which schema fields are portable to non-Gan seizure-frequency extraction and
   which are benchmark artifacts?
6. Can clean LLM-first attribution move materially above 0.6738 Purist without
   semantic deterministic repair?
7. What evidence-validity threshold should be required before a model schema is
   considered interpretable enough for paper-facing examples?
8. How should scorer-correct semantic mismatches be reported when Purist and
   Pragmatic categories agree but clinical meaning differs?

## Recommended Next Steps

1. Keep `rules_only_v1` frozen and use it as comparator, candidate generator,
   and ablation control rather than adding casual rules.
2. Continue v5 claim-table through a disciplined 50-row ladder only after
   reviewing the 25-row parse/selector-state issues.
3. Add or run a selector ablation over v5 claims: model final query versus
   deterministic query over identical model claims.
4. For hybrid adjudication, stop treating the LLM as a universal selector.
   Define a short list of overreach families and test adjudication only there.
5. Keep reporting grouped attribution ladders for any repair stack. The clean
   endpoint and hybrid endpoint should always be separate.
6. Do not inspect or tune on test rows. The V1 validation/test gap makes this
   discipline especially important.

## Source Artifacts

- `PROJECT_STATUS.md`
- `docs/research/gan2026_current_pipeline_results_report_2026-06-01.md`
- `docs/research/gan2026_next_architecture_decision_2026-06-01.md`
- `experiments/gan2026_v1_validation_ablation_2026-05-31.md`
- `experiments/gan2026_v1_validation_error_analysis_2026-05-31.md`
- `experiments/gan2026_v1_test_holdout_2026-05-31.md`
- `experiments/gan2026_grouped_attribution_repair_ladder650_v0_2026-06-01.md`
- `experiments/gan2026_section_claim_table_validation250_gpt41mini_v4_schema_replay_2026-06-01.md`
- `experiments/gan2026_section_claim_table_validation750_v4_interpretation_2026-06-01.md`
- `experiments/gan2026_llm_only_claim_table_selector_validation25_v5_component_ablation_2026-06-01.json`
- `experiments/gan2026_arch2_validation750_v01_interpretation_2026-06-01.md`
- `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_validation250_gpt41mini_v02_live_2026-06-01.md`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/pipeline_v1.py`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_only_structured_events.py`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_only_claim_table_selector.py`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/hybrid/hybrid_rules_candidates_llm_adjudicator.py`
