# Gan 2026 Seizure-Frequency Pipeline V1

## Objective

Build a hybrid deterministic-LLM pipeline that exceeds 0.9 purist F1 on Gan 2026 seizure-frequency extraction.

## Initial Schemas

Event schema:

```text
{
  seizure_event: {
    raw_value: str,
    evidence: str,
    assertion_status: str,
    temporality: str,
    uncertainty: str,
    normalized_value: str | null,
    anchor_date: date | null
  }
}
```

Final schema:

```text
{
  final_value: str,
  rationale: str,
  evidence: str
}
```

## Pipeline Hypothesis

1. DSPy extracts all seizure-frequency events from the note.
2. Deterministic rules normalize frequencies, cluster expressions, and date-derived rates.
3. DSPy clinical reasoner groups or disambiguates events and selects the benchmark answer.
4. Deterministic validation checks schema validity and evidence substring validity.
5. Deterministic repair normalizes accepted-value formatting when clinical interpretation is unchanged.
6. Gan-compatible evaluation reports purist and pragmatic metrics.

## Expected Failure Modes To Track

- Missed current seizure-frequency evidence
- Historical frequency selected instead of current frequency
- Seizure-free duration confused with seizure rate
- Cluster frequency multiplied incorrectly
- Implicit dates converted incorrectly
- Multiple recent events not aggregated correctly
- Uncertain or negated statements treated as asserted
- Final label valid but incompatible with Gan normalization policy
- Evidence citation absent from source note

