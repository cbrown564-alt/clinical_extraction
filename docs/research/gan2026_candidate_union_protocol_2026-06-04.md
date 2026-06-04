# Gan 2026 Candidate Union Protocol

Date: 2026-06-04

Status: pre-run validation-development protocol. This protocol authorizes
materializing candidate-union artifacts before any new live model calls. It is
not a holdout-transfer, production, or benchmark-comparable claim.

## Question

Does a gated union of deterministic candidates and selective LLM
boundary/ambiguity candidate proposals improve hard-state representability
without unacceptable candidate burden or deterministic-correct regressions?

The component question is candidate breadth and attribution. It is not a final
F1 experiment.

## Prior Evidence

RQ1 showed that deterministic/state-graph candidates remain the broad substrate
and safety floor. Broad LLM candidate generation is unsafe as a replacement, but
has selective value for unknown boundaries, seizure-free blockers,
conditional-only states, competing semiologies, and ambiguous currentness.

RQ2-RQ4 showed that exact evidence and projection policy remain separate
component questions. This protocol must therefore materialize candidate
surfaces separately from selected-state reasoning and final-label projection.

## Fixed Surface

- Split manifest: `gan2026_split_v1`.
- Development surface: validation only.
- Locked holdout: no row-level inspection or tuning.
- Primary rows: saved validation hard-panel rows already used for RQ1-RQ4
  mechanism analysis.
- Optional expansion: balanced validation50 after the hard-panel artifact is
  coherent.
- Deterministic role: fixed broad substrate, comparator, safety floor, and
  miss-slice source only.
- LLM role: selective candidate proposal for named boundary/ambiguity families
  only.

## Candidate Surfaces

Materialize one row per source row with three candidate lists:

1. `deterministic_candidates`
   - Existing deterministic/state-graph candidates.
   - Must preserve candidate id, label or normalized state, evidence, source id,
     currentness metadata when available, and hidden-family tags.
2. `llm_boundary_candidate_proposals`
   - New or replayed LLM proposals for named hard families.
   - Must not emit a final Gan label as the prediction-bearing answer.
   - Must include exact evidence, source id, candidate kind, currentness,
     assertion/certainty, semiology, rate/window/denominator fields,
     seizure-free duration fields, cluster fields, and ambiguity flags when
     applicable.
3. `union_verified_candidates`
   - Deduplicated, gated union.
   - Must preserve provenance for every retained candidate:
     `deterministic`, `llm_boundary_proposal`, or `both`.

## LLM Candidate Proposal Scope

The LLM proposer should look only for candidate facts that the deterministic
surface plausibly collapses or misses:

- unknown or no-reference boundary states;
- exclusive conditional-only events;
- seizure-free claims with recent-event blockers;
- seizure-free claims that apply to one semiology but not all seizure types;
- competing current semiologies;
- diary/log candidate states with implicit observation windows;
- cluster cadence and per-cluster burden candidates;
- vague rate phrases with explicit denominators;
- source-near phrases that are projection-compatible but not already Gan
  syntax.

It should not optimize final F1, choose the final label, repair benchmark
syntax, or replace ordinary deterministic rate candidates.

## Union Gates

A candidate can enter `union_verified_candidates` only if it passes the gates
needed for its type:

- exact evidence substring, unless the candidate is explicitly marked
  `diagnostic_source_near` and excluded from promotion metrics;
- valid source id when the source format supports ids;
- no unsupported arithmetic;
- no invented denominator or duration;
- candidate-kind-specific required metadata;
- max candidate burden per source row, with overflow candidates retained only
  in a diagnostic rejected-candidate list;
- duplicate or near-duplicate candidates merged with provenance preserved.

Candidate-kind metadata requirements:

- frequency: count or range, denominator/window, currentness, semiology scope;
- cluster: cluster cadence when known, per-cluster burden when known, and
  whether either axis is missing;
- seizure-free: duration, all-type scope, recent-event blockers, and
  currentness;
- unknown/no-reference: reason for uncertainty and whether any competing state
  exists;
- conditional: trigger/condition and whether events occur outside that
  condition.

## Artifact Schema

Each source-row record should include:

- `source_row_index`;
- `split`;
- `gold_label`, for development scoring only;
- `hidden_families`;
- `deterministic_candidates`;
- `llm_boundary_candidate_proposals`;
- `union_verified_candidates`;
- `rejected_candidates`;
- `candidate_burden_summary`;
- `gold_state_recall_summary`;
- `metadata_completeness_summary`;
- `gate_failures`;
- `deterministic_top_label`;
- downstream placeholder fields for selected-state replay, left empty until a
  separate selected-state experiment consumes the union.

## Metrics

Primary metrics:

- gold-state candidate recall for each surface;
- LLM recall rescue over deterministic candidates;
- deterministic recall lost by union gating;
- exact-evidence rate;
- valid-source-id rate;
- unsupported-candidate rate;
- candidate count per note, median and p90;
- rejected-candidate burden;
- metadata completeness by candidate kind;
- hidden-family recall.

Secondary metrics:

- downstream selected-state W->C and C->W when the same union is later consumed;
- how often LLM candidates are retained, rejected, or merged with deterministic
  candidates;
- first gate responsible for rejected but potentially useful candidates.

## Success Criteria

The candidate union is useful for validation development if:

- it rescues gold-relevant candidate states in named hard families;
- it does not remove deterministic gold-state coverage;
- exact evidence and source-id gates remain high precision;
- candidate burden remains bounded enough for a fixed downstream selector;
- retained LLM candidates have enough metadata for rich selected-state
  reasoning.

## Negative Result Criteria

The union should be rejected or narrowed if:

- retained LLM candidates create high unsupported burden;
- broad ordinary-rate rows become harder for downstream selection;
- deterministic-correct rows regress after selected-state replay;
- metadata is too incomplete for projection policy;
- the only apparent benefit comes from validation-specific label anchoring.

## Stop Rule

First materialize a replay/diagnostic candidate-union artifact from saved
surfaces where possible. Do not run new live LLM calls until the artifact schema,
gates, and metrics can be computed on saved rows.

After the saved-surface pass, run new LLM candidate proposal only on a
predeclared hard slice if the saved artifact shows that the gating and scoring
machinery can separate rescue from burden.

## Claim Boundary

This protocol supports validation-development component analysis only. It does
not authorize locked-test inspection, whole-pipeline promotion, scorer/gold
policy change, or benchmark-comparable language.
