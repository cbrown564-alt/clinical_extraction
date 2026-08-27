# Gan 2026 v0.5 local test450 and Qwen validation750 protocol

Date: 2026-07-18  
Status: test450 extension complete; Qwen validation attempt retained
Authorization: the user explicitly requested these runs on 2026-07-18.

## Question

Complete the missing local Qwen 3.6:35B and Gemma 4 26B conditions for the
shared Gan v0.5 test450 comparison, then run Qwen on validation750 with that
same prompt. In parallel, complete the already-authorized DeepSeek V4 Flash
v0.5 continuation under the hosted protocol.

This closes the same-prompt six-model aggregate panel needed before the
development hard-slice study. It does not authorize test-row inspection,
prompt tuning from test results, or a general model-capability claim.

Before extending the panel, replay the completed GPT-4.1-mini, GPT-5.6 Luna,
and GPT-5.6 Sol raw outputs through today's shared schema repair and the
unchanged downstream stack. This is a no-call aggregate-only replay. DeepSeek
receives the same replay after its v0.5 call artifact reaches 450 rows.

## Frozen local conditions

- Dataset and manifest: Gan 2026, `gan2026_split_v1`.
- Test surface: `test450`, aggregate-only; no row-level output may be inspected
  or reported.
- Development surface: `validation750`; row review is permitted, but this run
  is initially an aggregate comparator.
- Models and order: `ollama_chat/qwen3.6:35b` test450, then
  `ollama_chat/gemma4:26b` test450, then `ollama_chat/qwen3.6:35b`
  validation750.
- Prompt: `gan2026_hybrid_structured_events_v0.5` for every call.
- Pipeline: `llm_with_rules`, one structured event call per note, followed by
  the current shared schema repair and `hybrid_full_stack` repair.
- Runtime: native Ollama chat, thinking disabled, temperature 0, maximum
  completion tokens 16,000, cache disabled.
- Scoring: unchanged Gan Purist primary and Pragmatic secondary mappings.
- Output repair may correct shared JSON/schema defects only; it may not retry a
  clinically undesirable but valid answer or apply a model-specific semantic
  rule.

The current schema-repair implementation is used for the new local conditions.
It adds shared format aliases used by local structured outputs. This differs
from the intermediate dirty-tree schema file recorded for the first hosted
v0.5 calls, while the prompt, clinical repair, normalization, labels, and
scorer remain fixed. The difference must remain visible in the final panel.

## Current-schema no-call replay

For each completed hosted v0.5 artifact:

1. require exactly 450 unique IDs matching the test manifest;
2. require 450 non-empty raw outputs and prompt version v0.5;
3. reuse those raw outputs without a model call;
4. run today's JSON/schema repair, structured validation, normalization,
   selected-evidence repair, full clinical repair, rendering, and frozen
   Purist/Pragmatic scoring across all 450 rows; and
5. retain only aggregate changed-label, wrong-to-correct, correct-to-wrong,
   evidence, parse/schema, and score counts outside the sealed root.

The expected result is zero final-label and score change. Any nonzero change is
reported as a schema-repair replay effect and does not authorize row inspection
or tuning. The replay source and result artifacts must be fingerprinted.

## Pilot gate

Before each local test450 run, run the first five validation-manifest records
with the exact model, prompt, pipeline, temperature, token limit, cache state,
and repair configuration. The gate requires:

- 5/5 calls completed;
- 5/5 structured records;
- zero blocking parse/schema/label failures; and
- 5/5 exact selected-evidence substrings.

Pilot accuracy is not a gate and may not change the prompt or repair policy.

## Artifacts and readout

Each JSONL row preserves the source identifier, rendered prompt, raw model
output, schema/format events, structured record, normalized events, final
label, exact-evidence status, and scorer comparison. Test JSONL remains sealed
under ignored `scratch/holdout/`; only aggregate counts, runtime metadata, and
artifact fingerprints may be retained outside it.

Planned roots:

- `scratch/validation/gan2026_matched_v05_local/qwen36_35b/`
- `scratch/holdout/gan2026_matched_v05_local/qwen36_35b/`
- `scratch/validation/gan2026_matched_v05_local/gemma4_26b/`
- `scratch/holdout/gan2026_matched_v05_local/gemma4_26b/`
- `scratch/local_queue/qwen36_35b/gan/v05_validation750_full.*`

## DeepSeek parallel continuation

DeepSeek remains governed by the
[hosted v0.5 protocol](gan2026_matched_v05_test450_protocol_2026-07-16.md).
Its 150-row base plus 200-row resume checkpoint contain 350 unique test rows.
The remaining 100 calls may run in parallel with the local queue using the
same v0.5 prompt and today's shared schema repair, as explicitly accepted by
the user. Because this is a mixed schema-repair continuation, the final report
must disclose the change. Its required full current-schema replay prevents the
mixed parser history from becoming the reported DeepSeek score.

## Stop rule and claim boundary

Stop a condition on an incomplete artifact, runner failure, or failed pilot.
Retain a complete aggregate regardless of score. Do not repair, rerun, or tune
from test450 row behavior. The final v0.5 table is an aggregate-only comparison
on a previously used holdout with route and schema-adapter caveats. The Qwen
validation750 result is development evidence.

## Completion addendum, 2026-07-20

The Qwen and Gemma test450 conditions and the DeepSeek continuation completed
with 450 unique test-manifest rows each. Their aggregate-only Purist/Pragmatic
results are Qwen 362/384, Gemma 355/374, and DeepSeek 344/366. The retained
aggregate file records the six-condition v0.5 panel without exposing row data.

The separate Qwen v0.5 validation command produced only 45 rows despite its
`validation750` filename and is not a complete validation condition. It is an
operational artifact and is not used as evidence. The complete six-model
validation evidence is owned by the separate matched v0.7/v0.8 protocol and
its twelve 750-row artifacts.
