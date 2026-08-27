# 0046: ExECT primary method comparison uses one-call Sol peers

Date: 2026-08-01  
Status: accepted  
Amends: paper-facing ExECT method identity implied by
[canon scoring](../canon/04_scoring.md) and
[paper provenance](../canon/10_paper_provenance.md)  
Does not change: [decision 0040](0040-final-exect-llm-with-rules-family-ownership.md)
family ownership, [decision 0041](0041-single-call-exect-model-comparison.md)
one-call architecture, or [decision 0045](0045-exect-default-policy-not-joint-combined.md)
`default` / `default` assembly

## Decision

The paper's **primary ExECT three-method comparison** uses:

| Method | Primary fill |
| --- | --- |
| Rules only | Sol-matched four-family clinical fact recovery (`clinical_headline` / `headline_target`) on deterministic rules-only predictions restricted to the four key families (all-nine extractors may run; non-key entities are excluded from this peer score only). Not the older multi-entity `clinical_recovery_scorecard` overall. |
| LLM only | GPT-5.6 Sol `raw_candidate` / `raw_lane_score` from the one-call four-family pipeline |
| LLM with rules | GPT-5.6 Sol Selected ExECT hybrid (one-call, decision 0040 / 0041, `default` / `default`) |

The comparison score is matched four-family clinical fact recovery (Diagnosis,
Seizure Frequency, Prescription, Investigations). The nine-entity
paper-derived rules-only metrics remain a **secondary** published-metric
reference, not the three-method peer score.

Historical ExECT hybrid control (`v08`, clinical fact F1 `0.9202` on `dev140`;
superseded value `0.9189`, pre the disclosed Diagnosis subsumption-guard fix,
commit `41165adc`, 2026-08-11)
is **demoted** from the primary hybrid method row. It may appear only in a
**secondary results table** with an explicit ownership caveat: it does not
satisfy decision 0040.

GEPA GPT-4.1-mini LLM-only (`0.7393`) remains a **historical / negative
architecture comparator**, not the primary peer of Sol hybrid.

## Split policy

- `dev140`: all three primary fills; rules-only is a no-call four-family
  re-score of retained deterministic outputs (row-level analysis permitted).
- `test60`: all three primary fills once aggregate-safe sources exist.
  - Sol LLM-only and Sol hybrid stage scores already exist in sealed
    aggregates; before the paper cites holdout LLM-only cells, promote a
    **public aggregate-only six-model `test60` stage panel** under
    `experiments/` with at least `raw_lane_score` vs final
    clinical fact recovery for all six models (primary table still cites Sol).
  - Rules-only four-family clinical fact recovery on `test60` is materialized as
    aggregate-only scoring (no row inspection). The selected fill after the
    2026-08-15 Investigations result-binding remasure is overall F1 `0.7918`
    ([artifact](../../experiments/exectv2_rules_only_four_family_clinical_headline_test60_20260815.json)).
    The 2026-08-01 fill `0.7154` remains the historical Decision 0046
    baseline.

Do not inspect sealed `test60` rows. Do not treat the Gan six-model LLM-only
`test450` panel as ExECT evidence.

## Why

The pipeline understandability review (finding 7) found that the manuscript's
ExECT three-method strip mixed incompatible experiments: nine-entity
rules-only published metrics, GEPA mini LLM-only, and historical `v08` hybrid
under a non-selected ownership pattern. Preferring `v08`'s higher clinical fact
score over the selected one-call architecture would make the paper's method
story false even if the number looked stronger.

Sol is the method-identity model for the primary hybrid and LLM-only rows
because it leads the retained six-model panels; the six-model tables remain
model-comparison evidence. LLM-only means `raw_lane_score`, not
`source_scored` and not GEPA, so the hybrid delta is attributable to
deterministic stages on the same Sol calls.

## Consequences

- Canon score tables, paper manuscript method rows, and architecture method
  cards that still present `v08` or GEPA as the primary ExECT hybrid /
  LLM-only peers are stale relative to this decision until updated.
