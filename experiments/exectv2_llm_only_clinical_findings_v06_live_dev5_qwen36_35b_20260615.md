# ExECTv2 LLM-Only Clinical Findings - SeizureFrequency

- JSONL: `experiments\exectv2_llm_only_clinical_findings_v06_live_dev5_qwen36_35b_20260615.jsonl`
- Pipeline family: `exectv2_llm_only_clinical_findings`
- Prompt version: `exectv2_llm_only_sf_clinical_findings_v0.6`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 5

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Raw model findings: 14
- Evidence-invalid dropped: 1
- Format-projected mentions: 13
- CUI-projected mentions: 13
- Evidence validity rate: 0.9286

## Attribution Layers

### format_projected

- phrase_only per-item F1=0.917 (P=0.846 R=1.000); per-letter F1=1.000
- sf_semantic per-item F1=0.833 (P=0.769 R=0.909); per-letter F1=1.000
- sf_benchmark per-item F1=0.000 (P=0.000 R=0.000); per-letter F1=0.000

### cui_projected

- phrase_only per-item F1=0.917 (P=0.846 R=1.000); per-letter F1=1.000
- sf_semantic per-item F1=0.833 (P=0.769 R=0.909); per-letter F1=1.000
- sf_benchmark per-item F1=0.833 (P=0.769 R=0.909); per-letter F1=1.000
