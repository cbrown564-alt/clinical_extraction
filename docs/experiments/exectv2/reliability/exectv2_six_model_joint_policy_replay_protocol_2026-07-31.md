# ExECTv2 six-model joint-policy no-call replay protocol

Date: 2026-07-31  
Status: answered; archived after decision 0045 demoted joint/combined  
Result:
[exectv2_six_model_joint_policy_replay_2026-07-31.md](exectv2_six_model_joint_policy_replay_2026-07-31.md)  
Parent policy decision:
[joint bounded policy](exectv2_joint_bounded_policy_replay_2026-07-15.md)

## Primary question

Under the fixed decision-0041 one-call architecture and frozen saved producers,
what are the six-model ExECTv2 `dev140` and aggregate-only `test60`
`clinical_headline` scores when Diagnosis/Prescription assembly uses the
selected joint bounded policy (`combined` / `combined`) instead of the
`default` policy recorded in the retained panel aggregates?

This is a no-call policy reassembly. It does not change prompts, call new
models, or inspect sealed `test60` rows.

## Why this study

The selected comparison policy is joint bounded, but the retained six-model
panel aggregates were assembled under Diagnosis/Prescription `default`. The
Luna prompt-variant thread exposed the gap (Luna test60 `0.7950` default vs
`0.8141` joint on the same sealed raws). A matched six-model joint replay is
required before updating paper-facing comparison tables.

## Fixed conditions

- Models: GPT-4.1-mini, GPT-5.6 Luna, GPT-5.6 Sol, DeepSeek V4 Flash,
  Qwen 3.6:35B, Gemma 4 26B.
- Architecture: decision 0040/0041 single-call.
- Prompt of saved producers: `exectv2_hybrid_key_family_event_ledger_v0.9.24`
  (or the retained local compact variant where that was the frozen condition).
- Call mode: **zero new model calls**; local saved structured + SF suppression
  producers only.
- Policies compared per model/split:
  - `default`: `diagnosis_policy_variant=default`,
    `prescription_policy_variant=default`
  - `joint`: `diagnosis_policy_variant=combined`,
    `prescription_policy_variant=combined`
- Scorer: `clinical_headline` overall and by family.
- `dev140`: row-level inspection permitted; deltas may be summarized without
  promoting row examples into the six-model report.
- `test60`: **aggregate-only**; no letter identifiers, notes, predictions, or
  failure cases may leave sealed storage.

## Producer sources

| Model | `dev140` structured | `test60` structured |
| --- | --- | --- |
| GPT-4.1-mini | `experiments/..._gpt41mini_dev140_20260715_structured.jsonl` | `scratch/holdout/exectv2_test60/gpt41mini/...` |
| GPT-5.6 Luna | `experiments/..._gpt56luna_dev140_20260715_structured.jsonl` | `scratch/holdout/exectv2_test60/gpt56luna/...` |
| GPT-5.6 Sol | `experiments/..._gpt56sol_dev140_20260715_structured.jsonl` | `scratch/holdout/exectv2_test60_sol_credit_v2/gpt56sol/...` (canonical credit-restart) |
| DeepSeek V4 Flash | `experiments/..._deepseek_v4_flash_dev140_20260715_structured.jsonl` | `scratch/holdout/exectv2_test60/deepseek_v4_flash/...` |
| Qwen 3.6:35B | `experiments/..._qwen36_35b_dev140_20260715_structured.jsonl` | `scratch/local_queue/qwen36_35b_exect/test60/qwen36_35b/...` |
| Gemma 4 26B | `experiments/..._gemma4_26b_dev140_20260715_structured.jsonl` | `scratch/local_queue/gemma4_26b_exect/test60/gemma4_26b/...` |

Companion SF `*_sf_unknown_suppression.jsonl` files beside each structured
artifact are required. Sol must use the credit-restart root so the default
reassembly reproduces the retained `0.8047` panel cell.

## Required artifacts

Root: `experiments/exectv2_six_model_joint_policy_replay_20260731/`

| File | Role |
| --- | --- |
| `panel_summary.json` | Default vs joint overall/family F1 for all six models on both splits |
| `dev140_deltas.json` | Aggregate default→joint deltas on development |
| Narrative report under `docs/experiments/exectv2/reliability/` | Answer and claim boundary |

Sealed per-model assembly intermediates for `test60`, if written, stay under
`scratch/holdout/exectv2_six_model_joint_policy_replay_20260731/`.

## Stop rule

- **Answer:** publish matched default and joint six-model aggregates; state
  whether joint changes model order on either split.
- **Negative:** producers missing or default reassembly fails to reproduce a
  retained panel cell within rounding tolerance.
- **Reject:** any live model call, sealed-row inspection, or prompt/scorer
  change.
- After a positive answer, update `PROJECT_STATUS.md` and the six-model
  comparison report to disclose both the historical default panel and the joint
  reassembly, without silently replacing hashes of the frozen default
  aggregates.

## Claim boundary

No-call ExECTv2 policy-reassembly evidence for the named saved producers and
joint bounded Diagnosis/Prescription policy. Not clinical validation, not a
prompt change, and not automatic promotion that erases the historical default
panel provenance.
