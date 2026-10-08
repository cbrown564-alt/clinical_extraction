# Trained-model baseline experiments: ModernBERT and LFM2.5

Status: proposed follow-up / supplementary baseline work.

## Motivation

The active one-call study asks whether a capable general model can produce both the established current seizure-frequency answer and a richer source-grounded record without task-specific training. A complementary comparison is therefore useful: how far can models trained directly on the available task data go?

Two baseline families answer different questions:

- **ModernBERT**: a conventional supervised encoder baseline for the narrow seizure-frequency endpoint. This asks how strong a compact discriminative model can be when trained specifically for the benchmark label.
- **LFM2.5**: a compact generative baseline for the richer extraction task. This asks whether a smaller specialised model can learn the structured seizure-frequency record from supervised examples, rather than relying on a large general model plus instructions and schema.

These baselines should be treated as trained comparators, not as replacements for the current one-call method or as prerequisites for the current paper.

## Proposed comparison

| Method | Training on project data | Output | Primary question |
| --- | --- | --- | --- |
| ModernBERT | Yes | Current seizure-frequency class / native task target | How strong is a conventional task-specific classifier? |
| LFM2.5 | Yes | R7 structured record plus declared answer | How strong is compact task-specific structured generation? |
| Current large-model method | No task-specific training | R7 record plus declared answer | How strong is configuration / in-context extraction? |

The value of this comparison is not simply another leaderboard result. It separates two strategies:

1. **large general model + task specification**, and
2. **small specialised model + supervised examples**.

That distinction is relevant to deployment cost, local inference, data efficiency, portability to new extraction families, and the possible use of reviewed rich records as training data.

## ModernBERT baseline

### Scope

Use ModernBERT as a deliberately simple supervised baseline for the existing single-label seizure-frequency endpoint.

A suitable first implementation is:

- note text as input;
- ModernBERT encoder plus classification head;
- standard supervised fine-tuning;
- no deterministic clinical rules;
- no evidence-extraction auxiliary objective;
- no elaborate hyperparameter or architecture search beyond a small predeclared development budget.

The target should align directly with the existing Gan scoring semantics. Preserve the native Purist and Pragmatic evaluation rather than inventing a separate success definition for the baseline.

### Why it is useful

This establishes how much of the narrow task can be solved by conventional task-specific representation learning. It provides a useful counterpoint to both the current one-call LLM and the historical fine-tuned comparator:

> What is gained by a rich, inspectable generative record if a small supervised encoder can already solve much of the selected-label task?

The encoder baseline does not need to produce the richer finding inventory. Its role is to establish a strong narrow-task reference point.

## LFM2.5 baseline

### Scope

Fine-tune LFM2.5 as a compact generative extractor once the reviewed finding-level reference is stable.

The preferred task is:

`source note -> R7 structured seizure-frequency record + declared answer`

Training examples should therefore include the reviewed source-first findings rather than transient model outputs or a schema version still being revised.

### Evaluation

Use the same evaluation decomposition planned for the general-model method:

- native answer agreement;
- whole-finding precision, recall and F1 under the reviewed matching policy;
- attribute-level errors;
- evidence occurrence / location;
- source-support assessment where available;
- schema validity / unusable-output rate;
- runtime, memory and hardware requirements.

This enables a direct comparison between a large untrained model and a small specialised model without reducing the experiment to the final answer label alone.

### Why it is especially interesting

If a compact trained model can reproduce a large proportion of the rich extraction quality, the one-call system may serve not only as an extraction method but also as a route to creating reviewed supervision for cheaper specialised models.

That creates a plausible downstream research programme:

1. define and validate the rich extraction record;
2. construct a reviewed training set;
3. train a small local model on that record;
4. quantify the accuracy / completeness / cost trade-off against the large model.

This is a stronger downstream test of the rich representation than simply adding additional large LLMs to the benchmark.

## Data and split safeguards

Do not train or tune either baseline on locked test450 rows, on labels derived from those rows, or on finding annotations created from those rows before the frozen comparison.

A defensible initial design is:

- use `dev750` as the complete development pool;
- create an internal training / validation partition inside dev750 for supervised optimisation and early stopping;
- freeze architecture, preprocessing, target mapping, decoding and evaluation before test execution;
- execute `test450` only under the same aggregate-only / no-error-inspection restrictions used by the active study;
- retain the reused-holdout limitation when interpreting the result.

If additional genuinely untouched data later becomes available, use it for the stronger generalisation claim rather than treating test450 as fresh holdout evidence.

## Experimental discipline

### ModernBERT

Keep the first baseline intentionally boring. The useful scientific comparison is against a recognisable standard supervised encoder, not against a large hyperparameter search tailored to dev750.

Predeclare at minimum:

- checkpoint / model revision;
- input truncation policy;
- target representation;
- train / validation split;
- random seeds;
- optimisation settings;
- early-stopping rule;
- model-selection metric;
- final native scoring path.

### LFM2.5

Do not begin the main rich-generation experiment until the finding reference and matching policy are sufficiently stable to act as a training target.

Predeclare at minimum:

- exact model checkpoint and parameter scale;
- full fine-tuning versus LoRA / QLoRA;
- R7 serialization used as the target;
- treatment of optional fields and null / omitted values;
- maximum sequence lengths;
- decoding policy;
- schema enforcement or repair policy;
- model-selection metric;
- hardware and training cost.

Any output repair must remain distinguishable from model generation, consistent with the active repository's evaluation principles.

## Suggested priority

1. **Run ModernBERT first** if a lightweight supplementary narrow-task baseline is useful. It is relatively cheap and does not depend on the new finding reference.
2. **Stabilise and evaluate the finding-level reference.** This remains the higher-priority scientific task for the active paper.
3. **Run LFM2.5 after the rich target is stable.** This is the more interesting follow-up experiment because it tests whether reviewed rich outputs can supervise a compact specialised extractor.

## Relationship to the current paper

These experiments should not expand the current paper's critical path unless there is a clear manuscript need for a trained baseline.

ModernBERT is plausible as a supplementary comparator because it tests the narrow endpoint cheaply. LFM2.5 is better framed as follow-up work unless the finding reference is completed early enough that the comparison can be frozen without delaying the principal study.

The current paper already has a coherent question: whether a capable general model can return a richer source-grounded record in one call while preserving the established task outcome. Trained baselines add context to that question; they should not displace it.

## Decision criterion for proceeding

Proceed with a baseline when it answers a distinct question that the current conditions cannot answer:

- **ModernBERT:** what can straightforward supervised classification achieve on the narrow endpoint?
- **LFM2.5:** how much of the richer extraction contract can a compact specialised generative model learn from reviewed examples?

Avoid running them merely to increase the number of models in a results table.
