# One-pass evidence-grounded seizure-frequency extraction

Working manuscript outline, 2026-09-13. This is Strand A of the
[active roadmap](../../docs/plans/ACTIVE_ROADMAP.md), not a submitted manuscript.
The [draft evaluation protocol](../../docs/research/gan2026/one_shot_paper_protocol.md)
owns the proposed comparisons, unresolved decisions and execution conditions.
The completed dissertation remains separately owned under
[dissertation](../dissertation/README.md).

## Intended argument

Test whether locally deployable models can extract a task-defined seizure-frequency
answer with supporting evidence in one inference call, without fine-tuning or
clinical repair. Real-patient evaluation must carry any clinical performance claim.
Gan supplies controlled synthetic comparisons. A compact ExECT demonstration
illustrates configurability within epilepsy. Longitudinal evaluation is primarily
separate-paper material, with only an optional fictional application illustration.

This is an argument to test. No capability threshold has been met by this outline,
and existing two-stage results are not results for the proposed method.

## Premise to investigate

Conor's proposed contribution is a practical combination: accurate extraction,
inspectable source support, configuration through task descriptions and schemas,
and execution on locally controlled hardware. The progress of local models supplies
the background narrative. Whether a specified model crosses a useful threshold
must be measured on the named task and hardware.

The model remains internally opaque. Source-grounded answers can make the output
auditable without making generated explanations faithful accounts of computation.
Schema compliance, clinical correctness and evidence support are distinct outcomes.
Avoid the categorical claims that hallucinations have ended or that all accuracy/
explainability tradeoffs have disappeared.

The potentially distinctive method is a reproducible way to translate a clinical
extraction specification into prompt components: target concepts, scope, temporal
policy, uncertainty, evidence requirements, output fields and examples. Explore
whether domain experts can review and change those components with less programming
support. Configurability comparable to rules, reduced authoring effort and greater
domain-expert participation remain separate hypotheses requiring direct evidence.
The protocol describes a bounded exploration; they are not established by a second
JSON schema or a successful demonstration alone.

## Manuscript structure

| Section | Question to answer | Required material |
| --- | --- | --- |
| Introduction | Can a locally executable, one-call extractor provide a useful answer and inspectable support? | Clinical extraction motivation; precise task and operating condition; distinguish evidence visibility from evidence correctness. Literature and journal requirements need a separate source review. |
| Methods: task and data | What constitutes the current seizure-frequency answer, and whose reference defines correctness? | Real cohort, sampling and reference procedure once confirmed; separate Gan population, split and row policy; missing, uncertain and multiple-frequency conventions. |
| Methods: extraction | What reaches the model and what happens to its response? | Actual rendered request and schema; model-authored answer and supporting assertions; versioned format handling and task projection; exact call boundary. |
| Methods: evaluation | What would count as useful and reliable? | Frozen primary endpoint, capability thresholds, evidence review, failure denominators, controlled prompt comparisons and runtime measurements from the protocol. |
| Results: primary task | How well does the frozen method perform on real notes? | Separate real-patient table, uncertainty estimates, coverage, evidence support and failures. Leave empty until authorised evaluation exists. |
| Results: controlled experiments | Does the rich specification improve on a simple answer and an external prompt? | Own rich versus label-with-evidence prompt under matched conditions; Ben Holgate's full Llama 2 prompt once supplied, evaluated as a whole-prompt comparator; paired differences and resource use. Explain Gan scoring centrally. |
| Results: configuration | Can the method support a second extraction specification? | Compact ExECT reference check with explicit component changes, retained shared execution and failures; detailed native scoring in the supplement. Adaptation alone does not establish reduced expertise. |
| Discussion | Where does the method work, fail, and remain untested? | Clinically consequential errors, annotation limits, synthetic/real differences, prior holdout exposure, hardware limits and the gap between retrospective evaluation and deployment. |

## Planned exhibits

1. **Figure 1: one-call method.** Permitted note → composed request → raw response
   containing assertions, evidence and answer → explicit format handling → frozen
   task scoring. Make the emitted fact inventory and model-selected answer explicit.
2. **Table 1: populations and references.** Separate real patients, Gan and ExECT;
   include sampling unit, reference provenance,
   access history, intended role and what each reference cannot measure.
3. **Table 2: real-patient primary evaluation.** Task correctness, coverage,
   unsupported assertions, evidence support and execution failures; no pooled score.
4. **Table 3: Gan prompt comparisons.** Own rich prompt versus single label with
   evidence, plus the supplied Holgate prompt on matched models. Separate the
   controlled joint task/output change from the external whole-prompt comparison;
   show denominators, paired uncertainty and prespecified model conditions.
5. **Table 4: runtime and reliability.** Exact model/runtime configuration,
   first-call success, retries, latency, token use and measured memory requirements.
6. **Figure 2: ExECT configuration.** One permitted example showing changed task
   definitions/schema components and retained execution/evidence handling. Include
   a compact descriptive reference check, with detailed results in the supplement.

Draft without longitudinal results. Consider one fictional longitudinal illustration
in the discussion or supplement only if it explains downstream value that ExECT
does not show. It must not imply validated history reconstruction or cohort selection.

The supplement should contain full prompts and hashes, schemas, scorer versions,
reference instructions, detailed ExECT scoring, ablation settings and reproducible
commands. Only permitted development or fictional examples may be shown.

## Drafting boundary

Write the task and method only after resolving the protocol's reference and scoring
decisions. Populate Results from reviewed machine artifacts, not historical headline
scores. Use “locally deployable” for a demonstrated runtime configuration; describe
hospital-controlled execution as intended until that environment is actually tested.
Journal formatting, submission and publication are later work.
