# Paper roadmap

Updated: 2026-09-22. Owner: Conor Brown.

## Current focus

Exclusive focus for this period is the one-call seizure-frequency paper.
Longitudinal prototype development, cohort expansion, clinical review of that
prototype, research-paper tables and optimizer experiments are postponed. The
dev750 v0.7 reference is assembled after all 750 source rereads and cross-letter
checks. The eight source-ambiguous references are resolved. The R7 development
failures and rich/simple disagreements are classified. One R8 rich dev750 pass,
scored with the same matcher, matches 1,032 of 2,097 reviewed findings. That is
higher than R7 and still about half the reference. Finding Purist, the
inventory endpoint, is now scored on those saved outputs: R8 recall is
1,226/2,097 and R7 recall is 993/2,097. The
[finding-match note](../research/gan2026/finding_purist_match.md) owns the rule
and the execution record owns the counts. Do not extend annotation or extraction
to medications, diagnoses and investigations until Conor decides the seizure
annotation process is ready for that extension. Use of
the real-letter annotators through Yujian Gan comes after that. Preserve
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
  Grok 4.6 supplied the v0.6 initials after replacing Gemini. Codex defines the
  guidelines and coordinates the independent review; the v0.7 continuation used
  three authorised parallel Codex reviewers after 26 saved Cursor batches.
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

## Bounded Jev exploration (2026-09-21)

Conor approved recording and prototyping the Jev exploration developed in the
[ChatGPT conversation](https://chatgpt.com/c/6aacde68-12a0-83eb-b035-6794b02456c0)
and the 18 September TypeSafe research report. This is a supplementary,
fictional-development comparison, separate from the paper's primary one-call
method and from the proposed ModernBERT/LFM2.5 trained baselines in PR #14.
The annotation reference and R7 disagreement review retain priority.

First compare Jev and a generative model on identical source text, candidates and
bounded semantic questions. Build candidates from source alone, bind each field
to a named candidate, retain missing/unsupported answers, and score selection and
attributes separately. Prove the offline loop before authorising paid execution
or extending to dev750. The [protocol](../research/gan2026/one_shot_paper_protocol.md#jev-fictional-comparison)
owns the experimental limits; the execution record owns verification.

The [completed v2 pilot](../../results/letter-benchmarks/gan/jev_fictional_v2/README.md)
on 22 related fictional conditions found repeated Jev quantity-binding and field-
applicability errors: 9/22 complete answers versus 22/22 for DeepSeek, despite both
models matching all 67 role labels. **Do not expand the current Jev design to
dev750.** The subsequently completed
[v3 classification/verification pilot](../../results/letter-benchmarks/gan/jev_fictional_v3/README.md)
used eight development and eight reserved fictional letters. On reserved cases,
Jev matched 84/100 classifications versus DeepSeek's 99/100. Its verifier accepted
one deliberately wrong tuple and deferred 11/45 correct actual proposals across
both splits. The sole DeepSeek discrepancy is a pre-adjudicated reference ambiguity,
so the apparent verification benefit is weak. **Stop this Jev candidate; no dev750
extension or further live Jev run is active.** Return priority to the paper's
source-ambiguity adjudication and R7 failure/disagreement review. Any future Jev
work needs a distinct question, not another broad run of the same design.

The tested LLM-plus-Jev verifier has two clinical calls and must not be counted
as the paper's one-call method.
The report's architectural recommendations are research proposals, not instructions
to replace the current study. No test450 or patient-data access is authorised here.

## Work ahead

Conor confirmed this order after reviewing the r5 dev750 findings on 2026-09-14.
Completion reliability is not a separate research programme; measure time per letter
and retain accurate attempt accounting. Expected Purist agreement around 0.88 for
both conditions is an expectation to test, not a target for tuning.

| Order | Work and owner | Completion evidence |
| --- | --- | --- |
| 1 — complete | Evaluation contributor reran the 14 r4 simple and 40 r5 rich timeouts at 600 seconds. | All 54 returned; original attempts preserved and replay verified. Both conditions reached 658/750 Purist answer agreement; rich strict is 656/750. The execution record owns results, timing and costs. |
| 2 — complete | Implementation contributor makes the smallest demonstrated representation corrections, then reviews rich/simple disagreements. | R7 dev750 mixed view: 650/750 Purist answer, 619/750 strict, 36 schema-invalid records. Classification, 2026-09-22: schema failures are serialization against existing slots; 74 of 100 Purist misses are shared with r4 simple. The execution record owns the causes. Frozen timeout-rerun conditions are unchanged. |
| 3 — v0.7 authored and checked | Codex maintains the [annotation guide](../research/gan2026/seizure_finding_annotation_guide.md), portable schema and lean review procedure. | Conor approved verbatim vague absence durations and recurrence denominators on 21 September, and bimonthly = one per two months on 22 September, retaining exact evidence. R8 no-call revision and 16 fictional fixtures support these conventions. The canonical repeat rule includes period, and assembly performs no semantic merging. Earlier guide versions and outputs remain preserved. |
| 4 — complete | Preserve the 26 Cursor batches; three authorised Codex reviewers completed the 49 missing batches. Codex assembled the reference and coordinated consistency corrections. | All 750 letters reviewed. Conor resolved the remaining source ambiguities, ending with 15672: one to two per year applies to generalised tonic–clonic seizures only. The reference has 2,097 findings, all in complete letters, including 42 empty inventories. The [execution record](../research/gan2026/one_shot_execution_record.md#source-15672-annual-rate-adjudicated-2026-09-22) owns coverage and provenance. Clinical validation remains separate. |
| 5 — complete | Freeze and implement Finding Purist beside the exact matcher, then rescore the saved R7 and R8 dev750 inventories. No new model call. | `finding_purist_v1` and `tests/test_finding_purist.py` cover same-band, different-band, period, status, qualitative, seizure-free duration, event, and timing. R8 is 1,226/1,792 precision and 1,226/2,097 recall; R7 is 993/2,197 precision and 993/2,097 recall. The exact scores were reproduced beside them. The [execution record](../research/gan2026/one_shot_execution_record.md#finding-purist-dev750-rescore-2026-09-22) owns the counts. |
| 6 | If the seizure annotation process works well, extend it to medications, diagnoses and investigations. Conor and Codex define the extension and review its annotations. | Reviewed four-family development reference and a frozen paired comparison of seizure-only versus all-four-family extraction on the original frequency-label endpoint. |
| 7 | Conor provides the reviewed dataset and guidelines to Yujian Gan and asks whether the King's College London Hospital annotators are willing to apply the expanded annotation to real patient letters. | Collaborator feedback and agreed clinical annotation scope, permissions and review procedure; no willingness or real annotation assumed in advance. |
| 8 | Conor/custodian and evaluation collaborator freeze and execute the authorised real-letter study; manuscript contributor completes the paper. | Separate real and synthetic results, finding measures supported by the references actually obtained, native answer agreement, time per letter and declared limitations. |

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
