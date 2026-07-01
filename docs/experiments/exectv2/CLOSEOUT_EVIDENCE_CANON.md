# ExECTv2 Closeout Evidence Canon

Last updated: 2026-07-01

**Absorbs:** [`docs/research/final_architecture_selection_2026-06-22.md`](../../research/final_architecture_selection_2026-06-22.md),  
[`key_entities/exectv2_cross_model_closeout_2026-06-22.md`](key_entities/exectv2_cross_model_closeout_2026-06-22.md),  
reliability same-core / component-off / simplification docs under [`reliability/`](reliability/),  
v08/v09 reports under [`key_entities/`](key_entities/).

**Frozen index:** [`final_artifact_index_2026-06-22.md`](../final_artifact_index_2026-06-22.md) — **do not rename paths**  
**Scoring vocabulary:** [`exectv2_evaluation_canon.md`](../../research/exectv2_evaluation_canon.md)  
**Paper claims:** [`PAPER_CANON.md`](../../research/PAPER_CANON.md)

---

## Selected architecture set (≤5 for paper tables)

From final architecture selection memo:

| Role | Run / config | Model | Surface | Claim boundary |
| --- | --- | --- | --- | --- |
| **Performance control** | `exectv2_holistic_finding_assembly_v08_dev140` | GPT-4.1-mini-family lanes | dev140 `clinical_headline` | Dev-only; all 4 key families >0.900 |
| **Simplicity control** | v09 partial hybrid dev140 | Same | dev140 | Overall 0.9059; Inv drops to 0.8549 |
| **Hosted non-GPT diagnostic** | v0.9.16 DeepSeek reparse dev140 | deepseek-chat artifact | dev140 | Do-not-promote; changed-row controls fail |
| **Local-model diagnostic** | v0.9.22 Qwen compact dev140 | qwen3.6:35b | dev140 | Do-not-promote; Dx below target |
| **Gan reliability subject** | Gan reliability package | gpt-4.1-mini + comparators | validation / locked test | Aggregate holdout only |

**Production reference:** v08 dev140 report  
`key_entities/exectv2_holistic_finding_assembly_v08_dev140_20260621.md` (**frozen**).

---

## v08 dev140 headline (performance control)

Holistic finding assembly v08 — only current row with Diagnosis, SeizureFrequency,
Prescription, and Investigations all above **0.900** on dev140 `clinical_headline`.

- Config + JSON/JSONL + error ledger: paths in `final_artifact_index`  
- **Do-not-promote note:** Changed-row controls can fail Rx/Inv despite strong headline — promotion gates in ADR 0008 / component contract  

v09 simplification: drops Investigations stack; overall 0.9059 but not full replacement.

---

## Full-200 aggregate evidence (frozen)

Predeclaration: `reliability/exectv2_same_core_full200_predeclaration_2026-06-25.md`

### Same-core model swap (`clinical_headline`)

| Model | Overall | SF | Notes |
| --- | ---: | ---: | --- |
| GPT-4.1-mini v08 current code | 0.8502 | — | Performance control replay |
| GPT-4.1-mini same-core | 0.8356 | 0.7525 | Operational candidate |
| DeepSeek same-core | 0.8566 | 0.7602 | Leads overall |
| Qwen repair v02 | 0.8197 | 0.7020 | Diagnostic; 0 parse failures |

Artifacts: `experiments/exectv2_same_core_model_swap_full200_20260625.json`

### Component-off replay (full200, aggregate-only)

Nine replay rows (GPT / DeepSeek / Qwen). Positive deltas:

- Dictionary normalization: **+0.019 to +0.029**  
- Residual semantic lens: **+0.010 to +0.012**  
- Headline projection: **+0.030 to +0.035**  

Report: `experiments/exectv2_component_off_replay_full200_20260626.md`  
JSON: `experiments/exectv2_component_off_replay_full200_20260626.json`

**Separate from Reliability Scorecard** — different split, scorer, inspection policy.

---

## Reliability annex (trust evidence)

Recorded on reliability scorecard phased plan (2026-06-21):

| Dimension | Result | Deployment |
| --- | --- | --- |
| Calibration ECE | 0.0432 | Shallow improvement (Brier Δ 0.0142) |
| Review routing | 0.9661 burden / 0.9037 catch | Not low-burden triage |
| Robustness hard-slice | F1 0.8336 / 414 cells | Passed |
| Self-consistency | 0.8857 aggregate | Not per-letter entropy routing |

Cross-model closeout (2026-06-22): three-model same-core dev140 table in results scaffold.

---

## Simplification frontier (accepted lean candidate)

GPT-4.1-mini simplification study: accepted lean path is **2-call no-SF adjudicator**
(`0.8356` overall / `0.7525` SF on full-200). Further simplification not active.

Reports under `reliability/` and `key_entities/` — see frozen index entries for v09.

---

## Cross-task component ablation (2026-06-27)

`docs/experiments/reliability/cross_task_shared_component_ablation_2026-06-27.md`:

- Evidence validation gate **inert** (Δ=0 both tasks)  
- Dictionary / normalize **positive** on both tasks  

**Manuscript:** Propagate to C2; remove stale “not yet executed” limitation.

---

## Prediction-bearing vs format-only (closeout answer)

**Prediction-bearing:** reconciliation, SF state arbitration, Rx/Inv verifier decisions,
dictionary/lens changes that alter clinical identity, hybrid rescue when fact changes.

**Format-only:** meaning-preserving projection, schema repair, CUI spelling when clinical
fact unchanged — tag score lines per projection taxonomy.

---

## Rejected / superseded branches

- Pure single-GPT + dictionary v09 on mini: 0.7552 — rejected as control  
- LLM-only dedup phase6 as production: ~0.73 plateau — diagnostic only  
- Qwen / DeepSeek dev140 rows as v08 replacement: changed-row controls fail  

---

## Long tail (not merged — bucket pointers)

| Bucket | Content | Future canon |
| --- | --- | --- |
| `diagnosis/` | Verifier ladder, dx row analysis | Family one-pager |
| `seizure_frequency/` | Adjudicator v01–v05, agentic redo | WS SF canon |
| `key_entities/` | Holistic v01–v07 | Absorbed into v08 narrative |
| `reliability/` | Calibration, robustness audits | This doc §Reliability annex |

---

## Related reading

- [`exectv2_final_key_family_architecture_synthesis_2026-06-18.md`](../../research/exectv2_final_key_family_architecture_synthesis_2026-06-18.md)  
- [`exectv2_gepa_canon.md`](../../research/exectv2_gepa_canon.md)  
- [`experiments/registry.jsonl`](../../../experiments/registry.jsonl)  
- [`docs/THREAD_MAP.md`](../../THREAD_MAP.md) T3
