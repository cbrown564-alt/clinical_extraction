# One-call study execution record

## R7 rich dev750 first attempt and no-response reruns (2026-09-14 to 2026-09-16)

`scripts/benchmarks/run_r7_dev750.py` (`prepare`, `run`, `replay`) executed the
finalised R7 rich candidate (`one_shot_frequency_v2_measurements_r7`, revision
`simplified_dates_v1`) on all 750 synthetic dev750 rows with DeepSeek V4.1 Flash,
thinking enabled/low, 24,000-token limit, concurrency 12, a 600-second request
timeout and no retries or repairs. The run was prepared on 2026-09-14 at 19:37 and
finished on 2026-09-15 at 07:11; it was executed before this record was written,
and the 2026-09-15 status line "r7 has no benchmark evaluation" was stale from that
point. Scoring is the native Purist/Pragmatic answer measure plus the whole-record
strict view (record schema-valid and answer correct).

First attempt: Purist answer 526/750 (70.13%), Pragmatic 537/750 (71.60%); strict
Purist 508/750 (67.73%), strict Pragmatic 516/750 (68.80%). Failures: 151 no
response, 21 invalid schema, seven invalid target labels; all count as wrong.
The 151 no-response rows were 108 client `ReadTimeout`, 35 provider error payloads
("unable to start processing your request within the 900-second timeout limit"),
two HTTP 503, three `ReadError`, one `RemoteProtocolError` and two returned
completions with empty content after reasoning. Successful requests took a mean of
29.9 seconds (maximum 70.5); the `ReadTimeout` requests hung for 1,683 to 7,308
seconds before failing, so provider capacity on the night of 2026-09-14, not the
600-second limit, caused the failures. Conservative first-attempt charge:
US$13.0313082; cumulative study charges US$42.213597 of US$100. Offline replay was
byte-identical for the aggregate and diagnostics.

On 2026-09-16 Conor authorised one rerun of the failed requests at 600 seconds.
`scripts/benchmarks/rerun_r7_no_response.py` (`prepare`, `run`, `replay`; run as
`python -m scripts.benchmarks.rerun_r7_no_response`) verifies the frozen r7 identity
and saved request bodies, hashes the six original artifacts, and reruns only the
149 requests that returned no model output: the transport errors and provider error
payloads. The two empty-content completions are returned outputs and were not
rerun, matching the r4/r5 rule that returned failures stay as they are. Request
bodies, model settings, scorer and no-repair policy are unchanged. All 149 finished
in about 7.5 minutes; 146 returned and three failed again with `ReadError`. Mean
rerun request time was 32.6 seconds. Conservative rerun charge: US$1.8573933;
cumulative study charges US$44.0709903 of US$100. No attempts were outstanding.

Mixed-attempt view (original usable responses plus single reruns; all 750 rows):

| View | Purist answer | Pragmatic answer | Strict Purist | Strict Pragmatic |
| --- | --- | --- | --- | --- |
| r7 rich, first attempt | 526/750 (70.13%) | 537/750 (71.60%) | 508/750 (67.73%) | 516/750 (68.80%) |
| r7 rich, no-response reruns | 650/750 (86.67%) | 668/750 (89.07%) | 619/750 (82.53%) | 634/750 (84.53%) |

Residual failures in the mixed view: 36 invalid schema, five no response (three
`ReadError`, two empty completions) and seven invalid target labels. The 31-row
gap between the answer and strict views comes from schema-invalid records whose
declared answer was correct; 36 records were schema-invalid in total, against two
in the r5 rich mixed view. This is a mixed-attempt development view under a changed
schema, not a fresh first-pass run and not a matched comparison with the r4/r5
timeout-completed views, whose reruns selected `ReadTimeout` only. Classification
of the schema failures and rich/simple disagreements remains the pending roadmap
step; no rows were repaired, and no locked-test rows were used.

Raw first-attempt artifacts: `runs/one_shot_frequency_v2_measurements_r7/dev750/`;
reruns and original-request links: `.../dev750/timeout600/` with the merged view in
`timeout_completed/`. Reviewed aggregates:
[first attempt](../../../results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r7/dev750/)
and [mixed view with per-request timing](../../../results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r7/dev750_timeout600/).
Replay of both views was byte-identical.

Execution default: from 2026-09-16 the request timeout for new one-call runners is
600 seconds. Frozen modules keep their recorded values (`one_shot_study` 180 s,
`one_shot_thinking` 300 s) because their identities are checked against saved plans;
new runners set 600 seconds explicitly and record it in their plan.

## Grok batches 013–146 initials under v0.6 (2026-09-15)

Grok 4.6 (`cursor-grok-4.6`, no AGY effort flag) saved first valid initials for
the remaining 666 Gan synthetic dev750 letters (batches 013–146; batch 146 is
one letter). The segment contains 2,570 findings, 25 empty inventories and 48
`needs_review` letters. Each batch passed the frozen v0.6 structural checker
(`--expected 5`, batch 146 `--expected 1`). The 666-letter subset checker also
passed against its matching sources. The concatenated 750-letter v0.6 checker
fails only A01 on 34 historical records that still declare a pre-v0.6
`guide_version`; those initials were not rewritten.

`annotations/initial.jsonl` now holds 750 distinct source records (84 historical
plus the 666 new initials). Raw per-batch copies, provenance and checkers remain
in the local run. These initials are not an accepted reference. The accepted
34-letter/107-finding set is unchanged. Both required full750 reviews and C08
propagation remain pending. Source ambiguities 816, 1597 and 1640 stay open on
the 003–012 correction snapshot.

Source-bearing files remain local-only. No extraction code, scorer, frozen
package or locked-test inspection changed; repository tests were not rerun for
this annotation/documentation update.

## Batches 008–012 corrections and current totals (2026-09-15)

Codex applied the remaining source-specific corrections under v0.6: 25 letters
now contain 79 findings (previously 64). Twenty-three letters are adjudicable;
two retain the subtype-scope ambiguity selected by CB. Cluster occurrence and
size, omitted subsets, event identity, restricted absence and duplicate claims
are corrected without changing the original initials.

Across batches 003–012, all 102 proposals are implemented: 50 letters, 165 findings,
47 adjudicable letters/157 findings and three deliberately retained source issues.
Final A01–A09 review has 444 passing checks, six unresolved and no failures. All ten
structural checks and 165 isolated R7 finding parses passed, together with evidence,
source identity, proposal coverage and CB-decision checks. Final C01–C07 review
covers 42 groups/1,911 memberships and 12 explicit comparisons. Seven C08 screens
with 3,342 memberships still require wider full-source propagation review.

