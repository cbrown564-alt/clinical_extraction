<!-- GENERATED FILE. Do not edit by hand.
     Source: src/clinical_extraction/architecture/ (stage manifests +
     executed teaching cases). Regenerate with
     python scripts/build_architecture_docs.py -->

# ExECTv2 - Rules only

Method id: `exectv2_rules_only`  
Role: **selected**  
Stages: 4  
Stages that may change clinical meaning: 2

## One sentence

> Nine independent deterministic extractors produce the all-nine prediction, while an explicit four-family projection defines the primary model comparison.

## Sixty seconds

No model is involved. Nine entity-specific extractors run over the same note text: Diagnosis, Investigations, Onset, When Diagnosed, Birth History, Epilepsy Cause, Patient History, Prescription, and Seizure Frequency. Seizure Frequency is not a flat extractor - it runs its own staged deterministic sub-pipeline. The nine mention lists are concatenated and passed through mention-identity de-duplication, which is the only place where one extractor's output can suppress another's. The canonical orchestrator preserves that all-nine prediction and also materializes an explicit pure four-family comparison projection for Diagnosis, Seizure Frequency, Prescription, and Investigations. The all-nine result remains available for the secondary published-metric view; the primary model comparison uses only the named four-family projection.

## The five recall questions

| Question | Answer |
| --- | --- |
| What enters? | ExectLetter - see `exect.rules.extract_seizure_frequency` |
| Who first proposes the clinical answer? | the nine deterministic extractors (stage exect.rules.extract_entities); the four-family projection is scorer-facing |
| Which later stages may change clinical meaning? | `exect.rules.extract_entities` |
| What final representation is scored? | An all-nine PredictedLetter plus an explicit four-family comparison projection, each scored under its named view. |
| What evidence shows whether each component helped or harmed? | `docs/canon/07_exect_plan11.md`, `docs/canon/04_scoring.md` |

## Stages

Read the `Effect` column first. `CLINICAL MEANING` marks every stage that can change the answer.

| # | Stage | Owner | Effect | What it does |
| --- | --- | --- | --- | --- |
| 1 | `exect.rules.extract_seizure_frequency`<br>Extract seizure frequency | rules | CLINICAL MEANING | Run the staged deterministic seizure-frequency sub-pipeline, which has its own candidate, association, and temporal rule layers. |
| 2 | `exect.rules.extract_entities`<br>Extract the other eight entities | rules | CLINICAL MEANING | Run the Diagnosis, Investigations, Onset, When Diagnosed, Birth History, Epilepsy Cause, Patient History, and Prescription extractors over the note text and concatenate their mentions with the seizure-frequency mentions. |
| 3 | `exect.rules.dedupe`<br>De-duplicate mentions | rules | representation | Collapse mentions that share a mention identity, so the same finding produced by two extractors is counted once. |
| 4 | `exect.rules.score`<br>Score against gold | scorer | benchmark projection | Keep the all-nine prediction intact, project a separate four-family comparison view, and match each named view to gold under the configured policy. |

## Stage walkthrough

### 1. Extract seizure frequency

`exect.rules.extract_seizure_frequency` - rules-owned, CLINICAL MEANING, rule category `seizure_frequency`

Run the staged deterministic seizure-frequency sub-pipeline, which has its own candidate, association, and temporal rule layers.

|  | Type | Example |
| --- | --- | --- |
| In | ExectLetter | "Seizures are now occurring about twice a month." |
| Out | PredictedLetter (seizure-frequency mentions plus diagnostics) | one SeizureFrequency mention with state and rate attributes |

> Seizure Frequency is the only family in this baseline with a multi-stage sub-pipeline of its own; the other eight are single extractors.

