# Seizure-finding annotation workflow and review

Canonical owner of annotation execution, both reviewers' checks and finding matching.
Workflow revision: v0.7 lean review, 2026-09-16. Apply with the [annotation guide](seizure_finding_annotation_guide.md).
The [study protocol](one_shot_paper_protocol.md) owns the separate Gan answer endpoint.

## v0.7 review procedure (2026-09-16)

Under guide v0.7 the review unit is the letter, not the candidate statement. For
each letter one independent reviewer rereads the full source, then records either
`agree` or the corrected record with a one-line reason per changed finding. There
are no candidate ledgers, `source_checks`, `finding_context`, relations, A01–A09
tables or C01–C08 comparison groups; the offline checker covers source identity,
schema, exact quotation occurrence and state consistency. Cross-letter consistency
is checked by searching the annotation file for identical qualitative values,
event labels and evidence phrases and comparing their structured values; record
only the differences found and how they were resolved. `needs_review` letters are
excluded from finding scoring; report their count out of 750.

Matching under v0.7 follows the rules below with three changes: a prediction
matches a reference when its evidence span overlaps the reference span; the
`approximate` flag, inclusivity flags and any relation fields are ignored; and
`timing` values other than `current`/`historical` in a prediction are compared as
`current`.

The detailed procedure that follows describes the v0.6 workflow. It remains the
record of how the saved dev750 and test450 artifacts were produced and reviewed;
it is not applied to v0.7 work.

The user authorised source annotation and self-review by Gemini through AGY on
2026-09-14, then replaced Gemini with Grok 4.6 as the annotator on 2026-09-15.
Codex remains the coordinator and independent secondary reviewer. Grok owns the
remaining initial annotations and the primary full-set review, including earlier
Gemini-annotated sources; preserve Gemini's original outputs and actual review scope.
Record Grok as a new model segment with its verified provider model identifier,
effort/settings, input hashes and attempts before execution. Do not assume that the
Gemini AGY route or effort flag applies to Grok. The execution record owns readiness.
Codex may assess the pilot/batch checkpoint against the written criteria and
continue when it passes; only unresolved clinical or consequential new policy
questions require Conor/domain input.

## Simplified ChatGPT review continuation — 2026-09-15

After the first 50-source Pro review took 130 minutes, Conor requested completing
the remaining 700 in the next turn with substantially less procedural overhead.
For this Pro continuation, read each full source alongside its baseline annotation
and record substantive omissions, unsupported claims, incorrect values/scope/time,
inadequate evidence and unresolved questions. The clinical guide remains unchanged.

Return one compact source-level verdict with evidence-linked issues, a short
summary and exact reviewed/pending IDs. Separate candidate files, nine saved checks
per source, exhaustive group/page/member accounting, version-migration proposals,
replacement snapshots and repeated post-correction cycles are not required for
this continuation. Compare recurring semantic problems through targeted searches
and source rereads where warranted. Full reading and truthful coverage remain
required; do not manufacture completion to meet the one-turn target.

Preserve the first-50 artifacts and attribute the changed review method. Codex
handles supported correction application and mechanical verification locally.
Skipped procedural checks must not be reported as completed, and the Pro output
alone does not establish an accepted reference. The exact continuation instructions
are saved under the local Pro package as `SIMPLIFIED_CONTINUATION.txt`.
The detailed procedure below describes the earlier workflow and other review
stages; this amendment takes precedence for the remaining-700 Pro pass.

## Working procedure

Use one fixed source file, one initial record per letter, and two review passes.
Batching controls workload; it must not change annotation decisions. The active
run manifest identifies current files. Earlier responses and snapshots remain
history and must never be mistaken for the current reference.

### 1. Freeze the inputs and review the pilot

The source export contains all 750 authorised dev750 letters, including
`row_ok=False`, with `source_id`, `source_row_index`, `source_sha256`, `row_ok` and
complete `note_text`. Hash the exact UTF-8 text without normalisation. Strip native
labels and evaluated predictions. Reject duplicate IDs/row indices, missing notes
and rows outside the authorised split. Keep identical texts with distinct source
IDs; compare them during review.

Supply the guide, schema, worked examples and their hashes together. The primary annotator must
be able to reopen any of the 750 sources and previous annotations throughout the
run. Verify access to the manifest, first/last source and another batch. Visibility
means retrievable files; it does not require putting 750 letters into one prompt.
All source-bearing files stay in the local `runs/` folder.

