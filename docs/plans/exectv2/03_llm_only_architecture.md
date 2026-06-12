# Satellite 03 — LLM-Only Architecture

Parent: [[00_overarching_implementation_plan]] · Phases 3 & 6
Status: Phase 3 infrastructure complete (2026-06-10). Dev-split only until the Phase 7 audit.

## Purpose

Build the LLM-only ExECTv2 extractor — the upper bound on unaided model
reasoning, bounded only by the schema-validation and evidence-verification gates.
The LLM produces the prediction-bearing clinical interpretation; deterministic
code may validate JSON, check evidence, and score, but must not introduce or
choose the clinical fact (the `llm_only` family rule from
`contribution_thesis.md`).

## 1. Shape

```
raw letter text
  → LLM extraction call(s)   (structured output: all entity mentions + attributes + evidence + rationale)
  → schema validation gate   (contract/validate.py; semantically-neutral repair only)
  → evidence verification    (each mention's evidence is an exact source substring)
  → adapter → PredictedLetter
```

Two configurations to compare (mirroring Gan 2026's
`llm_only_direct_labeler` vs `llm_only_canonical_pipeline`):

- **`llm_only_single_pass`** — one call per letter emits the full set of entity
  mentions for all in-scope entities. Cheapest, most "honest fully-LLM".
- **`llm_only_per_entity`** — one focused call per entity type per letter (or per
  small entity group). Higher recall per entity, more calls; useful to isolate
  whether breadth fails from attention dilution.

Phase 3 builds these for **Seizure Frequency only**; Phase 6 extends the schema
to all nine entities.

## 2. Output schema & gates

The model emits structured JSON matching `contract/prediction.py`. The gates are
the reliability story:

- **Schema validity**: entity/attribute legality via the registry. Invalid →
  repair (neutral) or drop, both logged. Report schema-validity + repair rate.
- **Evidence verification**: `evidence_is_substring`; mentions whose evidence is
  not an exact substring are flagged (and, per policy, dropped from the scored
  set — never silently kept). Report evidence-validity rate.

These gates are what let an LLM-only system make a *reliability* claim rather
than a raw-score claim.

## 3. Prompt design

Governed by ADR 0015: every model-facing string is a plain clinical brief with
no internal architecture vocabulary; enforced by a prompt-hygiene test (mirror
`test_gan2026_llm_prompt_hygiene.py`).

- A clear task brief per entity: what the entity is, what each attribute means in
  plain clinical language, the legal value vocab, and "quote the exact span you
  used as evidence."
- For Seizure Frequency, port the hard-case guidance proven in Gan 2026's
  `guidance_for_tricky_cases` (current-vs-historical, seizure-free, cluster
  cadence vs intra-cluster rate, conditional/triggered windows, ranges with
  windows), reworded for ExECTv2's mention-level output.
- Ground the `confidence` field operationally (Gan 2026 Phase 3 pre-condition A):
  define low/medium/high against observable note features, not undefined.
- Use the closed `uncertainty_flags` vocabulary (satellite 07).

## 4. Versioning & runs

- `PROMPT_VERSION` string per config, bumped on every prompt change (Gan 2026
  discipline). Recorded in run metadata.
- Pilot on a tiny dev slice (≈25 letters) for 0-failure confirmation before any
  full dev-split run (the validation25 → validation750 pattern).
- Model as an experimental variable: run gpt-4.1-mini first; add qwen3.6-35b /
  deepseek as conditions. Long local runs use the detached `Start-Process`
  pattern to survive the harness's ~9-minute background kill.

## 5. Cross-pollination (Phase 5 input)

The LLM-only error analysis feeds the hybrid design: where the model reliably
picks the right fact but mis-formats attributes, that representation work should
move to a deterministic normalize stage (the central hybrid lesson). Where it
mis-judges the clinical fact, that stays the LLM's job. Catalog both, per entity.

## 6. Deliverables & tests

- `llm/llm_only_single_pass.py`, `llm/llm_only_per_entity.py` with prompt builders
- Schema-validation + evidence-verification integration into the call path
- Prompt-hygiene test; structured-output parse tests on fixtures
- Pilot + dev-split run artifacts registered in the run registry
- Per-config dev per-item/per-letter F1 + row-level error list

## 7. Exit criteria

- **Phase 3**: both LLM-only configs score SF on dev with 0 unexplained
  failures; schema-validity and evidence-validity rates reported; prompts
  hygiene-clean and versioned.
- **Phase 6**: schema extended to all 9 entities; overall dev F1 reported per
  config and per model.

---

## 3a. Phase 3 — Infrastructure complete (2026-06-10)

Both LLM-only extractors are built, gated, and test-covered; live runs are
the next step (pilot 25 letters, then full dev split).

