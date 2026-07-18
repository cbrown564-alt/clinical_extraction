# Gan 2026 local Qwen/Gemma validation750 protocol

Date: 2026-07-18

## Question

Complete the full Gan 2026 validation750 runs for the local Qwen 3.6:35B and
Gemma 4 26B conditions using the same prompt, pipeline, and transport settings
as their completed test450 runs. The run order is Qwen first, then Gemma, with
no validation5 gate.

## Frozen condition

- Dataset: Gan 2026; manifest `gan2026_split_v1`; split `validation`;
  expected row count 750.
- Model routes: `ollama_chat/qwen3.6:35b`, then `ollama_chat/gemma4:26b`.
- Prompt: `gan2026_hybrid_structured_events_v0.7`.
- Architecture: `llm_with_rules` through `run_gan2026_hosted_condition.py`.
- Temperature: 0.
- Maximum completion tokens: 16,000.
- DSPy/LiteLLM cache: disabled for fresh calls.
- Ollama endpoint and local model policies remain those recorded in the
  2026-07-15 local queue protocol; no prompt, architecture, repair, or scorer
  change is introduced.

The runner's required validation ladder override is recorded as an escalation
reason for this explicitly requested full validation750 completion. It is an
operational bypass only; it does not add a gate or authorize test-row use.

## Evidence and row policy

Each condition writes a machine-readable JSONL artifact with one row per
validation record and an aggregate Markdown report. Validation rows may be
inspected for operational diagnosis, but this run is intended for aggregate
comparison with the completed test450 conditions. No Gan test450 row is opened,
used for tuning, or altered by this study.

## Scoring and attribution

Use the existing Purist and Pragmatic Gan scorers and the current report
accounting. Preserve raw model output, format/schema repair, semantic repair,
final prediction, evidence validity, and call/parse/schema/label events as
provided by the runner. Attribute any change to the existing `llm_with_rules`
condition; no new component is being tested.

## Stop rule and claim boundary

Stop each condition on a runner failure or incomplete artifact. A successful
run answers only whether the two named local conditions completed on the full
validation750 split under this fixed configuration. It is development evidence,
not clinical validation, holdout evidence, or a model-neutral ranking.

## Planned artifacts

- `scratch/local_queue/qwen36_35b/gan/validation750_full.jsonl`
- `scratch/local_queue/qwen36_35b/gan/validation750_full.md`
- `scratch/local_queue/gemma4_26b/gan/validation750_full.jsonl`
- `scratch/local_queue/gemma4_26b/gan/validation750_full.md`
- `scratch/local_queue/gan_val750_queue_20260718.stdout.log`
- `scratch/local_queue/gan_val750_queue_20260718.stderr.log`
