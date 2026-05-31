# Gan 2026 Deterministic V1 Rule Review

Date: 2026-05-31

Scope: `src/clinical_extraction/tasks/seizure_frequency/gan2026/pipeline_v1.py`,
`tests/test_gan2026_pipeline_v1.py`, the validation artifacts, and the locked
test aggregate in `experiments/gan2026_v1_test_holdout_2026-05-31.md`.

## Executive Assessment

Deterministic-only V1 is useful, transparent, and clinically instructive, but it
is no longer a clean deterministic baseline. It has become a validation-saturated
rule stack. The validation score of 0.9280 Purist micro F1/accuracy is impressive,
but the locked test score of 0.7600 shows that the rule implementation is brittle
and substantially overfit to the validation surface.

The main research value of V1 is now as a controlled object for ablation and as
a source of failure families for a hybrid LLM/DSPy system. It should not be
extended with more unbounded hand rules unless each rule is categorized,
ablatable, and justified as portable clinical logic or as intentionally
Gan-specific benchmark support.

## Strengths

- The pipeline preserves intermediate candidate events, normalized events, final
  selection, semantic kind, monthly scorer value, and evidence validity.
- Evidence traceability is excellent: validation had 750/750 exact selected
  evidence substrings, and the test holdout had 450/450.
- Label normalization is delegated to the Gan-specific normalization/scoring
  layer rather than reimplementing the scorer in the extractor.
- The code explicitly separates candidate extraction, candidate normalization,
  final selection, date helpers, number helpers, and evidence cleanup.
- The rule set captures many clinically real expression families: rates,
  intervals, recent windows, seizure-free intervals, clusters, diaries, multiple
  semiologies, trigger-conditioned uncertainty, medication/dose distractors, and
  historical-versus-current cues.
- The tests provide broad regression coverage for many formerly missed
  validation-derived patterns.

## Major Concerns

### 1. Generalization Failure

The gap from 0.9280 validation Purist F1 to 0.7600 test Purist F1 is the most
important finding. This is too large to treat as ordinary split noise. It
suggests that the late rule additions learned validation phrasing families
rather than stable extraction principles.

The score is still clinically meaningful for a rules-only system, but the
research claim must shift: deterministic V1 demonstrates the ceiling and failure
mode of hand-coded saturation, not a robust final system.

### 2. Rule Accretion

`pipeline_v1.py` is 3,420 lines with 174 `re.compile(...)` calls, 123
`.finditer(...)` calls, and 113 `candidates.append(...)` sites. The extractor is
now a long sequence of pattern cases rather than a small set of compositional
clinical operations.

This makes behavior difficult to reason about. A new rule can shadow, duplicate,
or conflict with an earlier rule without any local signal. The final behavior
depends on extraction order, deduplication, pruning, normalization, and a global
selection score.

### 3. Weak Rule Taxonomy In Code

The project documents rule categories, but the implementation does not encode
them. Portable date logic, seizure-frequency expression parsing, clinical
temporal selection, Gan synthetic diary phrasing, and benchmark-specific repairs
are interleaved in the same functions.

This blocks clean ablation. It also makes it hard to defend which components are
clinically general and which are dataset accommodations.

### 4. Selection Policy Is Too Implicit

The final selector uses a tuple priority:

- trigger-conditioned unknown beats all else;
- current seizure-free beats ordinary frequency;
- frequency beats unresolved multiple;
- unresolved multiple beats ordinary seizure-free;
- unknown beats no-reference;
- frequency tie-breaks by summary priority and monthly frequency.

This is compact, but clinically under-explained. It encodes strong assumptions:
current seizure-free can override frequency candidates, highest frequency usually
wins, and selected `unknown` can dominate if its evidence matches a small trigger
list. Those may be defensible in some Gan cases, but they are not expressed as a
clinical decision model.

### 5. Fragile Temporal Logic

The date helpers are useful but approximate. Month spans use month arithmetic
with several variants: plain span, floor, terminal partial, and inclusive span.
Which variant is used depends on the matched pattern, not a typed temporal
normalization policy.

Relative month inference uses the clinic date and rolls month-only mentions into
the previous year when the month is after the anchor month. That is reasonable
for some letters but brittle without a documented temporal-anchor field per
candidate.

### 6. Clinical Semiology Is Mostly Lexical

The rules recognize many seizure descriptors, but they do not model semiology as
structured data. The selector cannot robustly reason about whether focal auras,
myoclonic jerks, tonic-clonic seizures, non-epileptic events, warnings, anxiety
episodes, or device-detected events should count for the benchmark target.

