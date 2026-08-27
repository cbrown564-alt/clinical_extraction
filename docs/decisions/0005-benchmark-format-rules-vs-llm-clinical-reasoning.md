# 0005: Keep Arbitrary Benchmark Format Rules Separate From LLM Clinical Reasoning

Date: 2026-06-02

## Decision

Treat arbitrary or dataset-specific Gan 2026 gold-label conventions as
benchmark-format policy, not necessarily as clinical reasoning failures.

The project may test whether an LLM can learn these conventions, but it must
not assume that moving every benchmark convention into the prompt is the best
architecture. Some conventions may remain better as explicit deterministic
post-processing rules when they are arbitrary, stable, auditable, and clearly
separate from the model-owned clinical interpretation.

This decision applies especially to conventions such as:

- `bimonthly`, which Gan 2026 gold labels consistently treat as `1 per 2 month`
  even though the word can reasonably be interpreted either way in ordinary use;
- cluster-rendering preferences, where `1 per 4 week cluster` may be clinically
  intelligible but not the exact representation chosen by the gold labels;
- benchmark-compatible shorthand that rewards a particular label format rather
  than a materially better clinical answer.

## Context

The first saved-output LLM-replacement ablation showed that
selected-evidence arithmetic and benchmark alignment materially improve Gan 2026
validation250 scores over the raw LLM-heavy v1 labels. Many corrected rows are
not pure clinical reasoning errors. Instead, they reflect a mismatch between a
reasonable model-rendered answer and the benchmark's preferred representation.

For example, the model may select the right evidence and express a plausible
clinical interpretation, while the gold label encodes a narrower convention:

- `bimonthly seizures` becomes `1 per 2 month`;
- `1 per 4 week cluster` becomes `1 per 4 week`;
- cluster burden is represented as `N cluster per period, M per cluster` rather
  than a flattened or prose-like label.

These distinctions matter for attribution. If deterministic code converts an
LLM-selected clinical answer into the benchmark's chosen label format, the
result must be described as an LLM-with-rules or benchmark-adapted development artifact
unless the LLM itself produced the final benchmark-compatible label.

They also matter for prompt design. Adding more rules and examples may improve
specific benchmark rows but can overload the model, make simple cases more
complicated, or cause broad regressions. The project has observed this pattern
before: more complex instructions can encourage over-interpretation of simple
answers.

## Consequences

- Do not call every mismatch with a Gan 2026 gold label a clinically important
  model failure.
- Separate reports must distinguish:
  - clinically wrong selected fact;
  - right evidence but wrong arithmetic/rendering;
  - arbitrary benchmark-format mismatch;
  - parser or schema compatibility issue.
- Deterministic benchmark adapters are acceptable when they are:
  - explicitly named;
  - categorized as `benchmark_format` or `gan2026_specific`;
  - ablated against raw model output;
  - reported as post-processing rather than hidden scorer normalization.
- LLM-heavy experiments may try to make the model own these conventions, but the
  experiment must measure whether added instructions cause overload or
  regressions on simpler rows.
- A decision to keep an arbitrary convention as deterministic post-processing is
  not a failure of the research program. It may be the more transparent and
  generalizable architecture.

## Evaluation Policy

When testing whether the LLM may absorb a benchmark convention, use a paired
comparison rather than only aggregate F1:

- same validation set;
- same saved/raw outputs when possible, or the smallest live validation smoke
  when prompt changes are required;
- condition A: simpler clinical-reasoning prompt plus explicit deterministic
  benchmark adapter;
- condition B: prompt teaches the convention and asks the model to render the
  final benchmark-compatible label;
- report both improvements on target convention rows and regressions on simple
  rows.

Required checks:

- target-convention accuracy, such as bimonthly and cluster-rendering rows;
- simple-frequency regression count;
- selected-evidence exactness;
- selected-event trace mismatches;
- raw-correct to final-wrong changes;
- instruction/schema failure rate;
- whether the model over-complicates previously simple answers.

## Claim Language

Use conservative language:

- "benchmark-format adapter" for deterministic conversion into Gan-compatible
  labels;
- "LLM-owned rendering" only when the raw model output itself contains the
  benchmark-compatible label;
- "clinical mismatch" only when the model selected the wrong clinical fact or
  materially wrong interpretation;
- "arbitrary gold-label convention" when the benchmark chose one defensible
  representation among multiple clinically plausible forms.

The goal is not to maximize model burden. The goal is to know which component
owns each decision and to choose the architecture that is most transparent,
auditable, and robust.
