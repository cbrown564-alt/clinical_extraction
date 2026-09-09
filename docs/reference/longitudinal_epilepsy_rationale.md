# Longitudinal epilepsy extraction: literature rationale

Date: 2026-09-09. Status: focused Phase 1 research, not a systematic review.
Owner: this document for the literature comparison; the
[task definition](../longitudinal/task_definition.md) owns project decisions.

## Conclusion

Longitudinal epilepsy analysis, clinical temporal annotation and question answering
over patient histories already exist. The research question here is narrower:
whether explicit links between assertions in successive letters improve cohort
answers while preserving both the account available at a cutoff and subsequent
reinterpretation of that account. That benefit remains a hypothesis.

Do not claim the first longitudinal epilepsy application, the first temporal
clinical benchmark, or superior annotation. The comparison below identifies
relevant precedents and differences in evaluated outputs, not proof of novelty.

## Search and version checks

On 2026-09-09, searched by the named authors/titles in P1.1 and by longitudinal
clinical benchmark, temporal annotation, clinical summarization and seizure outcome
extraction. Checked publisher, ACL, arXiv, author-repository and dataset-record
pages. Local manuscript references were discovery aids, not publication authority.
No source corpus or locked benchmark examples were inspected for this review.

This is a targeted comparison, not exhaustive screening. Publication details below
are the versions verified on this date. No later journal version of Gan was found
in this search; that is not evidence that none exists. Some publisher full-text
requests failed, so the table states where only metadata/abstracts were available.

The local PDF named `Longitudinal seizure outcome extraction from epilepsy clinic
notes.pdf` actually opens with the title and DOI of Xie 2023 below. Its filename
must not become a separate bibliography entry.

## Prior work and implications

