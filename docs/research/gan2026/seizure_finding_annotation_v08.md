# Seizure-finding annotation v0.8

Versioned owner for the simplified annotation unit and finding scorer agreed after
reviewing the saved R8 development errors on 23 September 2026. The [v0.7
guide](seizure_finding_annotation_guide.md) remains the rule for its frozen
reference and published development scores. The full inventory of distinct
current, historical and event-type claims remains in scope.

## Annotation unit

Keep the v0.7 event, timing, evidence and measurement structures except for
these changes:

1. A numeric rate/count and accompanying trend, rarity or variability language
   about the same event and observation window make **one scored finding**. Keep
   the numeric finding. Trend and variability are neither separate findings nor
   scored modifiers. If the text gives only a trend and no level or quantity,
   do not annotate it.
2. A standalone qualitative frequency has only two values: `occasional` and
   `frequent`. Map `rare`, `infrequent`, `intermittent` and `sporadic` to
   `occasional`. Do not score `increased`, `decreased`, `unchanged`, `variable`
   or `unknown` as frequency levels. Keep a standalone level when no more precise
   measurement of the same claim is present.
3. A diary or source list of counts for the **same measured event** across named
   months makes one count over the listed interval. Add the stated numbers, with
   zero months included in the interval. State the interval in `period.time`;
   the combined period need not be a verbatim phrase. Do not infer missing months
   or combine different event types. Counts of *seizure days* remain seizure-day
   counts. A count for one event type and a separate count for another remain
   separate unless the source states a joint total.
4. A list of individually dated occurrences of the same event makes one count
   over the listed dates. When a stated total already counts those same dates,
   retain the stated total once.
5. A single absence statement listing several named seizure types in the same
   observation interval makes one seizure-free finding for the combined claim.
   Distinct time windows or independently stated absences stay separate.
6. Match equivalent source descriptions of the same observation window (for
   example, “over the past week” and “this week” in one source sentence). Keep
   different denominators and periods distinct. Evidence must still overlap;
   event, timing, status and measurement must meet the versioned scorer rules.

Do not apply a blanket “one finding per sentence” rule. A sentence can state
distinct event types, windows, or measurements that remain independently scored.
The v0.7 guide's conservative source and holdout safeguards still apply.

## Saved R8 development conversion

The v0.8 reference is a **new** local-only snapshot converted from the reviewed
v0.7 dev750 reference. The scorer projects saved R8 findings with the same
representation rules, without changing the raw response or calling a model.
Every changed finding is recorded in `conversion_audit.jsonl`; every source row
and its exact source hash are retained. The code's explicit month-list and
date-list row sets are the audited conversion manifest for this saved dataset.
They prevent a proximity rule from summing separate historical incidents.

Source 5995 is left as an exception for further review: its month list mixes
generalised convulsions, an absence cluster and brief events. A joint seizure
count would require deciding whether the three brief events within the cluster
are additional to the cluster count. No total is inferred. Other residual
prediction and reference differences remain available for the next review pass.

Run `.venv/bin/python scripts/benchmarks/score_findings_v08.py` to reproduce the
reference, audit and saved-response score. The portable structural schema is
`results/letter-benchmarks/gan/seizure_finding_annotation_v0_8/annotation.schema.json`.
The local artifacts are under `runs/seizure_finding_annotation_v0_8/dev750_r8_saved/`;
the aggregate and per-letter score is under
`results/letter-benchmarks/gan/seizure_finding_annotation_v0_8/dev750_r8_saved/score.json`.
The local workbench can compare the versions using **Labels → v0.7 Finding
Purist / v0.8 simplified** at `?dataset=ganR8`; v0.8 rows come from the saved
review bundle and keep the original R8 selected-answer endpoint.
This is a changed target and scorer on synthetic development letters, not a new
model result or a holdout estimate.

## v0.8.1 timing amendment (23 September 2026)

