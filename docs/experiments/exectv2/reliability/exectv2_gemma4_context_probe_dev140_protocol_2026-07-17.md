# Gemma 4 context probe on two dev140 failures

Date: 2026-07-17

## Question

Did the two residual blocking Gemma 4 26B structured-output failures on ExECTv2
`dev140` result from the declared 32,768-token context, and does a 65,536-token
context recover them without changing the prompt, schema, parser, or clinical
policy?

## Fixed comparison

- Dataset and inspection policy: ExECTv2 `dev140`; only EA0132 and EA0135,
  whose development failures may be inspected.
- Model: Ollama `gemma4:26b`, digest
  `5571076f3d70050487b26b341705799e0ab29b808164f90d20d4cf84f699d251`,
  Q4_K_M.
- Candidate: the original single-call program with `num_ctx=65536`.
- Comparator: each row's saved original output from the otherwise identical
  `num_ctx=32768` run.
- Fixed settings: temperature 0, maximum output 16,000 tokens, native schema
  constraint, no DSPy cache, one row at a time, unchanged full prompt profile.
- This is a fresh-call development diagnostic, not a replacement for the
  frozen full-run condition.

## Measurements and artifact

The machine-readable probe artifact must retain, per call: row identifier,
configured context and output limits, prompt and response character counts,
provider prompt/evaluation token counts when exposed, finish reason or done
reason, elapsed/load/prompt-evaluation/evaluation durations, parse result and
failure codes, Ollama resident context and VRAM allocation, sampled NVIDIA VRAM
and GPU utilization, process working set, and system available memory. Raw
model output remains in the local diagnostic artifact because this is an
inspectable development split.

## Stop rule and interpretation

Run each of the two rows once at 65,536 context. Stop after both complete or on
an out-of-memory/provider failure. A clean recovery supports context pressure
as the mechanism only when token accounting or the provider stop reason is
consistent with that explanation. A complete but malformed response remains a
schema-format failure. A cut-off response far below both limits without a
length stop remains a runtime/model-generation failure. Do not change the
prompt or promote the new context to full runs from these two rows alone.

## Claim boundary

The result is a two-row Gemma 4 development diagnostic on this Windows RTX 4070
Laptop GPU workstation. It cannot establish model quality, holdout behavior,
or a generally optimal context size.

## Result

The 65,536-context candidate returned valid structured records for both rows.
EA0132 used 14,785 prompt and 1,229 completion tokens (16,014 total), completed
in 179.7 seconds, and produced nine events. EA0135 used 13,838 prompt and 1,632
completion tokens (15,470 total), completed in 153.9 seconds, and produced seven
events. Both provider responses reported `finish_reason=stop`.

The fresh 32,768-context control also returned EA0132 cleanly, using 16,763
total tokens. EA0135 reproduced the saved failure: it stopped after 303
completion tokens and 14,141 total tokens with truncated JSON, again reporting
`finish_reason=stop`. The mechanism is therefore a context-sensitive Gemma or
Ollama early stop, not literal consumption of the declared context or maximum
output tokens. EA0132's original complete object plus extra delimiters is
generation/format variability.

At 65,536 context, Ollama reported the requested loaded context and 3.36 GiB of
VRAM allocation. NVIDIA telemetry peaked at 4,931 MiB used and 99% utilization.
The Python probe peaked below 260 MiB working set. Available system memory fell
transiently to about 0.06 GiB on the first 64K load and remained above 2.5 GiB
on the second call. This supports 64K only for sequential, one-call execution
on this workstation; it does not support concurrency.

## Decision

Declare `num_ctx=65536` for the Gemma ExECT condition while retaining the same
prompt, schema, parser, temperature, and 16,000-token output limit. Keep Qwen at
32K. Do not replace the original full-run artifact with these two diagnostic
calls, and do not infer a score change from them.

Machine-readable artifacts:

- `experiments/exectv2_gemma4_context_probe_dev140_20260717.json`
- `experiments/exectv2_gemma4_context_probe_dev140_32768_control_20260717.json`
