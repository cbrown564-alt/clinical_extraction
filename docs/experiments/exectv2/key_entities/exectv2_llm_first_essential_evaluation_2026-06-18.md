# ExECTv2 LLM-First Essential Clinical Evaluation

- Generated: `2026-06-18`
- Split: `dev` (140 letters)
- Plan: `docs/plans/exectv2/11_llm_first_essential_clinical_evaluation_plan.md`
- Mode: **analysis-only, no model calls** (existing artifacts replayed).

Architectures and ownership (plan §Evaluation Contract):

| Architecture | Ownership | Source |
| --- | --- | --- |
| deterministic_all9 | `rules_only` | generated (run_all9_on_letters) |
| llm_only_all_entities (single pass) | `llm_first` | experiments/exectv2_audit_llm_only_all_entities_full200_gpt41mini_20260612.jsonl |
| hybrid_all_entities (candidate-set + verify) | `hybrid` | experiments/exectv2_hybrid_all_entities_dev140_gpt41mini_20260617.jsonl |

## 5. Baseline and hybrid comparator — essential clinical-recovery headline

Clinical-fact recovery over the five essential families only (Prescription, SeizureFrequency, Diagnosis, EpilepsyCause, Investigations). The primary headline is CUI-free; certainty remains a deterministic projection layer and is reported separately from the LLM-owned clinical headline.

| Architecture | Ownership | Recovery F1 | Precision | Recall |
| --- | --- | ---: | ---: | ---: |
| deterministic_all9 | `rules_only` | 0.716 | 0.721 | 0.711 |
| llm_only_all_entities (single pass) | `llm_first` | 0.422 | 0.478 | 0.379 |
| hybrid_all_entities (candidate-set + verify) | `hybrid` | 0.550 | 0.559 | 0.542 |

CUI-projected companion score (reported because the legacy SeizureFrequency state key can use CUI as seizure-type identity):

| Architecture | CUI-projected essential F1 | Precision | Recall |
| --- | ---: | ---: | ---: |
| deterministic_all9 | 0.724 | 0.729 | 0.719 |
| llm_only_all_entities (single pass) | 0.422 | 0.478 | 0.379 |
| hybrid_all_entities (candidate-set + verify) | 0.566 | 0.575 | 0.556 |

### Per-entity clinical-recovery headline F1

| Entity | deterministic_all9 | llm_only_all_entities | hybrid_all_entities |
| --- | ---: | ---: | ---: |
| Prescription | 0.907 | 0.747 | 0.824 |
| SeizureFrequency | 0.728 | 0.012 | 0.296 |
| Diagnosis | 0.699 | 0.316 | 0.461 |
| EpilepsyCause | 0.622 | 0.000 | 0.200 |
| Investigations | 0.526 | 0.748 | 0.741 |

## 4. LLM-first single-call report

Single all-entities pass (`llm_only_all_entities (single pass)`), ownership `llm_first`. Overall clinical recovery F1 **0.422** (P 0.478 / R 0.379).

Per-entity reading (which families clear, which collapse):

| Entity | Recovery F1 | Precision | Recall |
| --- | ---: | ---: | ---: |
| Prescription | 0.747 | 0.816 | 0.689 |
| SeizureFrequency | 0.012 | 0.013 | 0.011 |
| Diagnosis | 0.316 | 0.416 | 0.255 |
| EpilepsyCause | 0.000 | 0.000 | 0.000 |
| Investigations | 0.748 | 0.675 | 0.838 |

### Evidence validation and error taxonomy

Evidence policy: exact source-substring evidence is required when a prediction emits evidence text. Error categories are coarse diagnostics and can overlap.
Invalid evidence counts emitted mentions without exact source-substring evidence, including missing evidence.

- evidence present: **1.000** (743/743)
- exact evidence: **1.000** (743/743)
- candidate_miss: **563**
- wrong_detail_selection: **362**
- evidence_failure: **0**

Evidence-validity by essential family for the single-pass LLM artifact:

| Entity | Predictions | Evidence present | Present rate | Exact evidence | Exact rate | Invalid evidence | Invalid rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 252 | 252 | 1.000 | 252 | 1.000 | 0 | 0.000 |
| SeizureFrequency | 152 | 152 | 1.000 | 152 | 1.000 | 0 | 0.000 |
| Diagnosis | 164 | 164 | 1.000 | 164 | 1.000 | 0 | 0.000 |
| EpilepsyCause | 12 | 12 | 1.000 | 12 | 1.000 | 0 | 0.000 |
| Investigations | 163 | 163 | 1.000 | 163 | 1.000 | 0 | 0.000 |

## 2. Certainty projection audit

SeizureFrequency already ignores Certainty/Negation in its benchmark key (guideline convention), so it contributes no certainty-only loss.

