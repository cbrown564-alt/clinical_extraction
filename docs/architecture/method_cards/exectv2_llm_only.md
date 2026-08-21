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

> ExECT LLM only: one model call on the note proposes four-family findings, and the selected view scores those findings without family repair.

## Sixty seconds

ExECT LLM only (`exect_llm_only`) uses its own request, separate from ExECT LLM with rules. It builds the LLM-only four-family prompt (no suggested-evidence scan), makes or replays one model call, parses Compact events, optionally performs a format-only retry for eligible local models, and applies evidence and render-safety gates. Family and fact names are spelled into the scorer mention fields as part of that parse. Its scored prediction is the raw candidate view (raw F1). It does not run seizure-frequency projection, Diagnosis reconciliation, Prescription normalization, or any other family transform. The unrepaired output of ExECT LLM with rules is not this method.

## The five recall questions

| Question | Answer |
| --- | --- |
| What enters? | ExectLetter - see `exect.llm.build_prompt` |
| Who first proposes the clinical answer? | the named model (stage exect.llm.model_call); deterministic stages only parse, represent, and gate its findings |
| Which later stages may change clinical meaning? | none - the first proposer is the only one |
| What final representation is scored? | The raw_candidate four-family PredictedLetter from the ExECT LLM only request, scored per entity and overall (raw F1). |
| What evidence shows whether each component helped or harmed? | `docs/paper/decisions/exect-compact-is-the-cited-hybrid.md`, `docs/paper/methods.md`, `docs/paper/claims.md` |

## Stages

Read the `Effect` column first. `CLINICAL MEANING` marks every stage that can change the answer.

| # | Stage | Owner | Effect | What it does |
| --- | --- | --- | --- | --- |
| 1 | `exect.llm.build_prompt`<br>Build the four-family prompt | rules | transport/schema only | Render the note text and the four-family event-ledger schema into the prompt input for one structured call. |
| 2 | `exect.llm.model_call`<br>Model proposes four-family findings | model | CLINICAL MEANING | One structured call returns candidate findings for Diagnosis, Seizure Frequency, Prescription, and Investigations, each with evidence. |
| 3 | `exect.llm.parse_and_retry`<br>Parse output with format-only retry | rules | transport/schema only | Recover the structured event record and, when eligible, accept one format-only retry only after schema validation. |
| 4 | `exect.llm.project_and_gate`<br>Apply representation and evidence gates | rules | gate | Normalize closed-vocabulary attributes, require exact source evidence, and withhold mentions rejected by the shared render-safety gates. |
| 5 | `exect.llm.raw_candidate`<br>Materialize the raw candidate view | rules | benchmark projection | Expose the producer's gated mentions as the selected LLM-only scoring view without applying the LLM-with-rules family transforms. |
| 6 | `exect.llm.score`<br>Score against gold | scorer | benchmark projection | Match predicted mentions to gold annotations under the configured ExECT match policy and report per-entity and overall metrics. |

## Stage walkthrough

### 1. Build the four-family prompt

`exect.llm.build_prompt` - rules-owned, transport/schema only, rule category `general`

Render the note text and the four-family event-ledger schema into the prompt input for one structured call.

|  | Type | Example |
| --- | --- | --- |
| In | ExectLetter | letter text plus letter id |
| Out | prompt input JSON (str) | {"note_text": "...", "families": ["Diagnosis", "SeizureFrequency", "Prescription", "Investigations"]} |

- Code: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/orchestration/structured_one_call.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/orchestration/structured_one_call.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.structured_one_call:produce_structured_letter`)
- Test: [`tests/test_exectv2_llm_vertical_slice.py`](../../../tests/test_exectv2_llm_vertical_slice.py)
- Proven in a trace by: `prompt_input_json`, `prompt_version`
- Paper wording: The selected LLM-only method starts from one structured four-family prompt.

### 2. Model proposes four-family findings

`exect.llm.model_call` - model-owned, CLINICAL MEANING

One structured call returns candidate findings for Diagnosis, Seizure Frequency, Prescription, and Investigations, each with evidence.

|  | Type | Example |
| --- | --- | --- |
| In | prompt input JSON (str) | letter text plus the four-family schema |
| Out | raw structured JSON (str) | {"clinical_events": [{"family": "diagnosis", "evidence": "Diagnosis: focal epilepsy"}]} |

- Code: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/orchestration/structured_one_call.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/orchestration/structured_one_call.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.structured_one_call:produce_structured_letter`)
- Test: [`tests/test_exectv2_llm_vertical_slice.py`](../../../tests/test_exectv2_llm_vertical_slice.py)
- Proven in a trace by: `raw_output`, `model`, `prompt_version`
- Paper wording: A single language-model call proposes candidate findings for all four families.

### 3. Parse output with format-only retry

