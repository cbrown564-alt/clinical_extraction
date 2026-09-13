# Longitudinal epilepsy benchmark: task definition

Date: 2026-09-09. Version: working definition v0.2 (with 2026-09-09 adjudication clarification).
Mode: Explore. Owner: Conor Brown for research decisions.

This document owns cohort questions, the two patient views, proposed annotation
needs, seed eligibility and pilot/scaling criteria. It is a concrete starting
definition for the authored example, not a frozen evaluation protocol or an
implemented annotation schema. The [literature rationale](../reference/longitudinal_epilepsy_rationale.md)
owns source comparisons; the [roadmap](../plans/ACTIVE_ROADMAP.md) owns task order.

## Question and bounded population

Does explicit linking of assertions across letters improve evidence-supported
cohort membership compared with independent letter extraction and simple
aggregation, when both systems receive the same permitted letters?

The working population is fictional adults (18 or older at the first visit) in
English-language outpatient epilepsy care, including uncertain diagnoses and
suspected non-epileptic events. Known patient IDs are supplied. Patient matching,
paediatric care, emergency/inpatient reconstruction, treatment recommendation,
prediction, and inferring a new diagnosis from tests are outside this version.
This adult/outpatient restriction is a project choice, not an eligibility rule
transferred from an existing benchmark.

Use four clinical families: epilepsy diagnosis, seizure events/patterns,
medications, and investigations. The first patient has three letters; the pilot
has 12 patients / 36 letters. The later 300-patient target remains provisional.
The authored example is not generated from a source letter and is development-only.

## Evidence time and the two views

Every evaluation request specifies a patient, an index date `T`, an information
cutoff, a query, and a view. Dates are inclusive calendar dates unless the query
states otherwise. A 90-day lookback is `[T-89 days, T]`; a 180-day lookback is
`[T-179 days, T]`. Calendar months must not silently become 30-day units.

| Time | Meaning | Consequence |
| --- | --- | --- |
| Visit date | When the consultation occurred | Anchors “since the last visit” only when that visit is identifiable. |
| Document availability | When the letter/version became available to the evaluated system | Determines whether the text is allowed at a cutoff. Never backdate a delayed letter to its visit. |
| Event/valid interval | When an assertion says an event occurred or a state applied | Determines whether it answers the query window. It may be uncertain or earlier than the visit. |
| Later evidence cutoff `R` | Last date from which retrospective evidence is allowed | Must be declared, at least `T`, and common to all methods. |

**Visit account:** use only document versions available by `T`. Preserve the
assertions and uncertainty supported then, even if later letters correct them.

**Retrospective account:** answer the same question about the same index/window,
but allow documents available by `R`. A later assertion may reinterpret an earlier
event only when its text supports that relationship. Return the earlier assertion,
the later evidence and the link that changes the interpretation. A subsequent
new seizure is not a correction to an earlier seizure-free interval.

For the pilot, preassign two exact query index dates 180 days apart per patient in
the case metadata, independently of the clinical state. Set `R = T + 180 days`
for each request: retrospective follow-up has a fixed 180-day information window.
Missing follow-up does not remove the request or imply absence of events; later
documents beyond `R` are excluded even when present in the case pack.
Query dates and `R` are supplied
evaluation metadata, not inferred from hidden history. The two views receive
physically filtered inputs; full histories cannot be passed with an instruction
to ignore future letters.

For partial dates, retain bounds and original text. An event wholly inside a
window can support membership; one overlapping its boundary may leave it
indeterminate. For availability bounds, admit a document only when its latest
possible availability date is at or before the cutoff. Missing availability is
not imputed from visit date; the letter is excluded with that reason. In the
synthetic case pack, availability metadata should normally be exact even when
dates inside the letter are vague. A missing visit date must not prevent using
independently dated evidence in an otherwise eligible document.

“Current” without a supported duration anchors a statement to its visit, not to
every subsequent day. A continuing diagnosis may remain documented until an
explicit revision; this is persistence of the documented diagnosis, not proof of
unchanging clinical truth. Medication use and seizure absence are not extended
across unobserved intervals merely because nothing else was recorded. No letter
means missing observation, not remission, cessation or a negative test.

## Cohort questions

All five questions apply to every case at both supplied index dates in both views.
Each returns `eligible`, `ineligible`, or `indeterminate`, plus evidence and a reason.
Here “eligible” means the documented predicate is supported, not eligible for a
clinical intervention. `Ineligible` requires evidence that the predicate is false;
failure to find support is `indeterminate`. A contradiction that can change the
answer remains indeterminate until an explicitly supported resolution exists.

