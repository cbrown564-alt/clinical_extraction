> **Status: HISTORICAL** — design record only. See [`ACTIVE_ROADMAP.md`](ACTIVE_ROADMAP.md) and [`recent_plan_rationalisation_2026-06-25.md`](recent_plan_rationalisation_2026-06-25.md).

# Closing-Campaign Orchestration Plan — Binding the Three 06-27 Threads

**Date:** 2026-06-27
**Status:** Orchestration plan — sits *on top of* three source docs, does not supersede them.
**Vehicle:** Thermo-nuclear `/loop` pattern (orchestrator commits to `main`; reconcile plan vs repo each tick; sub-agents forbidden from git).

## What this binds

Three documents written today are one closing campaign at three altitudes, sharing
one spine — **the cross-task shared-component story**:

1. [`decomposition_research_impact_review_2026-06-27.md`](../research/decomposition_research_impact_review_2026-06-27.md)
   — engineering enablement: what the cleanup made queryable, and the one verified
   caveat (SF registry catalog-indexed but legacy-executed).
2. [`evidence_validity_unification_plan_2026-06-27.md`](evidence_validity_unification_plan_2026-06-27.md)
   — a concrete shared-component *build*: one canonical evidence-groundedness metric
   in `core/`. The cleanest worked example of "shared core demonstrably reused."
3. [`closing_stage_research_critique_2026-06-27.md`](../research/closing_stage_research_critique_2026-06-27.md)
   — the paper-facing claims the first two make true or false. Holds the
   **submission blocker** (the unowned benchmark-metric pivot).

The binding is mechanical, not thematic:
- The **portability decomposition** (decomp §1a) *is* the **benchmark reconciliation**
  (critique pri-1). Same replay over the same artifacts via `definitions.yaml`.
- The **evidence-validity build** (plan) *produces the cleanest subject* for the
  **cross-task shared-component ablation** (decomp §1b + critique pri-2).
- The **integrity gates** (SF-registry audit, `shadow_diff` CI gate) are what make
  both numbers trustworthy as *rule-level* and *equivalence-checked* surfaces.

## Verified load-bearing paths (HEAD, 2026-06-27)

- `…/exectv2/reports/component_ablation/definitions.yaml` (portability categories) ✓
- `…/exectv2/reports/reliability/catalog.yaml` (provenance ledger) ✓
- `src/clinical_extraction/core/evidence.py` (repair cascade) ✓
- `…/sf_surface_registry/builders/_legacy_impl.py` + `_legacy_residual.py` (legacy
  execution confirmed) ✓; bonus seam `…/builders/projection_evidence_repair.py` ✓
- Evidence call sites: `agentic/llm_event_reasoner.py`, `runners/llm_only_canonical.py`,
  `assembly/lens_ops.py` **plus** sibling lenses
  (`investigations.py`, `prescription.py`, `seizure_frequency.py`, `diagnosis.py`) ✓
- `.github/workflows/ci.yml` — **no** `parity`/`shadow` step ✓

---

## Standing guardrails (apply to every workstream)

- **Full-200 authorized for M1 only, aggregate-only** (Decision B = yes): recompute
  the reconciliation rate on full-200 under the holdout protocol; **no row-level
  read**. All other workstreams remain dev/validation-side.
- No reopening the Gan accuracy-optimization freeze.
- Replay-only recompute keeps the aggregate-only contract on frozen/locked rows.
- Sub-agents do analysis / code / replay; **the orchestrator alone does git**.
- Each `/loop` tick reconciles this plan against repo HEAD before dispatch.

---

## Workstreams

IDs are stable handles for dispatch. "Replay" = saved-output recompute, no model
calls. "Soft-dep" = strengthened by, not blocked by.

### Track I — Integrity foundations (engineering/analysis; parallelizable; unblock *trust*)

- **I1 — Audit SF registry legacy-delegation depth.** (decomp §3a / pri-2)
  Per rule-family verdict: promote catalog to own behavior, or label honestly as
  catalog-indexed / legacy-executed in methods text. Output: a per-family table +
  the exact sentence the paper may claim. *Gates the credibility of M1's rule-level
  reads, not M1 itself.*
