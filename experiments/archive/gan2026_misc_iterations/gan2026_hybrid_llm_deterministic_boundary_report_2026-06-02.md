# Gan 2026 Hybrid LLM/Deterministic Boundary Report

Date: 2026-06-02

This report records two architecture failures observed across the current Gan
2026 hybrid and LLM-heavy work, and turns them into concrete workstreams. It is
a validation-development planning artifact, not a benchmark claim and not a
holdout analysis.

## Summary

The project has sometimes used the right components in the wrong roles.

In the hybrid adjudicator line, deterministic candidate selection became a hard
information bottleneck. The model was asked to adjudicate over candidates that
rules had already selected. When candidate recall failed, the model could not
recover because it never saw enough source context to choose the missing fact.
That made the LLM useful only inside the deterministic selector's recall
envelope.

In the LLM-heavy line, the opposite error appeared. The model was asked to own
decisions that are often better treated as deterministic policy: parser grammar,
stable benchmark conventions, selected-evidence arithmetic side-cars, and
arbitrary Gan-compatible renderings. Some of these choices are not clinical
ambiguities at all. They are fixed conventions that should be explicit,
testable, and ablatable rather than repeatedly taught to the model.

Going forward, new DSPy LLM architectures should use typed outputs with scoped
`JSONAdapter` as the default substrate unless a comparator intentionally
preserves the older opaque-string behavior.

## Failure 1: Deterministic Candidate Selection As A Recall Ceiling

The hybrid adjudicator experiments were useful attribution studies, but their
design put deterministic rules upstream of the model's evidence access. The
model did not get a fair chance to perform clinical candidate selection when
the deterministic candidate selector missed the relevant event, collapsed a
cluster, ignored a diary/log pattern, over-pruned a seizure-free duration, or
favored the wrong temporal state.

That architecture answers a narrow question:

```text
Given the deterministic candidates, can an LLM choose better than the
deterministic selector?
```

It does not answer the stronger hybrid question:

```text
Can an LLM and deterministic rules compensate for each other's candidate-recall
and semantic-selection failures?
```

### Better Hybrid Designs

Two candidate designs should be tested separately.

1. `hybrid_parallel_candidate_context_reasoner`

   Run deterministic candidate selection and model candidate selection in
   parallel. Then give a second model pass both candidate sets, provenance, and
   the source letter. The adjudication prompt should ask which candidate or
   synthesized event best supports the final clinical frequency. This tests
   whether LLM candidate recall adds value without discarding deterministic
   precision.

2. `hybrid_full_letter_with_deterministic_hints`

   Give the model the whole source letter plus deterministic candidates as
   advisory context. The deterministic output should be labeled as a hint:
   rule IDs, evidence spans, candidate labels, confidence/failure flags, and
   known blind spots. The model should be allowed to reject, revise, or ignore
   the hints when source evidence supports a better answer.

Both designs need score layers that keep component ownership visible:

- raw model-owned final label;
- deterministic top candidate;
- model candidate selector output;
- final hybrid adjudicator output;
- side-car benchmark adapters;
- rows where deterministic-only was correct and hybrid regressed;
- rows where deterministic candidate recall failed but the model recovered.

The important new metric is not only aggregate Purist F1. It is candidate-recall
rescue: how often the model finds or preserves a correct source fact outside the
deterministic selector's top candidate set.

## Failure 2: LLMs Owning Arbitrary Or Mechanical Rules

The LLM-heavy variants moved too much work into the model. This created two
problems.

First, it wasted model capacity on conventions that deterministic code can
apply more consistently. A benchmark convention such as mapping an ambiguous
word to one accepted label is not automatically a clinical reasoning task. If
the gold labels apply a fixed convention, a named deterministic adapter may be
more transparent than a long prompt section that encourages the model to
overfit the benchmark.

Second, it blurred attribution. If deterministic post-processing changes the
selected fact, category, arithmetic, or benchmark label, then the primary result
is no longer cleanly LLM-owned. It may be the right architecture, but it should
be named as hybrid or benchmark-adapted.

### Initial Ownership Policy

The exhaustive audit should classify each deterministic rule family into one of
four ownership buckets.

