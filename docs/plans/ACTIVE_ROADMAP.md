# Paper roadmap

Updated: 2026-09-14. Owner: Conor Brown.

## Current focus

Exclusive focus for this period is the one-call seizure-frequency paper.
Longitudinal prototype development, cohort expansion, clinical review of that
prototype, research-paper tables and optimizer experiments are postponed. The main next research step is a complete seizure-finding annotation of dev750,
starting with annotation guidelines. Prove this approach before extending annotation
and extraction to medications, diagnoses and investigations, then explore its use
with the real-letter annotators through Yujian Gan. Preserve
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
- Build a source-first seizure-finding reference for all dev750 letters to measure
  finding correctness and completeness separately from the existing answer label.
  Codex defines the guidelines and coordinates Grok 4.6 for annotation and
  self-review, replacing Gemini; Codex performs the independent secondary review.
  Model annotations are provisional until reviewed; clinical disagreements remain explicit.
- Use one compact ExECT configuration example with native reference semantics.
  No longitudinal results, usability study, rule-authoring study, broad ExECT model
  comparison or different-domain evaluation is in the current paper programme.
- Use the DeepSeek API from this computer for main synthetic evaluations, within
  Conor's current total US$100 API budget, and supplementary local runs on the Dell XPS 15.
  The collaborator owns local DeepSeek cluster runs on real data; no cluster budget
  is needed here. Record each runtime separately.
- Plan two real-data runs: single-label frequency extraction and a separate
  multi-family extension. Freeze both before real evaluation; written permission
  remains pending with Conor.
- Develop on dev750 and evaluate frozen conditions once on aggregate-only test450,
  disclosing prior exposure. Report agreement and paired differences with 95%
  intervals, without adequacy thresholds or a non-inferiority claim.
- Keep historical hybrid/two-call results as dissertation context. No semantic
  deterministic repair or extra clinical call may be hidden in the primary method.
- Reconstruction and migration are complete on `main` at `205cdb16`, now integrated
  into this branch. Preserve request identity, raw attempts, replay and the no-install
  HPC workflow. No further architecture programme is required before protocol work.

## Current development decision (2026-09-14)

