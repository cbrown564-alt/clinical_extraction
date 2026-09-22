# Why the R7 inventory score is low

Development analysis of the saved R7 rich mixed view against the completed v0.7
dev750 reference. The primary score is unchanged: precision 742/2,197 on usable
inventories, recall 742/2,097 of all reference findings, exact inventory 75/750.
This note explains that score. It is not a replacement matcher, not a corrected
result, and not clinical validation.

The counts below come from
`.venv/bin/python scripts/benchmarks/analyze_r7_finding_errors.py`.
Letters are synthetic.

## The score is strict, and one mistake is counted twice

A match requires the event label, seizure status, timing, measurement type,
quantity, unit, cluster parts, period or date, and an exact overlapping
quotation. One field fails the whole finding. No partial credit.

Of 2,097 reference findings:

| Class | Findings | What it is |
| --- | ---: | --- |
| Whole match | 742 | Every required field agrees. |
| Same quotation, different record | 900 | A prediction quotes the same passage and still fails at least one field. |
| No shared quotation | 196 | No prediction quote overlaps the reference quote. One of these would overlap after whitespace normalisation. |
| Reference finding R7 cannot represent | 125 | Qualitative duration or a `quarter` unit, on a usable inventory. None matched. One further such finding sits in an unusable inventory. |
| Unusable inventory | 134 | The 36 schema-invalid records and five rows with no response. |

The 2,197 predictions split as 742 matches, 939 that share a quotation with an
unmatched reference finding, 43 duplicates of an already matched finding, and
473 that share no quotation with the reference.

The headline 1,355 false negatives and 1,455 false positives are therefore not
2,810 independent clinical mistakes. About 900 reference findings and 939
predictions are the two sides of the same passage-level disagreement.

## Layer 1. The reference was rewritten after R7 was frozen

R7 was run on 14–16 September under its own finding instructions. Guide v0.7
was approved on 16 September and then tightened through 22 September. R8 was
later written so that the finding schema and its instructions match v0.7. The
scored outputs are R7. The answer task was deliberately left unchanged, which
is why answer agreement can stay near 650/750 while the inventory fails.

The conflicts are explicit.

| Decision | R7 instruction the model saw | v0.7 reference used for scoring |
| --- | --- | --- |
| Qualitative frequency | Copy the source expression, such as "less frequent". | Map it onto eight values: rare, occasional, frequent, increased, decreased, unchanged, variable, unknown. |
| Seizure status | `stated`, `uncertain`, `non_seizure`, or `unspecified`. Preserve uncertainty. | `stated` unless the source questions whether the events are seizures. There is no `unspecified`. |
| Period | Omit an observation window that is not specified. A rate's `per` is not a period. | Copy the source window whenever one is stated. |
| Event label | The source event name, without inferring a diagnosis. | The words of the quantified statement. A heading or an earlier sentence does not rename it. |
| Bare denial | Absence may be recorded without requiring a duration. | A denial with no duration and no anchor is not a finding. |
| Bare cluster | An unquantified cluster may omit every number. | A cluster with no cadence, count, or size is not a finding. |
| Vague duration and quarter | Not in the R7 schema. | 121 qualitative durations and five `quarter` units are legal reference findings. |

The distributions follow those instructions.

- Reference seizure status is stated 2,010, uncertain 71, non-seizure 16.
  Predictions are stated 1,790, uncertain 371, non-seizure 20, unspecified 16.
- Reference qualitative values are only the eight closed-list words, led by
  occasional 199 and increased 117. Of 412 predicted qualitative frequencies,
  280 are outside that list: intermittent, infrequent, recurrent, occasionally,
  daily, "rarer", "some days", "most shifts".