Including the earlier pieces, 84 reviewed letters contain 272 findings; 81 letters
and 264 findings are adjudicable. The previously accepted 34-letter/107-finding
set remains separately recorded. There are 666 unannotated letters, with batch_013
next in the assignment list. Both full750 reviews remain pending. These counts
are annotation progress, not clinical validation or benchmark performance.

The local correction report, summary, checks, changes and immutable snapshot hashes
are under the correction directory named below. Current per-batch paths are in the
run's `batches/manifest.json`; `progress.jsonl` and `TERMINAL_HANDOFF.md` point to the
corrected records. Source-bearing files remain local-only. No paid calls, locked-test
inspection or extraction-code changes were needed; repository tests were not rerun
for these annotation/documentation changes. Historical sections below retain the
counts and pending work at their original checkpoints.

## Batches 003–007 corrections implemented (2026-09-15)

Codex applied the source-specific review corrections in separate v0.6 snapshots:
25 letters now contain 86 findings (previously 76). Twenty-four letters are
adjudicable; the source date ambiguity selected by CB remains open in one letter.
The five batch structural checks pass. Explicit numeric quantities, conditional
recurrence, omitted event subsets, partial calendar windows and duplicate claims
are corrected with verbatim evidence and stable surviving finding IDs.

The local evidence owner is
`runs/seizure_finding_annotation_v0_2/agy_gemini38_high/reviews/codex/grok_batches003_012/corrections/`.
Its per-batch snapshots, attributed changes and proposal resolutions preserve the
raw Grok initials and the earlier CB snapshot. No extraction code, scorer, frozen
package or model output was overwritten; no model calls were made.

## Batch 003–012 domain decisions applied (2026-09-15)

CB selected 1A, 2A, 3A and 4A from the secondary review. Codex applied the choices
in a separate five-source partial snapshot under
`reviews/codex/grok_batches003_012/adjudication_CB_1A_2A_3A_4A/` in the local run.
The source date conflict retains unclear timing; both potentially overlapping
counts remain unchanged with issues and no sum. Named aura-event absence is
included, and duration-qualified convulsive-event absence retains its restriction.

All five records, now 15 findings, pass the frozen v0.6 checker and targeted
application checks. Three source ambiguities intentionally remain open; no domain
choice is awaiting a response. Other proposed batch corrections and full-set
reviews remain pending. The accepted reference stays at 34 letters/107 findings.
Grok initials, historical checks and their hashes are preserved. This is an
attributed source-annotation application on Gan synthetic dev750, not a schema,
scorer or model-output repair. No model calls or locked data were used.


## Grok batches 003–012 secondary review (2026-09-15)

Codex completed full-source secondary review of the 50 saved v0.6 initials:
140 findings across ten batches. All 50 structural checks and raw-initial comparisons
pass. The 450 A01–A09 judgements comprise 271 pass, 174 fail and 5 unresolved.
All ten batches need corrections before acceptance. There are 102 proposed review
items across 49 records, including evidence/context cleanup; these counts are not
a clinical accuracy estimate. Four domain questions remain in the local report.

Review evidence is under `reviews/codex/grok_batches003_012/` in the existing local
annotation run. `REVIEW.md`, `checks.jsonl`, `changes.jsonl` and `summary.json`
record source-specific proposals, original hashes and exact evidence. C01–C07
cover 38 generated groups/1,780 memberships, with 12 named comparisons. Seven C08
all750 lexical screens yield 3,342 candidate memberships; full-source propagation
outside these 50 letters remains pending. The candidate set is not an error count.

This is Gan synthetic dev750, all750 row policy including `row_ok=False`, annotator
recorded as Cursor Grok 4.6 (`cursor-grok-4.6`), effort unavailable, guide v0.6.
Offline rechecking used saved outputs and no scorer. No model calls, locked-row
inspection or raw-output repairs occurred. All corrections are proposed, not
applied; accepted reference pieces remain 34 letters and 107 findings. Initials
remain 84 with 666 unannotated. Full750 primary and secondary review remain pending.
Record hashes, exact quotations, raw preservation and group coverage passed.
Extraction tests were not rerun because this review changes no extraction code.



## Grok batches 003–012 initials under v0.6 (2026-09-15)

Grok 4.6 (`cursor-grok-4.6`, no AGY effort flag) saved first valid initials for
the assigned ten batches (50 letters: 003–012) using frozen
`guide_versions/v0.6_quarter/`. Quarterly recurrence is encoded as a native
duration unit where the source states it (source 1773: increase over the last
quarter plus 2 drop attacks and 9 convulsions in the past three months). The
v0.6 checker passed structurally on each five-letter file. There are now 84
initial records and 666 unannotated letters. These initials are not accepted
and are not a full-set review. Codex still owns independent secondary review
before throughput increases further.

## Native quarter implementation and concurrent continuation (2026-09-15)

The user authorised increased concurrency and assigned Grok the next ten batches
(003–012). Keep five-letter assignments, one writer per source and distinct batch
attempts; the coordinator merges shared manifests and progress. Do not dispatch
duplicate annotation work. Use frozen `guide_versions/v0.6_quarter/` for new
assignments. Already-running v0.5 assignments retain their actual package/version
and receive separate reviewed quarter reclassification where needed.

The separate R7 quarter candidate and annotation guide/schema v0.6 are implemented.
The schema decision owner records native-unit semantics and version isolation.
In the local annotation run, `batches/batch_002.adjudicated_v06.jsonl` records source
531's estimated 12–30 seizures per quarter as an approximate range rate per one
quarter. CB 1A remains applied. The other four records change wrapper version only;
all prior initials and reviewed snapshots remain preserved. Five letters, 18
findings and 45 final checks pass. Reviewed pieces still cover 34 letters and 107
findings; this does not claim completion of the externally assigned batches.

`reviews/codex/grok_batch002/quarter_verification.json`, `quarter_changes.jsonl`
and `checks_v06.jsonl` own the checks and attributed changes. A source-only dev750
lexical screen found 18 quarter-wording candidates including the reclassified 531;
the other 17 require full-source review, not automatic conversion. No scorer was
used: these are annotation/representation checks on Gan synthetic dev750, all750
row policy including `row_ok=False`, with no model calls, repairs to raw output or
locked-row inspection. Verification passed: 26 fictional candidate fixtures, 32
portable-package checks, 832 tests, Ruff and mypy (420 source files). Full-set
primary and secondary annotation review remain pending.

