# 0003: Experiment Family Ontology

Date: 2026-06-01

## Decision

Name Gan 2026 experiment code, CLI choices, reports, and new artifacts by
research role rather than by iteration order or informal architecture numbers.

Current experiments should be organized under three top-level families:

- `rules_only`: deterministic rules produce the prediction-bearing clinical
  interpretation.
- `llm_only`: the LLM produces the prediction-bearing clinical interpretation;
  deterministic code may validate, format, normalize already selected facts, and
  score.
- `hybrid`: deterministic rules and LLM components both contribute semantic
  behavior, with extraction, selection/adjudication, and repair ownership named
  explicitly.

## Context

Early Gan 2026 work accumulated labels such as `Architecture 2` and
`section-claim-table`. These described implementation history but not the
scientific object under test. That made it harder to compare pipelines, assign
attribution, and explain whether a result was rules-only, LLM-only, or hybrid.

The project is young enough that clean current names matter more than backward
compatibility. Historical documents and artifact filenames may keep old labels
when describing prior runs, but runnable code should not preserve old aliases.

## Consequences

- Current CLI choices use ontology-aligned names such as
  `llm_only_direct_labeler`, `llm_only_structured_events`,
  `llm_only_claim_table_selector`, and
  `hybrid_rules_candidates_llm_adjudicator`.
- Current modules use matching names, for example
  `llm_only_claim_table_selector.py` and
  `hybrid_rules_candidates_llm_adjudicator.py`.
- Old runnable aliases such as `architecture2`, `section-claim-table`,
  `dspy_modules.py`, and `section_claim_table.py` are removed.
- New artifact names should put the experiment family and decomposition before
  split, model, version, and date.
- Historical runs worth preserving can be rerun under the new naming scheme
  rather than supported through compatibility layers.
