# ExECTv2 Key-Entity dev140 Transfer Readout

Date: 2026-06-18  
Split: dev140  
Model: `openai/gpt-4.1-mini`  
Draft: `exectv2_llm_only_key_entities_structured_v0.5`  
Verifiers: Diagnosis v0.5, SeizureFrequency v0.3

## Decision

The dev25 target-clearing configuration does not transfer to dev140. Treat the
dev25 result as a useful development signal, not as a promoted architecture.

| Family | Candidate used | dev25 F1 | dev140 F1 | dev140 P | dev140 R | Gate |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Prescription | single structured v0.5 | 0.897 | 0.777 | 0.768 | 0.788 | 0 call/parse failures |
| Diagnosis | verifier v0.5 | 0.837 | 0.616 | 0.680 | 0.564 | 0 call/parse failures; evidence 0.9832 |
| SeizureFrequency | verifier v0.3 | 0.831 | 0.602 | 0.594 | 0.610 | 0 call/parse failures; evidence 0.9796 |
| Investigations | single structured v0.5 | 0.837 | 0.786 | 0.752 | 0.824 | 0 call/parse failures |

The broad draft run was operationally clean (`0` call failures, `0` parse
failures, evidence validity `0.9563`) but all four key-family headlines are now
below `0.8` on dev140. Medication and Investigations are near misses; Diagnosis
and SeizureFrequency require broader error-analysis-led development.

## Interpretation

The single structured schema remains valuable as a substrate: it gives exact
evidence, family-level drafts, and high source-near signal. The verifier pattern
also improves Diagnosis and SeizureFrequency over the single structured dev140
draft, but not enough:

| Family | Single structured dev140 F1 | Verifier dev140 F1 | Delta |
| --- | ---: | ---: | ---: |
| Diagnosis | 0.525 | 0.616 | +0.091 |
| SeizureFrequency | 0.558 | 0.602 | +0.044 |

The result argues against more dev25 prompt accretion. The next loop should use
dev140 residual slices and distinguish source coverage, concept normalization,
attribute/state rendering, and over-emission separately.

## Next Iteration

1. Build dev140 error ledgers for all four key families using the clinical
   recovery keys, not only source-near overlap.
2. Triage near-target medication and Investigations first for low-risk precision
   and recall fixes.
3. Redesign Diagnosis and SeizureFrequency prompts from dev140 residual families,
   possibly with narrower specialist prompts or verifier/checker decomposition.
4. Keep component ownership explicit: single structured draft, specialist
   verifier output, deterministic evidence gate, and CUI projection remain
   separate reported layers.
