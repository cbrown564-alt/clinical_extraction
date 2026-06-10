# Satellite 03 — LLM-Only Architecture

Parent: [[00_overarching_implementation_plan]] · Phases 3 & 6
Status: planning. Dev-split only until the Phase 7 audit.

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
