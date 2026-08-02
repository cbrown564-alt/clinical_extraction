<!-- GENERATED FILE. Do not edit by hand.
     Source: src/clinical_extraction/architecture/ (stage manifests +
     executed teaching cases). Regenerate with
     python scripts/build_architecture_docs.py -->

# Teaching case: ExECTv2

Case id: `exectv2_four_family_ordinary_letter`  
Letter: `TEACH-EXECT-01`

## How to read this

The letter is synthetic and the raw model outputs are fixtures standing in for one model call each. No model call is made when this case is built. Every stage after the model boundary is the real selected implementation.

## The letter

```text
Epilepsy clinic letter, 14 March 2026.

Diagnosis: focal epilepsy.

Mr B has been seizure free since March 2025. MRI brain was normal. He continues on levetiracetam 500mg twice daily.
```

**Expected answer:** (no gold annotations; this is a synthetic teaching letter)

This case teaches the shape of the pipeline and the comparison boundary, not accuracy. The rules-only baseline answers over nine entities; the two model-led methods answer over four families. Their overall numbers are not interchangeable.

## Outcome by method

| Method | Final answer | Correct? |
| --- | --- | --- |
| Rules only | Diagnosis x2, Investigations x1, Prescription x1, SeizureFrequency x1 | not scored |
| LLM only | Diagnosis x1, Investigations x1, Prescription x1, SeizureFrequency x1 | not scored |
| LLM with rules | Diagnosis x1, Investigations x1, Prescription x1, SeizureFrequency x1 | not scored |

## Rules only

> Nine independent deterministic extractors produce the all-nine prediction, while an explicit four-family projection defines the primary model comparison.

**Prediction owner:** the nine deterministic extractors (stage exect.rules.extract_entities); the four-family projection is scorer-facing

**Final answer:** Diagnosis x2, Investigations x1, Prescription x1, SeizureFrequency x1

This teaching letter carries no gold annotations, so no correctness verdict is claimed. The comparable unit is nine entities.

3 of 4 stages changed something on this letter.

### 1. Extract seizure frequency <sub>`exect.rules.extract_seizure_frequency`</sub>

rules-owned, CLINICAL MEANING - **changed**

```text
in : Epilepsy clinic letter, 14 March 2026.  Diagnosis: focal epilepsy.  Mr B has been seizure free since March 2025. MRI brain was normal. He continues on levetiracetam 500mg twice daily.
out: 1
```

> Canonical rules-only stage.

### 2. Extract the other eight entities <sub>`exect.rules.extract_entities`</sub>

rules-owned, CLINICAL MEANING - **changed**

```text
in : Epilepsy clinic letter, 14 March 2026.  Diagnosis: focal epilepsy.  Mr B has been seizure free since March 2025. MRI brain was normal. He continues on levetiracetam 500mg twice daily.
out: {'Prescription': 1, 'Investigations': 1, 'Diagnosis': 2, 'Onset': 0, 'WhenDiagnosed': 0, 'BirthHistory': 0, 'EpilepsyCause': 0, 'PatientHistory': 0, 'SeizureFrequency': 1}
```

> Nine independent extractors. This baseline covers nine entities while the model-led comparison covers four.

### 3. De-duplicate mentions <sub>`exect.rules.dedupe`</sub>

rules-owned, representation - no change

```text
in : 5
out: 5
```

> Canonical rules-only stage.

### 4. Score against gold <sub>`exect.rules.score`</sub>

scorer-owned, benchmark projection - **changed**

```text
in : 5 finding(s) over nine entities
out: {'Diagnosis': 2, 'Investigations': 1, 'Prescription': 1, 'SeizureFrequency': 1}
```

> Scored against gold in a real run. Here the point is the comparison boundary: this method is scored over nine entities.

## LLM only

> One structured model call proposes four-family findings, and the selected LLM-only view scores those findings without the hybrid family lenses.

**Prediction owner:** the named model (stage exect.llm.model_call); deterministic stages only parse, represent, and gate its findings