The owner changed the meaning of `timing` after reviewing recent dated events
that v0.7/v0.8 marked historical. Use the **clinic date** as the reference; use
the letter date if no usable clinic date is present. A finding is `historical`
only when its measured event, or the end of its observation interval, is **more
than one calendar year** before that reference date. An event on the one-year
anniversary is `current`. An interval that reaches into the last year is
`current`, even if an earlier part is older. An ongoing current pattern or
seizure-free state stays `current` regardless of when it began.

An explicit, usable date or relative interval takes precedence over narrative
words such as `initial`, `previously` or `before treatment`. If the event
date cannot be resolved enough to apply the cutoff, explicit past wording
(including `in childhood`) still makes the finding `historical`; otherwise
default to `current`. When a coarse date such as a year alone straddles the
cutoff, retain the source's explicit past/current wording and flag it for review
rather than inventing a month. Compare dates to assign `timing`, but preserve
the source time expression in the finding. Do not infer an event count or new
duration from this comparison.

The original v0.8 reference and saved-R8 score remain frozen. The versioned
v0.8.1 conversion reads all 750 v0.8 development letters, records every changed
finding with its clinic date and source evidence, and keeps the projected saved
R8 predictions unchanged. Its producer is
`scripts/benchmarks/retime_findings_v081.py`; the local audit and reference
are under `runs/seizure_finding_annotation_v0_8_1/dev750_r8_saved/`, and the
new score is under
`results/letter-benchmarks/gan/seizure_finding_annotation_v0_8_1/dev750_r8_saved/`.
The workbench **Labels → v0.8.1 one-year timing** view shows this comparison.

The prospective model-facing wording is in
`src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/one_shot_measurements_r9.py`.
The saved R8 prompt and outputs are untouched. R9 is a prompt candidate; it has
not been run or evaluated as a new model result.

## Subsequent owner decisions for the next annotation revision

These decisions were made during the continuing saved-R8 error review. They are
prospective and have **not** been applied to the v0.8.1 reference or score.

- When a letter gives a dated last seizure and a current seizure-free interval,
  an undated, vague statement that events happened `occasionally` in the same
  history is context, not another scored frequency finding (source 2992).
- When a stated total is broken down by trigger, score the total once and keep
  the subcounts as context. A separately stated last-seizure date remains a
  finding (source 14146: three total, one after missed doses and two without a
  clear trigger).
- A longest seizure-free gap within an ongoing seizure pattern is a distinct
  scored finding from the event rate (source 12506: three weeks and one to two
  tonic-clonic seizures per month).
- A symptom explicitly lacking seizure features is not a seizure-frequency
  finding unless the clinician identifies it as a seizure event (source 8355:
  occasional `head-fog`).
- Use a concise, source-supported event label. An incidental descriptor such as
  `brief` does not distinguish `brief nocturnal episodes` from `nocturnal
  episodes` when the evidence and rate are the same (source 704). Preserve
  seizure subtype and counted unit: clusters, seizures and seizure days are
  different; a rate covering only one listed subtype must not be attached to
  all listed types. The R9 prompt candidate includes this instruction. A future
  versioned scorer must test label equivalence with evidence and measurement;
  the current v0.8.1 saved-response score remains unchanged.
- Score subtype, event label and measurement as separate diagnostic components alongside
  the whole-finding score. When an adjacent sentence gives the frequency of a
  just-described subtype, carry that subtype into the event label (source 3999:
  `focal impaired-awareness episodes`, one per month). Saved R8 got the
  measurement right and the subtype wrong. The versioned v0.8.1 component
  diagnostic records these separately without changing the whole-finding score.
- An overall rate for `episodes` stays overall when the source says the episodes
  are `predominantly focal`; that word describes the mix, not a restriction on
  the denominator (source 5551). A separately stated generalised breakthrough
  rate remains its own finding. Do not attach the overall rate only to focal
  events because they are the majority. This corrects the prospective R9
  instruction; the saved R8 response and v0.8.1 gold stay unchanged.
