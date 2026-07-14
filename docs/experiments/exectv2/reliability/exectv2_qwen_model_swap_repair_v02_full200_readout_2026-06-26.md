# ExECTv2 Qwen Same-Core Repair v02 Full-200 Aggregate Readout

- Readout date: `2026-06-26`
- Candidate id: `exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_full200`
- Predeclaration: `docs/experiments/exectv2/reliability/exectv2_qwen_repair_v02_full200_predeclaration_2026-06-26.md`
- Frozen core: `exectv2_2call_no_sf_adjudicator_model_swap`
- Model/runtime: `ollama_chat/qwen3.6:35b` / `ollama_chat_think_false_qwen_output_contract_repair_v02`
- Decision: **passes full-200 aggregate stop rule; same-core model-family evidence with aggregate-only boundaries**

## Summary

The authorized same-core full-200 aggregate-only run completed `200/200` rows with
`0` call failures and `0` blocking parse/schema failures across the live
structured and Diagnosis producers. Structured saved-raw replay reports
`0.9950` evidence validity (`1191/1197` scored mentions, `6` evidence-invalid
dropped). Final assembled lane diagnostics report `1.0000` exact evidence for
Diagnosis, SeizureFrequency, Prescription, and Investigations.

Overall `clinical_headline` F1 is `0.8197`, below the already recorded
GPT-4.1-mini (`0.8356`) and DeepSeek (`0.8566`) same-core full-200 rows but
above the predeclared full-200 floor of `0.8000`. This readout does not
retroactively alter the GPT-4.1-mini plus DeepSeek full-200 predeclaration; it
is a separate same-core model-family row.

One Diagnosis call emitted a DSPy truncation warning at `max_tokens=3200`, but
the Diagnosis artifact still completed `200/200` rows with `0` call failures and
`0` parse/schema failures.

## Structured Producer

Artifact:
`experiments/exectv2_2call_no_sf_model_swap_qwen36_repair_v02_full200_20260626_structured.jsonl`

Report:
`experiments/exectv2_2call_no_sf_model_swap_qwen36_repair_v02_full200_20260626_structured.md`

| Evaluation set | Rows | Call failures | Blocking parse/schema failures | Evidence validity |
| --- | ---: | ---: | ---: | ---: |
| structured producer after shared evidence repair | 200 / 200 | 0 | 0 | 0.9950 |

Structured counts:

- clinical events raw: `1168`
- mentions raw: `1197`
- mentions scored: `1191`
- evidence-invalid dropped: `6`

## Downstream Assembly

Artifact:
`experiments/exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_full200_20260626.json`

Report:
`docs/experiments/exectv2/reliability/exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_full200_2026-06-26.md`

| Score view | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| clinical_headline | 0.8197 | 0.8307 | 0.7020 | 0.8926 | 0.8503 |
| evidence_valid | 0.7895 | 0.8307 | 0.5799 | 0.8926 | 0.8503 |
| benchmark_cui companion | 0.4537 overall | diagnostic only | diagnostic only | diagnostic only | diagnostic only |

Final lane diagnostics report `0` call failures, `0` parse/schema failures, and
`1.0000` exact evidence for Diagnosis, SeizureFrequency, Prescription, and
Investigations after the repaired producer artifacts and deterministic replay
components are assembled.

## Aggregate Comparison (diagnostic only)

| Candidate | Overall | SF | Call failures | Parse/schema failures |
| --- | ---: | ---: | ---: | ---: |
| GPT-4.1-mini same-core full-200 | 0.8356 | 0.7525 | 0 | 0 |
| DeepSeek same-core full-200 | 0.8566 | 0.7602 | 0 | 1 |
| Qwen repair v02 same-core full-200 | 0.8197 | 0.7020 | 0 | 0 |

Source for GPT-4.1-mini and DeepSeek rows:
`docs/experiments/exectv2/reliability/exectv2_same_core_model_swap_full200_2026-06-25.md`

## Gate Decision

| Gate | Predeclared threshold | Observed | Decision |
| --- | --- | --- | --- |
| Architecture parity | same frozen core | same config core and live components | pass |
| Operational stability | `0` call failures and `<=1` blocking parse/schema failures | structured and Diagnosis producers `0` / `0`; final lanes `0` / `0` | pass |
| Evidence validity | `>=0.99` exact evidence rate | structured replay `0.9950`; final lane diagnostics `1.0000` | pass |
| Clinical floor | overall `>=0.8000` | overall `0.8197` | pass |

Qwen repair v02 therefore passes the predeclared full-200 aggregate stop rule.
This is same-core model-family evidence with explicit aggregate-only boundaries,
not a strict benchmark or holdout claim. No full-200 row-level failure analysis,
prompt/parser/threshold tuning, or scorer changes are authorized from this
readout.