**Final answer:** Diagnosis x1, Investigations x1, Prescription x1, SeizureFrequency x1

This teaching letter carries no gold annotations, so no correctness verdict is claimed. The comparable unit is four families.

4 of 7 stages changed something on this letter.

### 1. Build the four-family prompt <sub>`exect.llm.build_prompt`</sub>

rules-owned, transport/schema only - **changed**

```text
in : TEACH-EXECT-01
out: {"architecture": {"component_ownership": "The deterministic ledger proposes possible evidence spans only. The model owns keep/reject/split/merge decisions and final rendered mentions. Deterministic code later validates evidence, strips illegal attributes, attaches finite ontology codes, and evaluates outputs.", "inspiration": "Gan structured-events discipline: source-near candidate evidence, typed state lanes, exact evidence, then final mention renderings.", "name": "single hybrid key-family event ledger"}, "attribute_vocabulary": {"Diagnosis": {"CUI": "UMLS CUI only if explicitly available; o ... (truncated)
```

> Canonical LLM-only stage.

### 2. Model proposes four-family findings <sub>`exect.llm.model_call`</sub>

model-owned, CLINICAL MEANING - **changed**

```text
in : {"architecture": {"component_ownership": "The deterministic ledger proposes possible evidence spans only. The model owns keep/reject/split/merge decisions and final rendered mentions. Deterministic code later validates evidence, strips illegal attributes, attaches finite ontology codes, and evaluates outputs.", "inspiration": "Gan structured-events discipline: source-near candidate evidence, typed state lanes, exact evidence, then final mention renderings.", "name": "single hybrid key-family event ledger"}, "attribute_vocabulary": {"Diagnosis": {"CUI": "UMLS CUI only if explicitly available; o ... (truncated)
out: {"clinical_events": [{"family": "diagnosis", "anchor_text": "focal epilepsy", "evidence": "Diagnosis: focal epilepsy", "event_state": {}, "mentions": [{"entity": "Diagnosis", "text": "focal epilepsy", "attributes": {"DiagCategory": "Epilepsy", "Negation": "Affirmed"}}], "confidence": "high", "rationale": "stated under the diagnosis heading"}, {"family": "seizure_frequency", "anchor_text": "seizure free since March 2025", "evidence": "Mr B has been seizure free since March 2025", "event_state": {}, "mentions": [{"entity": "SeizureFrequency", "text": "seizures", "attributes": {"NumberOfSeizures" ... (truncated)
```

> Fixture boundary at the one-call producer; downstream stages are the selected implementation.

### 3. Parse output with format-only retry <sub>`exect.llm.parse_and_retry`</sub>

rules-owned, transport/schema only - no change

```text
in : {"clinical_events": [{"family": "diagnosis", "anchor_text": "focal epilepsy", "evidence": "Diagnosis: focal epilepsy", "event_state": {}, "mentions": [{"entity": "Diagnosis", "text": "focal epilepsy", "attributes": {"DiagCategory": "Epilepsy", "Negation": "Affirmed"}}], "confidence": "high", "rationale": "stated under the diagnosis heading"}, {"family": "seizure_frequency", "anchor_text": "seizure free since March 2025", "evidence": "Mr B has been seizure free since March 2025", "event_state": {}, "mentions": [{"entity": "SeizureFrequency", "text": "seizures", "attributes": {"NumberOfSeizures" ... (truncated)
out: [{'family': 'diagnosis', 'anchor_text': 'focal epilepsy', 'evidence': 'Diagnosis: focal epilepsy', 'event_state': {}, 'mentions': [{'entity': 'Diagnosis', 'text': 'focal epilepsy', 'attributes': {'DiagCategory': 'Epilepsy', 'Negation': 'Affirmed'}}], 'confidence': 'high', 'rationale': 'stated under the diagnosis heading'}, {'family': 'seizure_frequency', 'anchor_text': 'seizure free since March 2025', 'evidence': 'Mr B has been seizure free since March 2025', 'event_state': {}, 'mentions': [{'entity': 'SeizureFrequency', 'text': 'seizures', 'attributes': {'NumberOfSeizures': '0'}}], 'confidenc ... (truncated)
```

