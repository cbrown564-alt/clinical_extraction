# Inspectable Clinical Extraction from Epilepsy Letters

Updated: 2026-07-14
Status: working manuscript

The [paper claim status](../canon/10_paper_provenance.md) limits what this
manuscript may say. The [retained evidence index](../experiments/retained_evidence_manifest.md)
records the supporting files and hashes.

## Abstract

Clinical extraction results are difficult to interpret when model output,
deterministic rules, repair, evidence checks, and scoring are reported as one
method. We evaluate three methods—rules only, LLM only, and LLM with rules—on
two epilepsy-letter tasks. Gan 2026 asks for one current seizure-frequency
label; ExECTv2 extracts several epilepsy phenotypes. On Gan validation750, the
three selected methods produced 697/750, 581/750, and 661/748 rendered
Purist-correct predictions. Saved Gan holdout results are 364/450 for the
single-pass system and 379/450 for a multi-model comparison. On ExECT dev140,
rules only reached 0.6020 paper-derived all-features macro item F1 (0.3548 under
the existing strict micro scorer), the GEPA LLM-only negative comparison
reached 0.7393 clinical fact F1, and the LLM-with-rules method reached 0.9189.
Three full200 model runs ranged from 0.8197 to 0.8566 clinical fact F1, but used
different runtime conditions. Replays of saved outputs found normalization
gains on both tasks (+0.0389 ExECT; +0.0293 Gan); the exact-evidence check did
not change those replay scores. The selected evidence supports a reproducible
component comparison with explicit data limits and a tested implementation of
the published ExECT metric views. It does not reproduce the original ExECT
system or its reported 0.87/0.90 scores, and it does not support a six-model
conclusion or independent clinical validation.

## 1. Introduction

Epilepsy letters contain temporal statements, clinical terminology, medication
regimens, investigations, and ambiguous distinctions between current and past
events. Language models can handle varied phrasing but can hide how an answer
was chosen. Deterministic systems are easier to inspect but often miss
linguistic variation and long-range clinical relationships.

This study keeps extraction, clinical selection, normalization, repair,
evidence checking, and scoring separate. The same package supports a deep
single-label task and a broader multi-entity task. We ask which components help,
which results transfer, and which conclusions remain unsupported.

The paper contributes:

1. selected rules-only, LLM-only, and LLM-with-rules results on both tasks;
2. component-level ownership of clinical and formatting decisions;
3. saved aggregate Gan holdout evidence and a three-model ExECT study; and
4. recorded prompts, scorers, splits, repairs, runtimes, dependencies, and hashes.

## 2. Related work

ExECT extracted structured epilepsy data from clinic letters, and later work
described the annotation resource [1,2]. Other studies extracted seizure
frequency with machine reading, pretrained language models, fine-tuned LLMs,
and synthetic letters [3–6]. We compare rules and models while keeping their
different repair and scoring steps visible.

## 3. Methods

### 3.1 Tasks and data splits

Gan 2026 asks for one current seizure-frequency label per synthetic letter.
Validation750 permits row review and replay. Test450 is locked: only saved
aggregate results may be used, and holdout failures cannot guide development.

ExECTv2 covers diagnosis, seizure frequency, prescriptions, and investigations
in the main comparison. The rules-only reference also covers five additional
entity types. Dev140 permits row review. Full200 combines dev140 with held-out
test60 and is therefore not an independent holdout.

### 3.2 Compared methods

- **Rules only:** deterministic rules determine clinical facts and format them.
- **LLM only:** the model determines clinical facts; deterministic code validates
  or formats facts the model has already selected.
- **LLM with rules:** model and deterministic code can both affect clinical meaning.

Gan's selected combined method uses one model call to extract structured events,
then deterministic normalization and scoring. ExECT combines entity-specific
extractors and deterministic transforms before scoring.

### 3.3 Scores

