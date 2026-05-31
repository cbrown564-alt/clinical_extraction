# Deterministic Rule Catalogue Change Report

Date: 2026-05-31

## Summary

The deterministic V1 seizure-frequency extractor has been refactored from a
validation-saturated regex stack into a mostly catalogued, metadata-rich rule
surface. The main improvement is not higher recall by itself. The improvement is
that deterministic behavior is now easier to inspect, safer to change, and ready
for validation-only ablation reporting.

The refactor preserved default V1 behavior while adding:

- rule groups and portability categories
- rule-level IDs, examples, and provenance
- group, portability, and rule-ID ablation switches
- selected-candidate metadata in pipeline diagnostics
- structured final-selection scores
- traceable benchmark-format repair metadata

One planned deliverable is still outstanding: the formal validation-only
ablation table by rule group. The report below distinguishes completed catalogue
work from that remaining experiment artifact.

## Why This Was Needed

Before this work, deterministic extraction had become a high-performing but
hard-to-audit rule stack. Regexes, date arithmetic, rate normalization, cluster
arithmetic, dataset-specific shorthand, and benchmark repair were too closely
interleaved. That made it difficult to answer research-critical questions:

- Which specific rule fired?
- Was the rule portable clinical logic or Gan-specific support?
- What did the regex capture versus what Python inferred?
- Which rule family caused a false positive or false negative?
- What happens when one family of deterministic logic is disabled?

The catalogue change addresses those questions by making deterministic rules
controlled variables rather than hidden implementation detail.

## What Changed

### 1. Rule Metadata And Ablation Scaffold

The new metadata scaffold defines the initial ablation surface:

```python
class RuleGroup(StrEnum):
    DATE_DURATION_UTILITIES = "date_duration_utilities"
    PORTABLE_RATE_EXPRESSIONS = "portable_rate_expressions"
    SEIZURE_FREE_NO_EVENT_ASSERTIONS = "seizure_free_no_event_assertions"
    CLUSTER_ARITHMETIC = "cluster_arithmetic"
    DIARY_LOG_AGGREGATION = "diary_log_aggregation"
    TEMPORAL_SELECTION = "temporal_selection"
    GAN_SHORTHAND = "gan_shorthand"
    BENCHMARK_REPAIR = "benchmark_repair"
```

Each rule also has a portability category:

```python
class Portability(StrEnum):
    GENERAL = "general"
    CLINICAL_EPILEPSY = "clinical_epilepsy"
    SEIZURE_FREQUENCY = "seizure_frequency"
    GAN2026_SPECIFIC = "gan2026_specific"
    BENCHMARK_FORMAT = "benchmark_format"
```

Rules are controlled through `AblationConfig`:

```python
@dataclass(frozen=True)
class AblationConfig:
    enabled_groups: frozenset[RuleGroup] = frozenset(RuleGroup)
    enabled_portability: frozenset[Portability] = frozenset(Portability)
    disabled_rule_ids: frozenset[str] = frozenset()
```

Why this is better:

- Default behavior stays unchanged because every group and portability category
  is enabled by default.
- Experiments can disable one group, one portability class, or one rule ID.
- The deterministic layer now supports controlled ablations instead of ad hoc
  boolean flags scattered through the extractor.

### 2. Rules Became Named Catalogue Entries

Before, a rate pattern was effectively embedded in the extraction flow. A reader
had to inspect the surrounding code to infer intent, exclusions, and examples.

Representative before shape:

```python
for match in re.finditer(pattern, text):
    if medication_or_dose_context(match):
        continue
    candidates.append(
        RawCandidate(
            kind=CandidateKind.FREQUENCY,
            label=build_rate_label(match),
            evidence=clean(match.group(0)),
        )
    )
```

After, the same behavior is represented as a named rule:

```python
DIRECT_RATE_RULE = RuleSpec(
    rule_id="rate.direct_count_per_period",
    group=RuleGroup.PORTABLE_RATE_EXPRESSIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Generic direct count per period with medication-dose exclusions.",
    pattern=re.compile(...),
    build=_build_direct_rate,
    exclude=(
        _is_medication_or_dose_rate_distractor,
        _is_nonprogressive_myoclonic_rate_distractor,
    ),
    examples=(
        RuleExample(
            text="He still has focal seizures four times per day.",
            expected_label="4 per day",
            expected_evidence="four times per day",
        ),
        RuleExample(
            text="Current medication is lamotrigine 100 mg twice per day.",
            anti_example=True,
            note="Medication dose frequency is not a seizure-frequency candidate.",
        ),
    ),
    provenance="Portable V1 direct count-per-period expression.",
)
```

Before/after behavior example:

