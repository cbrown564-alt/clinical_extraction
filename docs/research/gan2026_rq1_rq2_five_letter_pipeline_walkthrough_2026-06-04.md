# Gan 2026 RQ1/RQ2 Five-Letter Pipeline Walkthrough

Date: 2026-06-04

Status: validation-development component walkthrough. This is not an F1,
holdout, or benchmark-comparable claim.

Source artifact:
`experiments/gan2026_rq1_rq2_component_control_matrix_2026-06-04.jsonl`

Purpose: make the component-control analysis visible by tracing five distinct
clinic letters through the experimental setups. Each letter is judged by what
the setup was supposed to do, not by final F1.

## Reading Key

The setups are:

- `candidate_only`: expose plausible seizure-frequency facts without deciding.
- `gold_query_evidence_only`: broad evidence search for the seizure-frequency
  question.
- `candidate_conditioned_evidence_only`: evidence check for a fixed candidate.
- `projection_only`: choose/render a state from fixed candidate/evidence input.
- `candidate_plus_evidence`: discover candidates and evidence together.
- `evidence_plus_projection`: evidence check plus provisional projection for a
  fixed candidate.
- `candidate_plus_evidence_plus_projection`: full one-prompt bundle.

The question in each letter is: which component preserved the clinically
important information, which component distorted it, and why does that matter
for architecture?

## Letter A: Ordinary Quantified Rate With Cluster Context

Source row: `10`

Panel: `balanced_validation50`

Gold: `4 per day`

Hidden families: `cluster_burden`, `diary_or_log_aggregation`,
`rate_bucket_or_denominator`, `current_vs_historical`

### What The Letter Requires

This is the easy-looking case that still tests fundamentals. A good component
should find the current rate, keep the cluster caveat visible, and avoid being
thrown by the upper-bound wording.

Good means:

- expose `four per day` or `<= four per day`;
- preserve that clustering is variable and not fully quantified;
- avoid converting cluster uncertainty into failure;
- render `4 per day` only at the projection/rendering layer.

### What Happened

| Setup | What happened | Component judgment |
| --- | --- | --- |
| `candidate_only` | Found one exact current `frequency_rate`: observed frequency `<= four per day` with variable clustering. | Good RQ1 behavior: compact, faithful, ambiguity-preserving. |
| `gold_query_evidence_only` | Selected three exact spans: broad fluctuating-pattern context, the decisive accommodation-log rate, and seizure semiology context. | Good broad locator, but higher burden than needed for final state selection. |
| `candidate_conditioned_evidence_only` | Selected the exact decisive span `<= four per day`, with missing `timeframe`, `unit`, `per_cluster_burden`, and `seizure_free_duration`. | Best primitive: precise evidence plus operand gaps. |
| `projection_only` | Rendered `4 per day` correctly. | Projection can work on ordinary frequency when fixed input already contains the answer. |
| `candidate_plus_evidence` | Produced zero candidates/evidence in this run. | Bad overload/syntax behavior: combining candidate and evidence did not preserve the simple fact. |
| `evidence_plus_projection` | Selected exact `four per day`, but decision was `frequency` with no `seizure_frequency_label` because it treated missing unit/timeframe as blocking. | Evidence survived; rendering did not. |
| `candidate_plus_evidence_plus_projection` | Found two candidates and two exact evidence spans, selected the better current candidate, but again omitted the final label because of upper-bound/cluster uncertainty. | Clinically faithful but not benchmark-renderable. |

### Why It Matters

This letter shows the difference between clinical preservation and benchmark
rendering. The LLM can locate and explain the right fact. It can even preserve
the cluster caveat. But when asked to project and render, it becomes too timid
and often omits the final label.

Architecture implication: keep LLM evidence/candidate outputs, but let a
deterministic compiler render ordinary rates when the operands are present.

## Letter B: Unresolved Multiple Events In A Day

Source row: `280`

Panel: `balanced_validation50`

Gold: `multiple per day`

Hidden families: `cluster_burden`, `diary_or_log_aggregation`,
`rate_bucket_or_denominator`, `current_vs_historical`,
`competing_semiologies`, `benchmark_format_convention`

