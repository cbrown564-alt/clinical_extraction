# ExECTv2 LLM-Only Clinical Findings - SeizureFrequency

- JSONL: `experiments\exectv2_llm_only_clinical_findings_v08_live_dev10_qwen36_35b_20260615.jsonl`
- Pipeline family: `exectv2_llm_only_clinical_findings`
- Prompt version: `exectv2_llm_only_sf_clinical_findings_v0.8`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 10

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Raw model findings: 19
- Evidence-invalid dropped: 2
- Format-projected mentions: 17
- CUI-projected mentions: 17
- Evidence validity rate: 0.8947

## Attribution Layers

### format_projected

- phrase_only per-item F1=0.769 (P=0.882 R=0.682); per-letter F1=1.000
- sf_semantic per-item F1=0.718 (P=0.824 R=0.636); per-letter F1=1.000
- sf_benchmark per-item F1=0.000 (P=0.000 R=0.000); per-letter F1=0.000

### cui_projected

- phrase_only per-item F1=0.769 (P=0.882 R=0.682); per-letter F1=1.000
- sf_semantic per-item F1=0.718 (P=0.824 R=0.636); per-letter F1=1.000
- sf_benchmark per-item F1=0.718 (P=0.824 R=0.636); per-letter F1=1.000
