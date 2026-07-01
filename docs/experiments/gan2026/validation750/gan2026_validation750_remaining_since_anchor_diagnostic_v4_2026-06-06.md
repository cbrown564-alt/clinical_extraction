> **Superseded for navigation —** canonical summary: [`VALIDATION750_CANON.md`](../VALIDATION750_CANON.md). Full detail retained below.

# Gan 2026 Validation750 Remaining Since-Anchor Diagnostic V4

Date: 2026-06-06

Status: validation mechanics diagnostic over saved V4 projection/render
artifacts. This report is for component design only. It does not authorize
locked-test row-level review, benchmark-comparable claims, or promotion of a
whole pipeline.

## Source Artifacts

- Projection/render:
  `experiments/gan2026_clinical_assessment_projection_render_validation750_gpt41mini_context_repair_v4_2026-06-06.jsonl`
- Candidate set:
  `experiments/gan2026_validation750_candidate_set_v3_nested_dedupe_context_v0_2026-06-06.jsonl`
- Architecture synthesis:
  ``

V4 left 19 unresolved seizure-free since-anchor rows:

- `seizure_free_since_date_anchor_unparsed`: 19;
- rendered rows: 573;
- null-rendered rows: 177;
- route rows: 48;
- V0 verification decisions: 48 `abstain`.

## Diagnostic Goal

The goal is not to rescue every row. The goal is to decide whether any remaining
surface implies a logical, clean, generalisable component that should help with
the validation/test generalisation gap.

The bar for a next component is:

- explicit ownership in the reset stage model;
- source-backed state, not hidden scorer-facing fallback;
- ablatable behavior and issue traces;
- plausible reuse beyond these 19 rows;
- no broad inference from the current note date alone.

## Remaining Surface Summary

| Bucket | Count | Rows | Interpretation |
| --- | ---: | --- | --- |
| Prior-encounter anchor | 7 | 3118, 4842, 5197, 7738, 7872, 8188, 8802 | Needs a prior-visit / prior-contact date contract. |
| Treatment or surgery event anchor without date | 7 | 8724, 8922, 8924, 14250, 14540, 14581, 14672 | Needs event-date extraction for medication, dose, regimen, surgery, or withdrawal events. |
| Same-note antecedent unclear | 4 | 14282, 14284, 14332, 14454 | V4 correctly refuses because the antecedent has no single clean date anchor or has competing event semantics. |
| Initial-referral anchor | 1 | 5092 | Needs referral-date context and may be historical / no-epilepsy boundary, not a seizure-free projection problem. |

## Bucket 1: Prior-Encounter Anchors

Examples:

```json
{
  "source_row_index": 3118,
  "source_phrase": "No seizures since last visit",
  "row_context": {
    "reference_date": {
      "date": "2023-08-26",
      "source": "note_header"
    }
  },
  "current_state": {
    "state_kind": "unresolved_anchor",
    "instrumentation_issues": [
      "seizure_free_since_date_anchor_unparsed"
    ]
  }
}
```

```json
{
  "source_row_index": 8802,
  "source_phrase": "no episodes suggestive of seizures since last review",
  "supporting_summary": "Patient reports no seizures since last review, confirmed by wearable diary data over 12 months showing no detected events.",
  "row_context": {
    "reference_date": {
      "date": "2014-01-10",
      "source": "note_header"
    }
  }
}
```

Clean component idea:

```json
{
  "row_context": {
    "reference_date": {
      "date": "2023-08-26",
      "source": "note_header"
    },
    "prior_encounter": {
      "date": "2023-02-26",
      "date_precision": "day",
      "source": "explicit_followup_interval",
      "source_phrase": "last appointment six months ago",
      "context_role": "prior_visit_date"
    }
  }
}
```

Recommended policy:

- Do not infer a prior-visit date from `last visit` alone.
- Allow prior-encounter anchoring only when a separate source-backed prior
  encounter date or interval exists, for example `last appointment six months
  ago`.
- If only the current clinic date is known, keep unresolved.

Generalisability value: high. Prior-encounter anchoring is common clinical
language and will likely recur outside validation750. But the right component is
a row-context / encounter-context extractor, not a seizure-free renderer patch.

## Bucket 2: Treatment Or Surgery Event Anchors Without Dates

Examples:

```json
{
  "source_row_index": 8922,
  "source_phrase": "being without further seizures since the most recent dose increase",
  "missing_contract": "dose_increase_event_date"
}
```