- Evidence protocol A→B→C is complete (2026-08-01). Canon primary fills are
  recorded. Manuscript primary ExECT three-method rows were aligned
  2026-08-03; `v08` and GEPA remain secondary / historical only.
- Do not reopen `v08` as the primary hybrid to recover `0.9202`.
- Do not put nine-entity published metrics beside Sol `0.81` / `0.89` as if
  they measured the same task.

## 2026-08-15 amendment — rules-only Investigations result binding

The standalone Investigations extractor now binds List 9 findings instead of
emitting bare modality tokens. That is a semantic change to the rules-only
method. Intermediate four-family fills:

| Split | Previous fill | Intermediate fill | Investigations |
| --- | ---: | ---: | ---: |
| `dev140` | 0.8160 | 0.8982 | 0.9579 |
| `test60` | 0.7154 | 0.7918 | 0.8706 |

## 2026-08-15 amendment — Rules-Only Parity Campaign (Phases E1–E5)

Following the exhaustive residual cataloging of all 140 development letters across all four target families, targeted gold-free refinements landed in Investigations (PNES EEG confirmation), Prescription (future/titration plan and initiation filters), and SeizureFrequency (statement parser recovery from unkept bare-zero associated mentions).

Selected rules-only four-family fills:

| Split | Pre-campaign fill | Selected fill | Investigations | Prescription | Diagnosis | SeizureFrequency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `dev140` | 0.8982 | **0.9042** | 0.9618 | 0.9780 | 0.8633 | 0.8402 |
| `test60` | 0.7918 | **0.7937** | 0.8706 | 0.8395 | 0.8550 | 0.5899 |

Owners:
[`dev140` / `test60` Phase E5 JSON](../../experiments/exectv2_rules_only_campaign_e5_remeasure_20260815.json),
[E5 remeasure report](../research/exectv2/rules_only_campaign_e5_remeasure_2026-08-15.md).
`test60` remains aggregate-only (0 model calls, 0 row inspection). Hybrid and LLM-only fills are unchanged (decision 0050).
(decision 0050). The 2026-08-01 artifacts stay as historical baselines.

## Numeric hybrid fills (amended 2026-08-14)

Method identity above is unchanged. Selected Sol hybrid **numbers** now come
from [decision 0050](0050-current-stack-hybrid-primary-fills.md): `dev140`
**0.9032**, `test60` **0.8289**. The 13 Aug current-stack values 0.8895 /
0.8196 and the 1 Aug stage-panel values 0.8920 / 0.8047 remain historical
readouts.

## Evidence and glossary owners

- Evidence protocol (A → B → C):
  [primary method-comparison surface protocol](../experiments/exectv2/reliability/exectv2_primary_method_comparison_surface_protocol_2026-08-01.md)
- Phase A — public six-model `test60` stage panel:
  [stage panel report](../experiments/exectv2/reliability/exectv2_six_model_test60_stage_panel_2026-08-01.md)
  and [panel aggregate](../../experiments/exectv2_six_model_test60_stage_panel_20260801/panel_aggregate.json)
- Phase B — rules-only four-family `dev140`:
  [Phase B report](../experiments/exectv2/reliability/exectv2_rules_only_four_family_clinical_headline_dev140_2026-08-15.md)
  (08-01 headline pruned 2026-08-16; recover from Git history; living
  rules-only fill is E5)
- Phase C — rules-only four-family aggregate-only `test60`:
  [Phase C report](../experiments/exectv2/reliability/exectv2_rules_only_four_family_clinical_headline_test60_2026-08-15.md)
  (08-01 headline pruned 2026-08-16; living aggregate is
  [`test60` `20260815`](../../experiments/exectv2_rules_only_four_family_clinical_headline_test60_20260815.json))
- Architecture:
  [architecture index](../architecture/README.md)
- Selected hybrid architecture:
  [decision 0040](0040-final-exect-llm-with-rules-family-ownership.md),
  [decision 0041](0041-single-call-exect-model-comparison.md)
- Six-model panel:
  [six-model comparison report](../research/shared/six_model_comparison_report_2026-07-18.md)
- Glossary terms: [CONTEXT.md](../../CONTEXT.md)