> Canonical LLM-only stage.

### 4. Flatten events into mentions <sub>`exect.llm.flatten_events`</sub>

rules-owned, representation - **changed**

```text
in : [{'family': 'diagnosis', 'anchor_text': 'focal epilepsy', 'evidence': 'Diagnosis: focal epilepsy', 'event_state': {}, 'mentions': [{'entity': 'Diagnosis', 'text': 'focal epilepsy', 'attributes': {'DiagCategory': 'Epilepsy', 'Negation': 'Affirmed'}}], 'confidence': 'high', 'rationale': 'stated under the diagnosis heading'}, {'family': 'seizure_frequency', 'anchor_text': 'seizure free since March 2025', 'evidence': 'Mr B has been seizure free since March 2025', 'event_state': {}, 'mentions': [{'entity': 'SeizureFrequency', 'text': 'seizures', 'attributes': {'NumberOfSeizures': '0'}}], 'confidenc ... (truncated)
out: [{'entity': 'Diagnosis', 'text': 'focal epilepsy', 'attributes': {'DiagCategory': 'Epilepsy', 'Negation': 'Affirmed'}, 'evidence': 'Diagnosis: focal epilepsy', 'confidence': 'high', 'rationale': 'stated under the diagnosis heading', 'component_owner': ''}, {'entity': 'SeizureFrequency', 'text': 'seizures', 'attributes': {'NumberOfSeizures': '0'}, 'evidence': 'Mr B has been seizure free since March 2025', 'confidence': 'high', 'rationale': 'explicit seizure-free statement', 'component_owner': ''}, {'entity': 'Investigations', 'text': 'MRI', 'attributes': {'MRI_Performed': 'Yes', 'MRI_Results':  ... (truncated)
```

> Canonical LLM-only stage.

### 5. Apply representation and evidence gates <sub>`exect.llm.project_and_gate`</sub>

rules-owned, gate - no change

```text
in : [{'entity': 'Diagnosis', 'text': 'focal epilepsy', 'attributes': {'DiagCategory': 'Epilepsy', 'Negation': 'Affirmed'}, 'evidence': 'Diagnosis: focal epilepsy', 'confidence': 'high', 'rationale': 'stated under the diagnosis heading', 'component_owner': ''}, {'entity': 'SeizureFrequency', 'text': 'seizures', 'attributes': {'NumberOfSeizures': '0'}, 'evidence': 'Mr B has been seizure free since March 2025', 'confidence': 'high', 'rationale': 'explicit seizure-free statement', 'component_owner': ''}, {'entity': 'Investigations', 'text': 'MRI', 'attributes': {'MRI_Performed': 'Yes', 'MRI_Results':  ... (truncated)
out: [{'entity': 'Diagnosis', 'text': 'focal epilepsy', 'attributes': {'DiagCategory': 'Epilepsy', 'Negation': 'Affirmed', 'CUI': 'C0014547', 'CUIPhrase': 'focal epilepsy'}, 'evidence': 'Diagnosis: focal epilepsy', 'confidence': 'high', 'rationale': 'stated under the diagnosis heading', 'component_owner': 'hybrid_key_family_event_ledger'}, {'entity': 'SeizureFrequency', 'text': 'seizures', 'attributes': {'NumberOfSeizures': '0', 'CUI': 'C0036572', 'CUIPhrase': 'seizures'}, 'evidence': 'Mr B has been seizure free since March 2025', 'confidence': 'high', 'rationale': 'explicit seizure-free statement' ... (truncated)
```

> Canonical LLM-only stage.

### 6. Materialize the raw candidate view <sub>`exect.llm.raw_candidate`</sub>

rules-owned, benchmark projection - no change

```text
in : 4
out: 4
```

> Canonical LLM-only stage.

### 7. Score against gold <sub>`exect.llm.score`</sub>

