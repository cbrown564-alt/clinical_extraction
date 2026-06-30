# GEPA from-scratch (ExECTv2 de-dup facts) — exectv2_gepa_investigations_lane_deepseekreasoner_smoke

Date: 2026-06-30

DSPy-native GEPA run. The optimizable surface is the signature instruction; the existing de-dup parse/evidence-gate/adapter and the canonical clinical_headline scorers are reused unchanged. Trained on a seeded sub-split of `dev` (optimizer-only); evaluated on the full `dev` split (development surface, NOT test). Attribution-clean LLM-only: the adapter performs representation mapping only, it adds no facts.

## Models

- Task model: `deepseek/deepseek-reasoner` (temp 0.0, max_tokens 8000)
- Reflection (teacher) model: `deepseek/deepseek-reasoner`
- GEPA budget: auto=None max_metric_calls=24 (trainset 8, valset 6)

## Length penalty (prompt-bloat control)

- enabled: True
- instruction budget: 2000 tok (beta 0.25)
- demo budget: 800 tok (beta 0.25)
- output budget: 2000 tok (alpha 0.05)
- **final instruction length: 625 tokens** (seed was 625 tokens)

## Final evaluation (dev, clinical-recovery surface)

- **Canonical clinical_headline overall F1: 0.660** (P=0.607 R=0.724, Diagnosis=concept_negation)
  - Diagnosis=0.308  SeizureFrequency=0.333  Prescription=1.000  Investigations=1.000
- **Producer evidence-recall (source_near): 0.579** (GEPA per-family baseline 0.694, v08 hybrid 0.883) — Dx=0.312 SF=0.444 Rx=1.000 Inv=1.000
- Strict benchmark per-item F1 (diagnostic, NOT paper-cleared): 0.123
- Semantic (CUI-dropped) per-item F1: 0.123
- Letters: 4 (unscorable: 0); facts emitted 28, scored 27

## Comparators (dev140, from plan 13)

- Hand-tuned single-prompt de-dup plateau: GPT-4.1-mini 0.710, DeepSeek 0.745, Qwen 0.694
- v08 hybrid (multi-component) control: 0.9155

## Evolved instruction

```text
=== diagnosis ===
You read one clinical letter and list its distinct diagnosis facts.

Emit every distinct diagnosis or syndrome concept once (epilepsy type and any
comorbid conditions), with negation=affirmed, or negated if the diagnosis is
explicitly excluded (a negated diagnosis is still a fact). Ground each by an
exact substring of the letter as evidence. Return exactly one JSON object
matching output_schema with a 'clinical_facts' list, no markdown.

=== seizure_frequency ===
You read one clinical letter and list its seizure-frequency facts.

Emit one fact per distinct seizure type (use the named type, or 'seizures' if
generic) with a coarse state: active_rate, seizure_free, changed, or unknown.
Do not enumerate individual dated events. Ground each by an exact substring of
the letter as evidence. Return exactly one JSON object matching output_schema
with a 'clinical_facts' list, no markdown.

=== prescription ===
You read one clinical letter and list its current prescription facts.

Emit each distinct current drug regimen once as drug + dose + dose_unit +
frequency (1/2/3/As_Required); omit past or planned-only medications. Ground
each by an exact substring of the letter as evidence. Return exactly one JSON
object matching output_schema with a 'clinical_facts' list, no markdown.

=== investigation ===
You read one clinical letter and list its investigation facts EXHAUSTIVELY.

Check independently for EACH of the four modalities: MRI, CT, EEG, and telemetry --
do not stop after finding one. A letter that reports an MRI very often ALSO reports an
EEG (or vice versa); these are reported in different parts of the letter and must BOTH
be extracted. The most common mistake is anchoring on one modality (usually the MRI)
and silently dropping another (usually the EEG) that is mentioned elsewhere in the same
letter -- actively guard against this by scanning the whole letter for each modality in
turn rather than stopping at the first investigation you find. If the letter reports more
than one instance of the same modality (e.g. two EEGs from different dates, or with
different results), emit each as its own distinct fact rather than merging or keeping
only one. Emit each distinct completed-modality instance once with a result: normal,
abnormal, or unknown. Do not invent a modality the letter does not state. Ground each by
an exact substring of the letter as evidence. Return exactly one JSON object matching
output_schema with a 'clinical_facts' list, no markdown.
```

## Provenance

`dev` is sub-split deterministically (seed 20260627) into an optimizer-only trainset and a selection valset; `test` is never touched. The full-dev headline is a superset of the valset, so it is mildly optimistic versus a disjoint split — a development-only number, NOT paper-comparable and NOT a test readout. The length penalty is part of the GEPA selection metric, so a shorter evolved instruction is a recorded optimization outcome.