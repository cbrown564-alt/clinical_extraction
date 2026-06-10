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
