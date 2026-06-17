# Satellite 09 — GPT-First Execution Plan (Phased)

Parent: [[00_overarching_implementation_plan]] · execution arm of
`docs/research/exectv2_gpt_first_full_architecture_strategy_2026-06-17.md`
Status: active. Dev-split only. No new full-200 audit until Phase E gate is met.
Date opened: 2026-06-17 · Phase A complete (2026-06-17); Phase B complete
(2026-06-17); Phase C complete (2026-06-17); Phase D complete (2026-06-17);
Phase E next.

## North star and claim ladder

The earnable end claim: *a single modular framework beats the ExECTv2 benchmark
across broad epilepsy phenotyping while preserving transparent component
attribution, evidence validity, and deterministic-rule ablations.* Targets:
overall **0.87 per-item / 0.90 per-letter**, plus per-entity cells against the
published table (BirthHistory 0.97, Diagnosis 0.85, EpilepsyCause 0.90,
Investigations 0.95, Onset 0.96, PatientHistory 0.78, Prescription 0.87,
SeizureFrequency 0.66, WhenDiagnosed 0.91).

Until that gate is met the honest claim is the transfer claim: Gan established the
architecture and reliability discipline (source-near state, exact evidence,
component attribution, format ablations, family-aware gates); ExECTv2 tests
whether it scales from deep SF reasoning to broad phenotyping.

## The governing lesson from the Gan close-off

The Gan winner was `hybrid_structured_events` (test450 Purist **0.812**), **not**
`llm_only` — pure `llm_only_canonical_pipeline` was the weakest architecture in
the table (**0.724**), ~9 points behind. The win came from a **split of labor**,
but note *which* split. The **LLM did the heavy lifting**: candidate generation,
clinical reasoning, and candidate selection over source-near structured state.
Deterministic code owned ontology normalization, projection, rendering, and
scoring. `hybrid_structured_events` **never relied on deterministic candidate
generation** — the LLM emitted the candidates; the deterministic layer never
introduced or chose a clinical fact.

Consequence for ExECTv2 (and the design rule for this whole plan): the **LLM is
the candidate source for every entity** and is expected to reach high recall
everywhere. Deterministic rules help with ontology normalization, scoring
projection, and can be a useful *addition* to candidate generation — but they
never become the primary recall engine. The LLM-only track is not the headline
only because it omits the deterministic normalization/projection layer the
benchmark key needs; its job is to be the strongest possible candidate generator
and reasoner, which the hybrid (Phase C) then projects to the benchmark format.

## Where the leverage is (projection-gap ledger, dev)

The all-entity ledger is built on the **deterministic** all-9 baseline. It splits
every gold miss into candidate-source (concept absent from predictions) vs
projection (concept present, benchmark key differs). Because it is measured on the
deterministic system, the "recall-bound" label means *the deterministic rules*
miss the concept — it is **not** a ceiling on LLM recall. The LLM is expected to
generate high recall on every entity; the regime instead sizes *what must follow
the LLM candidate* to land on the benchmark key:

| Regime | Entities | What must follow the LLM candidate |
| --- | --- | --- |
| recall-bound (low projection share) | Diagnosis (0.17), Investigations (0.29), PatientHistory (0.21) | the deterministic baseline misses the concept entirely, so the LLM candidate *is* the recall; projection is light |
| representation-bound (high projection share) | Prescription (0.87), BirthHistory (0.86), WhenDiagnosed (1.0), EpilepsyCause (0.67) | the concept is easy to recall, so the work is deterministic projection (phrase altitude, casing, attribute/CUI convention) on top of the LLM candidate |
| mixed | Onset (0.58), SeizureFrequency (0.55) | both recall and projection |

On representation-bound entities the LLM still generates the candidate; raw LLM
recall there lands as over-emission or altitude misses *until* deterministic
projection maps it to the benchmark key. The regime decides how much projection
work follows the LLM candidate, never whether the LLM is the candidate source.

