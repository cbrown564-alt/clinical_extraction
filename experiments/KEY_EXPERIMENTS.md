# Key Experiments Explained

Last updated: 2026-07-06

Start here before diving into [`RUN_INDEX.md`](RUN_INDEX.md) or [`registry.jsonl`](registry.jsonl).

Link to glossary: [`docs/reference/plain_language_glossary.md`](../docs/reference/plain_language_glossary.md)

---

## Gan — production & comparators

### Production structured-event pass (promoted)

| | |
| --- | --- |
| **What we ran** | Single GPT-4.1-mini structured-event extraction → deterministic render (no reasoner, no multi-agent consensus) |
| **Split** | Locked test450 holdout (450 rows) |
| **Outcome** | **364/450 Purist = 0.809** — promoted go-forward architecture |
| **Claim boundary** | Aggregate holdout only; no row-level test inspection for tuning. Smallest val→test drop among promoted candidates (0.881 val → 0.809 test). |
| **Deep dive** | [`docs/canon/06_gan_clinical_policy.md`](../docs/canon/06_gan_clinical_policy.md) · [`gan2026_test450_phase4_frozen_audit_hybrid_structured_events_gpt41mini_2026-06-09.md`](gan2026_test450_phase4_frozen_audit_hybrid_structured_events_gpt41mini_2026-06-09.md) |

### V12 fresh-evidence ceiling (comparator only)

| | |
| --- | --- |
| **What we ran** | Full three-model hybrid: GPT/Qwen/DeepSeek structured events + gpt-4.1 reasoner with 3-trace corroboration |
| **Split** | Locked test450 holdout |
| **Outcome** | **379/450 Purist = 0.842** — best holdout; **+15 rows** over production SE |
| **Claim boundary** | Ceiling comparator, not production. Reasoner runs on full gpt-4.1; production SE is mini-verified. ~0.842 is a **prior** (The Wall), not a tuning target. |
| **Deep dive** | [`docs/canon/06_gan_clinical_policy.md`](../docs/canon/06_gan_clinical_policy.md) · [`gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_4_2026-06-13.md`](gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_4_2026-06-13.md) |

### Deterministic rules floor (controlled baseline)

| | |
| --- | --- |
| **What we ran** | `rules_only` — deterministic prediction-bearing interpretation with no LLM clinical fact |
| **Split** | Locked test450 holdout |
| **Outcome** | **343/450 Purist = 0.762** — controlled floor for hybrid lift measurement |
| **Claim boundary** | Rules as controlled variable (C4); not a production candidate. Generalization gap val→test is decisive (−16.7pp). |
| **Deep dive** | [`docs/canon/06_gan_clinical_policy.md`](../docs/canon/06_gan_clinical_policy.md) · [`gan2026_test450_phase4_frozen_audit_deterministic_canonical_pipeline_gpt41mini_2026-06-09.md`](gan2026_test450_phase4_frozen_audit_deterministic_canonical_pipeline_gpt41mini_2026-06-09.md) |

---

## Gan — confident over-reading limit (The Wall)

### P2.1 — semantic entropy probe

| | |
| --- | --- |
| **What we ran** | Multi-sample structured-event extraction at temps {0.3, 0.5, 0.7, 1.0}, k=4; measure Purist-label and event-kind entropy |
| **Split** | Validation only (150 rows; 23 residual-enriched) |
| **Outcome** | Mean label entropy **0.012**; `band_unknown` entropy **0.000** → **H0 confirmed: over-reading is confident**, not uncertain |
| **Claim boundary** | Validation-only mechanism falsification. No abstention/calibration signal derivable from model samples. Does not change production champion. |
| **Deep dive** | [`gan2026_reliability_p2_1_semantic_entropy_preflight150_2026-06-17.md`](gan2026_reliability_p2_1_semantic_entropy_preflight150_2026-06-17.md) · [`docs/canon/05_ceilings_wall.md`](../docs/canon/05_ceilings_wall.md) |

### P0.2 — risk–coverage / External Risk Score

