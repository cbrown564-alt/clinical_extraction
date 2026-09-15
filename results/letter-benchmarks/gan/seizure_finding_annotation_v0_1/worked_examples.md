# Seizure-finding annotation: fictional examples, v0.4

All letters and decisions below are authored illustrations, not patient records,
benchmark rows or validation results. The
[annotation guide](../../../../docs/research/gan2026/seizure_finding_annotation_guide.md#seizure-finding-annotation-guidelines--v03-2026-09-15)
is the canonical policy. These examples contain no Gan answer labels.

## Gemini handoff

Use the [exported guide](annotation_guide.md) and [JSON Schema](annotation.schema.json)
with the full working folder described in the guide. The guide export is generated
from the annotation guide and review documents; it is not a second policy owner. The directory name
records its creation at v0.1; the file contents and hashes identify the active v0.4.
These artifacts contain no dev750 sources or completed annotations.

**Initial annotation instruction**

> Read annotation_guide.md, annotation.schema.json, worked_examples.md, manifest.json,
> decisions.jsonl and progress.jsonl. Confirm access to all sources and saved outputs
> as the guide requires. Execute the next assigned annotation batch using D01–D12.
> Read each whole source and account for candidate statements in source_checks.
> Apply A01–A09 before saving each record. Do not return benchmark answer labels.
> Save outputs and progress to the working folder; preserve raw attempts. Record
> unresolved questions rather than inventing values. Resume from saved progress,
> not remembered conversation. Do not scale beyond the pilot before its acceptance.

**Gemini self-review instruction**

> Freeze the initial annotation snapshot. For every source, read the full letter
> and list candidate quotes before examining its saved findings. Run A01–A09 and
> save checks.jsonl in reviews/gemini. Then run C01–C08 over all 750 sources and
> annotations, including earlier batches, empty records and unresolved cases.
> Save every comparison group, its members and its decisions. Apply supported
> corrections in a new snapshot and log them in changes.jsonl. Search all sources
> for each correction pattern, record justified exceptions and rerun affected checks.
> Report checked and pending coverage; do not claim completion while checks remain.

**Codex second-review instruction**

> Repeat the same per-letter and cross-sample procedure on Gemini's reviewed
> snapshot. First list candidate quotes from each full source independently of the
> saved finding list and Gemini's conclusions. Use the same A01–A09 and C01–C08
> definitions; save separate reports in reviews/codex. Review all 750 letters,
> not only Gemini's flags. Preserve disagreements and source-based corrections.
> Reconcile coverage, hashes and unresolved cases before freezing the reference.

These instructions invoke the full guide; they do not replace its detailed rules.
No evaluated predictions or existing Gan answer labels are inputs to annotation.

## Complete record: recurrence and an observed count

Fictional source:

```text
She currently has two focal seizures per week. She also had three tonic-clonic seizures in the past six weeks.
```

The first sentence states recurrence; the second counts observed events. They
concern distinct event types and neither is a combined count. The recent count is
current because “the past six weeks” anchors it to the current review. No date or condition is stated.
The source hash below was computed from this fictional source as one line,
without a trailing newline. Actual annotation identifiers and hashes must be copied
from the supplied manifest, not calculated or invented by Gemini.

```json
{
  "guide_version": "seizure_finding_annotation_v0.6",
  "source_id": "fictional-example-01",
  "source_row_index": 0,
  "source_sha256": "a3ca54724e1f1f34dfd614e7797d466c1b12e10212ae22acb589a093be1913c6",
  "annotation_state": "complete",
  "document_dates": [],
  "findings": [
    {
      "id": "f1",
      "event": {
        "type": "focal seizures",
        "scope": "specific",
        "seizure_status": "stated"
      },
      "measurement": {
        "type": "rate",
        "count": {
          "type": "number",
          "value": 2
        },
        "per": {
          "type": "number",
          "value": 1,
          "unit": "week"
        }
      },
      "timing": "current",
      "evidence": "She currently has two focal seizures per week."
    },
    {
      "id": "f2",
      "event": {
        "type": "tonic-clonic seizures",
        "scope": "specific",
        "seizure_status": "stated"
      },
      "measurement": {
        "type": "count",
        "count": {
          "type": "number",
          "value": 3
        }
      },
      "timing": "current",
      "period": {
        "time": "the past six weeks",
        "duration": {
          "type": "number",
          "value": 6,
          "unit": "week"
        }
      },
      "evidence": "She also had three tonic-clonic seizures in the past six weeks."
    }
  ],
  "finding_context": [
    {
      "finding_id": "f1",
      "mentions": [
        "She currently has two focal seizures per week."
      ],
      "relations": []
    },
    {
      "finding_id": "f2",
      "mentions": [
        "She also had three tonic-clonic seizures in the past six weeks."
      ],
      "relations": []
    }
  ],
  "issues": [],
  "source_checks": [
    {
      "evidence": "She currently has two focal seizures per week.",
      "disposition": "included",
      "finding_ids": [
        "f1"
      ],
      "issue_ids": [],
      "rule_id": "D06",
      "reason": ""
    },
    {
      "evidence": "She also had three tonic-clonic seizures in the past six weeks.",
      "disposition": "included",
      "finding_ids": [
        "f2"
      ],
      "issue_ids": [],
      "rule_id": "D06",
      "reason": ""
    }
  ]
}
```

## Worked scope and identity decisions

Each quoted source is a complete fictional snippet for this exercise. In a letter,
read surrounding text before deciding scope, timing or uncertainty.

| Source | Expected inventory and reason |
| --- | --- |
| “Previously she had one focal seizure daily. She now has one focal seizure per month.” | Two rates: historical 1/day and current 1/month. Do not discard the earlier rate or average them. |
| “She has two seizures weekly. Her seizures occur twice a week.” | One rate, 2/week, with both exact mentions. Repetition does not create a second finding. |
| “She reports two seizures weekly. Her mother reports five seizures weekly.” | Two rates with separate reporters and `conflicts_with`; preserve both without adjudicating whose account is true. |
| “Focal and tonic-clonic seizures together occur four times monthly.” | One rate, 4/month, `scope: combined`. No type-specific allocation. |
| “She has brief staring spells twice weekly, but whether these are seizures is unclear.” | One specific-event rate with `seizure_status: uncertain`; quote the uncertainty as well as the number. |
| “The shaking spells occurring once weekly are explicitly described as non-epileptic events.” | One rate, 1/week, `seizure_status: non_seizure`; do not turn it into an epileptic seizure rate. |
| “She has two seizures per day when she misses medication.” | One rate with the stated condition. This does not assert an unconditional daily rate. |
| “She expects her seizures to become less frequent next month.” | One future qualitative finding, retaining “less frequent” and the time expression. An expectation is not an observed improvement. |
| “Call the clinic if she has two seizures in a day.” | Empty inventory: hypothetical advice alone is not an observed count or recurrence. |
| “Her father has weekly seizures. She takes medication twice daily.” | Empty inventory: family history and medication schedule are outside scope. |
| “She has epilepsy. Frequency is not documented.” | One qualitative finding, “Frequency is not documented.” Evidence must include the epilepsy context. Do not return seizure freedom. |
| “Blood pressure was measured.” | Complete empty inventory, empty contexts and issues. This is different from an annotation failure. |

## Worked measurements and time

| Source | Expected representation |
| --- | --- |
| “She has about 2–3 seizures every two weeks.” | Rate count range 2–3, `per` number 2 weeks, measurement `approximate: true`. Do not replace with a midpoint or a weekly rate. |
| “She has up to 2–3 seizures per week.” | Rate count `{type: bound, relation: at_most, value: {type: range, lower: 2, upper: 3}}`, per 1 week. |
| “She has more than two but at most five seizures weekly.” | Count range lower 2, upper 5, `lower_inclusive: false`, per 1 week. Upper inclusivity defaults true. |
| “She had several seizures in roughly six weeks.” | Observed count `{type: qualitative, quantity: several}`, period duration 6 weeks, `approximate: true` because of the period. |
| “She has seizures on most days.” | Qualitative frequency “most days”; no inferred seizure count. |
| “She has no more than two seizures weekly.” | Rate with `at_most` 2/week, not seizure freedom. |
| “She has no daily seizures.” | Qualitative denial of daily recurrence. Do not infer zero seizures or a less-than-daily numerical rate. |
| “She has had no tonic-clonic seizures since May but has one focal seizure weekly.” | Event-scoped seizure freedom since calendar “May”, plus a focal rate 1/week. Do not add a last seizure in May. |
| “Her last seizure was on 12 May; she has had none since.” | Last seizure with calendar “12 May”, plus seizure freedom since relative “since”, with the full sentence supporting the anchor. No inferred year or elapsed duration. |
| “She had two seizures on 12 May.” | Count 2 with `occurred_at` calendar “12 May”. Timing is unclear without review context; it is not necessarily the last seizure. |
| “She had three clusters in the past six weeks, each containing two to four seizures.” | One cluster finding: cluster count 3, seizures-per-cluster range 2–4, period six weeks. No derived total of 6–12 seizures. |
| “She has two clusters weekly, each containing three seizures.” | One cluster finding: nested rate count 2 per 1 week; seizures-per-cluster 3. Do not emit a source rate of six seizures weekly. |
| “She has clusters every four weeks.” | One qualitative finding preserving “clusters every four weeks”; no inferred cluster count. |
| “She has clusters of seizures.” | One cluster finding with no numeric components. Do not invent cluster size or recurrence. |
| “She had three clusters.” | `needs_review`: R7 cluster count requires an anchor; retain the exact claim as `representation_gap`, with no invented period. |
| “She had seizures on three days last month.” | `needs_review`: seizure-days are not a seizure count. Retain a `representation_gap`; do not encode three seizures. |
| “She has two or three seizures a week or month.” | `needs_review`: denominator ambiguity. Retain the exact statement and week/month alternatives in an issue. |
| “Clinic Date: 14 September 2026. Letter Date: 16 September 2026.” | Two document dates with distinct roles and empty findings. Document dates do not enter the seizure-finding denominator. |

For a representation gap, an issue can be the only retained candidate assertion:

```json
{
  "id": "i1",
  "finding_ids": [],
  "evidence": "She had seizures on three days last month.",
  "kind": "representation_gap",
  "question": "How should the seizure-day counting unit be retained without treating days as seizures?",
  "alternatives": ["Retain as an unresolved seizure-day assertion pending a representation decision."]
}
```

The complete wrapper for this case has `annotation_state: needs_review`, empty
`findings` and `finding_context`, this issue, and a `source_checks` entry linking
the quote to `i1` with disposition `unresolved` and rule D12. It is not a reviewed empty
reference. A guide/schema decision is needed before the letter becomes adjudicable.

## Overlap and contextual evidence

Fictional source:

> She reported two clusters of tonic-clonic seizures in August. The latest cluster
> occurred on 28 August. Her last tonic-clonic seizure was on that date, and she
> has had none since.

Retain four claims: interval cluster count 2; dated cluster count 1; last seizure;
and seizure freedom. Link the dated cluster to the interval total with
`overlaps_with`. The interval and dated counts have unclear timing without further review context.
The current last-event and ongoing-freedom claims have current timing.
The dated cluster's evidence must include the first sentence to support its event
type. The last-event and freedom evidence must include the date antecedent. Preserve
“that date” without computing or substituting a date. Do not add the dated cluster
to the total and do not infer a seizure count from the cluster count.

The older R7 design fixtures illustrate schema serialization, not annotation
reference quality. In particular, a short quote may parse successfully yet omit
antecedents needed for whole-finding support under this guide.

## Worked scoring

Suppose the reviewed reference contains two findings from the complete record:
a rate 2/week and an observed count 3 in six weeks.

| Prediction | Whole-finding result |
| --- | --- |
| Both findings with sufficient exact evidence | TP=2, FP=0, FN=0; precision=recall=1. |
| Rate only | TP=1, FP=0, FN=1; precision=1, recall=0.5. |
| Correct rate twice; count omitted | TP=1, FP=1, FN=1; precision=recall=0.5. |
| Correct rate; count changed to 0.5/week | TP=1, FP=1, FN=1. Derived rate cannot match source count. |
| Correct values, but count quotation says only “three” | TP=1, FP=1, FN=1. Exact occurrence is insufficient to support event and period. |
| Valid empty inventory | TP=0, FP=0, FN=2; precision undefined, recall=0. |
| Unparseable response | No TP, FN=2, predicted count unknown; record a failed letter, with precision reporting limitations specified in the guide. |

For a reviewed empty source, a valid empty inventory is a correct empty inventory;
a failed response is not. Neither earns invented precision/recall of 1. These are
arithmetic examples, not measured extraction performance.

## Cross-sample review: same words, different decisions

These fictional members illustrate a C03 comparison. Actual group records retain
source IDs, exact quotes, finding IDs and links to any changes.

| Member | Source | Saved annotation | Review decision |
| --- | --- | --- | --- |
| A | “She had three seizures in the past month.” | Rate 3/month | Error under D06: change to count 3 with a past-month period. |
| B | “She has three seizures per month.” | Rate 3/month | Retain under D06: explicit recurrence. |
| C | “She has daily seizures.” | Rate 1/day | Error under D07: change to qualitative “daily”. No event count was stated. |
| D | “She has one seizure daily.” | Rate 1/day | Retain under D07: count is explicit. |

A reviewer must not change B just to agree with A, or D just to agree with C.
After correcting A, C08 searches every source for observed counts expressed with
“in the past”, “last” and equivalent wording, including records with no emitted
finding. After correcting C, it searches unquantified recurrence across the set.
Save corrected members and justified exceptions. Rebuild the groups after edits.

For example, the A/B comparison within a group can be recorded as:

```json
{
  "member_ids": ["A", "B"],
  "outcome": "error",
  "rule_ids": ["D06"],
  "reason": "A reports an observed past-month total; B asserts recurrence. A's rate is incorrect.",
  "change_ids": ["change-A-01"],
  "issue_ids": []
}
```

The same fields are used in Gemini's and Codex's group reports. A corrected A/B
comparison in the new snapshot becomes `justified_difference`, with the count/rate
distinction as its reason. Keep the earlier comparison rather than overwriting it.

A07 also has two distinct outcomes: a tool may confirm that “three seizures” occurs
in a source, while the reviewer fails that quote because it omits the event's period.
Record the insufficient-support reason even when exact quotation checking passes.

For a clean letter, record all nine A checks as `pass`, with empty finding/issue
lists and notes where no explanation is needed. Record the independently reread
candidate quotations at the top of the check record. For a problem, use `fail` for
a demonstrated error and `unresolved` for a question the guide/source cannot settle.
A completed mechanical report alone never supplies the nine review decisions.

## Expanded-pilot scope checks

| Source wording | Decision |
| --- | --- |
| “Events occur twice weekly, typically as brief focal episodes.” | One rate; the typical event description remains in its evidence. No separate “typically” frequency. |
| “Events occur twice weekly; occasional episodes progress to convulsions.” | Rate plus a qualitative progression finding. “Occasional” describes occurrence of the additional event. |
| “Frequency fell to twice weekly.” | Current rate plus qualitative reduction, with overlap recorded. Do not invent the earlier rate. |
| “Better control on treatment; seizures remain twice weekly.” | Current rate; no separate frequency change inferred from “better control”. |
| “Previously weekly clusters, usually three events within about two hours.” | One historical qualitative finding retaining the complete cluster phrase and approximation. No invented cluster count. |
| “Spells occurred on several mornings.” | Qualitative phrase plus an affected-period counting-unit issue; no guessed event count. |

## Qualified conditions (D08)

| Source wording | Decision |
| --- | --- |
| “She has three seizures per month. Missed meals may trigger these seizures.” | Retain rate 3/month and the qualified condition “Missed meals may trigger these seizures”. Include both sentences in evidence. Do not change this into three seizures only when meals are missed, or assert a proven cause. |
| “A cluster occurred yesterday. No clear trigger was identified, though poor sleep was noted beforehand.” | Retain the observed cluster and the full qualified context. “No clear trigger” must not be dropped while retaining poor sleep. |
| “She had one seizure on Monday. In general, missed meals may trigger her seizures.” | Retain the observed count and Monday. The general statement does not establish that a missed meal preceded Monday's event; do not attach an invented incident-specific cause. |


## Native quarter representation (v0.6)

Fictional source: “Seizures occur at an estimated 8 to 16 per quarter.”
Represent this as a `rate` with range count 8–16, `per` equal to a number duration
of 1 `quarter`, and `approximate: true`. Preserve the unit; do not convert to months.
The native-quarter candidate's fictional fixtures also exercise cluster-rate ranges
and bounded seizure-free durations. These are representation checks, not performance evidence.
