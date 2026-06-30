# Exploratory Research Directions: Multi-Agent Review (2026-07-01)

Status: exploratory, read-only review. Produced by nine sub-agent investigations
(six generative, three adversarial) run against the current repo state, not by
manual analysis. No code was edited, no experiments were run, and no guardrail
was tested or reopened in the course of producing this document; one new data
finding (below) was independently verified against raw files by two of the nine
agents. This document supersedes nothing and is not part of either the
`manuscript_evidence_gaps_closure_plan_2026-07-01.md` or the
`calibration_abstention_review_routing_strengthening_plan_2026-07-01.md` tracks;
it is deliberately downstream of neither — the brief was to set the existing
manuscript and `PROJECT_STATUS.md` priorities aside and ask what *new* research
questions this project's accumulated data, code, and experiment log make
answerable that have not been asked yet.

## Method

Round 1: six agents, each assigned a distinct disciplinary lens with no
knowledge of the others' assignments, were pointed at concrete artifacts
(`experiments/registry.jsonl`, the GEPA package, the reliability/calibration
code, the raw synthetic corpora, the predecessor-lessons packet) and asked to
propose 3-5 new, falsifiable research questions from that lens, ranked, with an
explicit feasibility/novelty argument for each. Lenses: benchmark-validity
meta-science, LLM pipeline architecture science, cross-model uncertainty
science, meta-research on the research process itself, synthetic data as an
object of study, and cost-quality decision theory. This produced 24 candidate
questions.

