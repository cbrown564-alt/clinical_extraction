# ExECTv2 Qwen Same-Core Repair v01 Dev140 Readout

- Generated: `2026-06-25`
- Predeclaration: `docs/experiments/exectv2/reliability/exectv2_qwen_model_swap_repair_v01_predeclaration_2026-06-25.md`
- Candidate id: `exectv2_2call_no_sf_adjudicator_qwen36_repair_v01_dev140`
- Config: `configs/exectv2/model_swap/exectv2_2call_no_sf_adjudicator_qwen36_repair_v01_dev140.json`
- Architecture core: `exectv2_2call_no_sf_adjudicator_model_swap`
- Model/runtime: `ollama_chat/qwen3.6:35b` / `ollama_chat_think_false_qwen_output_contract_repair_v01`
- Split/scope: dev140, early-stopped after structured producer checkpoint
- Row inspection boundary: dev140 row-level inspection only; no full-200 or holdout row-level inspection

## Decision

Qwen repair v01 **does not pass** the frozen-core dev140 operational gate. The
run was stopped after `50/140` structured-producer rows because the predeclared
promotion gate required `0` blocking parse/schema failures, and two blocking
schema/parse failures had already occurred. Since the gate was already
unrecoverable, the full two-call assembly was not completed.

Qwen remains diagnostic-only for same-core model-swap evidence. Do not include
Qwen in the next same-core full-200 aggregate-only predeclaration unless a fresh
v02 repair is predeclared and passes dev140.

## What Was Tested

Repair v01 added:

- shared ExECTv2 parser support for format-preserving JSON dialect repair:
  Python-literal dict/list syntax, literal-control-character JSON loading, and
  top-level mention-list coercion
- a Qwen compact Diagnosis output-contract reminder
- runtime-adapter fallback that recovers a DSPy adapter-parse exception when the
  exception contains a complete `LM Response` payload
- a separate `qwen36_repair_v01` model-swap config and artifact namespace

The architecture core, row count, model-owned live components, deterministic SF
chain, Prescription repair, lenses, scorer, and claim boundary remained frozen.

## Runtime Health

The first attempts were invalid because local Ollama was not reliably serving
Qwen and produced connection-refused rows. After local runtime recovery, a
native Qwen probe on `http://127.0.0.1:11434` passed:

- response: `OK`
- `context_length`: `12288`
- `size_vram`: `4844263832`
- NVIDIA memory used: approximately `4793` MiB

The reported repair-v01 checkpoint below is from the clean GPU-backed run
against that healthy endpoint.

## Early-Stop Checkpoint

Artifact:
`experiments/exectv2_2call_no_sf_model_swap_qwen36_repair_v01_dev140_20260625_structured.jsonl`

| Checkpoint | Rows | Call failures | Blocking parse/schema failures | Evidence validity |
| --- | ---: | ---: | ---: | ---: |
| structured producer | 50 / 140 | 0 | 2 | 0.9639 |

The structured checkpoint report recorded:

- clinical events raw: `288`
- mentions raw: `277`
- mentions scored: `267`
- evidence-invalid dropped: `10`

## Blocking Rows

| Letter id | Failure | Interpretation |
| --- | --- | --- |
| `EA0007` | `schema_validation_error` because `clinical_events.0.family` was `diabetes`, outside the allowed `medication | diagnosis | seizure_frequency | investigation` enum. | Not a JSON dialect issue. Qwen emitted a non-target family and a non-target `Diabetes` mention inside a Diagnosis-shaped event. |
| `EA0035` | `invalid_json: Invalid control character at` on a long structured response. | Still an output-contract failure under v01. It may be repairable by a stricter event-object extractor or sanitizer, but that would require a v02 predeclaration. |

## Gate Result

| Gate | Required | Result | Status |
| --- | --- | --- | --- |
| Architecture parity | frozen same-core graph | unchanged config signature versus baseline Qwen | pass |
| Operational stability | `0` call failures and `0` blocking parse/schema failures | `0` call failures, `2` blocking parse/schema failures by 50 rows | fail |
| Evidence validity | `>=0.99` minimum exact evidence rate | structured checkpoint `0.9639` | fail at checkpoint |
| Clinical non-regression | complete dev140 overall `>=0.8018`, SF `>=0.6919` | not evaluated because operational gate failed before completion | not run |

## Next Action

Default next same-core full-200 candidate set remains GPT-4.1-mini plus DeepSeek.
Qwen can be revisited only with a fresh v02 predeclaration. A plausible v02
would need to decide explicitly whether dropping invalid event-family objects or
extracting later valid objects from a malformed response is format-only schema
repair or a semantic adapter, then test that boundary on dev140 before any
full-200 inclusion.
