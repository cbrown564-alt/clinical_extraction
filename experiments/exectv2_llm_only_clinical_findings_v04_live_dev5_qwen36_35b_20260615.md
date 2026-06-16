# ExECTv2 LLM-Only Clinical Findings - SeizureFrequency

- JSONL: `experiments\exectv2_llm_only_clinical_findings_v04_live_dev5_qwen36_35b_20260615.jsonl`
- Pipeline family: `exectv2_llm_only_clinical_findings`
- Prompt version: `exectv2_llm_only_sf_clinical_findings_v0.4`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 5

## Gate Summary

- Call failures: 0
- Parse/schema failures: 1
- Raw model findings: 7
- Evidence-invalid dropped: 0
- Format-projected mentions: 7
- CUI-projected mentions: 7
- Evidence validity rate: 1.0000

## Attribution Layers

### format_projected

- phrase_only per-item F1=0.667 (P=0.857 R=0.545); per-letter F1=0.889
- sf_semantic per-item F1=0.444 (P=0.571 R=0.364); per-letter F1=0.750
- sf_benchmark per-item F1=0.000 (P=0.000 R=0.000); per-letter F1=0.000

### cui_projected

- phrase_only per-item F1=0.667 (P=0.857 R=0.545); per-letter F1=0.889
- sf_semantic per-item F1=0.444 (P=0.571 R=0.364); per-letter F1=0.750
- sf_benchmark per-item F1=0.444 (P=0.571 R=0.364); per-letter F1=0.750
