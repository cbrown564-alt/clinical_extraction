# ExECTv2 LLM-Only Clinical Findings - SeizureFrequency

- JSONL: `experiments\exectv2_llm_only_clinical_findings_v02b_live_dev5_qwen36_35b_20260615.jsonl`
- Pipeline family: `exectv2_llm_only_clinical_findings`
- Prompt version: `exectv2_llm_only_sf_clinical_findings_v0.2`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 5

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Raw model findings: 8
- Evidence-invalid dropped: 0
- Format-projected mentions: 8
- CUI-projected mentions: 8
- Evidence validity rate: 1.0000

## Attribution Layers

### format_projected

- phrase_only per-item F1=0.632 (P=0.750 R=0.545); per-letter F1=1.000
- sf_semantic per-item F1=0.316 (P=0.375 R=0.273); per-letter F1=0.571
- sf_benchmark per-item F1=0.000 (P=0.000 R=0.000); per-letter F1=0.000

### cui_projected

- phrase_only per-item F1=0.632 (P=0.750 R=0.545); per-letter F1=1.000
- sf_semantic per-item F1=0.316 (P=0.375 R=0.273); per-letter F1=0.571
- sf_benchmark per-item F1=0.316 (P=0.375 R=0.273); per-letter F1=0.571
