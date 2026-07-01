> **Status: HISTORICAL** — design record only. See [`ACTIVE_ROADMAP.md`](ACTIVE_ROADMAP.md) and [`recent_plan_rationalisation_2026-06-25.md`](recent_plan_rationalisation_2026-06-25.md).

# Scope — GEPA over a multi-stage ExECTv2 program (toward the 0.9155 hybrid)

Status: **DRAFT scope, SUPERSEDED in emphasis (not started).** Decision gate at the end of Phase 1.
Owner: ExECTv2 GEPA workstream. Date: 2026-06-28.

> **Redirect (2026-06-28):** the evidence decomposition
> (`docs/research/exectv2_gepa_vs_hybrid_evidence_decomposition_2026-06-28.md`) shows the
> GEPA→hybrid gap is **producer evidence-retrieval** (ev-recall 0.694 → 0.883), not the
> verify/arbitrate/deterministic stages (which net only +0.016 evidence-recall and +0.058 F1,
> all Diagnosis). This scope's Phase-1 bet on an evolvable **S1 verify** stage is therefore
> demoted to a secondary lever. The active plan is
> `docs/plans/exectv2_gepa_focused_lanes_recall_plan_2026-06-28.md` (recall-oriented S0
> producers on a DeepSeek task model). Keep this scope for the verify/arbitrate design if the
> producer lever plateaus.

Companion: `docs/research/exectv2_gepa_underperformance_investigation_2026-06-27.md`
(the investigation this scope follows from). Code under
`src/.../epilepsy_phenotyping/exectv2/gepa/`.

## 1. Why this exists

The GEPA under-performance investigation is resolved: the flat ≈-seed result was a
**harness** bug, not a task ceiling. Fixing the two harness defects climbed dev140
`clinical_headline` monotonically — H1 (diff-feedback metric) 0.628→0.702, H2
(`minibatch=8` selection) →0.719, per-family instructions →**0.731** — beating the
hand-tuned single prompt (0.710) and the prior multi-family run (0.631).

But a new, **different** ceiling is now characterised: **single-pass GEPA (monolith or
per-family) plateaus ~0.72–0.73, ~0.18 below the multi-stage v08 hybrid (0.9155).** The
gap families Diagnosis (0.66) and SeizureFrequency (0.59) sit at ~0.91 each in the hybrid.
That remaining gap is **architectural**: the hybrid's lift comes from *stages*
(generation → verification → arbitration → deterministic projection) that GEPA cannot
invent by evolving the instructions of a single-pass extractor.

**This scope tests whether giving GEPA a multi-stage program to optimize closes the gap.**

## 2. Goal & hypothesis

- **Goal:** beat the single-pass GEPA plateau (0.731) on dev140 `clinical_headline`, with
  a credible path toward the v08 hybrid 0.9155 — by evolving the instructions of a
  *multi-stage* program rather than a single-pass one.
- **Primary hypothesis (H-arch):** the hybrid's Dx/SF lift is recoverable by an *evolvable*
  generate→verify→arbitrate pipeline; the hand-written verification rules
  (`entity_verifier/_clinical_rules`, `_worked_examples`) are exactly the kind of structure
  GEPA's reflective mutation produces from diff feedback (it already re-derived the
  hand-tuned monolith rules in H1).
- **Falsifiable kill-criterion:** if an evolvable **verify** stage on top of the per-family
  generator does not beat 0.731 by ≥ +0.03 on dev140 in Phase 1, the architectural lift is
  **not** instruction-recoverable single-model, and we stop (see §9 risk on cross-model).

## 3. The design constraint: what GEPA can and cannot optimize

GEPA evolves the **instruction text** of each `dspy.Predict` in a fixed-shape `dspy.Module`;
it does **not** invent new modules or control flow. So "give GEPA a multi-stage program"
means: *we* author the stage graph (generate→verify→arbitrate) as a `dspy.Module`, seed each
stage with a lean instruction, and GEPA evolves all stage instructions jointly under the
existing length-penalized diff-feedback metric. Infra already supports this — `run_gepa.
run_experiment(seed_program=, final_instruction_fn=)` optimizes any `dspy.Module` whose
`forward` returns `clinical_facts_json` (the per-family program proves the pattern).

