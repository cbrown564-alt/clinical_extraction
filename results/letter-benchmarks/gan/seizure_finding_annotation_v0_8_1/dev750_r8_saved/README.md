# One-year timing amendment: saved R8 development replay

This is a versioned correction of the **gold timing field** across all 750 Gan
synthetic development letters. It changes neither the v0.8 finding inventory nor
the saved R8 responses. The v0.8 reference, score and review bundle remain
available at their original paths.

| Saved-response score | v0.8 | v0.8.1 timing |
| --- | ---: | ---: |
| Gold findings | 1,575 | 1,575 |
| True positives | 1,025 | 1,019 |
| Extra predictions | 416 | 422 |
| Missed gold | 550 | 556 |
| Usable responses | 714 | 714 |

There are **94 audited timing corrections**: 79 historical-to-current and 15
current-to-historical. Twenty-four of the former have explicit calendar dates
inside the last year. Fifty-three use a stated recent month, relative interval
or nearby dated event; two describe a present, unchanged pattern. The 15 older
events include dated last seizures, elapsed intervals over a year and one
synthetic letter that says “2017 so far” despite a 2025 letter date.

The source-bearing adjudication file is local:
`runs/seizure_finding_annotation_v0_8_1/dev750_r8_saved/timing_adjudications.jsonl`.
The full converted reference and side-by-side workbench bundle are beside it.
Every changed finding retains its ID, source ID, source hash, source quotation,
document date, old timing, new timing and basis. The reproducible producer is
`scripts/benchmarks/retime_findings_v081.py`. The score metadata records the
base reference and score hashes.

One coarse date remains unresolved: source row 14592, finding `f3`, says only
that two lifetime episodes occurred in **2023**, with a 14 June 2024 clinic
date. Part of 2023 falls on each side of the cutoff. Its existing historical
label is retained under the explicit past-wording fallback; no month is
invented. It should receive human review if that distinction becomes
consequential.

This is a changed development reference, not a new model run or evidence that
the model became worse. The R8 prompt used for the saved responses still has
the former timing rule. The prospective R9 prompt candidate states the one-year
boundary and has not been used for inference.

## Separate event and measurement diagnostic

The additive [component score](component_score.json) pairs whole-finding
matches first, then pairs remaining gold and saved R8 findings one-to-one when
their exact source quotations overlap. It scores two fields independently:
`measurement` is the native type, value and denominator; `subtype` is the set of
named seizure features after removing cluster and seizure-day unit words; and
`event` is the broader event-label key, including counted unit. Observation period,
timing, seizure status and evidence remain visible in the original whole-finding
score. A field mismatch gives a false positive and false negative for that field;
an unpaired finding does the same. This diagnostic does **not** replace the
whole-finding endpoint.

| Component | Correct | Extra | Missed | Precision | Recall |
| --- | ---: | ---: | ---: | ---: | ---: |
| Measurement | 1,133 | 308 | 442 | 78.6% | 71.9% |
| Seizure subtype | 1,242 | 199 | 333 | 86.2% | 78.9% |
| Event label | 1,222 | 219 | 353 | 84.8% | 77.6% |

On source 3999, both saved R8 findings have the correct measurements, but the
monthly rate is attached to generic `seizures` instead of the gold `focal
impaired-awareness episodes`. That finding receives measurement credit but no
subtype or event-label credit. The other finding on the letter receives all
three. This is a
synthetic development diagnostic based on saved R8 responses, not an R9 run.
Only source-exact overlapping quotations qualify for residual pairing, so a
paraphrased or invalid quote can still leave both sides unpaired. Event-label
agreement uses the existing v0.7 key and can treat generic labels as equivalent.
The subtype diagnostic is a source-label token comparison, not a
clinician-validated ontology. Reproduce with
`.venv/bin/python scripts/benchmarks/score_finding_components_v081.py`.
