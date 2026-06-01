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

## Policy Decisions From 2026-06-01 Review

The following decisions were made from validation-only row inspection. They are
development-surface policy decisions, not locked-test findings.

### Clean LLM-First Scorer-Facing Normalization

These transformations are eligible for the clean LLM-first scorer-facing path
when the source-near trace preserves the original expression and the
normalization preserves the selected clinical fact.

| Family | Clean scorer-facing policy | Representative validation rows |
|---|---|---|
| Cluster-name stripping | If evidence states recurring cluster cadence but no usable within-cluster event count, and Gan gold represents the cadence as a plain rate, drop `cluster` only in the scorer-facing label. | `190`: clusters every 4 weeks -> `1 per 4 week`; `16356`: clusters every 4 days -> `1 per 4 day`; `16394`: clusters every 2 to 4 days -> `1 per 2 to 4 day` |
| Vague weekday cadence | Map multi-day weekday language such as `most weekdays` to Gan's coarse `multiple per week`; do not infer daily or within-day multiplicity. | `744`: most weekdays -> `multiple per week` |
| Gan-specific `bimonthly` | Map bare `bimonthly` / `bi-monthly` to `1 per 2 month` for Gan scorer-facing normalization; contradictory explicit wording overrides the bare term. | `959`, `960`, `987`: bimonthly -> `1 per 2 month` |
| Vague quantity with explicit denominator | Map vague count words to Gan coarse labels only when the phrase already supplies the denominator and preserves the same coarse class. | `1707`/`1687`: several last week -> `multiple per week`; `12111`/`12130`: several times each week -> `multiple per week`; `280`: multiple in past day -> `multiple per day` |
| Period dialect and shorthand | Expand period names, abbreviations, and terse seizure-frequency shorthand into Gan syntax when count, period, and event structure are preserved. | `531`: per quarter -> per 3 month; `4110`: q1-2d -> `1 per 1 to 2 day`; `3949`: Xfour/wk -> `4 per week`; `3827`: X7/mo -> `7 per month` |
| Cluster syntax grammar | Normalize source-near cluster primitives into Gan cluster syntax when cadence and per-cluster load are preserved. | `11118`: 2 cluster days/month, six in 24 h -> `2 cluster per month, 6 per cluster`; `10894`: weekly clusters, four events -> `1 cluster per week, 4 per cluster` |
| Single already-totaled count/window | Rephrase a single selected total count and explicit window into Gan syntax. | `7 in past 3 months`-style source-near facts may become `7 per 3 month` without arithmetic if already totaled in the selected fact. |

### Named Deterministic Modules

These transformations are not clean scorer-facing normalization because they
change epistemic status, compute a new label, classify evidence state, or select
among competing temporal/clinical facts. They may still be useful, but they need
separate naming, tests, ablation, and claim language.

| Family | Decision | Representative validation rows |
|---|---|---|
| Upper-bound phrasing | Named upper-bound module: converting a ceiling such as `up to 4 per day` or `<= once per month` into a point estimate changes epistemic status. | `409`: <= once per month -> `1 per month`; `10`: <= four per day -> `4 per day`; `3623`: up to seven in bad weeks -> `7 per week` |
| Seizure-free/no-event final selection | Named temporal-selection module except for simple spelling/duration grammar after seizure-free has already been selected. | `12584`: weekly absences persist despite no events since last visit -> `1 per week`; `12548`: daily drop attacks despite no events since review -> `1 per day`; `3048`: no events for 16 months -> seizure-free grammar only if already selected |
| Diary/calendar arithmetic | Named arithmetic module when summing counts, constructing ranges, inferring denominators, aggregating semiologies, or calculating month spans. | `9496`: monthly cells -> `6 per 12 month`; `16162`: 6 + 0 + 5 -> `11 per 3 month`; `1922`: two drop attacks plus five convulsions -> `7 per 3 month` |
| Unknown vs no-reference classification | Named evidence-state module except for literal grammar. Preserve `unknown` and `no seizure frequency reference` as distinct semantic states even though Gan scoring collapses both numerically. | `10147`: cluster frequency uncertain -> `unknown`; `11254`: last seizure date only -> `unknown`; `11434`: administrative cancellation letter -> no-reference |
| Cluster arithmetic/reconstruction | Named cluster module for multiplication, reconstruction from evidence, unresolved `multiple per cluster` scoring, or plain-total conversion. | `2 cluster per month, 6 per cluster` -> `12 per month`; `3224`: plain `6 to 7 per month` repaired to cluster syntax is reconstruction |
| Last-event-only elapsed interval | Named temporal module; last-event-only statements stay out of the clean path unless the selected fact explicitly states a seizure-free duration or an explicit count/window. | `11254`: last seizure on 31-May -> `unknown`; `14040`: latest one on 05/Apr but unable to quantify -> `unknown`; `3048`: no events for 16 months -> clean only after seizure-free selection |

### Explicit Boundary Cases

- `several focal seizures last month` is clean only if it maps to
  `multiple per month`; converting it to
  `multiple cluster per month, multiple per cluster` is not clean because it
  introduces cluster structure.
- `monthly clusters` may be clean cluster grammar if the selected source-near
  fact is already cluster-structured; it is not license to infer a per-cluster
  count.
- `yearly`, `monthly`, `weekly`, or shorthand expressions in medication,
  rescue-plan, post-ictal-duration, or administrative contexts must be ignored.
- Contradictory explicit wording overrides a bare normalization convention, for
  example `bimonthly, twice per month` should not become `1 per 2 month`.

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
