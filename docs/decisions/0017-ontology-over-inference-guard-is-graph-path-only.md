# 0017: The Ontology Over-Inference Guard Runs At Graph Generation Only, Not Over The Deterministic Path

Date: 2026-06-15

## Status

Accepted.

## Decision

The admissible-state ontology's no-over-inference-out-of-`unknown` guard
(`state_graph/ontology.py::is_admissible_assignment`, which drops `frequency`/
`seizure_free` nodes whose evidence is a `UNKNOWN_ONLY_SHAPE`) applies **only to
graph-minted components**. It does **not** supersede or filter the legacy
deterministic `is_current_seizure_free_evidence` path.

The fix for the no-correct-component residual is to mint a **new, clean,
competing component** (`unknown`) on the graph path and let the consensus+fresh
selector choose it — not to retroactively suppress the deterministic over-read.

This is the answer to contradiction **C2** in [[gan2026_rule_register]].

## Context

`is_current_seizure_free_evidence` (register §5, the seed of C2) treats
`"last seizure on …"` and `"no seizures since last visit"` as seizure-free —
exactly the last-event-only (§7.2) and open-ended-since (§7.3) shapes the author
unknown policy says must be `unknown`. The ontology (§9.1) blocks these mints;
the deterministic path still generates them and feeds the selector. This is the
documented `11/750` no-correct residual: three "independent" sources making the
same over-read.

The open question was whether the ontology guard should *supersede*
`is_current_seizure_free_evidence` (filter the over-reads at source, across all
candidates) or run *in parallel* (graph path only).

## Considered Options

- **Supersede** — apply the ontology admission gate as a filter over every
  candidate, including deterministic ones. Rejected: the v0.10
  deterministic-repair probe already tried reaching into the deterministic path
  to suppress these and cost **`-8/-10` rows** — it broke cases the deterministic
  path got right (the literature's "a graph layer breaks cases the bare model
  already handled" caveat, made concrete).
- **Parallel** (chosen) — the guard is a generation-time constraint for the
  graph builder; the deterministic path is untouched; correctness comes from a
  better competing component, not from filtering.

## Why

C2 is resolved *at generation for the graph path* — the over-inferred graph
component is never minted. Whether it resolves a given *row* depends on the
selector preferring the clean component, which is exactly what the Stage C
raw-wrong→final-correct / correct→wrong accounting measures
([[gan2026_kg_grounded_component_generation_design_2026-06-15]] §5). Suppressing
the deterministic over-read directly is the move that already failed at `-8/-10`;
adding evidence rather than removing it keeps the safe rows safe.

## Consequences

- `is_current_seizure_free_evidence` and the deterministic over-reads remain in
  the candidate pool. This is deliberate, not an oversight.
- C2 is "resolved at generation," not "resolved for every row." The honest
  claim is bounded; the row-level result is an empirical Stage C outcome.
- If Stage C shows the selector persistently picking the deterministic over-read
  over the clean graph `unknown`, the supersede option may be reopened behind an
  explicit ablation — but only with fresh evidence that it beats the `-8/-10`
  baseline.

## Related Artifacts

- [[gan2026_rule_register]] — contradiction C2, §5, §7.2, §7.3, §9.1
- [[gan2026_resolve_label_spec]] — §3 Step 0, §4
- [[0016-current-rate-supersedes-coexisting-current-seizure-free]]
