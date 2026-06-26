# ExECTv2 Qwen Same-Core Repair v02 Dev140 Readout

- Readout date: `2026-06-25`
- Candidate id: `exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_dev140`
- Predeclaration: `docs/experiments/exectv2/reliability/exectv2_qwen_model_swap_repair_v02_predeclaration_2026-06-25.md`
- Frozen core: `exectv2_2call_no_sf_adjudicator_model_swap`
- Model/runtime: `ollama_chat/qwen3.6:35b` / `ollama_chat_think_false_qwen_output_contract_repair_v02`
- Decision: **passes dev140 v02 gates; eligible for a fresh full-200 decision/predeclaration**

## Summary

Repair v02 addressed the two v01 blocking structured-output failures as
predeclared:

- `EA0007`-style out-of-enum clinical events are dropped rather than coerced.
- `EA0035`-style malformed non-scored `rationale` text can be blanked before
  JSON/schema validation.

The concrete v01 failure payloads both parse under v02 regression tests. The
live v02 structured producer completed `140/140` rows with `0` call failures
and `0` parse/schema failures. After adding the shared standard evidence-repair
family, the saved structured raw outputs replay to `0.9964` evidence validity.
The downstream same-core assembly then completed successfully.

## Structured Producer

Artifact:
`experiments/exectv2_2call_no_sf_model_swap_qwen36_repair_v02_dev140_20260625_structured.jsonl`

Report:
`experiments/exectv2_2call_no_sf_model_swap_qwen36_repair_v02_dev140_20260625_structured.md`

| Surface | Rows | Call failures | Blocking parse/schema failures | Evidence validity |
| --- | ---: | ---: | ---: | ---: |
| structured producer after shared evidence repair | 140 / 140 | 0 | 0 | 0.9964 |

Structured counts:

- clinical events raw: `817`
- mentions raw: `827`
- mentions scored: `824`
- evidence-invalid dropped: `3`

The remaining three evidence-invalid mentions are one source typo normalization
case (`Sine`/`Since`) and two EA0114 carbamazepine rows where Qwen appended a
sentence not present in the source.

## Downstream Assembly

Artifact:
`experiments/exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_dev140_20260625.json`

Report:
`docs/experiments/exectv2/reliability/exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_dev140_2026-06-25.md`

| Surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| clinical_headline | 0.8319 | 0.8473 | 0.7182 | 0.8895 | 0.8755 |
| evidence_valid | 0.8049 | 0.8473 | 0.6126 | 0.8895 | 0.8755 |

Final lane diagnostics report `0` call failures, `0` parse/schema failures, and
`1.0000` exact evidence for Diagnosis, SeizureFrequency, Prescription, and
Investigations after the repaired producer artifacts and deterministic replay
components are assembled.

The completed rerun emitted a DSPy truncation warning for one Diagnosis call
(`max_tokens=3200`), but the Diagnosis artifact completed `140/140` rows with
`0` call failures and `0` parse/schema failures.

## Gate Decision

| Gate | Predeclared threshold | Observed | Decision |
| --- | --- | --- | --- |
| Architecture parity | same frozen core | same config core and live components | pass |
| Operational stability | `0` call failures and `0` blocking parse/schema failures | structured and Diagnosis producers `0` / `0`; final lanes `0` / `0` | pass |
| Evidence validity | `>=0.99` exact evidence rate | structured replay `0.9964`; final lane diagnostics `1.0000` | pass |
| Clinical non-regression | overall `>=0.8018`, SF `>=0.6919` | overall `0.8319`; SF `0.7182` | pass |

Qwen repair v02 therefore passes the predeclared dev140 repair gates. This
readout does not retroactively alter the already-written GPT-4.1-mini plus
DeepSeek full-200 predeclaration; it supports a fresh decision on whether to
add Qwen v02 to a same-core full-200 candidate set.

## Repair Family Added

The shared evidence gate now applies standard source-exact evidence repair
before dropping a mention:

- case plus whitespace drift
- escaped tab/newline drift
- bounded `...` omission repair when it resolves to one exact source span
- section-header plus selected list-item repair when it resolves to one exact
  source section span

These repairs are source-exact: the repaired evidence must be an actual
contiguous source substring. They do not introduce or reinterpret clinical
facts.
