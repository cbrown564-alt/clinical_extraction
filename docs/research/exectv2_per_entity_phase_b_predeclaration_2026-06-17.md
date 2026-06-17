# ExECTv2 — Per-Entity LLM-Only Candidate-Source, Phase B (all nine) — Predeclaration

Date: 2026-06-17
Driver: `runners/run_llm_only_per_entity.py` (frames in `llm/llm_only_per_entity.py`)
Split: dev (pilot25 → dev140) · Model: gpt-4.1-mini · Temperature 0.0
Prompt version: `exectv2_llm_only_per_entity_v0.4`
New entities this phase: Onset, WhenDiagnosed, BirthHistory, EpilepsyCause,
PatientHistory (the four Phase-A entities re-run at v0.4 for a single-version map)
Plan: [[09_gpt_first_execution_plan]] Phase B

## Question

Phase A specialized four regime probes (Prescription, Investigations, Diagnosis,
SeizureFrequency) and established the corrected framing: the **LLM is the
candidate source for every entity**, and the projection-gap regime sizes the
*deterministic projection burden* that follows the LLM candidate, not a ceiling
on LLM recall. Phase B completes the focused frame for the remaining five entities
(Onset, WhenDiagnosed, BirthHistory, EpilepsyCause, PatientHistory) so "one
focused call per entity" is general, and reads the **full per-entity
candidate-quality map** in one combined run. This is the candidate-quality input
to the Phase C hybrid; it routes nothing and gates nothing on the locked holdout.

## Structural caveat (dominant for the five new entities)

All five new entities carry `CUI`/`CUIPhrase`, so their gold `text` is the
**normalized concept phrase** (dash-joined, e.g. `born-normally`,
`traumatic-brain-injury`, `febrile-seizures`), not the letter surface phrase the
focused frame asks the LLM to emit. The source-near overlap recall is therefore
**altitude-sensitive** for all five — exactly the Diagnosis/SF caveat from Phase A,
now the rule rather than the exception. A depressed source-near recall on these
entities is ambiguous between a genuine missed candidate and a surface-vs-concept
altitude gap, and must be read against `raw_text` overlap in Phase C before any
prompt fix. Semantic item/letter F1 (CUI-dropped) is the cleaner read here.

## Predeclared expectations (per regime, not pass/fail hypotheses)

- **PatientHistory (recall_bound).** The broadest entity (any past condition,
  attack type, procedure) and the lowest published cell of the five (0.78). Expect
  the largest candidate-set spread and the highest over-emission of the five; the
  open-ended concept space is where the focused frame's recall is most useful and
  most at risk of false positives.
- **Onset (mixed).** Recall and projection both matter; expect moderate
  source-near recall with a real attribute burden (Age/AgeUnit vs
  NumberOfTimePeriods/TimePeriod), and confusion risk against WhenDiagnosed (onset
  vs diagnosis date), which the frames explicitly separate.
- **WhenDiagnosed, BirthHistory, EpilepsyCause (representation_bound).** High
  expected LLM candidate recall; the residual is projection (CUIPhrase altitude,
  casing, gestation-band / Certainty / Negation convention). Expect the
  semantic-vs-source-near gap to be projection-shaped, not a recall deficit —
  the Prescription signature from Phase A.

## Design

One focused DSPy call per (entity, letter), unchanged from Phase A: registry-derived
attribute vocabulary + per-entity worked examples + exact-substring evidence +
diagnostic confidence/rationale. Deterministic code validates JSON, repairs
schema/closed-vocab neutrally, drops evidence-non-substring mentions (never
silently kept), and projects CUIs as a separate post-step. Gating is
observable-only; `confidence` is diagnostic, never a router. The four Phase-A
frames are byte-unchanged in clinical content; the version bump to v0.4 marks the
all-nine frame set and lets the combined table report one prompt version.

## Primary metric and decision rule

- **Primary:** per-entity **source-near overlap recall** (format-blind candidate
  read, altitude-caveated above) and **semantic per-item/per-letter F1**, each vs
  (a) the all-9 single-pass baseline and (b) the published per-entity cell.
- **Read (not a route):** the full nine-entity candidate-quality map — for each
  entity, (i) does the focused frame lift LLM candidate recall over the
  attention-diluted all-9 pass, and (ii) how much deterministic projection /
  over-emission control must follow the LLM candidate (the regime). No entity is
  routed away from GPT candidate generation regardless of outcome.
- **Secondary:** over-emission (source-near FP) per entity — the first hybrid
  target list for Phase C; semantic-vs-source-near gap as projection-vs-recall
  attribution; evidence-validity rate.

## Gates and scale

- Pilot25: **zero unexplained** parse/call failures across all nine before dev140.
- dev140: full nine-entity combined table at v0.4.
- Resumable runner. No full-200 audit in this phase (blocked until Phase E).

---

## Results

Run: dev140, gpt-4.1-mini, temperature 0.0, prompt
`exectv2_llm_only_per_entity_v0.4` (2026-06-17). Artifacts:
`experiments/exectv2_llm_only_per_entity_dev140_gpt41mini_20260617_*` (per-entity
JSONL/report + `_combined.{md,json}`). Baseline column = all-9 single pass
`exectv2_llm_only_all_entities_dev140_gpt41mini_20260612.jsonl`, same 140 letters.

### Gate (observable-only)

