# Gan gold phrase variants: why the rules do not belong in the prompt

Date: 2026-08-13  
Status: paper source; development gold only; writing-test passed 2026-08-14  
Parent: [why the proposed method is a model plus recorded rules](why_hybrid_architecture_2026-08-09.md)  
Companion catalog: [every development gold label and its official source phrases](gan_gold_phrase_variant_catalog_2026-08-13.md)  
Workbook: [row spreadsheet](../artifacts/gan_gold_phrase_variants_2026-08-13.xlsx)  
Artifact: [`experiments/gan2026_gold_phrase_variant_inventory_20260813.json`](../../../experiments/gan2026_gold_phrase_variant_inventory_20260813.json)  
Regenerator: `python scripts/build_gan2026_gold_phrase_variant_inventory.py`

## The short answer

Gan gold is a small output dialect and a large input dialect.

On the 1,050 development rows (`train` 300 + `validation` 750) there are **45
render templates** and **333 distinct gold labels**. Those labels are licensed
by **852 distinct official source phrases**. The gold string itself appears
inside the official reference on **11 of 1,050 rows**. Almost every scored
answer is a transformation, not a copy.

In principle a prompt could list every normalisation, selection, and rendering
rule those phrases require. That is the wrong place to put them.

1. **Cost.** The list is long. Most of it is irrelevant to any one letter.
   Carrying it on every call spends tokens and latency on unused cases.
2. **Interference.** A simple “once a week” letter then sits next to cluster
   grammar, diary aggregation, date arithmetic, and abstention policy. The
   model is invited to do complicated work on an ordinary rate.
3. **Opacity.** When the mapping lives in generated prose, a later change to
   a duration convention or a cluster render is not a named, replayable
   stage. It is a wording change in a long prompt.

The hybrid keeps the two jobs apart. The model reads flexible clinical
language and selects evidence. Deterministic stages own the output dialect,
the selection policies, and the record of what changed.

This draft is Gan only. The ExECT sibling is
[exect_gold_phrase_variants_2026-08-13.md](exect_gold_phrase_variants_2026-08-13.md).
It is not a performance claim.

## What “exhaustive” means here

| Item | Count | What it is |
| --- | ---: | --- |
| Development rows | 1,050 | `train` + `validation` only |
| Distinct gold labels | 333 | The scored strings, including 192 that appear once |
| Distinct render templates | 45 | Digits replaced by `N`; cluster gold further collapsed by unit and per-cluster burden |
| Distinct official source phrases | 852 | Dataset `gold_reference` field, case-preserved |
| Gold string inside the official reference | 11 | Near-copy is rare |
| Official reference verbatim in the letter | 729 | The usual case |
| Official reference only after case folding | 44 | Capitalisation differs |
| Official reference not in the letter | 277 | Compressed token, paraphrase, theme tag, or generation prompt |
| Letter span recovered | 1,011 | Official quote, or a scored sentence from the letter |
| Admin / no frequency letter | 38 | Generation prompts; no frequency span to recover |
| Residual `other_paraphrase` | 63 (6.0%) | Below the 10% review target |

The [existing gold taxonomy](../gan2026/gold_task_taxonomy_2026-08-06.md)
partitions labels by semantic kind and shape (`ordinary_point_rate`,
`cluster_burden`, `seizure_free`, …). This inventory answers a different
question: **how many different ways does the source say something that gold
then renders as one string?**

Locked `test` rows were not loaded. The official reference is still the
dataset field. A second pass now also recovers a letter span: if the
official reference occurs in the letter, that span is used; otherwise the
pass scores frequency-bearing sentences and records the method
(`official_reference_in_letter`, `scored_frequency_sentence`,
`weak_frequency_sentence`, `admin_or_no_frequency_letter`). Source
constructions are assigned from the recovered span when one exists.
Some recoveries remain weak; they are labelled rather than silently
trusted. The [workbook](../artifacts/gan_gold_phrase_variants_2026-08-13.xlsx)
has both the official reference and the recovered span on every row.

## The output dialect is small

Gold is not free text. It is a closed render language.

| Render template | Development rows | Distinct labels |
| --- | ---: | ---: |
| `N per N month` | 179 | 86 |
| `unknown` | 125 | 1 |
| `seizure free for multiple month` | 69 | 1 |
| `N per month` | 67 | 13 |
| `N per day` | 66 | 6 |
| `N per week` | 58 | 12 |
| `seizure free for N month` | 52 | 13 |
| `no seizure frequency reference` | 38 | 1 |
| `multiple per week` | 30 | 1 |
| `N to N per N month` | 27 | 20 |
| Remaining 35 templates | 339 | 179 |

The long tail is real — 192 labels occur once — but it is still a dialect:
point rates, ranges, two-part clusters, free-interval durations, and a few
sentinels. A prompt could print the 45 templates. That would not tell the
model how to get there from the letter.

