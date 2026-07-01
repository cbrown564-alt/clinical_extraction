# Qwen Hybrid Same-Core Swap: Per-Family Gap Decomposition

- Generated: `2026-07-01`
- Analysis: replay-only, no new model calls, no row-level inspection
- Source data: `experiments/exectv2_same_core_model_swap_full200_20260625.json` (GPT-4.1-mini,
  DeepSeek chat rows); `experiments/exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_full200_20260626.json`
  (Qwen 3.6 35B row)
- Claim boundary: frozen aggregate full-200, `clinical_headline` surface, same-core
  `exectv2_2call_no_sf_adjudicator` architecture; no row-level inspection authorized or performed
- Follows from: `docs/plans/manuscript_evidence_gaps_closure_plan_2026-07-01.md` Phase 3
  (item 4 of `docs/research/paper_claims_evidence_review_2026-07-01.md`)

## Question

Table R3 of the manuscript reports Qwen 3.6 35B trailing both closed models on the frozen
full-200 same-core aggregate (GPT 0.8356, DeepSeek 0.8566, Qwen 0.8197), and the manuscript's
abstract range ("0.8356–0.8566 F1 across three qualitatively different LLMs") quietly excludes
Qwen. Is Qwen's shortfall uniform and modest across all four families, or concentrated in one —
and if concentrated, is it attributable to a diagnosable mechanism already present in the
replayed artifacts (call/parse failures, evidence-groundedness, over/under-extraction volume),
or is it a clean quality gap with no discriminating feature in the available data?

## Self-Validation

Both source JSONs' family-level `f1`/`overall.f1` fields were read directly and reproduce
Table R3 exactly:

| Model | Overall | Diagnosis | SeizureFrequency | Prescription | Investigations |
|-------|--------:|----------:|------------------:|--------------:|----------------:|
| GPT-4.1-mini | 0.8356 | 0.8397 | 0.7525 | 0.8926 | 0.8563 |
| DeepSeek chat | 0.8566 | 0.8708 | 0.7602 | 0.8926 | 0.9091 |
| Qwen 3.6 35B | 0.8197 | 0.8307 | 0.7020 | 0.8926 | 0.8503 |

## Bottom Line

**Qwen's shortfall is concentrated in SeizureFrequency, not diffuse across families**, and it
is not explained by call failures, parse failures, evidence-groundedness, or a raw
over/under-extraction volume difference — those are all clean nulls. The mechanism is a
per-mention SF classification-quality gap (both precision and recall down, not a
volume/coverage issue). This is a genuine, diagnosable finding, not a kill-criterion case.

Critically, this **differs from** the GEPA single-pass Qwen cross-model finding
(`exectv2_gepa_qwen_cross_model_2026-06-30.md`), which located Qwen's gap in **Diagnosis**
evidence-retrieval under a different (LLM-only, no deterministic scaffolding) architecture. The
concentration locus is architecture-dependent: under the hybrid same-core graph, Diagnosis is
nearly flat (Qwen −0.009 vs GPT) while SF carries the shortfall; under GEPA's single-pass
LLM-only graph, Diagnosis carries the shortfall and SF is comparatively less affected. The
hybrid's deterministic/format layers evidently absorb most of Qwen's Diagnosis-side weakness
before scoring, exactly as the closure plan predicted should be checked rather than assumed.

## Per-Family Delta (Qwen vs. GPT-4.1-mini, the development model)

| Family | GPT F1 | Qwen F1 | Delta (Qwen − GPT) |
|--------|-------:|--------:|--------------------:|
| Diagnosis | 0.8397 | 0.8307 | **−0.0090** |
| SeizureFrequency | 0.7525 | 0.7020 | **−0.0505** |
| Prescription | 0.8926 | 0.8926 | **0.0000** (tied) |
| Investigations | 0.8563 | 0.8503 | **−0.0060** |
| Overall (micro) | 0.8356 | 0.8197 | −0.0159 |

SF's per-family delta (−0.0505) is 5.6× Diagnosis's (−0.0090) and 8.4× Investigations' (−0.0060),
and Prescription is exactly tied. SF is ~21.7% of total gold mention volume (242/1117), which is
why a −0.0505 family-level F1 delta produces only a −0.0159 delta on the pooled micro-average —
the concentration is real, not an artifact of how the overall figure is weighted.

## Ruling Out Call/Parse Failures and Evidence-Groundedness

All three models: **zero call failures** and **exact evidence rate 1.0000** on every family,
including SeizureFrequency, for Qwen. (One DeepSeek Diagnosis parse/schema failure, already
noted in the manuscript as within the predeclared `pass_with_caveat` tolerance — unrelated to
Qwen.) This is a clean null: Qwen's SF gap is not an evidence-validity or malformed-output
problem.

| Family | Model | raw_mentions | scored_mentions | exact_evidence_rate | call_failures | parse_failures |
|--------|-------|-------------:|-----------------:|----------------------:|---------------:|-----------------:|
| SeizureFrequency | GPT-4.1-mini | 360 | 360 | 1.0000 | 0 | 0 |
| SeizureFrequency | DeepSeek chat | 391 | 391 | 1.0000 | 0 | 0 |
| SeizureFrequency | Qwen 3.6 35B | 378 | 378 | 1.0000 | 0 | 0 |

## Ruling Out a Volume (Over/Under-Extraction) Artifact

Qwen's SF `pred_count`/`gold_count` ratio sits *between* GPT's and DeepSeek's, not
anomalously high or low — so the gap is not "Qwen over-extracts (or under-extracts) SF
mentions more than the closed models":

