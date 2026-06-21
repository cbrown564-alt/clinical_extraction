# ExECTv2 Holistic Assembly v03 Diagnosis Phase 2 Error Analysis

- Date: `2026-06-21`
- Split: `dev140`
- Control: v02 holistic finding assembly
- Target model for live panel: `openai/gpt-4.1-mini`
- Winning implemented change: `diagnosis_heading_recovery_convention_cleanup_v03`

## Phase Result

Diagnosis improved, but remains unsolved.

| Artifact | Overall headline | Diagnosis headline | Diagnosis P | Diagnosis R | Diagnosis strict ledger F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| v02 | 0.8038 | 0.7658 | 0.7346 | 0.7811 | 0.7061 |
| v03 | 0.8130 | 0.7894 | 0.7944 | 0.7845 | 0.7276 |

Prescription, SeizureFrequency, and Investigations were unchanged. v03 changes 21 Diagnosis rows, all by dropping over-emitted concepts.

## Tested Hypotheses

| Hypothesis | Test | Result | Decision |
| --- | --- | --- | --- |
| H2 GPT-4.1-mini candidate selector can adjudicate residual candidates | 32-row residual panel, live, fixed candidate sources | F1 `0.697`, delta `-0.012` vs v02 panel control; 0 call/parse failures; evidence `1.000` | reject |
| H3 GPT-4.1-mini direct re-reader can recover missed concepts | same panel, live, direct note read | F1 `0.693`, delta `-0.016`; 0 call/parse failures; evidence `1.000` | reject |
| H4 narrow convention cleanup can remove symptom/non-epileptic over-emissions | no-call dev140 ablation over v02 | headline `0.7578 -> 0.7808` in scratch; implemented v03 gives holistic Diagnosis `0.7658 -> 0.7894` | accept as diagnostic v03 |

The live panel was useful as a negative test. It recovered zero of the 19 panel false negatives and only added false positives such as `myoclonic jerks`, `dissociative seizures`, and generic `seizures`.

## What v03 Fixed

v03 suppresses a narrow set of standalone Diagnosis over-emissions when they are better treated as seizure manifestations or non-epileptic/non-diagnostic context:

- `absence seizures`, `absences`, `absence like seizures`
- `myoclonic jerks`, `myoclonus`
- `dissociative seizures`
- `multiple seizures`, `single seizure`, generic `seizures`, `convulsive seizure`
- weak generic `epilepsy` evidence such as DVLA, clinic/service, medication, or history context

Strict Diagnosis false positives dropped `95 -> 73`; strict true positives dropped `221 -> 219`.

## Remaining Diagnosis Error Surface

Top strict misses after v03:

- generic affirmed `epilepsy`: 18
- `secondary generalised seizures`: 6
- `tonic clonic seizures`: 6
- `focal seizures with altered awareness`: 4
- `focal seizures`: 4
- `generalised`: 4
- `symptomatic epilepsy`: 4
- JME certainty variants: 6 total across certainty 4/5

Top strict over-emissions after v03:

- generic affirmed `epilepsy`: 41
- `tonic clonic seizures`: 26
- `focal epilepsy` certainty 5: 9
- `focal seizures`: 5
- `secondary generalised tonic clonic seizures`: 5
- `focal epilepsy` certainty 4: 4

## Interpretation

Diagnosis is not primarily blocked by source availability. It is blocked by convention selection:

- the model often identifies clinically plausible facts but chooses the wrong granularity for ExECTv2 scoring;
- generic `epilepsy` is both commonly missed and commonly over-emitted, so broad generic rules are unstable;
- tonic-clonic facts often sit between diagnosis, seizure-type history, and frequency, and require local convention decisions;
- some gold Diagnosis concepts are CUIPhrase fragments such as `drug`, `focal`, `occipital`, and `secondary`, so the headline is partly benchmark-convention recovery, not pure clinical diagnosis recovery.

## Next Hypotheses

1. H5: build a convention-aware Diagnosis repair lens that handles specific residual families separately: generic epilepsy, tonic-clonic, secondary-generalised, focal-with-altered-awareness, and syndrome/structural concepts. Each family needs its own no-call ablation before promotion.
2. H6: recover benchmark-convention fragments only from explicit Diagnosis or Impression headings, with separate provenance category `benchmark_format`, not `clinical_epilepsy`.
3. H7: use GPT-4.1-mini only for structured row explanations or candidate evidence classification, not direct prediction, unless a panel shows false-negative recovery without new false positives.

Promotion remains blocked: Diagnosis is `0.7894`, still `0.1106` short of `>0.900`.
