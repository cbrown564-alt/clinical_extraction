# Gan 2026 LLM Component Mechanics Synthesis

Date: 2026-06-03

Protocol:
`docs/research/gan2026_llm_component_mechanics_protocol_2026-06-03.md`

## Answer

The first-pass RQ1/RQ2/RQ4 reports are diagnostic baseline audits, not completed
research answers. Once deterministic candidates are removed as eligible answers,
the useful signal is narrower and more interesting:

- LLM candidate generation is not a broad replacement, but it exposes boundary
  and uncertainty states that deterministic rules often collapse into
  seizure-free or simple frequency labels.
- LLM evidence selection is often source-near and exact, but exact evidence is
  frequently not clinically decisive without better state attributes.
- LLM/graph projection has selective value on explicit boundary and duration
  mechanisms, but broad projection remains fragile when current-versus-
  historical, competing semiology, cluster, and uncertainty decisions are mixed.

This is a validation-development mechanics synthesis, not a holdout-transfer or
benchmark claim.

## Source-Backed Readout

RQ1 candidate generation, validation replay:

| Generator | Source rows | Candidates | Recalled rows | Recall | Exact evidence |
| --- | ---: | ---: | ---: | ---: | ---: |
| `llm_candidate_selector_raw` | 739 | 2,126 | 642 | 0.869 | 0.985 |
| `llm_selected_state_or_evidence` | 250 | 250 | 222 | 0.888 | 0.956 |

The raw LLM candidate selector found 11 rows recalled by the LLM but not by
`deterministic_candidates_all`; it missed 94 rows recalled by
`deterministic_candidates_all`. It produced at least four candidates on 136
source rows. This is the core RQ1 trade-off: the LLM has real rescue behavior,
but the burden and misses are too large for a broad generator.

RQ2 evidence selection, validation replay:

| LLM component | Rows | Judged | Purist correct | Exact evidence | Source-id valid | Changed | W->C | C->W |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `hybrid_adjudicator_raw` | 750 | 750 | 693 | 750 | 750 | 4 | 0 | 4 |
| `llm_candidate_selector_raw` | 739 | 161 | 107 | 727 | 738 | 724 | 7 | 49 |
| `llm_heavy_selected_fact` | 250 | 240 | 203 | 242 | 0 | 0 | 0 | 0 |
| `claim_table_final_query` | 250 | 242 | 223 | 246 | 248 | 0 | 0 | 0 |

The key point is not that deterministic top is safer. The key point is that LLM
evidence exactness is high while clinical state conversion remains weak. The
evidence selector often points at the right neighborhood but does not reliably
decide count, denominator, temporality, certainty, or boundary status.

RQ4 projection, validation and diagnostic replay:

| Component | Rows | Judged | Correct | Changed | W->C | C->W | Main surface |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `boundary_state_priority` | 42 | 42 | 17 | 20 | 17 | 0 | projection hard slice |
| `graph_gated_month_bucket_duration` | 250 | 250 | 199 | 18 | 18 | 0 | duration target plus regression panel |
| `llm_heavy_selected_fact` | 250 | 240 | 203 | 0 | 0 | 0 | validation25 |
| `claim_table_final_query` | 248 | 242 | 223 | 0 | 0 | 0 | validation25 |
| `hybrid_adjudicator_raw` | 750 | 750 | 693 | 4 | 0 | 4 | validation750 |
| `state_graph_projection` | 750 | 750 | 655 | 49 | 0 | 42 | validation750 |

The graph policies are most useful when the projection problem is explicit:
boundary-state priority corrected 17/42 projection hard-slice rows with no
regressions on that slice, and graph-gated month-bucket duration corrected 18/18
target duration rows with no changed labels on its 232-row regression panel.
That is selective mechanism evidence, not a broad replacement result.

## Row-Level Mechanisms

### RQ1: LLM Candidate Generation

`source_row_index=3356`, gold `unknown`, hidden families
`unknown_boundary`, `seizure_free_duration`, `uncertainty_or_ambiguity`.

The raw LLM candidate selector produced an `unknown` candidate from evidence
about events occurring only after curtailed sleep and another seizure-free
candidate from "no events reported when sleep has been adequate." The
deterministic candidate set collapsed the row to a seizure-free duration. The
mechanism is useful: the LLM represented conditional uncertainty instead of
treating the absence statement as a clean seizure-free state.

`source_row_index=6077`, gold `unknown`, hidden families
`unknown_boundary`, `seizure_free_duration`, `uncertainty_or_ambiguity`.

The LLM produced both a seizure-free candidate from "no episodes in the
preceding eight months" and unknown candidates from a breakthrough travel event
and a two-year sleep/stress pattern. The deterministic candidate set selected
the eight-month seizure-free phrase. The useful mechanism is boundary
competition: the LLM preserved incompatible candidate states instead of reducing
the row to the easiest duration phrase.

`source_row_index=10266`, gold `unknown`, hidden families `unknown_boundary`,
`cluster_burden`, `diary_or_log_aggregation`, `uncertainty_or_ambiguity`.

The LLM exposed "Uncertain frequency; device logs suggest short clusters without
counts" and the family's uncertainty about whether staring episodes correspond
to device alerts. The deterministic candidate set selected `1 per 5 day`. This
is a candidate-generation win because the LLM recognized that a count-like
device interval was not a decisive clinical seizure frequency.

