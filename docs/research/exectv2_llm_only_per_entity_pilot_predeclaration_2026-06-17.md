# ExECTv2 — Per-Entity LLM-Only Candidate-Source Pilot — Predeclaration

Date: 2026-06-17
Driver: `runners/run_llm_only_per_entity.py` (generalized
`llm/llm_only_per_entity.py`)
Split: dev (pilot25 → dev140) · Model: gpt-4.1-mini · Temperature 0.0
Entities: Prescription, Investigations, Diagnosis, SeizureFrequency
Plan: [[09_gpt_first_execution_plan]] Phase A

## Question

Does a **focused per-entity** LLM-only frame (one call per entity, entity-legal
attributes only) generate clinical candidates the all-9 single-pass run misses —
and does that lift land **only where the projection-gap ledger says the entity is
recall-bound**? This decides which entities should use GPT as a candidate source
in the Phase C hybrid, and which stay deterministic-candidate + projection.

This is a candidate-generation experiment, not a final-labeler experiment. The
all-9 single pass is the documented negative baseline (attention-diluted,
over-emitting, dev140 semantic 0.087 item / 0.236 letter; best cells Diagnosis
0.176, Investigations 0.328).

## Predeclared hypotheses

- **H1 — recall lift where recall-bound.** Focused per-entity raises the
  **source-near overlap recall** (and semantic F1) on Diagnosis and Investigations
  above the all-9 single-pass baseline, because a single-entity frame cuts
  attention dilution and lets real missed candidates surface. These are the
  entities (ledger projection share 0.17 / 0.29) where new candidates can exist.
- **H2 — no recall lift where representation-bound (Prescription = control).**
  On Prescription, focused per-entity gives little or no source-near recall gain
  over all-9; any F1 movement is projection-format, and over-emission persists
  (ledger: 0.87 projection share, 136 FP, headline dominated by phrase altitude).
- **H3 — SF mixed, focused > single.** Per-entity beats single-pass on SF
  semantic (replicating the dev140 gpt-4.1-mini result, per_entity 0.135 vs
  single_pass 0.094 item) but stays well below the 0.66 published cell — the hard
  transfer case.

## Design

One focused DSPy call per (entity, letter). The model emits source-near frames
(anchor phrase + entity-legal attributes + exact evidence + diagnostic
confidence/rationale). Deterministic code validates JSON, repairs schema/closed-
vocab neutrally, drops evidence-non-substring mentions (never silently kept), and
projects CUIs as a separate post-step. Gating is observable-only; `confidence`
is diagnostic, never a router.

## Primary metric and decision rule

- **Primary:** per-entity **source-near overlap recall** (format-blind candidate
  read) and **semantic per-item/per-letter F1**, each vs (a) the all-9 single-pass
  baseline and (b) the published per-entity cell.
- **Decision:** an entity is confirmed a **GPT candidate source** for Phase C when
  focused per-entity beats the all-9 baseline on source-near recall by a clear
  margin. Entities that do not improve recall are routed deterministic-candidate +
  projection in the hybrid. Expected outcome under H1–H3: Diagnosis, Investigations
  (and SF partially) confirmed; Prescription not.
- **Secondary:** phrase_only and with-CUI layers (with-CUI expected ~0 absent the
  shared lexicon — Phase D); per-entity over-emission (FP) count; semantic-vs-
  source-near gap as the projection-vs-recall attribution.

## Gates and scale

- Pilot25: **zero unexplained** parse/call failures before dev140 (the
  validation25 → full pattern). Evidence-validity rate reported.
- dev140: full per-entity table for the four entities.
- Resumable runner. No full-200 audit in this phase (blocked until Phase E).

This gates nothing on the locked full-200 holdout and promotes no architecture; it
is a dev diagnostic that maps per-entity candidate quality for the hybrid.

---

## Results

Run: dev140, gpt-4.1-mini, temperature 0.0, prompt `exectv2_llm_only_per_entity_v0.3`
(2026-06-17). Artifacts: `experiments/exectv2_llm_only_per_entity_dev140_gpt41mini_20260617_*`
(per-entity JSONL/report + `_combined.{md,json}`). Baseline column = all-9 single
pass `exectv2_llm_only_all_entities_dev140_gpt41mini_20260612.jsonl`, restricted to
the same 140 letters.

