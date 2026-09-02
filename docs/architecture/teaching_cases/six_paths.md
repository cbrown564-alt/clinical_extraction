<!-- GENERATED FILE. Do not edit by hand.
     Source: src/clinical_extraction/architecture/ (stage manifests +
     executed teaching cases). Regenerate with
     python scripts/build_architecture_docs.py -->

# Four-letter teaching walkthrough

Read this page as one continuous tour of the six implemented runners. The tour uses four development-split paper letters: two Gan 2026 rows and two ExECTv2 letters. Model outputs are replay fixtures; no live model call is made. Prediction-bearing stages and post-model gates use the real implemented pipelines. ExECT Score lists the four-family units that left the line; gold comparison lives on Workbench.

The five-stage diagram in the [repository README](../../../README.md) is the short orientation. Each letter page is the full in/out trace.

## The four letters

| Letter | Task | Gold | What it teaches |
| --- | --- | --- | --- |
| `GAN-15431` | Gan 2026 | 1 cluster per 4 month, 5 per cluster | Quiet interval and cluster grammar compete; codebook extract does not assemble the two-part gold. |
| `GAN-2166` | Gan 2026 | unknown | Qualitative 'frequent' has no countable rate; gold is unknown. |
| `EA0186` | ExECTv2 | 21 gold annotations | All four families are present; seizure-frequency windows must stay named, not become a monthly rate. |
| `EA0057` | ExECTv2 | 29 gold annotations | Epileptic and dissociative diagnoses share the letter; rates must stay attached to the right one. |

## `GAN-15431` — Quiet interval versus cluster grammar

The letter states a seizure-free interval of up to four months and clusters of five seizures in a day. Gold needs both parts. Rules get the two-part label; model-led cells collapse toward one part.

**Gold:** 1 cluster per 4 month, 5 per cluster  

Gold is the two-part cluster label `1 cluster per 4 month, 5 per cluster`.

### Gan 2026 — Rules only

**Letter:** `GAN-15431` · **Final output:** `1 cluster per 4 month, 5 per cluster` · **Status:** correct