```text
Input:
Present Seizure Frequency: He still has focal seizures four times per day.

Before:
final label = 4 per day
diagnostic attribution = generic or absent

After:
final label = 4 per day
rule_id = rate.direct_count_per_period
rule_group = portable_rate_expressions
portability = seizure_frequency
match_groups = {"count": "four", "denominator": null, "unit": "day"}
```

Why this is better:

- The output is the same, but the reason is now inspectable.
- Medication-frequency distractors are documented as anti-examples.
- Error analysis can group failures by rule and by portability class.

### 3. Seizure-Free And No-Event Logic Was Separated

Before, seizure-free logic lived near ordinary rate extraction. That made absence
assertions, historical distractors, and current-control statements harder to
review independently.

After, rules such as `seizure_free.generic_duration_or_since` live in
`rules/seizure_free.py` with conservative examples and anti-examples:

```python
GENERIC_SEIZURE_FREE_RULE = RuleSpec(
    rule_id="seizure_free.generic_duration_or_since",
    group=RuleGroup.SEIZURE_FREE_NO_EVENT_ASSERTIONS,
    portability=Portability.SEIZURE_FREQUENCY,
    description="Generic seizure-free/free-of/no-seizure duration or since assertion.",
    pattern=re.compile(...),
    build=_build_generic_seizure_free,
    exclude=(_is_generic_seizure_free_distractor,),
    examples=(
        RuleExample(
            text="She remains free of seizures for two years on the current regimen.",
            expected_label="seizure free for 2 year",
            expected_evidence="free of seizures for two years",
        ),
        RuleExample(
            text=(
                "The driving plan is to reassess after the seizure-free interval. "
                "Current seizures are weekly."
            ),
            anti_example=True,
            note="Administrative seizure-free interval mention is not current no-event evidence.",
        ),
    ),
)
```

Before/after behavior example:

```text
Input:
The driving plan is to reassess after the seizure-free interval. Current seizures are weekly.

Before risk:
The phrase "seizure-free interval" could be difficult to distinguish from a
current no-event assertion without reading context-specific guards.

After:
The phrase is documented as an anti-example for the generic seizure-free rule.
The guard is part of the rule catalogue rather than hidden in the extraction flow.
```

Why this is better:

- Absence/current-control logic is independently ablatable.
- Historical and administrative seizure-free mentions are explicitly guarded.
- The system can report whether a selected candidate came from no-event logic
  rather than ordinary rate extraction.

### 4. Cluster Arithmetic Became Auditable

Cluster expressions are clinically meaningful but easy to misread because they
mix cluster frequency and seizures per cluster.

Before, a cluster phrase could produce a final label without clear diagnostics
showing which part was the cluster period and which part was the cluster size.

After:

```text
Input:
Present Seizure Frequency: Monthly clusters, typically 6 to 7 seizures over 24 h.

Output:
final label = 1 cluster per month, 6 to 7 per cluster
rule_id = cluster.monthly_rate_with_size
rule_group = cluster_arithmetic
portability = seizure_frequency
match_groups = {"per_cluster": "6 to 7"}
```

Why this is better:

- Cluster behavior can be switched off independently from ordinary rate rules.
- Row-level analysis can distinguish "missed cluster pattern" from "bad cluster
  arithmetic" or "bad final selection".
- The report can separate portable seizure-frequency logic from cluster-specific
  interpretation.

### 5. Diary And Log Mini-Languages Were Isolated

Diary-style rows have formats that do not look like ordinary prose:

```text
Seizure events on 03-07, 03-27, 05-15, 05-19, 05-24
2025: January 0; February 1; March 3
This month: 4 events; in April: 2
```

Before, these patterns sat close to ordinary rates, making the extractor look
like one large pile of regexes.

After, `rules/diary.py` contains the date-list, monthly-log, sparse-month, and
recent-month-summary rules under `diary_log_aggregation`.

Why this is better:

- Diary/log aggregation can be disabled without disabling ordinary seizure-rate
  extraction.
- The catalogue makes clear that compact logs are a distinct mini-language.
- Future parser work, if needed, can be local to diary/log expressions instead
  of becoming a broad rewrite.

### 6. Gan-Specific Shorthand Was Marked As Dataset-Specific

Before, compact synthetic patterns such as `TC nine/mo`, `sz xnine/mo`, and
`q2-3wk` were functionally mixed with portable clinical rules.

After:

```text
Input:
Present Seizure Frequency: TC nine/mo.

Output:
final label = 9 per month
rule_id = gan_shorthand.tc_sz_count_rate
rule_group = gan_shorthand
portability = gan2026_specific
match_groups = {"evidence": "TC nine/mo", "count": "nine", "unit": "mo"}
```

