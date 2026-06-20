# ExECTv2 v0.42 Dev140 Qwen Same-Raw Ablation Predeclaration

Date: 2026-06-20

## Decision

Run one full dev140 local-Qwen live set for the ADR 0030 target indicators, then
use the saved raw outputs for a no-call same-raw ablation of the quarantined
projection families.

This run is justified as an attribution surface, not as a headline-score
promotion attempt. The previous no-go/defer decision blocked on missing
same-raw attribution. Since then, the projection-family registry, default
quarantine switches, audit replay switches, and dev25 same-raw ablation have
landed. The remaining blocker is that every dev25 keep candidate fires on one
letter; a broader raw-output surface is needed to decide whether those families
are portable enough to keep, remain quarantined, or cut.

## Scope

- Split: `dev`
- Rows: first 140 development letters only
- Indicators: `Diagnosis`, `SeizureFrequency`, `Prescription`,
  `Investigations`
- Prompt/source code condition: current
  `exectv2_target_indicators_single_call_v0.42`
- Model: local `ollama_chat/qwen3.6:35b`
- Runtime: local Ollama native route, `num_ctx=16384`, `num_gpu` unset so
  Ollama may use automatic partial GPU offload
- Projection defaults: quarantined projection families disabled in normal
  prediction; effective switches must be recorded in row diagnostics
- Locked surfaces: no test split, no full-200 audit, no row-level locked-test
  inspection

## Primary Question

On a broader dev140 raw-output surface, do the four dev25 same-raw keep
candidates still improve the paper-comparable benchmark key without degrading
the clinical-fidelity companions?

Keep candidates from dev25:

- `projected_diagnosis_context_to_controlled_sf_state`
- `projected_diagnosis_context_to_remote_last_seizures_state`
- `projected_infrequent_context_state`
- `projected_several_since_last_clinic`

## Required Readouts

Report all surfaces together:

- Headline target F1, overall and by indicator
- Benchmark after CUI projection, overall and by indicator
- `Diagnosis.concept_negation`
- `SeizureFrequency.active_rate_fidelity`
- Per-family fires and marginal deltas versus default quarantine
- Parse/schema failure count and checkpoint/resume status

Do not use headline F1 alone for promotion.

## Stop Rule

No prompt, parser, projection, or scoring changes are allowed after the live
run starts. If the process crashes, resume the same command against the same
artifact path. If the completed artifact shows severe format failure, record it
as a failed local-Qwen condition rather than editing the prompt and rerunning
under the same predeclaration.

Promotion criteria after no-call ablation:

- Candidate families must move benchmark or a fidelity companion in the right
  direction on dev140.
- They must not degrade `Diagnosis.concept_negation` or
  `SeizureFrequency.active_rate_fidelity`.
- Single-letter-only dev140 effects remain insufficient evidence.
- Any promoted family needs a portability label and focused test coverage before
  it returns to default prediction.

## Live Run Command

```powershell
Remove-Item Env:\CLINICAL_EXTRACTION_OLLAMA_NUM_GPU -ErrorAction SilentlyContinue
$env:OPENAI_API_KEY = "ollama"
$env:CLINICAL_EXTRACTION_OLLAMA_NUM_CTX = "16384"

.\.venv\Scripts\python.exe -m clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.run_target_indicators_single_call `
  --split dev `
  --pilot 140 `
  --mode live `
  --model ollama_chat/qwen3.6:35b `
  --api-base http://localhost:11434 `
  --temperature 0 `
  --max-tokens 6000 `
  --no-dspy-cache `
  --resume `
  --progress-every 10 `
  --out-jsonl experiments\exectv2_target_indicators_single_call_v042_live_default_quarantine_dev140_qwen36_35b_ollama_autogpu_ctx16384_20260620.jsonl `
  --out-report experiments\exectv2_target_indicators_single_call_v042_live_default_quarantine_dev140_qwen36_35b_ollama_autogpu_ctx16384_20260620.md
```

## No-Call Ablation Command

```powershell
.\.venv\Scripts\python.exe scripts\phase2_family_ablation.py `
  --source experiments\exectv2_target_indicators_single_call_v042_live_default_quarantine_dev140_qwen36_35b_ollama_autogpu_ctx16384_20260620.jsonl `
  --out-json experiments\exectv2_phase3_family_ablation_same_raw_dev140_qwen36_35b_20260620.json `
  --out-md docs\experiments\exectv2\key_entities\exectv2_phase3_family_ablation_same_raw_dev140_qwen36_35b_20260620.md `
  --date 2026-06-20 `
  --source-note "Live v0.42 local-Qwen dev140 raw output generated under default quarantined projection switches; replay enables one quarantined family at a time for attribution."
```

