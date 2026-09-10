# Pilot review and scoring dry run

Updated: 2026-09-09. P2.6 remains incomplete. The earlier agreement, timing and
field-sensitivity claims are withdrawn: the script supplied constants without a
saved independent annotation pass, timing records or field-ablation experiment.
They must not inform schema changes, effort estimates or publication claims.
The old machine-readable report is marked withdrawn.

This document owns the correction record and remaining review work. The
[task definition](task_definition.md) owns query logic; the
[annotation guide](annotation_guide.md) owns annotation meaning. The current
[current computed summary](../../results/longitudinal/pilot_v0.3/pilot_dry_run_report.json)
records input hashes, program hash, provenance and per-patient baseline scores.

## Current authored coverage revision: v0.3

Cases 002, 005, 007, 011 and 012 now have explicit, versioned fictional content for
missing coverage. Their v0.2 files remain in the source snapshot; this revision
intentionally changes source text rather than relabelling unchanged evidence.
Query dates are preserved. The pack has 210 assertions, 49 links and 125 reference
spans/paragraphs. One administrative letter has an explicit no-assertion reason.
There are 39 eligible, 21 ineligible and 180 indeterminate answers; every query has
at least two of each status. Fourteen of 120 view pairs differ. The
[coverage matrix](pilot_coverage_matrix.md) maps every required feature to cases.

The [48 independent-pass jobs](../../results/longitudinal/pilot_v0.3/independent_pass/README.md)
contain permitted letters, instructions, schemas and queries only. Every job must
run in a fresh context without existing references. No job has been run. Research
metadata and timing records remain separate; no independent measurements exist.
The v0.3 checks pass all 12 focused tests; full suite is 792 passed with the same
pre-existing architecture drift failure. Lint, types and documentation checks pass.
All 48 job hashes and exact permitted input copies were verified.

## Historical correction: v0.2

The pilot contains 12 authored patients, 36 unchanged fictional letters and 240
requests. Cases 002–012 now retain their original first index, place the second
index exactly 180 days later, and use R = T + 180. All inputs include exact text,
visit date and availability date from the permitted source letters. These are
corrections to an existing authored schedule, not evidence of prospective sampling.

All 220 answers in cases 002–012 were reassessed by the authoring assistant against
that schedule. Missing history is indeterminate; current medication use is not an
initiation history; a current absence statement does not cover an unobserved
interval; one pending investigation does not exclude other qualifying requests.
Patient 010's agreed medication plan is indeterminate at T1. The later letter
confirms initiation for the retrospective account. Original case 001 is preserved.

The annotations now contain 202 assertions and 44 relationships, with assertions
in all 36 letters. They include later event reports, explicit absence intervals,
medication proposals and use, test requests and results, copied statements and
unresolved reporter disagreement. Uncertain identity links remain uncertain.
Evidence uses 112 reference paragraphs/spans; paragraph selections deliberately
retain context and are not a claim of minimal evidence selection.

| Reference status | Count |
| --- | ---: |
| Eligible | 34 |
| Ineligible | 17 |
| Indeterminate | 189 |

Ten of 120 matched visit/retrospective pairs differ (8.3%). Constant-status
baselines are calculated from exact status matches, averaged within patient and
then across patients: always eligible 14.2%, always ineligible 7.1%, always
indeterminate 78.8%. These are arithmetic baselines on authored development
references, not extraction results or clinical performance. The high unknown
rate exposes missing evidence and unmet pilot coverage targets; it is not a
reason to invent negatives or tune references to a target distribution.

## What was verified

The case validator checks unique IDs, source hashes, the complete request grid,
fixed dates and query parameters, exact filtered input content, evidence offsets,
answer coverage and evidence cutoffs. It delegates annotation checking to the
canonical checker, including link endpoints, link evidence and numerical/date
bounds. Corruption tests exercise the public case validator, not only its helper.

