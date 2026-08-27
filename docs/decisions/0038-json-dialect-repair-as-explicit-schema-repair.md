# 0038: JSON Dialect Repair As Explicit Schema Repair

Date: 2026-06-02

Extended by [decision 0042](0042-shared-local-model-structured-output-repair.md),
which applies named format repairs, failure classification, bounded retry, and
runtime probes consistently across local models.

## Decision

Treat local-model JSON dialect recovery as an explicit schema-repair step, not
as hidden parser leniency.

Structured LLM pipelines may first try strict `json.loads`. If that fails, they
may apply a bounded non-semantic dialect repair for Python-literal style objects
such as single-quoted keys/strings and `None`, then continue through normal
schema validation.

This repair must be surfaced in run artifacts as:

- `json_dialect_repaired: python_literal`
- a separate summary count, `json_dialect_repairs`

It must not count as a blocking parse/schema failure, and it must not be mixed
with deterministic label repair notes such as `final_label_repaired`.

## Context

The Qwen 35B local structured-events validation run produced many clinically
usable outputs in Python-literal syntax rather than strict JSON. In the
validation250 artifact, 83 rows failed strict JSON parsing, but all 83 could be
schema-validated after a format-only Python-literal parse, and 79 of those rows
then scored purist-correct.

This is a local-model serialization compliance issue, not a semantic extraction
change. Closed-model runs may not need this repair, so its effect must remain
measurable rather than being absorbed into the headline score.

## Consequences

- JSON dialect repair is allowed only when it preserves payload semantics and
  still passes the existing schema validators.
- Reports must keep strict parse/schema/label failures separate from JSON
  dialect repairs.
- Experiment interpretation can compare strict end-to-end results with
  format-repaired content results.
- Future local-model runs must mention non-zero `json_dialect_repairs` when
  discussing structured-output reliability.
- If dialect repair grows beyond Python-literal recovery, add named repair
  notes for each dialect rather than broadening the existing note silently.
