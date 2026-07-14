# Gan 2026 Hybrid Multi-Component Staged Assembly V1 Qwen 3.6 35B Ollama Frozen Holdout Protocol

Date: 2026-06-05

Status: model-specific frozen holdout protocol variant. Not authorized for
locked-test execution until the validation freeze gate, local endpoint
provenance, and this variant are explicitly approved.

Base protocol:
``

Review artifact:
``

Ollama runbook:
`docs/runbooks/windows_local_ollama.md`

## Variant Purpose

This variant freezes a local Qwen 3.6:35b Ollama version of
`hybrid_multi_component_staged_assembly_v1`. It tests local-model transfer and
deployment feasibility under the same staged assembly guardrails. It is not a
hospital deployment claim and not a benchmark-comparable result.

This variant may be used only as one of these predeclared choices:

- the single authorized final holdout audit for v1; or
- one arm of a symmetric model-swap comparison where both arms are reported
  without selecting a promoted winner from locked-test results.

## Frozen Model Identity

| Field | Frozen value |
| --- | --- |
| Variant id | `hybrid_multi_component_staged_assembly_v1_qwen36_35b_ollama` |
| Candidate version | `hybrid_multi_component_staged_assembly_v1` |
| Runtime model display/API id | `ollama_chat/qwen3.6:35b` |
| Ollama model name | `qwen3.6:35b` |
| Provider | local Ollama via DSPy/LiteLLM native chat provider |
| API base | `http://localhost:11434` |
| Forbidden route | `http://localhost:11434/v1` with `openai/qwen3.6:35b` |
| Model role | hybrid reasoner source materialization for staged assembly |
| Prompt/program family | `gan2026_hybrid_parallel_state_candidate_reasoner_v0` until superseded by a separately frozen v1 live-source program |
| Temperature | `0.0` |
| Max tokens | `5000` unless the live-source runner freezes a different value before authorization |
| DSPy/LiteLLM cache | disabled for locked-test live calls |
| Thinking mode | disabled; repo LM builder sends `extra_body={"think": False}` for `ollama_chat/...` |
| Live-call status | not run; authorization pending |

At execution time, record local model metadata from `http://localhost:11434/api/tags`,
including digest, parameter size, quantization, host machine, GPU/CPU notes if
available, endpoint smoke result, and latency summary.

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
- a frozen live Qwen source artifact is materialized through an existing LLM CLI
  surface, then consumed by a reviewed assembly adapter whose public test report
  remains aggregate-only.

The live source artifact may contain row-level operational outputs only because
they are required for scoring and provenance. It must not be inspected for
development, tuning, failure analysis, model selection, or slice creation.

## Required Endpoint Smoke

Before any locked-test run, run and record a native Ollama smoke check:

```powershell
$body = @{
  model = "qwen3.6:35b"
  messages = @(@{ role = "user"; content = "Return exactly JSON: {`"ok`": true}" })
  stream = $false
  options = @{ temperature = 0; num_predict = 32 }
  think = $false
} | ConvertTo-Json -Depth 6
Invoke-RestMethod -Method Post -Uri http://localhost:11434/api/chat -ContentType "application/json" -Body $body
```

Also record `http://localhost:11434/api/tags` metadata before the test run.

## Frozen Source Materialization Command

If the existing LLM CLI is used for source materialization, the command must be
predeclared before execution:

```powershell
$env:OPENAI_API_KEY = "ollama"
gan2026-llm-experiment `
  --pipeline hybrid_parallel_state_candidate_reasoner `
  --split test `
  --mode live `
  --model ollama_chat/qwen3.6:35b `
  --api-base http://localhost:11434 `
  --temperature 0 `
  --max-tokens 5000 `
  --disable-dspy-cache `
  --jsonl experiments\gan2026_hybrid_multi_component_staged_assembly_v1_qwen36_35b_ollama_test450_live_source_2026-06-05.jsonl
```

This command is a source-materialization step, not the public holdout report.
The public report must be generated only by the frozen aggregate assembly path.

Expected public aggregate artifacts, if authorized:

```text
experiments/gan2026_hybrid_multi_component_staged_assembly_v1_qwen36_35b_ollama_test450_aggregate_2026-06-05.json
experiments/gan2026_hybrid_multi_component_staged_assembly_v1_qwen36_35b_ollama_test450_aggregate_2026-06-05.md
experiments/gan2026_hybrid_multi_component_staged_assembly_v1_qwen36_35b_ollama_test450_component_summary_2026-06-05.csv
```

## Allowed Readouts

Allowed public readouts are exactly the base protocol's aggregate and
predeclared-slice readouts, plus local-runtime telemetry:

- call count, success count, retry count, timeout count, empty-content count,
  and parse-validity aggregate;
- latency summary;
- cache status;
- Ollama model digest, parameter size, quantization, host hardware notes, and
  endpoint smoke result;
- output-format failure counts as operational evidence.

No row ids, note text, raw model outputs, gold labels by row, or row-level
failures may appear in the public report.

## Qwen-Specific Interpretation Rules

Allowed language:

- local Qwen 3.6:35b frozen holdout variant;
- local-model transfer audit;
- deployment-feasibility signal under Ollama;
- aggregate-only model-specific generalisation audit.

Disallowed language:

- benchmark result;
- best-model claim based on locked-test comparison;
- Qwen superiority claim;
- validated hospital deployment;
- production-ready clinical model.

If Qwen produces empty content, invalid JSON, or parse failures, report those as
operational/model-interface failures. Do not repair them using test outcomes or
convert them into new prompt/schema tuning on the locked test split.

## Authorization Record

Authorization status: not yet authorized.

Before execution, record whether this is the single authorized final audit or
one arm of a predeclared symmetric model-swap comparison.
