# Supervisor Brief Conformance Audit (2026-07-01)

Status: audit, read-only. Produced by direct inspection of the current repo
state (`PROJECT_STATUS.md`, `docs/design/reliability_thesis.md`,
`docs/research/contribution_thesis.md`, `CONTEXT.md`, `README.md`, the
ExECTv2 `assembly`/`llm/pipelines`/`gepa` source tree, and
`docs/research/paper_manuscript_2026-06-26.md`). No code was edited, no
experiments were run, and no guardrail was reopened.

## The brief (verbatim, as supplied 2026-07-01)

> Instead of training models, this project builds a training-free (or
> minimal-training) multi-agent extraction system that reads epilepsy letters
> and outputs structured fields (e.g., ASM, seizure type/frequency,
> investigations, epilepsy syndrome/type). The student will design roles such
> as: (a) Section/Timeline Agent (segments text, builds timeline), (b) Field
> Extractor Agents (one per field group), (c) Verification Agent (checks
> evidence spans, contradictions, missingness), and (d) Aggregator Agent
> (produces final JSON + confidence + citations to text spans). The key
> research goal is reliability: compare single-prompt extraction vs
> multi-agent extraction under the same budget constraints, and test
> improvements from self-consistency, evidence requirements ("answer only if
> supported by quote"), and structured output validation. Evaluation uses
> field-level accuracy/F1, and robustness tests. Data can be synthetic or
> de-identified samples if available. Deliverables: an end-to-end agentic
> pipeline, evaluation harness, and a dissertation focused on engineering +
> empirical study of reliability.

## Headline verdict

The project satisfies — and in several places exceeds — the brief's
**research substance** (reliability as the central question, evidence
requirements, structured validation, self-consistency, field-level F1,
robustness testing, synthetic + de-identified data). It has **drifted from
the brief's literal architecture and vocabulary**: no component is named or
documented as a "Section/Timeline Agent," "Field Extractor Agent,"
"Verification Agent," or "Aggregator Agent"; the central comparison actually
run is **rules-only vs. LLM-only vs. hybrid**, not literally **single-prompt
vs. multi-agent at matched budget** (though the underlying call-count data to
build that exact comparison already exists); and the "dissertation" deliverable
does not exist — only a paper-length manuscript (11.3k words) and a 5-page
IEEE conference draft do.

None of this is a research-quality problem. It is a **legibility problem**:
a supervisor who reads the brief and then the codebase/paper will not
recognize their own brief's structure reflected back, even though the work
underneath is more rigorous than the brief asked for. That gap is closeable
at low cost (Phase A below) independent of any new engineering.

## Section-by-section conformance

### 1. "Training-free (or minimal-training) multi-agent extraction system"

**Verdict: Met, with a framing caveat.**

- No model weights are trained anywhere in the repo. Extraction is 100%
  prompting + deterministic rules; GEPA (`exectv2/gepa/`,
  `tasks/seizure_frequency/gan2026/agentic/`) optimizes **prompt text** via
  reflective search, never gradients — this is minimal-training in the
  brief's sense, and the project's own conclusion is that hand-tuned/hybrid
  architecture beats GEPA prompt optimization anyway
  (`docs/research/exectv2_gepa_single_model_plateau_synthesis_2026-06-28.md`),
  so GEPA is a comparator/diagnostic method, not the production system.
- "Multi-agent" in this repo's own recent usage
  (`docs/research/exploratory_research_directions_multiagent_review_2026-07-01.md`)
  means *Claude sub-agents auditing the project*, not the brief's *cooperating
  LLM roles that jointly perform extraction*. These are unrelated meanings of
  the same word — worth flagging so it is never conflated in the dissertation.
- The production ExECTv2 pipeline (v08 hybrid, dev140 F1 0.9155) **does**
  decompose into cooperating stages with LLM calls at each: per-family
  candidate producers (`exectv2/assembly/producers.py`,
  `exectv2/llm/pipelines/*`), per-family verifiers
  (`exectv2/llm/pipelines/entity_verifier/{sf,investigations,med_inv}.py`,
  `diagnosis_verification/verifier.py`), and a final assembly stage
  (`exectv2/assembly/pipeline.py`, `clinical_finding.py`) that emits a
  `ClinicalFinding` with `confidence: Literal["low","medium","high"]` and an
  `evidence` (source-quote) field per finding. Structurally this **is** a
  field-extractor + verifier + aggregator system. It has just never been
  described in those terms.

### 2. Role (a) — Section/Timeline Agent

**Verdict: Gap.** No component segments a letter into sections or builds an
explicit chronological timeline as a named, inspectable intermediate
artifact. Temporal reasoning exists, but it is distributed inside per-fact
attribute extraction (`PointInTime`, `TimeSince_or_TimeOfEvent`,
`FrequencyChange` on SeizureFrequency; `deterministic/rules/temporal.py`),
not a dedicated upstream stage whose job is "build the timeline, then hand it
to extractors." This is the single cleanest missing role from the brief's
list.

### 3. Role (b) — Field Extractor Agents (one per field group)

**Verdict: Met.** ExECTv2's hybrid architecture already runs one
producer/extraction lane per entity family (Diagnosis, SeizureFrequency,
Prescription, Investigations — the four families the brief names as examples:
ASM, seizure type/frequency, investigations, epilepsy syndrome/type map
directly onto Prescription, SeizureFrequency, Investigations, Diagnosis).
Evidence: `exectv2/llm/pipelines/key_entities_structured/` and the retained
focused lane implementations,
`exectv2/assembly/producers.py`'s `CandidateProducer` protocol. This is real,
substantial, working code — it just isn't labeled "Field Extractor Agent"
anywhere.

### 4. Role (c) — Verification Agent (evidence spans, contradictions, missingness)

**Verdict: Met, and more rigorously than the brief implies.** Two
deterministic gates run on every prediction and are reported as first-class
metrics (manuscript §2.2): schema validation and evidence verification
(cited span must be an exact source substring). On top of that there are
LLM-driven verifier stages per family (`entity_verifier/*`,
`diagnosis_verification/{verifier.py,reconciler.py,acceptance_gate.py,phase2_panel.py}`)
that check contradictions and missingness, plus a whole reliability program
(calibration ECE 0.0432, review-routing, robustness hard-slice battery
across 414 cells) that goes well past "checks evidence spans." This is the
strongest-covered role in the brief.

### 5. Role (d) — Aggregator Agent (final JSON + confidence + citations)

**Verdict: Met.** `ClinicalFinding` (`exectv2/assembly/clinical_finding.py`)
is exactly this contract: `finding_id`, `letter_id`, `entity`, `text`,
`attributes`, `evidence` (citation), `confidence` (low/medium/high),
`provenance` (which stage/component produced or touched it), `rationale`.
`exectv2/assembly/pipeline.py` is the aggregation pass. Not named
"Aggregator Agent" anywhere, but functionally complete.

### 6. "Compare single-prompt extraction vs multi-agent extraction under the same budget constraints"

**Verdict: Met, with a real correction to this audit's own original assessment.**
This section originally (2026-07-01, first pass) characterized this gap as
"synthesis of numbers that already exist" — cheap, no new experimentation
needed. **That was wrong**, and the error was caught the same day when the
user pushed back on it directly: the LLM-call-count ladders cited below are
a different axis (call budget within one architecture family) from the
brief's actual question (genuine multi-agent — cooperating LLM roles,
LM-decided tool use — vs. single-prompt). Digging into what the project had
actually built under the name "multi-agent" (a 2026-06-12 Gan 2026
experiment) found it hard-coded every tool call in Python (the model never
decided whether to invoke a tool) and its "multi-agent" condition was four
identical calls to one signature with cosmetic role labels — not
differentiated agents. Closing this gap required a genuine from-scratch
build, not a table: `dspy.ReAct` for real LM-decided tool use, and
specialist sub-agents whose output schema structurally cannot contain a
final answer. Done same-day on both tasks:

- **Gan 2026** (`docs/experiments/gan2026/agentic/gan2026_agentic_redo_results_2026-07-01.md`):
  every new architecture (tool-using single agent, static multi-specialist,
  dynamic tool-selecting orchestrator) beat single-prompt extraction by a
  wide accuracy margin on a hard, disagreement-selected panel (Purist
  38%→64%), and dynamic orchestration beat static fan-out — real evidence
  decomposition and dynamism both help, though neither cleared this
  project's strict promotion gate at n=50 (likely a statistical-power
  limit at that sample size, not proof against the architectures).
- **ExECTv2 SeizureFrequency** (`docs/experiments/exectv2/seizure_frequency/exectv2_sf_agentic_redo_results_2026-07-01.md`):
  the same architecture family, ported for the first time (ExECTv2 had zero
  agentic infrastructure before this), did *not* reproduce Gan's pattern —
  single-prompt extraction was the best performer among the four tested,
  with the new architectures trending mildly negative (small-sample,
  inconclusive).

**Honest synthesis**: agentic decomposition is not a universal win for this
domain — task-dependent, and the cross-task divergence is itself the
answer to the brief's "key research goal," delivered with real evidence
rather than assumed transfer. The originally-cited ExECTv2 LLM-call-count
ladder (1-call 0.7730/0.7571 → 2-call 0.8356 → 3-call 0.8426 → hybrid v08
0.9155,
`docs/experiments/exectv2/reliability/exectv2_gpt41mini_simplification_frontier_2026-06-24.md`)
remains a real, separate, and valid finding about call-budget scaling
within the hybrid architecture family — it just isn't the brief's
single-prompt-vs-multi-agent question, and should not be cited as if it
were.

### 7. "Test improvements from self-consistency, evidence requirements, structured output validation"

