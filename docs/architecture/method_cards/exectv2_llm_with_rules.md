<!-- GENERATED FILE. Do not edit by hand.
     Source: src/clinical_extraction/architecture/ (stage manifests +
     executed teaching cases). Regenerate with
     python scripts/build_architecture_docs.py -->

# ExECTv2 - LLM with rules

Method id: `exectv2_llm_with_rules`  
Role: **selected**  
Stages: 15  
Stages that may change clinical meaning: 6

## One sentence

> The model proposes findings for four families in one call; deterministic family transforms reconcile those findings into the final scored representation.

## Sixty seconds

One structured call per letter asks the named model for candidate findings across Diagnosis, Seizure Frequency, Prescription, and Investigations. No deterministic extractor proposes findings and none is unioned in - that is the family-ownership rule from decision 0040. After the call, code parses and may make one format-only retry, flattens the model's events into ExECT mentions, projects the model's seizure-frequency facts into the required state representation, and suppresses a narrowly defined class of unsupported unknown states. Raw and scored findings are both registered in a finding store, so every later change stays attributable. Then one family transform runs per entity, and the four behave differently: Diagnosis may rewrite, drop, or add concepts; Seizure Frequency is a thin assembly over the earlier projection; Prescription applies dictionary-driven regimen processing with bounded correction; Investigations validates, normalizes, and de-duplicates. Every final finding must carry exact source evidence, and the scored views are then materialized.

## The five recall questions

| Question | Answer |
| --- | --- |
| What enters? | ExectLetter - see `exect.llm_with_rules.build_prompt` |
| Who first proposes the clinical answer? | the named model proposes all four families (exect.llm_with_rules.model_call); four family transforms may change findings afterwards |
| Which later stages may change clinical meaning? | `exect.llm_with_rules.project_and_gate`, `exect.llm_with_rules.sf_state_projection`, `exect.llm_with_rules.sf_unknown_suppression`, `exect.llm_with_rules.lens.diagnosis`, `exect.llm_with_rules.lens.prescription` |
| What final representation is scored? | A PredictedLetter of four-family mentions materialized into named score views; the primary view is clinical fact recovery (`clinical_headline`). |
| What evidence shows whether each component helped or harmed? | `docs/decisions/0040-final-exect-llm-with-rules-family-ownership.md`, `docs/decisions/0041-single-call-exect-model-comparison.md`, `docs/decisions/0045-exect-default-policy-not-joint-combined.md`, `docs/research/six_model_comparison_report_2026-07-18.md` |

## Stages

Read the `Effect` column first. `CLINICAL MEANING` marks every stage that can change the answer.