Cluster gold is collapsed more than ordinary rates. Digit counts, 1-vs-N
periods, and period ranges are dropped, leaving **nine** templates:
`cluster per {day|week|month}, {N|range|multiple} per cluster`. That
turns 68 distinct cluster labels / 27 digit-stripped shapes into a
readable family without pretending every cluster string is unique.

## The input dialect is not small

One gold string is licensed by many source constructions. The clearest
ordinary-rate example is `1 per day` (46 rows, **42 distinct official
references**):

| Official source phrase | What has to happen |
| --- | --- |
| `once per day` | Near-copy into Gan unit grammar |
| `every day` / `daily` | Cadence word → `1 per day` |
| `seizures every night` / `once per night` | Night is treated as the day unit |
| `one seizures yesterday` | A deictic count becomes a daily rate |
| `sz X1/d`, `sz xone/d`, `sz *one/d`, `TC *one/d` | Chart shorthand, including word numbers and decorative separators |
| `drop attack daily`, `myoclonic jerk daily` | Type prefix is dropped; cadence remains |
| `Since the head injury, she has experienced clusters of absence almost daily` | Cluster language is present; gold still wants a daily point rate |
| `Her parents report … Brief myoclonic jerks persist daily on awakening` | A competing monthly convulsion is ignored; the daily jerk is selected |

`1 per month` (29 rows, 23 phrases) and `1 per week` (15 rows, 14 phrases)
repeat the pattern. `unknown` has **96** official phrases. `seizure free for
multiple month` has **40**, almost none of which contain the gold string:

`Event-free`, `No recurrence`, `Complete control of seizures`, `Durable
seizure control`, `Interval history negative for seizures`, `Seizure burden
0% on device metrics`, `non-epileptic seizures only`.

The [catalog](gan_gold_phrase_variant_catalog_2026-08-13.md) lists every
development label and every distinct official phrase under it. The
[workbook](../artifacts/gan_gold_phrase_variants_2026-08-13.xlsx) is the
row-level view, including the recovered letter span.

## A cluster family

Cluster gold is the place where input variety and output dialect pull
hardest. On development there are **89 cluster-gold rows** and **68
distinct cluster labels**, grouped into **nine** templates. Most say
“cluster” in the letter. Some do not.

| How the letter says it | Gold |
| --- | --- |
| Quiet interval plus an explicit cluster: `She may remain seizure-free for up to 4 month, but then will experience clusters of 5 seizures in a single day` | `1 cluster per 4 month, 5 per cluster` |
| Cluster meaning without the word: `seizure-free for five consecutive days, followed by a day with multiple events, typically 2 tonic seizures` | `1 cluster per 5 day, 2 per cluster` |
| Quiet gap plus a same-day range: `go nearly two week without seizures, but when they recur he tends to have several in one day, often between three and six` | `1 cluster per 2 week, 3 to 6 per cluster` |

A prompt that listed “if the letter says cluster, emit `N cluster per T, M
per cluster`” would miss the second and third rows. A prompt that also
listed every paraphrase of “batch”, “day of multiple events”, and “several
in one day after a gap” would be the list this inventory is trying not to
put in the model call.

## How similar things are said

The constructions below are mutually exclusive. They are assigned from the
**recovered letter span** when one exists, otherwise from the official
reference, in a fixed order, by
`scripts/build_gan2026_gold_phrase_variant_inventory.py`. This is a review
taxonomy, not a change to gold or to the scorer. **63 rows (6.0%)** remain
`other_paraphrase`.

