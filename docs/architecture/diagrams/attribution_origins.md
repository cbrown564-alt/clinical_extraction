<!-- GENERATED FILE. Do not edit by hand.
     Source: src/clinical_extraction/architecture/ (stage manifests +
     executed teaching cases). Regenerate with
     python scripts/build_architecture_docs.py -->

# Result attribution: where a rescue or regression can originate

If a letter's answer changed for the better or the worse, one of the stages below did it. This is the candidate list, derived from the stage manifests - it is structural, not a measurement.

**Counts belong elsewhere.** Measured rescues and regressions live in the retained attribution artifacts named in each method card's evidence owners. This page deliberately does not restate them.

## Gan 2026 - Rules only

First proposer: deterministic rules (stage gan.rules.select_and_render)

```mermaid
flowchart LR
  origin_gan2026_rules_only["answer changed"]
  gan_rules_extract["Extract candidate events"]
  origin_gan2026_rules_only --> gan_rules_extract
  gan_rules_select_and_render["Select the current event and render the label"]
  origin_gan2026_rules_only --> gan_rules_select_and_render
```

## Gan 2026 - LLM only

First proposer: the model (stage gan.llm.model_call), with one deterministic override at gan.llm.selected_evidence_repair

```mermaid
flowchart LR
  origin_gan2026_llm_only["answer changed"]
  gan_llm_model_call["Model decides the final label"]
  origin_gan2026_llm_only --> gan_llm_model_call
  gan_llm_selected_evidence_repair["Evidence-based label repair"]
  origin_gan2026_llm_only --> gan_llm_selected_evidence_repair
```

## Gan 2026 - LLM with rules

First proposer: the model proposes and selects (gan.llm_with_rules.model_call); ten deterministic repair families may change the answer afterwards

```mermaid
flowchart LR
  origin_gan2026_llm_with_rules["answer changed"]
  gan_llm_with_rules_model_call["Model extracts events and selects the answer"]
  origin_gan2026_llm_with_rules --> gan_llm_with_rules_model_call
  gan_llm_with_rules_repair_selected_evidence["Repair 1 - evidence-based label repair"]
  origin_gan2026_llm_with_rules --> gan_llm_with_rules_repair_selected_evidence
  gan_llm_with_rules_repair_monthly_diary["Repair 2 - monthly diary"]
  origin_gan2026_llm_with_rules --> gan_llm_with_rules_repair_monthly_diary
  gan_llm_with_rules_repair_usual_interval["Repair 3 - usual interval"]
  origin_gan2026_llm_with_rules --> gan_llm_with_rules_repair_usual_interval
  gan_llm_with_rules_repair_typical_over_ytd["Repair 4 - typical rate over year-to-date"]
  origin_gan2026_llm_with_rules --> gan_llm_with_rules_repair_typical_over_ytd
  gan_llm_with_rules_repair_breakthrough["Repair 5 - breakthrough seizures"]
  origin_gan2026_llm_with_rules --> gan_llm_with_rules_repair_breakthrough
  gan_llm_with_rules_repair_non_epileptic["Repair 6 - non-epileptic events"]
  origin_gan2026_llm_with_rules --> gan_llm_with_rules_repair_non_epileptic
  gan_llm_with_rules_repair_residual_jerk["Repair 7 - residual jerks"]
  origin_gan2026_llm_with_rules --> gan_llm_with_rules_repair_residual_jerk
  gan_llm_with_rules_repair_post_change_burst["Repair 8 - post-change burst"]
  origin_gan2026_llm_with_rules --> gan_llm_with_rules_repair_post_change_burst
  gan_llm_with_rules_repair_dated_sequence["Repair 9 - dated sequence"]
  origin_gan2026_llm_with_rules --> gan_llm_with_rules_repair_dated_sequence
  gan_llm_with_rules_repair_elapsed_anchor["Repair 10 - elapsed since anchor"]
  origin_gan2026_llm_with_rules --> gan_llm_with_rules_repair_elapsed_anchor
```

## ExECTv2 - Rules only

First proposer: the nine deterministic extractors (stage exect.rules.extract_entities); the four-family projection is scorer-facing

```mermaid
flowchart LR
  origin_exectv2_rules_only["answer changed"]
  exect_rules_extract_seizure_frequency["Extract seizure frequency"]
  origin_exectv2_rules_only --> exect_rules_extract_seizure_frequency
  exect_rules_extract_entities["Extract the other eight entities"]
  origin_exectv2_rules_only --> exect_rules_extract_entities
```

## ExECTv2 - LLM only

First proposer: the named model (stage exect.llm.model_call); deterministic stages only parse, represent, and gate its findings

```mermaid
flowchart LR
  origin_exectv2_llm_only["answer changed"]
  exect_llm_model_call["Model proposes four-family findings"]
  origin_exectv2_llm_only --> exect_llm_model_call
```

## ExECTv2 - LLM with rules

First proposer: the named model proposes all four families (exect.llm_with_rules.model_call); four family transforms may change findings afterwards

```mermaid
flowchart LR
  origin_exectv2_llm_with_rules["answer changed"]
  exect_llm_with_rules_model_call["Model proposes findings for four families"]
  origin_exectv2_llm_with_rules --> exect_llm_with_rules_model_call
  exect_llm_with_rules_project_and_gate["Enrich attributes and apply render-safety gates"]
  origin_exectv2_llm_with_rules --> exect_llm_with_rules_project_and_gate
  exect_llm_with_rules_sf_state_projection["Project seizure-frequency facts into the state representation"]
  origin_exectv2_llm_with_rules --> exect_llm_with_rules_sf_state_projection
  exect_llm_with_rules_sf_unknown_suppression["Suppress unsupported unknown states"]
  origin_exectv2_llm_with_rules --> exect_llm_with_rules_sf_unknown_suppression
  exect_llm_with_rules_lens_diagnosis["Diagnosis family transform"]
  origin_exectv2_llm_with_rules --> exect_llm_with_rules_lens_diagnosis
  exect_llm_with_rules_lens_prescription["Prescription family transform"]
  origin_exectv2_llm_with_rules --> exect_llm_with_rules_lens_prescription
```
