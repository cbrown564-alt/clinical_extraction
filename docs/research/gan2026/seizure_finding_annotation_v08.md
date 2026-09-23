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
whether a cluster's within-cluster span belongs in scored `period` is unresolved.

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
saved-R8 result. The question of scoring the span *within* a cluster remains
open; it is different from the observation window for a cluster count.
