# ExECTv2 LLM-Only Clinical Findings - SeizureFrequency

- JSONL: `experiments\exectv2_llm_only_clinical_findings_v02b_live_dev1_qwen36_35b_20260615.jsonl`
- Pipeline family: `exectv2_llm_only_clinical_findings`
- Prompt version: `exectv2_llm_only_sf_clinical_findings_v0.2`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 1

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Raw model findings: 2
- Evidence-invalid dropped: 0
- Format-projected mentions: 2
- CUI-projected mentions: 2
- Evidence validity rate: 1.0000

## Attribution Layers

### format_projected

- phrase_only per-item F1=1.000 (P=1.000 R=1.000); per-letter F1=1.000
- sf_semantic per-item F1=1.000 (P=1.000 R=1.000); per-letter F1=1.000
- sf_benchmark per-item F1=0.000 (P=0.000 R=0.000); per-letter F1=0.000

### cui_projected

- phrase_only per-item F1=1.000 (P=1.000 R=1.000); per-letter F1=1.000
- sf_semantic per-item F1=1.000 (P=1.000 R=1.000); per-letter F1=1.000
- sf_benchmark per-item F1=1.000 (P=1.000 R=1.000); per-letter F1=1.000