scorer-owned, benchmark projection - **changed**

```text
in : 4 finding(s) over four families
out: {'Diagnosis': 1, 'SeizureFrequency': 1, 'Investigations': 1, 'Prescription': 1}
```

> Scored against gold in a real run. Here the point is the comparison boundary: this method is scored over four families.

## LLM with rules

> The model proposes findings for four families in one call; deterministic family transforms reconcile those findings into the final scored representation.

**Prediction owner:** the named model proposes all four families (exect.hybrid.model_call); four family transforms may change findings afterwards

**Final answer:** Diagnosis x1, Investigations x1, Prescription x1, SeizureFrequency x1

This teaching letter carries no gold annotations, so no correctness verdict is claimed. The comparable unit is four families.

11 of 15 stages changed something on this letter.

### 1. Build the four-family prompt <sub>`exect.hybrid.build_prompt`</sub>

rules-owned, transport/schema only - **changed**

```text
in : TEACH-EXECT-01
out: {"architecture": {"component_ownership": "The deterministic ledger proposes possible evidence spans only. The model owns keep/reject/split/merge decisions and final rendered mentions. Deterministic code later validates evidence, strips illegal attributes, attaches finite ontology codes, and evaluates outputs.", "inspiration": "Gan structured-events discipline: source-near candidate evidence, typed state lanes, exact evidence, then final mention renderings.", "name": "single hybrid key-family event ledger"}, "attribute_vocabulary": {"Diagnosis": {"CUI": "UMLS CUI only if explicitly available; o ... (truncated)
```

> Canonical LLM-with-rules stage.

### 2. Model proposes findings for four families <sub>`exect.hybrid.model_call`</sub>

model-owned, CLINICAL MEANING - **changed**

```text
in : {"architecture": {"component_ownership": "The deterministic ledger proposes possible evidence spans only. The model owns keep/reject/split/merge decisions and final rendered mentions. Deterministic code later validates evidence, strips illegal attributes, attaches finite ontology codes, and evaluates outputs.", "inspiration": "Gan structured-events discipline: source-near candidate evidence, typed state lanes, exact evidence, then final mention renderings.", "name": "single hybrid key-family event ledger"}, "attribute_vocabulary": {"Diagnosis": {"CUI": "UMLS CUI only if explicitly available; o ... (truncated)
out: {"clinical_events": [{"family": "diagnosis", "anchor_text": "focal epilepsy", "evidence": "Diagnosis: focal epilepsy", "event_state": {}, "mentions": [{"entity": "Diagnosis", "text": "focal epilepsy", "attributes": {"DiagCategory": "Epilepsy", "Negation": "Affirmed"}}], "confidence": "high", "rationale": "stated under the diagnosis heading"}, {"family": "seizure_frequency", "anchor_text": "seizure free since March 2025", "evidence": "Mr B has been seizure free since March 2025", "event_state": {}, "mentions": [{"entity": "SeizureFrequency", "text": "seizures", "attributes": {"NumberOfSeizures" ... (truncated)
```

> Fixture boundary at the one-call producer; no live model call is made.

### 3. Parse output, with format-only retry when eligible <sub>`exect.hybrid.parse_and_retry`</sub>

rules-owned, transport/schema only - no change

```text
in : {"clinical_events": [{"family": "diagnosis", "anchor_text": "focal epilepsy", "evidence": "Diagnosis: focal epilepsy", "event_state": {}, "mentions": [{"entity": "Diagnosis", "text": "focal epilepsy", "attributes": {"DiagCategory": "Epilepsy", "Negation": "Affirmed"}}], "confidence": "high", "rationale": "stated under the diagnosis heading"}, {"family": "seizure_frequency", "anchor_text": "seizure free since March 2025", "evidence": "Mr B has been seizure free since March 2025", "event_state": {}, "mentions": [{"entity": "SeizureFrequency", "text": "seizures", "attributes": {"NumberOfSeizures" ... (truncated)
out: [{'family': 'diagnosis', 'anchor_text': 'focal epilepsy', 'evidence': 'Diagnosis: focal epilepsy', 'event_state': {}, 'mentions': [{'entity': 'Diagnosis', 'text': 'focal epilepsy', 'attributes': {'DiagCategory': 'Epilepsy', 'Negation': 'Affirmed'}}], 'confidence': 'high', 'rationale': 'stated under the diagnosis heading'}, {'family': 'seizure_frequency', 'anchor_text': 'seizure free since March 2025', 'evidence': 'Mr B has been seizure free since March 2025', 'event_state': {}, 'mentions': [{'entity': 'SeizureFrequency', 'text': 'seizures', 'attributes': {'NumberOfSeizures': '0'}}], 'confidenc ... (truncated)
```