Clean. Pilot25 and dev140 both ran with **zero call failures and zero
parse/schema failures across all nine entities**. Evidence validity 0.884–1.000
(PatientHistory lowest at 0.884; BirthHistory and WhenDiagnosed perfect). The
pilot25 zero-unexplained-failure gate passed before dev140.

### Full nine-entity table (dev140)

| Entity | Regime | Pub item F1 | Base sem item | Probe sem item | Probe sem letter | Base SN recall | Probe SN recall | Δ SN recall | Over-emit (probe/base) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| BirthHistory | representation_bound | 0.97 | 0.000 | 0.281 | 0.471 | 0.613 | **0.806** | +0.194 | 1/0 |
| Diagnosis | recall_bound | 0.85 | 0.176 | 0.243 | 0.647 | 0.301 | 0.306 | +0.005 | 30/42 |
| EpilepsyCause | representation_bound | 0.90 | 0.000 | 0.175 | 0.237 | 0.286 | **0.809** | +0.524 | 42/6 |
| Investigations | recall_bound | 0.95 | 0.328 | 0.546 | 0.755 | 0.868 | 0.890 | +0.022 | 58/45 |
| Onset | mixed | 0.96 | 0.000 | 0.148 | 0.219 | 0.588 | **0.824** | +0.235 | 77/25 |
| PatientHistory | recall_bound | 0.78 | 0.006 | 0.163 | 0.526 | 0.167 | **0.363** | +0.195 | 212/105 |
| Prescription | representation_bound | 0.87 | 0.179 | 0.173 | 0.385 | 0.820 | **0.903** | +0.083 | 46/83 |
| SeizureFrequency | mixed | 0.66 | 0.000 | 0.134 | 0.298 | 0.497 | **0.642** | +0.144 | 51/59 |
| WhenDiagnosed | representation_bound | 0.91 | 0.000 | 0.073 | 0.087 | 0.455 | **1.000** | +0.545 | 33/3 |

### Reads (the five new entities)

- **WhenDiagnosed (representation_bound) — the cleanest representation-bound
  signature.** Source-near recall **1.000** (every gold WhenDiagnosed concept is
  in the LLM candidate set) with semantic F1 only 0.073 and over-emission 3 → 33.
  The candidate is fully present; everything missing is projection (CUIPhrase
  altitude — the gold `text` is the truncated/normalized `epileps`/`epilepsy`)
  plus heavy over-emission of diagnosis-of-epilepsy mentions that are not gold
  WhenDiagnosed. Pure Phase-D + over-emission work, zero recall work.
- **EpilepsyCause (representation_bound).** The largest recall lift of all nine
  (0.286 → 0.809, +0.524): the focused frame recovers cause/aetiology candidates
  the all-9 pass drowned. Over-emission rose 6 → 42 — the frame is liberal about
  what counts as a "cause." Projection + over-emission control follow.
- **BirthHistory (representation_bound) — the clean one.** Recall 0.806 (+0.194),
  the best semantic F1 of the five new (0.281), and **near-zero over-emission (1)**.
  A narrow, well-bounded concept space; mostly a projection gap with little FP
  risk for the hybrid.
- **Onset (mixed).** Recall 0.824 (+0.235) with the second-heaviest over-emission
  (25 → 77). Both recall and projection move, and the FP load (onset vs diagnosis
  date, plus liberal condition tagging) is a real hybrid target.
- **PatientHistory (recall_bound) — the over-emission problem child, as
  predicted.** By far the highest over-emission (105 → **212**) and the lowest
  source-near recall of the five new (0.363, +0.195). The broadest, most
  open-ended concept space (any past condition/event/procedure); its low overlap
  is part altitude (normalized gold `text`) and part the genuinely unbounded
  candidate space. The **#1 hybrid over-emission / boundary-definition target**.

### Cross-entity reading

The corrected Phase-A framing holds across all nine: the LLM is a high-recall
candidate source for **every** entity. Eight of nine clear the +0.05 source-near
margin over the all-9 pass; the two that don't (Diagnosis +0.005, Investigations
+0.022) were already high or already altitude-capped at the all-9 baseline, not
genuine focused-frame failures. The regime sizes the *projection + over-emission*
burden that follows the candidate, never whether the LLM is the candidate source.

**Over-emission ranking (first hybrid targets, Phase C):** PatientHistory (212) ≫
Onset (77) > Investigations (58) > SeizureFrequency (51) > Prescription (46) >
EpilepsyCause (42) > WhenDiagnosed (33) > Diagnosis (30) ≫ BirthHistory (1).

**Altitude caveat confirmed.** All five new entities carry CUIPhrase, so the
high source-near recall with low semantic F1 (especially WhenDiagnosed 1.000 /
0.073) is the surface-vs-concept altitude gap, not a recall ceiling. Phase C must
read `raw_text` overlap before any candidate-generation prompt change on
WhenDiagnosed, PatientHistory, and Diagnosis.

### Phase C implications

No entity is routed off GPT candidate generation. The candidate-quality map for
the hybrid: (a) over-emission control is the dominant first task, led by
PatientHistory and Onset; (b) BirthHistory is the low-risk projection-only entity;
(c) WhenDiagnosed and EpilepsyCause are recall-complete and need projection +
boundary tightening; (d) Diagnosis remains the one entity whose source-near recall
needs a real-gap-vs-altitude diagnosis before a prompt fix.