**Deliverables shipped:**
- `llm/llm_only_single_pass.py` — one-call-per-letter extractor + runner
- `llm/llm_only_per_entity.py` — focused-entity extractor (reuses core logic)
- `runners/run_llm_only_sf.py` — CLI (`--config {single_pass|per_entity}`,
  `--mode {live|prompt-only}`, `--pilot N`)
- `tests/test_exectv2_llm_only_sf.py` — 26 tests all passing:
  prompt hygiene (2), parse (7), attribute repair (5), evidence gate (4),
  adapter (3), prompt content (5)

**Architecture:**
- MentionRecord → parse_extraction_json → repair_attributes + check_evidence
  → to_predicted_letter → score_entity (PHRASE_ONLY / SF_SEMANTIC / SF_BENCHMARK)
- Evidence-invalid mentions are **dropped** (never silently kept); attribute
  violations are **stripped** (neutral repair); all actions logged in
  `gate_warnings`.
- Prompts are hygiene-clean: no internal architecture vocabulary (ADR 0015).

**Pilot 25 live results (single-pass v0.2, gpt-4.1-mini, D16-rescored gold):**

| config | per-item P / R / F1 | per-letter P / R / F1 |
|--------|--------------------|-----------------------|
| phrase_only | 0.655 / 0.613 / **0.633** | 0.684 / 0.867 / **0.765** |
| sf_semantic | 0.069 / 0.065 / 0.067 | 0.250 / 0.133 / 0.174 |
| sf_benchmark | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 / 0.000 |

Gate health: 0 call failures, 0 parse failures, evidence validity 100% (29/29).
Deterministic baseline for comparison (dev, repaired gold): phrase_only 0.485 / 0.604.
**LLM single-pass beats the deterministic baseline on both phrase axes at N=25.**
**phrase_only per-letter 0.765 exceeds the SF benchmark target (0.68).**

sf_semantic near-0 is an attribute-convention gap (MonthDate numeric vs name, range
encoding, extra keys), NOT phrase errors — 2 TPs confirm the model can match the
full bundle when the pattern is unambiguous (EA0009 range+period, EA0025
FrequencyChange). sf_benchmark = 0 because LLM doesn't produce CUI (D3; CUI
is a shared post-step, not per-architecture).

**Full dev results (140 letters, D16 repaired gold) — two model conditions:**

#### gpt-4.1-mini

| config | per-item P / R / F1 | per-letter P / R / F1 |
|--------|--------------------|-----------------------|
| single_pass phrase_only | 0.456 / 0.476 / **0.466** | 0.704 / 0.697 / **0.701** |
| single_pass sf_semantic | 0.092 / 0.096 / 0.094 | 0.326 / 0.141 / 0.197 |
| per_entity phrase_only | 0.492 / 0.481 / **0.486** | 0.720 / 0.677 / **0.698** |
| per_entity sf_semantic | 0.137 / 0.134 / **0.135** | 0.422 / 0.192 / **0.264** |

Gate health: 0 call failures, 0 parse failures on both.
Evidence validity: single_pass 195/199 (97.5%), per_entity 183/190 (96.3%).

#### qwen3.6:35b

| config | per-item P / R / F1 | per-letter P / R / F1 |
|--------|--------------------|-----------------------|
| single_pass phrase_only | 0.381 / 0.385 / **0.383** | 0.679 / 0.576 / **0.623** |
| single_pass sf_semantic | 0.090 / 0.091 / 0.090 | 0.357 / 0.151 / 0.213 |
| per_entity phrase_only | 0.391 / 0.412 / **0.401** | 0.682 / 0.606 / **0.642** |
| per_entity sf_semantic | 0.035 / 0.037 / **0.036** | 0.200 / 0.071 / **0.104** |

Gate health: single_pass 2 parse failures / per_entity 0 parse failures; 0 call failures on both.
Evidence validity: single_pass 189/200 (94.5%), per_entity 197/205 (96.1%).

Deterministic baseline (repaired gold, dev): phrase_only 0.382 per-item / 0.604 per-letter.

> **Phase 6 (all-9 scale-up) execution plan — start here next session.** See
> §3b below. Approach chosen 2026-06-12 (user): **LLM-only first, end-to-end,
> gpt-4.1-mini only**; hybrid + the 8 deterministic entity engines follow in a
> later pass. The shared scoring foundation is already landed.

**Key findings:**
- **gpt-4.1-mini beats qwen on phrase extraction**: per-letter phrase_only 0.701/0.698 vs
  0.623/0.642 — ~11% gap. Both models beat deterministic baseline (0.604) per-letter.
- **gpt-4.1-mini phrase_only per-letter ≥ 0.698 exceeds SF benchmark target (0.68)**;
  qwen (0.623/0.642) does not.
