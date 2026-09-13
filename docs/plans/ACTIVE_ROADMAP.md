# Paper roadmap

Updated: 2026-09-13. Owner: Conor Brown.

## Current focus

Exclusive focus for this period is the one-call seizure-frequency paper.
Longitudinal prototype development, cohort expansion, clinical review of that
prototype, research-paper tables and optimizer experiments are postponed. Preserve
their code, examples and saved results; none is a prerequisite for this paper.

The [paper outline](../../publications/jamia-one-shot/README.md) owns the argument
and exhibits. The [evaluation protocol](../research/gan2026/one_shot_paper_protocol.md)
owns conditions, denominators, analysis and execution decisions. This roadmap owns
priorities and the decisions below, without repeating either document.

## Decisions already made

- Study one clinical model call per note, returning seizure-frequency findings,
  quotations, qualifiers and one declared task answer. A one-call prompt may
  contain examples; one-call and zero-shot are different properties.
- The intended primary evaluation is agreement with the existing expert-selected
  real Gan 300 current-frequency label: native Purist, with Pragmatic companion.
  Use remains contingent on confirmed permissions and prior-exposure restrictions.
- Compare the rich prompt with our single-label-with-evidence prompt on permitted
  synthetic Gan notes. Match model, runtime, task semantics and clinical example
  content. This changes requested scope and output together, not schema alone.
- Include Holgate's whole-prompt comparator only after the original prompt and
  use conditions arrive through Conor's supervisor. Do not recreate it from memory.
- No new complete assertion-level reference is required. Schema validity, quote
  exactness and finding counts describe the output contract; they do not establish
  clinical correctness or completeness of every finding.
- Use one compact ExECT configuration example with native reference semantics.
  No longitudinal results, usability study, rule-authoring study, broad ExECT model
  comparison or different-domain evaluation is in the current paper programme.
- Prioritise locally deployable models. Record actual runtime and basic reliability;
  local execution does not establish hospital deployment or clinical adoption.
- Keep historical hybrid/two-call results as dissertation context. No semantic
  deterministic repair or extra clinical call may be hidden in the primary method.
- Reconstruction and migration are complete on `main` at `205cdb16`, now integrated
  into this branch. Preserve request identity, raw attempts, replay and the no-install
  HPC workflow. No further architecture programme is required before protocol work.

## Work ahead

| Order | Work and owner | Completion evidence |
| --- | --- | --- |
| 1 | Conor confirms real-set permitted use and prior exposure with its custodian. | Written access/reuse decision, reference version and eligible-note policy; no sealed-note inspection during planning. |
| 2 | Implementation contributor proves the rich/simple contract without model calls. | Rendered prompt/schema diff, fixed fictional or permitted development fixtures, native-label adapter audit, explicit invalid-output handling. |
| 3 | Conor approves the protocol's remaining execution choices. | Model/runtime panel, budget, synthetic selection/evaluation policy and frozen analysis; any adequacy threshold or non-inferiority margin agreed before results. |
| 4 | Run authorised synthetic development and controlled comparison. | Saved requests/responses, paired all-note scores, contract reliability and cost; a frozen selected condition for real evaluation. |
| 5 | Run authorised real-letter evaluation once the condition is frozen. | Aggregate Purist/Pragmatic results and failures, uncertainty and exposure disclosure; no development from sealed errors. |
| 6 | Complete the compact configuration exhibit and manuscript. | One inspectable component change, descriptive native check, tables generated from reviewed artifacts, limitations matching the evidence. |

Draft introduction, methods and exhibit structures alongside steps 1–3. Holgate
receipt may delay that comparator but need not delay our matched comparison.
Results stay empty until supported by authorised machine artifacts. This plan
authorises documentation and no-call preparation, not spending or sealed evaluation.

## Documentation and completion

Keep at most 50 Markdown documents under `docs/`, including generated reference
pages and the paused longitudinal policies needed by saved artifacts. The existing
migration record owns the deletion counts, recovery revision and dispositions.
Remove obsolete narratives from the checkout rather than moving them into another
archive. Preserve machine evidence, frozen result records, publication assets and
sole local copies. Publication writing and artifact README files are separate from
this documentation count and must not become a destination for displaced prose.

Update existing owners rather than adding status reports. Current status is brief
and local in `PROJECT_STATUS.md`; historical checks belong to the migration record
or their result artifact. For documentation changes, check links and hygiene; for
code changes, use the repository's documented tests. No model calls, locked-row
inspection or broad artifact regeneration are needed to prune prose.
