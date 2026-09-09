# 0003: Use plain names for pipeline comparisons

Date: 2026-06-01

> [!NOTE]
> **Historical Guidance Archive**
> This document records historical guidance from earlier phases of the project. It does not authorize new runs, govern the longitudinal schema, or supersede current project direction. The active project plan is `docs/plans/ACTIVE_ROADMAP.md` (relative link: `../../plans/ACTIVE_ROADMAP.md`). Existing benchmark split, scoring, and holdout safeguards remain in force.

Updated: 2026-07-14

## Decision

Use names that say how a prediction is produced. Command-line choices are
`rules`, `llm`, and `llm_with_rules`.

Research tables may use the corresponding method names:

- `rules_only`: deterministic rules produce the clinical interpretation.
- `llm_only`: the LLM produces the clinical interpretation. Deterministic code
  may validate or format facts the model has already selected.
- `llm_with_rules`: an LLM extracts or selects clinical facts and deterministic
  code can change clinical meaning through normalization, selection, or repair.

## Context

Early work accumulated version codes and names such as `Architecture 2`,
`section-claim-table`, `deterministic_canonical_pipeline`, and
`hybrid_structured_events`. These names record implementation history but do
not help a new collaborator choose a pipeline.

Saved evidence and its filenames keep their original identifiers because hashes
and replay checks depend on them. Current commands and prose use plain names.

## Consequences

- CLI help uses `rules`, `llm`, and `llm_with_rules`.
- Code may retain an old identifier only when saved evidence or an import path
  requires it. Comments must identify it as a retained evidence ID.
- New output filenames start with the task and plain method name, followed by
  the split, model, date, and version when needed.
- Prose gives a version code such as `V12` or `v08` only when linking to saved
  evidence; it also states what the version does.
