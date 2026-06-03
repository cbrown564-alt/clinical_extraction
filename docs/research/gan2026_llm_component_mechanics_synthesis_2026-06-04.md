# Gan 2026 LLM Component Mechanics Synthesis

Date: 2026-06-04

Status: final validation-development synthesis for RQ1, RQ2, and RQ4. This is
not a holdout-transfer, production, or benchmark-comparable claim.

## Answer

The component mechanics follow-up panel converts the RQ1/RQ2/RQ4 reset into
three final validation-development answers:

1. RQ1 candidate generation: the useful LLM role is selective proposal of
   boundary, uncertainty, seizure-free, and competing-state candidates. Broad
   LLM candidate generation is unsafe because candidate burden and C->W
   regressions overwhelm selective rescues.
2. RQ2 evidence selection: LLMs are strong exact-evidence locators, but unsafe
   broad clinical selectors. Exact text often exists before the system has the
   typed state needed to decide currentness, denominator, cluster axis,
   seizure-free duration, or uncertainty.
3. RQ4 projection: projection succeeds only when gated by explicit metadata and
   exact evidence. Broad graph projection and unconstrained LLM label projection
   are negative results.

The deterministic system remains the fixed comparator, safety floor, and
substrate for future work. It is not the research answer for RQ1/RQ2/RQ4.

## Source-Backed Panel Readout

Primary panel:
`experiments/gan2026_component_projection_followup_panel_2026-06-04.md`

The panel is a frozen validation-development replay over saved RQ2/RQ4
artifacts:

- 654 panel rows.
- 371 represented source rows.
- Split manifest: `gan2026_split_v1`.
- No scorer, prompt, model, projection-policy, or holdout change.

| Component | Rows | W->C | C->W | Exact evidence | Synthesis role |
| --- | ---: | ---: | ---: | ---: | --- |
| `boundary_state_priority` | 17 | 17 | 0 | 17 | Accepted gated projection mechanism. |
| `graph_gated_month_bucket_duration` | 250 | 18 | 0 | 250 | Accepted gated duration projection mechanism. |
| `competing_frequency_uncertainty` | 1 | 1 | 0 | 1 | Diagnostic only; too small for broad claim. |
| `claim_table_final_query` | 38 | 0 | 0 | 38 | Diagnostic selected-state/evidence surface. |
| `llm_heavy_selected_fact` | 95 | 0 | 0 | 94 | Diagnostic selected-fact surface. |
| `hybrid_adjudicator_raw` | 61 | 0 | 8 | 61 | Evidence locator only; label changes blocked. |
| `llm_candidate_selector_raw` | 61 | 7 | 49 | 61 | Selective rescue signal, rejected as broad selector. |
| `state_graph_projection` | 131 | 0 | 84 | 125 | Rejected broad replacement projection. |

First-failure ownership in the panel:

| Owner | Rows | Interpretation |
| --- | ---: | --- |
| `projection_policy` | 152 | Largest remaining bottleneck; mapping source-near states to Gan labels. |
| `typed_state_representation` | 109 | Schema lacks currentness, denominator, cluster, duration, or uncertainty fields. |
| `candidate_generation` | 78 | Boundary/uncertainty candidates still need selective LLM proposal. |
| `llm_clinical_selection` | 36 | LLM sometimes chooses the wrong clinical fact from exact text. |
| `projection` | 19 | Projection mechanics beyond named policy gaps. |
| `operand_exposure` | 18 | Selected evidence lacks complete computable operands. |
| `evidence_selection` | 1 | Pure text-location failure is rare in this panel. |

## RQ1 Final Answer

See:
`docs/research/gan2026_rq1_candidate_discovery_answer_2026-06-04.md`

The LLM component is useful when the note contains a tempting deterministic
state plus a competing uncertainty or boundary state. Examples include
conditional sleep-deprivation-only events (`3356`), breakthrough/stress
competition against seizure-free duration (`6077`), and device-log clusters
without counts (`10266`).

The LLM component is not a broad generator. In the RQ1 matrix,
`llm_candidate_selector_raw` recalled 642/739 represented rows with 0.985 exact
evidence, but produced 2,126 candidates and missed 94 rows recalled by
`deterministic_candidates_all`. In the follow-up panel, raw LLM selection has 7
W->C and 49 C->W changes.

Decision: keep LLM candidate generation as a selective rescue proposer under
strict evidence, burden, and metadata gates.

## RQ2 Final Answer

See:
`docs/research/gan2026_rq2_evidence_selection_answer_2026-06-04.md`

Evidence location is mostly not the failure. The panel has only one row owned
by pure `evidence_selection`. The broader RQ2 matrix shows the hybrid
adjudicator can attach 750/750 exact evidence spans and 750/750 valid source
ids on validation750, but label-changing use regresses deterministic-correct
rows.