Failure mode: on rows such as `source_row_index=278`, `744`, and `1357`, the
deterministic candidate set captured explicit benchmark frequency text while the
raw LLM produced looser labels such as "multiple times per week", "frequent", or
"seizure". The LLM was often semantically near but failed the benchmark grammar
or denominator binding needed for candidate recall.

Burden mode: rows such as `source_row_index=79`, `187`, `212`, `218`, and `446`
show the raw LLM preserving multiple plausible states: current rate, clusters,
historical rates, rare event types, and non-frequency context. That breadth is
useful for recall but must be paired with a ranker or verifier; otherwise it
creates too many downstream projection decisions.

### RQ2: LLM Evidence Selection

`hybrid_adjudicator_raw` produced 750/750 exact evidence and valid source ids,
but its four changed labels were all deterministic-correct regressions. The
row-level pattern is over-abstraction from exact evidence:

- `source_row_index=190`: evidence described clusters every four weeks, but the
  candidate changed from `1 per 4 week` to `unknown`.
- `source_row_index=2822`: evidence included a daily myoclonic jerk, but the
  candidate changed from `1 per day` to `unknown`.
- `source_row_index=3623`: evidence described variable clusters over three
  months, but the candidate changed from `7 per week` to `unknown`.
- `source_row_index=4116`: evidence described events occurring every one to two
  days on workdays, but the candidate collapsed to `1 per day`.

The mechanism is not bad evidence selection. It is uncertainty over-projection:
the LLM can find the sentence, then becomes too conservative or loses the
benchmark denominator.

`llm_candidate_selector_raw` has the opposite profile. It produced seven W->C
changes, including boundary rows such as `3356`, `6244`, `6321`, and `10266`,
but also 49 C->W changes. On `source_row_index=1695`, it selected a current
"no events recorded" phrase and called the row seizure-free while the gold was
`multiple per month`. On `source_row_index=5767`, it changed
`1 per 1 to 2 week` into `1-2 per week`. These are projection/normalization
errors from plausible evidence, not source-nearness failures.

`llm_heavy_selected_fact` and `claim_table_final_query` are the clearest schema
signals. Their exact-evidence rates are high, and their failures often identify
the missing state operation:

- `source_row_index=744`: selected most-weekday absence evidence but rendered
  `4 to 5 per 7 day` instead of benchmark `multiple per week`.
- `source_row_index=959`: selected bimonthly/cluster evidence but projected
  `2 per 1 to 2 month` instead of `1 per 2 month`.
- `source_row_index=1317`: claim-table extraction represented a cluster as
  `1 cluster per 1 day, multiple per cluster`, close to the gold
  `unknown, multiple per cluster` but not benchmark-equivalent.

The LLM is giving structured clinical facts that the benchmark adapter cannot
yet safely collapse.

### RQ4: LLM And Graph-Assisted Projection

`boundary_state_priority` corrected rows where the graph already exposed the
right competing state:

- `source_row_index=278`: baseline projected seizure-free, policy selected
  `multiple per week`.
- `source_row_index=338`: baseline had no frequency reference, policy selected
  `multiple per month`.
- `source_row_index=744`: baseline selected `1 per 8 week`, policy selected
  `multiple per week`.

The mechanism is strong but narrow: when a boundary or unresolved-multiple node
exists, prioritizing that node can prevent seizure-free or stale-frequency
overreach.

`graph_gated_month_bucket_duration` corrected target duration rows such as
`3118`, `3137`, `4839`, `4842`, and `4951` from over-specific or year-bucketed
seizure-free labels to `seizure free for multiple month`. It also made no
changed labels on the 232-row regression panel. This is a clean selective
projection mechanism because the gate is explicit and the regression panel is
separate.

Broad `state_graph_projection` remains a negative result as a replacement
projection policy: it created 42 C->W regressions and no W->C gains on
validation750. Its failures, however, are useful instrumentation. They show that
representing nodes is easier than choosing among current, stale, seizure-free,
cluster, and competing-semiology nodes.

## Mechanistic Conclusions

1. LLM candidate generation is most useful for uncertainty and boundary recall,
   not for broad frequency extraction.

2. LLM evidence selectors often find exact text, but exact text is not enough.
   The bottleneck is deciding whether the text is current, decisive, count-like,
   seizure-type relevant, and benchmark-renderable.

3. The most credible projection gains are gated graph policies with explicit
   metadata, not broad graph replacement and not unconstrained LLM label changes.

4. Claim-table and selected-fact schemas are promising because their failures
   are interpretable: they expose clinical facts that need a better projection
   and rendering contract.

5. The next useful experiment is not another validation aggregate. It is a
   row-level LLM mechanism matrix that labels each failure as candidate
   generation, evidence selection, state representation, projection, rendering,
   or scorer/gold ambiguity.

## Claim Boundary

This synthesis uses saved validation and diagnostic replay artifacts. It does
not tune on locked test rows, make a benchmark claim, or promote an architecture.
It supersedes the deterministic-default conclusions in the first-pass RQ1/RQ2/RQ4
reports only as research-question interpretation; the underlying matrices remain
valid diagnostic artifacts.

## Decision

RQ1/RQ2/RQ4 are not answered as completed component questions. They are open as
LLM mechanics questions.

The next action is to build a compact row-level LLM mechanism artifact over the
representative examples above plus systematic same-row slices:

- LLM candidate wins over deterministic misses;
- LLM exact-evidence-but-wrong rows;
- LLM changed W->C and C->W rows;
- graph projection W->C rows;
- broad graph C->W rows;
- claim-table and selected-fact schema-near misses.
