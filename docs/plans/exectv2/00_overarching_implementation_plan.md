> **Status: HISTORICAL** — design record only. See [`ACTIVE_ROADMAP.md`](../ACTIVE_ROADMAP.md) and [`recent_plan_rationalisation_2026-06-25.md`](../recent_plan_rationalisation_2026-06-25.md).

# ExECTv2 — Overarching Implementation Plan

Date: 2026-06-09
Author: Claude
Status: planning spine. This document defines the end-to-end workstream for the
second task (ExECTv2 broad epilepsy phenotyping) and points to the satellite
plans that fully specify each slice. It is governed by
`docs/design/reliability_thesis.md` (why) and `docs/design/architecture.md`
(package shape). Holdout-facing work is gated exactly as in the Gan 2026
workstream — see Phase gates below and [[06_evaluation_and_benchmark_protocol]].

---

## 0. What "done" means

Beat the published ExECTv2 benchmark (Fonferko-Shadrach 2024:
**0.87 F1 per item / 0.90 per letter**, overall, with all features) using the
**three canonical architecture families** — rules-based, LLM-only, hybrid —
built over **one shared modular core** that is demonstrably reused from the Gan
2026 task, with the schema-validation and evidence-verification gates active,
and with the transparency artifacts (evidence trails, error taxonomy, ablations,
calibrated uncertainty) that distinguish this work from black-box clinical NLP.

Three tiers, from `reliability_thesis.md` §7:

- **Minimum**: beat the benchmark with ≥1 architecture, gates active.
- **Target**: beat it with all three, with a three-way comparison + ablations.
- **Thesis-complete**: the above on both tasks, shared core demonstrably reused,
  plus full transparency artifacts.

The headline benchmark number is **overall across all 9 entities**. Seizure
Frequency is the bridge entity we build and prove the machinery on first
(deepest reasoning, weakest benchmark cell at **0.66 per item / 0.68 per letter**
— Table 1, Fonferko-Shadrach 2024), then we generalize to the full entity set.

---

## 1. Strategy in one paragraph

We build the data/scoring foundation first (done), then a single shared
extraction contract and core (Phase 1). We bring up the three architectures on
**Seizure Frequency only** (Phases 2–4), reusing the Gan 2026 normalization
model and rule taxonomy, and run a Gan-2026-style three-way comparison +
cross-pollination on that one entity (Phase 5) to validate that the whole
machine works and that capability transfers. We then **scale the same machine to
all nine entities** (Phase 6), and run the full benchmark assault to clear
0.87/0.90 with all three families (Phase 7). Transparency, ablations, and paper
outputs are produced continuously and consolidated last (Phase 8). Every
development read is on a **dev split**; the benchmark-comparable full-200 and
held-out reads are **frozen, authorized audits**.

---

## 2. Phase map

| Phase | Goal | Satellite | Gate |
| --- | --- | --- | --- |
| **0** | Foundation: loader, label-based scorer, thesis | (done — see §3) | none |
| **1** | Shared core + ExECTv2 extraction contract & prediction schema; normalization reuse from Gan 2026 | (DONE — see reuse ledger §5) | none (structural) |
| **2** | Rules-based Seizure-Frequency extractor → first dev benchmark read | **DONE (2026-06-10) — see §3a** · [[02_rules_based_architecture]] | none (dev-only) |
| **3** | LLM-only Seizure-Frequency extractor | **DONE (2026-06-10) — per_entity phrase_only 0.486/0.698, sf_semantic 0.135/0.264; both beat det. baseline per-letter** · [[03_llm_only_architecture]] | none (dev-only) |
| **4** | Hybrid Seizure-Frequency extractor | **DONE (2026-06-11) — dev140 gpt-4.1-mini: phrase_only 0.585/0.781 (best of any family; only per-letter to clear the 0.68 SF target), sf_benchmark 0.327/0.578; registered** · [[04_hybrid_architecture]] | none (dev-only) |
| **5** | Three-way SF comparison + cross-pollination (mirror the Gan 2026 plan) | **Comparison harness DONE (2026-06-11) — `reports/three_way_comparison.py` + first dev artifact; cross-pollination ongoing** · [[05_experiment_harness_and_loops]], [[07_transparency_ablations_and_paper_outputs]] | none (dev-only) |
| **6** | Scale all three architectures to the full 9-entity set | **LLM-only all-9 slice DONE (2026-06-12) — dev140 semantic overall 0.087/0.236; full-200 frozen audit semantic overall 0.084/0.232, benchmark with-CUI 0.000/0.000; deterministic + hybrid all-9 still deferred. Details: [[03_llm_only_architecture]] §3b** · [[02_rules_based_architecture]], [[04_hybrid_architecture]] | none (dev-only) |
| **7** | Full benchmark assault: clear 0.87/0.90 overall with all three; held-out + frozen full-200 audit | **SF-cell audit DONE (2026-06-11); first all-9 overall audit DONE for LLM-only (2026-06-12, authorized), not competitive: semantic 0.084/0.232, with-CUI 0.000/0.000. Overall audits for hybrid/deterministic remain future gated work** · [[06_evaluation_and_benchmark_protocol]] §8 | **explicit user authorization** for held-out / full-200 audit |
| **8** | Consolidate transparency, ablations, error analysis, paper tables/figures | [[07_transparency_ablations_and_paper_outputs]], [[08_paper_outputs_and_milestones]] | authorization for any final holdout numbers reported |