## Grok batch 002 secondary review (2026-09-15)

The user asked Grok 4.6 to annotate batch 002 while Codex finished batch 001.
The recorded runtime is Cursor Grok 4.6 (`cursor-grok-4.6`), with no AGY effort
flag. All five initials are preserved. There are 34 initials and 716 unannotated
sources. Codex completed a source-first secondary review and saved a separate
corrected snapshot: `batches/batch_002.codex_reviewed.jsonl` in the existing run.

The batch changed from 17 to 18 findings. Corrections added a missed named-event
absence and conditional subtype occurrence, separated hypothetical advice from
actual evidence, removed general deterioration as a frequency change, restored
joint scope/antecedents, removed false sleep/wake overlap links and retained
explicit approximation and document times. All five records pass the structural
checker. The 45 Codex checks comprise 43 pass and two unresolved judgements for
one source-specific issue in letter 531. Four letters are adjudicable; 531 remains
excluded pending Conor/domain interpretation of an aura-scope clause.

The report, exact issue/options, seven named reference comparisons, immutable
before/after records, propagation candidates and verification are under
`reviews/codex/grok_batch002/`. The report is `REVIEW.md`; `summary.json` records
review completion with one unresolved case. Both full-set reviews remain required.
The available Grok provenance does not include a complete raw conversation or
per-letter timing/usage; no missing metadata was invented. No model calls or
locked-row inspection were performed by Codex for this review.

CB subsequently selected option 1A for letter 531: exclude its aura clause as a
warning-feature description. Codex applied the decision in a separate
`batches/batch_002.adjudicated.jsonl` snapshot and verified five complete letters,
18 unchanged findings, zero issues and 45 passing final checks. Batch 002 is now
accepted. The original unresolved report and snapshot remain preserved; application
and the affected comparison are recorded beside the batch report. All 34 reviewed
letters are adjudicable under the current v0.5 conventions.

The user subsequently requested native quarter support in R7 for letter 531's
quarterly recurrence. The existing reviewed snapshot preserves the phrase under
v0.5; numeric reclassification was subsequently completed in the versioned change above.
Frozen schemas and original outputs are preserved. This is separate from the
resolved aura issue. This initial review changed no extraction code; the later
schema implementation has its own full verification above.

## Low-effort continuation and Grok 4.6 handover (2026-09-15)

The user authorised Gemini low effort, then replaced Gemini with Grok 4.6 as the
annotator and requested a documentation handover. Codex remains coordinator and
independent secondary reviewer. Grok will annotate the remaining sources and perform
the primary full-set review, including earlier Gemini annotations. Preserve the
Gemini high/low segments and their actual review scope. No Grok model call or runtime
configuration was tested; its provider model identifier, settings and access must
be verified and recorded before starting a new segment. Execution is paused for
handover, with no annotation process from this task left running.

The segment retains the frozen v0.5 guide/schema and source-only Gan synthetic
dev750 export, including `row_ok=False`. The accepted high-effort pilot remains
24 letters and 77 adjudicated findings. The new first batch saved five immutable
initial records with 14 findings. There are now 29 initial records in total and
721 unannotated letters; batch 002 has not started. The original 146 assignments
covered 726 letters at the segment's start.

All five initials passed the structural checker but required semantic corrections:
inferred counts from qualitative cadence, general condition changes treated as
frequency changes, a location used as an event time, event-identity errors and
insufficient antecedent evidence. Gemini's targeted correction pass saved five
records with 11 findings. Codex then saved three further source-specific corrections
in a separate five-record snapshot, also with 11 findings. All three batch snapshots
pass the offline checker. These are annotation counts, not benchmark scores or
clinical validation.

Batch 001 is now closed and accepted after Codex's final full-source reread. That
reread added one omitted named-event absence and completed explicit source exclusions:
five final letters, 12 findings, no open issues. The final snapshot is
`batches/batch_001.codex_final.jsonl`. All 45 A01–A09 Codex checks and seven named
comparisons against accepted pilot conventions are recorded. The original Gemini
review was normalized to keyed checks and actual snapshot hashes without changing
its 45 judgements; it retains its earlier scope and missed finding. No further
model call was made. The detailed batch report is `reviews/codex/low_batch001/REVIEW.md`.

An all750 lexical screen for the added omission pattern leaves 132 candidate
matches for full-source review during continuation; they are not proven errors.
The final batch checker, report/hash coverage, raw-initial preservation and
correction-chain checks passed. The reviewed pieces now cover 29 letters and
89 findings; full-set review remains pending. Grok batch 002 initials arrived in the shared workspace during closure; review
that new model segment before increasing throughput. The leading section owns
its current execution state.

The existing local run is
`runs/seizure_finding_annotation_v0_2/agy_gemini38_high/`. Its historical name is
retained. `TERMINAL_HANDOFF.md` contains the Grok handover, exact next assignment,
commands, rule reminders, runtime lessons and provenance paths. `manifest.json`
and `progress.jsonl` identify the separate adjudicated pilot and latest batch
snapshot; no final 29-letter reference has been assembled. The two setup attempts
produced no annotations; the third produced the five initials. A provider SUCCESS
on the second setup attempt did not mean annotation succeeded.

Handover verification rechecked all three batch snapshots, distinct initial/source
coverage, raw-initial preservation and manifest hashes. The initial handover check is preserved in
`reviews/codex/low_batch001/handoff_verification.json`; the final batch closure is
in `reviews/codex/low_batch001/verification.json`. Documentation hygiene passed.
No source annotation, earlier frozen package, benchmark output, scorer or extraction
code was changed for this handover. The portable guide was refreshed for the new
annotator and snapshotted separately as `guide_versions/v0.5_grok_handoff/`; the
clinical rules and JSON Schema remain unchanged. The stale wrapper version bullet
now agrees with the existing v0.5 schema. Full extraction pytest/Ruff/mypy were not rerun for
these documentation and run-metadata updates.

## Simplified workflow and completed pilot secondary review (2026-09-15)

At the user's request, Codex retired the unfinished automatic annotation runner
and simplified continuation to five-letter assignments, immutable initial records
and the existing offline checker. The failed runner/tests remain local historical
provenance; they are not part of the continuation path. No new model calls were
made during this simplification and final secondary review.