Round 2: three adversarial agents reviewed the combined list of 24 independently
of each other — a feasibility/rigor skeptic (does this actually work from
artifacts that exist, without violating a standing guardrail), a
novelty/significance judge (would anyone outside this project's authors care),
and a data-integrity auditor tasked specifically with independently
re-verifying one round-1 factual claim (synthetic-corpus patient/metadata reuse)
against the raw letter files rather than taking the originating agent's word for
it. All three were explicitly invited to disagree with the round-1 framing, and
did.

This document is the synthesis of both rounds, written by the orchestrating
session rather than any sub-agent.

## An Actionable Finding, Independent Of Any Research Direction

While verifying a round-1 claim about administrative-metadata reuse in the
ExECTv2 synthetic corpus, the data-integrity auditor ran an md5 hash over all
200 letters in `data/ExECTv2 (2025)/Gold1-200_corrected_spelling/` and found
**4 pairs of byte-identical letters** (8/200 letters, 4%): (EA0021, EA0183),
(EA0149, EA0185), (EA0159, EA0160), (EA0169, EA0181). The `.ann` gold files are
duplicated too (one pair differs by a single trivial offset typo).

Checked against `data/ExECTv2 (2025)/splits/exectv2_split_v1.json` (dev140/
test60, stratified only by `has_seizure_frequency_mention`, not batch- or
identity-aware): three of the four duplicate pairs land entirely within dev
(harmless beyond dev140 having ~138 independent letters rather than 140). The
fourth, **EA0159 (test) / EA0160 (dev), is split across the frozen holdout** —
`diff` shows zero text differences between them; same patient, same date, same
clinical body, same plan. This is literal content leakage across the
train/tune-vs-test boundary, on one of 60 test letters.

Severity assessment (data-integrity auditor, independently corroborated by the
feasibility skeptic's separate read of the split manifest): too small (1.7% of
test) to have driven the direction of any reported finding, and it does not
differentially affect the GEPA-vs-hybrid or model-swap comparisons, which all
evaluate the same contaminated set equally. It is nonetheless a discrete,
measurable, fixable bug, not a research question. **Recommendation:** before
the next claim that ExECTv2 `test60` is "frozen and untouched" is made, dedupe
the corpus by content hash, reassign or drop one of EA0159/EA0160, and check
whether either letter's row was ever cited as a standalone example in any
report.

A related but lower-stakes claim from the same round-1 investigation —
administrative-header reuse (shared NHS numbers / "Our Ref" codes) across
*different* named patients — was confirmed real (three genuine cross-patient
collisions found via full 200-letter scan, not just the two the originating
agent cited; one of the originating agent's two illustrative examples was
itself wrong about which pair crosses the split) but assessed as clinically and
statistically inert: in every case the shared field is header boilerplate and
the clinical body (diagnoses, drug regimens, ages, histories) is independently
written. It does not threaten the dev/test independence assumption any existing
finding relies on, beyond the EA0159/EA0160 case above.

## Where The Three-Round Process Changed The Answer

The brief asked for agents to "argue with each other." Three cases were
materially resolved or reframed by that argument, not just re-ranked:

1. **Synthetic-corpus patient/metadata reuse**, as above: round 1 framed this as
   a possible threat to every cross-split generalization claim in the project;
   round-2 verification found the loud version of the claim was mostly cosmetic
   and based partly on a wrong example, while surfacing a narrower, real,
   previously-unknown bug (the duplicate-letter leak) that round 1 had not been
   looking for at all.
2. **"Reversal taxonomy" — findings in this project are overturned only by more
   scrutiny, never by less** (the meta-research-on-process lens's leading
   question): the novelty/significance judge pointed out this is close to
   tautological — a correction is *labeled* a reversal precisely because later
   scrutiny found an error, so the directional claim carries near-zero
   information by construction. This document accepts that critique and drops
   the question from the priority list.
3. **Survivorship bias via the registry's promote/revise/reject lifecycle**: the
   meta-research lens proposed this as a modest, illustrative curiosity. The
   feasibility skeptic, while fact-checking an unrelated claim, independently
   computed the exact figures from `experiments/registry.jsonl` (9/244 = 3.7%
   `promote`, 146 = 59.8% `revise`, 34 = 13.9% `reject`; `supersedes` populated
   on 127/244 rows vs. `superseded_by` on only 8/244), and the significance
   judge ranked the finding top-4 independently. It moved from "interesting if
   substantiated" to "substantiated and high-value" during the cross-check
   itself, which is the strongest argument in this document for running the
   three-round structure at all rather than taking round 1 at face value.

## Recommended Priority Order

### Tier 1 — high significance, feasible now, not already answered elsewhere

**1. Verify-stage credit assignment in multi-stage GEPA.** The repo already has
a documented negative result: the generate-then-verify multi-stage GEPA program
(`program_multistage.py`) missed its kill-criterion (0.7235 vs. the single-pass
0.731 ceiling) because the verifier stage was scored on the same undecomposed
end-to-end `clinical_headline` F1 as the generator, giving reflection no way to
credit "correctly rejected a bad candidate" separately from "produced a good
final list" — it drifted toward reformatting the whole output rather than
filtering it. This generalizes past this repo: *if a verify/critique stage in a
reflective-prompt-optimization pipeline shares an undecomposed scalar reward
with its upstream generator, optimization will not learn to verify — it will
learn to regenerate.* Falsifiable and cheap to test: rerun with a stage-local
metric (verifier scored on accept/reject precision against a frozen generator's
candidate set, independent of final headline F1) and check whether the evolved
instruction text becomes filter-shaped (explicit keep/reject criteria) and the
kill-criterion delta turns positive. No new infrastructure — a metric edit plus
one GEPA rerun.

**2. Write up the survivorship-bias finding properly.** The core numbers are
already verified (see above). What remains is the part neither round-2 agent
did: cross-reference the run_ids actually cited in
`docs/research/paper_manuscript_2026-06-26.md` back through their
`supersedes` chains in the registry to get a mean chain-length-to-publication,
and state plainly what fraction of registry churn a finished paper's prose
narrative hides. This is a genuine, citable instance of the
preregistration-vs-narrative gap that reproducibility research usually has to
infer indirectly; here it is a literal, structured audit trail. Near-zero
marginal cost — the hard part is done.

**3. Build the matched-split, cross-architecture cost-quality table.** Existing
artifacts already show the marginal return on LLM calls collapsing sharply (1
to 2 calls: +0.063-0.083 F1 for 2x the call budget; 2 to 3 calls: +0.007 F1 for
1.5x the budget) while the deterministic post-processing stack adds +0.062 F1
on the same 2-call base for zero marginal model calls — roughly 9x better
F1-per-cost than the third LLM call. Separately, the often-cited "the hybrid is
worth +0.2 F1" claim is split-dependent by roughly 5x (full200 hybrid premium
+0.0076 vs. dev140 +0.076) purely because no single table puts every
architecture family on the same split. Building that table is synthesis over
numbers that already exist in separate documents; it both answers a real
cost-quality question and resolves an internal inconsistency that should be
fixed before it is cited again.

