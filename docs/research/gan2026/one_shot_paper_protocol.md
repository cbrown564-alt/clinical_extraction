# Strand A: one-call extraction evaluation protocol

Draft for decisions, 2026-09-13. Owner: Conor Brown.
Not frozen; no new calls, spending, data access or locked-test evaluation authorised.
The [roadmap](../../plans/ACTIVE_ROADMAP.md) owns scope and sequencing;
the [manuscript outline](../../../publications/jamia-one-shot/README.md) owns presentation.
This protocol owns the future comparison procedure, including its distinct real-data
evaluation. Its location under `gan2026/` does not give real records Gan permissions
or reference semantics.

## Question and proposed method

Can a locally deployable model provide a correct current seizure-frequency answer
and supported structured assertions in one inference call, with acceptable coverage
and execution reliability? The primary task is seizure frequency. ExECT schema
adaptation is a compact secondary demonstration within epilepsy. Longitudinal
evaluation belongs primarily to a separate paper; an optional fictional example
may illustrate downstream use without adding a longitudinal performance claim.

Proposed terminology: **one-call** means one clinical inference request per note;
**zero-shot** means no demonstrations. A one-call prompt may contain demonstrations.
Use these terms separately in tables instead of relying on an ambiguous “one-shot”.

The model returns the task answer and the assertions/evidence supporting it in the
same response. Freeze which assertion families and temporal qualifiers are required
before implementation. Preserve original responses, parse failures and any transforms.
Syntax checking or value-preserving serialization must not select events, change
clinical values, resolve uncertainty or invent an answer. A second clinical call or
deterministic clinical selection is a separate method, outside the primary condition.

The existing `gan_llm_extract` path is a reconstruction/replay starting point, not
automatically the final study method. Audit its exact prompt, parser and projection
for semantic changes before adopting it. The architecture's compatibility path
preserves historical behaviour; that alone does not prove a repair-free condition.

## Data and reference roles

| Source | Role | Permitted planning basis and unresolved conditions |
| --- | --- | --- |
| Real-patient seizure-frequency notes | Primary clinical evaluation | Confirm source, access authority, cohort and sample, patient linkage, reference process and all prior development/test exposure. Existing Real(300) is sealed under the retained policy; its existence grants no new use. |
| Gan synthetic letters | Controlled prompt/model comparisons | Retain `dev750` development and `test450` aggregate-only restrictions. The historical paper uses 1,200 letters, including `row_ok=False`; `train300` is not implicitly available. A new experiment needs an explicit reuse decision. |
| ExECT synthetic, expert-annotated letters | Small descriptive schema-adaptation check | Keep `dev140`/`test60` permissions and native reference semantics. Select the demonstration from permitted development data; describe selection and avoid a new multi-model benchmark. |
| Authored/generated longitudinal cases | Outside the core evaluation; optional application illustration | Primarily separate-paper material. Synthetic development references and saved predictions remain separately labelled. Existing query-conditioned captures cannot establish fresh query-independent extraction. |

Counts and historical row policies are documented in the
[dataset description](../shared/dataset_description_2026-08-26.md).
The [holdout policy](../../benchmarks/holdout-is-aggregate-only.md) applies
throughout. Repeated historical evaluation must be disclosed; an old holdout must
not be described as newly untouched. No locked rows or errors are needed for planning.

## Outcomes and capability decision

The real-data reference and intended use determine the primary endpoint. Do not
assume its labels support Gan's categories or complete assertion-level recall.
Proposed capability decision: require a prespecified lower confidence bound for
task correctness and minimum coverage, plus upper bounds for unsupported assertions
and execution failures. Conor and a named domain reviewer must set the numerical
thresholds and clinically consequential error definitions before model selection.
Until then, the study may describe measurements but cannot establish “good enough”.

| Measure | Proposed denominator and interpretation |
| --- | --- |
| Primary task correctness | All eligible evaluation notes, including execution failures. Freeze scoring of uncertain states and abstention; distinguish a correct reference “unknown” from system refusal. |
| Answer coverage | Notes with a usable task answer / all eligible notes. Also show correctness conditional on coverage; it cannot replace the all-note result. |
| Gan task agreement | Native Purist micro-F1 (accuracy for one label per note), with Pragmatic as companion; retain frozen scorer and row policy. These do not score complete histories. |
| Unsupported assertions | Unsupported / reviewed emitted assertions, plus notes with at least one unsupported assertion / reviewed notes. Review clinical support separately from exact quote location. |
| Evidence support | Supported / reviewed asserted clinical facts, with missing evidence counted explicitly. Report exact-span validity separately. A quotation match alone is insufficient. |
| Omission and uncertainty | Recall only where a complete task-scoped reference exists. Otherwise report a bounded reviewed sample and do not invent a recall denominator. Preserve missing, negated, uncertain and conflicting states. |
| Execution reliability | First-call parse/schema failures, timeouts and empty responses / all scheduled notes. A format-only retry has separate recovered counts, residual failures and total calls. |
| Runtime | Latency distribution, input/output tokens, measured memory, hardware, engine and concurrency. State whether queueing, loading and retries are included. |