Codex reread all 24 complete pilot sources and completed 216 per-letter checks plus
38 comparison groups covering 1,476 pilot memberships. The final pilot contains
77 findings; 20 letters are adjudicable and four retain explicit source-specific
issues owned by Conor/domain reviewer. Corrections preserve qualified conditions,
source antecedents and the shared observation window. The complete change chain
and original initial annotations are retained. No new general clinical rule was added.

Gemini has saved per-letter self-review outputs for all 24, and its earlier
cross-sample report covers 23 sources/1,319 memberships. Codex checked the extra
letter and later corrections across the pilot; this is not described as Gemini
independently cross-reviewing the final 24-source snapshot. Both full750 review
passes remain required before the development reference is complete.

The pilot is accepted for staged continuation, starting with five letters. All 726
remaining sources are assigned once across 146 batches; none has a bulk initial.
Execution is paused for the next phase. Named searches cover all750 source texts,
but semantic review of non-pilot matches remains pending. The pilot is a reviewed
synthetic development artifact, not independent clinical validation.

The active local manifest is
`runs/seizure_finding_annotation_v0_2/agy_gemini38_high/manifest.json`.
Its `reviews/codex/REVIEW.md` explains the decision; `TERMINAL_HANDOFF.md` is the
short continuation procedure. Integrity checks verified both pilot snapshots,
review hashes/coverage, original-record preservation, the full change chain and
exactly 726 remaining sources. The portable package's 32 fictional checks, Ruff,
and documentation hygiene passed. Production extraction code and benchmark outputs
were unchanged; the full extraction pytest/mypy suite was not rerun for this scope.

## Earlier terminal handoff (2026-09-15)

The user requested continuation in their own AGY terminal. The local handoff is
`runs/seizure_finding_annotation_v0_2/agy_gemini38_high/TERMINAL_HANDOFF.md`.
There are24 saved pilot initials and no bulk initials. Gemini self-review outputs
exist for all24; later corrections have not yet been assembled or accepted as a
final24-source reference. The23-source comparison report reconciled39 groups and
1,319 supplied memberships, before the latest corrections and extra letter.
Four source-specific issues remain open. Pilot acceptance is pending.

The latest runner-edit attempt ended with provider503/no capacity. A fresh mocked
runner check ran11 tests with3 recovery failures; it is not ready for bulk use.
The portable annotation package passed32 fictional checks and Ruff. These are
structural/tooling checks, not clinical validation. The handoff specifies runner
repair,24-source reconciliation, pilot review,726 remaining annotations, Gemini's
full review and the subsequent Codex secondary review. Earlier dated pilot counts
below describe their respective snapshots.

Canonical owner of dated run authorisations, settings and completed comparison summaries.
Reorganised 2026-09-14 from the [study protocol](one_shot_paper_protocol.md).
Preserve the original meaning of every named run and linked artifact. Earlier
budgets and runtime settings apply to their named runs; subsequent amendments do
not rewrite earlier attempts. “Pending” in a dated record is not current status;
[PROJECT_STATUS.md](../../../PROJECT_STATUS.md) owns current work.

Annotation runs use the separate [annotation review procedure](seizure_finding_annotation_review.md).
Representation decisions belong to [schema decisions](one_shot_schema_decisions.md).

## Annotation instructions and pilot (2026-09-15)

The protocol was split into separate study, annotation, review, schema-decision and
execution documents. The portable annotation package contains the guide, JSON
Schema, fictional examples and a read-only checker. Its file hashes and 12 fictional
checks pass; documentation hygiene and Ruff checks pass. These checks do not
establish annotation completeness or clinical validity.

Codex exported all 750 permitted development letters, including 32 `row_ok=False`
rows, with exact source hashes and without benchmark labels or predictions. The
source-only JSONL SHA-256 is
`f4a5e9b01c31b526e93347dc3ab61d2f6d07db7eae449ff8eecadfc95084d9b2`.
The local run is `runs/seizure_finding_annotation_v0_2/agy_gemini38_high/`;
the directory name records its creation version. Its `guide_versions/v0.3/`
directory pins the revised instructions.

Gemini ran through AGY as `gemini-3.8-flash-high`, with `--effort high`. All 20
initial pilot records, Gemini self-reviews, corrections and Codex source-first
review notes are retained. Earlier AGY attempts encountered network/stream errors;
complete recovered drafts are distinguished from provider successes. The four
latest five-letter correction requests each returned provider success and all 20
records pass the offline source/schema checks. Codex also corrected one partial
calendar date's form, with before/after hashes. Three source-specific issues remain
explicit: disjunctive numeric wording, a bare resolved historical diagnosis and a
seizure-day counting unit. These letters are not yet adjudicable for finding scoring.

Cross-sample review detected omitted subtype mentions, lost condition qualifiers,
duplicate freedom claims and insufficient quotation context. Exact-source group
membership is now generated separately from reviewer judgements; a model-written
comparison report with shortened, non-exact quotations is retained as a defective
draft. Final pilot group rechecking and batch-runner review remain in progress.
No full dev750 annotation reference or finding-performance result exists yet.
AGY attempts retain available usage and batch timing; provider dollar cost and
individual-letter latency are unavailable and must not be inferred from batch time.

## Current plan: timeout reruns and expanded annotation (2026-09-14)

Conor approved the following priorities after the r5 dev750 review. This amendment
supersedes the earlier decision to require no assertion-level annotation. It records
planned work, not completed reruns, annotations or clinical validation.

## Timeout reruns

Rerun each timed-out request from r4 simple (14) and r5 rich (40), using a
600-second limit: 54 condition-specific requests, not only the seven letters where
both timed out. Preserve the original prompt, schema, model settings, scorer and
row policy; no representation correction is included in these reruns. Save new
attempts separately with links to the originals. Keep the original first-attempt
aggregate unchanged. Report a separately named timeout-completed view that uses
the new attempt only for each originally timed-out request, with all 750 letters
in each condition and residual failures retained. This is a mixed-attempt view,
not a fresh first-pass experiment at 600 seconds. Do not rerun returned wrong,
schema-invalid or envelope-invalid outputs under this permission.

