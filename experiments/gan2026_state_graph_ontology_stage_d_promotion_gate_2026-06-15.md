# Gan 2026 State-Graph Ontology Stage D (Promotion Gate)

Date: 2026-06-15

Stage D of the KG-grounded component-generation ladder. Wires the **P2-gated** `resolve_label` graph query as a fourth component to the frozen v0.9 consensus+fresh selector on a **predeclared 250-row slice that contains all 11/750 no-correct residual rows**. Validation-only over `gan2026_split_v1`; no holdout rows, no model calls (the graph is rebuilt deterministically from the v4 section claim-table).

- Predeclared slice: 11 no-correct residual rows UNION the first 239 non-residual validation rows in source_row_index order; 250 rows; deterministic, reproducible, residual-inclusive, source-ordered (no slice-shopping).
- Source claim-table: `experiments/gan2026_section_claim_table_validation750_gpt41mini_v4_2026-06-01.jsonl`
  - v4 at validation750 scale - the only no-call source covering the residual; v3 (Stage A/B/C) was never run past the first 250 rows. Declared confound, held constant across the whole Stage D slice.
- v0.9 selector replay: `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_validation750_no_call_replay_2026-06-15.jsonl`
- Residual audit: `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_residual_component_generation_audit_2026-06-15.json`
- Rebuilt graphs (replay artifact): `experiments/gan2026_state_graph_ontology_stage_d_promotion_gate_2026-06-15_graphs.jsonl`
- Per-row accounting: `experiments/gan2026_state_graph_ontology_stage_d_promotion_gate_2026-06-15_rows.jsonl`
- Graph builder: `llm-sg-stage-d-v4-raw-frequency-normalized`
- Promotion posture: `P2_corroborated`
- Rows: 250

## Experiment Unit

- Work class: hybrid selector / saved-output replay with a rebuilt graph component, on a predeclared residual-inclusive slice.
- Scorer: Gan-compatible Purist, unchanged.
- Baseline: v0.9 selected label per row.
- Promotion posture: `P2_corroborated` (graph overrides only when an independent existing candidate is monthly-equivalent) - the only regression-safe posture from Stage C.
- Stop rule (design §6): the kill metric is P2 correct->wrong; promote only with net uplift, residual minting, and no band_weekly/band_unknown regression; reject if P2 itself regresses at scale.

## Headline

- v0.9 selected Purist: 238/250
- Graph component standalone Purist: 99/250
- Graph final-kind counts: `{'frequency': 64, 'no_reference': 70, 'seizure_free': 2, 'unknown': 92, 'unresolved_multiple': 22}`

## Arm 1 - component-pool coverage of the no-correct residual

- Pool ({deterministic, consensus, fresh}) already correct: 239/250
- No-correct pool rows in slice: 11
- Predeclared residual rows in slice: 11 (`[5534, 6321, 6368, 6571, 9937, 9943, 11216, 11254, 11272, 13209, 14025]`)
- Graph mints a correct component for a predeclared residual row: **7/11** (`[5534, 6321, 6368, 6571, 11254, 11272, 14025]`)
- Graph mints a correct component for any no-correct slice row: 7/11
- Of those, P2 (promotion posture) *recovers* at selection time: **0/7** (`[]`) - corroboration cannot fire where every other component is wrong, so component availability (Arm 1) exceeds realized selection recovery (Arm 2).

Residual minting by audit category:

| Audit category | Residual rows | Minted correct |
| --- | ---: | ---: |
| `cluster_burden_component_failure` | 2 | 0 |
| `highest_semiology_or_denominator_conflict` | 1 | 0 |
| `last_event_or_seizure_free_overinfer_unknown` | 6 | 5 |
| `unknown_over_quantified_rate` | 5 | 5 |

## Arm 2 - selection contribution under override postures

Final labels scored against the v0.9 selected baseline. `correct->wrong` is the design §6 kill metric; `P2_corroborated` is the promotion posture.

| Posture | Overrides | Final Purist | W->C | C->W | Net | C->W bands |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `P1_unilateral` | 188 | 99/250 | 8 | 147 | -139 | band_daily:14, band_monthly:35, band_submonthly:11, band_weekly:50, band_zero:37 |
| `P2_corroborated` (promotion) | 28 | 239/250 | 1 | 0 | 1 | - |
| `P3_unknown_only` | 90 | 174/250 | 7 | 71 | -64 | band_daily:5, band_monthly:15, band_submonthly:5, band_weekly:23, band_zero:23 |

### P2 changed-label precision by band (design §5 / spec §5)

Of the rows P2 overrode, the share that landed Purist-correct, per band. `band_weekly` and `band_unknown` are the val->test regression surface.

| Band | P2 overrides | Correct | Precision |
| --- | ---: | ---: | ---: |
| `band_unknown` | 27 | 26 | 0.96 |
| `band_monthly` | 1 | 0 | 0.00 |

## Boundary bands

| Band | Rows | v0.9 sel | Graph | No-correct | P2 ovr | P2 W->C | P2 C->W |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `band_zero` | 37 | 37 | 0 | 0 | 0 | 0 | 0 |
| `band_unknown` | 44 | 35 | 43 | 8 | 27 | 1 | 0 |
| `band_submonthly` | 26 | 25 | 14 | 1 | 0 | 0 | 0 |
| `band_monthly` | 51 | 49 | 14 | 2 | 1 | 0 | 0 |
| `band_weekly` | 70 | 70 | 20 | 0 | 0 | 0 | 0 |
| `band_daily` | 22 | 22 | 8 | 0 | 0 | 0 | 0 |

## v3<->v4 cross-check (overlap row 5534)

- v3 graph: `unknown` (unknown); v4 graph: `unknown` (unknown); Purist-equivalent: True.
  The v3->v4 extractor change is a declared Stage D confound (only v4 covers the residual). On the single overlap row the two extractors resolve to the same Purist class.

## Decision

`promote_clears_validation_ladder`

Stage D wires the P2-gated graph component at 250-row scale on a predeclared slice containing all 11 no-correct residual rows. Arm 1: the graph mints a Purist-correct component for 7/11 predeclared residual rows (and 7/11 of all no-correct rows in the slice). Arm 2 (P2 corroborated, the only Stage C survivor): W->C 1, C->W 0 (the §6 kill metric), net 1; P2 regression bands {}. Effect bounds: P1 unilateral net -139 (C->W 147), P3 unknown-only net -64 (C->W 71). P2 is regression-safe (0 C->W, no band_weekly/band_unknown regression) with net uplift and band_unknown override precision 26/27=0.96, and the generator covers 7/11 of the component-starvation residual (the branch's raison d'etre), so it clears the validation ladder. Honest realized-vs-available gap: of those 7 newly-minted residual components P2 *recovers* only 0 at selection time, because corroboration cannot fire where every other component is wrong (the defining property of the no-correct residual). The unrealized residual uplift is a downstream selection-posture problem (a corroboration-free trust rule for the graph's clean unknown that avoids P3's regressions), not a generator failure, and is the explicit next question. This is NOT a holdout authorization: test450 remains locked and requires a separate frozen protocol (design §4) that must weigh whether the realized selection uplift justifies the spend.
