# Longitudinal annotation guide

Version 0.1, paired with [annotation schema](annotation.schema.json) version 0.2.
Provisional development policy, exercised on 12 AI-authored patients. An independent AI pass and development adjudication are recorded in the pilot
review; no independent clinical validation is claimed. The [task definition](task_definition.md)
owns cohort queries and cutoff rules; this guide owns annotation meaning.

## Units and evidence

The case manifest owns patient ID, letter IDs, source hashes, visit dates and dates
letters became available. The annotation file contains only assertions and links.
Use stable patient-local assertion IDs (for example `L1.staring`) and link IDs.
Evidence mentions are identified by `(letter_id, start, end)`; repeated use of the
same span does not create another clinical event. Offsets count Unicode characters
in the unchanged UTF-8 source, starting at zero, with an exclusive end. Preserve
line endings; do not calculate offsets against a reformatted copy.

Create one assertion per attributable fact, status and time. Split a request,
performance and result even when one sentence contains all three. Multiple spans
may support one assertion, including its qualifications and scope. Assertion spans
belong to the asserting letter; relationship evidence may refer to several letters.
Keep contradictory assertions separately. Record the actual reporter, expressed
certainty and polarity. `mixed` requires explicit agreement; disagreement needs
separate assertions. `not_started` and seizure `absence` are already negative
clinical statements: use `affirmed` when the source asserts them.

## Time and uncertainty

Keep clinical time in each assertion and documentation availability in the manifest.
A later letter can report an earlier occurrence or earlier clinical result availability.
It becomes usable only when that letter is available. Physically filter source
letters before annotation for each permitted information cutoff. Do not expose a
full-history reference to a visit-view annotator.

`start` and `end` describe the clinical interval. Each has earliest/latest bounds
on that endpoint; equal bounds mean an exact date. For “since November”, onset
bounds are November 1–30, not an invented November 15. An unknown endpoint is
null. An unbounded endpoint must not silently become the first or last visit.
Retain the source time expression and anchor relative expressions to the named
letter's visit date. An implicit current assertion may use that visit date with
`text: null`; the anchor records the basis. Do not use letter availability as an
occurrence date. A point event has equal start and end. `as_of` states only what
is supported at that date and does not imply an uninterrupted preceding interval.

A correction link's `decision_time` records when the interpretation changed,
separately from the event being reinterpreted and the letter reporting the change.
If the decision date is unspecified, keep it unknown. Different timeframes alone
are not a contradiction. Preserve uncertainty when bounds straddle a query boundary.

## Clinical families

| Family | Annotation rule and downstream purpose |
| --- | --- |
| Diagnosis | Record the documented diagnosis and whether current or historical. Do not infer epilepsy or subtype from event terminology, medication or a normal test. Supports the diagnosis condition in Q1. |
| Seizure | Separate individual occurrences, recurring patterns, absence statements and explicit inventories. Keep pattern identity separate from its epileptic/non-epileptic interpretation. Supports Q1, Q2 and Q5 without erasing reinterpreted events. |
| Medication | Distinguish proposed, conditional, prescribed, started, taking, not started and stopped. Taking does not supply a start date. Silence does not mean cessation; a deferred proposal does not establish no earlier use. Q3 needs actual initiation. |
| Investigation | Separate requested, performed, result, pending and cancelled. Keep distinct requests of the same modality separate. A request inventory needs explicit coverage of the relevant interval. Q4 needs the matching request and clinical result availability. |

Preserve seizure burden as a count, rate, clusters, freedom duration or qualitative
wording. Keep count bounds, time basis and events per cluster separate. Null bounds
mean unknown, not zero. Strict inequalities use the inclusivity flags; otherwise
bounds are inclusive. Do not replace ranges with midpoints, convert months into a
fixed number of days, or turn “occasional” into a number. `approximate` preserves
qualifiers without inventing an uncertainty interval. A rate's `count` means events
per `period`; a cluster rate's `count` means clusters per `period` and
`events_per_cluster` means events in each cluster. A count uses the assertion's
clinical interval. For freedom, `period` is the reported duration; do not impute a
rate or infer an exact last seizure. Unknown cluster spacing stays null.

Absence applies only to the named scope and interval. No convulsions does not mean
no epileptic seizures. `coverage: complete` requires explicit exhaustive wording;
missing types or unmentioned treatments never establish complete negative evidence.
The same applies to inventories of requests or patterns. Reference query reasons
may require information beyond the present structured fields, such as an explicit
statement that a correction was the first ever. Preserve that evidence; this draft
is not yet a complete executable query representation.

## Relationships and disagreement

Use `same_pattern` only when wording or context supports identity. Similar names
alone are insufficient. `overlaps_active` needs supported concurrent activity.
`repeats` records repeated information without treating copying as independent
corroboration. `updates` records a later account or extended interval; it need not
invalidate the earlier account. `corrects_interpretation` requires explicit
reinterpretation of the same event or pattern. Keep both endpoint assertions.

Use `contradicts` when accounts about the same clinical scope and time disagree;
do not resolve reporter disagreement by voting or by taking the latest statement.
If identity is uncertain, leave the assertions unlinked or mark a proposed link
`uncertain`. Never use an uncertain link as proof of identity. The endpoint field
names indicate source and target; within-letter overlap may use either order.

