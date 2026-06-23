# ADR 0033: Deduplicated Clinical-Fact Recovery Is The Primary LLM-Only Target

Date: 2026-06-23

## Status

Accepted for ExECTv2 LLM-only development on the dev split.

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

The primary ExECTv2 LLM-only development target is now a single-prompt,
attribution-clean route that emits de-duplicated clinical facts directly for
the `clinical_headline` scorer.

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

The working target is `>0.900` dev140 `clinical_headline` F1 with GPT-4.1-mini,
followed by unchanged-configuration rollout to DeepSeek and Qwen. The strict
benchmark surface remains a required diagnostic and paper-comparability
readout, but it is not the optimization target for this LLM-only workstream.

## Consequences

- Satellite 13 becomes the primary active ExECTv2 research workstream.
- Rich-schema LLM-only and hybrid artifacts are demoted to comparison controls,
  not active optimization targets.
- Phase 1 must archive superseded rich-schema iteration sprawl without deleting
  evidence, leaving only the two live comparators in the active scoreboard:
  bare rich-schema LLM-only and v08 hybrid.
- Phase 2 must prove the adapter by reproducing the existing de-duplicated
  baseline before any new prompt result is claimed.
- Result language must say "clinical-recovery" or "`clinical_headline`"; it
  must not describe de-duplicated recovery as clearing the strict benchmark.
- Any future full-200 or holdout-facing audit requires a separate frozen
  protocol and authorization.

## Verification

Phase 0 is complete when:

- this ADR is accepted;
- `docs/plans/exectv2/13_dedup_clinical_facts_llm_only.md` names the route and
  de-duplicated clinical-recovery surface as the primary LLM-only target; and
- `PROJECT_STATUS.md` records Phase 1 cleanup as the next active step.