Phases 1–6 are development mechanics on the dev split and need no new
authorization. Phase 7's held-out and full-200 audits are the only
holdout-facing steps and follow the same frozen-aggregate, no-row-tuning
discipline proven in the Gan 2026 workstream.

---

## 3. Phase 0 — Foundation (DONE)

Already shipped this session:

- `src/clinical_extraction/core/scoring.py` — task-neutral PRF1 (multiset
  matching, micro-averaging). The DRY home for precision/recall/F1 arithmetic.
- `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/data.py` —
  `load_letters()` over all 200 letters; `ExectLetter`/`ExectAnnotation`. Gold
  offsets retained for provenance but never used (they drift; matching is on
  labels).
- `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/scoring.py` —
  `normalize_phrase`, `MatchConfig` (`PHRASE_ONLY` / `PHRASE_AND_FEATURES`),
  `score_entity()` returning per-item and per-letter F1.
- `docs/design/reliability_thesis.md` — the project thesis.
- Tests: `tests/test_core_scoring.py`, `tests/test_exectv2_data.py`,
  `tests/test_exectv2_scoring.py` (19 passing; gold-vs-gold = 1.0, corpus shape
  verified: 200 letters / 263 SF mentions / 142 SF letters / 92 seizure-free).

This means: **the moment any architecture emits `ExectLetter` predictions, we
can score them against the benchmark axes.**

---

## 3a. Phase 2 — Rules-based Seizure Frequency (DONE, 2026-06-10)

The deterministic SF extractor is built, scored on the dev split, error-analysed,
and portability-tagged — the first real benchmark signal of the whole task.
Detail and gap analysis: [[02_rules_based_architecture]] §3a; row-level error
analysis and noise ceiling: `docs/research/exectv2_sf_error_analysis_2026-06-10.md`.

- **Result (dev, 140 letters / 187 gold SF mentions)**: per-item F1 `phrase_only`
  **0.382** / `sf_semantic` **0.272** / `sf_benchmark` **0.272**; per-letter
  0.604 / 0.482 / 0.482; per-letter precision **0.868**. Pinned in
  `tests/test_exectv2_deterministic_sf.py::test_dev_split_baseline_pinned`.
- **Shape**: anchor + association pipeline (`deterministic/{pipeline,association,
  overlap}.py`) with named, portability-tagged rule families (anchor / rate /
  seizure_free / change / temporal) and a finite phrase→CUI lexicon. The largest
  precision lever was a same-sentence, bounded-gap association rule.
- **De-overfitting result**: per-statement emission (D8) was implemented and
  measured **net-negative** on dev, so reverted — recorded, not hidden.
- **Noise ceiling (quantified)**: ≈26.7% of gold SF mentions are un-winnable on
  exact text (19.8% offset-drift corruption + 7.0% singular/plural). Scoring kept
  as exact match per the scope decision; the corrupt-adjusted `sf_semantic`
  recall is ≈0.31.
- **Still below the SF benchmark bar (0.66 per item / 0.68 per letter).** The
  remaining gap is the noise ceiling plus a small, precision-risky recall tail
  (logged in 02 §3a), not a missing mechanism. The architecture and tests are
  ready to generalize in Phase 6.