Select a source-based pilot covering the main measurement, scope and ambiguity
cases; start with 20 letters and add only necessary cases. Record actual coverage
and gaps. Do not claim a category is absent solely because a search found no match.
Codex reviews the pilot against A01–A09 and C01–C08, resolves general instruction
gaps, and records the decision to proceed. Source-specific issues can remain open
with an owner and exclusion from scoring. State the exact scope of the primary annotator's and
Codex's reviews; acceptance is not clinical validation.

### 2. Annotate in five-letter batches

Order remaining sources by `source_row_index`; include pilot letters once in the
750-row manifest. Use five-letter assignments, with a smaller final batch. Process
and save each letter separately so an incomplete answer cannot erase completed
letters. Keep the whole source collection accessible across batches.

For each letter, read the full source, list candidates, apply D01–D12, populate
findings/issues/source checks, reread the source and run A01–A09. Save the first
complete valid record as the immutable initial. Preserve raw requests, responses,
provider status, model/effort, timestamps and available usage. Mark unavailable
settings or timings unavailable; do not invent per-letter timings from a batch.

Run the offline checker after each batch. Fix formatting separately from semantic
changes. Retain invalid/truncated responses; retry only missing or invalid letters
as new recorded attempts, at most three attempts per letter under this run policy.
Never choose a more plausible later response over an existing valid initial.
A provider error with a complete valid record remains a provider-error attempt,
even if its record is usable. A failed letter is not an empty inventory.

Use the small file workflow first. An automatic scheduler, retry engine or custom
model client is not required. The user authorised increased concurrency for the next ten batches on 2026-09-15.
Keep five-letter assignments, give each source a single writer, and save outputs
in distinct batch/attempt directories. The coordinator alone updates shared
collections and manifests after checking saved files. Preserve each running batch's
actual package/version; apply v0.6 to newly dispatched batches and review quarter
wording separately in any already-running v0.5 batch. On interruption, inspect saved files and resume pending source IDs;
do not reconstruct annotations from chat memory. Freeze any model/settings change
as a new segment and compare its decisions with the earlier segment.

### 3. Grok reviews; then Codex reviews

After the initial pass, Grok rereads every source in a fresh review pass, records
candidate quotations before looking at the saved findings, then runs A01–A09 and
C01–C08 across all 750. Empty records and unresolved letters are included. Save the
review even when nothing changes. Source-specific issues do not block other letters.
A new general rule must be resolved and versioned before affected cases continue.

Codex performs the same full-source and cross-sample checks independently, then
compares decisions and applies supported corrections. Preserve each review's actual
input hash. Codex checks the final corrections and affected comparison groups;
Grok does not need to reapprove every Codex correction. Reopen a disagreement
only when source support or a rule remains unsettled. Do not create a third blanket
review cycle merely to make both reports name the same final snapshot.

Both full-set review passes are required before the 750-letter reference is
complete. A pilot acceptance or a passed batch checker is not full-set completion.
The final report states reviewed, unresolved and adjudicable source counts and
retains the complete correction history. Finding matching remains separate from
the native Gan answer endpoint.

## Active files

| File | Purpose |
| --- | --- |
| `sources.jsonl` | Immutable full dev750 source export. |
| `manifest.json` | Authorised sources, frozen package hashes, batch assignments and current artifact paths. |
| `raw/` and original attempt folders | Immutable first records, requests/responses, failures and provider provenance. |
| `annotations/initial.jsonl` | Source-ordered collection of first valid records, retaining historical pilot guide versions. |
| `annotations/grok_reviewed.jsonl`, `annotations/codex_reviewed.jsonl` | One active snapshot per review stage; preserve the parent before replacing it. |
| `reviews/grok/`, `reviews/codex/` | Per-letter checks, comparison groups, changes, summaries and unresolved issues for each reviewer. |
| `progress.jsonl` | Derived coverage from saved artifacts; never use a stale progress row to override an existing record. |
| `decisions.jsonl` | Run-local rule applications and unresolved decisions; general rules belong in the guide. |

Do not create another status board or duplicate review report. Update the active
paths in the manifest; keep superseded artifacts only as provenance. The run's
short handoff identifies the next batch and exact commands. Existing Gemini paths
remain historical provenance; use new Grok paths for new outputs and preserve the
actual model identity for every record/review. Never rename Gemini results as Grok.

## Run the supplied offline checker

