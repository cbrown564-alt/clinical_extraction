# Decomposition Research-Impact Review: What the Thermo-Nuclear Cleanup Opens, Traces, and Hides

Date: 2026-06-27

Status: analysis-only review. Asks one question — *now that the codebase is
navigable, what does that do for the research?* — split into the three sub-questions
posed: does it open new avenues, does it make past avenues easier to trace, and
does it highlight areas of concern. Grounded in verified code facts as of HEAD
`2163cd6` (52-commit remediation cycle `9d6ac46`…`2163cd6`). Proposes no edits to
results, authorizes no holdout or full-200 read, reopens no freeze. Complements
the paper-facing [`closing_stage_research_critique_2026-06-27.md`](closing_stage_research_critique_2026-06-27.md);
where they intersect (cross-task shared-component ablation; the portability map)
this doc supplies the *mechanical* feasibility and one verified caveat that bears
on whether those artifacts are trustworthy.

## Bottom Line

The cleanup's real research dividend is not smaller files — it is that **three
previously-implicit research judgments are now validated, queryable data**: the
component **portability taxonomy** (`component_ablation/definitions.yaml`), the
run **provenance ledger** (`reliability/catalog.yaml`), and the SF **rule catalog**
(`sf_surface_registry/catalog/*.yaml`). That makes the long-standing
"clinical-recovery vs benchmark-format" question (the spine of the closing-stage
critique) a config diff rather than a code fork, and it structurally defuses the
model-mislabeling risk recorded across the project's own notes. The exposure is
in one verified place: **the flagship SF surface registry is catalog-indexed but
legacy-executed** — its "live" builders still delegate to a 925-LOC legacy
implementation — so the declarative surface is, today, partly relocation theater.
And the *research substance itself* — the 21k-LOC `agentic/` reasoner cluster — was
not decomposed at all. The plumbing became navigable; the experiments did not.

The cycle, for scale: **434 files changed, +49,005 / −39,544 lines, line-count
gate green.** The eight worst concentration points were dissolved (e.g.
`llm_only_key_entities_generation_selection.py` 5,285 → 94 LOC facade;
`llm_only_clinical_findings.py` 3,295 → 45; `all_entities.py` 1,455 → per-entity
package; Gan `runner.py` 1,103 → 108). Raw LOC rose, because complexity moved into
package scaffolding, tests, and twelve YAML corpora — redistribution, not deletion.

---

## 1. Does it open new avenues?

### 1a. Clinical-recovery vs benchmark-format F1 is now a config field, not a fork
`reports/component_ablation/definitions.yaml` tags every ladder component with
`component_portability_category` (`general` / `clinical_epilepsy` /
`benchmark_format`) and `prediction_bearing_status` (`yes` / `no` / `conditional`).
This operationalizes the exact distinction the project has flagged repeatedly as
a scoring artifact (`exectv2_scoring_artifacts`, `exectv2_benchmark_vs_clinical_recovery`):
a "portable clinical recovery" score (general + clinical_epilepsy only) can be read
against the full headline by **selecting on a YAML category**, not by maintaining a
parallel pipeline. The two score-bearing layers — `residual_semantic_lens` and
`headline_projection` — are openly tagged `benchmark_format`, which both *enables*
the decomposition and *makes the concern legible*: the gains concentrate in the
format-fitting layers. This is the single highest-value avenue the cleanup unlocks,
and it is the mechanical backing for the critique's §5 "task-neutral-vs-task-specific
component map."

### 1b. Cross-family component-impact comparison is now stateable
Both task families sit on one `StageLadderProvider` seam with per-family adapters
(`project_component_impact_unified_ladder`), and both ladders are data-driven. The
question "does evidence-validation buy the same marginal F1 in epilepsy phenotyping
as the equivalent SF stage" was unstateable when each family hid its ladder in a
2k-LOC module; it is now a two-config read. This is the concrete artifact behind the
§7 *thesis-complete* criterion ("shared core demonstrably reused") that the critique
correctly flags as asserted-not-measured.