- When a device reports no convulsive activity over six months and an event log
  explicitly corroborates it with no events requiring rescue measures, score
  one absence finding for `convulsive activity` (source 8805). The rescue-log
  clause is supporting context. The v0.8.1 gold currently says `events requiring
  rescue measures`; correct that label in the next versioned reference rather
  than editing the frozen score in place.
- When the source describes weekly clusters of roughly six events each, use
  `clusters` as the event label and keep weekly cadence and events per cluster
  in the cluster measurement (source 8969). A generic `events` label loses the
  counted unit even when the measurement type is `cluster`. The existing gold
  already uses `clusters`; the R9 prompt now states this convention.

## v0.8.2 claim-unit amendment (23 September 2026)

The owner confirmed that a recalled brief episode of confusion without
collapse is an **unscored possible event**, unless the letter identifies it as
a seizure or connects it to an established seizure type (source 8805). This
extends the established rule for symptoms lacking seizure features (8355),
without excluding all explicitly named possible seizures.

Apply one scored finding to a continuous seizure-free interval stated several
ways across a letter. Prefer a stated duration as the scored measurement;
retain a co-stated `since` anchor as unscored context. Different seizure
subtypes, event scopes, and independently measured windows remain separate.
When a total count is followed by its trigger or time-of-day breakdown, score
the total once unless a breakdown separately measures a named seizure subtype.
The longest seizure-free gap amid ongoing events remains a separate measured
claim from their rate. For a device absence corroborated by an event log, name
the directly reported clinical event (`convulsive activity` in 8805).

The complete dev750 saved-R8 comparison was screened by
`scripts/benchmarks/audit_claim_representation_v082.py`. Its local JSONL has
one record per source letter, preserving IDs, hashes, exact quotations,
source-aligned component differences, unpaired findings and rule-review flags.
The flags are review candidates: a repeated absence may cover a different
subtype or window, and a qualitative level beside a number may refer to a
different event. Do not delete either solely because it was flagged.

The source-adjudicated v0.8.2 reference applies the clear owner decisions
using the explicit manifest in `scripts/benchmarks/revise_findings_v082.py`.
Every changed finding has before/after evidence in local
`runs/seizure_finding_annotation_v0_8_2/dev750_r8_saved/claim_adjudications.jsonl`.
The v0.8.1 reference and raw R8 output remain unchanged. The v0.8.2 scorer
ignores a `since` anchor when both sides state a seizure-free duration; it
still requires the duration, source overlap, event label and timing. This is a
changed synthetic-development target, not a new model run. The workbench
version selector can display **v0.8.2 claim units**.

## v0.8.3 owner batch decisions (23 September 2026)

The owner resolved four question groups from the full development audit:

- Give a mixed diary **one overall count of individual seizures** when its
  components can be added without counting a subset twice. Retain separate
  named subtype and cluster findings. In source 5995, the January–September
  diary has two generalised convulsions and an absence cluster containing three
  events: five individual seizures overall. The cluster is one cluster, not one
  additional individual seizure; zero months establish the observation interval
  but are not separate seizure-free findings. Do not infer a total when cluster
  size or overlap is unclear. Sources 15982 and 16041 have clear combined
  daytime and nocturnal counts; a zero subtype alone does not justify an
  otherwise identical duplicate overall count (15992).
- A broad seizure-free summary can be **one additional scored finding** beside
  subtype-specific absence claims with different anchors. In source 9190,
  absence of focal impaired-awareness events or convulsions since February,
  absence of auras since April, and the broader no-clinical-seizures summary
  each have a distinct scope or interval. A second broad restatement, a vague
  prior `occasional auras` description, and another observer's corroboration
  of the February absence remain context. Preserve both named types in the
  February combined absence label.
- A **recurring grouped-event pattern** supports a cluster measurement even
  without the source word `cluster` (for example 15442, with recurring days of
  multiple tonic seizures after seizure-free days). Name the counted unit as
  `clusters` or `clusters of [named subtype]`. An isolated multiple-event day
  does not by itself establish a recurring cluster cadence. Existing explicit
  single-cluster count/size findings remain separately reviewable under the
  earlier count-versus-cluster rule.
