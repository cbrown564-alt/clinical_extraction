# Gan 2026 RQ1 Candidate-Discovery Answer

Date: 2026-06-03

Supersession note, 2026-06-03: this report is retained as a diagnostic baseline
audit, not a completed RQ1 research answer. Its deterministic-default conclusion
falls into the validation-tuned selector trap described in
`` and is
superseded by
``.

Status: answered for saved validation replay as a development question; not yet
answered as a holdout-transfer or benchmark-comparable claim.

## Answer

This report gives a clean development answer, not a final generalization
answer. It is useful because it separates candidate discovery from
selection/projection/rendering and identifies where candidate recall is probably
not the broad bottleneck. It is not sufficient, by itself, to claim that the
same conclusion will transfer to the locked holdout.

For broad validation-development candidate discovery, the best default source is
the deterministic candidate set, with state-graph nodes as an equivalent
representability view. Both cover 725/750 validation source rows under the RQ1
gold-state recall definition, with modest candidate burden. The deterministic
top candidate is nearly as strong and much leaner, but it hides useful alternate
candidates needed for later evidence-selection and projection studies.

The LLM candidate sidecar should not replace deterministic candidate discovery
as a broad source. It has excellent exact-evidence behavior, but materially
higher false-positive burden and weaker broad source-row recall. Its strongest
value is selective: on rows already classified by the hidden-family atlas as
candidate-generation first failures, the saved LLM sidecar recalls 30/44 rows
versus 19/44 for deterministic all-candidates or state-graph nodes.

The practical RQ1 answer is therefore:

- use deterministic all-candidates, or state-graph nodes when graph
  representability is needed, as the default candidate substrate;
- keep deterministic top only as the transparent comparator, not as the full
  candidate substrate;
- test LLM candidate generation as a selective rescue sidecar for
  candidate-generation first-failure and unknown/seizure-free boundary slices;
- do not promote a broad LLM candidate generator without a verifier gate that
  reduces false-positive burden and repairs metadata gaps.

The deeper transferable hypothesis is narrower than the validation numbers:
candidate discovery is probably not the broad bottleneck, but
unknown/seizure-free boundary exposure, uncertainty handling, evidence
selection, and projection among already exposed candidates remain the main
transfer risks.

## Claim Boundary

This report uses only saved validation artifacts under `gan2026_split_v1`.

Primary matrix:
`experiments/gan2026_rq1_candidate_discovery_matrix_2026-06-03.jsonl`

Matrix report:
`experiments/gan2026_rq1_candidate_discovery_matrix_2026-06-03.md`

Protocol:
``

The recall definition is candidate-level: `exact_label`, `purist_category`, or
`semantic_state` counts as exposing the gold-relevant clinical state. This
intentionally separates candidate discovery from Gan rendering quality,
projection policy, and final Purist/Pragmatic F1.

No fresh model calls were made. Locked holdout was not inspected for this
question.

This claim is deliberately weaker than "RQ1 solved for holdout." It means the
saved validation artifacts are strong enough to guide the next development
question. They are not strong enough to support a benchmark, production, or
holdout-transfer conclusion.

## Generator Trade-Offs

| Generator | Source rows | Candidates | Recalled source rows | Recall | False positives/note | Exact evidence | Median candidates/note | p90 candidates/note |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `deterministic_candidates_all` | 750 | 1,194 | 725 | 0.967 | 0.257 | 0.898 | 1 | 3 |
| `state_graph_nodes` | 750 | 1,122 | 725 | 0.967 | 0.244 | 0.891 | 1 | 3 |
| `deterministic_top_candidate` | 750 | 750 | 716 | 0.955 | 0.045 | 0.847 | 1 | 1 |
| `llm_candidate_selector_raw` | 739 | 2,126 | 642 | 0.869 | 1.365 | 0.985 | 3 | 4 |
| `llm_selected_state_or_evidence` | 250 | 250 | 222 | 0.888 | 0.112 | 0.956 | 1 | 1 |

Interpretation:

- `deterministic_candidates_all` and `state_graph_nodes` are the best
  validation-replay candidate substrates. They tie on source-row recall and
  have similar burden.
- `deterministic_top_candidate` is useful as a comparator and safety-floor
  source, but drops 9 source rows relative to all deterministic candidates.
- `llm_candidate_selector_raw` has the best exact-evidence rate but produces
  almost twice as many candidates per represented note as deterministic all
  candidates, with many nonmatching candidates.
- `llm_selected_state_or_evidence` is promising as an evidence-selection input,
  but only covers the 250-row LLM-heavy surface and should be interpreted under
  RQ2 rather than as the broad RQ1 winner.

The inferred union of deterministic candidates, graph nodes, LLM sidecar, and
LLM selected-state/evidence recalls 736/750 validation source rows. Most of that
gain comes from adding the LLM sidecar to deterministic candidates. The union
result is diagnostic only because `union_verified_candidates` has not yet been
materialized as a gated generator with stable source ids and burden controls.

## Hidden-Family Readout

| Hidden family | Default recall | LLM sidecar recall | Interpretation |
| --- | ---: | ---: | --- |
| `rate_bucket_or_denominator` | 201/204 | 170/201 | Deterministic and graph sources already expose most rate candidates. |
| `cluster_burden` | 123/126 | 117/126 | Deterministic recall is high, but cluster metadata remains incomplete. |
| `competing_semiologies` | 280/292 | 246/287 | Candidate discovery is usually present; later selection/projection is likely the harder question. |
| `current_vs_historical` | 289/303 | 257/298 | Candidate discovery is usually present; temporal selection remains separate. |
| `seizure_free_duration` | 155/175 | 148/173 | This is a meaningful weak slice for all generators. |
| `unknown_boundary` | 76/92 | 57/92 | This remains the largest candidate-discovery weakness. |
| `uncertainty_or_ambiguity` | 90/107 | 69/107 | Candidate generation still underexposes uncertainty states. |
| `benchmark_format_convention` | 78/82 | 48/81 | Most failures here should not be solved by candidate discovery alone. |

