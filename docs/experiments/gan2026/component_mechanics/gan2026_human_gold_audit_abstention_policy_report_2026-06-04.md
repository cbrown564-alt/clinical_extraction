# Gan 2026 Human Gold Audit And Abstention Policy Report

This is a validation-development qualitative report from the human Gold Audit
worklist in the Observatory. It interprets manual review decisions over the
validation750 gold/reference ambiguity inventory and turns them into an
abstention and human-review policy direction.

It does not change scorer policy, gold labels, prompts, deterministic rules,
projection policy, locked-test behavior, or benchmark-comparable claims.

## Answer

The human audit supports an explicit abstention and human-review policy. The
reviewed rows show that some residual Gan 2026 seizure-frequency disagreements
are not ordinary extraction failures. They are often subjective, convention
dependent, or internally contradictory at the level of the note/reference/gold
contract. This is especially true for `unknown`, drop attacks, trigger-only
frequencies, last-event-only evidence, cluster semantics, and "since X" windows.

The practical consequence is that future evaluation should report both:

- accuracy on rows where the system makes a prediction; and
- coverage, abstention rate, human-review rate, and over-abstention rate.

Selective accuracy without coverage accounting would be misleading. A model can
cheat by abstaining on all difficult rows and scoring only easy cases. Abstention
is still necessary, but it must be predeclared, bounded, and audited.

## Evidence Base

Artifacts:

- Human decisions: `experiments/gold_audit_decisions.jsonl`
- Source worklist:
  `experiments/gan2026_validation750_gold_reference_ambiguity_review_2026-06-04.csv`
- Related RQ10 report:
  ``
- Related RQ9 predeclaration:
  ``

The decision log contains repeated submissions for some rows. Deduplicating by
latest `(split, source_row_index)` yields 140 unique reviewed validation rows.
There were 196 raw submit lines and 140 unique latest reviewed rows. One row
changed human class after resubmission: source row 6180 changed from `correct` to
`ambiguous`.

## Human Judgment Summary

| Human class | Rows | Rate |
| --- | ---: | ---: |
| `correct` | 94 | 67.1% |
| `ambiguous` | 37 | 26.4% |
| `wrong` | 9 | 6.4% |
| non-correct (`ambiguous` or `wrong`) | 46 | 32.9% |

The first 100 reviewed rows were all originally flagged `ambiguous` by the CSV
heuristic. The next 40 included 11 heuristic-`clear` rows; all 11 were judged
`correct`. This is encouraging for the `clear` bucket, but it is still a small
sample and should be treated as a safety check rather than proof that all clear
rows are safe.

| Review tranche | Reviewed | Non-correct | Non-correct rate | Heuristic clear rows |
| --- | ---: | ---: | ---: | ---: |
| First 100 | 100 | 39 | 39.0% | 0 |
| Next 40 | 40 | 7 | 17.5% | 11 |
| All reviewed | 140 | 46 | 32.9% | 11 |

## Difference From The CSV Heuristic

The original CSV heuristic marked 506 of the 750 validation rows as
`ambiguous`, and 244 as `clear`.

Among the 140 reviewed rows:

| CSV heuristic | Human correct | Human ambiguous | Human wrong |
| --- | ---: | ---: | ---: |
| `ambiguous` | 83 | 37 | 9 |
| `clear` | 11 | 0 | 0 |

For the reviewed heuristic-`ambiguous` rows, precision for "needs review"
(`ambiguous` or `wrong`) is 46/129 = 35.7%. The heuristic is therefore useful as
a high-recall worklist, but it over-flags substantially.

The heuristic-`clear` sample is small but clean: 11/11 reviewed clear rows were
human-`correct`. More clear-row sampling would improve confidence, but the
current audit is already enough to stop treating 100% exact-label accuracy as a
reasonable expectation on the full worklist.

## Gold-Kind Risk

| Gold label kind | Reviewed | Non-correct | Rate |
| --- | ---: | ---: | ---: |
| `unknown` | 28 | 18 | 64.3% |
| `unresolved_multiple` | 33 | 12 | 36.4% |
| `no_reference` | 4 | 1 | 25.0% |
| `frequency` | 58 | 12 | 20.7% |
| `seizure_free` | 17 | 3 | 17.6% |

