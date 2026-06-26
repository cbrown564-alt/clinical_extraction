# Gan 2026 State-Graph Ontology Stage C (Component Contribution)

Date: 2026-06-15

Stage C of the KG-grounded component-generation ladder. Feeds the `resolve_label` graph query as a fourth component to the frozen v0.9 consensus+fresh selector on the predeclared first-50 validation rows. Validation-only over `gan2026_split_v1`; no holdout rows, no model calls (the graph is rebuilt deterministically from the v3 section claim-table).

- Source claim-table: `experiments/gan2026_section_claim_table_validation50_gpt41mini_v3_2026-06-01.jsonl`
- v0.9 selector replay: `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_validation750_no_call_replay_2026-06-15.jsonl`
- Rebuilt graphs (replay artifact): `experiments/gan2026_state_graph_ontology_stage_c_component_contribution_2026-06-15_graphs.jsonl`
- Per-row accounting: `experiments/gan2026_state_graph_ontology_stage_c_component_contribution_2026-06-15_rows.jsonl`
- Graph builder: `llm-sg-stage-c-v3-raw-frequency-normalized`
- Rows: 50

## Experiment Unit

- Work class: hybrid selector / saved-output replay with a rebuilt graph component.
- Scorer: Gan-compatible Purist, unchanged.
- Baseline: v0.9 selected label per row.
- Stop rule (design §6): promote only with net component uplift and near-zero correct->wrong regression, gains localized to named edge/ontology mechanisms; reject if the graph layer breaks band cases the bare components already handled.

## Headline

- v0.9 selected Purist: 50/50
- Graph component standalone Purist: 30/50
- Graph final-kind counts: `{'frequency': 28, 'no_reference': 6, 'unknown': 9, 'unresolved_multiple': 7}`

## Arm 1 - component-pool coverage of the no-correct residual

- Pool ({deterministic, consensus, fresh}) already correct: 50/50
- No-correct pool rows (Arm 1 targets): 0
- Graph mints a correct component for a no-correct row: 0

The 11/750 no-correct residual is not in the first-50 slice: the pool covers every row, so Arm 1 has no targets here. This is a slice fact, not a negative on the mechanism - the component-starvation benefit must be evaluated where the residual lives, under its own predeclared protocol.

## Arm 2 - selection contribution under override postures

Final labels scored against the v0.9 selected baseline. `correct->wrong` is the design §6 kill metric.

| Posture | Overrides | Final Purist | W->C | C->W | Net | C->W bands |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `P1_unilateral` | 28 | 30/50 | 0 | 20 | -20 | band_daily:1, band_monthly:6, band_submonthly:3, band_weekly:10 |
| `P2_corroborated` | 5 | 50/50 | 0 | 0 | 0 | - |
| `P3_unknown_only` | 8 | 45/50 | 0 | 5 | -5 | band_monthly:2, band_weekly:3 |

Postures: `P1_unilateral` = graph overrides on any disagreement (effect bound); `P2_corroborated` = graph overrides only when an independent existing candidate (consensus or fresh) is monthly-equivalent to it; `P3_unknown_only` = graph overrides only when it resolves to `unknown` (the ADR 0017 clean-`unknown` arm).

## Boundary bands

| Band | Rows | v0.9 sel | Graph | No-correct | P1 C->W | P3 C->W |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `band_unknown` | 6 | 6 | 6 | 0 | 0 | 0 |
| `band_submonthly` | 12 | 12 | 9 | 0 | 3 | 0 |
| `band_monthly` | 11 | 11 | 5 | 0 | 6 | 2 |
| `band_weekly` | 18 | 18 | 8 | 0 | 10 | 3 |
| `band_daily` | 3 | 3 | 2 | 0 | 1 | 0 |

## Decision

`revise`

On the predeclared first-50 validation slice the v0.9 pool is already Purist-correct on 50/50 rows (0 no-correct), so Arm 1 has 0 residual targets and the graph mints a correct component for 0 of them - the component-starvation benefit cannot be demonstrated where the 11/750 residual does not live. In Arm 2 an unconditional graph component only regresses (P1 unilateral net -20, C->W 20; P3 unknown-only net -5, C->W 5) - the literature caveat made concrete. Only the independent-corroboration posture (P2) is regression-safe (W->C 0, C->W 0, net 0), and it is exactly neutral here. Stage C therefore does not promote the graph as an unconditional component: it must enter the selector under corroboration gating, and the no-correct-residual uplift must be evaluated on the rows where the residual actually lives under a separate predeclared protocol (no slice-shopping within Stage C).
