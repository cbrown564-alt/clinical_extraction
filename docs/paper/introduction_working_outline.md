# Introduction working outline

Status: a decision record and paragraph-card outline, not draft prose. It records the current focus so that later drafting does not reopen settled choices by accident.

## Central argument

Epilepsy clinic letters contain rich, relevant, but temporally distributed and uncertain information. Turning that information into a structured output is not a task-neutral act of finding facts: it applies a purpose-specific policy about what to retain and how to represent it. Modern language models can produce rich, evidence-linked candidate records; explicit rules can then make that policy transparent, configurable, and replayable.

## Scope and claim boundaries

- The paper evaluates an engineering approach to structured extraction, not a deployed clinical decision-support system.
- Evidence links, model-proposed selections, stated rationales, and deterministic changes support review. They do not prove clinical correctness or expose hidden model reasoning.
- The study evaluates two public epilepsy-letter datasets with different task demands. This supports breadth and evidence about transferability; it is not automatically formal external clinical validation.
- The contribution is not that hybrid or neuro-symbolic clinical NLP is new. Prior work already combines rules, retrieval, schemas, validation, and review.
- The contribution is the controlled comparison of where rule assistance is applied, and the analysis of how explicit policy operates on evidence-rich model candidates in two complementary tasks.
- Do not claim that greater symbolic authority is always better. The design involves trade-offs among constraint, flexibility, latency, and cost.

## Paragraph 1 - Clinical information creates the technical problem

**Reader question:** Why does this extraction problem matter?

**Conclusion:** Important epilepsy information is often contained in narrative clinic letters, limiting the structured information available for several established clinical-information-extraction uses.

**Context and content:** Explain that seizure frequency, treatment changes, and related clinical context are often expressed in free text rather than clean structured fields. Cohort identification, retrospective outcome analysis, and longitudinal patient timelines illustrate why clinical information extraction needs such structured information. They motivate the field; this study does not evaluate those downstream uses.

**Bridge:** A clinically important question becomes a problem of converting flexible narrative into structured information.

**Decision:** Keep the clinical motivation focused on the narrative-data bottleneck. Do not introduce drug resistance, seizure-freedom targets, trial cost, or treatment impact.

**Still to decide / source:** Select sources for the narrative-data bottleneck and representative downstream uses.

## Paragraph 2 - Structured extraction necessarily applies policy

**Reader question:** Why is this more difficult than recognising medical terms?

**Conclusion:** A letter may support several true, overlapping, temporal, or uncertain statements, whereas a downstream task requires a particular structured representation; every such output therefore applies policy.

**Context and content:** Explain that there is no task-neutral complete extraction of a clinical letter. A task must choose purpose, timeframe, granularity, uncertainty treatment, and what counts as a retained fact. Gan illustrates selection of a current seizure-frequency representation; ExECT illustrates a finite inventory with attributes and inclusion rules.

**Bridge:** The methodological question is how to combine flexible interpretation with an explicit, reviewable representation policy.

**Decision:** Keep this paragraph fully general. Introduce Gan and ExECT only in the study paragraph.

**Still to decide / source:** Cite the general clinical-extraction and representation problem without relying on a task-specific example.

## Paragraph 3 - Prior methods and the location of rule authority

**Reader question:** Why are existing rule-based, model-based, and hybrid approaches insufficient on their own?

**Conclusion:** The decisive hybrid design choice is where symbolic rules enter the pipeline and whether they can influence, validate, or change a model-proposed output.

**Context and content:** Rules are controllable and effective for constrained representations but brittle with varied narrative context. LLMs are flexible in interpretation but need outputs to be reconciled with explicit task requirements. Prior clinical hybrids already use retrieval, schemas, rule guidance, validation, and review. The neuro-symbolic literature frames these variants by symbolic authority rather than by the mere presence of rules.

**Bridge:** This motivates evaluating a division of labour: model-produced, evidence-linked candidates followed by explicit task policy.

**Decision:** Do not introduce the five experimental configurations in detail here. The Introduction states the architectural question; Methods defines the comparison.

**Still to decide / source:** Cite prior hybrids carefully and do not claim novelty of hybridisation itself.

## Paragraph 4 - This study

**Reader question:** What exactly does this study contribute and test?

**Conclusion:** The study evaluates evidence-backed hybrid extraction across two public epilepsy-letter benchmarks that require different forms of structured representation.

**Context and content:** State the common architecture at a high level: models interpret and produce evidence-linked candidates; deterministic rules apply explicit task policy and record their transformations. Name the two tasks succinctly: Gan evaluates selection and rendering of a current seizure-frequency state; ExECT evaluates construction of a supported multi-family fact inventory. State that rules-only, model-only, and intermediate rule-assistance configurations are compared, with task-specific results kept separate.

**Closing contribution:** The paper examines not only final agreement with benchmark labels but also the role of rule assistance in producing constrained, evidence-linked, reviewable outputs.

**Still to decide / source:** Final wording of research questions and contribution sentence; ensure every claimed property has a corresponding measured result or is described as a design feature.

## Sequence check

1. Why narrative epilepsy information matters.
2. Why conversion to structure requires explicit choices.
3. Why the placement and authority of rules is the methodological issue.
4. What this study evaluates to address that issue.