Verification on 2026-09-09: 12 focused tests pass. The full always-on suite has
792 passes and one pre-existing architecture-document drift failure (gan-2166).
Ruff, mypy (399 source files), documentation hygiene and diff formatting pass.
All 36 original letter hashes match; the summary reproduces exactly and the
derived-file rebuild is idempotent.

The previous clinical authoring script duplicated every letter and annotation in
Python and could overwrite the corrected references. Canonical authored content
now lives in the case files. `build_patient_case.py` rebuilds only derived inputs
and README tables; it does not infer clinical answers or regenerate letters.

## Remaining work before P2.6 completion

1. Arrange a separate annotation pass on the permitted letters and guide without
   exposing the existing references or hidden scenario descriptions. Save annotator
   identity/model and configuration, raw outputs, start/end times and any repairs.
   A repeat pass by this authoring assistant is not independent evidence.
2. Compare saved assertions by family, time and relationships, as well as all 20
   answers per patient. Preserve disagreements and acceptable alternative evidence
   explanations; unresolved status remains indeterminate.
3. Decide explicit conventions for fuzzy seasonal/holiday dates. This correction
   keeps unsupported endpoints null and records the wording. It does not invent
   narrow bounds. This conservative representation may be revised after review.
4. Independently check the authored [coverage mapping](pilot_coverage_matrix.md).
   The minimum case/status counts are now represented. Patient 008 still keeps
   later relapse outside its fixed query inputs; 002 L3 explicitly supplies no
   clinical update. Do not infer clinical negatives from that administrative letter.
5. Measure field utility with an actual comparison before deleting fields. Retain
   strict quantity inclusivity: “over fourteen months” differs from exactly fourteen.
   Sub-day timestamps were never a field in this date-only schema. No schema v0.2
   simplification or claimed percentage effort saving is supported by this review.

Independent agreement, annotation effort and field utility are null in the
summary. No paid model calls, expert review or holdout inspection occurred.


## Predeclared independent AI pass through agy (2026-09-09)

Question: where does a fresh Gemini annotation disagree with the authored v0.3
reference on the fixed 240 requests and supporting clinical assertions?
Use the 48 hashed, reference-free jobs, all development-only; no row exclusions.
Comparator: unchanged authored v0.3 references. Model: gemini-3.8-flash-high via
agy, high effort, new context for every job, isolated temporary working directory,
no reference files or repository context, no tools requested. Abort a job on
unexpected tool use, authentication, quota or isolation failure. No paid API fallback.
The user explicitly directed use of agy; no additional paid-call budget is added.

First run one representative job to check output capture and isolation, then
continue the same input/model configuration for the remaining jobs if usable.
Save original input hashes, requested model, CLI identity, actual UTC start/end,
wall seconds, exit status and untouched stdout/stderr. Provider-reported usage
and model identity are recorded if returned; absent values remain unknown.
No retries based on clinical disagreement. Format parsing may remove a surrounding
JSON code fence only; no semantic repair or reference revision during this pass.

Primary result: patient-averaged exact query-status agreement, with missing or
invalid answers counted as failures, not exclusions. Also report per-query/view
counts, confusion matrix, evidence validity and an inspectable disagreement list.
For assertions/links, report validity and explicit matching limitations; do not
invent kappa where independently aligned units are absent. Model wall time is
not human effort or per-family annotation time. No field-utility claim without
an actual field comparison. A positive result supports only AI development
agreement on this authored pack; P2.6 human effort/clinical validity remain separate.


Instrumentation correction: three jobs emitted error_message events, which the
initial monitor incorrectly classified as tool use and terminated before the
final error detail. These attempts are retained separately. Permit error_message
for error capture (not as successful annotation), then retry one identical job
in a fresh context. Stop before further jobs if the failure persists. This is a
transport/instrumentation retry, not a clinical-output retry or prompt revision.


