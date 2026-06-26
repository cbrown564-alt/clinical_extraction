# ExECTv2 LLM-Only Clinical Findings - SeizureFrequency

- JSONL: `experiments\exectv2_llm_only_clinical_findings_v14_action_revise_live_dev25_qwen36_35b_20260616.jsonl`
- Pipeline family: `exectv2_llm_only_clinical_findings`
- Prompt version: `exectv2_llm_only_sf_clinical_findings_v0.14`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Verification call failures: 0
- Parse/schema failures: 0
- Verification parse/schema failures: 2
- First-pass findings: 38
- Verified findings: 29
- Final model findings: 34
- Evidence-invalid dropped: 1
- Format-projected mentions: 33
- CUI-projected mentions: 33
- Evidence validity rate: 0.9706

## Attribution Layers

### format_projected

- phrase_only per-item F1=0.688 (P=0.667 R=0.710); per-letter F1=0.839
- sf_semantic per-item F1=0.656 (P=0.636 R=0.677); per-letter F1=0.800
- sf_benchmark per-item F1=0.000 (P=0.000 R=0.000); per-letter F1=0.000

### cui_projected

- phrase_only per-item F1=0.688 (P=0.667 R=0.710); per-letter F1=0.839
- sf_semantic per-item F1=0.656 (P=0.636 R=0.677); per-letter F1=0.800
- sf_benchmark per-item F1=0.656 (P=0.636 R=0.677); per-letter F1=0.800