The first clinical proposer is deterministic rules (stage gan.rules.select_and_render). Open the [method card](../method_cards/gan2026_rules_only.md) for the contract, then the [full stage trace](gan-15431.md#rules-only) for the observed inputs, outputs, and ownership at each stage.

### Gan 2026 — LLM with rules

**Letter:** `GAN-15431` · **Final output:** `1 cluster per 4 month, 5 per cluster` · **Status:** correct

The first clinical proposer is the model proposes and selects (gan.llm_with_rules.model_call); ten deterministic repair families may change the answer afterwards. Open the [method card](../method_cards/gan2026_llm_with_rules.md) for the contract, then the [full stage trace](gan-15431.md#llm-with-rules) for the observed inputs, outputs, and ownership at each stage.

### Gan 2026 — LLM with rules

**Letter:** `GAN-15431` · **Final output:** `1 cluster per 4 month, 5 per cluster` · **Status:** correct

The first clinical proposer is the model proposes and selects (gan.llm_with_rules.model_call); ten deterministic repair families may change the answer afterwards. Open the [method card](../method_cards/gan2026_llm_with_rules.md) for the contract, then the [full stage trace](gan-15431.md#llm-with-rules) for the observed inputs, outputs, and ownership at each stage.

### Gan 2026 — LLM with rules

**Letter:** `GAN-15431` · **Final output:** `1 cluster per 4 month, 5 per cluster` · **Status:** correct

The first clinical proposer is the model proposes and selects (gan.llm_with_rules.model_call); ten deterministic repair families may change the answer afterwards. Open the [method card](../method_cards/gan2026_llm_with_rules.md) for the contract, then the [full stage trace](gan-15431.md#llm-with-rules) for the observed inputs, outputs, and ownership at each stage.

### Gan 2026 — LLM with rules

**Letter:** `GAN-15431` · **Final output:** `1 cluster per 4 month, 5 per cluster` · **Status:** correct

The first clinical proposer is the model proposes and selects (gan.llm_with_rules.model_call); ten deterministic repair families may change the answer afterwards. Open the [method card](../method_cards/gan2026_llm_with_rules.md) for the contract, then the [full stage trace](gan-15431.md#llm-with-rules) for the observed inputs, outputs, and ownership at each stage.

### Gan 2026 — LLM only

**Letter:** `GAN-15431` · **Final output:** `(no scorable label)` · **Status:** incorrect

The first clinical proposer is the model (stage gan.llm.model_call), with one deterministic override at gan.llm.selected_evidence_repair. Open the [method card](../method_cards/gan2026_llm_only.md) for the contract, then the [full stage trace](gan-15431.md#llm-only) for the observed inputs, outputs, and ownership at each stage.

### Gan 2026 — LLM with rules

**Letter:** `GAN-15431` · **Final output:** `1 cluster per 4 month, 5 per cluster` · **Status:** correct

The first clinical proposer is the model proposes and selects (gan.llm_with_rules.model_call); ten deterministic repair families may change the answer afterwards. Open the [method card](../method_cards/gan2026_llm_with_rules.md) for the contract, then the [full stage trace](gan-15431.md#llm-with-rules) for the observed inputs, outputs, and ownership at each stage.

### What the three Gan answers show

Rules-only returns `1 cluster per 4 month, 5 per cluster`. LLM-only returns `(no scorable label)` (incorrect) against gold `1 cluster per 4 month, 5 per cluster`. LLM-with-rules returns `1 cluster per 4 month, 5 per cluster` (correct).

On this letter the hybrid path is a rescue, credited to `a named deterministic repair`.

This is a mechanism example from a development letter and a replayed model output, not a holdout result.

## `GAN-2166` — Abstain when the letter has no countable rate

The letter says frequent petit mal and increasing absences, with no number. Gold is unknown. Rules abstain. Model-led cells may render a qualitative rate that still sits in the unknown bucket.

**Gold:** unknown  

Gold is the unknown sentinel: the letter has no countable rate.

### Gan 2026 — Rules only

**Letter:** `GAN-2166` · **Final output:** `no seizure frequency reference` · **Status:** correct

The first clinical proposer is deterministic rules (stage gan.rules.select_and_render). Open the [method card](../method_cards/gan2026_rules_only.md) for the contract, then the [full stage trace](gan-2166.md#rules-only) for the observed inputs, outputs, and ownership at each stage.

### Gan 2026 — LLM with rules

**Letter:** `GAN-2166` · **Final output:** `unknown` · **Status:** correct

The first clinical proposer is the model proposes and selects (gan.llm_with_rules.model_call); ten deterministic repair families may change the answer afterwards. Open the [method card](../method_cards/gan2026_llm_with_rules.md) for the contract, then the [full stage trace](gan-2166.md#llm-with-rules) for the observed inputs, outputs, and ownership at each stage.

### Gan 2026 — LLM with rules

**Letter:** `GAN-2166` · **Final output:** `1 per 1 year` · **Status:** incorrect

Changed repair stages: `Repair 5 - breakthrough seizures`.

The first clinical proposer is the model proposes and selects (gan.llm_with_rules.model_call); ten deterministic repair families may change the answer afterwards. Open the [method card](../method_cards/gan2026_llm_with_rules.md) for the contract, then the [full stage trace](gan-2166.md#llm-with-rules) for the observed inputs, outputs, and ownership at each stage.

### Gan 2026 — LLM with rules

**Letter:** `GAN-2166` · **Final output:** `1 per 1 year` · **Status:** incorrect

Changed repair stages: `Repair 5 - breakthrough seizures`.

The first clinical proposer is the model proposes and selects (gan.llm_with_rules.model_call); ten deterministic repair families may change the answer afterwards. Open the [method card](../method_cards/gan2026_llm_with_rules.md) for the contract, then the [full stage trace](gan-2166.md#llm-with-rules) for the observed inputs, outputs, and ownership at each stage.

### Gan 2026 — LLM with rules

**Letter:** `GAN-2166` · **Final output:** `unknown` · **Status:** correct

The first clinical proposer is the model proposes and selects (gan.llm_with_rules.model_call); ten deterministic repair families may change the answer afterwards. Open the [method card](../method_cards/gan2026_llm_with_rules.md) for the contract, then the [full stage trace](gan-2166.md#llm-with-rules) for the observed inputs, outputs, and ownership at each stage.

### Gan 2026 — LLM only

**Letter:** `GAN-2166` · **Final output:** `(no scorable label)` · **Status:** incorrect

The first clinical proposer is the model (stage gan.llm.model_call), with one deterministic override at gan.llm.selected_evidence_repair. Open the [method card](../method_cards/gan2026_llm_only.md) for the contract, then the [full stage trace](gan-2166.md#llm-only) for the observed inputs, outputs, and ownership at each stage.

### Gan 2026 — LLM with rules

**Letter:** `GAN-2166` · **Final output:** `1 per 1 year` · **Status:** incorrect

Changed repair stages: `Repair 5 - breakthrough seizures`.

The first clinical proposer is the model proposes and selects (gan.llm_with_rules.model_call); ten deterministic repair families may change the answer afterwards. Open the [method card](../method_cards/gan2026_llm_with_rules.md) for the contract, then the [full stage trace](gan-2166.md#llm-with-rules) for the observed inputs, outputs, and ownership at each stage.

### What the three Gan answers show

Rules-only returns `no seizure frequency reference`. LLM-only returns `(no scorable label)` (incorrect) against gold `unknown`. LLM-with-rules returns `1 per 1 year` (incorrect).

On this letter the hybrid path is not a rescue. The trace keeps the wrong answer visible.

This is a mechanism example from a development letter and a replayed model output, not a holdout result.

## `EA0186` — Four families and named time windows

The letter has diagnosis, several dated seizure statements, a current regimen, and completed tests. The hard part is binding 'last month' and '10 months ago' to counts, not to a recurring rate.

**Gold:** 21 gold annotations  

Gold covers diagnosis, dated seizure-frequency windows, lamotrigine, and abnormal MRI/EEG.

### ExECTv2 — Rules only

**Letter:** `EA0186` · **Final output:** `Diagnosis: focal epilepsy; focal to bilateral convulsive seizure; focal motor seizure
Seizure frequency: seizure (active-rate); focal to bilateral convulsive seizure (active-rate); focal (seizure-free)
Prescription: lamotrigine 75 mg ×2
Investigations: MRI performed abnormal; EEG performed abnormal` · **Status:** no correctness verdict is claimed for this trace

The first clinical proposer is the nine deterministic extractors (stage exect.rules.extract_entities); the four-family projection is scorer-facing. Open the [method card](../method_cards/exectv2_rules_only.md) for the contract, then the [full stage trace](ea0186.md#rules-only) for the observed inputs, outputs, and ownership at each stage.

### ExECTv2 — LLM pre-post

**Letter:** `EA0186` · **Final output:** `Diagnosis: focal epilepsy; focal to bilateral convulsive seizure; focal motor seizure
Seizure frequency: event (seizure-free)
Prescription: lamotrigine 75 mg ×2
Investigations: MRI performed abnormal; EEG performed abnormal` · **Status:** no correctness verdict is claimed for this trace

The first clinical proposer is the named model proposes all four families (exect.llm_pre_post.model_call); four family transforms and the named Select-rule stack may change findings afterwards. Open the [method card](../method_cards/exectv2_llm_pre_post.md) for the contract, then the [full stage trace](ea0186.md#llm-pre-post) for the observed inputs, outputs, and ownership at each stage.

### ExECTv2 — LLM only

**Letter:** `EA0186` · **Final output:** `Diagnosis: focal epilepsy; focal to bilateral convulsive seizure; focal motor seizure
Seizure frequency: seizure (active-rate); These (unknown); event (seizure-free); focal to bilateral convulsive seizure (active-rate)
Prescription: lamotrigine 75 mg ×2
Investigations: MRI performed abnormal; EEG performed abnormal` · **Status:** no correctness verdict is claimed for this trace

The first clinical proposer is the named model (stage exect.llm.model_call); deterministic stages only parse, represent, and gate its findings. Open the [method card](../method_cards/exectv2_llm_only.md) for the contract, then the [full stage trace](ea0186.md#llm-only) for the observed inputs, outputs, and ownership at each stage.

### ExECTv2 — LLM only

**Letter:** `EA0186` · **Final output:** `Diagnosis: focal epilepsy; focal to bilateral convulsive seizure; focal motor seizure
Seizure frequency: seizure (active-rate); focal motor seizures (unknown); focal to bilateral convulsive seizure (active-rate)
Prescription: lamotrigine 75 mg ×2
Investigations: MRI performed abnormal; EEG performed abnormal` · **Status:** no correctness verdict is claimed for this trace

The first clinical proposer is the named model (stage exect.llm.model_call); deterministic stages only parse, represent, and gate its findings. Open the [method card](../method_cards/exectv2_llm_only.md) for the contract, then the [full stage trace](ea0186.md#llm-only) for the observed inputs, outputs, and ownership at each stage.

### ExECTv2 — LLM only

**Letter:** `EA0186` · **Final output:** `Diagnosis: focal epilepsy; focal to bilateral convulsive seizure; focal motor seizure
Seizure frequency: seizure (active-rate); focal motor seizures (unknown); focal to bilateral convulsive seizure (active-rate)
Prescription: lamotrigine 75 mg ×2
Investigations: MRI performed abnormal; EEG performed abnormal` · **Status:** no correctness verdict is claimed for this trace

The first clinical proposer is the named model (stage exect.llm.model_call); deterministic stages only parse, represent, and gate its findings. Open the [method card](../method_cards/exectv2_llm_only.md) for the contract, then the [full stage trace](ea0186.md#llm-only) for the observed inputs, outputs, and ownership at each stage.

This is a mechanism example from a development letter and a replayed model output, not a holdout result.

## `EA0057` — Which rate belongs to which diagnosis

The letter states structural epilepsy that is now quiet and dissociative attacks twice a week. A model that puts the weekly rate on epilepsy has mixed the two diagnoses.

**Gold:** 29 gold annotations  

Gold separates symptomatic structural epilepsy from dissociative attacks and keeps each frequency on its own diagnosis.

### ExECTv2 — Rules only

**Letter:** `EA0057` · **Final output:** `Diagnosis: focal epilepsy; focal motor seizure; focal to bilateral convulsive seizure; epileptic seizure
Seizure frequency: seizures (active-rate); focal motor seizures (seizure-free)
Prescription: levetiracetam 1000 mg ×2
Investigations: MRI performed abnormal` · **Status:** no correctness verdict is claimed for this trace

The first clinical proposer is the nine deterministic extractors (stage exect.rules.extract_entities); the four-family projection is scorer-facing. Open the [method card](../method_cards/exectv2_rules_only.md) for the contract, then the [full stage trace](ea0057.md#rules-only) for the observed inputs, outputs, and ownership at each stage.

### ExECTv2 — LLM pre-post

**Letter:** `EA0057` · **Final output:** `Diagnosis: focal epilepsy; focal motor seizure; focal to bilateral convulsive seizure
Seizure frequency: seizure (seizure-free); focal to bilateral convulsive seizures (seizure-free)
Prescription: levetiracetam 1000 mg ×2
Investigations: MRI performed abnormal` · **Status:** no correctness verdict is claimed for this trace

The first clinical proposer is the named model proposes all four families (exect.llm_pre_post.model_call); four family transforms and the named Select-rule stack may change findings afterwards. Open the [method card](../method_cards/exectv2_llm_pre_post.md) for the contract, then the [full stage trace](ea0057.md#llm-pre-post) for the observed inputs, outputs, and ownership at each stage.

### ExECTv2 — LLM only

**Letter:** `EA0057` · **Final output:** `Diagnosis: symptomatic structural epilepsy; epilepsy; focal motor seizure; focal to bilateral convulsive seizure; epileptic seizure
Seizure frequency: seizure like this (seizure-free); focal to bilateral convulsive seizures (seizure-free)
Prescription: levetiracetam 1000 mg ×2
Investigations: MRI performed abnormal` · **Status:** no correctness verdict is claimed for this trace

The first clinical proposer is the named model (stage exect.llm.model_call); deterministic stages only parse, represent, and gate its findings. Open the [method card](../method_cards/exectv2_llm_only.md) for the contract, then the [full stage trace](ea0057.md#llm-only) for the observed inputs, outputs, and ownership at each stage.

### ExECTv2 — LLM only

**Letter:** `EA0057` · **Final output:** `Diagnosis: focal epilepsy; focal motor seizure; focal to bilateral convulsive seizure
Seizure frequency: seizures (seizure-free); focal to bilateral convulsive seizures (seizure-free)
Prescription: levetiracetam 1000 mg ×2
Investigations: MRI performed abnormal` · **Status:** no correctness verdict is claimed for this trace

The first clinical proposer is the named model (stage exect.llm.model_call); deterministic stages only parse, represent, and gate its findings. Open the [method card](../method_cards/exectv2_llm_only.md) for the contract, then the [full stage trace](ea0057.md#llm-only) for the observed inputs, outputs, and ownership at each stage.

### ExECTv2 — LLM only

**Letter:** `EA0057` · **Final output:** `Diagnosis: focal epilepsy; focal motor seizure; focal to bilateral convulsive seizure
Seizure frequency: seizures (seizure-free); focal to bilateral convulsive seizures (seizure-free)
Prescription: levetiracetam 1000 mg ×2
Investigations: MRI performed abnormal` · **Status:** no correctness verdict is claimed for this trace

The first clinical proposer is the named model (stage exect.llm.model_call); deterministic stages only parse, represent, and gate its findings. Open the [method card](../method_cards/exectv2_llm_only.md) for the contract, then the [full stage trace](ea0057.md#llm-only) for the observed inputs, outputs, and ownership at each stage.

This is a mechanism example from a development letter and a replayed model output, not a holdout result.