Evidence review needs written task-specific support criteria, a prespecified sample,
reviewer roles, independent review/adjudication and recorded uncertainty. Select
samples without filtering to correct answers or successful parses. This protocol
does not claim that such review or a suitable clinical reference currently exists.

Use patient-level uncertainty estimates when multiple notes belong to one patient;
respect known synthetic source families. Compare matched predictions with paired
intervals on the same sampling units. Choose sample size from the desired precision,
error thresholds and available independent patients before evaluation; no sample
size or power claim is supplied here. Prespecify primary contrasts and treat other
slice analyses as descriptive. A domain reviewer should define the error slices
(for example temporal selection, multiple seizure types and unsupported certainty).

## Bounded comparison design

First prove one complete development condition: fixed input and reference, rendered
request, untouched response, declared format handling, native scoring and evidence
review output. Then extend the same mechanism to the planned comparisons.

### Agreed prompt comparisons (2026-09-13)

Conor will compare the structured prompt with Ben Holgate's Llama 2 prompt.
Conor's supervisor will obtain the full prompt from Holgate. It has not been
received or inspected for this protocol; do not reconstruct it from a description
or substitute a repository prompt based only on its name. Record the supplied
version, provenance, system/user messages, demonstrations, output instructions and
any original runtime requirements. Confirm quotation/sharing permission before
including supplied prompt text in publication materials.

| Condition | Task and emitted output | Purpose |
| --- | --- | --- |
| Holgate prompt | Exact supplied task instructions and output format, once obtained | External whole-prompt comparator |
| Own rich prompt | Extract all seizure-frequency facts within the declared scope; represent each fact with evidence, then select one final label with a rationale in the same response | Full structured condition |
| Own simple prompt | Return one final seizure-frequency label with supporting evidence; omit the emitted fact inventory and selection rationale | Matched simplified condition |

Run the Holgate and own-prompt conditions on the same model and same permitted
notes to estimate a prompt-package difference. Comparing only Holgate/Llama 2 with
the new prompt on a newer model would conflate prompt and model progress. If a
historical Llama 2 condition is included, either cross both prompts with both model
conditions or label the unmatched comparison as historical context. Do not assume
the original model was unadapted or its inference setup from the prompt's name.

The rich-versus-simple own-prompt comparison is the primary controlled contrast.
Keep model/revision, decoding, runtime, input text, target label definitions,
selection policy, uncertainty conventions, evidence requirement, examples' clinical
content, scorer and row policy fixed. Change only the extraction-scope instructions
and their corresponding output fields. Where example outputs must match the schema,
record the exact paired edits; do not improve the examples in only one condition.
Inspect a rendered prompt diff before execution.

Both conditions make one clinical inference call. “Then select” specifies the
requested organisation of that response, not a second call or proof of internal
reasoning order. The model selects the final label; no deterministic clinical
selector replaces it. Assess the rationale for support and consistency with the
facts and final label, not as a faithful account of hidden computation.

This contrast estimates the combined effect of requesting comprehensive extraction,
emitting a fact inventory and providing a selection rationale. It cannot attribute
any improvement solely to schema richness or precise wording. If attribution is
needed after the representative comparison, consider prespecified intermediate
conditions: single label/evidence plus rationale, then fact inventory plus final
label/evidence without rationale. These are proposals, not agreed extra runs.
Instructions to extract all facts without emitting them cannot verify whether a
complete internal inventory was produced.

Use the same sufficiently generous output cap and timeout for the controlled
conditions, with the limit chosen on development inputs; report truncation and
actual token/latency costs. Do not force equal realised output length, since richer
output is part of the intervention. Keep any schema-constrained decoding policy
fixed and record the condition-specific schema. For the external comparison,
preserve Holgate's supplied output form and document format-specific parsing; an
adapted Holgate prompt must be a separately named condition.

