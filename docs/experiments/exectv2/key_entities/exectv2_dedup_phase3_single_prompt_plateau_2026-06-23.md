# ExECTv2 Deduplicated Clinical Facts Phase 3 Single-Prompt Readout

Date: 2026-06-23

## Scope

Phase 3 tested whether the attribution-clean `single_call_dedup_facts` route
could clear `>0.900` dev140 `clinical_headline` F1 with a single GPT-4.1-mini
prompt. All runs used the dev split only, `openai/gpt-4.1-mini`, temperature 0,
and direct model-emitted `clinical_facts` mapped one-to-one by the adapter.

## Prompt Iterations

| Variant | Split | Prompt focus | Clinical-recovery F1 | P | R | Evidence validity | Call/schema failures |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| v0.1 | dev25 | Phase 2 baseline prompt | 0.743 | 0.719 | 0.768 | 0.9839 | 0 |
| v0.2 | dev25 | Split compound diagnoses; emit seizure-type diagnoses; include historical SF and prior investigations | 0.772 | 0.733 | 0.816 | 0.9427 | 0 |
| v0.3 | dev25 | Precision repair for non-target diagnoses, prescriptions, planned investigations, and evidence copying | 0.792 | 0.763 | 0.824 | 0.9854 | 0 |
| v0.4 | dev25 | Seizure-frequency state boundary rules and examples | 0.798 | 0.767 | 0.832 | 0.9392 | 0 |
| v0.5 | dev25 | v0.4 state rules with compact examples trimmed for evidence stability | 0.800 | 0.752 | 0.856 | 0.9600 | 0 |
| v0.5 | dev140 | Confirmation run | 0.710 | 0.691 | 0.729 | 0.9613 | 0 |

Primary artifacts:

- `experiments/exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_phase3_v05_dev140_gpt41mini_20260623.jsonl`
- `experiments/exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_phase3_v05_dev140_gpt41mini_20260623.md`

## Dev140 Result

Canonical `clinical_headline` overall (Diagnosis = `concept_negation`):
F1 `0.710`, precision `0.691`, recall `0.729`.

| Entity | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.814 | 0.764 | 0.871 | 168 | 52 | 25 |
| Diagnosis | 0.672 | 0.663 | 0.680 | 202 | 98 | 95 |
| SeizureFrequency | 0.558 | 0.535 | 0.583 | 98 | 85 | 70 |
| Investigations | 0.832 | 0.847 | 0.816 | 111 | 20 | 25 |

Strict `model_preserving_canonical` remains diagnostic only for this route:
F1 `0.126`, precision `0.133`, recall `0.120`.

## Interpretation

The single-prompt simplified target improved on dev25 but did not generalize to
dev140. The confirmed dev140 result is essentially at the Phase 2 no-call replay
baseline (`0.7114`) rather than near the `>0.900` target, so Phase 3 is a
localized plateau rather than a successful clearance.

The plateau is concentrated in the two expected gap families:

- Diagnosis: persistent misses for broad epilepsy concepts and focal epilepsy,
  plus false positives from seizure-type over-enumeration and non-target
  seizure-like labels.
- SeizureFrequency: state/key confusion remains substantial, especially generic
  seizures active-rate versus seizure-free/unknown, qualitative frequency
  language, and seizure-type specificity.

Prescription and Investigations remain useful but are not stable enough inside
the single prompt to compensate for the Diagnosis/SF gap.

## Phase 3 Closeout

Phase 3 is closed as a single-prompt plateau:

- no call failures;
- no parse/schema failures;
- evidence validity above the Phase 3 gate on dev140 (`0.9613`);
- `clinical_headline` dev140 did not clear `>0.900`;
- the remaining gap is localized to Diagnosis and SeizureFrequency.

Next recommended phase: Phase 4 fallback rung 1, lean per-family LLM-only
prompts, starting with Diagnosis and SeizureFrequency.
