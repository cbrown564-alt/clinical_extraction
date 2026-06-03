# Executive Report: A2 Validation750 Full Readout

**Date:** June 3, 2026  
**Pipeline:** `llm_only_sparse_operands_selected_state_reasoner` (A2)  
**Evaluation Surface:** Full Validation split, 750 rows (`gan2026_split_v1`)

---

## 1. Full Metric Readout

| Metric Layer | validation25 (Replay) | validation50 (Live) | validation250 (Live) | validation750 (Live) |
| :--- | :---: | :---: | :---: | :---: |
| **Structured Records** | 25/25 (100.0%) | 50/50 (100.0%) | 248/250 (99.2%) | 749/750 (99.9%) |
| **Selected Evidence Arithmetic** | 23/25 (92.0%) | 47/50 (94.0%) | 232/250 (92.8%) | 569/750 (75.87%) |
| **Sparse Operand Adapter (Purist)** | 23/25 (92.0%) | 48/50 (96.0%) | 232/250 (92.8%) | 551/750 (73.47%) |
| **Sparse Operand Adapter (Pragmatic)** | 23/25 (92.0%) | 49/50 (98.0%) | 240/250 (96.0%) | 606/750 (80.80%) |

---

## 2. Key Observations & Generalization Gap

### Generalization Gap Analysis
There is a substantial performance drop between the validation250 ladder (92.8% Purist) and the full validation750 readout (73.47% Purist). This indicates a significant **generalization gap** on the latter 500 rows of the validation split. 
* The first 250 rows represent a much cleaner subset of notes where the reasoner's direct prompt mappings hold up well.
* The remaining 500 rows contain higher semiotic complexity, multiple distracting timelines, and ambiguous seizure targets (e.g. distinguishing focal clonic vs. generalized events in the presence of complex non-seizure descriptions).

### Adapter vs. Arithmetic
* Across 750 rows, the **Sparse Operand Adapter (73.47%)** dropped slightly below **Selected-Evidence Arithmetic (75.87%)**, with 37 correct-to-wrong regressions and 19 wrong-to-correct progressions.
* This indicates that while the boundary-check fallbacks resolved localized regressions on the stress panel, the LLM still struggles to consistently output matching operands under more complex clinical notes.

---

## 3. Conclusions and Next Steps

1. **LLM-Only Limitation**: This run confirms that an LLM-only pipeline (even with optimized sparse schemas and boundary checks) cannot match the **92.93% Purist F1** achieved by the hybrid deterministic safety-floor pipeline (`hybrid_parallel_state_candidate_reasoner`).
2. **Next Steps**:
   * Integrate A2's selection logic into the **hybrid safety-floor architecture** as a clinical-selection sidecar to salvage the LLM's high selection performance on clean rows while keeping the deterministic floor active for safety.
   * Evaluate schema and token efficiency to optimize latency.