| ID | Predicate / fixed window | Required support and negative/unknown boundary |
| --- | --- | --- |
| Q1 | Documented epilepsy at `T` and at least one epileptic seizure in the 90-day lookback | Link events to their documented interpretation. Explicit whole-window absence of all epileptic seizures, or an explicitly ruled-out epilepsy diagnosis at `T`, can make the conjunction false. Absence of one seizure type cannot establish global seizure freedom. Missing diagnosis/event evidence is indeterminate. |
| Q2 | At least two distinct patterns interpreted as epileptic in the selected view, with overlapping active intervals somewhere in the 90-day lookback | Retain non-epileptic patterns in the history but do not count them in this predicate. Two mentions of the same pattern count once. Different names alone do not prove different patterns. Explicitly only one/no active epileptic pattern throughout the window can support ineligible; an incomplete inventory is indeterminate. |
| Q3 | A named antiseizure medication was actually started during the 180-day lookback | The query names the drug in supplied metadata, fixed before extraction. Require reported/confirmed use with a start interval; a prescription, conditional plan or proposed increase alone does not count. Explicit non-initiation throughout the relevant period can refute; silence after a plan is indeterminate. |
| Q4 | An EEG or MRI requested in the 180-day lookback has a documented result available by `T` | Query metadata names the modality. Link request, performance and result; a result for an unrelated older test cannot satisfy it. Cancellation or explicit pending/no-result status as of `T` can refute; no follow-up text is indeterminate. Retrospective evidence may clarify that a result existed by `T`, but a result first available after `T` cannot satisfy the predicate. |
| Q5 | A previously documented epileptic event/pattern from the 180-day lookback was explicitly reinterpreted as non-epileptic by `T` | Require earlier and revising assertions about the same event/pattern, and a dated reinterpretation no later than `T`. A new unrelated event is not a revision. An explicit reassessment retaining the interpretation can refute; absence of a revision alone is indeterminate. Retrospective text can reveal a revision made earlier, not move a later decision back in time. |

Drug/modality query parameters are fixed in the scenario plan, never chosen from
model successes. For conjunctions use three-valued logic: any definitively false
required predicate makes the conjunction false; all true makes it true; otherwise
indeterminate. For existence over events, one supported qualifying event suffices;
an incomplete event inventory cannot prove none exist.

For Q4, “result available by T” means explicitly reported as available to the
treating clinical team by T. The availability of the letter reporting that fact is
a separate time controlling the model's input. Retrospective text can establish an
earlier clinical result date; a performed date alone cannot. For Q5, an event or
pattern is “from the lookback” when a supported occurrence lies within it, even if
the pattern's first description predates it. Both identity and the date of the
reinterpretation still need evidence. Boundary-overlapping occurrence dates remain
indeterminate unless other evidence settles the predicate.

The queries deliberately cover distinct mechanisms, not prevalence estimates or
treatment effects. No primary causal claim about medication response is proposed.
Frequency ranges, bounds and cluster counts remain explanatory history outputs:
they must not be converted into invented point estimates to answer these queries.

## Primary endpoint and comparison

The selected primary downstream endpoint is **patient-averaged cohort-answer
accuracy** on the fixed five queries, two index dates and two views. For patient
`p`, count exact matches of the three-way membership status across its 20 requests
and divide by 20; average that value over patients. Report the linked-minus-simple-
aggregation paired difference. Every patient has equal weight. Call/parse failures
are wrong answers, not indeterminate answers or dropped rows.

The reference status is determined from permitted text, not the hidden scenario.
Irreducible uncertainty has the status indeterminate and may allow multiple
evidence explanations; do not award either eligible or ineligible for the same
unresolved reference. Report uncertainty reasons separately.

Report both views and each query separately, all three reference-state counts,
the confusion matrix, eligible precision/recall, indeterminate performance and
always-indeterminate/majority baselines. This prevents easy unknown cases from
being mistaken for useful cohort extraction. Seed-family clustered paired
uncertainty estimates belong in the frozen evaluation protocol; the 12-patient
pilot reports counts and paired changes, not powered significance claims.

Predeclare these comparisons before Phase 7 model selection:

- **Simple aggregation comparator:** identical per-letter extraction outputs;
  exact normalized-name matching and date filtering, no inferred cross-letter
  event identity or correction links. Preserve unresolved conflicts. Fix the
  matching and tie rules before comparing results.
- **Linked candidate:** same extracted facts and query evaluator; add only the
  cross-letter identity/update/correction decisions under study. Keep every
  assertion and the evidence for each link.
- **Whole-history comparator:** a model answers from the same eligible letters
  directly. Keep model/version and available context comparable; record token,
  call and latency differences rather than asserting equal computation.
- **Majority-phenotype diagnostic comparator:** following the aggregation idea in
  [Chang 2026](../reference/longitudinal_epilepsy_rationale.md#chang-reference-resolved),
  compare majority epilepsy category across eligible visits, then specificity
  within that category. Apply the same cutoff and preserve ties as unresolved.
  This is an epilepsy-phenotype diagnostic, not a complete Q1–Q5 baseline or a
  substitute for text-supported reference. Do not extend voting to drug use or
  event corrections.
- **Attribution checks:** reference per-letter facts with/without reference links,
  plus removal of inferred links from candidate output. Attribute a changed
  answer to extraction, temporal normalization, linking or query evaluation.

Supporting measures: supported fact and link precision/recall, evidence-span
validity, temporal-boundary errors, unsupported corrections, cutoff leakage,
plan-as-use errors and lost concurrent patterns. They explain the endpoint; they
do not replace it after seeing which metric improves. Freeze scorer details and
split assignments before model comparison. Pilot revisions require a versioned
amendment here, with the reason; all inspected pilot cases remain development.

## Proposed annotation information and purpose

This is a minimum information inventory for Phase 2, not a JSON schema or an LLM
prompt. The worked example decides the final field names and representation.
No field is required solely because another benchmark has it.

| Proposed information | Downstream use |
| --- | --- |
| Patient ID, letter/version ID, assertion ID | Supplied patient grouping; evidence lookup and reproducible Q1–Q5 answers. |
| Visit date, availability date/bounds and uncertainty reason | Filter inputs; distinguish late documentation from an event at Q1–Q5 cutoffs. |
| Exact source span offsets and text | Verify that facts, negation and links are supported; explain all query answers. |
| Family, source wording and normalized concept | Distinguish epilepsy diagnosis, seizure pattern, named drug and test modality. |
| Reporter/author attribution, assertion certainty and negation | Preserve patient/clinician disagreement without voting or inventing certainty. |
| Event/state time text, bounds, precision and temporal anchor | Determine membership in query windows without false date precision. |
| Pattern/event identity and type, concurrent pattern relation | Avoid duplicate counting and loss of concurrent patterns in Q1/Q2/Q5. |
| Frequency count/range/bound, denominator interval, cluster count and events per cluster when stated | Explain reconstructed burden without collapsing concurrent patterns or treating clusters as individual events. |
| Absence scope and supported interval | Distinguish type-specific absence from global absence in Q1/Q2. |
| Diagnosis assertion and revision relationship | Establish documented epilepsy and event reinterpretation in Q1/Q5. |
| Medication name, plan/prescription/use/non-initiation/stop status and supported time | Q3; dose fields are deferred because this query does not require dose comparison. |
| Investigation modality, request/performed/result/pending/cancelled status and time | Q4; retain reported results, never infer a diagnosis from them. |
| Link endpoints, relation, certainty and evidence | Repetition, updates, correction and unresolved conflict in Q1–Q5. |
| Query/index/view, membership status, evidence IDs and uncertainty reason | Primary scoring and inspectable answers. |
| Source release/record ID, seed-family ID, generated-patient lineage, versions and text hashes | Prevent descendant leakage and reproduce the case; kept separately from model inputs. |

Demographic detail beyond eligibility, unrestricted past medical history, full
ontologies, treatment-response causality and inferred disease severity are deferred.
Hidden generation facts are a separate authoring record; they never fill gaps in
the text-supported reference or appear in extractor inputs.

## Seed eligibility and allocation decision

Replace the infeasible 150 ExECT / 150 Gan distinct-record assumption with a
**provisional ceiling of 140 ExECT development records plus 160 Gan development
records**, one selected source record per generated patient. These are maximum
candidate allocations, not verified counts of eligible independent families.
If provenance, duplication or content checks reduce a pool, reduce the total or
author additional seed-free patients with disclosed origin; do not silently reuse
records to satisfy 300. New seed-free cases form their own disclosed authoring
lineage. Source style and clinical outcome must be varied independently.

The only existing candidate pools are ExECT `dev140` and Gan `dev750` (the latter
is `validation` in its split manifest). Exclude `test60`, `test450`, Gan `train300`,
and unsplit ExECT material. Public download availability does not override these
repository inspection boundaries. Original benchmark labels are not longitudinal
gold. No source records have been selected or copied during Phase 1.

Metadata-only split inspection on 2026-09-09 pinned these local manifests:

| Manifest | SHA256 |
| --- | --- |
| `data/ExECTv2 (2025)/splits/exectv2_split_v2.json` | `d5109b158d18c4234a86d4dacfc9621421351045b5d4b9351479b941ebb92cbc` |
| `data/Gan (2026)/splits/gan2026_split_v1.json` | `c5f512d8744261916bd6d92562430489a3ba0494b0bf7c6575bfaa9e58680143` |

Counts/pool meanings follow the existing
[dataset inventory](../research/shared/dataset_description_2026-08-26.md).
No locked IDs or contents are reproduced here.

The [source-use audit](../reference/longitudinal_epilepsy_rationale.md#source-use-findings)
verifies the ExECT letter release licence; Gan subset release terms remain
unresolved. Before source-conditioned generation, record release/version, local
hash match, permitted split membership, attribution and any restrictions for the
actual input. A seed-free worked example can proceed immediately.

Before splitting generated data, group all descendants of a source record and
any shared original template/description ancestor. Distinct Gan rows are not
necessarily independent: its paper describes ten base letters. Record exact and
near-duplicate checks on permitted material, review duplicate groups, and keep
each connected lineage in one split. Do not use held-out letter content to tune
duplicate thresholds. When upstream ancestry is unavailable, use conservative
grouping and narrow claims; do not call a random row split source-independent.
Actual lineage audit and split freeze occur before corpus generation/scaling.

## Coverage, budget and conditions for scaling

Use the authored three-letter patient to test concurrent patterns, a medication
plan not enacted, and later reinterpretation. Expand only after its text and both
accounts can be inspected. For the 12-patient pilot, the following are coverage
targets, not mutually exclusive strata or population frequencies:

| Feature | Minimum pilot coverage | Purpose |
| --- | --- | --- |
| Ordinary unchanged follow-up | 3 patients | Avoid a corpus consisting only of traps. |
| Concurrent patterns / type-specific absence | 3 | Q1/Q2 distinction. |
| Copied or renamed history | 2 | Repetition must not count twice. |
| Planned medication not enacted; actual start | 2 each | Q3 negative/positive cases. |
| Requested test with later result; pending/cancelled test | 2 each | Q4 identity and timing. |
| Explicit reinterpretation; unresolved reporter disagreement | 2 each | Q5 and indeterminate answers. |
| Delayed document; partial event dates | 2 each | Availability versus event-time boundaries. |
| No-reference letter / missing outcome / irregular gap | 3 | No inference from silence. |

Across pilot requests, each query must have at least two examples of each
membership status. Include cases where the two views differ and where they agree;
do not force differences in every history. Show which request needs evidence from
more than one letter. Match ordinary and difficult cases across styles where
feasible; do not always associate one source style with one outcome.

**Budget:** £0 in additional paid model calls is authorized by this document.
No calls are needed for Phase 1 or the authored example. A question about a later
pilot cap is pending with Conor; absent an answer, £0 remains the working cap.
Do not start a provider run based on the 300-patient target. Before any paid run,
record provider/model/version, data terms, input/output token estimate, retries,
per-patient cap and total hard cap in the generation protocol. Stop when the next
request could exceed the remaining cap; include failed calls in cost accounting.

The 300 target is a workload/coverage allowance, not a power calculation. The
pilot determines annotation time, ambiguity, eligible lineage count and generation
failure rates. Re-estimate scale using those measurements and available budget;
do not manufacture precision from 12 development patients.

Before expanding beyond the pilot, require:

1. Every scored assertion/link has valid evidence or an explicit unsupported flag;
   references contain zero unsupported definitive answers and zero cutoff leaks.
2. Every pilot request has a reference status or a recorded annotation defect;
   defects are repaired or converted to text-supported indeterminacy, not dropped.
3. A second independent annotation pass reports disagreement and time by family,
   time field and relation. Unresolved disagreements remain visible. AI agreement
   is not expert agreement; lack of expert review is stated rather than fabricated.
4. The coverage matrix is met; no field is retained without a query/history purpose.
5. Seed lineage, source terms, revision/version records and a costed generation
   configuration are complete for the proposed next batch.
6. One end-to-end patient/query replay is reproducible. The pilot need not show a
   model gain to justify a useful negative result; unsupported links are not hidden
   to improve a score. Revise or simplify if annotation cost defeats the question.

## Phase 1 disposition and next action

P1.2–P1.3 have concrete working definitions above; P1.4 has a revised allocation
and explicit source-use conditions; P1.5 has coverage and a zero-spend default.
The supplied Chang preprint resolves P1.1's named-reference comparison. Gan source-use
evidence and any paid pilot cap are required only for their dependent generation,
not for a seed-free example. Phase 1 working documents are ready for the Phase 2
example; clinical validation and generation prerequisites remain outstanding.

P2.1 now has a [three-letter authored example](../../examples/longitudinal/authored_patient_001/README.md)
with all 20 expected answers. Version 0.2 clarifies Q2's epileptic-pattern scope,
Q4's clinical result availability and Q5's occurrence-based lookback membership;
the example demonstrates each. These are pre-comparison task clarifications,
not changes to Gan or ExECT scoring.

Phase 2 is complete for authored development under the v0.8 pilot review.
Current work advances to the prepared Phase 3 seed-free probe.
The pilot review owns current findings; the generation protocol owns the next
seed-free batch procedure. No corpus freeze, expert reference or clinical release
is established by these development checks.


## Pilot reference amendment: v0.4 (2026-09-09)

User-authorized adjudication corrects patient 003 T1 Q5 in both views from
ineligible to indeterminate. Seizure freedom excludes active epileptic seizures
for Q2 when it covers the whole window, but does not inventory earlier episodes
that may have been reclassified for Q5. A visit-level negative about tests or a
named pattern is not a whole-window inventory for Q4 or Q2. The five predicates,
query dates and schema are unchanged. The pilot review owns all five decisions;
original v0.3 references and model captures remain preserved separately.


## Pilot reference amendment: v0.5 (2026-09-10)

Adjudication of the remaining 12 disagreements corrects three reference decisions
and retains nine. Two parallel T1 visit answers receive the same correction as
their identical-input retrospective counterparts, for five reference changes.
Patient 005 T1 Q1 is eligible in both views using coarse holiday inclusion in a
broad window; Q2 is ineligible in both views using explicit exclusion of all
other patterns in the described history. Patient 010 T2 retrospective Q3 is
ineligible using confirmed pre-window initiation and affirmative continued
adherence. No exact holiday date or new date bound is imputed. The annotation
guide owns these interpretation clarifications; the pilot review records each
decision. This revises the previous overly strict date-bound/reference treatment,
not the five predicates, supplied cutoffs or frozen model inputs.


## Pilot annotation amendment: v0.7 (2026-09-10)

The five predicates, fixed query dates and all reference statuses are unchanged.
Four temporal annotation records were corrected and patient 011 gained existing
patient-wide first-reinterpretation evidence under schema v0.2. The pilot review
owns the before/after evidence and a full 240-request field-deletion diagnostic.
Internal coverage minimums are accepted; incomplete negative-history representation,
semantic link alignment and missing within-family/human timing prevent broad
P2.6 closure. The generation protocol prepares a zero-additional-paid-call,
seed-free one-patient probe before any 5/12-patient expansion.


## Pilot annotation amendment and Phase 2 disposition: v0.8 (2026-09-10)

Schema/guide v0.3 adds optional evidence for explicitly complete prior history,
exercised on four non-use assertions in patients 001 and 005. A null onset alone
still cannot establish that scope. The 36 source letters, fixed query dates and
all 240 expected answers are unchanged. The five predicates and scoring policy
are unchanged; this amendment adds representation rather than a new clinical rule.

The pilot review records Phase 2 completion with explicit unresolved cases:
144 temporal-pair and 89 unaligned-link dispositions, 18 measured independent AI
calls by activity, paired schema/guide revision, accepted coverage and nine-variant
query replay. The incomplete structured evaluator matches 229/240 authored answers;
11 conservative gaps remain named implementation cases. Raw output QC errors and
source-attribution alternatives remain visible. No clinical agreement or human
effort is inferred from these measurements. The original completion criterion
permits a provisional schema and unresolved cases; full execution and expert
reference retain their own later-phase requirements.
