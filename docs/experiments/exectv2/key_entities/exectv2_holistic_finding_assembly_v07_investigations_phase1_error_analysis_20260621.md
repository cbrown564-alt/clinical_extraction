# ExECTv2 Holistic Assembly v07 Investigations Phase 1 Error Analysis

Date: 2026-06-21  
Split: dev140  
Current assembly: `exectv2_holistic_finding_assembly_v07_dev140`  
Source architecture: holistic finding assembly over frozen family producers  
Model-bearing source: `openai/gpt-4.1-mini` Investigations verifier v0.1  

## Decision

Investigations now clears the >0.9 family target in the official holistic
assembly headline. v07 keeps Diagnosis v05 and SF v08 fixed, leaves
Prescription on the v0.42 control, and swaps Investigations to a no-call
arbitration over the saved GPT-4.1-mini Investigations verifier.

| Assembly | Investigations F1 | P | R | TP | FP | FN | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| v06 control | 0.8615 | 0.9032 | 0.8235 | 112 | 12 | 24 | superseded |
| verifier v0.1 drop-in | 0.8864 | 0.8832 | 0.8897 | 121 | 16 | 15 | improves recall, misses target |
| verifier/control intersection | 0.8000 | 0.9787 | 0.6765 | 92 | 2 | 44 | too recall-poor |
| verifier/control union | 0.8372 | 0.7636 | 0.9265 | 126 | 39 | 10 | recall ceiling, too noisy |
| v07 verifier + pending-test arbitration | 0.9132 | 0.9380 | 0.8897 | 121 | 8 | 15 | target cleared |

Overall holistic headline moved from v06 `0.8789` to v07 `0.8873`. The gate
still does not promote because Prescription remains below target.

## Hypothesis

The main verifier residual was not lack of completed-test recall. It was a
specific precision failure: planned, requested, arranged, or awaited tests were
sometimes emitted as `Performed=No` or `Results=Unknown`. Because dev140 has no
gold `Performed=No` Investigations labels, and the clinical task asks for
completed historical tests, those pending-test emissions should be suppressed
when the evidence/rationale itself says the test is future or not yet done.

This is a prediction-bearing `clinical_epilepsy` rule, not a benchmark-format
rewrite.

## Tested Ablations

Verifier-only was a near miss: recall rose from v06 `0.8235` to `0.8897`, but
precision fell from `0.9032` to `0.8832`. Row-level review showed the precision
loss clustered around pending-test false positives:

- MRI planned/awaited/no: EA0024, EA0123, EA0149, EA0182, EA0185.
- CT requested/no: EA0108.
- EEG awaiting/no: EA0154.
- EEG requested/unknown: EA0054.

Naive union showed recoverable recall (`0.9265`) but over-emitted 39 false
positives, especially EEG abnormal states from narrative or weak-control
evidence. Intersection achieved high precision (`0.9787`) but collapsed recall
to `0.6765`, confirming the verifier should remain primary rather than require
agreement with the v0.42 control.

The final arbitration drops exactly eight pending-test residuals:

| Rule | Count | Category |
| --- | ---: | --- |
| `drop_pending_or_planned_investigation` | 7 | clinical_epilepsy |
| `drop_requested_unknown_investigation` | 1 | clinical_epilepsy |

## Remaining Row-Level Errors

v07 residuals: 15 FN and 8 FP.

Top misses are completed result states the verifier still fails to recover or
normalize:

- EEG Yes/Abnormal: 7 misses across EA0044, EA0111, EA0117, EA0132, EA0182,
  EA0200. These are often terse heading lines or explanatory EEG-result
  references, e.g. spike-and-wave, multifocal abnormalities, temporal slowing,
  or captured events.
- MRI Yes/Abnormal: 4 misses across EA0046, EA0061, EA0104, EA0106. These are
  mostly structural findings such as gliosis, meningioma/post-surgical changes,
  or stable lesion language.
- EEG Yes/Normal: 2 misses across EA0102 and EA0146.
- MRI Yes/Normal: 2 misses across EA0188 and EA0197.

Top over-emissions are now smaller and clinically ambiguous:

- EEG Yes/Abnormal: 2 over-emissions, including EEG-confirmed nonepileptic
  events and EEG-confirmed diagnosis wording.
- EEG Yes/Normal: 2 over-emissions where lack of ictal EEG change was inferred
  as a normal investigation.
- One each: EEG Unknown for "captured on EEG", MRI Abnormal for "normal apart
  from tiny hyperintensities", MRI Normal for stable post-surgical appearances,
  and MRI Unknown for a stable follow-up scan.

## Next Hypotheses

Further Investigations gains are possible but lower priority than Prescription:

- A conservative heading-result recovery rule could add abnormal EEG/MRI from
  explicit `Investigations:` lines with abnormal tokens (`spike and wave`,
  `slow waves`, `gliosis`, `lesion`, `meningioma`, `post surgery changes`).
- A result-state arbitration rule could rewrite "confirmed on EEG" in
  nonepileptic contexts to EEG Normal rather than Abnormal, but this is more
  clinically subtle and should be tested separately.
- Do not use v0.42 union without strong suppression; the union ablation proves
  recall is available, but the false-positive cost is too high.

## Artifacts

- Manifest: `configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v07_dev140.yaml`
- Assembly JSON: `experiments/exectv2_holistic_finding_assembly_v07_dev140_20260621.json`
- Assembly JSONL: `experiments/exectv2_holistic_finding_assembly_v07_dev140_20260621.jsonl`
- Assembly report: `docs/experiments/exectv2/key_entities/exectv2_holistic_finding_assembly_v07_dev140_20260621.md`
- Error ledger JSON: `experiments/exectv2_holistic_finding_assembly_v07_error_ledger_dev140_20260621.json`
- Error ledger MD: `experiments/exectv2_holistic_finding_assembly_v07_error_ledger_dev140_20260621.md`
- Component JSONL: `experiments/exectv2_llm_investigations_arbitration_v02_dev140_20260621.jsonl`
- Component report: `experiments/exectv2_llm_investigations_arbitration_v02_dev140_20260621.md`
