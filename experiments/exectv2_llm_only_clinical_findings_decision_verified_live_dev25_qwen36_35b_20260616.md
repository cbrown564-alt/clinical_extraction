# ExECTv2 LLM-Only Clinical Findings - SeizureFrequency

- JSONL: `experiments\exectv2_llm_only_clinical_findings_decision_verified_live_dev25_qwen36_35b_20260616.jsonl`
- Pipeline family: `exectv2_llm_only_clinical_findings`
- Prompt version: `exectv2_llm_only_sf_clinical_findings_v0.8`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Verification call failures: 0
- Parse/schema failures: 0
- Verification parse/schema failures: 7
- First-pass findings: 37
- Verified findings: 22
- Final model findings: 36
- Evidence-invalid dropped: 5
- Format-projected mentions: 31
- CUI-projected mentions: 31
- Evidence validity rate: 0.8611

## Attribution Layers

### format_projected

- phrase_only per-item F1=0.710 (P=0.710 R=0.710); per-letter F1=0.824
- sf_semantic per-item F1=0.581 (P=0.581 R=0.581); per-letter F1=0.750
- sf_benchmark per-item F1=0.000 (P=0.000 R=0.000); per-letter F1=0.000

### cui_projected

- phrase_only per-item F1=0.710 (P=0.710 R=0.710); per-letter F1=0.824
- sf_semantic per-item F1=0.581 (P=0.581 R=0.581); per-letter F1=0.750
- sf_benchmark per-item F1=0.581 (P=0.581 R=0.581); per-letter F1=0.750