Run `python verify_handoff.py` in the supplied package first: it verifies file
hashes and runs the fictional checker, group-generation and decision-coverage cases. No dataset
access is needed. Copy `check_annotations.py` with the schema into the working folder. It uses
Python 3.11+ and `jsonschema` 4.x; record exact versions in the run manifest. In this
repository use `.venv/bin/python`. From the annotation working folder run:

```sh
python check_annotations.py --sources sources.jsonl --annotations annotations/initial.jsonl > reviews/initial_checks.json
python check_annotations.py --sources sources.jsonl --annotations annotations/grok_reviewed.jsonl > reviews/grok/mechanical_checks.json
python check_annotations.py --sources sources.jsonl --annotations annotations/codex_reviewed.jsonl > reviews/codex/mechanical_checks.json
```

Create the review directories before redirecting output. For the pilot, use its
source subset and `--expected 20` (or its recorded size). For the full run keep the
default 750. The checker reads files only and exits nonzero on errors. It checks
source hashes, JSON Schema, coverage, duplicate IDs, links, exact quotation
occurrence and basic state consistency. It cannot check whether the supplied
sources truly equal the authorised split: compare against the custodian's original
manifest during setup. It also cannot establish semantic support, complete reading
or cross-sample consistency; complete the human/model review tables after it passes.
An unresolved annotation can pass structural checks and still be unfit for scoring.

The package's `export_guide.py` regenerates the portable guide and file hashes from
the annotation guide and review documents without reading datasets. Run it with the repository `.venv` after
editing this section or the examples. The JSON Schema is pinned separately; review
any schema change explicitly and update its version with the guide. Keep the hash
manifest with the exact files supplied to the primary annotator.

### Build the comparison groups from files

After the annotation checker passes, run `build_review_groups.py`. It generates
group membership with readable source/finding IDs, exact source quotations and
input hashes. It also searches the raw source text for possible omissions. It does
not decide whether a label is correct. The group-tool and decision-coverage tests run with `verify_handoff.py`, alongside
the annotation-checker cases.

```sh
python build_review_groups.py --sources sources.jsonl --annotations annotations/grok_reviewed.jsonl --candidates reviews/grok/candidates.jsonl --correction-patterns review_searches.json --out reviews/grok/groups_pass1
```

Use the corresponding Codex files and a separate output directory for the second
review. For a pilot, supply its source subset and `--expected 24` (or the actual
recorded size); add `--all-sources sources.jsonl` to search the complete development
set for propagation candidates. The supplied search list is a backstop, not a
clinical classifier. Save any expanded search list and rebuild groups after a
correction. A search match is pending until its source context and annotation have
been reviewed. Use a new output directory each time; retain earlier memberships.

After a reviewer returns whole-group decisions with named exceptions, run
`expand_group_review.py --groups supplied_groups.jsonl --report review.json --out reviewed_groups`.
`supplied_groups.jsonl` must be the exact membership given to that reviewer, with
its source and annotation hashes recorded in the request metadata. The formatter
rejects missing/duplicate groups and unknown/duplicate exception members. It copies
explicit judgements; it does not decide whether they are correct. Preserve the raw
report alongside the expanded comparisons. A page-level report covers only that
page; keep the complete group pending until all pages and cross-page comparisons
are reconciled. The supplied group tool includes nested quantity/date enums in C07;
if batch metadata is unavailable, supply the run's recorded batch assignments to
review counts by batch separately.

Member IDs belong to the recorded input hashes. Do not carry a comparison to a
different snapshot merely because its member IDs look the same. Reviewers must
complete the comparisons in the generated groups and reconcile their membership
coverage before marking the groups reviewed. If a group is too large for one
response, use recorded pages in source-row order, retain the common group ID, and
keep it pending until every page and the comparisons between pages are checked.

## Shared per-letter checks

Each reviewer writes one `checks.jsonl` record for each source with `source_id`,
`source_sha256`, `annotation_sha256`, `guide_version`, `reviewer`, `pass_id`,
`candidate_quotes` (exact quotations listed on the source reread), and `checks`.
`checks` has exactly A01–A09, each with `status` (`pass`, `fail`, `unresolved`),
`finding_ids`, `issue_ids` and a short `note`. A pass note may be empty. A failed or
unresolved check must identify the evidence and reason in the note or linked issue.
Schema validation cannot decide clinical support or completeness; mark those checks
only after reading the source. Do not use an overall “looks correct” verdict.

