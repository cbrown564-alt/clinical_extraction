# ExECTv2 LLM-Only Clinical Findings - SeizureFrequency

- JSONL: `experiments\exectv2_llm_only_clinical_findings_v16_family_checklist_live_dev25_qwen36_35b_20260616.jsonl`
- Pipeline family: `exectv2_llm_only_clinical_findings`
- Prompt version: `exectv2_llm_only_sf_clinical_findings_v0.16`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Verification call failures: 0
- Parse/schema failures: 0
- Verification parse/schema failures: 1
- First-pass findings: 36
- Verified findings: 33
- Final model findings: 35
- Evidence-invalid dropped: 1
- Format-projected mentions: 34
- CUI-projected mentions: 34
- Evidence validity rate: 0.9714

## Attribution Layers

### format_projected

- phrase_only per-item F1=0.708 (P=0.676 R=0.742); per-letter F1=0.903
- sf_semantic per-item F1=0.615 (P=0.588 R=0.645); per-letter F1=0.828
- sf_benchmark per-item F1=0.000 (P=0.000 R=0.000); per-letter F1=0.000

### cui_projected

- phrase_only per-item F1=0.708 (P=0.676 R=0.742); per-letter F1=0.903
- sf_semantic per-item F1=0.615 (P=0.588 R=0.645); per-letter F1=0.828
- sf_benchmark per-item F1=0.615 (P=0.588 R=0.645); per-letter F1=0.828
