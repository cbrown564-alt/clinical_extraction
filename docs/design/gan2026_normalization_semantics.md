# Gan 2026 Normalization Semantics

## Purpose

Gan 2026 labels need two representations:

- a clinical/semantic representation that preserves what the source label means
- a Gan-compatible scoring representation that matches the author evaluation script

The project keeps these separate because the scorer uses sentinel values that are not
clinically meaningful. In particular, both `unknown` and `no seizure frequency reference`
score as `1000.0`, but they are different evidence states.

## Conversion Layers

### Raw Label

The raw label is the source string from the Gan JSON, for example:

```text
unknown
no seizure frequency reference
2 cluster per month, 6 per cluster
seizure free for multiple month
```

Raw labels are preserved unchanged in each record's `raw` field and exposed as
`gold_label`.

### Light Normalization

`normalize_frequency_label()` performs only conservative text cleanup:

- trim leading/trailing whitespace
- lowercase
- collapse repeated whitespace

This step should not change clinical meaning.

### Semantic Conversion

`label_to_frequency_record()` converts a label into a `FrequencyLabelRecord` with:

- `raw_label`: original label text
- `normalized_label`: conservative normalized text
- `kind`: semantic state
- `yearly_bounds`: lower/upper yearly numeric bounds when meaningful
- `monthly_frequency`: Gan scorer-facing numeric value

The semantic state is represented by `FrequencyLabelKind`:

```text
frequency
seizure_free
unknown
no_reference
unresolved_multiple
```

This keeps clinically different states separate before scoring collapse.

## Scoring Collapse

Gan scoring consumes numeric monthly values. The current project policy follows the author
evaluation script:

- ordinary frequency labels convert to yearly bounds, then midpoint per month
- seizure-free labels convert to `0.0`
- `unknown` converts to `1000.0`
- `no seizure frequency reference` converts to `1000.0`
- unresolved multiple/unknown cluster cases convert to `1000.0`

The value `1000.0` is an evaluator sentinel, not a clinical frequency.

## Cluster Policy

The author scripts contain two cluster interpretations:

- CSV-preparation parser: drops the trailing `per cluster` detail
- evaluation script: multiplies cluster count by seizures per cluster

This project uses the evaluation-script policy for scoring. For example:

```text
2 cluster per month, 6 per cluster
```

is converted as `12 per month`, not `2 per month`.

This is more clinically plausible for a total seizure-frequency target, but results should
state that they use the evaluation-script cluster interpretation.

## Prediction Repair

`repair_prediction_label()` repairs common free-form model outputs into allowed Gan label
formats before parsing. Examples:

```text
twice weekly -> 2 per week
3-5/mo -> 3 to 5 per month
seizure-free since 2020 -> seizure free for multiple year
2 clusters per month 3 per cluster -> 2 cluster per month, 3 per cluster
2 per 0 month -> unknown
```

Prediction repair is benchmark-formatting behavior. It should be measured in experiments
because heavy repair can hide model-output ambiguity.

## Clinical Validity

Clinically valid aspects:

- `unknown` and `no seizure frequency reference` remain distinct evidence states.
- seizure-free labels are represented as zero current frequency for Gan scoring.
- ranges retain lower and upper bounds before midpoint collapse.
- cluster labels can preserve both cluster frequency and seizures per cluster before total-rate conversion.

Clinical limitations:

- monthly midpoint values are scoring conveniences, not exact clinical facts.
- seizure-free duration is mostly lost after conversion to `0.0`.
- vague `multiple` repairs are benchmark-specific heuristics, not clinically grounded counts.
- `1000.0` should never be interpreted as a real seizure frequency.
- repaired prediction labels should be reported separately from direct model outputs in paper-facing analysis.

## Logical Contract

Downstream code should treat these as separate concepts:

- semantic state: `FrequencyLabelKind`
- numeric scoring value: `monthly_frequency`
- evaluation category: Purist or Pragmatic class after numeric mapping

Do not infer clinical meaning from the scorer sentinel alone. If a report needs clinical
interpretability, use `gold_label_kind`, `gold_normalized_label`, and `gold_yearly_bounds`
alongside `gold_monthly_frequency`.
