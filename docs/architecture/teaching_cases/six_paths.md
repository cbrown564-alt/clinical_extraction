<!-- GENERATED FILE. Do not edit by hand.
     Source: src/clinical_extraction/architecture/ (stage manifests +
     executed teaching cases). Regenerate with
     python scripts/build_architecture_docs.py -->

# Six-path teaching walkthrough

Read this page as one continuous tour of the selected system. The tour uses two synthetic letters because Gan 2026 and ExECTv2 have different output contracts: `TEACH-GAN-01` supplies the competing frequency example, and `TEACH-EXECT-01` supplies the four-family example. No model call is made; fixture model outputs are marked at the model boundary, and every later observation comes from the real implementation.

The five-stage diagram in the [repository README](../../../README.md) is the short orientation. Each link below opens the generated method card and the full stage trace for that path.

## Walk the six paths in order

### 1. Gan 2026 — Rules only

**Letter:** `TEACH-GAN-01` · **Final output:** `1 per month` · **Status:** correct

**Stages:** Extract candidate events → Normalize candidate events → Select the current event and render the label → Check evidence and clinical trace → Project to Purist and Pragmatic scoring

The first clinical proposer is deterministic rules (stage gan.rules.select_and_render). Open the [method card](../method_cards/gan2026_rules_only.md) for the contract, then the [full stage trace](gan2026.md#rules-only) for the observed inputs, outputs, and ownership at each stage.

### 2. Gan 2026 — LLM only

**Letter:** `TEACH-GAN-01` · **Final output:** `7 per year` · **Status:** incorrect

**Stages:** Build the decision prompt → Model decides the final label → Repair JSON dialect and payload shape → Validate the decision schema → Evidence-based label repair → Check the label is scorable → Check evidence is an exact substring → Project to Purist and Pragmatic scoring

The first clinical proposer is the model (stage gan.llm.model_call), with one deterministic override at gan.llm.selected_evidence_repair. Open the [method card](../method_cards/gan2026_llm_only.md) for the contract, then the [full stage trace](gan2026.md#llm-only) for the observed inputs, outputs, and ownership at each stage.

### 3. Gan 2026 — LLM with rules

**Letter:** `TEACH-GAN-01` · **Final output:** `1 per month` · **Status:** correct

**Stages:** Build the structured-events prompt → Model extracts events and selects the answer → Repair JSON dialect and payload shape → Format-only retry (local models) → Validate the extraction schema → Normalize every event → Resolve the label from the model's selection → Repair 1 - evidence-based label repair → Repair 2 - monthly diary → Repair 3 - usual interval → Repair 4 - typical rate over year-to-date → Repair 5 - breakthrough seizures → Repair 6 - non-epileptic events → Repair 7 - residual jerks → Repair 8 - post-change burst → Repair 9 - dated sequence → Repair 10 - elapsed since anchor → Check the label is scorable → Check evidence is an exact substring → Project to Purist and Pragmatic scoring

The first clinical proposer is the model proposes and selects (gan.hybrid.model_call); ten deterministic repair families may change the answer afterwards. Open the [method card](../method_cards/gan2026_llm_with_rules.md) for the contract, then the [full stage trace](gan2026.md#llm-with-rules) for the observed inputs, outputs, and ownership at each stage.

### 4. ExECTv2 — Rules only

**Letter:** `TEACH-EXECT-01` · **Final output:** `Diagnosis x2, Investigations x1, Prescription x1, SeizureFrequency x1` · **Status:** no correctness verdict is claimed for this fixture

**Stages:** Extract seizure frequency → Extract the other eight entities → De-duplicate mentions → Score against gold

The first clinical proposer is the nine deterministic extractors (stage exect.rules.extract_entities); the four-family projection is scorer-facing. Open the [method card](../method_cards/exectv2_rules_only.md) for the contract, then the [full stage trace](exectv2.md#rules-only) for the observed inputs, outputs, and ownership at each stage.

### 5. ExECTv2 — LLM only

**Letter:** `TEACH-EXECT-01` · **Final output:** `Diagnosis x1, Investigations x1, Prescription x1, SeizureFrequency x1` · **Status:** no correctness verdict is claimed for this fixture

**Stages:** Build the four-family prompt → Model proposes four-family findings → Parse output with format-only retry → Flatten events into mentions → Apply representation and evidence gates → Materialize the raw candidate view → Score against gold

The first clinical proposer is the named model (stage exect.llm.model_call); deterministic stages only parse, represent, and gate its findings. Open the [method card](../method_cards/exectv2_llm_only.md) for the contract, then the [full stage trace](exectv2.md#llm-only) for the observed inputs, outputs, and ownership at each stage.

### 6. ExECTv2 — LLM with rules

**Letter:** `TEACH-EXECT-01` · **Final output:** `Diagnosis x1, Investigations x1, Prescription x1, SeizureFrequency x1` · **Status:** no correctness verdict is claimed for this fixture

**Stages:** Build the four-family prompt → Model proposes findings for four families → Parse output, with format-only retry when eligible → Flatten model events into mentions → Enrich attributes and apply render-safety gates → Project seizure-frequency facts into the state representation → Suppress unsupported unknown states → Register raw and scored findings → Diagnosis family transform → Seizure Frequency family transform → Prescription family transform → Investigations family transform → Require exact evidence for every finding → Materialize the score views → Score against gold

The first clinical proposer is the named model proposes all four families (exect.hybrid.model_call); four family transforms may change findings afterwards. Open the [method card](../method_cards/exectv2_llm_with_rules.md) for the contract, then the [full stage trace](exectv2.md#llm-with-rules) for the observed inputs, outputs, and ownership at each stage.

## Deliberate failure and recovery

**Failure:** the Gan LLM-only path returns `7 per year` against the teaching answer `1 per month`. Its full trace preserves the model label and quoted evidence, making the selection error visible rather than silently rewriting it.

**Recovery:** the LLM-with-rules path starts from the same competing model choice and reaches `1 per month`. The change is credited to `Repair 4 - typical rate over year-to-date`; the [Gan teaching trace](gan2026.md#llm-with-rules) shows the before/after values and the evidence check.

This is a mechanism example from a synthetic fixture, not a clinical validation result.