The diagnostic retry returned ERROR with an explicit output-token-limit message.
The CLI reported 61,005 thinking tokens and 70,960 total output tokens, including
its automatic continuation. No repaired/truncated output is accepted as a completed
annotation. High-effort captures remain under agy_pass for provenance.

Before further annotation, change only the requested model/effort to
`gemini-3.8-flash-medium` / medium in a separate `agy_pass_medium` run. Preserve
the exact prepared inputs and wrapper instruction. Test the two-letter job that
exposed the limit, then run all 48 jobs under this one configuration if usable.
Do not mix high-effort outputs into the medium run. This is an instrumentation
revision based on token-limit failure, not optimization against clinical answers.


## agy medium pass: interrupted capture (2026-09-09)

The run stopped on transport errors: 14 of 48 jobs produced parseable responses,
three attempted jobs ended with `The stream was interrupted`, and 31 were not
started. Raw traces, per-attempt configuration and hashes are retained under
`results/longitudinal/pilot_v0.3/agy_pass_medium/attempts`; `analysis.json` owns the
machine-readable partial audit. No failed output was repaired or substituted.
No observed tool steps occurred in accepted captures. The CLI advertised tools;
monitoring actual steps does not establish that tools were unavailable.

Among the 70 returned query answers, 65 statuses match the provisional authored
references and five disagree. This is a partial count, not the predeclared
patient-averaged full-pass result: that result remains null. Only 27 of these
answers pass the exact evidence check; four of 14 annotation objects pass both
schema and evidence validation. Status agreement does not establish valid evidence.
The audit separately records quote presence and exact character-offset validity.
Assertion comparisons use unique identical letter/content pairs only; differing
wording is not automatically a clinical disagreement. No kappa is calculated.

The five query disagreements identify two interpretation questions for adjudication:

- Patient 002, T2 retrospective, Q2 and Q4: the model treats statements about
  unchanged patterns and no investigations as complete inventories over the
  lookback. The reference does not infer full-window completeness from them.
- Patient 003, Q5 in both T1 views and Q2 at T2 retrospective: the model retains
  indeterminate because explicit revision/inventory documentation is absent;
  the reference uses global seizure freedom to exclude qualifying events.

References and instructions remain unchanged. These disagreements need explicit
review of temporal coverage and negative-answer logic before any revision. The
next capture decision is operational: diagnose stream interruption and predeclare
how to resume the 31 unstarted jobs while retaining all three failed attempts.
Do not retry selectively based on clinical answers. Human annotation effort,
field utility and clinical validity remain unmeasured; P2.6 remains open.

Verification: 14 focused tests passed; Ruff and mypy passed. The full always-on
suite returned 794 passed and one failure in the existing generated teaching-case
consistency check (`gan-2166.md`); that unrelated artifact was not regenerated.


## User-authorized adjudication: pilot v0.4 (2026-09-09)

Scope: the five saved query-status disagreements, adjudicated by the authoring
assistant against permitted letters and task v0.2. This is development reference
review, not an independent clinical adjudication. No model calls or raw-output
repairs were made. Evidence-offset policy is separate and unchanged by this review.

| Patient / request | Original reference | Model | Decision | Reason |
| --- | --- | --- | --- | --- |
| 002 T2 retrospective Q2 | indeterminate | ineligible | Retain indeterminate | L2 reports an unchanged named pattern and excludes named alternatives since February, but does not explicitly inventory every active epileptic pattern throughout 12 May–9 August. |
| 002 T2 retrospective Q4 | indeterminate | ineligible | Retain indeterminate | “No investigations were requested” describes the 15 August visit, after T2 on 9 August; it does not exclude requests during 11 February–9 August. L3 supplies no clinical update. |
| 003 T1 visit Q5 | ineligible | indeterminate | Correct to indeterminate | L1 seizure freedom does not inventory previously epileptic-labelled episodes later reclassified. No dated revision or complete reassessment history is supplied. |
| 003 T1 retrospective Q5 | ineligible | indeterminate | Correct to indeterminate | L2 adds a May breakthrough after T1, not a reassessment history for T1. It does not resolve the missing revision evidence. |
| 003 T2 retrospective Q2 | ineligible | indeterminate | Retain ineligible | L3 explicitly excludes seizures of any kind from 29 May to 18 September, covering the full 31 May–28 August window. No additional pattern inventory is needed. |

