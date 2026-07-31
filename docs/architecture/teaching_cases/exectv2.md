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

> Nine independent deterministic extractors read the letter, their findings are pooled and de-duplicated, and the result is scored.

**Prediction owner:** the nine deterministic extractors (stage exect.rules.extract_entities)

**Final answer:** Diagnosis x2, Investigations x1, Prescription x1, SeizureFrequency x1

This teaching letter carries no gold annotations, so no correctness verdict is claimed. The comparable unit is nine entities.

3 of 4 stages changed something on this letter.

### 1. Extract seizure frequency <sub>`exect.rules.extract_seizure_frequency`</sub>

rules-owned, CLINICAL MEANING - **changed**

```text
in : Epilepsy clinic letter, 14 March 2026.  Diagnosis: focal epilepsy.  Mr B has been seizure free since March 2025. MRI brain was normal. He continues on levetiracetam 500mg twice daily.
out: ['SeizureFrequency: seizure free [CUI=C1299590, CUIPhrase=seizure free, MonthDate=3, NumberOfSeizures=0, TimeSince_or_TimeOfEvent=Since, YearDate=2025]']
```

> Its own staged sub-pipeline, not a single pattern match.

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
in : 5 mention(s) before identity de-duplication
out: 5 mention(s) after
```

> Removes duplicates, never disagreements.

### 4. Score against gold <sub>`exect.rules.score`</sub>

scorer-owned, benchmark projection - **changed**

```text
in : 5 finding(s) over nine entities
out: {'Diagnosis': 2, 'Investigations': 1, 'Prescription': 1, 'SeizureFrequency': 1}
```

> Scored against gold in a real run. Here the point is the comparison boundary: this method is scored over nine entities.

## LLM only

> A GEPA-optimized program emits de-duplicated clinical facts for four families, and an adapter maps them into ExECT mentions without adding or merging any fact.

**Prediction owner:** the GEPA program (stage exect.llm.gepa_program)

**Final answer:** Diagnosis x1, Investigations x1, Prescription x1, SeizureFrequency x1

This teaching letter carries no gold annotations, so no correctness verdict is claimed. The comparable unit is four families.

3 of 6 stages changed something on this letter.

### 1. GEPA program emits clinical facts <sub>`exect.llm.gepa_program`</sub>

model-owned, CLINICAL MEANING - **changed**

```text
in : Epilepsy clinic letter, 14 March 2026.  Diagnosis: focal epilepsy.  Mr B has been seizure free since March 2025. MRI brain was normal. He continues on levetiracetam 500mg twice daily.
out: {"clinical_facts": [{"family": "diagnosis", "concept": "focal epilepsy", "evidence": "Diagnosis: focal epilepsy", "negation": "affirmed"}, {"family": "seizure_frequency", "seizure_type": "seizures", "state": "seizure_free", "evidence": "Mr B has been seizure free since March 2025"}, {"family": "investigations", "evidence": "MRI brain was normal", "modality": "MRI", "performed": "yes", "result": "normal"}, {"family": "prescription", "source_text": "levetiracetam 500mg twice daily", "evidence": "He continues on levetiracetam 500mg twice daily", "drug": "levetiracetam", "dose": "500", "dose_unit" ... (truncated)
```

> Fixture boundary. Everything after this line is real code.

### 2. Parse JSON and coerce the facts list <sub>`exect.llm.parse_and_coerce`</sub>

rules-owned, transport/schema only - no change

```text
in : {"clinical_facts": [{"family": "diagnosis", "concept": "focal epilepsy", "evidence": "Diagnosis: focal epilepsy", "negation": "affirmed"}, {"family": "seizure_frequency", "seizure_type": "seizures", "state": "seizure_free", "evidence": "Mr B has been seizure free since March 2025"}, {"family": "investigations", "evidence": "MRI brain was normal", "modality": "MRI", "performed": "yes", "result": "normal"}, {"family": "prescription", "source_text": "levetiracetam 500mg twice daily", "evidence": "He continues on levetiracetam 500mg twice daily", "drug": "levetiracetam", "dose": "500", "dose_unit" ... (truncated)
out: 4 fact(s); notes []
```

### 3. Drop malformed or unevidenced facts <sub>`exect.llm.drop_unusable_facts`</sub>

rules-owned, gate - no change

```text
in : 4 parsed fact(s)
out: 4 usable fact(s); notes []
```

> A gate: it removes facts the model produced, it never invents one.

### 4. Map facts to ExECT mentions <sub>`exect.llm.map_to_mentions`</sub>

rules-owned, representation - **changed**

```text
in : ['diagnosis: concept=focal epilepsy, negation=affirmed', 'seizure_frequency: seizure_type=seizures, state=seizure_free', 'investigation: modality=MRI, performed=yes, result=normal', 'prescription: dose=500, dose_unit=milligrams, drug=levetiracetam, frequency=twice a day, source_text=levetiracetam 500mg twice daily']
out: ['Diagnosis: focal epilepsy [Negation=Affirmed]', 'SeizureFrequency: seizures [NumberOfSeizures=0]', 'Investigations: MRI [MRI_Performed=Yes, MRI_Results=Normal]', 'Prescription: levetiracetam 500mg twice daily [DoseUnit=mg, DrugDose=500, DrugName=levetiracetam, Frequency=twice a day]']
```

> Every provenance entry records added_fact={False} and action={'representation_mapping_only'}, so the no-addition claim is checkable per fact.

### 5. Apply evidence and schema gates <sub>`exect.llm.evidence_schema_gates`</sub>

rules-owned, gate - no change

```text
in : 4 mapped mention(s)
out: 4 mention(s) survived; gate warnings ["Prescription: dropped_illegal_value: 'Frequency'='twice a day' not in ['1', '2', '3', 'As_Required']"]
```

### 6. Score against gold <sub>`exect.llm.score`</sub>

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

7 of 15 stages changed something on this letter.

### 1. Build the four-family prompt <sub>`exect.hybrid.build_prompt`</sub>

rules-owned, transport/schema only - **changed**

```text
in : Epilepsy clinic letter, 14 March 2026.  Diagnosis: focal epilepsy.  Mr B has been seizure free since March 2025. MRI brain was normal. He continues on levetiracetam 500mg twice daily.
out: four-family prompt input
```

> Transport only.

### 2. Model proposes findings for four families <sub>`exect.hybrid.model_call`</sub>

model-owned, CLINICAL MEANING - **changed**

```text
in : prompt input (fixture: no model call is made)
out: {"clinical_events": [{"family": "diagnosis", "anchor_text": "focal epilepsy", "evidence": "Diagnosis: focal epilepsy", "event_state": {}, "mentions": [{"entity": "Diagnosis", "text": "focal epilepsy", "attributes": {"DiagCategory": "Epilepsy", "Negation": "Affirmed"}}], "confidence": "high", "rationale": "stated under the diagnosis heading"}, {"family": "seizure_frequency", "anchor_text": "seizure free since March 2025", "evidence": "Mr B has been seizure free since March 2025", "event_state": {}, "mentions": [{"entity": "SeizureFrequency", "text": "seizures", "attributes": {"NumberOfSeizures" ... (truncated)
```

> Fixture boundary. The model supplies all four families; no deterministic extractor proposes findings here.

### 3. Parse output, with format-only retry when eligible <sub>`exect.hybrid.parse_and_retry`</sub>

rules-owned, transport/schema only - no change

```text
in : {"clinical_events": [{"family": "diagnosis", "anchor_text": "focal epilepsy", "evidence": "Diagnosis: focal epilepsy", "event_state": {}, "mentions": [{"entity": "Diagnosis", "text": "focal epilepsy", "attributes": {"DiagCategory": "Epilepsy", "Negation": "Affirmed"}}], "confidence": "high", "rationale": "stated under the diagnosis heading"}, {"family": "seizure_frequency", "anchor_text": "seizure free since March 2025", "evidence": "Mr B has been seizure free since March 2025", "event_state": {}, "mentions": [{"entity": "SeizureFrequency", "text": "seizures", "attributes": {"NumberOfSeizures" ... (truncated)
out: parsed; notes []
```

### 4. Flatten model events into mentions <sub>`exect.hybrid.flatten_events`</sub>

rules-owned, representation - **changed**

```text
in : 4 model event(s)
out: ['Diagnosis: focal epilepsy [DiagCategory=Epilepsy, Negation=Affirmed]', 'SeizureFrequency: seizures [NumberOfSeizures=0]', 'Investigations: MRI [MRI_Performed=Yes, MRI_Results=Normal]', 'Prescription: levetiracetam [DoseUnit=mg, DrugDose=500, DrugName=levetiracetam, Frequency=2]']
```

### 5. Enrich attributes and apply render-safety gates <sub>`exect.hybrid.project_and_gate`</sub>

rules-owned, CLINICAL MEANING - **changed**

```text
in : ['Diagnosis: focal epilepsy [DiagCategory=Epilepsy, Negation=Affirmed]', 'SeizureFrequency: seizures [NumberOfSeizures=0]', 'Investigations: MRI [MRI_Performed=Yes, MRI_Results=Normal]', 'Prescription: levetiracetam [DoseUnit=mg, DrugDose=500, DrugName=levetiracetam, Frequency=2]']
out: ['Diagnosis: focal epilepsy [CUI=C0014547, CUIPhrase=focal epilepsy, DiagCategory=Epilepsy, Negation=Affirmed]', 'SeizureFrequency: seizures [CUI=C0036572, CUIPhrase=seizures, NumberOfSeizures=0]', 'Investigations: MRI [CUI=C0436481, CUIPhrase=mri normal, MRI_Performed=Yes, MRI_Results=Normal]', 'Prescription: levetiracetam [CUI=C0377265, CUIPhrase=levetiracetam, DoseUnit=mg, DrugDose=500, DrugName=levetiracetam, Frequency=2]']
```

> Concept identifiers are attached here, which is why the findings gain CUI attributes they did not have a moment ago. Gate warnings on this letter: none.

### 6. Project seizure-frequency facts into the state representation <sub>`exect.hybrid.sf_state_projection`</sub>

rules-owned, CLINICAL MEANING - no change

```text
in : ['SeizureFrequency: seizures [CUI=C0036572, CUIPhrase=seizures, NumberOfSeizures=0]']
out: ['SeizureFrequency: seizures [CUI=C0036572, CUIPhrase=seizures, NumberOfSeizures=0]']
```

> Named 'projection', but it can create the scored state representation and add mentions. Recorded actions: {}

### 7. Suppress unsupported unknown states <sub>`exect.hybrid.sf_unknown_suppression`</sub>

rules-owned, CLINICAL MEANING - no change

```text
in : 1 projected mention(s)
out: 1 mention(s) after suppression
```

> Removes model-produced findings; a clinical change, not noise filtering.

### 8. Register raw and scored findings <sub>`exect.hybrid.register_findings`</sub>

rules-owned, transport/schema only - **changed**

```text
in : 4 model mention(s)
out: 4 raw and 4 scored finding(s) registered
```

> Raw survives beside scored, which is what makes attribution possible.

### 9. Diagnosis family transform <sub>`exect.hybrid.lens.diagnosis`</sub>

rules-owned, CLINICAL MEANING - no change

```text
in : ['Diagnosis: focal epilepsy [CUI=C0014547, CUIPhrase=focal epilepsy, DiagCategory=Epilepsy, Negation=Affirmed]']
out: ['Diagnosis: focal epilepsy [CUI=C0014547, CUIPhrase=focal epilepsy, DiagCategory=Epilepsy, Negation=Affirmed]']
```

> lens diagnosis_heading_recovery_residual_benchmark_v05; diagnostics {'selected_findings': 1, 'added_heading_recovery_findings': 0, 'producer_id': 'structured_key_family_event_ledger', 'source_lane': 'model_structured_key_families', 'lens_id': 'diagnosis_heading_recovery_residual_benchmark_v05', 'rewritten_dictionary_findings': 0, 'added_dictionary_findings': 0, 'companion_dictionary_findings': 0, 'dropped_dictionary_findings': 0, 'diagnosis_policy_variant': 'default'}

### 10. Seizure Frequency family transform <sub>`exect.hybrid.lens.seizure_frequency`</sub>

rules-owned, representation - no change

```text
in : ['SeizureFrequency: seizures [CUI=C0036572, CUIPhrase=seizures, NumberOfSeizures=0]']
out: ['SeizureFrequency: seizures [CUI=C0036572, CUIPhrase=seizures, NumberOfSeizures=0]']
```

> lens sf_state_projection_suppression_v01; diagnostics {'selected_findings': 1, 'producer_id': 'sf_model_projection_suppression', 'source_lane': 'model_sf_projection_suppression'}

### 11. Prescription family transform <sub>`exect.hybrid.lens.prescription`</sub>

rules-owned, CLINICAL MEANING - no change

```text
in : ['Prescription: levetiracetam [CUI=C0377265, CUIPhrase=levetiracetam, DoseUnit=mg, DrugDose=500, DrugName=levetiracetam, Frequency=2]']
out: ['Prescription: levetiracetam [CUI=C0377265, CUIPhrase=levetiracetam, DoseUnit=mg, DrugDose=500, DrugName=levetiracetam, Frequency=2]']
```

> lens prescription_dictionary_v09; diagnostics {'lens_id': 'prescription_dictionary_v09', 'normalized_dictionary_findings': 0, 'split_regimen_dictionary_findings': 0, 'added_dictionary_findings': 0, 'dropped_dictionary_findings': 0, 'selected_findings': 1, 'prescription_policy_variant': 'default', 'available_residual_rule_groups': {}, 'added_residual_rule_groups': {}}

### 12. Investigations family transform <sub>`exect.hybrid.lens.investigations`</sub>

rules-owned, representation - no change

```text
in : ['Investigations: MRI [CUI=C0436481, CUIPhrase=mri normal, MRI_Performed=Yes, MRI_Results=Normal]']
out: ['Investigations: MRI [CUI=C0436481, CUIPhrase=mri normal, MRI_Performed=Yes, MRI_Results=Normal]']
```

> lens investigations_result_v01; diagnostics {'selected_findings': 1, 'producer_id': 'structured_key_family_event_ledger', 'source_lane': 'model_structured_key_families'}

### 13. Require exact evidence for every finding <sub>`exect.hybrid.evidence_requirement`</sub>

rules-owned, gate - no change

```text
in : 4 final finding(s)
out: all findings carry exact source evidence (assembly did not raise)
```

> This gate raises rather than silently dropping.

### 14. Materialize the score views <sub>`exect.hybrid.materialize_views`</sub>

rules-owned, benchmark projection - **changed**

```text
in : 4 final finding(s)
out: {'source_scored': 4, 'evidence_valid': 4, 'protocol_model_preserving_canonical': 4, 'dictionary_normalized': 4, 'residual_benchmark_added': 4}
```

> One set of findings, several numbers. Naming the view names the result.

### 15. Score against gold <sub>`exect.hybrid.score`</sub>

scorer-owned, benchmark projection - **changed**

```text
in : 4 finding(s) over four families
out: {'Diagnosis': 1, 'SeizureFrequency': 1, 'Prescription': 1, 'Investigations': 1}
```

> Scored against gold in a real run. Here the point is the comparison boundary: this method is scored over four families.