| | |
| --- | --- |
| **What we ran** | No-call replay ordering rows by External Risk Score (cross-model agreement + source flags + ambiguity); selective-prediction curve vs Purist correctness |
| **Split** | Validation750 (headline); test450 port in Phase 1 scorecard |
| **Outcome** | Validation: failure AUROC **0.781** (strongest forward-observable leg). Self-confidence degenerate (~chance). Holdout port: two-agent agreement AUROC **0.648**. |
| **Claim boundary** | Reliability/triage evidence, not a new benchmark claim. Cross-model agreement helps; single-model self-signals do not catch confident residuals. |
| **Deep dive** | [`gan2026_reliability_p0_2_risk_coverage_validation750_2026-06-17.md`](gan2026_reliability_p0_2_risk_coverage_validation750_2026-06-17.md) · [`gan2026_reliability_master_scorecard_2026-06-17.md`](gan2026_reliability_master_scorecard_2026-06-17.md) |

### Irreducible residual audit

| | |
| --- | --- |
| **What we ran** | Post-hoc audit of validation rows where no Purist-correct component exists and no route to gold without hidden labels |
| **Split** | Validation750 residual slice |
| **Outcome** | **11 rows** irreducible; **8/11** are `band_unknown` — no component, no selector route without gold |
| **Claim boundary** | Defines the binding residual behind The Wall. Distinct from ExECT gold-quality ceiling (different task, different mechanism). |
| **Deep dive** | [`docs/canon/06_gan_clinical_policy.md`](../docs/canon/06_gan_clinical_policy.md) · [`docs/research/wall_transfer_forward_observable_feature_inventory_2026-06-27.md`](../docs/research/wall_transfer_forward_observable_feature_inventory_2026-06-27.md) |

---

## Gan — selector ladder (not promoted)

Production remains the single SE pass (364/450). The v0.9 consensus/fresh **selector** is a separate holdout-backed candidate that passed its own Gate 4 bars but was **not promoted** over production.

### v0.9 selector — Gate 4 exact (passed bars)

| | |
| --- | --- |
| **What we ran** | No-call replay of frozen v0.9 consensus/fresh agreement selector over exact Gate 3 source set (rules floor + three-agent consensus + fresh-evidence components) |
| **Split** | Locked test450 aggregate-only |
| **Outcome** | Selected Purist **359/450** (+16 net vs deterministic 343/450); changed-label precision **0.60**; Gate 4 bars **passed** |
| **Claim boundary** | Holdout-backed **selector** evidence only — still below production SE (364/450). Aggregate-only; no row-level failure inspection. Do not tune from this result. |
| **Deep dive** | [`gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate4_exact_aggregate_audit_2026-06-26.md`](gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate4_exact_aggregate_audit_2026-06-26.md) · [`docs/experiments/gan2026/frozen_test/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_protocol_2026-06-26.md`](../docs/experiments/gan2026/frozen_test/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_protocol_2026-06-26.md) |

### v0.9 selector — Gate 4 constrained (failed promotion)

| | |
| --- | --- |
| **What we ran** | Same selector replay but with **constrained** source symmetry (older two-agent consensus artifact, not exact three-agent parity) |
| **Split** | Locked test450 aggregate-only |
| **Outcome** | Selected Purist **348/450**; precision **0.5909** — **failed** promotion bars (+10 net and precision ≥0.60 not both met under constrained sources) |
| **Claim boundary** | Final-evaluation evidence only. Proves source-symmetry matters; constrained result must not be used as tuning signal for later exact-source runs. |
| **Deep dive** | [`gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate4_constrained_aggregate_audit_2026-06-26.md`](gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate4_constrained_aggregate_audit_2026-06-26.md) · [`docs/research/consensus_fresh_selector_fate_2026-06-27.md`](../docs/research/consensus_fresh_selector_fate_2026-06-27.md) |

---

## ExECT — production control

### v08 holistic finding assembly (dev140 control)

