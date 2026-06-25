# ExECTv2 Qwen Same-Core Output-Contract Audit

- Generated: `2026-06-25`
- Candidate: `exectv2_2call_no_sf_adjudicator_qwen36_dev140`
- Model/runtime: `ollama_chat/qwen3.6:35b` / `ollama_chat_think_false`
- Architecture core: `exectv2_2call_no_sf_adjudicator_model_swap`
- Scope: dev140 row-level audit only
- Row inspection boundary: no full-200 or holdout row-level inspection

## Decision

Qwen should remain a same-core diagnostic row, not an operationally promoted
model-swap candidate for the next full-200 predeclaration. The failures are not
a local runtime outage: the run completed and most rows produced scored,
evidence-valid mentions. They are also not harmless aggregate-only noise because
the failures cluster in Qwen-specific output-contract violations and include
instruction-following drift in the raw failed Diagnosis rows.

If Qwen is revisited, do it as a Qwen-specific prompt/runtime-adapter repair on
the frozen core, with a dev140 rerun before any full-200 aggregate-only protocol.
Do not silently include Qwen in the next full-200 same-core candidate set.

## Counted Readiness Failures

| Producer | Counted failure rows | Letter ids | Classification |
| --- | ---: | --- | --- |
| `structured_key_family_event_ledger` | 1 call failure / 1 parse-schema failure | `EA0118` | Output-wrapper/adapter contract failure. The model returned a `clinical_events` JSON-looking object, but DSPy `JSONAdapter` expected the `extraction_json` output field and raised `AdapterParseError`; the row then recorded `parse_errors=["not_run"]`. |
| `diagnosis_decomposer` | 11 parse-schema failures | `EA0032`, `EA0055`, `EA0057`, `EA0075`, `EA0076`, `EA0081`, `EA0087`, `EA0103`, `EA0117`, `EA0137`, `EA0139` | Qwen-specific output-contract limitation. Failures are malformed JSON, Python-literal/single-quote payloads, top-level array/envelope drift, and reasoning leakage into the returned object. |

The assembly-level readiness artifact counts Qwen as `1` call failure and `12`
parse/schema failures because the structured `EA0118` row contributes both a
call failure and a blocking parse status, while the Diagnosis decomposer
contributes eleven additional blocking parse rows.

## Failure Taxonomy

| Class | Rows | Evidence from raw failed outputs | Interpretation |
| --- | --- | --- | --- |
| Python-literal or single-quote JSON dialect | `EA0055`, `EA0076`, `EA0081`, `EA0103`, `EA0117`, `EA0139` | Returned payloads use single-quoted dict/list syntax such as `{'mentions': ...}`. | Format-preserving repair may be possible, but the current Diagnosis parser treats these as blocking invalid JSON. |
| Top-level envelope or shape drift | `EA0087`, `EA0137` | Returned a bare list instead of the required `{"mentions": [...]}` object. | Adapter/prompt contract weakness; repair would need explicit Qwen handling or parser coercion. |
| Reasoning leakage / malformed JSON continuation | `EA0032`, `EA0057`, `EA0075`, `EA0137` | Raw output includes deliberative text or duplicate partial objects inside/after the payload, causing delimiter or control-character parse failures. | Model instruction-following limitation, not just a local JSON parser issue. |
| DSPy output-field mismatch | `EA0118` | Response had `clinical_events`, but the adapter reported missing expected field `extraction_json`. | Runtime adapter incompatibility for this model/profile; the row is unusable under the frozen run contract. |

## Non-Blocking Noise Separated From Failures

The structured producer has many non-blocking repair/coercion notes such as
`json_dialect_repaired: python_literal`, `coerced_attribute_value`, normalized
drug casing, repaired evidence from mention text, and dropped illegal
attributes. These are not the readiness-gate failures counted above because they
still produced usable rows. The audit separates them from the hard rows with
zero scored output or a blocking adapter failure.

## Operational Status

- Architecture parity remains intact: all model rows use the frozen same-core
  graph.
- Evidence validity for scored Qwen mentions remains `1.0000`.
- Operational stability is not promoted for Qwen.
- Next same-core full-200 predeclaration should default to GPT-4.1-mini plus
  DeepSeek. Include Qwen only as an explicitly caveated diagnostic row, or after
  a predeclared Qwen-specific adapter/prompt repair passes dev140 on the frozen
  core.

