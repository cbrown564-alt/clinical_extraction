# Gan 2026 Hybrid Multi-Component Staged Assembly V1 Frozen Protocol Review

Date: 2026-06-05

Reviewed protocol:
`docs/research/gan2026_hybrid_multi_component_staged_assembly_v1_frozen_holdout_protocol_2026-06-05.md`

## Review Verdict

The base protocol is acceptable as a saved-replay aggregate-only holdout
protocol. Its strongest properties are split discipline, source-artifact hashes,
explicit policy ids, predeclared allowed readouts, and a clear prohibition on
locked-test row-level failure review.

It should not be treated as sufficient for live model variants without separate
model-specific addenda. Live variants change the experimental object because raw
model output, endpoint routing, cache behavior, call telemetry, and runtime
failure modes become part of the candidate.

## Findings

### P1: Live model variants need separate frozen identities

The base protocol states that no live model calls are part of the saved-replay
candidate. That is correct, but it means GPT-4.1 mini and Qwen 3.6:35b cannot
be run under the base protocol as incidental runtime substitutions.

Resolution: create model-specific protocol variants that freeze model id,
provider route, prompt/source materialization policy, cache policy, telemetry,
and interpretation language before any locked-test use.

### P1: Do not use two holdout variants as a winner-selection tournament

Running both model variants on locked test and then selecting the better branch
would turn test450 into a model-selection surface. That would violate the split
discipline even if both public reports are aggregate-only.

Resolution: before test execution, either select exactly one variant as the
authorized final audit or explicitly predeclare a symmetric model-swap
comparison whose result will not choose a promoted branch or tune either model.

### P1: Current v1 assembly runner is saved-replay validation-only

`src/clinical_extraction/tasks/seizure_frequency/gan2026/hybrid/staged_assembly_v1.py`
currently accepts only `--split validation` and `--mode saved-replay`. It cannot
execute a live GPT/Qwen holdout variant as documented.

Resolution: each live variant must either add runner support before
authorization or first materialize a frozen live source artifact through an
existing LLM CLI surface, then assemble only aggregate public outputs without
inspecting row-level test failures.

### P2: Qwen requires the native Ollama chat route

The repo model strategy and Windows Ollama runbook require
`ollama_chat/qwen3.6:35b` with `--api-base http://localhost:11434`, not an
OpenAI-compatible `/v1` route. The shared LM builder sets
`extra_body={"think": False}` for `ollama_chat/...` models.

Resolution: the Qwen variant must freeze the native route, require an endpoint
smoke check, record `/api/tags` metadata, and treat empty-content/parse failure
rates as operational evidence rather than clinical failures.

## Non-Issues

- The base protocol's artifact hashes were mechanically rechecked against files
  on disk.
- The allowed and disallowed readouts match the locked-test rules in
  `docs/design/gan2026_split_protocol.md` and
  `docs/design/gan2026_saturated_validation_protocol.md`.
- The protocol correctly keeps boundary/renderer claims bounded and rejects
  benchmark-comparable language.