### What The Letter Requires

This row is not about an exact integer count. The benchmark-relevant state is
that there were multiple seizures in the past day. A good component must
preserve the unresolved multiple state without demanding a precise count.

Good means:

- expose the phrase `multiple seizures in past day`;
- distinguish confirmed seizures from near-miss episodes;
- avoid collapsing the row to `unknown` or `no_reference`;
- preserve benchmark convention: "multiple per day" is acceptable even without
  a numeric count.

### What Happened

| Setup | What happened | Component judgment |
| --- | --- | --- |
| `candidate_only` | Found `multiple seizures in past day` and a separate near-miss/unknown candidate. | Good candidate behavior: it exposes the decisive fact and preserves uncertainty around near-misses. |
| `gold_query_evidence_only` | Selected the decisive past-day evidence, near-miss context, and future monitoring advice. | Good broad evidence; includes context but identifies the key span. |
| `candidate_conditioned_evidence_only` | Selected exact `multiple seizures in past day` and marked missing unit/time basis/cluster operands. | Good evidence primitive, but still not benchmark policy-aware. |
| `projection_only` | Chose `unknown` with no label because count/timeframe/unit were considered missing. | Projection failure: it over-requires numeric operands and misses the benchmark convention. |
| `candidate_plus_evidence` | Preserved one candidate and one exact decisive evidence span. | Good paired extraction when projection is absent. |
| `evidence_plus_projection` | Selected exact evidence and produced `multiple seizures per day`. | Best projection-like behavior here, because fixed candidate/evidence restrained the task. |
| `candidate_plus_evidence_plus_projection` | Produced zero candidates and zero evidence, then called it `no_reference`. | Full-bundle failure: the all-in-one prompt erased a straightforward decisive fact. |

### Why It Matters

This is the cleanest demonstration that projection policy is not the same as
clinical evidence selection. Evidence components handled the row. Projection
failed because it treated a benchmark-convention state as under-specified.

Architecture implication: benchmark convention must be explicit and
deterministic. Do not ask the LLM to infer when "multiple" is enough for Gan
syntax while also managing evidence and ambiguity.

## Letter C: Conditional Events Versus Seizure-Free Overreach

Source row: `3356`

Panel: `hidden_family_hard_panel`

Gold: `unknown`

Hidden families: `unknown_boundary`, `seizure_free_duration`,
`uncertainty_or_ambiguity`, `current_vs_historical`,
`competing_semiologies`, `candidate_absent_or_weak`, `cluster_or_diary`,
`deterministic_miss`, `seizure_free_overreach`,
`unknown_no_reference_boundary`

### What The Letter Requires

This row is a boundary case. The letter describes events occurring only under a
condition, with no events when sleep is adequate. The right behavior is not to
turn "no events when sleep is adequate" into seizure freedom.

Good means:

- expose the conditional event state;
- preserve that frequency is unknown or conditional, not absent;
- avoid seizure-free overreach;
- avoid no-reference collapse.

### What Happened

| Setup | What happened | Component judgment |
| --- | --- | --- |
| `candidate_only` | Found the conditional current/recent frequency candidate tied to curtailed sleep. | Good candidate rescue: it exposes the boundary state. |
| `gold_query_evidence_only` | Selected the conditional event evidence and the contextual no-events-when-sleep-adequate phrase. | Good broad evidence: both sides of the boundary are visible. |
| `candidate_conditioned_evidence_only` | Selected `no events reported` for the fixed candidate and listed many missing components. | Mixed: exact but vulnerable to upstream candidate choice. It validates the wrong side if supplied the wrong target. |
| `projection_only` | Chose `seizure_free`. | Bad projection: classic seizure-free overreach. |
| `candidate_plus_evidence` | Preserved the conditional event evidence and candidate. | Good paired extraction. |
| `evidence_plus_projection` | Selected `no events reported` and chose `seizure_free`. | Exact evidence plus wrong clinical interpretation: source grounding alone is not enough. |
| `candidate_plus_evidence_plus_projection` | Preserved conditional event evidence, chose `frequency`, but omitted the label because the rate is conditional and not numeric. | Better than seizure-free, but still not a final renderer. |