The failure mode is exact evidence without a complete clinical state:

- local no-event phrases over-selected against previous-month active burden
  (`1695`);
- cluster evidence selected but cluster axis or per-cluster burden lost (`1317`,
  `1706`, `3261`);
- exact rate evidence selected but projected to `unknown` through uncertainty
  overreach (`190`, `2822`, `3623`);
- denominator/window or diary aggregation missing from selected operands.

Decision: use LLM evidence components as source-grounded evidence locators,
while blocking unconstrained label changes.

## RQ4 Final Answer

See:
`docs/research/gan2026_rq4_projection_answer_2026-06-04.md`

Projection is the dominant bottleneck and the clearest positive result. The
accepted mechanisms are narrow:

- `boundary_state_priority`: 17/17 W->C, 0 C->W.
- `graph_gated_month_bucket_duration`: 18/18 target corrections, 0 C->W, 0
  changed labels on the 232-row regression panel.

The rejected broad mechanisms are also clear:

- `state_graph_projection`: 84 C->W and 0 W->C in the panel.
- `hybrid_adjudicator_raw`: 8 C->W and 0 W->C in the panel.
- `llm_candidate_selector_raw`: 49 C->W despite 7 W->C.

The ACD decision log stabilizes projection policy for recurring ambiguous
representations. ACD-001 and ACD-002 classify projection-compatible phrases.
ACD-003 through ACD-010 are predeclared validation-development projection
policies for vague count adjectives, conditional-only triggers, relative-only
trends, diary date lists, non-epileptic events, qualitative summary overrides,
previous-month/current-month aggregation, and multi-semiology severity
prioritization.

Decision: accept only gated projection mechanisms with exact evidence and
changed-row accounting; reject broad graph or LLM projection replacement.

## Row-Level Mechanism Map

| Row | Gold | Mechanism | Component lesson |
| ---: | --- | --- | --- |
| 3356 | `unknown` | Conditional sleep-deprivation-only events. | LLM candidate proposal should preserve uncertainty; projection maps conditional-only to `unknown`. |
| 338 | `multiple per month` | Active cluster/frequency state competes with non-decisive context. | Boundary projection can recover when state exists. |
| 1165 | `5 to 7 per 3 week` | Recent travel-related focal cluster followed by seizure-free weeks. | Projection must preserve the recent counted window. |
| 1317 | `unknown, multiple per cluster` | Multiple events in a day without cadence. | Evidence/schema can be near-correct while adapter/projection misses benchmark shape. |
| 1363 | `3 per day` | Major tonic-clonic relapse competes with minor aura rate. | Projection policy must prioritize major relapsed semiology. |
| 1695 | `multiple per month` | Previous month active burden plus current month to date zero. | Short no-event window is not seizure freedom. |
| 2748 | `1 per month` | Clinician summary conflicts with derived long-period average. | Projection should prefer explicit current summary. |
| 3137 | `seizure free for multiple month` | No definite seizures; non-epileptic ED symptoms. | Candidate/evidence should preserve triage; projection maps to seizure-free. |

## Transfer Confidence

| Finding | Development confidence | Holdout-transfer confidence | Reason |
| --- | --- | --- | --- |
| Broad LLM/graph replacement is unsafe. | High | Moderate-to-high | Regressions are severe and mechanistically coherent. |
| LLM evidence location is strong. | High | Moderate | Exact evidence/source-id gates are simple, but replay is validation-only. |
| LLM candidate generation has selective boundary value. | Moderate | Low-to-moderate | Validation-derived slices need a frozen stress check. |
| Gated projection policies are useful. | High | Moderate | Precision is strong on target panels, but target panels are validation-derived. |
| Projection policy dominates remaining failures. | High | Moderate | Hidden-family breadth is strong, but still development evidence. |

## Decision

RQ1, RQ2, and RQ4 are answered for validation-development component mechanics.
They are not holdout-transfer answers.

The architecture direction is:

- deterministic/state-graph candidates as fixed substrate and safety floor;
- selective LLM candidate rescue for boundary/uncertainty states only;
- LLM evidence adjudication as exact span/source-id support only;
- gated projection policies with explicit metadata, exact evidence, and
  changed-row accounting;
- no broad LLM or graph replacement policy.

## Next Action

Move to RQ5: deterministic compilation/rendering from fixed selected states and
projection-policy decisions into Gan-compatible output. The RQ5 protocol should
hold candidate/evidence/projection state fixed and measure semantic drift,
benchmark-format rendering, exact evidence retention, and ACD-policy
ablatability.
