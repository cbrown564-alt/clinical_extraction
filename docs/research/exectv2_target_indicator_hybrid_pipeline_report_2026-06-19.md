# ExECTv2 Target-Indicator Hybrid Pipeline Research Report

Date: 2026-06-19

## Executive Summary

This research pass narrowed ExECTv2 Plan 11 to exactly four target indicators:
`Diagnosis`, `SeizureFrequency`, `Prescription`, and `Investigations`. The
objective was to beat the target core-F1 threshold of `>0.900` for each
indicator using a hybrid architecture: one LLM call per letter for candidate
generation and selection, followed by deterministic normalization and scoring
projection.

The central methodological correction was to score target indicators after the
same kind of deterministic projection used in the Gan 2026 seizure-frequency
work. Diagnosis is not scored as raw surface-form matching or assertion-weighted
capture in this target loop. The executable target definition is projected
clinical-fact `concept_only`: one normalized clinically relevant Diagnosis fact
per letter, after deterministic normalization/projection. SeizureFrequency is
scored analogously through projected seizure-state `clinical_headline`.

The strongest completed artifact at this pause point is v0.42 saved-output
replay over a fresh local-Qwen v0.41 dev25 raw generation:

| Artifact | Mode | Overall | Diagnosis | SeizureFrequency | Prescription | Investigations | Clears all four |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `exectv2_target_indicators_single_call_v042_reproject_v041live_dev25_qwen36_35b_ollama_cpu_ctx16384_20260619.md` | saved-output replay | 0.9487 | 0.9376 | 0.9811 | 0.9250 | 0.9756 | yes |

This is a hybrid development artifact, not a final benchmark claim. It shows
that the single local-Qwen call captured enough clinically relevant target facts
for deterministic projection to clear all four indicators on dev25. A fresh
v0.42 local-Qwen dev25 live run was started but deliberately paused by user
direction before completion; no result from that interrupted run is retained or
interpreted.

## Research Question

Can a target-only ExECTv2 extractor clear core F1 `>0.900` on the four exact
indicators using:

1. one LLM call per letter for candidate generation and selection;
2. deterministic evidence repair, normalization, CUI projection, and
   scorer-facing projection;
3. error analysis restricted exclusively to `Diagnosis`, `SeizureFrequency`,
   `Prescription`, and `Investigations`; and
4. Diagnosis and SeizureFrequency scored after projection, mirroring the Gan
   frequency normalization/projection discipline?

## Governing Decisions

- ADR 0030 fixes the optimization surface to the four exact indicators and
  excludes non-target ExECT families from this phase of error analysis.
- ADR 0031 fixes the Diagnosis target definition: projected clinical-fact
  `concept_only`, not raw phrase matching, not assertion-weighted diagnosis
  scoring, and not repeated mention counting.
- The SeizureFrequency target headline is projected seizure-state
  `clinical_headline`, so variant forms of frequency statements are normalized
  into scorer space before evaluation.
- Prescription and Investigations use their clinical-headline component scores
  after deterministic medication/investigation normalization and projection.
- Development evidence here is dev-split only. These results do not authorize a
  final holdout or benchmark-comparable claim.

## Evaluation Surface

The rapid target loop used dev25 as the main local-Qwen ladder surface. Earlier
dev140 work established that the broader family-routed assembly was not enough:
best current dev140 F1 by target before the target-only runner was Diagnosis
`0.7302`, SeizureFrequency `0.7277`, Prescription `0.9072`, and Investigations
`0.7475`; the focused routed assembly remained below target on all four.

The target-only runner reports the same four headline policies in every run:

| Indicator | Headline score |
| --- | --- |
| Diagnosis | projected clinical-fact `concept_only` after deterministic Diagnosis normalization/projection |
| SeizureFrequency | projected seizure-state `clinical_headline` after deterministic frequency-state normalization/projection |
| Prescription | clinical-headline regimen after deterministic medication normalization/projection |
| Investigations | clinical-headline modality/performed/result after deterministic investigation normalization/projection |

