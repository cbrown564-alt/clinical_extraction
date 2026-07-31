<!-- GENERATED FILE. Do not edit by hand.
     Source: src/clinical_extraction/architecture/ (stage manifests +
     executed teaching cases). Regenerate with
     python scripts/build_architecture_docs.py -->

# ExECTv2 - LLM only

Method id: `exectv2_llm_only`  
Role: **selected**  
Stages: 6  
Stages that may change clinical meaning: 1

## One sentence

> A GEPA-optimized program emits de-duplicated clinical facts for four families, and an adapter maps them into ExECT mentions without adding or merging any fact.

## Sixty seconds

The retained GEPA program produces a list of clinical facts, each with a family, evidence, and attributes, already de-duplicated by the program itself. The adapter then does four things: it repairs JSON dialect and coerces the facts list; it drops facts that are malformed or carry no evidence; it maps each surviving fact into an ExECT mention, normalizing representation fields such as negation, dose units, medication frequency, modality, investigation state, and seizure-frequency state; and it passes the mentions through the shared evidence and schema gates. The adapter explicitly does not add or merge clinical facts, and records that claim per fact in its provenance. The honest caveat is that representation normalization is not nothing: a fact whose dose unit or seizure state normalizes differently can match or miss gold on that basis alone.

## The five recall questions

| Question | Answer |
| --- | --- |
| What enters? | ExectLetter - see `exect.llm.gepa_program` |
| Who first proposes the clinical answer? | the GEPA program (stage exect.llm.gepa_program) |
| Which later stages may change clinical meaning? | none - the first proposer is the only one |
| What final representation is scored? | A PredictedLetter of four-family mentions with attributes and evidence, scored per entity and overall. |
| What evidence shows whether each component helped or harmed? | `docs/canon/08_gepa.md`, `docs/canon/07_exect_plan11.md` |

## Stages

Read the `Effect` column first. `CLINICAL MEANING` marks every stage that can change the answer.

| # | Stage | Owner | Effect | What it does |
| --- | --- | --- | --- | --- |
| 1 | `exect.llm.gepa_program`<br>GEPA program emits clinical facts | model | CLINICAL MEANING | The optimized program reads the letter and returns de-duplicated clinical facts across Diagnosis, Seizure Frequency, Prescription, and Investigations. |
| 2 | `exect.llm.parse_and_coerce`<br>Parse JSON and coerce the facts list | rules | transport/schema only | Recover the JSON object, repair Python-literal dialect, accept either the clinical_facts or facts key, and coerce each entry to a fact-shaped mapping. |
| 3 | `exect.llm.drop_unusable_facts`<br>Drop malformed or unevidenced facts | rules | gate | Discard facts that fail fact-level validation, name an unsupported family, or carry no evidence span. |
| 4 | `exect.llm.map_to_mentions`<br>Map facts to ExECT mentions | rules | representation | Turn each fact into an ExECT mention and attribute set, normalizing negation, dose units, medication frequency, modality, investigation performed and result state, and seizure-frequency state. |
| 5 | `exect.llm.evidence_schema_gates`<br>Apply evidence and schema gates | rules | gate | Run the shared projection gates: require grounded evidence, enforce the render-safety rules, and emit gate warnings for anything rejected. |
| 6 | `exect.llm.score`<br>Score against gold | scorer | benchmark projection | Match predicted mentions to gold annotations under the configured match policy and report per-entity and overall precision, recall, and F1. |

## Stage walkthrough

### 1. GEPA program emits clinical facts

`exect.llm.gepa_program` - model-owned, CLINICAL MEANING

The optimized program reads the letter and returns de-duplicated clinical facts across Diagnosis, Seizure Frequency, Prescription, and Investigations.

|  | Type | Example |
| --- | --- | --- |
| In | ExectLetter | "Diagnosis: focal epilepsy. MRI brain normal. Levetiracetam 500mg twice daily." |
| Out | raw structured JSON (str) | {"clinical_facts": [{"family": "diagnosis", "text": "focal epilepsy", "evidence": "Diagnosis: focal epilepsy"}]} |

> GEPA optimization is closed. One saved run is retained as a negative comparison; see docs/canon/08_gepa.md.

- Code: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/gepa/dedup_adapter.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/gepa/dedup_adapter.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.dedup_adapter:PROMPT_VERSION`)
- Test: [`tests/test_exectv2_gepa_dedup_adapter.py`](../../../tests/test_exectv2_gepa_dedup_adapter.py)
- Proven in a trace by: `raw_output`, `prompt_version`
- Paper wording: A GEPA-optimized program produces de-duplicated clinical facts for four families.

### 2. Parse JSON and coerce the facts list

`exect.llm.parse_and_coerce` - rules-owned, transport/schema only, rule category `general`

Recover the JSON object, repair Python-literal dialect, accept either the clinical_facts or facts key, and coerce each entry to a fact-shaped mapping.

|  | Type | Example |
| --- | --- | --- |
| In | raw structured JSON (str) | output wrapped in prose, or using the 'facts' key |
| Out | DedupClinicalFactsRecord plus notes | a validated record with two clinical facts |

- Code: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/gepa/dedup_adapter.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/gepa/dedup_adapter.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.dedup_adapter:parse_dedup_clinical_facts_json`)
- Test: [`tests/test_exectv2_gepa_dedup_adapter.py`](../../../tests/test_exectv2_gepa_dedup_adapter.py)
- Proven in a trace by: `parse_errors`
- Paper wording: Malformed program output is repaired at the transport and schema level only.

### 3. Drop malformed or unevidenced facts