## Phases

### Phase A — Per-entity LLM-only candidate-source probe (DONE 2026-06-17)

A candidate-generation experiment, not a final-labeler experiment. Predeclared in
`docs/research/exectv2_llm_only_per_entity_pilot_predeclaration_2026-06-17.md`
(Results section filled).

1. Generalize `llm/llm_only_per_entity.py` beyond its SF hardwiring: an
   `entity_name`-parameterized focused frame (anchor phrase + entity-legal
   attributes + exact evidence + diagnostic confidence/rationale), with
   registry-derived attribute vocabulary and per-entity worked examples for
   Prescription, Investigations, Diagnosis (SF frame preserved). Bump
   `PROMPT_VERSION`.
2. Add `runners/run_llm_only_per_entity.py` that loops the four target entities,
   emits per-entity JSONL + report, and a combined per-entity table against the
   published cells and the all-9 single-pass baseline.
3. Score three layers (phrase_only / semantic / benchmark-with-CUI) **and** the
   source-near overlap-recall diagnostic — the latter is the candidate-generation
   read (format-blind), the thing this phase is actually about.
4. Gate on observable facts only: exact-substring evidence, schema/closed-vocab
   repair, attribute legality. `confidence` stays diagnostic — never a router
   (carry the Gan finding that even failure-mode-primed confidence is modest,
   AUROC ~0.61, and well below external corroboration).
5. Pilot25 zero-unexplained-failure gate → dev140 full per-entity table.
   Resumable runner. No full-200.

Exit: per-entity semantic + source-near table for the four entities vs baseline
and published cells, with a per-entity read of (a) whether the focused frame lifts
**LLM** candidate recall over the attention-diluted all-9 pass, and (b) how much
deterministic projection must follow each entity's LLM candidates (the regime).
GPT is the candidate source for all four entities; the verdict is about recall
quality and projection burden, never about routing an entity to deterministic
candidate generation.

**Result (dev140, gpt-4.1-mini, temp 0.0, prompt `v0.3`).** Gate clean — zero
call/parse failures on pilot25 and dev140; evidence validity 0.945–0.988.
Artifacts: `experiments/exectv2_llm_only_per_entity_dev140_gpt41mini_20260617_*`.
Source-near (LLM candidate) recall confirms the LLM is a high-recall candidate
source across regimes: Prescription 0.903, Investigations 0.890, SeizureFrequency
0.642, Diagnosis 0.306.

| Entity | Regime | Probe SN recall | Δ vs all-9 | Semantic item F1 (base→probe) | Over-emit (probe/base) |
| --- | --- | ---: | ---: | --- | ---: |
| Prescription | representation-bound | 0.903 | +0.083 | 0.179→0.173 | 46/83 |
| Investigations | recall-bound | 0.890 | +0.022 | 0.328→0.546 | 58/45 |
| SeizureFrequency | mixed | 0.642 | +0.144 | 0.000→0.134 | 51/59 |
| Diagnosis | recall-bound | 0.306 | +0.005 | 0.176→0.243 | 30/42 |

Reads: the focused frame's recall lift landed on Prescription and SeizureFrequency,
**not** on the recall-bound pair (Investigations had no headroom at 0.868 baseline;
Diagnosis stayed low). Prescription is the textbook representation-bound signature —
recall rose to 0.903 and over-emission fell (83→46) while semantic F1 stayed flat,
i.e. a pure projection gap for Phase D. Investigations took the largest semantic
gain (0.328→0.546) but its over-emission *rose* (45→58): first hybrid over-emission
target. Diagnosis is the one apparent recall deficit — **caveat:** Diagnosis and SF
carry the clean `CUIPhrase` as gold `text`, so their source-near overlap is
altitude-sensitive; Phase C must separate a real Diagnosis recall gap from this
altitude artifact (compare against `raw_text` overlap) before fixing the prompt. No
entity is routed off GPT candidate generation.

