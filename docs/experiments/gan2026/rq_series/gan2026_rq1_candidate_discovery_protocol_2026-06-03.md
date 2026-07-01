> **Superseded for navigation —** canonical summary: [`COMPONENT_MECHANICS_CANON.md`](../COMPONENT_MECHANICS_CANON.md). Full detail retained below.

# Gan 2026 RQ1 Candidate-Discovery Protocol

Date: 2026-06-03

Scope: validation-development protocol for RQ1, candidate discovery. This is a
component protocol, not a whole-pipeline architecture plan, benchmark claim, or
locked-holdout plan.

## Research Question

Which component produces the best candidate set for seizure-frequency state:
high gold-state recall, exact evidence, rich useful metadata, and bounded
candidate count?

Candidate discovery is credited only for exposing the gold-relevant clinical
state as a candidate. Evidence selection, projection, deterministic rendering,
and safety-floor policy are fixed comparison layers unless explicitly listed as
secondary diagnostics.

## Fixed Inputs

- Task: `seizure_frequency`
- Dataset: `gan2026`
- Split manifest: `gan2026_split_v1`
- Primary development surface: validation replay and validation hard slices.
- Locked holdout: excluded from RQ1 until this protocol has produced a frozen
  pre-run plan and the user explicitly authorizes a holdout audit.

Replay-first artifacts:

- `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl`
- `experiments/gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation250_gpt41mini_v1_live_2026-06-03.jsonl`
- `experiments/gan2026_hidden_family_first_failure_atlas_2026-06-03.csv`
- `experiments/gan2026_atlas_candidate_generation_projection_hard_slice_diagnostic_2026-06-03.jsonl`

## Candidate Generators

Compare generators as candidate sources, not as final policies:

| Generator | Family | RQ1 role |
| --- | --- | --- |
| `deterministic_candidates_all` | `rules_only` | All deterministic candidate events before top-candidate pruning. |
| `deterministic_top_candidate` | `rules_only` | Current transparent comparator candidate selected by deterministic rules. |
| `state_graph_nodes` | `hybrid_diagnostic` | Graph nodes as representability candidates, with projection held out. |
| `llm_candidate_selector_raw` | `llm_only` | Independent source-near LLM candidates from saved sidecars. |
| `llm_selected_state_or_evidence` | `llm_only` | LLM-selected state/evidence artifacts that can be replayed as candidates. |
| `union_verified_candidates` | `hybrid_diagnostic` | Union of deterministic, graph, and LLM candidates after exact-evidence gates. |

Fresh model calls are not allowed in the first pass. A small missing-candidate
proposer may be added only after replay proves a specific instrumentation gap,
with fixed rows, schema, model, prompt version, max candidates per note, and
stop rule recorded before the call.

## Matrix Schema

Build one row per source row, generator, and candidate. Required fields:

| Field | Meaning |
| --- | --- |
| `source_row_index` | Gan source row index. |
| `split` | Train, validation, or test from `gan2026_split_v1`; RQ1 should use validation only. |
| `distribution` | `validation750`, `validation_hard_slice`, or `synthetic_stress_panel`. |
| `artifact_path` | Source artifact used for replay. |
| `generator_name` | Candidate generator from the fixed list above. |
| `candidate_id` | Stable candidate id within the generator and row. |
| `candidate_kind` | `frequency_rate`, `cluster_frequency`, `seizure_free`, `last_event_only`, `unknown_frequency`, `no_reference`, or `unresolved_multiple`. |
| `candidate_label` | Generator-rendered label when present; nullable for source-near candidates. |
| `candidate_evidence` | Candidate evidence text. |
| `evidence_status` | `exact`, `source_near`, `invalid`, `missing`, or `not_applicable`. |
| `source_id_valid` | Whether the candidate source id resolves to an artifact source. |
| `temporality` | `current`, `recent`, `historical`, `future`, `unclear`, or missing. |
| `assertion_status` | `asserted`, `negated`, `hypothetical`, `uncertain`, or missing. |
| `certainty` | `certain`, `uncertain`, `possible`, or missing. |
| `applies_to` | Seizure type, semiology, or clinical target when available. |
| `denominator_or_window` | Count/window/unit fields when available. |
| `cluster_burden` | Cluster cadence and events-per-cluster fields when available. |
| `seizure_free_duration` | Duration/date fields for seizure-free candidates when available. |
| `hidden_families` | Tags from the hidden-family atlas. |
| `first_failure_owner` | Atlas first-failure owner when available. |
| `gold_label` | Normalized gold label under current scorer policy. |
| `gold_match_status` | `exact_label`, `purist_category`, `semantic_state`, `no_match`, or `not_judged`. |
| `gold_match_basis` | Which candidate fields support the match. |
| `metadata_missing_fields` | List of required metadata fields missing for the candidate kind. |

## Gold-State Matching Policy

Use a tiered match so candidate recall is not confused with rendering quality:

1. `exact_label`: candidate label parses and equals the gold normalized label.
2. `purist_category`: candidate label parses into the gold Purist category.
3. `semantic_state`: exact evidence and metadata expose the gold-relevant
   clinical state, but rendering is absent or not Gan-compatible.
4. `no_match`: candidate does not expose the gold-relevant state.
5. `not_judged`: missing note text, gold policy, or candidate fields prevent
   a defensible call.

RQ1 primary recall is `exact_label OR purist_category OR semantic_state`.
Rendering-only failures should be sent to RQ5, not counted as missing
candidates.

## Metrics

Primary metrics:

- gold-state candidate recall by generator;
- exact-evidence rate by generator;
- candidates per note, median and p90;
- false-positive burden: nonmatching candidates per note;
- metadata completeness by required field and candidate kind;
- hidden-family recall for candidate-generation first-failure rows.

Secondary diagnostics:

- recall delta over `deterministic_top_candidate`;
- union marginal gain by added generator;
- sidecar rescue rate on `candidate_generation_rescue`;
- boundary-state recall on
  `candidate_generation_unknown_seizure_free_boundary`;
- parse/scorability rate when generator emits labels.

Do not use final Purist or Pragmatic F1 as the RQ1 decision metric.

## Readouts

The RQ1 report must include:

- overall generator matrix with recall, exact evidence, burden, and metadata;
- the same matrix by hidden family;
- candidate-generation first-failure rows before and after each generator;
- examples of true rescues, false positives, metadata gaps, and not-judged rows;
- instrumentation gaps that block a stronger answer;
- claim boundary naming distribution, artifacts, replay mode, and absence of
  locked-holdout evidence.

## Stop Rule

RQ1 can be marked answered for validation development when the report can state:

- which generator or union has the best recall, evidence, metadata, and burden
  trade-off;
- which hidden families still lack candidate recall;
- whether replay is enough or a fixed missing-candidate proposer is justified;
- which failures should move to RQ2, RQ4, or RQ5 instead of remaining RQ1.

If saved artifacts cannot populate the matrix fields above, the next task is
instrumentation or a small predeclared proposer, not a broad validation run.