`Default recall` is the deterministic all-candidates/state-graph value; those
two generators match on these slices in the replay matrix.

The hidden-family result says RQ1 should not keep chasing broad recall. The
hard remaining candidate-discovery problem is boundary and uncertainty state
exposure, especially unknown versus seizure-free language. Many rate,
competing-semiology, and current-versus-historical rows already have a candidate
and should move to evidence selection or projection analysis.

## Candidate-Generation First Failures

On the 44 validation rows the atlas classified as candidate-generation first
failures:

| Generator | Recalled source rows | Recall |
| --- | ---: | ---: |
| `llm_candidate_selector_raw` | 30/44 | 0.682 |
| `deterministic_candidates_all` | 19/44 | 0.432 |
| `state_graph_nodes` | 19/44 | 0.432 |
| `deterministic_top_candidate` | 17/44 | 0.386 |

This is the strongest evidence for selective LLM value in RQ1. It does not mean
the LLM sidecar is a better broad generator. It means an LLM missing-candidate
proposer is worth testing only on fixed candidate-generation rescue slices,
with exact evidence, source-id validity, max-candidate limits, and
false-positive accounting.

Transfer confidence for this signal is low-to-moderate, not high. The 44-row
slice comes from validation first-failure attribution, and the LLM sidecar
signal could be tuned to validation-family phrasing. Treat it as a mechanism
hypothesis to stress-test, not as a holdout-ready intervention.

## Transfer Confidence

| Finding | Development confidence | Holdout-transfer confidence | Why |
| --- | --- | --- | --- |
| Broad candidate discovery is not the main bottleneck for most rows. | High | Moderate | Deterministic and graph sources recall 725/750 validation rows, but all evidence is validation replay. |
| Unknown/seizure-free boundary and uncertainty states remain hard. | High | Moderate-to-high | Multiple hidden families converge on the same weakness, and this is clinically plausible rather than only metric-shaped. |
| LLM sidecar helps candidate-generation first-failure rows. | Moderate | Low-to-moderate | The effect is selective but comes from 44 validation rows and needs stress testing. |
| State-graph nodes are an equivalent broad candidate substrate. | Moderate | Moderate | They match deterministic all-candidate recall in replay, but graph representability may depend on current rule coverage. |
| The inferred union reaches 736/750 source-row recall. | Low | Low | The union is not a materialized, verifier-gated generator and should remain diagnostic. |

Before any holdout-facing use, RQ1 needs one of two anti-overfit checks:

- a fixed validation hard-slice stress test for `unknown_boundary`,
  `uncertainty_or_ambiguity`, and `seizure_free_duration`, with no broad
  validation-F1 optimization; or
- a synthetic mechanism panel built before any new model calls, focused on
  unknown versus seizure-free language, stale historical seizure-free claims,
  ambiguous nocturnal events, and competing semiologies.

These checks should judge candidate recall, exact evidence, candidate burden,
and metadata completeness only. They should not tune final labels or aggregate
F1.

## Metadata And Instrumentation Gaps

The matrix can answer the main RQ1 trade-off, but it exposes instrumentation
that should be improved before promotion or a paper table:

- deterministic candidates lack explicit `temporality` and `assertion_status`
  in the saved matrix, even when rules imply those states;
- deterministic top candidates often lose denominator/window metadata compared
  with the underlying event;
- LLM sidecar candidates often expose exact source-near evidence but not
  denominator/window or cluster-burden fields;
- `union_verified_candidates` is not yet a real generator artifact, so union
  recall is inferred rather than replayed through a verifier;
- the 250-row `llm_selected_state_or_evidence` surface is useful but not
  distribution-equivalent to validation750.

These are instrumentation gaps, not reasons for another broad validation run.

## Decision

RQ1 is answered for saved validation replay as a development-control question:

- Best broad substrate: `deterministic_candidates_all` or `state_graph_nodes`.
- Best transparent comparator: `deterministic_top_candidate`.
- Best selective rescue signal: `llm_candidate_selector_raw` on
  candidate-generation first-failure rows.
- Main unresolved candidate-discovery families: `unknown_boundary`,
  `uncertainty_or_ambiguity`, and `seizure_free_duration`.
- Main next use of RQ1 output: feed fixed candidates into RQ2 evidence
  selection and RQ4 projection, while optionally predeclaring a narrow LLM
  missing-candidate rescue experiment for boundary/uncertainty slices.

RQ1 is not answered as a holdout-transfer claim. The report should be carried
forward as a disciplined hypothesis about where the bottleneck is, not as a
permission slip for locked-test execution.

## Next Action

Move the active primary question to RQ2, evidence selection, using
deterministic all-candidates or state-graph nodes as the fixed candidate
substrate. Keep the LLM missing-candidate proposer as an optional RQ1 follow-up
only if the RQ2 setup reveals that missing candidates, rather than selection or
projection, still block the answer.

Before any future holdout-facing candidate uses this RQ1 conclusion, require a
predeclared boundary/uncertainty stress check or explicitly label the RQ1
evidence as validation-development only.