| Check | Required check |
| --- | --- |
| A01 — identity and format | Source ID/index/hash match the manifest; JSON and schema valid; guide version correct; IDs unique; every context/relation/issue target exists; arrays and states are consistent. |
| A02 — coverage | Full source read; each candidate statement accounted for as finding, repetition, excluded statement or unresolved issue. Search the source for possible omissions; search terms are a backstop, not the reading method. |
| A03 — event | Event name, patient scope, combined/specific/unspecified scope and seizure status follow D01–D02. No inferred subtype. |
| A04 — measurement | Type and counting unit follow D03–D07; all cluster components retained; no count-to-rate conversion, double-counted freedom or invented event count. |
| A05 — quantity | Number/range/bound, inclusivity, approximation and vague quantity match the source; denominator is recurrence time, not event duration. |
| A06 — time and condition | Timing follows D09; window/date/condition retained; no inferred year, duration or date resolution. |
| A07 — evidence | Every evidence and mention occurs exactly in the source; each principal quote supports all populated attributes and contains needed antecedents. |
| A08 — identity of claims | Repeats merged, distinct claims retained, overlaps/conflicts/corrections recorded; no arithmetic across overlapping claims. |
| A09 — issues and state | Gaps/ambiguities retained, no silent guesses; complete empty records justified; `complete` has no open issues; source failures not labelled empty success. |

## Shared cross-sample checks

Both reviewers build `groups.jsonl` from the full source set and the snapshot under
review. Generate source IDs, member IDs and exact quotation spans from the saved
files; do not ask a model to recreate them. Use readable member IDs such as
`128/f2` and `128/candidate001`; hashes identify file/record versions. A reviewer
may apply one comparison to all members of a supplied group, with named exceptions;
the formatter must expand that declaration to the group's exact saved membership.
Reject missing, duplicate or unknown groups/members before calling the report
complete. A prose “all checked” summary cannot override a failed coverage check. Each group has `check_id`, `group_id`, `selection_rule`, `members`
(source ID, finding/issue ID if present, exact candidate quote), and `comparisons`.
Each comparison records member IDs, `outcome` (`consistent`, `justified_difference`,
`error`, `unresolved`), `rule_ids`, `reason` and linked change/issue IDs. Preserve
all group members and decisions, not just anomalies. Review the full source when
context could explain a difference. Include source candidates with no finding so
that an omitted claim can be detected. A missing comparison group cannot count as
reviewed: record “no candidates” and the search used where a category is absent.

| Check | Build and examine these groups across all batches |
| --- | --- |
| C01 — coverage | Compare manifest IDs with each snapshot and both review reports. List missing, duplicate, extra, wrong-version and blocked records. Require 750 distinct source records; do not confuse source IDs with a count of successful annotations. |
| C02 — repeated wording | Group identical source hashes, then identical candidate quotes. For near repetitions, compare lowercased text with whitespace collapsed and numeric tokens replaced by a marker, retaining negation, units and time words. This is a search aid only; inspect contextual differences. |
| C03 — measurement decisions | Collect source phrases containing per/every/daily/weekly/monthly, in/past/since/on, cluster, last, none/free, unknown/not documented, and the lexical variants found during reading. Compare count/rate/qualitative/freedom/latest-event choices, including missing findings. |
| C04 — quantities and units | Group bounds, ranges, approximations, vague counts, seizure-days, cluster counts and cluster sizes. Check the same wording preserves the same operator and counting unit; search for unsupported numeric values and omitted qualifiers. |
| C05 — event and time | Compare uncertain/non-seizure/combined events and current/historical/future/unclear assignments. Inspect each different label for similar source wording; require a quoted context explaining the difference. |
| C06 — identity and evidence | Compare repeated mentions, overlapping totals, last-event-plus-freedom and conflicting reporters. Check consistent splitting/merging and whether short quotes omit needed context. |
| C07 — empty and unusual records | Reread every empty record, every issue, each measurement/enum value occurring only once, and letters with the smallest/largest finding counts. Inspect counts by batch/model segment for possible drift; do not force counts or label proportions to match. |
| C08 — correction propagation | For each corrected interpretation, search all 750 source texts and annotations for the same pattern, including earlier batches. List affected records, corrected records and retained exceptions with reasons. Rebuild relevant groups after edits. |

Use a versioned search list saved with each review. Expand it when a new expression
is found and rerun it across all sources; never apply the new expression only to
later batches. Every finding belongs to C03's measurement inventory even when no
search term matched. Every issue belongs to C07. Record group/member totals and
checked/pending counts in `summary.json`, alongside letter coverage and open issues.
Frequency tables and schema checks identify candidates for review; they do not prove
consistent semantics. An identical source phrase can legitimately have a different
annotation when event attribution or surrounding time context differs.

