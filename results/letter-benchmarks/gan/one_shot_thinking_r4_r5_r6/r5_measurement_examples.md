# R5 dev750: examples of the six measurement types

These are actual saved R5 extractions from **synthetic Gan dev750 letters**,
not newly authored fictional fixtures or real-patient annotations. Each complete
finding object below is copied unchanged from a schema-valid original response.
Examples illustrate representation; they are not a reviewed reference, an accuracy
estimate, or evidence that all source details were captured correctly.

## Provenance and selection

- Dataset/split: Gan synthetic development set, dev750 (loader split `validation`).
- Run row policy: all 750 development letters, including `row_ok=False`; this document
  selects six findings for readability and type coverage, not a representative sample
  for estimating performance.
- Condition/version: `r5_rich`, `one_shot_frequency_v2_measurements_r5`.
- Model/runtime: DeepSeek V4.1 Flash, thinking enabled/low, temperature 0,
  24,000-token limit, original 300-second timeout.
- Attempts: original saved responses only; no timeout-rerun substitutions.
- Replay/repair: offline JSON extraction and R5 schema validation; no model calls,
  format repair, semantic repair, or changes to the saved finding fields.
- Scoring: no scores calculated here. The study uses native Gan Purist with Pragmatic
  companion; these examples concern findings rather than the selected answer.
- Local source files: `runs/one_shot_thinking_r4_r5_r6/dev750/requests.jsonl` and
  `runs/one_shot_thinking_r4_r5_r6/dev750/responses.jsonl`. Response line numbers below
  are one-based. Source row identifiers are preserved exactly, not display ordinals.

## Recurring rate: `recurring_rate`

A recurring count of 17 seizures per month. The denominator belongs to the rate; no observation period was extracted.

Source row: `128` · Finding: `f1` · Response line: `6`

Request ID: `11412353e741cdf335f89efff730b7d1823694f2262f7ef45352230df762c7c5`

Source quotation (exact substring checked against the saved request):

> current seizure frequency of 17 per month

Saved finding:

```json
{
  "finding_id": "f1",
  "event": {
    "description": "seizures",
    "grouping": "unspecified",
    "seizure_interpretation": "stated_seizure"
  },
  "measurement": {
    "kind": "recurring_rate",
    "count": {
      "kind": "exact",
      "value": 17,
      "approximate": false
    },
    "denominator": {
      "quantity": {
        "kind": "exact",
        "value": 1,
        "approximate": false
      },
      "unit": "month"
    }
  },
  "temporal_status": "current",
  "observation_period": null,
  "condition": null,
  "evidence": "current seizure frequency of 17 per month"
}
```

## Observed count: `observed_count`

Two witnessed episodes during the past week. This is an observed count with a separate observation period, not an asserted recurring rate.

Source row: `278` · Finding: `f2` · Response line: `60`

Request ID: `2072dd0a8e6faaf3f1d71817647a21f1217b301b06d497954e0d7a0f2afa7f28`

Source quotation (exact substring checked against the saved request):

> including two episodes witnessed by a friend

Saved finding:

```json
{
  "finding_id": "f2",
  "event": {
    "description": "episodes witnessed by a friend",
    "grouping": "one_type",
    "seizure_interpretation": "stated_seizure"
  },
  "measurement": {
    "kind": "observed_count",
    "count": {
      "kind": "exact",
      "value": 2,
      "approximate": false
    }
  },
  "temporal_status": "current",
  "observation_period": {
    "wording": "past week",
    "start": null,
    "end": null,
    "duration": {
      "quantity": {
        "kind": "exact",
        "value": 1,
        "approximate": false
      },
      "unit": "week"
    }
  },
  "condition": null,
  "evidence": "including two episodes witnessed by a friend"
}
```

## Cluster pattern: `cluster_pattern`

Cluster recurrence is every four weeks. R5 represents the within-cluster quantity qualitatively as “multiple”. The source also describes clusters lasting 1–2 days and possible triggers; those details remain in the quotation but are not populated as separate fields here. This illustrates the saved output, not a completeness judgement.

Source row: `190` · Finding: `f1` · Response line: `48`

Request ID: `d5c30d7f1bbd4087597f2060618e1efbd6530b910356132d0fe3ce76d4789f3b`

Source quotation (exact substring checked against the saved request):

> At present he reports clusters of brief absence episodes every 4 weeks, usually over 1–2 days, often precipitated by reduced sleep and academic stress.

Saved finding:

