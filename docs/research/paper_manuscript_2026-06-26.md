# Inspectable Clinical Extraction from Epilepsy Letters

Updated: 2026-07-18
Status: working manuscript

The [paper claim status](../canon/10_paper_provenance.md) limits what this
manuscript may say. The [retained evidence index](../experiments/retained_evidence_manifest.md)
records the supporting files and hashes.

## Abstract

Clinical extraction results are difficult to interpret when model output,
deterministic rules, repair, evidence checks, and scoring are reported as one
method. We evaluate three methods—rules only, LLM only, and LLM with rules—on
two epilepsy-letter tasks. Gan 2026 asks for one current seizure-frequency
label; ExECTv2 extracts several epilepsy phenotypes. On Gan dev750, the
three selected methods produced 697/750, 581/750, and 661/748 rendered
Purist-correct predictions. Saved Gan holdout results are 364/450 for the
single-pass system and 379/450 for a multi-model comparison. On ExECT dev140,
rules only reached 0.6020 paper-derived all-features macro item F1 (0.3548 under
the existing strict micro scorer), the GEPA LLM-only negative comparison
reached 0.7393 clinical fact F1, and the historical LLM-with-rules development
control reached 0.9189. That control uses a deterministic Prescription producer
and a Seizure Frequency extractor union, so it is not the final model-led
architecture. In the fixed six-model ExECT test60 panel, Sol led at 0.8047
clinical-headline F1; in the selected matched Gan v0.5 test450 panel, Sol led
at 373/450 Purist. Replays of saved outputs found normalization
gains on both tasks (+0.0389 ExECT; +0.0293 Gan); the exact-evidence check did
not change those replay scores. The selected evidence supports a reproducible
component comparison with explicit data limits and a tested implementation of
the published ExECT metric views. It does not reproduce the original ExECT
system or its reported 0.87/0.90 scores, general model superiority, cross-task
reliability transfer, or independent clinical validation.

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
3. saved aggregate Gan holdout evidence and partial ExECT model-transfer evidence;
   and
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
Dev750 permits row review and replay. Retained artifacts use the legacy split
identifier `validation750`. Test450 is locked: only saved
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

For the final ExECT model comparison, the named model must supply the candidate
facts for all four main families. Deterministic clinical changes remain
attributed, but an independent Prescription or Seizure Frequency extractor
cannot replace or be unioned into the named model's answer. The retained `v08`
run predates and does not satisfy this final ownership boundary.

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
| ExECTv2 | Historical LLM with rules (`v08`) | dev140 | clinical fact F1 0.9189 | Reproducible development control; not the final model-led family architecture |
| Gan 2026 | Rules only | dev750 | 697/750 Purist | Development comparison |
| Gan 2026 | LLM only | dev750 | 581/750 Purist | Development comparison |
| Gan 2026 | LLM with rules | dev750 | 661/748 rendered Purist | Development comparison |

All six runs replay from selected files without model calls. The ExECT combined
method also returns evidence-valid F1 0.8913. Its legacy benchmark/CUI companion
replays at 0.4791 versus 0.4729 in the saved run; that diagnostic does not define
the new paper-derived rules-only result and does not affect the reproduced
0.9189 clinical fact score. Its deterministic Prescription producer and
Seizure Frequency extractor union are now disclosed architecture limits, not
model contributions.

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

### 4.4 Fixed ExECT model comparison

| Model condition | dev140 | test60 | Diagnosis | Seizure frequency | Prescription | Investigations | Test call / parse failures |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT-4.1-mini | 0.8202 | 0.7572 | 0.8470 | 0.6936 | 0.8672 | 0.8538 | 0 / 0 |
| GPT-5.6 Luna | 0.8832 | 0.7950 | 0.8910 | 0.7892 | 0.9250 | 0.9202 | 0 / 0 |
| GPT-5.6 Sol | 0.8920 | 0.8047 | 0.8882 | 0.8012 | 0.9432 | 0.9358 | 0 / 0 |
| DeepSeek V4 Flash | 0.8767 | 0.7881 | 0.8764 | 0.7610 | 0.9280 | 0.9389 | 0 / 0 |
| Qwen 3.6:35B, local | 0.8571 | 0.7872 | 0.8720 | 0.7062 | 0.9249 | 0.9105 | 0 / 0 |
| Gemma 4 26B, local | 0.8016 | 0.7169 | 0.8378 | 0.6226 | 0.9046 | 0.8047 | 0 / 6 |

Decision 0039 fixes the six model conditions. Decision 0040 requires each
named model to supply Diagnosis, Seizure Frequency, Prescription, and
Investigations facts, followed only by attributable deterministic correction.
The historical GPT, DeepSeek, and Qwen rows are excluded because their
Prescription column was deterministic-only and their Seizure Frequency column
included an independent extractor union. The fixed rows use the decision-0041
one-call architecture and preserve attribution, `state_profile`,
schema/evidence, and regression records. DeepSeek uses the official
`deepseek-v4-flash` route. Dev140 family scores are shown
above; test60 is aggregate only and uses the same internal scorer. Hosted/local
route and temperature differences prevent a model-neutral capability ranking.

