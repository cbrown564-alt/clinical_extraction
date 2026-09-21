# Seizure-finding annotation guide

Canonical owner of source annotation rules and the output format. Version v0.7,
2026-09-16 (simplification approved by Conor; CB confirmed the cadence-as-rate
default on 2026-09-16, superseding the earlier singular-article decision). Apply with
the [annotation workflow and review](seizure_finding_annotation_review.md).
The [study protocol](one_shot_paper_protocol.md) owns benchmark endpoints and permissions.

v0.7 replaces v0.6 and its layered v0.3–v0.6 amendments with one integrated rule set.
Original v0.6 dev750 and test450 artifacts retain their recorded guide version;
those files are not rewritten. The frozen v0.6 text is in Git history and in the run folders'
`guide_versions/`. Migration of existing annotations is described at the end.

## Why v0.7 is narrower

The v0.6 dev750 reference held 2,962 findings: 37% qualitative wording and 26%
absence statements, of which 507 were bare denials with no time anchor, and 312
qualitative phrases carried no frequency information. Three models and two review
passes left 170 open questions across 136 letters; 115 of them asked whether two
source labels named the same events or whether a denied feature was an event. Those
questions are not answerable from the source, so v0.7 removes the rules that raise
them. The reference records what the letter says about how often seizures happen,
under the label the letter uses, and nothing else.

## Scope

Annotate every statement in the letter that quantifies or bounds how often the
patient's seizures (or explicitly seizure-like events) occur over time. A statement
is in scope only if it can be written as one of the five measurements below. Read
the whole letter; historical statements are in scope when they are quantified.

| Measurement | Use for | Plain-reading default |
| --- | --- | --- |
| `rate` | Recurrence per time: "twice weekly", "every 4–6 weeks", "q2wk", "an absence every night", "daily", "median interval ≈ 6 weeks", "3 seizure days per week" | Cadence without a stated count is 1 per interval. "Every N–M units" is 1 per N–M units. A bound ("up to 3 a week") is a bounded count. "Several per week" keeps the vague count. |
| `count` | Events in a stated window or on a stated date: "three in the past month", "one seizure on 12 May", "seizure days: 8/30 this month" | "N or M" is the range N–M. Affected-period counts use the event label "seizure days". |
| `seizure_free` | Absence with a duration or an anchor: "seizure-free for 14 months", "no seizures since March", "none in the past year" | Required: `duration` or `since`. A denial with neither is out of scope. |
| `last_seizure` | Explicit latest event with a time: "last seizure on 12 June", "most recent event three weeks ago" | Required: `occurred_at`. A dated event that is not called the latest is a count. |
| `qualitative` | Frequency wording with no number, from the closed list: `rare`, `occasional`, `frequent`, `increased`, `decreased`, `unchanged`, `variable`, `unknown` | Map source wording to the nearest value; "infrequent/intermittent/sporadic" → `occasional`; "most days/near-daily" → `frequent`; "not documented/unable to quantify" → `unknown`. Trend values are used only when the sentence is about frequency. |

Clusters keep the R7 `cluster` measurement: "monthly clusters of 3–4" is a cluster
with rate 1 per month and `seizures_per_cluster` 3–4; "clusters spaced 5 days
apart" is a cluster rate of 1 per 5 days; "two clusters this month" is a cluster
count with its period. "Clusters" without any cadence, count or size is out of scope.