Measure time per letter, distinguishing original and rerun duration and cumulative
work for repeated requests. Include all costs in the existing US$100 study ceiling,
including the separately authorised r6 test450 run; reconcile current spending and
outstanding reservations before calls. Completion reliability is not a separate
research priority. Conor expects approximately 0.88 Purist performance for both
conditions; test that expectation using the existing native agreement measure,
without relabelling it as a new F1 metric or tuning to the expected value.

## Completed timeout reruns (2026-09-14)

All 54 authorised requests returned at the 600-second limit: 14 r4 simple and
40 r5 rich, with no remaining transport failures. Frozen request bodies, model,
thinking enabled/low, 24,000-token limit, native scorer and no-repair policy were
unchanged. Original artifacts were hash-verified and preserved. This is a
mixed-attempt dev750 view, not a fresh all-row run at 600 seconds.

| Condition | Purist answer | Pragmatic answer | Strict Purist | Strict Pragmatic |
| --- | --- | --- | --- | --- |
| r4 simple | 658/750 (87.73%) | 673/750 (89.73%) | 658/750 (87.73%) | 673/750 (89.73%) |
| r5 rich | 658/750 (87.73%) | 678/750 (90.40%) | 656/750 (87.47%) | 676/750 (90.13%) |

Rich-minus-simple Purist answer difference: 0.00 percentage points
(paired 95% interval −1.73 to +1.60); Pragmatic: +0.67 points (−0.80 to +2.27).
Original non-timeout failures remain: each condition has two invalid envelopes
and one invalid target label; rich also has two schema failures. R6 development
results remain original first attempts, including 29 timeouts; their presence
in the replay aggregate does not make them a matched timeout-completed comparison.
No locked rows were inspected or executed for this rerun work.

Mean rerun request time was 11.96 seconds for simple and 32.07 seconds for rich.
Across all 750 letters, mean cumulative original-plus-rerun request time was
41.01 and 121.29 seconds respectively. These sum request durations, not concurrent
batch wall time. Per-request original, rerun and cumulative durations are retained.
Conservative rerun charge: US$0.5514081; cumulative study charges including the
completed r6 test450 run: US$29.1822888 of US$100. No attempts were outstanding
at reconciliation.

Runner: `scripts/benchmarks/rerun_thinking_timeouts.py` (`prepare`, `run`, `replay`).
Raw attempts and original-request links: `runs/one_shot_thinking_r4_r5_r6/dev750/timeout600/`.
The [aggregate and timing artifacts](../../../results/letter-benchmarks/gan/one_shot_thinking_r4_r5_r6/dev750_timeout600/)
retain all-row denominators and residual failures. Offline replay was byte-identical.
Verification: 831 always-on tests, Ruff and mypy (418 source files).

## R6 live test450 comparison (2026-09-14)

Conor authorised a fresh r6 test450 run, compared side by side with the saved
20260910 aggregate, and an increased timeout. The new request timeout is 600
seconds, up from 300 seconds in the completed dev750 comparison. The historical
DeepSeek model spec defaulted to 600 seconds and the saved command had no override;
the old aggregate did not record timeout, so this value is reconstructed from the
pre-migration code and protocol, rather than confirmed by a per-run timeout log.

`scripts/benchmarks/run_r6_test450.py` verifies the frozen development source and
data identities. It retains the r6 prompt, original schema/raw_model parser,
current strict envelope handling, thinking enabled/low, 24,000-token limit and
submitted temperature 0. It uses concurrency 12 and no retries or automatic adapter
fallback. The historical command used synchronous transport; this new runner uses
concurrent HTTP requests. These execution differences remain explicit.

All 450 locked notes are included. Tools/runners may read them to execute the
frozen requests and score outputs, but no identifiers, notes, predictions or
failures are exposed for inspection. Only aggregate results are reported. Replay
rows contain only source_row_index, prompt_version and raw_output; provider
responses remain local. There is no holdout row-diagnostic report. Historical
scores are 369/450 Purist and 385/450 Pragmatic. This is a reused-holdout replication
comparison, not fresh generalization evidence, and cannot authorize tuning on rows.

The US$100 cumulative ceiling includes US$24.255057 in prior conservative study
charges. Before calls, the runner reserves the worst-case cost of all remaining
requests. Requests and analysis remain frozen for replay. Run artifacts are under
`runs/one_shot_original_r6/test450_timeout600/`; the comparison aggregate is written
to `results/letter-benchmarks/gan/one_shot_original_r6/test450_timeout600/`.

## Thinking-enabled r4/r5/r6 development comparison (2026-09-14)

Budget amendment: after 1,782 attempts (594 per condition), the initial US$20
safeguard stopped execution at a conservative US$19.7474916 cumulative bound.
Conor raised the ceiling to US$100 and authorised resuming the remaining 468
unstarted calls. The frozen plan and all completed attempts, including 78 timeouts,
are preserved. `scripts/benchmarks/resume_one_shot_thinking.py --budget 100`
verifies the original source/request identity before applying the budget-only
override. The active authorization and its history are saved alongside the run.
No completed attempt was retried in that original run. The later authorised
r4/r5 timeout reruns above are separate attempts. The US$20 values below describe
the initial cap.


Conor authorised r4 simple, r5 rich and r6 original on dev750 and raised the total
DeepSeek study budget to US$20. Thinking enabled, reasoning effort low and a
24,000-token response limit are now the defaults for new one-shot study runs.
Frozen earlier runners and request identities are unchanged. Temperature 0 is
submitted to match the original configuration; DeepSeek documents that temperature
is ignored in thinking mode. Model alias: `deepseek-flash`, provider-documented
DeepSeek-V4.1-Flash. All three use identical provider settings, no local response
cache, concurrency 12, 300-second timeout and no retries or automatic adapter
fallback calls. Condition order rotates between letters. The native API receives
the rendered ChatAdapter messages directly, with text output.

| Condition | Prompt/output | Scoring |
| --- | --- | --- |
| r4 simple | Unchanged r4 answer-only request. | Independent declared answer and whole-output strict agreement. |
| r5 rich | Original task/cases, revised measurement schema and schema-population instructions. | Independent declared answer, complete-record validity, and strict end-to-end agreement. |
| r6 original | Original `gan_llm_extract_encode_select` prompt and original schema verbatim. | Original `raw_model` parser and native selected-label scorer; legacy parser semantics remain explicit. |