### Why It Matters

This letter shows why exact evidence is necessary but insufficient. The evidence
can be exact and still support the wrong state if the selected target is wrong
or the projection policy is weak.

Architecture implication: evidence gates must be paired with typed state fields
for conditionality, currentness, and seizure-free boundaries. Projection needs a
policy that says conditional events block seizure-free claims and usually map to
`unknown`.

## Letter D: Cluster Burden With Seizure-Free Distractor

Source row: `10618`

Panel: `hidden_family_hard_panel`

Gold: `unknown, 4 to 6 per cluster`

Hidden families: `seizure_free_duration`, `cluster_burden`,
`competing_semiologies`, `uncertainty_or_ambiguity`

### What The Letter Requires

This letter has a cluster burden but not a clean cluster cadence. It also has a
seizure-free-ish distractor: several days without events or no consistent focal
auras. Good behavior must keep "4 to 6 per cluster" visible while preserving the
unknown cadence.

Good means:

- expose the per-cluster burden;
- avoid treating several days without events as seizure freedom;
- preserve that the cluster cadence is unknown;
- keep historical medication/cluster context separate from current state.

### What Happened

| Setup | What happened | Component judgment |
| --- | --- | --- |
| `candidate_only` | Produced four candidates: current cluster burden, unknown-frequency gap, historical cluster context, and reduced cluster burden. One evidence check was non-exact. | Useful but noisy: candidate generation exposes the right structure but needs evidence validation and pruning. |
| `gold_query_evidence_only` | Selected exact current cluster burden and contextual no-event/medication spans. | Strong broad evidence. |
| `candidate_conditioned_evidence_only` | Selected `no consistent focal auras reported` as supporting context. | Shows the danger of fixed-candidate conditioning when the candidate target is bad. |
| `projection_only` | Chose `seizure_free`. | Severe projection failure: distractor evidence overrode active cluster burden. |
| `candidate_plus_evidence` | Preserved current cluster burden, several-days-without-events, and historical medication/cluster context. | Good extraction but includes distractors requiring typed arbitration. |
| `evidence_plus_projection` | Again followed `no consistent focal auras reported` to seizure-free. | Exact evidence, wrong target, wrong projection. |
| `candidate_plus_evidence_plus_projection` | Preserved current cluster burden and historical cluster evidence, then emitted `clustered seizures` with no Gan-compatible label. | Clinically closer than projection-only but still not benchmark-renderable. |

### Why It Matters

This is the archetype for "candidate generation helps, projection hurts." The
LLM can surface the right clinical pieces, including a cluster burden that
deterministic systems often struggle with. But without a typed state and policy,
projection grabs a seizure-free distractor.

Architecture implication: RQ3 should focus on representing cluster burden,
cluster cadence, currentness, and seizure-free distractors explicitly. A final
label should be compiled after those fields are set.

## Letter E: Current Summary Versus Derived Year Rate

Source row: `2748`

Panel: `hidden_family_hard_panel`

Gold: `1 per month`

Hidden families: `rate_bucket_or_denominator`, `competing_semiologies`

### What The Letter Requires

This row has two plausible frequency expressions: a derived year-to-date count
and a current clinician/patient summary of monthly focal seizures. Good behavior
should prefer the current explicit summary for projection while preserving the
year-to-date context.

Good means:

- expose both seven-so-far-this-year and monthly-current-summary candidates;
- classify the monthly summary as decisive for current state;
- avoid abstaining just because one candidate is derived or missing a denominator;
- avoid changing the clinical fact during rendering.

### What Happened