| # | Stage | Owner | Effect | What it does |
| --- | --- | --- | --- | --- |
| 1 | `exect.llm_with_rules.build_prompt`<br>Build the four-family prompt | rules | transport/schema only | Render the note text and the four-family event-ledger schema into the prompt input for one structured call. |
| 2 | `exect.llm_with_rules.model_call`<br>Model proposes findings for four families | model | CLINICAL MEANING | One structured call returns candidate findings for Diagnosis, Seizure Frequency, Prescription, and Investigations, each with evidence. |
| 3 | `exect.llm_with_rules.parse_and_retry`<br>Parse output, with format-only retry when eligible | rules | transport/schema only | Recover and repair the JSON payload, coerce legacy mention shapes into events, and for eligible local models make one format-only retry that is accepted only if it validates. |
| 4 | `exect.llm_with_rules.flatten_events`<br>Flatten model events into mentions | rules | representation | Turn each model event into an ExECT mention with its entity, text, attributes, and evidence. |
| 5 | `exect.llm_with_rules.project_and_gate`<br>Enrich attributes and apply render-safety gates | rules | CLINICAL MEANING | Attach CUI and canonical-phrase attributes, drop attribute values outside the closed vocabulary, drop seizure-frequency mentions that carry no frequency state, and drop modality-only Investigations duplicates. |
| 6 | `exect.llm_with_rules.sf_state_projection`<br>Project seizure-frequency facts into the state representation | rules | CLINICAL MEANING | Convert the model's seizure-frequency facts into the state and ownership representation the ExECT scorer expects, adding state attributes and named-type ownership the model did not supply. |
| 7 | `exect.llm_with_rules.sf_unknown_suppression`<br>Suppress unsupported unknown states | rules | CLINICAL MEANING | Remove seizure-frequency findings whose state is unknown and unsupported under the narrowly defined suppression rule. |
| 8 | `exect.llm_with_rules.register_findings`<br>Register raw and scored findings | rules | transport/schema only | Record both the raw and the scored surface of every finding in the finding store, with its producer, source lane, and ownership label. |
| 9 | `exect.llm_with_rules.lens.diagnosis`<br>Diagnosis family transform | rules | CLINICAL MEANING | Reconcile Diagnosis findings using heading recovery and the standard dictionary; may rewrite, drop, or add concepts. |
| 10 | `exect.llm_with_rules.lens.seizure_frequency`<br>Seizure Frequency family transform | rules | representation | Assemble the already-projected and already-suppressed seizure-frequency findings; a thin transform that adds no further clinical change. |
| 11 | `exect.llm_with_rules.lens.prescription`<br>Prescription family transform | rules | CLINICAL MEANING | Apply dictionary-driven regimen processing and bounded correction to Prescription findings. |
| 12 | `exect.llm_with_rules.lens.investigations`<br>Investigations family transform | rules | representation | Validate, normalize, and de-duplicate Investigations findings, including dropping modality-only duplicates of a finding that already carries a result. |
| 13 | `exect.llm_with_rules.evidence_requirement`<br>Require exact evidence for every finding | rules | gate | Reject the assembled letter if any final finding lacks evidence or carries evidence that is not an exact substring of the note. |
| 14 | `exect.llm_with_rules.materialize_views`<br>Materialize the score views | rules | benchmark projection | Build the named prediction views - raw candidate, evidence valid, and clinical fact recovery - from the same assembled findings. |
| 15 | `exect.llm_with_rules.score`<br>Score against gold | scorer | benchmark projection | Match the materialized view's mentions to gold annotations and report per-entity and overall precision, recall, and F1. |

## Stage walkthrough

### 1. Build the four-family prompt

`exect.llm_with_rules.build_prompt` - rules-owned, transport/schema only, rule category `general`

Render the note text and the four-family event-ledger schema into the prompt input for one structured call.

|  | Type | Example |
| --- | --- | --- |
| In | ExectLetter | letter text plus letter id |
| Out | prompt input JSON (str) | {"note_text": "...", "families": ["Diagnosis", "SeizureFrequency", "Prescription", "Investigations"]} |

- Code: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/llm/pipelines/key_entities_structured/prompt_builders.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/llm/pipelines/key_entities_structured/prompt_builders.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured.prompt_builders:build_prompt_input`)
- Test: [`tests/test_exectv2_llm_only_prompt_contract.py`](../../../tests/test_exectv2_llm_only_prompt_contract.py)
- Proven in a trace by: `prompt_version`
- Paper wording: A single prompt requests candidate findings for four clinical families.

### 2. Model proposes findings for four families

`exect.llm_with_rules.model_call` - model-owned, CLINICAL MEANING

One structured call returns candidate findings for Diagnosis, Seizure Frequency, Prescription, and Investigations, each with evidence.

|  | Type | Example |
| --- | --- | --- |
| In | prompt input JSON (str) | letter text plus the four-family schema |
| Out | raw structured JSON (str) | {"events": [{"family": "Diagnosis", "text": "focal epilepsy", "evidence": "Diagnosis: focal epilepsy"}]} |

> Decision 0040: the named model supplies all four families. No deterministic extractor may replace or be unioned into its result. This is what historical v08 did differently.

- Code: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/llm/pipelines/key_entities_structured/signatures.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/llm/pipelines/key_entities_structured/signatures.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured.signatures`)
- Test: [`tests/test_exectv2_llm_only_prompt_contract.py`](../../../tests/test_exectv2_llm_only_prompt_contract.py)
- Proven in a trace by: `raw_output`, `model`, `prompt_version`
- Paper wording: A single language-model call proposes candidate findings for all four families.

### 3. Parse output, with format-only retry when eligible

`exect.llm_with_rules.parse_and_retry` - rules-owned, transport/schema only, rule category `general`

Recover and repair the JSON payload, coerce legacy mention shapes into events, and for eligible local models make one format-only retry that is accepted only if it validates.

|  | Type | Example |
| --- | --- | --- |
| In | raw structured JSON (str) | an events list with one unclosed mention object |
| Out | StructuredExtractionRecord plus parse notes | a validated record with four events |