R5 has one observation_period field for all findings; recurring-rate denominators
remain separate. It allows unquantified clusters, qualitative numeric quantities,
and week/hour/minute/second time precision. Durations must remain positive and
unknown answers must link to findings. A schema-population example explains unknown
answer links. These changes do not modify the historical task or selection cases.
Sixteen fictional r5 outputs cover the changes, and the test explicitly proves
that invalid additional findings do not invalidate an independently valid answer.
A missing answer is never inferred from findings. R4 and r5 answer checks both use
the same required label/evidence contract; quotation exactness is not added as a
new label-scoring condition. The original r6 parser does not implement this newer
answer-only contract, so its validity counts have different semantics.

The runner is `evaluation/one_shot_thinking.py` (prepare/run/replay). It includes all
750 development rows, including row_ok=False, with 2,250 scheduled first attempts.
Plan, all source hashes, requests, responses, usage and development diagnostics
are local under `runs/one_shot_thinking_r4_r5_r6/dev750/`. Rendered empty-note
requests and fixtures are under `results/letter-benchmarks/gan/one_shot_thinking_r4_r5_r6/`.
Cost accounting reserves each input-byte bound and full 24,000-token output before
starting it, then uses returned token usage at peak cache-miss prices. Prior study
spending is US$4.4273178; the runner cannot exceed the US$20 cumulative ceiling.
No prompt or scorer changes are permitted during this comparison. Prior synthetic
development exposure remains disclosed; dev750 scores are not holdout replication.

Historical replication evidence: the located 20260910 aggregate reports 369/450
Purist and 385/450 Pragmatic, thinking enabled, low effort and 24,000 tokens. The
current original-prompt source is byte-identical to its pre-migration snapshot.
Aggregate-only replay of the saved outputs through the current original parser and
scorer reproduced both counts exactly, with zero parse failures. See
[replay aggregate](../../../results/letter-benchmarks/gan/one_shot_original_r6/replay.aggregate.json).
The removed protocol remains recoverable in the pre-migration snapshot; this
protocol owns its current interpretation. No holdout identifiers, notes or failures
were inspected. This establishes replay compatibility, not fresh-call determinism.
Thinking alone has not yet been isolated as the cause of prior score differences:
output budget, schema, parser and evaluation population also differed.

## Paired dev750 execution (2026-09-14)

Conor authorised running both r4 prompts on all dev750 rows. The separate
`evaluation/one_shot_measurements_dev.py` runner supports development only; it
cannot execute a test or patient partition. The prepared identity is saved under
`runs/one_shot_frequency_v2_measurements_r4/dev750/plan.json`. All 750 development
IDs are included regardless of `row_ok`, with one first attempt per condition
(1,500 calls), alternating condition order between letters. The model is
`deepseek-flash` (provider-documented DeepSeek-V4.1-Flash), temperature 0, thinking
disabled, maximum 4,096 output tokens for each condition, concurrency 6 and a
180-second timeout. The provider response model is saved for every call.

The ChatAdapter envelope uses text output, rather than v1's API JSON-object mode.
Exactly one `structured_json` section is extracted, with an optional `completed`
marker; bare JSON, duplicate sections and truncated responses fail. Its JSON is
then checked by the unchanged r4 validators. No retries, fallback calls, syntax
repair, semantic repair or answer inference are allowed. Raw responses and
extracted JSON remain separate. This transport setting follows the restored
prompt and is shared between conditions; it differs from frozen v1.

The existing native purist/pragmatic scorer and paired analysis are reused.
Every scheduled row remains in the denominator; failed outputs count as wrong.
Exact quotation diagnostics are reported separately from label agreement.
These are previously exposed synthetic development data, not held-out evidence
or validation of the richer measurements. No test-row failures are inspected.
The total US$10 study budget includes v1's US$1.1732 conservative charge. Each
new call reserves its input-byte upper bound plus maximum output charge; returned
usage releases that reservation to peak cache-miss prices (US$0.30/1M input and
US$1.20/1M output, checked 2026-09-14). Execution stops before exceeding the budget.
Interrupted requests are never silently resent. Replay uses saved first responses
without model access.

Completed: all 1,500 requests returned, with no transport, envelope or truncation
failures. Rich purist agreement was 521/750 (69.47%) and simple 570/750 (76.00%);
pragmatic was 564/750 (75.20%) and 620/750 (82.67%). Rich had 72 schema failures
and six invalid labels; simple had ten invalid labels. Failures count as wrong.
The paired purist difference was −6.53 points (95% CI −8.80 to −4.40), pragmatic
−7.47 points (−9.73 to −5.33). These are synthetic development results only.
Offline replay was byte-identical. Conservative run cost was US$3.2541282,
US$4.4273178 including v1. Detailed results and metadata are owned by the
[dev750 result artifact](../../../results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r4/dev750/README.md).
The prompt and validators were not changed in response to these outputs.

## Confirmed execution decisions (2026-09-13)

- Main synthetic evaluations use the DeepSeek API from Conor's current computer.
  The total API budget is US$10 across development and evaluation, including failed
  attempts and any retries. Reserve the frozen comparison cost before development;
  stop before the cap rather than silently reducing the evaluation denominator.
  Exact model identifier, current pricing, decoding and call limits remain to be
  pinned before calls.
- Supplementary local runs use Conor's Dell XPS 15. Hardware, model and runtime
  feasibility remain to be recorded; these are distinct execution conditions.
- Conor's collaborator owns the cluster and local DeepSeek execution on real patient
  data. No cluster budget is required from this task. Written custodian permission
  and the exposure/reference metadata remain pending with Conor.
- Two real-data runs are planned: one-call single-label seizure-frequency extraction
  and a separate extension across several clinical families. The extension's exact
  families, fields, reference availability and analysis must be specified and frozen
  before either real run; no adaptation from the first run's sealed errors is allowed.
  Gan's existing single-frequency reference cannot score the additional families.
  This original decision did not authorise additional annotation; the current
  dev750 annotation amendment above now supersedes that restriction for development.
- Develop on dev750, then run one frozen evaluation on test450 with aggregate-only
  reporting. Conor confirmed this policy; record prior exposure and retain all
  eligible rows, including row_ok=False. train300 remains outside this permission.
- Report agreement and paired rich-minus-simple differences with 95% intervals.
  Do not pursue a clinical adequacy threshold, equivalence or non-inferiority claim.
  The exact interval implementation and development selection rule still need to
  be specified before the evaluation freeze.

## Prespecified synthetic execution and analysis