| Setup | What happened | Component judgment |
| --- | --- | --- |
| `candidate_only` | Found both candidates: seven focal impaired-awareness seizures so far this year and monthly focal seizure pattern. | Good candidate behavior: exposes competing rates. |
| `gold_query_evidence_only` | Selected both decisive spans and supporting improvement context, but one evidence exactness check failed. | Mechanistically good but evidence hygiene needs inspection. |
| `candidate_conditioned_evidence_only` | Selected the year-to-date candidate, not the monthly summary. | Exact but not the best target if the task is current-state projection. |
| `projection_only` | Abstained due to missing count/timeframe/unit details. | Projection failure: it had enough clinical material to choose monthly but lacked policy/representation. |
| `candidate_plus_evidence` | Preserved both exact decisive candidates and evidence spans. | Good paired extraction. |
| `evidence_plus_projection` | Selected exact year-to-date evidence and chose frequency but omitted the label. | Evidence survived, rendering failed. |
| `candidate_plus_evidence_plus_projection` | Selected both candidates and evidence, recognized monthly as current, but omitted the label and had one non-exact evidence status. | Best clinical reasoning among broad prompts, still not a final renderer. |

### Why It Matters

This letter shows why "final label" is a bad way to judge the component. The
full bundle did useful clinical arbitration by preferring the current monthly
pattern over the derived year count, but it still failed the rendering contract.
Conversely, exact evidence for the wrong candidate is not enough.

Architecture implication: selected-state schemas must carry both candidate
facts and the reason one is current/projection-relevant. Rendering `1 per month`
should be deterministic once the selected state is monthly.

## Cross-Letter Lessons

### Candidate Generation

Candidate generation is best when it is allowed to expose alternatives without
deciding. It did useful work in Letters B, C, D, and E by surfacing boundary,
conditional, cluster, or competing-rate facts.

Its failure mode is not usually total blindness. Its failure mode is burden and
schema drift: extra candidates, raw-output fallbacks, or missing source
instrumentation. That is why candidate generation should feed an evidence gate,
not a final label.

### Evidence Selection

Evidence selection is the most stable LLM-owned capability. It located decisive
text in all five letters. Candidate-conditioned evidence is cleaner when the
candidate is right; gold-query evidence is safer when candidate coverage is
uncertain.

Its failure mode is target dependence. Letters C and D show that exact evidence
for the wrong supplied target can still support the wrong interpretation.

### Projection

Projection is where clinical facts become benchmark policy. The current
`projection_only` result should be read as an under-instructed fixed-input
projection test, not as a complete negative result for LLM projection. The
policy choices are non-obvious and partly subjective: without explicit
annotation instructions, reasonable reviewers may not consistently make the
same choices about currentness, cluster burden, conditional events,
seizure-free distractors, and unresolved multiple events.

The light prompt failed in different ways:

- Letter B: over-demanded numeric operands for `multiple per day`;
- Letter C: overcalled seizure freedom from conditional/no-event context;
- Letter D: followed a seizure-free distractor over cluster burden;
- Letter E: abstained or omitted a label despite enough current summary evidence.

Projection can work on ordinary fixed-input rates, as in Letter A, but that is
not enough to make the light prompt a reliable component. The fairer comparison
is a fixed-input, instruction-heavy projection variant that states general
principles without copying row-specific examples from this panel.

### Paired Prompts

Paired prompts are not all equal.

`candidate_plus_evidence` often preserves useful material when no projection is
required. `evidence_plus_projection` preserves evidence well but usually omits
labels. The full bundle sometimes reasons clinically, but it also has the
largest risk of evidence loss, no-reference collapse, and schema drift.

## Final Judgment

The five letters support this component ranking:

1. `candidate_conditioned_evidence_only` when the candidate is trustworthy.
2. `gold_query_evidence_only` when candidate coverage is uncertain.
3. `candidate_only` as selective rescue and ambiguity exposure.
4. `candidate_plus_evidence` as a useful paired extraction stress surface.
5. `evidence_plus_projection` only as provisional state classification, not
   rendering.
6. `candidate_plus_evidence_plus_projection` as overload diagnostics only.
7. `projection_only` as a negative result for under-instructed direct
   final-label ownership.

The next experiment should not ask whether the LLM can get a higher F1. It
should first compare the light projection prompt against an instruction-heavy
fixed-input projection variant covering the common policy scenarios. After that,
it should ask whether candidate/evidence facts can be carried into a typed
selected state with explicit currentness, conditionality, cluster burden, rate
time basis, seizure-free boundary, and ambiguity fields, then rendered by an
auditable projection policy.
