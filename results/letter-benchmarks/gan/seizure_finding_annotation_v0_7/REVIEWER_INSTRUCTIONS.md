# Seizure-finding review instructions — guide v0.7

You are the independent reviewer for a batch of synthetic clinic letters. For each
letter you receive the full source text and a candidate annotation produced by a
mechanical migration. Your job is to make each record correct under the rules below
and to say whether you agreed with the candidate or corrected it.

Work letter by letter. First read the whole letter and list, for yourself, every
statement about how often the patient's seizures or seizure-like events occur. Then
compare with the candidate record. Then write the final record. Do not trust the
candidate for coverage: it may be missing statements, and it may contain findings
that the rules below exclude.

## What is a finding

A finding is one statement that quantifies or bounds how often the patient's seizures
(or explicitly seizure-like events) occur, written as exactly one of:

| Type | Use for | Rule |
| --- | --- | --- |
| `rate` | Recurrence per time | Cadence with no count is 1 per interval: "every 4–6 weeks" → count 1 per range 4–6 week; "an absence every night", "daily", "weekly", "q2wk", "a focal seizure monthly" → count 1 per 1 unit; "median interval ≈ 6 weeks" → 1 per 6 week. "Up to 3 a week" → bound at_most 3 per 1 week. "Several per week" → qualitative quantity "several" per 1 week. Keep the unit (second, minute, hour, day, week, month, quarter, year); never convert. |
| `count` | Events in a stated window or on a date | Keep `period.time` or `occurred_at` verbatim. "N or M" → range N–M. "Seizure days: 8/30 this month" → count 8, event type "seizure days", period "this month". Never turn a count into a rate. |
| `cluster` | Cluster measurements | "Monthly clusters of 3–4" → rate {count 1, per 1 month} plus seizures_per_cluster range 3–4. "Clusters spaced 5 days apart" → rate 1 per 5 day. "Two clusters this month" → count 2 with period. A cluster with no rate, count or size is not a finding. |
| `seizure_free` | Absence with a duration or anchor | Needs `duration` or `since`: "seizure-free for 14 months", "none since March", "no seizures in the past year" (duration 1 year). A denial with neither is not a finding. |
| `last_seizure` | Latest event with a time | Needs `occurred_at`; only when the source calls it the last/latest/most recent. A dated event not called latest is a `count`. |
| `qualitative` | Frequency words, no number | `frequency` must be one of: rare, occasional, frequent, increased, decreased, unchanged, variable, unknown. infrequent/intermittent/sporadic/sometimes → occasional; most days/near-daily → frequent; more frequent/worsening frequency → increased; less frequent/reduced → decreased; not documented/unable to quantify → unknown; fluctuating → variable. Trend values only when the sentence is about frequency. |

