# Gan 2026 DSPy Adapter Architecture Report

Date: 2026-06-02

## Summary

The repo is using DSPy in a valid but adapter-underpowered way. Current Gan 2026
LLM pipelines wrap each task as a single JSON-string input and a single
JSON-string output, then parse and repair that output outside DSPy. This is
workable, and it preserves the project's raw-output audit trail, but it does not
test whether DSPy's typed signatures and JSON-oriented adapters can improve
schema reliability or model-owned final-label rendering.

Do not fold this directly into `llm_heavy_clinical_frequency_reasoner_v2`.
Instead, create a separate architecture:

```text
llm_only_typed_adapter_reasoner
```

This architecture should test the adapter hypothesis cleanly while keeping
`llm_heavy_clinical_frequency_reasoner_v2` as the existing prompt-redesign path
gated by Decision 0006.

## Local Finding

The installed local DSPy version is `3.2.1`. The active repo dependency is broad:

```text
dspy>=2.5.0
```

Current live runs call `dspy.configure(lm=...)` without setting an adapter.
Observed `dspy.settings.adapter` is `None`, so DSPy uses its default adapter
behavior. The current pipeline signatures use a single opaque output string:

- `decision_json: str` in `llm_only_direct_labeler` and the hybrid adjudicator;
- `structured_json: str` in `hybrid_structured_events`;
- `llm_heavy_reasoner_json: str` in `llm_heavy_clinical_frequency_reasoner`;
- `boundary_state_graph_builder_json: str` in the boundary-state graph builder.

This means DSPy is currently acting mostly as a prompt and LM-call wrapper. The
repo's own parsers remain responsible for extracting an inner JSON object,
repairing aliases, validating Pydantic records, checking evidence spans, and
scoring.

That pattern has one important advantage: saved `raw_output` artifacts contain
the prediction-bearing text that downstream parsers score. It also has a cost:
DSPy cannot fully use field types, Pydantic models, adapter parsing, or
structured-output provider features for the actual clinical payload.

## Upstream DSPy Guidance

DSPy documentation points in a different direction for structured tasks:

- Signatures should carry semantically meaningful field names, because the LM
  reads those names and uses them as task guidance.
- Typed fields make programs more reliable by letting DSPy coerce outputs and
  surface parse failures instead of hiding them in prompt-only workflows.
- Richer output types such as Pydantic models, TypedDicts, and dataclasses can
  express structure that is awkward to encode in prose instructions.
- `JSONAdapter` is designed for JSON-oriented structured output. In DSPy 3.2.1,
  it tries native structured-output response formatting and falls back to JSON
  object mode when appropriate.
- `dspy.context(...)` is the right place for scoped LM or adapter overrides when
  the repo wants one architecture to use a different adapter without changing
  every other pipeline.

Relevant docs:

- https://dspy.ai/getting-started/expanding-signatures/
- https://dspy.ai/api/adapters/JSONAdapter/
- https://dspy.ai/diving-deeper/adapters/
- https://dspy.ai/diving-deeper/settings-and-context/

## Why Not Patch V2

`llm_heavy_clinical_frequency_reasoner_v2` already has a specific research
purpose: test whether the model can own selected-evidence arithmetic and
parser-ready final-label rendering without deterministic semantic replacement.
Decision 0006 makes that a promotion gate against v1 failure modes.

Changing v2 to also test a new DSPy adapter/signature substrate would mix two
questions:

1. Did the prompt/schema redesign improve LLM-owned clinical rendering?
2. Did typed DSPy output and `JSONAdapter` improve schema reliability or reduce
   parsing/rendering failures?

Those are both useful questions, but they should not share one architecture
name or one promotion path.

## Proposed Architecture

Name:

```text
llm_only_typed_adapter_reasoner
```

Research family:

```text
llm_only
```

Prediction-bearing component:

```text
LLM typed DSPy program
```

Deterministic components:

- evidence substring validation;
- parser compatibility checks;
- schema validation;
- scorer normalization for already model-selected labels;
- named side-car benchmark adapters;
- reporting and ablation summaries.

The deterministic code must not silently replace the model's selected clinical
fact or final model-owned label in the primary score layer.

## Architecture Sketch

The new program should replace the single string output with typed DSPy output
fields that mirror the clinical contract:

```text
note_text: str
task_instructions: list[str]
output_contract: dict
->
events: list[TypedClinicalFrequencyEvent]
selection: TypedClinicalSelection
final_answer: TypedGanFinalAnswer
```

Recommended record concepts:

- `TypedClinicalFrequencyEvent`: source-near seizure-frequency fact, semiology,
  temporality, assertion status, raw value, time window, evidence text, and
  optional structured operands.
- `TypedClinicalSelection`: selected event IDs, clinical rationale, selected
  evidence, and trace consistency fields.
