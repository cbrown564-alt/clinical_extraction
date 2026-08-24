# Related-work source map

Date: 2026-08-17
Revised: 2026-08-17 (upgraded from the retired-manuscript seed list)
Status: paper source; citation and local-file map. Not a literature
review and not a novelty claim.

## The short answer

Use this map to find a paper, its local copy, and the `paper/` brief
that may cite it. Write related work from the briefs, not from this
list.

| Brief | Job |
| --- | --- |
| [Why narrative letters are a research problem](why_narrative_letters_are_a_research_problem_2026-08-17.md) | Opening motivation |
| [What the two golds already decided](what_the_two_golds_already_decided_2026-08-17.md) | Why the golds are different objects |
| [What prior extraction approaches already did](what_prior_extraction_approaches_already_did_2026-08-17.md) | Related work by problem shape and method |
| [Why evidence, uncertainty, and human review belong together](why_evidence_uncertainty_and_human_review_belong_together_2026-08-09.md) | Reviewability requirements and evidence-strength distinctions |
| [Why the proposed method is a model plus recorded rules](why_hybrid_architecture_2026-08-09.md) | Project-lane response to the literature gap; not a novelty source |

Diagnostic owners that stay out of the main writing path:

- [annotation comparison](../shared/annotation_approach_comparison_2026-08-16.md)
- [IAA theme scan](../shared/annotation_iaa_literature_theme_2026-08-16.md)
- [IAA convention review](../shared/annotation_convention_iaa_literature_review_2026-08-16.md)

Planning reviews, not writing sources:

- `docs/literature/literature_review.pdf` (7 June 2026)
- `docs/literature/llm_reliability_literature_review.pdf` (10 June 2026)
- `literature/hybrid_seizure_phenotype_literature_review.pdf` (31 May 2026)
- `literature/gan2026_critical_analysis_pathways_forward.pdf`

## Epilepsy extraction and golds

| Citation | Local copy | Used by |
| --- | --- | --- |
| Fonferko-Shadrach B, Lacey AS, Roberts A, et al. Using natural language processing to extract structured epilepsy data from unstructured clinic letters: development and validation of the ExECT (extraction of epilepsy clinical text) system. *BMJ Open*. 2019;9:e023232. | `literature/Epilepsy Extraction/Rules-Based/ExECT.pdf` | letters; prior approaches |
| Fonferko-Shadrach B. PhD thesis. Swansea University; 2023. Especially Abstract, Ch. 1, 2.2, 3, 8.1–8.2. | `literature/Epilepsy Extraction/Rules-Based/2023_Fonferko-Shadrach_B.final.65061.pdf` | letters; golds |
| Fonferko-Shadrach B, et al. Annotation of epilepsy clinic letters for natural language processing. *J Biomed Semantics*. 2024;15:17. | `data/ExECTv2 (2025)/Annotation of Epilepsy Clinic Letters for NLP (Fonferko-Shadrach 2024).pdf` | letters; golds; prior approaches |
| *ExECT V2.1 — What and How of annotating with Markup*. v9. 09.09.2023. | `data/ExECTv2 (2025)/ExECT V2 .1- What and How of annotating_v9.docx`; extract: [v9](../exectv2/annotation_guidelines_v9_extracted.md) | golds |
| Xie K, Gallagher RS, Conrad EC, et al. Extracting seizure frequency from epilepsy clinic notes: a machine reading approach to natural language processing. *JAMIA*. 2022;29:873–881. | `literature/Epilepsy Extraction/LLMs/BERT/Extracting seizure frequency from epilepsy clinic notes - a machine reading approach to natural language processing.pdf` | prior approaches; golds (via annotation comparison) |
| Xie K, Gallagher RS, Shinohara RT, et al. Long-term epilepsy outcome dynamics revealed by natural language processing of clinic notes. *Epilepsia*. 2023;64:1900–1909. | `literature/Epilepsy Extraction/Rules-Based/Long term epilepsy outcome dynamics revealed by natural language processing of clinic notes.pdf` | prior approaches |
| Decker BM, Turco A, Xu J, et al. Development of a natural language processing algorithm to extract seizure types and frequencies from the electronic health record. *Seizure*. 2022;101:48–51. | `literature/Epilepsy Extraction/Rules-Based/Development of a natural language processing algorithm to extract seizure .pdf` | prior approaches |
| Holgate B, Davies J, Fang S, Winston JS, Teo JT, Richardson MP. Fine-tuning LLMs to extract epilepsy seizure frequency data from health records. In: *BioNLP*; 2025:44–55. | `literature/Other Clinical Extraction/Fine-tuning LLMs to Extract Epilepsy Seizure Frequency Data from Health Records.pdf` | prior approaches |
| Fang B, Akbari A, Pickrell WO, et al. Extracting epilepsy-related information from unstructured clinic letters using large language models. *Epilepsia*. 2025. | `literature/Epilepsy Extraction/LLMs/GPT/Extracting epilepsy-related information from unstructured clinic letters using LLMS.pdf` | paper keep-set (b13); prior approaches |
| Abeysinghe R, Tao S, Lhatoo SD, Zhang G-Q, Cui L. Leveraging pretrained language models for seizure frequency extraction from epilepsy evaluation reports. *npj Digit Med*. 2025. | `literature/Epilepsy Extraction/LLMs/GPT/Leveraging pretrained language models for seizure frequency extraction from epilepsy evaluation reports.pdf` | prior approaches |
| Gan Y, Barlow SH, Holgate B, Davies J, Teo JT, Winston JS, Richardson MP. Reproducible synthetic clinical letters for seizure frequency information extraction. arXiv:2603.11407. 2026. | `data/Gan (2026)/Synthetic Clinical Letters for Seizure Frequency.pdf` | letters; golds; prior approaches |

## Method lessons outside epilepsy

| Citation | Local copy | Used by |
| --- | --- | --- |
| Liu S, McCoy AB, Chen Q, Wright A. Integrating rule-based NLP and large language models for statin information extraction from clinical notes. *Int J Med Inform*. 2026;205:106104. | `literature/Other Clinical Extraction/Integrating rule-based NLP and large language models for statin information extraction from clinical notes.pdf` | prior approaches (method lesson only) |
| Dao N, Quesada L, Hassan SM, et al. Generative artificial intelligence for automated data extraction from unstructured medical text. *JAMIA Open*. 2025;8:ooaf097. | `literature/Other Clinical Extraction/Generative artificial intelligence for automated data extraction from unstructured medical text.pdf` | prior approaches (method lesson only) |

## Reviewability guidelines

These are owned by
[why evidence, uncertainty, and human review belong together](why_evidence_uncertainty_and_human_review_belong_together_2026-08-09.md).
They are not epilepsy-extraction comparators.

## What this source is for

Look up a citation. Do not paste the tables as related work. Do not
treat coverage of this map as a completed review or a novelty
argument.

## Writing test

**Question:** can the author find the local PDF for ExECT 2019, Xie
2022, Holgate 2025, Abeysinghe 2025, and Gan 2026, and name the brief
that is allowed to use each one?

**Success:** those five rows resolve here, and the map still refuses to
be the related-work section.
