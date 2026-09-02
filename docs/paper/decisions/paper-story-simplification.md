# Paper-story simplification

Date: 2026-09-02
Status: current
Owner: [paper keep-set](../README.md)
Related: [Gan is the dissertation paper](gan-is-the-dissertation-paper.md),
[holdout is aggregate-only](holdout-is-aggregate-only.md),
[Gemini is the cited model](gemini-is-the-cited-model.md)
Results outline: [results](../sections/results.md)
Evidence protocol:
[directional adjudication on `dev750`](../../research/gan2026/gan_directional_evidence_adjudication_dev750_protocol_2026-09-02.md)
Implemented 2026-09-02 in `paper/draft/FES.tex`,
`paper/supporting materials/Supporting materials.tex`,
[results](../sections/results.md), [methods](../sections/methods.md),
[introduction](../sections/introduction.md),
[literature review](../sections/literature_review.md), and the
[paper keep-set](../README.md). Adjudication under Decision 2 has not
started.

This is a paper-scope and writing decision. Existing reports and
machine-readable artifacts remain the owners of exact results. Gan 2026
and ExECTv2 keep their separate task, split, scorer, and claim
boundaries. This file does not authorize retuning, new headline
benchmark runs, holdout row inspection, or relabelling historical
outputs.

## Decision 1 — claim hierarchy and two decision executors

Keep comparison with the previously reported fine-tuned benchmark as the
primary paper claim, and state clearly that the held-out samples are not
identical. Use extract-then-decide as the explanation of system
behaviour and as the secondary contribution.

Remove the end-to-end Rules-only configuration from the dissertation
paper and supporting materials. Keep those repository experiments
unchanged as research history. Removal from the paper is not deletion
or reinterpretation of those experiments.

The paper's core method comparison is one shared LLM extraction record
with two decision executors:

1. deterministic rules (the Hybrid executor); and
2. a second LLM call (the LLM-only executor).

The shared record holds the extracted candidates and intermediate
evidence needed by either executor. The older three-configuration /
Find–Encode–Select account mixed stage ownership, representation
changes, and final decision ownership, so it is historical terminology
unless a stage name is needed to identify an existing artifact.

The paper may make a matched, bounded comparison to the previously
reported fine-tuned benchmark. It must disclose the non-identical
held-out samples and must not imply a paired comparison, a
state-of-the-art result, or a clinical deployment result.

## Decision 2 — extraction measurement

Retain the existing provisional-answer and final scores. Add a
development-first directional evidence analysis before any
aggregate-only holdout replay.

The annotation reference text is a loose comparator, not ground truth
for evidence-span correctness. A reference may be exact, paraphrased,
abbreviated, ellipsized, or missing. Measure two separate properties:

- **reference exactness:** whether the reference can be located as an
  exact source substring (with the existing normalization policy used
  only as a diagnostic);
- **reference semantic sufficiency:** whether the reference conveys
  enough meaning to support the target label, even when it is not an
  exact substring.

For pipeline records, measure:

- **source exactness:** whether the collected spans occur in the source
  letter;
- **adjudicated semantic evidence sufficiency:** whether all raw grouped
  spans, considered together, support the target label under the
  already-defined decision policy.

The pipeline adjudicator receives only the target label, raw grouped
spans, and the decision policy. It must not receive the full letter,
normalized labels, the predicted answer, or the annotation reference.
It returns `supported`, `unsupported`, or `insufficient`, a concise
reason, and controlled policy-operation tags.

A development pilot and an explicit acceptance decision must precede
any aggregate-only holdout replay. The pilot is a directional
measurement and protocol check. It is not clinical validation and not
permission to inspect or tune locked rows.

Operational owner:
[protocol](../../research/gan2026/gan_directional_evidence_adjudication_dev750_protocol_2026-09-02.md),
[prompt](../../research/gan2026/gan_directional_evidence_adjudication_prompt_2026-09-02.json),
[rendered example](../../research/gan2026/gan_directional_evidence_adjudication_rendered_example_2026-09-02.md).
Adjudication has not started.

## Decision 3 — main-paper mechanism evidence

Retain a compact ablation table using the full codebook prompt and
exactly three focused variants:

1. **No examples:** remove examples while retaining the rest of the
   codebook request.
2. **No closed allowed-label forms:** remove the closed allowed-label
   forms while retaining examples.
3. **Evidence obligation:** remove the evidence fields and the
   exact-quote instruction as one bundled package.

The third variant is **evidence obligation**, not quote-only. The table
must show provisional-answer F1 and final F1. State that the effects
are not additive.

Keep source-near, Holgate structured/one-label, and extra-LLM
encode/select experiments explicitly secondary. Summarize why each
exists and retain its evidence; do not delete it or promote it into the
main comparison.

The draft results outline applies this cut in
[results section D](../sections/results.md). Exact values stay on the
ablation owners; do not invent numbers here.

## Decision 4 — architecture terminology and presentation

Do not call the LLM calls agents, and do not call the system agentic
or multi-agent. The system is a fixed sequential pipeline with no
iterative reasoning, autonomous tool selection, or LLM orchestration.
Use **LLM call**.

The two paper stages are **extract** and **decide**. The extraction
call reads the full letter and produces a multi-event candidate record
containing exact evidence spans, normalized representations, and a
provisional answer. The optional second LLM decision call receives that
record, not the letter, and applies the same policy. In Hybrid,
deterministic rules perform the decision role.

The paper should include a concise interface-contract figure:

```text
letter → LLM extraction → shared candidate record
       → rule decide OR second LLM decide → final answer
```

Show the interface contract and decision ownership in the main paper.
Full prompts and schemas belong in supporting material. Methods should
name the prompt ingredients—instructions, examples, allowed labels, and
the evidence obligation—so the later ablations follow naturally.

## Decision 5 — remaining result threads

The main paper keeps the two-executor comparison, the compact
extraction-prompt ablations, the six-model comparison, compact schema
and exact-evidence adherence alongside it, a concise hardware/software
environment table, metrics and limitations, a compact error analysis
with one confusion figure, a short temperature/thinking result, and the
bounded previous-benchmark comparison.

Full specifications, artifacts, the detailed error taxonomy, and
extended configuration analyses belong in supporting material.
Source-near, Holgate structured/one-label, and extra-LLM encode/select
remain secondary. ExECT transfer and inventory evaluation stay out of
the dissertation paper, consistent with
[Gan is the dissertation paper](gan-is-the-dissertation-paper.md).
The 100-letter Gan inventory panel remains a descriptive feasibility
study, not a second accuracy table.

Preserve model, split, scorer, environment, and aggregate-only
boundaries in every retained result.

## Decision 6 — practical claims

Claim technical feasibility only. Local-model evaluation tests whether
the evidence-backed structured extraction design can execute on local
hardware under the same synthetic task conditions. That is design
evidence that later researchers or healthcare organisations may
evaluate locally.

Do not claim real-letter performance, clinical validity, workflow
integration, privacy compliance, or deployment readiness. Evaluation is
synthetic-data research. Real-record validation, prospective workflow
evaluation, and clinical safety assessment remain future work.

Motivation may mention cohort identification, longitudinal or
retrospective analysis, and future modelling. Those are intended later
uses, not demonstrated capabilities.

## What this does not change

- Gan `test450` remains locked and aggregate-only.
- Existing five-cell, Rules-only, and ExECT artifacts remain valid
  repository evidence.
- Component attribution, replay, and conservative claims still apply.
- Exact scores stay on their current experiment and
  `paper_experiments/` owners.
