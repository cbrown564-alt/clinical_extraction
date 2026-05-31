# Deterministic Rule Catalogue Implementation Plan

Date: 2026-05-31

## Purpose

Turn deterministic regex extraction from a validation-saturated rule stack into
an inspectable, ablatable rule catalogue.

This is not a rewrite for elegance alone. The rule catalogue should make the
deterministic layer easier to review, safer to change, and more useful for the
hybrid LLM system's audit trail. Regexes should locate source text; Python code
should explain date arithmetic, rate conversion, cluster arithmetic, temporal
selection, and benchmark repair; metadata should make each rule experimentally
ablatable.

## Design Principles

- Preserve frozen V1 behavior until an intentional ablation or candidate change
  is declared.
- Do not tune on, inspect row-level failures from, or otherwise use the locked
  test split.
- Treat every deterministic rule as a controlled variable with a unique ID,
  group, portability category, examples, and provenance.
- Keep deterministic audit fields honest. Use `null` for temporality,
  certainty, or applies-to fields when a rule did not actually infer them.
- Prefer a Python rule catalogue before YAML or external configuration, so rules
  retain type checking, constants, helper functions, and refactoring support.
- Split matching from interpretation. Regex should find an evidence shape;
  builder code should convert that shape into candidate primitives.
- Refactor in small behavior-preserving increments. Avoid a big-bang grammar or
  parser rewrite.

## Target Rule Groups

These groups are the initial ablation surface:

1. `date_duration_utilities`: dates, relative windows, month spans, duration
   parsing, and anchor inference.
2. `portable_rate_expressions`: direct rates, intervals, counts in windows,
   adjective/adverbial rates, and ordinary seizure frequency expressions likely
   to transfer beyond Gan 2026.
3. `seizure_free_no_event_assertions`: seizure-free intervals, no-event
   assertions, last-event-only evidence, and no-reference or unknown-frequency
   distinctions.
4. `cluster_arithmetic`: cluster counts, events per cluster, cluster periods,
   vague cluster-size handling, and cluster expansion primitives.
5. `diary_log_aggregation`: date lists, month logs, year-to-date summaries,
   sparse month lists, sleep/awake splits, and diary-style aggregation.
6. `temporal_selection`: current-versus-historical cues, supersession,
   breakthrough handling, improvement/worsening cues, and final currentness
   preferences.
7. `gan_shorthand`: compact Gan-style shorthand such as `TC nine/mo`,
   `sz xnine/mo`, `q2-3wk`, and validation-derived synthetic phrasing.
8. `benchmark_repair`: label formatting, Gan scorer sentinel handling, accepted
   prediction repair, and compatibility-only transformations.

Every rule also gets a portability category:

- `general`
- `clinical_epilepsy`
- `seizure_frequency`
- `gan2026_specific`
- `benchmark_format`

## Target Objects

### RuleSpec

`RuleSpec` should make rule intent visible without requiring readers to inspect
the regex first.

```python
@dataclass(frozen=True)
class RuleSpec:
    rule_id: str
    group: RuleGroup
    portability: Portability
    description: str
    pattern: Pattern[str]
    build: Callable[[Match[str], ExtractionContext], RawCandidate | None]
    exclude: tuple[ExclusionPredicate, ...] = ()
    examples: tuple[RuleExample, ...] = ()
    provenance: str | None = None
```

Minimum registry validation:

- `rule_id` is unique.
- `group` and `portability` are set.
- at least one positive example exists unless the rule is only a helper or
  repair rule.
- each example either produces the expected candidate or is documented as an
  anti-example.
- every group can be disabled by ablation config.

### Raw Candidate Audit Fields

Extend deterministic candidates toward the LLM audit schema without pretending
the deterministic extractor knows more than it does:

```python
@dataclass(frozen=True)
class RawCandidate:
    kind: CandidateKind
    label: str | None
    evidence: str
    rule_id: str = "unknown"
    rule_group: RuleGroup | None = None
    portability: Portability | None = None
    match_groups: Mapping[str, str | None] = field(default_factory=dict)
    occurrences_low: float | None = None
    occurrences_high: float | None = None
    period_low: float | None = None
    period_high: float | None = None
    period_unit: str | None = None
    applies_to: str | None = None
    assertion_status: str | None = None
    temporality: str | None = None
    certainty: str | None = None
```

