# ExECTv2 LLM-Only Clinical Findings - SeizureFrequency

- JSONL: `experiments\exectv2_llm_only_clinical_findings_v07_live_dev10_qwen36_35b_20260615.jsonl`
- Pipeline family: `exectv2_llm_only_clinical_findings`
- Prompt version: `exectv2_llm_only_sf_clinical_findings_v0.7`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 10

## Gate Summary

- Call failures: 0
- Parse/schema failures: 1
- Raw model findings: 20
- Evidence-invalid dropped: 2
- Format-projected mentions: 18
- CUI-projected mentions: 18
- Evidence validity rate: 0.9000

## Attribution Layers

### format_projected

- phrase_only per-item F1=0.800 (P=0.889 R=0.727); per-letter F1=0.941
- sf_semantic per-item F1=0.650 (P=0.722 R=0.591); per-letter F1=0.941
- sf_benchmark per-item F1=0.000 (P=0.000 R=0.000); per-letter F1=0.000

### cui_projected

- phrase_only per-item F1=0.800 (P=0.889 R=0.727); per-letter F1=0.941
- sf_semantic per-item F1=0.650 (P=0.722 R=0.591); per-letter F1=0.941
- sf_benchmark per-item F1=0.650 (P=0.722 R=0.591); per-letter F1=0.941
