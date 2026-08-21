# Methods draft

## Data

This study used two public epilepsy-letter resources with complementary output requirements. They were selected to test whether the same evidence-backed workflow could be evaluated both where a task requires selection of one structured clinical state and where it requires recovery of several supported clinical facts. The datasets, labels, and scoring schemes are distinct; results are therefore reported separately and are not treated as directly comparable.

The Gan 2026 resource supplied a local 1,500-letter subset of fully synthetic epilepsy clinic letters. Each record contains a full letter, a canonical seizure-frequency label, supporting text, and source quality flags. The label scheme represents explicit rates and ranges, cluster patterns, seizure-free durations, unknown frequency, and the absence of a seizure-frequency reference. Its gold label therefore defines a narrow task: select and render the patient's current seizure-frequency state from potentially competing statements in a letter. The fixed, stratified split reserved 300 letters for optimiser-only work, 750 letters for development and error analysis, and 450 letters as a locked holdout. Holdout results were retained and reported in aggregate only; they were not used to inspect failures or to change the system.

ExECTv2 supplied 200 real epilepsy clinic letters with paired stand-off annotations. The full annotation scheme covers nine entity families and associated attributes, including certainty, negation, timing, dose, and investigation result. The primary comparison in this study uses four families: Diagnosis, SeizureFrequency, Prescription, and Investigations. ExECTv2 therefore evaluates recovery of a supported, multi-fact clinical inventory rather than selection of a single answer. The fixed split comprises 140 development letters and a sealed 59-letter holdout. The original 60-letter holdout was reduced by one letter after a duplicate pair crossing the development-test boundary was identified; the development partition was unchanged. As with Gan 2026, holdout rows were not inspected during development.

Preparation was deliberately limited. The supplied letters and annotations were loaded with their original identifiers, labels, attributes, and quality information retained. A small number of non-semantic encoding artefacts, such as literal escaped line breaks, HTML character encodings, garbled quotation marks, and null bytes, were repaired so that text could be read and matched consistently. No clinical wording, frequency statement, gold label, or annotation was rewritten. The fixed split manifests were applied before development or evaluation. In ExECTv2, historical character offsets can no longer align exactly with the corrected letter text; matching therefore uses the benchmark's defined entity and attribute representation rather than treating those offsets as a source of truth.

## Methods still to develop

1. **Study design and the five rungs of rule assistance.** Define the five comparable conditions precisely, including where rules enter before or after the model, which stages share saved model output, and why rule assistance is treated as a depth axis rather than a binary hybrid label.

2. **Common representation and evidence record.** Explain what a model or rules-only path produces, how source evidence is attached, what transformations are recorded, and the boundary between a recorded transformation and a claim of clinical correctness.

3. **Task-specific workflows.** Describe how the common design operates for the one-label Gan task and the four-family ExECTv2 task without implying that their outputs or scores are interchangeable.

4. **Rules-only condition.** State what the deterministic baseline extracts, normalises, selects or assembles, and how its policy differs across the two tasks.

5. **Model procedure.** Document the model roster, the one-call structured request, prompt/schema versions, decoding settings, format-failure handling, and the exact model-produced object before rule assistance.

6. **Deterministic rule assistance.** Explain the pre-generation suggestions and post-generation transformations used at each rung. Separate formatting or validation from transformations that may change the represented clinical answer; give the rationale for the latter without listing every implementation rule in the main text.

7. **Development, model selection, and tuning policy.** Specify what was tuned or selected on development data, what was held fixed before each holdout run, whether any training or hyperparameter optimisation occurred, and how the split policy prevented holdout-driven changes.

8. **Evaluation protocol.** Define the submitted representation and metrics for each task, justify the metrics, state the distinction between primary and diagnostic score views, and describe how aggregate-only holdout reporting was enforced.

9. **Implementation and reproducibility.** Record the software environment, dependencies, runtime configuration, saved-output replay procedure, artifact lineage, and the information needed to reproduce a reported cell.

10. **Ethics and scope.** State the privacy distinction between synthetic Gan letters and the real annotated ExECTv2 corpus, the limits of the evaluation, and that the study is not a clinical deployment or validation claim.