| Bucket | Use | Examples to audit |
| --- | --- | --- |
| Model instruction | The model should use this clinical principle while reading the note because context, assertion, temporality, or semantics matter. | current-vs-historical selection, conflicting active and historical frequencies, conditional seizures, perimenstrual/boundary states, whether cluster context changes the clinical interpretation |
| Deterministic extraction or adapter | A stable mechanical or benchmark convention should be applied explicitly and ablated. | parser-ready unit grammar, word-number normalization, slash/per variants, accepted label syntax, arbitrary bimonthly/biweekly-style benchmark policy when the dataset fixes one meaning |
| Hybrid side-car | Deterministic logic can check or propose a result, but it must not silently replace the model-owned primary answer. | selected-evidence arithmetic, cluster burden rendering, duration bucketing, benchmark alignment |
| Research comparison | The rule is plausible but may overfit Gan 2026; keep it as an ablation condition until generalization evidence exists. | diary-specific patterns, synthetic-letter shorthand, highly specific temporal-selection heuristics |

This policy should be applied to every rule group already present in the repo:

- `date_duration_utilities`
- `portable_rate_expressions`
- `seizure_free_no_event_assertions`
- `cluster_arithmetic`
- `diary_log_aggregation`
- `temporal_selection`
- `gan_shorthand`
- `benchmark_repair`
- `gold_normalization_policy`

The audit should produce a rule matrix with `rule_id`, group, portability,
current module, current prediction effect, proposed owner, prompt-instruction
status, deterministic-adapter status, ablation switch, target failure rows, and
claim-language constraint.

## DSPy Adapter Policy

The current adapter evidence supports a default change for new LLM/DSPy work:
use typed DSPy fields and scoped `dspy.JSONAdapter()` unless a run is explicitly
an opaque-string comparator.

This should not retroactively mutate historical pipelines. Frozen comparators
should remain comparable to their saved artifacts. But new LLM-heavy and hybrid
candidate-selection architectures should start from:

```python
with dspy.context(lm=lm, adapter=dspy.JSONAdapter()):
    prediction = program(...)
```

Required metadata for those runs:

- DSPy version;
- adapter class and native structured-output setting when available;
- structured-output parse failures;
- Pydantic/schema validation failures;
- raw model-owned score layer;
- deterministic side-car score layers;
- evidence exactness and trace-mismatch counts.

## Workstreams

### Workstream A: Hybrid Candidate Recall Without A Deterministic Bottleneck

Predeclare a validation25 paired smoke comparing:

- deterministic top-candidate-only adjudication;
- parallel deterministic and LLM candidate selectors followed by adjudication;
- full-letter adjudication with deterministic hints.

Promotion should depend on candidate-recall rescue, selected-evidence exactness,
trace consistency, and deterministic-correct regression counts, not only F1.

### Workstream B: Exhaustive Rule Ownership Audit

Inventory every deterministic rule and post-processing adapter. For each rule,
decide whether it belongs in model instructions, deterministic policy, hybrid
side-car diagnostics, or research-only comparison. The output should be a
durable rule matrix and, where the decision is hard to reverse, a follow-up
decision note.

The audit should pay special attention to ambiguous or arbitrary conventions:
`bimonthly`/`biweekly`-style mappings, cluster syntax, compact intervals,
vague quantities, unit grammar, and single-total-window rendering.

### Workstream C: Typed DSPy JSONAdapter As The Default LLM Substrate

Make scoped `JSONAdapter` and typed output fields the default for new LLM/DSPy
architectures. Existing opaque-string runners may stay as frozen comparators.
Any new prompt/schema redesign should justify deviations from typed adapter
outputs in the experiment predeclaration.

## Claim Language

Use the following language discipline until the workstreams are complete:

- "LLM-owned" only when the raw model output contains the selected clinical fact
  and parser-ready final label being scored.
- "Hybrid" when deterministic and model components both contribute semantic
  behavior or candidate selection.
- "Benchmark adapter" when deterministic code maps an already selected fact into
  Gan-compatible surface form.
- "Deterministic side-car" when deterministic logic proposes or checks a result
  but is not part of the primary score layer.
- "Candidate-recall rescue" when the model recovers a correct source fact that
  deterministic candidate selection did not expose as the top or admissible
  candidate.

The goal is not to make the LLM do everything. The goal is to assign each
decision to the component that can make it most transparently, robustly, and
reproducibly.