> Canonical LLM-with-rules stage.

### 4. Flatten model events into mentions <sub>`exect.hybrid.flatten_events`</sub>

rules-owned, representation - **changed**

```text
in : [{'family': 'diagnosis', 'anchor_text': 'focal epilepsy', 'evidence': 'Diagnosis: focal epilepsy', 'event_state': {}, 'mentions': [{'entity': 'Diagnosis', 'text': 'focal epilepsy', 'attributes': {'DiagCategory': 'Epilepsy', 'Negation': 'Affirmed'}}], 'confidence': 'high', 'rationale': 'stated under the diagnosis heading'}, {'family': 'seizure_frequency', 'anchor_text': 'seizure free since March 2025', 'evidence': 'Mr B has been seizure free since March 2025', 'event_state': {}, 'mentions': [{'entity': 'SeizureFrequency', 'text': 'seizures', 'attributes': {'NumberOfSeizures': '0'}}], 'confidenc ... (truncated)
out: [{'entity': 'Diagnosis', 'text': 'focal epilepsy', 'attributes': {'DiagCategory': 'Epilepsy', 'Negation': 'Affirmed'}, 'evidence': 'Diagnosis: focal epilepsy', 'confidence': 'high', 'rationale': 'stated under the diagnosis heading', 'component_owner': ''}, {'entity': 'SeizureFrequency', 'text': 'seizures', 'attributes': {'NumberOfSeizures': '0'}, 'evidence': 'Mr B has been seizure free since March 2025', 'confidence': 'high', 'rationale': 'explicit seizure-free statement', 'component_owner': ''}, {'entity': 'Investigations', 'text': 'MRI', 'attributes': {'MRI_Performed': 'Yes', 'MRI_Results':  ... (truncated)
```

> Canonical LLM-with-rules stage.

### 5. Enrich attributes and apply render-safety gates <sub>`exect.hybrid.project_and_gate`</sub>

rules-owned, CLINICAL MEANING - no change

```text
in : [{'entity': 'Diagnosis', 'text': 'focal epilepsy', 'attributes': {'DiagCategory': 'Epilepsy', 'Negation': 'Affirmed'}, 'evidence': 'Diagnosis: focal epilepsy', 'confidence': 'high', 'rationale': 'stated under the diagnosis heading', 'component_owner': ''}, {'entity': 'SeizureFrequency', 'text': 'seizures', 'attributes': {'NumberOfSeizures': '0'}, 'evidence': 'Mr B has been seizure free since March 2025', 'confidence': 'high', 'rationale': 'explicit seizure-free statement', 'component_owner': ''}, {'entity': 'Investigations', 'text': 'MRI', 'attributes': {'MRI_Performed': 'Yes', 'MRI_Results':  ... (truncated)
out: [{'entity': 'Diagnosis', 'text': 'focal epilepsy', 'attributes': {'DiagCategory': 'Epilepsy', 'Negation': 'Affirmed', 'CUI': 'C0014547', 'CUIPhrase': 'focal epilepsy'}, 'evidence': 'Diagnosis: focal epilepsy', 'confidence': 'high', 'rationale': 'stated under the diagnosis heading', 'component_owner': 'hybrid_key_family_event_ledger'}, {'entity': 'SeizureFrequency', 'text': 'seizures', 'attributes': {'NumberOfSeizures': '0', 'CUI': 'C0036572', 'CUIPhrase': 'seizures'}, 'evidence': 'Mr B has been seizure free since March 2025', 'confidence': 'high', 'rationale': 'explicit seizure-free statement' ... (truncated)
```

