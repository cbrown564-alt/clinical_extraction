> **Superseded for navigation —** canonical summary: [`HOLISTIC_ASSEMBLY_LADDER_CANON.md`](HOLISTIC_ASSEMBLY_LADDER_CANON.md). Full detail retained below.

# ExECTv2 Holistic Assembly v04 Diagnosis Phase 3 Error Analysis

- Date: `2026-06-21`
- Split: `dev140`
- Control: v03 holistic finding assembly
- Winning implemented change: `diagnosis_heading_recovery_convention_alias_v04`
- Rule category: `benchmark_format` for alias rewrites; residual drops remain deterministic convention cleanup.

## Phase Result

v04 improves Diagnosis materially but remains short of target.

| Artifact | Overall headline | Diagnosis headline | Diagnosis P | Diagnosis R | Diagnosis strict ledger F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| v03 | 0.8130 | 0.7894 | 0.7944 | 0.7845 | 0.7276 |
| v04 | 0.8278 | 0.8301 | 0.8459 | 0.8148 | 0.7609 |

Prescription, SeizureFrequency, and Investigations were unchanged. v04 changes 17 Diagnosis rows: 13 convention alias rewrites and 5 residual drops.

## Tested H5 Ablations

| Hypothesis | Test | Diagnosis headline | Decision |
| --- | --- | ---: | --- |
| Replace `secondary generalised tonic clonic` variants with `secondary generalised seizures` | no-call v03 replay | 0.7775 | reject |
| Drop tonic-clonic Diagnosis mentions in frequency-only contexts | no-call v03 replay | 0.7890 | reject/flat |
| Add secondary-generalised concepts from heading | no-call v03 replay | 0.7837 | reject |
| Add tonic-clonic concepts from heading | no-call v03 replay | 0.7881 | reject/flat |
| Add JME from heading with certainty cue | no-call v03 replay | 0.7894 | reject/flat |
| Add symptomatic epilepsy from heading | no-call v03 replay | 0.7754 | reject |
| Convention alias rewrites plus residual non-diagnostic drops | no-call v03 replay | 0.8301 | accept as v04 |

The accepted v04 rule family is deliberately not a broad “more diagnosis concepts” rule. It corrects cases where the model already selected a nearby clinical fact but used a phrase that ExECTv2 scores under a different CUIPhrase or benchmark convention.

## Accepted v04 Actions

Alias rewrites:

- `focal dyscognitive seizures` -> `dyscognitive seizures`
- `tonic clonic seizures alone` and `epilepsy with tonic clonic seizures alone` -> `epilepsy with generalised tonic clonic seizures alone`
- `focal to bilateral seizures` -> `focal to bilateral convulsive seizures`
- `focal frontal lobe seizures` -> `frontal lobe seizures`
- `grand mal seizure` -> `grand mal`
- `drug resistant focal epilepsy` -> `drug resistant epilepsy`
- `secondarily generalised seizures` -> `secondary generalised seizures`
- structural dysplasia/hippocampal-sclerosis phrases to the closest scored convention term

Residual drops:

- `Hydrocephalus`
- `learning difficulties`
- `drop attacks`
- `nocturnal seizures`
- generic single `seizure`

## Remaining Diagnosis Error Surface

Top strict misses after v04:

- generic affirmed `epilepsy`: 18
- `tonic clonic seizures`: 6
- `secondary generalised seizures`: 5
- `focal seizures with altered awareness`: 4
- `focal seizures`: 4
- `generalised`: 4
- `symptomatic epilepsy`: 4
- JME certainty variants: 6 total across certainty 4/5

Top strict over-emissions after v04:

- generic affirmed `epilepsy`: 40
- `tonic clonic seizures`: 26
- `focal epilepsy` certainty 5: 11
- `focal seizures`: 5
- `secondary generalised tonic clonic seizures`: 5
- `focal epilepsy` certainty 4: 4

## Interpretation

The positive result confirms that a meaningful share of remaining Diagnosis error is benchmark-convention mismatch, not missing clinical evidence. The negative ablations confirm that broad tonic-clonic, secondary-generalised, JME, and symptomatic-epilepsy recovery rules still add more false positives than true positives.

The next useful Diagnosis phase should avoid broad add/drop rules and instead attack the two largest unstable families with row-level gates:

1. generic epilepsy over-emission versus missed generic epilepsy;
2. tonic-clonic over-emission versus scored tonic-clonic seizure-type diagnosis.

Diagnosis is now `0.8301`, still `0.0699` short of the `>0.900` family target.
