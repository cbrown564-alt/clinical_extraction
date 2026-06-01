# Gan 2026 Gold Normalization Policy Question

Date: 2026-06-01

## Core Question

Can we discern the normalization rules the Gan 2026 authors used when converting
clinical seizure-frequency language into gold labels, and are those rules
consistent enough that we should reproduce them for scorer-facing evaluation?

This is now a first-class research question, not a minor parsing detail. The
project needs to separate three things:

- the source-near clinical fact extracted from the note
- the benchmark-facing label needed to match Gan gold labels
- the clinical/research claim we make about the system

If the gold label applies a simple, consistent scorer convention, reproducing
that convention is not corrupting the clinical semantics. It is aligning the
evaluation layer with the benchmark. If the convention is inconsistent or
clinically debatable, we should preserve traces, report the ambiguity, and avoid
overstating exact-label correctness.

## Working Principle

Maintain rich extraction traces and source-near labels, then apply an explicit
gold-normalization policy only at the scorer-facing layer. Each policy rule
should be justified with direct row evidence:

1. Quote the exact source evidence.
2. Compare gold label and predicted/source-near label.
3. Decide whether the gold transformation is a benchmark-format convention, a
   clinically reasonable inference, or an inconsistent/debatable annotation.
4. Check whether similar rows are handled consistently before implementing or
   claiming the rule.

## Illustrative Examples

### Cluster Name Stripping

Row `190`

- Evidence: "he reports clusters of brief absence episodes every 4 weeks,
  usually over 1-2 days"
- Gold label: `1 per 4 week`
- Source-near predicted label: `1 cluster per 4 week`

This looks like a simple scorer-facing convention. The gold label strips the
word `cluster` while preserving the cadence. Removing `cluster` for scoring does
not change the cadence or pretend that the clinical events were not clustered;
it aligns the benchmark label with the authors' chosen representation.

Validation sniff:

- `clusters every 4 days` -> gold `1 per 4 day`
- `clusters every 2 to 4 days` -> gold `1 per 2 to 4 day`

Provisional decision: likely `benchmark_format` or `gan2026_specific` scoring
normalization, provided the trace keeps the original cluster semantics.

### Vague Weekday Cadence

Row `744`

- Evidence: "brief absences occurring on most weekdays, often clustering around
  late afternoon"
- Gold label: `multiple per week`
- Source-near predicted label: `most weekdays`

This may be a reasonable normalization, but it is less obviously mechanical than
cluster-name stripping. `Most weekdays` implies recurring events on several days
per week, but it also carries a natural-language ambiguity about whether the
frequency is per day, per week, or clustered on affected days. In the validation
split, this exact phrase appears once.

Provisional decision: do not silently fold this into strict format repair. Audit
related vague-cadence phrases before deciding whether to implement a named
scoring policy such as `vague_weekday_cadence_to_multiple_per_week`.

### Ambiguous Bimonthly

Rows `959`, `960`, and `987`

- Row `959` evidence: "events are occurring bimonthly on average, though some
  months she has none and then two in quick succession"
- Row `959` gold label: `1 per 2 month`
- Row `959` source-near predicted label in the clean attribution replay:
  `2 per month`

`Bimonthly` is famously ambiguous: it can mean twice per month or once every two
months. The validation split has three `bimonthly` hits and all three gold labels
are `1 per 2 month`, which suggests a consistent Gan convention on this surface.

Provisional decision: likely implementable as a named scorer-facing policy after
checking train/validation consistency and any contradictory phrasing.

## Categories To Audit

Use this taxonomy while working through gold-normalization questions:

- `benchmark_format`: label grammar and scorer syntax that preserve the selected
  clinical fact, such as plural units or accepted period names
- `gold_normalization_policy`: transformations that match Gan's annotation
  convention while preserving source-near traces, such as cluster-name stripping
  if consistently applied
- `clinical_inference`: transformations requiring clinical interpretation beyond
  the literal selected label
- `ambiguous_or_debatable`: cases where reasonable annotators may disagree, such
  as vague cadence or ambiguous terms
- `inconsistent_gold_policy`: cases where similar source phrasing maps to
  different gold-label logic

## Audit Plan

1. Build a validation-only inventory of candidate normalization families:
   cluster cadence, vague weekday cadence, vague quantity words, bimonthly,
   less-than/upper-bound phrasing, seizure-free/no-event statements, and diary
   arithmetic.
2. For each family, create a row table with source row, exact quote, gold label,
   source-near predicted label, proposed scorer-facing normalized label, and
   decision category.
3. Check consistency within validation before touching train or test. Use train
   only if a future optimizer or policy-learning experiment explicitly requires
   it. Do not inspect test-row failures.
4. Decide whether each family should be:
   - allowed in clean scorer-facing normalization with trace preservation
   - promoted as a named deterministic module with ablation
   - left unresolved and reported as annotation ambiguity
5. Record every adopted rule as a named policy with examples and tests.

## Paper-Framing Implication

If Gan normalization rules are mostly consistent, we can report a benchmark
alignment layer that preserves clinical traces while matching the original
authors' scoring choices. If the rules are inconsistent or materially
debatable, that is also a publishable finding: exact-label agreement is partly
limited by annotation-policy ambiguity, and the system should report both
source-near extraction quality and benchmark-label agreement.
