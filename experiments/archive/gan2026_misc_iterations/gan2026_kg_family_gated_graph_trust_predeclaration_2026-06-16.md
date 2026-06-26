# Gan 2026 KG Family-Gated Graph-Trust (P2.5) — Predeclaration

Date: 2026-06-16
Cycle: C7 (Gan 2026 F1 dynamic workflow)
Owner: rule-designer -> experiment-runner (orchestrator session)

## Context (why this experiment exists)

KG Stage D (cycle C4) relocated the component wall from GENERATION to
SELECTION. On a predeclared residual-inclusive validation250 slice, the
KG-grounded `resolve_label` generator mints a Purist-correct, regression-free
competing component for **7/11** no-correct residual rows
(`[5534, 6321, 6368, 6571, 11254, 11272, 14025]`), localized in the residual
*audit* to the families `unknown_over_quantified_rate` (5/5) and
`last_event/seizure_free_overinfer` (5/6), 0/2 cluster, 0/1 semiology.

Under the only regression-safe Stage D selector posture (P2 corroborated: the
graph overrides only when consensus or fresh is monthly-equivalent), realized
recovery of those 7 minted residual rows is **0/7**, because corroboration
cannot fire where every other component is wrong — the defining property of the
no-correct residual. P1 (unilateral) and P3 (unknown-only) over-fire hard
(net -139 / -64 on the slice). The open question Stage D left: is there a
**corroboration-free** trust rule that harvests those 7 rows without
re-introducing P3's genuine-rate regressions?

## The posture under test — P2.5 (family-gated graph trust)

P2.5 trusts/harvests the graph's withholding component **without** requiring
consensus/fresh corroboration, but **only when a forward-observable "family"
signal fires** that is intended to localize to the high-precision families
(`unknown_over_quantified_rate`, `last_event/seizure_free_overinfer`).

Concretely, P2.5 overrides the selected baseline with the graph component
(`graph_label`) on a row iff ALL of:

1. The graph resolves to a **withholding kind**: `graph_kind ∈ {unknown,
   no_reference}` (the kinds the over-reading families resolve to).
2. The graph component **differs** from the selected baseline (it is an actual
   change).
3. The **family gate** fires. We predeclare the family gate as the strongest
   forward-observable proxy available for the two high-precision families:
   **no admitted node in the dual-validated graph carries a quantified semantic
   kind** (`frequency` or `seizure_free`) — i.e. the graph has no surviving
   quantifiable evidence, so withholding is the ontology-grounded resolution
   rather than a discarded rate. This is the corroboration-free analogue of
   "the ontology guard / withholding families fired", computed entirely from the
   saved graph (no model calls, no gold).

Reported alongside, as effect bounds and as an honest discriminability probe:
P2.5a = the same gate additionally requiring the ontology over-inference guard
(`over_inference_out_of_unknown:<shape>`, shape in the unknown-only family set)
to have rejected ≥1 uncurated node. This is the literal reading of "ontology-
guard families".

P2.5 is compared explicitly to P1/P2/P3 (recomputed on the same slice) on
overrides / W->C / C->W / net / per-band, so we can see whether family-gating is
the regression-safe harvester P2 cannot be.

## Trusted families / guards

Intended trust set: the audit families `unknown_over_quantified_rate` and
`last_event/seizure_free_overinfer`. Forward proxy actually computable at
selection time: withholding `graph_kind` + no surviving quantified admitted
node (P2.5), optionally + ontology over-inference rejection on an unknown-only
shape (P2.5a). NOT trusted: cluster_burden, semiology/denominator (0 minted).

## Expected effect (predeclared)

Target: the 7 minted residual rows
(`[5534, 6321, 6368, 6571, 11254, 11272, 14025]`), all gold `unknown`-band. If
the forward family signal cleanly localizes to those rows, P2.5 should harvest
W->C ≈ 6–7 with C->W ≈ 0 and be gap-robust. If instead the forward signal also
fires on genuine-rate rows whose gold is a real quantified rate or seizure-free
duration (which withholding would destroy), P2.5 leaks C->W in genuine bands —
the P3 failure mode — and must be rejected or tightened.

## Stop rule (gap-robust + ZERO genuine-rate regression)

- PROMOTE only if: gap_robust=True (held-out-band CV, no boundary band
  regresses, changed-label precision clears the bar) AND **zero** genuine-rate
  regressions, i.e. C->W = 0 in every non-`band_unknown` boundary band
  (`band_zero/submonthly/monthly/weekly/daily`).
- If the family gate still leaks genuine rates like P3 did (any genuine-band
  C->W > 0, or not gap_robust): **TIGHTEN the family gate, do not loosen.** If no
  forward-observable tightening separates the harvest set from the genuine-rate
  casualties, the honest decision is **REJECT** P2.5 — the family localization is
  a post-hoc gold property, not a selection-time signal.
- Do NOT read or run test450 unless the validation posture is gap-robust with
  zero genuine-rate regressions AND a frozen test KG component exists. (Scoping
  note: there is no `gan2026_section_claim_table_test450_v4` artifact on disk; a
  test KG component would require a live gpt-4.1-mini claim-extraction run over
  450 test rows. That is a sizable live/graph build, not a no-call replay.)

## Evidence validity

Validation-only no-call replay over the existing Stage D predeclared 250-row
residual-inclusive slice. Graphs are reused from the frozen Stage D graphs
artifact; dual-validation/`resolve_label` recomputed deterministically (no model
calls). The v0.9 selected/consensus/fresh components and baseline come from the
saved v0.9 replay. Gold labels used only for post-hoc Purist scoring and the
honest discriminability probe. No holdout rows are read.
