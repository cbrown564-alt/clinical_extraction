# One-call evidence-grounded seizure-frequency extraction

Working manuscript outline, 2026-09-13. This is Strand A of the
[active roadmap](../../docs/plans/ACTIVE_ROADMAP.md), not a submitted manuscript.
It owns the paper's argument, structure and planned exhibits. The
[draft evaluation protocol](../../docs/research/gan2026/one_shot_paper_protocol.md)
owns future comparison conditions, permissions, unresolved execution decisions,
thresholds and safeguards. The completed two-stage dissertation remains separately
owned under [dissertation materials](../dissertation/README.md).

## Paper in one paragraph

This paper tests whether a sufficiently capable current model can return, in one
clinical inference call, both the established answer to a narrow seizure-frequency
task and a reusable, structured record of the source facts that bear on it. The
record contains multiple seizure-frequency findings, their temporal and uncertainty
qualifiers, exact source quotations, and one declared task answer. For notes with
competing temporal, uncertain or heterogeneous statements, a final label that omits
the relevant competing source facts is an incomplete research representation when
the richer contract is technically feasible. The claim is not that the record reveals
hidden model reasoning: its inspectable chain is **source note → structured
findings and quoted evidence → declared task answer**.

The method aims to preserve uncertainty, temporality, competing evidence and source
provenance in computable form, bridging clinical narrative and research or database
uses. It does not claim clinical adoption, deployment benefit, or general LLM
trustworthiness. Historical Gan results and the dissertation's extract-then-decide
rules are context only; they are not results for this one-call method.

## What the paper will and will not establish

### Adequacy standard

For the notes in scope, structured evidence, exact quotations and an explicit task
configuration are part of an adequate extraction contract, not optional
explainability additions. The contract must make the relevant findings and their
relationship to the task answer inspectable. Exact quotation establishes a source
location; it does **not** by itself make the quoted finding clinically correct,
complete or entailed by the answer.

The output is model-produced evidence inventory, not access to a model's private
chain of thought. If the response includes a short stated selection basis, assess it
only for consistency with the visible findings and final answer, not as an account of
the model's internal computation.

### Reference and scope boundary

Gan provides 1,200 expert-annotated synthetic letters and a separately available set
of 300 expert-annotated real-patient letters. The available reference for each
letter is one expert-selected current seizure-frequency label. That existing label,
under Gan's native Purist definition, is the primary outcome for the real-letter
evaluation if use is authorised under the protocol. Pragmatic scoring is a companion
outcome.

The reference does not gold-label a complete inventory of seizure-frequency facts.
The additional findings and quotations therefore require no new full
assertion-level annotation: report their exactness, schema validity, count and type
as contract evidence or descriptive output, not as a new gold-scored fact benchmark.
Do not infer clinical validity for every emitted finding from an exact substring
match.

The primary task result is all-note agreement with the existing real-letter expert
label. Schema-invalid or otherwise unusable responses remain failures in that task
denominator. Any use of the sealed real set, its reference and its exposure history
requires the permissions and procedure in the protocol; this outline does not
authorise access or evaluation.

### Bounded trust claim

The paper can make a bounded, testable claim: a clinical extraction contract can be
evaluated through expert-label agreement, schema validity, exact source evidence and
visible classified failures. It cannot conclude that LLMs are generally trustworthy.
A model panel may show that weaker models fail visibly while stronger models meet the
contract under the specified condition. That would distinguish model capability from
the prompt and schema design; it would not prove that either alone guarantees
reliability elsewhere.

Local execution is an enabling condition for sensitive data, rather than a core
performance claim. Report the actual runtime environment and basic
completion/reliability measures so the work is reproducible. Describe a
hospital-controlled or server deployment only if it is demonstrated and verified;
laptop results are optional execution context, not a clinical deployment result.

## Study questions and planned evidence

| Question | Planned evidence | Claim boundary |
| --- | --- | --- |
| Can the rich one-call contract retain the established seizure-frequency task outcome on real letters? | All-note agreement with the existing expert-selected label on real Gan 300, scored natively with Purist; Pragmatic companion score; unusable responses included. | The primary clinical-task claim is limited to the authorised reference, cohort and stated exposure history. |
| Does asking for a rich evidence record harm the established task outcome? | Matched rich-contract versus simple-label-with-evidence comparison on permitted Gan notes. | This changes the requested extraction scope and output together. It is not a pure schema-only ablation. |
| Is the contract reliably produced and visibly inspectable? | First-pass schema validity; exact-source evidence rate; separately reported format repair, unparsed and unusable failures; descriptive retained-finding counts and types. | Exact spans locate text but do not establish clinical correctness, inventory completeness or entailment. |
| Can the method be configured without retraining or hyperparameter changes? | One compact worked configuration with explicit component edits and retained execution structure. | This demonstrates a technical property, not clinician usability, reduced expertise or predictable control. |
| Does capability matter? | A prespecified model panel, if run under the protocol, with the same contract and visible failures. | Results distinguish the tested model/runtime condition from prompt or schema effects and do not generalise to LLMs as a class. |

## Method to present

### One-call contract

For each note, one clinical model request returns a structured record with:

- zero or more task-scoped seizure-frequency findings;
- a normalised value or finding type, relevant seizure type where applicable,
  temporality, uncertainty/negation and other declared qualifiers;
- an exact quotation for each finding, retained as source provenance;
- links from the declared answer to the relevant findings where the schema supports
  them; and
- one final answer in the existing task's label definition.

The model produces the record and final answer in the same call. Parsing, schema
checking and value-preserving serialization may be described separately, but they
must not select an event, resolve a clinical ambiguity, alter clinical meaning or
invent an answer. Preserve raw responses, first-pass failures, any format-only
repair and residual unparsed output. The protocol owns the final rendering,
serialization and repair policy.

