# ExECTv2 LLM-Only Clinical Findings - SeizureFrequency

- JSONL: `experiments\exectv2_llm_only_clinical_findings_v08_live_dev25_qwen36_35b_20260615.jsonl`
- Pipeline family: `exectv2_llm_only_clinical_findings`
- Prompt version: `exectv2_llm_only_sf_clinical_findings_v0.8`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Raw model findings: 37
- Evidence-invalid dropped: 4
- Format-projected mentions: 33
- CUI-projected mentions: 33
- Evidence validity rate: 0.8919

## Attribution Layers

### format_projected

- phrase_only per-item F1=0.625 (P=0.606 R=0.645); per-letter F1=0.788
- sf_semantic per-item F1=0.531 (P=0.515 R=0.548); per-letter F1=0.710
- sf_benchmark per-item F1=0.000 (P=0.000 R=0.000); per-letter F1=0.000

### cui_projected

- phrase_only per-item F1=0.625 (P=0.606 R=0.645); per-letter F1=0.788
- sf_semantic per-item F1=0.531 (P=0.515 R=0.548); per-letter F1=0.710
- sf_benchmark per-item F1=0.531 (P=0.515 R=0.548); per-letter F1=0.710