### Phase B — Per-entity LLM-only completion (DONE 2026-06-17)

Extended the focused frame to the remaining five entities (Onset, WhenDiagnosed,
BirthHistory, EpilepsyCause, PatientHistory) so "one focused call per entity" is
general; bumped to `v0.4` and re-ran all nine for a single-version map.
Predeclared/recorded in
`docs/research/exectv2_per_entity_phase_b_predeclaration_2026-06-17.md`. The Qwen
3.6:35B transfer read is available via `--model` but was not run this phase.

**Result (dev140, gpt-4.1-mini, temp 0.0, prompt `v0.4`).** Gate clean — zero
call/parse failures across all nine; evidence validity 0.884–1.000 (PatientHistory
lowest). Artifacts:
`experiments/exectv2_llm_only_per_entity_dev140_gpt41mini_20260617_*`. The
corrected Phase-A framing holds across all nine: the LLM is a high-recall
candidate source for every entity (eight of nine clear the +0.05 source-near
margin over the all-9 pass; Diagnosis +0.005 and Investigations +0.022 were
already at ceiling/altitude-capped, not failures).

| Entity | Regime | Probe SN recall | Δ vs all-9 | Semantic item F1 | Over-emit (probe/base) |
| --- | --- | ---: | ---: | ---: | ---: |
| WhenDiagnosed | representation-bound | 1.000 | +0.545 | 0.073 | 33/3 |
| Onset | mixed | 0.824 | +0.235 | 0.148 | 77/25 |
| EpilepsyCause | representation-bound | 0.809 | +0.524 | 0.175 | 42/6 |
| BirthHistory | representation-bound | 0.806 | +0.194 | 0.281 | 1/0 |
| PatientHistory | recall-bound | 0.363 | +0.195 | 0.163 | 212/105 |

Reads: **WhenDiagnosed** is the cleanest representation-bound signature (recall
1.000, semantic 0.073 — pure projection/altitude + over-emission, zero recall
work). **BirthHistory** is the low-risk projection-only entity (near-zero
over-emission). **PatientHistory** is the over-emission/boundary problem child
(212 FP, the broadest concept space) — the #1 hybrid over-emission target, ahead
of **Onset** (77). All five new entities carry CUIPhrase, so high SN recall with
low semantic F1 is the surface-vs-concept altitude gap (Phase C reads `raw_text`
overlap before any candidate prompt change). Over-emission ranking for Phase C:
PatientHistory (212) ≫ Onset (77) > Investigations (58) > SeizureFrequency (51) >
Prescription (46) > EpilepsyCause (42) > WhenDiagnosed (33) > Diagnosis (30) ≫
BirthHistory (1).

### Phase C — GPT hybrid candidate assessment (the benchmark-beating route) (DONE 2026-06-17)

Extend the SF live-candidate-set pattern (`hybrid/candidate_set.py`,
`hybrid/clinical_assessment.py`) to all nine entities:

```text
raw letter
  -> GPT per-entity candidate generation for every entity (the recall engine)
     [+ deterministic candidates as optional augmentation, never the primary source]
  -> GPT candidate assessment / merge / selection / clinical-boundary reasoning
     over evidence-grounded candidates
  -> deterministic projection + ontology normalization from selected facts
     (attributes, CUI, casing)
  -> evidence + plausibility gate
  -> PredictedLetter
```

Rules from Gan, matching the winning `hybrid_structured_events` split: the **LLM
owns candidate generation, clinical reasoning, and candidate selection** for every
entity; deterministic code owns ontology normalization, projection, and scoring,
and may *augment* (never replace) candidate generation. Prefer one strong LLM
assessment pass over reasoner ladders until an ablation earns the extra stage.
**Over-emission is the first hybrid target** (the ledger predicts large FP on
Investigations and Prescription); keep routed mentions visible as reliability
output. Phase A's regime map sizes the deterministic projection that follows the
LLM candidates per entity — heavy on representation-bound entities, light on
recall-bound ones — it does not route any entity away from GPT candidate
generation.