Gan uses Purist and Pragmatic label accuracy; Purist is primary. ExECT's primary
internal score is de-duplicated clinical fact recovery (`clinical_headline`).
Phrase, CUI, evidence-valid, and full-attribute scores remain separate.
`clinical_headline` is not the published strict ExECT benchmark.

The paper-derived ExECT views score each entity type separately and report their
macro mean. Normalized phrase compares entity-linked surface forms; CUI compares
entity-linked concept identifiers; all features adds the entity-specific
attributes. Certainty applies to Diagnosis and PatientHistory; negation applies
only to PatientHistory.
Per-item scoring counts every mention, while per-letter scoring asks whether a
letter contains at least one correct mention and attribute bundle.

### 3.4 Repair and attribution

The pipeline records raw model selection, JSON or format repair, evidence repair,
clinical deterministic repair, final formatting, and scoring separately.
Transport fixes and output-shape repairs do not count as model quality. A rule
that changes clinical meaning remains attributable to deterministic code.

### 3.5 Reproducibility

Retained evidence index v3 records source commit
`465621341c6af59f2fc028be7bf5f9e325739c50`, dependency versions, prompts,
scorers, split rules, repair policies, model policy, runbooks, and CI. Any change
that can alter a prediction requires a new recorded version and complete replay.
This rule does not authorize model calls.

## 4. Results

### 4.1 Two-task comparison

| Task | Method | Split | Result | Use |
| --- | --- | --- | ---: | --- |
| ExECTv2 | Rules only | dev140 | all-features macro item F1 0.6020 | Paper-derived metric development reference; strict micro item F1 0.3548 |
| ExECTv2 | LLM only | dev140 | clinical fact F1 0.7393 | GEPA negative development comparison |
| ExECTv2 | LLM with rules | dev140 | clinical fact F1 0.9189 | Current development reference |
| Gan 2026 | Rules only | validation750 | 697/750 Purist | Development comparison |
| Gan 2026 | LLM only | validation750 | 581/750 Purist | Development comparison |
| Gan 2026 | LLM with rules | validation750 | 661/748 rendered Purist | Development comparison |

All six runs replay from selected files without model calls. The ExECT combined
method also returns evidence-valid F1 0.8913. Its legacy benchmark/CUI companion
replays at 0.4791 versus 0.4729 in the saved run; that diagnostic does not define
the new paper-derived rules-only result and does not affect the reproduced
0.9189 clinical fact score.

### 4.2 ExECT paper-derived metric replay

| View | Macro per-item F1 | Macro per-letter F1 |
| --- | ---: | ---: |
| Normalized phrase | 0.5687 | 0.7518 |
| CUI | 0.7144 | 0.8534 |
| All features | 0.6020 | 0.7922 |

The no-call rules-only replay covers all nine entity types on dev140. CUI
identity recovers many matches lost to surface variation, while the fall from
CUI to all features shows that attribute agreement is the main remaining loss,
especially for Diagnosis. One gold mention and six predictions lack a CUI;
missing identifiers never match each other. The paper's original 0.87 per-item
and 0.90 per-letter results remain reference values, not reproduced scores.

### 4.3 Gan locked holdout

| Method | Purist | Limit |
| --- | ---: | --- |
| Single-pass event extractor | 364/450 (0.809) | Saved aggregate only |
| Multi-model comparison (`V12`) | 379/450 (0.842) | Saved aggregate; source removed |

The saved difference is 15 rows, or 3.33 percentage points. A cold execution
requires one model pass per note for the single-pass system and three for the
saved V12 test condition (GPT and Qwen extractors plus one reasoner). DeepSeek
input was unavailable on all 450 rows. The V12 holdout audit itself made 450
new reasoner calls while replaying the two upstream traces.

Matched prompt/completion tokens, cost, wall time, hardware, and cache telemetry
were not retained. These runs therefore support a quality-versus-model-pass
comparison, not measured token, dollar, energy, or latency efficiency.

### 4.4 ExECT three-model results