```json
{
  "source_row_index": 14581,
  "source_phrase": "No further seizures since surgery and initiation of Levetiracetam.",
  "missing_contract": "surgery_or_medication_start_event_date"
}
```

Some summaries mention dates or intervals, but these are not consistently
selected/source-backed in the current reset contracts. For example:

```json
{
  "source_row_index": 8724,
  "assessment_summary": "seizure-free since titration to the current levetiracetam dose three months ago",
  "selected_candidate_phrase": "Since titration to her current antiepileptic dose, she describes no episodes suggestive of seizures"
}
```

Clean component idea:

```json
{
  "event_date_context": {
    "event_kind": "medication_titration",
    "event_date": {
      "date": "2025-07",
      "date_precision": "month",
      "source": "explicit_relative_event_interval",
      "source_phrase": "titration to the current levetiracetam dose three months ago"
    },
    "linked_candidate_ids": ["llm:8724:2"],
    "issues": [
      "event_date_inferred_from_relative_interval"
    ]
  }
}
```

Recommended policy:

- Do not use treatment/surgery anchor phrases unless the event date or relative
  interval is source-backed and carried by a named event-date context.
- Do not silently use LLM assessment-summary dates as new facts unless they can
  be tied back to source evidence or selected candidate ids.
- Keep `since surgery`, `since dose increase`, and `since starting regimen`
  unresolved when no event date is available.

Generalisability value: medium to high, but only if implemented as a general
event-date extraction contract. It should cover medication start, dose change,
surgery, device implantation, withdrawal, and other clinical interventions. It
should not be implemented as seizure-free-specific regex rescue.

## Bucket 3: Same-Note Antecedent Unclear

Examples:

```json
{
  "source_row_index": 14282,
  "source_phrase": "No further seizures have occurred since",
  "summary": "several seizures in the week following Levetiracetam withdrawal but has had no further seizures since",
  "status": "unresolved"
}
```

```json
{
  "source_row_index": 14332,
  "source_phrase": "She has not had any further events since.",
  "summary": "cluster of five seizures around early October ... Lamotrigine was stopped on 01-Oct",
  "status": "unresolved"
}
```

V4 already implemented the safe part of this family:

```json
{
  "antecedent": {
    "link_type": "local_since_then_antecedent",
    "source_phrase": "The patient experienced 2 to 3 seizures shortly after discontinuing valproate on 10 Jul",
    "anchor_date": {
      "date": "2019-07-10",
      "source_phrase": "since 10 Jul"
    }
  }
}
```

The remaining rows are not clean. They are missing a single local date-bearing
antecedent, or they include competing event semantics such as medication
withdrawal, stopping a medication, last events, and treatment changes.

Recommended policy:

- Do not extend the same-note antecedent resolver now.
- Keep these rows unresolved unless a future event-date extractor produces a
  named candidate event date.

Generalisability value: low for further direct antecedent work. The next
generalisable idea is event-date extraction, not looser antecedent matching.

## Bucket 4: Initial-Referral Anchor

Example:

```json
{
  "source_row_index": 5092,
  "source_phrase": "No clinical seizures observed since the initial referral",
  "candidate_temporality": "historical",
  "row_reference_date": "2020-03-31"
}
```

This is not a clean seizure-free duration case unless the initial referral date
is known. It may also belong to a no-epilepsy / no-current-epileptic-events
boundary rather than a benchmark seizure-free interval.

Recommended policy:

- Do not implement a special initial-referral fallback.
- If referral dates matter later, include them under the same broader
  event/context-date contract as prior encounters.

Generalisability value: low as a standalone component.

## Recommendation

There is no clean solution that should be added directly inside seizure-free
duration normalization for all 19 remaining rows.

The most logical next component is a **prior-encounter date context** component,
because it is:

- common in clinical documentation;
- cleanly owned by row context rather than projection;
- useful beyond seizure-free rows;
- directly relevant to generalisation, because `since last visit/review` style
  language is likely to recur in validation/test distribution shifts.

But it should only be built if we can source a prior encounter date or explicit
relative interval. Without that, the correct behavior is to leave rows
unresolved.

The second-best generalisable component is a broader **event-date context**
extractor for medication changes, surgery, device implantation, withdrawal, and
dose titration. This has more scope and higher risk, so it should probably come
after prior-encounter context or be designed separately.

## Suggested Next Conversation

Proposed next action:

```text
Design prior_encounter_context_v0.
```

Minimum viable schema:

