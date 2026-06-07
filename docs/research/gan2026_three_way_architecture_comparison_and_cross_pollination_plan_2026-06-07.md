# Gan 2026 Three-Way Architecture Comparison And Cross-Pollination Plan

Date: 2026-06-07

Author: Claude

Status: planning document — defines the workstream; execution requires the
phased authorization gates named below. No benchmark-comparable claim or
holdout-facing protocol is authorized by this document.

Working agreement: as we work through each phase of this plan, run a
`/grill-with-docs` session before locking in terminology or architectural
decisions (e.g. the Section 2 canonical-runner choice, the Section 4/5
cross-pollination mechanisms, the Section 8 open questions). Use it to
stress-test naming and decisions against this project's existing `CONTEXT.md`
/ ADRs, and to capture newly-resolved terms or hard-to-reverse calls inline as
they crystallise rather than after the fact.

---

## 1. Objective

Run a disciplined side-by-side comparison of the three architecture families
this project has built toward:

1. **Fully deterministic** — `Gan2026PipelineV1` (`pipeline_v1.py`): rule-based
   extraction, normalization, selection, render/score. Known to show signs of
   overfitting to validation phrasing.
2. **Fully LLM** — currently fragmented across ~11 standalone
   `llm_only_*.py` experiments with no unified end-to-end runner and no
   downstream projection/render/verify chain.
3. **Hybrid (reset-native)** — `reset_clinical_assessment_pipeline.py`: the
   current focus, combining deterministic Extract/Normalize/Project/Render
   with an LLM-owned Select/ClinicalAssessment stage, organized around the
   staged contract `Extract -> Select/ClinicalAssessment -> Normalize ->
   Project -> Verify -> Render/Score`.

The comparison is not an end in itself. Its purpose is to **feed back into
both of the other two architectures**:

- use what the hybrid reset discipline has taught us about *generalizable
  versus validation-tuned* rules to refine the deterministic pipeline so it
  stops overfitting;
- use the same discipline — explicit, named, stage-owned, ablatable
  components — to decide which clinical-reasoning aspects the LLM-only
  pipeline's prompts should own outright (broad exploration, clinical
  judgment, contradiction resolution) versus which aspects should be peeled
  off into deterministic normalization/projection so the LLM is not asked to
  also be a parser.

---

## 2. Prerequisite: One Canonical Runner Per Architecture

**Status update (post Phase F consolidation, 2026-06-07): substantially
resolved.** The repo-consolidation plan's Phase F replaced the "assemble a
fully-LLM runner" open question with a unified, parameterized
`Gan2026PipelineRunner` (`src/.../gan2026/runner.py`) that already executes
four named `PipelineArchitecture` configurations — `deterministic`, `hybrid`,
`llm_only_direct_labeler`, and `llm_only_structured_events` — through one
shared projection/render/score/route/decision artifact contract. The
`llm_only_structured_events` configuration *is* the assembled Option-A chain
described below: it already wires an LLM-forward Select/ClinicalAssessment
stage through the same deterministic Normalize→Project→Render→Score→Route→
Decision stages the hybrid configuration uses. No separate assembly step
remains for that comparator.

| Architecture | Canonical runner | Status |
| --- | --- | --- |
| Deterministic | `Gan2026PipelineRunner` `"deterministic"` config (wraps `Gan2026PipelineV1` internals) **and**, as of 2026-06-07, the staged `"deterministic_canonical_pipeline"` config | both exist; the canonical config is now staged into named, ablatable Extract/Normalize/[[Select & Render]]/[[Evidence Trace Check]] form (`deterministic_canonical_stages.py`), proven byte-identical to `"deterministic"` by `tests/test_gan2026_deterministic_canonical_pipeline.py` — see resolution note below |
| Hybrid | `Gan2026PipelineRunner` `"hybrid"` config / `hybrid/reset_clinical_assessment_pipeline.py` | exists, already the named "current focus" |
| Fully LLM | `Gan2026PipelineRunner` `"llm_only_direct_labeler"` and `"llm_only_structured_events"` configs | exist and assembled (Option A is done); see `llm_only_canonical_pipeline` below for the still-open "purest form" comparator |