The two corrected Q5 statuses are in patient 003 reference v0.4. Other statuses,
letters, annotations, request dates and frozen model inputs are unchanged.
Original references and manifests for all 12 cases are preserved under
`results/longitudinal/pilot_v0.3/reference_snapshot/`. The original-pass analyzer
now reads that snapshot, preventing later reference edits from silently changing
its five-disagreement result. The guide and task amendment explain the shared
negative-answer rules.

Current reference summary: `results/longitudinal/pilot_v0.4/pilot_dry_run_report.json`.
There are 39 eligible, 19 ineligible and 182 indeterminate answers; all queries
retain at least two examples of each status. On the same 70 returned statuses,
two reference corrections would raise agreement from 65 to 67, leaving three
model disagreements. This is a post-adjudication count on inspected development
outputs, not an independent performance improvement or full-pass score.
P2.6 remains open; incomplete capture, field utility and human effort are unresolved.

Adjudication verification: 15 focused tests passed; Ruff (src, tests and
longitudinal scripts), mypy and diff whitespace checks passed. Full always-on
suite: 795 passed, with the same pre-existing stale `gan-2166.md` generated-document
failure. That unrelated teaching-case artifact was left unchanged.


## Evidence audit v2 (2026-09-09)

Implements the user-approved flexible evidence standard on saved outputs only.
`results/longitudinal/pilot_v0.3/agy_pass_medium/analysis_evidence_v2.json`
is separate from the original strict-offset `analysis.json`; both retain the
original v0.3 reference comparator and unchanged query-status results.

All 14 parsed annotation objects pass structure and source-grounding checks.
Among 70 returned answers, 64 contain evidence, all source-grounded; six contain
no evidence. Fifty-five have nonempty evidence with every selection overlapping
a reference passage under same-letter normalized containment. Nine evidenced
answers do not meet that reference-overlap test; this is not automatically a
clinical error, since alternative supporting passages can be acceptable.
The original offset check passes 27 answer rows, including empty evidence lists;
it measures bookkeeping and must not be presented as clinical validity.

No raw output or clinical meaning was repaired. No new model calls were made.
The earlier four-of-fourteen strict-validity count is superseded for evidence
acceptability by fourteen-of-fourteen source-grounded annotation objects, not
by a claim that all clinical assertions are correct. Human effort, clinical
validation, full capture and field utility remain unresolved.

## Predeclared resume of unstarted jobs (2026-09-09)

User requested continuation. Resume only the 31 jobs without a saved attempt,
serially to reduce concurrent transport load. Preserve all 17 previous attempts,
including three failures; do not retry or replace failed clinical outputs.
Use the same hashed inputs, wrapper, medium model/effort and timeout. Stop on a
new failure. Save resume progress separately from the original capture summary.
This is an operational scheduling change, not a prompt or reference optimization.
The evaluator continues to use the original reference snapshot; adjudicated
references remain separate. No paid API fallback is authorized.


The nine original non-overlap answers were inspected during resume. All nine
are patient 001 answers with grounded, relevant alternative selections. The
review accepts them as alternative evidence explanations, including explicit
recognition of incomplete follow-up for indeterminate answers. Decisions are
saved in `agy_pass_medium/alternative_evidence_review.json`; this manual
interpretation does not change the automatic overlap metric or any raw output.


## Serial resume outcome (2026-09-09)