### 1c. Strategy × model sweeps became first-class
`llm/pipelines/key_entities_generation_selection/` now exposes per-strategy modules
(`facts`, `pool`, `projection`, `single_call_*`) and per-model prompt builders
(`prompt_builders_qwen_pool`, `prompt_builders_dedup`). The route-level ceiling
finding (`exectv2_qwen_llm_only_dev140`: strict ~0.34, model-independent) can now be
attacked along the *strategy* axis cheaply, rather than only by swapping models —
which is the correct axis, since the ceiling was shown to be route-level.

### 1d. A reusable refactor-equivalence instrument exists
`sf_surface_registry/parity/shadow_diff.py` (legacy-vs-registry diff +
`format_diff_ledger`) is a template for "did this simplification change behavior."
It lowers the cost of aggressive simplification experiments — *if* it is promoted to
a gate (see §3d).

---

## 2. Does it make past avenues easier to trace?

### 2a. Yes — `reliability/catalog.yaml` is now a provenance ledger
Every reliability run carries `candidate`, `model_label`, `role`, `claim_boundary`,
and artifact paths, validated on load via `schema.ReliabilityCatalog`. This
structurally defuses the recorded failure mode in `project_model_stack` — "many
gan2026 numbers were on full gpt-4.1, not mini." Mislabeling a model is now hard
because the model, the role, and the claim boundary are explicit and parsed. The
ledger already lines GPT-4.1-mini / DeepSeek / Qwen runs side-by-side with their
claim boundaries, which is exactly what the critique needs for its DeepSeek-≥-GPT
promotion.

### 2b. The SF rule corpus is enumerable
`sf_surface_registry/catalog/{convention_noise,convention_residual,convention_rewrite,extract,projection_sf}.yaml`
make the rules that were buried across three parallel ~1.5k-LOC stacks readable. The
`claim_boundary` discipline recurs throughout the new YAML, which is the scoping
hygiene that lets a number be traced to what it actually claims.

### 2c. Partly undermined — the analysis code was quarantined, not indexed
`artifact_analysis/` now has **0 production importers** (good hygiene) but holds
**25,801 LOC across 66 files** — including past error-analysis avenues
(`reset_stage_component_ablation_v6.py`, 1,118 LOC). "Trace past avenues" is *weaker*
here: that code is off the import graph, will bit-rot, and has no index. If those
analyses are ever re-run, the quarantine is a memory hole rather than an archive. It
needs a one-page README mapping what each module computed.

---

## 3. Areas of concern