**Remaining Phase 0 work** is narrower than originally scoped: add two new
`PipelineArchitecture` configurations to the *existing* unified runner — not
standalone forked modules (see `CONTEXT.md` for the resolved naming):

- **`deterministic_canonical_pipeline`** *(done — 2026-06-07)*: the existing
  deterministic logic restructured into four named, stage-owned, ablatable
  stages — Extract, Normalize, [[Select & Render]] (this architecture's named
  selection-and-rendering stage; see `CONTEXT.md` for why it is one combined
  stage here rather than mirroring the hybrid pipeline's separate
  Project/Render seam), and [[Evidence Trace Check]] (this architecture's
  verify-adjacent stage, deliberately *not* named `Verify` — see
  `docs/decisions/0014-evidence-trace-check-not-verify-for-deterministic-canonical-pipeline.md`
  for why it does not reuse `VerificationDecision`/`Verifier Action`
  vocabulary) — implemented in `deterministic_canonical_stages.py` as thin
  named wrappers over the existing internals, with its current rules left
  unchanged — a pure staging pass, so Section 4's family-by-family
  de-overfitting rewrite has a legible, measurable starting point. Proven
  byte-identical to `"deterministic"` (`output` and `diagnostics`, including
  diagnostics-key shape) by
  `tests/test_gan2026_deterministic_canonical_pipeline.py` on a small
  known-row sample — the directly assertable "rules unchanged" guard. See
  `docs/decisions/0013-stage-deterministic-canonical-config-before-generalizing-its-rules.md`
  for why staging and generalizing are deliberately kept as two passes.
- **`llm_only_canonical_pipeline`**: a new single-shot configuration that
  collapses extract→select→normalize→project→render into one LLM call, with
  the now-mature deterministic rule taxonomy (cluster-axis ambiguity,
  seizure-free conflict, same-window additive frequency, and similar named
  families) embedded as prompt instructions rather than pre/post processing —
  the "purest form" fully-LLM comparator, sitting alongside (not replacing)
  the existing `llm_only_direct_labeler`/`llm_only_structured_events`
  configurations. It reports a distinct evidence text-containment metric
  rather than the formal `CandidateSet` source-id validity rate, since forcing
  single-shot LLM output through that machinery would misrepresent what the
  architecture actually produces.

The historical "Option A vs Option B" framing below is now superseded by this
resolution — Option A is built (`llm_only_structured_events`), and
`llm_only_canonical_pipeline` is the new, more precisely-scoped "purest form"
target that replaces the open-ended Option B framing:

- **Option A — minimal-difference comparator** *(done — `llm_only_structured_events`)*:
  reuse the reset pipeline's deterministic Normalize/Project/Render/Score/
  Route/Decision stages verbatim, swapping only the Select/ClinicalAssessment
  stage for a more LLM-forward module. This isolates "how much does moving
  more responsibility onto the LLM change the result" — the cleanest
  apples-to-apples read.
- **Option B — maximal-LLM comparator** *(superseded by `llm_only_canonical_pipeline`)*:
  rather than the original "claim table / direct label chained to a render/score
  boundary" framing, the resolved target is a true single-shot, rules-in-prompt
  pipeline that owns normalize/project itself — the most honest "fully LLM"
  test, wrapped in a thin artifact-shape adapter so the existing comparison
  tooling still runs.

---

## 3. Comparison Protocol

Run all three canonical runners over the **same validation750 surface** (and
only later, as a frozen aggregate audit, over `test450` — see Section 6),
using the existing artifact and scoring tooling so the comparison is
apples-to-apples:

- rendered / null / routed counts
- Purist-correct / Pragmatic-correct on rendered rows
- routed-row taxonomy (which families route, and why)
- evidence-trace and source-id validity rates (this doubles as input to
  [[gan2026_evidence_grounded_thesis_assessment_plan]])