## 4. Target architecture (evolvable multi-stage program)

New module `gepa/program_multistage.py`, a `dspy.Module` chaining:

| stage | evolvable? | seed from | role |
| --- | --- | --- | --- |
| **S0 Generate** | yes (4 instr) | `program_multifamily.py` per-family signatures | draft facts per family (high recall) |
| **S1 Verify** | yes (per-family instr) | `llm/pipelines/entity_verifier/*` rules+examples, distilled to a lean seed | per draft fact, accept / reject / correct against the letter (precision + attribute fidelity) |
| **S2 Arbitrate** | yes (1 instr) | `llm_sf_union_arbitration.py` / `llm_*_arbitration.py` | de-dup, resolve conflicts, select the final fact set across families |
| **S3 Project** | **no (fixed)** | existing `clinical_facts_to_mentions` + evidence/render gates + `project_cuis` | deterministic representation/CUI projection — already in the GEPA adapter path |

- `forward(letter_text, output_schema)`: S0 emits draft facts → S1 verifies each → S2
  arbitrates to a final `clinical_facts` list → return `clinical_facts_json`. S3 runs inside
  the metric/eval as today (unchanged).
- **Stamp** summed instruction tokens across **all** evolvable stages (S0+S1+S2) onto the
  prediction, exactly as `program_multifamily.forward` does, so the length penalty sees the
  whole evolved surface. Budget rises (see §6).
- `combined_instruction(program)` concatenates every stage instruction (labelled
  `=== generate.diagnosis ===`, `=== verify.sf ===`, `=== arbitrate ===`, …) for the
  artifact + token count, mirroring the per-family helper.
- The metric, adapter, and the four canonical scorers are **reused unchanged** — the program
  still only has to produce a `clinical_facts_json`.

### Stage I/O contracts (seed signatures)
- **S1 Verify** (one per family, mirrors `entity_verifier` config): inputs = `letter_text` +
  `draft_<family>_facts_json`; output = `verified_<family>_facts_json` (kept/corrected facts
  with evidence). Seed instruction = a *lean* distillation of the family's `_clinical_rules`
  (NOT the full hand prompt — GEPA grows it, the length penalty keeps it honest).
- **S2 Arbitrate**: inputs = `letter_text` + all verified family facts; output = final
  de-duplicated `clinical_facts_json`. Seed = "merge, drop duplicates and contradictions,
  keep the best-grounded fact per concept."

## 5. Metric & per-stage credit assignment

- Reuse `build_metric` (length-penalized, diff-feedback) **as-is** for selection — it already
  scores the final facts and feeds concrete missed/spurious diffs to the reflector. GEPA's
  multi-predictor reflection mutates one stage at a time and evaluates the whole program, so
  baseline credit assignment works out of the box (as it did for the per-family run).
- **Phase-2 enhancement (only if needed):** the final-fact diff is *coarse* for deep stages
  (the verify stage is blamed for a missed gold fact that S0 never generated). If Phase 1
  shows the verify stage is starved of targeted signal, enrich the feedback with **stage-local
  diffs** — e.g. tell S1 which of *its* accept/reject decisions flipped a fact from correct to
  wrong (recall lost by an over-aggressive reject; precision lost by a missed reject). This is
  a metric/trace change, not an architecture change; defer until Phase 1 proves the stage.

## 6. Cost & budget

Per-letter LLM calls grow with stages: S0(4) + S1(4) + S2(1) ≈ **9 calls/letter** (vs 4 for
per-family, 1 for monolith). Each GEPA *metric call* = one letter eval, so the metric-call
budget is unchanged in count but ~2× the wall/$ of the per-family run.

| run | calls/letter | metric calls | est. wall (mini) |
| --- | ---: | ---: | ---: |
| per-family (done) | 4 | ~2705 | 39 min |
| multi-stage S0+S1 (Phase 1) | ~8 | ~2705 | ~70–80 min |
| + S2 arbitrate (Phase 2) | ~9 | ~2705 | ~80–90 min |

