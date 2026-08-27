# 0002: Deterministic Rules As Controlled Variables

Date: 2026-05-31

## Decision

Treat deterministic preprocessing, normalization, temporal reasoning helpers, validation, and repair logic as explicit experimental variables.

## Context

Prior clinical extraction systems often rely on some rules even when the headline method is an LLM. Those rules can be underreported, difficult to reproduce, or mixed together in ways that obscure what actually improves performance.

For this project, deterministic rules are part of the scientific contribution.
Each prediction-bearing rule must have a meaningful category. Ablation studies
must isolate the rule groups needed for the claim being tested.

## Consequences

- Rules must carry a category such as general, epilepsy clinical, seizure-frequency, Gan-specific, or benchmark-formatting.
- Specific rules can be useful, but they must be named as specific rather than disguised as general clinical logic.
- Experiments report the effect of adding or removing a rule category when that
  category contributes to the comparison or claim.
- Prefer readable, tested rule code over compact regular expressions whose
  clinical behavior is difficult to inspect.