- **gpt-4.1-mini per_entity dramatically better on sf_semantic**: 0.135/0.264 vs qwen
  per_entity 0.036/0.104. The focused per_entity prompt helps gpt-4.1-mini (+44% vs its
  single_pass) but hurts qwen (worse than qwen single_pass 0.090/0.213). Model-dependent
  response to prompt structure.
- **qwen single_pass sf_semantic per-letter 0.213 slightly beats gpt-4.1-mini 0.197** —
  qwen is marginally better at attributes in the single-pass regime.
- **sf_benchmark = 0.000 for both**: LLM omits CUI (D3); CUI lookup is the shared post-step.
- **Per-item below 0.66 benchmark target** for all configs/models; per-letter gap narrower.
  The per-item gap is partly FP proliferation (LLM emits more mentions than gold).

Artifacts:
- `exectv2_llm_only_single_pass_dev140_gpt41mini_20260610.{jsonl,md}`
- `exectv2_llm_only_per_entity_dev140_gpt41mini_20260610.{jsonl,md}`
- `exectv2_llm_only_single_pass_dev140_qwen3635b_20260610.{jsonl,md}`
- `exectv2_llm_only_per_entity_dev140_qwen3635b_20260610.{jsonl,md}`

**Next:** Phase 4 hybrid extractor.

---

## 3b. Phase 6 — All-9 LLM-only scale-up (execution plan, 2026-06-12)

**Status: in progress — scoring foundation landed, extractor/runner/audit + runs
remain.** This section is the pick-up point for the next session. The user
authorized Phase 6 *and* the Phase 7 full-200 audit (2026-06-12) and chose to do
the **LLM-only family first, end-to-end, with gpt-4.1-mini only** — i.e. take one
architecture from SF-only to all-9 entities on dev and through the frozen
full-200 audit before touching the hybrid or building the 8 deterministic
per-entity engines. The deterministic and hybrid all-9 builds are explicitly
deferred to a later pass.

### What "complete" means for this slice

1. The LLM-only single-pass extractor emits **all nine entities** (entity-tagged
   mentions) per letter, gated and scored.
2. A full **dev** run (140 letters, gpt-4.1-mini) producing overall +
   per-entity per-item/per-letter F1 vs the published per-entity cells and the
   0.87/0.90 overall headline.
3. The **frozen full-200 Phase 7 audit** of the locked all-9 LLM-only extractor,
   registered immutably, with the overall headline and per-entity table vs
   0.87/0.90, bootstrap CI, and dev→audit gap — the benchmark-comparable number.

### Already done (2026-06-12, committed as the foundation)

- **Per-entity match policy in `scoring.py`** (the protocol §2 generalization):
  `benchmark_ignore_for(entity)` / `semantic_ignore_for(entity)` and the
  `benchmark_config_for(entity)` / `semantic_config_for(entity)` `MatchConfig`
  builders. Policy encoded: CUIPhrase always ignored; **Certainty + Negation
  ignored for SeizureFrequency only** (guideline L17/L19), in scope for every
  other entity; CUI kept in the benchmark headline, dropped in the semantic
  variant. Smoke-tested; `tests/test_exectv2_scoring.py` still green (8/8).
  This is the only code landed; everything below is still to build.

### Build steps (in order)

1. **Overall scorer** — add to `scoring.py` a `score_overall(gold, pred,
   entities, config_for)` that returns `(overall EntityScore, per_entity dict)`.
   Aggregation: per-item = `sum_prf1` over the per-entity `per_item` PRF1s
   (micro-average across every mention of every entity); per-letter = `sum_prf1`
   over the per-entity `per_letter` PRF1s (micro-average across every
   (letter, entity) presence cell). `config_for` is `benchmark_config_for` for
   the headline and `semantic_config_for` for the CUI-dropped variant. Document
   the aggregation choice (micro over entity cells) in the docstring — the
   benchmark's own overall-aggregation method is a point estimate; ours adds the
   per-entity breakdown and a CI at audit. Pin gold-vs-gold = 1.0 overall and
   per entity in `tests/test_exectv2_scoring.py`.

