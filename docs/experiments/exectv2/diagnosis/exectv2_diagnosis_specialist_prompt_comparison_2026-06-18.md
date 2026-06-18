# ExECTv2 Diagnosis Specialist Prompt Comparison

Date: 2026-06-18  
Split: dev25 only  
Specialist pipeline: `exectv2_llm_only_per_entity`  
Structured comparator: `exectv2_llm_only_key_entities_structured_v0.5`  
Model: `openai/gpt-4.1-mini`

## Decision

The existing specialist Diagnosis prompt is not a better replacement for the
v0.5 single structured prompt. It is useful as a historical focused-frame
baseline, but it underperforms the v0.5 structured prompt on the
objective-aligned Diagnosis clinical-recovery headline:

| Candidate | Diagnosis clinical headline F1 | Precision | Recall | Read |
| --- | ---: | ---: | ---: | --- |
| v0.5 single structured prompt | 0.569 | 0.554 | 0.585 | Current best Diagnosis path. |
| existing per-entity Diagnosis prompt | 0.282 | 0.375 | 0.226 | Not competitive. |

The per-entity prompt had a clean gate (`0` call failures, `0` parse failures,
evidence validity `1.0000`) and lifted source-near recall versus the old all-9
baseline (`+0.089`), but its candidate recall and assertion agreement are too
low for the current key-entity goal.

## Implication

The first multi-prompt comparison rejects the existing specialist Diagnosis
prompt as-is. The next architectural step should not be a rollback to the old
per-entity frame; it should either:

1. build a new Diagnosis-specialist prompt using the v0.5 structured diagnosis
   guidance as the starting point, or
2. keep the v0.5 single structured prompt and add a lightweight verifier/repair
   prompt only for Diagnosis concept spans and certainty.

Either option must preserve the attribution rule: the model owns the clinical
selection, while deterministic code remains limited to schema/evidence gates,
neutral projection, and scoring.