> Canonical LLM-with-rules stage.

### 6. Project seizure-frequency facts into the state representation <sub>`exect.hybrid.sf_state_projection`</sub>

rules-owned, CLINICAL MEANING - **changed**

```text
in : [{'entity': 'Diagnosis', 'text': 'focal epilepsy', 'attributes': {'DiagCategory': 'Epilepsy', 'Negation': 'Affirmed', 'CUI': 'C0014547', 'CUIPhrase': 'focal epilepsy'}, 'evidence': 'Diagnosis: focal epilepsy', 'confidence': 'high', 'rationale': 'stated under the diagnosis heading', 'component_owner': 'hybrid_key_family_event_ledger'}, {'entity': 'SeizureFrequency', 'text': 'seizures', 'attributes': {'NumberOfSeizures': '0', 'CUI': 'C0036572', 'CUIPhrase': 'seizures'}, 'evidence': 'Mr B has been seizure free since March 2025', 'confidence': 'high', 'rationale': 'explicit seizure-free statement' ... (truncated)
out: [{'entity': 'SeizureFrequency', 'text': 'seizures', 'attributes': {'NumberOfSeizures': '0', 'CUI': 'C0036572', 'CUIPhrase': 'seizures'}, 'evidence': 'Mr B has been seizure free since March 2025', 'rationale': 'explicit seizure-free statement', 'confidence': 'high', 'component_owner': 'named_model_sf_plus_projection_suppression', 'source_artifact': 'sf.jsonl', 'source_lane': 'model_sf_projection_suppression', 'source_pipeline_family': 'exectv2_hybrid_sf_unknown_suppression', 'source_model': '', 'source_prompt_version': 'exectv2_hybrid_sf_unknown_suppression_v0.7', 'fact_origin': 'target_model_g ... (truncated)
```

> Canonical LLM-with-rules stage.

### 7. Suppress unsupported unknown states <sub>`exect.hybrid.sf_unknown_suppression`</sub>

rules-owned, CLINICAL MEANING - no change

```text
in : [{'entity': 'Diagnosis', 'text': 'focal epilepsy', 'attributes': {'DiagCategory': 'Epilepsy', 'Negation': 'Affirmed', 'CUI': 'C0014547', 'CUIPhrase': 'focal epilepsy'}, 'evidence': 'Diagnosis: focal epilepsy', 'confidence': 'high', 'rationale': 'stated under the diagnosis heading', 'component_owner': 'hybrid_key_family_event_ledger'}, {'entity': 'SeizureFrequency', 'text': 'seizures', 'attributes': {'NumberOfSeizures': '0', 'CUI': 'C0036572', 'CUIPhrase': 'seizures'}, 'evidence': 'Mr B has been seizure free since March 2025', 'confidence': 'high', 'rationale': 'explicit seizure-free statement' ... (truncated)
out: [{'entity': 'SeizureFrequency', 'text': 'seizures', 'attributes': {'NumberOfSeizures': '0', 'CUI': 'C0036572', 'CUIPhrase': 'seizures'}, 'evidence': 'Mr B has been seizure free since March 2025', 'rationale': 'explicit seizure-free statement', 'confidence': 'high', 'component_owner': 'named_model_sf_plus_projection_suppression', 'source_artifact': 'sf.jsonl', 'source_lane': 'model_sf_projection_suppression', 'source_pipeline_family': 'exectv2_hybrid_sf_unknown_suppression', 'source_model': '', 'source_prompt_version': 'exectv2_hybrid_sf_unknown_suppression_v0.7', 'fact_origin': 'target_model_g ... (truncated)
```

> Canonical LLM-with-rules stage.

### 8. Register raw and scored findings <sub>`exect.hybrid.register_findings`</sub>

