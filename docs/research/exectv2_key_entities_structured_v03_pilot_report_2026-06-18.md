# ExECTv2 Key-Entity Structured Prompt v0.3 Pilot

Date: 2026-06-18  
Split: dev25 only  
Pipeline: `exectv2_llm_only_key_entities_structured`  
Model: `openai/gpt-4.1-mini`

## Decision

v0.3 is a revise-only prompt iteration. It validates two parts of the
single-prompt structured-event path: Prescription/medication now clears the
clinical-recovery headline target (`0.883` F1), and Investigations clears it
after precision cleanup (`0.878` F1). Diagnosis improved modestly (`0.414 ->
0.455`), but SeizureFrequency slipped (`0.456 -> 0.421`), so the candidate is
not ready for dev140.

The run remains schema-clean (`0` call failures, `0` parse failures), but the
stricter prompt lowered evidence validity from `0.9760` to `0.9441`. That is a
real regression to keep in the gate for v0.4.

## v0.2 -> v0.3 Comparison

| Layer | v0.2 item F1 | v0.3 item F1 | Delta |
| --- | ---: | ---: | ---: |
| source-near | 0.680 | 0.718 | +0.038 |
| phrase-only | 0.408 | 0.436 | +0.028 |
| semantic | 0.272 | 0.282 | +0.010 |
| benchmark | 0.220 | 0.235 | +0.015 |

| Entity | v0.2 clinical F1 | v0.3 clinical F1 | Read |
| --- | ---: | ---: | --- |
| Prescription | 0.846 | 0.883 | Above target; protect. |
| Diagnosis | 0.414 | 0.455 | Improved, but still far below target. |
| SeizureFrequency | 0.456 | 0.421 | Regressed despite better source-near overlap. |
| Investigations | 0.783 | 0.878 | Above target after FP cleanup. |

## Error-Analysis Read

The v0.3 prompt targeted the observed v0.2 misses: diagnosis uncertainty and
generic symptoms, generic-versus-specific seizure anchors, interval/cluster
frequency statements, frequency-change-only mentions, and investigation
over-emission. This helped precision-heavy families: Prescription and
Investigations now exceed `0.8`.

The SeizureFrequency result shows that prompt breadth alone is not enough. The
source-near SF F1 rose (`0.632 -> 0.737`), but headline state recovery fell,
which means the model is finding more plausible frequency anchors while still
choosing the wrong clinical state or seizure concept often enough to lose the
objective metric.

## Next Iteration

Do not spend dev140 yet. Build v0.4 on dev25 with a narrower SF/Diagnosis focus:

1. Preserve v0.3 medication and investigation instructions.
2. Audit v0.3 SeizureFrequency headline misses by state family:
   active-rate, seizure-free, unknown/frequency-change, and cluster.
3. Add only targeted SF prompt changes that can be traced to those miss families;
   avoid adding more broad examples unless they reduce a named miss class.
4. Continue Diagnosis work on certainty calibration and specific syndrome
   preservation, but do not let symptom/non-epileptic FP suppression hide true
   named seizure-type recall.
