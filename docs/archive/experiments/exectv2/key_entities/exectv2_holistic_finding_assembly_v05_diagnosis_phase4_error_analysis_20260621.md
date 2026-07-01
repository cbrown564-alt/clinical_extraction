> **Superseded for navigation —** canonical summary: [`HOLISTIC_ASSEMBLY_LADDER_CANON.md`](HOLISTIC_ASSEMBLY_LADDER_CANON.md). Full detail retained below.

# ExECTv2 Holistic Assembly v05 Diagnosis Phase 4 Error Analysis

- Date: `2026-06-21`
- Split: `dev140`
- Control: v04 holistic finding assembly
- Winning implemented change: `diagnosis_heading_recovery_residual_benchmark_v05`
- Rule category: `benchmark_format`

## Phase Result

v05 clears the active Diagnosis headline target on the declared target-indicator
surface. The gain is dev-only and should be read as benchmark-format residual
repair over the frozen GPT-4.1-mini Diagnosis producer, not as a benchmark,
full-200, or holdout claim.

| Artifact | Overall headline | Diagnosis headline | Diagnosis P | Diagnosis R | Diagnosis strict ledger F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| v04 | 0.8278 | 0.8301 | 0.8459 | 0.8148 | 0.7609 |
| v05 | 0.8576 | 0.9083 | 0.8762 | 0.9428 | 0.8127 |

Prescription, SeizureFrequency, and Investigations were unchanged:
Prescription `0.8214`, SeizureFrequency `0.8068`, Investigations `0.8615`.

## Tested Ablations

| Hypothesis | Test | Diagnosis headline | Decision |
| --- | --- | ---: | --- |
| Drop generic `epilepsy` when a more specific diagnosis is present | no-call v04 replay | 0.8289 | reject |
| Drop generic `epilepsy` outside heading evidence | no-call v04 replay | 0.7956 | reject |
| Add generic `epilepsy` from any Diagnosis heading | no-call v04 replay | 0.8257 | reject |
| Drop tonic-clonic when secondary-generalised concept is present | no-call v04 replay | 0.8358 | too small alone |
| Rewrite exact symptomatic/lobe/secondary convention residuals | no-call v04 replay | 0.8740 | partial accept |
| Add residual exact source phrase concepts plus generic-noise suppression | no-call v04 replay | 0.9083 | accept as v05 |

## Accepted v05 Actions

Aggregate lens diagnostics across dev140:

- Rewritten residual benchmark findings: 10.
- Added residual benchmark findings: 41.
- Dropped residual benchmark noise findings: 22.

Largest accepted action families:

- Rewrites: `symptomatic epilepsy` x4, `secondary generalised seizures` x3,
  plus single rewrites for `symptomatic focal epilepsy`,
  `secondary generalisation`, and `temporal lobe seizures`.
- Additions: exact source-phrase recoveries for lobe-specific epilepsy,
  `generalised`, `focal`, `secondary`, `status epilepticus`,
  `typical absences`, `drug refractory epilepsies`, and related scored
  benchmark residual concepts.
- Drops: generic `epilepsy` noise x12 and tonic-clonic shadows from
  secondary-generalised evidence x10.

## Residual Surface After v05

On the declared target-indicator Diagnosis headline, residual errors are down
to 17 candidate misses and 39 wrong-detail selections. The strict assertion
ledger remains lower because it requires certainty/negation and stricter scored
concept shape:

- Strict Diagnosis F1: `0.8127`, precision `0.8000`, recall `0.8258`.
- Top strict misses remain generic `epilepsy`, tonic-clonic seizure variants,
  focal seizure variants, and JME certainty variants.
- Top strict over-emissions remain generic `epilepsy`, tonic-clonic seizures,
  focal/focal-epilepsy variants, and a small number of residual tokenized
  benchmark concepts.

## Interpretation

The failed generic-epilepsy ablations show that the concept-only headline
already collapses many generic-parent errors when a more specific descendant is
present. The winning phase instead repairs exact residual convention shapes:
the model had usually found the right clinical neighborhood, but ExECTv2 scored
nearby source wording as a different concept.

Diagnosis is now above the active `>0.900` family headline target on dev140.
The next weakest headline is SeizureFrequency (`0.8068`), followed by
Prescription (`0.8214`) and Investigations (`0.8615`). Prescription should still
be maximized last because it is clinically least ambiguous and likely has the
highest ceiling once the shared family architecture is stable.