- **I2 — Promote `shadow_diff` to a named CI gate.** (decomp §3d / pri-3)
  Add a `parity` step to `ci.yml` running the legacy↔registry diff. Pure engineering.
- **I3 — Index `artifact_analysis/`.** (decomp §2c / pri-4)
  One-page README mapping what each of the 66 quarantined modules computed, so it's
  an archive not a memory hole. Quick.

### Track M — Measurement & reconciliation (replay-only; produces the numbers the paper needs)

- **M1 — Portability decomposition → benchmark-surface reconciliation.**
  (decomp §1a / pri-1 + critique §1 / pri-1 — **SUBMISSION BLOCKER**)
  Re-score existing artifacts with `benchmark_format` components toggled off using
  only the `definitions.yaml` category field. Report clinical-recovery F1 vs headline
  F1 across the GPT / DeepSeek / Qwen rows in `catalog.yaml`; report the like-for-like
  number and the **rules > hybrid inversion** as findings. **Full-200 authorized,
  aggregate-only** (Decision B): report the reconciliation on full-200 under the
  holdout protocol, no row-level read; carry dev140 (`0.3877`/`0.6972`) alongside for
  continuity. Doubles as a pressure-test that `definitions.yaml` actually drives
  scoring. Soft-dep I1 (for honest caveating). Near-zero new code.
- **M2 — Evidence-validity unification.** (the dedicated plan, Phases 0–4)
  One canonical `score_evidence_set` in `core/evidence.py`; replace the 3 named +
  sibling lens call sites; replay-recompute the 15 surfaced/promoted rows; one doc.
  Gate-widening (plan Phase 5) stays quarantined under protocol. Produces the
  canonical shared component M3 ablates and removes the Qwen footnote P4 needs.
- **M3 — Cross-task shared-component ablation.** (decomp §1b + critique pri-2 — thesis-complete)
  Turn one shared component off, report the delta on **both tasks at once**.
  Primary subject = the M2 evidence-groundedness component (cleanest shared-core);
  secondaries = date-arithmetic policy, SF-normalization structure. Soft-dep M2.
  Validation-side, aggregate, no new freeze.

### Track P — Paper reframes & restructure (writing; consumes Track M)

- **P1 — Benchmark reconciliation subsection.** (critique pri-1) Consumes M1 + I1.
  First-class subsection: the number, the offset-drift non-reproducibility reason
  (thesis §5), the named closeable fidelity lever, the rules>hybrid inversion.
  Retire the dependence on the 60-row checkpoint.
- **P2 — Promote DeepSeek ≥ GPT.** (critique pri-4) Consumes `catalog.yaml` + M1/M2
  recompute. Reframe from apology to evidence for the model-agnostic thesis.
- **P3 — Wall-transfers reframe.** (both reviews; highest research value — **in scope**,
  Decision A) Probe ExECTv2 SF with the same forward-observable features used on Gan.
  Gated on **full S1** completing the `agentic/` decomposition.
- **P4 — Tighten calibration claim.** (critique pri-5) Consumes M2. Near-base-rate
  Brier honesty; external signal not self-confidence; drop the Qwen apologetic footnote.
- **P5 — Decide consensus/fresh selector fate.** (critique pri-3) Keep only if it
  survives a pre-registration check; else cut and let the closeout headline stand.
- **P6 — Capability-first manuscript restructure.** (critique §4) Last; consumes all.

### Track S — Structural long-pole (research-enabling; **in scope, full**)

