# Gan 2026 Direct-Citation Policy Row Tables

Date: 2026-06-01

This is a validation-only policy audit on `gan2026_split_v1`. It is not a
holdout or benchmark result. The tables use direct source quotes from validation
rows and saved structured-output traces from
`experiments/gan2026_llm_structured_validation750_gpt41mini_v05_completion5_2026-06-01.jsonl`.

## Purpose

The next scorer-facing policy change should be justified by row evidence before
it is implemented. These tables separate:

- exact source evidence from the note
- Gan gold label
- raw/source-near model label where available
- proposed scorer-facing normalization
- decision category

## Clean Scorer-Facing Candidates

These families look eligible for clean scorer-facing normalization when the
trace preserves the source-near expression and the normalization preserves the
selected clinical fact.

### Cluster-Name Stripping

| Row | Exact source quote | Gold label | Raw/source-near label | Proposed scorer-facing label | Decision category |
|---:|---|---|---|---|---|
| 190 | he reports clusters of brief absence episodes every 4 weeks, usually over 1–2 days | `1 per 4 week` | `1 cluster per 4 weeks` | `1 per 4 week` | `gold_normalization_policy` |
| 16356 | typically occurring in clusters every 4 days | `1 per 4 day` | `1 cluster per 4 days` | `1 per 4 day` | `gold_normalization_policy` |
| 16394 | Seizures remain relatively stable, typically occurring in clusters every 2 to 4 days. | `1 per 2 to 4 day` | `1 cluster every 2 to 4 days` | `1 per 2 to 4 day` | `gold_normalization_policy` |

Interpretation: Gan consistently drops `cluster` from cadence-only cluster
labels when no within-cluster count is represented. Keep cluster semantics in
the trace; drop the word only for scorer-facing labels.

### Vague Weekday Or Weekly Cadence

| Row | Exact source quote | Gold label | Raw/source-near label | Proposed scorer-facing label | Decision category |
|---:|---|---|---|---|---|
| 744 | brief absences occurring on most weekdays, often clustering around late afternoon | `multiple per week` | `most weekdays` | `multiple per week` | `gold_normalization_policy` |
| 3988 | The patient keeps a seizure diary that records these events as occurring on most weeks, with occasional weeks free | `multiple per week` | `multiple per week` | `multiple per week` | `benchmark_format` |
| 7409 | over the past six months she experiences focal aware seizures most weeks | `unknown` | `multiple per week` | unresolved | `ambiguous_or_debatable` |

Interpretation: `most weekdays` is reasonably mapped to `multiple per week` for
Gan scoring, but `most weeks` is not automatically equivalent. Row `7409`
shows the boundary: a weekly-ish phrase can still be gold-`unknown` when the
annotation does not commit to a countable frequency.

### Gan-Specific Bimonthly

| Row | Exact source quote | Gold label | Raw/source-near label | Proposed scorer-facing label | Decision category |
|---:|---|---|---|---|---|
| 959 | She notes the events are occurring bimonthly on average, though some months she has none and then two in quick succession. | `1 per 2 month` | `2 per month` | `1 per 2 month` | `gold_normalization_policy` |
| 960 | ongoing events occurring with bimonthly seizures | `1 per 2 month` | `2 to 3 per month` | `1 per 2 month` | `gold_normalization_policy` |
| 987 | bimonthly seizures | `1 per 2 month` | `2 per month` | `1 per 2 month` | `gold_normalization_policy` |

Interpretation: on validation, bare `bimonthly` maps consistently to
`1 per 2 month`. This should remain Gan-specific and must be overridden by
explicit contradictory wording such as `twice per month`.

### Vague Quantity With Explicit Denominator