```json
{
  "finding_id": "f1",
  "event": {
    "description": "brief absence episodes",
    "grouping": "one_type",
    "seizure_interpretation": "stated_seizure"
  },
  "measurement": {
    "kind": "cluster_pattern",
    "cadence": {
      "kind": "recurring_rate",
      "count": {
        "kind": "exact",
        "value": 1,
        "approximate": false
      },
      "denominator": {
        "quantity": {
          "kind": "exact",
          "value": 4,
          "approximate": false
        },
        "unit": "week"
      }
    },
    "seizures_per_cluster": {
      "kind": "qualitative",
      "wording": "multiple"
    }
  },
  "temporal_status": "current",
  "observation_period": null,
  "condition": null,
  "evidence": "At present he reports clusters of brief absence episodes every 4 weeks, usually over 1–2 days, often precipitated by reduced sleep and academic stress."
}
```

## Seizure-free interval: `seizure_free_interval`

Seizure freedom is scoped to generalised tonic–clonic seizures since May 2025. The duration is null: the output does not calculate elapsed time from the clinic date.

Source row: `190` · Finding: `f3` · Response line: `48`

Request ID: `d5c30d7f1bbd4087597f2060618e1efbd6530b910356132d0fe3ce76d4789f3b`

Source quotation (exact substring checked against the saved request):

> His last generalised tonic–clonic seizure was in May 2025 after a night of sleep deprivation, and there have been none since.

Saved finding:

```json
{
  "finding_id": "f3",
  "event": {
    "description": "generalised tonic–clonic seizures",
    "grouping": "one_type",
    "seizure_interpretation": "stated_seizure"
  },
  "measurement": {
    "kind": "seizure_free_interval",
    "duration": null,
    "since": {
      "wording": "May 2025",
      "form": "calendar",
      "precision": "month"
    }
  },
  "temporal_status": "current",
  "observation_period": null,
  "condition": null,
  "evidence": "His last generalised tonic–clonic seizure was in May 2025 after a night of sleep deprivation, and there have been none since."
}
```

## Last seizure: `last_seizure`

The last generalised tonic–clonic seizure is dated to May 2025, with calendar form and month precision. This and the preceding example are separate findings from the same sentence.

Source row: `190` · Finding: `f2` · Response line: `48`

Request ID: `d5c30d7f1bbd4087597f2060618e1efbd6530b910356132d0fe3ce76d4789f3b`

Source quotation (exact substring checked against the saved request):

> His last generalised tonic–clonic seizure was in May 2025 after a night of sleep deprivation, and there have been none since.

Saved finding:

```json
{
  "finding_id": "f2",
  "event": {
    "description": "generalised tonic–clonic seizures",
    "grouping": "one_type",
    "seizure_interpretation": "stated_seizure"
  },
  "measurement": {
    "kind": "last_seizure",
    "when": {
      "wording": "May 2025",
      "form": "calendar",
      "precision": "month"
    }
  },
  "temporal_status": "historical",
  "observation_period": null,
  "condition": null,
  "evidence": "His last generalised tonic–clonic seizure was in May 2025 after a night of sleep deprivation, and there have been none since."
}
```

## Qualitative frequency: `qualitative_frequency`

“Most days” remains qualitative wording. The observation period retains March 2025 as its start, without inventing a day or an end date.

Source row: `10` · Finding: `f1` · Response line: `10`

Request ID: `c40572ec6cf15376cbd106fb3f726d5101f46b1237f7796070fd7c508eedb1d1`

Source quotation (exact substring checked against the saved request):

> brief episodes most days

Saved finding:

```json
{
  "finding_id": "f1",
  "event": {
    "description": "brief episodes",
    "grouping": "unspecified",
    "seizure_interpretation": "stated_seizure"
  },
  "measurement": {
    "kind": "qualitative_frequency",
    "wording": "most days"
  },
  "temporal_status": "current",
  "observation_period": {
    "wording": "Since his last review here in March 2025",
    "start": {
      "wording": "March 2025",
      "form": "calendar",
      "precision": "month"
    },
    "end": null,
    "duration": null
  },
  "condition": null,
  "evidence": "brief episodes most days"
}
```

## What these examples show about dates

R5 keeps calendar or relative date wording in `TimePoint` objects. Row 190 uses
`May 2025` both for `last_seizure.when` and `seizure_free_interval.since`.
Row 10 uses `March 2025` in `observation_period.start`. These fields preserve
wording and precision; they are not normalized ISO dates.

The saved input letters for rows 10 and 190 both contain `Clinic Date: 02 October 2025`.
That date is present in the source text but has no dedicated field in the R5 output.
A clinic date is not automatically a separate letter-authorship date. R5 also has
no dedicated date field for an individual seizure other than the last seizure.
The new R7 representation candidate does not change these date fields.
