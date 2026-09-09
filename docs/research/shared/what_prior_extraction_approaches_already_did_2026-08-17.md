# What prior extraction approaches already did

Date: 2026-08-17
Revised: 2026-08-19 (open question restated as source span plus named mappings)
Status: literature-grounded paper source; related-work brief. Not a
novelty claim and not a systematic review.

## The short answer

Prior work already extracts epilepsy facts from clinic letters. It
does so under one of two problem shapes, and with one of three method
classes.

- **Inventory.** Recover a coded set of mentions and attributes.
- **Selection.** Commit to a current frequency, freedom, or last-event
  state.

The method classes are rules, learned or prompted models, and hybrids
that use both. What the literature leaves open is not “whether an
extractor can score.” It is whether a method keeps a source span and a
named record of later shaping into a designed form. Prior work rarely reports
which evidence was used, which later operation changed clinical meaning,
and how the submitted object became the reported score.

This brief locates those approaches. It does not claim that this
project's architecture is novel or state of the art.

## Inventory by rules

ExECT 2019 is the deterministic inventory lineage. A GATE system
combined rules and statistical components to extract nine epilepsy
categories from Welsh clinic letters and compared them with clinician
review (Fonferko-Shadrach et al. 2019). The later annotation paper and
thesis made the gold look like that pipeline so validation could be
automatic (see
[what the two golds already decided](what_the_two_golds_already_decided_2026-08-17.md)).

Decker et al. 2022 applied rules to seizure type and frequency in the
EHR. The short paper is a warning about single-site rule systems: the
local hybrid review records poor external generalisation as the lesson
to keep.

## Selection by classification, spans, or fine-tuning

Xie et al. 2022 treated seizure frequency, seizure freedom, and date
of last seizure as a machine-reading task: find the answer in the
note, not only the entity. Classification IAA was high; overall span
F1 was much lower. The one-year window for a “recent seizure” is
named as pragmatic and, from a machine-learning perspective,
arbitrary. Later papers convert those strings to numbers for
longitudinal outcome work and say human agreement with the merged gold
is inflated (Xie et al. 2023).

Holgate et al. 2025 and Fang et al. 2025 take the coarse-category
path. Frequency becomes a closed set of bands, or a seizures-per-month
number, so a fine-tuned model can be scored. High annotator kappa and
an admission that purist band edges are arbitrary can coexist. The
scheme is stable because it is coarse, not because the clinical
question is settled.

Abeysinghe et al. 2025 extract frequency phrases and attributes from
epilepsy evaluation reports with pretrained and generative models.
Normalising frequency remains a live problem after the model call.

## Synthetic labels and prompted models

Gan et al. 2026 respond to privacy, scale, and representation at once.
Humans label a closed frequency dialect; letters are generated around
those labels; open-weight models are trained without sharing patient
text; evaluation includes real letters. Structured labels keep range,
cluster, duration, and unknown. The paper is a dataset-and-supervision
argument, not a hybrid-architecture argument.

Zero-shot and other prompted extractors in the local tree reuse
Xie-style outcome definitions. They show that a model can read a
letter. They do not show where a later formatting or selection step
changed the clinical answer.

## Hybrids outside epilepsy, as a method lesson only

Clinical IE already combines rules and models when the notes are
large and the target is narrow. Liu et al. 2025 filter statin-barrier
notes with rules, then use an LLM to refine and classify. Dao et al.
2025 add schema instructions and a retry loop to keep a generative
extractor inside a predefined field list.

Those papers teach a division of labour: rules constrain; the model
reads. They do not study epilepsy selection versus inventory, and they
are not comparators for this project's scores.

## What they leave open

Across these papers, the scored object is usually a final label, span,
or category. The literature rarely reports evidence choice, clinical
representation, winner or inventory policy, semantic post-processing,
and score projection as separately attributable stages. When conversion
happens — categories to a monthly number, hedges to a band, missing dose
to a default — it is often unpublished, prompted, or folded into the
model or evaluator.

Evidence spans appear in some recent work, including Gan. Exact
quoted evidence does not by itself prove that the right statement was
chosen. Attribution of a later clinical change to a deterministic
stage is not the evaluation object in the papers above.

The June narrative reviews in `docs/literature/` and
`literature/hybrid_seizure_phenotype_literature_review.pdf` already
argue for a hybrid framing. They are planning reviews, not evidence
that this implementation is the method those reviews imagined.

## What this permits the paper to say

| Supported interpretation | Unsupported extension |
| --- | --- |
| Prior work already covers inventory-by-rules and selection-by-model on epilepsy letters. | This architecture is the first hybrid, or the state of the art. |
| Frequency work keeps collapsing a story into a band, a number, or a span. | Those papers failed and this system succeeds. |
| Some non-epilepsy IE systems already split rules and models. | Those systems are the same experiment as Gan and ExECT. |
| The proposed method's source span and named rule changes are not usually reported as separately attributable stages. | The literature has never used evidence, intermediate representations, or deterministic post-processing. |

This source belongs to the literature lane. Project scores, stage
replays, and component harms stay with the task stories and
[paper claim status](../../canon/10_paper_provenance.md).

The project-lane account of the proposed method is
[why the proposed method is a model plus recorded rules](why_hybrid_architecture_2026-08-09.md).

## Sources

Local paths and the remaining bibliography are on the
[citation map](related_work_seed_2026-08-17.md). The epilepsy papers
used here are ExECT 2019 and 2024, Decker 2022, Xie 2022 and 2023,
Holgate 2025, Fang 2025, Abeysinghe 2025, and Gan 2026. The method
lessons are Liu 2025 and Dao 2025.

## Writing test

**Question:** can the author write related work as “prior work solved X
with Y and left Z open,” organised by inventory versus selection,
without a score table or a novelty sentence?

**Success:** ExECT, Xie/Holgate/Fang, and Gan are each one move; the
open issue is whether a method keeps a source span and named later
mappings; this project's results are not used as evidence.