`CandidateEvent` and diagnostics should expose the rule metadata so row-level
error analysis can answer:

- Which rule fired?
- Which group and portability category did it belong to?
- What groups did the regex capture?
- Which parsed primitives came from matching versus later normalization?
- Which rule group caused a false positive, false negative, or wrong selection?

### AblationConfig

Add an explicit config object instead of scattering boolean flags through the
extractor.

```python
@dataclass(frozen=True)
class AblationConfig:
    enabled_groups: frozenset[RuleGroup] = frozenset(RuleGroup)
    enabled_portability: frozenset[Portability] = frozenset(Portability)
    disabled_rule_ids: frozenset[str] = frozenset()
```

The runner should apply rules only when their group, portability, and rule ID
are enabled. V1 default config should enable all groups and preserve current
behavior.

## Iterative Work Plan

### Chunk 1: Metadata Scaffold

Goal: Add the smallest metadata layer without moving rules.

Tasks:

- Add `RuleGroup`, `Portability`, `AblationConfig`, and a minimal rule metadata
  helper module.
- Extend `_RawCandidate` and public candidate diagnostics with optional
  `rule_id`, `rule_group`, `portability`, and `match_groups`.
- Update candidate construction to default metadata to `unknown` or `None` so
  behavior remains unchanged.
- Add tests proving existing V1 outputs are unchanged with default metadata.

Exit criteria:

- Current pipeline tests pass.
- Candidate diagnostics can carry rule metadata.
- No extraction behavior changes are expected.

### Chunk 2: Registry And Ablation Runner

Goal: Create the machinery for catalogued rules before migrating many rules.

Tasks:

- Add `RuleSpec`, `RuleExample`, `ExtractionContext`, and `apply_rule`.
- Add registry validation tests for unique IDs, required categories, and example
  shape.
- Add `AblationConfig` to the extraction path, with all groups enabled by
  default.
- Migrate one tiny low-risk rule to prove the path works.

Exit criteria:

- One catalogued rule emits the same candidate as before.
- Disabling that rule or group removes its candidate in a focused test.
- Default config remains behavior-preserving.

### Chunk 3: Portable Rate Expressions

Goal: Move the highest-value ordinary rate rules into the catalogue.

Tasks:

- Create `rules/rate.py`.
- Migrate direct count-per-period, every-N interval, adjective/adverbial rate,
  count-in-recent-window, and period-first count rules.
- Convert selected patterns to verbose regex only when it improves readability.
- Add positive and negative examples per rule, including medication/dose
  distractors where relevant.

Exit criteria:

- Rate rules are skimmable as a named catalogue.
- Rule-level examples pass.
- Validation behavior with all groups enabled is unchanged or any difference is
  explicitly documented as a candidate-version change.

### Chunk 4: Seizure-Free And No-Event Assertions

Goal: Separate absence/current-control logic from ordinary rate extraction.

Tasks:

- Create `rules/seizure_free.py`.
- Migrate seizure-free-since, seizure-free-for-duration, no-definite-event,
  no-recent-event, last-event-only, and no-reference/unknown evidence rules.
- Keep assertion and temporality fields conservative.
- Add anti-examples for historical seizure-free distractors and breakthrough
  contexts.

Exit criteria:

- Seizure-free and no-event rules can be disabled independently.
- Candidate diagnostics show whether the rule emitted seizure-free, unknown, or
  no-reference semantics.
- Historical/current guard behavior is covered by focused tests.

### Chunk 5: Cluster Arithmetic

Goal: Make cluster behavior auditable before adding any new cluster logic.

Tasks:

- Create `rules/cluster.py`.
- Migrate cluster count, events-per-cluster, cluster-rate, vague cluster-size,
  and cluster-over-period rules.