### Controlled comparison

The main controlled comparison is the rich evidence contract against an own simple
prompt that returns one final label with supporting evidence but omits the emitted
fact inventory. Keep the model and revision, notes, decoding, runtime, examples'
clinical content, label definition, uncertainty convention, scorer and row policy
the same. This tests whether requesting the richer representation harms the
established task outcome; it does not isolate a single schema field or wording
effect.

The Holgate external whole-prompt comparator remains contingent on receiving the
original supplied prompt and permission to use it, as specified in the protocol. Do
not reconstruct or substitute that prompt. If available, report it as an external
whole-prompt condition, with its own output and parsing constraints, rather than as
an isolated prompt-feature comparison.

### Compact configuration example

Show one worked specification change, likely either a limited epilepsy variation or
an ExECT task. The exhibit should map the written task to the editable components:
concept definitions, scope and time rules, uncertainty conventions, evidence
obligations, output fields and examples. For example, it may retain frequency by
seizure type and distinguish current from historical statements. The model,
decoding and hyperparameters do not change; the changed components and any
regressions remain visible. ExECT is compact configuration evidence with its native
reference semantics, not a new multi-model benchmark. Longitudinal extraction is
outside the core paper.

## Manuscript flow

| Section | Purpose | Material and boundary |
| --- | --- | --- |
| Introduction | Show why immediate flattening of ambiguous clinical narrative to one label loses relevant competing facts. State the positive thesis: capable models may meet a richer one-call adequacy contract while accurately answering the existing task. | Do not frame evidence, quotations or configuration as optional enhancements; do not claim clinical deployment. |
| Task, data and reference | Define the narrow current seizure-frequency task, the existing single-label expert reference and what it cannot score. Separate real Gan 300 from Gan synthetic 1,200 and ExECT. | The real-letter reference is primary; synthetic Gan supports controlled comparisons. No assertion-level gold is assumed. |
| Method | Specify the one-call record, declared task view, source-provenance fields, format boundary and reproducibility record. | The visible chain is source → record → answer, not hidden reasoning. Historic two-stage methods are context, not the proposed method. |
| Evaluation | Define all-note Purist agreement as the primary endpoint, Pragmatic companion score, and contract reliability measures. | Include schema-invalid and unusable output in the task denominator. The protocol owns thresholds, permissions, review design and future execution choices. |
| Results: primary real-letter evaluation | Report the authorised real Gan 300 primary result with denominators, uncertainty, coverage and classified failures. | Leave empty until a reviewed, authorised evaluation exists; do not pool with synthetic results. |
| Results: controlled synthetic comparison | Compare own rich versus simple prompts on the same permitted Gan condition; report the Holgate comparison only if supplied and permitted. | Treat rich-versus-simple as a joint task/output contrast; distinguish the external whole-prompt comparator. |
| Results: reliability and capability | Report first-pass schema validity, source-quote exactness, repair/unparsed failure paths, descriptive findings, runtime and any model panel. | Separate exact-span validity from clinical support; distinguish model capability from contract design. |
| Results: configuration | Present one compact configuration map and descriptive native reference check. | Demonstrates editable task components without retraining; it does not establish clinician usability or reduced expertise. |
| Discussion | Explain the contribution for evidence-grounded clinical extraction and bounded research/database use. | Discuss annotation limits, synthetic/real differences, prior exposure, local-execution limits, non-deployment and the need for future clinical or usability studies. |

## Planned exhibits

1. **Figure 1 — One-call evidence contract.** Note → one request → raw structured
   response containing findings, quotations, qualifiers and declared answer →
   explicit format handling → native task scoring. Mark which values are
   model-produced and which handling is format-only.
2. **Table 1 — Data and reference roles.** Real Gan 300, synthetic Gan 1,200 and
   ExECT: population, existing reference, sampling unit, permitted role and what
   each reference cannot measure. State that the Gan reference is one selected
   current-frequency label per letter.
3. **Table 2 — Primary real-letter task result.** Purist all-note agreement,
   Pragmatic companion, usable-answer coverage, denominator, uncertainty and
   classified unusable failures. Populate only after authorised evaluation.
4. **Table 3 — Controlled synthetic prompt comparison.** Rich versus simple own
   prompt, matched on all named conditions, with paired task differences,
   denominators and richer-output costs. Add the Holgate whole-prompt condition only
   when its original supplied prompt and permissions are documented.
5. **Table 4 — Contract reliability and runtime.** First-pass schema validity,
   exact-source evidence rate, format repair, residual unparsed/unusable responses,
   retained-finding types/counts and actual runtime environment. Do not turn exact
   substring rate into a clinical-fact correctness claim.
6. **Figure 2 — Worked configuration.** A compact before/after map from written
   task definition to the components changed, with the retained execution pathway
   and a descriptive native reference check. Keep ExECT scoring and its mapping
   losses explicit if it is the example.

The supplement should hold versioned rendered prompts and hashes, schemas, examples,
scorer versions, reference instructions, component-change maps, full run records,
format-repair accounting and detailed configuration scoring. Show only permitted
development or fictional examples. It must keep raw output, format repair, semantic
adaptation and scoring independently inspectable.

## Drafting boundary

Draft the argument and method now; populate results only from reviewed, authorised
machine artifacts. Do not reuse dissertation headline scores, historical two-stage
rules or Gan-only results as if they evaluated this one-call contract. Do not inspect
locked rows, call models or create a new evidence benchmark while developing this
outline. Journal formatting, submission, clinical deployment and broad
generalisability are outside this document's current scope.
