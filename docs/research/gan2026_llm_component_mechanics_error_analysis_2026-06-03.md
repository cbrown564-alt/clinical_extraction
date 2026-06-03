# Gan 2026 LLM Component Mechanics Error Analysis

Date: 2026-06-03

Protocol:
`docs/research/gan2026_llm_component_mechanics_protocol_2026-06-03.md`

Source artifact:
`experiments/gan2026_llm_component_mechanics_rows_2026-06-03.jsonl`

Human index:
`experiments/gan2026_llm_component_mechanics_rows_2026-06-03.md`

Interpretation-policy update:
`docs/research/gan2026_llm_component_interpretation_policy_and_controlled_experiments_2026-06-03.md`

## Claim Boundary

This is a validation-development mechanism analysis over saved replay artifacts.
It does not inspect locked holdout rows, make a benchmark-comparable claim, or
promote an architecture. Deterministic outputs are comparator context only.

The row-level artifact contains 195 mechanism rows over 111 validation source
rows:

| Clinical subproblem | Rows |
| --- | ---: |
| Evidence selection | 83 |
| Projection | 65 |
| Candidate generation | 47 |

The central finding is that the LLM components are not failing mainly because
they cannot find text. They fail because source-near text has to pass through
three stricter gates: deciding whether a candidate state is clinically decisive,
keeping enough typed state to make that decision auditable, and projecting the
state into Gan-compatible labels without overreaching.

Important correction: projection-compatible phrases and faithful ambiguous
clinical facts must not be counted as LLM component failures. For example,
`multiple times per week` is a correct representation of `multiple per week`,
and `multiple per shift` is a valid clinical fact that requires an uncertainty
classification plus a transparent projection policy. Multiple candidates per
row are also not a defect by default; their value must be tested with a fixed
downstream selector.

## Hidden-Family Coverage

Hidden-family tagging is strongest for candidate generation and weaker for
evidence/projection rows. That is itself an instrumentation result: the next
artifact should carry hidden-family tags through every copied projection and
changed-row slice rather than leaving most evidence/projection rows
`unclassified`.

| Hidden family | All rows | Candidate generation | Evidence selection | Projection |
| --- | ---: | ---: | ---: | ---: |
| `unclassified` | 114 | 3 | 59 | 52 |
| `current_vs_historical` | 44 | 24 | 13 | 7 |
| `competing_semiologies` | 39 | 18 | 13 | 8 |
| `rate_bucket_or_denominator` | 33 | 17 | 9 | 7 |
| `benchmark_format_convention` | 29 | 11 | 10 | 8 |
| `cluster_burden` | 19 | 10 | 6 | 3 |
| `uncertainty_or_ambiguity` | 18 | 10 | 8 | 0 |
| `unknown_boundary` | 16 | 8 | 8 | 0 |
| `seizure_free_duration` | 12 | 9 | 2 | 1 |
| `diary_or_log_aggregation` | 11 | 6 | 4 | 1 |
| `numeric_seizure_free_duration` | 1 | 0 | 0 | 1 |

## Candidate-Generation Mechanics

LLM candidate generation has a credible role in preserving boundary,
uncertainty, and competing-state hypotheses that deterministic rules often
collapse. It should not be judged by benchmark-ready label syntax alone:
clinically faithful, projection-compatible phrases are successful candidate
representations when the missing operation is only projection or rendering.

| RQ1 bucket | Rows | Dominant hidden families |
| --- | ---: | --- |
| `rq1_llm_candidate_win_over_deterministic_miss` | 11 | `seizure_free_duration`, `uncertainty_or_ambiguity`, `unknown_boundary` |
| `rq1_llm_candidate_loss_vs_deterministic` | 12 | `current_vs_historical`, `benchmark_format_convention`, `rate_bucket_or_denominator`, `competing_semiologies` |
| `rq1_llm_candidate_burden` | 12 | `rate_bucket_or_denominator`, `current_vs_historical` |
| `rq1_llm_selected_state_recall` | 12 | `current_vs_historical`, `cluster_burden`, `competing_semiologies` |

### Useful Candidate Mechanism