| Row | Exact source quote | Gold label | Raw/source-near label | Proposed scorer-facing label | Decision category |
|---:|---|---|---|---|---|
| 1707 | a brief cluster of events occurring on multiple days within the past week | `multiple per week` | `multiple per week` | `multiple per week` | `benchmark_format` |
| 1687 | several focal seizures last week characterised by brief behavioural arrest, loss of awareness, and post-event confusion | `multiple per week` | `several per week` | `multiple per week` | `gold_normalization_policy` |
| 12111 | focal epileptic spasm occur several times each week, particularly in the evenings | `multiple per week` | `multiple per week` | `multiple per week` | `benchmark_format` |
| 12130 | focal sensory occur several times each week, particularly in the evenings | `multiple per week` | `multiple per week` | `multiple per week` | `benchmark_format` |
| 280 | In the 24 hours prior to clinic he experienced multiple seizures in past day | `multiple per day` | `multiple per day` | `multiple per day` | `benchmark_format` |

Interpretation: vague count words are clean only when the denominator is already
explicit and the coarse class is preserved. They should not introduce cluster
structure or arithmetic.

### Period Dialect And Shorthand

| Row | Exact source quote | Gold label | Raw/source-near label | Proposed scorer-facing label | Decision category |
|---:|---|---|---|---|---|
| 531 | Current estimated seizure frequency is 12 to 30 per quarter | `12 to 30 per 3 month` | `12 to 30 per quarter` | `12 to 30 per 3 month` | `benchmark_format` |
| 4110 | He reports continuing episodes occurring at a frequency of q1 - 2d | `1 per 1 to 2 day` | `1 to 2 per day` | `1 per 1 to 2 day` | `gold_normalization_policy` |
| 3949 | sz Xfour/wk on average over the last 8 weeks | `4 per week` | `4 per week` | `4 per week` | `benchmark_format` |
| 3827 | Recently, the pattern has intensified to an average of sz X7/mo | `7 per month` | `7 per month` | `7 per month` | `benchmark_format` |

Interpretation: period aliases and terse seizure-frequency shorthand are
scorer-format issues when count, period, and event structure are preserved.
The `q1 - 2d` row needs a narrow parser because `1 to 2 per day` would be the
wrong clinical reading.

### Cluster Syntax Grammar

| Row | Exact source quote | Gold label | Raw/source-near label | Proposed scorer-facing label | Decision category |
|---:|---|---|---|---|---|
| 11118 | "Cluster days twice this month; typically six seizures in 24 h." | `2 cluster per month, 6 per cluster` | `2 cluster days per month, 6 seizures per cluster day` | `2 cluster per month, 6 per cluster` | `benchmark_format` |
| 10894 | weekly clusters, usually four events within ~2 h | `1 cluster per week, 4 per cluster` | `weekly clusters` | `1 cluster per week, 4 per cluster` | `gold_normalization_policy` |

Interpretation: cluster syntax can be clean when both cluster cadence and
within-cluster load are already present in the selected source evidence. Row
`10894` is borderline because the raw label omits the within-cluster count even
though the selected evidence contains it.

## Named Deterministic Module Candidates

These families change epistemic status, compute new labels, classify evidence
state, or select between competing clinical facts. They should remain outside
clean scorer-facing normalization and require named ablations before claims.

### Upper-Bound Phrasing

| Row | Exact source quote | Gold label | Raw/source-near label | Module output if enabled | Decision category |
|---:|---|---|---|---|---|
| 409 | Over the past five months on the present regimen, events have reduced to ≤ once per month, typically brief focal impaired awareness episodes without generalisation | `1 per month` | `1 per month or less` | `1 per month` | `clinical_inference` |
| 10 | On the accommodation logs, the observed frequency is noted as ≤ four per day, with variable clustering | `4 per day` | `up to 4 per day` | `4 per day` | `clinical_inference` |
| 3623 | Over the past three months, he and his partner report clusters of events with variable frequency: on steadier stretches he may go a week without any, while during flares he experiences multiple events, with a reported frequency of up to seven in bad weeks. | `7 per week` | `multiple per week` | `7 per week` | `clinical_inference` |

Interpretation: converting a ceiling into a point estimate changes uncertainty.
This is useful for Gan alignment but should be a named upper-bound module.

### Seizure-Free Or No-Event Selection

