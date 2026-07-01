# Gan Component Mechanics Canon (RQ1–RQ10)

Last updated: 2026-07-01

**Scope:** Numbered research-question program on **what each pipeline component
owns** on validation750 (June 2026).  
**Claim boundary:** Validation-development / saved-replay evidence — not
production promotion, not benchmark-comparable holdout claims.

**Parent canon:** [`GAN2026_RESEARCH_CANON.md`](../../research/gan2026/GAN2026_RESEARCH_CANON.md)  
**Companion:** [`VALIDATION750_CANON.md`](VALIDATION750_CANON.md)  
**Long tail:** 31 files in [`rq_series/`](rq_series/) + protocols (stubbed)

---

## Program thesis

Rules and LLM stages are **controlled variables**. Each RQ isolates one component
role (candidate generation, evidence selection, projection, selective LLM value)
with saved-output replay and explicit W→C / C→W accounting.

**Durable meta-lessons:**

1. **Broad LLM replacement loses** to selective, gated interventions.  
2. **Validation-prefix success ≠ hidden-family transfer** (RQ7).  
3. **Projection works narrow**; broad graph projection is a negative result (RQ4).  
4. **Hard-row residue** mixes scorer ambiguity with true extraction failure — route
   through review policy, not undifferentiated rule retuning (RQ10).

---

## RQ answer table (canonical 2026-06-04 answers)

| RQ | Question focus | Verdict (one line) | Primary answer doc |
| --- | --- | --- | --- |
| **RQ1** | Candidate discovery | LLM adds **selective boundary-state proposal**, not broad replacement generation | `rq1_candidate_discovery_answer_2026-06-04.md` |
| **RQ2** | Evidence selection | LLM should **choose among compatible candidates**, not re-extract | `rq2_evidence_selection_answer_2026-06-04.md` |
| **RQ3** | Rich selected state | Rich state helps **boundary/competing-state** rows; burden rises | `rq3_rich_selected_state_five_letter_answer_2026-06-04.md` |
| **RQ4** | Projection | **Narrow gated projection** works; broad graph/LLM projection **rejected** | `rq4_projection_answer_2026-06-04.md` |
| **RQ5** | Deterministic compile/render | Deterministic rendering owns **format**; LLM must not smuggle clinical facts | `rq5_deterministic_compilation_rendering_answer_2026-06-04.md` |
| **RQ6** | Selective LLM value | **`selective_safety_floor_gate_v0`**: 21 val750 changes (11 W→C, 0 C→W); frozen test450 audit 14 rows (8 W→C) | `rq6_selective_llm_value_answer_2026-06-04.md` |
| **RQ7** | Hidden-family generalization | **Partly answered** — boundary/uncertainty families yes; rate/cluster families need more tests | `rq7_hidden_family_generalization_synthesis_2026-06-04.md` |
| **RQ7b** | Family-indexed matrix | Component effects **vary by hidden family** — matrix documents ownership | `rq7_family_indexed_component_matrix_answer_2026-06-04.md` |
| **RQ8** | Efficiency / ops reliability | Operational reliability constraints documented; not production SLA | `rq8_efficiency_operational_reliability_answer_2026-06-04.md` |
| **RQ9** | Selective action / abstention | Selective-action policy with frozen holdout **audit protocol**; complements RQ6 gate | `rq9_selective_action_answer_2026-06-04.md` |
| **RQ10** | Gold/scorer ambiguity | **64%** of Purist misses are non-plain extraction failures; hard rows need **ambiguity/review routing**, not blind rule retune | `rq10_gold_scorer_ambiguity_audit_answer_2026-06-04.md` |

Superseded 2026-06-03 answer drafts: use **2026-06-04** rows unless reproducing
historical registry lineage.

---

## Strongest component artifact: selective safety floor

**`selective_safety_floor_gate_v0`** (RQ6/RQ9):

| Surface | Changed | W→C | C→W | Notes |
| --- | ---: | ---: | ---: | --- |
| validation750 | 21 | 11 | 0 | 21/21 exact evidence on changed rows |
| test450 frozen audit | 14 | 8 | 0 | Aggregate-only; no row-level tuning |

Machine artifacts under `experiments/gan2026_selective_safety_floor_gate_v0_*`.

This is the **positive selective LLM** result that survived hidden-family scrutiny —
distinct from V12 fresh-evidence ceiling (+15 test rows) in research closeout.

---

## RQ4 projection highlights

Gated policies with high precision on panel:

- **`boundary_state_priority`:** 17 W→C, 0 C→W, 17/17 exact evidence  
- **`graph_gated_month_bucket_duration`:** 18 W→C on target panel, 0 C→W on regression panel  

Broad typed operations and unconstrained LLM label projection: **negative**.

---

## RQ7 hidden-family map (architecture implications)

| Family | Evidence | Implication |
| --- | --- | --- |
| `unknown_boundary` | LLM preserves boundary facts | Selective LLM + deterministic unknown policy |
| `competing_state` / `current_vs_historical` | Selective gate helps | Do not broad-project |
| `rate` / `denominator` / `cluster` / `diary` | Incomplete transfer | More controlled component tests needed |
| `benchmark_convention` | Risky for broad LLM | Keep deterministic |

Negative exemplar: **A2 sparse operands** — strong on validation250, collapsed on
later validation rows.

---

## RQ10 ambiguity classes (53 Purist-wrong rows)

| Class | Rows | Action |
| --- | ---: | --- |
| `underdetermined_note` | 23 | Review/abstention policy |
| `true_extraction_failure` | 19 | Candidate generation |
| Other RQ10 classes | remainder | Mixed — see audit JSON |

29 rows have exact evidence but scorer/gold-wrong under primary layer — supports
**gold-quality / convention** thread linking to ExECT C1 mechanism (different task).

---

## Protocol vs answer files

Each RQ typically has:

- `*_protocol_2026-06-*.md` — predeclaration (historical)  
- `*_answer_2026-06-04.md` — **canonical verdict**

For paper/crosswalk citations, prefer **answer** docs or this canon table. Protocols
remain for audit trail.

---

## Cross-links to ExECT / paper

| Gan RQ lesson | ExECT echo |
| --- | --- |
| RQ10 ambiguity routing | ExECT gold-quality ceiling + review routing failure |
| RQ6 selective gate | Hybrid buys little at Gan aggregate; ExECT needs per-family producers |
| RQ4 narrow projection | Deterministic projection taxonomy; benchmark vs clinical layers |
| RQ7 non-transfer | dev25→dev140 non-transfer in ExECT key-family synthesis |

---

## Related reading

- [`docs/design/component_evidence_attribution_architecture.md`](../../design/component_evidence_attribution_architecture.md)  
- [`docs/experiments/reliability/cross_task_shared_component_ablation_2026-06-27.md`](../reliability/cross_task_shared_component_ablation_2026-06-27.md)  
- [`docs/research/PAPER_CANON.md`](../../research/PAPER_CANON.md) C2, C5
