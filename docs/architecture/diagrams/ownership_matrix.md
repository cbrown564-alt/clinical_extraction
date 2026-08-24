<!-- GENERATED FILE. Do not edit by hand.
     Source: src/clinical_extraction/architecture/ (stage manifests +
     executed teaching cases). Regenerate with
     python scripts/build_architecture_docs.py -->

# Ownership matrix

Every stage of every implemented runner, counted by what it is allowed to change. A runner is only as explainable as this row.

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
| ExECTv2 | LLM only | 6 | 2 | 0 | 1 | 2 | 1 |
| ExECTv2 | LLM pre-post | 15 | 3 | 2 | 7 | 2 | 1 |

## Who owns the first clinical answer

| Task | Method | Prediction owner | Scored representation |
| --- | --- | --- | --- |
| Gan 2026 | Rules only | deterministic rules (stage gan.rules.select_and_render) | One Gan label string per letter, projected to a Purist and a Pragmatic category. |
| Gan 2026 | LLM only | the model (stage gan.llm.model_call), with one deterministic override at gan.llm.selected_evidence_repair | One Gan label string per letter, projected to a Purist and a Pragmatic category. |
| Gan 2026 | LLM with rules | the model proposes and selects (gan.llm_with_rules.model_call); ten deterministic repair families may change the answer afterwards | One Gan label string per letter, projected to a Purist and a Pragmatic category. |
| ExECTv2 | Rules only | the nine deterministic extractors (stage exect.rules.extract_entities); the four-family projection is scorer-facing | An all-nine PredictedLetter plus an explicit four-family comparison projection, each scored under its named view. |
| ExECTv2 | LLM only | the named model (stage exect.llm.model_call); deterministic stages only parse, represent, and gate its findings | The raw_candidate four-family PredictedLetter from the ExECT LLM only request, scored per entity and overall (raw F1). |
| ExECTv2 | LLM pre-post | the named model proposes all four families (exect.llm_pre_post.model_call); four family transforms and the named Select-rule stack may change findings afterwards | A PredictedLetter of four-family mentions materialized into named score views; paper primary is 4-family micro F1 (`clinical_inventory_unit_keys`); `clinical_headline` is the historical Compact/headline view id. |

## Every clinical-meaning stage in the system

| Task | Method | Stage | Owner | Rule category |
| --- | --- | --- | --- | --- |
| Gan 2026 | Rules only | `gan.rules.extract` | rules | seizure_frequency |
| Gan 2026 | Rules only | `gan.rules.select_and_render` | rules | seizure_frequency |
| Gan 2026 | LLM only | `gan.llm.model_call` | model | - |
| Gan 2026 | LLM only | `gan.llm.selected_evidence_repair` | rules | seizure_frequency |
| Gan 2026 | LLM with rules | `gan.llm_with_rules.model_call` | model | - |
| Gan 2026 | LLM with rules | `gan.llm_with_rules.repair.selected_evidence` | rules | seizure_frequency |
| Gan 2026 | LLM with rules | `gan.llm_with_rules.repair.monthly_diary` | rules | seizure_frequency |
| Gan 2026 | LLM with rules | `gan.llm_with_rules.repair.usual_interval` | rules | seizure_frequency |
| Gan 2026 | LLM with rules | `gan.llm_with_rules.repair.typical_over_ytd` | rules | seizure_frequency |
| Gan 2026 | LLM with rules | `gan.llm_with_rules.repair.breakthrough` | rules | seizure_frequency |
| Gan 2026 | LLM with rules | `gan.llm_with_rules.repair.non_epileptic` | rules | clinical_epilepsy |
| Gan 2026 | LLM with rules | `gan.llm_with_rules.repair.residual_jerk` | rules | clinical_epilepsy |
| Gan 2026 | LLM with rules | `gan.llm_with_rules.repair.post_change_burst` | rules | seizure_frequency |
| Gan 2026 | LLM with rules | `gan.llm_with_rules.repair.dated_sequence` | rules | seizure_frequency |
| Gan 2026 | LLM with rules | `gan.llm_with_rules.repair.elapsed_anchor` | rules | seizure_frequency |
| ExECTv2 | Rules only | `exect.rules.extract_seizure_frequency` | rules | seizure_frequency |
| ExECTv2 | Rules only | `exect.rules.extract_entities` | rules | clinical_epilepsy |
| ExECTv2 | LLM only | `exect.llm.model_call` | model | - |
| ExECTv2 | LLM pre-post | `exect.llm_pre_post.model_call` | model | - |
| ExECTv2 | LLM pre-post | `exect.llm_pre_post.project_and_gate` | rules | clinical_epilepsy |
| ExECTv2 | LLM pre-post | `exect.llm_pre_post.sf_state_projection` | rules | seizure_frequency |
| ExECTv2 | LLM pre-post | `exect.llm_pre_post.sf_unknown_suppression` | rules | seizure_frequency |
| ExECTv2 | LLM pre-post | `exect.llm_pre_post.lens.diagnosis` | rules | clinical_epilepsy |
| ExECTv2 | LLM pre-post | `exect.llm_pre_post.lens.prescription` | rules | clinical_epilepsy |
| ExECTv2 | LLM pre-post | `exect.llm_pre_post.select_rules` | rules | general |