The initial main condition is `deepseek-flash`, provider-documented DeepSeek-V4.1-Flash,
via `https://api.deepseek.com/chat/completions`. The provider offers a mutable alias,
not an immutable weight revision: record the documented version and every returned
model identifier without claiming exact weight reproducibility. Both prompts use
thinking disabled, temperature 0, JSON-object output (schema supplied in the prompt),
4,096 output tokens, 180-second timeout and concurrency six. No hidden SDK retries,
format recovery, semantic repair or second clinical request is permitted.

Pricing checked 2026-09-13 against [DeepSeek's official table](https://api-docs.deepseek.com/quick_start/pricing/):
reserve US$0.30/million input and US$1.20/million output tokens, the peak cache-miss
rates. This deliberately overestimates off-peak/cache-hit charges. Preflight bounds
input tokens by rendered UTF-8 bytes plus framing allowance and output by its cap;
all pending requests must fit before a phase starts. Missing usage or interrupted
requests keep their full reservation. Development is capped at US$1, retaining at
least US$9 for the comparison within the US$10 total.

Develop on 20 dev750 notes chosen without predictions by ascending
SHA-256 of `20260913:<source_row_index>`. Include row_ok=False if selected. Run both
conditions once on each note. This is a technical development comparison, not a
representative clinical-performance estimate. One model/runtime is prespecified;
freeze it unchanged if first-pass technical checks pass. Any development correction
requires a recorded new version and new checks, never an invisible replacement of
first attempts. Select the rich frequency condition for later real evaluation
before viewing synthetic test results; the real runtime still needs its own freeze.

The test phase schedules both conditions for every test450 note, including
row_ok=False. Freeze dataset/manifest, prompt, parser, native scoring, analysis and
runtime hashes before execution. Save full local requests/responses and separate
attempt records; the holdout replay file retains only source ID, prompt version and
raw output. Publish aggregate results only. No new test failure inspection or tuning
is permitted. Earlier studies used both partitions; describe this as reused-holdout
evaluation, not a fresh untouched test cohort.

Use Wilson 95% intervals for absolute all-note agreement. Use 10,000 paired
letter-level percentile bootstrap replicates, seed 20260913, for rich-minus-simple
agreement (sorted draws 250 and 9750, one-based). Report wins, losses and ties.
Patient and synthetic source-family linkage fields are absent from the supplied
row schema, so these intervals assume independent letters; they do not establish
patient/family-level precision. Do not infer clusters from clinical note text.
No inferential subgroup analyses are planned; degenerate bootstrap intervals are
explicitly flagged. Unusable responses count as incorrect even for unknown gold.
Failure precedence is truncation, no response, invalid syntax, invalid schema,
invalid target label, absent required evidence; transport error types are also
reported. Required quotation slots are countable in parseable object outputs;
report unparseable/absent output separately and count it as failure in the all-note
quotation measure. Empty no-evidence states never count as exact-quote successes.

## Completed synthetic comparison (2026-09-13)

The fixed development comparison made 40 calls, all usable, with exact quotations
in every required slot. Development Purist agreement was 12/20 rich and 10/20 simple.
The condition was frozen unchanged before the 900-call test450 comparison. No
repair calls, operational retries, transport failures or truncations occurred.
The frozen rich frequency condition was selected before test evaluation; the
collaborator's real-data runtime and permission remain pending.

| Test450 measure | Rich | Simple |
| --- | --- | --- |
| Purist agreement, all 450 notes | 342/450 (76.0%; 95% CI 71.8–79.7%) | 334/450 (74.2%; 95% CI 70.0–78.0%) |
| Pragmatic agreement, all 450 notes | 368/450 (81.8%) | 360/450 (80.0%) |
| Usable responses | 446/450 | 447/450 |
| Schema-valid responses | 448/450 | 450/450 |
| Exact required quotations | 1,547/1,558 | 423/429 |
| Notes with every required quote exact / all notes | 420/450 | 423/450 |
| No-evidence states, separately reported | 20 | 21 |
| Median request latency | 1.75 seconds | 0.97 seconds |
| Completion tokens | 160,864 | 22,024 |

Rich won 16 paired Purist comparisons, lost eight and tied 426: +1.78 percentage
points, paired 95% CI −0.44 to +4.00 points. This does not establish superiority,
equivalence or non-inferiority. Rich had two invalid-schema and two invalid-label
responses; simple had three invalid-label responses. All remained in the denominator
as incorrect. Twenty row_ok=False notes were included. No sealed failures were
inspected. Quote exactness establishes source location only.

The peak-price charge estimate is US$0.0506 development plus US$1.1226 evaluation,
US$1.1732 total, below the approved US$10 ceiling. These are conservative token-based
estimates, not a provider invoice; cache/off-peak billing can be lower.

The [artifact directory](../../../results/letter-benchmarks/gan/one_shot_frequency_v1/)
contains fictional rendered requests/schemas, the matched diff, development aggregate,
pre-test freeze, [test aggregate](../../../results/letter-benchmarks/gan/one_shot_frequency_v1/test450.aggregate.json)
and verification record. Private requests/responses and attempt logs remain in
`runs/one_shot_frequency_v1/`. Offline replay reproduced the aggregate exactly and
left the attempt ledger unchanged. The new checks and full always-on suite passed
(828 tests), as did Ruff, mypy and document hygiene. No deep tests were needed for
these new first-attempt/split safeguards; the local client was checked with a
fictional loopback stub, not an actual Dell model.

## Supplementary local preparation

`runs/one_shot_frequency_v1/local_preparation/` contains the same 20-note synthetic
development bundle and an explicit runtime metadata template. The no-install
`scripts/benchmarks/run_one_shot_local.py` client accepts that bundle and a completed
runtime file. It preserves requests/responses, performs no retries or repair and
uses the same strict parser and all-note scoring. A loopback stub check passed with
two fictional responses; this verifies client wiring only, not local model behavior.

From the repository root in the Dell's `.venv`, after supplying its actual server,
model revision, quantisation, hardware, engine/version and non-thinking parameters:

```sh
python scripts/benchmarks/run_one_shot_local.py \
  --bundle runs/one_shot_frequency_v1/local_preparation/synthetic_development_bundle.json \
  --runtime runs/one_shot_frequency_v1/local_preparation/runtime.template.json \
  --output runs/one_shot_frequency_v1/dell_development
```

The template intentionally has unfilled runtime fields; no Dell server or model has
been assumed. Report its results as a separate supplementary development condition.
The historical `run.py` route includes different clinical handling and does not
substitute for this paper-specific client.

## Pilot domain adjudication (2026-09-15)

CB returned four selected decisions. Codex applied them under annotation guide v0.5:
faithful qualitative preservation of ambiguous quantities and affected-period
recurrence, and exclusion of bare resolved historical diagnoses. All 24 pilot
letters are complete with 77 unchanged findings and no open issues. The original
export and pre-adjudication review remain preserved. Supporting rationales are
attributed to Codex because the export contained one UI-test placeholder and three
blank rationales. The source-bearing evidence owner is local-only
`runs/seizure_finding_annotation_v0_2/agy_gemini38_high/reviews/adjudication/REVIEW.md`.

The v0.5 structural/source checker passed all 24 records. Codex checked all four
decision changes and the other pilot wording-search candidates. The new snapshot
is `annotations/adjudicated.jsonl`; earlier per-source/group reports remain tied
to their original snapshot. The propagation search contains 133 candidates in 114
dev750 letters, not a completed full-set semantic review. The remaining 726 letters
and both full-set reviews are pending; execution remains paused. No model calls,
locked rows or real-patient data were used.

## 2026-09-16: Pro recovery, Codex review and test450 launch

Initial checkpoint; subsequent recovery and receipt updates follow below.

Grok's completed dev750 baseline is now the input for review. The downloaded Pro
continuation contains 473 unique records, not the claimed650. Pro retracted that
claim: a further177 had not been saved. The first50 archive is separately reported
complete but has not arrived locally. A fresh Pro continuation is reviewing the
missing177; do not count its unsaved progress as reviewed coverage.

Codex completed full-source review of positions701–750: 50 records,36 corrected,
three retaining questions. Codex also read a random100 full letters from the473
recovered reviews (seed20260916; not blinded). Main-decision judgments are57 agree,
31 partial and12 missed correction. These are review judgments, not extraction
accuracy or clinical validation. Applied corrections affect81 sampled records and
242 additional records from source-backed pattern review. Originals remain immutable.

The local evidence owner is
`runs/seizure_finding_annotation_v0_2/agy_gemini38_high/reviews/codex/pro_final/REVIEW.md`.
Before/after files, random IDs, reversals after guide rereading, proposal dispositions
and checker outputs are alongside it. The working750 candidate contains152 open
issue objects in124 records, grouped into eight CB question categories. The full
reference is not accepted: first50 receipt, missing177 completion, remaining
evidence/source-check reconciliation and CB decisions are outstanding. Untouched
older guide declarations have not been relabelled as reviewed migrations.

A new visible GPT6Pro web annotation task was launched at
https://chatgpt.com/c/6aaa0c04-067c-83ed-ab2d-9d81b42c9c11 using
`runs/seizure_finding_annotation_test450_6pro_2026-09-15/gan_test450_6pro_lean_2026-09-16.zip`.
It contains450 unique source-only letters (20 row_ok=false retained), the frozen
v0.6 guide/schema/examples/checker and lean instructions. Package SHA256:
`44e1f8fa5bfefdb85a391fd8d3d6557ffc7e848b20537a39a6924fb2eef17b41`.
The launch record preserves model visibility, destination and package details.
This is initial annotation, not test scoring or accepted reference production.
The web task is still running; no annotation output has yet been downloaded or
verified. No test labels, evaluated predictions, or test-driven rule changes were used.

### 2026-09-16 — recovered review outputs and merged development candidate

The user saved `review_missing177.jsonl` and
`gan_dev750_section_01_preserved_recovered.zip` to Downloads. Both were preserved
under `runs/seizure_finding_annotation_v0_2/agy_gemini38_high/reviews/codex/pro_final/`.
`coverage.json` records SHA-256 hashes and checks the first50, original473 and
new177 against their expected source-ID sets: all700 Pro reviews are now locally
accounted for, disjoint from the final50 reviewed by Codex. The original473 file
has a different internal ordering from the manifest; membership and uniqueness
match. The new177 order also matches the manifest.

The first50 archive supplied47 replacements. All205 new177 proposals have recorded
dispositions; the two newly imported sets changed168 candidate records. CB's
confirmed qualitative singular-article cadence resolved nine issues; the approved
event/feature convention retains source ambiguities. Source-check commentary was
reconciled in ten records. Seven remaining guide-version migrations were inspected
against full sources. A random six-letter acceptance spot-check from otherwise
unchanged new177 records required two qualifier/evidence repairs; two additional
targeted evidence repairs were applied. These checks do not replace or enlarge the
earlier100-letter sample (57 agree,31 partial,12 missed corrections, sampled from473,
not blinded). Individual change logs retain before/after annotations.

The merged `working750_candidate.jsonl` passes the supplied v0.6 checker for all750:
zero schema, source-hash, exact-quote or reference-link errors. This is mechanical
verification, not clinical validation. There remain170 issue objects across136
records, grouped in the regenerated `CB_QUESTIONS.md` and `.jsonl`; resolved cadence
questions are removed. Some ambiguities may remain under the approved convention.
The full candidate is not yet an accepted reference. No benchmark scoring or model
calls were run for this artifact-only integration.

The separate source-only test450 web task continued after its initial runtime limit.
It verified371 unique saved records before resuming missing IDs under its frozen
v0.6 instructions. Completion and downloaded output remain to be checked locally.
No test labels, predictions or model failures informed these development changes.

### 2026-09-16 — test450 output received and mechanically verified

The user downloaded all three final outputs from the source-only annotation task.
Original files are preserved under
`runs/seizure_finding_annotation_test450_6pro_2026-09-15/received_completed450/`.
The annotation SHA-256 is
`2e4c87c33fc5475aa49b62289d6a1483a53d3bda2526b511d5a265c1b3313b1d`;
the annotation and frozen source hashes match the delivered coverage report.
Local verification using the frozen execution package's checker passes with zero
errors:450 records,450 expected unique IDs,1754 findings,339 complete and111
needs_review. All131 issue references in the grouped report match saved issues
exactly once. `import_summary.json` and `local_verification.json` retain the checks.

These are initial annotations, not an accepted reference. Independent semantic
review remains pending. The original371-record preservation claim is reported by
Pro; the separate partial file has not been imported for a local byte comparison.
No labels, predictions or scores were accessed, no extraction rules were changed,
and no benchmark evaluation was performed. Only artifact checks and documentation
whitespace checks were needed; the repository test suite was not run.