One additional job, patient 005 T1 retrospective, returned parseable output.
Patient 005 T2 visit then failed with the same stream-interruption error; the
serial resume stopped. Totals are now 15 parsed, four failed and 29 unstarted.
Serial scheduling did not resolve the transport failure. Original failures were
not retried. `resume_capture_summary.json` preserves these two new attempts.

The refreshed evidence-v2 audit has 75 returned answers, all with grounded
supplied evidence where present, and 15 structurally valid, grounded annotation
objects. The original-reference comparison now has seven disagreements among
75 returned statuses (68 matches). Two of the original seven have already been
resolved by the separately versioned v0.4 reference corrections; the new Q1/Q2
disagreements for patient 005 remain unadjudicated. Q1 concerns interpreting
“around Christmas” within the November–February window; Q2 concerns whether
reported absence of other patterns constitutes a complete whole-window inventory.
Full-pass agreement remains null. No new clinical-validation claim is supported.

Further capture requires diagnosing the agy stream failure rather than repeating
this unchanged invocation. No paid API fallback or prompt change was attempted.
Only local artifact/document updates were made in this continuation; diff whitespace
checks passed. The previous code verification remains applicable.

## Sleep-interruption diagnosis and probe (2026-09-09)

All four medium failures show wall-clock durations exceeding process-monotonic
elapsed time by 209–354 seconds. The latest attempt ran 21:47:02–21:54:04 UTC;
macOS records maintenance sleep from 22:47:33 to 22:53:30 local (+0100), directly
inside that attempt. This supports host sleep as the interruption mechanism;
it does not prove absence of provider errors. Serial scheduling did not address it.

Predeclare one fresh-context retry of patient 005 T2 visit under `caffeinate -is`,
with the identical input, model, wrapper and timeout. Keep this diagnostic retry
in `agy_sleep_probe`, separate from the original failed attempt and primary score.
The assertion lasts only for the command; it does not change system settings or
prevent explicit software/lid sleep. If successful, resume unstarted jobs with the
same temporary assertion. No retry selection based on clinical disagreements.

The sleep-prevented diagnostic succeeded in 51.4 seconds with no clock gap and
no observed tool use. Resume the 29 unstarted jobs under the temporary sleep
assertion with the original three-worker scheduling. This changes host availability,
not model or clinical inputs. Stop scheduling on any new failure. The diagnostic
retry is excluded from primary results; original four failures remain failures.


## Completed attempt coverage (2026-09-10)

The sleep-prevented resume completed all 29 unstarted jobs without failure.
Every one of the 48 jobs now has a primary attempt: 44 parsed, four original
sleep-associated failures, zero unstarted. The separate successful retry probe
is excluded from primary scoring. Raw traces and original inputs are unchanged.
The temporary sleep assertion ended with the command; system settings were not changed.

`agy_pass_medium/completion_summary.json` owns the compact final counts;
`analysis_evidence_v2.json` contains every answer, evidence diagnostic and
literal assertion comparison. The frozen v0.3 reference comparison has 206/240
status matches, giving patient-averaged agreement 0.858333. All 20 requests lost
to four failed calls count as failures, as predeclared. Among 220 returned
answers, 14 disagree with v0.3; two are the previously adjudicated patient 003
reference errors. Twelve disagreements remain against the current v0.4 reference.
This is AI development agreement with provisional authored references, not
clinical accuracy, human agreement or holdout performance.

All 44 annotation objects pass schema and source-grounding checks. Of the 220
answers, 194 supply grounded quotations and 26 supply none. For 178 answers,
every selection overlaps a reference passage under the stated containment rule.
The nine previously reviewed alternative explanations remain recorded separately;
new overlap misses have not been automatically adjudicated.