- Code: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/llm/pipelines/key_entities_structured/parsing.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/llm/pipelines/key_entities_structured/parsing.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured.parsing:parse_structured_events_json`)
- Test: [`tests/test_exectv2_local_format_retry.py`](../../../tests/test_exectv2_local_format_retry.py)
- Proven in a trace by: `parse_errors`, `format_retry_notes`
- Paper wording: Malformed model output is repaired at the transport and schema level, with one format-only retry for local models.

### 4. Flatten model events into mentions

`exect.llm_with_rules.flatten_events` - rules-owned, representation, rule category `general`

Turn each model event into an ExECT mention with its entity, text, attributes, and evidence.

|  | Type | Example |
| --- | --- | --- |
| In | StructuredExtractionRecord | an event with family 'Diagnosis' and text 'focal epilepsy' |
| Out | list[MentionForEvidence] | a Diagnosis mention 'focal epilepsy' with its evidence span |

- Code: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/llm/pipelines/key_entities_structured/parsing.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/llm/pipelines/key_entities_structured/parsing.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured.parsing:flatten_events`)
- Test: [`tests/test_exectv2_llm_only_parsing.py`](../../../tests/test_exectv2_llm_only_parsing.py)
- Proven in a trace by: `n_mentions_raw`
- Paper wording: Model events are flattened into entity mentions.

### 5. Enrich attributes and apply render-safety gates

`exect.llm_with_rules.project_and_gate` - rules-owned, CLINICAL MEANING, rule category `clinical_epilepsy`

Attach CUI and canonical-phrase attributes, drop attribute values outside the closed vocabulary, drop seizure-frequency mentions that carry no frequency state, and drop modality-only Investigations duplicates.

|  | Type | Example |
| --- | --- | --- |
| In | list[MentionForEvidence] plus note text | a SeizureFrequency mention with no state attributes; a Prescription mention with Frequency 'twice a day' |
| Out | PredictedLetter plus gate warnings | the SeizureFrequency mention is dropped; the out-of-vocabulary Frequency value is removed |

> Classed as clinical_meaning because it can remove a finding the model produced: a seizure-frequency mention without a frequency state is dropped outright. Its more common behaviour is representation enrichment, which is why it is easy to read as inert.

- Code: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/llm/pipelines/key_entities_structured/projection.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/llm/pipelines/key_entities_structured/projection.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured.projection:to_predicted_letter`)
- Test: [`tests/test_exectv2_llm_only_projection.py`](../../../tests/test_exectv2_llm_only_projection.py)
- Proven in a trace by: `gate_warnings`, `n_evidence_invalid`, `n_mentions_scored`
- Paper wording: Model mentions are enriched with concept identifiers and passed through render-safety gates before assembly.

### 6. Project seizure-frequency facts into the state representation

`exect.llm_with_rules.sf_state_projection` - rules-owned, CLINICAL MEANING, rule category `seizure_frequency`

Convert the model's seizure-frequency facts into the state and ownership representation the ExECT scorer expects, adding state attributes and named-type ownership the model did not supply.

|  | Type | Example |
| --- | --- | --- |
| In | row of seizure-frequency mentions | a mention 'seizure free since March' with no state attribute |
| Out | row of projected seizure-frequency mentions plus recorded actions | the same mention carrying a seizure-free state and last-event date attributes |

> Named 'projection' but classed here as clinical_meaning: it can create the state representation that is scored, and it can add mentions from a candidate. Finding 4 of the 2026-07-30 review names this exact case. The selected setting is ablation='combined', which enables both the state and ownership projections.

- Code: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/sf_state_projection.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/sf_state_projection.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_state_projection:project_row`)
- Test: [`tests/test_exectv2_sf_state_projection.py`](../../../tests/test_exectv2_sf_state_projection.py)
- Proven in a trace by: `diagnostics.actions`, `diagnostics.action_counts`
- Paper wording: Model-produced seizure-frequency facts are projected into the scored state representation, with every projection action recorded.

### 7. Suppress unsupported unknown states

`exect.llm_with_rules.sf_unknown_suppression` - rules-owned, CLINICAL MEANING, rule category `seizure_frequency`

Remove seizure-frequency findings whose state is unknown and unsupported under the narrowly defined suppression rule.