Score the same final target in all conditions through declared value-preserving
adapters. Missing evidence or unavailable output fields in the supplied comparator
are reported as such, not invented by a repair step. Compare selected-answer evidence
on the common output where available; assess full-inventory support/completeness
separately for rich outputs. Keep failures in denominators and report richer-output
costs even when accuracy improves.

### Subsequent comparisons and execution order

1. Prove the rich and simple conditions with no-call rendering and permitted
   development examples before expanding the experiment matrix.
2. Additional component ablations (field descriptions, evidence obligation, scope
   wording or demonstrations) remain optional. Each needs a named question and
   controlled rendered edits; they are not prerequisites to the agreed contrast.
3. Freeze the main prompt before the local-model panel. Pin model revision, size,
   quantisation, context, inference engine, hardware and decoding. Select feasible
   older and newer models only after checking their runtime and source conditions.
   No particular roster or performance ranking is established here.
4. Change runtime settings in separately named conditions. Do not attribute a
   difference simultaneously caused by model, quantisation, hardware and prompt
   to model age or capability alone. Published unmatched results are context.
5. Freeze the chosen condition and reference protocol before authorised real-data
   evaluation. Synthetic development guides selection; real-test failures do not.

Keep historical hybrid and two-call results as dissertation context, rather than
the main method or a main comparator. Do not relabel historical provisional-answer
scores as results of a newly frozen prompt. The ExECT extension uses one declared
condition with native family-level reference checks and explicit mapping losses;
it does not inherit Gan's scorer or capability threshold.

## Reproducibility and execution readiness

### Optional exploration: configuration and authoring effort

Conor proposes that task descriptions and schemas could offer some of the practical
control of rules with less programming effort. Explore this before adding a broad
usability claim to the paper. Keep it separate from the primary accuracy comparison;
a small rules-authoring comparison would investigate configurability, not restore a
rule-heavy main extraction method.

Start with one permitted development task and two prespecified changes, such as
retaining frequency per seizure type and distinguishing current from historical
statements. Give each approach the same written target and acceptance examples.
Map the target to concept definitions, scope/time rules, uncertainty conventions,
evidence obligations, schema fields and examples. Record the exact edits and why
each belongs in that component. Freeze evaluation cases independently of examples
used during authoring; use no existing locked-test material.

Measure intended behaviour on the changed cases and regressions on unaffected
cases, along with authoring time, iterations, code changes and technical assistance.
If a rule implementation is compared, match starting functionality and author
experience and report setup costs. A developer's own exercise establishes software
feasibility only. Claims about lower expertise or domain-expert participation need
representative participants, recorded roles and a comparable task procedure.

Natural-language editability does not establish predictable control: a local prompt
edit may alter unrelated behaviour. Preserve those failures as evidence. A useful
deliverable from the exploration is one worked specification → component mapping →
verified change, with the limitations visible. Expansion and participant recruitment
remain future decisions.

### Required run record

Each future result records dataset/version, split, patient/note selection and row
policy, reference/scorer version, model/runtime, prompt components and rendered
request hashes, source hashes, replay mode, repair policy, raw attempts, failures,
exclusions, denominators and resource accounting. Keep extraction, format handling,
semantic adaptation and scoring independently inspectable. Record whether a value
was model-produced or changed by an adapter.

Before requesting an experiment run, resolve these decisions in this document:

| Decision | Responsible person | Current state |
| --- | --- | --- |
| Real-data source, permitted use and prior exposure | Conor with data custodian | Unconfirmed; no inspection or new use authorised |
| Task target, reference and clinical error costs | Conor with domain reviewer | Frequency task agreed; precise reference and review procedure open |
| Primary endpoint, numerical thresholds and precision/sample size | Conor with domain reviewer and analysis contributor | Proposed structure above; values unset |
| Prompt, permissible serialization and native scoring | Implementation contributor, reviewed by Conor | Audit and no-call development proof required |
| Full Holgate comparator prompt and original setup | Conor's supervisor obtains from Ben Holgate | Pending receipt; exact contents and runtime assumptions unknown |
| Local model panel, hardware feasibility and execution budget | Conor with implementation contributor | Unselected; no spending authorised |
| Locked evaluation/reuse procedure | Conor with evaluation owner | Retained protections apply; new protocol not frozen |

The immediate planning decision is which real-data reference can support the primary
claim and what prior use constrains it. Resolve it from existing documentation and
custodian confirmation, without opening sealed notes. Engineering reconstruction
remains the prerequisite to new experiment execution under the roadmap.