| | |
| --- | --- |
| **What we ran** | Manifest-driven clinical finding assembly v08 — per-family producers, entity lenses, headline projection (no-call replay) |
| **Split** | dev140 (140 rows) |
| **Outcome** | `clinical_headline` **0.9152** overall; all four key families >0.900 (Dx 0.9083, SF 0.9053, Rx 0.9357, Inv 0.9132) |
| **Claim boundary** | **Performance control** on development split only — not holdout, not full-200 headline claim. Primary ExECT scoreboard surface. |
| **Deep dive** | [`docs/experiments/exectv2/key_entities/exectv2_holistic_finding_assembly_v08_dev140_20260621.md`](../docs/experiments/exectv2/key_entities/exectv2_holistic_finding_assembly_v08_dev140_20260621.md) · [`docs/experiments/exectv2/key_entities/HOLISTIC_ASSEMBLY_LADDER_CANON.md`](../docs/experiments/exectv2/key_entities/HOLISTIC_ASSEMBLY_LADDER_CANON.md) |

### Component-off replay (full-200)

| | |
| --- | --- |
| **What we ran** | Aggregate replay turning off one component at a time (`standard_dictionary`, `residual_semantic_lens`, `headline_projection`) on frozen full-200 artifacts |
| **Split** | full200 aggregate (200 rows; GPT, DeepSeek, Qwen repair families) |
| **Outcome** | All selected components show **positive contribution deltas** on `clinical_headline` (e.g. GPT headline_projection Δ **+0.0317**; standard_dictionary Δ **+0.0186**) |
| **Claim boundary** | Component-impact evidence only — not reliability scorecard, not holdout. Aggregate-only; no row-level inspection authorized. |
| **Deep dive** | [`exectv2_component_off_replay_full200_20260626.md`](exectv2_component_off_replay_full200_20260626.md) · [`docs/experiments/exectv2/reliability/exectv2_component_off_full200_predeclaration_2026-06-26.md`](../docs/experiments/exectv2/reliability/exectv2_component_off_full200_predeclaration_2026-06-26.md) |

### Same-core model swap (full-200)

| | |
| --- | --- |
| **What we ran** | Frozen 2-call no-SF adjudicator architecture with model swapped (GPT-4.1-mini vs DeepSeek chat); identical component graph |
| **Split** | full200 aggregate (200 rows) |
| **Outcome** | DeepSeek **0.8566** overall · GPT **0.8356** overall (`clinical_headline`); DeepSeek leads SF (0.7602 vs 0.7525) |
| **Claim boundary** | Same-core aggregate validation with schema-stability caveat (1 Dx parse failure tolerated on DeepSeek). Diagnostic/comparability — v08 dev140 control remains the optimization anchor. |
| **Deep dive** | [`docs/experiments/exectv2/reliability/exectv2_same_core_model_swap_full200_2026-06-25.md`](../docs/experiments/exectv2/reliability/exectv2_same_core_model_swap_full200_2026-06-25.md) |

---

## What these are NOT

These categories live in [`RUN_INDEX.md`](RUN_INDEX.md) and [`archive/`](archive/) but are **not** headline production or holdout claims:

| Category | Examples | Why excluded from “key” |
| --- | --- | --- |
| **Validation-only development** | Gan validation750 verifier iterations, ExECT dev25/dev5 smoke lanes, DSPy GEPA train runs | Tuning signal only; no holdout authority |
| **Historical / superseded** | Pre-v08 ExECT lanes, Gan V1–V11 agentic ladder, direct labeler | Retired after regression or weaker holdout transfer |
| **Mechanism panels (non-benchmark)** | Gan Gate 2 robustness batteries, ExECT adversarial fixture stress | Source-near or synthetic; not natural-corpus headline scores |
| **Diagnostic surfaces** | ExECT benchmark/CUI F1, Gan Pragmatic-only quotes, rescoring under `state_profile` | Representation or scorer effects — never quote alone as extractor quality |
| **Registry housekeeping** | Replay hashes, cache lineage, superseded run_ids | Machine index metadata; see [`registry.jsonl`](registry.jsonl) |

For the full decision index (promote / revise / superseded / historical), use [`RUN_INDEX.md`](RUN_INDEX.md).