Out of scope, with no issue logged: denials without a time anchor ("no auras", "no
history of status epilepticus", "no secondary generalisation", "no nocturnal
events"); occurrence-only statements ("recurrent seizures", "ongoing", "history of
epilepsy", "developed myoclonic jerks"); statements of pattern or circumstance without
a frequency ("predominantly nocturnal", "clusters around menses", "no clear catamenial
pattern"); maximal or typical gaps ("may go five days without seizures"); general
control or benefit ("better control", "improved"); device or diary signals; future
expectations, plans and thresholds; family history; medication schedules;
diagnostic, aetiological or classification uncertainty.

## Fixed defaults

These decide the cases that generated most v0.6 disagreement. Apply them without
raising an issue.

- Event label: use the source's words for the measured event (`event.type`). Each
  quantified statement is one finding under its own label. Never merge, sum,
  distribute or link findings because two labels might name the same events. There
  are no relations between findings.
- `event.scope` is a function of the label, not a judgement: `specific` when the
  label itself names a seizure type; `combined` only when the label is an explicit
  joint total ("focal and tonic-clonic seizures total four"); otherwise
  `unspecified`. Headings and context do not change it. Scoring recomputes scope
  from the label and does not compare emitted values.
- `event.seizure_status` has three values with `stated` as the default: `uncertain`
  only when the source explicitly questions whether the events are seizures
  ("possible seizures", "differential includes syncope"); `non_seizure` when
  explicitly excluded. There is no `unspecified`; a letter that never says treats
  them as stated. Uncertain subtype, aetiology or classification does not change
  this. (Decision 2026-09-16; v0.6 `unspecified` migrates to `stated`.)
- `timing`: `current` by default. `historical` only when the source explicitly marks
  a superseded period ("previously", "before treatment", "in 2015", "at diagnosis")
  and a later state is described or implied. There is no `unclear` or `future`.
- `period` and time points: copy the source expression; add numeric duration only
  when stated. Do not resolve relative dates, infer years or compute durations. A
  chronologically impossible date in a synthetic letter is annotated literally.
- `condition`: only a stated circumstance that restricts when the events occur
  (sleep/wake, time of day, a named trigger). Reporter, recording scope and hedges
  ("reported", "witnessed", "diary", "typically", "usually") are not annotated;
  strip a leading hedge and keep the circumstance. Condition is recorded but not
  part of the whole-match in finding scoring (decision 2026-09-16).
- Quantities: `number`, `range`, `bound` (`at_least`, `more_than`, `at_most`,
  `less_than`). No `approximate` flag and no inclusivity flags; the quotation
  carries "about", "roughly" and "on average". Durations use the R7 units,
  including `quarter`.
- Evidence: the shortest contiguous span containing the measurement and its time
  or window. Extend backwards by at most one sentence, and only when the event
  label does not appear in the measurement sentence. Matching requires overlap
  with the reference span, not an identical span. Inherited v0.6 spans are trimmed
  to this rule automatically and confirmed by the reviewer.
- Historical findings are kept and scored like current findings; results are
  reported by timing.
- Repeats: identical measurement, label, timing, period and condition within a
  letter is one finding; keep the first occurrence. Adding or omitting an
  observation window changes the period; do not automatically merge those findings.
  A correction ("in fact five,
  not four") keeps only the corrected value.

### Development review clarification (2026-09-21)

Conor approved preserving vague seizure-free durations rather than excluding them.
For "seizure-free for several months", use `seizure_free` with
`duration: {"type": "qualitative", "quantity": "several months"}`. Copy the complete
duration phrase, including its time unit, without inventing a number or a `since`
anchor. This extension applies to `seizure_free.duration`; numeric durations and
rate denominators retain their existing structures. Approximate but numeric
durations such as "about six months" keep numeric 6 month and the exact evidence.
An explicitly named observation interval with no numeric duration ("this month",
"In October", "during this interval") uses the same verbatim duration structure;
do not turn it into a full numeric month or a `since` anchor. Keep relative `since`
expressions relative even when another statement supplies a possible calendar date.

The Cursor reviewer instructions and assembler had introduced a broader repeat
rule that ignored an added or omitted observation window. That change was not in
this guide and is withdrawn. Assembly must preserve reviewed findings without
semantic merging. Preserve previously completed review files; apply any supported
corrections in a separate, attributed snapshot. These development clarifications
do not rewrite the frozen test450 annotations or authorise test-derived tuning.

## When to refuse

Raise `needs_review` only when all three hold: the statement is in scope; no default
above applies; and the competing readings produce different structured values
(for example "bimonthly", or a rate that could attach to either of two labels with
different numbers). Record one sentence in `review_reason`. Everything else is
decided by the defaults or excluded. Do not log candidates, alternatives, or
statements you excluded. A letter with `needs_review` is excluded from finding
scoring, so a question must be worth a whole letter.

## Decision table

| Step | Question | Action |
| --- | --- | --- |
| 1 | Does the statement say how often, how many, how long without, or when last? | No → skip. Yes → continue. |
| 2 | Is there a number, cadence, window, anchor or closed-list word? | No → skip (occurrence-only). Yes → continue. |
| 3 | Is it a denial? | With duration/since → `seizure_free`. Without → skip. |
| 4 | Is it the latest event with a time? | → `last_seizure`. |
| 5 | Is the measured unit clusters? | → `cluster` with the stated rate/count/size. |
| 6 | Is it events per time or a cadence? | → `rate` (cadence = 1 per interval). |
| 7 | Is it events in a window or on a date? | → `count` ("N or M" = range). |
| 8 | Otherwise map the wording to the closed qualitative list. | → `qualitative`; unmappable → skip. |
| 9 | Fill label, scope, status, timing, period, condition by the fixed defaults. | Quote the minimal span. |
| 10 | Do two readings still give different structured values? | Yes → `needs_review` with one-line reason. No → done. |

## Output

One JSON object per letter (JSONL for batches). Findings use the R7 `Finding` and
`DocumentDate` structures, restricted as above (no `approximate`, no inclusivity
flags, timing `current`/`historical` only). Wrapper fields:

- `guide_version`: `seizure_finding_annotation_v0.7`.
- `source_id`, `source_row_index`, `source_sha256`: copied from the manifest.
- `annotation_state`: `complete`, `needs_review` or `source_unavailable`.
- `document_dates`, `findings`: arrays; empty arrays are explicit.
- `review_reason`: one sentence, required when `needs_review`.
- `notes`: optional free text for the reviewer; never scored.

There are no `finding_context`, `source_checks`, `issues` or relation fields. The
offline checker verifies source identity, schema, exact quotation occurrence and
state consistency; the semantic review is one independent full-source reread per
letter recording agreement or the corrected record.

## Migration from v0.6

`scripts/benchmarks/migrate_seizure_findings_v07_dry_run.py` applies these rules
mechanically to a v0.6 annotation file and writes a report, a migrated candidate, the
conversions it made, the qualitative phrases it excluded and the phrases needing a
human decision, all under a new local `runs/` directory. On the merged dev750
working candidate (2026-09-16) it maps 2,962 findings to 2,215: 507 bare denials and
240 occurrence/condition/no-frequency phrases dropped, 160 cadence, alternative-count,
seizure-day and cluster phrases converted to structured values, 597 phrases mapped to
the closed list, 95 phrases left for manual mapping, and 130 of 170 open questions
dissolved (127 by rule, three because their findings were dropped), leaving 40
questions in 34 letters marked `needs_review`. The migrated candidate is a dry
run, not an accepted reference: the manual-mapping phrases and the 34 retained
questions need a human pass, and the same script must be run over the test450
annotations in aggregate-only mode with no test-derived rule changes.