The strongest wins are not ordinary frequency extraction. They are rows where
the note contains an apparently easy seizure-free or rate-like phrase plus a
second state that makes the benchmark answer uncertain.

- `source_row_index=3356`, gold `unknown`, families
  `unknown_boundary`, `seizure_free_duration`,
  `uncertainty_or_ambiguity`: the LLM preserved a gold-relevant `unknown`
  candidate from recent conditional events while deterministic candidates
  favored a seizure-free duration.
- `source_row_index=6077`, gold `unknown`, families
  `unknown_boundary`, `seizure_free_duration`,
  `uncertainty_or_ambiguity`: the LLM held both the eight-month seizure-free
  phrase and a breakthrough travel event, exposing boundary competition instead
  of reducing the row to duration.
- `source_row_index=10266`, gold `unknown`, families `unknown_boundary`,
  `cluster_burden`, `diary_or_log_aggregation`,
  `uncertainty_or_ambiguity`: the LLM treated device-log clusters without
  counts as uncertainty rather than converting the log cadence into a seizure
  frequency.

The transferable mechanism is candidate pluralism under boundary ambiguity.
The LLM is useful when the correct answer depends on preserving incompatible
states long enough for a later verifier to decide.

### Projection-Compatible Candidate Mechanism

Some rows previously looked like candidate losses only because the candidate was
not already in Gan parser syntax. Under the interpretation policy, these should
be split into representation success plus projection/rendering responsibility
when the phrase preserves the clinical fact.

- `source_row_index=278`, gold `multiple per week`, families
  `rate_bucket_or_denominator`, `current_vs_historical`,
  `benchmark_format_convention`: the LLM emitted "multiple times per week",
  which is a correct clinical representation and should project directly to
  `multiple per week`.
- `source_row_index=744`, gold `multiple per week`, families `cluster_burden`,
  `rate_bucket_or_denominator`, `current_vs_historical`,
  `competing_semiologies`, `benchmark_format_convention`: the LLM emitted a
  vague "frequent" candidate for most-weekday absence evidence. This remains a
  candidate-specific weakness because it loses the rate signal, but the row
  should also be tested under a projection-compatible-phrase policy.
- `source_row_index=1357`, gold `1 per day`, families
  `rate_bucket_or_denominator`, `competing_semiologies`: the LLM emitted only
  a seizure-event candidate rather than binding one event to the daily window.

The durable lesson is first-failure ownership. If the LLM preserves the clinical
fact, projection owns the Gan-surface conversion. If the LLM loses the count,
denominator, currentness, or seizure-frequency signal, candidate generation owns
the failure.

### Candidate Multiplicity Mechanism

The raw LLM often preserves four or more candidates on rows where there is a
single relatively direct gold answer. Examples include `source_row_index=79`,
`187`, `218`, `446`, `1880`, and `2681`.

This breadth may be useful for recall, especially in cluster and competing-state
rows. It should not be called a defect without a controlled downstream-selector
experiment. The unresolved question is whether broad candidate preservation
improves the whole system when paired with a strong selector, or whether it
creates regressions under fixed selection policy.

## Evidence-Selection Mechanics

LLM evidence selection is frequently exact and source-near, but exact evidence
does not guarantee a correct clinical state. The row artifact separates three
evidence-selection failure families:

| RQ2 bucket | Rows | Mechanism |
| --- | ---: | --- |
| `rq2_exact_evidence_but_wrong_state` | 48 | Exact text found, wrong state/projection chosen |
| `rq2_incomplete_typed_operands` | 12 | Useful text found, but state attributes are incomplete |
| `rq2_llm_correct_to_wrong` | 16 | LLM change regresses deterministic-correct rows |
| `rq2_llm_wrong_to_correct` | 7 | LLM change rescues deterministic-wrong rows |

### Exact Evidence, Wrong State

The clearest pattern is over-trusting a local phrase without enough state
metadata to decide whether it is current, decisive, count-like, or
benchmark-renderable.

- `source_row_index=1695`, gold `multiple per month`: both
  `claim_table_final_query` and `llm_candidate_selector_raw` selected exact
  current-month no-event evidence and projected seizure freedom, missing the
  broader active monthly burden.