- An uncertain symptom is unscored unless the clinician identifies it as a
  seizure/event in scope or explicitly links it to an established seizure type.
  Non-specific nocturnal restlessness (4694, 7093), prior collapse later
  assessed as non-epileptic (5092), a possible isolated brief event (7195),
  and bed-disarray inference without a witnessed event (15783) are unscored.
  A brief aura described elsewhere as the patient's focal aura (8144) remains
  in scope; uncertainty wording alone does not erase that clinical link.

The additive v0.8.3 producer is `scripts/benchmarks/revise_findings_v083.py`.
Its local adjudication manifest records every changed finding with source
identity, evidence, and before/after values; it reads the frozen v0.8.2
reference and saved R8 projection. The same v0.8.2 scorer is used, so any
score change reflects reference representation rather than a new model run.
The workbench **v0.8.3 owner decisions** view exposes the revised comparison.

## Prospective two-week seizure-free minimum (23 September 2026)

The owner set **two weeks** as the minimum for a separately scored seizure-free
interval. A known shorter interval is context, including four or five days
between recurring cluster days (sources 15442 and 15470). The threshold is a
necessary condition, not sufficient evidence of a separate absence claim:
"may remain seizure-free for up to four months, then has a cluster" (15404)
describes a typical or maximum gap in an ongoing pattern. Keep the cluster
finding; do not add seizure freedom from that gap. A distinct current absence
of two weeks (14872) and an explicitly reported longest seizure-free period
of three weeks (12506) remain eligible. When a since anchor has no resolvable
duration, retain an explicit seizure-free state without inventing an interval.
An anchor explicitly known to be under two weeks is ineligible (15513:
"none since" a seizure ten days ago); its last-seizure finding remains.

This is a prospective annotation decision and R9 prompt amendment. The v0.8.3
reference and saved-R8 score remain frozen; source 15513 needs a versioned
reference edit before any new score claims this rule. The separate question of
whether a cluster's within-cluster span belongs in scored `period` was resolved
in v0.8.5 below.

## Prospective cluster and seizure-link decisions (23 September 2026)

- A single grouped occurrence is **one cluster** with `count: 1` and the
  stated `seizures_per_cluster`, even without a recurring pattern (16645:
  one August cluster of three; 16757: one April run of six). Keep its date in
  `occurred_at` for review, but do not score that date. Source 16772 literally
  describes a run of one seizure; retain the source's one-cluster representation
  without inferring additional events.
- A statement giving both affected cluster days and seizures per cluster day
  is **one structured cluster finding**: `count` is the number of cluster days,
  `seizures_per_cluster` is the within-day seizure number, and `period` is the
  observation window (11109, 11118, 11131). Do not score a second seizure-day
  count from the same claim. A separate claim about individual seizure days
  remains independently reviewable.
- Score uncertain spells only when the source explicitly identifies them as
  seizures or links them to a named or established seizure type. The suggestion
  of brief absences in 3528 and the established focal auras in 8144 qualify.
  In 6738, the clinician's concern for reduced-awareness spells alone is not
  an explicit seizure link, so its six-to-eight-week rate is unscored context.

These decisions are prospective relative to the frozen v0.8.3 reference and
saved-R8 result. Scoring the span *within* a cluster is resolved in v0.8.5
below; it differs from the observation window for a cluster count.

The additive v0.8.4 development reference now applies these decisions and the
two-week minimum. Its producer is `scripts/benchmarks/revise_findings_v084.py`;
the [v0.8.4 result](../../../results/letter-benchmarks/gan/seizure_finding_annotation_v0_8_4/dev750_r8_saved/README.md)
owns the edit manifest, score and exceptions. The saved R8 predictions are
unchanged. R9 is still an unrun prompt candidate.

## v0.8.5 unscored within-cluster span (23 September 2026)