Across repeated job/view inputs, the literal comparison contains 522 reference
and 506 observed assertions, with 202 unique exact letter/content matches.
On those pairs, exact time-object agreement is 15/202, reporter 171/202,
certainty 200/202, polarity 200/202 and coverage 191/202. These are exact object
comparisons on a restricted matching subset, not semantic field accuracy.
Differing time wording or representation can fail equality without a clinical
boundary error; semantic temporal review is still needed. No field should be
deleted based on these numbers. Relationships are compared only on matched
endpoints in the detailed artifact; incomplete matching precludes a general
link-accuracy claim.

The remaining query disagreements concern complete-window pattern inventories
(Q2), fuzzy holiday dates and retrospective resolution of reporter conflict
(Q1), medication initiation versus prior use or ongoing therapy (Q3), and the
previously retained visit-level investigation negative (Q4). Adjudicate these
against the full permitted window before revising more references. Full attempt
coverage is complete; P2.6 remains open for this review, temporal/relationship
interpretation, field utility and any genuinely human effort measurement.

This continuation changed saved artifacts and documentation only. Diff whitespace
checks passed. Previous verification remains 796 tests passed with the unrelated
stale `gan-2166.md` failure, plus passing Ruff and mypy.


## Remaining status adjudication completed: v0.5 (2026-09-10)

All 12 remaining disagreements have a recorded development adjudication in
`results/longitudinal/pilot_v0.5/status_adjudication.json`. Three model answers
exposed reference defects; nine original references are retained. The reviewer
is the user-authorized authoring assistant, not an independent clinical expert.

Corrections: patient 005 T1 retrospective Q1 becomes eligible because “around
Christmas” is clearly within the broad November–February window without assigning
an exact day. Its Q2 becomes ineligible because L1 explicitly excludes all other
patterns in the recurring history. Apply both decisions to T1 visit, whose
permitted text is identical. Patient 010 T2 retrospective Q3 becomes ineligible:
confirmed initiation on 18 January plus reliable use and subsequent “remains
compliant” support one ongoing course across the later index. T2 visit remains
indeterminate because it lacks the later continuity evidence.

Retentions: the three earlier retained decisions (002 Q2/Q4 and 003 Q2) stand.
Patient 005 T2 Q2 and patient 011 T2 Q2 in both views lack full-window coverage.
Patient 006 T1 retrospective Q1 lacks a supported resolution of the specific
February episode; June video confirmation is insufficient. Patient 006 T2 Q3
lacks the confirmed start/continuity history supplied in patient 010. Patient 012
T2 Q3 cannot derive full-window non-initiation from a November no-change statement.
The machine record includes per-request reasons and reference evidence IDs.

Five total reference answers change, in patients 005 and 010, now reference v0.5.
All prior references/manifests are preserved in `pilot_v0.4/reference_snapshot`.
Letters, annotations, exact date schedules, frozen inputs, original model outputs
and the original 206/240 score are unchanged. The resulting reference distribution
is 41 eligible, 22 ineligible and 177 indeterminate; each query still meets its
minimum of two examples per status. This is not a measured model improvement:
the reference was reviewed using inspected development outputs. All returned
status disagreements are now reviewed; semantic temporal/relationship review,
field utility and human effort remain separate P2.6 work.

V0.5 verification: 16 focused tests passed, including the expanded existing
adjudication boundary test. Ruff and mypy passed. Full always-on suite: 796 passed,
with the same unrelated stale `gan-2166.md` generated-document failure. Current
reference view differences are 15/120; the additional difference is patient 010 Q3.

## Temporal, relationship and field-purpose review (2026-09-10)

`pilot_v0.5/temporal_relationship_audit.json` records all 202 uniquely
content-matched assertion pairs and all permitted links across successful jobs.
Reproduce with `python scripts/longitudinal/audit_temporal_relationships.py`.
Normalization ignores time-expression wording and equates a null endpoint with
an endpoint whose two bounds are null. It never changes a date, kind or anchor.

Fifteen times match exactly; 43 additional pairs differ only in representation.
Fifty-six differ in bounds and 88 in kind or anchor (possibly also bounds).
These 144 are unresolved semantic candidates, not 144 demonstrated errors.
The matching subset excludes differently worded content and repeated matches;
counts repeat assertions across views and must not be called patient-level rates.