Keep `reflection_minibatch_size=8` (H2). Keep `auto="medium"`; bump only if proposal count
drops. Task model `gpt-4.1-mini`, reflection `deepseek-reasoner` (unchanged). Resumable via
the existing `log_dir` checkpoint + summary-gate (the orchestrator pattern).

## 7. Build plan (phased, with decision gates)

- **Phase 0 — infra (no run):** `gepa/program_multistage.py` (S0+S1 only), `combined_instruction`,
  token stamping; a `gepa_multistage_exectv2.py` launcher mirroring the H2/multifamily ones;
  a `--smoke` end-to-end check. Unit-test the `forward` merge (no synthetic `attributes` key —
  the trap the per-family build hit). **Gate:** smoke green.
- **Phase 1 — verify stage (1 run):** S0 (seed = evolved per-family instructions from the
  0.731 run) + evolvable S1 verify. Run on mini, dev140. **Gate / kill-criterion:** beats
  0.731 by ≥ +0.03 → continue; else stop and write the negative (architectural lift is not
  single-model instruction-recoverable — likely cross-model; see §9).
- **Phase 2 — arbitration + stage-local feedback (1–2 runs):** add S2; if verify is
  signal-starved, add stage-local diffs (§5). **Gate:** monotone gain over Phase 1.
- **Phase 3 — readout & (only if a real candidate emerges) freeze discipline:** dev140 is the
  development surface; `test60` stays frozen. A test readout needs the same preflight rigor as
  the other frozen holdouts. Reaching ~0.85+ dev140 is the trigger to even consider it.

## 8. Success criteria

- **Minimum success:** dev140 `clinical_headline` > 0.76 (clears the single-pass plateau by a
  margin beyond selection noise SE ≈ 0.03), concentrated in Dx/SF.
- **Target:** ≥ 0.85 dev140, closing most of the gap to the 0.9155 hybrid with an *evolved*
  (not hand-written) pipeline — the headline capability claim.
- **Either way it is a result:** success ⇒ the architectural gap is instruction-recoverable;
  failure ⇒ the hybrid's lift is structural/cross-model, bounding what single-model
  prompt-evolution can do (a clean negative for the paper).

## 9. Risks & mitigations

- **R1 — the lift is cross-model, not multi-stage.** The hybrid may win partly via cross-model
  corroboration (cf. gan2026 needing all 3 traces), which single-model GEPA cannot reproduce.
  *Mitigation:* Phase 1 isolates the verify stage single-model; the kill-criterion catches this
  early. A later arm could make S1/S2 a *different* model (deepseek verify over mini generate).
- **R2 — verify can't exceed generation recall.** S1 only filters/corrects S0's drafts; if S0
  misses a gold fact, no verify recovers it. *Mitigation:* seed S0 for high recall (lenient
  generate), let S1 carry precision; consider an S1 "add missed fact" affordance.
- **R3 — credit assignment too coarse.** (See §5 stage-local feedback; deferred enhancement.)
- **R4 — cost/latency.** ~9 calls/letter. *Mitigation:* keep mini; resumable runs; don't add
  S2 until S1 earns it.
- **R5 — length-penalty mis-budgeted across many stages.** *Mitigation:* set per-stage budgets
  summing to a sane total; watch evolved token counts as in prior runs.

## 10. Out of scope / non-goals

- No new scorers or change to the canonical `clinical_headline` surface (decision 0027).
- No `test60` readout until a dev candidate clears the §8 target and passes preflight.
- Not rebuilding the hybrid; reusing its *prompt content* as seeds only.
- Registry registration remains blocked by the malformed `registry.jsonl:63` (artifacts still
  written) — fix is orthogonal and tracked in the workstream memory.

## 11. Open questions

1. Seed S0 from the 0.731 evolved per-family instructions, or from the lean seeds? (Lean lets
   GEPA co-adapt generate+verify; warm-start is faster but may local-optimum.)
2. Single arbitration stage vs per-family verify-then-global-arbitrate vs per-family
   verify-only (no S2)? Phase 1 tests verify-only first.
3. Is dev140 large enough to detect a +0.03 gain given SE ≈ 0.03? (Borderline — consider
   reporting with a bootstrap CI, not a point estimate.)