rules-owned, transport/schema only - **changed**

```text
in : 4
out: 4
```

> Canonical LLM-with-rules stage.

### 9. Diagnosis family transform <sub>`exect.hybrid.lens.diagnosis`</sub>

rules-owned, CLINICAL MEANING - **changed**

```text
in : [{'entity': 'Diagnosis', 'text': 'focal epilepsy', 'attributes': {'DiagCategory': 'Epilepsy', 'Negation': 'Affirmed', 'CUI': 'C0014547', 'CUIPhrase': 'focal epilepsy'}, 'evidence': 'Diagnosis: focal epilepsy', 'rationale': 'stated under the diagnosis heading', 'confidence': 'high', 'component_owner': 'named_model_structured_facts', 'source_artifact': 'structured.jsonl', 'source_lane': 'model_structured_key_families', 'source_pipeline_family': 'exectv2_hybrid_key_family_event_ledger', 'source_model': '', 'source_prompt_version': 'exectv2_hybrid_key_family_event_ledger_v0.9.24', 'fact_origin': ' ... (truncated)
out: [{'entity': 'Diagnosis', 'text': 'focal epilepsy', 'attributes': {'DiagCategory': 'Epilepsy', 'Negation': 'Affirmed', 'CUI': 'C0014547', 'CUIPhrase': 'focal epilepsy'}, 'evidence': 'Diagnosis: focal epilepsy', 'rationale': 'stated under the diagnosis heading', 'confidence': 'high', 'component_owner': 'named_model_structured_facts', 'source_artifact': 'structured.jsonl', 'source_lane': 'model_structured_key_families', 'source_pipeline_family': 'exectv2_hybrid_key_family_event_ledger', 'source_model': '', 'source_prompt_version': 'exectv2_hybrid_key_family_event_ledger_v0.9.24', 'fact_origin': ' ... (truncated)
```

> Canonical LLM-with-rules stage.

### 10. Seizure Frequency family transform <sub>`exect.hybrid.lens.seizure_frequency`</sub>

rules-owned, representation - **changed**

```text
in : [{'entity': 'SeizureFrequency', 'text': 'seizures', 'attributes': {'NumberOfSeizures': '0', 'CUI': 'C0036572', 'CUIPhrase': 'seizures'}, 'evidence': 'Mr B has been seizure free since March 2025', 'rationale': 'explicit seizure-free statement', 'confidence': 'high', 'component_owner': 'named_model_sf_plus_projection_suppression', 'source_artifact': 'sf.jsonl', 'source_lane': 'model_sf_projection_suppression', 'source_pipeline_family': 'exectv2_hybrid_sf_unknown_suppression', 'source_model': '', 'source_prompt_version': 'exectv2_hybrid_sf_unknown_suppression_v0.7', 'fact_origin': 'target_model_g ... (truncated)
out: [{'entity': 'SeizureFrequency', 'text': 'seizures', 'attributes': {'NumberOfSeizures': '0', 'CUI': 'C0036572', 'CUIPhrase': 'seizures'}, 'evidence': 'Mr B has been seizure free since March 2025', 'rationale': 'explicit seizure-free statement', 'confidence': 'high', 'component_owner': 'named_model_sf_plus_projection_suppression', 'source_artifact': 'sf.jsonl', 'source_lane': 'model_sf_projection_suppression', 'source_pipeline_family': 'exectv2_hybrid_sf_unknown_suppression', 'source_model': '', 'source_prompt_version': 'exectv2_hybrid_sf_unknown_suppression_v0.7', 'fact_origin': 'target_model_g ... (truncated)
```

> Canonical LLM-with-rules stage.

### 11. Prescription family transform <sub>`exect.hybrid.lens.prescription`</sub>

rules-owned, CLINICAL MEANING - **changed**

