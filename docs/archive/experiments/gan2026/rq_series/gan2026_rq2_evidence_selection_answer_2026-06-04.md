> **Superseded for navigation —** canonical summary: [`COMPONENT_MECHANICS_CANON.md`](../COMPONENT_MECHANICS_CANON.md). Full detail retained below.

# Gan 2026 RQ2 Evidence-Selection Answer

Date: 2026-06-04

Status: final validation-development answer for LLM component mechanics. This is
not a holdout-transfer, production, or benchmark-comparable claim.

## Answer

RQ2 is answered for saved validation-development replay:

```text
LLMs are strong evidence locators, but unsafe broad clinical selectors.
```

The key RQ2 distinction is text location versus clinical decision ownership.
`hybrid_adjudicator_raw`, `claim_table_final_query`, and
`llm_heavy_selected_fact` usually select exact or source-near evidence. The
remaining failures usually occur after evidence selection: the component
under-specifies typed state, chooses the wrong clinical fact from exact text, or
projects a faithful but ambiguous fact into the wrong Gan label.

In the 2026-06-04 follow-up panel, `hybrid_adjudicator_raw` has 61/61 exact
evidence rows but 0 W->C and 8 C->W changes. `llm_candidate_selector_raw` has
61/61 exact evidence rows in the panel, with 7 W->C changes and 49 C->W
regressions. By contrast, `llm_heavy_selected_fact` and
`claim_table_final_query` are useful diagnostic evidence/state surfaces, but
they are not yet same-surface promoted selectors.

## Claim Boundary

Supporting artifacts:

- ``
- ``
- `experiments/gan2026_component_projection_followup_panel_2026-06-04.md`
- `experiments/gan2026_rq2_evidence_selection_matrix_2026-06-03.jsonl`
- `experiments/gan2026_llm_component_mechanics_rows_2026-06-03.jsonl`

All evidence comes from saved validation artifacts under `gan2026_split_v1`.
Locked holdout rows were not used for this answer.

## LLM Component Trade-Offs

| Component | Panel rows | W->C | C->W | Exact evidence | Interpretation |
| --- | ---: | ---: | ---: | ---: | --- |
| `hybrid_adjudicator_raw` | 61 | 0 | 8 | 61 | Excellent evidence locator; label changes are regressive. |
| `llm_candidate_selector_raw` | 61 | 7 | 49 | 61 | Finds text but unsafe as a selector. |
| `llm_heavy_selected_fact` | 95 | 0 | 0 | 94 | Diagnostic selected-fact surface; lacks source-id trace. |
| `claim_table_final_query` | 38 | 0 | 0 | 38 | Diagnostic claim-query surface with exact spans. |

The broader RQ2 matrix supports the same interpretation: the hybrid adjudicator
has 750/750 exact evidence and 750/750 valid source ids on validation750, but
its four broad-matrix label changes are all deterministic-correct regressions.
Exact evidence is necessary for promotion, but not sufficient for clinical
selection.

## Deterministic Baseline Role

The deterministic top candidate remains the fixed safety floor and comparator
for RQ2. It should not be re-described as an LLM evidence-selection answer. Its
role is to block unsafe label changes while allowing LLM components to attach
auditable evidence spans and source ids.

## Row-Level Mechanism Examples

`source_row_index=190`, gold `1 per 4 week`: the hybrid adjudicator found exact
cluster evidence but changed the answer to `unknown`. This is over-conservative
state interpretation after correct evidence location.

`source_row_index=2822`, gold `1 per day`: exact evidence for daily myoclonic
jerks was present, but the changed label regressed to `unknown`.

`source_row_index=3623`, gold `7 per week`: exact variable-cluster evidence was
selected, but operand exposure and projection retreated to `unknown`.

`source_row_index=1695`, gold `multiple per month`: LLM selectors found exact
"current month to date: no events" evidence but over-selected that local phrase,
missing the previous-month active burden. This is clinical selection over exact
text, not evidence search.

`source_row_index=1317`, gold `unknown, multiple per cluster`: the claim-table
surface represented `1 cluster per 1 day, multiple per cluster`, which is close
to the source fact but not benchmark-equivalent. The failure belongs to typed
state/projection and adapter rendering rather than text location.

## Hidden-Family Readout

The follow-up panel assigns major evidence-adjacent failures to later component
owners:

- `typed_state_representation`: 109 rows, including 67
  `competing_semiologies`, 53 `current_vs_historical`, 42
  `rate_bucket_or_denominator`, 30 `seizure_free_duration`, and 25
  `cluster_burden`.
- `llm_clinical_selection`: 36 rows, including 28 `current_vs_historical`, 19
  `competing_semiologies`, 15 `unknown_boundary`, 15 `seizure_free_duration`,
  and 15 `uncertainty_or_ambiguity`.
- `operand_exposure`: 18 rows, including 17 `current_vs_historical`, 10
  `seizure_free_duration`, and 9 `unknown_boundary`.

These rows show that LLMs often locate the right neighborhood, but the evidence
surface lacks the attributes required for currentness, cluster-axis,
denominator, seizure-free duration, and uncertainty arbitration.

## Transfer Confidence

| Finding | Development confidence | Holdout-transfer confidence | Reason |
| --- | --- | --- | --- |
| LLM evidence location can be exact and source-traced. | High | Moderate | Exact substring/source-id constraints are simple, but evidence is validation replay. |
| Broad LLM clinical selection is unsafe. | High | Moderate-to-high | C->W regressions appear across raw selector and adjudicator surfaces. |
| Typed operands are the main evidence-to-state gap. | High | Moderate | The same missing attributes recur across clinical hidden families. |

## Metadata/Instrumentation Gaps

- `llm_heavy_selected_fact` lacks selected source ids, so it cannot support an
  exact-source-id promotion claim.
- Claim-table and selected-fact diagnostics are not full validation750
  same-row replacements.
- The evidence matrix needs complete hidden-family tags for every copied
  evidence/projection row.
- RQ2 does not resolve projection-compatible phrase mapping; that belongs to
  RQ4/RQ5.

## Decision

RQ2 is answered for validation development:

- Promote LLM evidence components only as evidence locators under exact span and
  source-id gates.
- Block unconstrained LLM label changes.
- Treat claim-table and selected-fact outputs as diagnostic state/evidence
  surfaces until source-id and operand completeness improve.

## Next Action

Use exact LLM evidence spans to support RQ4/RQ5, but keep clinical label changes
behind predeclared projection gates with W->C/C->W accounting.