- Of 473 predictions that share no quotation with any reference finding, 150
  are seizure-freedom with neither duration nor anchor ("There have been no
  generalised tonic–clonic seizures reported") and 111 are clusters with no
  rate, count, or size. Those 261 extras are in scope for the R7 prompt and
  out of scope for v0.7.

## Layer 2. Same quotation, one blocking field

Five hundred and eighty of the 900 same-quotation misses differ in exactly one
attribute. The measurement itself is often already the reference measurement.

**Period omitted, 103 of the 120 period-only misses.** Source 156. Both sides
say one seizure per six days. The reference also stores the window "over the
past two months". R7 left the period empty, which the R7 instructions permit
when the recurrence is already in `per`. The matcher treats a missing period
as a different finding. Sources 103 and 182 are the same pattern: "every 1 or
2 weeks" and "every 2 days", with the reference adding "prior to this period"
and "since the last review".

**Qualitative wording, 90 of the 142 value-only misses.** Source 79. The
quotation is identical: "rarer generalised tonic–clonic seizures typically
following multiple long-haul flights". The model stored `rarer`. The reference
stored `rare`. Source 694 stores "some days" against `occasional`. Source 743
stores "most shifts" against `frequent`. The guide's short synonym list
(intermittent, infrequent, sporadic, most days, near-daily, more frequent,
less frequent) would repair 36 of these 90 and leave 54, including "rarer" and
"most shifts", which are the same kind of mapping but not in that short list.
The other 52 value-only misses are numeric disagreements on the same passage:
29 seizure-free durations, 12 cluster sizes, 10 counts, and one rate.

**Event label, 101.** Source 725. The quotation says "events occur daily".
The reference event is "events". The model named "focal impaired-awareness
episodes", taken from elsewhere in the letter. The guide forbids that rename.
Source 3827 is "clusters" against "seizures" for the same "clusters of 3".

**Seizure status, 97, and a wider uncertain bias.** Source 704. Both sides
quote "Frequency is now reported as twice a month" and both store two per
month. The model marks the nocturnal episodes `uncertain` because awareness
was discussed. The reference marks them `stated`. Across all predictions the
model uses `uncertain` 371 times against 71 in the reference. On
same-quotation pairs, 186 are predicted uncertain against a stated reference.
R7 told the model to preserve uncertainty. v0.7 reserves `uncertain` for an
explicit question of whether the events are seizures.

**Measurement type, 73.** These are the cases where the family itself
changes. Source 466: "No generalised tonic–clonic seizures documented in the
past six months" is a six-month seizure-free interval in the reference and a
qualitative sentence in the prediction. R7 already said absence with a
duration is `seizure_free`, so this one is a model miss against its own
instructions, not only a v0.7 change. Source 278: "multiple times in past
week" is a count in the reference and a weekly rate in the prediction.

**Timing, 47.** Source 816: "only four brief seizures recorded in 2017 so
far" is current in the reference and historical in the prediction. Source
2459 is the reverse: "this month so far she has 2 seizures" is historical in
the reference because the letter frames it as before a deterioration, and
current in the prediction. Timing is a real but smaller layer. Predicted
`unclear` and `future` are three findings in total.

The other 320 same-quotation misses combine two or more of these fields.
When a period difference occurs at all, the prediction omitted it 251 times,
the reference omitted it 52 times, and both stated a disagreeing window 22
times.

## Layer 3. What remains after the cross-version effect

Not everything is an instruction mismatch.

- 196 reference findings have no overlapping prediction quote. Quote
  normalisation would recover one. The rest were not extracted, or were
  extracted from a different sentence. Source 128's reference splits a long
  history into a rare progression and a separate historical decrease. The
  model did not quote those spans.
- 52 value-only misses are different numbers or durations on the same
  passage, not a closed-list synonym.
- 43 predictions repeat a finding that already matched.
- 27 of the no-overlap seizure-free extras do have a duration or anchor, so
  they are not the bare denials v0.7 dropped. Nine of the no-overlap cluster
  extras are quantified. Those still need a source reading before they are
  called model inventions.
- The 41 unusable letters remain a contract failure. They create 134 false
  negatives. They are not the bulk of the 1,355.

## What not to do with this

Do not read 0.35 as the rate at which the model invented a frequency. On most
missed reference findings that the model could represent, it quoted the same
passage. Do not edit the frozen matcher so that a missing period, a synonym,
or `uncertain` versus `stated` starts to count as a match. That would define
correctness after seeing the misses. Do not tune an R7 prompt against this
list. The prompt that should be compared with this reference is the one
already written to match it.

## Options

1. **Report the two endpoints separately.** Answer agreement, 650/750 Purist,
   answers the paper's current question. Inventory agreement, 742/2,097,
   answers a stricter and later question under instructions the model was not
   given. The decomposition above is the limitation statement. This requires
   no new run.

2. **Run R8 once on dev750 and score it with this same matcher.** R8 changes
   the finding schema and the population instructions to the v0.7 rules and
   leaves the answer task alone. That is the comparison that can separate
   instruction mismatch from extraction failure. It is a new paid run and is
   not authorised by this analysis. It should not be redesigned from the R7
   miss list first. The classes above are already the differences R8 was
   written to close: closed qualitative list, stated-by-default status,
   anchored seizure freedom, no bare clusters, copied periods, qualitative
   durations, and quarter.

3. **Keep any sensitivity diagnostic.** A count such as "36 value-only
   qualitative misses are the guide's published synonyms" can be published as
   a sensitivity. It must not replace 742/2,097.

4. **Do not extend annotation to medications, diagnoses, and investigations
   on this inventory.** The seizure record is not yet a same-instruction
   measurement. Adding families would apply a second new convention before
   the first one has been run.