```text
in : [{'entity': 'Prescription', 'text': 'levetiracetam', 'attributes': {'DrugName': 'levetiracetam', 'DrugDose': '500', 'DoseUnit': 'mg', 'Frequency': '2', 'CUI': 'C0377265', 'CUIPhrase': 'levetiracetam'}, 'evidence': 'He continues on levetiracetam 500mg twice daily', 'rationale': 'current regimen', 'confidence': 'high', 'component_owner': 'named_model_structured_facts', 'source_artifact': 'structured.jsonl', 'source_lane': 'model_structured_key_families', 'source_pipeline_family': 'exectv2_hybrid_key_family_event_ledger', 'source_model': '', 'source_prompt_version': 'exectv2_hybrid_key_family_eve ... (truncated)
out: [{'entity': 'Prescription', 'text': 'levetiracetam', 'attributes': {'DrugName': 'levetiracetam', 'DrugDose': '500', 'DoseUnit': 'mg', 'Frequency': '2', 'CUI': 'C0377265', 'CUIPhrase': 'levetiracetam'}, 'evidence': 'He continues on levetiracetam 500mg twice daily', 'rationale': 'current regimen', 'confidence': 'high', 'component_owner': 'named_model_structured_facts', 'source_artifact': 'structured.jsonl', 'source_lane': 'model_structured_key_families', 'source_pipeline_family': 'exectv2_hybrid_key_family_event_ledger', 'source_model': '', 'source_prompt_version': 'exectv2_hybrid_key_family_eve ... (truncated)
```

> Canonical LLM-with-rules stage.

### 12. Investigations family transform <sub>`exect.hybrid.lens.investigations`</sub>

rules-owned, representation - **changed**

```text
in : [{'entity': 'Investigations', 'text': 'MRI', 'attributes': {'MRI_Performed': 'Yes', 'MRI_Results': 'Normal', 'CUI': 'C0436481', 'CUIPhrase': 'mri normal'}, 'evidence': 'MRI brain was normal', 'rationale': 'investigation with a stated result', 'confidence': 'high', 'component_owner': 'named_model_structured_facts', 'source_artifact': 'structured.jsonl', 'source_lane': 'model_structured_key_families', 'source_pipeline_family': 'exectv2_hybrid_key_family_event_ledger', 'source_model': '', 'source_prompt_version': 'exectv2_hybrid_key_family_event_ledger_v0.9.24', 'fact_origin': 'target_model_gener ... (truncated)
out: [{'entity': 'Investigations', 'text': 'MRI', 'attributes': {'MRI_Performed': 'Yes', 'MRI_Results': 'Normal', 'CUI': 'C0436481', 'CUIPhrase': 'mri normal'}, 'evidence': 'MRI brain was normal', 'rationale': 'investigation with a stated result', 'confidence': 'high', 'component_owner': 'named_model_structured_facts', 'source_artifact': 'structured.jsonl', 'source_lane': 'model_structured_key_families', 'source_pipeline_family': 'exectv2_hybrid_key_family_event_ledger', 'source_model': '', 'source_prompt_version': 'exectv2_hybrid_key_family_event_ledger_v0.9.24', 'fact_origin': 'target_model_gener ... (truncated)
```

> Canonical LLM-with-rules stage.

### 13. Require exact evidence for every finding <sub>`exect.hybrid.evidence_requirement`</sub>

rules-owned, gate - no change

```text
in : 4
out: True
```

> Canonical LLM-with-rules stage.

### 14. Materialize the score views <sub>`exect.hybrid.materialize_views`</sub>

rules-owned, benchmark projection - **changed**

```text
in : 4
out: {'source_scored': 4, 'evidence_valid': 4, 'protocol_model_preserving_canonical': 4, 'dictionary_normalized': 4, 'residual_benchmark_added': 4}
```

> Canonical LLM-with-rules stage.

### 15. Score against gold <sub>`exect.hybrid.score`</sub>

scorer-owned, benchmark projection - **changed**

```text
in : 4 finding(s) over four families
out: {'Diagnosis': 1, 'SeizureFrequency': 1, 'Prescription': 1, 'Investigations': 1}
```

> Scored against gold in a real run. Here the point is the comparison boundary: this method is scored over four families.