### Gate (observable-only)

Clean. Pilot25 and dev140 both ran with **zero call failures and zero parse/schema
failures** across all four entities. Evidence validity 0.945–0.988 (Diagnosis
lowest at 0.945). The pilot25 zero-unexplained-failure gate passed before dev140.

### Per-entity table (dev140)

| Entity | Regime | Pub item F1 | Base sem item | Probe sem item | Probe sem letter | Base SN recall | Probe SN recall | Δ SN recall | Over-emit (probe/base) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | representation_bound | 0.87 | 0.179 | 0.173 | 0.385 | 0.820 | **0.903** | +0.083 | 46/83 |
| Investigations | recall_bound | 0.95 | 0.328 | 0.546 | 0.755 | 0.868 | **0.890** | +0.022 | 58/45 |
| Diagnosis | recall_bound | 0.85 | 0.176 | 0.243 | 0.647 | 0.301 | 0.306 | +0.005 | 30/42 |
| SeizureFrequency | mixed | 0.66 | 0.000 | 0.134 | 0.298 | 0.497 | **0.642** | +0.144 | 51/59 |

### Hypotheses

- **H1 (recall lift where recall-bound) — NOT supported as stated.** The focused
  frame did *not* lift source-near recall on the two recall-bound entities:
  Diagnosis +0.005 (flat at 0.306), Investigations +0.022 (flat at 0.890).
  Investigations had little headroom — the all-9 baseline already recalled 0.868.
  The recall lifts instead landed on Prescription (+0.083) and SeizureFrequency
  (+0.144). H1 located the lift on the wrong entities.
- **H2 (Prescription = control, no recall lift) — refuted, favourably.** The
  focused frame *did* lift Prescription source-near recall (0.820 → 0.903) **and**
  cut over-emission (83 → 46 FP). Semantic item F1 stayed flat (0.179 → 0.173):
  the recovered recall did not convert to the benchmark key because projection is
  not done — exactly the representation-bound signature. So the LLM is a strong
  Prescription candidate source; the residual is projection, not recall.
- **H3 (SF mixed, focused > single, below 0.66) — supported.** SF semantic item
  F1 0.134 (≈ predeclared 0.135), source-near recall 0.497 → 0.642, still far
  below the 0.66 published cell. The hard-transfer reading holds.

### Recall-bound vs representation-bound read (corrected framing)

The headline correction (see [[09_gpt_first_execution_plan]]): the LLM is the
candidate source for **every** entity, and the data bears this out — source-near
(LLM candidate) recall is 0.90 on Prescription, 0.89 on Investigations, 0.64 on
SeizureFrequency. The ledger regime sizes the *projection burden* that follows the
LLM candidate, not whether the LLM can recall:

- **Prescription** — high LLM recall (0.903), flat semantic F1, dropped
  over-emission. Pure projection gap → Phase D, not a recall problem.
- **Investigations** — high LLM recall (0.890) and the largest semantic gain
  (0.328 → 0.546); but over-emission *rose* (45 → 58). First hybrid over-emission
  target.
- **SeizureFrequency** — focused frame clearly lifts recall; both recall and
  projection work remain.
- **Diagnosis** — the standout deficiency: source-near recall only 0.306 and the
  focused frame barely moved it. **Caveat:** Diagnosis (and SF) carry the clean
  `CUIPhrase` as gold `text`, so the "format-blind" overlap is altitude-sensitive
  for these two — the LLM copies the letter surface phrase, the gold is the
  normalized concept term, so some of this low overlap is altitude, not absent
  candidates. Phase C must separate a genuine Diagnosis recall gap from this
  altitude artifact (compare against `raw_text` overlap) before concluding the LLM
  under-recalls Diagnosis.

### Phase C implications

The LLM stays the candidate source for all four. Prescription and Investigations
need deterministic projection + over-emission control on top of already-strong LLM
recall; SeizureFrequency needs both; Diagnosis needs a recall diagnosis (real gap
vs CUIPhrase altitude) before deciding the candidate-generation prompt fix. No
entity is routed to deterministic candidate generation.