| Source construction | n | What the source is doing | Example → gold |
| --- | ---: | --- | --- |
| `cluster_structure` | 137 | Mentions clusters | `clusters of 5 seizures in a single day` → `1 cluster per 4 month, 5 per cluster` |
| `range_or_bound` | 117 | Range or upper bound | `8 or 9 simple partial seizures in three weeks` → `8 to 9 per 3 week` |
| `non_rate_unknown_statement` | 80 | Clinical statement, not a countable current rate | `Better over the past 6 months` → `unknown` |
| `adjective_cadence` | 78 | Cadence adjective in a longer phrase | `yearly seizures` → `1 per year` |
| `month_by_month_count` | 72 | Separate months, each with a count | `In Oct … 2 … In Nov … 5` → `8 per 2 month` |
| `seizure_free_duration_or_interval` | 61 | Quiet interval without a calendar date | `No seizures since last visit` → `seizure free for multiple month` |
| `other_paraphrase` | 63 | Residual | see workbook |
| `qualitative_control` | 60 | Control or remission language, no count | `Complete control of seizures` → `seizure free for multiple month` |
| `count_in_named_window` | 48 | N events in a named window | `about six to eight seizures in the last three months` → `6 to 8 per 3 month` |
| `admin_or_generation_prompt` | 38 | Generation instruction, not a frequency statement | `Create a reasonable NHS letter…` → `no seizure frequency reference` |
| `count_per_period` | 35 | Explicit N per unit | `once per day` → `1 per day` |
| `vague_multiple` | 35 | Several / frequent / many | `several petit mal in the past week` → `multiple per week` |
| `summed_type_counts_in_window` | 33 | Add typed counts in one window | `one absence and four petit mal in last month` → `5 per month` |
| `every_n_interval` | 32 | Every N units | `every 2 days` → `1 per 2 day` |
| `clinical_shorthand` | 31 | Chart notation | `sz X1/d` → `1 per day` |
| `cluster_paraphrase` | 20 | Cluster meaning without the word cluster | `a day with multiple events, typically 2 tonic seizures` → `1 cluster per 5 day, 2 per cluster` |
| `dated_event_sequence` | 19 | First event on one date, later event on another | first seizure January, second June → `2 per 5 month` |
| `last_event_then_quiet` | 13 | Last-event date plus stability since | last episode 09 October, stable since → `1 per 2 month` |
| `seizure_free_since_date` | 11 | Free since a calendar date | `Seizure-free since 27 March 2024` → `seizure free for 6 month` |
| `cadence_token` | 9 | A single cadence word as the official reference | `weekly` → `1 per week` |
| `diary_or_calendar_log` | 9 | `Jan x1, Feb x0, …` | `7 per 7 month` |
| `soft_or_unconfirmed` | 8 | Suspected or direction-unclear | `frequency changed unclear direction` → `unknown` |
| `last_major_plus_since` | 7 | Last major seizure plus residual events | last TC in Apr/2022, 3 jerks since → `4 per 13 month` |
| `interseizure_interval` | 6 | Typical gap between events | `Median inter-seizure interval ≈ five months` → `1 per 5 month` |
| `electrographic_rate` | 6 | EEG hourly burden | `Electrographic seizures frequent on EEG (~4/h)` → `multiple per day` |
| `situational_or_triggered` | 5 | Events only under a trigger | `seizures happen after lack of sleep` → `unknown` |
| `quiet_then_breakthrough` | 5 | Free interval ended by a later event | seizure-free for 4 months until … → `1 per 4 month` |
| `post_change_burst` | 5 | Burst at a medication change, then quiet | withdrew, had 4 seizures, stable since → `4 per 3 month` |
| `slash_or_fraction_rate` | 4 | Compact `N/D` rate | `seizure frequency 6/7` → `6 per week` |
| `non_rate_theme_tag` | 2 | Official tag is not the rate; letter span still not classifiable | — |
| `last_event_date` | 1 | Last-event date as a free-interval gold | — |

The same phrase family is not one rule. `monthly` as a cadence token can
gold as `1 per month`, or as `1 per 4 to 5 week` when the letter says
“roughly every four to five weeks.” `Last seizure on DATE` sometimes golds
as a free-interval duration and sometimes as `unknown`. Those are selection
conventions, not parse failures.

## What must happen between phrase and label

The transform column is the job a prompt-only system would have to perform
in language, on every letter.

| Transform | n | Job |
| --- | ---: | --- |
| `cluster_two_part_render` | 155 | Prose or paraphrase cluster → two-part grammar |
| `abstain_to_unknown` | 112 | Withhold a rate |
| `word_number_to_digit` | 85 | `nineteen`, `twice`, `xone` → digits |
| `cadence_expansion` | 84 | `daily` / `nightly` / `yearly` → `1 per unit` |
| `diary_window_aggregation` | 81 | Calendar or month-by-month log → one windowed total |
| `qualitative_to_free_sentinel` | 60 | `complete control` → `seizure free for multiple month` |
| `duration_normalization` | 55 | Quiet-interval wording → Gan free-duration string |
| `windowed_count_to_rate` | 48 | `N in the last T` → `N per T` |
| `vague_to_multiple_sentinel` | 43 | `several` or EEG hourly → `multiple per unit` |
| `interval_inversion` | 38 | `every 2 months` or median gap → `1 per 2 month` |
| `assert_no_reference` | 38 | Admin or empty letter → sentinel |
| `rate_dialect_normalization` | 34 | `once a week` → Gan `N per unit` |
| `sum_typed_counts` | 33 | Add two typed counts in one window |
| `shorthand_expansion` | 31 | `TC *ten/wk` → `10 per week` |
| `hedge_or_bound_dropped` | 23 | `≤`, `up to`, `roughly` stripped |
| `dated_sequence_to_rate` | 19 | First/second event dates → count over the span |
| `last_event_to_rate` | 13 | Last event plus quiet → `1 per N unit` |
| `date_elapsed_arithmetic` | 12 | `since 27 March 2024` → duration in months |
| `identity_or_near_copy` | 11 | Gold string already in the source |
| `other_semantic_map` | 52 | Residual |

