# ExECTv2 Deduplicated Clinical Facts Phase 4 Error Analysis

Date: 2026-06-24

## Scope

This analyzes where the current direct de-duplicated clinical-fact LLM-only
route fails, using dev artifacts only. The primary target is canonical
`clinical_headline` with Diagnosis scored as `concept_negation`.

Primary current artifact:

- `experiments/exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_per_family_phase4_dev25_gpt41mini_20260624.{jsonl,md}`

Stability comparator:

- `experiments/exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_phase3_v05_dev140_gpt41mini_20260623.{jsonl,md}`

Important scorer detail: Diagnosis recall can be satisfied by any predicted
annotation carrying the same diagnosis concept, while Diagnosis precision is
charged only for home-family Diagnosis over-emissions. SeizureFrequency,
Prescription, and Investigations are keyed on their family-specific headline
units.

## Headline Residuals

Best Phase 4 gate, compact per-family dev25:

| Family | TP | FP | FN | F1 | Residual share |
| --- | ---: | ---: | ---: | ---: | ---: |
| Diagnosis | 30 | 10 | 11 | 0.698 | 21 / 53 |
| SeizureFrequency | 20 | 12 | 10 | 0.690 | 22 / 53 |
| Prescription | 31 | 2 | 7 | 0.873 | 9 / 53 |
| Investigations | 20 | 1 | 0 | 0.976 | 1 / 53 |

The failure is concentrated almost entirely in Diagnosis and SeizureFrequency:
43 of 53 residual headline errors on the current best Phase 4 gate. This is
the same shape as Phase 3 dev140, where Diagnosis and SeizureFrequency account
for 367 of 489 residual headline errors.

## Failure Taxonomy

### 1. Diagnosis: target ontology and granularity are not stable in the model

Phase 4 residuals:

- 11 missed Diagnosis keys.
- 10 extra Diagnosis keys.
- Top missed keys: `epilepsy` (4), `focal seizures` (3),
  `focal to bilateral convulsive seizures` (3), plus one-off syndrome/core
  concepts such as `generalised epilepsy`, `focal epilepsy`, `temporal lobe
  epilepsy`, and `intractable epilepsy`.
- Top extra keys: generic `epilepsy` (3), `myoclonic jerks` (2), plus
  `absence like seizures`, `focal epilepsy`, and `temporal lobe epilepsy`.

Representative example, `EA0006`:

- Source/gold: "Epilepsy - unclassified, possibly generalised" contributes
  `generalised epilepsy`.
- Model emitted: `epilepsy unclassified`.
- Why it fails: the model chose a plausible literal diagnosis label, but the
  headline key expects the more specific projected concept.

Same letter:

- Source/gold: `generalised tonic clonic seizures` is a target seizure-type
  diagnosis.
- Model emitted: `generalised tonic clonic seizures`, but also emitted
  `absence like seizures`.
- Why it fails: it mixes valid target seizure types with borderline/non-target
  seizure-like phenomena. The prompt asks for named seizure types, but the model
  cannot reliably distinguish target epileptic seizure types from narrative
  seizure-like episodes.

Representative example, `EA0018`:

- Source: "temporal lobe onset focal seizures".
- Gold headline keys include seizure-type concepts such as temporal-lobe seizure
  and focal seizures.
- Model emitted: `temporal lobe epilepsy`.
- Why it fails: the clinical meaning is nearby, but the model moves from
  seizure-type assertion to epilepsy-syndrome assertion, causing one FP and
  multiple FNs.

### 2. SeizureFrequency: the model over-converts qualitative language into rates

Phase 4 residuals:

- 10 missed SeizureFrequency keys.
- 12 extra SeizureFrequency keys.
- Extra active-rate states are the largest category: 9 of 12 SF false positives.
- Misses split across active-rate/count/window (4), seizure-free/last-event (3),
  and qualitative/unknown state (3).

Representative example, `EA0014`:

- Source: "she continues to get general and complex partial seizures".
- Model emitted two active-rate facts: `general seizures` and
  `complex partial seizures`.
- Why it fails: the phrase says seizures continue, but gives no count, cadence,
  interval, last-event, or change-state payload. The model manufactures an
  active-rate state with `NumberOfSeizures=1`, producing false positives.