`plan_not_enacted` connects an identifiable plan to explicit evidence that it was
not enacted. `request_performed` and `request_has_result` require evidence matching
the particular request. The worked patient's February EEG and July EEG illustrate
why modality equality is insufficient.

## Worked reference and checks

[Authored patient 001](../../examples/longitudinal/authored_patient_001/README.md)
contains 35 assertions and 10 relationships. Its original 20 query answers remain
separate from this representation; no extractor predictions or scorer are implied.
The full-history annotations are reference material, not an input for visit queries.

Run `python scripts/longitudinal/check_annotations.py` from the activated repository
environment. It checks JSON Schema, source hashes, exact spans, unique IDs, link
endpoints, date bounds and quantity bounds. Its optional Python `cutoff` argument
rejects annotations using unavailable letters, including evidence and date anchors.
It does not prove clinical entailment, completeness, identity, or query correctness.
The automated shape probe for clusters is not source-supported annotation evidence.

Next, independently annotate the corrected 12-patient development pilot without
seeing these references or hidden scenario truth. Record time and disagreements
by family, temporal field and relationship; retain unresolved alternatives. Revise
and version this guide and schema together before a full schema implementation.

## Model-facing language audit

The schema is the candidate output specification; no provider prompt is deployed.
An inspection-only rendering combines plain extraction instructions, permitted
letters and this schema. All acceptance checks passed: rendered input inspected;
plain language used; research metadata kept separate; non-obvious fields described;
jargon removed or defined; length limited to the provisional structured task.
There are no controlled-experiment deviations. This is a text audit, not evidence
of provider compatibility or extraction performance.


## Negative-answer adjudication clarification (2026-09-09)

For Q2 and Q4, a statement at one visit does not establish a complete inventory
throughout the query window. An unchanged named pattern does not exclude all
other patterns; “no investigations were requested” at a visit does not exclude
requests elsewhere in the lookback.

Explicit absence of all seizures throughout the 90-day window can refute Q2
without an additional named-pattern inventory. For Q5, seizure freedom alone
does not exclude episodes previously considered epileptic and subsequently
reclassified. Require evidence addressing the reassessment history to establish
a negative. Missing revision documentation remains indeterminate. These rules
are illustrated by the adjudication in the pilot review; schema fields are unchanged.


## Evidence evaluation clarification (2026-09-09)

For independent outputs, source grounding means the nonempty quote occurs in the
specified permitted letter after light Unicode, case, whitespace and dash
normalization. Incorrect character offsets are a separate diagnostic, not a
clinical evidence failure. Stored authored offsets remain checked for integrity.

Reference evidence agreement uses same-letter normalized containment: either
selection may contain the other, following the Gan content-recall diagnostic.
Selections shorter than five characters require equality. This does not match
arbitrary shared words, paraphrases or quotations from different letters.
Source grounding and reference overlap do not prove that evidence supports the
clinical interpretation. Empty evidence has no overlap and needs separate review;
it is not a positive evidence-retrieval result.

The frozen agy inputs and schema are preserved. This audit amendment changes
neither model instructions nor raw outputs; schema shape checks still apply.


## Adjudication clarifications for pilot v0.5 (2026-09-10)

A named holiday can support qualitative inclusion when clearly internal to a
broad window, even without an exact date. Patient 005's “around Christmas” before
1 February supports inclusion in 4 November–1 February. Preserve the original
wording and unknown exact endpoints. This is an adjudicated coarse-time judgment,
not an invented Christmas-day timestamp or a fixed holiday tolerance. Near a
window boundary, unresolved timing remains indeterminate.

An explicit exclusion of all other patterns in a described recurring history
can establish the inventory for that history. Excluding selected named types
cannot. Neither statement automatically extends to an unobserved future interval.

A confirmed initiation date plus affirmative continuing adherence to that same
course can establish that the start predates a window. Current medication use,
a dose increase or a later visit's “no changes” alone do not establish that
history. Patient 010's retrospective continuation supports a negative; its visit
view lacks that later continuity evidence. Later confirmation of a similar event
pattern must support the disputed earlier interval to resolve an earlier conflict;
a June video alone does not settle a specific February episode.


## Patient-wide first reinterpretation (schema/guide v0.2)

A `corrects_interpretation` link may include `first_reinterpretation_evidence`:
source quotations explicitly stating that this is the first change from an
epileptic to a non-epileptic interpretation anywhere in the patient's history.
Omit it or use an empty list when that completeness is unknown. A first correction
of one named pattern does not establish the absence of corrections to other
patterns. Other relationship types cannot carry nonempty first-reinterpretation
evidence. The quotations follow the same grounding and cutoff rules as link evidence.

Combined with a supported decision date strictly after T, this patient-wide claim
can refute Q5 at T. A decision interval crossing T remains indeterminate. Conflicting
positive and negative evidence must not be silently resolved. The new field is
optional for compatibility with schema v0.1; absence never means first or not first.
The field is exercised on patient 001 only before broader annotation migration.
