# Supervisor Brief Gap Closure Plan (2026-07-01)

Status: **all four phases complete as of 2026-07-01** (A: legibility
crosswalk; B: single-prompt-vs-multi-agent redo, both tasks, revised scope
— see Phase B below; C: Section/Timeline Agent, built and ablated, null
result; D: out of scope, target is the existing IEEE paper, user-owned).
Companion to
`docs/research/supervisor_brief_conformance_audit_2026-07-01.md` (read that
first — this plan only makes sense against its verdicts). Owner: whole-repo
/ closing-campaign workstream.

## Scope and sequencing principle

Order phases by **cost-to-close vs. protective value**, not by the brief's
own ordering. The audit found one cheap, high-value, near-zero-risk phase
(A), one medium phase that is mostly synthesis of numbers already on disk
(B), one genuine engineering decision (C), and one large writing project
(D). Do A and B regardless of what gets decided about C and D — they are
cheap, reversible, and de-risk the supervisor conversation on their own.

**Decisions confirmed 2026-07-01:** Phase C is **approved** — build the
minimal Section/Timeline stage (Option C1). Phase D is **out of scope** —
the actual target deliverable is a 5,000-word, 8-page IEEE paper (not a
full dissertation), which the user is writing directly; the existing
manuscript and IEEE draft already substantially cover it. Phase D is kept
below only as a record of what was considered and ruled out.

## Phase A — Legibility crosswalk (cheap, do first, no code changes)

**Goal:** make the brief's own vocabulary findable in the repo without
renaming working code or risking regressions.

1. Add a **role crosswalk table** to `CONTEXT.md` (or a new
   `docs/design/brief_role_crosswalk.md`, linked from `CONTEXT.md`) mapping
   the brief's four named roles to the actual components:
   - Section/Timeline Agent → *gap, see Phase C*
   - Field Extractor Agents → `exectv2/assembly/producers.py`,
     `exectv2/llm/pipelines/{key_entities_structured,
     key_entities_generation_selection, target_indicators_single_call}/`
     (one lane per entity family: Diagnosis, SeizureFrequency, Prescription,
     Investigations)
   - Verification Agent → `exectv2/llm/pipelines/entity_verifier/*`,
     `diagnosis_verification/{verifier.py,reconciler.py,acceptance_gate.py}`,
     plus the always-on schema/evidence gates (manuscript §2.2)
   - Aggregator Agent → `exectv2/assembly/{pipeline.py,clinical_finding.py}`
     (`ClinicalFinding.confidence`, `.evidence`, `.provenance`)
2. Add one paragraph to the manuscript's Methods section (§2.2 or a new
   §2.2.1) stating explicitly, in the brief's language, that the
   decomposed architecture *is* a field-extractor/verifier/aggregator
   system, and naming the one role not implemented (Section/Timeline) with
   a pointer to Phase C's resolution once decided.
3. Add a short **"Relationship to the original brief"** subsection to the
   dissertation (once Phase D exists) or, in the interim, to
   `PROJECT_STATUS.md`, stating plainly what was kept, what was generalized
   beyond (two tasks instead of one, three architecture families instead of
   two), and why (the reliability thesis's cross-task generalization
   argument).
4. Disambiguate the "multi-agent" term collision: add a one-line note to
   `docs/research/exploratory_research_directions_multiagent_review_2026-07-01.md`'s
   header (it already exists as a research artifact, do not rewrite it)
   clarifying that its "multi-agent" means Claude sub-agents auditing the
   project, distinct from the brief's cooperating-LLM-extraction-roles sense
   used everywhere else. One sentence, no content change.

**Effort:** ~1–2 hours. **Risk:** none — documentation only.

## Phase B — The single-prompt vs. multi-agent matched-budget table (DONE, 2026-07-01, revised scope)

**Original goal (wrong, corrected same day):** this phase was originally
scoped as "assemble a table from numbers that already exist" — cheap
synthesis, no new experimentation. The user challenged that framing
directly and it did not survive scrutiny: the cited LLM-call-count ladders
were a different axis (budget within one architecture) from the brief's
actual question (genuine multi-agent vs. single-prompt), and the one thing
in the codebase actually named "multi-agent" (a 2026-06-12 Gan 2026
experiment) turned out to hard-code every tool call and use four identical
calls with cosmetic role labels as its "multi-agent" condition — not real.