- `source_row_index=1923`, gold `7 per 6 month`: the claim-table final query
  selected exact six-month evidence but rendered `2 to 3 per 6 month`, losing
  the sum across two drop attacks and five spasms.
- `source_row_index=3261`, gold `2 cluster per month, 4 per cluster`: the
  claim-table final query selected exact cluster evidence but projected one
  cluster per month rather than two.
- `source_row_index=3623`, gold `7 per week`: exact cluster evidence was found,
  but both claim-table and hybrid adjudicator surfaces retreated to `unknown`.

The failure is state selection over exact evidence, not evidence location.

### Incomplete Typed Operands

`llm_heavy_selected_fact` exposes the missing operands most clearly. It often
selects useful evidence but leaves the downstream renderer without a complete
state object.

- `source_row_index=743`, gold `multiple per week`, families
  `rate_bucket_or_denominator`, `benchmark_format_convention`: the selected
  fact says `multiple per shift`, which is a valid clinical fact. It should be
  classified as denominator-ambiguous and then projected by an explicit policy,
  rather than treated as an evidence-selection failure.
- `source_row_index=1706`, gold
  `multiple cluster per month, multiple per cluster`, families
  `cluster_burden`, `current_vs_historical`, `competing_semiologies`,
  `benchmark_format_convention`: the selected fact collapses a cluster burden
  row to `1 per 1 month`.
- `source_row_index=3118`, gold `seizure free for multiple month`, families
  `seizure_free_duration`, `current_vs_historical`: the selected fact captures
  seizure freedom but loses duration.
- `source_row_index=3507` and `3512`, gold `unknown`, families
  `unknown_boundary`, `diary_or_log_aggregation`, `current_vs_historical`,
  `uncertainty_or_ambiguity`: percent-change diary/log phrasing is recognized
  as relevant but not convertible into a complete benchmark state.

The schema needs explicit fields for denominator source, cluster axis, duration,
currentness, uncertainty, and aggregation method so faithful but ambiguous facts
can be projected transparently.

### Changed-Row Accounting

The artifact has seven LLM W->C rows, mostly unknown/boundary rescues:
`3356`, `6244`, `6321`, `10266`, `11259`, `14076`, and `15193`.

It also has 16 C->W rows, including:

- `source_row_index=190`, gold `1 per 4 week`: hybrid adjudication found the
  cluster sentence but changed the row to `unknown`.
- `source_row_index=2822`, gold `1 per day`: hybrid adjudication saw daily
  myoclonic jerks but became too conservative.
- `source_row_index=5767`, gold `1 per 1 to 2 week`: the LLM inverted "every
  one to two weeks" into `1-2 per week`.
- `source_row_index=10097`, gold `3 cluster per month, multiple per cluster`:
  the LLM flattened a cluster-axis answer to `3 per month`.

The change profile argues for selective use: LLM evidence/state changes are
useful for unknown-boundary rows, but unsafe as broad overrides of deterministic
correct frequency and cluster rows.

## Projection Mechanics

Projection is the main bottleneck. The artifact separates broad projection
failure from narrow gated projection success.

| RQ4 bucket | Rows | Mechanism |
| --- | ---: | --- |
| `rq4_projection_wrong_to_correct` | 25 | Gated projection corrects specific hard slices |
| `rq4_projection_correct_to_wrong` | 16 | Broad projection/adjudication regresses baseline-correct rows |
| `rq4_schema_near_projection_miss` | 24 | Structured state is close but final label is wrong |

### Narrow Projection Wins

`boundary_state_priority` corrected 12 rows in this compact artifact. The
mechanism is not general graph replacement; it is prioritizing an already
represented boundary or unresolved state over a misleading easy state.

Representative rows:

- `source_row_index=278`: projected `multiple per week` instead of a
  seizure-free overreach.
- `source_row_index=338`: projected `multiple per month` instead of treating
  cluster context as non-decisive.
- `source_row_index=744`: projected `multiple per week` from a most-weekday
  absence pattern.