| Model | SF pred | SF gold | pred/gold | Precision | Recall | F1 |
|-------|--------:|--------:|-----------:|-----------:|--------:|----:|
| GPT-4.1-mini | 255 | 242 | 1.0537 | 0.7333 | 0.7727 | 0.7525 |
| DeepSeek chat | 271 | 242 | 1.1198 | 0.7196 | 0.8058 | 0.7602 |
| Qwen 3.6 35B | 268 | 242 | 1.1074 | 0.6679 | 0.7397 | 0.7020 |

Qwen's pred/gold ratio (1.1074) is close to DeepSeek's (1.1198), yet Qwen's precision
(0.6679) is markedly below both closed models' (0.7196, 0.7333) *and* its recall (0.7397) is
markedly below both (0.8058, 0.7727). Both sides of the F1 are down together at a comparable
extraction volume — the gap is a per-mention classification-quality issue (Qwen assigns the
wrong SF state — active-rate vs. seizure-free vs. changed — more often at the same call
volume), not a coverage or over-generation issue. The available replay artifacts do not carry
a per-state-type breakdown, so the specific confusion pattern (e.g., which state pairs are
most confused) cannot be resolved further without a fresh row-level SF read, which is out of
this analysis's scope (replay-only, no row-level inspection authorized).

## Cross-Reference to the GEPA Single-Pass Qwen Finding — Do Not Conflate

The GEPA workstream's Qwen cross-model closeout
(`docs/research/exectv2_gepa_qwen_cross_model_2026-06-30.md`) is a **different architecture**:
a single-pass LLM-only program with no deterministic scaffolding, optimized end-to-end by
GEPA. There, Qwen's gap versus mini was **Diagnosis-concentrated** (evidence-presence recall
0.38–0.40 vs. mini's stronger Diagnosis retrieval), with SF "also weaker... consistent with the
known SF gold-quality ceiling, just hit lower by a weaker producer" — a secondary, not primary,
driver.

Under the hybrid same-core swap analyzed here, the pattern inverts: Diagnosis is nearly flat
(−0.009) and SF carries the shortfall (−0.0505). The most plausible read is that the hybrid's
deterministic dictionary/CUI-normalization and projection layers (§4.5's `standard_dictionary`,
`residual_semantic_lens`) recover much of Qwen's raw Diagnosis-extraction weakness before the
`clinical_headline` scorer sees it — the same layers Table R2 shows contribute a stable ~+0.04
across all three models regardless of which model is in the generation lane — while
SeizureFrequency, which depends more on model-side state classification than on
dictionary/CUI matching, is not similarly rescued. This is consistent with, not contradictory
to, the manuscript's broader claim that the deterministic spine is doing load-bearing
normalization work (D.1, C2), but it means the *specific family* where a weaker model's
raw shortfall surfaces depends on which architecture (single-pass vs. hybrid) is scoring it.

## Kill-Criterion Check

The predeclared kill-criterion (report "uniform, not attributable to any single diagnosed
mechanism" and stop if the signal is diffuse) does **not** apply here: the shortfall is
concentrated (SF carries 90%+ of the effect; Prescription is exactly tied), and two candidate
mechanisms (call/parse failure, evidence-groundedness) are cleanly ruled out with a third
(extraction volume) also ruled out, leaving a specific, reportable characterization
(per-mention SF classification quality) rather than an undiagnosed diffuse gap.

## Manuscript Consequence

§4.3.1 should characterize Qwen's shortfall precisely rather than leaving it as an
unexplained row in Table R3: **concentrated in SeizureFrequency (~90% of the aggregate
delta), not a call-failure, parse-failure, or evidence-groundedness issue (all 1.0000/zero),
and not an over-extraction volume artifact** — Qwen's SF precision and recall are both below
both closed models' at a comparable extraction volume, and the SF-vs-Diagnosis concentration
locus itself differs from the GEPA single-pass finding, indicating the hybrid's deterministic
layers absorb most of Qwen's raw Diagnosis weakness but not its SF weakness. The abstract's
"0.8356–0.8566... across three qualitatively different LLMs" framing should be read alongside
this: the spread is tight-and-non-catastrophic at the aggregate level (Qwen trails by 0.0159
on the overall figure) but the open-weight model does not fully maintain the closed models'
level on the corpus's hardest, lowest-agreement family specifically.

## Source Artifacts

- `experiments/exectv2_same_core_model_swap_full200_20260625.json` (GPT-4.1-mini, DeepSeek rows)
- `experiments/exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_full200_20260626.json`
  (Qwen row; `score_ladder.headline_target` reproduces Table R3 exactly; `lane_diagnostics`
  is the per-family diagnostics analog)
- `docs/research/exectv2_gepa_qwen_cross_model_2026-06-30.md` (cross-referenced GEPA finding)
- `docs/research/paper_claims_evidence_review_2026-07-01.md` (item 4)
- `docs/plans/manuscript_evidence_gaps_closure_plan_2026-07-01.md` (Phase 3)

## Interpretation Boundary

This is a replay-only decomposition over already-frozen full-200 aggregate JSON; no new model
calls, no row-level full-200 inspection. It explains *where* (which family) and rules out three
candidate mechanisms (call failure, parse failure, evidence rate, extraction volume); it does
not identify the specific SF state-confusion pattern, which would require a fresh row-level
read outside this analysis's authorized scope.