**4. Mechanical heuristic for predicting gold-inflation vs. genuine error.**
The four completed family adjudications (Diagnosis 93.5% H-inflated, SF 61-83%,
Prescription 52.2% via a *different* mechanism — transcription typos breaking
substring matching, not cardinality — Investigations 26-30%, a clean negative)
are, lined up, an unintended labeled dataset for a cheap triage rule: a
cardinality/dedup-convention split predicts the adjudication outcome
near-perfectly for Investigations but poorly for Prescription, because
Prescription's inflation runs through a confound (orthographic/typo variance)
the cardinality split was never built to see. Adding an orthographic-variance
feature to the existing mechanism label, and checking whether it recovers
Prescription's missed precision without degrading Investigations, is pure
re-analysis of adjudication output that already exists on disk — no new LLM
calls, no new adjudication. Useful immediately as a pre-flight check before
committing adjudication budget to a new entity family.

### Tier 2 — real, but more expensive or narrower in reach

**5. Lexicon-openness as a continuous predictor of gold-inflation share.**
Extends item 4 from a binary split into a continuous predictor, tested
out-of-sample on entities that currently have F1 but no adjudication (Onset,
EpilepsyCause, WhenDiagnosed). The most methodologically disciplined item in
the full candidate set — a genuine preregistered, falsifiable test rather than
a post-hoc story — but the feasibility skeptic is right that this is a full new
adjudication phase (each existing phase was itself a multi-agent, full-dev140
effort), not a quick follow-up to item 4.

**6. Cross-tabulate the ~20 existing component-ladder registry rows by
component type.** The one cross-task component-transfer claim currently in the
manuscript (canonicalization/dictionary components transfer positively across
ExECTv2 and Gan2026; a soft `evidence_validation` gate is inert, Δ=0.0000 on
both) rests on N=2. The registry already contains roughly 20 other
component-ladder comparisons (Gan2026 graph-construction-vs-projection-policy
rungs, clean-policy-vs-repair-stack ladders, gate/filter variants) that have
never been reclassified by component *type* rather than by task. Nearly free —
systematic relabeling of existing Δ values, no new runs — and would turn an N=2
anecdote into an actual structural taxonomy (canonicalization/re-keying
components transfer; gating/filtering components without new credit-assignment
signal do not).