`exect.llm.parse_and_retry` - rules-owned, transport/schema only, rule category `general`

Recover the structured event record and, when eligible, accept one format-only retry only after schema validation.

|  | Type | Example |
| --- | --- | --- |
| In | raw structured JSON (str) | an events list with a transport or JSON dialect error |
| Out | StructuredExtractionRecord plus parse notes | a validated event record with parse and retry notes |

- Code: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/orchestration/structured_one_call.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/orchestration/structured_one_call.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.structured_one_call:produce_structured_letter`)
- Test: [`tests/test_exectv2_local_format_retry.py`](../../../tests/test_exectv2_local_format_retry.py)
- Proven in a trace by: `initial_parse_errors`, `parse_errors`, `format_retry_notes`
- Paper wording: Malformed model output is handled at the transport and schema boundary.

### 4. Apply representation and evidence gates

`exect.llm.project_and_gate` - rules-owned, gate, rule category `clinical_epilepsy`

Normalize closed-vocabulary attributes, require exact source evidence, and withhold mentions rejected by the shared render-safety gates.

|  | Type | Example |
| --- | --- | --- |
| In | Compact events plus note text | a mention whose evidence does not appear in the note |
| Out | PredictedLetter plus gate warnings | the ungrounded mention is withheld and a gate warning is recorded |

- Code: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/orchestration/structured_one_call.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/orchestration/structured_one_call.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.structured_one_call:produce_structured_letter`)
- Test: [`tests/test_exectv2_llm_only_projection.py`](../../../tests/test_exectv2_llm_only_projection.py)
- Proven in a trace by: `gate_warnings`, `n_mentions_scored`, `n_evidence_invalid`
- Paper wording: The LLM-only candidate must pass evidence and render-safety gates before scoring.

### 5. Materialize the raw candidate view

`exect.llm.raw_candidate` - rules-owned, benchmark projection, rule category `benchmark_format`

Expose the producer's gated mentions as the selected LLM-only scoring view without applying the LLM-with-rules family transforms.

|  | Type | Example |
| --- | --- | --- |
| In | gated PredictedLetter | four-family mentions from the LLM-only producer |
| Out | raw_candidate PredictedLetter | the same four-family mentions with raw_candidate provenance |

- Code: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/orchestration/structured_one_call.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/orchestration/structured_one_call.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.structured_one_call:run_llm_only_letter`)
- Test: [`tests/test_exectv2_llm_vertical_slice.py`](../../../tests/test_exectv2_llm_vertical_slice.py)
- Proven in a trace by: `scored_view`, `predicted_mentions`
- Paper wording: The selected LLM-only view is the raw candidate from the ExECT LLM only request.

### 6. Score against gold

`exect.llm.score` - scorer-owned, benchmark projection

Match predicted mentions to gold annotations under the configured ExECT match policy and report per-entity and overall metrics.

|  | Type | Example |
| --- | --- | --- |
| In | raw_candidate PredictedLetter plus gold annotations | predicted Diagnosis 'focal epilepsy' against gold 'focal epilepsy' |
| Out | OverallScore plus per-entity EntityScore | a four-family overall F1 |

- Code: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/scoring/match.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/scoring/match.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match:score_overall`)
- Test: [`tests/test_exectv2_scoring_match_fidelity.py`](../../../tests/test_exectv2_scoring_match_fidelity.py)
- Proven in a trace by: `scores.overall`, `scores.per_entity`
- Paper wording: The raw candidate view is scored by mention matching against ExECTv2 gold.

## Code map

Entry point: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/orchestration/structured_one_call.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/orchestration/structured_one_call.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.structured_one_call:run_llm_only_letter`)

| Stage | Implementation | Governing test |
| --- | --- | --- |
| `exect.llm.build_prompt` | `clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.structured_one_call:produce_structured_letter` | `tests/test_exectv2_llm_vertical_slice.py` |
| `exect.llm.model_call` | `clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.structured_one_call:produce_structured_letter` | `tests/test_exectv2_llm_vertical_slice.py` |
| `exect.llm.parse_and_retry` | `clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.structured_one_call:produce_structured_letter` | `tests/test_exectv2_local_format_retry.py` |
| `exect.llm.project_and_gate` | `clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.structured_one_call:produce_structured_letter` | `tests/test_exectv2_llm_only_projection.py` |
| `exect.llm.raw_candidate` | `clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.structured_one_call:run_llm_only_letter` | `tests/test_exectv2_llm_vertical_slice.py` |
| `exect.llm.score` | `clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match:score_overall` | `tests/test_exectv2_scoring_match_fidelity.py` |

## Executable trace

See the [ExECTv2 teaching letters](../teaching_cases/exectv2.md), which run this method over the paper flagship letters and record what every stage above actually did.
