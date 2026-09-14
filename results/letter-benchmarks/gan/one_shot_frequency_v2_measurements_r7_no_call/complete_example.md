# R7 fictional design example

This example illustrates representation, not benchmark performance. The full JSON fixture includes a placeholder unknown answer and selected_ids solely for schema checks; they are omitted from this design view.

> Clinic Date: 14 September 2026

> Letter Date: 16 September 2026

> She currently reports about three brief staring episodes per week. It remains uncertain whether these are seizures.

> Between 1 June and 31 August 2026, she reported two clusters of tonic-clonic seizures, with three to four seizures in each cluster. The latest cluster occurred on 28 August 2026. Her last tonic-clonic seizure was on that date, and she has had none since.

```json
{
  "document_dates": [
    {
      "role": "clinic",
      "time": "14 September 2026",
      "form": "calendar",
      "evidence": "Clinic Date: 14 September 2026"
    },
    {
      "role": "letter",
      "time": "16 September 2026",
      "form": "calendar",
      "evidence": "Letter Date: 16 September 2026"
    }
  ],
  "findings": [
    {
      "id": "f1",
      "event": {
        "type": "brief staring episodes",
        "scope": "specific",
        "seizure_status": "uncertain"
      },
      "measurement": {
        "type": "rate",
        "count": {
          "type": "number",
          "value": 3
        },
        "per": {
          "type": "number",
          "value": 1,
          "unit": "week"
        },
        "approximate": true
      },
      "timing": "current",
      "evidence": "She currently reports about three brief staring episodes per week. It remains uncertain whether these are seizures."
    },
    {
      "id": "f2",
      "event": {
        "type": "tonic-clonic seizures",
        "scope": "specific",
        "seizure_status": "stated"
      },
      "measurement": {
        "type": "cluster",
        "count": {
          "type": "number",
          "value": 2
        },
        "seizures_per_cluster": {
          "type": "range",
          "lower": 3,
          "upper": 4
        }
      },
      "period": {
        "time": "Between 1 June and 31 August 2026",
        "start": {
          "time": "1 June",
          "form": "calendar"
        },
        "end": {
          "time": "31 August 2026",
          "form": "calendar"
        }
      },
      "timing": "current",
      "evidence": "Between 1 June and 31 August 2026, she reported two clusters of tonic-clonic seizures, with three to four seizures in each cluster."
    },
    {
      "id": "f3",
      "event": {
        "type": "tonic-clonic seizures",
        "scope": "specific",
        "seizure_status": "stated"
      },
      "measurement": {
        "type": "cluster",
        "count": {
          "type": "number",
          "value": 1
        },
        "occurred_at": {
          "time": "28 August 2026",
          "form": "calendar"
        }
      },
      "timing": "current",
      "evidence": "The latest cluster occurred on 28 August 2026."
    },
    {
      "id": "f4",
      "event": {
        "type": "tonic-clonic seizures",
        "scope": "specific",
        "seizure_status": "stated"
      },
      "measurement": {
        "type": "last_seizure",
        "occurred_at": {
          "time": "that date",
          "form": "relative"
        }
      },
      "timing": "current",
      "evidence": "The latest cluster occurred on 28 August 2026. Her last tonic-clonic seizure was on that date, and she has had none since."
    },
    {
      "id": "f5",
      "event": {
        "type": "tonic-clonic seizures",
        "scope": "specific",
        "seizure_status": "stated"
      },
      "measurement": {
        "type": "seizure_free",
        "since": {
          "time": "that date",
          "form": "relative"
        }
      },
      "timing": "current",
      "evidence": "The latest cluster occurred on 28 August 2026. Her last tonic-clonic seizure was on that date, and she has had none since."
    }
  ]
}
```

The dated cluster is part of the period total, not an additional cluster. The schema does not encode that overlap as a link. Relative references such as that date remain unresolved, with their antecedent preserved in evidence. Missing years are not filled in. Approximate defaults to false, range endpoints default to inclusive, and absent optional fields are omitted.