Representative example, `EA0011`:

- Source includes `focal seizures with altered awareness approximately 1 per
  fortnight` and `focal to bilateral convulsive seizures, last event around
  Christmas 2017`, plus narrative "infrequent" convulsive seizures.
- Model emitted one active-rate fact and one seizure-free fact.
- Gold still has additional headline units for the qualitative/unknown
  infrequency state and a related convulsive-seizure state.
- Why it fails: a lean de-duplicated model output is clinically reasonable, but
  the scorer's target surface still distinguishes related seizure-type/state
  units that the model does not enumerate.

Representative example, `EA0006`:

- Gold has active-rate for `generalised tonic clonic seizures` in 2014.
- Model also emits a generic `seizures` seizure-free fact from "he remains
  seizure free".
- Why it fails: the model does not adjudicate competing historical and current
  statements into the target key inventory. It adds a generic current state
  while still missing or mismatching a specific historical state.

### 3. Prescription: stronger, but current-regimen scope still breaks in complex letters

Phase 4 residuals:

- 7 missed current regimen keys.
- 2 extra regimen keys.

Representative examples:

- `EA0009`: missed both current `levetiracetam 750 mg twice a day` and
  `lamotrigine 100 mg twice a day`.
- `EA0018`: missed current `sodium valproate 500 mg twice a day` and
  `levetiracetam 1000 mg twice today`.
- `EA0011`: over-emitted rescue `clobazam as required`.

Why it fails: the model is mostly good at medications, but misses regimen lines
when they sit inside narrative medication-change discussions, and it sometimes
promotes rescue/contingency medication into the current-regimen surface.

### 4. Investigations: nearly solved on dev25, but planned-test suppression remains fragile

Phase 4 residuals:

- 0 missed investigation keys.
- 1 extra investigation key.

Representative example, `EA0014`:

- Source: "I am therefore arranging an MRI scan of the brain."
- Model emitted: `MRI`, result `unknown`.
- Why it fails: the model treated a planned/future investigation as completed.

Phase 3 dev140 shows the broader pattern: Investigation misses and overcalls
are mostly abnormal/normal result recovery versus planned/unknown-result
over-emission.

## Evidence Gate

The route is not primarily failing at evidence validation:

- Phase 4 compact dev25: 5 evidence-invalid drops out of 128 raw mentions,
  evidence validity `0.9609`.
- Phase 3 dev140: 34 evidence-invalid drops, evidence validity `0.9613`.

Evidence failures still matter because they can erase an otherwise correct
fact. Example: `EA0011` loses a Diagnosis prediction after the evidence gate,
leaving the temporal-lobe-epilepsy key missed. But the main plateau remains
clinical fact selection/state/keying, not JSON parsing or substring copying.

## Why The Model Is Failing

The direct de-duplicated prompt asks the model to do three hard things at once:

1. Recover the clinically relevant fact from the note.
2. Choose the scorer's exact headline unit, including ontology/granularity.
3. Decide when duplicate-looking source statements are actually distinct target
   units.

The Phase 4 per-family split improved focus but did not solve these decisions.
Diagnosis failures are mostly ontology/granularity failures: broad epilepsy
versus focal epilepsy, seizure type versus syndrome, and target seizure type
versus non-target seizure-like event. SeizureFrequency failures are mostly
state and unit-boundary failures: active-rate over-triggering, generic-vs-
specific seizure type mismatch, and missed qualitative/unknown or last-event
states.

This is why the route plateaus below the v08 hybrid control. The hybrid system
can use specialized components, candidate inventories, verifier-style
adjudication, and deterministic representation checks. The direct LLM-only
route cannot add ontology companions, select missing states, or repair target
units after the model output without becoming hybrid under the attribution
protocol.

## Bottom Line

Current direct de-duplicated clinical-fact LLM-only prompting is not blocked by
format, calls, parsing, or evidence hygiene. It is blocked by prediction-bearing
clinical ontology and state-selection decisions. The model often extracts a
nearby clinical fact, but not the exact de-duplicated target fact that the
headline scorer requires.
