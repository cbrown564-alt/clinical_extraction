# Gan 2026 Seizure-Frequency Pipeline V1

## Objective

Build a hybrid deterministic-LLM pipeline that exceeds 0.9 purist F1 on Gan 2026 seizure-frequency extraction.

LLM-backed experiments should follow the model policy in
`docs/design/model_strategy.md`: GPT-4.1 mini is the default rapid-iteration
model, Qwen 3.6:35b is reserved for later local strong-reasoning experiments
after a pipeline exceeds 0.8 purist F1, and GPT-5.4 is only planned as a
possible DSPy GEPA teacher model.

## Schema Direction

The first schema sketch was intentionally small. After inspecting real Gan 2026
letters, V1 should use a richer intermediate event schema while keeping the final
Gan-compatible answer simple.

Rationale:

- Frequency statements include point values, ranges, vague `multiple` statements,
  cluster rates, seizure-free intervals, last-event-only statements, and
  no-reference letters.
- Many letters contain multiple seizure types with different frequencies.
- Gan scoring collapses clinically distinct states such as `unknown` and
  `no seizure frequency reference`, so semantic state must be preserved before
  scoring.
- A first implementation is expected to miss or mis-handle some cases; the schema
  should make those failures visible for row-level error analysis.

See `docs/research/gan2026_schema_exploration_10_examples.md` for the
example-driven analysis behind this direction.

## Candidate Event Schema

The event schema should capture source-near clinical facts. It should not require
the LLM to produce every benchmark-normalized value directly.

```text
{
  event_id: str,
  kind: "frequency_rate" |
        "cluster_frequency" |
        "seizure_free" |
        "last_event_only" |
        "unknown_frequency" |
        "no_reference",

  raw_value: str | null,
  applies_to: str | null,

  occurrences_low: float | null,
  occurrences_high: float | null,
  period_low: float | null,
  period_high: float | null,
  period_unit: "day" | "week" | "month" | "year" | null,

  clusters_low: float | null,
  clusters_high: float | null,
  cluster_period_low: float | null,
  cluster_period_high: float | null,
  cluster_period_unit: "day" | "week" | "month" | "year" | null,
  events_per_cluster_low: float | null,
  events_per_cluster_high: float | null,

  seizure_free_duration_low: float | null,
  seizure_free_duration_high: float | null,
  seizure_free_duration_unit: "day" | "week" | "month" | "year" | null,
  last_event_date_text: str | null,

  assertion_status: "asserted" | "negated" | "historical" | "hypothetical" | "unknown",
  temporality: "current" | "recent" | "historical" | "future" | "unclear",
  certainty: "certain" | "uncertain" | "approximate" | "unknown",
  anchor: {
    kind: "letter_date" | "explicit_date" | "relative_date" | "unknown",
    date: date | null,
    raw_text: str | null
  },
  evidence: {
    text: str,
    start_char: int | null,
    end_char: int | null
  }
}
```

Field guidance:

- `applies_to` preserves semiology, such as focal impaired-awareness seizures
  versus generalized tonic-clonic seizures, so the final selector can compare
  competing rates.
- Ordinary frequency rates use `occurrences_*` and `period_*`.
- Cluster frequencies use `clusters_*`, `cluster_period_*`, and
  `events_per_cluster_*`.
- Seizure-free statements use seizure-free duration fields. These should remain
  distinct from ordinary zero-frequency rates.
- Last-event-only statements preserve the event date or date text even when no
  recurring rate can be inferred.
- `unknown_frequency` means seizure-frequency evidence exists but cannot be
  converted into a rate.
- `no_reference` means the letter contains no seizure-frequency evidence.

## Deterministic Normalization Schema

Deterministic normalization should attach benchmark-facing values to candidate
events after extraction:

```text
{
  event_id: str,
  normalized_label: str | null,
  semantic_kind: "frequency" |
                 "seizure_free" |
                 "unknown" |
                 "no_reference" |
                 "unresolved_multiple",
  yearly_bounds: tuple[float, float] | null,
  monthly_frequency: float | null,
  normalization_policy: str,
  repair_applied: bool,
  validation_errors: list[str]
}
```

This layer owns:

- rate conversion to yearly bounds
- Gan monthly midpoint conversion
- cluster expansion under the documented evaluation-script policy
- seizure-free duration threshold checks
- accepted Gan label formatting
- scorer sentinel handling

The LLM should extract clinical candidates; deterministic code should handle
arithmetic, date conversion, label policy, and benchmark formatting where
possible.

## Final Selection Schema

The final schema should remain compact and Gan-compatible, but traceable to the
candidate events:

```text
{
  final_label: str,
  final_kind: "frequency" |
              "seizure_free" |
              "unknown" |
              "no_reference" |
              "unresolved_multiple",
  selected_event_ids: list[str],
  rationale: str,
  evidence: str,
  monthly_frequency: float | null,
  validation_errors: list[str]
}
```

The final selector should explain clinically meaningful decisions, especially:

- selecting the highest current seizure frequency among multiple semiologies
- selecting a recent high-frequency window rather than a long-term average
- preserving `unknown` when a last event is known but no recurring rate is given
- preserving `no_reference` when a letter contains no seizure-frequency evidence
- avoiding unsupported cluster labels when the text only mentions vague
  clustering

## Pipeline Hypothesis

1. DSPy extracts all seizure-frequency events from the note.
2. Deterministic rules normalize frequencies, cluster expressions, and date-derived rates.
3. DSPy clinical reasoner groups or disambiguates events and selects the benchmark answer.
4. Deterministic validation checks schema validity and evidence substring validity.
5. Deterministic repair normalizes accepted-value formatting when clinical interpretation is unchanged.
6. Gan-compatible evaluation reports purist and pragmatic metrics.

The default early runtime model for the DSPy extractor and clinical reasoner is
GPT-4.1 mini. Stronger or local models should be introduced as controlled
model-swap experiments, not while the schema and deterministic substrate are
still moving.

## Deterministic Rule Design

Rules in V1 should be explicit and categorized. The goal is not simply to maximize local score with ever more specific patterns. The goal is to measure which kinds of rules improve performance, where they fail, and which ones are likely to transfer beyond Gan 2026.

Initial categories:

- general date and duration normalization
- seizure-frequency expression normalization
- cluster/event aggregation arithmetic
- current-versus-historical temporal cues
- Gan-specific diary or synthetic-letter phrasing
- benchmark label repair and formatting

Every rule category should be easy to disable in ablations once the baseline works.

## Expected Failure Modes To Track

- Missed current seizure-frequency evidence
- Range parsed as a point value
- `multiple` incorrectly coerced to a numeric count
- Historical frequency selected instead of current frequency
- Seizure-free duration confused with seizure rate
- Last-event-only evidence mislabeled as seizure-free
- No-reference letter mislabeled as unknown frequency
- Lower-frequency semiology selected over higher-frequency semiology
- Vague cluster mention converted into unsupported cluster label
- Cluster frequency multiplied incorrectly
- Cluster count extracted but events per cluster missed
- Implicit cluster interval missed
- Implicit dates converted incorrectly
- Multiple recent events not aggregated correctly
- Uncertain or negated statements treated as asserted
- Final label valid but incompatible with Gan normalization policy
- Evidence citation absent from source note
- Score improves only because Gan-specific wording is overfit
- Rule interaction becomes too complex to explain cleanly