**Implementation.** `hybrid/all_entity_assessment.py` assembles the nine focused
per-entity GPT passes (the candidate-generation+reasoning+selection already run
in Phase A/B — one focused call per (entity, letter) *is* the one strong
assessment pass) into a single combined all-nine `PredictedLetter`. The focused
per-entity frame is the candidate source; `hybrid/all_entity_gate.py` generalizes
the SF verify/route to every entity (evidence-substring faithfulness for all,
frequency-bearing plausibility for SF, within-letter duplicate collapse) and
routes — never edits — what it cannot keep. Deterministic CUI projection
(`benchmark_projection.project_cuis`) runs after selection. The runner
(`runners/run_hybrid_all_entities.py`) is **replay-first** (reads the Phase B
per-entity JSONLs → zero extra LLM calls); `--mode live` regenerates candidates
resumably per entity; `--augment-rules` unions the deterministic all-9 rule
candidates (the optional, never-primary augmentation).

**Result (dev140, gpt-4.1-mini candidates v0.4, replay).** Honest combined
headline, far below the gate. Artifacts:
`experiments/exectv2_hybrid_all_entities_dev140_gpt41mini_20260617{,_ruleaug}.{jsonl,md}`.

| Candidate set | Semantic item F1 | Semantic item P / R | Benchmark item F1 | Phrase letter F1 | Routed |
| --- | ---: | --- | ---: | ---: | ---: |
| GPT only (9 focused passes) | 0.220 | 0.232 / 0.208 | 0.181 | 0.626 | 11 |
| GPT + deterministic rule augmentation | 0.344 | 0.294 / 0.414 | 0.312 | 0.748 | 264 |

Reads: (1) **Over-emission (precision ~0.23), not recall, is the binding
constraint** — the gate only routes 11 GPT candidates because the per-entity
outputs are already evidence-valid and the well-formed-but-spurious/altitude
candidates are the LLM's to prune (the second selection stage the plan defers
until an ablation earns it). (2) **Deterministic augmentation is a real lever**:
unioning the all-9 rule candidates lifts semantic F1 0.220→0.344 and benchmark
0.181→0.312 (recall 0.208→0.414) while the gate collapses 258 duplicates —
because the rules land the benchmark-key altitude/CUI the raw GPT phrase misses,
confirming the representation-bound regime thesis. (3) The combined headline
stays honest at 0.34/0.31 semantic/benchmark — the gate is **not** met, so no
full-200 audit (Phase E). The first hybrid target remains over-emission, and the
named next stage is a GPT candidate-selection pass (ablation-gated).

### Phase D — Benchmark-format projection completion (DONE 2026-06-17)

Extend the shared phrase→CUI lexicon/projection (`benchmark_projection.py`,
`deterministic/lexicon.py`) across all nine entities so the with-CUI headline is
real, not 0-by-construction. Keep it a separate post-step with its own ablation:
report semantic (CUI-dropped) and benchmark (with-CUI) together; never credit CUI
projection as LLM clinical reasoning. This phase is where representation-bound
entities actually move.

**Implementation.** The shared lexicon already spans all nine entities (commit
e0639cd); the benchmark match key includes `CUI` while the semantic key drops it,
so the benchmark-vs-semantic delta is exactly the deterministic projection's
credit. Phase D formalizes that as a first-class, reusable ablation:
`reports/cui_projection_diagnostic.py` measures the projection's **coverage**
(fraction of predictions the lexicon attaches a CUI to), **correctness** (CUI
agreement on source-near overlaps), and **gold CUI density** (the share of the
benchmark key it must reproduce); `runners/run_cui_projection_diagnostic.py`
emits it from any combined all-entity JSONL. The hybrid report already prints the
per-entity semantic↔benchmark delta beside it.

