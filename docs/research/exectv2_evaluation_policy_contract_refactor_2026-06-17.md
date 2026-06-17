# ExECTv2 Evaluation Policy Contract Refactor

Date: 2026-06-17

Status: implementation note and durable architecture decision. This records the
follow-up refactor from the ExECTv2 gold-representation principles note and the
thermo-nuclear code-quality review: per-entity evaluation policy is now a
first-class contract rather than scattered constants in loader, scorer, and
deterministic extraction code.

This note is a companion to:

- `exectv2_gold_representation_and_scoring_principles_2026-06-17.md`
- `exectv2_deterministic_all9_layered_error_analysis_2026-06-17.md`
- `exectv2_data_discoveries_log.md` D16 and D18

## Decision

The durable ExECTv2 policy surface is:

```text
src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/contract/evaluation.py
```

That module owns the entity-specific decisions that make ExECTv2 evaluation
meaningful:

- which gold phrase representation is used as `ExectAnnotation.text`;
- which attributes are ignored under benchmark and semantic scoring;
- whether duplicate same-concept predictions should preserve distinct textual
  occurrences.

The policy is intentionally small. It does **not** create a generic registry
framework, and it does not claim to solve candidate generation or projection-gap
analysis. It centralizes the known load-bearing policy so later work can consume
one contract.

## Why This Was Needed

The gold-representation pass showed that the headline ExECTv2 benchmark number
fuses target choice, scorer behavior, and extractor emission unit. Before this
refactor, those choices lived in separate code locations:

- phrase-target repair was encoded in `data.py`;
- benchmark/semantic ignored-attribute policy was encoded in `scoring.py`;
- occurrence-preserving de-duplication was encoded inside the large
  deterministic `all_entities.py` extractor.

That structure worked locally but preserved the same failure mode the research
notes warned about: per-entity policy could drift independently across loader,
scorer, extractor, prompts, and reports.

The refactor keeps the heterogeneity, but makes it explicit and DRY.

## Implemented Changes

### 1. Central Evaluation Policy

Added `EntityEvaluationPolicy` in `contract/evaluation.py`.

Current policy:

| Entity | Gold phrase target | Benchmark ignored attrs | Semantic extra ignored attrs | Preserve distinct occurrences |
| --- | --- | --- | --- | --- |
| SeizureFrequency | `CUIPhrase` | `CUIPhrase`, `Certainty`, `Negation` | `CUI` | no |
| Diagnosis | `CUIPhrase` | `CUIPhrase` | `CUI` | no |
| PatientHistory | raw `text` | `CUIPhrase` | `CUI` | yes |
| Other entities | raw `text` | `CUIPhrase` | `CUI` | no |

This preserves the measured decisions from the 2026-06-17 structural pass:

- `text := CUIPhrase` is benchmark-faithful only for SeizureFrequency and
  Diagnosis;
- Certainty/Negation are out of scope for SeizureFrequency only;
- PatientHistory is the only current entity where per-occurrence emission is
  net-positive.

### 2. Loader Consumes Policy

`data.py` now calls `uses_cuiphrase_as_gold_text(entity)` when loading gold
annotations. The loader no longer owns its own phrase-repair entity set.

This keeps the raw JSON span in `raw_text` for provenance while using the declared
per-entity phrase target for scoring.

### 3. Scorer Consumes Policy

`scoring.py` now delegates:

- `benchmark_ignore_for(entity)` to `benchmark_ignore_attributes_for(entity)`;
- `semantic_ignore_for(entity)` to `semantic_ignore_attributes_for(entity)`.

The existing public scoring helpers remain intact, so callers do not need to
change. The source of truth moved from scoring implementation comments to the
evaluation contract.

### 4. Mention Identity Split Out

Added:

```text
src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/mention_identity.py
```

It owns:

- `match_span(match)`: exact source span for a rule match;
- `dedupe_mentions(mentions)`: entity-policy-aware de-duplication.

This removes cross-cutting identity policy from `deterministic/all_entities.py`.
It also fixes a contract ambiguity: `EvidenceSpan.text` now represents the exact
source slice at `start_char:end_char`, while the broader `evidence` field can
remain a sentence or regimen context.

### 5. Tests Lock The Contract

Added tests that assert:

- every ExECTv2 entity has an evaluation policy;
- SeizureFrequency and Diagnosis use `CUIPhrase` as gold text, while
  PatientHistory does not;
- SeizureFrequency's Certainty/Negation scoring exception is centralized;
- PatientHistory preserves distinct textual occurrences;
- Diagnosis repeated prose tokens still collapse to one concept-level prediction;
- emitted `EvidenceSpan` offsets and text agree with the note slice.

## What Did Not Change

This refactor should not be read as an extractor improvement claim by itself.

It does not:

- broaden candidate generation;
- change the benchmark target decisions;
- relax scoring;
- de-duplicate gold;
- inspect or tune on any locked test failures;
- claim that Diagnosis or Investigations duplicate ceilings are recovered.

It makes the existing measured policy explicit and harder to accidentally
diverge.

## Verification

Verification after the refactor:

```text
ruff check touched ExECTv2 Python files: passed
pytest tests/test_exectv2_contract.py tests/test_exectv2_scoring.py tests/test_exectv2_deterministic_all9.py -q: 55 passed
pytest all tests/test_exectv2_*.py files: 272 passed
```

## Research Implications

This supports three paper-facing claims:

1. **Generalisation discipline.** Benchmark-specific policy is isolated in the
   ExECTv2 contract rather than leaking into general extraction logic.
2. **Transparency.** The phrase target, score-layer ignored attributes, and
   occurrence policy are inspectable per entity.
3. **Deterministic rules as controlled variables.** Occurrence-preserving
   de-duplication is now an explicit policy decision, not an incidental side
   effect of the extractor.

The immediate practical effect is architectural, not metric-driven: future
deterministic, LLM-only, and hybrid ExECTv2 runs can all point at the same
evaluation contract.

## Next Work

The next foundation step should be the projection-gap ledger, not more policy
fields guessed in advance.

That ledger should consume `EntityEvaluationPolicy` and report, per row/entity:

- phrase-target gap;
- semantic attribute-bundle gap;
- CUI / benchmark-format projection gap;
- duplicate/split/merge gap;
- candidate-source miss versus projection miss.

The policy module should grow only when that ledger shows a repeated, explicit
evaluation decision that needs to be shared across loader, scorer, extractor, and
reports.

## Safe Claim Language

Safe:

```text
ExECTv2 evaluation policy is now centralized in an explicit per-entity contract:
gold phrase target, benchmark/semantic ignored attributes, and occurrence
de-duplication policy are shared by the loader, scorer, and deterministic
extractor. This preserves the measured 2026-06-17 decisions without claiming a new
candidate-generation gain.
```

Unsafe:

```text
The refactor improves ExECTv2 extraction quality or recovers the duplicate
ceilings for all entities.
```

Why unsafe: the change centralizes and tests evaluation policy. It does not add
assertion-level occurrence selection for Diagnosis/Investigations or new candidate
generation.