```json
{
  "row_context": {
    "reference_date": {
      "date": "2021-11-05",
      "source": "note_header"
    },
    "prior_encounter": {
      "date": "2021-05-05",
      "date_precision": "day",
      "source": "explicit_relative_interval",
      "source_phrase": "last appointment six months ago",
      "context_role": "prior_visit_date",
      "issues": [
        "prior_encounter_date_inferred_from_relative_interval"
      ]
    }
  }
}
```

Decision needed before implementation:

- Should prior-encounter context accept relative intervals such as `last
  appointment six months ago`, or only explicit prior dates?
- Should `last notification period` be included under prior encounter, or kept
  as a separate administrative/contact-period context?
- Should prior-encounter-derived seizure-free durations render automatically,
  or route as policy-sensitive until validated?

## Implementation Addendum: Prior-Encounter Context V5

Decision taken after discussion:

- Accept explicit relative prior-encounter intervals.
- Do not treat `last notification period` itself as a prior encounter.
- Route prior-encounter-derived seizure-free durations as policy-sensitive.

Implemented schema:

```json
{
  "row_context": {
    "reference_date": {
      "date": "2021-11-05",
      "source": "note_header"
    },
    "prior_encounter": {
      "date": "2021-05-05",
      "date_precision": "day",
      "source": "explicit_relative_interval",
      "source_phrase": "last appointment six months ago",
      "context_role": "prior_visit_date",
      "issues": [
        "prior_encounter_date_inferred_from_relative_interval"
      ]
    }
  }
}
```

Accepted phrase families include:

- `last appointment six months ago`;
- `last review three months ago`;
- `six months since the last review`.

Rejected / not treated as prior encounter:

- bare `since last visit` with no separate prior date or interval;
- `last notification period`;
- treatment/event anchors such as `since dose titration`.

Projection policy trace:

```json
{
  "normalization_issues": [
    "seizure_free_anchor_from_prior_encounter_context",
    "prior_encounter_derived_seizure_free_duration"
  ]
}
```

Route behavior:

```json
{
  "route_families": [
    "rendered_label_supported_but_policy_sensitive"
  ],
  "route_reasons": [
    "seizure-free duration was derived from prior-encounter context"
  ]
}
```

### Validation750 V5 Result

The context V1 candidate-set surface found 8 rows with prior-encounter context:

- `prior_encounter` present: 8;
- `prior_encounter` missing: 742.

The V5 projection/render replay did not recover additional null-rendered rows
relative to V4:

- Rendered rows: 573.
- Null-rendered rows: 177.
- Remaining unresolved since anchors: 19.

However, it did add the intended policy-sensitive trace to one already-rendered
row:

| Row | Rendered label | Trace |
| --- | --- | --- |
| 7785 | `seizure free for 12 month` | `prior_encounter_derived_seizure_free_duration` |

Route/decision impact:

- Routed rows: 49, up from 48.
- New route family count:
  `rendered_label_supported_but_policy_sensitive`: 1.
- VerificationDecision V0 actions: 49 `abstain`.

Interpretation: this is a useful architecture/generalisation component, but not
a row-rescue component on the current V4 unresolved surface. It improves
ownership and route discipline for relative prior-encounter intervals. It also
confirms that the remaining unresolved `since last visit/review` rows generally
lack the source-backed prior date/interval we would need for safe automation.

### New Artifacts

- `experiments/gan2026_validation750_candidate_set_deterministic_context_v1_2026-06-06.*`
- `experiments/gan2026_validation750_candidate_set_v3_nested_dedupe_context_v1_2026-06-06.*`
- `experiments/gan2026_clinical_assessment_projection_render_validation750_gpt41mini_context_repair_v5_2026-06-06.*`
- `experiments/gan2026_clinical_assessment_projection_score_validation750_gpt41mini_context_repair_v5_2026-06-06.*`
- `experiments/gan2026_validation750_verification_route_gpt41mini_context_repair_v5_2026-06-06.*`
- `experiments/gan2026_validation750_verification_decision_gpt41mini_context_repair_v5_2026-06-06.*`

### Tests Run

- `uv run pytest tests/test_gan2026_candidate_set_contract.py tests/test_gan2026_candidate_set_union.py tests/test_gan2026_clinical_assessment_contract.py tests/test_gan2026_clinical_assessment_projection_render.py tests/test_gan2026_clinical_assessment_verification_route.py tests/test_gan2026_clinical_assessment_verification_decision.py`

### Next Recommendation

Do not keep expanding prior-encounter logic for the remaining unresolved rows.
The component has done the clean thing it can do. The next generalisable
component, if we continue this line, should be a separate event-date context
extractor for treatment/surgery/withdrawal/dose-change anchors.