- validation-to-test gap, once a frozen `test450` audit is authorized

Report format: reuse `reports/base.py` and the existing
`reset_stage_component_ablation_v6`-style comparison shape rather than
inventing a new one — this is itself a small DRY exercise that previews
[[gan2026_repo_consolidation_and_cleanup_plan]] Phase F.

---

## 4. Cross-Pollination A: De-Overfitting The Deterministic Pipeline

**Problem**: the deterministic pipeline's rules were largely written and tuned
against validation phrasing. Some are likely genuinely general; others are
likely literal-phrase or threshold matches that happen to fire on validation
rows and will not generalize.

**Mechanism**:

1. Walk the deterministic rule inventory (`deterministic/rule_metadata.py`,
   `deterministic/rules/`, `deterministic_rate_extraction.py`) and classify
   each rule family as: *clinically general principle*, *format/representation
   rule*, or *validation-phrase-shaped pattern match*.
2. Cross-reference each family against the now-mature hybrid
   Normalize/Project family taxonomy (the same families named in
   `gan2026_test450_null_reduction_synthesis_and_hypotheses_2026-06-07.md`
   Section 3 and the reset-stage component inventory). Where a hybrid family
   already expresses the same clinical intent in a more general,
   source-backed, ablatable form, treat that as the **rewrite target** for the
   deterministic counterpart.
3. Rewrite validation-phrase-shaped rules into the same general form: anchor
   to source-backed structure (operands, anchors, windows) rather than literal
   phrase lists, and add the same trace/ownership fields the reset pipeline
   already requires.
4. Re-run the deterministic comparator after each rewritten family and check:
   does the validation score move in a *plausible, explicable* direction (not
   just "up")? Is there any sign the rewrite reduces phrase-overfitting
   without losing genuinely-general coverage?

**Guardrail**: this is explicitly *not* "make the deterministic pipeline score
like the hybrid one." It is "make the deterministic pipeline's rules
expressible as general, source-backed, ablatable principles" — the same
standard already applied to every new hybrid Normalize/Project family. If a
rule cannot be rewritten that way, that is itself a useful finding: it means
the rule was never a generalizable clinical principle, and its retirement (not
its preservation) is the correct action.

---

## 5. Cross-Pollination B: Refining The Fully-LLM Prompts

**Problem**: the `llm_only_*` prompts currently ask the model to do
everything — extraction, normalization, projection, and clinical judgment —
in one pass. The hybrid reset architecture's central lesson (made explicit by
the HN1-HN5 null-reduction synthesis) is that **representation loss is mostly
a normalization/projection problem, not a clinical-judgment problem**. The
model is already choosing the right fact in most null rows; it is the
downstream representation that fails to carry it through.

**Mechanism**:

1. Catalog the Normalize/Project families now under explicit stage ownership
   in the reset pipeline (frequency value recovery, multi-month bucket
   aggregation, seizure-free anchor/duration instrumentation, cluster operand
   completion, vague-with-window rendering, denominator-window resolution,
   etc. — see the reset-stage component inventory). This catalog becomes a
   **checklist of things the fully-LLM prompt should be relieved of**: if a
   deterministic stage already owns turning a selected fact into a renderable
   value, the LLM prompt does not need to also reason about count/range/period
   formatting, anchor arithmetic, or denominator windows.
2. Catalog, in parallel, the things the reset pipeline still routes to a
   human/LLM-facing decision because no deterministic rule safely resolves
   them: competing-burden ambiguity, current-vs-historical distinction,
   clinical plausibility judgments, contradiction detection. This becomes a
   checklist of **things the fully-LLM prompt should be asked to focus on**.