|  | Type | Example |
| --- | --- | --- |
| In | row of projected seizure-frequency mentions | a seizure-frequency mention with an unknown state and no supporting rate |
| Out | row with the suppressed mentions removed plus recorded actions | the unknown-state mention is dropped and the action recorded |

> Removes model-produced findings. Suppression is a clinical change, not a filter on noise.

- Code: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/sf_unknown_suppression.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/sf_unknown_suppression.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_unknown_suppression:suppress_row`)
- Test: [`tests/test_exectv2_sf_unknown_suppression.py`](../../../tests/test_exectv2_sf_unknown_suppression.py)
- Proven in a trace by: `diagnostics.actions`, `diagnostics.action_counts`
- Paper wording: A narrowly scoped deterministic rule suppresses unsupported unknown seizure-frequency states.

### 8. Register raw and scored findings

`exect.llm_with_rules.register_findings` - rules-owned, transport/schema only, rule category `general`

Record both the raw and the scored surface of every finding in the finding store, with its producer, source lane, and ownership label.

|  | Type | Example |
| --- | --- | --- |
| In | per-entity rows plus the letter | the Diagnosis row from the structured producer |
| Out | ClinicalFindingStore | raw and scored surfaces for each of the four families |

> This stage is what makes component attribution possible: the model's raw output survives beside the reconciled output for every entity.

- Code: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/assembly/finding_store.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/assembly/finding_store.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.finding_store:ClinicalFindingStore`)
- Test: [`tests/test_exectv2_clinical_finding_assembly.py`](../../../tests/test_exectv2_clinical_finding_assembly.py)
- Proven in a trace by: `lanes[entity].raw_lane_mentions`, `lanes[entity].predicted_mentions`
- Paper wording: Raw and scored findings are retained separately so every deterministic action stays attributable.

### 9. Diagnosis family transform

`exect.llm_with_rules.lens.diagnosis` - rules-owned, CLINICAL MEANING, rule category `clinical_epilepsy`

Reconcile Diagnosis findings using heading recovery and the standard dictionary; may rewrite, drop, or add concepts.

|  | Type | Example |
| --- | --- | --- |
| In | Diagnosis findings in the store | model finding 'epilepsy' under a 'Diagnosis:' heading listing two conditions |
| Out | reconciled Diagnosis findings plus lens diagnostics | two Diagnosis concepts, one recovered from the heading |

> The active policy variant is 'default' (decision 0045). The 'combined' variant is archived development evidence and must not be the default for new runs. This is the family transform with the widest licence: it is the only one that can add a concept the model did not produce.

- Code: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/assembly/lenses/diagnosis.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/assembly/lenses/diagnosis.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.lenses.diagnosis:DiagnosisDictionaryLens`)
- Test: [`tests/test_exectv2_diagnosis_decomposer.py`](../../../tests/test_exectv2_diagnosis_decomposer.py)
- Proven in a trace by: `lanes.Diagnosis.lens_diagnostics`, `provenance[].action`
- Paper wording: A deterministic Diagnosis transform reconciles model findings against heading structure and the standard dictionary.

### 10. Seizure Frequency family transform

`exect.llm_with_rules.lens.seizure_frequency` - rules-owned, representation, rule category `seizure_frequency`

Assemble the already-projected and already-suppressed seizure-frequency findings; a thin transform that adds no further clinical change.

|  | Type | Example |
| --- | --- | --- |
| In | Seizure Frequency findings in the store | projected seizure-free findings from the sf producer |
| Out | reconciled Seizure Frequency findings | the same findings in assembled form |

> The clinical work for this family happened earlier, at exect.llm_with_rules.sf_state_projection and exect.llm_with_rules.sf_unknown_suppression. Reading the lens alone will understate what happened to Seizure Frequency.

- Code: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/assembly/lenses/seizure_frequency.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/assembly/lenses/seizure_frequency.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.lenses.seizure_frequency:SeizureFrequencyLens`)
- Test: [`tests/test_exectv2_clinical_finding_assembly.py`](../../../tests/test_exectv2_clinical_finding_assembly.py)
- Proven in a trace by: `lanes.SeizureFrequency.lens_diagnostics`
- Paper wording: The Seizure Frequency transform assembles findings whose clinical projection has already been applied.

### 11. Prescription family transform

`exect.llm_with_rules.lens.prescription` - rules-owned, CLINICAL MEANING, rule category `clinical_epilepsy`

