# Gan 2026 KG Family-Gated Graph-Trust (P2.5)

Date: 2026-06-16

C7 of the Gan 2026 F1 workflow. Tests the untried corroboration-free lever P2.5 (family-gated graph trust) over the frozen Stage D 250-row residual-inclusive validation slice. No-call replay: graphs reused from the Stage D graphs artifact; dual-validation recomputed deterministically; v0.9 components/baseline from the Stage D rows artifact. Gold used only for post-hoc Purist scoring.

- Predeclaration: `experiments/gan2026_kg_family_gated_graph_trust_predeclaration_2026-06-16.md`
- Source slice: `experiments/gan2026_state_graph_ontology_stage_d_promotion_gate_2026-06-15_rows.jsonl (Stage D predeclared 250-row residual-inclusive slice)`
- Rows: 250
- v0.9 selected baseline Purist: 238/250
- Minted residual targets (gold-`unknown`): [5534, 6321, 6368, 6571, 11254, 11272, 14025]

## Posture comparison (selected baseline -> posture override)

`P2.5` = withholding graph_kind + no admitted quantified node (corroboration-free family gate). `P2.5a` = P2.5 + ontology over-inference guard fired. `genuine C->W` = C->W in any non-`band_unknown` boundary band (the stop-rule kill metric).

| Posture | Overrides | Final Purist | W->C | C->W | Net | genuine C->W | harvested minted |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `P1_unilateral` | 188 | 99/250 | 8 | 147 | -139 | 147 | [5534, 6321, 6368, 6571, 11254, 11272, 14025] |
| `P2_corroborated` | 28 | 239/250 | 1 | 0 | 1 | 0 | [] |
| `P3_unknown_only` | 90 | 174/250 | 7 | 71 | -64 | 71 | [5534, 6321, 6571, 11254, 11272, 14025] |
| `P2_5_family_gated` | 149 | 125/250 | 8 | 121 | -113 | 121 | [5534, 6321, 6368, 6571, 11254, 11272, 14025] |
| `P2_5a_guarded` | 3 | 235/250 | 0 | 3 | -3 | 3 | [] |

## P2.5 gate discriminability (honest probe)

- Rows the P2.5 gate fires on: 149
- Their gold-band breakdown: `{'band_daily': 10, 'band_monthly': 32, 'band_submonthly': 9, 'band_unknown': 25, 'band_weekly': 39, 'band_zero': 34}`

The gate fires on both the harvestable gold-`band_unknown` rows and genuine-rate rows. Those genuine-rate rows are feature-identical to the harvest set on every forward-observable graph signal (graph_kind, admitted node kinds, missing-variable flags, claim count); only the hidden gold band distinguishes them.

## P2.5 held-out-family CV

- gap_robust: **False**
- aggregate net Purist gain: -113
- regressing held-out bands: ['band_zero', 'band_submonthly', 'band_monthly', 'band_weekly', 'band_daily']
- worst held-out fold: {'family': 'band_weekly', 'net_purist_gain': -39}

## P2.5 per-band transitions

| Band | Rows | Overrides | W->C | C->W |
| --- | ---: | ---: | ---: | ---: |
| `band_zero` | 37 | 34 | 0 | 34 |
| `band_unknown` | 44 | 25 | 8 | 0 |
| `band_submonthly` | 26 | 9 | 0 | 8 |
| `band_monthly` | 51 | 32 | 0 | 30 |
| `band_weekly` | 70 | 39 | 0 | 39 |
| `band_daily` | 22 | 10 | 0 | 10 |

## Decision

`reject`

P2.5 leaks 121 genuine-rate regression(s) (gap_robust=False). The forward family gate fires on genuine-rate rows indistinguishable from the harvest set on every observable graph feature; the family localization is a post-hoc gold property, not a selection-time signal. Per the stop rule, tightening on a forward feature is impossible here, so the honest decision is reject (same structural wall Stage D identified).