Three of these are not “say it differently.” They are **selection**:

- A letter can state a usual rate, a recent cluster, a dated total, and a
  quiet interval. Only one string is scored.
- `non_rate_theme_tag` rows show the official reference naming a trigger
  (`Only with sleep deprivation`) while gold is a windowed rate found
  elsewhere in the letter (`five focal aware events` over three months).
- Some `unknown` rows contain countable language (`seven seizures so far
  this year`, `last seizure on DATE`) that gold still withholds.

A prompt that enumerated surface forms would still not have enumerated the
winner policy. That policy is already recorded in the
[clinical selection catalog](../shared/clinical_selection_policy_catalog_2026-07-31.md).

## Why this is the hybrid argument

The theoretical alternative is: put the 45 templates, the 22 constructions,
the transforms, the selection policies, and a long list of observed
paraphrases into the prompt, and ask the model to apply them.

That alternative fails in the three ways this inventory makes concrete.

**It is expensive.** 852 observed official phrases on development alone,
192 singleton labels, and a residual of unsystematised narratives. A
complete prompt would keep growing as new paraphrases appear. Most of that
text is idle on any given letter.

**It overloads simple cases.** `once a week` → `1 per week` is a dialect
rewrite. If the same context also contains cluster assembly, diary
summation, elapsed-date arithmetic, “several” → `multiple`, and the
unknown-versus-rate policies, the model is asked to reason about machinery
that this letter does not need. The retained development cases already
include well-formed, grounded answers that still pick the wrong statement.

**It hides the decision.** Evidence reconciliation, monthly-diary
selection, and free-interval rendering are inspectable stages today. If
those mappings live only as prompt paragraphs, a change to “what `monthly`
means” or “when to abstain” is not a named component. The
[rescue-source study](../shared/hybrid_rescue_source_provenance_2026-08-13.md)
found that almost all first Gan rescues re-render a span the model already
chose. That is an argument for keeping rendering in code, not for asking
the model to memorise the dialect.

The hybrid does not make every decision correct. It makes the intended
jobs explicit. Flexible reading stays with the model. The output dialect,
the winner rule, and the record of the change stay deterministic.

## How to use this draft

- Use the construction table when writing the “why hybrid” paragraph.
- Use four worked families: `1 per day`, cluster gold, `unknown`, and
  `seizure free for multiple month`.
- Use the [workbook](../artifacts/gan_gold_phrase_variants_2026-08-13.xlsx)
  to filter by construction, compare official reference with recovered
  span, and inspect residuals.
- Use the [catalog](gan_gold_phrase_variant_catalog_2026-08-13.md) when a
  sentence needs a longer list of official phrases.
- Do not cite these counts as model performance, holdout evidence, or
  clinical validation.

## What this draft still needs

- **6.0% residual.** 63 rows remain `other_paraphrase`. Some recovered
  spans are still weak (headers or nearby sentences rather than the
  justifying rate).
- **ExECT now has a sibling draft.** Diagnosis aliases, prescription
  renderings, and seizure-frequency state phrases on `dev140` live in
  [exect_gold_phrase_variants_2026-08-13.md](exect_gold_phrase_variants_2026-08-13.md).
- **No prompt-length experiment.** The token, latency, and interference
  costs are argued from the size of the dialect. They are not measured
  here as a prompt-ablation result.

## Evidence and limits

Literature and dataset lane: the [task-shape framework](../shared/task_shape_framework_2026-08-06.md)
and [Gan gold taxonomy](../gan2026/gold_task_taxonomy_2026-08-06.md) own the
task definition. This draft adds a gold-only phrase inventory on
development rows.

Project lane: [why the proposed method is a model plus recorded rules](why_hybrid_architecture_2026-08-09.md)
owns the architectural claim. Pipeline behaviour stays with
[system architecture](../../canon/01_system_architecture.md) and
[paper provenance](../../canon/10_paper_provenance.md).

This draft does not establish that a long prompt would fail, that the
current hybrid is optimal, or that every construction is a clinical
universal. It shows that the mapping from letter language to Gan gold is
large, structured, and mostly not an identity.

## Later writing test

**Question:** can the user show a reader, with actual phrases, why Gan
cannot treat extraction as “copy the rate out of the letter” and why
enumerating the rest in the prompt is the wrong design?

**Success:** the user can point at the closed output dialect, the open
input dialect, one ordinary-rate family with dozens of source forms, the
three costs of prompt enumeration, and the claim limits, without opening
the full technical record.

**Result:** passed 2026-08-14. The closed 45-template dialect, the 852
official phrases, the `1 per day` family (42 surfaces), the three
enumeration costs, and the development-gold / not-performance limits are
all on this page. The catalog and workbook stay available when a sentence
needs a longer list.