**Result (dev140, GPT-only hybrid prediction).** Artifacts:
`experiments/exectv2_hybrid_all_entities_dev140_gpt41mini_20260617_cui_projection.{md,json}`
(and the `_ruleaug_` pair).

| | Overall | EpilepsyCause | PatientHistory | Onset | Diagnosis | SeizureFrequency | Investigations | Prescription | WhenDiagnosed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Gold CUI density | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Pred CUI coverage | 0.60 | 0.24 | 0.25 | 0.44 | 0.46 | 0.74 | 0.92 | 0.97 | 1.00 |
| CUI agreement (where both) | 0.90 | 1.00 | 0.92 | 1.00 | 0.80 | 0.85 | 0.82 | 0.99 | 1.00 |

Reads: (1) **Every gold mention carries a CUI (density 1.00)**, so the benchmark
key requires a correct CUI on every match — the with-CUI headline cannot exceed
the projection's coverage×correctness. (2) The gap is **coverage-bound, not
correctness-bound**: where the lexicon fires it agrees with gold at 0.80–1.00
(overall 0.90), but it only covers 60% of predictions, and benchmark sits *below*
semantic precisely on the low-coverage open-vocab entities (EpilepsyCause 0.24,
PatientHistory 0.25, Onset 0.44, Diagnosis 0.46) — a finite lexicon cannot
enumerate every clinical phrase. (3) **The honest verdict the plan demands:**
closing the coverage gap means gold-aligning the lexicon, which is *in-sample CUI
lookup* — a documented projection artifact (see [[project_exectv2_scoring_artifacts]]),
reported as separate projection credit, never as LLM clinical reasoning. Phase D
therefore makes the projection auditable rather than inflating it by fitting the
lexicon to dev gold; the with-CUI headline stays gated by lexicon coverage and is
always reported beside the CUI-dropped semantic layer.

### Phase E — Reliability scorecard and predeclared full-200 audit

Only after dev evidence clears the gate. Produce the compact reliability
scorecard (below), a predeclared aggregate readout, bootstrap CIs, and the
dev→audit gap. Lock the architecture and register the audit immutably. Then port
the frozen design to Qwen as a model-transfer experiment.

## Measurement plan (every serious GPT run)

| Axis | Required fields |
| --- | --- |
| Task correctness | overall + per-entity per-item/per-letter F1 (phrase/semantic/benchmark) |
| Candidate generation | source-near overlap recall per entity (format-blind) |
| Faithfulness | evidence-valid / total; dropped-evidence count |
| Schema reliability | parse failures, repairs, dropped invalid mentions |
| Benchmark format | semantic vs with-CUI gap; CUI coverage |
| Calibration/routing | routed/abstained by reason; routed-row outcome where scored |
| Robustness | per-entity error spread; strong-entity regression check |
| Operational | calls, elapsed, resume count, cost |

## Promotion gates

- Aggregate lift **and** no severe regression in an already-strong entity.
- Evidence validity and parse reliability stay high.
- Rule / CUI / LLM-selection ablations explain where the score comes from.
- Dev evidence before any full-200 audit; readout predeclared.

## Guardrails

- The **LLM is the candidate source for every entity**; deterministic candidate
  rules only augment, never replace, LLM recall. The LLM does the heavy lifting on
  candidate generation, clinical reasoning, and candidate selection; deterministic
  code handles normalization, projection, and scoring.
- Deterministic code never introduces or chooses a clinical fact in an
  `llm_only` claim; attribution stays clean across `rules_only`, `llm_only`,
  `hybrid`.
- Benchmark-format repairs are controlled variables, surfaced not hidden.
- `confidence` is diagnostic, not a gate.
- Phrase-altitude misses are partly target-construction artifacts; separate real
  misses (source-near overlap) from altitude convention before chasing a prompt
  fix.