Apply dictionary-driven regimen processing and bounded correction to Prescription findings.

|  | Type | Example |
| --- | --- | --- |
| In | Prescription findings in the store | model finding 'levetiracetam 500mg BD' |
| Out | reconciled Prescription findings plus lens diagnostics | a Prescription finding with normalized drug, dose, and regimen attributes |

> The active policy variant is 'default' (decision 0045). Decision 0040 requires bounded correction here rather than deterministic substitution: the rules may correct the model, they may not replace it as the producer.

- Code: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/assembly/lenses/prescription.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/assembly/lenses/prescription.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.lenses.prescription:PrescriptionDictionaryLens`)
- Test: [`tests/test_exectv2_prescription_bounded_policy_candidate.py`](../../../tests/test_exectv2_prescription_bounded_policy_candidate.py)
- Proven in a trace by: `lanes.Prescription.lens_diagnostics`, `provenance[].action`
- Paper wording: A deterministic Prescription transform applies bounded post-model correction to regimen findings.

### 12. Investigations family transform

`exect.llm_with_rules.lens.investigations` - rules-owned, representation, rule category `clinical_epilepsy`

Validate, normalize, and de-duplicate Investigations findings, including dropping modality-only duplicates of a finding that already carries a result.

|  | Type | Example |
| --- | --- | --- |
| In | Investigations findings in the store | 'MRI brain' and 'MRI brain normal' from the same letter |
| Out | reconciled Investigations findings | one Investigations finding 'MRI brain' with a normal result |

- Code: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/assembly/lenses/investigations.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/assembly/lenses/investigations.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.lenses.investigations:InvestigationsLens`)
- Test: [`tests/test_exectv2_clinical_finding_assembly.py`](../../../tests/test_exectv2_clinical_finding_assembly.py)
- Proven in a trace by: `lanes.Investigations.lens_diagnostics`
- Paper wording: A deterministic Investigations transform validates, normalizes, and de-duplicates findings.

### 13. Require exact evidence for every finding

`exect.llm_with_rules.evidence_requirement` - rules-owned, gate, rule category `general`

Reject the assembled letter if any final finding lacks evidence or carries evidence that is not an exact substring of the note.

|  | Type | Example |
| --- | --- | --- |
| In | assembled findings plus note text | a Diagnosis finding whose evidence was paraphrased |
| Out | the assembled letter, or a ValueError | ValueError: assembled 'EA0117' with 1 finding(s) without exact source evidence |

> This gate raises rather than silently dropping. A family transform that invented an unevidenced concept fails the whole letter, which is why the Diagnosis transform's add licence is bounded in practice.

- Code: [`src/clinical_extraction/operational/exect.py`](../../../src/clinical_extraction/operational/exect.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.letter_assembly:assemble_letter`)
- Test: [`tests/test_exectv2_clinical_finding_assembly.py`](../../../tests/test_exectv2_clinical_finding_assembly.py)
- Proven in a trace by: `n_evidence_invalid`
- Paper wording: Every final finding is required to carry evidence that appears verbatim in the source note.

### 14. Materialize the score views

`exect.llm_with_rules.materialize_views` - rules-owned, benchmark projection, rule category `benchmark_format`

Build the named prediction views - raw candidate, evidence valid, and clinical fact recovery - from the same assembled findings.

|  | Type | Example |
| --- | --- | --- |
| In | assembled findings | four families of reconciled findings |
| Out | named FindingViewResult views | a clinical fact recovery (`clinical_headline`) view holding the unit keys |

> One set of findings, several numbers. Naming the view is part of naming the result.

- Code: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/assembly/views.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/assembly/views.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.views:build_scoring_views`)
- Test: [`tests/test_exectv2_scoring_headlines.py`](../../../tests/test_exectv2_scoring_headlines.py)
- Proven in a trace by: `prediction_surfaces`
- Paper wording: Findings are materialized into named scoring views; the primary view is clinical fact recovery (`clinical_headline`).

### 15. Score against gold

`exect.llm_with_rules.score` - scorer-owned, benchmark projection

Match the materialized view's mentions to gold annotations and report per-entity and overall precision, recall, and F1.

|  | Type | Example |
| --- | --- | --- |
| In | materialized view plus gold annotations | clinical fact recovery view against the four-family gold |
| Out | OverallScore plus per-entity EntityScore | a clinical fact recovery overall F1 |