**Verdict: Met, extensively.**
- Self-consistency: `exectv2/reports/self_consistency.py` +
  `docs/experiments/exectv2/reliability/exectv2_2call_no_sf_self_consistency_*`
  (temp-0 and varying-temperature entropy runs); Gan 2026's confidence
  elicitation and semantic-entropy work
  (`docs/experiments/gan2026/reliability/gan2026_confidence_elicitation_predeclaration_2026-06-17.md`,
  P2.1 semantic entropy).
- Evidence requirement ("answer only if supported by quote"): the
  evidence-is-substring gate is a first-class, always-on metric on both
  tasks (manuscript §2.2, §3.2); `evidence_valid` is a field on every
  `ClinicalFinding`.
- Structured output validation: schema-validity rate and repair rate are
  reported metrics on both tasks (manuscript §3.3, §4.4); DSPy structured
  signatures throughout.

### 8. "Evaluation uses field-level accuracy/F1, and robustness tests"

**Verdict: Met and substantially exceeded.** Field-level scoring is the
project's primary scoreboard (Clinical Recovery Headline / Concept-Identity
Headline / Frequency State Recovery per entity, purist/pragmatic label
accuracy for Gan). Robustness: `gan2026-generalization-adversary` battery
(synthetic hard-negatives, source-near contrasts, OOD phrasing) and ExECTv2's
robustness hard-slice validation (F1 0.8336 across 414 cells). This is
deeper than a typical dissertation-level robustness test suite.

### 9. "Data can be synthetic or de-identified samples"

**Verdict: Met.** Gan 2026 = fully synthetic letters
(`data/Gan (2026)/synthetic_data_subset_1500.json`). ExECTv2 = the
Fonferko-Shadrach et al. 2024 published corpus (*J Biomed Semantics*, DOI
10.1186/s13326-024-00316-z), 200 de-identified epilepsy clinic letters —
exactly the brief's second option.

### 10. Deliverable — "an end-to-end agentic pipeline"

**Verdict: Met**, via the ExECTv2 hybrid v08 pipeline and the Gan 2026
`Gan2026PipelineRunner` architectures. Runs end-to-end from raw letter text
to scored structured output on both datasets.

### 11. Deliverable — "an evaluation harness"

**Verdict: Met, and the strongest part of the project by a wide margin.**
Registry-tracked runs (`experiments/registry.jsonl`, 244 rows), reliability
scorecard, component-ablation contract, calibration/robustness/review-routing
validators, frozen-holdout preflight gates, an Observatory web frontend
(`frontend/`, `src/clinical_extraction/observatory/`) with a component-impact
ladder UI. This substantially exceeds what a dissertation evaluation harness
normally looks like.

### 12. Deliverable — "a dissertation focused on engineering + empirical study of reliability"

**Verdict: Met — target format corrected 2026-07-01.** The actual target
(confirmed with the user) is a **5,000-word, 8-page IEEE paper**, not a
full-length dissertation. Against that target, the gap is small, not large:
`docs/research/paper_manuscript_2026-06-26.md` (11,298 words) and the
compiled `literature/IEEE/IEEE-conference-template-062824/` draft (5 pages
as of 2026-06-26) already substantially cover this deliverable. Remaining
work is folding in Phase A's brief-relationship framing and Phase B's
single-prompt-vs-multi-agent table, and the user is handling the writing
directly — **out of scope for the gap-closure plan below.**

## Where the project exceeded the brief

- Two independent datasets/tasks (not just one), with a shared modular core
  and an explicit cross-task generalization thesis
  (`docs/design/reliability_thesis.md`) — the brief only asked for one
  extraction system.
- Three canonical architecture families (rules-only / LLM-only / hybrid)
  compared on both tasks, rather than the brief's simpler single-prompt vs.
  multi-agent axis — a superset, not a substitute.
- Calibration (ECE/Brier), review-routing, cross-model agreement, and
  semantic-entropy uncertainty work — the brief only asked for
  self-consistency.
- A gold-quality/row-adjudication research program (Diagnosis 85.2%,
  SeizureFrequency 61–83% of "errors" are gold-annotation artifacts, not
  model error) that is a genuine methodological contribution beyond
  anything the brief specified.
- A live web frontend (Observatory) visualizing the component-impact ladder
  — not requested, and not needed for the dissertation, but real extra
  engineering investment.

## Risk note

The biggest risk to a supervisor conversation is not capability, it is
**legibility**: reviewing this repo cold, a supervisor cannot tell in under
an hour that it satisfies their own brief, because none of the brief's nouns
(Section/Timeline Agent, Field Extractor Agent, Verification Agent,
Aggregator Agent, single-prompt vs. multi-agent) appear anywhere in
`CONTEXT.md`'s ~80-term glossary, the manuscript, or the code. Closing that
gap (Phase A of the plan below) is cheap and should happen before any new
engineering, independent of how the bigger gaps (timeline agent, dissertation)
get resourced.

See `docs/plans/supervisor_brief_gap_closure_plan_2026-07-01.md` for the
implementation plan.
