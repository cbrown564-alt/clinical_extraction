# ExECTv2 LLM-Only Clinical Findings - SeizureFrequency

- JSONL: `experiments\exectv2_llm_only_clinical_findings_v06_live_dev25_qwen36_35b_20260615.jsonl`
- Pipeline family: `exectv2_llm_only_clinical_findings`
- Prompt version: `exectv2_llm_only_sf_clinical_findings_v0.6`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Raw model findings: 45
- Evidence-invalid dropped: 4
- Format-projected mentions: 41
- CUI-projected mentions: 41
- Evidence validity rate: 0.9111

## Attribution Layers

### format_projected

- phrase_only per-item F1=0.556 (P=0.488 R=0.645); per-letter F1=0.625
- sf_semantic per-item F1=0.389 (P=0.342 R=0.452); per-letter F1=0.533
- sf_benchmark per-item F1=0.000 (P=0.000 R=0.000); per-letter F1=0.000

### cui_projected

- phrase_only per-item F1=0.556 (P=0.488 R=0.645); per-letter F1=0.625
- sf_semantic per-item F1=0.389 (P=0.342 R=0.452); per-letter F1=0.533
- sf_benchmark per-item F1=0.389 (P=0.342 R=0.452); per-letter F1=0.533