- `source_row_index=3371`, `3469`, `3482`, and `3528`: projected `unknown`
  where the graph exposed unresolved/boundary states.

`graph_gated_month_bucket_duration` corrected 12 duration rows in this compact
artifact, including `3118`, `3137`, `4839`, `4842`, `4951`, `5040`, `5082`,
`5092`, `5110`, `5121`, `5136`, and `5141`. The credible mechanism is an
explicit duration gate that maps over-specific or underspecified seizure-free
duration states to the intended month bucket.

These wins support gated projection policies with named preconditions. They do
not support replacing the whole projection layer with the broad graph policy.

### Projection Regressions

The broad `state_graph_projection` rows show why representability is
insufficient:

- `source_row_index=278`, gold `multiple per week`, candidate
  `seizure free for multiple year`: a stale seizure-free node beats a current
  active-frequency node.
- `source_row_index=744`, gold `multiple per week`, candidate
  `1 per 8 week`: the policy chooses a lower or stale rate over most-weekday
  absence evidence.
- `source_row_index=2965`, gold `seizure free for 16 month`, candidate
  `4 to 5 per week`: historical active-frequency evidence beats current
  seizure freedom.
- `source_row_index=3371`, `3469`, `3482`, and `3534`, gold `unknown`: the
  policy turns boundary uncertainty into ordinary rate or seizure-free labels.

These are first-failure-owner examples for projection. The graph may contain a
useful node, but the selector lacks a reliable currentness, boundary, and
staleness policy.

### Schema-Near Misses

The schema-near rows are promising because the selected facts are often close
enough to expose the missing operation:

- `source_row_index=744`, gold `multiple per week`, selected fact
  `4 to 5 per 7 day`: the state is clinically close, but the renderer chooses
  an exact weekly count instead of the benchmark category.
- `source_row_index=959`, `960`, and `987`, gold `1 per 2 month`: bimonthly or
  interval evidence is represented but normalized to the wrong count/interval.
- `source_row_index=1694`, gold `1 cluster per 2 week, 3 per cluster`: the
  selected fact preserves cadence but drops per-cluster burden.
- `source_row_index=2731`, gold `1 per 2 week`: fractional rendering
  (`0.5 per 2 week`) is an adapter/rendering error over an otherwise near
  frequency state.
- `source_row_index=3137`, gold `seizure free for multiple month`: the schema
  confuses no definite seizure events with no seizure frequency reference.

These rows are better targets for a projection benchmark than another broad
validation aggregate because the missing operation is inspectable.

## Mechanism Verdict

1. Candidate generation: useful for preserving uncertain, boundary, cluster, and
   competing-state hypotheses; unsafe as a broad generator without a verifier
   because it adds burden and loses parser-ready ordinary rates.

2. Evidence selection: strong at exact source-near evidence; weak at deciding
   whether that evidence is current, decisive, complete, and benchmark-facing.
   Exact evidence should be treated as necessary but not sufficient.

3. Projection: credible gains come from narrow gated policies, especially
   boundary-state priority and month-bucket seizure-free duration. Broad graph
   projection is a negative result as a replacement policy but a useful source
   of first-failure-owner examples.

4. Hidden-family instrumentation: candidate-generation rows already explain
   family-specific behavior. Evidence and projection rows need full hidden-
   family propagation before the next report can make a clean by-family claim.

## Next Experiment Design

The next useful experiment is a frozen component-projection panel, not another
aggregate validation run:

- propagate hidden-family tags into every RQ2/RQ4 changed-row and schema-near
  row;
- add first-failure owner labels: candidate generation, evidence selection,
  typed-state representation, projection, rendering, or scorer/gold ambiguity;
- evaluate gated projection policies only on predeclared family slices, with a
  separate regression panel;
- keep deterministic top as a safety floor/comparator rather than an eligible
  RQ1-RQ4 answer;
- report W->C, C->W, exact evidence, and hidden-family precision for each gate.

Until that panel exists, the defensible answer is a mechanism map: LLMs help
most where ambiguity must be preserved, while deterministic or gated projection
is still required to render stable Gan labels.