- Code: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/scoring/match.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/scoring/match.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match:score_overall`)
- Test: [`tests/test_exectv2_scoring_match_fidelity.py`](../../../tests/test_exectv2_scoring_match_fidelity.py)
- Proven in a trace by: `scores.overall`, `scores.per_entity`
- Paper wording: Predictions are scored by mention matching against the ExECTv2 gold annotations under the named view.

## Code map

Entry point: [`src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/orchestration/structured_one_call.py`](../../../src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/orchestration/structured_one_call.py) (`clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.structured_one_call:run_llm_with_rules_letter`)

| Stage | Implementation | Governing test |
| --- | --- | --- |
| `exect.llm_with_rules.build_prompt` | `clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured.prompt_builders:build_prompt_input` | `tests/test_exectv2_llm_only_prompt_contract.py` |
| `exect.llm_with_rules.model_call` | `clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured.signatures` | `tests/test_exectv2_llm_only_prompt_contract.py` |
| `exect.llm_with_rules.parse_and_retry` | `clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured.parsing:parse_structured_events_json` | `tests/test_exectv2_local_format_retry.py` |
| `exect.llm_with_rules.flatten_events` | `clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured.parsing:flatten_events` | `tests/test_exectv2_llm_only_parsing.py` |
| `exect.llm_with_rules.project_and_gate` | `clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured.projection:to_predicted_letter` | `tests/test_exectv2_llm_only_projection.py` |
| `exect.llm_with_rules.sf_state_projection` | `clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_state_projection:project_row` | `tests/test_exectv2_sf_state_projection.py` |
| `exect.llm_with_rules.sf_unknown_suppression` | `clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_unknown_suppression:suppress_row` | `tests/test_exectv2_sf_unknown_suppression.py` |
| `exect.llm_with_rules.register_findings` | `clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.finding_store:ClinicalFindingStore` | `tests/test_exectv2_clinical_finding_assembly.py` |
| `exect.llm_with_rules.lens.diagnosis` | `clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.lenses.diagnosis:DiagnosisDictionaryLens` | `tests/test_exectv2_diagnosis_decomposer.py` |
| `exect.llm_with_rules.lens.seizure_frequency` | `clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.lenses.seizure_frequency:SeizureFrequencyLens` | `tests/test_exectv2_clinical_finding_assembly.py` |
| `exect.llm_with_rules.lens.prescription` | `clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.lenses.prescription:PrescriptionDictionaryLens` | `tests/test_exectv2_prescription_bounded_policy_candidate.py` |
| `exect.llm_with_rules.lens.investigations` | `clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.lenses.investigations:InvestigationsLens` | `tests/test_exectv2_clinical_finding_assembly.py` |
| `exect.llm_with_rules.evidence_requirement` | `clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.letter_assembly:assemble_letter` | `tests/test_exectv2_clinical_finding_assembly.py` |
| `exect.llm_with_rules.materialize_views` | `clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.views:build_scoring_views` | `tests/test_exectv2_scoring_headlines.py` |
| `exect.llm_with_rules.score` | `clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match:score_overall` | `tests/test_exectv2_scoring_match_fidelity.py` |

## Not this method

These paths exist and are easy to mistake for the selected method. They are named here so they cannot be read as it.

| Path | Role | Why it is not the selected method |
| --- | --- | --- |
| `src/clinical_extraction/operational/exect.py` | operational wrapper | Adds endpoint handling and live assembly around the same stages. Not a separate method; it must not drift from this manifest. |
| `src/clinical_extraction_local/clinical_findings/pipeline.py` | operational wrapper | The readable public surface over the operational wrapper. |
| `docs/experiments/exectv2/reliability/archive/exectv2_joint_policy_archive_README.md` | historical performance control | v08 used a deterministic Prescription producer and a Seizure Frequency extractor union. It does NOT meet decision 0040 and is not this method, despite sharing the label 'LLM with rules'. |
| `scripts/check_exectv2_joint_bounded_policy_replay.py` | rejected candidate or ablation | The combined/combined Diagnosis and Prescription policy. Demoted by decision 0045; requires an explicit opt-in flag. |

## Executable trace

See the [ExECTv2 teaching case](../teaching_cases/exectv2.md), which runs this method over one letter and records what every stage above actually did.
