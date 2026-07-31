<!-- GENERATED FILE. Do not edit by hand.
     Source: src/clinical_extraction/architecture/ (stage manifests +
     executed teaching cases). Regenerate with
     python scripts/build_architecture_docs.py -->

# Ownership matrix

Every stage of every selected method, counted by what it is allowed to change. A method is only as explainable as this row.

## Effect classes

| Class | Meaning |
| --- | --- |
| `transport_or_schema` | Changes transport or schema shape only. Cannot change which clinical answer is expressed. |
| `representation` | Changes how a clinical fact is written down (units, casing, state fields) without changing which clinical fact it is. |
| `clinical_meaning` | May change clinical selection or meaning: a different label, a different event, an added or removed finding. |
| `benchmark_projection` | Projects a settled clinical answer into a scorer-facing view. Changes the measured number, not the clinical answer. |
| `validation_gate` | Accepts or rejects. Cannot rewrite a clinical answer, but can fail a row or finding out of the scored set. |

## Counts by method

| Task | Method | Stages | `transport_or_schema` | `representation` | `clinical_meaning` | `benchmark_projection` | `validation_gate` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Gan 2026 | Rules only | 5 | 0 | 1 | 2 | 1 | 1 |
| Gan 2026 | LLM only | 8 | 2 | 0 | 2 | 1 | 3 |
| Gan 2026 | LLM with rules | 20 | 3 | 2 | 11 | 1 | 3 |
| ExECTv2 | Rules only | 4 | 0 | 1 | 2 | 1 | 0 |
| ExECTv2 | LLM only | 6 | 1 | 1 | 1 | 1 | 2 |
| ExECTv2 | LLM with rules | 15 | 3 | 3 | 6 | 2 | 1 |

## Who owns the first clinical answer

| Task | Method | Prediction owner | Scored representation |
| --- | --- | --- | --- |
| Gan 2026 | Rules only | deterministic rules (stage gan.rules.select_and_render) | One Gan label string per letter, projected to a Purist and a Pragmatic category. |
| Gan 2026 | LLM only | the model (stage gan.llm.model_call), with one deterministic override at gan.llm.selected_evidence_repair | One Gan label string per letter, projected to a Purist and a Pragmatic category. |
| Gan 2026 | LLM with rules | the model proposes and selects (gan.hybrid.model_call); ten deterministic repair families may change the answer afterwards | One Gan label string per letter, projected to a Purist and a Pragmatic category. |
| ExECTv2 | Rules only | the nine deterministic extractors (stage exect.rules.extract_entities) | A PredictedLetter of entity mentions with attributes and evidence, scored per entity and overall. |
| ExECTv2 | LLM only | the GEPA program (stage exect.llm.gepa_program) | A PredictedLetter of four-family mentions with attributes and evidence, scored per entity and overall. |
| ExECTv2 | LLM with rules | the named model proposes all four families (exect.hybrid.model_call); four family transforms may change findings afterwards | A PredictedLetter of four-family mentions materialized into named score views; the canonical view is clinical_headline. |

## Every clinical-meaning stage in the system

| Task | Method | Stage | Owner | Rule category |
| --- | --- | --- | --- | --- |
| Gan 2026 | Rules only | `gan.rules.extract` | rules | seizure_frequency |
| Gan 2026 | Rules only | `gan.rules.select_and_render` | rules | seizure_frequency |
| Gan 2026 | LLM only | `gan.llm.model_call` | model | - |
| Gan 2026 | LLM only | `gan.llm.selected_evidence_repair` | rules | seizure_frequency |
| Gan 2026 | LLM with rules | `gan.hybrid.model_call` | model | - |
| Gan 2026 | LLM with rules | `gan.hybrid.repair.selected_evidence` | rules | seizure_frequency |
| Gan 2026 | LLM with rules | `gan.hybrid.repair.monthly_diary` | rules | seizure_frequency |
| Gan 2026 | LLM with rules | `gan.hybrid.repair.usual_interval` | rules | seizure_frequency |
| Gan 2026 | LLM with rules | `gan.hybrid.repair.typical_over_ytd` | rules | seizure_frequency |
| Gan 2026 | LLM with rules | `gan.hybrid.repair.breakthrough` | rules | seizure_frequency |
| Gan 2026 | LLM with rules | `gan.hybrid.repair.non_epileptic` | rules | clinical_epilepsy |
| Gan 2026 | LLM with rules | `gan.hybrid.repair.residual_jerk` | rules | clinical_epilepsy |
| Gan 2026 | LLM with rules | `gan.hybrid.repair.post_change_burst` | rules | seizure_frequency |
| Gan 2026 | LLM with rules | `gan.hybrid.repair.dated_sequence` | rules | seizure_frequency |
| Gan 2026 | LLM with rules | `gan.hybrid.repair.elapsed_anchor` | rules | seizure_frequency |
| ExECTv2 | Rules only | `exect.rules.extract_seizure_frequency` | rules | seizure_frequency |
| ExECTv2 | Rules only | `exect.rules.extract_entities` | rules | clinical_epilepsy |
| ExECTv2 | LLM only | `exect.llm.gepa_program` | model | - |
| ExECTv2 | LLM with rules | `exect.hybrid.model_call` | model | - |
| ExECTv2 | LLM with rules | `exect.hybrid.project_and_gate` | rules | clinical_epilepsy |
| ExECTv2 | LLM with rules | `exect.hybrid.sf_state_projection` | rules | seizure_frequency |
| ExECTv2 | LLM with rules | `exect.hybrid.sf_unknown_suppression` | rules | seizure_frequency |
| ExECTv2 | LLM with rules | `exect.hybrid.lens.diagnosis` | rules | clinical_epilepsy |
| ExECTv2 | LLM with rules | `exect.hybrid.lens.prescription` | rules | clinical_epilepsy |