| Work and verified version | Evaluated object / evidence | Implication for this project |
| --- | --- | --- |
| Fonferko-Shadrach et al., **Using natural language processing to extract structured epilepsy data from unstructured clinic letters: development and validation of the ExECT system**, BMJ Open 9:e023232 (2019), [DOI](https://doi.org/10.1136/bmjopen-2018-023232). Publisher abstract and PubMed metadata checked. | Structured epilepsy information extracted from clinic letters using GATE-based NLP. | A domain extraction predecessor. Letter-level extraction does not by itself establish accuracy of cross-letter corrections or cohort membership at a cutoff. |
| Xie et al., **Extracting seizure frequency from epilepsy clinic notes: a machine reading approach to natural language processing**, JAMIA 29(5):873–881 (2022), [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC9006692/), DOI 10.1093/jamia/ocac018. | Annotated 1,000 notes/paragraphs for recent seizures, frequency and most recent seizure; classification and extracted-span evaluation. Notes temporal reasoning, copied text and combining seizure types as limitations. | Keep seizure identity, observation windows and missing answers explicit. Its recent-seizure definition is a study choice, not a universal window to inherit. |
| Xie, Litt, Roth and Ellis, **Quantifying Clinical Outcome Measures in Patients with Epilepsy Using the Electronic Health Record**, BioNLP 2022:369–375, [ACL version](https://aclanthology.org/2022.bionlp-1.36/), DOI 10.18653/v1/2022.bionlp-1.36. | Turns extracted seizure outcome descriptions into quantitative measures. | Normalization is a distinct component from locating the evidence; correct spans alone do not prove a correct longitudinal answer. |
| Xie et al., **Long-term epilepsy outcome dynamics revealed by natural language processing of clinic notes**, Epilepsia 64:1900–1909 (2023), [publisher](https://doi.org/10.1111/epi.17633), [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC10523917/). | Applied outcome extraction to 55,630 notes from 9,510 patients and analysed trajectories. Clinical notes are not publicly released. | Direct precedent for longitudinal epilepsy research. This project's proposed comparison concerns explicit assertion links and two evidence cutoffs, not the existence of longitudinal analysis. |
| Fonferko-Shadrach et al., **Annotation of epilepsy clinic letters for natural language processing**, Journal of Biomedical Semantics 15:17, version of record 15 September 2024, [publisher](https://doi.org/10.1186/s13326-024-00316-z). | 200 synthetic letters, double annotation and consensus reference, plus ExECTv2 evaluation. | Reuse lessons about annotation disagreement and family-specific facts. Existing annotations do not automatically become reference answers for new patient histories. |
| Gan et al., **Reproducible Synthetic Clinical Letters for Seizure Frequency Information Extraction**, [arXiv:2603.11407v1](https://arxiv.org/abs/2603.11407v1), 12 March 2026, [methods](https://arxiv.org/html/2603.11407v1). | Synthetic letter supervision, structured frequency labels and evidence, evaluated for single-visit frequency extraction; generation uses a small base-letter set and agreement filtering. | Preserve ranges and cluster structure, but do not inherit its single-label scoring or teacher-agreement acceptance rule. Distinct generated letters need not be independent source families. |
| Styler et al., **Temporal Annotation in the Clinical Domain**, TACL 2:143–154 (2014), [paper](https://aclanthology.org/Q14-1012/). | THYME annotates clinical events, times and temporal relations, distinguishing linguistic support from inferred ordering. | Temporal relations and partial dates are established annotation concerns. Use only the subset required by cohort questions; do not claim temporal annotation itself as new. |
| Adams et al., **LongHealth: A Question Answering Benchmark with Long Clinical Documents**, Journal of Healthcare Informatics Research 9:280–296, 14 June 2025, [journal version](https://doi.org/10.1007/s41666-025-00204-w); supersedes citing only the [2024 preprint](https://arxiv.org/abs/2401.14490). | 20 fictional cases and 400 multiple-choice questions covering retrieval, negation and sorting; the journal version updates the model evaluation. | Include missing-information cases. Long context and multiple documents are already benchmarked; the proposed output is structured cohort membership with evidence and revision history. |
| Cui et al., **TIMER: temporal instruction modeling and evaluation for longitudinal clinical records**, npj Digital Medicine 8:577 (2025), [journal DOI](https://doi.org/10.1038/s41746-025-01965-9), [PubMed](https://pubmed.ncbi.nlm.nih.gov/41006898/), [preprint methods](https://arxiv.org/html/2503.04176v1). | Timestamp-linked instructions and evaluation over longitudinal EHRs. Journal metadata and indexed methods checked; direct journal rendering was unavailable. | Explicit temporal grounding is a comparator idea, not a novelty claim. Availability of its code does not confer access to Stanford source records. |
| Kruse et al., **Large Language Models with Temporal Reasoning for Longitudinal Clinical Summarization and Prediction**, Findings of EMNLP 2025:20715–20735, [ACL](https://aclanthology.org/2025.findings-emnlp.1128/), DOI 10.18653/v1/2025.findings-emnlp.1128. | Publisher abstract describes long clinical summarization and prediction tasks, including RAG comparisons. | Include a whole-history comparator rather than assuming explicit links beat long context. Prediction remains outside this project's first release. |
| Chen et al., **LongMedBench: Benchmarking Medical Agents for Long-Horizon Clinical Decision-Making**, [arXiv:2607.09322](https://arxiv.org/abs/2607.09322), July 2026 preprint; abstract/record checked. | Describes fact QA, temporal reasoning and long-horizon decisions over MIMIC-IV-derived event streams. | Recent adjacent benchmark to revisit before a publication claim. Different clinical setting and outputs mean its scores cannot be compared directly with this task. |

These sources support design choices, not a performance ranking. Different data,
units, annotation policies and metrics prevent a league table of their scores.
In particular, do not equate human agreement with model accuracy against consensus.

### Chang reference resolved

Conor supplied the PDF of Ellie Chang et al., **Automated epilepsy and seizure
type phenotyping with pre-trained language models**, medRxiv version 1, posted
22 February 2026, DOI [10.64898/2026.02.11.26346003](https://doi.org/10.64898/2026.02.11.26346003).
The supplied full text and [indexed record](https://pmc.ncbi.nlm.nih.gov/articles/PMC12934892/)
match. The targeted publication check on 2026-09-09 found the preprint; no journal
version was established. This is the intended Chang reference, not Ojemann et al.

The methods distinguish single-label epilepsy type from multi-label fine-grained
seizure types. Three neurologists annotated 309 notes, with two independent labels
per note and consensus adjudication. The selected DeepSeek-R1-Distill-Llama-8B
model was applied to 77,049 notes from 18,566 patients. Patient epilepsy phenotypes
were aggregated by majority category across visits, followed by the most specific
subtype within that category. A continuous-time hidden Markov model analysed
visit-level diagnostic transitions, accommodating irregular follow-up.

This is a direct longitudinal phenotyping precedent, including diagnostic change
and co-occurring seizure types. However, the described reference evaluation is
note classification; it does not establish accuracy of evidence-linked corrections
under paired availability cutoffs. Majority aggregation is a useful diagnostic
comparator, not a reference rule for deciding which conflicting assertion is true.

The authors explicitly acknowledge possible optimism from iterative DeepSeek
prompt refinement on the full labelled dataset and the need for independent
held-out evaluation. Our prompt development must stay in development cases.
The study's patient data do not become available for seeding because its preprint
is open access. P1.1's named-reference gap is now resolved.

## Source-use findings

| Material | Verified evidence | Decision / remaining check |
| --- | --- | --- |
| ExECT synthetic letter release | [Zenodo 8381080](https://zenodo.org/records/8381080), version 1, 26 September 2023, lists 200 letters and CC BY 4.0. | Candidate seeds must still be in local `dev140`. Preserve attribution, release ID and changed-from-source lineage. Verify the local copy against the release before generation. |
| ExECT JSON annotations | [Zenodo 8356494](https://zenodo.org/records/8356494), v1, 11 January 2024, identifies a separate annotation release. | Do not assume the article's licence settles every annotation/ontology component. The new task needs fresh references, not copied benchmark gold. |
| Gan local 1,500-letter subset | The paper describes the generation method and a larger corpus. No matching public dataset release/licence for this local subset was established from the checked paper or repository documentation. | `dev750` is the only candidate pool; source-conditioned generation/sharing awaits provenance and terms for the actual subset. Authored seed-free cases can proceed. |
| Xie clinical notes, Stanford records, MIMIC-derived benchmarks | Publication access is distinct from source-data access. | Literature comparators only in this phase. No downloading clinical corpora or transplanting their permissions. |

This is a source-record audit, not a legal opinion or a public-release approval.
No original letters, annotation files or local literature PDFs are copied into
these tracked documents.

## Design decisions supported by the comparison

1. Compare linked histories against both independent letter extraction plus
   simple aggregation and a whole-history model with the same allowed evidence.
2. Score cohort answers directly. Use extraction, normalization and link errors to
   explain results rather than treating their scores as downstream utility.
3. Keep assertions and later interpretations separately attributable; document
   availability determines what can be known at a cutoff.
4. Preserve indeterminate answers, partial times and unresolved disagreements.
   Text-supported reference and hidden scenario truth must remain separate.
5. Treat seed lineage, style and outcome as separate factors. A synthetic sample
   of 300 patients cannot justify a population prevalence or clinical-use claim.

These are project inferences. Their executable definitions and revision conditions
are in the task definition; expert review and empirical benefit are still absent.
