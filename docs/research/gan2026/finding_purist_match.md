# Finding Purist match

Owner of the Finding Purist inventory score. The frozen exact matcher remains
`finding_matching_v07`. The scorer is `finding_purist_v1`. It rescores saved
outputs only and does not authorise a model run. The dev750 counts are in the
[execution record](one_shot_execution_record.md#finding-purist-dev750-rescore-2026-09-22).
Reproduce with `.venv/bin/python scripts/benchmarks/score_finding_purist.py`.

Reproduce the diagnostic with
`.venv/bin/python scripts/benchmarks/analyze_r8_purist_finding_bands.py`.
The machine summary is
[purist_band_diagnostic.json](../../../results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r8/dev750_rich_only/purist_band_diagnostic.json).

## Why the exact inventory score is the wrong strictness

The answer endpoint does not ask whether two label strings are identical. It
projects each label to a monthly frequency and asks whether both fall in the
same Purist band. "1 per 6 day" and another rate in the same band can agree.
Seizure-free labels of any duration agree, because every seizure-free label
projects to zero. Status, observation-window wording, and quotation length are
not part of the answer.

The finding score does the opposite. A match requires the event label, seizure
status, timing, measurement type, quantity, unit, cluster parts, period, and
an overlapping quotation. One differing field fails the whole finding. On the
R8 dev750 run that score is precision 1,032/1,792 and recall 1,032/2,097.
Exact inventories are 185/750. The answer on the same outputs is 638/750
Purist. Those numbers answer different questions. The inventory number is not
a finer version of the answer number.

## What the R8 exact misses actually are

Of 2,097 reference findings, 1,032 match exactly, 115 sit in an unusable
inventory, and 950 are exact misses on a usable inventory. The 950 split by
the closest prediction that quotes the same passage:

| Nearest difference | Findings | Meaning for a Purist-like score |
| --- | ---: | --- |
| Same event, timing, and measurement | 223 | The frequency record already agrees. 186 differ only by the period string, usually because the prediction omitted a window the reference copied. 25 differ only by seizure status. |
| Same event and timing, same Purist band, measurement not exact | 52 | 37 of these are seizure-free findings. Answer Purist would call them equal because every seizure-free label is "no current seizures". The other 15 are rates or counts inside one band. |
| Same event and timing, different Purist band | 8 | A real frequency disagreement. These should stay misses. |
| Event label | 169 | The quoted passage is about a differently named event. |
| Timing | 68 | Current versus historical on the same passage. |
| Not a Purist rate | 202 | Qualitative wording, a count whose window is prose, a cluster or last-seizure that does not render to a Gan label. |
| No shared quotation | 228 | Nothing the model quoted overlaps the reference quote. |

A sketch that keeps every exact match, and also matches an unused pair when
the evidence overlaps, the event labels are equivalent, the timing agrees, and
the projected Purist band agrees, moves the score from 1,032 to 1,202 true
positives. Recall becomes 1,202/2,097 (0.573) and precision 1,202/1,792
(0.671). Of the 170 added matches, 106 exist only because every seizure-free
finding was collapsed to one band. That sketch is greedy and is not a
proposed result.

## Examples

Source 156. Both sides are one per six days, Purist band
`seizure_freq_more1week_less1day`. The prediction quotes "Patient reports
seizures every 6 days". The reference quote continues into the episode
description, and the reference also stores the window "over the past two
months". The exact matcher fails. The frequency band does not.

Source 103. "every 1 or 2 weeks" is the same rendered rate on both sides.
The reference period is "prior to this period" and the prediction has no
period. Same band, exact miss.

Source 5873, from the same-evidence value check. The prediction is 3 per 6
weeks and the reference is 2 per 6 weeks. Both fall in
`seizure_freq_more1mon_less1week`. A band match would call this a true
positive. That is the resolution Purist already gives up for answers, and it
should be an explicit choice for findings rather than an accident.

Source 190. Both quotations say there have been no generalised tonic–clonic
seizures since the one in May 2025. Answer Purist scores both as no current
seizures and cannot tell a six-month absence from a two-week absence. The
finding reference exists so that duration remains visible.

Source 79. The same quotation, "rarer generalised tonic–clonic seizures…",
is `decreased` in the prediction and `rare` in the reference. No monthly band
adjudicates that. Qualitative findings need their own rule.

## Proposed score

Name it separately from the exact matcher. Do not edit
`finding_matching_v07`. Rescore saved outputs only. Do not tune a prompt
against the new score, and do not spend a model call to create it.

A predicted finding matches a reference finding when:

1. The quotations overlap in the source.
2. The event labels are equivalent under the existing label key. A weekly
   rate for a different event is not the same finding. The answer score never
   faces this choice because it keeps one label per letter.
3. Timing agrees. A historical rate is not the current rate.
4. The frequency agrees on the native Purist bands when both findings render
   to a Gan label: a rate, a count with a numeric window, or a cluster label
   the existing label parser accepts. Bounds and ranges use the same midpoint
   the answer scorer uses. This forgives "1 per 6 day" versus another rate in
   that band, and it forgives 3 per 6 weeks versus 2 per 6 weeks.
5. Qualitative findings agree after the v0.7 closed-list map, not after a
   monthly projection. `intermittent` may match `occasional`. `decreased`
   does not match `rare`.
6. Seizure-free findings do **not** inherit the answer collapse to zero.
   Duration or the `since` anchor still has to agree, with only the spelling
   tolerance already used for time points. Report the collapsed version, if
   at all, as a named companion, the way Pragmatic accompanies Purist.
7. Last-seizure findings agree when the existing time comparison agrees.
8. Seizure status, condition, approximation, inclusivity, and the period
   string are not compared when the measurement already determines the band.
   A missing "over the past two months" does not fail a rate of one per six
   days.

Counts whose only window is prose ("since the last review", "this month so
far") stay outside the band until a window rule is frozen. Do not invent a
numeric month for them in the first implementation. They are 233 of the
unmatched reference findings in the projection diagnostic, and they are part
of this phase's design work rather than a hidden conversion.

Unusable inventories stay unusable. An illegal record still contributes every
reference finding as a false negative and does not contribute false positives.
Empty inventories stay empty. One-to-one maximum matching stays. Evidence
overlap stays. The exact score continues to be reported beside the band score.

## What this phase produced

The rule is frozen in `tests/test_finding_purist.py`: a same-band rate, a
different-band rate, a period omission, a status difference, a qualitative
synonym, a qualitative contradiction, two seizure-free durations, an event
rename, and a timing swap. Prose-only count windows stay unmatched. The scorer
is `finding_purist.py`, beside the exact matcher. Saved R7 and R8 dev750
inventories were rescored with no model call. Both scores are in the execution
record. Finding Purist is the inventory endpoint for later writing. The exact
score remains the description of field-level agreement. The common R8 misses
are described in the
[execution record](one_shot_execution_record.md#r8-finding-purist-misses-2026-09-22).

The seizure-free collapsed companion is reported separately. It is not the
inventory endpoint. This phase does not extend annotation to medications,
diagnoses, or investigations. It does not authorise an R8 rerun. It does not
change the answer endpoint.