The `unknown` bucket is the main instability zone. It contains true
unquantified-frequency cases, but also cases where a clinician or benchmark
author could defensibly render a frequency, seizure-free interval, or review
route instead.

## High-Yield Ambiguity Families

| Heuristic reason | Reviewed | Non-correct | Rate |
| --- | ---: | ---: | ---: |
| `last_event_or_seizure_free_boundary` | 3 | 3 | 100.0% |
| `unknown_gold_boundary` | 28 | 18 | 64.3% |
| `conditional_or_trigger_bound` | 5 | 3 | 60.0% |
| `uncertainty_language` | 12 | 5 | 41.7% |
| `calendar_or_diary_arithmetic` | 27 | 11 | 40.7% |
| `cluster_or_per_cluster_convention` | 28 | 11 | 39.3% |
| `unresolved_multiple_or_vague_count` | 33 | 12 | 36.4% |
| `vague_count_or_period` | 75 | 25 | 33.3% |
| `range_or_upper_bound` | 21 | 5 | 23.8% |
| `reference_does_not_explicitly_support_frequency` | 25 | 5 | 20.0% |
| `(none)` | 11 | 0 | 0.0% |

The low-yield `reference_does_not_explicitly_support_frequency` flag often
catches terse but clinically acceptable references. By contrast,
`unknown_gold_boundary`, trigger-only evidence, last-event boundaries, calendar
arithmetic, and cluster conventions repeatedly identify real human-review
questions.

## Qualitative Findings

### Unknown Is Not One Class

The human-ambiguous `unknown` rows include several distinct mechanisms:

- True unquantified frequency. Example: source row 14040 says there have been
  multiple drop attacks since ketogenic diet, with the latest on a date, but the
  family is unable to quantify frequency and has no diary.
- Trigger-only or condition-only frequency. Example: source row 3371 reports
  focal seizures only when sleep deprived, with no events outside curtailed
  sleep.
- Last-event-only evidence. Example: source row 11282 says "Last seizure on
  05-Aug, with none since" from a later clinic date. `unknown` is arguably too
  weak because a seizure-free interval can be derived.
- Count since an unclear or clinically awkward anchor. Example: source row
  14002 says several seizures since discharge, last on a date; the discharge
  anchor may or may not be a valid denominator.
- Calendar/range evidence. Example: source row 14137 says 3-4 GTC seizures
  since beginning Clobazam, with the most recent date. If the medication start
  date is known, this may be a rate/range; if not, `unknown` is defensible.
- Vague trend evidence. Example: source row 12963 says seizure frequency
  decreased markedly, with only seven seizures so far this year. The note
  contains count-like evidence, but benchmark rendering depends on the current
  date/window convention.

These are not interchangeable. A single final `unknown` label erases the
difference between "frequency genuinely unknowable", "event type uncertain",
"denominator missing", "last-event interval could be rendered", and "benchmark
convention chooses not to render".

### Drop Attacks Are Context Dependent

The audit confirms a real inconsistency around drop attacks.

Drop attacks tend to become `unknown` or review-worthy when:

- they are described as collapses, loss of tone, or non-injurious brief events
  with uncertain classification;
- the note says several or multiple since an anchor but does not provide a
  denominator;
- the author explicitly says frequency cannot be quantified;
- the event type is still under investigation.

Examples:

- Source row 14040: multiple drop attacks since ketogenic diet, latest on a
  date, but unable to quantify frequency.
- Source row 14029: several drop attacks since ketogenic diet, latest on a
  date, with a brief-collapse phenotype and work-shift context.

Drop attacks tend to control the final frequency when:

- the note frames them as seizure events in an established epilepsy context;
- there is an explicit rate or window;
- they are the highest current seizure burden among multiple semiologies.

Examples:

- Source row 2513: 2 to 3 drop attacks during the last two weeks in established
  generalized epilepsy.
- Source row 12537: daily drop attacks coexist with less frequent GTC and focal
  impaired-awareness seizures, so daily drop attacks are the highest current
  burden.

The implicit rule is clinically plausible, but it is not explicit enough for
100% exact-label matching: drop attacks are sometimes seizure-frequency evidence
and sometimes event-type uncertainty.

### Wrong Rows Are Mostly Representation Problems