- `TypedGanFinalAnswer`: parser-ready final label, final kind, confidence,
  arithmetic/rendering explanation, and any declared benchmark-format caveat.

The output models may reuse existing Pydantic record concepts where stable, but
the first implementation should avoid making old parser-repair behavior
prediction-bearing. The goal is to test typed model output, not hide the same
opaque JSON string behind a different adapter.

## Adapter Policy

Use scoped adapter configuration for this architecture:

```python
with dspy.context(lm=lm, adapter=dspy.JSONAdapter()):
    prediction = program(...)
```

Do not change global adapter defaults for the whole repo during the first test.
Existing pipelines should remain comparable to their saved artifacts.

For local or provider setups where native structured output is unreliable,
record the adapter mode and failure in metadata. If needed, compare:

- `JSONAdapter(use_native_function_calling=True)`;
- `JSONAdapter(use_native_function_calling=False)`;
- current default `ChatAdapter` behavior as an ablation.

## Experiment Plan

Initial surface:

```text
validation25 under gan2026_split_v1
```

Default model:

```text
GPT-4.1 mini
```

Primary question:

```text
Can typed DSPy output plus JSONAdapter reduce schema/parser/rendering failures
while preserving LLM-owned clinical interpretation?
```

Comparator:

- `llm_heavy_clinical_frequency_reasoner_v1` validation25/v1-derived layers;
- pending `llm_heavy_clinical_frequency_reasoner_v2` smoke, if run separately;
- current opaque-string DSPy pipelines where relevant.

Required score layers:

- raw model-owned label;
- format-only repair;
- deterministic selected-evidence arithmetic side-car;
- benchmark-aligned adapter side-car;
- full-stack score, explicitly marked as post-processing.

Required non-score diagnostics:

- structured-output success count;
- DSPy adapter parse failures;
- Pydantic validation failures;
- parser-compatible final labels;
- exact selected evidence spans;
- selected-event trace mismatches;
- raw-correct to side-car-wrong regressions;
- raw-wrong to side-car-correct replacements.

## Promotion Gate

Promote to validation50 only if:

- 25/25 calls return adapter-parseable structured output or have clearly
  isolated provider failures;
- at least 24/25 final labels are parser-compatible before semantic repair;
- at least 23/25 selected evidence spans are exact and source-near;
- selected-event trace mismatches are 0/25;
- raw model-owned Purist score is at least competitive with the v2 smoke target,
  or misses are explicitly benchmark-format conventions rather than arithmetic
  or selected-fact failures;
- deterministic selected-evidence arithmetic improves no more than five rows
  over the raw model-owned label.

Reject or redesign if:

- the architecture still needs deterministic semantic replacement to look good;
- `JSONAdapter` mostly returns a wrapper around an opaque string payload;
- typed fields cause recurrent enum drift or field omission;
- adapter/provider behavior makes outputs less reproducible than the current
  opaque-string approach;
- simple rows regress because the typed contract overloads the prompt.

## Implementation Notes

Keep this architecture separate in code and artifacts. Recommended module path:

```text
src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_only_typed_adapter_reasoner.py
```

Recommended artifact stem:

```text
gan2026_llm_only_typed_adapter_reasoner_validation25_gpt41mini_v0_2026-06-02
```

Recommended metadata additions:

- `architecture: llm_only_typed_adapter_reasoner`;
- `claim_type: llm_only_typed_adapter_reasoner`;
- `dspy_version`;
- `dspy_adapter`;
- `dspy_adapter_native_function_calling`;
- `response_format_mode`;
- `typed_output_schema_version`;
- `raw_model_owned_score_layer`;
- `side_car_score_layers`.

The first implementation should be intentionally conservative: create the new
program, runner, parser bridge, and report writer with focused tests around
adapter parsing and attribution metadata before running live validation25.

## Claim Language

Use:

```text
typed-adapter LLM-only architecture
```

for this experiment.

Use:

```text
LLM-owned final label
```

only when the raw typed model output contains the parser-ready final Gan label.

Use:

```text
side-car deterministic arithmetic
```

when deterministic code derives or replaces a final label from selected
evidence.

Do not describe a score as an LLM-only score if the primary improvement comes
from deterministic selected-evidence arithmetic, benchmark-format adapters, or
hidden semantic repair.

## Recommendation

Create `llm_only_typed_adapter_reasoner` as the next adapter-specific test
architecture. Keep `llm_heavy_clinical_frequency_reasoner_v2` separate as the
prompt/schema redesign path. This gives the project a clean comparison between:

- opaque JSON-string DSPy programs;
- LLM-heavy prompt redesign under the current adapter substrate;
- typed DSPy signatures using `JSONAdapter`;
- deterministic side-car adapters for benchmark-specific rendering.

That separation is the cleanest way to learn whether DSPy adapter best practices
help this task without corrupting the attribution story that the repo is trying
to preserve.
