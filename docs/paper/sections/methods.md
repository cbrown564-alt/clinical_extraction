# Paper methods

Date: 2026-08-17
Revised: 2026-08-23 (cited five-cell table uses 4-family micro F1)
Status: current
Owner: this file

## Research questions

This study treats the route from a clinic letter to a submitted
task answer as three distinct stages: **candidate recognition**,
**task encoding**, and **final selection**. This is a study-specific
decomposition, not a replacement taxonomy for clinical NLP. It makes
explicit three decisions that are often folded together in an
end-to-end system: what evidence and candidate facts to collect, how
to write an already chosen fact in the task's required form, and what
the final answer should contain.

**Primary question.** When candidate recognition, task encoding, and
final selection are treated as distinct stages in clinical information
extraction, how should language models and recorded deterministic
rules be combined across those stages to produce structured epilepsy
information?

**Supporting questions.**

1. How do final results change when models and rules take different
   responsibilities for candidate recognition, task encoding, and
   final selection?
2. Does the preferred division of responsibility differ between one
   current seizure-frequency answer (Gan 2026) and a multi-fact
   clinical inventory (ExECTv2)?
3. When the later rule-based stages are held constant, how much do the
   final results depend on the model used for candidate recognition and
   on the reasoning budget given to that model?

The five role rows answer the first two questions. The six-model
cell-3 comparison, Gemini low/medium/high thinking, and the Gemini
and Grok temperature 0 versus 1 ablation answer the third. Saved outputs, evidence spans, and replayed rule stages are
the experimental controls that make the comparisons possible; they are
not a separate research question.

## A. Study design and task definitions

This study examines how a clinical information-extraction system
should divide work between language models and recorded deterministic
rules. Rather than treating extraction as one indivisible operation,
it distinguishes three stages in the route from a clinic letter to a
submitted structured answer: candidate recognition, task encoding, and
final selection. Candidate recognition identifies evidence-linked
clinical facts; task encoding expresses an already chosen fact in the
representation required by the task; and final selection determines
which candidate facts, if any, form the submitted answer. The study
compares alternative allocations of these stages between models and
rules.

The comparison is conducted on two public epilepsy-letter tasks
(Fonferko-Shadrach et al., 2024; Gan et al., 2026) that
require different final answers. Gan 2026 requires one label describing
the patient's current seizure frequency, despite a letter potentially
containing several true statements about different periods or seizure
types. ExECTv2 requires a structured inventory of supported diagnoses,
seizure-frequency facts, prescriptions, and investigations. The tasks
therefore test the same proposed division of work under different
output requirements: selecting one current state and assembling a
multi-fact clinical record. Their scores are reported separately
because they measure different target forms.

The study evaluates agreement with these task-specific reference
standards, not clinical correctness or deployment readiness. Locked
test results are reported only as aggregate totals, while development
data are used to examine mechanisms and limitations. The study does
not claim a universal extraction architecture, clinical validation, or
performance transfer between tasks.

## B. Datasets, gold forms, and split policy

| Characteristic | Gan 2026 | ExECTv2 |
| --- | --- | --- |
| Source material | Public synthetic epilepsy follow-up letters | Public clinician-written synthetic epilepsy clinic letters |
| Full resource | 1,500 letters | 200 letters |
| Task output | One current seizure-frequency label per letter | Multi-fact clinical inventory |
| Development split | 750 letters | 140 letters; 836 scored fact units |
| Locked test split | 450 letters | 59 available letters; 349 scored fact units |
| Main target content | Frequency, seizure-free, unknown, unresolved-multiple, or no-reference outcome | Diagnoses, seizure-frequency facts, prescriptions, and investigations |
| Scoring unit | One task label per letter | Micro-averaged fact units within four clinical families |

We evaluated the proposed division of model and rule responsibilities
on two publicly available synthetic epilepsy-letter resources. Gan 2026
comprises 1,500 follow-up letters constructed around a seizure-frequency
outcome. Its reference standard assigns each letter one label describing
the required current-frequency answer. ExECTv2 comprises 200
clinician-written synthetic clinic letters annotated as a structured
clinical inventory. Its reference standard records supported facts in
four families: diagnoses, seizure-frequency information, prescriptions,
and investigations (Fonferko-Shadrach et al., 2024; Gan et al., 2026).
The datasets therefore provide two deliberately
different forms of clinical extraction: one requires a single answer
from potentially competing statements in a letter, whereas the other
requires a set of supported facts.

