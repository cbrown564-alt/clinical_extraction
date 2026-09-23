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