Phases 1–5 are complete on Seizure Frequency: shared core + contract (1), the
deterministic (2), LLM-only (3), and hybrid (4) SF extractors, and the three-way
comparison harness (5) are all built, run on dev, and registered. The **Phase 7
frozen SF-cell audit is also done** (2026-06-11, authorized): `run_phase7_audit`
ran each architecture once over the full 200, with bootstrap CIs and the
dev→audit gap, registered immutably (06 §8). **No architecture clears the SF cell
0.66/0.68** on the with-CUI headline — best is rules at 0.321/0.539, hybrid
0.246/0.470, llm_only 0.000 (emits no CUI). The **LLM-only all-entity scale-up
slice is also complete** (2026-06-12): the user authorized Phase 6 plus the
Phase 7 overall audit and chose gpt-4.1-mini first. The resulting all-9
single-pass extractor is contract-clean but not competitive: dev140 semantic
overall F1 `0.087` per-item / `0.236` per-letter; frozen full-200 audit semantic
overall `0.084` / `0.232` with benchmark with-CUI `0.000` / `0.000`. The
remaining Phase 6-family work is deterministic and hybrid all-9 scale-up, not
the LLM-only slice. Details and interpretation: [[03_llm_only_architecture]] §3b.

A note on the audit ordering: Phase 7 is normally "after dev is locked" for the
whole entity set, but SF is locked and is the benchmark's hardest cell, so the
SF-cell audit was run now as the honest frozen read of where the machine stands.
It is not the overall headline (that needs the 9 entities); it is the
benchmark-comparable SF number, and it says the single-architecture SF cell is
not yet beaten — the remaining gap is the documented noise ceiling plus
hybrid's attribute generalization, not a missing mechanism.

---

## 4. Guardrails (inherited from the Gan 2026 workstream)

These are not new; they are the project's existing discipline applied to task 2.

- **Score on labels, not gold offsets** (offsets drift post spelling-correction).
- **Define our own dev/test splits** and develop only on dev. The benchmark
  scored on all 200, so the headline comparable number is a **frozen full-200
  audit** run once development is locked — never iterated against.
- **No row-level holdout tuning. No hidden repair, no holdout-tuned fallback, no
  verifier-written labels.**
- **Every rule and prompt rule must be named, portability-classified
  (`general` / `clinical_epilepsy` / task / dataset / `benchmark_format`),
  source-backed, trace-visible, and ablatable** — the standard from
  `architecture.md` and the Gan 2026 Phase 2 de-overfitting work.
- **Model choice is an experimental variable**, recorded as run metadata
  (`docs/design/model_strategy.md`). Report gpt-4.1-mini, qwen3.6-35b,
  deepseek-v4-flash etc. as distinct conditions, never blended.
- **Model-facing prompt language drops internal architecture vocabulary**
  (ADR 0015; enforced by a prompt-hygiene test).
- **Reuse before rebuild**: the runner/registry/report/observatory machinery is
  reuse surface (see [[05_experiment_harness_and_loops]]); new code is justified
  only where the task genuinely differs (span-free set scoring, multi-entity
  output, attribute structure).

---

## 5. The reuse ledger (DRY mandate, made concrete)

The whole point of task 2 is to collect the modular dividend. This ledger names
what is reused, lifted, or net-new. It is maintained as the build proceeds;
[[01_shared_core_and_extraction_contract]] owns the detail.

| Capability | Decision | Where |
| --- | --- | --- |
| PRF1 arithmetic | **lifted to core** | `core/scoring.py` (done) |
| Evidence substring / repair utils | **reused as-is** | `core/evidence.py` |
| Pipeline protocol, result container, validation types | **reused as-is** | `core/pipeline.py`, `core/validation.py` |
| Seizure-frequency normalization (count/range × period × anchor → rate) | **DONE — lifted to `tasks/shared/epilepsy/normalization.py`**; `contract/label_parser.py` is now a re-export shim; Gan 2026 suite green | `tasks/shared/epilepsy/normalization.py` |
| Seizure-free detection logic | **DONE — `SeizureFreeAssertion` + `is_zero_count_mention` in `tasks/shared/epilepsy/seizure_free.py`**; vocabulary lifted to `terms.py`; Gan 2026 rules import from shared | `tasks/shared/epilepsy/{seizure_free,terms}.py` |
| ExECTv2 extraction contract (prediction schema + entity registry + validation) | **DONE — `contract/{prediction,entities,validate}.py`**; gold-as-prediction validates clean, scores 1.0 | `tasks/epilepsy_phenotyping/exectv2/contract/` |
| Rule taxonomy + portability metadata pattern | **reused pattern**, new rule instances | exectv2 deterministic |
| Runner / `PipelineArchitecture` config pattern | **reused pattern**, new ExECTv2 runner | exectv2 |
| Run registry + `validate_run_registry_artifacts` | **reused as-is** | `experiments/registry.jsonl` |
| Report base (`reports/base.py`) + three-way comparison shape | **DONE — `reports/three_way_comparison.py`** (model-parameterized rules/llm_only/hybrid table over the six shared axes; `ARCHITECTURE_FAMILY` grouping; rules computed live, llm_only/hybrid from the registry; entity-parameterized for the Phase 6 all-9 table) | `tasks/epilepsy_phenotyping/exectv2/reports/` |
| Observatory | **reused / extended** if useful | observatory |

