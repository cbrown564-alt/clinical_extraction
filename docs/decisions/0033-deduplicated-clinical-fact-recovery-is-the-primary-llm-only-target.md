# ADR 0033: Deduplicated Clinical-Fact Recovery Is The Primary LLM-Only Target

Date: 2026-06-23

## Status

Closed negative. The de-duplicated fact representation survives only in the
retained GEPA LLM-only comparator.

## Context

The recent ExECTv2 LLM-only and hybrid runs show a stable distinction between
two evaluation surfaces:

- the strict benchmark-style surface, which rewards exact annotation rendering,
  multiplicity, and full-schema attributes; and
- the `clinical_headline` surface, which measures de-duplicated clinical fact
  recovery at concept/component level.

Bare LLM-only rich-schema runs with GPT-4.1-mini and Qwen score around
`0.334`/`0.339` on the strict surface, but the same outputs score
`0.713`/`0.725` on de-duplicated `clinical_headline`. The v08 hybrid remains
the dev140 performance control at `0.9155` on `clinical_headline`. This makes
the gap look less like model capability on the whole extraction task and more
like a mismatch between the prompt target and the clinical-recovery headline.

Decision 0027 already makes clinical recovery the ExECTv2 headline and treats
mention/CUI projection as an artifact layer. The missing LLM-only experiment is
a route that directly emits de-duplicated clinical facts rather than a full
ExECTv2 annotation schema that is later collapsed by the scorer.

## Decision

The ExECTv2 LLM-only study targeted an attribution-clean program that emitted
de-duplicated clinical facts directly for the `clinical_headline` scorer.

The route will use a simplified model-owned fact schema:

- Diagnosis: concept plus affirmed/negated status.
- SeizureFrequency: seizure type plus coarse state.
- Prescription: current regimen as drug, dose, and frequency.
- Investigations: modality, performed/completed status, and result.

The model must emit every scored fact and evidence span. Deterministic code may
validate evidence, parse JSON, map the emitted simplified fact into the existing
headline scorer representation, and score the result. It must not add missing
facts, choose omitted seizure-frequency states, expand ontology companions, or
perform deterministic de-duplication that rescues a fact the model did not
select.

The study did not clear the `>0.900` dev140 target or displace the v08 hybrid.
The retained GEPA result is a negative LLM-only comparator. Its exact program,
adapter, artifacts, tests, and claim boundary are recorded in the retained
evidence manifest.

## Consequences

- The historical prompt variants, strategy registry, CLI, snapshots, and
  candidate-specific tests are not active repository interfaces.
- `exectv2/gepa/dedup_adapter.py` retains only the representation mapping needed
  by the selected GEPA comparator.
- Result language must say "clinical-recovery" or "`clinical_headline`"; it
  must not describe de-duplicated recovery as clearing the strict benchmark.
- Any future full-200 or holdout-facing audit requires a separate frozen
  protocol and authorization.

## Verification

`tests/test_exectv2_gepa_dedup_adapter.py` protects one-to-one mapping,
evidence gating, and GEPA component attribution. The retained evidence manifest
owns the no-call result replay.