The owner confirmed that **cluster size and any stated cadence are scored**.
The span containing seizures *within* a cluster, such as `a day`, `within 24
hours`, or `within half an hour`, is **unscored context**. Keep it in the exact
evidence quotation for review, but do not use `period` for that span or infer a
daily span when none is stated. `period` remains the observation window for an
observed cluster count: `two cluster days this month` (11131) and `two clusters
within a fortnight` (10618) still require those windows. `occurred_at` remains
useful unscored detail for a dated single cluster.

The [v0.8.5 result](../../../results/letter-benchmarks/gan/seizure_finding_annotation_v0_8_5/dev750_r8_saved/README.md)
owns the 18 source-audited edits, versioned scorer and saved-R8 comparison.
The prior references and results remain frozen. R9 has prospective instructions
but no new model output.

## Candidate compact primary finding policy (23 September 2026)

Conor chose a narrower **primary finding score** after reviewing the saved-R8
errors. This is a prospective candidate, not a change to v0.8.5, its 750-letter
reference, or any saved score. The paper's primary selected-frequency answer and
one-call design remain separate and unchanged. The candidate finding score should
measure the seizure activity needed to explain the current clinical state, rather
than every historical quantified mention. The extraction prompt and gold guide
must use the same scope before a new run can test it.

### One-sentence rule

Record each distinct, source-supported measurement of **current seizure activity**
once, together with an explicitly stated last event and the nearest measured prior
state that the letter uses to explain a change; preserve event subtype, counted
unit, uncertainty and observation window, and keep corroboration or incidental
detail in evidence rather than making another scored claim.

### What enters the candidate primary score

1. **Current activity:** an ongoing or current-assessment rate, observed count,
   measured cluster pattern, anchored seizure-free state, or standalone
   occasional/frequent level when no more precise statement measures the same
   event and window. Current means the state presented as applying at the clinic
   assessment; the one-year recency flag does not make a superseded pattern
   ongoing.
2. **Last event:** one explicitly identified last or most recent seizure/event,
   with its stated date or relative time, even when the current state is
   seizure-free. An ordinary dated event is not promoted to the last event.
3. **Change comparator:** for each current event population, at most the nearest
   earlier measured state that the source explicitly contrasts with the current
   state (for example, a prior monthly rate before treatment versus current
   seizure freedom, or a prior absence interval before a documented relapse).
   A source-stated change in the named seizure type can justify one separate
   comparator for that type. Do not infer a comparison merely from chronological
   ordering of diary entries.
4. **When no current measurement is given:** retain the most recent measured
   seizure-activity claim as a primary finding so the inventory does not imply
   that the letter contained no relevant measurement. Its phase remains
   `past_or_unclear`, not ongoing by default. This does not create a current
   frequency answer from an old count.

Other historical measurements, repeated summaries, diary entries that merely
support a selected total, trend-only language, trigger/time-of-day breakdowns
without a distinct named subtype, and within-cluster spans are unscored context.
The exact quotation remains available for review. An old diary is not summed into
a current rate. A source-stated total and an affected-day count are different
units; do not substitute one for the other.

### Decision order for an annotator

1. Is this the patient's event, explicitly a seizure or linked by the clinician
   to an established seizure type? Exclude plans, thresholds, family history,
   non-seizure events and unlinked symptoms. A linked but explicitly possible
   seizure keeps `uncertain` status.
2. Is there a stated rate, count with window/date, cluster count/cadence/size,
   anchored absence, explicit last event, or standalone frequency level? If not,
   retain the text only as context.
3. Identify the event population and the **counted unit**: individual seizure,
   affected day/night, cluster, or cluster day. Attach the source window and
   any qualifier that changes who or what was counted.
4. Is it current activity, an explicit last event, the nearest source-stated
   change comparator, or the most recent measurement when no current one exists?
   If none applies, it is outside the primary finding score.
5. Does an existing finding already measure the same population, unit and window?
   Add corroborating evidence to that finding. Keep a different subtype,
   counted unit or measured window separate. The approved diary-total rule above
   permits addition of disjoint, same-unit components for one measured window;
   do not add overlapping subtype progressions or invent duration, subtype or
   seizure status to make two statements agree.