- Code: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/pipeline.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/pipeline.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.pipeline:extract_seizure_frequency`)
- Test: [`tests/test_exectv2_deterministic_sf_pipeline.py`](../../../tests/test_exectv2_deterministic_sf_pipeline.py)
- Proven in a trace by: `diagnostics.sf_diagnostics`
- Paper wording: A staged deterministic sub-pipeline extracts seizure-frequency findings.

### 2. Extract the other eight entities

`exect.rules.extract_entities` - rules-owned, CLINICAL MEANING, rule category `clinical_epilepsy`

Run the Diagnosis, Investigations, Onset, When Diagnosed, Birth History, Epilepsy Cause, Patient History, and Prescription extractors over the note text and concatenate their mentions with the seizure-frequency mentions.

|  | Type | Example |
| --- | --- | --- |
| In | note text (str) | "Diagnosis: focal epilepsy. MRI brain was normal. Continue levetiracetam 500mg twice daily." |
| Out | tuple[PredictedMention, ...] | Diagnosis 'focal epilepsy', Investigations 'MRI brain', Prescription 'levetiracetam' |

> The extractors are independent: none reads another's output, so a Diagnosis miss cannot be recovered from a Prescription hit.

- Code: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/all_entities/orchestrator.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/all_entities/orchestrator.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities.orchestrator:ACTIVE_DETERMINISTIC_ENTITIES`)
- Test: [`tests/test_exectv2_deterministic_all9.py`](../../../tests/test_exectv2_deterministic_all9.py)
- Proven in a trace by: `diagnostics.entity_counts`, `diagnostics.active_entities`
- Paper wording: Entity-specific deterministic extractors produce findings for nine clinical entities.

### 3. De-duplicate mentions

`exect.rules.dedupe` - rules-owned, representation, rule category `general`

Collapse mentions that share a mention identity, so the same finding produced by two extractors is counted once.

|  | Type | Example |
| --- | --- | --- |
| In | tuple[PredictedMention, ...] | two identical Diagnosis mentions of 'focal epilepsy' |
| Out | tuple[PredictedMention, ...] | one Diagnosis mention of 'focal epilepsy' |

> The only stage where one extractor's output can remove another's. It removes duplicates, never disagreements.

- Code: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/mention_identity.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/mention_identity.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.mention_identity:dedupe_mentions`)
- Test: [`tests/test_exectv2_deterministic_all9.py`](../../../tests/test_exectv2_deterministic_all9.py)
- Proven in a trace by: `diagnostics.entity_counts`
- Paper wording: Findings are de-duplicated by mention identity before scoring.

### 4. Score against gold

`exect.rules.score` - scorer-owned, benchmark projection

Keep the all-nine prediction intact, project a separate four-family comparison view, and match each named view to gold under the configured policy.

|  | Type | Example |
| --- | --- | --- |
| In | PredictedLetter plus gold annotations | predicted Diagnosis 'focal epilepsy' against gold 'focal epilepsy' |
| Out | OverallScore plus per-entity EntityScore | Diagnosis P/R/F1 and an overall F1 |

> The canonical result exposes all-nine output and the pure four-family comparison projection. Never place the two overall numbers side by side without naming the view.

- Code: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/scoring/match.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/scoring/match.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match:score_overall`)
- Test: [`tests/test_exectv2_scoring_match_fidelity.py`](../../../tests/test_exectv2_scoring_match_fidelity.py)
- Proven in a trace by: `scores.overall`, `scores.per_entity`
- Paper wording: Predictions are scored by mention matching against the ExECTv2 gold annotations.

## Code map

Entry point: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/orchestration/rules.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/orchestration/rules.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.rules:run_letter`)

| Stage | Implementation | Governing test |
| --- | --- | --- |
| `exect.rules.extract_seizure_frequency` | `clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.pipeline:extract_seizure_frequency` | `tests/test_exectv2_deterministic_sf_pipeline.py` |
| `exect.rules.extract_entities` | `clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities.orchestrator:ACTIVE_DETERMINISTIC_ENTITIES` | `tests/test_exectv2_deterministic_all9.py` |
| `exect.rules.dedupe` | `clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.mention_identity:dedupe_mentions` | `tests/test_exectv2_deterministic_all9.py` |
| `exect.rules.score` | `clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match:score_overall` | `tests/test_exectv2_scoring_match_fidelity.py` |

## Not this method

These paths exist and are easy to mistake for the selected method. They are named here so they cannot be read as it.

| Path | Role | Why it is not the selected method |
| --- | --- | --- |
| `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/scoring/published.py` | historical performance control | Reproduces the paper-derived metric view, which is not the internal clinical fact recovery scorer (`clinical_headline`). |
| `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/all_entities/diagnosis.py` | rejected candidate or ablation | include_diagnosis_resolution_candidate and include_diagnosis_benchmark_residuals are off in the selected baseline. |

## Executable trace

See the [ExECTv2 teaching case](../teaching_cases/exectv2.md), which runs this method over one letter and records what every stage above actually did.