Where "lift" appears, the rule is: extract the genuinely task-neutral part into
`core` (or a shared epilepsy layer under `tasks/`), leave the dataset-specific
part in the task, and cover the lift with tests so Gan 2026 behavior is provably
unchanged (the same byte-identical-staging discipline used for the deterministic
canonical pipeline, ADR 0013).

---

## 6. Sequencing rationale

- **Seizure Frequency first, all entities later.** It is the deepest reasoning
  target, the weakest benchmark cell, and the direct transfer test from task 1.
  Proving the full three-architecture machine on one hard entity de-risks the
  9-entity scale-up, which is then mostly breadth, not new mechanism.
- **Rules → LLM-only → Hybrid.** Rules first gives a portable, reproducible
  baseline and a like-for-like comparator to the benchmark's own rule-based
  pipeline. LLM-only sets the unaided-reasoning bar. Hybrid combines, informed by
  the first two — the same order that worked for Gan 2026.
- **Comparison before scale.** The Phase 5 three-way comparison on SF surfaces
  cross-pollination (de-overfit rules, refine prompts) cheaply on one entity
  before that effort is multiplied across nine.
- **Audit last, once.** The benchmark-comparable number is expensive in
  credibility if iterated against; it is produced once, frozen, authorized.

---

## 7. Risk register

| Risk | Mitigation |
| --- | --- |
| Offset drift corrupts matching | Already handled — label-based matching, verified gold-vs-gold = 1.0 |
| "All features" match too strict / CUI policy ambiguous | `MatchConfig` makes the policy explicit and ablatable; pin the benchmark-comparable policy in [[06_evaluation_and_benchmark_protocol]] and report sensitivity |
| Overfitting to 200-letter set | Dev/test split + frozen full-200 audit; de-overfitting discipline from Gan 2026 |
| Multi-entity scope balloons effort | SF-first proves machine; entities share the contract + runner; per-entity work is rules/prompts, not architecture |
| Long live LLM runs killed at ~9 min by harness | Use PowerShell `Start-Process` detached pattern (documented in the Gan 2026 plan §8a) |
| Annotation noise in gold (stray attributes on SF) | Quantify and document; decide per-attribute inclusion in the match policy |

---

## 8. Satellite index

1. [[01_shared_core_and_extraction_contract]] — package layout, core/shared
   lifts, ExECTv2 data contract, prediction schema, normalization reuse.
2. [[02_rules_based_architecture]] — deterministic ExECTv2 extractor, rule
   taxonomy, SF-first then all entities.
3. [[03_llm_only_architecture]] — single-/multi-pass LLM extractor, schema +
   evidence gates, prompt design and versioning.
4. [[04_hybrid_architecture]] — candidate-set + assessment + deterministic
   normalize, routing/verification.
5. [[05_experiment_harness_and_loops]] — runner, splits, registry, reports,
   experiment-loop discipline, the three-way comparison harness.
6. [[06_evaluation_and_benchmark_protocol]] — match policy, split protocol,
   benchmark comparison, authorization gates, holdout audit procedure.
7. [[07_transparency_ablations_and_paper_outputs]] — evidence trails, error
   taxonomy, component + rule ablations, uncertainty calibration.
8. [[08_paper_outputs_and_milestones]] — tables/figures, milestones, the path to
   the paper.
9. [[12_holistic_clinical_finding_architecture]] — refactor Plan 11 around a
   unified clinical finding store, entity lenses, manifest-driven assembly, and
   explicit scoring views.
10. [[13_dedup_clinical_facts_llm_only]] — **PRIMARY FOCUS (2026-06-23).**
    De-duplicated clinical-fact recovery on the `clinical_headline` surface via a
    single-prompt attribution-clean LLM-only system; goal `>0.900` with
    GPT-4.1-mini, then DeepSeek/Qwen. Rich-schema (certainty/negation/operand)
    runs are demoted to 1–2 comparison baselines (cleanup phase).
