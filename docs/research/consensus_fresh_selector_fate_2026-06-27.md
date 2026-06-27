# Consensus/Fresh Selector Fate — Pre-Registration Check

Date: 2026-06-27

Status: analysis-only. No code changes, no git, no holdout re-runs.

Scope: decide whether `gan2026_consensus_fresh_agreement_selector_v0_9` deserves
a paper-facing or promoted-architecture role, or should be cut so the Gan closeout
headline stands alone.

## Question

Does the consensus/fresh selector add **defensible value beyond the frozen closeout
headline** (single structured-event pass `364/450 = 0.809`; V12 ceiling
`379/450 = 0.842`), or is it fragile complexity that barely clears a late
promotion bar?

## Pre-Registration Criteria (applied retrospectively)

These criteria mirror the frozen protocol
(`docs/experiments/gan2026/frozen_test/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_protocol_2026-06-26.md`)
plus the closing-campaign guardrail: **survive only if it adds a claim the closeout
does not already own.**

| # | Criterion | Threshold | Rationale |
| --- | --- | --- | --- |
| P1 | Holdout selected Purist beats closeout production headline | Selected > `364/450` | Selector must outperform the chosen architecture, not only the deterministic floor |
| P2 | Holdout selected Purist approaches ceiling comparator | Selected within defensible margin of `379/450` | Hybrid stack should justify its complexity vs V12 |
| P3 | Changed-label precision with margin | ≥ `0.60` with ≥ `0.02` headroom, or validation precision holds on holdout | Bare threshold clearance is fragile |
| P4 | Stable pass across source-symmetry variants | Same directional pass on constrained and exact audits | Avoid variant-selection suspicion |
| P5 | Validation portability without weak-band warnings | Weekly/submonthly precision ≥ `0.60`; no “revise, not freeze” from origin artifacts | Transfer risk must be low before holdout claim |
| P6 | Net gain not dominated by a failing variant | Passing variant has ≥ net gain of any failing variant | Prevents “pick the passing run” optics |
| P7 | Adds a novel paper claim beyond closeout | New, reviewer-defensible insight not covered by 0.809 / 0.842 / “hybrid buys little” | Closeout already settled the headline |
| P8 | Formal gate battery (G1–G4) | All predeclared gates pass on exact-source path | Necessary but not sufficient |

## Evidence Table

| Criterion | Result | Evidence | Pass? |
| --- | --- | --- | --- |
| **P1 — Beat production headline** | Selected `359/450` (`0.7978`) | Exact Gate 4 (`experiments/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate4_exact_aggregate_audit_2026-06-26.md`); closeout single SE `364/450` (`docs/research/gan2026/retrospectives/gan2026_research_closeout_synthesis_2026-06-17.md` §Part I) | **FAIL** (−5 rows vs headline) |
| **P2 — Near ceiling** | Selected `359/450` vs V12 `379/450` | Closeout synthesis row 8; exact Gate 4 | **FAIL** (−20 rows vs ceiling) |
| **P3 — Precision with margin** | Exact holdout `0.6000`; validation `0.7347` | Exact Gate 4: 21 W→C, 5 C→W, 35 changed; validation750 replay (`experiments/archive/gan2026_validation750_iterations/gan2026_consensus_fresh_agreement_selector_v0_9_validation750_no_call_replay_2026-06-15.md`) | **FAIL** (holdout at floor ±0; 40% of changed labels wrong) |
| **P4 — Cross-variant stability** | Constrained **fail**; exact **pass** | Constrained Gate 4 (`348/450`, precision `0.5909`, 7 C→W); exact Gate 4 (`359/450`, precision `0.6000`, 5 C→W); critique §2 (`docs/research/closing_stage_research_critique_2026-06-27.md`) | **FAIL** |
| **P5 — Band portability** | Weekly `0.40`, submonthly `0.20` on validation changed rows | validation750 band table; Gate 1 names both as “portability risks” (`experiments/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate1_hard_slice_audit_2026-06-26.md`) | **FAIL** |
| **P6 — Gain vs failing variant** | Passing exact `+16`; failing constrained `+19` | Constrained vs exact Gate 4 aggregates; critique §2 | **FAIL** |
| **P7 — Novel claim beyond closeout** | Reinforces “hybrid buys little” | Closeout: V12 only `+15` over single SE; selector below single SE and adds 9-version selector ladder over det+consensus+fresh | **FAIL** |
| **P8 — Gate battery** | G1 pass, G2 pass (24 synthetic rows), G3 exact pass, G4 exact pass | Frozen gate reports 2026-06-26; constrained G4 fails | **PASS** (exact path only) |

### Supporting context

**Iteration arc.** v0.1→v0.9 over 2026-06-14–2026-06-26 (nine policies, stacked
rescues). Origin validation artifact decision text: *“Revise, not freeze”*
(`consensus_fresh_agreement_selector.py` `_decision_text_for_selector`; validation750
replay §Decision). Holdout work completed **after** the 2026-06-17 closeout that
already froze single SE and V12.

**Comparator choice.** Exact Gate 4 deterministic floor is `343/450`; headline
single SE is `364/450`. The selector’s `+16` net gain is vs the rules-tool floor,
not vs the promoted architecture — a bounded component-ladder read, not a
production upgrade.

**Residual headroom.** Gate 1: `11/17` selected-wrong residual rows have no
Purist-correct component among det/consensus/fresh; selector cannot fix
component-generation failures.

