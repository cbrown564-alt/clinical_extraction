# ExECTv2 LLM-Only Clinical Findings - SeizureFrequency

- JSONL: `experiments\exectv2_llm_only_clinical_findings_v10_live_dev25_qwen36_35b_20260616.jsonl`
- Pipeline family: `exectv2_llm_only_clinical_findings`
- Prompt version: `exectv2_llm_only_sf_clinical_findings_v0.10`
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
- Verified findings: 33
- Final model findings: 36
- Evidence-invalid dropped: 4
- Format-projected mentions: 32
- CUI-projected mentions: 32
- Evidence validity rate: 0.8889

## Attribution Layers

### format_projected

- phrase_only per-item F1=0.635 (P=0.625 R=0.645); per-letter F1=0.688
- sf_semantic per-item F1=0.603 (P=0.594 R=0.613); per-letter F1=0.645
- sf_benchmark per-item F1=0.000 (P=0.000 R=0.000); per-letter F1=0.000

### cui_projected

- phrase_only per-item F1=0.635 (P=0.625 R=0.645); per-letter F1=0.688
- sf_semantic per-item F1=0.603 (P=0.594 R=0.613); per-letter F1=0.645
- sf_benchmark per-item F1=0.603 (P=0.594 R=0.613); per-letter F1=0.645