`exect.llm.drop_unusable_facts` - rules-owned, gate, rule category `general`

Discard facts that fail fact-level validation, name an unsupported family, or carry no evidence span.

|  | Type | Example |
| --- | --- | --- |
| In | list of candidate facts | a fact with family 'diagnosis' and an empty evidence field |
| Out | filtered list of facts plus notes | the unevidenced fact is dropped and noted |

> A gate, not a rewrite: it removes facts the model produced, and it never invents one.

- Code: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/gepa/dedup_adapter.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/gepa/dedup_adapter.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.dedup_adapter:_coerce_facts`)
- Test: [`tests/test_exectv2_gepa_dedup_adapter.py`](../../../tests/test_exectv2_gepa_dedup_adapter.py)
- Proven in a trace by: `adapter_notes`
- Paper wording: Facts that are malformed or carry no evidence are dropped rather than scored.

### 4. Map facts to ExECT mentions

`exect.llm.map_to_mentions` - rules-owned, representation, rule category `clinical_epilepsy`

Turn each fact into an ExECT mention and attribute set, normalizing negation, dose units, medication frequency, modality, investigation performed and result state, and seizure-frequency state.

|  | Type | Example |
| --- | --- | --- |
| In | list[DedupClinicalFactRecord] | a prescription fact with dose_unit 'milligrams' and frequency 'twice a day' |
| Out | tuple[list[MentionForEvidence], provenance, notes] | a Prescription mention with dose_unit 'mg' and frequency 'BD' |

> Every provenance entry records action 'representation_mapping_only', added_fact false, and deduplicated_by_adapter false, so the no-addition claim is checkable per fact rather than asserted in prose. The normalization itself can still change whether a fact matches gold.

- Code: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/gepa/dedup_adapter.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/gepa/dedup_adapter.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.dedup_adapter:clinical_facts_to_mentions`)
- Test: [`tests/test_exectv2_gepa_dedup_adapter.py`](../../../tests/test_exectv2_gepa_dedup_adapter.py)
- Proven in a trace by: `provenance[].action`, `provenance[].added_fact`, `provenance[].deduplicated_by_adapter`
- Paper wording: An adapter maps program facts into the ExECT representation without adding or merging clinical facts.

### 5. Apply evidence and schema gates

`exect.llm.evidence_schema_gates` - rules-owned, gate, rule category `general`

Run the shared projection gates: require grounded evidence, enforce the render-safety rules, and emit gate warnings for anything rejected.

|  | Type | Example |
| --- | --- | --- |
| In | list[MentionForEvidence] plus note text | a mention whose evidence does not appear in the note |
| Out | PredictedLetter plus gate warnings | the ungrounded mention is withheld and a gate warning is recorded |

- Code: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/llm/pipelines/key_entities_structured/projection.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/llm/pipelines/key_entities_structured/projection.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured.projection:to_predicted_letter`)
- Test: [`tests/test_exectv2_llm_only_projection.py`](../../../tests/test_exectv2_llm_only_projection.py)
- Proven in a trace by: `gate_warnings`, `n_evidence_invalid`
- Paper wording: Findings must pass evidence-grounding and schema gates before scoring.

### 6. Score against gold

`exect.llm.score` - scorer-owned, benchmark projection

Match predicted mentions to gold annotations under the configured match policy and report per-entity and overall precision, recall, and F1.

|  | Type | Example |
| --- | --- | --- |
| In | PredictedLetter plus gold annotations | predicted Diagnosis 'focal epilepsy' against gold 'focal epilepsy' |
| Out | OverallScore plus per-entity EntityScore | a four-family overall F1 |

- Code: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/scoring/match.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/scoring/match.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match:score_overall`)
- Test: [`tests/test_exectv2_scoring_match_fidelity.py`](../../../tests/test_exectv2_scoring_match_fidelity.py)
- Proven in a trace by: `scores.overall`, `scores.per_entity`
- Paper wording: Predictions are scored by mention matching against the ExECTv2 gold annotations.

## Code map

Entry point: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/gepa/dedup_adapter.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/gepa/dedup_adapter.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.dedup_adapter:to_predicted_letter_from_dedup_facts`)

| Stage | Implementation | Governing test |
| --- | --- | --- |
| `exect.llm.gepa_program` | `clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.dedup_adapter:PROMPT_VERSION` | `tests/test_exectv2_gepa_dedup_adapter.py` |
| `exect.llm.parse_and_coerce` | `clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.dedup_adapter:parse_dedup_clinical_facts_json` | `tests/test_exectv2_gepa_dedup_adapter.py` |
| `exect.llm.drop_unusable_facts` | `clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.dedup_adapter:_coerce_facts` | `tests/test_exectv2_gepa_dedup_adapter.py` |
| `exect.llm.map_to_mentions` | `clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.dedup_adapter:clinical_facts_to_mentions` | `tests/test_exectv2_gepa_dedup_adapter.py` |
| `exect.llm.evidence_schema_gates` | `clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured.projection:to_predicted_letter` | `tests/test_exectv2_llm_only_projection.py` |
| `exect.llm.score` | `clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match:score_overall` | `tests/test_exectv2_scoring_match_fidelity.py` |

## Not this method

These paths exist and are easy to mistake for the selected method. They are named here so they cannot be read as it.

| Path | Role | Why it is not the selected method |
| --- | --- | --- |
| `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/gepa/` | rejected candidate or ablation | The optimization loop that produced the retained program. Closed; see docs/canon/08_gepa.md. |

## Executable trace

See the [ExECTv2 teaching case](../teaching_cases/exectv2.md), which runs this method over one letter and records what every stage above actually did.