**7. Independent reliability check on the row-adjudication method itself.**
Nearly every gold-inflation finding in this project (items 4-5 above, and the
manuscript's C1 argument) rests on row-level adjudication performed by the
project's own research pipeline. A blind re-adjudication of a sample, scored
for inter-rater kappa against the original verdicts, would be high-value — but
only if the second pass uses a genuinely independent method or population, not
a same-agent-type rerun that would measure self-consistency and call it
validity. Worth doing, but the design has to be specified carefully enough that
it does not silently launder the same circularity it is meant to test.

**8. Cross-model disagreement structure and its overlap with self-consistency
entropy.** Two sub-questions, both answerable from existing dev140 artifacts
with no new calls: whether cross-model disagreement is structured by model
identity (is Qwen 3.6 35B a systematic outlier in split-decision cells,
concentrated in Diagnosis/SF, rather than a symmetric third vote) and whether
cross-model disagreement and within-model temperature-sampling entropy are
redundant or complementary signals on the one slice (GPT-4.1-mini dev140) where
both exist on the same letters. Moderate priority — real, cheap, but narrower
in who outside the project would care.

### Dropped or reframed, with reasons

- **Whether the Gan2026 dataset designers' own "Representative Boundary
  Examples.xlsx" cases were independently rediscovered by this project's SF
  error analysis** — a flat category error as originally framed. The
  boundary-examples file's `source_row_index` values live in the Gan2026
  corpus; the SF Phase 6/7 row-adjudication that was supposed to be
  cross-checked against it operates on the unrelated ExECTv2 dev140 corpus.
  There is no shared ID space. Rejected as stated; not reframed, since no
  equivalent boundary-examples artifact is known to exist for ExECTv2.
- **Whether "review nearly everything" (the current 97%-burden review-routing
  policy) is closer to economically rational than it looks** — not answerable
  empirically from repo artifacts, since no real clinician-review-time or
  clinical-harm-cost telemetry exists anywhere in the codebase; the breakeven
  analysis required would rest entirely on analyst-supplied cost assumptions.
  Could be reframed as an explicit sensitivity-analysis exercise (show how the
  breakeven threshold moves across a range of plausible cost ratios) but should
  not be reported as a finding.
- **"Reversal taxonomy"** — see "Where The Three-Round Process Changed The
  Answer," item 2, above. Dropped as near-tautological.
- **Registry `decision`-field schema drift (15 ad hoc values over 244 rows,
  127-vs-8 `supersedes`/`superseded_by` asymmetry)** — confirmed exactly true
  by direct inspection, and genuinely the same "same word, different meaning"
  failure mode the project's own predecessor-lessons packet warns about
  recurring across repos, now recurring within this one. Real, but the
  significance judge's assessment stands: this is internal hygiene, not a
  result an outside reader would weigh. Worth a one-line fix (freeze the
  `decision` vocabulary going forward) rather than a research write-up.
- **Gan2026 gold labels being themselves LLM-generated and self-validated, with
  zero `row_ok` failures on the curator's own hardest category ("unknown")** —
  real (confirmed: 65/1500 rows, 4.33%, fail `row_ok`, no chain-of-thought
  field is persisted to test the proposed correlation with labeler hedging),
  but the significance judge's pushback holds: "unknown" passing cleanly is not
  very surprising given it is exactly the category the dataset designers
  already flagged as boundary-prone. Downgraded to a one-line caveat rather
  than a priority item.

## Full Candidate List (for reference)

The complete set of 24 round-1 candidates, grouped by originating lens, is
preserved here so nothing generated in round 1 is lost even where round 2
deprioritized it:

- **Benchmark-validity meta-science:** mechanical heuristic for gold-inflation
  prediction (Tier 1, item 4); row-adjudication method reliability (Tier 2,
  item 7); lexicon-openness as continuous predictor (Tier 2, item 5); registry
  decision-deltas vs. measured reproducibility noise floor (dropped — bigger
  than advertised; no uniform SE/CI fields exist to query).
- **LLM pipeline architecture science:** verify-stage credit assignment (Tier
  1, item 1); prospective zero-LLM error-type fingerprint for GEPA-vs-stage
  payoff (depends on item 5, sequenced after it); component-ladder
  cross-tabulation by type (Tier 2, item 6); whether GEPA's reflection
  rediscovers, extends, or omits the ~25 hand-written rules it replaced
  (interesting qualitative aside, not prioritized — no round-2 agent
  contested or championed it strongly).
- **Cross-model uncertainty science:** cross-model agreement vs. the official
  calibration rule, head-to-head in one harness (real but flagged by the
  feasibility skeptic as dependent on row-level feature logging that may not
  be uniform across protocols — verify before committing); model-identity
  structure in disagreement and overlap with self-consistency entropy (Tier 2,
  item 8); naive 3-model ensembling vs. the hybrid architecture's 0.9155
  (plausible follow-on to item 8, not separately prioritized).
- **Meta-research on the research process:** reversal taxonomy (dropped);
  survivorship bias (Tier 1, item 2); whether "absorbed" predecessor-lessons
  status is self-graded or independently verified (real circularity point, but
  requires qualitative coding with no clean rubric — lower priority);
  within-project registry schema drift (dropped to a one-line fix); whether
  "no-call replay" rows predict higher revision rates than live-call rows
  (secretly depends on resolving the schema-drift classification first).
- **Synthetic data as object of study:** patient/metadata reuse and the
  duplicate-letter leak (resolved above — one real bug, rest cosmetic);
  Gan2026 gold-label self-validation blind spot (downgraded to a caveat);
  Representative Boundary Examples cross-check (rejected — category error);
  whether ExECTv2's documented phrase-fragmentation annotation rule varies in
  application rate by letter-template family (a real, cheap refinement of the
  existing Diagnosis gold-multiplicity finding; not separately prioritized
  above but worth folding into any future write-up of that finding); templated
  injected noise weakening real-world-transfer claims (confirmed true, cheap,
  but better stated as a limitations-section caveat than a research question).
- **Cost-quality decision theory:** marginal F1-per-call and split-dependent
  architecture premium (Tier 1, item 3); review-routing economic rationality
  (dropped — not empirically answerable from existing telemetry); local vs.
  cloud model deployment breakeven (partially answerable — same-core quality
  and local latency are both logged, but no cloud $/latency telemetry exists
  anywhere in the repo to compare against, so this stays an open instrumentation
  gap rather than a present-day finding).

## Agents Consulted

Round 1 (generative, parallel, independent): benchmark-validity meta-science;
LLM pipeline architecture science; cross-model uncertainty science;
meta-research on the research process; synthetic data as object of study;
cost-quality decision theory.

Round 2 (adversarial, parallel, independent, given the full round-1 output):
feasibility and rigor skeptic; novelty and contribution-significance judge;
data-integrity auditor (independent re-verification of the synthetic-corpus
metadata-reuse claim against raw files, which surfaced the EA0159/EA0160
finding above).

## Source Artifacts (verified for this review)

- `experiments/registry.jsonl` (244 rows; `decision`, `supersedes`,
  `superseded_by`, `mode` distributions directly inspected)
- `data/ExECTv2 (2025)/Gold1-200_corrected_spelling/` (full 200-letter raw text
  and `.ann` gold; md5-hashed and diffed directly)
- `data/ExECTv2 (2025)/splits/exectv2_split_v1.json`
- `data/Gan (2026)/synthetic_data_subset_1500.json`,
  `data/Gan (2026)/Representative Boundary Examples.xlsx`
- `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/gepa/`
  (`program_multistage.py`, `metric.py`, `program.py`, `run_gepa.py`)
- `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/reports/reliability/`
  (`constants.py`, `calibration.py`, `review_routing.py`)
- `docs/research/exectv2_gepa_vs_hybrid_evidence_decomposition_2026-06-28.md`,
  `docs/research/exectv2_gepa_single_model_plateau_synthesis_2026-06-28.md`
- `docs/experiments/exectv2/diagnosis/exectv2_dx_canonical_row_analysis_2026-06-30.md`,
  `docs/experiments/exectv2/seizure_frequency/exectv2_sf_canonical_metric_row_analysis_2026-06-29.md`,
  `docs/experiments/exectv2/exectv2_rx_inv_ev_recall_consolidation_check_2026-06-30.md`
- `docs/experiments/reliability/cross_task_shared_component_ablation_2026-06-27.md`
- `docs/experiments/exectv2/reliability/exectv2_sf_wall_transfer_probe_2026-06-27.md`
- `docs/research/predecessor_lessons/01_failure_modes_and_guardrails.md`,
  `02_reusable_best_practices.md`, `03_promising_unfinished_avenues.md`
- `docs/research/exectv2_annotation_guidelines_v9_extracted.md`
- `experiments/exectv2_gpt41mini_simplification_frontier_2026-06-24.md` /
  underlying `experiments/exectv2_component_off_replay_full200_20260626.md`
- `PROJECT_STATUS.md` (guardrail text: full-200/holdout row-level inspection
  remains blocked for model-output development; this review's corpus-content
  inspection of raw letter text for the integrity check above was read-only and
  did not inspect model predictions or holdout scoring)
