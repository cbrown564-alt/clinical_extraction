# ExECTv2 Key-Entity Structured Prompt v0.4 Pilot

Date: 2026-06-18  
Split: dev25 only  
Pipeline: `exectv2_llm_only_key_entities_structured`  
Model: `openai/gpt-4.1-mini`

## Decision

v0.4 is the best single-prompt structured-event dev25 candidate so far, but it is
not promoted to dev140. It validates the error-analysis-led narrowing after
v0.3: SeizureFrequency clinical-recovery headline F1 recovered from `0.421` to
`0.644`, while Prescription/medication (`0.900`) and Investigations (`0.837`)
remain above the `0.8` target.

Diagnosis remains the limiting family at `0.460` F1. The next loop should focus
on Diagnosis concept identity and certainty, with only regression-protection
changes for the other families.

## v0.3 -> v0.4 Comparison

| Layer | v0.3 item F1 | v0.4 item F1 | Delta |
| --- | ---: | ---: | ---: |
| source-near | 0.718 | 0.728 | +0.010 |
| phrase-only | 0.436 | 0.446 | +0.010 |
| semantic | 0.282 | 0.295 | +0.013 |
| benchmark | 0.235 | 0.256 | +0.021 |

| Entity | v0.3 clinical F1 | v0.4 clinical F1 | Read |
| --- | ---: | ---: | --- |
| Prescription | 0.883 | 0.900 | Above target; protect. |
| Diagnosis | 0.455 | 0.460 | Still the bottleneck. |
| SeizureFrequency | 0.421 | 0.644 | Large recovery from targeted SF prompt fixes. |
| Investigations | 0.878 | 0.837 | Still above target; protect precision. |

## Error-Analysis Read

The v0.4 rules were deliberately narrow: approximate count words, last-event as
seizure-free, exclusion of non-epileptic events/blackouts from SF, and preserving
full seizure-type modifiers. The result confirms that the single structured
prompt can internalize a clinically meaningful SF decomposition without adding
deterministic semantic repair.

Diagnosis barely improved because the remaining failures are less about one or
two lexical rules and more about concept projection: exact syndrome specificity,
uncertainty calibration, seizure-type multiplicity, and deciding when named
events are true epilepsy diagnoses versus contextual history.

## Next Iteration

Do not spend dev140 yet. Build v0.5 on dev25 with Diagnosis as the primary
target:

1. Keep v0.4 medication, investigation, and SF rules unless a targeted error
   row proves a regression cause.
2. Create a Diagnosis hard-case panel from v0.4 misses: syndrome specificity,
   certainty 3/4, tonic-clonic wording, altered-awareness modifiers,
   non-epileptic/dissociative mentions, and duplicate seizure-type mentions.
3. If prompt-only Diagnosis remains below `0.6`, compare the single-prompt path
   against a specialist Diagnosis prompt before adding verifier stages.