3. Rewrite the canonical fully-LLM prompt (from Section 2's chosen runner)
   around this division: "select and judge the dominant current clinical
   fact; do not worry about exact value formatting — describe what you found
   in the source's own terms and let normalization carry it."
4. State the **portable principle** explicitly, in writing, as a standalone
   short note this plan can point to: *the LLM should reason about clinical
   truth (which fact is true, how confidently, how it relates to competing
   claims); deterministic stages should own representation, arithmetic, and
   format*. This is the same separation of concerns already proven out by the
   hybrid reset pipeline's stage contract — it is not a new idea, just an
   explicit statement of why it generalizes.
5. Stress-test the rewritten prompt the same way the hybrid pipeline's
   components are stress-tested: validation-only proxy slices first, no
   holdout-facing claims until promotion criteria are met (reuse Section 7.4
   of the null-reduction synthesis as the promotion rubric, generalized to
   "prompt change" rather than "Normalize component").

---

## 6. Phasing And Authorization Gates

| Phase | Work | Gate |
| --- | --- | --- |
| 0 | Select/assemble one canonical runner per architecture (Section 2); confirm artifact-shape compatibility with existing scoring tooling | none — mechanical/structural work |
| 1 | Run all three canonical runners on validation750; produce one comparison report using shared reporting machinery | none — validation-only |
| 2 | Apply the de-overfitting rewrite to one deterministic rule family at a time; re-run and compare after each | none — validation-only, ablatable, one family at a time |
| 3 | Apply the prompt-refinement principle to the canonical fully-LLM runner; re-run and compare after each change | none — validation-only |
| 4 | Frozen `test450` aggregate audit of the refined deterministic, refined fully-LLM, and current hybrid pipelines, using the exact frozen-aggregate-audit protocol already proven in `gan2026_test450_hn1_frozen_aggregate_audit_2026-06-07.md` | **requires explicit user authorization**, exactly as already required for any holdout-facing reset work |

Phases 0-3 are validation-only development mechanics and need no new
authorization beyond what the project's existing guardrails already grant.
Phase 4 is the only phase that touches the locked `test450` split, and must
follow the same frozen-aggregate, no-row-tuning discipline already
established and proven.

---

## 7. Guardrails (inherited, not new)

- No row-level holdout tuning; `test450` is touched only as a frozen aggregate
  audit, and only with explicit authorization (Section 6, Phase 4).
- No hidden repair, no holdout-tuned fallback, no verifier-written labels for
  null rows.
- Every ported or rewritten rule must be named, stage-owned, source-backed,
  trace-visible, and ablatable — the same bar already applied to every HN1-HN5
  component.
- Treat "the deterministic pipeline scores lower after de-overfitting" as a
  *possible correct outcome*, not a failure: the goal is generalizability, not
  validation score maximization. Report both validation and (eventually,
  frozen-aggregate) holdout reads so the trade is visible.

---

## 8. Open Questions

1. Should the fully-LLM canonical runner ultimately retain *any* deterministic
   scaffolding, or should a second "maximal-LLM" comparator (Option B in
   Section 2) be required before the thesis comparison in
   [[gan2026_evidence_grounded_thesis_assessment_plan]] is considered complete?
2. If the de-overfitted deterministic pipeline converges toward the same
   general principles the hybrid pipeline already encodes, does it remain
   worth maintaining as a separate architecture, or does it become a
   documented historical baseline (a question for
   [[gan2026_repo_consolidation_and_cleanup_plan]])?
3. How much of the "things the LLM should not need to reason about" checklist
   from Section 5 can be expressed as a single portable prompt-design
   appendix versus needing per-task customization for future benchmark
   families beyond Gan 2026?

---

## 9. Relationship To The Other Two Workstreams

- This plan **produces** the comparison surface that
  [[gan2026_evidence_grounded_thesis_assessment_plan]] needs to score the
  three architectures against the project's core thesis axes.
- This plan's Phase 0 (canonical-runner selection) **is** the architectural
  decision that [[gan2026_repo_consolidation_and_cleanup_plan]] needs before it
  can name removal candidates. Do Phase 0 once, and let both other plans
  consume its output — see the sequencing recommendation in the cleanup plan,
  Section 2.