- Keep regex matching separate from multiplication and label construction.
- Record parsed primitives for cluster count, cluster period, and events per
  cluster.

Exit criteria:

- Cluster rules can be ablated independently.
- Diagnostics can distinguish a match failure from an arithmetic or
  normalization failure.
- Tests cover vague cluster handling and known unsupported cluster labels.

### Chunk 6: Diary And Log Aggregation

Goal: Pull diary-like mini-languages out of the general rate path.

Tasks:

- Create `rules/diary.py`.
- Migrate date lists, month-count logs, sparse month lists, year-to-date logs,
  and compact recent-month summaries.
- Consider a tiny parser only for bounded diary/log expressions if regex
  remains hard to read after catalogue migration.

Exit criteria:

- Diary/log aggregation can be disabled independently.
- Rule examples cover representative compact and sparse formats.
- Any parser use is local and does not replace the broader deterministic
  pipeline.

### Chunk 7: Temporal Selection And Decision Records

Goal: Make final selection explainable rather than only tuple-ranked.

Tasks:

- Replace or wrap the tuple score with a `SelectionDecision` or
  `SelectionScore` object.
- Record semantic priority, currentness cue, specificity cue, monthly frequency
  tie-break, and reason text.
- Keep sorting behavior identical at first.
- Add diagnostics showing why the final candidate won over alternatives.

Exit criteria:

- Existing selected labels remain unchanged under default config.
- Error analysis can group failures by selected rule and selection reason.
- The final selector is ready for comparison against LLM reasoner outputs.

### Chunk 8: Gan Shorthand And Benchmark Repair

Goal: Isolate intentionally dataset- or benchmark-specific behavior.

Tasks:

- Create `rules/gan_shorthand.py` and `rules/benchmark_repair.py`.
- Migrate compact shorthand and accepted-label repair behavior into explicitly
  non-general categories.
- Add registry tests requiring `gan2026_specific` or `benchmark_format`
  portability for these rules.

Exit criteria:

- Gan-specific behavior can be switched off as a category.
- Benchmark repair is visibly separate from clinical extraction.
- Reports can say exactly how much performance depends on dataset-specific
  phrasing and scorer compatibility.

### Chunk 9: Ablation Reporting

Goal: Produce the first validation-only ablation table by rule group.

Tasks:

- Add an experiment script or report command that evaluates validation with one
  rule group disabled at a time.
- Report Purist/Pragmatic micro F1, evidence validity, no-reference/unknown
  distribution, and top changed rows by rule group.
- Save run records under `experiments/`.

Exit criteria:

- Validation-only ablation table exists.
- Frozen test score is reported only as already-known V1 holdout context.
- No test split row-level diagnostics are generated.

## Suggested Session Order

1. Implement Chunk 1 and run focused tests plus full `pytest` if feasible.
2. Implement Chunk 2 with one safe proof-of-concept rule.
3. Migrate `portable_rate_expressions` in several small PR-sized passes.
4. Migrate `seizure_free_no_event_assertions`.
5. Run the first coarse ablation with only partially migrated groups to validate
   the mechanism.
6. Continue group migration by risk: cluster arithmetic, diary/log aggregation,
   temporal selection, Gan shorthand, benchmark repair.
7. Generate the formal validation-only ablation table.

## Non-Goals For The First Pass

- Do not add new deterministic recall rules while building the catalogue unless
  the rule is required to preserve current behavior.
- Do not rewrite the full extractor in Lark, pyparsing, spaCy, or another parser
  framework.
- Do not externalize the rule catalogue to YAML before the Python catalogue is
  stable.
- Do not force deterministic candidates to mimic LLM fields when the evidence is
  not actually available.
- Do not change locked test handling or use test rows for development.

## Success Criteria

The refactor is succeeding when a reviewer can answer these questions without
reading thousands of lines of regex:

- What deterministic rule groups exist?
- Which rules are portable clinical logic versus Gan-specific support?
- Which rule fired for a selected candidate?
- What did the regex capture?
- What did Python infer after the match?
- Why did final selection choose this candidate?
- What happens to validation performance when a group is disabled?

