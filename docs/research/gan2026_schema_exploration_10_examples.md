# Gan 2026 Schema Exploration: 10 Letter Examples

Date: 2026-05-31

## Purpose

This note grounds the V1 seizure-frequency schema in real Gan 2026 letters rather
than abstract schema preferences. The goal is to choose an intermediate
representation that is rich enough to expose clinical reasoning and error modes,
while keeping final Gan-compatible evaluation simple and rigorous.

The exploration uses 10 deliberately mixed rows from
`data/Gan (2026)/synthetic_data_subset_1500.json`: simple rates, ranges, clusters,
seizure-free statements, unknown frequency, no-reference letters, and competing
seizure types.

## Dataset Pressures

The full 1,500-row local surface already shows why a flat event schema is too
thin:

- `937` ordinary frequency rows
- `223` seizure-free rows
- `200` unknown rows
- `86` unresolved `multiple` rows
- `54` no-reference rows
- `151` cluster labels
- `255` range labels
- `277` labels involving `multiple`

The letters also frequently contain clinical distractors:

- `1,194` notes contain multiple seizure or semiology terms.
- `793` notes contain temporal language such as `since`, `last seizure`, or
  `no further events`.

The hard problem is therefore not just parsing `n per unit`; it is extracting
candidate events, preserving the meaning of each candidate, and selecting the
benchmark answer under a documented policy.

## Worked Examples

### Row 441: Simple Current Rate

Gold label: `2 per month`

Evidence: `twice per month`

Clinical reading: the note states current frequency directly: "twice per month
on average over the last three months." There is no current clustering and no
seizure-free conflict.

Schema implication: a simple `frequency_rate` event is enough:

- occurrences: `2`
- period: `1 month`
- temporality: `current`
- certainty: likely `certain` or `approximate`, depending on whether "on average"
  is treated as approximation

### Row 1165: Recent High-Frequency Window

Gold label: `5 to 7 per 3 week`

Evidence: `5 or 7 focal onset seizures in three weeks`

Clinical reading: the patient had a recent three-week period with 5 or 7 focal
seizures, linked to travel anxiety and sleep disruption. Outside that window,
there were no further episodes for six weeks. Gan selects the high-frequency
recent period rather than smoothing across the full follow-up period.

Schema implication: the event should preserve context and temporality. The final
selector needs to explain that it selected a recent high-frequency window, not a
longitudinal average.

### Row 11118: Explicit Cluster Frequency

Gold label: `2 cluster per month, 6 per cluster`

Evidence: `Cluster days twice this month; typically six seizures in 24 h`

Clinical reading: the event has two levels: cluster days per month and seizures
per cluster day. Collapsing this into a single raw value loses the structure
needed for deterministic cluster arithmetic.

Schema implication: cluster frequency needs explicit fields for both cluster
rate and events per cluster.

### Row 10967: Cluster Frequency With Range Size

Gold label: `3 cluster per month, 4 to 5 per cluster`

Evidence: `three nocturnal clusters this month; each ~4 - 5 events`

Clinical reading: this has a definite cluster count and an approximate range for
events per cluster. There are no daytime events competing with this frequency.

Schema implication: ranges are needed inside cluster subfields, not only for
ordinary rates.

### Row 15376: Inferred Cluster Interval

Gold label: `1 cluster per 2 week, 4 to 6 per cluster`

Evidence: `He can sometimes go nearly two week without seizures, but when they
recur he tends to have several in one day, often between 4 and 6`

Clinical reading: the text does not use a tidy `cluster per` phrase. The label is
inferred from an inter-cluster interval and a cluster burden.

Schema implication: a useful first implementation may miss this, and that is
acceptable if the error is visible. We should track "implicit cluster interval"
as an error mode rather than hide it under repair.

### Row 12111: Competing Seizure Types

Gold label: `multiple per week`

Evidence: `focal epileptic spasm occur several times each week, particularly in
the evenings. Generalised convulsions seizures are rare, typically four events
per year`

