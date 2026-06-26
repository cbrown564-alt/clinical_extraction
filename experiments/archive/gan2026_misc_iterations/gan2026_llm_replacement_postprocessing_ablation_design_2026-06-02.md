# Gan 2026 LLM-Replacement Post-Processing Ablation Design

Date: 2026-06-02

Diagnostic only: this is a predeclared validation-cycle ablation plan. It does
not change the scorer, deterministic V1, state-graph builder, projection policy,
prompt text, locked-test behavior, or benchmark claim language.

## Experiment Unit

- Hypothesis: several strong Gan 2026 scores depend on deterministic
  post-processing modules that are acting as prediction-bearing clinical
  interpreters. Before another LLM-heavy v2 prompt run, each module should be
  replaced, removed, or isolated so score gains can be attributed to either
  model reasoning, deterministic graph construction, projection, or
  benchmark-facing repair.
- Minimal change under test: create no-call ablation runners over saved
  validation artifacts that swap one deterministic post-processing layer at a
  time for an LLM-owned, null, or oracle condition. The first artifact should be
  an analysis replay, not a live model run.
- Data surface: validation-only `gan2026_split_v1` hard panels. Start with
  existing 250-row hard-slice union plus the LLM-heavy v1 validation250 failure
  rows; do not use train or locked test.
- Scorer: Gan-compatible Purist F1 as the primary score, Pragmatic F1 as a
  side-car, exact-label match for duration-specific rows, plus repair,
  evidence, and replay-variance accounting.
- Comparators: frozen `rules_only_v1`, rejected
  `llm_heavy_clinical_frequency_reasoner_v1`, diagnostic
  `hybrid_clinical_frequency_state_graph`, and claim-table v5 only as
  comparator/complementarity sources.
- Decision: keep as diagnostic unless the ablation separates prediction-bearing
  ownership cleanly enough to justify a subsequent validation25 LLM-heavy v2
  redesign.

## Replacement Targets

| Target layer | Existing role | Replacement ablation | Required attribution |
| --- | --- | --- | --- |
| `strict_format` / schema repair | Makes saved model output parseable. | Raw model only, format-only aliases, and null-on-parse-failure. | Parse failures, raw scorable rows, format-only corrected rows, raw-correct to repaired-wrong regressions. |
| `selected_evidence_arithmetic` | Derives Gan labels from model-selected evidence. | Model-rendered label only, deterministic arithmetic only when the model emitted all operands, and oracle arithmetic upper bound. | Rows where deterministic arithmetic changes semantic kind, label, denominator, or selected event. |
| `benchmark_aligned` repair | Maps clinical labels to Gan-compatible labels. | Clean scorer-facing policy only, benchmark-aligned policy, and no benchmark repair. | Benchmark-format versus clinical-reasoning changes; Purist/Pragmatic category transitions. |
| State-graph node construction | Builds deterministic and hosted graph nodes. | Deterministic graph only, LLM boundary nodes only, LLM atomic claims only, and merged graph. | Oracle coverage, exact-evidence node rate, source component of selected node. |
| Projection / arbitration | Chooses final graph node. | Deterministic projection, LLM projection over the same nodes, null projection, and oracle projection. | Projection-only score, oracle gap, selected-node source, selected-node evidence validity. |
| Deterministic fallback | Replaces failed or unsafe LLM decisions. | No fallback, deterministic fallback only, and full stack. | Fallback rate, fallback wrong-to-correct, fallback correct-to-wrong, changed-label precision. |

## Planned Conditions