**Manuscript status.** `docs/research/paper_manuscript_2026-06-26.md` §4.1.2 reports
both Gate 4 audits; “Do Not Use” list correctly flags constrained Gate 4 as not
promoted, but still elevates exact-source as “frozen exact v0.9 selector holdout.”

## Synthesis

The selector **clears its own narrow Gate 4 promotion bars** on the exact-source
path (gain ≥10, C→W ≤5, precision ≥0.60) but **fails the closing-campaign
pre-registration bar**: it does not beat the closeout headline, shows
variant-dependent pass/fail with the higher-gain run failing, holds changed-label
precision at the floor (two in five holdout label changes wrong), and its
validation band weaknesses (weekly/submonthly) were flagged before holdout. The
closeout already states the durable Gan result — single SE `0.809`, V12 ceiling
`0.842`, hybrid complexity buys little — and this selector substantiates that
negative finding rather than overturning it.

Including it as a promoted or holdout-facing result invites the critique in
§2 of the closing-stage research critique: a barely-passing late add-on whose
passing variant is not the highest-gain variant.

---

## RECOMMENDATION: **CUT**

Cut the consensus/fresh selector from paper-facing promoted results and
manuscript headline tables. Let the closeout headline stand:

- **Production:** single GPT structured-event pass, `364/450` Purist (`0.809`)
- **Ceiling comparator:** V12 fresh-evidence hybrid, `379/450` Purist (`0.842`)

**Permitted retention (optional, one sentence max in appendix):** validation-side
component-ladder evidence that corroboration-gated switching over a deterministic
floor can yield validation gains (`733/750`, 0 C→W) but **does not transfer** to
a holdout score above the simpler promoted architecture — consistent with closeout
finding #3 (“hybrid/ensemble/guard apparatus buys little”).

### Manuscript actions (reporting only)

1. Remove §4.1.2 and Table 3 (consensus/fresh Gate 4 audits) from
   `docs/research/paper_manuscript_2026-06-26.md`.
2. Remove exact-source “frozen v0.9 selector holdout” from promoted-result prose;
   retain constrained audit only if needed as a one-line negative result (“late
   hybrid selector did not beat single SE on holdout”).
3. Do not add selector rows to architecture comparison tables alongside single SE
   and V12.

### Deletion list (for a future cleanup pass; no action in this task)

**Source module and tests**

- `src/clinical_extraction/tasks/seizure_frequency/gan2026/agentic/consensus_fresh_agreement_selector.py`
- `tests/test_gan2026_consensus_fresh_agreement_selector.py`

**Build drivers**

- `experiments/build_gan2026_v05_boundary_rescue_stress.py`
- `experiments/build_gan2026_v06_profile_guard_selector_replays.py`
- `experiments/build_gan2026_v08_parseable_refinement_replays.py`
- `experiments/build_gan2026_v09_semantic_equiv_unknown_replays.py`
- `experiments/build_gan2026_v09_residual_component_generation_audit.py`
- `experiments/build_gan2026_v09_frozen_gate1_hard_slice_audit.py`
- `experiments/build_gan2026_v09_frozen_gate2_robustness_stress.py` (if present)
- `experiments/build_gan2026_v09_frozen_gate3_source_symmetry_preflight.py`
- `experiments/build_gan2026_v09_frozen_gate3_exact_source_symmetry_preflight.py`
- `experiments/build_gan2026_v09_frozen_gate4_constrained_aggregate_audit.py`
- `experiments/build_gan2026_v09_frozen_gate4_exact_aggregate_audit.py`
- `experiments/build_gan2026_v10_component_repair_probe.py`

**Protocol doc**

- `docs/experiments/gan2026/frozen_test/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_protocol_2026-06-26.md`

**Experiment artifacts** (already partially archived under
`experiments/archive/gan2026_misc_iterations/` and
`experiments/archive/gan2026_validation750_iterations/`; remaining
non-archived `experiments/gan2026_consensus_fresh_*` and frozen gate reports
2026-06-26)

**Cross-references to scrub**

- `docs/research/paper_manuscript_2026-06-26.md` §4.1.2, Table 3, source list
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/agentic/README.md`
- `docs/experiments/FROZEN_EVIDENCE_MANIFEST_2026-06-26.md`
- `docs/experiments/gan2026/agentic/gan2026_agentic_next_phase_brief_2026-06-14.md`
  (selector ladder sections — trim or footnote as superseded)
- `docs/design/gan2026_rule_register.md` (selector policy entries)

Preserve archived copies under `experiments/archive/` for reproducibility unless
a repo-wide archive policy says otherwise.

## Source Artifacts

- `docs/research/closing_stage_research_critique_2026-06-27.md` §2
- `docs/research/gan2026/retrospectives/gan2026_research_closeout_synthesis_2026-06-17.md`
- `docs/experiments/gan2026/frozen_test/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_protocol_2026-06-26.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate4_exact_aggregate_audit_2026-06-26.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate4_constrained_aggregate_audit_2026-06-26.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate1_hard_slice_audit_2026-06-26.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate2_robustness_stress_2026-06-26.md`
- `experiments/archive/gan2026_validation750_iterations/gan2026_consensus_fresh_agreement_selector_v0_9_validation750_no_call_replay_2026-06-15.md`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/agentic/consensus_fresh_agreement_selector.py`
- `docs/research/paper_manuscript_2026-06-26.md` §4.1.2