| Model condition | Overall | Diagnosis | Seizure frequency | Prescription | Investigations | Call / parse failures |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| DeepSeek chat | 0.8566 | 0.8708 | 0.7602 | 0.8926 | 0.9091 | 0 / 1 |
| GPT-4.1-mini | 0.8356 | 0.8397 | 0.7525 | 0.8926 | 0.8563 | 0 / 0 |
| Qwen 3.6 35B, repair v02 | 0.8197 | 0.8307 | 0.7020 | 0.8926 | 0.8503 | 0 / 0 |

These are full200 development-inclusive aggregates. They do not form a strict
same-prompt comparison: GPT used temperature 0.3, and Qwen used a shorter prompt
and output repair. Three further model conditions remain to be specified.

### 4.5 Component replays

| Component removed | ExECT dev140 score change | Gan validation750 score change |
| --- | ---: | ---: |
| Normalization and shared dictionary | +0.0389 | +0.0293 |
| Exact-evidence check | 0.0000 | 0.0000 |

No score change does not make the evidence check unnecessary. Rejection and
repair tests cover malformed or unsupported outputs that do not occur in the
selected replay rows.

### 4.6 Reliability evidence

| Subject | Selected result | Limit |
| --- | --- | --- |
| ExECT evidence | Minimum exact-evidence rate 1.0000 for the combined dev140 run | Development result |
| ExECT internal calibration | Brier 0.2225; base-rate Brier 0.2340; ECE 0.0587 | Full200 aggregate scoring-rule result |
| Gan grounding | Validation evidence exists for each selected method | Metrics differ by method |
| Clean-checkout reproducibility | 1,157 tests, Ruff, mypy, hashes, split restrictions, and six replays passed on Python 3.11 | Engineering verification, not clinical validation |

Model-reported confidence is not used, and no low-burden review policy has been
adopted. No selected report supports a cross-task over-reading claim.

## 5. Discussion

The repository can replay six selected runs while preserving which component
made each clinical decision. On ExECT's internal clinical fact score, the
combined method exceeds the selected rules-only and LLM-only development
references. Those three results do not share the paper-derived metric views, so
they cannot establish strict benchmark superiority. The rules-only replay does
show that CUI matching recovers surface-form variation, but feature completion
remains a larger limitation than identifier coverage.

The ExECT pipeline ran with three different model providers. Runtime differences
and the incomplete model set limit the conclusion to those named runs.
Normalization helped on both development replays. The exact-evidence result
shows why a component cannot be judged by aggregate score alone: its rejection
and repair behavior require direct tests.

## 6. Limitations

- Gan test450 permits saved aggregate results only.
- ExECT full200 includes development rows and is not an independent holdout.
- The internal ExECT clinical fact score is not the published strict benchmark.
- The paper-derived rules-only replay uses permitted development data and does
  not reproduce the original ExECT system, annotation process, or reported
  0.87/0.90 validation scores.
- A legacy ExECT benchmark/CUI companion has a small unresolved scorer difference.
- The model study covers three of six planned conditions and uses different runtimes.
- Model-reported confidence and low-burden review routing are not validated.
- Annotation findings were reviewed internally, not by an independent clinical team.
- The selected evidence does not support a cross-task over-reading claim.

## 7. Conclusion

The selected results support an inspectable comparison of rules-only, LLM-only,
and LLM-with-rules methods on two tasks, saved Gan holdout results, and three
named ExECT model runs. They do not yet support strict ExECT benchmark
score reproduction, a six-model conclusion, or independent clinical validation.

## References

1. Fonferko-Shadrach B, et al. *BMJ Open*. 2019;9:e023232.
2. Fonferko-Shadrach B, et al. *Journal of Biomedical Semantics*. 2024;15:17.
3. Xie K, et al. *JAMIA*. 2022;29:873–881.
4. Abeysinghe R, et al. *npj Digital Medicine*. 2025.
5. Holgate B, et al. *BioNLP*. 2025:44–55.
6. Gan Y, et al. arXiv:2603.11407. 2026.