This limitation matches the residual validation finding: semiology
reconciliation is better suited to a clinical reasoner than more regex cases.

### 7. Unknown, No-Reference, And Seizure-Free Are Semantically Fragile

The scorer collapses some semantic states, but the pipeline preserves them. That
is good. The brittle part is extraction and selection: broad current-control
phrases map to multi-year seizure-free; trigger-conditioned phrases map to
unknown; and no-reference is only a fallback when no candidates are found.

These choices are plausible for Gan scoring but not clinically complete. A note
can contain seizure terminology without a frequency, a historical seizure-free
phrase with current breakthrough, or uncertain events with a count that should
not become either a rate or a clean unknown.

### 8. Tests Are Broad But Too Example-Literal

`tests/test_gan2026_pipeline_v1.py` is 2,410 lines and mostly asserts expected
labels/evidence for specific short snippets. This is valuable regression
coverage, but it encourages adding one more example-shaped rule.

There are few invariant/property tests for:

- rule category behavior;
- temporal anchoring choices;
- conflict resolution among multiple candidates;
- monotonicity of interval/rate conversion;
- medication/dose distractor boundaries;
- historical/current cue interactions;
- generated paraphrase robustness;
- ablation behavior.

The only real-row scoring test covers five hand-selected rows and requires
accuracy >= 0.8, which is too weak to detect most brittleness.

## Clinical Logic Assessment

Clinically sound elements:

- Seizure-free state is kept distinct from ordinary zero frequency.
- Unknown frequency is preserved when seizure-frequency evidence exists but
  cannot be normalized.
- Medication-dose distractors are explicitly rejected in common situations.
- Historical-current suppression exists and catches obvious lead-ins.
- Cluster expressions preserve count and per-cluster size before Gan
  normalization.
- Evidence spans make each final call auditable.

Clinically brittle elements:

- Highest-frequency selection can overvalue incidental, historical, aura-only,
  or lower-clinical-significance semiologies.
- Current seizure-free priority can suppress breakthrough or residual-event
  evidence if the pattern set does not catch the exception.
- Cluster handling is phrase-dependent and can infer `multiple per cluster`
  without enough evidence.
- "Multiple", "several", "most days", and "near-daily" are coerced into scorer
  labels with limited representation of uncertainty.
- Trigger-conditioned events are treated as unknown by pattern rather than by
  assertion/condition structure.
- Non-epileptic, functional, anxiety, warning, aura, and EEG/device-only
  mentions require deeper assertion and target-event modeling than regex can
  reliably provide.

## Readability And Maintainability

The top-level pipeline API is readable. The internal extractor is not. The file
is navigable only if the reader already knows the validation history. Many
patterns are named after the specific phrase family they fix, which is helpful
locally but reveals the overfit path globally.

The most urgent readability issue is not formatting; it is missing structure.
Rules need metadata:

- category;
- portability level;
- clinical target;
- assertion/temporality assumptions;
- expected normalized form;
- whether the rule is Gan-specific;
- ablation switch.

Without that metadata, a 0.9 validation score is hard to interpret and harder to
defend.

## Recommended Next Steps

1. Freeze deterministic-only V1 as the saturated hand-rule baseline. Do not tune
   it from test performance.
2. Add rule metadata and ablation switches before adding any more deterministic
   rules.
3. Split extraction into rule groups: date/duration utilities, portable rate
   expressions, seizure-free/no-event assertions, cluster arithmetic, diary/log
   aggregation, temporal selection, Gan-specific shorthand, and benchmark repair.
4. Build an ablation table on validation only, then report the already-frozen
   test result as deterministic V1 holdout performance.
5. Replace broad final-selection tuple logic with an explicit decision record
   over structured candidate attributes: assertion, temporality, semiology,
   event target, window, normalized rate, and uncertainty.
6. Start LLM/DSPy validation experiments for the failure families that are
   clearly reasoning problems: semiology reconciliation, trigger conditions,
   current-versus-historical selection, non-epileptic/EEG-only mapping, and
   cluster-detail interpretation.
7. Add paraphrase and adversarial tests for core portable rules so future gains
   are not only exact-snippet gains.

## Bottom Line

V1 did exactly what a good research baseline should do: it climbed high enough
on validation to expose the limits of deterministic saturation. The held-out
drop is not a failure of the project; it is evidence for the project thesis.
The next credible improvement should come from structure, ablation, and hybrid
reasoning, not from another layer of hand-written regexes.
