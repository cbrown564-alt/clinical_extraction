> **Status: HISTORICAL** — design record only. See [`ACTIVE_ROADMAP.md`](../ACTIVE_ROADMAP.md) and [`recent_plan_rationalisation_2026-06-25.md`](../recent_plan_rationalisation_2026-06-25.md).

# Satellite 08 — Paper Outputs & Milestones

Parent: [[00_overarching_implementation_plan]] · Phase 8 (+ milestone tracker)
Status: planning.

## Purpose

Tie the workstream to the paper: the concrete tables/figures we must produce, and
the milestones that track progress from foundation to a benchmark-beating,
reliability-demonstrating result across both tasks.

## 1. Paper-relevant outputs (ExECTv2 side)

Mapping each thesis claim to an artifact (per `reliability_thesis.md` §6):

| Claim | Artifact |
| --- | --- |
| Beats the benchmark | Overall per-item/per-letter F1 vs 0.87/0.90, all three architectures, with CIs and dev→audit gap |
| Generalization by transfer | Same shared core scored on both tasks; reuse ledger; rule-category ablation |
| Robustness via gates | Schema-validity, repair, evidence-validity rates per architecture |
| Calibrated uncertainty | Accuracy-by-confidence, closed-flag frequency, calibration view |
| Transparency | Per-prediction trace examples; corpus error taxonomy with component attribution |
| What the LLM adds | Three-way comparison (rules / llm_only / hybrid), SF and all-9 |
| Deterministic rules as a controlled variable | Component + rule-category ablation tables |

These sit alongside the Gan 2026 equivalents to form the two-task reliability
story.

## 2. Figures

- Two-task overview (deep SF extraction vs broad phenotyping) with the shared
  architecture in the middle.
- Per-entity F1 vs benchmark, three architectures (grouped bars).
- Three-way comparison radar/table.
- A worked SF example end-to-end: source → candidates → assessment →
  normalization → mention, with the evidence trail.
- Ablation waterfall (rule-category and component deltas).

## 3. Milestones

| # | Milestone | Definition of done |
| --- | --- | --- |
| M0 | Foundation | loader + label scorer + thesis (DONE) |
| M1 | Contract & core | shared layer lifted, prediction schema + validation gate, gold profile committed, Gan 2026 suite green ([[01_shared_core_and_extraction_contract]]) |
| M2 | SF rules baseline | deterministic SF dev F1 + error list ([[02_rules_based_architecture]]) |
| M3 | SF LLM-only | both configs dev F1, gates reported ([[03_llm_only_architecture]]) |
| M4 | SF hybrid | live candidate sets, dev F1, routed taxonomy ([[04_hybrid_architecture]]) |
| M5 | SF three-way + cross-pollination | comparison report; de-overfit rules / refined prompts ([[05_*]],[[07_*]]) |
| M6 | All-9 scale-up | all entities, all architectures, overall dev F1 ([[02]]–[[04]]) |
| M7 | Benchmark assault | dev clears 0.87/0.90 for ≥1 (min) / all three (target) architectures |
| M8 | Authorized audit | frozen full-200 + test reads, full reliability artifact set ([[06_evaluation_and_benchmark_protocol]]) |
| M9 | Paper outputs | all tables/figures for both tasks assembled ([[07]],[[08]]) |

## 4. Tier checkpoints (from the thesis)

- **Minimum** reached at M8 if ≥1 architecture's authorized audit clears the bar.
- **Target** reached when all three clear it with the comparison + ablations.
- **Thesis-complete** when the two-task story (shared core reused, both
  benchmarks addressed, full transparency artifacts) is assembled at M9.

## 5. Dependencies & ordering

M1 gates everything (the contract). M2→M4 are parallelizable per architecture
once M1 lands, but rules (M2) should lead so the candidate stage (M4) and the
de-overfitting comparison (M5) have a baseline. M6 needs M5's lessons. M7→M8 are
sequential and gated. M9 consumes all prior artifacts.

## 6. Project-status integration

Reflect these milestones in `PROJECT_STATUS.md` and `CONTEXT.md` as they land,
and keep each satellite's status-update section current (inline, as decisions
crystallize — the Gan 2026 three-way plan convention). The run registry is the
source of truth for which experiments back which milestone.