Clinical reading: two seizure types have different frequencies. Gan selects the
highest current seizure frequency: focal spasms several times weekly, not
generalised convulsions four times yearly.

Schema implication: `applies_to` matters. The event layer should preserve both
candidate rates, and the final selector should record why one was chosen.

### Row 13485: Seizure-Free Despite Diagnostic Ambiguity

Gold label: `seizure free for multiple year`

Evidence: `he has been seizure free for a long duration and has not reported
seizures for over several years`

Clinical reading: the letter also says the patient does not have current
epilepsy and prior events were reclassified as non-epileptic. Gan still treats
the explicit seizure-free statement as the answer.

Schema implication: `seizure_free` should be its own event kind, not merely a
frequency rate of zero. Diagnostic negation and seizure-frequency state must not
be collapsed.

### Row 11254: Last Event Without Rate

Gold label: `unknown`

Evidence: `Last seizure on 31-May`

Clinical reading: clinic date is 01 September 2021. The patient had a last seizure
on 31 May and no further events, so the seizure-free interval is about three
months, below the six-month seizure-free threshold used in these labels. No
recurring rate is stated.

Schema implication: this is not no-reference. It is an event with last-event
evidence but insufficient frequency information. A distinct `last_event_only` or
`unknown_frequency` state is useful for error analysis.

### Row 11434: No Frequency Reference

Gold label: `no seizure frequency reference`

Evidence: author prompt/reference indicates an appointment cancellation letter.

Clinical reading: the letter mentions generalized epilepsy but contains no
seizure count, event timing, seizure-free duration, or current frequency.

Schema implication: `no_reference` must remain separate from `unknown_frequency`,
even though Gan scoring collapses both to the unknown category.

### Row 11948: Highest Rate Among Multiple Semiologies

Gold label: `5 to 6 per week`

Evidence: `focal myoclonic with retained awareness are experienced 5 or 6 times
weekly, sometimes in clusters. Generalised tonic-clonic seizures have been
reported only twice in the past five years`

Clinical reading: the explicit weekly focal myoclonic rate is selected over the
rare generalized tonic-clonic rate. Clusters are mentioned, but without a
well-specified cluster size; the direct weekly rate is the best benchmark-facing
answer.

Schema implication: the selector should favor the highest current usable rate,
but it should not invent cluster detail when the note only says "sometimes in
clusters."

## Proposed V1 Interpretation

The V1 schema should be richer at the intermediate event layer and deliberately
simple at the final benchmark layer.

The extractor should produce source-near candidate events:

- ordinary frequency rates
- cluster frequencies
- seizure-free intervals
- last-event-only evidence
- unknown-frequency statements
- no-reference state when no seizure-frequency evidence exists

The deterministic layer should then handle:

- rate normalization to yearly bounds and Gan monthly midpoint
- cluster multiplication under the documented Gan evaluation policy
- date and duration calculations
- accepted-label formatting
- distinction between semantic states and scorer sentinels

The final selector should produce the Gan-compatible answer plus traceability:

- final label
- final semantic kind
- selected event ids
- selection rationale
- evidence quote

## Expected Early Error Modes

The first implementation should not be expected to solve every case. Its main
value is to produce interpretable failures under correct evaluation.

Important early error modes to track:

- simple rate missed
- range parsed as a point value
- `multiple` incorrectly coerced to a numeric count
- cluster count extracted but events per cluster missed
- implicit cluster interval missed
- events per cluster multiplied incorrectly
- last-event-only evidence mislabeled as seizure-free
- seizure-free duration threshold calculated incorrectly
- no-reference letter mislabeled as unknown frequency
- lower-frequency semiology selected over higher-frequency semiology
- historical or trigger-specific period selected without explanation
- vague cluster mention converted into unsupported cluster label
- evidence quote absent or not a source substring

## Research Consequence

This schema direction supports the project thesis: deterministic rules and LLM
reasoning remain explicit, inspectable, and ablatable. The first implementation
can be imperfect as long as it preserves enough intermediate state to show which
component failed and evaluation remains Gan-compatible.