Representative inspection:

- Patient 001 L1 pending EEG: “not yet” versus null time wording has identical
  as-of date and anchor. Accept as equivalent representation.
- Patient 001 L2 non-initiation: null start versus two null start bounds encodes
  the same unknown endpoint. Accept as equivalent representation.
- Patient 001 T2 retrospective L2 staring reinterpretation: the observed assertion
  uses the 20 June decision date where the reference preserves the November–June
  active interval. Its correction link correctly records 20 June as decision_time
  and its evidence quotes the retrospective onset scope. This is a structured
  interval omission, not an unsupported correction or missing source evidence.
  A future graph consumer cannot assume the raw answer's correct reasoning repairs
  that omitted interval. Keep assertion time and link decision_time separate.
- Patient 001 medication proposal represented as decision versus as_of is a
  convention difference to clarify. It does not by itself turn the proposal into
  actual initiation; medication status must remain decisive for Q3.

Permitted link instances: 97 reference, 111 observed. Only 20 reference and 37
observed links have both endpoints aligned by unique identical content. The other
77/74 are unaligned, not automatically missing/spurious clinical relationships.
The artifact exposes all raw link evidence, relation and decision_time for review.
Do not publish link accuracy from this restricted alignment. Semantic alignment
must handle differently granular assertions before comprehensive adjudication.

### Field-purpose assessment

This is a source-backed dependency review, not a measured field-deletion ablation.
There is no implemented structured-annotation-to-Q1–Q5 evaluator yet: the current
scoring dry run reads saved answers. Deleting a field from annotations and observing
unchanged saved answers would falsely claim that field is unnecessary.

| Field group | Supported purpose | Decision |
| --- | --- | --- |
| Source IDs, evidence text, availability | Grounding, cutoff filtering, inspection of all queries | Retain; offsets are bookkeeping and may be computed from quotes rather than model-counted in a future schema revision. |
| Assertion status, polarity, certainty, reporter | Distinguish proposal/use, epilepsy uncertainty and reporter conflict; patients 001, 006, 012 | Retain; no voting away unresolved disagreement. |
| Time bounds, kind, anchor | Q1–Q4 windows, delayed results and uncertainty | Retain; clarify event/state versus decision conventions. |
| Pattern identity, coverage, relationships | Q2 inventory and Q5 reinterpretation; patients 001/011 | Retain; exact-content matching is inadequate as the semantic alignment method. |
| Link decision_time | Q5 decision by T versus later reinterpretation | Retain separately from assertion valid interval. |
| Source time wording | Audit holiday/relative expressions without invented bounds | Retain for explanation even when ignored in representation comparison. |
| Burden count/range/period and cluster detail | Longitudinal burden history; patient 011 distinguishes clusters from constituent seizures | Not directly required by these five status predicates, but explicitly part of the history task. Retain provisionally; do not infer measured query utility or effort savings. |

No field is removed on the basis of unchanged stored answers. Actual per-family
human annotation effort remains unmeasured; total model latency cannot supply it.
The next bounded implementation should exercise structured assertions and links
through a query evaluator, beginning with the inspected patient 001 correction
and its decision-date boundary. That enables a genuine field ablation before
promoting the full schema. P2.6 remains open for this evidence, rather than blocked
on a fabricated requirement for an expert review of this development prototype.

Review-tool verification: 17 focused tests passed. Full always-on suite: 797
passed, with the same unrelated stale `gan-2166.md` failure. Ruff, mypy and diff
whitespace checks passed. No new model calls or raw-output repairs were made.

## Executable Q5 field comparison (2026-09-10)

