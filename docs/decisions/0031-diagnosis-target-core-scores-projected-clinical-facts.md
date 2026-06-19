# Diagnosis Target Core Scores Projected Clinical Facts

Date: 2026-06-19

## Status

Accepted.

## Context

ADR 0030 fixed the ExECTv2 Plan 11 target surface to four indicators:
`Diagnosis`, `SeizureFrequency`, `Prescription`, and `Investigations`.
During the first single-call target run, Diagnosis was reported through the
existing ExECT clinical-recovery concept score. That score is useful as a
legacy comparator, but it is not the intended Plan 11 target definition when
surface-form variation obscures the same clinically relevant diagnosis fact.

The Gan 2026 reliability work separated raw model output from deterministic
normalization and scoring projection for frequency statements. Diagnosis in
the ExECTv2 target loop must follow the same pattern.

## Decision

The ADR 0030 Diagnosis headline is a projected clinical-fact score:

1. The LLM owns candidate generation and selection in the single target call.
2. Evidence must remain an exact source substring.
3. Deterministic normalization may project Diagnosis text to the clinically
   relevant core fact before scoring.
4. The scoring unit is one projected Diagnosis fact per letter, not repeated
   surface mentions of the same fact.
5. The executable target score is the projected `concept_only` clinical-fact
   score. Certainty/negation assertion scoring remains diagnostic because the
   current target asks whether the LLM captured the clinically relevant facts.
6. Projection may strip certainty prefixes such as `probable` or `possible`,
   remove parenthetical causal context, normalize spelling/plural variants,
   preserve protected seizure-type compounds, and map benchmark-equivalent
   diagnosis phrases to the same clinical core.

Examples:

- `probable focal epilepsy (perinatal insult)` scores as `focal epilepsy`,
  while evidence remains the exact source string.
- `symptomatic structural focal epilepsy` scores as the core fact
  `focal epilepsy`.
- repeated `tonic clonic seizures` Diagnosis mentions in one letter count as
  one clinical fact.
- `focal seizures with altered awareness` remains one protected seizure-type
  diagnosis fact, not two split fragments.

## Consequences

- Target reports should use the deterministic normalization/projection layer
  for Diagnosis rather than raw phrase capture.
- Raw ExECT item scoring and assertion-weighted concept identity remain
  comparators and diagnostics, but they are not the ADR 0030 Diagnosis target
  headline when they disagree with the projected `concept_only` clinical-fact
  score.
- Any future projection that changes Diagnosis fact identity must be named,
  tested, and visible in run artifacts.
- Error analysis for Diagnosis should classify remaining misses after this
  projection layer; a miss caused only by allowed surface-form variation is a
  projection bug, not an LLM candidate-generation failure.
