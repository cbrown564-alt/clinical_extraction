# Supervisor Brief Role Crosswalk

Status: durable reference doc. Produced by
`docs/research/supervisor_brief_conformance_audit_2026-07-01.md`
(Phase A of `docs/plans/supervisor_brief_gap_closure_plan_2026-07-01.md`).
Maps the original supervisor brief's four named extraction roles onto the
components that actually implement them, so the brief's own vocabulary is
findable in this repo. No code was renamed to produce this table — it is a
documentation layer over the existing architecture described in
`docs/design/reliability_thesis.md` and `docs/design/architecture.md`.

| Brief role | Status | Implementing component(s) |
| --- | --- | --- |
| (a) Section/Timeline Agent — segments text, builds timeline | Built and ablation-tested 2026-07-01 (Phase C) — **null result** | `exectv2/deterministic/section_timeline.py` (segmentation + chronological-reference extraction, zero LLM cost) threaded as optional context into the SeizureFrequency and Investigations LLM prompts. dev140 ablation found no improvement (SeizureFrequency -0.0106, Investigations -0.0034, both within/near this project's measurement noise floor) — see `docs/experiments/exectv2/reliability/exectv2_section_timeline_ablation_2026-07-01.md`. The module remains in the codebase (tested, available) but is not wired into the production v08 pipeline; temporal reasoning continues to be handled by per-fact attribute extraction (`PointInTime`, `TimeSince_or_TimeOfEvent`, `FrequencyChange`). |
| (b) Field Extractor Agents — one per field group | Implemented | One producer/extraction lane per ExECTv2 entity family (Diagnosis, SeizureFrequency, Prescription, Investigations — the brief's own examples of epilepsy syndrome/type, seizure type/frequency, ASM, and investigations map directly onto these four). `exectv2/assembly/producers.py` (`CandidateProducer` protocol) and the retained focused lane implementations own these roles. |
| (c) Verification Agent — evidence spans, contradictions, missingness | Implemented in the retained system | Schema validation and exact-source evidence checks remain active on every retained prediction. The v08 replay also preserves per-finding evidence, provenance, and the outputs of its selected focused lanes. Closed per-family LLM verifier runtimes are historical experiments rather than active product components. |
| (d) Aggregator Agent — final JSON + confidence + citations | Implemented | `exectv2/assembly/{pipeline.py,clinical_finding.py}`. `ClinicalFinding` carries `confidence: Literal["low","medium","high"]`, `evidence` (the citation/quote span), `provenance` (which stage produced/touched the finding), and `rationale`. |
| Key research goal — single-prompt vs. multi-agent extraction, same budget | Answered with real evidence 2026-07-01, both tasks — **task-dependent, not a universal answer** | A genuine, from-scratch redo (the prior 2026-06-12 Gan2026 attempt was found to hard-code tool calls and use a fake "multi-agent" condition — four identical calls with cosmetic role labels). Rebuilt with real `dspy.ReAct` tool use and specialists whose output schema structurally cannot contain a final answer. **Gan 2026** (`docs/experiments/gan2026/agentic/gan2026_agentic_redo_results_2026-07-01.md`): every new architecture beat single-prompt by a wide accuracy margin on a hard panel (38%→64% Purist), dynamic orchestration beat static fan-out — though neither cleared the strict promotion gate at n=50. **ExECTv2 SeizureFrequency** (`docs/experiments/exectv2/seizure_frequency/exectv2_sf_agentic_redo_results_2026-07-01.md`): the same pattern did *not* repeat — single-prompt was the best performer among the four tested, with the new architectures trending mildly negative (small-sample, inconclusive, not a confident reversal). Taken together: agentic decomposition is not a universal win for this domain — it is at best task-dependent, and single-mention classification (Gan) transferred worse to multi-mention, richly-attributed extraction (ExECTv2 SF) than assumed. |
| Self-consistency / evidence requirements / structured output validation | Implemented | Self-consistency: `exectv2/reports/self_consistency.py`, `docs/experiments/exectv2/reliability/exectv2_2call_no_sf_self_consistency_*`, Gan 2026 confidence elicitation + semantic entropy. Evidence requirement: evidence-is-substring gate, always on. Structured validation: schema-validity rate + repair rate, reported metrics on both tasks. |
| Field-level accuracy/F1 + robustness tests | Implemented, exceeds brief | Clinical Recovery Headline / Concept-Identity Headline / Frequency State Recovery per entity; purist/pragmatic accuracy for Gan; `gan2026-generalization-adversary` robustness battery; ExECTv2 robustness hard-slice validation (F1 0.8336 across 414 cells). |
| Training-free / minimal-training | Implemented | No model weights are trained anywhere in the repo. GEPA (`exectv2/gepa/`, `tasks/seizure_frequency/gan2026/agentic/`) optimizes prompt text via reflective search, not gradients, and the project's own finding is that the hand-tuned/hybrid architecture beats GEPA anyway — GEPA is a comparator, not the production system. |
| Data — synthetic or de-identified | Implemented | Gan 2026 = fully synthetic (`data/Gan (2026)/synthetic_data_subset_1500.json`). ExECTv2 = the Fonferko-Shadrach et al. 2024 published de-identified corpus (*J Biomed Semantics*, DOI 10.1186/s13326-024-00316-z). |

## A note on "multi-agent"

This repo currently uses "multi-agent" in two unrelated senses. Do not
conflate them:

1. **The brief's sense** — cooperating LLM roles that jointly perform
   clinical extraction (this table). This is what the dissertation/paper
   should mean by the term.
2. **A separate, newer sense** used in
   `docs/research/exploratory_research_directions_multiagent_review_2026-07-01.md`
   — Claude Code sub-agents used as a *research methodology* to audit this
   project's own artifacts (registry, code, corpora) for new research
   questions. That document's findings are about the project's process, not
   about the extraction architecture, and are unrelated to the brief.

## Relationship to the original brief

The brief specified one extraction system with four named LLM roles on one
dataset. This project generalized the brief's own reliability question —
does a decomposed architecture beat a single prompt, and can evidence
requirements, structured validation, and self-consistency improve it — into
a **cross-task, cross-architecture-family study**: the same modular core
applied to two independent tasks (Gan 2026 seizure-frequency, ExECTv2 broad
phenotyping), compared across three architecture families (rules-only,
LLM-only, hybrid) rather than the brief's simpler single-prompt-vs-
multi-agent axis. The three-family comparison is a superset of the brief's
ask, not a substitute for it — Phase B of the gap-closure plan pulls the
brief's specific single-prompt-vs-multi-agent-at-matched-budget comparison
back out as its own named result inside that larger study, on both tasks.