The first structured evaluator is `scripts/longitudinal/evaluate_q5_slice.py`.
It uses schema-valid assertions, evidence, correction endpoints, clinical time,
decision time and permitted document availability; it does not read stored answers
to decide a status. This is a patient-001 positive-witness prototype, not a complete
Q5 implementation or a general clinical evaluator. Explicit endpoint contradictions
cause abstention; conflict-resolution traversal and complete negative inventories
are not implemented. No model calls were made.

`pilot_v0.5/q5_field_ablation.json` records all four requests under four variants,
with source/program hashes and witness evidence. The full evaluator returns
indeterminate, indeterminate, eligible, eligible in T1 visit, T1 retrospective,
T2 visit, T2 retrospective order. Three of four match the provisional reference.
Removing correction links changes both later answers to indeterminate. Removing
link decision_time causes the same two changes. Removing only time.text changes
no answer. These are measured decision changes on four development requests,
not general field-utility estimates, clinical accuracy or annotation-effort savings.

The mismatch is informative: T1 retrospective is reference-ineligible because
the letter explicitly calls 20 June the first reinterpretation. That exclusivity
is not encoded in a structured assertion or link field. A single correction after
T cannot establish that no earlier correction occurred. The evaluator therefore
returns indeterminate rather than reading the raw quote with an ad hoc phrase rule.
The next schema experiment should represent supported revision-history coverage
separately from the time of one correction, then test that boundary. It must not
infer complete history from the existence of one dated link.

Retain links and decision_time: they demonstrably change the two positive Q5
answers in this slice. Time wording remains useful for audit and uncertain-date
interpretation even though this already-normalized replay does not consume it.
This experiment supplies the first genuine field comparison; it does not close
P2.6's broader temporal/link review or human-effort questions.

Q5 slice verification: 18 focused tests passed; full suite 798 passed with the
same unrelated stale `gan-2166.md` failure. Ruff, mypy and diff whitespace checks
passed. Tests cover field removal, decision-date boundaries, cutoff filtering and
explicit endpoint conflicts.

## First-reinterpretation field experiment (2026-09-10)

Schema/guide v0.2 adds optional `first_reinterpretation_evidence` to correction
links. It records quoted support for the first reinterpretation anywhere in the
patient history; a pattern-specific first correction is insufficient. Other link
types cannot carry nonempty values. The source/evidence validator checks these
spans too. The existing explicit quote is annotated on patient 001 K1; no letter,
reference answer or frozen agy input is changed. Previous schema, guide and case
annotations/manifest are saved under `pilot_v0.5/schema_snapshot`.

The Q5 evaluator now uses a supported decision date wholly after T together with
that explicit patient-wide evidence to establish a negative. Missing evidence,
invalid quotes, unavailable letters, uncertain dates crossing T, or contradictory
positive and negative witnesses do not produce that negative. It does not infer
completeness from the existence of a single dated correction.

`pilot_v0.6/q5_field_ablation.json` records the five-variant replay: full structured
input matches all four patient-001 Q5 references. Removing the new field changes
only T1 retrospective from ineligible to indeterminate. Removing correction links
or decision_time changes all three determinate answers to indeterminate. Removing
time wording changes none. This is evidence of necessity for this evaluator and
example, not broad query accuracy or measured human annotation savings.

Plain-language audit: the rendered v0.2 schema input preview was inspected at
`pilot_v0.6/schema_v0.2_input_preview.json`. The field uses a short, explicit
patient-wide definition; research metadata is separate; omission means unknown;
no unexplained new terminology or controlled wording deviations were introduced.
The preview is not a new model run. No provider compatibility claim is made.

Next representative case: patient 011's explicitly first reinterpretation, followed
by boundary/partial-date and conflicting-history cases before broader migration.
The evaluator still does not implement all Q5 negative mechanisms or Q1–Q4.

Verification: 18 focused tests passed, including missing/invalid evidence and a
decision interval crossing T. Full suite: 798 passed with the same unrelated
stale `gan-2166.md` failure. Ruff, mypy and diff whitespace checks passed.
