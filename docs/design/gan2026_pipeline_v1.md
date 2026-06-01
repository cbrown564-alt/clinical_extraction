# Gan 2026 Seizure-Frequency Pipeline V1

## Objective

Build an LLM-first Gan 2026 seizure-frequency extraction pipeline that reaches
at least 0.9000 Purist F1 while using deterministic code only for validation,
evidence checks, arithmetic, Gan-compatible normalization, benchmark-format
repair, and scoring.

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

1. DSPy extracts seizure-frequency facts from the note without deterministic V1
   candidates in the prompt.
2. DSPy clinical reasoning selects the prediction-bearing interpretation.
3. Deterministic code validates schema validity and evidence substring validity.
4. Deterministic code normalizes frequencies, cluster expressions, date-derived
   rates, and accepted-value formatting when clinical interpretation is unchanged.
5. Gan-compatible evaluation reports purist and pragmatic metrics.

The frozen deterministic V1 rule stack remains a comparator and diagnostic
source. It should not be the first-stage candidate generator for the LLM-first
pipeline.

The default early runtime model for the DSPy extractor and clinical reasoner is
GPT-4.1 mini. Stronger or local models should be introduced as controlled
model-swap experiments, not while the schema and deterministic substrate are
still moving.

## Validation Escalation

LLM/DSPy runs should not default to the full 750-row validation split. Use the
standard validation ladder from `docs/design/gan2026_split_protocol.md`:

1. 25 validation rows for smoke tests after prompt/schema/code changes.
2. 50 validation rows for meaningful signal once the output contract is stable.
3. 250 validation rows after a decision gate when the result will decide whether
   to promote, revise, or reject the candidate.

Full 750-row validation runs are rare and should be reserved for stable
candidates or paper-facing comparisons where a 250-row slice is insufficient.
The experiment artifact must state why the full validation surface is necessary.
If a full run is needed, prefer raw-output reuse and checkpointing rather than
duplicating already-cached model calls.

## Shared LLM CLI Runner

Gan LLM/DSPy pipeline CLIs should bind into the general runner in
`src/clinical_extraction/tasks/seizure_frequency/gan2026/llm_pipeline_cli.py`.
That module is not owned by the direct LLM-first implementation or by the staged
structured extractor. It owns cross-pipeline concerns that should stay
consistent across experiments:

- split loading and optional validation-prefix limits
- artifact-level raw-output reuse
- DSPy cache enable/disable control
- progress and checkpoint emission, defaulting to every 10 processed rows
- recording rare full-validation escalation reasons

Each concrete LLM pipeline should keep a thin `*_cli.py` binding that supplies a
`GanLlmPipelineCliSpec` with its `run_split`, JSONL writer, report writer, default
artifact paths, and raw-output reuse loader. This keeps new extractors, DSPy
reasoners, and future hybrid architectures comparable without copying CLI
behavior.

## Shared Repair Boundaries

Use `schema_repair.py` for model-output shape repair: JSON payload aliases,
field aliases, selection wrappers, and schema compatibility for structured model
responses.

Use `normalize.py` for Gan-facing label repair: allowed label strings, frequency
and date arithmetic, cluster expansion, selected-evidence benchmark formatting,
and scorer-compatible sentinel handling. Pipelines may use LLM-extracted events
for arithmetic repair, but that repair should remain bounded to extracted or
selected evidence rather than introducing deterministic V1 candidates.

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
