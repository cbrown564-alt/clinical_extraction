# 0039: Final ExECT six-model roster

Date: 2026-07-15  
Status: accepted

## Decision

The final ExECT model comparison will use these six model conditions:

| Model condition | Availability class | Execution route |
| --- | --- | --- |
| GPT-4.1-mini | Closed-weight | Hosted |
| GPT-5.6 Luna | Closed-weight | Hosted |
| GPT-5.6 Sol | Closed-weight | Hosted |
| DeepSeek V4 Flash, thinking enabled | Open-weight | Hosted |
| Qwen 3.6:35B | Open-weight | Local |
| Gemma 4 26B | Open-weight | Local |

This gives three closed-weight and three open-weight conditions. Two of the
open-weight conditions, Qwen and Gemma, run locally. DeepSeek is the hosted
open-weight condition.

All six conditions must use the same corrected model-led ExECT pipeline and
scorer. Model-specific adapters may repair transport or output shape, but any
semantic prompt, clinical repair, or component-graph difference must be
declared as a separate condition.

## Context

The paper requires a six-model comparison, but cleanup intentionally did not
invent the three missing model identities. This decision closes the roster
question and replaces the earlier unspecified `3/6` target.

The retained evidence currently names GPT-4.1-mini, `deepseek/deepseek-chat`,
and Qwen 3.6:35B. `deepseek/deepseek-chat` is the API identifier for DeepSeek
V4 Flash. The API identifier alone does not distinguish whether thinking was
enabled. The final comparison and paper will use only the thinking-enabled
condition and will report its display name as **DeepSeek V4 Flash**.

The retained historical DeepSeek result does not record the thinking setting.
It remains useful as historical evidence, but it does not satisfy the final
DeepSeek condition unless durable run metadata proves that thinking was
enabled.

## Consequences

- Before new calls, the comparison protocol must record the exact provider or
  local runtime identifier, model revision when exposed, endpoint, temperature,
  token limits, cache mode, prompt profile, hardware for local models, and
  format-repair policy for every condition. The DeepSeek record must also state
  explicitly that thinking was enabled and how it was requested.
- GPT-4.1-mini and Qwen have directly named retained evidence. The other four
  roster conditions remain to be run unless the retained DeepSeek thinking
  state is resolved from durable runtime evidence.
- The final report must not substitute a different model, size, quantization,
  hosted alias, or local route without updating this decision.
- The current three-model table remains historical partial evidence. It is not
  the final model comparison, and its DeepSeek result must not be used as the
  paper's reported DeepSeek result without proof that thinking was enabled.
- No six-model ranking or closed-versus-open conclusion is permitted until all
  six conditions have completed the frozen comparison protocol.