Certainty-only benchmark loss is **0.003 F1** (4 TP) — measured on CUI-projected predictions so the residual is owned by `Certainty`/`Negation`, not missing CUI.

Guideline-rule projection now uses ExECT v9 List 2 certainty triggers, default affirmed negation, and the PatientHistory febrile-negation exception. It is scored after the clinical concept is selected.

Limitation: This audit implements explicit guideline-trigger rules and scores them over gold rows, using source-local context when offsets/text are available. It estimates projection reliability after the clinical concept is already selected; it does not license deterministic concept generation.

Gold distribution and default-projection ceiling (fraction correct if a rule assigned the dominant value):

| Entity | Certainty present | distinct | default ceiling | Negation present | distinct | default ceiling |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BirthHistory | 0.97 | 2 | 0.90 | 1.00 | 1 | 1.00 |
| Diagnosis | 1.00 | 3 | 0.83 | 0.99 | 1 | 1.00 |
| EpilepsyCause | 1.00 | 2 | 0.86 | 0.95 | 1 | 1.00 |
| Investigations | 0.00 | 0 | 0.00 | 0.00 | 0 | 0.00 |
| Onset | 0.94 | 1 | 1.00 | 0.94 | 1 | 1.00 |
| PatientHistory | 1.00 | 4 | 0.92 | 1.00 | 2 | 0.97 |
| Prescription | 0.00 | 0 | 0.00 | 0.00 | 0 | 0.00 |
| SeizureFrequency | 0.01 | 1 | 1.00 | 0.01 | 1 | 1.00 |
| WhenDiagnosed | 1.00 | 1 | 1.00 | 1.00 | 1 | 1.00 |

Guideline projection accuracy over gold rows:

| Entity | Certainty coverage | Certainty accuracy | Negation coverage | Negation accuracy |
| --- | ---: | ---: | ---: | ---: |
| BirthHistory | 1.00 | 1.00 | 1.00 | 1.00 |
| Diagnosis | 1.00 | 0.81 | 1.00 | 1.00 |
| EpilepsyCause | 1.00 | 0.95 | 1.00 | 1.00 |
| Investigations | 0.00 | 0.00 | 0.00 | 0.00 |
| Onset | 1.00 | 0.94 | 1.00 | 1.00 |
| PatientHistory | 1.00 | 0.82 | 1.00 | 0.99 |
| Prescription | 0.00 | 0.00 | 0.00 | 0.00 |
| SeizureFrequency | 0.00 | 0.00 | 0.00 | 0.00 |
| WhenDiagnosed | 1.00 | 0.91 | 1.00 | 1.00 |

## 3. CUI projection audit

CUI is benchmark-format projection: the benchmark key keeps CUI, the semantic key drops it. The benchmark-minus-semantic delta is owned by deterministic CUI projection, never by LLM clinical reasoning.

- Raw LLM benchmark F1 (no CUI emitted): **0.000**
- After deterministic CUI projection: **0.110** (projection recovers +0.110 F1)
- CUI-free semantic surface: **0.115** (residual CUI loss after projection: 0.005)

Concept bucket ledger (over gold concepts carrying a CUI):

| Bucket | Concepts | Mentions |
| --- | ---: | ---: |
| one_to_one | 283 | 1325 |
| result_conditioned | 2 | 10 |
| gold_inconsistent | 8 | 144 |
| missing_mapping | 149 | 162 |

Deterministic projection over gold (CUI stripped first, then re-attached — an in-sample lexicon lookup):

- coverage **0.890** (1317/1479)
- correctness **0.953** (1255/1317)
- missing_mapping mentions: **162**

## 6. Benchmark projection gap ledger

Per architecture, the artifact projection layers from the clinical-recovery scorecard (per-item F1): phrase-only -> semantic (CUI dropped) -> benchmark (CUI kept). The phrase->semantic step is attribute/format loss; the semantic->benchmark step is CUI projection loss.

| Architecture | phrase_only | semantic | benchmark |
| --- | ---: | ---: | ---: |
| deterministic_all9 | 0.540 | 0.372 | 0.354 |
| llm_only_all_entities (single pass) | 0.143 | 0.122 | 0.110 |
| hybrid_all_entities (candidate-set + verify) | 0.329 | 0.219 | 0.190 |

## 1. Essential clinical scorer specification

The essential clinical scorer is assembled in `reports/llm_first_essential_evaluation.py` from the existing `clinical_recovery_scorecard.py` / `scoring.py` primitives. It aggregates only Prescription, SeizureFrequency, Diagnosis, EpilepsyCause, and Investigations. The primary surface strips CUI from gold and predictions before scoring; Diagnosis and EpilepsyCause use concept-only recovery so `Certainty`/`Negation` do not drive the LLM-owned headline. CUI-projected and certainty-dropped scores are reported as diagnostic projection layers.
