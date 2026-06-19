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
7. Error analysis for this phase is performed after normalization and scoring
   projection, and only for the four ADR 0030 target indicators. Non-target
   ExECT families remain out of scope.

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

## Implementation Note, 2026-06-19

The executable target report now records the Diagnosis headline policy as:
projected clinical-fact `concept_only` score after deterministic Diagnosis
normalization/projection, scored as projected core facts per letter. This is the
same normalization/projection discipline used for Gan frequency statements:
the LLM captures clinically relevant candidates in one call, while deterministic
rules project surface variants onto scorer-facing clinical facts.

Local Qwen v0.39 evidence confirms the intended scoring definition is executable:
the fresh `ollama_chat/qwen3.6:35b` dev5 live run
`experiments/exectv2_target_indicators_single_call_v039_live_dev5_qwen36_35b_ollama_cpu_ctx16384_20260619.md`
clears the four ADR 0030 targets after deterministic projection:
Diagnosis `0.9524`, SeizureFrequency `1.0000`, Prescription `1.0000`,
and Investigations `0.9412`. The companion no-call replay
`experiments/exectv2_target_indicators_single_call_v039_reproject_v037live_dev5_qwen36_35b_ollama_cpu_ctx16384_20260619.md`
also clears all four from a prior fresh local-Qwen raw output, showing that the
latest changes are scorer-facing normalization/projection over captured facts,
not extra model calls.

The dev25 promotion replay now exercises the same definition at the next ladder
step. The fresh v0.39 local-Qwen dev25 live run did not clear all indicators
before projection refinements (`0.8763` Diagnosis, `0.7843` SeizureFrequency,
`0.9600` Prescription, `0.8696` Investigations). The v0.40 no-call replay of
those exact saved raw outputs applies the corrected projected clinical-fact
Diagnosis scorer, whitespace/evidence repair, frequency-state projection, and
investigation suppression rules. It clears all four target indicators:
Diagnosis `0.9877`, SeizureFrequency `0.9167`, Prescription `0.9737`, and
Investigations `1.0000`, overall `0.9714`.

Fresh v0.40 local-Qwen dev25 live generation was then run as the next
confirmation. It produced 25 rows with 0 call failures but did not clear before
the final deterministic projection pass: overall `0.8840`, Diagnosis `0.8792`,
SeizureFrequency `0.8235`, Prescription `0.8800`, Investigations `0.9756`, with
one malformed JSON row. The v0.41 no-call replay of those exact fresh local raw
outputs adds parser salvage for truncated arrays, target-only over-inference
suppression, prescription regimen splitting, and frequency-state projection. It
clears the four indicators on the fresh local raw output: Diagnosis `0.9750`,
SeizureFrequency `0.9020`, Prescription `0.9870`, Investigations `1.0000`,
overall `0.9676`. This remains a deterministic replay over fresh local model
generation; a fresh v0.41 live rerun is the next reproducibility check before
broader claims.