The Gan development set contains 750 letters, with numeric frequency
labels most common (468 letters), alongside seizure-free (112),
unknown (100), unresolved-multiple (43), and no-reference (27)
outcomes. These non-numeric classes matter because the task is not
reducible to finding a rate expression: the system must distinguish an
answerable current state from uncertainty, competing evidence, or the
absence of a relevant reference. The ExECTv2 development set contains
836 scored inventory units across 140 letters: 329 diagnoses, 165
seizure-frequency facts, 206 prescriptions, and 136 investigations.
The Compact/headline collapse of Diagnosis is 796 units (289
diagnoses); that is a historical Compact denominator, not the
cited 4-family micro F1. A
single ExECTv2 letter may contain facts from several families, including
no annotated fact in a particular family; absence from a family is
therefore an annotation outcome, not evidence that the corresponding
clinical feature is false.

The two reference standards are retained in their original task-specific
forms rather than being forced into a common label space. Gan is scored
as one submitted label per letter, using the task's mapping of clinical
wording to its expected outcome. ExECTv2 is scored at the level of
inventory fact units (`clinical_inventory_unit_keys`), so its
denominator is the number of gold fact units rather than the number of
letters. De-duplication is a select step, not a scoring collapse. Development splits were
used to develop and inspect mechanisms, while the held-out splits were
kept locked for final aggregate evaluation. All five model--rule
configurations received the same parsed source text and the same split
assignments; there was no substantive corpus transformation before the
evaluated candidate-recognition, task-encoding, and final-selection
stages.

## C. Candidate recognition, task encoding, and final selection

Candidate recognition produces a candidate record of plausible clinical
facts from a clinic letter, each linked to supporting source text. For
Gan 2026, candidates may describe seizure events, seizure-free
intervals, uncertainty, or competing possible current states. For
ExECTv2, they may describe diagnoses, seizure-frequency facts,
prescriptions, and investigations. Candidate recognition is intentionally
broader than the final task answer: a letter can contain several
relevant facts even where Gan requires only one submitted label. Models,
rules, or their combination may perform this stage, but all
configurations preserve the candidate record and its evidence before
later processing.

Task encoding expresses an already retained candidate in the
representation required by the relevant reference standard. It may
standardise a count, period, medicine name, diagnosis form, codebook
label, or other task-specific field, while retaining the underlying
clinical fact and its evidence link. For example, it may convert a
frequency phrase into Gan's required label form or map an ExECTv2
medicine mention to its structured field representation. Encoding is
therefore distinct from candidate recognition: it does not search the
letter for an additional fact, and it is distinct from final selection:
it does not choose a different clinical state simply because its form
is easier to score.

Final selection determines which encoded candidates form the submitted
answer. For Gan 2026, this means choosing the one answer that represents
the required current seizure-frequency state when the letter contains
multiple temporally or clinically distinct statements. For ExECTv2, it
means retaining the supported, deduplicated facts that form the
four-family inventory. Recorded selection policies may gate, drop,
rewrite, or reselect a candidate where their conditions are met; they do
not silently add leftover facts from a new scan of the source letter.
The experimental stage boundaries are defined through replay on saved
candidate outputs, allowing the effect of each role in the configuration
to be scored separately.

```mermaid
flowchart LR
    letter[Clinic letter] --> recognise[Candidate recognition<br/>creates a candidate record]
    recognise --> encode[Task encoding]
    encode --> select[Final selection]
    select --> output[Structured task output]

    classDef stage fill:#dbeafe,stroke:#2563eb,color:#173b65,stroke-width:1.5px;
    class recognise,encode,select stage;
```

**Figure 1.** General staged pipeline for clinical information
extraction. Candidate recognition creates a record of plausible,
evidence-linked facts from a clinic letter. Task encoding expresses
those facts in the form required by the task, and final selection
determines the submitted structured output. The highlighted stages are
performed by a language model, recorded rules, or both, depending on
the configuration.

## D. Stage-ownership configurations

| Configuration | Candidate recognition | Task encoding | Final selection |
| --- | --- | --- | --- |
| 1. Rules throughout | Recorded rules | Recorded rules | Recorded rules |
| 2. Combined candidate recognition | Language model and recorded rules | Recorded rules | Recorded rules |
| 3. Model candidate recognition | Language model | Recorded rules | Recorded rules |
| 4. Model recognition and encoding | Language model | Language model | Recorded rules |
| 5. Model throughout | Language model | Language model | Language model |

The study evaluates the same five ways of dividing the work between a
language model and recorded rules on Gan 2026 and ExECTv2. In the
rules-throughout condition, recorded deterministic procedures construct,
encode, and select the submitted answer. The combined-recognition
condition permits both a model and rules to contribute candidate facts,
after which encoding and selection remain rule based. The remaining
conditions place candidate recognition, then task encoding, then final
selection with the model. The table therefore shows which role each
component plays in each configuration. A language-model stage is its
saved output; a recorded-rule stage is a deterministic transformation or
decision policy specified before held-out evaluation.