2. **All-9 extractor** — new `llm/llm_only_all_entities.py` (do **not** overload
   the SF-only `llm_only_single_pass.py`; reuse its gates). Design:
   - `MentionRecord` gains an `entity` field (one of the nine names). Reuse
     `parse_extraction_json`, `_coerce_payload`, `check_evidence`,
     `repair_attributes` from `llm_only_single_pass` — but `repair_attributes`
     must look up the spec **per mention's entity** (`ENTITY_REGISTRY[m.entity]`),
     not a single fixed spec. Drop mentions whose `entity` is not a registry key
     (logged), same neutral-repair discipline.
   - `to_predicted_letter` builds `PredictedMention(entity=m.entity, …)` so a
     letter carries mixed-entity mentions; scoring already filters by entity via
     `ExectLetter.entities(entity)`.
   - **Prompt** (`build_prompt_input`): one brief covering all nine entities.
     Generate the per-entity attribute vocabulary + closed-vocab values
     **from `ENTITY_REGISTRY`** (don't hand-transcribe — drift risk), plus a
     short plain-clinical definition per entity and 1–2 worked examples for the
     high-frequency entities (PatientHistory 656, Diagnosis 572, Prescription
     294, SF 263 mentions — these dominate the overall micro-F1, so spend the
     prompt budget there). Keep ADR 0015 hygiene (no internal architecture
     vocabulary); add a hygiene assertion to the test. `PROMPT_VERSION =
     "exectv2_llm_only_all_entities_v0.1"`. Bump `max_tokens` (all-9 output is
     much larger than SF-only — start ~4000, watch for truncation parse fails).
   - Reuse the resume/checkpoint plumbing verbatim from `llm_only_single_pass`
     (`read_completed`/`pending_items`/`merge_rows`, key=`letter_id`); the row
     schema must carry `entity` on each predicted/gold mention so the audit's
     `_reconstruct_from_rows` can rebuild mixed-entity letters.

3. **Dev runner** — `runners/run_llm_only_all.py` mirroring `run_llm_only_sf`
   (`--model`, `--mode {live,prompt-only}`, `--pilot N`, `--resume`). Report:
   overall per-item/per-letter F1 (benchmark + semantic) and a per-entity table
   vs the published per-entity cells (BirthHistory 0.97, Diagnosis 0.85,
   EpilepsyCause 0.90, Investigations 0.95, Onset 0.96, PatientHistory 0.78,
   Prescription 0.87, SF 0.66, WhenDiagnosed 0.91; overall 0.87/0.90 — protocol
   §1). Pilot 25 → confirm 0 failures → full dev 140 (detached `Start-Process`;
   resume is in place).

4. **Overall Phase 7 audit** — add an `--entities all` (or a sibling
   `run_phase7_audit_overall.py`) path that runs the all-9 extractor over
   `load_letters()` (full 200) and scores `score_overall`. Reuse the bootstrap
   CI (resample letters; aggregate overall F1 on each resample — extend
   `_LetterRecord` to hold per-entity tallies, or bootstrap on the overall
   per-letter item counts), the dev→audit gap, the immutable report + registry
   row. Headline target becomes **overall 0.87 / 0.90**, with the per-entity
   table as the breakdown. Keep the SF-cell audit runner untouched (immutable
   record); generalize by parameter, not by editing the frozen path.

### Known traps (decided, so the next session doesn't re-litigate)

- **CUI = 0 headline is expected and honest.** The LLM emits no CUI (D3), so the
  with-CUI `benchmark` overall collapses toward 0 on every entity, exactly as the
  SF-cell audit showed. The *real* LLM-only quality is the `semantic`
  (CUI-dropped) overall; report both, lead with semantic, and carry the protocol
  §2 "CUI divergence surfaced not hidden" note. Clearing the literal 0.87 with-CUI
  bar requires the **shared phrase→CUI lexicon extended to all 9 entities** (a
  shared post-step, not LLM-only work; SF's lives in `deterministic/lexicon.py`).
  Flag that as the gating item for a true with-CUI overall, but do not build it in
  this pass.
- **D17 phrase basis is resolved as: repair `text:=CUIPhrase` for {SF, Diagnosis}
  only; keep the raw col5 span for the other seven.** The loader already does
  this. For Investigations (90% col5≠col6), Prescription (71%), WhenDiagnosed
  (82%) col6 is a *finding/concept normalization* (often a non-substring like
  `EEG`→`abnormal-eeg`), not a span cleanup, so it is **not** a valid phrase-match
  target and col5 stays the basis — at the cost of understated phrase recall on
  those three (a documented ceiling, like SF's was). Surface a per-entity
  `text≠CUIPhrase` divergence note in the audit so the ceiling is legible. See
  the discoveries log D17 (resolved) and D18.
- **Per-entity output sizing.** The all-9 single call is large; if gpt-4.1-mini
  truncates (parse failure = `max_tokens`), raise `max_tokens` before blaming the
  prompt. The `llm_only_per_entity` (one call per entity) variant is the fallback
  if single-pass attention-dilution tanks the rare entities — but try single-pass
  first (cheaper; the chosen scope).

### Exit criteria for the slice

All-9 LLM-only scores on dev (overall + per-entity, both configs, 0 unexplained
failures); the frozen full-200 audit is registered immutably with the overall
headline vs 0.87/0.90, CI, and dev→audit gap; satellites 03/06 and the phase map
(00 §2) updated with the numbers; discoveries log D17/D18 finalized.