**What actually happened:** a full from-scratch redo, both tasks, real
`dspy.ReAct` tool use and structurally-honest multi-agent specialists. See
`docs/plans/proud-bubbling-ocean.md` for the implementation plan and:
`docs/experiments/gan2026/agentic/gan2026_agentic_redo_results_2026-07-01.md`
(Gan 2026: new architectures win on accuracy, don't clear the strict gate)
and
`docs/experiments/exectv2/seizure_frequency/exectv2_sf_agentic_redo_results_2026-07-01.md`
(ExECTv2 SF: the same pattern does not transfer — single-prompt wins).
Cross-task divergence is itself the honest answer to the brief's key
research question.

1. **Gan 2026 side** (already scored, pure re-citation): pull
   `llm_only_canonical_pipeline` (single LLM call) vs.
   `hybrid_structured_events` (multi-stage) from the manuscript's §4.2
   Tables 1–2, at matched validation/test splits. Report LLM-call count per
   architecture alongside Purist/Pragmatic accuracy.
2. **ExECTv2 side** (mostly re-citation, some derivation — see the
   exploratory-directions plan's own accounting of what's sourced vs. needs
   computing): 1-call → 2-call → 3-call → hybrid v08, full200 and dev140,
   with LLM-call count and F1 per row. Reuse
   `experiments/exectv2_cost_quality_matched_split_table.py` if/when Phase 2
   of the exploratory-directions plan builds it; if that work has not
   landed yet by the time this phase starts, build the query directly
   against `experiments/registry.jsonl` rather than waiting.
3. Write one new doc,
   `docs/research/single_prompt_vs_multiagent_matched_budget_2026-MM-DD.md`,
   with:
   - one table per task: architecture, LLM-call count, primary metric,
     self-consistency/evidence-gate/schema-validation deltas layered on top
     where already measured
   - the headline finding stated in the brief's own words: does multi-agent
     decomposition beat single-prompt extraction at matched budget, and
     where does the marginal call stop paying for itself (the frontier data
     already shows 1→2 calls +0.063–0.083 F1, 2→3 calls +0.007 F1 — state
     this explicitly as the "same budget" answer)
4. Fold this table into the dissertation's Results chapter once Phase D
   starts (it becomes the direct answer to the brief's key research
   question, and should be positioned early/prominently, not buried).

**Effort:** ~0.5–1 day, almost entirely synthesis; zero to a handful of new
LLM calls only if a genuinely missing matched-budget cell is found (e.g., no
existing ExECTv2 single-call-vs-hybrid comparison on the *same* split/model
combination as Gan's).

**Guardrail check:** stays inside "aggregate validation outputs only" —
no row-level holdout inspection required for this table.

## Phase C — Section/Timeline Agent (APPROVED, Option C1)

The brief names this as role (a) and it is the one role genuinely absent.
Two paths, not mutually exclusive with documentation either way:

**Option C1 — Build a minimal real stage and ablate it.** Add a lightweight
pre-extraction pass that segments each letter into clinically meaningful
sections (history, current presentation, investigations, plan — headings are
often already present in the letters) and, where multiple encounter dates
appear, orders them into a simple timeline object passed to the field
extractors as context. Wire it in as a named, ablatable component (the
project's whole methodology is built around exactly this pattern —
`portability` category, on/off ablation, component-ladder registration), so
"does the Section/Timeline Agent help" becomes a real, falsifiable,
publishable result rather than an assertion. This is the more brief-faithful
option and produces genuine new evidence for the dissertation.

**Option C2 — Document, don't build.** Write a predeclared justification
that letters in both corpora are short, single-encounter documents where the
per-fact temporal attributes already extracted (`PointInTime`,
`TimeSince_or_TimeOfEvent`, `FrequencyChange`, `deterministic/rules/
temporal.py`) subsume what a timeline agent would add, and that a dedicated
segmentation stage was evaluated-by-design-reasoning and not pursued because
[cost/expected-value tradeoff]. This is cheaper but weaker: it is an
argument, not evidence, and a supervisor may reasonably ask "did you test
that assumption?"

**Recommendation:** C1. The marginal engineering cost is low (one new
ablatable stage in an architecture that already knows how to ablate things),
it directly answers the brief's own named role instead of arguing around it,
and a null result ("timeline context did not move F1, letters are too short
for it to matter") is itself a publishable, on-thesis finding — the project
already treats null results as first-class (see the wall-transfer and GEPA
plateau work). But this is real new engineering + at least one new
experiment run, not free, so it needs your go-ahead rather than being
assumed.

**Effort if C1:** ~1–2 days build + ablation run + writeup.
**Effort if C2:** ~2–3 hours.

## Phase D — The dissertation itself (OUT OF SCOPE — user-owned)

**Confirmed 2026-07-01:** the target deliverable is a 5,000-word, 8-page
IEEE paper, not a full dissertation. The existing manuscript (11.3k words)
and compiled IEEE draft already substantially satisfy this once Phase A's
brief-relationship framing and Phase B's matched-budget table are folded
in. The user is writing this directly. The chapter-mapping analysis below
is kept only as a record of what was considered before the target was
confirmed — do not act on it.

**Goal (superseded):** convert existing material into a dissertation-shaped document. This
is primarily an assembly and expansion task, not new research — the audit
found the underlying material (manuscript, 38 ADRs, 20 design docs, 15
literature PDFs already collected including two directly on-topic
multi-agent-clinical-extraction papers) is already unusually complete for
this.

Proposed chapter mapping (standard structure; adjust to your institution's
required template once known):

1. **Introduction** — expand manuscript §1; add explicit brief restatement
   and the "relationship to the original brief" note from Phase A.3.
2. **Literature Review** — new chapter, built from the 15 PDFs already in
   `literature/` plus `docs/research/contribution_thesis.md`'s framing of
   prior work (rule-based vs. LLM vs. hybrid clinical NLP, multi-agent
   clinical extraction precedents, epilepsy-specific NLP). Not written yet
   anywhere in the repo — the largest net-new writing block.
3. **Methodology / System Design** — from `docs/design/reliability_thesis.md`,
   `architecture.md`, the Phase A crosswalk, and the ADR trail
   (`docs/decisions/`, 38 entries) as the record of design decisions and
   why. Reframe explicitly around the brief's four roles plus Phase C's
   resolution.
4. **Implementation / Engineering** — repo tour, evidence-gate and
   schema-validation mechanics, self-consistency implementation, the
   registry/reliability-scorecard tooling. This is the brief's "engineering"
   half and currently has the least dedicated prose anywhere (it is
   implicit in the code and ADRs, not narrated).
5. **Evaluation** — lift manuscript §3–4 nearly directly; insert Phase B's
   single-prompt-vs-multi-agent table prominently as the direct answer to
   the brief's key research question; include the field-level F1 and
   robustness results already built.
6. **Discussion** — lift manuscript §5 (D.1–D.5) largely as-is; it already
   includes honest limitations (I1, S1, the wall, calibration).
7. **Conclusion and Future Work** — new, short; should explicitly revisit
   the brief's roles and state what was delivered, generalized, or
   deliberately not pursued (with reasons), matching the audit's own
   framing so the dissertation is self-auditing rather than requiring a
   separate document to be legible against the brief.

**Open input needed from you before this phase can be scoped properly:**
your institution's required dissertation length/format (word count, chapter
requirements, whether an IEEE-paper-style contribution can be an appendix
rather than rewritten). Word count alone changes this phase's effort by
roughly an order of magnitude between "expand the existing 11k-word
manuscript into a 15–20k-word dissertation" and "author a 40k+ word thesis
with a full standalone literature review."

**Effort:** unknown pending the above; provisionally 3–10 days of writing
depending on target length, most of it Literature Review (net-new) and
Implementation (net-new narrative over existing code), least of it
Evaluation/Discussion (near-direct reuse).

## Definition of done — all satisfied as of 2026-07-01

- Phase A: **DONE.** Crosswalk doc exists and is linked from `CONTEXT.md`;
  manuscript has the brief-relationship paragraph; term-collision note
  added.
- Phase B: **DONE, revised scope.** Not a table — a genuine from-scratch
  redo on both tasks with real `dspy.ReAct` tool use and structurally-honest
  multi-agent specialists, since the prior "multi-agent" artifact in this
  codebase was found to be fake. Gan 2026 result:
  `docs/experiments/gan2026/agentic/gan2026_agentic_redo_results_2026-07-01.md`.
  ExECTv2 SF result:
  `docs/experiments/exectv2/seizure_frequency/exectv2_sf_agentic_redo_results_2026-07-01.md`.
  Headline finding: agentic decomposition helps on Gan 2026, does not
  transfer to ExECTv2 SF — task-dependent, not universal.
- Phase C: **DONE.** C1's ablation was run and written up (null result,
  Section/Timeline context did not improve SF or Investigations on dev140).
- Phase D: **out of scope**, confirmed by the user — the real target is the
  existing 5,000-word IEEE paper, which the user is writing directly.

## Explicit non-goals

- No renaming of working code to match the brief's role names (Phase A adds
  a documentation crosswalk, not a refactor — the risk/reward of touching
  the v08 hybrid pipeline's naming is bad given its frozen-evidence status).
- No reopening of frozen holdouts (`test450`, ExECTv2 `test60`/`test59`) to
  produce Phase B or C evidence — both stay inside the aggregate-validation
  guardrails already in force.
- No new architecture families beyond Phase C's single addition — the
  three-family comparison (rules/LLM-only/hybrid) already exceeds the
  brief's two-way ask and should not be expanded further just because it is
  possible to.
