# Introduction working outline

Status: decision record and paragraph outline for `introduction_draft.md`, not manuscript prose. It records the agreed narrative and claim boundaries so later edits do not reopen settled choices without evidence.

## Central argument

Epilepsy research needs structured information that captures both a broad clinical phenotype and seizure burden or current control. Clinic letters contain this information in temporally distributed, uncertain, and sometimes overlapping statements. The study separates the conversion into three decisions—finding candidate statements, translating them into the required structured form, and deciding what enters the final record—then asks how learned interpretation and written task rules should share those decisions.

## Scope and claim boundaries

- The paper evaluates structured-extraction methods, not a deployed clinical decision-support system.
- A broad phenotype and current seizure frequency are complementary research targets. Neither is a complete patient record.
- Seizure frequency is a core clinical outcome measure, not the only or universally most important marker.
- Describe ExECT as rules-led and note its statistical components.
- Hybrid epilepsy NLP already exists. The contribution is the explicit three-decision comparison across two task forms, not the invention of hybrid extraction.
- Written rules may change clinically consequential choices, including time windows, categories, normalised values, and the selected fact. Do not describe them as formatting alone.
- Learned methods appear well suited to interpreting variable seizure-frequency language, but studies with different datasets and targets do not establish universal superiority.
- Quoted evidence and transformation records support review and replay. They do not prove clinical correctness or expose hidden model reasoning.
- The two public datasets enable independent re-evaluation and reduce dependence on private corpora. They do not isolate institutional transfer because source, task, and annotation policy differ together.
- Keep task scores separate and do not state this study's results in the Introduction.

## Paragraph 1 — Clinical motivation

**Reader question:** Why does structuring epilepsy letters matter?

**Conclusion:** Narrative clinic letters contain clinically useful epilepsy information that structured extraction can make available for cohort construction, retrospective review, and longitudinal outcome research.

**Content:** Name diagnoses, seizure types and frequencies, medicines, investigations, and treatment changes. State that manual review is difficult to scale. Bound the paper as a methods study rather than clinical deployment or replacement of clinical judgement.

**Source anchors:** Fonferko-Shadrach et al. (2019); Xie et al. (2023).

## Paragraph 2 — Complementary clinical targets and three decisions

**Reader question:** What must a useful research record capture, and why is extraction difficult?

**Conclusion:** Epilepsy research benefits from both broad phenotype information and seizure-burden or current-control information, while narrative letters may support several temporally or contextually different statements.

**Content:** Call seizure frequency a core clinical outcome measure. Explain the three decisions in plain language: find candidate statements, translate them into the required structured form, and decide what enters the final record. Introduce ExECT as the multi-fact inventory task and Gan as the current-frequency task. Present them as complementary research forms, not arbitrary output examples or complete patient records.

**Source anchors:** Decker et al. (2022); Fonferko-Shadrach et al. (2024); Gan et al. (2026).

## Paragraph 3 — Design question

**Reader question:** Why compare written rules, learned methods, and their combinations?

**Conclusion:** The central question is which component should make each clinically consequential decision.

**Content:** Rules are explicit and inspectable but depend on local wording. Learned models handle varied and temporally distributed narrative but are harder to constrain and inspect. Hybrids already exist. Ask how learned interpretation and written task rules should work together across finding, translating, and final choice. Do not introduce detailed experimental cells here.

**Source anchors:** Yew et al. (2023), with epilepsy-specific hybrid detail reserved for the literature review.

## Paragraph 4 — Study and contribution

**Reader question:** What does this study evaluate?

**Conclusion:** The study compares alternative divisions of work at the three decisions on two public epilepsy-letter datasets with different sources and target forms.

**Content:** State that the system retains quoted evidence and transformation records. Explain that public data allow independent replication or re-evaluation. State the transfer boundary: the design addresses private single-site evaluation but cannot isolate institutional transfer because source, task definition, and annotation policy change together. Do not report findings or imply that one division of work must suit both tasks.

**Source anchors:** Fonferko-Shadrach et al. (2024); Gan et al. (2026).

## Sequence check

1. Narrative epilepsy information motivates structured extraction.
2. Complementary phenotype and seizure-burden targets expose three decisions.
3. Rules, learned methods, and existing hybrids motivate the division-of-work question.
4. Two public tasks provide the study design, reproducibility contribution, and transfer boundary.