Conor approved the measurement-specific v2 rich record: event scope, typed rates/
counts/clusters/seizure-free intervals/last-seizure times/qualitative findings,
measurement bounds and approximation, explicit conditions and linked evidence.
Generic raw-value, certainty and negation fields are removed. A dev750 wording
review also removed the proposed measurement-denial flag; bounds, qualitative
wording and event-scoped seizure freedom cover the retrieved examples. The
[schema decisions](../research/gan2026/one_shot_schema_decisions.md#agreed-v2-measurement-design-2026-09-14)
owns the agreed fields and their semantics.

V2 r4 aligns the paired simple instructions with its answer-only schema; shared
clinical guidance and decision examples remain identical. V2 r3 restored the original one-shot task, extraction reminders, complete worked
selection cases, label forms and request envelope. Only the output schema and its
field-population instructions are adapted. The schema decisions own the component audit.
V2 was prepared as a separate development candidate with fictional
fixtures and matched rich/simple rendering. The completed v1 evaluation below is
preserved. Its scores do not evaluate v2, and its freeze is not transferred to v2.
The paired r4 dev750 assessment is complete; the protocol links its results.
The thinking-enabled r4/r5/r6 comparison and all 54 authorised r4/r5 timeout reruns
are complete. The next steps are minimal representation corrections and disagreement
review, followed by the full seizure-finding annotation programme below. The
separately authorised r6 test450 replication remains aggregate-only.

## Work ahead

Conor confirmed this order after reviewing the r5 dev750 findings on 2026-09-14.
Completion reliability is not a separate research programme; measure time per letter
and retain accurate attempt accounting. Expected Purist agreement around 0.88 for
both conditions is an expectation to test, not a target for tuning.

| Order | Work and owner | Completion evidence |
| --- | --- | --- |
| 1 — complete | Evaluation contributor reran the 14 r4 simple and 40 r5 rich timeouts at 600 seconds. | All 54 returned; original attempts preserved and replay verified. Both conditions reached 658/750 Purist answer agreement; rich strict is 656/750. The execution record owns results, timing and costs. |
| 2 — representation implemented; review pending | Implementation contributor makes the smallest demonstrated representation corrections, then reviews rich/simple disagreements. | Finalised r7 candidate covers cluster interval counts, compound bounds, agreed schema simplifications and document/event dates; 23 fictional fixtures and unchanged native task rules. Disagreement classification remains pending. Frozen timeout-rerun conditions are unchanged. |
| 3 — authored; pilot secondary review complete | Codex defined [v0.6 annotation guidelines](../research/gan2026/seizure_finding_annotation_guide.md) in the standalone annotation guide. | Portable instructions/schema, source-first decisions, offline checks and shared full-set Gemini/Codex review procedures are written, with fictional examples and matching rules. Codex completed secondary review of 24 pilot letters; CB subsequently adjudicated the four open cases under v0.5. All 24 are complete, and staged continuation is accepted. The execution record owns review scope and evidence; clinical validation remains separate. |
| 4 — 84 initials saved; 666 remaining | Grok 4.6 is annotator and primary self-reviewer; Codex coordinates and performs independent secondary review. Preserve model attribution and frozen five-letter assignments. | All 102 review corrections for batches 003–012 are implemented: 50 letters/165 findings, 47 adjudicable letters and three retained source ambiguities under CB decisions. Across reviewed pieces, 81 letters/264 findings are adjudicable; the earlier accepted 34-letter set remains separately recorded. Native quarter support and source531 reclassification use v0.6. Both full-set review passes and wider correction propagation remain pending. The [execution record](../research/gan2026/one_shot_execution_record.md#batches-008012-corrections-and-current-totals-2026-09-15) owns results and verification; the local manifest owns assignment and corrected snapshot paths. |
| 5 | If the seizure annotation process works well, extend it to medications, diagnoses and investigations. Conor and Codex define the extension and review its annotations. | Reviewed four-family development reference and a frozen paired comparison of seizure-only versus all-four-family extraction on the original frequency-label endpoint. |
| 6 | Conor provides the reviewed dataset and guidelines to Yujian Gan and asks whether the King's College London Hospital annotators are willing to apply the expanded annotation to real patient letters. | Collaborator feedback and agreed clinical annotation scope, permissions and review procedure; no willingness or real annotation assumed in advance. |
| 7 | Conor/custodian and evaluation collaborator freeze and execute the authorised real-letter study; manuscript contributor completes the paper. | Separate real and synthetic results, finding measures supported by the references actually obtained, native answer agreement, time per letter and declared limitations. |

Draft the manuscript alongside this work. Real-data permissions and exposure
metadata can be resolved in parallel; they do not block synthetic guideline work.
Holgate receipt blocks only that comparator. The protocol links the separate execution, annotation and review owners. A bounded output-only support audit is no
longer the planned substitute for a full source-first development inventory.

## Progress against steps 1–4 (2026-09-13)

1. **Pending Conor/custodian:** written real-set permission, reference/exposure,
   linkage and eligibility metadata. No patient-data access occurred.
2. **Implemented and verified:** strict rich/simple prompts, fictional fixtures,
   native-score adapter audit, explicit first-pass failures and matched rendered
   diff. Historical parsing/repair behavior is preserved.
3. **Main synthetic choices complete:** DeepSeek V4.1 Flash API, total US$10 ceiling,
   fixed dev750 sample, all-row test450 comparison and prespecified 95% intervals.
   Supplementary Dell runtime details and the real multi-family reference/scope
   remain pending. The protocol owns the exact settings and limitations.
4. **Main synthetic comparison complete:** 40 development calls and 900 frozen
   test450 calls, preserved requests/responses, aggregates and an identical offline
   replay. Purist agreement was 342/450 rich and 334/450 simple; the paired interval
   includes zero. Conservative total charge estimate US$1.1732. The rich frequency
   condition was selected before test results; no sealed errors were inspected.
   Dell execution awaits access, with a prepared development bundle and client.

See the [completed comparison](../research/gan2026/one_shot_execution_record.md#completed-synthetic-comparison-2026-09-13)
for results and artifact ownership. No superiority, non-inferiority, fresh-holdout
or real-patient result is claimed from this synthetic comparison.

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
