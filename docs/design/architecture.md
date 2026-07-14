# Software design

The package separates shared extraction code from task-specific clinical logic.

## Package ownership

`clinical_extraction.core` contains code shared across tasks:

- pipeline interfaces and result objects;
- evidence-span utilities;
- validation and repair results;
- shared schema base models.

`clinical_extraction.tasks` contains dataset and task implementations. Each task
owns its loader, schemas, label rules, deterministic components, model programs,
scorers, and error analysis.

The implementation keeps these decisions separate:

- loading and scoring;
- extracting events and selecting the final clinical answer;
- normalizing labels and mapping them to metrics;
- checking evidence and judging clinical correctness;
- choosing a model and choosing a prompt;
- saved outputs and package source;
- general, clinical, dataset-specific, and benchmark-format rules.

Record the model and route in every run. Use
[component attribution](component_evidence_attribution_architecture.md) when a
study compares methods or changes a selected result.

## ExECT clinical findings

Current ExECT code combines extracted findings before scoring them:

- `ClinicalFinding` stores one clinical assertion, its attributes, evidence,
  source, and change history.
- `ClinicalFindingStore` collects findings for one letter.
- `CandidateProducer` proposes findings, including adapters that replay saved
  JSONL outputs.
- `EntityLens` is the retained code name for entity-specific reconciliation.
  In prose, call it a diagnosis, seizure-frequency, prescription, or
  investigation transform.
- `FindingView` formats the final findings for each score.
- `AttributionSidecar` is the retained code name for records that identify the
  producer, deterministic changes, evidence status, and score-specific output.

The first saved implementation,
`exectv2_holistic_finding_assembly_v01_dev140`, replays development outputs
through these objects without changing behavior. Its identifier remains only
for saved-evidence compatibility.

## Final ExECT LLM-with-rules ownership

The final model comparison is model-led at the input to each main family:

| Family | Model supplies | Deterministic code may do | Deterministic code must not do |
| --- | --- | --- | --- |
| Diagnosis | Concepts, assertions, and evidence | Normalize and apply recorded heading, boundary, and residual recovery | Substitute a rules-only diagnosis result |
| Seizure Frequency | Structured frequency facts and evidence | Project model-selected operands and suppress unsupported states | Union an independent deterministic extractor into the answer |
| Prescription | Medication regimen facts and evidence | Normalize, split supported regimens, remove unsupported facts, and apply bounded repair | Substitute the deterministic all-entity or Prescription extractor |
| Investigations | Findings and evidence | Validate, normalize, and deduplicate | Substitute an independent deterministic extractor |

Rules that change a clinical fact remain prediction owners and make that fact
hybrid. The attribution record must preserve those changes instead of crediting
the final result entirely to the model. See
[decision 0040](../decisions/0040-final-exect-llm-with-rules-family-ownership.md).

## Deterministic rule groups

- `general`: dates, durations, intervals, sections, and evidence checks;
- `clinical_epilepsy`: seizure terminology and epilepsy-note conventions;
- `seizure_frequency`: rates, clusters, seizure-free duration, and temporal selection;
- `gan2026_specific`: Gan synthetic-letter patterns and data quirks;
- `benchmark_format`: Gan label formatting that does not change clinical meaning.

Each group must be testable and, where practical, removable for comparison.

## Deliberate exclusions

The project does not need a generic workflow engine, a fully pluggable registry,
dataset-independent prompt abstractions, or support for every epilepsy dataset.
Add such machinery only after repeated code demonstrates the need.
