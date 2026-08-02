# 0048: Refocus the repository for comprehension, live use, and external validation

Date: 2026-08-02
Status: accepted; implementation not yet complete

## Decision

Refactor the repository over the next working week into a clean research system
that is immediately useful to a supervisor and remains ready for new runs and
external validation. The goal is not a retrospective evidence archive and not
an expansion into a clinical deployment system. It is a working codebase,
frontend, evidence set, and explanation package with one clear path from the
system story to live execution, exact replay, and stated limits.

The retained operational system must support:

- the six selected models across the three selected methods and two tasks;
- live runs and saved/fixture demonstrations;
- full permitted development-split workflows in the frontend;
- exact no-call replay of selected results from saved raw outputs;
- the prompt, component, negative, and safety evidence needed to explain the
  selected methods, including the essential DeepSeek and Luna studies; and
- a focused, restricted research-validation workflow for future real-patient
  data, without presenting it as clinical deployment.

Everything else is a deletion or simplification candidate. Historical material
must be reviewed for value and regeneration status before removal. A retained
item must serve at least one of these purposes:

1. explain the system;
2. demonstrate a selected method;
3. support a named evidence claim;
4. reproduce a selected result; or
5. state a limitation, decision, or historical reason needed to prevent
   misunderstanding.

## Supervisor-facing completion standard

The final repository must let a supervisor, without agent assistance:

- understand the system from the README and concise supervisor path;
- open the frontend and run the selected development workflows;
- inspect one teaching letter through all six task-method paths;
- see one deliberate failure and its recovery or containment;
- find the canonical results report, evidence/limits table, and reproduction
  commands; and
- distinguish engineering verification, research evidence, clinical review,
  and clinical validation.

The frontend is the primary interactive demonstration. The teaching case is its
explanatory companion. Both saved/fixture mode and clearly marked live one-row
mode remain available.

## Reproduction standard

Selected results use protocol reproduction plus exact replay. A new run must
record the same task, model, method, prompt/program version, route, split,
repair policy, scorer, and run metadata. The original raw output must be
retained so the reported result can be replayed exactly without another model
call. Exact live model text is not promised for nondeterministic providers.

## Cleanup rules

- Active source, tests, frontend routes, configuration keys, and documentation
  may receive breaking renames when every retained caller and workflow is
  migrated and verified.
- Remove obsolete compatibility facades, historical paths, duplicate reports,
  and unused infrastructure after dependency and evidence review.
- Keep one canonical owner for each durable concern; other documents link to it.
- The main story covers the selected six methods. Historical candidates belong
  in focused decision evidence or a replay-only area.
- The cleanup is behavior-preserving by default. Clinical meaning, scoring,
  splits, prompts, model routing, and evidence policy require a separate
  predeclared study and verification if changed.
- External-validation runs require a readiness record naming the data owner,
  permitted dataset, split policy, technical run owner, independent clinical
  reviewer, review process, and claim boundary.

## Required owner documents and outputs

- `README.md` is the front door.
- `PROJECT_STATUS.md` owns current evidence and checks.
- `docs/canon/10_paper_provenance.md` owns claim strength and limits.
- `docs/REGENERATION.md` owns regeneration and historical-artifact triage.
- Source manifests and generated architecture documents own current stage
  definitions.
- One canonical results report owns the six-model, three-method, two-task
  results matrix. Focused reports own prompt, component, negative, safety, and
  validation evidence.

## Completion gate

Completion requires no unexplained obsolete active labels, broken internal
links, duplicate durable owners, stale claims outside the canonical results
report, unexplained retained artifacts, or unverified selected live and replay
paths. Generated architecture and frontend outputs must be rebuilt and checked.

This decision does not establish clinical validity. Independent clinical review
and external validation remain open work.