## Corrections, rule changes and completion

Use `changes.jsonl` for both reviewers. Each entry contains `change_id`, `source_id`,
`reviewer`, `pass_id`, `timestamp`, `input_annotation_sha256`, `output_annotation_sha256`,
`rule_ids`, `check_ids`, `finding_ids`, `before`, `after`, `evidence`, `reason`,
`related_source_ids` and `status` (`applied`, `proposed`, `unresolved`). A rejection
or no-change decision belongs in the check/group result; an applied change must
exist in the revised snapshot. Keep existing finding IDs when fixing attributes;
allocate new IDs for added claims; never reuse removed IDs. For a merge retain the
earliest ID and log the removed IDs; for a split retain the original for the first
claim and allocate new IDs for the rest. Update every relation/context reference.

A correction under an existing rule can be applied immediately, then checked across
all sources using C08. A new interpretation requires a proposed rule in
`decisions.jsonl`: decision ID, question, source IDs/quotes, proposed wording,
responsible reviewer, status and affected rule IDs. Do not silently change the
frozen guide. Resolve it in the annotation guide, increment the guide version, regenerate
the handoff files and review all affected sources in both passes. If the affected
set cannot be identified reliably, rereview all 750. Carry unchanged annotations
forward only with a recorded applicability check; do not silently relabel their
original version. Preserve the previous snapshot and decisions.

Completion requires C01 to reconcile every source, both reviewers' A01–A09 reports,
completed C02–C08 groups, all applied changes traceable to source evidence, and no
pending checks. Distinguish `review complete with unresolved cases` from `fully
adjudicated`: unresolved clinical/representation questions have named owners and
remain excluded from finding scoring. Report how many of 750 are adjudicable.
Freeze manifest, source, guide, schema, examples, final annotation, review and
change-log hashes in the final run manifest. Codex/model agreement remains a
reviewed development reference, not independent clinical validation.


## Finding correctness, completeness and matching

The scoring unit is a distinct source finding, not a quotation, field or selected
answer. Use only reviewed references and freeze matching decisions before comparing
conditions. Construct candidate pairs within the same letter; a whole match needs
all source-required attributes: event scope and seizure status, measurement type,
quantity and counting unit, bounds/inclusivity, approximation, rate denominator,
all stated cluster components, timing, period/date and condition. Unsupported added
attributes also prevent a match. Require an exact source quotation that supports
the whole claim, including relevant context. Different sufficient quotation spans
can match the same finding; identical quote strings alone never establish a match.

Ignore finding IDs, object-key order, explicit default values and number formatting
(`2` versus `2.0`). Source-equivalent event wording and harmless whitespace in
non-evidence text may match after a recorded reviewer decision. Do not silently
normalise units, substitute a calculated rate for a count, resolve dates or drop
qualifiers. Review-only relations/reporters determine which claim is being matched;
missing R7 relation fields are not separately penalised, but a quote supporting the
wrong reporter or a superseded claim does not support the current claim. Report
relation limitations descriptively. Document dates are audited separately and are
not extra seizure findings in either denominator.

Find a maximum-cardinality one-to-one matching among eligible whole matches, with
stable source/finding-ID order to break equivalent ties. Each prediction and each
reference can contribute at most one true positive. Do not greedily consume a
reference if another assignment permits more valid matches. Preserve the pairing
and attribute judgements for replay. A split/merged prediction cannot obtain several
matches for one record: missing a cluster component fails the whole cluster match;
one combined record cannot cover independently measured event types. Diagnostic
partial matches do not earn partial credit.

For adjudicable letters, sum true positives (TP), unmatched predictions (FP) and
unmatched reference findings (FN). Report finding correctness as micro precision
`TP / (TP + FP)`, completeness as micro recall `TP / (TP + FN)`, and optional
finding F1 `2TP / (2TP + FP + FN)`. The existing answer endpoint remains all-note
native agreement; it is not finding F1. Retain denominators, counts by measurement
type and timing, and the number of fully correct inventories.