Why this is better:

- The system no longer hides dataset-specific support inside apparently
  portable clinical extraction logic.
- Ablation reports can show how much validation performance depends on
  Gan-specific shorthand.
- Cross-dataset claims can exclude or separately report this category.

### 7. Benchmark Repair Became Traceable

Benchmark repair is necessary for Gan-style label compatibility, but it is not
clinical extraction. The refactor separates it as benchmark-format metadata.

Before:

```text
Input label:
about twice weekly

Output label:
2 per week

Diagnostic trace:
not exposed
```

After:

```text
Input label:
about twice weekly

Final repaired label:
2 per week

Repair trace:
benchmark_repair.once_twice_thrice:
  about twice weekly -> about 2 weekly
benchmark_repair.period_words:
  about 2 weekly -> about 2 per week
benchmark_repair.drop_prediction_noise:
  about 2 per week -> 2 per week
```

Why this is better:

- Benchmark-format transformations are visible and auditable.
- Clinical extraction behavior can be discussed separately from scorer
  compatibility.
- Reports can measure repair dependence without pretending repair is clinical
  reasoning.

### 8. Final Selection Became Explainable

Before, final selection used an opaque tuple priority. It worked, but a reviewer
could not easily see why one candidate won.

Representative before shape:

```python
selected = max(
    pairs,
    key=lambda pair: (
        semantic_priority(pair),
        evidence_priority(pair),
        monthly_frequency(pair),
    ),
)
```

After:

```python
class SelectionScore(BaseModel):
    semantic_priority: int
    evidence_priority: int
    monthly_frequency_priority: float
    reason: str

    def sort_key(self) -> tuple[int, int, float]:
        return (
            self.semantic_priority,
            self.evidence_priority,
            self.monthly_frequency_priority,
        )
```

Before/after behavior example:

```text
Input:
Present Seizure Frequency: He still has focal seizures four times per day.

Before:
selected label = 4 per day
selection reason = implicit in tuple ordering

After:
selected label = 4 per day
selected_score = {
  "semantic_priority": 4,
  "evidence_priority": 0,
  "monthly_frequency_priority": 121.66666666666667,
  "reason": "frequency_monthly_rate"
}
```

Why this is better:

- Sorting behavior is preserved, but the decision is now visible.
- Error analysis can distinguish extraction failures from selection failures.
- The deterministic selector is easier to compare against a future LLM reasoner.

## Current Catalogue Coverage

Current catalogued `RuleSpec` counts:

```text
portable_rate_expressions: 30
seizure_free_no_event_assertions: 10
cluster_arithmetic: 27
diary_log_aggregation: 22
gan_shorthand: 4
```

Benchmark repair is represented separately as 30 `BenchmarkRepairStep` records.

The following groups exist in `RuleGroup` but do not currently have normal
`RuleSpec` registries:

```text
date_duration_utilities
temporal_selection
benchmark_repair
```

This is partly intentional:

- `date_duration_utilities` currently functions as helper-backed parsing inside
  other rule groups.
- `temporal_selection` is represented by structured `SelectionScore`
  diagnostics rather than regex-style `RuleSpec` entries.
- `benchmark_repair` is represented by `BenchmarkRepairStep` records rather
  than extraction rules.

However, this means the implementation is not a literal full completion of the
original "every group as a rule catalogue" framing.

## Verification

Focused verification after the audit:

```text
pytest -q tests/test_gan2026_rule_metadata.py \
          tests/test_gan2026_normalize.py \
          tests/test_gan2026_pipeline_v1.py

373 passed in 0.92s
```

The tested areas cover:

- metadata and ablation configuration
- rule registry validation
- selected-candidate rule metadata
- group-level ablation tests for migrated rule groups
- benchmark repair trace tests
- structured final-selection score diagnostics

## Remaining Work

The original plan is not complete until the validation-only ablation report
exists.

Required next artifact:

```text
experiments/gan2026_v1_rule_group_ablation_2026-05-31.md
```

That artifact should evaluate validation rows with one rule group disabled at a
time and report:

- Purist micro F1
- Pragmatic micro F1
- evidence validity
- no-reference and unknown distribution changes
- top changed rows by disabled group
- frozen test result only as already-known holdout context

No test-row diagnostics should be generated for this ablation work.

## Bottom Line

The change is a major transparency and experimental-control improvement. The
deterministic extractor now exposes what fired, why it fired, how portable the
behavior is, and how the final candidate was selected. That makes the system
much more defensible as a research object.

The remaining gap is not extraction behavior. It is the formal validation-only
ablation report that turns the new controls into performance evidence.