### 4.5 Component replays

| Component removed | ExECT dev140 score change | Gan dev750 score change |
| --- | ---: | ---: |
| Normalization and shared dictionary | +0.0389 | +0.0293 |
| Exact-evidence check | 0.0000 | 0.0000 |

No score change does not make the evidence check unnecessary. Rejection and
repair tests cover malformed or unsupported outputs that do not occur in the
selected replay rows.

### 4.6 Reliability evidence

The paper-facing framework applies the same eight reliability criteria to both
tasks: clinical correctness and generalization; clinical selection and
unsupported inference; evidence support and faithfulness; uncertainty and
selective action; robustness and stability; component attribution and
correction safety; coverage and clinical-slice behavior; and operational
reliability. Measures, denominators, stages, and evidence limits remain
task-specific. Construct-only and not-comparable results do not produce a
cross-task numerical difference, and no composite reliability score is
reported.

| Subject | Selected result | Limit |
| --- | --- | --- |
| ExECT evidence | Minimum exact-evidence rate 1.0000 for the combined dev140 run | Development result |
| ExECT internal calibration | Brier 0.2225; base-rate Brier 0.2340; ECE 0.0587 | Full200 aggregate scoring-rule result |
| ExECT model confidence | Test60 failure AUROC 0.5394 GPT-4.1-mini; 0.5503 historical DeepSeek; 0.4895 Qwen | Aggregate negative result for saved outputs |
| ExECT six-model SF state replay | Final projection/suppression improves state-profile F1 for all six; 54 wrong-to-correct and one correct-to-wrong transition | dev140 development evidence; repeated letters across models |
| Gan grounding | Validation evidence exists for each selected method | Metrics differ by method |
| Clean-checkout reproducibility | Tests, Ruff, mypy, hashes, split restrictions, and six reference replays passed | Engineering verification, not clinical validation |

Neither predeclared model-confidence review rule met its test60 catch-rate and
burden gates, so no confidence-based review policy was adopted. No selected
result supports a cross-task over-reading claim. The predeclared ExECT analogue
has zero gold unknown-only letters; empty-gold letters remain diagnostic rather
than being substituted after the result. A 48-item ExECT dev140 semantic-support
sample is prepared across six models and four families, but independent review
has not started; exact source presence is therefore not presented as semantic
or clinical faithfulness.

## 5. Discussion

The repository can replay six selected runs while preserving component
provenance. On ExECT's internal clinical fact score, the historical `v08`
control exceeds the selected rules-only and LLM-only development references,
but its Prescription and Seizure Frequency ownership does not meet the final
model-led architecture. Those three results also do not share the
paper-derived metric views, so they cannot establish strict benchmark
superiority. The rules-only replay does
show that CUI matching recovers surface-form variation, but feature completion
remains a larger limitation than identifier coverage.

Historical ExECT artifacts ran with three different model providers, but their
Prescription and Seizure Frequency columns are excluded from model comparison.
The fixed panel replaces them with six exact model conditions under the same
component boundary. Runtime differences still prevent a general model-ordering
conclusion, and the ExECT and Gan orderings differ substantially.
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
- The selected `v08` control does not meet the final model-led family ownership
  boundary because Prescription is deterministic and Seizure Frequency uses an
  independent extractor union.
- The fixed six-model panels use different provider transports, temperatures,
  token limits, and local versus hosted runtimes.
- Model-reported confidence was uninformative for the three saved historical
  outputs under the frozen test60 analysis; this is not deployment calibration
  or a six-model result.
- Annotation findings were reviewed internally, not by an independent clinical team.
- The stratified ExECT semantic-support sample is an unreviewed substrate, not
  independent validation.
- Matched latency, token, cost, hardware, and retry telemetry is unavailable;
  hosted and local conditions cannot support an efficiency ranking.
- The selected evidence does not support a cross-task over-reading claim; the
  current ExECT gold has zero unknown-only letters under the predeclared metric.

## 7. Conclusion

The selected results support an inspectable comparison of rules-only, LLM-only,
and LLM-with-rules methods on two tasks plus fixed six-model panels under each
task's named scorer. The same eight reliability questions organize both tasks
without implying one metric or a composite score. The results expose the effect
and regression risk of deterministic components without assigning their gains
to the model. They do not support strict ExECT benchmark score reproduction,
general model superiority, cross-task reliability transfer, or independent
clinical validation.

## References

1. Fonferko-Shadrach B, et al. *BMJ Open*. 2019;9:e023232.
2. Fonferko-Shadrach B, et al. *Journal of Biomedical Semantics*. 2024;15:17.
3. Xie K, et al. *JAMIA*. 2022;29:873–881.
4. Abeysinghe R, et al. *npj Digital Medicine*. 2025.
5. Holgate B, et al. *BioNLP*. 2025:44–55.
6. Gan Y, et al. arXiv:2603.11407. 2026.
