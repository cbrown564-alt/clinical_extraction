# Rules-only Investigations result binding

Date: 2026-08-15
Status: **landed; holdout remasured; Decision 0046 fills updated**
Parent: [category-cut performance](../shared/six_model_category_cut_performance_2026-08-06.md)
Code: [`all_entities/investigations.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/all_entities/investigations.py)
Tests: `tests/test_exectv2_investigations_extraction.py`
Artifact: [`experiments/exectv2_rules_only_investigations_result_binding_dev140_20260815.json`](../../experiments/exectv2_rules_only_investigations_result_binding_dev140_20260815.json)

## Plain answer

The standalone Investigations extractor was a same-sentence token
detector with a nine-word abnormal list. It now binds a Normal /
Abnormal / Unknown result to each completed EEG / MRI / CT mention.

On `dev140`, Investigations clinical-headline F1 moves **0.5325 →
0.9579** (precision **1.000**, recall **0.9191**). Four-family
headline moves **0.8160 → 0.8982**. On aggregate-only `test60`,
Investigations moves **0.4037 → 0.8706** and four-family headline
moves **0.7154 → 0.7918**. Prescription and Diagnosis on holdout are
unchanged. Hybrid Investigations is still a no-op. Decision 0046
selected fills are these remasured numbers. No holdout rows were
inspected.

## Why the old rule failed

Gold wants `(modality, performed, result)`. Official spans are usually
just `MRI` / `EEG` / `CT`. The finding is List 9 prose, often in the
next sentence. The old rule emitted every token, including planned
tests, and only recognised `abnormal`, `lesion`, `infarct`,
`sclerosis`, `dysplasia`, `spike and wave`, `polyspike`, and
`epileptiform`.

On the previous `dev140` surface that produced 187 keys against 136
gold, 94 had no result. Almost every miss was “found the modality,
missed the finding.”

## What changed

Gold-free predicates only:

| Behaviour | Rule |
| --- | --- |
| Finding language | ExECT List 9 phrases, plus a few closed clinical synonyms (`hyperintensity`, `hippocampus`) |
| Local binding | Result cues stay with the nearest modality; coordinated `MRI and EEG have been normal` share a trailing result |
| Anaphora | Next sentence starting `It` / `This` / `They` / `Both` can carry the finding |
| Planned tests | `arrange` / `request` / `await` / `repeat` mentions are dropped |
| Polarity | `no epileptiform` is Normal; a stated result beats `I have not seen the report` |
| ECG | `normal QT` is not a CT result; `ECG and CT were normal` still grades the CT |
| Emission | Mentions without a result are not emitted; identical `(modality, result)` pairs collapse |

## Development measurement

Split: `dev140`. Scorer: Decision 0046 `headline_target`. No model
calls.

| Surface | Before | After |
| --- | ---: | ---: |
| Investigations F1 | 0.5325 | **0.9579** |
| Investigations P / R | 0.460 / 0.632 | **1.000 / 0.919** |
| Four-family F1 | 0.8160 | **0.8982** |
| Diagnosis F1 | 0.8599 | 0.8633 |
| SeizureFrequency F1 | 0.8323 | 0.8333 |
| Prescription F1 | 0.9615 | 0.9615 |

Remaining development Investigations misses are almost all gold
duplicate keys (one completed scan annotated twice). Two true gaps
stay: a CT with no result language that gold marks Unknown, and a PNES
letter whose gold EEG-Normal is only “confirmed on EEG.” Those are not
safe to generalise without empty-gold false positives.

## Holdout remasure

Split: locked `test60` (59 loadable letters). Row policy:
aggregate-only. Scorer: the same `headline_target`. No letter
identifiers, notes, predictions, or failure cases were read.

| Surface | Before | After |
| --- | ---: | ---: |
| Investigations F1 | 0.4037 | **0.8706** |
| Investigations P / R | 0.355 / 0.468 | **0.974 / 0.787** |
| Four-family F1 | 0.7154 | **0.7918** |
| Diagnosis F1 | 0.8550 | 0.8550 |
| SeizureFrequency F1 | 0.5652 | 0.5797 |
| Prescription F1 | 0.8395 | 0.8395 |

The Investigations lift transfers. Diagnosis and Prescription are
unchanged. Seizure frequency remains the rules-only holdout floor.

Owners:
[`dev140` JSON](../../experiments/exectv2_rules_only_four_family_clinical_headline_dev140_20260815.json),
[`test60` JSON](../../experiments/exectv2_rules_only_four_family_clinical_headline_test60_20260815.json).

## Claim boundary

Rules-only four-family remasure after a semantic Investigations change.
`test60` is aggregate-only. Not a hybrid change, not LLM-only, and not
clinical validation. The selected hybrid Investigations transform is
still a no-op.