| Row | Exact source quote | Gold label | Raw/source-near label | Module output if enabled | Decision category |
|---:|---|---|---|---|---|
| 12584 | Weekly absences persist | `1 per week` | `multiple per week` | `1 per week` | `clinical_inference` |
| 12548 | He also has daily drop attacks | `1 per day` | `daily` | `1 per day` | `benchmark_format` after selection |
| 3048 | Importantly, there have been No events for 16 months. | `seizure free for 16 month` | `seizure free for 16 months` | `seizure free for 16 month` | `benchmark_format` after selection |

Interpretation: grammar repair after a seizure-free or daily fact is already
selected can be clean. Choosing between persistent seizure types and no-event
phrasing is a temporal-selection module.

### Diary Or Calendar Arithmetic

| Row | Exact source quote | Gold label | Raw/source-near label | Module output if enabled | Decision category |
|---:|---|---|---|---|---|
| 9496 | Focal seizure: 2019: Aug x0, Sep x0, Oct x1, Nov x0, Dec x1. 2020: Jan x0, Feb x2, Mar x0, Apr x1, May x0, Jun x1, Jul x0 | `6 per 12 month` | `low-frequency` | `6 per 12 month` | `clinical_inference` |
| 16162 | This month, she has had six convulsions; 0 were in December and 5 in November | `11 per 3 month` | `6 per month` | `11 per 3 month` | `clinical_inference` |
| 1922 | Since her last review three months ago, she describes two drop attacks and five convulsions in the past three months. | `7 per 3 month` | `2 to 3 per month` | `7 per 3 month` | `clinical_inference` |

Interpretation: summing across months, semiologies, or diary cells is not
formatting. It belongs in a named arithmetic module with ablation.

### Unknown Versus No-Reference

| Row | Exact source quote | Gold label | Raw/source-near label | Module output if enabled | Decision category |
|---:|---|---|---|---|---|
| 10147 | Recurrent seizures with variable semiology and no consistent triggers identified. Cluster frequency uncertain. | `unknown` | `unknown` | `unknown` | `benchmark_format` |
| 11254 | Last seizure on 31-May | `unknown` | `seizure free for 3 months` | `unknown` | `clinical_inference` |
| 11434 | Create a reasonable NHS letter confirming cancellation of an epilepsy clinic appointment | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `benchmark_format` |

Interpretation: literal `unknown` and true no-reference administrative letters
can be clean. Reclassifying last-event-only or no-event-since statements as
unknown is a named evidence-state or temporal module.

### Cluster Arithmetic Or Reconstruction

| Row | Exact source quote | Gold label | Raw/source-near label | Module output if enabled | Decision category |
|---:|---|---|---|---|---|
| 3224 | Monthly clusters, typically 6 to 7 seizures over 24 h. | `1 cluster per month, 6 to 7 per cluster` | `6 to 7 per month` | `1 cluster per month, 6 to 7 per cluster` | `clinical_inference` |

Interpretation: reconstructing cluster structure from a plain model label is
not clean scorer-facing normalization even when the selected evidence contains
the needed details.

### Last-Event-Only Elapsed Interval

| Row | Exact source quote | Gold label | Raw/source-near label | Module output if enabled | Decision category |
|---:|---|---|---|---|---|
| 11254 | Last seizure on 31-May | `unknown` | `seizure free for 3 months` | `unknown` | `clinical_inference` |
| 14040 | he has had multiple drop attacks, the latest one on 05/Apr | `unknown` | `unknown` | `unknown` | `benchmark_format` |

Interpretation: a last-event date without an explicit seizure-free duration or
count/window should not be converted into a seizure-free interval by the clean
path.

## Decision

Use these tables as the gate for the next implementation step. The clean
scorer-facing policy may be extended only for the clean families above, with
tests that prove source-near traces are preserved. Upper-bound conversion,
temporal selection, diary arithmetic, evidence-state reclassification, and
cluster reconstruction should be named deterministic modules with ablations
before they are used in LLM-first claim language.