## Avenues Explored

### 1. Broader Family-Routed Architecture

The starting point was the Plan 11 family-routed architecture, which combined
deterministic all-entity behavior, shared broad-pass extraction, focused
Diagnosis work, and SeizureFrequency routing. This route improved over a
single-pass baseline but did not approach the four-indicator target:

- routed four-family CUI-free headline: `0.5592`;
- routed four-family CUI-projected headline: `0.5952`;
- focused Diagnosis no-call replay lifted Diagnosis but still left the
  four-target surface below the required threshold.

Interpretation: the family-routed architecture was useful scaffolding, but the
target objective required a cleaner target-only single-call formulation and a
target-specific scoring projection layer.

### 2. Target-Only Single LLM Call

A target-only runner was implemented for one structured LLM call per letter.
The prompt asks for only the four target entities and excludes non-target
families from output and analysis. The candidate generation burden remains on
the LLM; deterministic code handles validation, evidence repair, normalization,
projection, and scoring render.

Early GPT-4.1-mini target runs showed that the architecture was viable but that
Diagnosis and SeizureFrequency needed the corrected projected scoring surface.
The best completed GPT-4.1-mini dev25 run, v0.21 live, cleared all four:

| Artifact | Model | Mode | Overall | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `exectv2_target_indicators_single_call_v021_live_dev25_gpt41mini_20260619.md` | `openai/gpt-4.1-mini` | live | 0.9317 | 0.9360 | 0.9057 | 0.9367 | 0.9500 |

Interpretation: the single-call target architecture can clear the dev25 target
surface when paired with deterministic projection. This run established the
architecture but not the local-Qwen destination model.

### 3. Diagnosis Definition Correction

The user correctly flagged that Diagnosis must be evaluated like the Gan
frequency work: after normalization and scoring projection. The implemented
Diagnosis target score now measures whether the LLM captured the clinically
relevant Diagnosis facts, not whether it reproduced the exact annotation wording
or every assertion variant.

Concrete consequences:

- repeated projected Diagnosis facts count once per letter;
- certainty prefixes and parenthetical causal context can be stripped;
- benchmark-equivalent diagnosis phrases can map to the same clinical core;
- seizure-type compounds are protected from over-splitting;
- assertion-weighted Diagnosis remains diagnostic, not the target headline.

Interpretation: this changed several apparent candidate misses into projection
bugs. It aligned Diagnosis with the same projection philosophy already accepted
for frequency statements.

### 4. Local Qwen Deployment

The destination model was local `ollama_chat/qwen3.6:35b` through Ollama. The
installed model digest is recorded in `PROJECT_STATUS.md`. GPU loading on the
8 GB laptop RTX 4070 failed with CUDA out-of-memory, so completed local runs used
CPU mode with:

- `CLINICAL_EXTRACTION_OLLAMA_NUM_GPU=0`;
- `CLINICAL_EXTRACTION_OLLAMA_NUM_CTX=16384`;
- temperature `0`;
- no DSPy cache.

The first cleared local-Qwen gate was dev5:

| Artifact | Mode | Overall | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `exectv2_target_indicators_single_call_v039_live_dev5_qwen36_35b_ollama_cpu_ctx16384_20260619.md` | live | 0.9722 | 0.9524 | 1.0000 | 1.0000 | 0.9412 |

Interpretation: local Qwen was capable of the target task on a small pilot, but
dev5 was too small and too easy to treat as evidence of reproducibility.

### 5. Dev25 Local-Qwen Fresh-Live and Replay Ladder

The dev25 local-Qwen ladder separated fresh model generation from deterministic
saved-output projection. This was essential for attribution: the LLM is credited
for candidates present in the raw output; deterministic projection is credited
for scorer-facing normalization.