| Case | Required accounting |
| --- | --- |
| Duplicate emitted claim | Only one can match; every additional duplicate is FP. References merge true repeated mentions before scoring. |
| Wrong attribute or unsupported extra claim | No whole match: FP, plus FN for any corresponding reference left unmatched. Record the specific attribute errors. |
| Valid empty prediction, nonempty reference | Every reference finding is FN. Per-letter precision is undefined, not 1. |
| Nonempty prediction, reviewed empty reference | Every prediction is FP. Per-letter recall is undefined. |
| Valid empty prediction and reviewed empty reference | TP/FP/FN are zero; count as a correct empty inventory and report empty-state accuracy separately. Do not assign vacuous precision/recall of 1. |
| Absent or unusable finding output | No TP; every reviewed reference finding is FN. Record a failed letter, including when its reference is empty; never count it as a correct empty inventory. |
| Partially invalid output | For the primary finding analysis, an unparseable findings array or any invalid finding makes the inventory unusable. Count identifiable array entries as FP; for an unparseable array report the predicted count as unknown, not zero. Optional per-entry salvage is a separately named diagnostic, with raw output retained and no semantic repair. |
| Unresolved reference | Exclude the whole letter from the adjudicable finding score to avoid selectively retaining easy claims; list excluded letters, issue kinds and candidate findings locally. Report reviewed/adjudicable coverage out of 750. Never label that score an all-dev750 finding result. |

For unusable outputs with unknown predicted counts, precision is conditional on
countable predictions and must be labelled as such; report their number alongside
recall and all-letter exact-inventory success. An answer-only schema has no requested
inventory: report finding measures as not applicable for that condition, not as an
empty extraction. An invalid answer does not by itself invalidate a separately
parseable, valid inventory; report answer and whole-output validity independently.

Exact-inventory success requires a usable inventory, TP equal to reference count,
FP=FN=0 and adequate supporting quotations. Divide by all adjudicable scheduled
letters, including failures and reviewed empty references. Report unresolved
reference coverage separately. If an aggregate precision/recall denominator is
zero, report `not estimable` with its counts, never replace it with 0 or 1.

For unmatched pairs, record diagnostics for omission, duplicate, unsupported claim,
event/scope/status, measurement/counting unit, value/bound/approximation, time,
condition and evidence (missing/non-exact versus exact but insufficient support).
Several diagnostics may apply to one finding; their totals are not FP/FN totals.
Any newly noticed reference omission starts a logged full-source review under the
same guide and is applied to every condition; never add a prediction to the reference
solely because it was emitted. Preserve both reference versions and rescore all
conditions if the correction is accepted.

Report the dataset/split/row policy, guide and reference hashes, scorer/matching
version, extraction model and prompt version, replay and repair policy, exclusions
and failure counts with each result. Save row-level pairings only for permitted
development data. Use the protocol's existing sampling-unit and interval rules;
freeze implementation and seed before evaluation. No finding metrics are established
by the fictional examples or by this guide alone.

### 2026-09-16: recovered Pro coverage and lean test450 initial annotation

The user's latest instruction requests Codex completion of the outstanding review,
pattern-based adjudication of Pro feedback, a random 100-record agreement check,
grouped CB questions, and a fresh web 6 Pro test450 annotation task after feedback
has been digested. This supersedes the staged package's requirement to finish all
dev750 adjudication before starting the initial test annotation. It does not settle
open rules or permit tuning against test annotations or evaluated predictions.

The initially downloaded simplified Pro artifact contained473 unique records, not
650; Pro retracted the larger claim because177 records had not been saved. The
first50 archive and a fresh177 continuation have since been received: all700 Pro
reviews are locally accounted for, alongside Codex's final50 source reviews.
Local evidence is under `reviews/codex/pro_final/` in the active annotation run.
The random100 selection uses seed20260916 over the originally recovered473 reviews;
it does not represent the subsequently recovered227. Pattern inspection is distinct
from full-source review, and neither establishes an accepted reference. The execution
record owns merged coverage, corrections, unresolved counts and verification.

For the separately authorised source-only test450 task, use the frozen v0.6 schema
and semantic rules with the lean execution instructions in
`runs/seizure_finding_annotation_test450_6pro_2026-09-15/execution_package_2026-09-16/`.
Read each full source, author its inventory, and immediately check it against the
source. Keep canonical within-record evidence/context/issues/source_checks, but
omit separate candidate ledgers, A/C check tables, comparison groups, independent
self-review claims and repeated checkpoint ZIPs. Save incrementally and derive
actual coverage from the delivered JSONL. This produces initial annotations for
later review, not an accepted reference. Open policy questions stay unresolved;
no new general rule may be inferred from test sources. Preserve the earlier staged
package and all immutable source bytes.