- **S1 — `agentic/` decomposition onto `run_driver` (full).** (decomp §3b / pri-5)
  21k LOC across 11 files (`fresh_evidence_reasoner.py` 2,081;
  `direct_boundary_critic_rescue.py` 1,554; `cross_model_structured_event_adjudicator.py`
  1,508; `consensus_fresh_agreement_selector.py` 1,348; …) migrated onto
  `agentic/run_driver.py`. Highest-leverage remaining structural work; gates P3 and
  the broader reliability/semantic-entropy swing. **This is now the campaign's
  longest pole — it starts in Wave 1, not Wave 3.**
  - **Coordination with M2:** M2 re-points the evidence call site in
    `agentic/llm_event_reasoner.py` and must leave the `fresh_evidence_reasoner.py`
    gate byte-for-byte unchanged (plan Phase 2 guard). Land M2's agentic call-site
    swap **before** S1 begins restructuring those two files, or S1 owns the agentic
    surface and M2 rebases onto it. The orchestrator resolves this each tick — do not
    let both edit `agentic/` in the same wave uncoordinated.

---

## Wave schedule (orchestration order)

**Wave 1 — parallel, no cross-deps.** I1, I2, I3, M1 (full-200 aggregate), M2-Phase0
(audit), **and S1 kicks off here** (longest pole — must run concurrently with the
measurement track, not after it).
→ Clears the blocker's data (M1) + integrity gates, and starts the structural pole.

**Wave 2 — depends on Wave 1.** M2-Phases1–4 (agentic call-site swap coordinated with
S1), M3, P1, P2, P4, P5. S1 continues in background.
→ Builds the shared component, measures the dividend, writes the reframes.

**Wave 3 — research swing (gated on S1 done).** P3 wall-transfer probe through the
decomposed `agentic/`.

**Wave 4 — close.** P6 restructure (consumes P1–P5 and P3).

## Critical path

Two co-critical chains now run in parallel:
- **Reconciliation chain (blocker):** `M1 → P1`, with `I1` feeding P1's caveats; then
  the cheap consumes-M1/M2 reframes `P2 / P4 / P5`.
- **Structural chain (longest pole):** `S1 → P3`.

`P6` joins both at the end. Because full S1 is in scope, **S1 likely dominates total
duration** — start it Wave 1 and treat P3 as the gate, not the reconciliation work.
Coordinate M2 vs S1 on `agentic/` per the Track S note.

## Dispatch mapping (sub-agent → workstream)

- `Explore` / `general-purpose` → I1 (read-only audit), I3 (index).
- `general-purpose` → I2 (CI edit), M2 (engineering + replay), M1 (replay).
- `gan2026-error-analyst` (read-only) → P3 forward-observable feature inventory.
- `gan2026-experiment-runner` → M3 ablation runs; S1-slice extraction.
- `gan2026-scribe` → P1–P6 durable docs + scoreboard.
- Orchestrator (`/loop`) → reconcile, commit, gate APPROVE points.

## Acceptance gates

1. **M1:** clinical-recovery vs headline F1 table across GPT/DeepSeek/Qwen exists;
   `definitions.yaml` proven to drive scoring; rules>hybrid inversion reported.
2. **M2:** one function owns evidence validity (grep finds no bespoke
   `evidence in note_text`); 15 rows re-scored; Qwen gap explained by `REPAIRED_*`,
   not lost; no prediction/accuracy number moves (Phases 1–4).
3. **M3:** one shared component, delta reported on both tasks, aggregate-only.
4. **I-track:** SF-registry honesty verdict written; `parity` step green in CI;
   `artifact_analysis/` README exists.
5. **P-track:** benchmark reconciliation is a first-class subsection; DeepSeek &
   wall-transfer (if in scope) promoted; calibration claim matches evidence.

---

## Decisions (resolved 2026-06-27)

**Decision A — Wall-transfer swing in scope? → YES, full S1.** Track S decomposes
`agentic/` onto `run_driver` in full (not a slice), then P3 runs the wall-transfer
probe. Highest research value; this is the campaign's longest pole and starts Wave 1.

**Decision B — Full-200 read for M1? → YES, aggregate-only.** M1 reports the
benchmark reconciliation on full-200 under the holdout protocol (no row-level read),
carrying dev140 alongside for continuity.

## Source artifacts

- The three 06-27 docs linked above.
- `docs/plans/thermo_nuclear_code_quality_audit_plan_2026-06-26.md` (loop conventions).
- Verified paths listed under "Verified load-bearing paths."