| Version | Source raw output | Mode | Overall | D | SF | P | I | Clears all four |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| v0.39 | v0.39 fresh live | live | 0.8812 | 0.8763 | 0.7843 | 0.9600 | 0.8696 | no |
| v0.40 | v0.39 fresh live | saved-output replay | 0.9714 | 0.9877 | 0.9167 | 0.9737 | 1.0000 | yes |
| v0.40 | v0.40 fresh live | live | 0.8840 | 0.8792 | 0.8235 | 0.8800 | 0.9756 | no |
| v0.41 | v0.40 fresh live | saved-output replay | 0.9676 | 0.9750 | 0.9020 | 0.9870 | 1.0000 | yes |
| v0.41 | v0.41 fresh live | live | 0.9157 | 0.9250 | 0.8333 | 0.9250 | 0.9756 | no |
| v0.42 | v0.41 fresh live | saved-output replay | 0.9487 | 0.9376 | 0.9811 | 0.9250 | 0.9756 | yes |

Interpretation: the local-Qwen raw generations repeatedly contain enough signal
for a deterministic projection layer to clear the dev25 target surface, but
fresh-live reproducibility is not yet proven. Fresh runs vary in candidate
selection, formatting, and over/under-emission. Saved-output replay is strong
evidence about projection adequacy over specific raw generations; it is not the
same claim as a fresh-live candidate clearing the target.

### 6. SeizureFrequency Projection Recovery

The final v0.41 fresh-live residual analysis showed SeizureFrequency as the only
blocking indicator: `0.8333`, with Diagnosis, Prescription, and Investigations
already above target. Error analysis was restricted to the four target
indicators, with the microscope on SF residuals.

The residuals showed several clinically relevant frequency facts had either
already been emitted by the LLM or were recoverable from adjacent captured target
facts. v0.42 therefore added named deterministic SF projection families:

- remote teenage last-seizure projection;
- later infrequent convulsive-state projection;
- controlled-on-dose projection from captured Diagnosis context;
- frequent myoclonic-jerk projection;
- active recent-event preservation when a recent seizure is followed by
  "last had a seizure before this";
- suppression of impossible zero-state duplicates contradicted by a positive
  rate in the same evidence.

The v0.42 replay of the exact v0.41 fresh-live raw output moved SF from
`0.8333` to `0.9811` while keeping the other indicators above threshold.

Interpretation: this is the closest analogue to the Gan frequency projection
work. The LLM captured clinically relevant facts in heterogeneous forms; the
deterministic layer projected those forms into the scorer's seizure-state key
space.

## What Worked

The target-only single-call architecture worked better than broad family routing
for this objective. Restricting the prompt and the error analysis to the four
exact indicators reduced accidental optimization of non-target families.

The corrected Diagnosis definition was necessary. Once Diagnosis was scored as
projected clinical-fact `concept_only`, the evaluation matched the stated goal:
measure clinically relevant fact capture, not raw annotation-string mimicry.

Saved-output replay was valuable. It separated model candidate variability from
projection adequacy, making it clear when a miss was a deterministic projection
bug over a captured fact rather than a true LLM candidate miss.

The local-Qwen route is plausible. Dev5 fresh live cleared; multiple dev25 raw
generations cleared after deterministic projection; v0.41 fresh live cleared
three of four indicators before v0.42 SF projection.

## What Did Not Fully Work

Fresh local-Qwen dev25 has not yet cleared all four indicators in a completed
live run. The strongest local result at this pause point is a saved-output
replay, not a fresh-live confirmation.

The model remains variable even at temperature `0`. Across v0.39, v0.40, and
v0.41 fresh dev25 live runs, different indicators blocked: first Diagnosis/SF/I,
then Diagnosis/SF/P, then SF only. This suggests deterministic projection is
necessary but may not be sufficient for robust fresh-live reproducibility.

Prescription precision is fragile. v0.41 and v0.42 on the latest raw output both
show Prescription `0.9250`, above target but with 5 FP. It should not be treated
as solved beyond the current dev25 surface.