The rows marked `wrong` tended to be small numerical or rendering
misrepresentations rather than failures of the broader clinical extraction
approach. Examples include last-event dates rendered as `unknown`, ranges that
could be converted more directly, or a count window shifted by a month-like
denominator.

This matters because those rows should not drive wholesale architecture changes.
They mostly point to explicit projection, date-window, and benchmark-rendering
policy.

## Implication For System Design

The audit validates the rich intermediate schema strategy. The system should not
only emit a final Gan-compatible label. It should preserve and expose:

- candidate events and exact evidence spans;
- event type and seizure-or-event target;
- assertion status, temporality, trigger dependence, and uncertainty;
- denominator/window assumptions;
- competing semiologies and their separate frequencies;
- selected evidence and rejected evidence;
- rationale for the selected final state;
- projection/rendering rationale for the benchmark-facing label.

This higher-fidelity representation is a strength of the system. It makes
subjective or contradictory cases inspectable instead of hiding them behind a
single label mismatch.

## Proposed Abstention And Human-Review Policy

Future prediction-bearing evaluation should use a selective-action contract:

| Condition | Proposed action |
| --- | --- |
| Frequency evidence is present but denominator/window is missing | abstain or route to human review |
| Event type is uncertain (`drop attack`, collapse, spell) and not clearly tied to seizure burden | human review |
| Trigger-only evidence without stable baseline frequency | abstain or route `unknown_boundary` |
| Last-event-only evidence with derivable seizure-free interval but uncertain benchmark convention | human review |
| Multiple competing semiologies with different rates and uncertain seizure target | human review |
| Cluster frequency and per-cluster load both present but benchmark rendering ambiguous | human review |
| Plain exact frequency with explicit current/recent denominator | predict |
| Plain seizure-free interval with explicit last-event date and no contradictory current events | predict |

The policy should distinguish at least these abstention/review reasons:

- `unknown_frequency_unquantified`
- `event_type_uncertain`
- `trigger_conditioned_frequency`
- `missing_denominator_anchor`
- `last_event_boundary`
- `drop_attack_boundary`
- `cluster_projection_boundary`
- `competing_semiology_boundary`
- `benchmark_convention_boundary`

## Evaluation Contract

Selective-action evaluation must report all of the following:

| Metric | Definition |
| --- | --- |
| Coverage | rows with a prediction / all eligible rows |
| Abstention rate | abstained rows / all eligible rows |
| Human-review rate | human-review rows / all eligible rows |
| Accuracy on covered rows | exact-label accuracy among rows with predictions |
| Abstention precision | human-noncorrect or policy-nonpredictable rows among abstentions |
| Over-abstention rate | human-correct rows among abstentions |
| Class-specific coverage | coverage by gold kind and ambiguity family |
| Rescue value | unsafe predictions blocked by abstention/review |
| Hidden-error rate | true extraction failures incorrectly hidden by abstention |

The last two metrics are essential. Abstention is useful only when it blocks
unsafe predictions or genuinely subjective rows. It is harmful when it hides true
extraction failures or removes easy rows to inflate selective accuracy.

## Anti-Cheating Guardrails

Do not evaluate abstention by accuracy on covered rows alone.

A valid abstention policy must be:

- predeclared before scoring a new surface;
- bounded by a target coverage range or maximum abstention rate;
- reported with abstention precision and over-abstention;
- sliced by gold label kind and review reason;
- compared against the no-abstention baseline;
- audited for true extraction failures hidden by review routing.

An abstain-on-all-hard-questions strategy should fail the evaluation contract
even if selective accuracy becomes high.

## Recommended Next Step

Convert this qualitative policy into an RQ9 follow-up protocol that scores a
selective-action candidate on validation with:

- one final prediction-bearing label when the row is covered;
- an abstention/review reason when not covered;
- coverage and selective accuracy;
- over-abstention accounting;
- row-level packets showing candidate evidence, selected evidence, rejected
  evidence, uncertainty fields, and projection rationale.

The intended research claim is not that the system can always match subjective
gold conventions. The stronger claim is that the system can represent uncertainty
and competing evidence explicitly, make abstention/review auditable, and separate
true extraction failures from benchmark-convention or underdetermined-note
cases.