### 3a. (Sharpest, verified) The SF surface registry is catalog-indexed but legacy-executed
The flagship Wave C decomposition ("three parallel SF repair stacks collapsed into
one data-driven registry") is **shape-true but behavior-deferred**. The "live"
registry builders each delegate to the legacy stack:

- `builders/noise_builders.py`, `builders/residual_builders.py`,
  `builders/rewrite_builders.py` — all open with `from . import _legacy_impl as legacy`.
- `_legacy_impl.py` re-exports a **925-LOC `_legacy_residual.py`** via `import *`.

So the catalog YAML selects *which* rules and parameters apply, but the legacy Python
still provides the *mechanics*. Parity holds precisely **because it is the same code
running underneath.** This is an acceptable migration intermediate, but it is a trap
if read as "done": the declarative catalog gives an illusion of an owned rule system
while the rules still live in legacy code. The same "relocation theater" pattern the
audit itself caught in the LLM dispatch applies here. Research consequence: you cannot
yet answer "which rule fired and why" from the catalog, because the catalog does not
own behavior — which directly limits how far §1a/§2b can be trusted as a *rule-level*
research surface.

### 3b. The research substance is still monolithic
The `agentic/` cluster — where the actual Gan2026 reasoning lives — is **21,198 LOC
across 11 files >800 lines** (`fresh_evidence_reasoner.py` 2,081;
`direct_boundary_critic_rescue.py` 1,554; `cross_model_structured_event_adjudicator.py`
1,508; `consensus_fresh_agreement_selector.py` 1,348; …), none migrated onto the new
`agentic/run_driver.py`. The cleanup made dispatch, reports, and deterministic
projection navigable, but the reasoning experiments are untouched. This matters
because the stated research swing — semantic-entropy / reliability
(`gan2026_reliability_refocus`) — runs *through* these reasoners. The leverage areas
remain the hardest to read.

### 3c. Benchmark-format components sit at the top of the ladder, where score is added
Per `definitions.yaml`, `residual_semantic_added` is `prediction_bearing: yes` and
tagged `benchmark_format`; `source_scored` and `evidence_valid` are `inert: true` on
single-lane holistic runs (scoring/evidence add or drop nothing). The honest read:
the interesting component deltas are only dictionary + residual + projection, and the
score gains concentrate in the format-fitting layers. The structure now makes this
measurable (§1a) and undeniable — any external claim must report the clinical-only
number alongside the headline.

### 3d. The parity guarantee is not a CI gate
`shadow_diff` is referenced by three tests (`test_exectv2_sf_surface_registry`,
`test_exectv2_same_core_model_swap`, `test_exectv2_standard_dictionary`) but there is
no `parity`/`shadow` step named in `.github/workflows/ci.yml`. Given §3a — that the
registry's validity claim *rests* on legacy↔registry equivalence — the equivalence
that is load-bearing for the refactor is not a first-class boundary check. If a
catalog edit is made in the belief that the catalog owns behavior, nothing at the CI
boundary proves the two paths still agree.

---

## Recommended Priority Order

1. **Run the portability decomposition (§1a).** Re-score existing dev140 artifacts
   with `benchmark_format` components toggled off using only the YAML category field;
   report clinical-recovery F1 vs headline F1 across the GPT/DeepSeek/Qwen rows
   already in `reliability/catalog.yaml`. Near-zero new code, directly answers the
   recurring "is the score real or constructed" question, and pressure-tests whether
   `definitions.yaml` actually drives scoring.
2. **Audit the SF registry's legacy delegation depth (§3a) before relying on the
   catalog as a rule-level research surface.** Decide per rule-family: promote the
   catalog to own behavior, or label the registry honestly as catalog-indexed /
   legacy-executed in any methods text.
3. **Promote `shadow_diff` to a named CI gate (§3d)** so the equivalence claim is
   enforced, not assumed.
4. **Index `artifact_analysis/` (§2c)** with a one-page map of what each module
   computed, so the quarantine is an archive rather than a memory hole.
5. **Treat `agentic/` decomposition (§3b) as research-enabling, not hygiene** — it is
   the gating factor on instrumenting the reliability/semantic-entropy swing, and it
   is the highest-leverage remaining structural work.

## Guardrail Compliance

Nothing here requires holdout or full-200 row-level inspection or reopens any freeze.
The portability decomposition is a re-read of already-produced aggregate artifacts
via a config field; the registry-delegation and parity-gate items are
engineering/verification over existing code. A full-200 like-for-like read remains
gated under standing policy and is not assumed.

## Source Artifacts (verified for this review)

- `docs/plans/thermo_nuclear_code_quality_audit_plan_2026-06-26.md` (cycle scope)
- Git: `9d6ac46`…`2163cd6` (52 commits; +49,005 / −39,544 over 434 files;
  `scripts/check_line_counts.py` → OK)
- `…/exectv2/reports/component_ablation/definitions.yaml` (portability categories;
  `prediction_bearing_status`; `inert` flags)
- `…/exectv2/reports/reliability/catalog.yaml` (provenance ledger: `model_label`,
  `role`, `claim_boundary`)
- `…/exectv2/deterministic/sf_surface_registry/builders/{noise,residual,rewrite}_builders.py`
  (each `from . import _legacy_impl as legacy`); `…/builders/_legacy_residual.py`
  (925 LOC, re-exported via `_legacy_impl`); `…/parity/shadow_diff.py`
- `…/exectv2/llm/pipelines/key_entities_generation_selection/` (per-strategy +
  per-model modules)
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/agentic/` (21,198 LOC;
  11 files >800); `…/gan2026/artifact_analysis/` (25,801 LOC; 66 files; 0 importers)
- `.github/workflows/ci.yml` (no `parity`/`shadow` step)
- Companion: `docs/research/closing_stage_research_critique_2026-06-27.md`
</content>
</invoke>