Examples that the guide and scorer must distinguish:

| Source claim | Primary finding | Unscored context or forbidden inference |
| --- | --- | --- |
| “Now one focal impaired-awareness seizure per month; before treatment, four per week.” | Current monthly rate and one explicit prior comparator. | Earlier isolated diary counts are not additional primary findings. |
| “Three tonic-clonic seizure nights per week.” | Rate of three **affected nights** per week for the named subtype. | Do not assert three individual seizures per week. |
| “Two cluster days this month, usually six seizures each within 24 hours.” | One cluster-day claim with count two, window this month and stated size six. | The within-cluster 24-hour span is evidence, not the observation window or another finding. |
| “No convulsions since February; auras still weekly.” | Convulsion absence and separate current aura rate. | Do not call the patient globally seizure-free. |
| “Occasional head-fog,” with no clinician seizure link. | None. | Preserve the symptom only as context. |

The compact response shape is owned by
[schema decisions](one_shot_schema_decisions.md#candidate-compact-claim-record-2026-09-23).
For the first candidate, preserve the existing approved defaults unless Conor
changes them explicitly: score an explicitly reported longest seizure-free gap
of at least two weeks separately; retain a broad absence summary only when its
scope or interval adds a distinct claim; retain an explicitly stated last event
as a separate finding; and read bare daily cadence using the v0.7 one-per-day
default. The representative review should test whether these four defaults are
reproducible and whether “daily” genuinely describes an individual-event rate.
Any departure needs a named decision and a new reference version. This section
does not itself authorise reference conversion or a model call.

### Compact candidate v0.2 adjudication rules (24 September 2026)

The five dev750 review batches preserved all 1,524 original findings but left
116 source rows flagged for adjudication. A separate review of their reasons and
the 18 null primary claims found that phase and seizure linkage caused more
uncertainty than the record shape. These rules define a **new development
candidate**, not a correction to v0.8.5 or an accepted new reference.

- Apply the seizure-link test to each measured event population. A source-named
  seizure phenotype or an unambiguous reference to it qualifies; a diagnosis,
  diary heading, symptom or treatment discussion alone does not link every
  nearby event to seizures. Preserve an explicitly possible seizure as uncertain.
- Read `ongoing`, `superseded` and `past_or_unclear` from the note's clinical
  sequence. Keep literal dates and windows. Do not repair contradictory dates or
  make an old one-year recency flag determine phase.
- Keep event population, counted unit, measurement kind, restriction and window
  separate. Select each eligible current measurement once, plus an explicit last
  event and at most the nearest source-linked measured comparator for that
  population. Corroborating summaries and unlinked diary history are context.
- Use `seizure_free` only for explicit zero activity over an anchored interval
  and its stated subtype and reporting scope. “Largely event-free” and absence
  of documentation while frequency is uncertain do not assert zero. The
  existing two-week, distinct absence, last-event and bare-daily defaults above
  still apply.
- A prior comparison with an irreducibly unclear counted unit stays unscored
  context with its exact wording. A “most weeks/months” occupancy statement
  without an accepted event quantity, cluster measurement or standalone level
  is also context. Do not add an unknown-unit escape value or guess an event
  count. Explicit seizures **every night** count affected `seizure_night`s,
  one per day-cycle, when no per-night event count is given; “most nights” does
  not become exact nightly cadence.
- An observed count of explicitly named status-epilepticus episodes uses
  `counted_unit: status_episode`. It is never a count of individual seizures,
  attendances or rescue doses. An explicitly stated **median inter-seizure
  interval** uses `measurement.kind: median_interval`, its source duration and
  `counted_unit: not_applicable`; do not turn the median into a regular rate.

Unresolved central ambiguity remains a separately reported row partition with
source ID and reason. A row with an essential disputed primary measurement or
contradictory current state must not be marked complete, treated as an empty
inventory, or silently removed from a full-inventory reference. In particular,
“bimonthly” alone does not decide between twice monthly and every two months.
Adjudicate the source; keep it unresolved if the source does not settle it.

### Owner-reviewed compact candidate v0.3 (24 September 2026)

Conor reviewed the open dev750 examples and approved a source-literal v0.3
candidate. These decisions supersede the v0.2 handling **for this new development
candidate only**. They do not change the frozen v0.8.5 reference or any saved
score. The v0.2 record schema is reused; no new field or value is needed.

**One-sentence rule:** Record each distinct, source-stated current, last-event,
nearest prior or fallback seizure measurement with its literal event population,
counted unit, window and uncertainty; keep contradictory assertions separately,
but treat a less precise restatement of the same measurement as context.

- Do not make one source assertion override another merely to reconcile a
  contradictory clinical history. A current subtype rate and “no seizures
  recorded since the last appointment” can both be primary. The latter means
  absence of **recorded** events within that reporting scope, not proof of
  global clinical freedom. Preserve both source windows and any conflict in the
  evidence; do not invent a transition date. Likewise, retain distinct dated
  events and absence intervals without repairing contradictory dates.
- Use the more precise statement once when another sentence describes the
  **same** event population and period less precisely. In source 2678, “every
  night” supplies the primary affected-night cadence; “most nights” is context.
  In source 15497, the air-travel episode describes the already identified most
  recent flight cluster; it is not a second last event.
- An explicit clinician heading such as `Present Seizure Frequency` can link
  its immediately listed events to seizure activity (1706). A clinical account
  under evaluation can support a **possible** seizure finding when its
  phenomenology and management tie the measured events to that concern; retain
  `uncertain` status (1707, 10873). An anchored seizure-diary absence can
  describe possible events or auras with its app-reporting restriction (8577).
  A diagnosis or diary heading alone still does not convert every nearby
  symptom or fall into a seizure (14282).
- For this candidate, `bimonthly` means once every two months in 959 and 960.
  Keep two explicitly counted named populations separate without summing them
  when their overlap is not stated (1597, 1640). Use the event label in the
  counted sentence when a later clinical description uses another term (4496,
  3262). Preserve literal broader labels such as “generalised seizures” beside
  continuing absences or jerks; do not silently relabel them tonic–clonic
  (15168, 15193). A total spanning mixed semiology remains unspecified-scope
  rather than becoming a subtype total (15965, 16097).
- A phrase that measures two named populations can supply two claims with
  different units. In 12484, 12502 and 12506, “these occur roughly once a
  month” applies separately to myoclonic **clusters** and tonic **seizures**.
  A preceding occasional tonic level is not a third scored measurement of the
  same tonic pattern. A three-count of focal epileptic spasms counts individual
  spasms, even if the later semiology says they can cluster (1980).
- Preserve the source's selected window literally. Use “this month” for the
  two-cluster counts in 3242 and 3262 and the affected-day count in 3281,
  despite conflicting adjacent wording or the note date. Do not repair an
  impossible calendar sequence in the source. A diary cluster with no dated
  window stays `past_or_unclear`, not automatically ongoing (13209).
- Keep an explicitly stated maximum seizure-free gap of at least two weeks as
  a distinct past-or-unclear finding with its **literal unspecified event scope**,
  even alongside continuing subtype rates. Do not infer a subtype restriction
  or present the gap as current global freedom. An until-only statement with
  no start/duration (891), an unanchored denial (14187, 15429), or a phrase
  that may fall below two weeks (13149) remains context. A prior “once every
  couple of weeks” with no clear counted unit remains context (15771).

The owner-approved overlay is local-only under
`runs/seizure_finding_annotation_compact_v0_1/dev750/`. Structural completion
of all 750 source rows means the declared policy can represent their selected
claims; it does not establish independent annotator agreement, clinical
validation, model performance or holdout generalization.
The candidate v0.2 schema is
[`rich.v0_2.schema.json`](../../../results/letter-benchmarks/gan/one_shot_frequency_compact_scope_candidate_no_call/rich.v0_2.schema.json).

### Prospective compact scoring clarification from saved R9 (24 September 2026)

The [v2 scored-term source audit](../../../results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r9/dev750/concepts_v02_source_audit/README.md)
compares the unchanged v0.3 reference with saved R9 responses. It proposes
the following operational reading of the existing compact restriction rule;
it does **not** edit the v0.3 reference or make the provisional v2 score the
paper endpoint.

- A condition is scored when the measurement applies only to that event
  population or exposure: an absence of jerks **on waking**, a rate measured
  **on workdays**, or a daily rate occurring only for **brief periods**. Do not
  promote these to unrestricted absence or continuous rate (14187, 4116,
  16574).
- A trigger or circumstance of a counted single event remains in exact
  evidence, not `restriction`: the last seizure after a night shift (6029) and
  two convulsions at work (3846). The work setting *does* limit the separate
  two-per-day rate in 3846, so apply the rule to each claim rather than each
  letter.
- A condition already in the event label does not require an identical
  restriction string. `Events during sleep` plus `during sleep` is one
  sleep-only population (9103); `electrographic events` plus `on EEG` is one
  EEG-observed population (9815). Preserve both literal fields and evidence
  in source records while scoring the population once.
- An incidental descriptor such as `brief` is optional. Broad phenomenology
  can still distinguish populations: jerks and staring spells are separate in
  2513; convulsion and convulsive event can share a code. Do not infer a
  formal seizure subtype from either description alone.

The source audit leaves conditional qualitative findings, mixed broad event
sets, and contradictory observation scopes open. Those require explicit
adjudication before a frozen successor reference or another dev750 model run.

The [subsequent v3 policy audit](../../../results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r9/dev750/concepts_v03_policy_candidate/README.md)
narrows those questions for development scoring. Score a qualitative condition
when the source explicitly limits the level to it: `uncommon when meals are
regular` (6321), `convulsions if the cluster is prolonged` (10996), and an
explicitly perimenstrual-only pattern (3468). Keep non-exclusive associations
such as `occasional clustering on workdays when breakfast is missed` (2023)
in evidence without making the level conditional. If a combined event set has
an unclassified component, retain its literal combined scope and label rather
than infer a subtype or collapse it to one named member (17146, 17189).

The v0.3 owner record already retains the 5092 absence as **observed clinical**
seizures and retains the 6077 eight-month `day-to-day` absence only
provisionally. The latter's relation to a recent flight breakthrough is not
settled by the source; keep its `past_or_unclear` phase and restricted literal
wording. Do not report it as current global freedom. The v3 scorer makes these
distinctions without changing the source reference or resolving the remaining
source contradiction.

### Diary-total prompt alignment (24 September 2026)

The owner-approved v0.8.3 rule permits a total from disjoint diary components
with the same counted unit and measured interval. A review of eight selected
v0.3 references found such totals while the frozen R9 prompt prohibited all
arithmetic. In 15992, for example, seven awake events is four in December plus
three in January; the note does not state seven. R9 returned the two source
counts, so its missing total is a prompt/reference policy mismatch, not a
standalone model error. The same pattern occurs in 4402, 4410, 5995, 6065,
15965, 15982 and 16041. The
[source checks](../../../results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r9/dev750/concepts_v03_policy_candidate/README.md#diary-arithmetic-correction)
are selected examples, not an estimate of prevalence. A successor prompt
should state the bounded diary-sum rule before any new development run.

### Source 2023 mixed-diary question after R11 (24 September 2026)

The source lists four absence seizures and one myoclonic event this month.
The v0.3 reference retains the two named counts but no overall five-event
count. The v0.8.3 mixed-diary rule appears to permit one overall count when
these disjoint components can be added. Review this as a possible reference
omission before changing the frozen v0.3 reference or scoring a successor.
R11's single `combined absence and myoclonic` count of five still loses the
two distinct named findings; it is not an exact match to the current
reference. The [full R11 source audit](../../../results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r11/dev750/README.md)
preserves the owner reasons and both model outputs.