Not findings, and not to be logged anywhere: denials without a time anchor ("no
auras", "no history of status epilepticus", "no secondary generalisation", "no
nocturnal events"); occurrence-only statements ("recurrent seizures", "ongoing",
"history of epilepsy", "developed myoclonic jerks"); pattern or circumstance without a
frequency ("predominantly nocturnal", "clusters around menses", "no clear catamenial
pattern"); typical gaps ("may go five days without seizures"); general control or
benefit ("better control", "improved"); device or diary signals; plans, thresholds
and future expectations ("call if more than two a week"); family history; medication
schedules; diagnostic, aetiological or classification uncertainty.

## Fixed defaults

- `event.type`: the source's words for the measured event. One finding per quantified
  statement under its own label. Never merge, sum, distribute or link findings because
  two labels might name the same events.
- `event.scope`: `specific` if the label itself names a seizure type (absence, focal,
  tonic-clonic, myoclonic, drop attack, spasm, status, aura, convulsion, cluster,
  seizure days…); `combined` only for an explicit joint total ("focal and tonic-clonic
  seizures total four"); otherwise `unspecified` ("seizures", "events", "episodes",
  "nocturnal events", "blackouts"). The checker recomputes this from the label.
- `event.seizure_status`: `stated` (default). `uncertain` only when the source
  explicitly questions whether the events are seizures ("possible seizures",
  "differential includes syncope"). `non_seizure` when explicitly excluded. Uncertain
  subtype, aetiology or classification does not change it.
- `timing`: `current` (default). `historical` only when the source explicitly marks a
  superseded period ("previously", "before treatment", "in 2015", "at diagnosis") and a
  later state is described or implied.
- `period` / time points: copy the source expression into `time`; add `duration`
  (numeric with unit) only when stated ("in the past six weeks" → duration 6 week;
  "since last review" → no duration). Do not resolve relative dates, infer years or
  compute anything. An impossible date in a synthetic letter is annotated literally.
- `condition`: only a stated circumstance restricting when events occur (sleep/wake,
  time of day, a named trigger). Reporter, recording scope and hedges ("reported",
  "witnessed", "diary", "typically", "usually") are not conditions; strip a leading
  hedge and keep the circumstance. Omit the field when there is none.
- Quantities: `{"type":"number","value":3}`, `{"type":"range","lower":2,"upper":3}`,
  `{"type":"bound","relation":"at_most","value":3}` (value may be a number or a range
  object), `{"type":"qualitative","quantity":"several"}`. Durations add `"unit"`.
  There is no `approximate` flag and no inclusivity flag.
- `evidence`: an exact, contiguous quotation of the shortest span containing the
  measurement and its time or window. Extend backwards by at most one sentence, only
  when the event label is absent from the measurement sentence. Copy characters
  exactly (dashes, quotes, spacing).
- Repeats: identical measurement, label, timing, period and condition within a letter
  is one finding; keep the first occurrence. A correction keeps only the corrected value.
- `document_dates`: explicit clinic/letter dates with role, time, form and exact
  evidence. Not findings. Keep the candidate's unless wrong.

## When to mark needs_review

Only when all three hold: the statement is in scope; no default above decides it; and
the competing readings give different structured values (for example "bimonthly", or a
rate that could attach to either of two labels with different numbers). Then set
`annotation_state` to `needs_review` and write one sentence in `review_reason`. Every
other case is decided by the defaults or excluded. A needs_review letter is excluded
from scoring, so a question must be worth the whole letter.

Candidate records may carry `notes` such as `MANUAL f3: qualitative phrase '...'` (a
phrase the migration could not map; its measurement is a placeholder `unknown` that you
must replace or remove) or `CONDITION f2: check attribution in '...'`. Resolve every
note; do not copy notes into the final record. Candidate `review_reason` text from the
earlier review is a question for you to decide, not to carry forward, unless it meets
the three-part test above.

## Output

Write one JSON object per letter, one per line, to the batch's `reviewed.jsonl`, in
the same order as `candidate.jsonl`:

```json
{"guide_version":"seizure_finding_annotation_v0.7","source_id":"123","source_row_index":45,
 "source_sha256":"<copy from candidate>","annotation_state":"complete",
 "document_dates":[...],"findings":[{"id":"f1","event":{"type":"absence seizures","scope":"specific","seizure_status":"stated"},
 "measurement":{"type":"rate","count":{"type":"number","value":1},"per":{"type":"number","value":1,"unit":"day"}},
 "timing":"current","condition":"at night","evidence":"She reports an absence seizure every night."}],
 "review":{"verdict":"corrected","changes":["f2 removed: bare denial 'no auras'","f1 cadence converted to rate 1 per day"]}}
```

`review.verdict` is `agree` (record unchanged apart from formatting) or `corrected`;
`changes` lists each change in one short line. Number findings f1, f2, … in first-mention
order. Copy `source_id`, `source_row_index` and `source_sha256` from the candidate.
Omit optional fields that are absent (no nulls). An empty `findings` array is a valid
record for a letter with no in-scope statement.

Then run the checker from the repository root and fix every error before finishing:

```sh
.venv/bin/python scripts/benchmarks/check_annotations_v07.py --sources <batch>/sources.jsonl --annotations <batch>/reviewed.jsonl --expected <n>
```

The checker rejects unknown keys other than `review`; it verifies exact quotation
occurrence, the closed lists, anchors and derived scope. Finish only when it reports
`"error_count": 0`, and report the verdict counts and the checker result.
