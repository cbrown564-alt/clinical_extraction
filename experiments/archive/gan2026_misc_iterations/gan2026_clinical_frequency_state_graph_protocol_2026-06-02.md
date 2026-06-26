# Gan 2026 Clinical Frequency State Graph Protocol

Date: 2026-06-02

This artifact starts the validation-only cycle recommended by
`experiments/gan2026_generalization_gap_research_report_2026-06-02.md`.
It freezes hybrid v0.2 `cluster_diary_candidate_recall` as a comparator-only
generalization audit result and shifts development work to a semantic-state
graph substrate.

## Frozen Comparator Boundary

Hybrid v0.2 `cluster_diary_candidate_recall` is no longer a tuning target.

- Validation750 gated final: 677/750 Purist and 686/750 Pragmatic.
- Validation750 deterministic top comparator: 697/750 Purist and 704/750
  Pragmatic.
- Locked test450 gated final: 343/450 Purist and 353/450 Pragmatic.
- Locked test450 deterministic top comparator: 343/450 Purist and 354/450
  Pragmatic.
- Candidate Purist recall dropped from 707/750 validation to 359/450 test.

Any future use of this variant should be as a historical comparator or as a
source of component hypotheses on validation-only surfaces. Test row-level
failures must not be used for repair or prompt tuning.

## New Experiment Family

Working name: `hybrid_clinical_frequency_state_graph`.

Prediction-bearing path for this first scaffold:

1. High-recall deterministic span harvester creates graph nodes for source-near
   frequency, cluster, seizure-free, unknown, and no-reference states.
2. Graph nodes preserve exact evidence spans, normalized Gan-compatible labels,
   semantic kind, temporality, assertion state, certainty, rule id, and graph
   errors.
3. Deterministic projection maps the graph to a Gan-compatible label for
   projection-only diagnostics.
4. Counterfactual invariance uses graph signatures that ignore evidence wording
   and note order while preserving clinical-state fields.
5. Oracle coverage reports whether the gold normalized label or sentinel kind is
   representable in the harvested graph.

The first implementation is deliberately not an LLM final-label pipeline. Its
purpose is to expose the hidden variable behind the validation/test gap:
span absence, graph construction failure, projection policy failure, or
arbitration failure.

## Initial Scaffold

Code:

- `src/clinical_extraction/tasks/seizure_frequency/gan2026/state_graph/`

Tests:

- `tests/test_gan2026_state_graph.py`

Pinned behavior:

- Source-near graph nodes retain exact evidence offsets.
- Projection selects the highest current frequency over a partial seizure-free
  node when both are present.
- Projection can preserve uncertainty instead of forcing a single label when
  competing current frequency hypotheses remain.
- Counterfactual invariance signatures survive paraphrase and note-order
  changes.
- Oracle coverage summary reports gold representability by semantic kind.

## Next Validation-Cycle Experiments

1. Run oracle coverage on validation25/50 and the existing synthetic hard-case
   panel; report missing gold representability separately from projection F1.
2. Add graph-builder rows for LLM-extracted atomic claims, but require exact
   evidence entailment before a field becomes certain.
3. Build a projection-only ablation over validation hard slices before running
   any broad validation aggregate.
4. Generate a validation-derived counterfactual paraphrase panel and score graph
   invariance before final-label accuracy.
5. Add family-aware validation grouping using validation-only rows and
   non-test-derived surface features.

## Claim Language

This scaffold is architecture and diagnostic work, not a benchmark result. It
does not change scorer policy, deterministic V1, or locked-test interpretation.
Any future metric claim must name whether the reported score comes from graph
harvesting, graph construction, deterministic projection, LLM hypothesis
adjudication, or full-stack projection.