| Condition | Purpose | Promotion block |
| --- | --- | --- |
| `raw_model_selected_label` | Measures the model-owned prediction before repair. | Any threshold claim based on later semantic repair. |
| `format_only_repair` | Allows JSON/schema/unit aliases that do not change clinical meaning. | Hidden semantic-kind or event-selection changes. |
| `selected_evidence_arithmetic_only` | Tests whether the model selected the right evidence but failed label rendering. | Attribution must remain diagnostic, not LLM-heavy success. |
| `benchmark_aligned_adapter` | Measures Gan-format compatibility separate from clinical reasoning. | Must not be called scorer normalization or benchmark success. |
| `deterministic_graph_only` | Baseline graph behavior without LLM nodes. | Must remain frozen-comparator diagnostic. |
| `llm_boundary_nodes_only` | Tests hosted boundary-node contribution without deterministic node breadth. | Exact evidence and schema validity must be reported before score. |
| `llm_atomic_claim_nodes_only` | Tests saved LLM atomic claims as graph substrate. | Non-exact evidence claims must be downgraded or excluded. |
| `deterministic_projection` | Current projection policy over each node substrate. | Projection ownership stays deterministic. |
| `llm_projection_same_nodes` | Makes the model own arbitration while node candidates are fixed. | Requires validation25 smoke before any larger live run. |
| `oracle_projection` | Measures coverage ceiling on each node substrate. | Oracle result is a ceiling, not a candidate score. |
| `full_stack` | Existing best mixed artifact for comparison. | Must be labeled hybrid when semantic repair/fallback changes predictions. |

## Required Reports

Every replacement ablation report must include:

- Purist F1 and Pragmatic F1 for each condition on the same rows.
- Exact-label match for seizure-free duration and compact-interval rows where
  F1 category collapse hides duration errors.
- Repair attribution: rows changed by each layer, raw-wrong to final-correct,
  raw-correct to final-wrong, semantic-kind transitions, Purist/Pragmatic
  category transitions, and exact normalized-label transitions.
- Evidence validity: exact selected evidence, event/node evidence exactness,
  selected-event trace mismatches, selected-node source, and rows dropped for
  non-exact evidence.
- Replay variance: cached/raw-output reuse count, rows with stochastic or
  provider-call changes, run seed or cache key when available, and no-call
  replay versus live-call separation.
- Hard-slice breakdown: clusters, seizure-free duration, unknown/no-reference
  boundary, diary aggregation, recent-window arithmetic, competing semiologies,
  compact interval/bimonthly notation, conditional or perimenstrual windows,
  schema/parse failures, and template family when available.

## Validation Ladder

1. No-call design replay over saved artifacts only. This task completes that
   gate by naming replacement targets, conditions, and reporting requirements.
2. Implement a saved-output ablation runner against existing validation250
   artifacts. It must emit JSONL, JSON summary, Markdown report, and registry
   metadata.
3. If an LLM-owned replacement is needed, run validation25 only after the
   no-call runner exposes a specific deterministic module to replace.
4. Escalate to validation50 only when validation25 has no systemic schema,
   evidence, or trace failures.
5. Escalate to validation250 only with a written decision naming the module,
   comparator, inspection policy, and stop rule.

## Stop Rules

Reject or revise the replacement path before any LLM-heavy v2 run if:

- The proposed replacement changes labels but cannot report source evidence
  validity for the prediction-bearing fact.
- The score gain comes mainly from benchmark-aligned repair rather than model
  selected clinical meaning.
- A deterministic fallback fixes more rows than the LLM-owned layer while the
  artifact is still being described as LLM-heavy.
- Replay variance changes more than two rows on a 25-row smoke surface or more
  than 5% of rows on a larger surface without a cache/provenance explanation.
- Oracle projection is high but non-oracle projection remains low; that means
  projection/arbitration is the target, not graph-node construction.

## Implementation Notes

The next code task should add a saved-output ablation runner under
`gan2026/artifact_analysis`, reusing existing `repair_mode_metadata` and
component-ablation reporting helpers. It should read frozen validation
artifacts and produce condition-level rows with stable fields:

```text
source_row_index
split
condition
prediction_owner
node_source
projection_owner
repair_mode
raw_label
final_label
gold_label
purist_correct
pragmatic_correct
selected_evidence_valid
event_or_node_evidence_valid
changed_from_raw
changed_from_comparator
transition_reason
reused_raw_output
```

Do not implement LLM-heavy v2 prompt changes until this runner has produced at
least one no-call replay report or the project explicitly decides to skip the
replacement-ablation gate.
