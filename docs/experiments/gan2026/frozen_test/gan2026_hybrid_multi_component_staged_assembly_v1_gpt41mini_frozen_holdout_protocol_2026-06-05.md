# Gan 2026 Hybrid Multi-Component Staged Assembly V1 GPT-4.1 Mini Frozen Holdout Protocol

Date: 2026-06-05

Status: model-specific frozen holdout protocol variant. Not authorized for
locked-test execution until the validation freeze gate and this variant are
explicitly approved.

Base protocol:
``

Review artifact:
``

## Variant Purpose

This variant freezes a hosted GPT-4.1 mini version of
`hybrid_multi_component_staged_assembly_v1`. It is a model-specific holdout
audit plan, not a generic runtime switch. The model is part of the candidate
identity.

This variant may be used only as one of these predeclared choices:

- the single authorized final holdout audit for v1; or
- one arm of a symmetric model-swap comparison where both arms are reported
  without selecting a promoted winner from locked-test results.

## Frozen Model Identity

| Field | Frozen value |
| --- | --- |
| Variant id | `hybrid_multi_component_staged_assembly_v1_gpt41mini` |
| Candidate version | `hybrid_multi_component_staged_assembly_v1` |
| Runtime model display/API id | `openai/gpt-4.1-mini` |
| Provider | OpenAI hosted |
| Endpoint route | default DSPy/LiteLLM OpenAI route |
| Model role | hybrid reasoner source materialization for staged assembly |
| Prompt/program family | `gan2026_hybrid_parallel_state_candidate_reasoner_v0` until superseded by a separately frozen v1 live-source program |
| Temperature | `0.0` |
| Max tokens | `1800` unless the live-source runner freezes a different value before authorization |
| DSPy/LiteLLM cache | disabled for locked-test live calls |
| Live-call status | not run; authorization pending |

Exact SDK, provider, and model-version metadata must be recorded in the run
artifact at execution time. If the provider model alias changes or a dated model
snapshot becomes available, record that exact value before interpreting results.

## Inherited Frozen Policies

This variant inherits all base protocol hashes, guardrails, and policy ids:

- split manifest: `gan2026_split_v1`;
- comparator: `rules_only_v1`;
- repair policy: `h5_repair_policy_v1`;
- boundary policy: `seizure_free_boundary_event_v0`;
- renderer policy: `benchmark_convention_renderer_v0`;
- safety floor: `selective_safety_floor_gate_v0`;
- release policy: `untagged_nonprediction_release_candidate_v0` only;
- action policy: `staged_action_policy_v1`;
- rejected behavior: trigger-context release, last-event automatic release,
  broad structured projection port, and broad action-policy widening.

Any change to these policies invalidates this variant.

## Implementation Preconditions

The current v1 assembly runner is saved-replay validation-only. Before this
variant can be authorized for test450, one of the following must be true:

- `staged_assembly_v1` gains a reviewed frozen-live-source path for
  `--split test` that emits only aggregate public outputs; or
- a frozen live GPT-4.1 mini source artifact is materialized through an existing
  LLM CLI surface, then consumed by a reviewed assembly adapter whose public
  test report remains aggregate-only.

The live source artifact may contain row-level operational outputs only because
they are required for scoring and provenance. It must not be inspected for
development, tuning, failure analysis, model selection, or slice creation.

## Frozen Source Materialization Command

If the existing LLM CLI is used for source materialization, the command must be
predeclared before execution:

```bash
gan2026-llm-experiment \
  --pipeline hybrid_parallel_state_candidate_reasoner \
  --split test \
  --mode live \
  --model openai/gpt-4.1-mini \
  --temperature 0 \
  --max-tokens 1800 \
  --disable-dspy-cache \
  --jsonl experiments/gan2026_hybrid_multi_component_staged_assembly_v1_gpt41mini_test450_live_source_2026-06-05.jsonl \
  --markdown experiments/gan2026_hybrid_multi_component_staged_assembly_v1_gpt41mini_test450_live_source_2026-06-05.md
```

This command is a source-materialization step, not the public holdout report.
The public report must be generated only by the frozen aggregate assembly path.

Expected public aggregate artifacts, if authorized:

```text
experiments/gan2026_hybrid_multi_component_staged_assembly_v1_gpt41mini_test450_aggregate_2026-06-05.json
experiments/gan2026_hybrid_multi_component_staged_assembly_v1_gpt41mini_test450_aggregate_2026-06-05.md
experiments/gan2026_hybrid_multi_component_staged_assembly_v1_gpt41mini_test450_component_summary_2026-06-05.csv
```

## Allowed Readouts

Allowed public readouts are exactly the base protocol's aggregate and
predeclared-slice readouts, plus hosted-call telemetry:

- call count, success count, retry count, timeout count, and parse-validity
  aggregate;
- aggregate token usage and cost if available from provider metadata;
- latency summary;
- cache status;
- model/provider metadata recorded at runtime.

No row ids, note text, raw model outputs, gold labels by row, or row-level
failures may appear in the public report.

## Interpretation Rules

Allowed language:

- hosted GPT-4.1 mini frozen holdout variant;
- local aggregate-only model-specific generalisation audit;
- GPT-4.1 mini source-materialized staged assembly.

Disallowed language:

- benchmark result;
- best-model claim based on locked-test comparison;
- GPT-4.1 mini superiority claim;
- production-ready clinical model.

## Authorization Record

Authorization status: not yet authorized.

Before execution, record whether this is the single authorized final audit or
one arm of a predeclared symmetric model-swap comparison.
