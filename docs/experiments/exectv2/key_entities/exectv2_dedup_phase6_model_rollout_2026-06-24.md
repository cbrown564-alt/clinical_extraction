# ExECTv2 Deduplicated Clinical Facts Phase 6 Model Rollout

Date: 2026-06-24

## Question

The mixed `decision_table_sf_inv` prompt profile was good enough on GPT-4.1-mini
dev140 to answer a cross-model transfer question, even though it did not clear
the original `>0.900` clinical-recovery target. Phase 6 therefore ran the same
configuration unchanged on DeepSeek and Qwen:

- call strategy: `single_call_dedup_facts_per_family`
- prompt profile: `decision_table_sf_inv`
- split/surface: ExECTv2 dev140, canonical `clinical_headline`
- attribution: model-emitted facts only; deterministic code validates evidence,
  maps representation one-to-one, and scores

## Results

| Model | Clinical headline F1 | P | R | Diagnosis | SF | Rx | Inv | Strict F1 | Evidence validity | Failures |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| GPT-4.1-mini | 0.729 | 0.753 | 0.707 | 0.681 | 0.556 | 0.851 | 0.883 | 0.130 | 0.9694 | 0 |
| DeepSeek chat | 0.745 | 0.719 | 0.772 | 0.689 | 0.674 | 0.788 | 0.898 | 0.128 | 0.9617 | 0 |
| Qwen 3.6 35B | 0.694 | 0.680 | 0.708 | 0.633 | 0.562 | 0.795 | 0.837 | 0.127 | 0.9418 | 0 |

Primary artifacts:

- GPT-4.1-mini:
  `experiments/exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_per_family_phase4_decision_table_sf_inv_dev140_gpt41mini_20260624.{jsonl,md}`
- DeepSeek:
  `experiments/exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_per_family_phase6_seq_decision_table_sf_inv_dev140_deepseek_chat_20260624.{jsonl,md}`
- Qwen:
  `experiments/exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_per_family_phase6_seq_decision_table_sf_inv_dev140_qwen36_side11435_20260624.{jsonl,md}`

Qwen was run through native Ollama chat on the CUDA-forced side server
`http://127.0.0.1:11435`, model tag `qwen3.6:35b`, digest
`07d35212591fc27746f0a317c975a6d68754fb38e9053d82e25f06057af28522`,
Q4_K_M, context length `12288`, with `think=false` and no DSPy cache. The
earlier `http://localhost:11434` attempt failed before endpoint repair and is
not used as a result artifact.

## Interpretation

DeepSeek transferred slightly better than GPT-4.1-mini overall (`0.745` vs
`0.729`) and gave the clearest SeizureFrequency lift (`0.674` vs `0.556`), but
it still remained far below the v08 hybrid control (`0.9155`) and below the
original `>0.900` LLM-only target.

Qwen under the same direct de-duplicated fact prompt scored lower overall
(`0.694`) than GPT-4.1-mini and lower than its earlier clean-render replay
baseline on the de-duplicated surface (`0.7215`). Its largest residuals remain
Diagnosis granularity and SeizureFrequency state selection, with lower evidence
validity (`0.9418`) than GPT and DeepSeek.

The strict `model_preserving_canonical` scores remain diagnostic only
(`0.127`-`0.130`) for all three runs, confirming that these direct
de-duplicated clinical-fact prompts are clinical-recovery experiments rather
than strict benchmark-reproduction systems.

## Conclusion

Phase 6 answers the transfer question without changing the plateau conclusion:
model swap alone does not close the gap. DeepSeek is the best direct
LLM-only `decision_table_sf_inv` condition on dev140, but the remaining errors
are still prediction-bearing Diagnosis and SeizureFrequency decisions. Any
future improvement should be framed as a new architecture, ontology supervision
experiment, projection-aware analysis, or hybrid/selector-owned system rather
than a continuation of the same prompt ladder.