Gemini 3.7 Flash is the primary model for the five-configuration
comparison. The secondary model-configuration analyses hold the third
configuration fixed: model candidate recognition followed by rule-based
encoding and final selection, while varying either the model or the
reasoning budget used for candidate recognition.

The five configurations are comparisons of which component performs
each stage, rather than five depths of a single hybrid setting. Moving
from one row to another changes who may carry out a defined part of the
work; it does not simply add more rule assistance to a model answer.
Each configuration is evaluated against the task's own reference
standard, and final results are taken from the submitted answer after
final selection. The shared table therefore tests whether the preferred
way of dividing the work is stable across a single-label current-state
task and a multi-fact inventory task, while retaining task-specific
scores and gold forms.

## E. Development controls and reproducibility

All prompts, output schemas, recorded rules, and configuration choices
were developed using the designated development split for each task.
Development material was used to identify failure modes, refine the
candidate record, and specify task-encoding and final-selection
policies. The locked Gan 2026 and ExECTv2 test splits were reserved for
final evaluation: individual test letters and their outputs were not
inspected for development, and results are reported only as aggregate
totals. This separation means that the reported held-out scores assess
configurations fixed before test evaluation, rather than rules or
prompts tailored to particular held-out cases.

Each evaluated run retains the model-produced candidate record, its
evidence links, the subsequent rule transformations, and the final
submitted answer. Where a comparison changes task encoding or final
selection, the later stage is replayed from the same saved candidate
record rather than generated through a new model call. Consequently, a
difference between replayed conditions can be attributed to the changed
stage rather than variation in candidate generation. These retained
intermediate outputs also allow the submitted result to be reconstructed
and checked against the recorded policies.

The supporting material provides the full prompts, output schemas,
recorded-rule definitions, model settings, and replay artefacts. These
details are retained to allow implementation review without obscuring
the controlled comparisons in the main Methods section.

## F. Evaluation protocol

Evaluation was defined separately for the two task forms. The primary
reported measures are Purist accuracy for Gan 2026 and 4-family
micro F1 for ExECTv2. These are the measures used for the
headline configuration comparisons because they match the submitted
object required by each task. Additional task-specific measures are
reported to make the headline scores interpretable: Pragmatic accuracy
for Gan 2026, and precision and recall for ExECTv2. Scores are not
pooled or directly compared between tasks.

Gan 2026 requires one submitted seizure-frequency outcome for each
letter. We therefore report both Purist and Pragmatic accuracy,
following the two task-defined projections used in the prior Gan work.
Purist is the primary, finer-grained evaluation: it maps the submitted
label to a monthly-frequency band while retaining the task's
seizure-free and uncertainty outcomes. Pragmatic is a coarser companion
projection. Set-based precision, recall, and F1 are not reported for
Gan because each letter contributes one target answer rather than a set
of independently countable clinical facts (Gan et al., 2026).

For ExECTv2, the primary measure is 4-family micro F1 across
diagnoses, seizure-frequency facts, prescriptions, and investigations.
The four families were selected as a focused evaluation scope: each
represents clinically central information for epilepsy follow-up and
has sufficient annotation support for comparative evaluation. Four
other annotated families: birth history, epilepsy cause, onset, and
when diagnosed each contain fewer than 50 gold annotations and are
therefore too sparse to support a stable headline comparison. Patient
history was also excluded from this headline scope. Although clinically
useful, it combines heterogeneous comorbidities, generic seizure
mentions, and epilepsy-related events; the original annotation work
identified uncertainty at its boundaries with diagnosis and seizure
frequency, and treated meaningful validation as subgroup-specific. This
scope is not a claim that omitted information is clinically unimportant
(Fonferko-Shadrach, 2023; Fonferko-Shadrach et al., 2024).

ExECTv2 scoring treats the submitted output as a structured clinical-fact
inventory rather than as a count of textual mentions. Diagnosis and
seizure-frequency repeats are deduplicated within a letter, while
prescription and investigation facts retain distinct occurrences after
task-specific key filtering. F1 is the principal summary of this balance
between recovered and unsupported facts. Precision and recall are
additionally reported overall and by family where needed to show whether
a configuration primarily introduces unsupported facts, misses supported
facts, or changes that balance differently across clinical families.
This is an internal research measure, not a replication of the published
strict ExECT benchmark (Fonferko-Shadrach et al., 2024). The five
configurations are compared within each
task; model and reasoning-budget analyses use the fixed
model-candidate-recognition, rules-encoding, rules-selection condition,
and locked-test results are reported only as aggregates.

## Supporting implementation material

The task-specific implementation map is retained in
[five cells of rule help](method_x_stage.md). The detailed recorded-rule
catalogue, model roster, prompt decisions, and experiment scope remain
available in the linked paper documentation. They support reproducibility
and audit, but are not part of the main-paper Methods narrative.