CPU local-Qwen runtime is slow. A fresh v0.42 dev25 live confirmation was
started, reached only an early prefix, and was paused by user direction. No
partial result is interpreted.

## Interpretation

The main research finding is that the four target indicators behave like
clinical fact extraction plus deterministic projection, not like raw span
matching. This is especially clear for Diagnosis and SeizureFrequency:

- Diagnosis requires projection from surface phrases and repeated mentions into
  clinical core facts.
- SeizureFrequency requires projection from heterogeneous natural-language
  frequency/state statements into normalized seizure-state keys.

The hybrid pipeline is therefore the right architecture for this objective. The
LLM should own candidate generation and selection in a single call; deterministic
rules should own normalization, evidence repair, CUI projection, and
scorer-facing rendering. This keeps attribution auditable and makes the
evaluation answer the clinical question: did the model capture the clinically
relevant facts?

The strongest caution is reproducibility. Replays show that the projection layer
can recover target scores from fresh local-Qwen raw outputs. They do not yet
prove that v0.42 fresh local-Qwen live generation will clear dev25 end to end.
The next claim should therefore be framed as: "v0.42 is a cleared saved-output
hybrid development artifact over fresh local-Qwen generation," not as a final
local-Qwen live result.

## Evidence and Verification

Code and documentation for the latest completed phase were committed in:

- `954954f Recover target SF projection on fresh Qwen raw`

Focused verification passed after v0.42:

- `171` focused tests passed:
  `tests/test_exectv2_target_indicators_single_call.py`,
  `tests/test_exectv2_scoring.py`,
  `tests/test_gan2026_llm_config.py`,
  `tests/test_exectv2_clinical_recovery_error_ledger.py`;
- Ruff passed on the touched target/scoring/test files.

Key artifacts:

- `docs/decisions/0030-four-exact-indicators-drive-exectv2-plan11.md`
- `docs/decisions/0031-diagnosis-target-core-scores-projected-clinical-facts.md`
- `experiments/exectv2_target_indicators_single_call_v021_live_dev25_gpt41mini_20260619.md`
- `experiments/exectv2_target_indicators_single_call_v039_live_dev5_qwen36_35b_ollama_cpu_ctx16384_20260619.md`
- `experiments/exectv2_target_indicators_single_call_v039_live_dev25_qwen36_35b_ollama_cpu_ctx16384_20260619.md`
- `experiments/exectv2_target_indicators_single_call_v040_reproject_v039live_dev25_qwen36_35b_ollama_cpu_ctx16384_20260619.md`
- `experiments/exectv2_target_indicators_single_call_v040_live_dev25_qwen36_35b_ollama_cpu_ctx16384_20260619.md`
- `experiments/exectv2_target_indicators_single_call_v041_reproject_v040live_dev25_qwen36_35b_ollama_cpu_ctx16384_20260619.md`
- `experiments/exectv2_target_indicators_single_call_v041_live_dev25_qwen36_35b_ollama_cpu_ctx16384_20260619.md`
- `experiments/exectv2_target_indicators_single_call_v042_reproject_v041live_dev25_qwen36_35b_ollama_cpu_ctx16384_20260619.md`

## Recommended Next Steps

1. Run a fresh v0.42 local-Qwen dev25 live confirmation with the same CPU
   settings and no DSPy cache.
2. If fresh v0.42 dev25 clears all four, freeze the candidate and run a
   predeclared broader dev surface before any holdout-facing work.
3. If fresh v0.42 dev25 does not clear, perform target-only residual analysis
   on the blocking indicators only, and classify each residual as candidate
   miss, wrong detail selection, projection gap, or evidence failure after the
   normalization/projection layer.
4. Before moving beyond dev25, add an attribution table separating raw
   model-selected candidates, format-only repair, semantic projection families,
   and full hybrid output.
5. Keep claims conservative: development artifact until a fresh live run clears
   the predeclared surface; benchmark claim only after split/scorer/protocol
   alignment and locked holdout discipline.
