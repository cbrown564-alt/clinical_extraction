---
name: clinical-extraction-kanban
description: Maintain project momentum and documentation in the clinical-extraction repo. Use when updating PROJECT_STATUS.md, milestones, active tasks, backlog, blocked work, experiment decisions, runbook/documentation follow-through, or after meaningful project progress that should be captured for continuity.
---

# Clinical Extraction Kanban

Use this skill to leave the project easy to resume. The goal is steady progress
with enough context for the next contributor, not ceremony. `PROJECT_STATUS.md`
is a control surface, not a full changelog.

## Environment

When status work includes commands, tests, experiments, notebooks, or package
inspection, use the `clinical-extraction-env` skill first. Record durable
environment repairs in `PROJECT_STATUS.md` when they affect reproducibility.

## Required Context

Read these before updating project state:

- `PROJECT_STATUS.md`
- Any task-specific runbook or design doc touched by the work
- `docs/research/contribution_thesis.md` when project state touches paper claims, ablations, rule taxonomy, or research framing

## Workflow

1. Identify what changed durably: code, tests, docs, data policy, experiments, blockers, or decisions.
2. Update `PROJECT_STATUS.md` as the single project-control document.
3. Keep `PROJECT_STATUS.md` focused on active objective, strategy, recent context, active priorities, work board, immediate next step, and known blockers.
4. Use its `Work Board` section for work management:
   - `Now`: one to three active tasks.
   - `Next`: near-term tasks that unblock the active objective.
   - `Blocked`: tasks awaiting information, tooling, data access, or policy decisions.
   - `Backlog`: useful later work.
   - `Done Recently`: concise completion log with dates.
5. Keep entries action-oriented and concrete.
6. Move tasks between columns rather than duplicating them.
7. When an experiment or scoring-policy decision changes the plan, link the relevant doc or run artifact.
8. Run tests/Ruff if the documentation change accompanies code.
9. When research framing changes, record whether it affects modularity, generalisation, transparency, deterministic-rule ablations, or claim language.

## PROJECT_STATUS.md Discipline

When updating `PROJECT_STATUS.md`, enforce these constraints:

- Prefer a lean document that opens onto the current work, not a narrative archive.
- Summarize recent important events as context only when they change what to do next.
- Put detailed remediation logs, row lists, experiment tables, ablation details, and historical blow-by-blow notes in linked docs or run artifacts.
- Keep `Recent Context` short enough to scan quickly. It should explain the current state, key caveats, and why the next tasks matter.
- Keep `Active Priorities` and `Work Board` more prominent than `Done Recently`.
- Limit `Done Recently` to milestone-level completions. Collapse repeated same-day entries into one summary bullet.
- Preserve important numeric results and caveats, especially split discipline, validation/test distinction, benchmark-claim limits, and known score drift.
- Prefer links to durable artifacts over copying their contents into the status file.
- Remove or consolidate stale tasks when adding new ones.
- If the status file is becoming longer than roughly 100 lines, actively compress before finishing the update.

## Principles

- Documentation should make the next useful action obvious.
- Avoid stale optimism: record blockers and uncertainty plainly.
- Keep benchmark claims conservative until scoring policy and evaluation surface are explicit.
- Prefer short entries over narrative status dumps.
- Optimize for resumption: after reading the first screen and the `Now` list, the next contributor should know what to do.
