# 0042: Share structured-output repair across local models

Date: 2026-07-16  
Status: accepted and implemented

## Decision

Qwen, Gemma, and future local Ollama models use one shared structured-output
compatibility layer. Repairs are selected by the observed output defect, not by
the model name.

The layer must preserve the original response and report each action. It may
repair serialization and output shape, but it must not change selected clinical
facts, evidence, labels, timeframes, or other clinical values.

Allowed deterministic repairs are:

- extracting JSON from surrounding prose or a Markdown fence;
- parsing Python-literal objects with single quotes, `None`, `True`, or `False`;
- accepting literal control characters inside strings;
- removing trailing commas before `}` or `]`;
- quoting an otherwise bare object key and repairing a mixed single/double
  quote used only as an object-key delimiter;
- replacing an object close with the required array close at the boundary
  between `events` and `selection`;
- closing a scorer-facing ExECT mention object before a second mention that was
  accidentally nested beside it;
- removing a malformed, non-scored rationale while keeping scored fields;
- converting numeric attribute values to strings;
- adapting a top-level array or legacy `mentions` shape; and
- applying existing named field and enum aliases, including observed local-model
  misspellings of `anchor_text`, `event_id`, `temporality`, and `rationale`;
- assigning a missing structural `event_id` by list position when sibling event
  IDs establish the `eN` convention; and
- converting null evidence to an empty string only for an explicit
  `no_reference` event.

Every repair retains a named note such as
`json_dialect_repaired: trailing_commas`. Reports keep initial failures,
successful repairs, and remaining failures separate.

## Failure records

Every local structured-output row retains:

- the original raw response and call error;
- initial and final parse errors;
- explicit failure codes for provider error, empty content, reasoning-only
  content, schema-constraint bypass, repetition loop, truncation, invalid JSON,
  and schema validation;
- the retry response, when attempted; and
- whether the retry was applied or rejected.

Operational smoke runs must write row records before reporting an aggregate.
An aggregate parse count without the corresponding raw row is not sufficient
diagnostic evidence.

## Bounded format retry

A local model may receive one format-only retry only when its first response is
valid JSON after the allowed dialect repairs but fails schema validation. Empty
responses, plain-text schema bypass, truncated JSON, repetition loops, and
otherwise unparseable JSON are not eligible.

The retry receives the original response, the explicit JSON schema, and this
instruction: keep every clinical fact and value unchanged; add, remove, infer,
summarize, or reinterpret nothing; return only corrected JSON.

The retry is accepted only when it passes the target schema and preserves the
multiset of non-rationale scalar values under each field name from the first
payload. A rejected retry remains visible and the first failure remains the
final result.

This creates a narrow exception to [decision 0041](0041-single-call-exect-model-comparison.md).
The normal ExECT path still uses one extraction call per letter. A failed local
serialization may add at most one reformat call. That call is not allowed to
perform extraction or change clinical meaning, and run metadata must report it.

## Runtime probe

Before clinical rows, each exact local model tag must run a two-stage native
Ollama chat probe using `think=false` and a nested JSON schema. The first stage
tests whether Ollama enforces the schema without a JSON instruction. If that
fails, the second stage mirrors the application prompt by explicitly requiring
JSON while retaining the same schema. The queue may continue only when one
stage returns valid schema-matching JSON.

The result records one of two runtime modes:

- `native_schema_constraint`: Ollama enforced the schema directly; or
- `prompt_plus_shared_parser`: the model followed the explicit JSON instruction,
  but Ollama did not enforce the schema constraint.

The second mode is allowed because all clinical prompts already require JSON
and the shared parser records every repair and residual failure. It is not
reported as equivalent native constraint enforcement. Empty, reasoning-only,
or malformed output from both stages stops the queue before clinical data.

The native `ollama_chat/` route remains required. The OpenAI-compatible Ollama
route is not an equivalent runtime for these conditions.

## Context

[Decision 0038](0038-json-dialect-repair-as-explicit-schema-repair.md) established
Python-literal recovery as explicit schema repair after Qwen output drift. The
same principle now covers all local models and additional named, format-only
defects.

Ollama previously disabled JSON-schema constraints for thinking-capable Gemma
4 and Qwen 3.5 models when `think=false`. Ollama fixed that shared runtime bug
in April 2026. Gemma 4 also has reports of malformed constrained JSON, empty
content, and long free-text generation problems. These are reasons to probe and
classify the runtime, not reasons to add unmeasured Gemma-only clinical repair.

On Ollama 0.30.10, the installed `qwen3.6:35b` tag still reproduces the open
Qwen `think=false` defect through its `qwen3.5` renderer/parser: schema-only
requests return plain text. The same request with an explicit JSON instruction
returns valid JSON. The installed `gemma4:26b` tag enforces the schema directly.
This runtime difference is recorded in model configuration and probe logs.

A two-row ExECTv2 dev140 context probe found a separate Gemma runtime issue.
At `num_ctx=32768`, EA0135 twice stopped after roughly 300 completion tokens
with truncated JSON, `finish_reason=stop`, and only about 14,100 total tokens;
this was not exhaustion of the 16,000-token output allowance or advertised
32K context. At `num_ctx=65536`, both residual rows returned valid structured
records. A fresh 32K control also returned EA0132 cleanly, confirming that its
original extra delimiters were ordinary generation/format variability rather
than context exhaustion. Gemma ExECT runs therefore declare `num_ctx=65536`;
Qwen remains at 32K. The larger Gemma context is restricted to sequential,
single-call execution on this workstation because the measured run used
partial GPU offload and transient available system memory fell below 0.1 GiB.
This is a runtime accommodation, not a parser repair or prompt change.

Primary runtime references:

- [Ollama shared `think=false` structured-output fix](https://github.com/ollama/ollama/pull/15678)
- [Open Qwen `think=false` format issue](https://github.com/ollama/ollama/issues/14645)
- [Gemma 4 prompt formatting](https://ai.google.dev/gemma/docs/core/prompt-formatting-gemma4)
- [Gemma 4 constrained JSON investigation](https://github.com/ollama/ollama/issues/15502)

## Consequences

- Format reliability can be compared across local models without hiding model
  or runtime defects.
- Schema repair remains separate from deterministic clinical repair and Gan
  label normalization.
- New repair types require a named note, a value-preservation test, and an
  update to this decision or its successor.
- A successful retry is operational recovery, not evidence that the first call
  complied with the schema.
- Existing saved outputs are rewritten only by an explicit no-call schema
  replay. Such a replay must preserve the raw response and original failure
  fields, replace only previously blocking rows, keep already-successful rows
  unchanged, retain a pre-replay backup, and regenerate downstream artifacts
  without model access.
